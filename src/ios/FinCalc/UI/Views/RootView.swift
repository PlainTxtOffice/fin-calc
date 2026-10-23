import CoreTransferable
import SwiftUI
import UniformTypeIdentifiers

/// Main calculator screen assembling tape, display, and keypad.
struct RootView: View {
    let session: CalculatorSession

    @State private var isShowingSettings = false
    @State private var isConfirmingClear = false
    @FocusState private var hasKeyboardFocus: Bool

    var body: some View {
        let colors = ThemeColors.colors(for: session.settings.theme)
        NavigationStack {
            GeometryReader { proxy in
                VStack(spacing: 10) {
                    TapeView(
                        entries: session.history.entries,
                        colors: colors,
                        formatResult: session.formatResult,
                        onSelect: session.insertResult,
                    )
                    DisplayView(
                        expression: session.displayText,
                        status: session.statusText,
                        colors: colors,
                    )
                    KeypadView(colors: colors, onKey: press)
                        .frame(height: proxy.size.height * 0.5)
                }
            }
            .padding(.horizontal, 12)
            .padding(.bottom, 8)
            .background(colors.window)
            .navigationTitle("Fin Calc")
            .navigationBarTitleDisplayMode(.inline)
            .toolbarBackground(colors.window, for: .navigationBar)
            .toolbar { toolbarContent }
        }
        .preferredColorScheme(colors.colorScheme)
        .tint(colors.highlight)
        .sensoryFeedback(.error, trigger: session.statusText) { _, status in
            !status.isEmpty
        }
        .confirmationDialog(
            "Clear all history?",
            isPresented: $isConfirmingClear,
            titleVisibility: .visible,
        ) {
            Button("Clear History", role: .destructive) {
                session.clearHistory()
            }
        } message: {
            Text("This removes every saved calculation from the tape.")
        }
        .sheet(isPresented: $isShowingSettings) {
            SettingsView(settings: session.settings) { settings in
                session.applySettings(settings)
            }
        }
        // Hardware keyboards (iPad, simulator) type straight into the keypad.
        .focusable()
        .focused($hasKeyboardFocus)
        .focusEffectDisabled()
        .onKeyPress(phases: .down, action: pressHardwareKey)
        .onAppear { hasKeyboardFocus = true }
    }

    @ToolbarContentBuilder
    private var toolbarContent: some ToolbarContent {
        ToolbarItem(placement: .topBarLeading) {
            Menu("History", systemImage: "clock.arrow.circlepath") {
                ShareLink(
                    item: HistoryCSV(
                        text: HistoryExport.formatCSV(session.history),
                    ),
                    preview: SharePreview("Fin Calc history"),
                ) {
                    Label("Export CSV", systemImage: "square.and.arrow.up")
                }
                .disabled(session.history.entries.isEmpty)
                Button(
                    "Clear History",
                    systemImage: "trash",
                    role: .destructive,
                ) {
                    isConfirmingClear = true
                }
                .disabled(session.history.entries.isEmpty)
            }
        }
        ToolbarItem(placement: .topBarTrailing) {
            Button("Settings", systemImage: "gearshape") {
                isShowingSettings = true
            }
        }
    }

    private func press(_ key: KeypadKey) {
        switch key {
        case .symbol(let symbol): session.addSymbol(symbol)
        case .evaluate: session.evaluate()
        case .clear: session.clear()
        case .backspace: session.backspace()
        case .toggleSign: session.toggleSign()
        }
    }

    private func pressHardwareKey(_ keyPress: KeyPress) -> KeyPress.Result {
        switch keyPress.key {
        case .return:
            session.evaluate()
        case .escape:
            session.clear()
        case .delete:
            session.backspace()
        default:
            let character = keyPress.characters
            if character.lowercased() == "l" {
                session.addSymbol("log")
            } else if "0123456789.+-*/^()".contains(character),
                      character.count == 1
            {
                session.addSymbol(character)
            } else {
                return .ignored
            }
        }
        return .handled
    }
}

/// History exported as a shareable CSV file.
private struct HistoryCSV: Transferable {
    let text: String

    static var transferRepresentation: some TransferRepresentation {
        DataRepresentation(exportedContentType: .commaSeparatedText) {
            Data($0.text.utf8)
        }
        .suggestedFileName("history.csv")
    }
}
