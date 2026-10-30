/// Color theme name, stored as "dark" or "light".
enum Theme: String, CaseIterable, Sendable {
    case dark
    case light

    static let defaultTheme = Theme.dark
}

/// User-configurable application settings.
struct Settings: Equatable, Sendable {
    /// Decimal places shown for results; nil means full precision.
    var decimalPlaces: Int?
    /// Theme name, dark or light.
    var theme: Theme = .defaultTheme
    /// Maximum retained history entries; nil means unlimited.
    var maxHistoryEntries: Int? = History.defaultCap
}
