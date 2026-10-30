import Foundation
import os

/// JSON file persistence for application settings.
///
/// Invalid or missing files always produce default Settings; loading never
/// throws to the caller.
enum SettingsStore {
    private static let logger = Logger(
        subsystem: "com.tripp.fin-calc",
        category: "SettingsStore",
    )

    /// Load settings from a JSON file.
    ///
    /// - Returns: Loaded settings; individual invalid fields fall back to
    ///   their defaults, and a missing or corrupt file yields all defaults.
    static func loadSettings(from url: URL) -> Settings {
        guard FileManager.default.fileExists(atPath: url.path) else {
            return Settings()
        }
        do {
            let raw = try Data(contentsOf: url)
            if String(decoding: raw, as: UTF8.self)
                .trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            {
                return Settings()
            }
            return try JSONDecoder().decode(SettingsRecord.self, from: raw)
                .settings
        } catch {
            logger.error(
                "Failed to load settings from \(url.path): \(error)",
            )
            return Settings()
        }
    }

    /// Write settings to a JSON file.
    static func writeSettings(_ settings: Settings, to url: URL) throws {
        do {
            try FileManager.default.createDirectory(
                at: url.deletingLastPathComponent(),
                withIntermediateDirectories: true,
            )
            let encoder = JSONEncoder()
            encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
            try encoder.encode(SettingsRecord(settings))
                .write(to: url, options: .atomic)
        } catch {
            logger.error("Failed to write settings to \(url.path): \(error)")
            throw error
        }
    }
}

/// The JSON shape of the settings file, validated field by field.
private struct SettingsRecord: Codable {
    let settings: Settings

    private enum Key: String, CodingKey {
        case decimalPlaces = "decimal_places"
        case theme
        case maxHistoryEntries = "max_history_entries"
    }

    init(_ settings: Settings) {
        self.settings = settings
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: Key.self)
        let defaults = Settings()
        let theme = (try? container.decode(String.self, forKey: .theme))
            .flatMap(Theme.init(rawValue:))
        settings = Settings(
            decimalPlaces: Self.readBoundedInt(
                container,
                .decimalPlaces,
                minimum: 0,
                maximum: Formatting.maxDecimalPlaces,
            ),
            theme: theme ?? defaults.theme,
            maxHistoryEntries: Self.readHistoryCap(container),
        )
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: Key.self)
        try container.encode(settings.decimalPlaces, forKey: .decimalPlaces)
        try container.encode(settings.theme.rawValue, forKey: .theme)
        try container.encode(
            settings.maxHistoryEntries,
            forKey: .maxHistoryEntries,
        )
    }

    /// Return the value clamped to `maximum`, or nil if missing or invalid.
    ///
    /// Values below `minimum` are rejected rather than clamped.
    private static func readBoundedInt(
        _ container: KeyedDecodingContainer<Key>,
        _ key: Key,
        minimum: Int,
        maximum: Int,
    ) -> Int? {
        guard let value = try? container.decode(Int.self, forKey: key),
              value >= minimum
        else {
            return nil
        }
        return min(value, maximum)
    }

    /// Read the history cap, distinguishing absent, null, and invalid.
    ///
    /// An explicit JSON null means unlimited (nil); a missing or invalid
    /// value falls back to the default cap; valid ints are clamped.
    private static func readHistoryCap(
        _ container: KeyedDecodingContainer<Key>,
    ) -> Int? {
        guard container.contains(.maxHistoryEntries) else {
            return Settings().maxHistoryEntries
        }
        if (try? container.decodeNil(forKey: .maxHistoryEntries)) == true {
            return nil
        }
        return readBoundedInt(
            container,
            .maxHistoryEntries,
            minimum: History.minCap,
            maximum: History.maxCap,
        ) ?? Settings().maxHistoryEntries
    }
}
