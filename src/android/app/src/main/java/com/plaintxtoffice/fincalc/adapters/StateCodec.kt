package com.plaintxtoffice.fincalc.adapters

import com.google.gson.JsonArray
import com.google.gson.JsonElement
import com.google.gson.JsonObject
import com.google.gson.JsonParser
import com.plaintxtoffice.fincalc.config.Settings
import com.plaintxtoffice.fincalc.domains.calc.HistoryEntry
import java.time.Instant

/** One persisted snapshot keeps settings and history consistent after failed writes. */
data class StoredState(val history: List<HistoryEntry> = emptyList(), val settings: Settings = Settings())

/** JSON conversion only; invalid preference fields fall back independently. */
object StateCodec {
    private fun bounded(value: JsonElement?, minimum: Int, maximum: Int): Int? {
        if (value == null || !value.isJsonPrimitive || !value.asJsonPrimitive.isNumber) return null
        val raw = value.toString()
        if (!raw.matches(Regex("[0-9]+"))) return null
        val number = raw.toBigInteger()
        if (number < minimum.toBigInteger()) return null
        return number.min(maximum.toBigInteger()).toInt()
    }

    fun decode(text: String): StoredState {
        if (text.isBlank()) return StoredState()
        val root = JsonParser.parseString(text).asJsonObject
        val preferences = root.getAsJsonObject("settings") ?: JsonObject()
        val cap = preferences.get("max_history_entries")
        val settings = Settings(
            bounded(preferences.get("decimal_places"), 0, 6),
            if (preferences.get("theme")?.toString() == "\"light\"") "light" else "dark",
            if (cap?.isJsonNull == true) null else bounded(cap, 1, 10000) ?: 1000,
        )
        val entries = root.getAsJsonArray("history") ?: JsonArray()
        val history = entries.map { entry ->
            val row = entry.asJsonObject
            HistoryEntry(string(row, "expression"), string(row, "result"),
                Instant.parse(string(row, "timestamp")))
        }
        return StoredState(history, settings)
    }

    private fun string(row: JsonObject, key: String): String {
        val value = row.get(key)
        require(value != null && value.isJsonPrimitive && value.asJsonPrimitive.isString) {
            "History $key must be text"
        }
        return value.asString
    }

    fun encode(state: StoredState): String {
        val settings = JsonObject().apply {
            addProperty("decimal_places", state.settings.decimalPlaces)
            addProperty("theme", state.settings.theme)
            addProperty("max_history_entries", state.settings.maxHistoryEntries)
        }
        val rows = JsonArray()
        state.history.forEach { entry ->
            rows.add(JsonObject().apply {
                addProperty("expression", entry.expression)
                addProperty("result", entry.result)
                addProperty("timestamp", entry.timestamp.toString())
            })
        }
        return JsonObject().apply { add("settings", settings); add("history", rows) }.toString()
    }
}
