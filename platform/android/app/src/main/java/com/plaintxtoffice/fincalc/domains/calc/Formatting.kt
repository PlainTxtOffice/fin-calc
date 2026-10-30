package com.plaintxtoffice.fincalc.domains.calc

import java.math.BigDecimal
import java.math.RoundingMode

/** Largest decimal exponent shown as plain digits; matches the 28-digit engine precision. */
private const val PLAIN_EXPONENT_LIMIT = 28

/**
 * Write a result as plain digits, like the Windows and iOS apps, so 500 + 500 shows 1000
 * rather than 1E+3. Values beyond the engine's 28-digit range keep scientific notation so
 * they stay readable.
 */
fun plainResult(value: BigDecimal): String {
    val stripped = value.stripTrailingZeros()
    val exponent = stripped.precision() - stripped.scale() - 1
    return if (exponent in -PLAIN_EXPONENT_LIMIT..PLAIN_EXPONENT_LIMIT) stripped.toPlainString()
    else stripped.toString()
}

/** Round for presentation only; history and reuse always keep the original value. */
fun formatResult(value: String, places: Int?): String {
    return try {
        val decimal = value.toBigDecimal()
        when {
            // Results saved before plain display may still read like 1E+3.
            places == null -> plainResult(decimal)
            decimal.precision() - decimal.scale() + places > 28 -> value
            else -> decimal.setScale(places, RoundingMode.HALF_EVEN).toPlainString()
        }
    } catch (error: NumberFormatException) { value }
}
