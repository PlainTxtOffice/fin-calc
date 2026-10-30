import Foundation

/// A single calculation record.
struct HistoryEntry: Equatable, Sendable {
    /// The expression as entered (e.g. "12 + 3").
    var expression: String
    /// The full-precision Decimal result as a string (e.g. "15").
    var result: String
    /// When the calculation was performed.
    var timestamp: Date
}

/// In-memory ordered list of calculation history entries.
struct History: Equatable, Sendable {
    static let defaultCap = 1000
    static let minCap = 1
    static let maxCap = 10_000

    var entries: [HistoryEntry] = []
    /// Maximum retained entries; nil means unlimited.
    private(set) var maxEntries: Int?

    init(entries: [HistoryEntry] = [], maxEntries: Int? = nil) {
        self.entries = entries
        self.maxEntries = maxEntries
    }

    /// Add a new entry, trimming the oldest if over the cap.
    mutating func append(_ entry: HistoryEntry) {
        entries.append(entry)
        trim(to: maxEntries)
    }

    /// Set a new cap and drop the oldest entries beyond it.
    ///
    /// A cap of 0 empties the history.
    mutating func trim(to maxEntries: Int?) {
        self.maxEntries = maxEntries
        if let maxEntries, entries.count > maxEntries {
            entries.removeFirst(entries.count - maxEntries)
        }
    }

    /// Remove all entries from the history.
    mutating func clearAll() {
        entries.removeAll()
    }
}
