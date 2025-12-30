document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const tableBody = document.querySelector('#network-table tbody');
    const weightsDiv = document.getElementById('weights-info');
    const consoleArea = document.getElementById('console');
    const runBtn = document.getElementById('run-btn');
    const randomizeBtn = document.getElementById('randomize-btn');
    const loadingOverlay = document.getElementById('loading');
    const reportSection = document.getElementById('report-section');
    const reportContent = document.getElementById('report-content');
    const modelSelect = document.getElementById('model-select');

    // Global state for metadata
    let globalMetadata = {};

    // --- Data Fetching & Rendering ---

    const fetchNetwork = async () => {
        try {
            const response = await fetch('/api/network');
            const data = await response.json();
            globalMetadata = data.metadata;
            renderNetwork(data.connections);
            updateModelInfo(); // Render info for currently selected model
        } catch (err) {
            console.error("Failed to fetch network:", err);
        }
    };

    const renderNetwork = (connections) => {
        tableBody.innerHTML = '';
        // Group by pair to show unique connections
        const seen = new Set();
        
        Object.entries(connections).forEach(([key, info]) => {
            const sortedNodes = key.split('-').sort().join('-');
            if (seen.has(sortedNodes)) return;
            seen.add(sortedNodes);

            const row = document.createElement('tr');
            // Cost is dynamic based on model, so we show '?' or basic info here
            // or we could show a rough calc if we want.
            
            row.innerHTML = `
                <td>${key.replace('-', ' ↔ ')}</td>
                <td>${info.distance}</td>
                <td>${info.traffic}%</td>
                <td>${info.quality}</td>
                <td class="${info.blocked === 'Yes' ? 'status-blocked' : 'status-ok'}">${info.blocked}</td>
                <td>--</td> 
            `;
            tableBody.appendChild(row);
        });
    };

    const updateModelInfo = () => {
        const modelType = modelSelect.value;
        const info = globalMetadata[modelType];
        
        if (!info) {
            weightsDiv.innerHTML = '<em>No metadata available for this model.</em>';
            return;
        }

        if (modelType === 'linear') {
            weightsDiv.innerHTML = `
                <strong>Learned Weights (Linear Regression):</strong><br>
                Distance: ${info.w_distance.toFixed(3)} | 
                Traffic: ${info.w_traffic.toFixed(3)} | 
                Inverse Quality: ${info.w_quality_inv.toFixed(3)} | 
                Intercept: ${info.intercept.toFixed(3)}
            `;
        } else if (modelType === 'rf') {
            const imps = info.feature_importances;
            weightsDiv.innerHTML = `
                <strong>Feature Importances (Random Forest):</strong><br>
                Distance: ${imps.distance.toFixed(3)} | 
                Traffic: ${imps.traffic.toFixed(3)} | 
                Inverse Quality: ${imps.quality_inv.toFixed(3)}
            `;
        }
    };

    const log = (text, type = '') => {
        const p = document.createElement('p');
        if (type) p.classList.add(`log-${type}`);
        p.textContent = text;
        consoleArea.appendChild(p);
        consoleArea.scrollTop = consoleArea.scrollHeight;
    };

    // --- Event Handlers ---
    
    // Update info when model changes
    modelSelect.addEventListener('change', updateModelInfo);

    runBtn.addEventListener('click', async () => {
        const start = document.getElementById('start-node').value;
        const dest = document.getElementById('dest-node').value;
        const modelType = modelSelect.value;

        if (start === dest) {
            alert('Start and Destination cannot be the same!');
            return;
        }

        loadingOverlay.style.display = 'flex';
        consoleArea.innerHTML = '';
        log(`--- PreSaNa Session Started (${modelType === 'linear' ? 'Linear Regression' : 'Random Forest'}) ---`, 'header');

        try {
            const response = await fetch('/api/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ start, dest, model_type: modelType })
            });

            const data = await response.json();
            
            // Artificial delay for effect
            await new Promise(r => setTimeout(r, 800));

            if (data.logs) {
                data.logs.forEach((msg, i) => {
                    setTimeout(() => log(msg), i * 150);
                });
            }

            setTimeout(() => {
                if (data.best) {
                    reportSection.style.display = 'block';
                    const path = data.best.path.join(' ➔ ');
                    reportContent.innerHTML = `
                        <p>PreSaNa has concluded its search.</p>
                        <p>Optimal Route Found: <strong>${path}</strong></p>
                        <p>Total Estimated Cost: <strong>${data.best.cost}</strong></p>
                        <p style="margin-top: 1rem; font-size: 0.9rem; color: #94a3b8;">
                            Route optimized using <strong>${modelType === 'linear' ? 'Linear Regression' : 'Random Forest'}</strong> logic.
                        </p>
                    `;
                    log('SUCCESS: Route optimized.', 'success');
                } else if (data.error) {
                     log(`ERROR: ${data.error}`, 'error');
                } else {
                    reportSection.style.display = 'block';
                    reportContent.innerHTML = `<p class="log-error">No feasible route found. All paths are blocked.</p>`;
                    log('ERROR: Goal unreachable.', 'error');
                }
                loadingOverlay.style.display = 'none';
            }, (data.logs ? data.logs.length * 150 : 0) + 500);

        } catch (err) {
            console.error(err);
            loadingOverlay.style.display = 'none';
            log('System Error: Check console for details.', 'error');
        }
    });

    randomizeBtn.addEventListener('click', async () => {
        await fetch('/api/randomize');
        fetchNetwork();
        consoleArea.innerHTML = '<p class="placeholder">PreSaNa data randomized. Previous state cleared.</p>';
        reportSection.style.display = 'none';
    });

    // End Simulation Logic
    const endBtn = document.getElementById('end-btn');
    const endScreen = document.getElementById('end-screen');

    endBtn.addEventListener('click', () => {
        endScreen.style.display = 'flex';
    });

    fetchNetwork();
});
