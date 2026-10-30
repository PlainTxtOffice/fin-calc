import Foundation
import Observation

/// Own the expression, history, and settings for the running app.
///
/// Views send key presses here and render the published state; parsing,
/// evaluation, and persistence stay out of the view layer.
@MainActor
@Observable
final class CalculatorSession {
    private(set) var history: History
    private(set) var settings: Settings
    /// The expression being entered, or the formatted result after `=`.
    private(set) var displayText = ""
    /// The latest error or save failure; empty when there is none.
    private(set) var statusText = ""

    private var builder = ExpressionBuilder()
    @ObservationIgnored private let historyURL: URL
    @ObservationIgnored private let settingsURL: URL
    // One serial queue keeps history writes in order, off the main thread.
    @ObservationIgnored private let writeQueue = DispatchQueue(
        label: "com.tripp.fin-calc.history-write",
        qos: .utility,
    )

    init(
        history: History,
        settings: Settings,
        historyURL: URL,
        settingsURL: URL,
    ) {
        var history = history
        history.trim(to: settings.maxHistoryEntries)
        self.history = history
        self.settings = settings
        self.historyURL = historyURL
        self.settingsURL = settingsURL
    }

    /// Load saved history and settings from the app's data folder.
    static func load(
        historyURL: URL = PathHandler.historyFile,
        settingsURL: URL = PathHandler.settingsFile,
    ) -> CalculatorSession {
        CalculatorSession(
            history: HistoryStore.loadHistory(from: historyURL),
            settings: SettingsStore.loadSettings(from: settingsURL),
            historyURL: historyURL,
            settingsURL: settingsURL,
        )
    }

    /// Add a digit, operator, parenthesis, or function token.
    func addSymbol(_ symbol: String) {
        statusText = ""
        if !builder.addSymbol(symbol) {
            statusText = "Invalid input: \(symbol)"
        }
        updateDisplay()
    }

    /// Evaluate the expression, record it, and show the formatted result.
    func evaluate() {
        let tokens = builder.tokens
        guard !tokens.isEmpty else { return }
        let result: Decimal
        do {
            result = try Evaluator.evaluate(tokens)
        } catch {
            statusText = error.localizedDescription
            return
        }

        let resultText = result.description
        history.append(HistoryEntry(
            expression: builder.toDisplay(),
            result: resultText,
            timestamp: .now,
        ))
        writeHistory()

        builder.clear()
        builder.insertResult(resultText)
        statusText = ""
        displayText = formatResult(resultText)
    }

    func clear() {
        builder.clear()
        statusText = ""
        updateDisplay()
    }

    func backspace() {
        builder.backspace()
        updateDisplay()
    }

    func toggleSign() {
        builder.toggleSign()
        updateDisplay()
    }

    /// Insert a past full-precision result into the expression.
    func insertResult(_ result: String) {
        builder.insertResult(result)
        statusText = ""
        updateDisplay()
    }

    func clearHistory() {
        history.clearAll()
        writeHistory()
    }

    /// Apply and save new settings, trimming history to the new cap.
    func applySettings(_ newSettings: Settings) {
        settings = newSettings
        history.trim(to: newSettings.maxHistoryEntries)
        writeHistory()
        do {
            try SettingsStore.writeSettings(newSettings, to: settingsURL)
        } catch {
            statusText = "Settings could not be saved"
        }
        updateDisplay()
    }

    /// Round a stored result to the configured display precision.
    func formatResult(_ result: String) -> String {
        Formatting.formatResult(result, decimalPlaces: settings.decimalPlaces)
    }

    /// Block until queued history writes finish, e.g. before suspension.
    func waitForPendingWrites() {
        writeQueue.sync {}
    }

    private func updateDisplay() {
        displayText = builder.toDisplay()
    }

    /// Snapshot entries and write them to disk off the main thread.
    private func writeHistory() {
        let snapshot = history
        let url = historyURL
        writeQueue.async { [weak self] in
            do {
                try HistoryStore.writeHistory(snapshot, to: url)
            } catch {
                Task { @MainActor in
                    self?.statusText = "History could not be saved"
                }
            }
        }
    }
}
