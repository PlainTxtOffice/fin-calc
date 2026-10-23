package com.plaintxtoffice.fincalc

import com.plaintxtoffice.fincalc.adapters.*
import com.plaintxtoffice.fincalc.config.Settings
import com.plaintxtoffice.fincalc.domains.calc.HistoryEntry
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.io.StringWriter
import java.time.Instant

class StorageTest {
    @get:Rule val temporary = TemporaryFolder()
    private val entry = HistoryEntry("1 / 3", "0.3333333333333333333333333333", Instant.parse("2026-10-23T12:00:00Z"))

    @Test fun restartPreservesPrecisionAndSettings() {
        val file = File(temporary.root, "calculator.json")
        val saved = StoredState(listOf(entry), Settings(2, "light", null))
        StateStore(file).save(saved)
        assertEquals(saved, StateStore(file).load())
        assertFalse(File(temporary.root, "calculator.json.tmp").exists())
    }

    @Test fun missingAndInvalidFiles() {
        val file = File(temporary.root, "calculator.json")
        assertEquals(StoredState(), StateStore(file).load())
        file.writeText("{invalid")
        assertThrows(Exception::class.java) { StateStore(file).load() }
        file.writeText(" ")
        assertEquals(StoredState(), StateStore(file).load())
        assertThrows(Exception::class.java) { StateCodec.decode("""{"history":[{"result":false}]}""") }
    }

    @Test fun defensivePreferenceParsing() {
        assertEquals(Settings(), StateCodec.decode("""{"settings":{"decimal_places":true,"theme":7,"max_history_entries":0}}""").settings)
        assertEquals(Settings(6, "light", 10000), StateCodec.decode("""{"settings":{"decimal_places":12,"theme":"light","max_history_entries":99999}}""").settings)
        assertNull(StateCodec.decode("""{"settings":{"max_history_entries":null}}""").settings.maxHistoryEntries)
        assertEquals(1000, StateCodec.decode("""{"settings":{"max_history_entries":"12"}}""").settings.maxHistoryEntries)
    }

    @Test fun csvQuotesFieldsAndKeepsPrecision() {
        val text = StringWriter()
        HistoryExport.write(listOf(entry.copy(expression = "a,\"b\"\n")), text)
        assertEquals("timestamp,expression,result\n2026-10-23T12:00:00Z,\"a,\"\"b\"\"\n\",0.3333333333333333333333333333\n", text.toString())
    }
}
