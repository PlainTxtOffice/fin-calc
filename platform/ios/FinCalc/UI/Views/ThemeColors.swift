import SwiftUI

/// Colors for one theme, matching the Windows app's palettes.
struct ThemeColors {
    let colorScheme: ColorScheme
    let window: Color
    let key: Color
    let operatorKey: Color
    let keyText: Color
    let highlight: Color
    let highlightedText: Color
    let displayBackground: Color
    let displayText: Color
    let placeholderText: Color
    let errorText: Color
    let tapeBackground: Color
    let tapeText: Color

    static func colors(for theme: Theme) -> ThemeColors {
        switch theme {
        case .dark: dark
        case .light: light
        }
    }

    private static let dark = ThemeColors(
        colorScheme: .dark,
        window: Color(hex: 0x25282D),
        key: Color(hex: 0x33373D),
        operatorKey: Color(hex: 0x2D2D2D),
        keyText: Color(hex: 0xE6E6E6),
        highlight: Color(hex: 0x3D6FA5),
        highlightedText: .white,
        displayBackground: Color(hex: 0x1E1E1E),
        displayText: .white,
        placeholderText: Color(hex: 0x8A919C),
        errorText: Color(hex: 0xFF6B6B),
        tapeBackground: Color(hex: 0x2D2D2D),
        tapeText: Color(hex: 0xCCCCCC),
    )

    private static let light = ThemeColors(
        colorScheme: .light,
        window: Color(hex: 0xF2F3F5),
        key: Color(hex: 0xDFE3E8),
        operatorKey: Color(hex: 0xE8EAED),
        keyText: Color(hex: 0x1F2328),
        highlight: Color(hex: 0x3D6FA5),
        highlightedText: .white,
        displayBackground: .white,
        displayText: Color(hex: 0x111111),
        placeholderText: Color(hex: 0x6B7280),
        errorText: Color(hex: 0xC62828),
        tapeBackground: .white,
        tapeText: Color(hex: 0x333333),
    )
}

private extension Color {
    init(hex: UInt32) {
        self.init(
            red: Double((hex >> 16) & 0xFF) / 255,
            green: Double((hex >> 8) & 0xFF) / 255,
            blue: Double(hex & 0xFF) / 255,
        )
    }
}
