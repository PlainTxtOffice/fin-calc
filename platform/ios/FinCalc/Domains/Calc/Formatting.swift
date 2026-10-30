import Foundation

/// Presentation-only formatting for calculator results.
enum Formatting {
    static let maxDecimalPlaces = 6

    /// Round a result string for display without touching stored values.
    ///
    /// - Parameters:
    ///   - value: The full-precision Decimal result as a string.
    ///   - decimalPlaces: Places to show, or nil for full precision.
    /// - Returns: The rounded string, padded with zeros to `decimalPlaces`,
    ///   or `value` unchanged when `decimalPlaces` is nil, `value` is not a
    ///   number, or the rounded value would exceed the 28-digit precision.
    static func formatResult(_ value: String, decimalPlaces: Int?) -> String {
        guard let places = decimalPlaces,
              var number = DecimalMath.parseNumber(value)
        else {
            return value
        }
        if !number.isZero
            && DecimalMath.magnitude(of: number) + 1 + places
                > DecimalMath.precision
        {
            return value
        }
        var rounded = Decimal()
        NSDecimalRound(&rounded, &number, places, .bankers)
        var text = rounded.description
        guard places > 0 else { return text }
        if let dot = text.firstIndex(of: ".") {
            let shown = text.distance(from: dot, to: text.endIndex) - 1
            text += String(repeating: "0", count: places - shown)
        } else {
            text += "." + String(repeating: "0", count: places)
        }
        return text
    }
}
