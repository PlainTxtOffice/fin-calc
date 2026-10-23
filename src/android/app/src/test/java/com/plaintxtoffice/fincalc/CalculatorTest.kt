package com.plaintxtoffice.fincalc

import com.google.gson.JsonParser
import com.plaintxtoffice.fincalc.adapters.StoredState
import com.plaintxtoffice.fincalc.application.CalculatorSession
import com.plaintxtoffice.fincalc.config.Settings
import com.plaintxtoffice.fincalc.domains.calc.*
import org.junit.Assert.*
import org.junit.Test
import java.io.IOException
import java.math.BigDecimal

class CalculatorTest {
    @Test fun pythonReferenceCalculations() {
        val json = javaClass.getResource("/python-reference.json")!!.readText()
        JsonParser.parseString(json).asJsonArray.forEach { raw ->
            val row = raw.asJsonObject
            val tokens = row.getAsJsonArray("tokens").map { it.asString }
            val expected = BigDecimal(row.get("result").asString)
            val actual = Evaluator.evaluate(tokens)
            // Transcendental implementations may differ in their final rounded digit.
            val tolerance = expected.abs().max(BigDecimal.ONE).multiply(BigDecimal("2E-27"))
            assertTrue("$tokens: expected $expected, got $actual", actual.subtract(expected).abs() <= tolerance)
        }
    }

    @Test fun exactDecimalAndPrecedence() {
        assertEquals(0, Evaluator.evaluate(listOf("0.1", "+", "0.2")).compareTo(BigDecimal("0.3")))
        assertEquals(0, Evaluator.evaluate(listOf("-", "2", "^", "2")).compareTo(BigDecimal("4")))
        assertEquals(0, Evaluator.evaluate(listOf("2", "^", "3", "^", "2")).compareTo(BigDecimal("512")))
        assertEquals(0, Evaluator.evaluate(listOf("12345678901234567890123456789", "-", "12345678901234567890123456788")).compareTo(BigDecimal.ONE))
    }

    @Test fun invalidAndBoundedInput() {
        listOf(emptyList(), listOf("1", "/", "0"), listOf("log", "(", "0", ")"),
            listOf("(", "2"), listOf("0", "^", "0"), listOf("0", "^", "-1"),
            listOf("-2", "^", "0.5"), listOf("9", "^", "9999999"), listOf("NaN"),
            listOf("1", "2"), List(129) { "(" }).forEach { tokens ->
            assertThrows("$tokens", EvaluationError::class.java) { Evaluator.evaluate(tokens) }
        }
    }

    @Test fun resultReuseAndFreshDigits() {
        val session = CalculatorSession(StoredState()) {}
        listOf("1", "/", "3", "=").forEach(session::press)
        val result = session.state.history.single()
        session.press("C"); session.press("2"); session.press("*"); session.reuse(result)
        session.press("=")
        assertEquals("0.6666666666666666666666666666", session.state.history.last().result)
        session.press("7")
        assertEquals("7", session.builder.display())
    }

    @Test fun failedSaveKeepsCalculationAndHistory() {
        val session = CalculatorSession(StoredState()) { throw IOException("disk full") }
        listOf("2", "+", "3").forEach(session::press)
        assertThrows(IOException::class.java) { session.press("=") }
        assertEquals("2 + 3", session.builder.display())
        assertTrue(session.state.history.isEmpty())
        assertThrows(IOException::class.java) { session.updateSettings(Settings(theme = "light")) }
        assertEquals("dark", session.state.settings.theme)
    }

    @Test fun historyCapAndRounding() {
        val session = CalculatorSession(StoredState(settings = Settings(maxHistoryEntries = 2))) {}
        listOf("1", "2", "3").forEach { session.press(it); session.press("=") }
        assertEquals(listOf("2", "3"), session.state.history.map { it.result })
        session.updateSettings(Settings(maxHistoryEntries = 1))
        assertEquals("3", session.state.history.single().result)
        session.updateSettings(Settings(maxHistoryEntries = null))
        session.press("4"); session.press("=")
        assertEquals(2, session.state.history.size)
        assertEquals("1.24", formatResult("1.245", 2))
        assertEquals("1.26", formatResult("1.255", 2))
        assertEquals("1.255", formatResult("1.255", null))
        session.clearHistory()
        assertTrue(session.state.history.isEmpty())
    }

    @Test fun builderRestoresPendingResultAndParentheses() {
        val builder = ExpressionBuilder()
        builder.add("("); builder.add("2")
        val restored = ExpressionBuilder()
        restored.restore(builder.symbols(), builder.hasPendingResult())
        assertTrue(restored.add(")"))
        restored.clear(); restored.insertResult("1E+5")
        assertTrue(restored.add("7"))
        assertEquals(listOf("7"), restored.symbols())
        restored.toggleSign(); restored.backspace()
        assertTrue(restored.add("2"))
        assertEquals(listOf("-2"), restored.symbols())
    }
}
