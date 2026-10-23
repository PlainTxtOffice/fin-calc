package com.plaintxtoffice.fincalc.domains.calc

/** Build keypad expressions without merging digits into a reused result. */
class ExpressionBuilder {
    private val tokens = mutableListOf<String>()
    private var resultPending = false
    private var openParens = 0
    fun symbols(): List<String> = tokens.toList()
    fun display(): String = tokens.joinToString(" ")

    fun clear() { tokens.clear(); openParens = 0; resultPending = false }

    fun add(symbol: String): Boolean {
        if (tokens.size >= 128 || display().length >= 2048) return false
        if (resultPending) {
            resultPending = false
            if (symbol in digits || symbol in setOf(".", "(", "log")) {
                if (tokens.size == 1) clear() else return false
            }
        }
        val before = symbols()
        val last = tokens.lastOrNull()
        when {
            symbol in digits || symbol == "." -> addDigit(symbol)
            symbol in operators -> {
                if (last == null || last in operators || last in setOf("(", "log")) {
                    if (symbol == "-" && !isNegation()) tokens.add(symbol)
                } else tokens.add(symbol)
            }
            symbol == "(" || symbol == "log" -> {
                if (!isNumber(last) && last != ")") {
                    tokens.add(symbol)
                    if (symbol == "(") openParens++
                }
            }
            symbol == ")" -> if (openParens > 0 && last != null && last !in operators && last != "(") {
                tokens.add(symbol); openParens--
            }
        }
        return tokens != before
    }

    private fun isNegation(): Boolean = tokens.lastOrNull() == "-" &&
        (tokens.size == 1 || tokens[tokens.lastIndex - 1] in operators + setOf("(", "log"))

    private fun addDigit(symbol: String) {
        val last = tokens.lastOrNull()
        if (symbol == "." && last?.contains('.') == true) return
        if (last == ")" || last == "log") return
        if (isNumber(last) || isNegation()) tokens[tokens.lastIndex] += symbol
        else tokens.add(if (symbol == ".") "0." else symbol)
    }

    fun backspace() {
        resultPending = false
        val last = tokens.lastOrNull() ?: return
        if (last in operators || last in setOf("(", ")", "log") || last.length == 1) {
            tokens.removeAt(tokens.lastIndex)
            if (last == "(") openParens--
            if (last == ")") openParens++
        } else tokens[tokens.lastIndex] = last.dropLast(1)
    }

    fun toggleSign() {
        val last = tokens.lastOrNull() ?: return
        if (last in operators || last in setOf("(", ")", "log")) return
        tokens[tokens.lastIndex] = if (last.startsWith("-")) last.drop(1) else "-$last"
    }

    fun insertResult(result: String) {
        if (isNumber(tokens.lastOrNull())) return
        tokens.add(result)
        resultPending = true
    }

    /** Restore our own saved state across process recreation, including sealed result tokens. */
    fun restore(symbols: List<String>, pending: Boolean) {
        clear()
        if (symbols.size > 128 || symbols.sumOf { it.length } > 2048) return
        tokens.addAll(symbols)
        openParens = symbols.count { it == "(" } - symbols.count { it == ")" }
        resultPending = pending
    }
    fun hasPendingResult(): Boolean = resultPending

    companion object {
        private val digits = ('0'..'9').map { it.toString() }.toSet()
        private val operators = setOf("+", "-", "*", "/", "^")
        private fun isNumber(text: String?): Boolean = text != null && text.toBigDecimalOrNull() != null
    }
}
