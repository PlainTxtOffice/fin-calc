package com.plaintxtoffice.fincalc.domains.calc

import java.math.BigDecimal

/** Evaluate bounded token lists; unary minus binds tighter than right-associative powers. */
object Evaluator {
    fun evaluate(tokens: List<String>): BigDecimal {
        if (tokens.isEmpty()) throw EvaluationError("Empty expression")
        if (tokens.size > 128 || tokens.sumOf { it.length } > 2048) {
            throw EvaluationError("Expression is too long")
        }
        try {
            val parser = Parser(tokens)
            val result = parser.expression()
            if (parser.peek() != null) throw EvaluationError("Unexpected token after expression")
            return DecimalMath.checked(result)
        } catch (error: ArithmeticException) {
            throw EvaluationError("Result out of range")
        }
    }
}

private class Parser(private val tokens: List<String>) {
    private var position = 0
    private val context = DecimalMath.context
    fun peek(): String? = tokens.getOrNull(position)
    private fun consume(): String = tokens[position++]

    fun expression(): BigDecimal {
        var left = term()
        while (peek() == "+" || peek() == "-") {
            val operator = consume()
            val right = term()
            left = DecimalMath.checked(if (operator == "+") left.add(right, context)
                else left.subtract(right, context))
        }
        return left
    }

    private fun term(): BigDecimal {
        var left = exponent()
        while (peek() == "*" || peek() == "/") {
            val operator = consume()
            val right = exponent()
            if (operator == "/" && right.signum() == 0) throw EvaluationError("Division by zero")
            left = DecimalMath.checked(if (operator == "*") left.multiply(right, context)
                else left.divide(right, context))
        }
        return left
    }

    private fun exponent(): BigDecimal {
        val base = unary()
        if (peek() != "^") return base
        consume()
        return DecimalMath.power(base, exponent())
    }

    private fun unary(): BigDecimal {
        if (peek() != "-") return primary()
        consume()
        return primary().negate(context)
    }

    private fun primary(): BigDecimal {
        val current = peek() ?: throw EvaluationError("Unexpected end of expression")
        if (current == "log") {
            consume()
            if (peek() != "(") throw EvaluationError("Expected '(' after log")
            return DecimalMath.log10(parentheses())
        }
        if (current == "(") return parentheses()
        val raw = consume()
        return try {
            val value = BigDecimal(raw)
            val magnitude = value.precision().toLong() - value.scale() - 1
            if (value.signum() != 0 && magnitude !in -9999L..9999L) throw EvaluationError("Result out of range")
            value
        } catch (error: NumberFormatException) {
            throw EvaluationError("Invalid number: $raw")
        }
    }

    private fun parentheses(): BigDecimal {
        consume()
        val value = expression()
        if (peek() != ")") throw EvaluationError("Mismatched parentheses")
        consume()
        return value
    }
}
