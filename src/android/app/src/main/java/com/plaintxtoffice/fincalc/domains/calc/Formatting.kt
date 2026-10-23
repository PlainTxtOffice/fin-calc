package com.plaintxtoffice.fincalc.domains.calc

import java.math.RoundingMode

/** Round for presentation only; history and reuse always keep the original value. */
fun formatResult(value: String, places: Int?): String {
    if (places == null) return value
    return try {
        val decimal = value.toBigDecimal()
        if (decimal.precision() - decimal.scale() + places > 28) value
        else decimal.setScale(places, RoundingMode.HALF_EVEN).toPlainString()
    } catch (error: NumberFormatException) { value }
}
