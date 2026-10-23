package com.plaintxtoffice.fincalc.ui

import android.content.Context
import android.graphics.Color
import android.graphics.drawable.GradientDrawable

/** Colors shared by calculator views; the preference belongs to the configuration model. */
data class ThemeColors(val background: Int, val surface: Int, val key: Int, val text: Int, val accent: Int) {
    companion object {
        fun forName(name: String): ThemeColors = if (name == "light") ThemeColors(
            Color.rgb(242, 245, 249), Color.WHITE, Color.rgb(224, 231, 240),
            Color.rgb(24, 34, 49), Color.rgb(0, 105, 160),
        ) else ThemeColors(Color.rgb(25, 29, 35), Color.rgb(34, 40, 49), Color.rgb(48, 57, 69),
            Color.rgb(239, 244, 250), Color.rgb(129, 212, 250))
    }
}

fun Context.dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()
fun rounded(color: Int, radius: Float = 18f): GradientDrawable = GradientDrawable().apply {
    setColor(color); cornerRadius = radius
}
