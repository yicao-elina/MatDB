<?php
// api.php

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST');
header('Access-Control-Allow-Headers: Content-Type');

// Database configuration
$db_config = [
    'host' => 'dbase.cs.jhu.edu',
    'username' => 'FA25_ycao73',
    'password' => 'Mel62w66gA',
    'database' => 'FA25_ycao73_db',
    'charset' => 'utf8mb4'
];

// Query definitions
$queries = [
    'A1' => [
        'title' => 'Crystal System Analysis',
        'description' => 'Average band gap and formation energy for each crystal system',
        'sql' => "SELECT 
            crystal_system,
            COUNT(*) as material_count,
            ROUND(AVG(band_gap), 3) as avg_band_gap_eV,
            ROUND(AVG(formation_energy_per_atom), 3) as avg_formation_energy_eV_per_atom
        FROM materials 
        WHERE crystal_system IS NOT NULL 
            AND band_gap IS NOT NULL 
            AND formation_energy_per_atom IS NOT NULL
        GROUP BY crystal_system
        ORDER BY material_count DESC"
    ],
    'A2' => [
        'title' => 'Large Crystal Systems',
        'description' => 'Crystal systems with more than 5 materials',
        'sql' => "SELECT 
            crystal_system,
            COUNT(*) as material_count,
            ROUND(AVG(band_gap), 3) as avg_band_gap
        FROM materials 
        WHERE crystal_system IS NOT NULL
        GROUP BY crystal_system
        HAVING COUNT(*) > 5
        ORDER BY material_count DESC"
    ],
    'A3' => [
        'title' => 'Stability by Composition',
        'description' => 'Comparison of materials by number of elements',
        'sql' => "SELECT 
            nelements,
            COUNT(*) as material_count,
            ROUND(MIN(formation_energy_per_atom), 3) as most_stable_formation_energy,
            ROUND(AVG(formation_energy_per_atom), 3) as avg_formation_energy,
            COUNT(CASE WHEN is_stable = 1 THEN 1 END) as stable_materials_count
        FROM materials 
        WHERE nelements BETWEEN 1 AND 6 
            AND formation_energy_per_atom IS NOT NULL
        GROUP BY nelements
        ORDER BY nelements"
    ],
    'A4' => [
        'title' => 'Tellurium Materials',
        'description' => 'Materials containing Tellurium (Te)',
        'sql' => "SELECT 
            material_id,
            formula_pretty,
            elements,
            band_gap,
            crystal_system,
            formation_energy_per_atom
        FROM materials 
        WHERE elements LIKE '%Te%'
            AND band_gap IS NOT NULL
        ORDER BY band_gap DESC"
    ],
    'B1' => [
        'title' => 'Above Average Band Gap',
        'description' => 'Materials with band gaps greater than database average',
        'sql' => "SELECT 
            m.material_id,
            m.formula_pretty,
            m.band_gap,
            m.crystal_system,
            m.formation_energy_per_atom
        FROM materials m
        WHERE m.band_gap > (SELECT AVG(band_gap) FROM materials WHERE band_gap IS NOT NULL)
            AND m.band_gap IS NOT NULL
        ORDER BY m.band_gap DESC"
    ],
    'B2' => [
        'title' => 'Sb+Te Materials',
        'description' => 'Materials containing both Antimony (Sb) and Tellurium (Te)',
        'sql' => "SELECT 
            material_id,
            formula_pretty,
            elements,
            band_gap,
            formation_energy_per_atom,
            crystal_system
        FROM materials 
        WHERE elements LIKE '%Sb%' 
            AND elements LIKE '%Te%'
        ORDER BY band_gap DESC"
    ],
    'B3' => [
        'title' => 'Wide Gap Non-Oxides',
        'description' => 'Wide band gap materials (>3.0 eV) without Oxygen',
        'sql' => "SELECT 
            material_id,
            formula_pretty,
            elements,
            band_gap,
            formation_energy_per_atom,
            crystal_system
        FROM materials 
        WHERE band_gap > 3.0 
            AND (elements NOT LIKE '%O%' OR elements IS NULL)
            AND band_gap IS NOT NULL
        ORDER BY band_gap DESC"
    ],
    'B4' => [
        'title' => 'Most Stable 10%',
        'description' => 'Top 10% most stable materials by formation energy',
        'sql' => "WITH ranked AS (
            SELECT
              m.material_id,
              m.formula_pretty,
              m.crystal_system,
              m.formation_energy_per_atom,
              m.band_gap,
              m.is_stable,
              -- total materials in each crystal system
              COUNT(*) OVER (PARTITION BY m.crystal_system) AS total_materials_in_system,
              -- rank by formation energy within each crystal system (ascending)
              ROW_NUMBER() OVER (PARTITION BY m.crystal_system ORDER BY m.formation_energy_per_atom) AS rn,
              -- how many items correspond to the bottom 10% (at least 1)
              GREATEST(1, CEIL(0.10 * COUNT(*) OVER (PARTITION BY m.crystal_system))) AS bottom_10_count
            FROM materials m
            WHERE m.crystal_system IS NOT NULL
              AND m.formation_energy_per_atom IS NOT NULL
          ),
          p10_values AS (
            -- determine the numeric cutoff (10th-percentile approximation) per system:
            SELECT
              crystal_system,
              ROUND(MAX(formation_energy_per_atom), 3) AS p10_formation_energy,
              total_materials_in_system
            FROM ranked
            WHERE rn <= bottom_10_count
            GROUP BY crystal_system, total_materials_in_system
          )
          SELECT
            r.material_id,
            r.formula_pretty,
            r.crystal_system,
            r.formation_energy_per_atom,
            p.p10_formation_energy AS system_10th_percentile,
            r.band_gap,
            r.is_stable,
            r.total_materials_in_system
          FROM ranked r
          JOIN p10_values p ON r.crystal_system = p.crystal_system
          WHERE r.total_materials_in_system >= 3
            -- keep only items that fall in the bottom 10% by rank
            AND r.rn <= r.bottom_10_count
          ORDER BY r.crystal_system, r.formation_energy_per_atom;
          "
    ],

    'C1' => [
        'title' => 'Most Stable per System',
        'description' => 'Most thermodynamically stable material in each crystal system',
        'sql' => "SELECT 
            m.crystal_system,
            m.material_id,
            m.formula_pretty,
            m.formation_energy_per_atom,
            m.band_gap
        FROM materials m
        WHERE m.formation_energy_per_atom = (
            SELECT MIN(formation_energy_per_atom)
            FROM materials m2 
            WHERE m2.crystal_system = m.crystal_system 
                AND formation_energy_per_atom IS NOT NULL
        )
        AND m.crystal_system IS NOT NULL
        ORDER BY m.formation_energy_per_atom"
    ],

    'C2' => [
        'title' => 'Band Gap vs System Average',
        'description' => 'Materials with band gaps above their crystal system average',
        'sql' => "SELECT 
        material_id,
        formula_pretty,
        crystal_system,
        band_gap as material_band_gap,
        ROUND(AVG(band_gap) OVER (PARTITION BY crystal_system), 3) as system_avg_band_gap,
        ROUND(band_gap - AVG(band_gap) OVER (PARTITION BY crystal_system), 3) as difference_from_system_avg,
        CASE 
            WHEN band_gap > AVG(band_gap) OVER (PARTITION BY crystal_system) + STDDEV(band_gap) OVER (PARTITION BY crystal_system) 
            THEN 'High outlier'
            WHEN band_gap > AVG(band_gap) OVER (PARTITION BY crystal_system) 
            THEN 'Above average'
            WHEN band_gap < AVG(band_gap) OVER (PARTITION BY crystal_system) - STDDEV(band_gap) OVER (PARTITION BY crystal_system) 
            THEN 'Low outlier'
            ELSE 'Below average'
        END as band_gap_category,
        formation_energy_per_atom,
        is_stable
    FROM materials 
    WHERE crystal_system IS NOT NULL 
        AND band_gap IS NOT NULL
    ORDER BY crystal_system, ABS(band_gap - AVG(band_gap) OVER (PARTITION BY crystal_system)) DESC;"
    ],

    'C3' => [
        'title' => '5th Period Elements',
        'description' => 'Materials containing at least one element from the 5th period',
        'sql' => "SELECT 
        material_id,
        formula_pretty,
        elements,
        band_gap,
        crystal_system,
        formation_energy_per_atom,
        is_stable,
        ROW_NUMBER() OVER (ORDER BY band_gap DESC) as band_gap_rank,
        DENSE_RANK() OVER (ORDER BY band_gap DESC) as band_gap_dense_rank,
        NTILE(4) OVER (ORDER BY band_gap DESC) as band_gap_quartile
    FROM materials 
    WHERE (elements LIKE '%Rb%' OR elements LIKE '%Sr%' OR elements LIKE '%Y%' OR 
           elements LIKE '%Zr%' OR elements LIKE '%Nb%' OR elements LIKE '%Mo%' OR 
           elements LIKE '%Ru%' OR elements LIKE '%Rh%' OR elements LIKE '%Pd%' OR 
           elements LIKE '%Ag%' OR elements LIKE '%Cd%' OR elements LIKE '%In%' OR 
           elements LIKE '%Sn%' OR elements LIKE '%Sb%' OR elements LIKE '%Te%' OR 
           elements LIKE '%I%')
        AND band_gap IS NOT NULL
    ORDER BY band_gap DESC;"
    ],

    'C4' => [
        'title' => 'Density Moving Average',
        'description' => 'Materials with 5-point moving average of density',
        'sql' => "SELECT 
        material_id,
        formula_pretty,
        formation_energy_per_atom,
        density,
        ROUND(AVG(density) OVER (
            ORDER BY formation_energy_per_atom 
            ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
        ), 3) as moving_avg_density_5pt,
        ROUND(AVG(density) OVER (
            ORDER BY formation_energy_per_atom 
            ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING  
        ), 3) as moving_avg_density_3pt,
        ROW_NUMBER() OVER (ORDER BY formation_energy_per_atom) as energy_rank,
        crystal_system,
        band_gap
    FROM materials 
    WHERE formation_energy_per_atom IS NOT NULL 
        AND density IS NOT NULL
    ORDER BY formation_energy_per_atom;"
    ],

    'D1' => [
        'title' => 'Element Frequency',
        'description' => 'Frequency of each element in the materials database',
        'sql' => "SELECT 
            element,
            COUNT(*) as material_count
        FROM (
            SELECT 
                material_id,
                TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(elements, ',', numbers.n), ',', -1)) AS element
            FROM materials
            JOIN (
                SELECT 1 n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL 
                SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL 
                SELECT 9 UNION ALL SELECT 10
            ) numbers ON CHAR_LENGTH(elements) - CHAR_LENGTH(REPLACE(elements, ',', '')) >= numbers.n - 1
            WHERE elements IS NOT NULL
        ) AS element_list
        GROUP BY element    
        ORDER BY material_count DESC"
    ],

    'D2' => [
        'title' => 'Binary Element Pairs',
        'description' => 'Most common binary element pairs in materials',
        'sql' => "SELECT 
        COUNT(DISTINCT elements) AS unique_binary_pairs,
        COUNT(*) AS total_binary_materials,
        ROUND(AVG(band_gap), 3) AS avg_band_gap_binary,
        ROUND(AVG(formation_energy_per_atom), 3) AS avg_formation_energy_binary,
        COUNT(CASE WHEN is_stable = 1 THEN 1 END) AS stable_binary_count
    FROM materials 
    WHERE nelements = 2
      AND elements IS NOT NULL;"
    ],

    'D3' => [
        'title' => 'Hexagonal Semiconductors',
        'description' => 'Stable semiconductors in hexagonal crystal system',
        'sql' => "SELECT 
            material_id,
            formula_pretty,
            band_gap,
            formation_energy_per_atom,
            energy_above_hull,
            elements
        FROM materials 
        WHERE crystal_system = 'Hexagonal'
            AND band_gap BETWEEN 0.1 AND 3.0
            AND (formation_energy_per_atom < 0 OR is_stable = 1)
            AND band_gap IS NOT NULL
        ORDER BY band_gap"
    ],

    'D4' => [
        'title' => 'Band Gap Outliers',
        'description' => 'Materials with band gaps as outliers within their crystal system',
        'sql' => "SELECT
        material_id,
        formula_pretty,
        crystal_system,
        band_gap,
        ROUND(AVG(band_gap) OVER (PARTITION BY crystal_system), 3) AS system_avg_band_gap,
        ROUND(STDDEV(band_gap) OVER (PARTITION BY crystal_system), 3) AS system_band_gap_stddev,
        CASE 
            WHEN band_gap > AVG(band_gap) OVER (PARTITION BY crystal_system) + 2 * STDDEV(band_gap) OVER (PARTITION BY crystal_system) 
            THEN 'High outlier'
            WHEN band_gap < AVG(band_gap) OVER (PARTITION BY crystal_system) - 2 * STDDEV(band_gap) OVER (PARTITION BY crystal_system) 
            THEN 'Low outlier'
            ELSE 'Normal'
        END AS band_gap_outlier_status,
        formation_energy_per_atom,
        is_stable
    FROM materials
    WHERE crystal_system IS NOT NULL 
        AND band_gap IS NOT NULL
    ORDER BY crystal_system, band_gap;"
    ],

    'D5' => [
        'title' => 'Stable Hexagonal Semiconductors',
        'description' => 'Thermodynamically stable semiconductors in hexagonal crystal system',
        'sql' => "SELECT 
        material_id,
        formula_pretty,
        band_gap,
        formation_energy_per_atom,
        energy_above_hull,
        space_group,
        elements,
        density,
        volume,
        CASE 
            WHEN band_gap < 1.0 THEN 'Narrow gap'
            WHEN band_gap < 2.0 THEN 'Medium gap'  
            ELSE 'Wide gap'
        END as semiconductor_type
    FROM materials 
    WHERE crystal_system = 'Hexagonal'
        AND band_gap BETWEEN 0.1 AND 3.0
        AND (formation_energy_per_atom < 0 OR is_stable = 1)
        AND band_gap IS NOT NULL
        AND formation_energy_per_atom IS NOT NULL
    ORDER BY band_gap, formation_energy_per_atom;"
    ],


];


class MaterialsAPI {
    private $pdo;
    
    public function __construct($config) {
        try {
            $dsn = "mysql:host={$config['host']};dbname={$config['database']};charset={$config['charset']}";
            $this->pdo = new PDO($dsn, $config['username'], $config['password'], [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES => false,
            ]);
        } catch (PDOException $e) {
            $this->sendError("Database connection failed: " . $e->getMessage());
        }
    }
    
    public function handleRequest() {
        $action = $_GET['action'] ?? '';
        
        switch ($action) {
            case 'stats':
                $this->getDatabaseStats();
                break;
            case 'query':
                $queryId = $_GET['id'] ?? '';
                $this->executeQuery($queryId);
                break;
            case 'custom':
                $this->executeCustomQuery();
                break;
            default:
                $this->sendError('Invalid action');
        }
    }
    
    private function getDatabaseStats() {
        try {
            $stats = [];
            
            // Total materials
            $stmt = $this->pdo->query("SELECT COUNT(*) FROM materials");
            $stats['total_materials'] = $stmt->fetchColumn();
            
            // Crystal systems
            $stmt = $this->pdo->query("SELECT COUNT(DISTINCT crystal_system) FROM materials WHERE crystal_system IS NOT NULL");
            $stats['crystal_systems'] = $stmt->fetchColumn();
            
            // Semiconductors
            $stmt = $this->pdo->query("SELECT COUNT(*) FROM materials WHERE band_gap BETWEEN 0.1 AND 3.0");
            $stats['semiconductors'] = $stmt->fetchColumn();
            
            // Metals
            $stmt = $this->pdo->query("SELECT COUNT(*) FROM materials WHERE band_gap = 0.0");
            $stats['metals'] = $stmt->fetchColumn();
            
            $this->sendSuccess($stats);
            
        } catch (PDOException $e) {
            $this->sendError("Error getting stats: " . $e->getMessage());
        }
    }
    
    private function executeQuery($queryId) {
        global $queries;
        
        if (!isset($queries[$queryId])) {
            $this->sendError('Query not found');
            return;
        }
        
        try {
            $start_time = microtime(true);
            
            $stmt = $this->pdo->prepare($queries[$queryId]['sql']);
            $stmt->execute();
            $results = $stmt->fetchAll();
            
            $execution_time = round((microtime(true) - $start_time) * 1000, 2);
            
            $this->sendSuccess([
                'query' => $queries[$queryId],
                'results' => $results,
                'execution_time' => $execution_time
            ]);
            
        } catch (PDOException $e) {
            $this->sendError("Query execution failed: " . $e->getMessage());
        }
    }
    
    private function executeCustomQuery() {
        $input = json_decode(file_get_contents('php://input'), true);
        $sql = trim($input['sql'] ?? '');
        
        if (empty($sql)) {
            $this->sendError('No SQL query provided');
            return;
        }
        
        // Security check - only allow SELECT statements
        if (!preg_match('/^\s*SELECT\s+/i', $sql)) {
            $this->sendError('Only SELECT queries are allowed');
            return;
        }
        
        try {
            $start_time = microtime(true);
            
            $stmt = $this->pdo->prepare($sql);
            $stmt->execute();
            $results = $stmt->fetchAll();
            
            $execution_time = round((microtime(true) - $start_time) * 1000, 2);
            
            $this->sendSuccess([
                'results' => $results,
                'execution_time' => $execution_time
            ]);
            
        } catch (PDOException $e) {
            $this->sendError("Query execution failed: " . $e->getMessage());
        }
    }
    
    private function sendSuccess($data) {
        echo json_encode(['success' => true] + $data);
    }
    
    private function sendError($message) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => $message]);
    }
}

// Handle the request
$api = new MaterialsAPI($db_config);
$api->handleRequest();
?>