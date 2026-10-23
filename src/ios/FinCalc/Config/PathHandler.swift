import Foundation

/// File locations inside the app's sandboxed Application Support folder.
enum PathHandler {
    static let dataDirectory = URL.applicationSupportDirectory
        .appending(path: "FinCalc", directoryHint: .isDirectory)
    static let historyFile = dataDirectory.appending(path: "history.json")
    static let settingsFile = dataDirectory.appending(path: "settings.json")
}
