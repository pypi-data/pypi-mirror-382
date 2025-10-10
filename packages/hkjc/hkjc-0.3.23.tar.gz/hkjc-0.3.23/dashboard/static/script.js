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
        if (CONFIG.DEBUG) console.log(...args);
    },
    
    /**
     * DOM query helpers
     */
    $(selector, context = document) {
        return context.querySelector(selector);
    },
    
    $$(selector, context = document) {
        return Array.from(context.querySelectorAll(selector));
    },
    
    /**
     * Batch class operations
     */
    addClass(elements, className) {
        (Array.isArray(elements) ? elements : [elements]).forEach(el => el?.classList.add(className));
    },
    
    removeClass(elements, className) {
        (Array.isArray(elements) ? elements : [elements]).forEach(el => el?.classList.remove(className));
    },
    
    toggleClass(elements, className, force) {
        (Array.isArray(elements) ? elements : [elements]).forEach(el => el?.classList.toggle(className, force));
    },
    
    /**
     * Parse float with fallback
     */
    parseNum(value, fallback = 0) {
        const num = parseFloat(value);
        return isNaN(num) ? fallback : num;
    },
    
    /**
     * Create HTML element from string
     */
    createElement(html) {
        const template = document.createElement('template');
        template.innerHTML = html.trim();
        return template.content.firstChild;
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
    
    enqueue(requestFn, priority = 0) {
        return new Promise((resolve, reject) => {
            this.queue.push({ requestFn, resolve, reject, priority });
            this.queue.sort((a, b) => b.priority - a.priority);
            this.process();
        });
    },
    
    async process() {
        if (this.activeCount >= CONFIG.MAX_CONCURRENT_REQUESTS || !this.queue.length) return;
        
        const { requestFn, resolve, reject } = this.queue.shift();
        this.activeCount++;
        
        try {
            resolve(await requestFn());
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
            const response = await fetch(url, { ...options, signal: controller.signal });
            clearTimeout(timeoutId);
            
            if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') throw new Error('Request timeout');
            throw error;
        }
    },
    
    fetchOdds(raceNum) {
        return RequestQueue.enqueue(async () => {
            return (await this.fetch(`/live_odds/${raceNum}`)).json();
        }, 1);
    },
    
    fetchHorseHistory(horseNo, going, track, distance) {
        return RequestQueue.enqueue(async () => {
            const params = new URLSearchParams({ going: going || '', track: track || '', dist: distance || '' });
            return (await this.fetch(`/horse_info/${horseNo}?${params}`)).text();
        }, 0);
    },
    
    fetchSpeedmap(raceNum) {
        return RequestQueue.enqueue(async () => {
            return (await this.fetch(`/speedmap/${raceNum}`)).text();
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
        if (!State.caches[cacheName]) State.caches[cacheName] = new Map();
        State.caches[cacheName].set(key, value);
    },
    
    has(cacheName, key) {
        return State.caches[cacheName]?.has(key) || false;
    },
    
    clear(cacheName) {
        cacheName ? State.caches[cacheName]?.clear() : Object.values(State.caches).forEach(cache => cache.clear());
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
        const runnerRows = Utils.$$(`#race-${raceNum} .runner-row`);
        if (runnerRows.length === 0) return false;
        
        return runnerRows.some(row => {
            const fitness = Utils.parseNum(row.cells[8]?.textContent.trim());
            const energy = Utils.parseNum(row.cells[9]?.textContent.trim());
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
        }
    },
    
    updateDisplay(raceNum, oddsData) {
        if (!oddsData?.Raw || !oddsData?.Fit) return;
        
        // Update main odds cells
        const updates = [
            ['.odds-win', oddsData.Raw.WIN],
            ['.odds-win-fit', oddsData.Fit.WIN],
            ['.odds-pla', oddsData.Raw.PLA],
            ['.odds-pla-fit', oddsData.Fit.PLA]
        ];
        
        updates.forEach(([className, data]) => 
            this.updateCells(`${className}[data-race="${raceNum}"]`, data)
        );
        
        // Update odds tables
        Utils.$$(`.odds-table[data-race="${raceNum}"]`).forEach(table => 
            this.updateOddsTable(table, table.dataset.horse, oddsData)
        );
        
        PreferredHighlight.update(raceNum);
    },
    
    updateCells(selector, oddsData) {
        Utils.$$(selector).forEach(cell => {
            const odds = oddsData?.[cell.dataset.horse];
            if (odds !== undefined) cell.textContent = odds;
        });
    },
    
    updateOddsTable(table, horseNo, oddsData) {
        const otherHorses = Object.keys(oddsData.Raw.WIN || {})
            .sort((a, b) => parseInt(a) - parseInt(b))
            .filter(h => h !== horseNo);
        
        const rows = Utils.$$('tbody tr', table);
        if (rows.length < 4) return;
        
        const updateRow = (rowIndex, dataPath) => {
            const cells = Utils.$$('td:not(.odds-type-label)', rows[rowIndex]);
            cells.forEach((cell, idx) => {
                const h = otherHorses[idx];
                const odds = dataPath[horseNo]?.[h] || dataPath[h]?.[horseNo];
                cell.textContent = odds !== undefined ? odds : '-';
            });
        };
        
        [oddsData.Raw.QIN, oddsData.Fit.QIN, oddsData.Raw.QPL, oddsData.Fit.QPL]
            .forEach((data, i) => updateRow(i, data));
    },
    
    createSection(raceNum, horseNo, oddsData) {
        if (!oddsData?.Raw || !oddsData?.Fit) return '';
        
        const otherHorses = Object.keys(oddsData.Raw.WIN || {})
            .sort((a, b) => parseInt(a) - parseInt(b))
            .filter(h => h !== horseNo);
        
        if (otherHorses.length === 0) return '';
        
        const createRow = (label, data) => `
            <tr>
                <td class="odds-type-label">${label}</td>
                ${otherHorses.map(h => {
                    const odds = data?.[horseNo]?.[h] || data?.[h]?.[horseNo];
                    return `<td>${odds !== undefined ? odds : '-'}</td>`;
                }).join('')}
            </tr>`;
        
        const rows = [
            ['QIN', oddsData.Raw.QIN],
            ['QIN (fit)', oddsData.Fit.QIN],
            ['QPL', oddsData.Raw.QPL],
            ['QPL (fit)', oddsData.Fit.QPL]
        ];
        
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
                        ${rows.map(([label, data]) => createRow(label, data)).join('')}
                    </tbody>
                </table>
            </div>
        `;
    },
    
    startPolling() {
        const allRaceNums = Utils.$$('.race-content').map(el => el.id.replace('race-', ''));
        
        allRaceNums.forEach(raceNum => this.load(raceNum));
        
        if (State.polling.oddsIntervalId) clearTimeout(State.polling.oddsIntervalId);
        
        const scheduleNextPoll = () => {
            const jitter = Math.random() * CONFIG.POLL_JITTER - (CONFIG.POLL_JITTER / 2);
            State.polling.oddsIntervalId = setTimeout(() => {
                allRaceNums.forEach(raceNum => this.load(raceNum));
                scheduleNextPoll();
            }, CONFIG.ODDS_POLL_INTERVAL + jitter);
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
        const doc = new DOMParser().parseFromString(historyHtml, 'text/html');
        const table = Utils.$('table', doc);
        if (!table) return [];
        
        const headerRow = Utils.$('thead tr', table);
        if (!headerRow) return [];
        
        const styleColumnIndex = Utils.$$('th', headerRow)
            .findIndex(th => th.textContent.trim().toLowerCase() === 'style');
        
        if (styleColumnIndex === -1) return [];
        
        return Utils.$$('tbody tr', table)
            .slice(0, 5)
            .map(row => row.querySelectorAll('td')[styleColumnIndex]?.textContent.trim())
            .filter(Boolean);
    },
    
    calculateMode(arr) {
        if (!arr?.length) return null;
        
        const frequency = arr.reduce((acc, val) => {
            acc[val] = (acc[val] || 0) + 1;
            return acc;
        }, {});
        
        return Object.entries(frequency)
            .reduce((max, [val, freq]) => freq > max[1] ? [val, freq] : max, [null, 0])[0];
    },
    
    updateFavStyle(raceNum, horseNo, historyHtml) {
        const cell = Utils.$(`.fav-style[data-race="${raceNum}"][data-horse="${horseNo}"]`);
        if (!cell) return;
        
        try {
            cell.textContent = this.calculateMode(this.extractRunningStyles(historyHtml)) || 'Unknown';
            FavStyleChart.update(raceNum);
            PreferredHighlight.update(raceNum);
        } catch (error) {
            console.error(`Error updating fav style for horse ${horseNo}:`, error);
            cell.textContent = 'Unknown';
        }
    },
    
    async load(raceNum, horseNo, going, track, distance) {
        const cacheKey = `${raceNum}-${horseNo}`;
        
        if (Cache.has('runnerDetails', cacheKey)) {
            const cachedHtml = Cache.get('runnerDetails', cacheKey);
            this.updateFavStyle(raceNum, horseNo, cachedHtml);
            return cachedHtml;
        }
        
        const html = await API.fetchHorseHistory(horseNo, going, track, distance);
        Cache.set('runnerDetails', cacheKey, html);
        this.updateFavStyle(raceNum, horseNo, html);
        return html;
    },
    
    createContent(raceNum, runnerNo, horseNo, oddsData, historyHtml) {
        const oddsSection = oddsData ? `<div class="details-left">${Odds.createSection(raceNum, runnerNo, oddsData)}</div>` : '';
        const historySection = `<div class="details-right">${historyHtml}</div>`;
        return `<div class="runner-details-wrapper">${oddsSection}${historySection}</div>`;
    },
    
    async toggle(rowElement, raceNum, horseNo, going, track, distance) {
        const detailsRow = Utils.$(`#runner-details-${raceNum}-${horseNo}`);
        const expandIcon = Utils.$('.expand-icon', rowElement);
        const isExpanded = detailsRow.classList.contains('expanded');
        
        Utils.toggleClass([detailsRow, expandIcon], 'expanded', !isExpanded);
        
        if (!isExpanded) {
            const detailsContent = Utils.$(`#runner-details-content-${raceNum}-${horseNo}`);
            const runnerNo = Utils.$('.odds-win', rowElement)?.dataset.horse || horseNo;
            const oddsData = Cache.get('odds', raceNum);
            const cacheKey = `${raceNum}-${horseNo}`;
            
            if (!Cache.has('runnerDetails', cacheKey)) {
                detailsContent.innerHTML = this.createContent(raceNum, runnerNo, horseNo, oddsData,
                    '<div class="details-loading">Loading race history...</div>');
                
                try {
                    const historyHtml = await this.load(raceNum, horseNo, going, track, distance);
                    detailsContent.innerHTML = this.createContent(raceNum, runnerNo, horseNo, oddsData, historyHtml);
                } catch (error) {
                    detailsContent.innerHTML = this.createContent(raceNum, runnerNo, horseNo, oddsData,
                        `<div class="details-loading error">Error: ${error.message}</div>`);
                }
            } else {
                detailsContent.innerHTML = this.createContent(raceNum, runnerNo, horseNo, oddsData, 
                    Cache.get('runnerDetails', cacheKey));
            }
        }
        
        UI.updateExpandAllButtonState(raceNum);
    },
    
    async loadRunnerData(raceNum, runnerData, oddsData) {
        const { horseNo, runnerNo, going, track, distance } = runnerData;
        const cacheKey = `${raceNum}-${horseNo}`;
        
        if (Cache.has('runnerDetails', cacheKey)) return;
        
        const detailsContent = Utils.$(`#runner-details-content-${raceNum}-${horseNo}`);
        const detailsRow = Utils.$(`#runner-details-${raceNum}-${horseNo}`);
        
        if (!detailsRow.classList.contains('expanded')) return;
        
        try {
            const historyHtml = await this.load(raceNum, horseNo, going, track, distance);
            detailsContent.innerHTML = this.createContent(raceNum, runnerNo, horseNo, 
                Cache.get('odds', raceNum), historyHtml);
        } catch (error) {
            detailsContent.innerHTML = this.createContent(raceNum, runnerNo, horseNo, 
                Cache.get('odds', raceNum), 
                `<div class="details-loading error">Error: ${error.message}</div>`);
        }
    },
    
    async toggleAll(raceNum, buttonElement) {
        const raceContent = Utils.$(`#race-${raceNum}`);
        const runnerRows = Utils.$$('.runner-row', raceContent);
        const isExpanding = !buttonElement.classList.contains('all-expanded');
        
        if (isExpanding) {
            const oddsData = Cache.get('odds', raceNum);
            const runners = runnerRows.map(row => {
                const runnerData = Utils.getRunnerData(row);
                const cacheKey = `${raceNum}-${runnerData.horseNo}`;
                const detailsRow = Utils.$(`#runner-details-${raceNum}-${runnerData.horseNo}`);
                const detailsContent = Utils.$(`#runner-details-content-${raceNum}-${runnerData.horseNo}`);
                
                Utils.addClass([detailsRow, Utils.$('.expand-icon', row)], 'expanded');
                
                detailsContent.innerHTML = this.createContent(
                    raceNum, runnerData.runnerNo, runnerData.horseNo, oddsData,
                    Cache.has('runnerDetails', cacheKey) 
                        ? Cache.get('runnerDetails', cacheKey)
                        : '<div class="details-loading">Loading race history...</div>'
                );
                
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
            runnerRows.forEach(row => {
                const detailsRow = Utils.$(`#runner-details-${raceNum}-${row.dataset.horse}`);
                Utils.removeClass([detailsRow, Utils.$('.expand-icon', row)], 'expanded');
            });
            UI.updateExpandAllButtonState(raceNum);
        }
    },
    
    async prefetchAll(priorityRaceNum = null) {
        Utils.log('Starting background prefetch of runner histories...');
        
        const sortedRaces = Utils.$$('.race-content').sort((a, b) => {
            const aNum = a.id.replace('race-', '');
            const bNum = b.id.replace('race-', '');
            if (priorityRaceNum) {
                if (aNum === priorityRaceNum) return -1;
                if (bNum === priorityRaceNum) return 1;
            }
            return parseInt(aNum) - parseInt(bNum);
        });
        
        for (const raceContent of sortedRaces) {
            const raceNum = raceContent.id.replace('race-', '');
            Utils.log(`Prefetching race ${raceNum}${raceNum === priorityRaceNum ? ' (priority)' : ''}...`);
            
            for (const row of Utils.$$('.runner-row', raceContent)) {
                const { horseNo, going, track, distance } = Utils.getRunnerData(row);
                const cacheKey = `${raceNum}-${horseNo}`;
                
                if (!horseNo || Cache.has('runnerDetails', cacheKey)) continue;
                
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
        if (!Utils.$('img', container)) {
            container.innerHTML = `<img id="speedmap-${raceNum}" class="speedmap-image" alt="Race ${raceNum} Speed Map" />`;
        }
        return Utils.$(`#speedmap-${raceNum}`);
    },
    
    async load(raceNum) {
        const speedmapContainer = Utils.$(`#race-${raceNum} .speedmap-container`);
        const speedmapImg = Utils.$(`#speedmap-${raceNum}`);
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
        for (const img of Utils.$$('.speedmap-image')) {
            await this.load(img.id.replace('speedmap-', ''));
        }
    }
};

// ============================================================================
// PREFERRED HIGHLIGHT MODULE - Highlight preferred values and top horses
// ============================================================================
const PreferredHighlight = {
    // Column configuration: index, type (max/min/fixed/range), and value checker
    columns: [
        { name: 'draw', index: 2, check: v => [3, 4, 5].includes(parseInt(v)) },
        { name: 'rating', index: 7, type: 'max' },
        { name: 'fitness', index: 8, type: 'max' },
        { name: 'energyDiff', index: 9, type: 'max' },
        { name: 'favStyle', index: 10, check: v => v === 'FrontRunner' },
        { name: 'win', index: 11, type: 'min' },
        { name: 'pla', index: 13, type: 'min' }
    ],
    
    calculateRacePreferred(raceNum) {
        const raceContent = Utils.$(`#race-${raceNum}`);
        if (!raceContent) return null;
        
        const preferred = {};
        
        this.columns.filter(col => col.type).forEach(col => {
            preferred[col.name] = col.type === 'max' ? -Infinity : Infinity;
        });
        
        Utils.$$('.runner-row', raceContent).forEach(row => {
            this.columns.filter(col => col.type).forEach(col => {
                const value = Utils.parseNum(row.cells[col.index]?.textContent.trim(), 
                    col.type === 'max' ? -Infinity : Infinity);
                
                if (col.type === 'max' && value > preferred[col.name]) {
                    preferred[col.name] = value;
                } else if (col.type === 'min' && value > 0 && value < preferred[col.name]) {
                    preferred[col.name] = value;
                }
            });
        });
        
        return preferred;
    },
    
    applyHighlighting(raceNum) {
        const raceContent = Utils.$(`#race-${raceNum}`);
        if (!raceContent) return;
        
        const runnerRows = Utils.$$('.runner-row', raceContent);
        const racePreferred = this.calculateRacePreferred(raceNum);
        if (!racePreferred) return;
        
        const horseCounts = new Map();
        
        // First pass: highlight cells and count preferred attributes
        runnerRows.forEach(row => {
            const cells = row.cells;
            Utils.removeClass(Array.from(cells), 'preferred-cell');
            
            let count = 0;
            this.columns.forEach(col => {
                const cell = cells[col.index];
                const value = cell?.textContent.trim();
                
                let isPreferred = false;
                if (col.check) {
                    isPreferred = col.check(value);
                } else if (col.type && racePreferred[col.name] !== undefined) {
                    const numValue = Utils.parseNum(value, col.type === 'max' ? -Infinity : Infinity);
                    isPreferred = numValue === racePreferred[col.name] && 
                                  (col.type === 'max' || numValue > 0);
                }
                
                if (isPreferred) {
                    Utils.addClass(cell, 'preferred-cell');
                    count++;
                }
            });
            
            horseCounts.set(row.dataset.horse, count);
        });
        
        // Second pass: highlight horses with most preferred attributes
        const maxCount = Math.max(...horseCounts.values());
        
        runnerRows.forEach(row => {
            const count = horseCounts.get(row.dataset.horse);
            Utils.removeClass(row, 'most-preferred-horse');
            Utils.$('.most-preferred-badge', row)?.remove();
            
            if (count === maxCount && maxCount > 0) {
                Utils.addClass(row, 'most-preferred-horse');
                
                const nameCell = row.cells[4];
                if (nameCell && !Utils.$('.most-preferred-badge', nameCell)) {
                    const badge = document.createElement('span');
                    badge.className = 'most-preferred-badge';
                    badge.textContent = `${count}★`;
                    badge.title = `${count} preferred attribute${count > 1 ? 's' : ''}`;
                    nameCell.appendChild(badge);
                }
            }
        });
    },
    
    update(raceNum) {
        this.applyHighlighting(raceNum);
    },
    
    initAll() {
        Utils.$$('.race-content').forEach(raceContent => 
            this.applyHighlighting(raceContent.id.replace('race-', ''))
        );
    }
};

// ============================================================================
// FAV STYLE CHART MODULE - Pie chart for running style distribution
// ============================================================================
const FavStyleChart = {
    charts: new Map(),
    styleColors: {
        'FrontRunner': '#48bb78',
        'Pacer': '#667eea',
        'Closer': '#f56565',
        'Unknown': '#a0aec0'
    },
    
    getStyleDistribution(raceNum) {
        const raceContent = Utils.$(`#race-${raceNum}`);
        if (!raceContent) return {};
        
        return Utils.$$('.fav-style', raceContent).reduce((dist, cell) => {
            const style = cell.textContent.trim();
            if (style) dist[style] = (dist[style] || 0) + 1;
            return dist;
        }, {});
    },
    
    getColorForStyle(style) {
        return this.styleColors[style] || '#a0aec0';
    },
    
    draw(raceNum) {
        const canvas = Utils.$(`#fav-style-chart-${raceNum}`);
        if (!canvas) return;
        
        const distribution = this.getStyleDistribution(raceNum);
        const entries = Object.entries(distribution).sort((a, b) => b[1] - a[1]);
        
        if (this.charts.has(raceNum)) this.charts.get(raceNum).destroy();
        if (entries.length === 0) return;
        
        const labels = entries.map(([style]) => style);
        const data = entries.map(([, count]) => count);
        const colors = labels.map(style => this.getColorForStyle(style));
        
        const ctx = canvas.getContext('2d');
        const chart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                animation: {
                    duration: 500  // 2x faster (default is 1000ms)
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 8,
                            font: {
                                size: 10
                            },
                            generateLabels: function(chart) {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    const dataset = data.datasets[0];
                                    const total = dataset.data.reduce((a, b) => a + b, 0);
                                    return data.labels.map((label, i) => {
                                        const value = dataset.data[i];
                                        const percentage = ((value / total) * 100).toFixed(1);
                                        return {
                                            text: `${label}: ${value} (${percentage}%)`,
                                            fillStyle: dataset.backgroundColor[i],
                                            hidden: false,
                                            index: i
                                        };
                                    });
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
        
        this.charts.set(raceNum, chart);
    },
    
    update(raceNum) {
        const raceContent = Utils.$(`#race-${raceNum}`);
        if (this.charts.has(raceNum) || raceContent?.classList.contains('active')) {
            this.draw(raceNum);
        }
    },
    
    initAll() {
        const activeRace = Utils.$('.race-content.active');
        if (activeRace) this.draw(activeRace.id.replace('race-', ''));
    }
};

// ============================================================================
// UI MODULE - User interface interactions
// ============================================================================
const UI = {
    showRace(raceNum) {
        Utils.removeClass(Utils.$$('.tab-btn'), 'active');
        Utils.addClass(Utils.$(`#tab-${raceNum}`), 'active');
        Utils.removeClass(Utils.$$('.race-content'), 'active');
        Utils.addClass(Utils.$(`#race-${raceNum}`), 'active');
        
        sessionStorage.setItem('activeRaceTab', raceNum);
        
        if (!Cache.has('odds', raceNum)) Odds.load(raceNum);
        if (!FavStyleChart.charts.has(raceNum)) FavStyleChart.draw(raceNum);
        
        PreferredHighlight.update(raceNum);
    },
    
    updateExpandAllButtonState(raceNum) {
        const raceContent = Utils.$(`#race-${raceNum}`);
        const expandAllBtn = Utils.$('.expand-all-btn', raceContent);
        const detailsRows = Utils.$$('.runner-details-row', raceContent);
        const allExpanded = detailsRows.length > 0 && detailsRows.every(row => row.classList.contains('expanded'));
        
        Utils.toggleClass(expandAllBtn, 'all-expanded', allExpanded);
        Utils.$('.expand-all-text', expandAllBtn).textContent = allExpanded ? 'Collapse All' : 'Expand All';
        
        const icon = Utils.$('.expand-all-icon', expandAllBtn);
        if (icon) icon.textContent = allExpanded ? '▲' : '▼';
    },
    
    sortTable(raceNum, columnIndex, type) {
        const table = Utils.$(`#race-${raceNum} .runners-table`);
        const tbody = Utils.$('tbody', table);
        const headers = Utils.$$('thead th', table);
        const header = headers[columnIndex];
        const allHeaders = Utils.$$('thead th.sortable', table);
        const rows = Utils.$$('tr', tbody).filter((row, index) => index % 2 === 0);
        const isAscending = !header.classList.contains('sort-asc');
        
        // Reset all headers
        allHeaders.forEach(h => {
            Utils.removeClass(h, ['sort-asc', 'sort-desc']);
            const arrow = Utils.$('.sort-arrow', h);
            if (arrow) arrow.textContent = '⇅';
        });
        
        // Sort rows
        rows.sort((a, b) => {
            const getValue = (row) => {
                const val = row.cells[columnIndex].textContent.trim();
                return type === 'number' ? Utils.parseNum(val, -Infinity) : val.toLowerCase();
            };
            
            const aComp = getValue(a);
            const bComp = getValue(b);
            
            return isAscending ? 
                (aComp > bComp ? 1 : aComp < bComp ? -1 : 0) : 
                (aComp < bComp ? 1 : aComp > bComp ? -1 : 0);
        });
        
        // Update header
        Utils.addClass(header, isAscending ? 'sort-asc' : 'sort-desc');
        const arrow = Utils.$('.sort-arrow', header);
        if (arrow) arrow.textContent = isAscending ? '▲' : '▼';
        
        // Reorder rows
        rows.forEach(row => {
            tbody.appendChild(row);
            if (row.nextElementSibling) tbody.appendChild(row.nextElementSibling);
        });
        
        PreferredHighlight.update(raceNum);
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
        
        const savedRaceTab = sessionStorage.getItem('activeRaceTab');
        if (savedRaceTab && Utils.$(`#tab-${savedRaceTab}`)) {
            UI.showRace(savedRaceTab);
        }
        
        const activeRace = Utils.$('.race-content.active');
        const activeRaceNum = activeRace?.id.replace('race-', '');
        
        Speedmap.loadAll();
        FavStyleChart.initAll();
        PreferredHighlight.initAll();
        Odds.startPolling();
        RunnerDetails.prefetchAll(activeRaceNum).catch(error => 
            console.error('Error in background prefetch:', error)
        );
        
        console.log('Application initialized successfully');
    },
    
    cleanup() {
        Odds.stopPolling();
        RequestQueue.clear();
        Cache.clear();
        FavStyleChart.charts.forEach(chart => chart.destroy());
        FavStyleChart.charts.clear();
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
