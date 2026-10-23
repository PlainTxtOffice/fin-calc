import SwiftUI

/// Edit decimal precision, theme, and history cap.
struct SettingsView: View {
    let onSave: (Settings) -> Void

    @Environment(\.dismiss) private var dismiss
    @State private var draft: Settings
    @State private var isUnlimited: Bool
    @State private var historyCap: Int

    init(settings: Settings, onSave: @escaping (Settings) -> Void) {
        self.onSave = onSave
        _draft = State(initialValue: settings)
        _isUnlimited = State(initialValue: settings.maxHistoryEntries == nil)
        _historyCap = State(
            initialValue: settings.maxHistoryEntries ?? History.defaultCap,
        )
    }

    var body: some View {
        NavigationStack {
            Form {
                Section("Display") {
                    Picker("Decimal places", selection: $draft.decimalPlaces) {
                        Text("Full precision").tag(Int?.none)
                        ForEach(0...Formatting.maxDecimalPlaces, id: \.self) {
                            places in
                            Text("\(places)").tag(Int?.some(places))
                        }
                    }
                    Picker("Theme", selection: $draft.theme) {
                        ForEach(Theme.allCases, id: \.self) { theme in
                            Text(theme.rawValue.capitalized).tag(theme)
                        }
                    }
                }
                Section {
                    Toggle("Unlimited", isOn: $isUnlimited)
                    if !isUnlimited {
                        LabeledContent("Max entries") {
                            TextField(
                                "Max entries",
                                value: $historyCap,
                                format: .number.grouping(.never),
                            )
                            .keyboardType(.numberPad)
                            .multilineTextAlignment(.trailing)
                        }
                    }
                } header: {
                    Text("History")
                } footer: {
                    Text(
                        "Keep \(History.minCap) to \(History.maxCap) entries. "
                            + "The oldest calculations are removed first.",
                    )
                }
                Section("About") {
                    LabeledContent("Version", value: Self.appVersion)
                    Text(
                        "Decimal-precision arithmetic calculator with "
                            + "persistent history.",
                    )
                    .foregroundStyle(.secondary)
                }
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        onSave(selectedSettings())
                        dismiss()
                    }
                }
            }
        }
    }

    /// Return the edited settings with the history cap clamped to range.
    private func selectedSettings() -> Settings {
        var settings = draft
        settings.maxHistoryEntries = isUnlimited
            ? nil
            : min(max(historyCap, History.minCap), History.maxCap)
        return settings
    }

    private static var appVersion: String {
        Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString")
            as? String ?? "unknown"
    }
}
