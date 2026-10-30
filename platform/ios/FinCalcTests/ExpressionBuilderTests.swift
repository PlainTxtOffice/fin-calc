import Testing

@testable import FinCalc

/// Build an expression from symbols and return its display string.
private func displayOf(_ symbols: [String]) -> String {
    var builder = ExpressionBuilder()
    for symbol in symbols {
        builder.addSymbol(symbol)
    }
    return builder.toDisplay()
}

@Suite("Expression builder input")
struct ExpressionBuilderInputTests {
    @Test(arguments: [
        ([], ""),
        (["5"], "5"),
        (["1", "2", "3"], "123"),
        (["3", ".", "1", "4"], "3.14"),
        (["5", "+", "3"], "5 + 3"),
        (["5", "-", "3"], "5 - 3"),
        (["+"], ""),
        (["*"], ""),
        (["5", "+", "*"], "5 +"),
        (["3", ".", "."], "3."),
        (["."], "0."),
        (["-", "5"], "-5"),
        (["5", "+", "-", "3"], "5 + -3"),
        (["(", "-", "5", ")"], "( -5 )"),
        (["(", "3", "+", "2", ")"], "( 3 + 2 )"),
        (["(", "(", "1", "+", "2", ")", "*", "3", ")"], "( ( 1 + 2 ) * 3 )"),
        (["5", ")"], "5"),
        (["log", "(", "1", "0", ")"], "log ( 10 )"),
        (["2", "^", "3"], "2 ^ 3"),
    ])
    func displays(symbols: [String], expected: String) {
        #expect(displayOf(symbols) == expected)
    }

    @Test(arguments: [
        (["(", "1", ")"], "2"),
        (["(", "1", ")"], "("),
        (["log"], "1"),
        (["5"], "sqrt"),
    ])
    func rejects(prefix: [String], symbol: String) {
        var builder = ExpressionBuilder()
        for token in prefix {
            builder.addSymbol(token)
        }
        let before = builder.toDisplay()
        let accepted = builder.addSymbol(symbol)
        #expect(accepted == false)
        #expect(builder.toDisplay() == before)
    }
}

@Suite("Expression builder editing")
struct ExpressionBuilderEditingTests {
    @Test func clearRemovesEverything() {
        var builder = ExpressionBuilder()
        builder.addSymbol("5")
        builder.addSymbol("+")
        builder.clear()
        #expect(builder.tokens.isEmpty)
        #expect(builder.toDisplay() == "")
    }

    @Test func clearEntryRemovesLastToken() {
        var builder = ExpressionBuilder()
        ["5", "+", "3"].forEach { builder.addSymbol($0) }
        builder.clearEntry()
        #expect(builder.toDisplay() == "5 +")
    }

    @Test func backspaceRemovesLastDigit() {
        var builder = ExpressionBuilder()
        ["1", "2"].forEach { builder.addSymbol($0) }
        builder.backspace()
        #expect(builder.toDisplay() == "1")
    }

    @Test func backspaceOnEmptyDoesNothing() {
        var builder = ExpressionBuilder()
        builder.backspace()
        #expect(builder.toDisplay() == "")
    }

    @Test func backspaceRemovesCloseParenAndReopensGroup() {
        var builder = ExpressionBuilder()
        ["(", "1", ")"].forEach { builder.addSymbol($0) }
        builder.backspace()
        let accepted = builder.addSymbol(")")
        #expect(accepted)
        #expect(builder.toDisplay() == "( 1 )")
    }

    @Test(arguments: [
        (["5"], "-5"),
        (["-", "5"], "5"),
        ([], ""),
        (["5", "+"], "5 +"),
    ])
    func toggleSign(symbols: [String], expected: String) {
        var builder = ExpressionBuilder()
        symbols.forEach { builder.addSymbol($0) }
        builder.toggleSign()
        #expect(builder.toDisplay() == expected)
    }
}

@Suite("Expression builder results")
struct ExpressionBuilderResultTests {
    @Test func insertIntoEmpty() {
        var builder = ExpressionBuilder()
        builder.insertResult("42")
        #expect(builder.toDisplay() == "42")
    }

    @Test func insertAfterOperator() {
        var builder = ExpressionBuilder()
        ["5", "+"].forEach { builder.addSymbol($0) }
        builder.insertResult("10")
        #expect(builder.toDisplay() == "5 + 10")
    }

    @Test(arguments: [
        ("3", "3"),
        (".", "0."),
        ("(", "("),
        ("log", "log"),
        ("+", "5 +"),
    ])
    func symbolAfterResult(symbol: String, expected: String) {
        var builder = ExpressionBuilder()
        builder.insertResult("5")
        builder.addSymbol(symbol)
        #expect(builder.toDisplay() == expected)
    }

    @Test func secondInsertAfterScientificResultIsBlocked() {
        var builder = ExpressionBuilder()
        builder.insertResult("1E-30")
        builder.insertResult("42")
        #expect(builder.tokens == ["1E-30"])
    }

    @Test func scientificResultSpacing() {
        var builder = ExpressionBuilder()
        builder.insertResult("1E-30")
        ["+", "2"].forEach { builder.addSymbol($0) }
        #expect(builder.toDisplay() == "1E-30 + 2")
    }

    @Test func toggleSignOnScientificResult() {
        var builder = ExpressionBuilder()
        builder.insertResult("1E-30")
        builder.toggleSign()
        #expect(builder.toDisplay() == "-1E-30")
    }

    @Test func digitNeverMergesIntoMidExpressionResult() {
        var builder = ExpressionBuilder()
        ["5", "+"].forEach { builder.addSymbol($0) }
        builder.insertResult("10")
        let accepted = builder.addSymbol("3")
        #expect(accepted == false)
        #expect(builder.toDisplay() == "5 + 10")
    }
}
