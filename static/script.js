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

    // --- Data Fetching & Rendering ---

    const fetchNetwork = async () => {
        const response = await fetch('/api/network');
        const data = await response.json();
        renderNetwork(data.connections);
        renderWeights(data.weights);
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
            const cost = calculateLocalCost(info);

            row.innerHTML = `
                <td>${key.replace('-', ' ↔ ')}</td>
                <td>${info.distance}</td>
                <td>${info.traffic}%</td>
                <td>${info.quality}</td>
                <td class="${info.blocked === 'Yes' ? 'status-blocked' : 'status-ok'}">${info.blocked}</td>
                <td>${info.blocked === 'Yes' ? '∞' : cost}</td>
            `;
            tableBody.appendChild(row);
        });
    };

    const renderWeights = (weights) => {
        weightsDiv.innerHTML = `
            <strong>Learned Cost Weights (Linear Regression):</strong><br>
            Distance: ${weights.w_distance.toFixed(3)} | 
            Traffic: ${weights.w_traffic.toFixed(3)} | 
            Inverse Quality: ${weights.w_quality_inv.toFixed(3)} | 
            Intercept: ${weights.intercept.toFixed(3)}
        `;
    };

    // Note: We only use this for UI display, backend does the real math
    const calculateLocalCost = (info) => {
        // Just a dummy calc for the table until weights are loaded globally in JS if needed
        return "Calculated"; 
    };

    const log = (text, type = '') => {
        const p = document.createElement('p');
        if (type) p.classList.add(`log-${type}`);
        p.textContent = text;
        consoleArea.appendChild(p);
        consoleArea.scrollTop = consoleArea.scrollHeight;
    };

    // --- Event Handlers ---
    runBtn.addEventListener('click', async () => {
        const start = document.getElementById('start-node').value;
        const dest = document.getElementById('dest-node').value;

        if (start === dest) {
            alert('Start and Destination cannot be the same!');
            return;
        }

        loadingOverlay.style.display = 'flex';
        consoleArea.innerHTML = '';
        log('--- PreSaNa Session Started ---', 'header');

        try {
            const response = await fetch('/api/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ start, dest })
            });

            const data = await response.json();
            
            // Artificial delay for effect
            await new Promise(r => setTimeout(r, 800));

            data.logs.forEach((msg, i) => {
                setTimeout(() => log(msg), i * 150);
            });

            setTimeout(() => {
                if (data.best) {
                    reportSection.style.display = 'block';
                    const path = data.best.path.join(' ➔ ');
                    reportContent.innerHTML = `
                        <p>PreSaNa has concluded its search.</p>
                        <p>Optimal Route Found: <strong>${path}</strong></p>
                        <p>Total Estimated Cost: <strong>${data.best.cost}</strong></p>
                        <p style="margin-top: 1rem; font-size: 0.9rem; color: #94a3b8;">
                            This route was selected using PreSaNa's learned weights.                             It balances distance, traffic congestion, and road quality to achieve the goal.
                        </p>
                    `;
                    log('SUCCESS: Route optimized.', 'success');
                } else {
                    reportSection.style.display = 'block';
                    reportContent.innerHTML = `<p class="log-error">No feasible route found. All paths are blocked.</p>`;
                    log('ERROR: Goal unreachable.', 'error');
                }
                loadingOverlay.style.display = 'none';
            }, data.logs.length * 150 + 500);

        } catch (err) {
            console.error(err);
            loadingOverlay.style.display = 'none';
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
