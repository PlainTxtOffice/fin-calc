package com.plaintxtoffice.fincalc.adapters

import java.io.File
import java.nio.file.Files
import java.nio.file.StandardCopyOption

/** Local UTF-8 storage. Replacing a completed temporary file prevents partial saves. */
class StateStore(private val file: File) {
    fun load(): StoredState = if (!file.exists()) StoredState() else StateCodec.decode(file.readText(Charsets.UTF_8))

    fun save(state: StoredState) {
        file.parentFile?.mkdirs()
        val temporary = File(file.parentFile, file.name + ".tmp")
        try {
            temporary.outputStream().use { stream ->
                stream.write(StateCodec.encode(state).toByteArray(Charsets.UTF_8))
                stream.fd.sync()
            }
            Files.move(temporary.toPath(), file.toPath(), StandardCopyOption.ATOMIC_MOVE,
                StandardCopyOption.REPLACE_EXISTING)
        } finally {
            temporary.delete()
        }
    }
}
