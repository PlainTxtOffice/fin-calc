import SwiftUI
import UIKit

/// Scrollable tape of past calculations; tapping one reuses its result.
struct TapeView: View {
    let entries: [HistoryEntry]
    let colors: ThemeColors
    let formatResult: (String) -> String
    let onSelect: (String) -> Void

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(alignment: .trailing, spacing: 0) {
                    ForEach(Array(entries.enumerated()), id: \.offset) {
                        index, entry in
                        row(for: entry).id(index)
                    }
                }
                .padding(.vertical, 6)
            }
            .defaultScrollAnchor(.bottom)
            .onChange(of: entries.count) { _, count in
                guard count > 0 else { return }
                withAnimation(.easeOut(duration: 0.3)) {
                    proxy.scrollTo(count - 1, anchor: .bottom)
                }
            }
        }
        .overlay {
            if entries.isEmpty {
                Text("Calculations appear here")
                    .font(.callout)
                    .foregroundStyle(colors.placeholderText)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(colors.tapeBackground, in: .rect(cornerRadius: 12))
    }

    private func row(for entry: HistoryEntry) -> some View {
        let text = KeyLabels.format(
            "\(entry.expression) = \(formatResult(entry.result))",
        )
        return Button {
            onSelect(entry.result)
        } label: {
            Text(text)
                .font(.system(size: 17, design: .rounded))
                .monospacedDigit()
                .foregroundStyle(colors.tapeText)
                .multilineTextAlignment(.trailing)
                .frame(maxWidth: .infinity, alignment: .trailing)
                .padding(.horizontal, 14)
                .padding(.vertical, 6)
                .contentShape(.rect)
        }
        .buttonStyle(.plain)
        .accessibilityHint("Inserts this result into the expression")
        .contextMenu {
            Button("Use Result", systemImage: "arrow.down.to.line") {
                onSelect(entry.result)
            }
            Button("Copy Result", systemImage: "doc.on.doc") {
                UIPasteboard.general.string = entry.result
            }
        }
    }
}
