package com.plaintxtoffice.fincalc.domains.calc

import java.math.BigDecimal
import java.math.MathContext
import java.math.RoundingMode

/** Decimal operations with Python's 28 significant digits and half-even rounding. */
object DecimalMath {
    val context = MathContext(28, RoundingMode.HALF_EVEN)
    private val work = MathContext(42, RoundingMode.HALF_EVEN)
    private val ln2 = BigDecimal("0.693147180559945309417232121458176568075500134")
    private val ln10 = BigDecimal("2.30258509299404568401799145468436420760110149")
    private val epsilon = BigDecimal("1E-43")
    private val one = BigDecimal.ONE
    private val two = BigDecimal(2)

    /** Bound output size and exponent to keep interactive operations responsive. */
    fun checked(value: BigDecimal): BigDecimal {
        val rounded = value.round(context)
        val magnitude = rounded.precision().toLong() - rounded.scale() - 1
        if (rounded.signum() != 0 && magnitude !in -9999L..9999L) {
            throw EvaluationError("Result out of range")
        }
        return rounded
    }

    private fun ln(value: BigDecimal): BigDecimal {
        val tens = value.precision() - value.scale() - 1
        var mantissa = value.scaleByPowerOfTen(-tens)
        var halves = 0
        while (mantissa > BigDecimal("1.5")) {
            mantissa = mantissa.divide(two, work)
            halves++
        }
        val z = mantissa.subtract(one).divide(mantissa.add(one), work)
        val squared = z.multiply(z, work)
        var power = z
        var sum = z
        for (index in 1..200) {
            power = power.multiply(squared, work)
            val term = power.divide(BigDecimal(2 * index + 1), work)
            sum = sum.add(term, work)
            if (term.abs() < epsilon) break
        }
        return sum.multiply(two, work).add(ln2.multiply(BigDecimal(halves), work), work)
            .add(ln10.multiply(BigDecimal(tens), work), work)
    }

    fun log10(value: BigDecimal): BigDecimal {
        if (value.signum() <= 0) throw EvaluationError("Log undefined for non-positive values")
        return checked(ln(value).divide(ln10, work))
    }

    private fun exp(value: BigDecimal): BigDecimal {
        val twos = value.divide(ln2, 0, RoundingMode.HALF_EVEN).intValueExact()
        if (twos !in -33220..33220) throw EvaluationError("Result out of range")
        val remainder = value.subtract(ln2.multiply(BigDecimal(twos), work), work)
        var term = one
        var sum = one
        for (index in 1..200) {
            term = term.multiply(remainder, work).divide(BigDecimal(index), work)
            sum = sum.add(term, work)
            if (term.abs() < epsilon) break
        }
        return if (twos >= 0) sum.multiply(two.pow(twos, work), work)
        else sum.divide(two.pow(-twos, work), work)
    }

    fun power(base: BigDecimal, exponent: BigDecimal): BigDecimal {
        val whole = exponent.stripTrailingZeros().scale() <= 0
        if ((base.signum() == 0 && exponent.signum() == 0) || (base.signum() < 0 && !whole)) {
            throw EvaluationError("Invalid exponentiation: $base ^ $exponent")
        }
        if (base.signum() == 0) {
            if (exponent.signum() < 0) throw EvaluationError("Result out of range")
            return BigDecimal.ZERO
        }
        if (whole && exponent.abs() <= BigDecimal(9999)) {
            return checked(base.pow(exponent.toInt(), work))
        }
        var result = exp(ln(base.abs()).multiply(exponent, work))
        if (base.signum() < 0 && exponent.remainder(two).signum() != 0) result = result.negate()
        return checked(result)
    }
}

/** A readable arithmetic or input failure that can be shown by any interface. */
class EvaluationError(message: String) : IllegalArgumentException(message)
