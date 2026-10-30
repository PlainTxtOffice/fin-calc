import Foundation
import Testing

@testable import FinCalc

/// A fresh temporary folder per test, removed afterwards.
final class TemporaryFolder: Sendable {
    let url = FileManager.default.temporaryDirectory
        .appending(path: UUID().uuidString, directoryHint: .isDirectory)

    func file(_ name: String) -> URL {
        url.appending(path: name)
    }

    func write(_ text: String, to name: String) throws {
        try FileManager.default.createDirectory(
            at: url,
            withIntermediateDirectories: true,
        )
        try Data(text.utf8).write(to: file(name))
    }

    deinit {
        try? FileManager.default.removeItem(at: url)
    }
}

@Suite("History store")
struct HistoryStoreTests {
    let folder = TemporaryFolder()

    @Test func roundTrip() throws {
        let history = History(entries: [
            HistoryEntry(
                expression: "1 / 4",
                result: "0.25",
                timestamp: Date(timeIntervalSince1970: 1_700_000_000.5),
            ),
        ])
        let url = folder.file("nested/history.json")
        try HistoryStore.writeHistory(history, to: url)
        #expect(HistoryStore.loadHistory(from: url) == history)
        // Slashes stay readable, matching the Windows app's JSON.
        let text = try String(contentsOf: url, encoding: .utf8)
        #expect(text.contains("\"1 / 4\""))
    }

    @Test func readsWindowsTimestamps() throws {
        try folder.write("""
            [{"expression": "2 + 2", "result": "4",
              "timestamp": "2026-10-22T21:33:00+00:00"}]
            """, to: "history.json")
        let history = HistoryStore.loadHistory(from: folder.file("history.json"))
        #expect(history.entries.map(\.result) == ["4"])
    }

    @Test(arguments: ["", "   ", "{not json", "{\"a\": 1}", "[{\"result\": \"1\"}]"])
    func corruptFileLoadsEmpty(text: String) throws {
        try folder.write(text, to: "history.json")
        #expect(HistoryStore.loadHistory(from: folder.file("history.json")) == History())
    }

    @Test func missingFileLoadsEmpty() {
        #expect(HistoryStore.loadHistory(from: folder.file("none.json")) == History())
    }
}

@Suite("Settings store")
struct SettingsStoreTests {
    let folder = TemporaryFolder()

    private func load(_ text: String) throws -> Settings {
        try folder.write(text, to: "settings.json")
        return SettingsStore.loadSettings(from: folder.file("settings.json"))
    }

    @Test func roundTrip() throws {
        let settings = Settings(
            decimalPlaces: 2,
            theme: .light,
            maxHistoryEntries: nil,
        )
        let url = folder.file("settings.json")
        try SettingsStore.writeSettings(settings, to: url)
        #expect(SettingsStore.loadSettings(from: url) == settings)
        let text = try String(contentsOf: url, encoding: .utf8)
        #expect(text.contains("\"max_history_entries\" : null"))
    }

    @Test func missingFileUsesDefaults() {
        #expect(
            SettingsStore.loadSettings(from: folder.file("none.json"))
                == Settings(),
        )
    }

    @Test(arguments: ["", "[1, 2]", "not json"])
    func corruptFileUsesDefaults(text: String) throws {
        #expect(try load(text) == Settings())
    }

    @Test func invalidFieldsFallBackIndividually() throws {
        let settings = try load("""
            {"decimal_places": -1, "theme": "neon", "max_history_entries": true}
            """)
        #expect(settings == Settings())
    }

    @Test func valuesAboveMaximumAreClamped() throws {
        let settings = try load("""
            {"decimal_places": 40, "theme": "light", "max_history_entries": 99999}
            """)
        #expect(settings.decimalPlaces == Formatting.maxDecimalPlaces)
        #expect(settings.theme == .light)
        #expect(settings.maxHistoryEntries == History.maxCap)
    }

    @Test func nullHistoryCapMeansUnlimited() throws {
        let settings = try load(#"{"max_history_entries": null}"#)
        #expect(settings.maxHistoryEntries == nil)
    }

    @Test func missingHistoryCapUsesDefault() throws {
        let settings = try load(#"{"decimal_places": 3}"#)
        #expect(settings.decimalPlaces == 3)
        #expect(settings.maxHistoryEntries == History.defaultCap)
    }
}

@Suite("Calculator session")
@MainActor
struct CalculatorSessionTests {
    let folder = TemporaryFolder()

    private func makeSession(
        settings: Settings = Settings(),
    ) -> CalculatorSession {
        CalculatorSession(
            history: History(),
            settings: settings,
            historyURL: folder.file("history.json"),
            settingsURL: folder.file("settings.json"),
        )
    }

    private func press(_ session: CalculatorSession, _ symbols: [String]) {
        symbols.forEach(session.addSymbol)
    }

    @Test func evaluateRecordsAndSavesHistory() {
        let session = makeSession()
        press(session, ["0", ".", "1", "+", "0", ".", "2"])
        session.evaluate()
        #expect(session.displayText == "0.3")
        #expect(session.history.entries.map(\.expression) == ["0.1 + 0.2"])
        session.waitForPendingWrites()
        let saved = HistoryStore.loadHistory(from: folder.file("history.json"))
        #expect(saved.entries.map(\.result) == ["0.3"])
    }

    @Test func resultUsesDisplayPrecisionButStoresFullValue() {
        let session = makeSession(settings: Settings(decimalPlaces: 2))
        press(session, ["2", "/", "3"])
        session.evaluate()
        #expect(session.displayText == "0.67")
        #expect(
            session.history.entries.last?.result
                == "0.6666666666666666666666666667",
        )
    }

    @Test func operatorContinuesFromResult() {
        let session = makeSession()
        press(session, ["2", "+", "3"])
        session.evaluate()
        press(session, ["*", "4"])
        session.evaluate()
        #expect(session.displayText == "20")
    }

    @Test func errorsShowInStatusWithoutRecording() {
        let session = makeSession()
        press(session, ["5", "/", "0"])
        session.evaluate()
        #expect(session.statusText == "Division by zero")
        #expect(session.history.entries.isEmpty)
        session.clear()
        #expect(session.statusText.isEmpty)
        #expect(session.displayText.isEmpty)
    }

    @Test func rejectedSymbolShowsStatus() {
        let session = makeSession()
        session.addSymbol("*")
        #expect(session.statusText == "Invalid input: *")
    }

    @Test func applySettingsTrimsHistoryAndSaves() {
        let session = makeSession()
        for digit in ["1", "2", "3"] {
            session.addSymbol(digit)
            session.evaluate()
            session.clear()
        }
        session.applySettings(Settings(maxHistoryEntries: 2))
        #expect(session.history.entries.map(\.result) == ["2", "3"])
        #expect(
            SettingsStore.loadSettings(from: folder.file("settings.json"))
                .maxHistoryEntries == 2,
        )
    }

    @Test func clearHistoryEmptiesTape() {
        let session = makeSession()
        session.addSymbol("1")
        session.evaluate()
        session.clearHistory()
        session.waitForPendingWrites()
        #expect(session.history.entries.isEmpty)
        #expect(
            HistoryStore.loadHistory(from: folder.file("history.json"))
                .entries.isEmpty,
        )
    }
}
