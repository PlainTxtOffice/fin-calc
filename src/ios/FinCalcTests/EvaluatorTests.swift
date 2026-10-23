import Foundation
import Testing

@testable import FinCalc

private func decimal(_ text: String) -> Decimal {
    Decimal(string: text, locale: Locale(identifier: "en_US_POSIX"))!
}

private func evaluate(_ tokens: [String]) throws -> Decimal {
    try Evaluator.evaluate(tokens)
}

@Suite("Evaluator arithmetic")
struct EvaluatorArithmeticTests {
    @Test(arguments: [
        (["3", "+", "2"], "5"),
        (["10", "-", "4"], "6"),
        (["3", "*", "7"], "21"),
        (["15", "/", "4"], "3.75"),
        (["42"], "42"),
        (["-5", "+", "3"], "-2"),
        (["0.1", "+", "0.2"], "0.3"),
    ])
    func arithmetic(tokens: [String], expected: String) throws {
        #expect(try evaluate(tokens) == decimal(expected))
    }

    @Test func divisionRoundsTo28SignificantDigits() throws {
        // Matches Python: Decimal(1) / Decimal(3).
        let result = try evaluate(["1", "/", "3"])
        #expect(result.description == "0.3333333333333333333333333333")
    }
}

@Suite("Evaluator precedence and grouping")
struct EvaluatorPrecedenceTests {
    @Test(arguments: [
        (["2", "+", "3", "*", "4"], "14"),
        (["10", "-", "6", "/", "2"], "7"),
        (["2", "^", "3", "*", "4"], "32"),
        (["10", "-", "3", "-", "2"], "5"),
        (["(", "2", "+", "3", ")", "*", "4"], "20"),
        (["(", "(", "1", "+", "2", ")", "*", "3", ")"], "9"),
        (["(", "2", "+", "1", ")", "^", "2"], "9"),
        (["-2", "^", "2"], "4"),
        (["-", "(", "2", ")", "^", "2"], "4"),
        (["2", "^", "3", "^", "2"], "512"),
    ])
    func precedence(tokens: [String], expected: String) throws {
        #expect(try evaluate(tokens) == decimal(expected))
    }
}

@Suite("Evaluator functions and powers")
struct EvaluatorFunctionTests {
    @Test(arguments: [
        (["log", "(", "10", ")"], "1"),
        (["log", "(", "100", ")"], "2"),
        (["log", "(", "1", ")"], "0"),
        (["log", "(", "100", ")", "+", "3"], "5"),
        (["log", "(", "0.001", ")"], "-3"),
        (["2", "^", "10"], "1024"),
        (["5", "^", "0"], "1"),
        (["7", "^", "1"], "7"),
        (["2", "^", "-1"], "0.5"),
        (["0", "^", "0.5"], "0"),
    ])
    func exact(tokens: [String], expected: String) throws {
        #expect(try evaluate(tokens) == decimal(expected))
    }

    // Reference values from Python's decimal module at 28 digits.
    @Test(arguments: [
        (["log", "(", "2", ")"], "0.3010299956639811952137388947"),
        (["log", "(", "7", ")"], "0.8450980400142568307122162583"),
        (["2", "^", "0.5"], "1.414213562373095048801688724"),
        (["10", "^", "0.25"], "1.778279410038922801225421195"),
        (["-8", "^", "3"], "-512"),
    ])
    func matchesPython(tokens: [String], expected: String) throws {
        // The last of 28 digits may differ by rounding; compare to 26.
        let result = DecimalMath.roundToPrecision(
            try evaluate(tokens),
            digits: 26,
        )
        let reference = DecimalMath.roundToPrecision(
            decimal(expected),
            digits: 26,
        )
        #expect(result == reference)
    }
}

@Suite("Evaluator errors")
struct EvaluatorErrorTests {
    @Test(arguments: [
        (["5", "/", "0"], "Division by zero"),
        (["log", "(", "0", ")"], "Log undefined for non-positive values"),
        (["log", "(", "-5", ")"], "Log undefined for non-positive values"),
        ([], "Empty expression"),
        (["(", "3", "+", "2"], "Mismatched parentheses"),
        (["9", "^", "9999999"], "Result out of range"),
        (["0", "^", "-1"], "Result out of range"),
        (["0", "^", "0"], "Invalid exponentiation: 0 ^ 0"),
        (["-8", "^", "0.5"], "Invalid exponentiation: -8 ^ 0.5"),
        (["9", "^", "999", "*", "9", "^", "999"], "Result out of range"),
        (["-"], "Unexpected end of expression"),
        (["12abc"], "Invalid number: 12abc"),
        (["2", "3"], "Unexpected token after expression"),
    ])
    func error(tokens: [String], message: String) {
        #expect(throws: EvaluationError(message)) {
            try evaluate(tokens)
        }
    }
}
