import Foundation
import os

/// JSON file persistence for calculator history.
///
/// Uses the same layout as the Windows app: a list of objects with
/// `expression`, `result`, and ISO 8601 `timestamp` fields.
enum HistoryStore {
    private static let logger = Logger(
        subsystem: "com.plaintxtoffice.fincalc",
        category: "HistoryStore",
    )

    /// Load history entries from a JSON file.
    ///
    /// - Returns: Loaded history, or an empty History if the file is
    ///   missing or corrupt.
    static func loadHistory(from url: URL) -> History {
        guard FileManager.default.fileExists(atPath: url.path) else {
            return History()
        }
        do {
            let raw = try Data(contentsOf: url)
            if String(decoding: raw, as: UTF8.self)
                .trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            {
                return History()
            }
            let records = try JSONDecoder().decode(
                [HistoryRecord].self,
                from: raw,
            )
            return History(entries: try records.map { try $0.toEntry() })
        } catch {
            logger.error(
                "Failed to load history from \(url.path): \(error)",
            )
            return History()
        }
    }

    /// Write all history entries to a JSON file.
    ///
    /// - Throws: Write failures, after logging them, so callers can report
    ///   unsaved results.
    static func writeHistory(_ history: History, to url: URL) throws {
        do {
            try FileManager.default.createDirectory(
                at: url.deletingLastPathComponent(),
                withIntermediateDirectories: true,
            )
            let encoder = JSONEncoder()
            encoder.outputFormatting = [
                .prettyPrinted, .sortedKeys, .withoutEscapingSlashes,
            ]
            let records = history.entries.map(HistoryRecord.init)
            try encoder.encode(records).write(to: url, options: .atomic)
        } catch {
            logger.error("Failed to write history to \(url.path): \(error)")
            throw error
        }
    }
}

/// The JSON shape of one history entry.
private struct HistoryRecord: Codable {
    let expression: String
    let result: String
    let timestamp: String

    init(_ entry: HistoryEntry) {
        expression = entry.expression
        result = entry.result
        timestamp = Date.ISO8601FormatStyle(includingFractionalSeconds: true)
            .format(entry.timestamp)
    }

    func toEntry() throws -> HistoryEntry {
        HistoryEntry(
            expression: expression,
            result: result,
            timestamp: try Self.parseTimestamp(timestamp),
        )
    }

    /// Accept timestamps with or without fractional seconds.
    private static func parseTimestamp(_ text: String) throws -> Date {
        let withFraction = Date.ISO8601FormatStyle(
            includingFractionalSeconds: true,
        )
        if let date = try? withFraction.parse(text) {
            return date
        }
        return try Date.ISO8601FormatStyle().parse(text)
    }
}
