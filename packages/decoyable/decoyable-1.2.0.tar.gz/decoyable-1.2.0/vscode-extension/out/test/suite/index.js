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
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
const assert = __importStar(require("assert"));
const vscode = __importStar(require("vscode"));
const mocha_1 = require("mocha");
// You can import and use all API from the 'vscode' module
// as well as import your extension to test it
// const myExtension = require('../../extension');
(0, mocha_1.suite)('DECOYABLE Extension Test Suite', () => {
    vscode.window.showInformationMessage('Start all tests.');
    (0, mocha_1.test)('Sample test', () => {
        assert.strictEqual(-1, [1, 2, 3].indexOf(5));
        assert.strictEqual(-1, [1, 2, 3].indexOf(0));
    });
    (0, mocha_1.test)('Extension activation', async () => {
        // Test that the extension activates properly
        const extension = vscode.extensions.getExtension('kolerr-lab.decoyable-security');
        if (extension) {
            await extension.activate();
            assert.ok(extension.isActive);
        }
        else {
            assert.fail('Extension not found');
        }
    });
    (0, mocha_1.test)('Commands registration', async () => {
        // Test that commands are registered
        const commands = await vscode.commands.getCommands(true);
        const decoyableCommands = commands.filter((cmd) => cmd.startsWith('decoyable.'));
        assert.ok(decoyableCommands.length > 0, 'DECOYABLE commands should be registered');
        assert.ok(decoyableCommands.includes('decoyable.scanWorkspace'), 'scanWorkspace command should be registered');
        assert.ok(decoyableCommands.includes('decoyable.scanFile'), 'scanFile command should be registered');
    });
});
//# sourceMappingURL=index.js.map