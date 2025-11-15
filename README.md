# Materials Project Database Pipeline

A comprehensive pipeline for collecting, processing, and storing materials science data from the Materials Project API into a MySQL database using modern SQLAlchemy 2.0.

## 📋 Table of Contents

- [Overview](#overview)
- [Database Schema](#database-schema)
- [Pipeline Architecture](#pipeline-architecture)
- [Installation & Setup](#installation--setup)
- [Data Collection](#data-collection)
- [Database Import](#database-import)
- [Database Statistics](#database-statistics)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)

## 🎯 Overview

This project implements a complete ETL (Extract, Transform, Load) pipeline that:

1. **Extracts** materials data from the Materials Project API
2. **Transforms** and cleans the data for database storage
3. **Loads** the data into a MySQL database with proper schema design
4. **Provides** analysis and querying capabilities

### Key Features

- ✅ Modern SQLAlchemy 2.0 implementation
- ✅ Robust error handling and data validation
- ✅ Comprehensive materials properties coverage
- ✅ Efficient batch processing
- ✅ Data integrity and duplicate handling
- ✅ Detailed logging and progress tracking

## 🗄️ Database Schema

### Materials Table

The core `materials` table stores comprehensive materials properties:

```sql
CREATE TABLE materials (
    -- Primary Key
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Identifiers
    material_id VARCHAR(50) UNIQUE NOT NULL,     -- Materials Project ID (e.g., mp-149)
    formula_pretty VARCHAR(200) NOT NULL,        -- Chemical formula (e.g., Si, TiO2)
    formula_anonymous VARCHAR(200),              -- Anonymous formula (e.g., A, AB2)
    chemsys VARCHAR(200),                        -- Chemical system (e.g., Si, O-Ti)
    
    -- Crystal Structure
    crystal_system VARCHAR(50),                  -- Cubic, Tetragonal, etc.
    space_group VARCHAR(100),                    -- Space group symbol
    point_group VARCHAR(50),                     -- Point group symbol
    volume FLOAT,                                -- Unit cell volume (Ų)
    density FLOAT,                               -- Density (g/cm³)
    nsites INT,                                  -- Number of sites in unit cell
    
    -- Composition
    elements TEXT,                               -- Comma-separated elements
    nelements INT,                               -- Number of unique elements
    
    -- Energetics
    energy_per_atom FLOAT,                       -- Total energy per atom (eV)
    formation_energy_per_atom FLOAT,             -- Formation energy per atom (eV)
    energy_above_hull FLOAT,                     -- Energy above convex hull (eV)
    is_stable BOOLEAN,                           -- Thermodynamic stability
    theoretical BOOLEAN,                         -- Theoretical vs experimental
    
    -- Electronic Properties
    band_gap FLOAT,                              -- Electronic band gap (eV)
    cbm FLOAT,                                   -- Conduction band minimum (eV)
    vbm FLOAT,                                   -- Valence band maximum (eV)
    is_gap_direct BOOLEAN,                       -- Direct vs indirect band gap
    
    -- Structure Details
    structure_volume FLOAT,                      -- Structure volume
    structure_num_sites INT,                     -- Number of atomic sites
    structure_formula VARCHAR(200),              -- Structure formula
    
    -- Metadata
    query_type VARCHAR(100),                     -- Source query type
    collected_at DATETIME,                       -- Data collection timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for Performance
    INDEX idx_material_id (material_id),
    INDEX idx_formula (formula_pretty),
    INDEX idx_crystal_system (crystal_system),
    INDEX idx_band_gap (band_gap),
    INDEX idx_stable (is_stable),
    INDEX idx_elements (elements),
    INDEX idx_query_type (query_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### Material Properties Table

Extended properties storage for additional data:

```sql
CREATE TABLE material_properties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    material_id VARCHAR(50) NOT NULL,
    property_name VARCHAR(100) NOT NULL,
    property_value TEXT,
    source_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (material_id) REFERENCES materials(material_id) ON DELETE CASCADE,
    INDEX idx_material_property (material_id, property_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 🏗️ Pipeline Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Materials      │    │   Data           │    │   MySQL         │
│  Project API    │───▶│   Processing     │───▶│   Database      │
│                 │    │   & Validation   │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
   • Query by ID           • Clean NaN values      • Structured storage
   • Filter by props       • Type conversion       • Indexed queries  
   • Batch requests        • Error handling        • ACID compliance
   • Rate limiting         • Duplicate detection   • Backup & recovery
```

### Pipeline Components

1. **Data Collection (`collect_materials_data.py`)**
   - Materials Project API integration
   - Multiple query strategies
   - CSV/JSON export capabilities
   - Error handling and retry logic

2. **Data Import (`import_mp_data.py`)**
   - SQLAlchemy 2.0 ORM implementation
   - Batch processing with transaction management
   - Data validation and type conversion
   - Duplicate detection and updates

3. **Database Management**
   - Modern MySQL schema design
   - Optimized indexing strategy
   - Foreign key constraints
   - Performance monitoring

## 🚀 Installation & Setup

### Prerequisites

```bash
# Python 3.8+
python --version

# Required packages
pip install mp-api sqlalchemy pymysql pandas pymatgen numpy
```

### Environment Configuration

```bash
# Set environment variables
export MP_API_KEY="your_materials_project_api_key"
export DB_PASSWORD="your_database_password"

# Or create a .env file
echo "MP_API_KEY=your_api_key_here" > .env
echo "DB_PASSWORD=your_db_password" >> .env
```

### Database Connection

```python
# Database configuration
DB_CONFIG = {
    'host': 'dbase.cs.jhu.edu',
    'user': 'FA25_ycao73',
    'password': 'your_password',
    'database': 'FA25_ycao73_db',
    'charset': 'utf8mb4'
}
```

## 📊 Data Collection

### Query Strategies Implemented

Our pipeline implements multiple targeted query strategies:

#### 1. Specific Materials Query
```python
# Target high-impact materials
specific_materials = ["mp-149", "mp-13", "mp-390", "mp-2534", "mp-22526"]
docs = querier.query_summary_data(material_ids=specific_materials)
```

#### 2. Element-Based Queries
```python
# Silicon-containing materials
docs = querier.query_summary_data(elements=["Si"], limit=50)
```

#### 3. Property-Based Filtering
```python
# Semiconductor materials
docs = querier.query_summary_data(band_gap_range=(0.5, 4.0), limit=50)

# Stable materials
docs = querier.query_summary_data(
    formation_energy_range=(-3.0, 0.0), 
    energy_above_hull_range=(0, 0.1)
)
```

### Data Fields Collected

```python
fields = [
    # Identifiers
    'material_id', 'formula_pretty', 'formula_anonymous', 'chemsys',
    
    # Structure
    'crystal_system', 'space_group', 'point_group', 'volume', 
    'density', 'nsites', 'elements',
    
    # Energetics  
    'energy_per_atom', 'formation_energy_per_atom', 'energy_above_hull',
    'is_stable', 'theoretical',
    
    # Electronics
    'band_gap', 'cbm', 'vbm', 'is_gap_direct',
    
    # Structure details
    'structure', 'structure_volume', 'structure_num_sites'
]
```

## 💾 Database Import

### Import Process Flow

1. **Data Validation & Cleaning**
   ```python
   # Handle NaN values
   df = df.replace({pd.NA: None, pd.NaT: None})
   df = df.where(pd.notnull(df), None)
   df = df.replace([np.inf, -np.inf, np.nan], None)
   ```

2. **Duplicate Detection**
   ```python
   # Check for existing materials
   stmt = select(Material).where(Material.material_id == material_id)
   existing = session.scalars(stmt).first()
   ```

3. **Batch Processing**
   ```python
   # Process in batches for efficiency
   with session.no_autoflush:
       for index, row in df.iterrows():
           # Process each material
           # Commit every 10 records
   ```

4. **Error Handling**
   ```python
   try:
       session.commit()
   except Exception as e:
       session.rollback()
       # Log error and continue
   ```

## 📈 Database Statistics

### Current Database Contents

Based on our latest import:

```
📊 Database Overview:
   Total materials: 45

🔍 Materials by crystal system:
   Triclinic: 12 (26.7%)
   Cubic: 10 (22.2%)
   Monoclinic: 8 (17.8%)
   Tetragonal: 7 (15.6%)
   Orthorhombic: 3 (6.7%)
   Trigonal: 3 (6.7%)
   Hexagonal: 2 (4.4%)

📋 Materials by query type:
   elements_Si: 15 (33.3%)
   semiconductors: 20 (44.4%)
   specific_ids: 10 (22.2%)

⚡ Electronic properties:
   🔌 Semiconductors (0.1 < Eg < 5.0 eV): 30 (66.7%)
   🔗 Metals (Eg = 0.0 eV): 12 (26.7%)
   🧱 Insulators (Eg >= 5.0 eV): 1 (2.2%)
   ⚖️ Stable materials: 17 (37.8%)

📊 Band gap statistics:
   Min: 0.000 eV
   Max: 5.854 eV
   Avg: 1.334 eV

🔋 Formation energy statistics:
   Min: -3.508 eV/atom
   Max: 1.960 eV/atom  
   Avg: -0.698 eV/atom

🧪 Element distribution:
   Elemental (1 element): 17 (37.8%)
   Binary (2 elements): 9 (20.0%)
   Ternary (3 elements): 9 (20.0%)
   Quaternary (4 elements): 7 (15.6%)
   5+ elements: 3 (6.7%)
```

## 💡 Usage Examples

### 1. Connect to Database

```bash
# Command line access
mysql -h dbase.cs.jhu.edu -u FA25_ycao73 -p
USE FA25_ycao73_db;
```

### 2. Basic Queries

```sql
-- Count all materials
SELECT COUNT(*) FROM materials;

-- View sample materials
SELECT material_id, formula_pretty, crystal_system, band_gap 
FROM materials 
LIMIT 10;

-- Find semiconductors
SELECT material_id, formula_pretty, band_gap, crystal_system
FROM materials 
WHERE band_gap BETWEEN 1.0 AND 3.0
ORDER BY band_gap;

-- Group by crystal system
SELECT crystal_system, COUNT(*) as count
FROM materials 
GROUP BY crystal_system 
ORDER BY count DESC;
```

### 3. Advanced Analysis

```sql
-- Stable semiconductors for solar applications
SELECT material_id, formula_pretty, band_gap, formation_energy_per_atom
FROM materials 
WHERE band_gap BETWEEN 1.0 AND 2.0 
  AND is_stable = 1 
  AND energy_above_hull < 0.1
ORDER BY band_gap;

-- Materials by element count
SELECT nelements, COUNT(*) as count,
       AVG(band_gap) as avg_band_gap,
       AVG(formation_energy_per_atom) as avg_formation_energy
FROM materials 
WHERE nelements IS NOT NULL
GROUP BY nelements
ORDER BY nelements;

-- Wide band gap materials (for LEDs/lasers)
SELECT material_id, formula_pretty, band_gap, crystal_system
FROM materials 
WHERE band_gap > 3.0
ORDER BY band_gap DESC;
```

### 4. Python Analysis

```python
import pandas as pd
from sqlalchemy import create_engine

# Connect and query
engine = create_engine(connection_string)
query = """
SELECT material_id, formula_pretty, band_gap, 
       formation_energy_per_atom, crystal_system
FROM materials 
WHERE band_gap IS NOT NULL
"""

df = pd.read_sql(query, engine)

# Analysis
print("Band gap distribution:")
print(df['band_gap'].describe())

# Plotting
import matplotlib.pyplot as plt
df['band_gap'].hist(bins=20)
plt.xlabel('Band Gap (eV)')
plt.ylabel('Count')
plt.title('Band Gap Distribution')
plt.show()
```

## 🔧 API Reference

### Core Classes

#### `MaterialsDataCollector`
```python
class MaterialsDataCollector:
    def __init__(self, api_key, output_dir="mp_data")
    def collect_summary_data(self, query_name, **query_params)
    def save_data(self, materials_data, query_name)
```

#### `ModernDataImporter`  
```python
class ModernDataImporter:
    def setup_database_connection(self)
    def import_csv_data(self, csv_file)
    def verify_import(self)
    def generate_database_summary(self)
```

#### `Material` (SQLAlchemy Model)
```python
class Material(Base):
    __tablename__ = 'materials'
    
    # Key attributes
    material_id: Mapped[str]
    formula_pretty: Mapped[str] 
    crystal_system: Mapped[Optional[str]]
    band_gap: Mapped[Optional[float]]
    formation_energy_per_atom: Mapped[Optional[float]]
    # ... (see full schema above)
```

### Query Examples

```python
# Initialize collector
collector = MaterialsDataCollector(api_key)

# Collect specific materials
materials = collector.collect_summary_data(
    'high_performance_materials',
    material_ids=['mp-149', 'mp-390', 'mp-804']
)

# Collect by properties
semiconductors = collector.collect_summary_data(
    'wide_gap_semiconductors', 
    band_gap=(2.0, 4.0),
    is_stable=True
)
```

## 🔄 Pipeline Execution

### Complete Workflow

```bash
# 1. Collect data from Materials Project
python collect_materials_data.py

# 2. Import to database  
python import_mp_data.py

# 3. Verify and analyze
python analyze_database.py
```

### Automated Pipeline

```python
# run_pipeline.py
def main():
    # Data collection
    collector = MaterialsDataCollector(api_key)
    
    queries = [
        {'name': 'photovoltaics', 'params': {'band_gap': (1.0, 2.0)}},
        {'name': 'thermoelectrics', 'params': {'elements': ['Te', 'Bi']}},
        {'name': 'superconductors', 'params': {'elements': ['Cu', 'O']}}
    ]
    
    for query in queries:
        collector.collect_summary_data(query['name'], **query['params'])
    
    # Database import
    importer = ModernDataImporter()
    importer.setup_database_connection()
    importer.import_all_csv_files()
    importer.verify_import()
```

## 📝 Best Practices

### 1. Data Quality
- ✅ Always validate API responses
- ✅ Handle missing/NaN values appropriately  
- ✅ Implement comprehensive error logging
- ✅ Use transactions for data integrity

### 2. Performance Optimization
- ✅ Batch database operations
- ✅ Use appropriate indexes
- ✅ Implement connection pooling
- ✅ Monitor query performance

### 3. Scalability
- ✅ Design for incremental updates
- ✅ Implement proper pagination
- ✅ Use async operations for large datasets
- ✅ Plan for horizontal scaling

### 4. Maintenance
- ✅ Regular database backups
- ✅ Monitor API rate limits
- ✅ Update dependencies regularly
- ✅ Document schema changes

## 🚀 Future Enhancements

### Planned Features
- [ ] Real-time data synchronization
- [ ] Advanced materials property predictions
- [ ] Interactive web dashboard
- [ ] RESTful API for data access
- [ ] Machine learning integration
- [ ] Multi-database support

### Scaling Considerations
- [ ] Distributed database architecture
- [ ] Caching layer implementation
- [ ] API rate limit optimization
- [ ] Automated data pipeline monitoring

---

## 📞 Support

For questions or issues:
- 📧 Email: [yicao.alina@gmail.com]
- 🐛 Issues: [GitHub Issues](link-to-issues)
- 📖 Docs: [Full Documentation](link-to-docs)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Built with ❤️ for computatianal materials research at Johns Hopkins University*