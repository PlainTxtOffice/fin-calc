import Foundation

/// Decimal arithmetic that mirrors Python's default `decimal` context.
///
/// Python rounds every result to 28 significant digits, half-even, and
/// computes `ln` and fractional powers to that precision. Foundation's
/// `Decimal` carries up to 38 digits but has neither function, so `ln` and
/// `exp` are computed here from series at full width and then rounded.
enum DecimalMath {
    /// Significant digits kept in every result, as in Python's context.
    static let precision = 28

    private static let posix = Locale(identifier: "en_US_POSIX")

    // ln(2) and ln(10) to 38 significant digits, the width of Decimal.
    private static let ln2 = Decimal(
        string: "0.69314718055994530941723212145817656807",
        locale: posix,
    )!
    private static let ln10 = Decimal(
        string: "2.3025850929940456840179914546843642076",
        locale: posix,
    )!

    /// Return the value of a numeric literal, or nil if it is not one.
    ///
    /// `Decimal(string:)` accepts trailing garbage ("12abc" is 12), so the
    /// literal must match the evaluator's number grammar first.
    static func parseNumber(_ text: String) -> Decimal? {
        let literal = /-?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?/
        guard text.wholeMatch(of: literal) != nil else { return nil }
        return Decimal(string: text, locale: posix)
    }

    /// Power of ten of the leading digit: 2 for 123.4, -3 for 0.00123.
    static func magnitude(of value: Decimal) -> Int {
        let digits = value.significand.magnitude.description.count
        return value.exponent + digits - 1
    }

    /// Round to `digits` significant digits, half-even.
    static func roundToPrecision(
        _ value: Decimal,
        digits: Int = precision,
    ) -> Decimal {
        guard value.isFinite, !value.isZero else { return value }
        var source = value
        var result = Decimal()
        let places = digits - 1 - magnitude(of: value)
        NSDecimalRound(&result, &source, places, .bankers)
        return result
    }

    /// Base-10 logarithm of a positive value.
    static func log10(_ value: Decimal) -> Decimal {
        roundToPrecision(ln(value) / ln10)
    }

    /// Raise `base` to `exponent`, following Python's error cases.
    static func power(_ base: Decimal, _ exponent: Decimal) throws -> Decimal {
        let invalid = EvaluationError(
            "Invalid exponentiation: \(base) ^ \(exponent)",
        )
        let wholeExponent = integerValue(of: exponent)
        if base.isZero {
            if exponent.isZero { throw invalid }
            if exponent < 0 { throw EvaluationError.outOfRange }
            return 0
        }
        if base < 0 && wholeExponent == nil { throw invalid }
        let result: Decimal
        if let whole = wholeExponent, abs(whole) <= 9999 {
            result = pow(base, whole)
        } else {
            // base^exponent = exp(exponent * ln|base|), signed for odd powers.
            guard let size = exp(exponent * ln(base.magnitude)) else {
                throw EvaluationError.outOfRange
            }
            let isOdd = wholeExponent.map { !$0.isMultiple(of: 2) } ?? false
            result = base < 0 && isOdd ? -size : size
        }
        // A nonzero base never yields zero; zero here means underflow.
        guard !result.isZero else { throw EvaluationError.outOfRange }
        return try checked(result)
    }

    /// Return `value`, or throw if an operation overflowed to NaN.
    static func checked(_ value: Decimal) throws -> Decimal {
        guard value.isFinite, !value.isNaN else {
            throw EvaluationError.outOfRange
        }
        return value
    }

    /// Natural logarithm of a positive value.
    private static func ln(_ value: Decimal) -> Decimal {
        // value = mantissa * 10^tens, mantissa in [1, 10).
        let tens = magnitude(of: value)
        var mantissa = Decimal(
            sign: .plus,
            exponent: value.exponent - tens,
            significand: value.significand.magnitude,
        )
        // Halve into [1, 1.5] so the series below converges quickly.
        var halvings = 0
        while mantissa > 1.5 {
            mantissa /= 2
            halvings += 1
        }

        // ln(m) = 2 * atanh(z), z = (m - 1) / (m + 1).
        let z = (mantissa - 1) / (mantissa + 1)
        let zSquared = z * z
        var zPower = z
        var sum = z
        var denominator: Decimal = 1
        while !zPower.isZero {
            zPower *= zSquared
            denominator += 2
            let term = zPower / denominator
            if term.isZero || magnitude(of: term) < -40 { break }
            sum += term
        }
        return 2 * sum + Decimal(halvings) * ln2 + Decimal(tens) * ln10
    }

    /// e raised to `value`, or nil when the result is outside Decimal range.
    private static func exp(_ value: Decimal) -> Decimal? {
        // Decimal spans roughly 1e-128 ... 1e165, about 2^-425 ... 2^548.
        guard let twos = nearestInteger(value / ln2),
              (-425...548).contains(twos)
        else {
            return nil
        }

        // e^value = 2^twos * e^remainder, with |remainder| <= ln(2) / 2.
        // Dividing the remainder by 2^8 and squaring 8 times afterwards
        // keeps the Taylor series short.
        let reduced = (value - Decimal(twos) * ln2) / 256
        var term: Decimal = 1
        var sum: Decimal = 1
        var index: Decimal = 0
        while true {
            index += 1
            term = term * reduced / index
            if term.isZero || magnitude(of: term) < -40 { break }
            sum += term
        }
        for _ in 0..<8 {
            sum *= sum
        }
        let result = sum * pow(Decimal(2), twos)
        return result.isNaN || result.isZero ? nil : result
    }

    /// The value as an Int when it is a whole number that fits, else nil.
    private static func integerValue(of value: Decimal) -> Int? {
        guard let whole = nearestInteger(value), Decimal(whole) == value else {
            return nil
        }
        return whole
    }

    /// The value rounded to the nearest Int, or nil if it does not fit.
    private static func nearestInteger(_ value: Decimal) -> Int? {
        var source = value
        var whole = Decimal()
        NSDecimalRound(&whole, &source, 0, .plain)
        guard whole.magnitude < 1e18 else { return nil }
        return NSDecimalNumber(decimal: whole).intValue
    }
}
