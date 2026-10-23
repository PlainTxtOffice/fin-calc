package com.plaintxtoffice.fincalc.ui

import android.content.Context
import android.content.res.Configuration
import android.view.Gravity
import android.widget.LinearLayout
import android.widget.TextView
import com.plaintxtoffice.fincalc.application.ScreenState
import com.plaintxtoffice.fincalc.domains.calc.HistoryEntry

/** Render a vertical phone layout or a side-by-side landscape layout. */
class CalculatorView(context: Context, colors: ThemeColors, onKey: (String) -> Unit, reuse: (HistoryEntry) -> Unit) : LinearLayout(context) {
    private val tape = TapeView(context, colors, reuse)
    private val display = TextView(context).apply {
        textSize = 28f; gravity = Gravity.END or Gravity.CENTER_VERTICAL
        setTextColor(colors.text); background = rounded(colors.surface)
        setPadding(context.dp(12), context.dp(8), context.dp(12), context.dp(8))
        setTextIsSelectable(true)
    }
    private val status = TextView(context).apply {
        textSize = 14f; setTextColor(colors.accent)
        accessibilityLiveRegion = ACCESSIBILITY_LIVE_REGION_POLITE
        minHeight = context.dp(24)
    }
    init {
        val landscape = resources.configuration.orientation == Configuration.ORIENTATION_LANDSCAPE
        orientation = if (landscape) HORIZONTAL else VERTICAL
        val controls = LinearLayout(context).apply { orientation = VERTICAL }
        if (landscape) {
            addView(tape, LayoutParams(0, LayoutParams.MATCH_PARENT, 1f))
            addView(controls, LayoutParams(0, LayoutParams.MATCH_PARENT, 1.3f).apply { leftMargin = context.dp(8) })
        } else {
            addView(tape, LayoutParams(LayoutParams.MATCH_PARENT, 0, 1f))
            addView(controls, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT))
        }
        controls.addView(display, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT))
        controls.addView(status, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT))
        controls.addView(KeypadView(context, colors, onKey),
            if (landscape) LayoutParams(LayoutParams.MATCH_PARENT, 0, 1f)
            else LayoutParams(LayoutParams.MATCH_PARENT, context.dp(300)))
    }

    fun render(state: ScreenState) {
        display.text = state.expression.ifEmpty { "0" }
        status.text = state.status
        tape.showHistory(state.stored.history, state.stored.settings.decimalPlaces)
    }
}
