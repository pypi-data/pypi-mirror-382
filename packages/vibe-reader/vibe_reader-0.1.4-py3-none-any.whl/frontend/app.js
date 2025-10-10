// UI Elements
const tmuxBtn = document.getElementById('tmuxBtn');
const filesBtn = document.getElementById('filesBtn');
const configBtn = document.getElementById('configBtn');
const tmuxView = document.getElementById('tmuxView');
const filesView = document.getElementById('filesView');
const configView = document.getElementById('configView');
const refreshBtn = document.getElementById('refreshBtn');
const toggleSidebar = document.getElementById('toggleSidebar');
const autoScrollBtn = document.getElementById('autoScrollBtn');
const autoRefreshBtn = document.getElementById('autoRefreshBtn');
const tmuxControls = document.querySelector('.tmux-controls');

// Config elements
const scrollbackLinesInput = document.getElementById('scrollbackLines');
const fontSizeSelect = document.getElementById('fontSize');
const refreshIntervalSelect = document.getElementById('refreshInterval');
const refreshIdleTimeoutSelect = document.getElementById('refreshIdleTimeout');
const enableSyntaxHighlightingCheckbox = document.getElementById('enableSyntaxHighlighting');
const saveConfigBtn = document.getElementById('saveConfig');

// Sidebar elements
const tmuxSidebar = document.getElementById('tmuxSidebar');
const filesSidebar = document.getElementById('filesSidebar');

// Tmux elements
const tmuxTree = document.getElementById('tmuxTree');
const tmuxContent = document.getElementById('tmuxContent');
const pageUpTmux = document.getElementById('pageUpTmux');
const pageDownTmux = document.getElementById('pageDownTmux');

// Files elements
const filePath = document.getElementById('filePath');
const loadFiles = document.getElementById('loadFiles');
const fileList = document.getElementById('fileList');
const fileContentContainer = document.getElementById('fileContentContainer');
const fileContent = document.getElementById('fileContent');
const pageUpFiles = document.getElementById('pageUpFiles');
const pageDownFiles = document.getElementById('pageDownFiles');

// Current view state
const DEFAULT_REFRESH_INTERVAL = 5;
let currentView = 'tmux';
let selectedPane = null;
let selectedFile = null;
let autoScroll = true;
let sidebarCollapsed = false;
let refreshIntervalId = null;
let autoRefreshEnabled = false;
let currentRefreshInterval = DEFAULT_REFRESH_INTERVAL;
let idleTimeoutId = null;
let currentIdleTimeoutMinutes = 10;
let toastTimeoutId = null;

function clearTmuxSelectionHighlights() {
    if (!tmuxTree) {
        return;
    }

    tmuxTree
        .querySelectorAll(
            '.tree-session-name.active, .tree-window-name.active, .tree-pane.active'
        )
        .forEach((element) => element.classList.remove('active'));
}

function applyTmuxSelectionHighlight() {
    if (!tmuxTree || !selectedPane) {
        return false;
    }

    const sessionName = String(selectedPane.session);
    const windowIndex = String(selectedPane.window);
    const paneValue = selectedPane.pane;
    const paneIndex =
        paneValue === undefined || paneValue === null ? null : String(paneValue);

    const sessionEl = Array.from(tmuxTree.querySelectorAll('.tree-session-name')).find(
        (element) => element.dataset.sessionName === sessionName
    );
    const windowEl = Array.from(tmuxTree.querySelectorAll('.tree-window-name')).find(
        (element) =>
            element.dataset.sessionName === sessionName &&
            element.dataset.windowIndex === windowIndex
    );

    if (!sessionEl || !windowEl) {
        return false;
    }

    clearTmuxSelectionHighlights();
    sessionEl.classList.add('active');
    windowEl.classList.add('active');

    if (paneIndex !== null) {
        const paneEl = Array.from(tmuxTree.querySelectorAll('.tree-pane')).find(
            (element) =>
                element.dataset.sessionName === sessionName &&
                element.dataset.windowIndex === windowIndex &&
                element.dataset.paneIndex === paneIndex
        );

        if (paneEl) {
            paneEl.classList.add('active');
        }
    }

    return true;
}

// Sidebar toggle
toggleSidebar.addEventListener('click', () => {
    sidebarCollapsed = !sidebarCollapsed;
    if (currentView === 'tmux') {
        tmuxSidebar.classList.toggle('collapsed', sidebarCollapsed);
    } else {
        filesSidebar.classList.toggle('collapsed', sidebarCollapsed);
    }
});

// Auto-scroll toggle
autoScrollBtn.addEventListener('click', () => {
    autoScroll = !autoScroll;
    autoScrollBtn.classList.toggle('active', autoScroll);
});

// Auto-refresh toggle
autoRefreshBtn.addEventListener('click', () => {
    if (autoRefreshEnabled) {
        disableAutoRefresh();
    } else {
        enableAutoRefresh();
    }
});

// Page up/down for tmux
pageUpTmux.addEventListener('click', () => {
    // Disable auto-scroll when manually scrolling
    autoScroll = false;
    autoScrollBtn.classList.remove('active');

    const target = Math.max(tmuxContent.scrollTop - tmuxContent.clientHeight * 0.9, 0);
    tmuxContent.scrollTop = target;
});

pageDownTmux.addEventListener('click', () => {
    // Disable auto-scroll when manually scrolling
    autoScroll = false;
    autoScrollBtn.classList.remove('active');

    const maxScrollTop = Math.max(tmuxContent.scrollHeight - tmuxContent.clientHeight, 0);
    const target = Math.min(tmuxContent.scrollTop + tmuxContent.clientHeight * 0.9, maxScrollTop);
    tmuxContent.scrollTop = target;
});

// Page up/down for files
pageUpFiles.addEventListener('click', () => {
    fileContentContainer.scrollTop = Math.max(
        fileContentContainer.scrollTop - fileContentContainer.clientHeight * 0.9,
        0
    );
});

pageDownFiles.addEventListener('click', () => {
    const maxScrollTop = Math.max(
        fileContentContainer.scrollHeight - fileContentContainer.clientHeight,
        0
    );
    fileContentContainer.scrollTop = Math.min(
        fileContentContainer.scrollTop + fileContentContainer.clientHeight * 0.9,
        maxScrollTop
    );
});

// View switching helper
function setView(view) {
    currentView = view;
    markInteraction();

    // Update view visibility
    tmuxView.classList.toggle('active', view === 'tmux');
    filesView.classList.toggle('active', view === 'files');
    configView.classList.toggle('active', view === 'config');

    // Update button states
    tmuxBtn.classList.toggle('active', view === 'tmux');
    filesBtn.classList.toggle('active', view === 'files');
    configBtn.classList.toggle('active', view === 'config');

    updateTmuxControlsVisibility();

    // Handle sidebar state
    if (view === 'tmux') {
        tmuxSidebar.classList.toggle('collapsed', sidebarCollapsed);
        filesSidebar.classList.remove('collapsed');
        loadTmuxTree();
    } else if (view === 'files') {
        sidebarCollapsed = false;
        filesSidebar.classList.remove('collapsed');
        tmuxSidebar.classList.remove('collapsed');
        loadFileList();
    } else if (view === 'config') {
        tmuxSidebar.classList.remove('collapsed');
        filesSidebar.classList.remove('collapsed');
    }

    syncAutoRefreshState();
}

// View switching
tmuxBtn.addEventListener('click', () => setView('tmux'));
filesBtn.addEventListener('click', () => setView('files'));
configBtn.addEventListener('click', () => setView('config'));

// Shared fetch helper
async function fetchJSON(url, errorContext) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Failed to ${errorContext}`);
        return await response.json();
    } catch (error) {
        throw new Error(`${errorContext}: ${error.message}`);
    }
}

// Load tmux tree (sessions > windows > panes)
async function loadTmuxTree() {
    try {
        const tree = await fetchJSON('/api/tmux/tree', 'load tmux tree');
        tmuxTree.innerHTML = '';

        if (tree.length === 0) {
            selectedPane = null;
            tmuxTree.innerHTML = '<div style="padding: 20px;">No tmux sessions found</div>';
            tmuxContent.textContent = '';
            return;
        }

        tree.forEach(session => {
            const sessionDiv = document.createElement('div');
            sessionDiv.className = 'tree-session';

            const sessionName = document.createElement('div');
            sessionName.className = 'tree-session-name';
            sessionName.textContent = session.name;
            sessionName.dataset.sessionName = session.name;
            sessionDiv.appendChild(sessionName);

            session.windows.forEach(window => {
                const windowDiv = document.createElement('div');
                windowDiv.className = 'tree-window';

                // Mark single-pane windows
                if (window.panes.length === 1) {
                    windowDiv.classList.add('single-pane');
                }

                const windowName = document.createElement('div');
                windowName.className = 'tree-window-name';
                windowName.textContent = `${window.index}: ${window.name}`;
                windowName.dataset.sessionName = session.name;
                windowName.dataset.windowIndex = window.index;
                windowDiv.appendChild(windowName);

                // For single-pane windows, make window name clickable
                if (window.panes.length === 1) {
                    windowName.onclick = () => {
                        markInteraction();
                        selectedPane = {
                            session: session.name,
                            window: window.index,
                            pane: window.panes[0].index
                        };
                        loadTmuxContent();
                        applyTmuxSelectionHighlight();
                    };
                } else {
                    // Multiple panes - show them
                    window.panes.forEach(pane => {
                        const paneDiv = document.createElement('div');
                        paneDiv.className = 'tree-pane';
                        paneDiv.textContent = `Pane ${pane.index}${pane.active ? ' *' : ''}`;
                        paneDiv.dataset.sessionName = session.name;
                        paneDiv.dataset.windowIndex = window.index;
                        paneDiv.dataset.paneIndex = pane.index;

                        paneDiv.onclick = () => {
                            markInteraction();
                            selectedPane = {
                                session: session.name,
                                window: window.index,
                                pane: pane.index
                            };
                            loadTmuxContent();
                            applyTmuxSelectionHighlight();
                        };

                        windowDiv.appendChild(paneDiv);
                    });
                }

                sessionDiv.appendChild(windowDiv);
            });

            tmuxTree.appendChild(sessionDiv);
        });

        let selectionHighlighted = false;

        if (selectedPane) {
            selectionHighlighted = applyTmuxSelectionHighlight();
            if (!selectionHighlighted) {
                selectedPane = null;
            }
        }

        if (!selectionHighlighted) {
            for (const session of tree) {
                const firstWindow = session.windows.find(win => win.panes.length > 0);
                if (!firstWindow) {
                    continue;
                }

                const firstPane = firstWindow.panes[0];
                selectedPane = {
                    session: session.name,
                    window: firstWindow.index,
                    pane: firstPane.index
                };
                loadTmuxContent();
                applyTmuxSelectionHighlight();
                selectionHighlighted = true;
                break;
            }
        }

        if (!selectionHighlighted) {
            clearTmuxSelectionHighlights();
            tmuxContent.textContent = '';
        }
    } catch (error) {
        tmuxTree.innerHTML = `<div style="padding: 20px; color: red;">Error: ${error.message}</div>`;
    }
}

// Load tmux pane content
async function loadTmuxContent() {
    if (!selectedPane) return;

    try {
        const { session, window, pane } = selectedPane;

        // Save current scroll position if auto-scroll is OFF
        const savedScrollTop = autoScroll ? null : tmuxContent.scrollTop;

        // Get scrollback config
        const config = JSON.parse(localStorage.getItem('vibeReaderConfig') || '{}');
        const scrollbackLines = config.scrollbackLines || 400;

        const data = await fetchJSON(
            `/api/tmux/pane/${encodeURIComponent(session)}/${encodeURIComponent(window)}/${encodeURIComponent(pane)}?scrollback=${scrollbackLines}`,
            'load pane content'
        );
        tmuxContent.textContent = data.content;

        // Smart scroll positioning
        if (autoScroll) {
            // Scroll to bottom
            tmuxContent.scrollTop = tmuxContent.scrollHeight;
        } else {
            // Restore previous scroll position
            if (savedScrollTop !== null) {
                tmuxContent.scrollTop = Math.min(savedScrollTop, Math.max(tmuxContent.scrollHeight - tmuxContent.clientHeight, 0));
            }
        }
    } catch (error) {
        tmuxContent.textContent = `Error: ${error.message}`;
    }
}

// Load files from directory
async function loadFileList() {
    try {
        const path = filePath.value || '.';

        const files = await fetchJSON(`/api/files?path=${encodeURIComponent(path)}`, 'load files');
        fileList.innerHTML = '';

        if (files.length === 0) {
            fileList.innerHTML = '<div class="file-item">Empty directory</div>';
            return;
        }

        // Add parent directory link if not at root
        if (path !== '.' && path !== '/') {
            const parentDiv = document.createElement('div');
            parentDiv.className = 'file-item dir';
            parentDiv.textContent = '.. (parent)';
            parentDiv.onclick = () => {
                const parentPath = path.split('/').slice(0, -1).join('/') || '.';
                filePath.value = parentPath;
                loadFileList();
            };
            fileList.appendChild(parentDiv);
        }

        files.forEach(file => {
            const fileDiv = document.createElement('div');
            fileDiv.className = file.is_dir ? 'file-item dir' : 'file-item';
            fileDiv.textContent = file.is_dir ? `📁 ${file.name}` : file.name;

            // Restore active state if this is the selected file
            if (!file.is_dir && selectedFile === file.path) {
                fileDiv.classList.add('active');
            }

            fileDiv.onclick = () => {
                if (file.is_dir) {
                    filePath.value = file.path;
                    loadFileList();
                    fileContent.innerHTML = '';
                    fileContentContainer.dataset.language = 'TEXT';
                    fileContentContainer.dataset.mode = 'PLAIN';
                    fileContentContainer.classList.remove('markdown-mode');
                    fileContentContainer.classList.add('code-mode');
                    selectedFile = null;
                } else {
                    loadFileContent(file.path);
                    selectedFile = file.path;

                    // Update active state
                    document.querySelectorAll('.file-item').forEach(f => f.classList.remove('active'));
                    fileDiv.classList.add('active');
                }
            };

            fileList.appendChild(fileDiv);
        });
    } catch (error) {
        fileList.innerHTML = `<div class="file-item" style="color: red;">Error: ${error.message}</div>`;
    }
}

// Load file content
async function loadFileContent(path) {
    try {
        const config = JSON.parse(localStorage.getItem('vibeReaderConfig') || '{}');
        const enableHighlighting = config.enableSyntaxHighlighting !== false; // default true for backward compat

        const data = await fetchJSON(
            `/api/files/content?path=${encodeURIComponent(path)}&highlight=${enableHighlighting}`,
            'load file'
        );
        renderFileContent(data);
        fileContentContainer.scrollTop = 0;
    } catch (error) {
        fileContentContainer.dataset.language = 'TEXT';
        fileContentContainer.dataset.mode = 'PLAIN';
        fileContentContainer.classList.remove('markdown-mode');
        fileContentContainer.classList.add('code-mode');
        fileContent.innerHTML = `<div class="code-line"><span class="line-code">${escapeHtml(error.message)}</span></div>`;
    }
}

// Refresh current view
function refreshTmux() {
    if (currentView !== 'tmux') {
        return;
    }

    if (selectedPane) {
        loadTmuxContent();
    } else {
        loadTmuxTree();
    }
}

function showToast(message) {
    if (!message) {
        return;
    }

    let toast = document.getElementById('toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.className = 'toast';
        document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.classList.add('visible');

    if (toastTimeoutId) {
        clearTimeout(toastTimeoutId);
    }

    toastTimeoutId = setTimeout(() => {
        toast.classList.remove('visible');
    }, 4000);
}

function stopAutoRefreshTimers() {
    if (refreshIntervalId) {
        clearInterval(refreshIntervalId);
        refreshIntervalId = null;
    }

    if (idleTimeoutId) {
        clearTimeout(idleTimeoutId);
        idleTimeoutId = null;
    }
}

function disableAutoRefresh(message) {
    autoRefreshEnabled = false;
    autoRefreshBtn.classList.remove('active');
    stopAutoRefreshTimers();

    if (message) {
        showToast(message);
    }
}

function enableAutoRefresh() {
    if (currentRefreshInterval <= 0) {
        showToast('Set a refresh interval above 0 seconds to enable auto refresh.');
        return;
    }

    autoRefreshEnabled = true;
    autoRefreshBtn.classList.add('active');
    markInteraction();
    syncAutoRefreshState();
}

function scheduleIdleTimeout() {
    if (idleTimeoutId) {
        clearTimeout(idleTimeoutId);
        idleTimeoutId = null;
    }

    if (!autoRefreshEnabled || currentIdleTimeoutMinutes <= 0 || currentView !== 'tmux') {
        return;
    }

    idleTimeoutId = setTimeout(() => {
        disableAutoRefresh(`Auto refresh paused after ${currentIdleTimeoutMinutes} minutes of inactivity.`);
    }, currentIdleTimeoutMinutes * 60 * 1000);
}

function markInteraction() {
    scheduleIdleTimeout();
}

function syncAutoRefreshState() {
    stopAutoRefreshTimers();

    if (!autoRefreshEnabled || currentRefreshInterval <= 0 || currentView !== 'tmux') {
        return;
    }

    if (document.visibilityState === 'hidden') {
        return;
    }

    refreshIntervalId = setInterval(() => {
        if (document.visibilityState === 'hidden') {
            return;
        }
        refreshTmux();
    }, currentRefreshInterval * 1000);

    scheduleIdleTimeout();
}

function updateTmuxControlsVisibility() {
    if (!tmuxControls) {
        return;
    }

    const showTmuxControls = currentView === 'tmux';
    tmuxControls.classList.toggle('hidden', !showTmuxControls);
}

// Event listeners
loadFiles.addEventListener('click', () => {
    markInteraction();
    loadFileList();
});
refreshBtn.addEventListener('click', () => {
    refreshTmux();
    markInteraction();
});

// Enter key support
filePath.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        markInteraction();
        loadFileList();
    }
});

function escapeHtml(value) {
    return value
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function renderFileContent({ render_mode: renderMode, html, metadata = {} }) {
    const mode = (renderMode || 'plain').toUpperCase();
    const label = (metadata.language || (mode === 'MARKDOWN' ? 'MARKDOWN' : 'TEXT')).toUpperCase();

    fileContentContainer.dataset.language = label;
    fileContentContainer.dataset.mode = mode;
    const isMarkdown = mode === 'MARKDOWN';
    fileContentContainer.classList.toggle('markdown-mode', isMarkdown);
    fileContentContainer.classList.toggle('code-mode', !isMarkdown);

    fileContent.innerHTML = html || '';
}

// Config management
function loadConfig() {
    const config = JSON.parse(localStorage.getItem('vibeReaderConfig') || '{}');
    const storedScrollback = Number.isInteger(config.scrollbackLines) ? config.scrollbackLines : 400;
    const storedFontSize = Number.isInteger(config.fontSize) ? config.fontSize : 14;
    const storedInterval = Number.isInteger(config.refreshInterval) && config.refreshInterval > 0
        ? config.refreshInterval
        : DEFAULT_REFRESH_INTERVAL;
    const storedIdleMinutes = Number.isInteger(config.refreshIdleMinutes) ? config.refreshIdleMinutes : 10;
    const storedEnableHighlighting = config.enableSyntaxHighlighting !== false; // default true for backward compat

    scrollbackLinesInput.value = storedScrollback;
    fontSizeSelect.value = storedFontSize;
    refreshIntervalSelect.value = String(storedInterval);
    enableSyntaxHighlightingCheckbox.checked = storedEnableHighlighting;

    if (Array.from(refreshIdleTimeoutSelect.options).some(opt => parseInt(opt.value, 10) === storedIdleMinutes)) {
        refreshIdleTimeoutSelect.value = String(storedIdleMinutes);
    } else {
        refreshIdleTimeoutSelect.value = '10';
    }

    document.querySelectorAll('.content-box').forEach(el => {
        el.style.fontSize = storedFontSize + 'px';
    });

    currentRefreshInterval = storedInterval;
    currentIdleTimeoutMinutes = parseInt(refreshIdleTimeoutSelect.value, 10);

    // Auto refresh always starts disabled; users must opt in via the toggle button.
    disableAutoRefresh();
    syncAutoRefreshState();
}

function saveConfig() {
    const refreshInterval = parseInt(refreshIntervalSelect.value, 10);
    const config = {
        scrollbackLines: parseInt(scrollbackLinesInput.value, 10),
        fontSize: parseInt(fontSizeSelect.value, 10),
        refreshInterval: Number.isNaN(refreshInterval) || refreshInterval <= 0
            ? DEFAULT_REFRESH_INTERVAL
            : refreshInterval,
        refreshIdleMinutes: parseInt(refreshIdleTimeoutSelect.value, 10),
        enableSyntaxHighlighting: enableSyntaxHighlightingCheckbox.checked
    };

    localStorage.setItem('vibeReaderConfig', JSON.stringify(config));

    // Apply font size
    document.querySelectorAll('.content-box').forEach(el => {
        el.style.fontSize = config.fontSize + 'px';
    });

    currentRefreshInterval = config.refreshInterval;
    currentIdleTimeoutMinutes = Number.isNaN(config.refreshIdleMinutes) ? currentIdleTimeoutMinutes : config.refreshIdleMinutes;

    if (autoRefreshEnabled) {
        syncAutoRefreshState();
    } else {
        stopAutoRefreshTimers();
    }

    autoRefreshBtn.classList.toggle('active', autoRefreshEnabled);

    markInteraction();

    alert('Settings saved!');

}

saveConfigBtn.addEventListener('click', saveConfig);

['pointerdown', 'keydown', 'touchstart'].forEach(eventName => {
    document.addEventListener(eventName, markInteraction);
});

window.addEventListener('wheel', markInteraction, { passive: true });

document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
        stopAutoRefreshTimers();
    } else {
        markInteraction();
        syncAutoRefreshState();
    }
});

// Initialize
updateTmuxControlsVisibility();
loadConfig();
loadTmuxTree();
