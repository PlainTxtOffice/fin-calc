package com.plaintxtoffice.fincalc.application

import android.app.Application
import android.net.Uri
import android.os.Handler
import android.os.Looper
import android.util.Log
import androidx.lifecycle.AndroidViewModel
import com.plaintxtoffice.fincalc.adapters.*
import com.plaintxtoffice.fincalc.config.Settings
import com.plaintxtoffice.fincalc.domains.calc.HistoryEntry
import com.plaintxtoffice.fincalc.domains.calc.formatResult
import java.io.File
import java.io.IOException
import java.util.concurrent.Executors

/** Immutable UI state, also used to restore unfinished input after process recreation. */
data class ScreenState(
    val stored: StoredState = StoredState(), val expression: String = "", val status: String = "Loading…",
    val tokens: List<String> = emptyList(), val pending: Boolean = false, val ready: Boolean = false,
)

/** Serialize arithmetic and disk operations off the UI thread; survive Activity recreation. */
class CalculatorModel(application: Application) : AndroidViewModel(application) {
    private val queue = Executors.newSingleThreadExecutor()
    private val main = Handler(Looper.getMainLooper())
    private lateinit var session: CalculatorSession
    var current = ScreenState()
        private set
    var onChange: ((ScreenState) -> Unit)? = null

    init {
        queue.execute {
            val store = StateStore(File(application.filesDir, "calculator.json"))
            var warning = ""
            val stored = try { store.load() } catch (error: Exception) {
                Log.e("FinCalc", "Cannot load saved calculator state", error)
                warning = "Could not load saved history and settings. Defaults are in use."
                StoredState()
            }
            session = CalculatorSession(stored, store::save)
            publish(warning)
        }
    }

    private fun publish(message: String? = null) {
        val builder = session.builder
        val expression = if (builder.hasPendingResult() && builder.symbols().size == 1)
            formatResult(builder.symbols().single(), session.state.settings.decimalPlaces) else builder.display()
        val snapshot = ScreenState(session.state, expression, message ?: session.status,
            builder.symbols(), builder.hasPendingResult(), true)
        main.post { current = snapshot; onChange?.invoke(snapshot) }
    }

    private fun submit(action: () -> Unit) {
        queue.execute {
            try { action(); publish() } catch (error: Exception) {
                if (error is IOException) Log.e("FinCalc", "Storage operation failed", error)
                publish(if (error is IOException) "Could not save. Your previous history is unchanged."
                    else error.message ?: "Calculation failed")
            }
        }
    }

    fun press(key: String) = submit { session.press(key) }
    fun reuse(entry: HistoryEntry) = submit { session.reuse(entry) }
    fun clearHistory() = submit { session.clearHistory() }
    fun updateSettings(settings: Settings) = submit { session.updateSettings(settings) }
    fun restore(tokens: List<String>, pending: Boolean) = submit { session.builder.restore(tokens, pending) }

    fun export(uri: Uri) = submit {
        val resolver = getApplication<Application>().contentResolver
        val stream = resolver.openOutputStream(uri, "wt") ?: throw IOException("Cannot open export")
        stream.bufferedWriter(Charsets.UTF_8).use { HistoryExport.write(session.state.history, it) }
    }

    override fun onCleared() { queue.shutdown(); super.onCleared() }
}
