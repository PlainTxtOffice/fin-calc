package com.plaintxtoffice.fincalc.adapters

import com.plaintxtoffice.fincalc.domains.calc.HistoryEntry
import java.io.Writer

/** Write full precision CSV with the same columns as the other platform ports. */
object HistoryExport {
    private fun cell(value: String): String = if (value.any { it in ",\"\n\r" })
        "\"${value.replace("\"", "\"\"")}\"" else value

    fun write(entries: List<HistoryEntry>, writer: Writer) {
        writer.write("timestamp,expression,result\n")
        entries.forEach {
            writer.write(listOf(it.timestamp.toString(), it.expression, it.result).joinToString(",", transform = ::cell))
            writer.write("\n")
        }
    }
}
