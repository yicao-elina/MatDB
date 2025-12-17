<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Materials Project Database Query Interface</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .query-card {
            transition: transform 0.2s;
            cursor: pointer;
        }
        .query-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .result-table {
            font-size: 0.9em;
        }
        .category-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .loading {
            display: none;
        }
        .query-sql {
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-3 bg-light p-3">
                <h4><i class="fas fa-atom"></i> Materials DB</h4>
                <hr>
                
                <!-- Database Stats -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h6><i class="fas fa-chart-bar"></i> Database Overview</h6>
                    </div>
                    <div class="card-body" id="db-stats">
                        <div class="loading">Loading stats...</div>
                    </div>
                </div>
                
                <!-- Query Categories -->
                <div class="accordion" id="queryAccordion">
                    <!-- Category A -->
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#categoryA">
                                <i class="fas fa-layer-group me-2"></i> Aggregation & Grouping
                            </button>
                        </h2>
                        <div id="categoryA" class="accordion-collapse collapse show">
                            <div class="accordion-body p-2">
                                <div class="list-group list-group-flush">
                                    <a href="#" class="list-group-item list-group-item-action query-link" data-query="A1">
                                        <small>A1: Crystal System Analysis</small>
                                    </a>
                                    <a href="#" class="list-group-item list-group-item-action query-link" data-query="A2">
                                        <small>A2: Large Crystal Systems</small>
                                    </a>
                                    <a href="#" class="list-group-item list-group-item-action query-link" data-query="A3">
                                        <small>A3: Stability by Composition</small>
                                    </a>
                                    <a href="#" class="list-group-item list-group-item-action query-link" data-query="A4">
                                        <small>A4: Tellurium Materials</small>
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Category B -->
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#categoryB">
                                <i class="fas fa-filter me-2"></i> Complex Filtering
                            </button>
                        </h2>
                        <div id="categoryB" class="accordion-collapse collapse">
                            <div class="accordion-body p-2">
                                <div class="list-group list-group-flush">
                                    <a href="#" class="list-group-item list-group-item-action query-link" data-query="B1">
                                        <small>B1: Above Average Band Gap</small>
                                    </a>
                                    <a href="#" class="list-group-item list-group-item-action query-link" data-query="B2">
                                        <small>B2: Sb+Te Materials</small>
                                    </a>
                                    <a href="#" class="list-group-item list-group-item-action query-link" data-query="B3">
                                        <small>B3: Wide Gap Non-Oxides</small>
                                    </a>
                                    <a href="#" class="list-group-item list-group-item-action query-link" data-query="B4">
                                        <small>B4: Most Stable 10%</small>
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Category C -->
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#categoryC">
                                <i class="fas fa-sort-numeric-down me-2"></i> Window Functions
                            </button>
                        </h2>
                        <div id="categoryC" class="accordion-collapse collapse">
                            <div class="accordion-body p-2">
                                <div class="list-group list-group-flush">
                                    <a href="#" class="list-group-item list-group-item-action query-link" data-query="C1">
                                        <small>C1: Most Stable per System</small>
                                    </a>
                                    <a href="#" class="list-group-item list-group-item-action query-link" data-query="C2">
                                        <small>C2: Band Gap vs System Avg</small>
                                    </a>
                                    <a href="#" class="list-group-item list-group-item-action query-link" data-query="C3">
                                        <small>C3: 5th Period Elements</small>
                                    </a>
                                    <a href="#" class="list-group-item list-group-item-action query-link" data-query="C4">
                                        <small>C4: Density Moving Average</small>
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Category D -->
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#categoryD">
                                <i class="fas fa-project-diagram me-2"></i> Advanced Analysis
                            </button>
                        </h2>
                        <div id="categoryD" class="accordion-collapse collapse">
                            <div class="accordion-body p-2">
                                <div class="list-group list-group-flush">
                                    <a href="#" class="list-group-item list-group-item-action query-link" data-query="D1">
                                        <small>D1: Element Frequency</small>
                                    </a>
                                    <a href="#" class="list-group-item list-group-item-action query-link" data-query="D2">
                                        <small>D2: Binary Element Pairs</small>
                                    </a>
                                    <a href="#" class="list-group-item list-group-item-action query-link" data-query="D3">
                                        <small>D3: Hexagonal Semiconductors</small>
                                    </a>
                                    <a href="#" class="list-group-item list-group-item-action query-link" data-query="D4">
                                        <small>D4: Band Gap Outliers</small>
                                    </a>
                                    <a href="#" class="list-group-item list-group-item-action query-link" data-query="D5">
                                        <small>D5: Stable Hexagonal Semiconductors</small>
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Custom Query -->
                <div class="mt-3">
                    <button class="btn btn-outline-primary btn-sm w-100" data-bs-toggle="modal" data-bs-target="#customQueryModal">
                        <i class="fas fa-code"></i> Custom SQL Query
                    </button>
                    <button class="btn btn-outline-success btn-sm w-100 mt-2" data-bs-toggle="modal" data-bs-target="#llmQueryModal">
                        <i class="fas fa-language"></i> LLM Query
                    </button>
                </div>
            </div>
            
            <!-- Main Content -->
            <div class="col-md-9 p-3">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h2><i class="fas fa-search"></i> Query Results</h2>
                    <div>
                        <button class="btn btn-outline-secondary btn-sm" onclick="exportResults()">
                            <i class="fas fa-download"></i> Export CSV
                        </button>
                    </div>
                </div>
                
                <!-- Query Info -->
                <div id="query-info" class="alert alert-info" style="display: none;">
                    <h5 id="query-title"></h5>
                    <p id="query-description"></p>
                    <div id="query-sql" class="query-sql p-2 mt-2" style="display: none;"></div>
                    <button class="btn btn-sm btn-outline-primary mt-2" onclick="toggleSQL()">
                        <i class="fas fa-code"></i> <span id="sql-toggle-text">Show SQL</span>
                    </button>
                </div>
                
                <!-- Loading -->
                <div id="loading" class="text-center" style="display: none;">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Executing query...</p>
                </div>
                
                <!-- Results -->
                <div id="results-container">
                    <div class="alert alert-light text-center">
                        <i class="fas fa-mouse-pointer fa-2x text-muted mb-2"></i>
                        <p class="text-muted">Select a query from the sidebar to view results</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Custom Query Modal -->
    <div class="modal fade" id="customQueryModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Custom SQL Query</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">SQL Query:</label>
                        <textarea id="custom-sql" class="form-control" rows="8" placeholder="SELECT * FROM materials WHERE..."></textarea>
                    </div>
                    <div class="alert alert-warning">
                        <small><strong>Note:</strong> Only SELECT queries are allowed for security reasons.</small>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="window.materialsDB.executeCustomQuery()">Execute Query</button>
                </div>
            </div>
        </div>
    </div>

    <div class="modal fade" id="llmQueryModal" tabindex="-1">
        <div class="modal-dialog modal-lg modal-dialog-scrollable">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">LLM Query</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="llm-query-input" class="form-label">
                            Enter your request in English:
                        </label>
                        <textarea id="llm-query-input"
                                  class="form-control"
                                  rows="6"
                                  placeholder="e.g. Find crystal systems with more than 5 materials, return the system name, material count, and average band gap."></textarea>
                    </div>
                    <div class="alert alert-info mb-0">
                        <small>
                            This is a placeholder for the LLM interface.
                            For now, submitting will show a test message:
                            <code>test for LLM</code>.
                        </small>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button"
                            class="btn btn-secondary"
                            data-bs-dismiss="modal">
                        Cancel
                    </button>
                    <button type="button"
                            class="btn btn-success"
                            onclick="window.materialsDB.runLLMTest()">
                        Run (LLM Test)
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="materials-db.js"></script>
</body>
</html>