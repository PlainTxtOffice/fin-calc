package com.plaintxtoffice.fincalc.application

import com.plaintxtoffice.fincalc.adapters.StoredState
import com.plaintxtoffice.fincalc.config.Settings
import com.plaintxtoffice.fincalc.domains.calc.*
import java.time.Instant

/** Coordinate input and persistence; failed writes leave history and preferences unchanged. */
class CalculatorSession(initial: StoredState, private val save: (StoredState) -> Unit) {
    val builder = ExpressionBuilder()
    var state = initial.copy(history = trimHistory(initial.history, initial.settings.maxHistoryEntries))
        private set
    var status = ""
        private set

    fun press(key: String) {
        status = ""
        when (key) {
            "C" -> builder.clear()
            "backspace" -> builder.backspace()
            "sign" -> builder.toggleSign()
            "=" -> calculate()
            else -> if (!builder.add(key)) status = "Invalid input: $key"
        }
    }

    private fun calculate() {
        if (builder.symbols().isEmpty()) return
        val result = Evaluator.evaluate(builder.symbols()).stripTrailingZeros().toString()
        val entry = HistoryEntry(builder.display(), result, Instant.now())
        commit(state.copy(history = trimHistory(state.history + entry, state.settings.maxHistoryEntries)))
        builder.clear()
        builder.insertResult(result)
    }

    fun reuse(entry: HistoryEntry) { builder.insertResult(entry.result); status = "" }
    fun clearHistory() { commit(state.copy(history = emptyList())) }
    fun updateSettings(settings: Settings) {
        require(settings.decimalPlaces == null || settings.decimalPlaces in 0..6)
        require(settings.maxHistoryEntries == null || settings.maxHistoryEntries in 1..10000)
        require(settings.theme in setOf("dark", "light"))
        commit(state.copy(settings = settings, history = trimHistory(state.history, settings.maxHistoryEntries)))
    }
    private fun commit(updated: StoredState) { save(updated); state = updated }
}
