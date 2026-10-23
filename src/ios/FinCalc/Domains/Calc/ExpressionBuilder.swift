/// Build a mathematical expression token by token with validation.
///
/// Tracks tokens as a list of strings. Numbers are accumulated as a single
/// token. Operators, parentheses, and functions are individual tokens.
struct ExpressionBuilder: Equatable {
    static let operators: Set<String> = ["+", "-", "*", "/", "^"]
    private static let digits: Set<String> = [
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    ]
    private static let nonNumbers: Set<String> = ["(", ")", "log"]

    private(set) var tokens: [String] = []
    private var openParens = 0
    private var resultPending = false

    /// Append a symbol if it forms a valid sequence.
    ///
    /// - Returns: True if the symbol was accepted, false if rejected.
    @discardableResult
    mutating func addSymbol(_ symbol: String) -> Bool {
        if resultPending && !continueFromResult(symbol) {
            return false
        }
        let before = tokens.count
        let snapshot = tokens.last
        if Self.digits.contains(symbol) || symbol == "." {
            addDigitOrDot(symbol)
        } else if Self.operators.contains(symbol) {
            addOperator(symbol)
        } else if symbol == "(" {
            addOpenParen()
        } else if symbol == ")" {
            addCloseParen()
        } else if symbol == "log" {
            addFunction(symbol)
        } else {
            return false
        }
        return tokens.count != before || snapshot != tokens.last
    }

    /// Remove all tokens.
    mutating func clear() {
        tokens.removeAll()
        openParens = 0
        resultPending = false
    }

    /// Remove the last complete token.
    mutating func clearEntry() {
        resultPending = false
        guard let removed = tokens.popLast() else { return }
        if removed == "(" {
            openParens -= 1
        } else if removed == ")" {
            openParens += 1
        }
    }

    /// Remove the last character of the current number token.
    mutating func backspace() {
        resultPending = false
        guard let last = tokens.last else { return }
        if isOperatorOrNonNumber(last) {
            clearEntry()
        } else if last.count == 1 {
            tokens.removeLast()
        } else {
            tokens[tokens.count - 1] = String(last.dropLast())
        }
    }

    /// Toggle the sign of the current number being entered.
    mutating func toggleSign() {
        guard let last = tokens.last, !isOperatorOrNonNumber(last) else {
            return
        }
        if last.hasPrefix("-") {
            tokens[tokens.count - 1] = String(last.dropFirst())
        } else {
            tokens[tokens.count - 1] = "-" + last
        }
    }

    /// Insert a previous result value as a number token.
    ///
    /// The inserted token is sealed: digits never merge into it. When it is
    /// the only token, a following digit starts a fresh expression.
    mutating func insertResult(_ result: String) {
        if lastIsNumber() { return }
        tokens.append(result)
        resultPending = true
    }

    /// Format the token list for display.
    func toDisplay() -> String {
        var parts: [String] = []
        for (index, symbol) in tokens.enumerated() {
            if index > 0
                && !(Self.isNumber(tokens[index - 1]) && Self.isNumber(symbol))
            {
                parts.append(" ")
            }
            parts.append(symbol)
        }
        return parts.joined()
    }

    /// Resolve a pending result token before accepting `symbol`.
    ///
    /// - Returns: True if `addSymbol` should proceed, false to reject.
    private mutating func continueFromResult(_ symbol: String) -> Bool {
        resultPending = false
        let startsOperand =
            Self.digits.contains(symbol) || [".", "(", "log"].contains(symbol)
        guard startsOperand else { return true }
        if tokens.count == 1 {
            clear()
            return true
        }
        return false
    }

    private mutating func addDigitOrDot(_ char: String) {
        if char == ".", let last = tokens.last, last.contains(".") { return }
        if let last = tokens.last, last == ")" || last == "log" { return }
        if lastIsNumber() || isNegation() {
            tokens[tokens.count - 1] += char
        } else if char == "." {
            tokens.append("0.")
        } else {
            tokens.append(char)
        }
    }

    /// Check if the trailing lone "-" is a negation prefix.
    private func isNegation() -> Bool {
        guard tokens.last == "-" else { return false }
        if tokens.count == 1 { return true }
        let previous = tokens[tokens.count - 2]
        return Self.operators.contains(previous)
            || previous == "(" || previous == "log"
    }

    private mutating func addOperator(_ op: String) {
        guard let last = tokens.last else {
            if op == "-" { tokens.append("-") }
            return
        }
        if last == "-" && isNegation() { return }
        if Self.operators.contains(last) || last == "(" || last == "log" {
            if op == "-" { tokens.append("-") }
            return
        }
        tokens.append(op)
    }

    private mutating func addOpenParen() {
        if lastIsNumber() || tokens.last == ")" { return }
        tokens.append("(")
        openParens += 1
    }

    private mutating func addCloseParen() {
        guard openParens > 0, let last = tokens.last else { return }
        if Self.operators.contains(last) || last == "(" { return }
        tokens.append(")")
        openParens -= 1
    }

    private mutating func addFunction(_ name: String) {
        if lastIsNumber() || tokens.last == ")" { return }
        tokens.append(name)
    }

    private func lastIsNumber() -> Bool {
        guard let last = tokens.last else { return false }
        return Self.isNumber(last)
    }

    private func isOperatorOrNonNumber(_ token: String) -> Bool {
        Self.operators.contains(token) || Self.nonNumbers.contains(token)
    }

    private static func isNumber(_ value: String) -> Bool {
        DecimalMath.parseNumber(value) != nil
    }
}
