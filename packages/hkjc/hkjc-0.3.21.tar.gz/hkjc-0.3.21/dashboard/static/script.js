// ============================================================================
// HKJC Race Info - Main Application Script
// ============================================================================

// ============================================================================
// CONFIGURATION
// ============================================================================
const CONFIG = {
    ODDS_POLL_INTERVAL: 90000,        // 90 seconds
    REQUEST_DELAY: 100,                // Delay between sequential requests (ms)
    MAX_CONCURRENT_REQUESTS: 3,        // Max simultaneous requests
    REQUEST_TIMEOUT: 10000             // 10 second timeout
};

// ============================================================================
// STATE MANAGEMENT
// ============================================================================
const State = {
    caches: {
        runnerDetails: new Map(),
        speedmaps: new Map(),
        odds: new Map()
    },
    polling: {
        oddsIntervalId: null
    },
    activeRequests: new Set()
};

// ============================================================================
// REQUEST QUEUE MANAGER
// ============================================================================
const RequestQueue = {
    queue: [],
    activeCount: 0,
    
    /**
     * Add request to queue with priority support
     */
    async enqueue(requestFn, priority = 0) {
        return new Promise((resolve, reject) => {
            this.queue.push({ requestFn, resolve, reject, priority });
            this.queue.sort((a, b) => b.priority - a.priority);
            this.process();
        });
    },
    
    /**
     * Process queued requests with concurrency limit
     */
    async process() {
        if (this.activeCount >= CONFIG.MAX_CONCURRENT_REQUESTS || this.queue.length === 0) {
            return;
        }
        
        const { requestFn, resolve, reject } = this.queue.shift();
        this.activeCount++;
        
        try {
            const result = await requestFn();
            resolve(result);
        } catch (error) {
            reject(error);
        } finally {
            this.activeCount--;
            // Small delay between requests
            await this.delay(CONFIG.REQUEST_DELAY);
            this.process();
        }
    },
    
    /**
     * Clear all pending requests
     */
    clear() {
        this.queue = [];
    },
    
    /**
     * Helper delay function
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
};

// ============================================================================
// API MODULE - All server communication
// ============================================================================
const API = {
    /**
     * Generic fetch wrapper with timeout and error handling
     */
    async fetch(url, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.REQUEST_TIMEOUT);
        
        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    },
    
    /**
     * Fetch live odds for a race
     */
    async fetchOdds(raceNum) {
        return RequestQueue.enqueue(async () => {
            const response = await this.fetch(`/live_odds/${raceNum}`);
            return await response.json();
        }, 1); // Priority 1 for odds
    },
    
    /**
     * Fetch horse history
     */
    async fetchHorseHistory(horseNo, going, track, distance) {
        return RequestQueue.enqueue(async () => {
            const params = new URLSearchParams({
                going: going || '',
                track: track || '',
                dist: distance || ''
            });
            const response = await this.fetch(`/horse_info/${horseNo}?${params}`);
            return await response.text();
        }, 0); // Priority 0 for history
    },
    
    /**
     * Fetch speedmap
     */
    async fetchSpeedmap(raceNum) {
        return RequestQueue.enqueue(async () => {
            const response = await this.fetch(`/speedmap/${raceNum}`);
            return await response.text();
        }, 0); // Priority 0 for speedmaps
    }
};

// ============================================================================
// CACHE MODULE - Centralized caching logic
// ============================================================================
const Cache = {
    get(cacheName, key) {
        return State.caches[cacheName]?.get(key);
    },
    
    set(cacheName, key, value) {
        if (!State.caches[cacheName]) {
            State.caches[cacheName] = new Map();
        }
        State.caches[cacheName].set(key, value);
    },
    
    has(cacheName, key) {
        return State.caches[cacheName]?.has(key) || false;
    },
    
    clear(cacheName) {
        if (cacheName) {
            State.caches[cacheName]?.clear();
        } else {
            Object.values(State.caches).forEach(cache => cache.clear());
        }
    }
};

// ============================================================================
// ODDS MODULE - Live odds management
// ============================================================================
const Odds = {
    /**
     * Fetch and cache odds for a race
     */
    async load(raceNum) {
        try {
            const data = await API.fetchOdds(raceNum);
            Cache.set('odds', raceNum, data);
            this.updateDisplay(raceNum, data);
            return data;
        } catch (error) {
            console.error(`Error loading odds for race ${raceNum}:`, error);
            return null;
        }
    },
    
    /**
     * Update odds display in UI
     */
    updateDisplay(raceNum, oddsData) {
        if (!oddsData?.Raw || !oddsData?.Fit) return;
        
        // Update WIN columns
        this.updateCells(`.odds-win[data-race="${raceNum}"]`, oddsData.Raw.WIN);
        this.updateCells(`.odds-win-fit[data-race="${raceNum}"]`, oddsData.Fit.WIN);
        
        // Update PLA columns
        this.updateCells(`.odds-pla[data-race="${raceNum}"]`, oddsData.Raw.PLA);
        this.updateCells(`.odds-pla-fit[data-race="${raceNum}"]`, oddsData.Fit.PLA);
        
        // Update odds tables in expanded sections
        document.querySelectorAll(`.odds-table[data-race="${raceNum}"]`).forEach(table => {
            const horseNo = table.getAttribute('data-horse');
            this.updateOddsTable(table, horseNo, oddsData);
        });
    },
    
    /**
     * Helper to update cells with odds data
     */
    updateCells(selector, oddsData) {
        document.querySelectorAll(selector).forEach(cell => {
            const horseNo = cell.getAttribute('data-horse');
            const odds = oddsData?.[horseNo];
            if (odds !== undefined) {
                cell.textContent = odds;
            }
        });
    },
    
    /**
     * Update combination odds table
     */
    updateOddsTable(table, horseNo, oddsData) {
        const allHorses = Object.keys(oddsData.Raw.WIN || {}).sort((a, b) => parseInt(a) - parseInt(b));
        const otherHorses = allHorses.filter(h => h !== horseNo);
        const rows = table.querySelectorAll('tbody tr');
        
        if (rows.length < 4) return;
        
        const updateRow = (rowIndex, dataPath) => {
            const cells = rows[rowIndex].querySelectorAll('td:not(.odds-type-label)');
            otherHorses.forEach((h, idx) => {
                if (cells[idx]) {
                    const odds = dataPath[horseNo]?.[h] || dataPath[h]?.[horseNo];
                    cells[idx].textContent = odds !== undefined ? odds : '-';
                }
            });
        };
        
        updateRow(0, oddsData.Raw.QIN);     // QIN
        updateRow(1, oddsData.Fit.QIN);     // QIN (fit)
        updateRow(2, oddsData.Raw.QPL);     // QPL
        updateRow(3, oddsData.Fit.QPL);     // QPL (fit)
    },
    
    /**
     * Create HTML for odds section
     */
    createSection(raceNum, horseNo, oddsData) {
        if (!oddsData?.Raw || !oddsData?.Fit) return '';
        
        const allHorses = Object.keys(oddsData.Raw.WIN || {}).sort((a, b) => parseInt(a) - parseInt(b));
        const otherHorses = allHorses.filter(h => h !== horseNo);
        
        if (otherHorses.length === 0) return '';
        
        let html = '<div class="odds-table-container">';
        html += `<table class="odds-table" data-race="${raceNum}" data-horse="${horseNo}">`;
        html += '<thead><tr><th>Type</th>';
        
        // Header row
        otherHorses.forEach(h => html += `<th>vs ${h}</th>`);
        html += '</tr></thead><tbody>';
        
        // Data rows
        const createRow = (label, data) => {
            let row = `<tr><td class="odds-type-label">${label}</td>`;
            otherHorses.forEach(h => {
                const odds = data?.[horseNo]?.[h] || data?.[h]?.[horseNo];
                row += `<td>${odds !== undefined ? odds : '-'}</td>`;
            });
            return row + '</tr>';
        };
        
        html += createRow('QIN', oddsData.Raw.QIN);
        html += createRow('QIN (fit)', oddsData.Fit.QIN);
        html += createRow('QPL', oddsData.Raw.QPL);
        html += createRow('QPL (fit)', oddsData.Fit.QPL);
        
        html += '</tbody></table></div>';
        return html;
    },
    
    /**
     * Start polling for live odds
     */
    startPolling() {
        const allRaceNums = Array.from(document.querySelectorAll('.race-content'))
            .map(el => el.id.replace('race-', ''));
        
        // Initial load
        allRaceNums.forEach(raceNum => this.load(raceNum));
        
        // Clear existing interval
        if (State.polling.oddsIntervalId) {
            clearInterval(State.polling.oddsIntervalId);
        }
        
        // Set up polling
        State.polling.oddsIntervalId = setInterval(() => {
            allRaceNums.forEach(raceNum => this.load(raceNum));
        }, CONFIG.ODDS_POLL_INTERVAL);
    },
    
    /**
     * Stop polling
     */
    stopPolling() {
        if (State.polling.oddsIntervalId) {
            clearInterval(State.polling.oddsIntervalId);
            State.polling.oddsIntervalId = null;
        }
    }
};

// ============================================================================
// RUNNER DETAILS MODULE - Horse history and details
// ============================================================================
const RunnerDetails = {
    /**
     * Load runner details (history)
     */
    async load(raceNum, horseNo, going, track, distance) {
        const cacheKey = `${raceNum}-${horseNo}`;
        
        if (Cache.has('runnerDetails', cacheKey)) {
            return Cache.get('runnerDetails', cacheKey);
        }
        
        try {
            const html = await API.fetchHorseHistory(horseNo, going, track, distance);
            Cache.set('runnerDetails', cacheKey, html);
            return html;
        } catch (error) {
            console.error(`Error loading history for horse ${horseNo}:`, error);
            throw error;
        }
    },
    
    /**
     * Create complete details content (odds + history)
     */
    createContent(raceNum, runnerNo, horseNo, oddsData, historyHtml) {
        let content = '<div class="runner-details-wrapper">';
        
        // Add odds section if available
        if (oddsData) {
            content += '<div class="details-left">';
            content += Odds.createSection(raceNum, runnerNo, oddsData);
            content += '</div>';
        }
        
        // Add history section
        content += '<div class="details-right">';
        content += historyHtml;
        content += '</div>';
        
        content += '</div>';
        
        return content;
    },
    
    /**
     * Toggle single runner details
     */
    async toggle(rowElement, raceNum, horseNo, going, track, distance) {
        const detailsRow = document.getElementById(`runner-details-${raceNum}-${horseNo}`);
        const isExpanded = detailsRow.classList.contains('expanded');
        
        if (isExpanded) {
            // Collapse
            detailsRow.classList.remove('expanded');
            rowElement.querySelector('.expand-icon').classList.remove('expanded');
        } else {
            // Expand
            detailsRow.classList.add('expanded');
            rowElement.querySelector('.expand-icon').classList.add('expanded');
            
            const detailsContent = document.getElementById(`runner-details-content-${raceNum}-${horseNo}`);
            const runnerNo = rowElement.querySelector('.odds-win')?.getAttribute('data-horse') || horseNo;
            const oddsData = Cache.get('odds', raceNum);
            const cacheKey = `${raceNum}-${horseNo}`;
            
            if (!Cache.has('runnerDetails', cacheKey)) {
                // Show loading state
                detailsContent.innerHTML = this.createContent(
                    raceNum, runnerNo, horseNo, oddsData,
                    '<div class="details-loading">Loading race history...</div>'
                );
                
                try {
                    const historyHtml = await this.load(raceNum, horseNo, going, track, distance);
                    detailsContent.innerHTML = this.createContent(raceNum, runnerNo, horseNo, oddsData, historyHtml);
                } catch (error) {
                    detailsContent.innerHTML = this.createContent(
                        raceNum, runnerNo, horseNo, oddsData,
                        `<div class="details-loading error">Error loading race history: ${error.message}</div>`
                    );
                }
            } else {
                const historyHtml = Cache.get('runnerDetails', cacheKey);
                detailsContent.innerHTML = this.createContent(raceNum, runnerNo, horseNo, oddsData, historyHtml);
            }
        }
        
        UI.updateExpandAllButtonState(raceNum);
    },
    
    /**
     * Toggle all runners with sequential loading
     */
    async toggleAll(raceNum, buttonElement) {
        const raceContent = document.getElementById(`race-${raceNum}`);
        const runnerRows = Array.from(raceContent.querySelectorAll('.runner-row'));
        const isExpanding = !buttonElement.classList.contains('all-expanded');
        
        if (isExpanding) {
            // Expand all
            const oddsData = Cache.get('odds', raceNum);
            
            // First, expand UI immediately for all runners
            const runners = runnerRows.map(row => {
                const params = row.getAttribute('onclick').match(/'([^']+)'/g).map(s => s.replace(/'/g, ''));
                const horseNo = params[1];
                const runnerNo = row.querySelector('.odds-win')?.getAttribute('data-horse') || horseNo;
                const detailsRow = document.getElementById(`runner-details-${raceNum}-${horseNo}`);
                const detailsContent = document.getElementById(`runner-details-content-${raceNum}-${horseNo}`);
                const cacheKey = `${raceNum}-${horseNo}`;
                
                // Expand UI
                detailsRow.classList.add('expanded');
                row.querySelector('.expand-icon').classList.add('expanded');
                
                // Show initial state
                if (Cache.has('runnerDetails', cacheKey)) {
                    const historyHtml = Cache.get('runnerDetails', cacheKey);
                    detailsContent.innerHTML = this.createContent(raceNum, runnerNo, horseNo, oddsData, historyHtml);
                } else {
                    detailsContent.innerHTML = this.createContent(
                        raceNum, runnerNo, horseNo, oddsData,
                        '<div class="details-loading">Loading race history...</div>'
                    );
                }
                
                return { horseNo, runnerNo, params, detailsContent, cacheKey, detailsRow };
            });
            
            // Update button state immediately after expanding UI
            UI.updateExpandAllButtonState(raceNum);
            
            // Load uncached histories sequentially in background
            (async () => {
                for (const runner of runners) {
                    // Check if still expanded before loading
                    if (!runner.detailsRow.classList.contains('expanded')) {
                        continue; // Skip if user collapsed this runner
                    }
                    
                    if (!Cache.has('runnerDetails', runner.cacheKey)) {
                        try {
                            const historyHtml = await this.load(
                                raceNum,
                                runner.horseNo,
                                runner.params[2],
                                runner.params[3],
                                runner.params[4]
                            );
                            
                            // Check again if still expanded after async load
                            if (runner.detailsRow.classList.contains('expanded')) {
                                const currentOddsData = Cache.get('odds', raceNum);
                                runner.detailsContent.innerHTML = this.createContent(
                                    raceNum, runner.runnerNo, runner.horseNo, currentOddsData, historyHtml
                                );
                            }
                        } catch (error) {
                            // Check if still expanded before showing error
                            if (runner.detailsRow.classList.contains('expanded')) {
                                const currentOddsData = Cache.get('odds', raceNum);
                                runner.detailsContent.innerHTML = this.createContent(
                                    raceNum, runner.runnerNo, runner.horseNo, currentOddsData,
                                    `<div class="details-loading error">Error: ${error.message}</div>`
                                );
                            }
                        }
                    }
                }
            })();
        } else {
            // Collapse all
            runnerRows.forEach(row => {
                const params = row.getAttribute('onclick').match(/'([^']+)'/g).map(s => s.replace(/'/g, ''));
                const horseNo = params[1];
                const detailsRow = document.getElementById(`runner-details-${raceNum}-${horseNo}`);
                
                detailsRow.classList.remove('expanded');
                row.querySelector('.expand-icon').classList.remove('expanded');
            });
            
            // Update button state immediately after collapsing
            UI.updateExpandAllButtonState(raceNum);
        }
    }
};

// ============================================================================
// SPEEDMAP MODULE
// ============================================================================
const Speedmap = {
    /**
     * Load speedmap for a race
     */
    async load(raceNum) {
    const speedmapImg = document.getElementById(`speedmap-${raceNum}`);
    if (!speedmapImg) return;
    
        // Check cache first
        if (Cache.has('speedmaps', raceNum)) {
            speedmapImg.src = Cache.get('speedmaps', raceNum);
        speedmapImg.style.display = 'block';
        return;
    }
    
    speedmapImg.style.display = 'none';
    
        try {
            const base64String = await API.fetchSpeedmap(raceNum);
            Cache.set('speedmaps', raceNum, base64String);
            speedmapImg.src = base64String;
            speedmapImg.style.display = 'block';
        } catch (error) {
            console.error(`Error loading speedmap for race ${raceNum}:`, error);
            speedmapImg.style.display = 'none';
        }
    },
    
    /**
     * Load all speedmaps sequentially via queue
     */
    async loadAll() {
        const speedmapImages = document.querySelectorAll('.speedmap-image');
        for (const img of speedmapImages) {
            const raceNum = img.id.replace('speedmap-', '');
            await this.load(raceNum);
        }
    }
};

// ============================================================================
// UI MODULE - User interface interactions
// ============================================================================
const UI = {
    /**
     * Show a specific race tab
     */
    showRace(raceNum) {
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`tab-${raceNum}`).classList.add('active');
        document.querySelectorAll('.race-content').forEach(content => content.classList.remove('active'));
        document.getElementById(`race-${raceNum}`).classList.add('active');
        
        // Fetch odds if not cached
        if (!Cache.has('odds', raceNum)) {
            Odds.load(raceNum);
        }
    },
    
    /**
     * Update expand/collapse all button state
     */
    updateExpandAllButtonState(raceNum) {
        const raceContent = document.getElementById(`race-${raceNum}`);
        const expandAllBtn = raceContent.querySelector('.expand-all-btn');
        const detailsRows = Array.from(raceContent.querySelectorAll('.runner-details-row'));
        const allExpanded = detailsRows.length > 0 && detailsRows.every(row => row.classList.contains('expanded'));
        
        expandAllBtn.classList.toggle('all-expanded', allExpanded);
        expandAllBtn.querySelector('.expand-all-text').textContent = allExpanded ? 'Collapse All' : 'Expand All';
        const icon = expandAllBtn.querySelector('.expand-all-icon');
        if (icon) {
            icon.textContent = allExpanded ? '▲' : '▼';
        }
    },
    
    /**
     * Sort table by column
     */
    sortTable(raceNum, columnIndex, type) {
    const table = document.querySelector(`#race-${raceNum} .runners-table`);
    const tbody = table.querySelector('tbody');
    const header = table.querySelectorAll('thead th')[columnIndex];
    const allHeaders = table.querySelectorAll('thead th.sortable');
    const rows = Array.from(tbody.querySelectorAll('tr')).filter((row, index) => index % 2 === 0);
    const isAscending = !header.classList.contains('sort-asc');
    
        // Reset all headers
    allHeaders.forEach(h => {
        h.classList.remove('sort-asc', 'sort-desc');
        const arrow = h.querySelector('.sort-arrow');
        if (arrow) arrow.textContent = '⇅';
    });
    
        // Sort rows
    rows.sort((a, b) => {
        let aComp, bComp;
        
        if (type === 'number') {
            aComp = parseFloat(a.cells[columnIndex].textContent.trim());
            bComp = parseFloat(b.cells[columnIndex].textContent.trim());
            if (isNaN(aComp)) aComp = -Infinity;
            if (isNaN(bComp)) bComp = -Infinity;
        } else {
            aComp = a.cells[columnIndex].textContent.trim().toLowerCase();
            bComp = b.cells[columnIndex].textContent.trim().toLowerCase();
        }
        
            return isAscending ? 
                (aComp > bComp ? 1 : aComp < bComp ? -1 : 0) : 
                (aComp < bComp ? 1 : aComp > bComp ? -1 : 0);
    });
    
        // Update header
    header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
    const arrow = header.querySelector('.sort-arrow');
    if (arrow) arrow.textContent = isAscending ? '▲' : '▼';
    
        // Reorder rows
    rows.forEach(row => {
            const detailsRow = row.nextElementSibling;
        tbody.appendChild(row);
            if (detailsRow) tbody.appendChild(detailsRow);
        });
    },
    
    /**
     * Open track workout video
     */
    openTrackWorkoutVideo(raceDate, raceNum) {
        const dateParts = raceDate.split('-');
        const dateFormatted = dateParts.join('');
        const raceNumPadded = raceNum.toString().padStart(2, '0');
        const url = `https://streaminghkjc-a.akamaihd.net/hdflash/twstarter/${dateParts[0]}/${dateFormatted}/${raceNumPadded}/novo/twstarter_${dateFormatted}_${raceNumPadded}_novo_2500kbps.mp4`;
        window.open(url, 'trackWorkoutVideo', 'width=600,height=400,resizable=yes,scrollbars=yes');
    }
};

// ============================================================================
// APPLICATION INITIALIZATION
// ============================================================================
const App = {
    /**
     * Initialize the application
     */
    init() {
        console.log('Initializing HKJC Race Info...');
        
        // Load speedmaps
        Speedmap.loadAll();
        
        // Start odds polling
        Odds.startPolling();
        
        console.log('Application initialized successfully');
    },
    
    /**
     * Cleanup on page unload
     */
    cleanup() {
        Odds.stopPolling();
        RequestQueue.clear();
        Cache.clear();
    }
};

// ============================================================================
// GLOBAL FUNCTION EXPORTS (for inline HTML handlers)
// ============================================================================
window.showRace = (raceNum) => UI.showRace(raceNum);
window.toggleRunnerHistory = (row, raceNum, horseNo, going, track, dist) => 
    RunnerDetails.toggle(row, raceNum, horseNo, going, track, dist);
window.toggleAllRunners = (raceNum, btn) => RunnerDetails.toggleAll(raceNum, btn);
window.sortTable = (raceNum, colIdx, type) => UI.sortTable(raceNum, colIdx, type);
window.openTrackWorkoutVideo = (date, raceNum) => UI.openTrackWorkoutVideo(date, raceNum);

// ============================================================================
// EVENT LISTENERS
// ============================================================================
document.addEventListener('DOMContentLoaded', () => App.init());
window.addEventListener('beforeunload', () => App.cleanup());
