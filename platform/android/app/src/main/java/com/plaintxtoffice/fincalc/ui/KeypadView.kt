package com.plaintxtoffice.fincalc.ui

import android.content.Context
import android.view.Gravity
import android.widget.Button
import android.widget.GridLayout

/** Adding-machine keypad; forwards actions without evaluating expressions. */
class KeypadView(context: Context, colors: ThemeColors, onKey: (String) -> Unit) : GridLayout(context) {
    init {
        columnCount = 5
        rowCount = 5
        val rows = listOf(
            listOf("log", "(", ")", "C"), listOf("7", "8", "9", "/"),
            listOf("4", "5", "6", "*"), listOf("1", "2", "3", "-"),
            listOf("0", ".", "sign", "+"),
        )
        rows.forEachIndexed { row, keys -> keys.forEachIndexed { col, key ->
            addKey(key, row, col, 1, colors, onKey)
        } }
        addKey("backspace", 0, 4, 1, colors, onKey)
        addKey("^", 1, 4, 1, colors, onKey)
        addKey("=", 2, 4, 3, colors, onKey)
    }

    private fun addKey(key: String, row: Int, col: Int, span: Int, colors: ThemeColors, onKey: (String) -> Unit) {
        val labels = mapOf("*" to "×", "/" to "÷", "sign" to "±", "backspace" to "⌫")
        val descriptions = mapOf("*" to "Multiply", "/" to "Divide", "sign" to "Change sign",
            "backspace" to "Delete", "C" to "Clear", "=" to "Equals", "^" to "Power", "log" to "Log base 10")
        val button = Button(context).apply {
            text = labels[key] ?: key
            contentDescription = descriptions[key] ?: key
            textSize = 22f
            isAllCaps = false
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 0)
            minimumWidth = 0; minimumHeight = 0
            setTextColor(if (key == "=") colors.background else colors.text)
            background = rounded(if (key == "=") colors.accent else colors.key)
            setOnClickListener { onKey(key) }
        }
        addView(button, LayoutParams(spec(row, span, span.toFloat()), spec(col, 1f)).apply {
            width = 0; height = 0; setMargins(context.dp(3), context.dp(3), context.dp(3), context.dp(3))
        })
    }
}
