"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const configRunProvider_1 = require("./codelens/configRunProvider");
const runExperiment_1 = require("./commands/runExperiment");
/**
 * Checks if a document is a PyComex experiment config file.
 * A valid PyComex config YAML file must contain both "extend:" and "parameters:" fields.
 *
 * @param document The document to check
 * @returns true if the document is a PyComex config file
 */
function isPyComexConfigFile(document) {
    if (!document || document.languageId !== 'yaml') {
        return false;
    }
    const text = document.getText();
    const hasExtend = /^extend:/m.test(text);
    const hasParameters = /^parameters:/m.test(text);
    return hasExtend && hasParameters;
}
/**
 * Updates the context key that indicates whether the active file is a PyComex config.
 * This controls the visibility of the run button in the editor title bar.
 *
 * @param editor The active text editor
 */
function updatePyComexContext(editor) {
    const isConfig = isPyComexConfigFile(editor?.document);
    vscode.commands.executeCommand('setContext', 'pycomex.isConfigFile', isConfig);
}
/**
 * This method is called when the extension is activated.
 * The extension is activated the very first time a command is executed or
 * when a YAML file is opened (as defined in activationEvents in package.json).
 *
 * @param context The extension context provided by VS Code
 */
function activate(context) {
    console.log('PyComex extension is now active!');
    // Set initial context based on the active editor
    updatePyComexContext(vscode.window.activeTextEditor);
    // Update context when the active editor changes
    const editorChangeListener = vscode.window.onDidChangeActiveTextEditor(editor => {
        updatePyComexContext(editor);
    });
    // Update context when the document content changes (user types)
    const documentChangeListener = vscode.workspace.onDidChangeTextDocument(event => {
        if (event.document === vscode.window.activeTextEditor?.document) {
            updatePyComexContext(vscode.window.activeTextEditor);
        }
    });
    // Register the CodeLens provider for YAML files
    const codeLensProvider = vscode.languages.registerCodeLensProvider({ language: 'yaml', scheme: 'file' }, new configRunProvider_1.PyComexConfigCodeLensProvider());
    // Register the command to run an experiment config
    // This command now uses the active editor's document
    const runConfigCommand = vscode.commands.registerCommand('pycomex.runConfig', (uri) => {
        // If URI is provided (from CodeLens), use it
        // Otherwise, use the active editor's URI
        if (uri) {
            (0, runExperiment_1.runExperimentConfig)(uri);
        }
        else {
            (0, runExperiment_1.runExperimentFromActiveFile)();
        }
    });
    // Register the command to run from active file (can be triggered from command palette)
    const runActiveFileCommand = vscode.commands.registerCommand('pycomex.runActiveFile', runExperiment_1.runExperimentFromActiveFile);
    // Add all disposables to the context subscriptions
    // This ensures they are properly cleaned up when the extension is deactivated
    context.subscriptions.push(editorChangeListener, documentChangeListener, codeLensProvider, runConfigCommand, runActiveFileCommand);
    // Show a message when the extension is activated (optional, for debugging)
    // vscode.window.showInformationMessage('PyComex extension loaded!');
}
/**
 * This method is called when the extension is deactivated.
 * Use this to clean up any resources if necessary.
 */
function deactivate() {
    console.log('PyComex extension is now deactivated');
}
//# sourceMappingURL=extension.js.map