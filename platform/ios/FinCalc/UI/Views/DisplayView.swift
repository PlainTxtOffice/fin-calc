import SwiftUI

/// Shows the current expression and a status or error line.
struct DisplayView: View {
    let expression: String
    let status: String
    let colors: ThemeColors

    var body: some View {
        VStack(alignment: .trailing, spacing: 4) {
            Text(expression.isEmpty ? "0" : KeyLabels.format(expression))
                .font(.system(size: 40, weight: .light, design: .rounded))
                .monospacedDigit()
                .foregroundStyle(
                    expression.isEmpty ? colors.placeholderText
                        : colors.displayText,
                )
                .lineLimit(1)
                .minimumScaleFactor(0.4)
                .truncationMode(.head)
                .textSelection(.enabled)
            Text(status)
                .font(.footnote)
                .foregroundStyle(colors.errorText)
                .lineLimit(2)
                .frame(minHeight: 18)
        }
        .frame(maxWidth: .infinity, alignment: .trailing)
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(colors.displayBackground, in: .rect(cornerRadius: 12))
        .accessibilityElement(children: .combine)
        .accessibilityLabel(
            status.isEmpty ? expression : "\(expression). \(status)",
        )
    }
}
