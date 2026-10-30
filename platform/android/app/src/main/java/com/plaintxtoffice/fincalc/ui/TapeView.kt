package com.plaintxtoffice.fincalc.ui

import android.content.Context
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.plaintxtoffice.fincalc.domains.calc.HistoryEntry
import com.plaintxtoffice.fincalc.domains.calc.formatResult

/** Recycle tape rows so large histories do not create thousands of views. */
class TapeView(context: Context, private val colors: ThemeColors, private val reuse: (HistoryEntry) -> Unit) : RecyclerView(context) {
    private var entries: List<HistoryEntry> = emptyList()
    private var places: Int? = null
    private val rows = Rows()
    init {
        layoutManager = LinearLayoutManager(context).apply { stackFromEnd = true }
        adapter = rows
        background = rounded(colors.surface)
        contentDescription = "Calculation history. Tap a result to reuse it."
    }

    fun showHistory(history: List<HistoryEntry>, decimalPlaces: Int?) {
        if (history == entries && decimalPlaces == places) return
        val added = history != entries
        entries = history
        places = decimalPlaces
        rows.notifyDataSetChanged()
        if (added && entries.isNotEmpty()) scrollToPosition(entries.lastIndex)
    }

    private class Row(val label: TextView) : ViewHolder(label)
    private inner class Rows : Adapter<Row>() {
        override fun getItemCount(): Int = entries.size
        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): Row = Row(TextView(context).apply {
            layoutParams = LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT)
            minHeight = context.dp(48)
            textSize = 17f
            setTextColor(colors.text)
            setPadding(context.dp(12), context.dp(10), context.dp(12), context.dp(10))
        })
        override fun onBindViewHolder(holder: Row, position: Int) {
            val entry = entries[position]
            holder.label.text = "${entry.expression} = ${formatResult(entry.result, places)}"
            holder.label.setOnClickListener { reuse(entry) }
        }
    }
}
