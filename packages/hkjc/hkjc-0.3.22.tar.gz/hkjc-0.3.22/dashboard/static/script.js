// ============================================================================
// HKJC Race Info - Main Application Script
// ============================================================================

// ============================================================================
// CONFIGURATION
// ============================================================================
const CONFIG = {
    ODDS_POLL_INTERVAL: 90000,        // 90 seconds (base)
    POLL_JITTER: 10000,                // ±5 seconds jitter for polling
    MIN_REQUEST_DELAY: 80,             // Min delay between requests (ms)
    MAX_REQUEST_DELAY: 250,            // Max delay between requests (ms)
    MAX_CONCURRENT_REQUESTS: 3,        // Max simultaneous requests
    REQUEST_TIMEOUT: 10000,            // 10 second timeout
    DEBUG: false                       // Enable debug logging
};

// ============================================================================
// UTILITIES
// ============================================================================
const Utils = {
    /**
     * Get runner row data from HTML element
     */
    getRunnerData(row) {
        return {
            raceNum: row.dataset.race,
            horseNo: row.dataset.horse,
            going: row.dataset.going || '',
            track: row.dataset.track || '',
            distance: row.dataset.dist || '',
            runnerNo: row.querySelector('.odds-win')?.dataset.horse || row.dataset.horse
        };
    },

    /**
     * Conditional debug logging
     */
    log(...args) {
        if (CONFIG.DEBUG) {
            console.log(...args);
        }
    }
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
    raceReadiness: new Map()
};

// ============================================================================
// REQUEST QUEUE MANAGER
// ============================================================================
const RequestQueue = {
    queue: [],
    activeCount: 0,
    
    async enqueue(requestFn, priority = 0) {
        return new Promise((resolve, reject) => {
            this.queue.push({ requestFn, resolve, reject, priority });
            this.queue.sort((a, b) => b.priority - a.priority);
            this.process();
        });
    },
    
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
            await this.delay(this.getRandomDelay());
            this.process();
        }
    },
    
    getRandomDelay() {
        return Math.random() * (CONFIG.MAX_REQUEST_DELAY - CONFIG.MIN_REQUEST_DELAY) + CONFIG.MIN_REQUEST_DELAY;
    },
    
    clear() {
        this.queue = [];
    },
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
};

// ============================================================================
// API MODULE - All server communication
// ============================================================================
const API = {
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
    
    async fetchOdds(raceNum) {
        return RequestQueue.enqueue(async () => {
            const response = await this.fetch(`/live_odds/${raceNum}`);
            return await response.json();
        }, 1);
    },
    
    async fetchHorseHistory(horseNo, going, track, distance) {
        return RequestQueue.enqueue(async () => {
            const params = new URLSearchParams({
                going: going || '',
                track: track || '',
                dist: distance || ''
            });
            const response = await this.fetch(`/horse_info/${horseNo}?${params}`);
            return await response.text();
        }, 0);
    },
    
    async fetchSpeedmap(raceNum) {
        return RequestQueue.enqueue(async () => {
            const response = await this.fetch(`/speedmap/${raceNum}`);
            return await response.text();
        }, 0);
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
// RACE READINESS MODULE - Check if speed pro data is available
// ============================================================================
const RaceReadiness = {
    isReady(raceNum) {
        if (State.raceReadiness.has(raceNum)) {
            return State.raceReadiness.get(raceNum);
        }
        
        const ready = this.checkRaceData(raceNum);
        State.raceReadiness.set(raceNum, ready);
        return ready;
    },
    
    checkRaceData(raceNum) {
        const raceContent = document.getElementById(`race-${raceNum}`);
        if (!raceContent) return false;
        
        const runnerRows = raceContent.querySelectorAll('.runner-row');
        if (runnerRows.length === 0) return false;
        
        // Check if any runner has non-zero fitness or energy
        return Array.from(runnerRows).some(row => {
            const fitness = parseFloat(row.cells[8]?.textContent.trim()) || 0;
            const energy = parseFloat(row.cells[9]?.textContent.trim()) || 0;
            return fitness !== 0 || energy !== 0;
        });
    },
    
    recheck(raceNum) {
        State.raceReadiness.delete(raceNum);
        return this.isReady(raceNum);
    }
};

// ============================================================================
// ODDS MODULE - Live odds management
// ============================================================================
const Odds = {
    async load(raceNum) {
        if (!RaceReadiness.isReady(raceNum)) {
            Utils.log(`Skipping odds for race ${raceNum} - race not ready`);
            return null;
        }
        
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
    
    updateDisplay(raceNum, oddsData) {
        if (!oddsData?.Raw || !oddsData?.Fit) return;
        
        this.updateCells(`.odds-win[data-race="${raceNum}"]`, oddsData.Raw.WIN);
        this.updateCells(`.odds-win-fit[data-race="${raceNum}"]`, oddsData.Fit.WIN);
        this.updateCells(`.odds-pla[data-race="${raceNum}"]`, oddsData.Raw.PLA);
        this.updateCells(`.odds-pla-fit[data-race="${raceNum}"]`, oddsData.Fit.PLA);
        
        document.querySelectorAll(`.odds-table[data-race="${raceNum}"]`).forEach(table => {
            const horseNo = table.dataset.horse;
            this.updateOddsTable(table, horseNo, oddsData);
        });
    },
    
    updateCells(selector, oddsData) {
        document.querySelectorAll(selector).forEach(cell => {
            const horseNo = cell.dataset.horse;
            const odds = oddsData?.[horseNo];
            if (odds !== undefined) {
                cell.textContent = odds;
            }
        });
    },
    
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
        
        updateRow(0, oddsData.Raw.QIN);
        updateRow(1, oddsData.Fit.QIN);
        updateRow(2, oddsData.Raw.QPL);
        updateRow(3, oddsData.Fit.QPL);
    },
    
    createSection(raceNum, horseNo, oddsData) {
        if (!oddsData?.Raw || !oddsData?.Fit) return '';
        
        const allHorses = Object.keys(oddsData.Raw.WIN || {}).sort((a, b) => parseInt(a) - parseInt(b));
        const otherHorses = allHorses.filter(h => h !== horseNo);
        
        if (otherHorses.length === 0) return '';
        
        const createRow = (label, data) => {
            let row = `<tr><td class="odds-type-label">${label}</td>`;
            otherHorses.forEach(h => {
                const odds = data?.[horseNo]?.[h] || data?.[h]?.[horseNo];
                row += `<td>${odds !== undefined ? odds : '-'}</td>`;
            });
            return row + '</tr>';
        };
        
        return `
            <div class="odds-table-container">
                <table class="odds-table" data-race="${raceNum}" data-horse="${horseNo}">
                    <thead>
                        <tr>
                            <th>Type</th>
                            ${otherHorses.map(h => `<th>vs ${h}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${createRow('QIN', oddsData.Raw.QIN)}
                        ${createRow('QIN (fit)', oddsData.Fit.QIN)}
                        ${createRow('QPL', oddsData.Raw.QPL)}
                        ${createRow('QPL (fit)', oddsData.Fit.QPL)}
                    </tbody>
                </table>
            </div>
        `;
    },
    
    startPolling() {
        const allRaceNums = Array.from(document.querySelectorAll('.race-content'))
            .map(el => el.id.replace('race-', ''));
        
        // Initial load
        allRaceNums.forEach(raceNum => this.load(raceNum));
        
        // Clear existing interval
        if (State.polling.oddsIntervalId) {
            clearTimeout(State.polling.oddsIntervalId);
        }
        
        // Set up polling with jitter
        const scheduleNextPoll = () => {
            const jitter = Math.random() * CONFIG.POLL_JITTER - (CONFIG.POLL_JITTER / 2);
            const nextInterval = CONFIG.ODDS_POLL_INTERVAL + jitter;
            
            State.polling.oddsIntervalId = setTimeout(() => {
                allRaceNums.forEach(raceNum => this.load(raceNum));
                scheduleNextPoll();
            }, nextInterval);
        };
        
        scheduleNextPoll();
    },
    
    stopPolling() {
        if (State.polling.oddsIntervalId) {
            clearTimeout(State.polling.oddsIntervalId);
            State.polling.oddsIntervalId = null;
        }
    }
};

// ============================================================================
// RUNNER DETAILS MODULE - Horse history and details
// ============================================================================
const RunnerDetails = {
    extractRunningStyles(historyHtml) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(historyHtml, 'text/html');
        const table = doc.querySelector('table');
        
        if (!table) return [];
        
        // Find Style column
        const headerRow = table.querySelector('thead tr');
        if (!headerRow) return [];
        
        const headers = Array.from(headerRow.querySelectorAll('th'));
        const styleColumnIndex = headers.findIndex(th => 
            th.textContent.trim().toLowerCase() === 'style'
        );
        
        if (styleColumnIndex === -1) return [];
        
        // Extract styles from top 5 rows
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        const styles = [];
        
        for (let i = 0; i < Math.min(5, rows.length); i++) {
            const cells = rows[i].querySelectorAll('td');
            if (styleColumnIndex < cells.length) {
                const styleText = cells[styleColumnIndex].textContent.trim();
                if (styleText) {
                    styles.push(styleText);
                }
            }
        }
        
        return styles;
    },
    
    calculateMode(arr) {
        if (!arr || arr.length === 0) return null;
        
        const frequency = {};
        let maxFreq = 0;
        let mode = null;
        
        arr.forEach(value => {
            frequency[value] = (frequency[value] || 0) + 1;
            if (frequency[value] > maxFreq) {
                maxFreq = frequency[value];
                mode = value;
            }
        });
        
        return mode;
    },
    
    updateFavStyle(raceNum, horseNo, historyHtml) {
        const cell = document.querySelector(`.fav-style[data-race="${raceNum}"][data-horse="${horseNo}"]`);
        if (!cell) return;
        
        try {
            const styles = this.extractRunningStyles(historyHtml);
            const favStyle = this.calculateMode(styles);
            cell.textContent = favStyle || '-';
        } catch (error) {
            console.error(`Error updating fav style for horse ${horseNo}:`, error);
            cell.textContent = '-';
        }
    },
    
    async load(raceNum, horseNo, going, track, distance) {
        const cacheKey = `${raceNum}-${horseNo}`;
        
        if (Cache.has('runnerDetails', cacheKey)) {
            const cachedHtml = Cache.get('runnerDetails', cacheKey);
            this.updateFavStyle(raceNum, horseNo, cachedHtml);
            return cachedHtml;
        }
        
        try {
            const html = await API.fetchHorseHistory(horseNo, going, track, distance);
            Cache.set('runnerDetails', cacheKey, html);
            this.updateFavStyle(raceNum, horseNo, html);
            return html;
        } catch (error) {
            console.error(`Error loading history for horse ${horseNo}:`, error);
            throw error;
        }
    },
    
    createContent(raceNum, runnerNo, horseNo, oddsData, historyHtml) {
        const oddsSection = oddsData ? `<div class="details-left">${Odds.createSection(raceNum, runnerNo, oddsData)}</div>` : '';
        const historySection = `<div class="details-right">${historyHtml}</div>`;
        return `<div class="runner-details-wrapper">${oddsSection}${historySection}</div>`;
    },
    
    async toggle(rowElement, raceNum, horseNo, going, track, distance) {
        const detailsRow = document.getElementById(`runner-details-${raceNum}-${horseNo}`);
        const isExpanded = detailsRow.classList.contains('expanded');
        
        if (isExpanded) {
            detailsRow.classList.remove('expanded');
            rowElement.querySelector('.expand-icon').classList.remove('expanded');
        } else {
            detailsRow.classList.add('expanded');
            rowElement.querySelector('.expand-icon').classList.add('expanded');
            
            const detailsContent = document.getElementById(`runner-details-content-${raceNum}-${horseNo}`);
            const runnerNo = rowElement.querySelector('.odds-win')?.dataset.horse || horseNo;
            const oddsData = Cache.get('odds', raceNum);
            const cacheKey = `${raceNum}-${horseNo}`;
            
            if (!Cache.has('runnerDetails', cacheKey)) {
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
                        `<div class="details-loading error">Error: ${error.message}</div>`
                    );
                }
            } else {
                const historyHtml = Cache.get('runnerDetails', cacheKey);
                detailsContent.innerHTML = this.createContent(raceNum, runnerNo, horseNo, oddsData, historyHtml);
            }
        }
        
        UI.updateExpandAllButtonState(raceNum);
    },
    
    async loadRunnerData(raceNum, runnerData, oddsData) {
        const { horseNo, runnerNo, going, track, distance } = runnerData;
        const cacheKey = `${raceNum}-${horseNo}`;
        const detailsContent = document.getElementById(`runner-details-content-${raceNum}-${horseNo}`);
        const detailsRow = document.getElementById(`runner-details-${raceNum}-${horseNo}`);
        
        if (!Cache.has('runnerDetails', cacheKey)) {
            try {
                const historyHtml = await this.load(raceNum, horseNo, going, track, distance);
                
                if (detailsRow.classList.contains('expanded')) {
                    const currentOddsData = Cache.get('odds', raceNum);
                    detailsContent.innerHTML = this.createContent(raceNum, runnerNo, horseNo, currentOddsData, historyHtml);
                }
            } catch (error) {
                if (detailsRow.classList.contains('expanded')) {
                    const currentOddsData = Cache.get('odds', raceNum);
                    detailsContent.innerHTML = this.createContent(
                        raceNum, runnerNo, horseNo, currentOddsData,
                        `<div class="details-loading error">Error: ${error.message}</div>`
                    );
                }
            }
        }
    },
    
    async toggleAll(raceNum, buttonElement) {
        const raceContent = document.getElementById(`race-${raceNum}`);
        const runnerRows = Array.from(raceContent.querySelectorAll('.runner-row'));
        const isExpanding = !buttonElement.classList.contains('all-expanded');
        
        if (isExpanding) {
            const oddsData = Cache.get('odds', raceNum);
            
            // Expand UI immediately for all runners
            const runners = runnerRows.map(row => {
                const runnerData = Utils.getRunnerData(row);
                const cacheKey = `${raceNum}-${runnerData.horseNo}`;
                const detailsRow = document.getElementById(`runner-details-${raceNum}-${runnerData.horseNo}`);
                const detailsContent = document.getElementById(`runner-details-content-${raceNum}-${runnerData.horseNo}`);
                
                detailsRow.classList.add('expanded');
                row.querySelector('.expand-icon').classList.add('expanded');
                
                if (Cache.has('runnerDetails', cacheKey)) {
                    const historyHtml = Cache.get('runnerDetails', cacheKey);
                    detailsContent.innerHTML = this.createContent(raceNum, runnerData.runnerNo, runnerData.horseNo, oddsData, historyHtml);
                } else {
                    detailsContent.innerHTML = this.createContent(
                        raceNum, runnerData.runnerNo, runnerData.horseNo, oddsData,
                        '<div class="details-loading">Loading race history...</div>'
                    );
                }
                
                return runnerData;
            });
            
            UI.updateExpandAllButtonState(raceNum);
            
            // Load uncached histories in background
            (async () => {
                for (const runnerData of runners) {
                    await this.loadRunnerData(raceNum, runnerData, oddsData);
                }
            })();
        } else {
            // Collapse all
            runnerRows.forEach(row => {
                const horseNo = row.dataset.horse;
                const detailsRow = document.getElementById(`runner-details-${raceNum}-${horseNo}`);
                detailsRow.classList.remove('expanded');
                row.querySelector('.expand-icon').classList.remove('expanded');
            });
            
            UI.updateExpandAllButtonState(raceNum);
        }
    },
    
    async prefetchAll() {
        Utils.log('Starting background prefetch of runner histories...');
        
        const allRaces = Array.from(document.querySelectorAll('.race-content'));
        if (allRaces.length === 0) return;
        
        for (const raceContent of allRaces) {
            const raceNum = raceContent.id.replace('race-', '');
            const runnerRows = Array.from(raceContent.querySelectorAll('.runner-row'));
            
            for (const row of runnerRows) {
                const { horseNo, going, track, distance } = Utils.getRunnerData(row);
                if (!horseNo) continue;
                
                const cacheKey = `${raceNum}-${horseNo}`;
                if (Cache.has('runnerDetails', cacheKey)) continue;
                
                try {
                    await this.load(raceNum, horseNo, going, track, distance);
                    Utils.log(`✓ Prefetched race ${raceNum} - horse ${horseNo}`);
                } catch (error) {
                    console.error(`✗ Error prefetching race ${raceNum} - horse ${horseNo}:`, error);
                }
            }
        }
        
        Utils.log('✓ Background prefetch completed');
    }
};

// ============================================================================
// SPEEDMAP MODULE
// ============================================================================
const Speedmap = {
    ensureImageElement(raceNum, container) {
        if (!container.querySelector('img')) {
            container.innerHTML = `<img id="speedmap-${raceNum}" class="speedmap-image" alt="Race ${raceNum} Speed Map" />`;
        }
        return document.getElementById(`speedmap-${raceNum}`);
    },
    
    async load(raceNum) {
        const speedmapContainer = document.querySelector(`#race-${raceNum} .speedmap-container`);
        const speedmapImg = document.getElementById(`speedmap-${raceNum}`);
        if (!speedmapImg || !speedmapContainer) return;
        
        if (!RaceReadiness.isReady(raceNum)) {
            speedmapImg.style.display = 'none';
            speedmapContainer.innerHTML = '<div class="race-not-ready">Race not ready</div>';
            return;
        }
        
        if (Cache.has('speedmaps', raceNum)) {
            const img = this.ensureImageElement(raceNum, speedmapContainer);
            img.src = Cache.get('speedmaps', raceNum);
            img.style.display = 'block';
            return;
        }
        
        speedmapImg.style.display = 'none';
        
        try {
            const base64String = await API.fetchSpeedmap(raceNum);
            Cache.set('speedmaps', raceNum, base64String);
            const img = this.ensureImageElement(raceNum, speedmapContainer);
            img.src = base64String;
            img.style.display = 'block';
        } catch (error) {
            console.error(`Error loading speedmap for race ${raceNum}:`, error);
            speedmapImg.style.display = 'none';
        }
    },
    
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
    showRace(raceNum) {
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`tab-${raceNum}`).classList.add('active');
        document.querySelectorAll('.race-content').forEach(content => content.classList.remove('active'));
        document.getElementById(`race-${raceNum}`).classList.add('active');
        
        if (!Cache.has('odds', raceNum)) {
            Odds.load(raceNum);
        }
    },
    
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
    init() {
        console.log('Initializing HKJC Race Info...');
        
        Speedmap.loadAll();
        Odds.startPolling();
        RunnerDetails.prefetchAll().catch(error => {
            console.error('Error in background prefetch:', error);
        });
        
        console.log('Application initialized successfully');
    },
    
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
