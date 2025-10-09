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
exports.deactivate = exports.activate = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
const child_process_1 = require("child_process");
const util_1 = require("util");
const execAsync = (0, util_1.promisify)(child_process_1.exec);
class DecoyableExtension {
    constructor(context) {
        this.results = null;
        this.resultsProvider = new ResultsTreeProvider();
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('decoyable');
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
        this.outputChannel = vscode.window.createOutputChannel('DECOYABLE');
        context.subscriptions.push(this.resultsProvider, this.diagnosticCollection, this.statusBarItem, this.outputChannel);
        this.initialize(context);
    }
    async initialize(context) {
        // Register commands
        context.subscriptions.push(vscode.commands.registerCommand('decoyable.scanWorkspace', this.scanWorkspace.bind(this)), vscode.commands.registerCommand('decoyable.scanFile', this.scanFile.bind(this)), vscode.commands.registerCommand('decoyable.fixAll', this.fixAll.bind(this)), vscode.commands.registerCommand('decoyable.fixIssue', this.fixIssue.bind(this)), vscode.commands.registerCommand('decoyable.showResults', this.showResults.bind(this)), vscode.commands.registerCommand('decoyable.configure', this.configure.bind(this)), vscode.commands.registerCommand('decoyable.refreshResults', this.refreshResults.bind(this)));
        // Register tree view
        context.subscriptions.push(vscode.window.registerTreeDataProvider('decoyableResults', this.resultsProvider));
        // Register code actions provider
        context.subscriptions.push(vscode.languages.registerCodeActionsProvider(['python', 'javascript', 'typescript', 'java', 'cpp', 'c', 'php', 'ruby', 'go', 'rust'], new DecoyableCodeActionProvider(), { providedCodeActionKinds: [vscode.CodeActionKind.QuickFix] }));
        // Set up file watchers for real-time scanning
        this.setupFileWatchers(context);
        // Initialize status bar
        this.updateStatusBar();
        // Auto-scan on startup if configured
        const config = vscode.workspace.getConfiguration('decoyable');
        if (config.get('scanOnOpen', false) && vscode.workspace.workspaceFolders) {
            setTimeout(() => this.scanWorkspace(), 2000);
        }
    }
    setupFileWatchers(context) {
        const config = vscode.workspace.getConfiguration('decoyable');
        if (config.get('scanOnSave', true)) {
            const watcher = vscode.workspace.onDidSaveTextDocument(async (document) => {
                if (this.shouldScanFile(document)) {
                    await this.scanFileInternal(document.uri);
                }
            });
            context.subscriptions.push(watcher);
        }
    }
    shouldScanFile(document) {
        const supportedExtensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.php', '.rb', '.go', '.rs'];
        return supportedExtensions.includes(path.extname(document.fileName));
    }
    async scanWorkspace() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'DECOYABLE Security Scan',
            cancellable: true
        }, async (progress, token) => {
            try {
                progress.report({ increment: 0, message: 'Initializing scan...' });
                const startTime = Date.now();
                const result = await this.runDecoyableScan(['scan', 'all', '--path', workspaceFolder.uri.fsPath, '--format', 'json']);
                const duration = Date.now() - startTime;
                progress.report({ increment: 100, message: 'Processing results...' });
                const scanResult = {
                    timestamp: new Date().toISOString(),
                    duration,
                    filesScanned: result.filesScanned || 0,
                    issues: result.issues || [],
                    summary: result.summary || { critical: 0, high: 0, medium: 0, low: 0, info: 0 }
                };
                this.results = scanResult;
                this.updateDiagnostics();
                this.resultsProvider.refresh();
                this.updateStatusBar();
                // Show notification
                const config = vscode.workspace.getConfiguration('decoyable');
                if (config.get('showNotifications', true)) {
                    const totalIssues = scanResult.issues.length;
                    if (totalIssues > 0) {
                        const criticalCount = scanResult.summary.critical;
                        const highCount = scanResult.summary.high;
                        let message = `Found ${totalIssues} security issues`;
                        if (criticalCount > 0 || highCount > 0) {
                            message += ` (${criticalCount} critical, ${highCount} high)`;
                        }
                        vscode.window.showWarningMessage(message, 'View Results').then((selection) => {
                            if (selection === 'View Results') {
                                vscode.commands.executeCommand('decoyable.showResults');
                            }
                        });
                    }
                    else {
                        vscode.window.showInformationMessage('✅ No security issues found!');
                    }
                }
                this.logToOutput(`Scan completed in ${duration}ms. Found ${scanResult.issues.length} issues.`);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Scan failed: ${error}`);
                this.logToOutput(`Scan error: ${error}`);
            }
        });
    }
    async scanFile() {
        const activeEditor = vscode.window.activeTextEditor;
        if (!activeEditor) {
            vscode.window.showErrorMessage('No active file to scan');
            return;
        }
        await this.scanFileInternal(activeEditor.document.uri);
    }
    async scanFileInternal(uri) {
        try {
            const result = await this.runDecoyableScan(['scan', 'all', '--path', uri.fsPath, '--format', 'json']);
            const scanResult = {
                timestamp: new Date().toISOString(),
                duration: 0,
                filesScanned: 1,
                issues: result.issues || [],
                summary: result.summary || { critical: 0, high: 0, medium: 0, low: 0, info: 0 }
            };
            // Update existing results or create new ones
            if (this.results) {
                // Merge with existing results
                const existingIssues = this.results.issues.filter(issue => issue.file !== uri.fsPath);
                this.results.issues = [...existingIssues, ...scanResult.issues];
                this.results.filesScanned = new Set([...this.results.issues.map(i => i.file)]).size;
                this.results.summary = this.calculateSummary(this.results.issues);
            }
            else {
                this.results = scanResult;
            }
            this.updateDiagnostics();
            this.resultsProvider.refresh();
            this.updateStatusBar();
            const fileIssues = scanResult.issues.length;
            if (fileIssues > 0) {
                vscode.window.showWarningMessage(`Found ${fileIssues} issues in ${path.basename(uri.fsPath)}`);
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`File scan failed: ${error}`);
        }
    }
    async fixAll() {
        if (!this.results || this.results.issues.length === 0) {
            vscode.window.showInformationMessage('No issues to fix');
            return;
        }
        const config = vscode.workspace.getConfiguration('decoyable');
        const autoFix = config.get('autoFix', false);
        if (!autoFix) {
            const selection = await vscode.window.showWarningMessage(`Apply fixes for ${this.results.issues.length} issues?`, { modal: true }, 'Apply All', 'Review First');
            if (selection !== 'Apply All') {
                vscode.commands.executeCommand('decoyable.showResults');
                return;
            }
        }
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Applying DECOYABLE Fixes',
            cancellable: true
        }, async (progress, token) => {
            try {
                const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
                if (!workspaceFolder)
                    return;
                progress.report({ increment: 0, message: 'Preparing fixes...' });
                // Create backup
                await this.createBackup();
                // Apply fixes
                const result = await this.runDecoyableCommand([
                    'fix',
                    '--scan-results', this.getTempResultsFile(),
                    '--auto-approve',
                    '--confirm'
                ]);
                progress.report({ increment: 100, message: 'Fixes applied successfully' });
                vscode.window.showInformationMessage('✅ Fixes applied successfully!');
                // Re-scan to verify
                setTimeout(() => this.scanWorkspace(), 1000);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Fix failed: ${error}`);
            }
        });
    }
    async fixIssue(issue) {
        if (!issue) {
            const selectedIssue = await this.selectIssue();
            if (!selectedIssue)
                return;
            issue = selectedIssue;
        }
        try {
            const result = await this.runDecoyableCommand([
                'fix',
                '--file', issue.file,
                '--type', issue.type,
                '--ai-help',
                '--confirm'
            ]);
            vscode.window.showInformationMessage(`✅ Fixed: ${issue.title}`);
            // Update results
            if (this.results) {
                this.results.issues = this.results.issues.filter(i => i.id !== issue.id);
                this.results.summary = this.calculateSummary(this.results.issues);
                this.updateDiagnostics();
                this.resultsProvider.refresh();
                this.updateStatusBar();
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`Fix failed: ${error}`);
        }
    }
    async selectIssue() {
        if (!this.results || this.results.issues.length === 0) {
            return undefined;
        }
        const items = this.results.issues.map(issue => ({
            label: `${this.getSeverityIcon(issue.severity)} ${issue.title}`,
            description: `${issue.file}:${issue.line}`,
            detail: issue.description,
            issue
        }));
        const selection = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select issue to fix'
        });
        return selection?.issue;
    }
    async showResults() {
        const panel = vscode.window.createWebviewPanel('decoyableResults', 'DECOYABLE Scan Results', vscode.ViewColumn.One, { enableScripts: true });
        panel.webview.html = this.generateResultsHtml();
    }
    async configure() {
        const config = vscode.workspace.getConfiguration('decoyable');
        const items = [
            {
                label: 'Python Path',
                description: config.get('pythonPath', 'python'),
                detail: 'Path to Python executable'
            },
            {
                label: 'CLI Path',
                description: config.get('cliPath', '') || 'bundled',
                detail: 'Path to DECOYABLE CLI'
            },
            {
                label: 'Scan on Save',
                description: config.get('scanOnSave', true) ? 'Enabled' : 'Disabled',
                detail: 'Auto-scan files when saved'
            },
            {
                label: 'Auto Fix',
                description: config.get('autoFix', false) ? 'Enabled' : 'Disabled',
                detail: 'Automatically apply safe fixes'
            }
        ];
        const selection = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select setting to configure'
        });
        if (selection) {
            // Open settings
            vscode.commands.executeCommand('workbench.action.openSettings', 'decoyable');
        }
    }
    async refreshResults() {
        this.resultsProvider.refresh();
    }
    async runDecoyableScan(args) {
        const config = vscode.workspace.getConfiguration('decoyable');
        const pythonPath = config.get('pythonPath', 'python');
        const cliPath = config.get('cliPath', '');
        let command;
        if (cliPath) {
            command = `"${cliPath}" ${args.join(' ')}`;
        }
        else {
            // Use main.py from workspace
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder)
                throw new Error('No workspace folder');
            const mainPyPath = path.join(workspaceFolder.uri.fsPath, 'main.py');
            command = `"${pythonPath}" "${mainPyPath}" ${args.join(' ')}`;
        }
        this.logToOutput(`Running: ${command}`);
        const { stdout, stderr } = await execAsync(command, {
            cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath,
            timeout: 300000 // 5 minutes
        });
        if (stderr) {
            this.logToOutput(`Stderr: ${stderr}`);
        }
        try {
            return JSON.parse(stdout);
        }
        catch (error) {
            // If not JSON, try to parse as text output
            this.logToOutput(`Raw output: ${stdout}`);
            return this.parseTextOutput(stdout);
        }
    }
    async runDecoyableCommand(args) {
        const config = vscode.workspace.getConfiguration('decoyable');
        const pythonPath = config.get('pythonPath', 'python');
        const cliPath = config.get('cliPath', '');
        let command;
        if (cliPath) {
            command = `"${cliPath}" ${args.join(' ')}`;
        }
        else {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder)
                throw new Error('No workspace folder');
            const mainPyPath = path.join(workspaceFolder.uri.fsPath, 'main.py');
            command = `"${pythonPath}" "${mainPyPath}" ${args.join(' ')}`;
        }
        this.logToOutput(`Running: ${command}`);
        const { stdout, stderr } = await execAsync(command, {
            cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath,
            timeout: 300000
        });
        if (stderr) {
            this.logToOutput(`Stderr: ${stderr}`);
        }
        return stdout;
    }
    parseTextOutput(output) {
        // Parse text output into structured format
        const lines = output.split('\n');
        const issues = [];
        let currentIssue = null;
        for (const line of lines) {
            if (line.includes('[CRITICAL]') || line.includes('[HIGH]') || line.includes('[MEDIUM]') || line.includes('[LOW]')) {
                if (currentIssue) {
                    issues.push(currentIssue);
                }
                const severityMatch = line.match(/\[(\w+)\]/);
                const severity = severityMatch && severityMatch[1] ? severityMatch[1].toLowerCase() : 'medium';
                const typeMatch = line.match(/(\w+)\s*-\s*(.+)/);
                const type = typeMatch && typeMatch[1] ? typeMatch[1].toLowerCase() : 'sast';
                currentIssue = {
                    id: `issue_${issues.length + 1}`,
                    file: '',
                    line: 0,
                    column: 0,
                    severity,
                    type,
                    title: line.trim(),
                    description: ''
                };
            }
            else if (currentIssue && line.includes('Code snippet:')) {
                // Next line should have the code
                currentIssue.code = '';
            }
            else if (currentIssue && currentIssue.code === '') {
                currentIssue.code = line.trim();
            }
        }
        if (currentIssue) {
            issues.push(currentIssue);
        }
        return {
            issues,
            summary: this.calculateSummary(issues),
            filesScanned: 1
        };
    }
    calculateSummary(issues) {
        return {
            critical: issues.filter(i => i.severity === 'critical').length,
            high: issues.filter(i => i.severity === 'high').length,
            medium: issues.filter(i => i.severity === 'medium').length,
            low: issues.filter(i => i.severity === 'low').length,
            info: issues.filter(i => i.severity === 'info').length
        };
    }
    updateDiagnostics() {
        this.diagnosticCollection.clear();
        if (!this.results)
            return;
        const diagnosticsByFile = {};
        for (const issue of this.results.issues) {
            if (!diagnosticsByFile[issue.file]) {
                diagnosticsByFile[issue.file] = [];
            }
            const range = new vscode.Range(Math.max(0, issue.line - 1), Math.max(0, issue.column - 1), Math.max(0, issue.line - 1), 1000 // End of line
            );
            const severity = this.mapSeverityToDiagnostic(issue.severity);
            const diagnostic = new vscode.Diagnostic(range, `${issue.title}: ${issue.description}`, severity);
            diagnostic.source = 'DECOYABLE';
            diagnostic.code = issue.id;
            diagnosticsByFile[issue.file].push(diagnostic);
        }
        for (const [file, diagnostics] of Object.entries(diagnosticsByFile)) {
            const uri = vscode.Uri.file(file);
            this.diagnosticCollection.set(uri, diagnostics);
        }
    }
    mapSeverityToDiagnostic(severity) {
        switch (severity) {
            case 'critical': return vscode.DiagnosticSeverity.Error;
            case 'high': return vscode.DiagnosticSeverity.Error;
            case 'medium': return vscode.DiagnosticSeverity.Warning;
            case 'low': return vscode.DiagnosticSeverity.Information;
            case 'info': return vscode.DiagnosticSeverity.Hint;
            default: return vscode.DiagnosticSeverity.Warning;
        }
    }
    updateStatusBar() {
        if (!this.results) {
            this.statusBarItem.text = '$(shield) DECOYABLE';
            this.statusBarItem.tooltip = 'No scan results yet';
        }
        else {
            const total = this.results.issues.length;
            const critical = this.results.summary.critical;
            const high = this.results.summary.high;
            if (total === 0) {
                this.statusBarItem.text = '$(shield-check) DECOYABLE: Clean';
                this.statusBarItem.tooltip = 'No security issues found';
                this.statusBarItem.color = undefined;
            }
            else {
                const criticalText = critical > 0 ? `${critical} critical` : '';
                const highText = high > 0 ? `${high} high` : '';
                const issuesText = [criticalText, highText].filter(Boolean).join(', ') || `${total} issues`;
                this.statusBarItem.text = `$(shield-x) DECOYABLE: ${issuesText}`;
                this.statusBarItem.tooltip = `${total} security issues (${this.results.filesScanned} files scanned)`;
                this.statusBarItem.color = critical > 0 ? new vscode.ThemeColor('errorForeground') : new vscode.ThemeColor('warningForeground');
            }
        }
        this.statusBarItem.show();
    }
    getSeverityIcon(severity) {
        switch (severity) {
            case 'critical': return '🚨';
            case 'high': return '🔴';
            case 'medium': return '🟡';
            case 'low': return '🔵';
            case 'info': return 'ℹ️';
            default: return '⚠️';
        }
    }
    async createBackup() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder)
            return;
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const backupDir = path.join(workspaceFolder.uri.fsPath, `.decoyable-backup-${timestamp}`);
        // Create backup using git
        try {
            await execAsync('git add .', { cwd: workspaceFolder.uri.fsPath });
            await execAsync(`git commit -m "Backup before DECOYABLE fixes - ${timestamp}" --allow-empty`, {
                cwd: workspaceFolder.uri.fsPath
            });
        }
        catch (error) {
            // Git might not be available, continue without backup
            this.logToOutput('Git backup failed, continuing without backup');
        }
    }
    getTempResultsFile() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder)
            throw new Error('No workspace');
        const tempFile = path.join(workspaceFolder.uri.fsPath, '.decoyable-temp-results.json');
        if (this.results) {
            fs.writeFileSync(tempFile, JSON.stringify(this.results, null, 2));
        }
        return tempFile;
    }
    generateResultsHtml() {
        if (!this.results) {
            return '<html><body><h2>No scan results available</h2></body></html>';
        }
        const issues = this.results.issues;
        const summary = this.results.summary;
        return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>DECOYABLE Scan Results</title>
        <style>
          body { font-family: var(--vscode-font-family); margin: 20px; }
          .summary { background: var(--vscode-editorWidget-background); padding: 15px; border-radius: 5px; margin-bottom: 20px; }
          .issue { margin: 10px 0; padding: 10px; border-left: 4px solid; }
          .critical { border-left-color: #f44747; background: rgba(244, 71, 71, 0.1); }
          .high { border-left-color: #ffcc00; background: rgba(255, 204, 0, 0.1); }
          .medium { border-left-color: #ffa500; background: rgba(255, 165, 0, 0.1); }
          .low { border-left-color: #3794ff; background: rgba(55, 148, 255, 0.1); }
          .info { border-left-color: #888; background: rgba(136, 136, 136, 0.1); }
          .code { font-family: monospace; background: var(--vscode-textBlockQuote-background); padding: 5px; margin: 5px 0; }
        </style>
      </head>
      <body>
        <h1>🔒 DECOYABLE Security Scan Results</h1>

        <div class="summary">
          <h2>📊 Summary</h2>
          <p><strong>Files Scanned:</strong> ${this.results.filesScanned}</p>
          <p><strong>Scan Duration:</strong> ${this.results.duration}ms</p>
          <p><strong>Total Issues:</strong> ${issues.length}</p>
          <ul>
            <li>🚨 Critical: ${summary.critical}</li>
            <li>🔴 High: ${summary.high}</li>
            <li>🟡 Medium: ${summary.medium}</li>
            <li>🔵 Low: ${summary.low}</li>
            <li>ℹ️ Info: ${summary.info}</li>
          </ul>
        </div>

        <h2>🔍 Issues Found</h2>
        ${issues.map(issue => `
          <div class="issue ${issue.severity}">
            <h3>${this.getSeverityIcon(issue.severity)} ${issue.title}</h3>
            <p><strong>File:</strong> ${issue.file}:${issue.line}</p>
            <p><strong>Type:</strong> ${issue.type}</p>
            <p>${issue.description}</p>
            ${issue.recommendation ? `<p><strong>Recommendation:</strong> ${issue.recommendation}</p>` : ''}
            ${issue.code ? `<div class="code">${issue.code}</div>` : ''}
          </div>
        `).join('')}

        ${issues.length === 0 ? '<p>✅ No security issues found!</p>' : ''}
      </body>
      </html>
    `;
    }
    logToOutput(message) {
        this.outputChannel.appendLine(`[${new Date().toISOString()}] ${message}`);
    }
}
class ResultsTreeProvider {
    constructor() {
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    dispose() {
        this._onDidChangeTreeData.dispose();
    }
    getTreeItem(element) {
        if (typeof element === 'string') {
            // This is a category header
            const item = new vscode.TreeItem(element, vscode.TreeItemCollapsibleState.Expanded);
            item.iconPath = new vscode.ThemeIcon('folder');
            return item;
        }
        else {
            // This is a security issue
            const item = new vscode.TreeItem(`${element.title} (${element.file}:${element.line})`, vscode.TreeItemCollapsibleState.None);
            item.tooltip = `${element.description}\n\nRecommendation: ${element.recommendation || 'N/A'}`;
            item.command = {
                command: 'decoyable.fixIssue',
                title: 'Fix Issue',
                arguments: [element]
            };
            // Set icon based on severity
            switch (element.severity) {
                case 'critical':
                    item.iconPath = new vscode.ThemeIcon('error', new vscode.ThemeColor('errorForeground'));
                    break;
                case 'high':
                    item.iconPath = new vscode.ThemeIcon('warning', new vscode.ThemeColor('errorForeground'));
                    break;
                case 'medium':
                    item.iconPath = new vscode.ThemeIcon('warning', new vscode.ThemeColor('warningForeground'));
                    break;
                case 'low':
                    item.iconPath = new vscode.ThemeIcon('info', new vscode.ThemeColor('infoForeground'));
                    break;
                case 'info':
                    item.iconPath = new vscode.ThemeIcon('info', new vscode.ThemeColor('infoForeground'));
                    break;
            }
            item.contextValue = 'issue';
            return item;
        }
    }
    getChildren(element) {
        // Get the extension instance (this is a bit hacky but works for this demo)
        const extension = global.decoyableExtension;
        if (!extension || !extension.results) {
            return Promise.resolve([]);
        }
        if (!element) {
            // Root level - return categories
            const categories = [];
            const issues = extension.results.issues;
            if (issues.some((i) => i.severity === 'critical'))
                categories.push('🚨 Critical Issues');
            if (issues.some((i) => i.severity === 'high'))
                categories.push('🔴 High Priority');
            if (issues.some((i) => i.severity === 'medium'))
                categories.push('🟡 Medium Priority');
            if (issues.some((i) => i.severity === 'low'))
                categories.push('🔵 Low Priority');
            if (issues.some((i) => i.severity === 'info'))
                categories.push('ℹ️ Informational');
            return Promise.resolve(categories);
        }
        else if (typeof element === 'string') {
            // Category level - return issues in this category
            const severity = element.includes('Critical') ? 'critical' :
                element.includes('High') ? 'high' :
                    element.includes('Medium') ? 'medium' :
                        element.includes('Low') ? 'low' : 'info';
            const issues = extension.results.issues.filter((i) => i.severity === severity);
            return Promise.resolve(issues);
        }
        return Promise.resolve([]);
    }
}
class DecoyableCodeActionProvider {
    provideCodeActions(document, range, context, token) {
        const actions = [];
        // Check if there are diagnostics at this position
        const diagnostics = context.diagnostics.filter((d) => d.source === 'DECOYABLE');
        for (const diagnostic of diagnostics) {
            if (diagnostic.range.contains(range.start)) {
                const action = new vscode.CodeAction('Fix with DECOYABLE', vscode.CodeActionKind.QuickFix);
                action.command = {
                    command: 'decoyable.fixIssue',
                    title: 'Fix Issue',
                    arguments: [diagnostic.code] // This would need to be mapped to the actual issue
                };
                action.diagnostics = [diagnostic];
                actions.push(action);
            }
        }
        return actions;
    }
}
// Extension activation
function activate(context) {
    const extension = new DecoyableExtension(context);
    global.decoyableExtension = extension;
    vscode.window.showInformationMessage('🔒 DECOYABLE Security Scanner activated!');
    // Set context for when clauses
    vscode.commands.executeCommand('setContext', 'decoyable.hasResults', false);
    vscode.commands.executeCommand('setContext', 'decoyable.hasSelectedIssue', false);
}
exports.activate = activate;
// Extension deactivation
function deactivate() {
    vscode.window.showInformationMessage('🔒 DECOYABLE Security Scanner deactivated.');
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map