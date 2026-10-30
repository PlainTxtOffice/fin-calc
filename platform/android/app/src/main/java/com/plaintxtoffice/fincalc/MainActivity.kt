package com.plaintxtoffice.fincalc

import android.app.AlertDialog
import android.content.ActivityNotFoundException
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.ContextThemeWrapper
import android.view.Gravity
import android.widget.*
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.lifecycle.ViewModelProvider
import com.plaintxtoffice.fincalc.application.CalculatorModel
import com.plaintxtoffice.fincalc.application.ScreenState
import com.plaintxtoffice.fincalc.ui.*

/** Android lifecycle and document-picker boundary; calculations live in the domain. */
class MainActivity : ComponentActivity() {
    private lateinit var model: CalculatorModel
    private lateinit var calculator: CalculatorView
    private var shownTheme: String? = null
    private val export = registerForActivityResult(ActivityResultContracts.CreateDocument("text/csv")) { uri ->
        if (uri != null) model.export(uri)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        WindowCompat.setDecorFitsSystemWindows(window, false)
        model = ViewModelProvider(this)[CalculatorModel::class.java]
        if (savedInstanceState != null && !model.current.ready) {
            model.restore(savedInstanceState.getStringArrayList("tokens") ?: emptyList(),
                savedInstanceState.getBoolean("pending"))
        }
        render(model.current)
    }

    override fun onStart() {
        super.onStart()
        model.onChange = ::render
        render(model.current)
    }
    override fun onStop() { model.onChange = null; super.onStop() }
    override fun onSaveInstanceState(outState: Bundle) {
        outState.putStringArrayList("tokens", ArrayList(model.current.tokens))
        outState.putBoolean("pending", model.current.pending)
        super.onSaveInstanceState(outState)
    }

    private fun render(state: ScreenState) {
        if (shownTheme != state.stored.settings.theme) buildViews(state.stored.settings.theme)
        calculator.render(state)
    }

    private fun buildViews(theme: String) {
        shownTheme = theme
        val colors = ThemeColors.forName(theme)
        val root = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setBackgroundColor(colors.background) }
        val bar = LinearLayout(this).apply { gravity = Gravity.CENTER_VERTICAL }
        bar.addView(TextView(this).apply { text = "Fin Calc"; textSize = 22f; setTextColor(colors.text) },
            LinearLayout.LayoutParams(0, dp(48), 1f))
        bar.addView(Button(this).apply {
            text = "⋮"; textSize = 24f; contentDescription = "More options"
            setTextColor(colors.text); background = rounded(colors.surface)
            setOnClickListener { showMenu(this) }
        }, LinearLayout.LayoutParams(dp(48), dp(48)))
        root.addView(bar)
        calculator = CalculatorView(this, colors, model::press, model::reuse)
        root.addView(calculator, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f))
        ViewCompat.setOnApplyWindowInsetsListener(root) { view, insets ->
            val bars = insets.getInsets(WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.displayCutout())
            view.setPadding(bars.left + dp(12), bars.top + dp(8), bars.right + dp(12), bars.bottom + dp(8))
            insets
        }
        setContentView(root)
        WindowCompat.getInsetsController(window, root).apply {
            isAppearanceLightStatusBars = theme == "light"
            isAppearanceLightNavigationBars = theme == "light"
        }
    }

    private fun showMenu(anchor: Button) {
        if (!model.current.ready) return
        val context = ContextThemeWrapper(this, if (shownTheme == "light")
            android.R.style.Theme_Material_Light_Dialog_Alert else android.R.style.Theme_Material_Dialog_Alert)
        PopupMenu(context, anchor).apply {
            listOf("Settings", "Export History", "Clear History", "Privacy Policy", "About").forEach { menu.add(it) }
            setOnMenuItemClickListener { item ->
                when (item.title) {
                    "Settings" -> showSettings(context, model.current.stored.settings, model::updateSettings)
                    "Export History" -> export.launch("fin-calc-history.csv")
                    "Privacy Policy" -> try {
                        startActivity(Intent(Intent.ACTION_VIEW,
                            Uri.parse("https://plaintxtoffice.com/privacy-policy/")))
                    } catch (_: ActivityNotFoundException) {
                        AlertDialog.Builder(context).setTitle("Privacy Policy")
                            .setMessage("https://plaintxtoffice.com/privacy-policy/")
                            .setPositiveButton("OK", null).show()
                    }
                    "Clear History" -> AlertDialog.Builder(context).setTitle("Clear History?")
                        .setMessage("Remove all saved calculations from this device?")
                        .setNegativeButton("Cancel", null)
                        .setPositiveButton("Clear") { _, _ -> model.clearHistory() }.show()
                    "About" -> AlertDialog.Builder(context).setTitle("Fin Calc 0.1.0")
                        .setMessage("Decimal calculator by Plain Text Office.\n\nTap a tape result to reuse its full precision. Use log ( … ) for base-10 logarithms.\n\nMIT License · Copyright 2026 Tripp")
                        .setPositiveButton("OK", null).show()
                }
                true
            }
            show()
        }
    }
}
