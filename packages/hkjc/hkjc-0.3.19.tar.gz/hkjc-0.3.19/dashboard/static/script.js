/**
 * HKJC Race Info - Main JavaScript
 * Handles race tab navigation and horse history loading
 */

// Cache to store loaded history data
const historyCache = {};

// Cache to store speedmap images
const speedmapCache = {};

/**
 * Open track workout video in a new window
 * @param {string} raceDate - The race date in format YYYY-MM-DD (e.g., 2025-10-08)
 * @param {string} raceNum - The race number
 */
function openTrackWorkoutVideo(raceDate, raceNum) {
    // Parse the date
    const dateParts = raceDate.split('-');
    const year = dateParts[0];
    const dateFormatted = dateParts.join(''); // YYYYMMDD format
    
    // Pad race number to 2 digits
    const raceNumPadded = raceNum.toString().padStart(2, '0');
    
    // Construct the URL
    const url = `https://streaminghkjc-a.akamaihd.net/hdflash/twstarter/${year}/${dateFormatted}/${raceNumPadded}/novo/twstarter_${dateFormatted}_${raceNumPadded}_novo_2500kbps.mp4`;
    
    // Open in new window
    window.open(url, '_blank');
}

/**
 * Show a specific race tab and its content
 * @param {string} raceNum - The race number to display
 */
function showRace(raceNum) {
    // Update active tab
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`tab-${raceNum}`).classList.add('active');

    // Update active content
    document.querySelectorAll('.race-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`race-${raceNum}`).classList.add('active');
}

/**
 * Toggle all runner histories in a race (expand or collapse all)
 * @param {string} raceNum - The race number
 * @param {HTMLElement} buttonElement - The expand/collapse all button element
 */
function toggleAllRunners(raceNum, buttonElement) {
    const raceContent = document.getElementById(`race-${raceNum}`);
    const runnerRows = raceContent.querySelectorAll('.runner-row');
    const isExpanding = !buttonElement.classList.contains('all-expanded');
    
    runnerRows.forEach(row => {
        const expandIcon = row.querySelector('.expand-icon');
        const horseNo = row.onclick.toString().match(/'([^']+)'/g)[1].replace(/'/g, '');
        const historyRow = document.getElementById(`history-${raceNum}-${horseNo}`);
        const historyContent = document.getElementById(`history-content-${raceNum}-${horseNo}`);
        const cacheKey = `${raceNum}-${horseNo}`;
        
        if (isExpanding) {
            // Expand
            historyRow.classList.add('expanded');
            expandIcon.classList.add('expanded');
            
            // Load data if not already loaded
            if (!historyCache[cacheKey]) {
                historyContent.innerHTML = '<div class="history-loading">Loading history...</div>';
                
                // Extract parameters from onclick
                const onclickStr = row.getAttribute('onclick');
                const params = onclickStr.match(/'([^']+)'/g).map(s => s.replace(/'/g, ''));
                const going = params[2];
                const track = params[3];
                const distance = params[4];
                
                const url = `/horse_info/${horseNo}?going=${encodeURIComponent(going)}&track=${encodeURIComponent(track)}&dist=${encodeURIComponent(distance)}`;
                
                fetch(url)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.text();
                    })
                    .then(html => {
                        historyCache[cacheKey] = html;
                        historyContent.innerHTML = html;
                    })
                    .catch(error => {
                        console.error('Error loading horse history:', error);
                        historyContent.innerHTML = `<div class="history-loading" style="color: #ff4444;">Error loading history: ${error.message}</div>`;
                    });
            } else {
                historyContent.innerHTML = historyCache[cacheKey];
            }
        } else {
            // Collapse
            historyRow.classList.remove('expanded');
            expandIcon.classList.remove('expanded');
        }
    });
    
    // Update button state
    if (isExpanding) {
        buttonElement.classList.add('all-expanded');
        buttonElement.querySelector('.expand-all-text').textContent = 'Collapse All';
    } else {
        buttonElement.classList.remove('all-expanded');
        buttonElement.querySelector('.expand-all-text').textContent = 'Expand All';
    }
}

/**
 * Toggle individual runner history (expand or collapse)
 * @param {HTMLElement} rowElement - The runner row element
 * @param {string} raceNum - The race number
 * @param {string} horseNo - The horse number
 * @param {string} going - Track going conditions
 * @param {string} track - Track type
 * @param {string} distance - Race distance
 */
function toggleRunnerHistory(rowElement, raceNum, horseNo, going, track, distance) {
    const expandIcon = rowElement.querySelector('.expand-icon');
    const historyRow = document.getElementById(`history-${raceNum}-${horseNo}`);
    const historyContent = document.getElementById(`history-content-${raceNum}-${horseNo}`);
    const cacheKey = `${raceNum}-${horseNo}`;

    // Toggle expanded state
    const isExpanded = historyRow.classList.contains('expanded');

    if (isExpanded) {
        // Collapse
        historyRow.classList.remove('expanded');
        expandIcon.classList.remove('expanded');
    } else {
        // Expand
        historyRow.classList.add('expanded');
        expandIcon.classList.add('expanded');

        // Load data if not already loaded
        if (!historyCache[cacheKey]) {
            // Show loading state
            historyContent.innerHTML = '<div class="history-loading">Loading history...</div>';

            // Build URL with query parameters
            const url = `/horse_info/${horseNo}?going=${encodeURIComponent(going)}&track=${encodeURIComponent(track)}&dist=${encodeURIComponent(distance)}`;

            // Fetch history data
            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.text();
                })
                .then(html => {
                    // Cache the result
                    historyCache[cacheKey] = html;
                    
                    // Display the history table
                    historyContent.innerHTML = html;
                })
                .catch(error => {
                    console.error('Error loading horse history:', error);
                    historyContent.innerHTML = `<div class="history-loading" style="color: #ff4444;">Error loading history: ${error.message}</div>`;
                });
        } else {
            // Use cached data
            historyContent.innerHTML = historyCache[cacheKey];
        }
    }

    // Update "Expand All" button state
    updateExpandAllButtonState(raceNum);
}

/**
 * Update the state of the "Expand All" button based on current expanded rows
 * @param {string} raceNum - The race number
 */
function updateExpandAllButtonState(raceNum) {
    const raceContent = document.getElementById(`race-${raceNum}`);
    const expandAllBtn = raceContent.querySelector('.expand-all-btn');
    const runnerRows = raceContent.querySelectorAll('.runner-row');
    const historyRows = raceContent.querySelectorAll('.history-row');
    
    // Check if all rows are expanded
    let allExpanded = true;
    historyRows.forEach(row => {
        if (!row.classList.contains('expanded')) {
            allExpanded = false;
        }
    });
    
    // Update button state
    if (allExpanded && runnerRows.length > 0) {
        expandAllBtn.classList.add('all-expanded');
        expandAllBtn.querySelector('.expand-all-text').textContent = 'Collapse All';
    } else {
        expandAllBtn.classList.remove('all-expanded');
        expandAllBtn.querySelector('.expand-all-text').textContent = 'Expand All';
    }
}

/**
 * Load speedmap image for a specific race
 * @param {string} raceNum - The race number
 */
function loadSpeedmap(raceNum) {
    const speedmapImg = document.getElementById(`speedmap-${raceNum}`);
    
    if (!speedmapImg) {
        return;
    }
    
    // Check if already cached
    if (speedmapCache[raceNum]) {
        speedmapImg.src = speedmapCache[raceNum];
        speedmapImg.style.display = 'block';
        return;
    }
    
    // Show loading state
    speedmapImg.style.display = 'none';
    
    // Fetch speedmap from server
    fetch(`/speedmap/${raceNum}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(base64String => {
            // Create data URL from base64 string
            const dataUrl = base64String;
            
            // Cache the image
            speedmapCache[raceNum] = dataUrl;
            
            // Set image source
            speedmapImg.src = dataUrl;
            speedmapImg.style.display = 'block';
        })
        .catch(error => {
            console.error(`Error loading speedmap for race ${raceNum}:`, error);
            // Hide image on error
            speedmapImg.style.display = 'none';
        });
}

/**
 * Load all speedmaps on page load
 */
function loadAllSpeedmaps() {
    const speedmapImages = document.querySelectorAll('.speedmap-image');
    speedmapImages.forEach(img => {
        const raceNum = img.id.replace('speedmap-', '');
        loadSpeedmap(raceNum);
    });
}

// Load speedmaps when page is ready
document.addEventListener('DOMContentLoaded', loadAllSpeedmaps);

/**
 * Sort table by column
 * @param {string} raceNum - The race number
 * @param {number} columnIndex - The column index to sort by
 * @param {string} type - The data type ('number' or 'string')
 */
function sortTable(raceNum, columnIndex, type) {
    const table = document.querySelector(`#race-${raceNum} .runners-table`);
    const tbody = table.querySelector('tbody');
    const header = table.querySelectorAll('thead th')[columnIndex];
    const allHeaders = table.querySelectorAll('thead th.sortable');
    
    // Get all runner rows (every other row, excluding history rows)
    const rows = Array.from(tbody.querySelectorAll('tr')).filter((row, index) => index % 2 === 0);
    
    // Determine sort direction
    let isAscending = true;
    if (header.classList.contains('sort-asc')) {
        isAscending = false;
    }
    
    // Clear all sort indicators
    allHeaders.forEach(h => {
        h.classList.remove('sort-asc', 'sort-desc');
        const arrow = h.querySelector('.sort-arrow');
        if (arrow) arrow.textContent = '⇅';
    });
    
    // Sort rows
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        let aComp, bComp;
        
        if (type === 'number') {
            // Parse numeric values, treat non-numeric as -Infinity
            aComp = parseFloat(aValue);
            bComp = parseFloat(bValue);
            
            // Only treat actual non-numeric values (NaN) as -Infinity, not 0
            if (isNaN(aComp)) aComp = -Infinity;
            if (isNaN(bComp)) bComp = -Infinity;
        } else {
            aComp = aValue.toLowerCase();
            bComp = bValue.toLowerCase();
        }
        
        if (isAscending) {
            return aComp > bComp ? 1 : aComp < bComp ? -1 : 0;
        } else {
            return aComp < bComp ? 1 : aComp > bComp ? -1 : 0;
        }
    });
    
    // Update sort indicator
    header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
    const arrow = header.querySelector('.sort-arrow');
    if (arrow) {
        arrow.textContent = isAscending ? '▲' : '▼';
    }
    
    // Reorder rows in the table
    rows.forEach((row, index) => {
        const historyRow = row.nextElementSibling;
        tbody.appendChild(row);
        if (historyRow) {
            tbody.appendChild(historyRow);
        }
    });
}

