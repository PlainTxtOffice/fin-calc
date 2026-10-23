package com.plaintxtoffice.fincalc.domains.calc

import java.time.Instant

/** Preserve full result precision separately from its display representation. */
data class HistoryEntry(val expression: String, val result: String, val timestamp: Instant)

/** Retain the newest entries; null is unlimited and zero retains nothing. */
fun trimHistory(entries: List<HistoryEntry>, cap: Int?): List<HistoryEntry> =
    if (cap == null) entries.toList() else entries.takeLast(cap.coerceAtLeast(0))
