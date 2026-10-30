//
//  DevFeedback.swift
//
//  Debug-build feedback capture for testing on your own iPhone.
//
//  Shake the device in a Debug build to open a feedback sheet. Reports,
//  screenshots and an event log are written to Documents/DevFeedback inside the
//  app container. Pull them to the Mac with scripts/pull-dev-feedback.sh.
//
//  Only Debug builds contain the implementation. In Release (Archive,
//  TestFlight, App Store) `DevLog` and `devScreen(_:)` compile to empty stubs,
//  so call sites need no #if.
//

import SwiftUI
import UIKit

/// Records named events into the Debug feedback log. No-op in Release builds.
nonisolated enum DevLog {
    /// Logs an event, for example `DevLog.event("export_tapped", ["format": "csv"])`.
    /// Keep values short and never pass credentials or private document text.
    static func event(_ name: String, _ attributes: [String: String] = [:]) {
        #if DEBUG
        DevFeedbackStore.shared.record(name: name, attributes: attributes)
        #endif
    }

    /// Marks the screen the user is on. Feedback reports include the latest value.
    static func screen(_ name: String) {
        #if DEBUG
        DevFeedbackStore.shared.setScreen(name)
        #endif
    }
}

extension View {
    /// Tags this view as a named screen in Debug feedback. No-op in Release builds.
    func devScreen(_ name: String) -> some View {
        #if DEBUG
        onAppear { DevLog.screen(name) }
        #else
        self
        #endif
    }
}

#if DEBUG

// MARK: - Records

nonisolated struct DevFeedbackEvent: Codable, Sendable {
    let time: String
    let session: String
    let screen: String
    let name: String
    let attributes: [String: String]
}

nonisolated struct DevFeedbackReport: Codable, Sendable {
    let id: String
    let time: String
    let session: String
    let kind: String
    let note: String
    let screen: String
    let screenshot: String?
    let app: [String: String]
    let preferences: [String: String]
    let recentEvents: [DevFeedbackEvent]
}

// MARK: - Storage

/// Writes feedback files on a private serial queue. All mutable state is
/// accessed only on `queue`.
nonisolated final class DevFeedbackStore: @unchecked Sendable {
    static let shared = DevFeedbackStore()

    private let directory: URL
    private let reportsDirectory: URL
    private let eventsURL: URL
    private let session = UUID().uuidString
    private let queue = DispatchQueue(label: "DevFeedbackStore")
    private let recentLimit = 50
    private var screen = "unknown"
    private var recent: [DevFeedbackEvent] = []

    private init() {
        let documents = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        directory = documents.appendingPathComponent("DevFeedback", isDirectory: true)
        reportsDirectory = directory.appendingPathComponent("reports", isDirectory: true)
        eventsURL = directory.appendingPathComponent("events.jsonl")
        record(name: "session_start", attributes: Self.appInfo())
    }

    func setScreen(_ name: String) {
        queue.async { self.screen = name }
        record(name: "screen", attributes: ["name": name])
    }

    func record(name: String, attributes: [String: String]) {
        let time = Date.now.ISO8601Format()
        queue.async {
            let event = DevFeedbackEvent(
                time: time, session: self.session, screen: self.screen,
                name: name, attributes: attributes
            )
            self.recent.append(event)
            if self.recent.count > self.recentLimit {
                self.recent.removeFirst(self.recent.count - self.recentLimit)
            }
            self.appendLine(event)
        }
    }

    func currentScreen() -> String {
        queue.sync { screen }
    }

    func reportCount() -> Int {
        queue.sync {
            let names = (try? FileManager.default.contentsOfDirectory(atPath: reportsDirectory.path)) ?? []
            return names.filter { $0.hasSuffix(".json") }.count
        }
    }

    func saveReport(kind: String, note: String, screen: String, screenshot: Data?) {
        let now = Date.now
        let time = now.ISO8601Format()
        let id = Self.reportID(for: now)
        queue.async {
            self.ensureDirectories()
            var screenshotName: String?
            if let screenshot {
                let name = id + ".png"
                if (try? screenshot.write(to: self.reportsDirectory.appendingPathComponent(name))) != nil {
                    screenshotName = name
                }
            }
            let report = DevFeedbackReport(
                id: id, time: time, session: self.session, kind: kind, note: note,
                screen: screen, screenshot: screenshotName, app: Self.appInfo(),
                preferences: Self.preferences(), recentEvents: self.recent
            )
            let encoder = JSONEncoder()
            encoder.outputFormatting = [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]
            if let data = try? encoder.encode(report) {
                try? data.write(to: self.reportsDirectory.appendingPathComponent(id + ".json"), options: .atomic)
            }
        }
        record(name: "feedback_saved", attributes: ["id": id, "kind": kind])
    }

    func deleteAll() {
        queue.async {
            try? FileManager.default.removeItem(at: self.directory)
            self.recent.removeAll()
        }
    }

    private func ensureDirectories() {
        try? FileManager.default.createDirectory(at: reportsDirectory, withIntermediateDirectories: true)
    }

    private func appendLine(_ event: DevFeedbackEvent) {
        ensureDirectories()
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.sortedKeys, .withoutEscapingSlashes]
        guard var line = try? encoder.encode(event) else { return }
        line.append(0x0A)
        if let handle = try? FileHandle(forWritingTo: eventsURL) {
            defer { try? handle.close() }
            _ = try? handle.seekToEnd()
            try? handle.write(contentsOf: line)
        } else {
            try? line.write(to: eventsURL)
        }
    }

    private static func reportID(for date: Date) -> String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(identifier: "UTC")
        formatter.dateFormat = "yyyyMMdd-HHmmss"
        return formatter.string(from: date) + "-" + UUID().uuidString.prefix(4).lowercased()
    }

    private static func appInfo() -> [String: String] {
        let info = Bundle.main.infoDictionary ?? [:]
        var system = utsname()
        uname(&system)
        let model = withUnsafeBytes(of: system.machine) { bytes in
            String(decoding: bytes.prefix { $0 != 0 }, as: UTF8.self)
        }
        return [
            "bundle": Bundle.main.bundleIdentifier ?? "",
            "version": info["CFBundleShortVersionString"] as? String ?? "",
            "build": info["CFBundleVersion"] as? String ?? "",
            "os": ProcessInfo.processInfo.operatingSystemVersionString,
            "model": model,
        ]
    }

    /// The app's own UserDefaults domain, excluding system keys.
    private static func preferences() -> [String: String] {
        guard let id = Bundle.main.bundleIdentifier,
              let domain = UserDefaults.standard.persistentDomain(forName: id) else { return [:] }
        return domain.mapValues { String(String(describing: $0).prefix(500)) }
    }
}

// MARK: - Shake to open

extension UIWindow {
    override open func motionEnded(_ motion: UIEvent.EventSubtype, with event: UIEvent?) {
        super.motionEnded(motion, with: event)
        if motion == .motionShake {
            DevFeedbackPresenter.present(from: self)
        }
    }
}

final class DevFeedbackHostingController: UIHostingController<DevFeedbackSheet> {}

@MainActor
enum DevFeedbackPresenter {
    /// Presents the sheet above whatever is on screen, including other sheets.
    static func present(from window: UIWindow) {
        guard var top = window.rootViewController else { return }
        while let next = top.presentedViewController { top = next }
        guard !(top is DevFeedbackHostingController), !(top is UIAlertController) else { return }

        let screenshot = capture(window)
        let screen = DevFeedbackStore.shared.currentScreen()
        let dismisser = DevFeedbackDismisser()
        let sheet = DevFeedbackSheet(screenshot: screenshot, screen: screen) { dismisser.dismiss() }
        let controller = DevFeedbackHostingController(rootView: sheet)
        dismisser.controller = controller
        top.present(controller, animated: true)
    }

    private static func capture(_ window: UIWindow) -> Data? {
        let renderer = UIGraphicsImageRenderer(bounds: window.bounds)
        let image = renderer.image { _ in
            _ = window.drawHierarchy(in: window.bounds, afterScreenUpdates: false)
        }
        return image.pngData()
    }
}

@MainActor
private final class DevFeedbackDismisser {
    weak var controller: UIViewController?
    func dismiss() { controller?.dismiss(animated: true) }
}

// MARK: - Sheet

struct DevFeedbackSheet: View {
    let screenshot: Data?
    let screen: String
    let onDone: @MainActor () -> Void

    @State private var kind = "idea"
    @State private var note = ""
    @State private var attachScreenshot = true
    @State private var savedCount = DevFeedbackStore.shared.reportCount()
    @State private var confirmDelete = false
    @FocusState private var noteFocused: Bool

    private static let kinds = ["bug", "idea", "preference", "like", "dislike"]

    private var trimmedNote: String {
        note.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    Picker("Type", selection: $kind) {
                        ForEach(Self.kinds, id: \.self) { Text($0.capitalized).tag($0) }
                    }
                    LabeledContent("Screen", value: screen)
                }
                Section("What should change?") {
                    TextEditor(text: $note)
                        .frame(minHeight: 140)
                        .focused($noteFocused)
                }
                if let screenshot, let image = UIImage(data: screenshot) {
                    Section {
                        Toggle("Attach screenshot", isOn: $attachScreenshot)
                        if attachScreenshot {
                            Image(uiImage: image)
                                .resizable()
                                .scaledToFit()
                                .frame(maxHeight: 240)
                                .accessibilityLabel("Screenshot preview")
                        }
                    }
                }
                Section {
                    LabeledContent("Saved on this phone", value: "\(savedCount)")
                    Button("Delete All Saved Feedback", role: .destructive) { confirmDelete = true }
                } footer: {
                    Text("Debug builds only. Run scripts/pull-dev-feedback.sh on your Mac to copy reports into the repo.")
                }
            }
            .navigationTitle("Dev Feedback")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { onDone() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        DevFeedbackStore.shared.saveReport(
                            kind: kind, note: trimmedNote, screen: screen,
                            screenshot: attachScreenshot ? screenshot : nil
                        )
                        onDone()
                    }
                    .disabled(trimmedNote.isEmpty)
                }
            }
            .confirmationDialog(
                "Delete all saved feedback on this phone?",
                isPresented: $confirmDelete,
                titleVisibility: .visible
            ) {
                Button("Delete", role: .destructive) {
                    DevFeedbackStore.shared.deleteAll()
                    savedCount = 0
                }
            }
            .onAppear { noteFocused = true }
        }
    }
}

#endif
