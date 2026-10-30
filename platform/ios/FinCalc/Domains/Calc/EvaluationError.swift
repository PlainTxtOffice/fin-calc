import Foundation

/// Raised when an expression cannot be evaluated.
///
/// Covers division by zero, log of non-positive values, mismatched
/// parentheses, invalid token sequences, and results outside the range
/// `Decimal` can represent.
struct EvaluationError: LocalizedError, Equatable {
    let message: String

    init(_ message: String) {
        self.message = message
    }

    var errorDescription: String? { message }

    static let outOfRange = EvaluationError("Result out of range")
}
