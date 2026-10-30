import Foundation

/// Recursive descent evaluator over Decimal values.
///
/// Precedence (low to high):
///     addition / subtraction
///     multiplication / division
///     exponentiation (right-associative)
///     unary minus
///     functions (log)
///     parentheses
///
/// Unary minus deliberately binds tighter than `^` (Excel-style), so
/// `-2 ^ 2` means `(-2) ^ 2 = 4`. This matches the expression builder,
/// which folds a negation sign into the number token itself.
enum Evaluator {
    /// Evaluate a token list from `ExpressionBuilder.tokens`.
    ///
    /// - Throws: `EvaluationError` on invalid expressions, division by
    ///   zero, log domain errors, or results outside Decimal range.
    static func evaluate(_ tokens: [String]) throws -> Decimal {
        guard !tokens.isEmpty else {
            throw EvaluationError("Empty expression")
        }
        var parser = Parser(tokens: tokens)
        let result = try parser.parseExpression()
        if parser.position < tokens.count {
            throw EvaluationError("Unexpected token after expression")
        }
        return result
    }
}

private struct Parser {
    let tokens: [String]
    var position = 0

    init(tokens: [String]) {
        self.tokens = tokens
    }

    private func peek() -> String? {
        position < tokens.count ? tokens[position] : nil
    }

    private mutating func consume() -> String {
        defer { position += 1 }
        return tokens[position]
    }

    /// Parse addition and subtraction (lowest precedence).
    mutating func parseExpression() throws -> Decimal {
        var left = try parseTerm()
        while let op = peek(), op == "+" || op == "-" {
            _ = consume()
            let right = try parseTerm()
            left = try round(op == "+" ? left + right : left - right)
        }
        return left
    }

    /// Parse multiplication and division.
    private mutating func parseTerm() throws -> Decimal {
        var left = try parseExponent()
        while let op = peek(), op == "*" || op == "/" {
            _ = consume()
            let right = try parseExponent()
            if op == "*" {
                left = try round(left * right)
            } else {
                if right.isZero {
                    throw EvaluationError("Division by zero")
                }
                left = try round(left / right)
            }
        }
        return left
    }

    /// Parse exponentiation (right-associative).
    private mutating func parseExponent() throws -> Decimal {
        let base = try parseUnary()
        guard peek() == "^" else { return base }
        _ = consume()
        let exponent = try parseExponent()
        return try round(DecimalMath.power(base, exponent))
    }

    /// Parse unary minus.
    private mutating func parseUnary() throws -> Decimal {
        if peek() == "-" {
            _ = consume()
            return try -parsePrimary()
        }
        return try parsePrimary()
    }

    /// Parse numbers, parenthesised expressions, and functions.
    private mutating func parsePrimary() throws -> Decimal {
        guard let current = peek() else {
            throw EvaluationError("Unexpected end of expression")
        }
        if current == "log" {
            return try parseLog()
        }
        if current == "(" {
            _ = consume()
            let result = try parseExpression()
            guard peek() == ")" else {
                throw EvaluationError("Mismatched parentheses")
            }
            _ = consume()
            return result
        }
        return try parseNumber()
    }

    /// Parse log(expression) as base-10 logarithm.
    private mutating func parseLog() throws -> Decimal {
        _ = consume()  // consume "log"
        guard peek() == "(" else {
            throw EvaluationError("Expected '(' after log")
        }
        _ = consume()  // consume "("
        let value = try parseExpression()
        guard peek() == ")" else {
            throw EvaluationError("Mismatched parentheses in log")
        }
        _ = consume()  // consume ")"
        guard value > 0 else {
            throw EvaluationError("Log undefined for non-positive values")
        }
        return DecimalMath.log10(value)
    }

    /// Parse a numeric literal.
    private mutating func parseNumber() throws -> Decimal {
        let raw = consume()
        guard let value = DecimalMath.parseNumber(raw) else {
            throw EvaluationError("Invalid number: \(raw)")
        }
        return value
    }

    /// Reject overflow, then round to the shared 28-digit precision.
    private func round(_ value: Decimal) throws -> Decimal {
        DecimalMath.roundToPrecision(try DecimalMath.checked(value))
    }
}
