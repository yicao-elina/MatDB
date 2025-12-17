// materials-db.js
console.log("materials-db.js version LLM-TEST loaded");
class MaterialsDB {
    constructor() {
        this.currentQuery = null;
        this.currentResults = null;
        this.init();
    }
    
    init() {
        this.loadDatabaseStats();
        this.bindEvents();
    }
    
    bindEvents() {
        // Query link clicks
        document.querySelectorAll('.query-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const queryId = e.target.closest('.query-link').dataset.query;
                this.executeQuery(queryId);
            });
        });
    }
    
    async loadDatabaseStats() {
        try {
            const response = await fetch('api.php?action=stats');
            const stats = await response.json();
            
            const statsContainer = document.getElementById('db-stats');
            statsContainer.innerHTML = `
                <div class="row text-center">
                    <div class="col-6">
                        <div class="border-end">
                            <h5 class="text-primary mb-0">${stats.total_materials}</h5>
                            <small class="text-muted">Materials</small>
                        </div>
                    </div>
                    <div class="col-6">
                        <h5 class="text-success mb-0">${stats.crystal_systems}</h5>
                        <small class="text-muted">Crystal Systems</small>
                    </div>
                </div>
                <hr>
                <div class="row text-center">
                    <div class="col-6">
                        <div class="border-end">
                            <h6 class="text-info mb-0">${stats.semiconductors}</h6>
                            <small class="text-muted">Semiconductors</small>
                        </div>
                    </div>
                    <div class="col-6">
                        <h6 class="text-warning mb-0">${stats.metals}</h6>
                        <small class="text-muted">Metals</small>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    async executeQuery(queryId) {
        this.showLoading();
        
        try {
            const response = await fetch(`api.php?action=query&id=${queryId}`);
            const data = await response.json();
            
            if (data.success) {
                this.currentQuery = data.query;
                this.currentResults = data.results;
                this.displayResults(data);
            } else {
                this.showError(data.error);
            }
        } catch (error) {
            this.showError('Network error: ' + error.message);
        }
    }
    
    displayResults(data) {
        // Hide loading
        document.getElementById('loading').style.display = 'none';
        
        // Show query info
        const queryInfo = document.getElementById('query-info');
        document.getElementById('query-title').textContent = data.query.title;
        document.getElementById('query-description').textContent = data.query.description;
        document.getElementById('query-sql').textContent = data.query.sql;
        queryInfo.style.display = 'block';
        
        // Display results table
        const resultsContainer = document.getElementById('results-container');
        
        if (data.results.length === 0) {
            resultsContainer.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle"></i>
                    No results found for this query.
                </div>
            `;
            return;
        }
        
        // Create table
        const table = this.createTable(data.results);
        resultsContainer.innerHTML = `
            <div class="card">
                <div class="card-header d-flex justify-content-between">
                    <span><i class="fas fa-table"></i> Results (${data.results.length} rows)</span>
                    <small class="text-muted">Execution time: ${data.execution_time}ms</small>
                </div>
                <div class="card-body p-0">
                    <div class="table-responsive">
                        ${table}
                    </div>
                </div>
            </div>
        `;
    }
    
    createTable(results) {
        if (results.length === 0) return '';
        
        const headers = Object.keys(results[0]);
        
        let html = '<table class="table table-striped table-hover result-table mb-0">';
        
        // Headers
        html += '<thead class="table-dark"><tr>';
        headers.forEach(header => {
            html += `<th>${header.replace(/_/g, ' ').toUpperCase()}</th>`;
        });
        html += '</tr></thead>';
        
        // Body
        html += '<tbody>';
        results.forEach(row => {
            html += '<tr>';
            headers.forEach(header => {
                let value = row[header];
                
                // Format different data types
                if (value === null || value === undefined) {
                    value = '<span class="text-muted">NULL</span>';
                } else if (typeof value === 'number') {
                    if (value % 1 !== 0) {
                        value = parseFloat(value).toFixed(3);
                    }
                } else if (header.includes('material_id')) {
                    value = `<code>${value}</code>`;
                } else if (header.includes('formula')) {
                    value = `<strong>${value}</strong>`;
                }
                
                html += `<td>${value}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody></table>';
        
        return html;
    }
    
    showLoading() {
        document.getElementById('loading').style.display = 'block';
        document.getElementById('query-info').style.display = 'none';
        document.getElementById('results-container').innerHTML = '';
    }
    
    showError(message) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('results-container').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle"></i>
                <strong>Error:</strong> ${message}
            </div>
        `;
    }
    
    async executeCustomQuery() {
        const sql = document.getElementById('custom-sql').value.trim();
        
        if (!sql) {
            alert('Please enter a SQL query');
            return;
        }
        
        // Basic security check
        if (!sql.toLowerCase().startsWith('select')) {
            alert('Only SELECT queries are allowed');
            return;
        }
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('customQueryModal'));
        modal.hide();
        
        this.showLoading();
        
        try {
            const response = await fetch('api.php?action=custom', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ sql: sql })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentResults = data.results;
                this.displayCustomResults(data, sql);
            } else {
                this.showError(data.error);
            }
        } catch (error) {
            this.showError('Network error: ' + error.message);
        }
    }
    
    displayCustomResults(data, sql) {
        document.getElementById('loading').style.display = 'none';
        
        const queryInfo = document.getElementById('query-info');
        document.getElementById('query-title').textContent = 'Custom Query';
        document.getElementById('query-description').textContent = 'User-defined SQL query';
        document.getElementById('query-sql').textContent = sql;
        queryInfo.style.display = 'block';
        
        const table = this.createTable(data.results);
        document.getElementById('results-container').innerHTML = `
            <div class="card">
                <div class="card-header">
                    <i class="fas fa-table"></i> Custom Query Results (${data.results.length} rows)
                </div>
                <div class="card-body p-0">
                    <div class="table-responsive">
                        ${table}
                    </div>
                </div>
            </div>
        `;
    }

    async runLLMTest() {
        const textarea = document.getElementById('llm-query-input');
        const userInput = textarea ? textarea.value.trim() : '';

        if (!userInput) {
            alert('Please enter a question for the LLM.');
            return;
        }
        const modalEl = document.getElementById('llmQueryModal');
        if (modalEl && window.bootstrap && bootstrap.Modal) {
            const instance = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
            instance.hide();
        }

        const loadingEl = document.getElementById('loading');
        if (loadingEl) loadingEl.style.display = 'block';
        
        const resultsContainer = document.getElementById('results-container');
        if (resultsContainer) resultsContainer.innerHTML = '';

        try {
            const response = await fetch('llm.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: userInput })
            });

            const data = await response.json();
            if (loadingEl) loadingEl.style.display = 'none';

            if (!data.success) {
                this.showError(data.error || 'Unknown error from LLM backend.');
                return;
            }

            const answer = data.answer || '(no answer returned)';
        
            this.lastGeneratedSQL = answer;
            if (resultsContainer) {
                resultsContainer.innerHTML = `
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <i class="fas fa-robot"></i> LLM SQL Generated
                        </div>
                        <div class="card-body">
                            <p class="mb-2"><strong>Your Question:</strong></p>
                            <p class="text-muted border-bottom pb-2">${userInput}</p>
                            
                            <p class="mb-2"><strong>Generated SQL:</strong></p>
                            <pre class="bg-light p-3 border rounded" style="white-space: pre-wrap; font-family: monospace;">${answer}</pre>
                            
                            <div class="mt-3">
                                <button class="btn btn-primary" onclick="window.materialsDB.executeGeneratedSQL()">
                                    <i class="fas fa-play"></i> Execute This Query
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            this.currentResults = null;

        } catch (err) {
            if (loadingEl) loadingEl.style.display = 'none';
            this.showError('Network error: ' + err.message);
        }
    }

    async executeGeneratedSQL() {
        const sql = this.lastGeneratedSQL;
        
        if (!sql) {
            alert('No SQL query found to execute.');
            return;
        }
        
        this.showLoading();
        
        try {
            const response = await fetch('api.php?action=custom', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ sql: sql })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentResults = data.results;
                this.displayCustomResults(data, sql);
            } else {
                this.showError(data.error);
            }
        } catch (error) {
            this.showError('Execution error: ' + error.message);
        }
    }
}

// Utility functions
function toggleSQL() {
    const sqlDiv = document.getElementById('query-sql');
    const toggleText = document.getElementById('sql-toggle-text');
    
    if (sqlDiv.style.display === 'none') {
        sqlDiv.style.display = 'block';
        toggleText.textContent = 'Hide SQL';
    } else {
        sqlDiv.style.display = 'none';
        toggleText.textContent = 'Show SQL';
    }
}

function exportResults() {
    if (!window.materialsDB.currentResults) {
        alert('No results to export');
        return;
    }
    
    const results = window.materialsDB.currentResults;
    const headers = Object.keys(results[0]); let csv = headers.join(',') + '\n';
    results.forEach(row => {
        const values = headers.map(header => {
            let value = row[header];
            if (value === null || value === undefined) value = '';
            return `"${value}"`;
        });
        csv += values.join(',') + '\n';
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `materials_query_results_${new Date().getTime()}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.materialsDB = new MaterialsDB();
});