
-- Query 1: Average band gap and formation energy for each crystal system
SELECT 
    crystal_system,
    COUNT(*) as material_count,
    ROUND(AVG(band_gap), 3) as avg_band_gap,
    ROUND(AVG(formation_energy_per_atom), 3) as avg_formation_energy_eV_per_atom,
    ROUND(STDDEV(band_gap), 3) as stddev_band_gap,
    ROUND(STDDEV(formation_energy_per_atom), 3) as stddev_formation_energy
FROM materials 
WHERE crystal_system IS NOT NULL 
    AND band_gap IS NOT NULL 
    AND formation_energy_per_atom IS NOT NULL
GROUP BY crystal_system
ORDER BY material_count DESC, avg_band_gap DESC;

-- Query 2: Crystal systems with more than 5 materials (adjusted for current dataset size)
SELECT 
    crystal_system,
    COUNT(*) as material_count,
    ROUND(AVG(band_gap), 3) as avg_band_gap,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM materials WHERE crystal_system IS NOT NULL), 1) as percentage_of_total
FROM materials 
WHERE crystal_system IS NOT NULL
GROUP BY crystal_system
HAVING COUNT(*) > 5
ORDER BY material_count DESC;

-- Alternative: Show all crystal systems with their counts for current dataset
SELECT 
    crystal_system,
    COUNT(*) as material_count,
    CASE 
        WHEN COUNT(*) >= 10 THEN 'High'
        WHEN COUNT(*) >= 5 THEN 'Medium' 
        ELSE 'Low'
    END as frequency_category
FROM materials 
WHERE crystal_system IS NOT NULL
GROUP BY crystal_system
ORDER BY material_count DESC;

-- Query 3: Materials comparison by number of elements (stability analysis)
SELECT 
    nelements,
    COUNT(*) as material_count,
    ROUND(MIN(formation_energy_per_atom), 3) as most_stable_formation_energy,
    ROUND(AVG(formation_energy_per_atom), 3) as avg_formation_energy,
    ROUND(MAX(formation_energy_per_atom), 3) as least_stable_formation_energy,
    ROUND(STDDEV(formation_energy_per_atom), 3) as stddev_formation_energy,
    COUNT(CASE WHEN is_stable = 1 THEN 1 END) as stable_materials_count,
    ROUND(100.0 * COUNT(CASE WHEN is_stable = 1 THEN 1 END) / COUNT(*), 1) as stability_percentage
FROM materials 
WHERE nelements BETWEEN 1 AND 6 
    AND formation_energy_per_atom IS NOT NULL
GROUP BY nelements
ORDER BY nelements;

-- Additional: Show specific examples of most stable materials in each category
SELECT 
    nelements,
    material_id,
    formula_pretty,
    formation_energy_per_atom,
    crystal_system,
    is_stable
FROM materials m1
WHERE formation_energy_per_atom = (
    SELECT MIN(formation_energy_per_atom)
    FROM materials m2 
    WHERE m2.nelements = m1.nelements 
        AND formation_energy_per_atom IS NOT NULL
)
    AND nelements BETWEEN 1 AND 6
ORDER BY nelements;

-- Query 4: Materials containing Tellurium (Te)
SELECT 
    COUNT(*) as te_materials_count,
    ROUND(AVG(band_gap), 3) as avg_band_gap_eV,
    ROUND(MIN(band_gap), 3) as min_band_gap_eV,
    ROUND(MAX(band_gap), 3) as max_band_gap_eV,
    ROUND(STDDEV(band_gap), 3) as stddev_band_gap
FROM materials 
WHERE elements LIKE '%Te%' 
    AND band_gap IS NOT NULL;

-- Show specific Te-containing materials
SELECT 
    material_id,
    formula_pretty,
    elements,
    band_gap,
    crystal_system,
    formation_energy_per_atom
FROM materials 
WHERE elements LIKE '%Te%'
    AND band_gap IS NOT NULL
ORDER BY band_gap DESC;

-- Compare with overall database average
SELECT 
    'Te-containing' as material_type,
    COUNT(*) as count,
    ROUND(AVG(band_gap), 3) as avg_band_gap
FROM materials 
WHERE elements LIKE '%Te%' AND band_gap IS NOT NULL
UNION ALL
SELECT 
    'All materials' as material_type,
    COUNT(*) as count,
    ROUND(AVG(band_gap), 3) as avg_band_gap
FROM materials 
WHERE band_gap IS NOT NULL;

-- Query 5: Materials with above-average band gaps
WITH avg_bandgap AS (
    SELECT AVG(band_gap) as db_avg_bandgap
    FROM materials 
    WHERE band_gap IS NOT NULL
)
SELECT 
    m.material_id,
    m.formula_pretty,
    m.band_gap,
    ROUND(a.db_avg_bandgap, 3) as database_avg_bandgap,
    ROUND(m.band_gap - a.db_avg_bandgap, 3) as difference_from_avg,
    m.crystal_system,
    m.formation_energy_per_atom,
    m.is_stable
FROM materials m
CROSS JOIN avg_bandgap a
WHERE m.band_gap > a.db_avg_bandgap
    AND m.band_gap IS NOT NULL
ORDER BY m.band_gap DESC;

-- Summary statistics
SELECT 
    COUNT(*) as above_avg_count,
    (SELECT COUNT(*) FROM materials WHERE band_gap IS NOT NULL) as total_with_bandgap,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM materials WHERE band_gap IS NOT NULL), 1) as percentage_above_avg,
    (SELECT ROUND(AVG(band_gap), 3) FROM materials WHERE band_gap IS NOT NULL) as database_avg_bandgap
FROM materials 
WHERE band_gap > (SELECT AVG(band_gap) FROM materials WHERE band_gap IS NOT NULL);

-- Query 6: Materials with both Sb and Te
SELECT 
    material_id,
    formula_pretty,
    elements,
    band_gap,
    formation_energy_per_atom,
    crystal_system,
    nelements,
    is_stable
FROM materials 
WHERE elements LIKE '%Sb%' 
    AND elements LIKE '%Te%'
ORDER BY band_gap DESC;

-- Count and statistics
SELECT 
    COUNT(*) as sb_te_materials_count,
    ROUND(AVG(band_gap), 3) as avg_band_gap,
    ROUND(AVG(formation_energy_per_atom), 3) as avg_formation_energy,
    COUNT(CASE WHEN is_stable = 1 THEN 1 END) as stable_count
FROM materials 
WHERE elements LIKE '%Sb%' 
    AND elements LIKE '%Te%';

-- If no Sb+Te materials exist, show Sb materials and Te materials separately
SELECT 'Sb-containing' as type, COUNT(*) as count
FROM materials WHERE elements LIKE '%Sb%'
UNION ALL
SELECT 'Te-containing' as type, COUNT(*) as count  
FROM materials WHERE elements LIKE '%Te%'
UNION ALL
SELECT 'Sb+Te both' as type, COUNT(*) as count
FROM materials WHERE elements LIKE '%Sb%' AND elements LIKE '%Te%';

-- Query 7: Wide band gap materials (>3.0 eV) without Oxygen
SELECT 
    material_id,
    formula_pretty,
    elements,
    band_gap,
    formation_energy_per_atom,
    crystal_system,
    nelements,
    is_stable,
    CASE 
        WHEN band_gap > 5.0 THEN 'Ultra-wide gap'
        WHEN band_gap > 4.0 THEN 'Very wide gap'  
        ELSE 'Wide gap'
    END as gap_category
FROM materials 
WHERE band_gap > 3.0 
    AND (elements NOT LIKE '%O%' OR elements IS NULL)
    AND band_gap IS NOT NULL
ORDER BY band_gap DESC;

-- Statistics
SELECT 
    COUNT(*) as wide_gap_no_oxygen_count,
    ROUND(AVG(band_gap), 3) as avg_band_gap,
    ROUND(MIN(band_gap), 3) as min_band_gap,
    ROUND(MAX(band_gap), 3) as max_band_gap,
    COUNT(CASE WHEN is_stable = 1 THEN 1 END) as stable_count
FROM materials 
WHERE band_gap > 3.0 
    AND (elements NOT LIKE '%O%' OR elements IS NULL);

-- Compare with all wide gap materials
SELECT 
    'Without O' as material_type,
    COUNT(*) as count,
    ROUND(AVG(band_gap), 3) as avg_band_gap
FROM materials 
WHERE band_gap > 3.0 AND (elements NOT LIKE '%O%' OR elements IS NULL)
UNION ALL
SELECT 
    'All wide gap' as material_type,
    COUNT(*) as count,
    ROUND(AVG(band_gap), 3) as avg_band_gap
FROM materials 
WHERE band_gap > 3.0;

-- Query 8: Most stable materials (bottom 10% formation energy) by crystal system
WITH ranked AS (
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


-- -- Alternative approach using ROW_NUMBER for exact 10%
-- WITH ranked_materials AS (
--     SELECT 
--         material_id,
--         formula_pretty,
--         crystal_system,
--         formation_energy_per_atom,
--         band_gap,
--         is_stable,
--         ROW_NUMBER() OVER (PARTITION BY crystal_system ORDER BY formation_energy_per_atom) as stability_rank,
--         COUNT(*) OVER (PARTITION BY crystal_system) as total_in_system
--     FROM materials 
--     WHERE crystal_system IS NOT NULL 
--         AND formation_energy_per_atom IS NOT NULL
-- )
-- SELECT 
--     material_id,
--     formula_pretty,
--     crystal_system,
--     formation_energy_per_atom,
--     band_gap,
--     is_stable,
--     stability_rank,
--     total_in_system,
--     ROUND(100.0 * stability_rank / total_in_system, 1) as percentile_rank
-- FROM ranked_materials
-- WHERE stability_rank <= GREATEST(1, FLOOR(total_in_system * 0.1))
-- ORDER BY crystal_system, stability_rank;

-- Query 9: Most thermodynamically stable material per crystal system
WITH most_stable_per_system AS (
    SELECT 
        crystal_system,
        MIN(formation_energy_per_atom) as min_formation_energy
    FROM materials 
    WHERE crystal_system IS NOT NULL 
        AND formation_energy_per_atom IS NOT NULL
    GROUP BY crystal_system
)
SELECT 
    m.crystal_system,
    m.material_id,
    m.formula_pretty,
    m.formation_energy_per_atom as most_stable_formation_energy,
    m.band_gap,
    m.energy_above_hull,
    m.is_stable,
    m.nelements,
    COUNT(*) OVER (PARTITION BY m.crystal_system) as total_materials_in_system
FROM materials m
JOIN most_stable_per_system ms ON m.crystal_system = ms.crystal_system 
    AND m.formation_energy_per_atom = ms.min_formation_energy
ORDER BY m.formation_energy_per_atom, m.crystal_system;

-- Alternative using window functions
WITH ranked AS (
  SELECT 
    crystal_system,
    material_id,
    formula_pretty,
    formation_energy_per_atom,
    band_gap,
    is_stable,
    ROW_NUMBER() OVER (PARTITION BY crystal_system
                       ORDER BY formation_energy_per_atom) AS stability_rank
  FROM materials
  WHERE crystal_system IS NOT NULL
    AND formation_energy_per_atom IS NOT NULL
)
SELECT
  crystal_system,
  material_id,
  formula_pretty,
  formation_energy_per_atom,
  band_gap,
  is_stable,
  stability_rank
FROM ranked
WHERE stability_rank = 1
ORDER BY crystal_system, formation_energy_per_atom;


-- Query 10: Each material's band gap vs crystal system average
SELECT 
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
ORDER BY crystal_system, ABS(band_gap - AVG(band_gap) OVER (PARTITION BY crystal_system)) DESC;

-- Query 11: Materials containing 5th period elements (Rb-Xe) ranked by band gap
-- 5th period elements: Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe
SELECT 
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
ORDER BY band_gap DESC;

-- Summary of 5th period element presence
SELECT 
    '5th period elements' as element_group,
    COUNT(*) as material_count,
    ROUND(AVG(band_gap), 3) as avg_band_gap,
    ROUND(MIN(band_gap), 3) as min_band_gap,
    ROUND(MAX(band_gap), 3) as max_band_gap
FROM materials 
WHERE (elements LIKE '%Rb%' OR elements LIKE '%Sr%' OR elements LIKE '%Y%' OR 
       elements LIKE '%Zr%' OR elements LIKE '%Nb%' OR elements LIKE '%Mo%' OR 
       elements LIKE '%Ru%' OR elements LIKE '%Rh%' OR elements LIKE '%Pd%' OR 
       elements LIKE '%Ag%' OR elements LIKE '%Cd%' OR elements LIKE '%In%' OR 
       elements LIKE '%Sn%' OR elements LIKE '%Sb%' OR elements LIKE '%Te%' OR 
       elements LIKE '%I%')
    AND band_gap IS NOT NULL;

-- Query 12: Moving average of density ordered by formation energy
SELECT 
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
ORDER BY formation_energy_per_atom;

-- Density trends analysis
WITH bucketed AS (
    SELECT
        NTILE(5) OVER (ORDER BY formation_energy_per_atom) AS energy_quintile,
        formation_energy_per_atom,
        density
    FROM materials
    WHERE formation_energy_per_atom IS NOT NULL
      AND density IS NOT NULL
)
SELECT
    energy_quintile,
    COUNT(*) AS material_count,
    ROUND(AVG(formation_energy_per_atom), 3) AS avg_formation_energy,
    ROUND(AVG(density), 3) AS avg_density,
    ROUND(MIN(density), 3) AS min_density,
    ROUND(MAX(density), 3) AS max_density,
    ROUND(STDDEV(density), 3) AS stddev_density
FROM bucketed
GROUP BY energy_quintile
ORDER BY energy_quintile;


-- Query 13: Element frequency analysis
-- Note: This requires parsing the comma-separated elements field
WITH element_counts AS (
    SELECT 
        TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(elements, ',', numbers.n), ',', -1)) as element,
        COUNT(*) as frequency
    FROM materials
    CROSS JOIN (
        SELECT 1 n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL 
        SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL
        SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10
    ) numbers
    WHERE CHAR_LENGTH(elements) - CHAR_LENGTH(REPLACE(elements, ',', '')) >= numbers.n - 1
        AND elements IS NOT NULL
        AND TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(elements, ',', numbers.n), ',', -1)) != ''
    GROUP BY TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(elements, ',', numbers.n), ',', -1))
)
SELECT 
    element,
    frequency as material_count,
    ROUND(100.0 * frequency / (SELECT COUNT(*) FROM materials WHERE elements IS NOT NULL), 2) as percentage,
    DENSE_RANK() OVER (ORDER BY frequency DESC) as popularity_rank
FROM element_counts
WHERE element != ''
ORDER BY frequency DESC, element;

-- Simplified version using LIKE patterns for common elements
SELECT 
    'Si' as element, COUNT(*) as frequency FROM materials WHERE elements LIKE '%Si%'
UNION ALL SELECT 'O', COUNT(*) FROM materials WHERE elements LIKE '%O%'
UNION ALL SELECT 'Al', COUNT(*) FROM materials WHERE elements LIKE '%Al%'
UNION ALL SELECT 'Fe', COUNT(*) FROM materials WHERE elements LIKE '%Fe%'
UNION ALL SELECT 'Ti', COUNT(*) FROM materials WHERE elements LIKE '%Ti%'
UNION ALL SELECT 'Ga', COUNT(*) FROM materials WHERE elements LIKE '%Ga%'
UNION ALL SELECT 'Li', COUNT(*) FROM materials WHERE elements LIKE '%Li%'
UNION ALL SELECT 'Co', COUNT(*) FROM materials WHERE elements LIKE '%Co%'
UNION ALL SELECT 'Ni', COUNT(*) FROM materials WHERE elements LIKE '%Ni%'
UNION ALL SELECT 'Ag', COUNT(*) FROM materials WHERE elements LIKE '%Ag%'
ORDER BY frequency DESC;


-- Query 14: Element pairs in binary compounds
SELECT 
    elements as element_pair,
    COUNT(*) as frequency,
    ROUND(AVG(band_gap), 3) as avg_band_gap,
    ROUND(AVG(formation_energy_per_atom), 3) as avg_formation_energy,
    COUNT(CASE WHEN is_stable = 1 THEN 1 END) as stable_count,
    GROUP_CONCAT(DISTINCT crystal_system ORDER BY crystal_system) as crystal_systems_found,
    GROUP_CONCAT(DISTINCT material_id ORDER BY band_gap DESC LIMIT 3) as example_materials
FROM materials 
WHERE nelements = 2 
    AND elements IS NOT NULL
    AND elements NOT LIKE '%,%,%'  -- Ensure truly binary
GROUP BY elements
HAVING COUNT(*) > 1  -- Only pairs that appear multiple times
ORDER BY frequency DESC, avg_formation_energy;

-- Analysis of binary compound trends
SELECT 
    COUNT(DISTINCT elements) as unique_binary_pairs,
    COUNT(*) as total_binary_materials,
    ROUND(AVG(band_gap), 3) as avg_band_gap_binary,
    ROUND(AVG(formation_energy_per_atom), 3) as avg_formation_energy_binary,
    COUNT(CASE WHEN is_stable = 1 THEN 1 END) as stable_binary_count
FROM materials 
WHERE nelements = 2;


-- Query 15: Thermodynamically stable semiconductors in hexagonal crystal system
SELECT 
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
ORDER BY band_gap, formation_energy_per_atom;

-- Summary statistics
SELECT 
    COUNT(*) as hexagonal_semiconductor_count,
    ROUND(AVG(band_gap), 3) as avg_band_gap,
    ROUND(AVG(formation_energy_per_atom), 3) as avg_formation_energy,
    ROUND(MIN(band_gap), 3) as min_band_gap,
    ROUND(MAX(band_gap), 3) as max_band_gap,
    COUNT(CASE WHEN is_stable = 1 THEN 1 END) as confirmed_stable_count
FROM materials 
WHERE crystal_system = 'Hexagonal'
    AND band_gap BETWEEN 0.1 AND 3.0
    AND (formation_energy_per_atom < 0 OR is_stable = 1);


-- Query 16: Materials with band gaps >2 standard deviations above their element group mean
WITH element_stats AS (
    SELECT 
        nelements,
        AVG(band_gap) as mean_band_gap,
        STDDEV(band_gap) as stddev_band_gap,
        COUNT(*) as group_size
    FROM materials 
    WHERE band_gap IS NOT NULL 
        AND nelements IS NOT NULL
    GROUP BY nelements
    HAVING COUNT(*) >= 3  -- Need enough materials for meaningful statistics
),
anomalous_materials AS (
    SELECT 
        m.material_id,
        m.formula_pretty,
        m.band_gap,
        m.nelements,
        m.crystal_system,
        m.formation_energy_per_atom,
        e.mean_band_gap,
        e.stddev_band_gap,
        ROUND((m.band_gap - e.mean_band_gap) / e.stddev_band_gap, 2) as z_score
    FROM materials m
    JOIN element_stats e ON m.nelements = e.nelements
    WHERE m.band_gap > e.mean_band_gap + 2 * e.stddev_band_gap
        AND m.band_gap IS NOT NULL
)
SELECT 
    material_id,
    formula_pretty,
    band_gap,
    nelements,
    crystal_system,
    formation_energy_per_atom,
    ROUND(mean_band_gap, 3) as group_mean_band_gap,
    ROUND(stddev_band_gap, 3) as group_stddev_band_gap,
    z_score as standard_deviations_above_mean
FROM anomalous_materials
ORDER BY z_score DESC;

-- Show the statistics for each element group
SELECT 
    nelements as element_count,
    COUNT(*) as materials_in_group,
    ROUND(AVG(band_gap), 3) as mean_band_gap,
    ROUND(STDDEV(band_gap), 3) as stddev_band_gap,
    ROUND(MIN(band_gap), 3) as min_band_gap,
    ROUND(MAX(band_gap), 3) as max_band_gap
FROM materials 
WHERE band_gap IS NOT NULL 
    AND nelements IS NOT NULL
GROUP BY nelements
ORDER BY nelements;


-- Query 17: Space groups most associated with metallic behavior (band_gap = 0)
SELECT 
    space_group,
    COUNT(*) as total_materials,
    COUNT(CASE WHEN band_gap = 0.0 THEN 1 END) as metallic_materials,
    COUNT(CASE WHEN band_gap > 0.0 THEN 1 END) as non_metallic_materials,
    ROUND(100.0 * COUNT(CASE WHEN band_gap = 0.0 THEN 1 END) / COUNT(*), 1) as metallic_percentage,
    ROUND(AVG(band_gap), 3) as avg_band_gap,
    GROUP_CONCAT(DISTINCT crystal_system) as crystal_systems,
    GROUP_CONCAT(DISTINCT CASE WHEN band_gap = 0.0 THEN material_id END ORDER BY material_id LIMIT 3) as example_metals
FROM materials 
WHERE space_group IS NOT NULL 
    AND band_gap IS NOT NULL
GROUP BY space_group
HAVING COUNT(*) >= 2  -- Only space groups with multiple materials
ORDER BY metallic_percentage DESC, total_materials DESC;

-- Overall metallic behavior statistics
SELECT 
    COUNT(*) as total_materials_with_bandgap,
    COUNT(CASE WHEN band_gap = 0.0 THEN 1 END) as metallic_materials,
    COUNT(CASE WHEN band_gap BETWEEN 0.1 AND 3.0 THEN 1 END) as semiconductor_materials,
    COUNT(CASE WHEN band_gap > 3.0 THEN 1 END) as insulator_materials,
    ROUND(100.0 * COUNT(CASE WHEN band_gap = 0.0 THEN 1 END) / COUNT(*), 1) as metallic_percentage
FROM materials 
WHERE band_gap IS NOT NULL;

-- Crystal system vs metallic behavior
SELECT 
    crystal_system,
    COUNT(*) as total_materials,
    COUNT(CASE WHEN band_gap = 0.0 THEN 1 END) as metallic_count,
    ROUND(100.0 * COUNT(CASE WHEN band_gap = 0.0 THEN 1 END) / COUNT(*), 1) as metallic_percentage
FROM materials 
WHERE crystal_system IS NOT NULL 
    AND band_gap IS NOT NULL
GROUP BY crystal_system
ORDER BY metallic_percentage DESC;


-- Bonus: Comprehensive database overview
SELECT 
    'Total Materials' as metric,
    COUNT(*) as value,
    '' as details
FROM materials
UNION ALL
SELECT 
    'Crystal Systems',
    COUNT(DISTINCT crystal_system),
    GROUP_CONCAT(DISTINCT crystal_system ORDER BY crystal_system)
FROM materials WHERE crystal_system IS NOT NULL
UNION ALL
SELECT 
    'Metallic Materials',
    COUNT(*),
    CONCAT(ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM materials WHERE band_gap IS NOT NULL), 1), '%')
FROM materials WHERE band_gap = 0.0
UNION ALL
SELECT 
    'Semiconductor Materials', 
    COUNT(*),
    CONCAT(ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM materials WHERE band_gap IS NOT NULL), 1), '%')
FROM materials WHERE band_gap BETWEEN 0.1 AND 3.0
UNION ALL
SELECT 
    'Stable Materials',
    COUNT(*),
    CONCAT(ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM materials WHERE is_stable IS NOT NULL), 1), '%')
FROM materials WHERE is_stable = 1;

