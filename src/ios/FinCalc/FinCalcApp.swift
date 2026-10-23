import SwiftUI

/// App entry point: load saved state once and show the calculator.
@main
struct FinCalcApp: App {
    @State private var session = CalculatorSession.load()
    @Environment(\.scenePhase) private var scenePhase

    var body: some Scene {
        WindowGroup {
            RootView(session: session)
        }
        .onChange(of: scenePhase) { _, phase in
            // Finish queued history writes before iOS may suspend the app.
            if phase == .background {
                session.waitForPendingWrites()
            }
        }
    }
}
