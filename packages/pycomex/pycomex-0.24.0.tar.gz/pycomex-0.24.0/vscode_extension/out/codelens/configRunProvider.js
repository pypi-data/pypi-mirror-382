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
exports.PyComexConfigCodeLensProvider = void 0;
const vscode = __importStar(require("vscode"));
/**
 * CodeLens provider for PyComex experiment config YAML files.
 *
 * This provider detects YAML files that contain PyComex experiment configurations
 * (identified by the presence of "extend:" and "parameters:" fields) and provides
 * a "Run Experiment" CodeLens button at the top of the file.
 */
class PyComexConfigCodeLensProvider {
    /**
     * Provides CodeLenses for a given document.
     *
     * @param document The document in which the command was invoked.
     * @returns An array of CodeLens objects or a thenable that resolves to such.
     */
    async provideCodeLenses(document) {
        // Only process YAML files
        if (document.languageId !== 'yaml') {
            return [];
        }
        const text = document.getText();
        // Check if this is a PyComex experiment config file
        // by looking for required fields: "extend:" and "parameters:"
        const hasExtend = /^extend:/m.test(text);
        const hasParameters = /^parameters:/m.test(text);
        if (hasExtend && hasParameters) {
            // Create a CodeLens at the top of the file (line 0, column 0)
            const range = new vscode.Range(0, 0, 0, 0);
            const command = {
                title: "▶ Run Experiment",
                command: "pycomex.runConfig",
                arguments: [document.uri]
            };
            return [new vscode.CodeLens(range, command)];
        }
        return [];
    }
}
exports.PyComexConfigCodeLensProvider = PyComexConfigCodeLensProvider;
//# sourceMappingURL=configRunProvider.js.map