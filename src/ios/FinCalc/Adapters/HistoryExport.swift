import Foundation

/// CSV export for calculator history.
enum HistoryExport {
    /// Format history as CSV text with a timestamp, expression, result header.
    ///
    /// Matches Python's `csv.writer` output: CRLF line endings, and fields
    /// containing commas, quotes, or line breaks are quoted.
    static func formatCSV(_ history: History) -> String {
        var rows = [["timestamp", "expression", "result"]]
        for entry in history.entries {
            rows.append([
                entry.timestamp.formatted(.iso8601),
                entry.expression,
                entry.result,
            ])
        }
        return rows.map { row in
            row.map(quoteField).joined(separator: ",") + "\r\n"
        }.joined()
    }

    private static func quoteField(_ field: String) -> String {
        guard field.contains(where: { ",\"\r\n".contains($0) }) else {
            return field
        }
        return "\"" + field.replacingOccurrences(of: "\"", with: "\"\"") + "\""
    }
}
