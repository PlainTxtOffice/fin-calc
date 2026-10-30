package com.plaintxtoffice.fincalc.ui

import android.app.AlertDialog
import android.content.Context
import android.text.InputType
import android.widget.*
import com.plaintxtoffice.fincalc.config.Settings
import com.plaintxtoffice.fincalc.domains.calc.DecimalMath

/** Edit only presentation preferences and the history retention cap. */
fun showSettings(context: Context, settings: Settings, save: (Settings) -> Unit) {
    val form = LinearLayout(context).apply {
        orientation = LinearLayout.VERTICAL
        setPadding(context.dp(20), context.dp(8), context.dp(20), 0)
    }
    fun choices(label: String, options: List<String>, selection: Int): Spinner {
        form.addView(TextView(context).apply { text = label })
        return Spinner(context).apply {
            adapter = ArrayAdapter(context, android.R.layout.simple_spinner_dropdown_item, options)
            contentDescription = label
            setSelection(selection)
            form.addView(this)
        }
    }
    form.addView(TextView(context).apply {
        text = "Calculations and stored results: ${DecimalMath.context.precision} significant digits"
    })
    form.addView(TextView(context).apply {
        text = "Significant digits count across the whole number. " +
            "Saved results retain calculation precision when reused."
        setPadding(0, context.dp(4), 0, context.dp(16))
    })
    val places = choices("Decimal places shown", listOf("All stored digits") + (0..6).map { "$it" },
        settings.decimalPlaces?.plus(1) ?: 0)
    form.addView(TextView(context).apply {
        text = "Applies to results shown in the calculator and history. " +
            "Display rounding does not change saved results or later calculations."
        setPadding(0, context.dp(4), 0, context.dp(16))
    })
    val theme = choices("Theme", listOf("Dark", "Light"), if (settings.theme == "light") 1 else 0)
    val unlimited = Switch(context).apply { text = "Unlimited history"; isChecked = settings.maxHistoryEntries == null }
    form.addView(unlimited)
    form.addView(TextView(context).apply { text = "Maximum history entries (1–10,000)" })
    val cap = EditText(context).apply {
        inputType = InputType.TYPE_CLASS_NUMBER
        contentDescription = "Maximum history entries"
        setText((settings.maxHistoryEntries ?: 1000).toString())
        isEnabled = !unlimited.isChecked
    }
    form.addView(cap)
    unlimited.setOnCheckedChangeListener { _, checked -> cap.isEnabled = !checked }
    val scroll = ScrollView(context).apply { addView(form) }
    val dialog = AlertDialog.Builder(context).setTitle("Settings").setView(scroll)
        .setNegativeButton("Cancel", null).setPositiveButton("Save", null).create()
    dialog.setOnShowListener {
        dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
            val limit = if (unlimited.isChecked) null else cap.text.toString().toIntOrNull()
            if (!unlimited.isChecked && (limit == null || limit !in 1..10000)) {
                cap.error = "Enter a whole number from 1 to 10,000"
            } else {
                save(Settings(if (places.selectedItemPosition == 0) null else places.selectedItemPosition - 1,
                    if (theme.selectedItemPosition == 1) "light" else "dark", limit))
                dialog.dismiss()
            }
        }
    }
    dialog.show()
}
