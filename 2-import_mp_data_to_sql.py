#!/usr/bin/env python3
# file: import_mp_data_to_sql.py

import os
import json
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import glob

# Database configuration
DB_CONFIG = {
    'host': 'dbase.cs.jhu.edu',
    'user': 'FA25_ycao73',
    'password': 'Mel62w66gA',  
    'database': 'FA25_ycao73',
    'charset': 'utf8mb4'
}

Base = declarative_base()

class Material(Base):
    __tablename__ = 'materials'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic identifiers
    material_id = Column(String(50), unique=True, nullable=False, index=True)
    formula_pretty = Column(String(200), nullable=False)
    formula_anonymous = Column(String(200))
    chemsys = Column(String(200))
    
    # Structure information
    crystal_system = Column(String(50))
    space_group = Column(String(100))
    point_group = Column(String(50))
    volume = Column(Float)
    density = Column(Float)
    nsites = Column(Integer)
    
    # Elements (stored as comma-separated string)
    elements = Column(Text)
    nelements = Column(Integer)
    
    # Energy properties
    energy_per_atom = Column(Float)
    formation_energy_per_atom = Column(Float)
    energy_above_hull = Column(Float)
    is_stable = Column(Boolean)
    theoretical = Column(Boolean)
    
    # Electronic properties
    band_gap = Column(Float)
    cbm = Column(Float)  # Conduction band minimum
    vbm = Column(Float)  # Valence band maximum
    is_gap_direct = Column(Boolean)
    
    # Structure details
    structure_volume = Column(Float)
    structure_num_sites = Column(Integer)
    structure_formula = Column(String(200))
    
    # Metadata
    query_type = Column(String(100))
    collected_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add indexes for common queries
    __table_args__ = (
        Index('idx_formula', 'formula_pretty'),
        Index('idx_crystal_system', 'crystal_system'),
        Index('idx_band_gap', 'band_gap'),
        Index('idx_stable', 'is_stable'),
        Index('idx_elements', 'elements'),
        Index('idx_query_type', 'query_type'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
    )

class MaterialProperty(Base):
    __tablename__ = 'material_properties'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    material_id = Column(String(50), nullable=False, index=True)
    property_name = Column(String(100), nullable=False)
    property_value = Column(Text)
    source_type = Column(String(50))  # 'summary', 'electronic_structure', etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_material_property', 'material_id', 'property_name'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
    )

class DataImporter:
    def __init__(self):
        self.engine = None
        self.session = None
    
    def setup_database_connection(self):
        """Setup database connection"""
        db_password = os.getenv('DB_PASSWORD')
        if not db_password:
            db_password = input("Enter database password: ")
        
        DB_CONFIG['password'] = db_password
        
        connection_string = (
            f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['host']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"
        )
        
        try:
            self.engine = create_engine(connection_string, echo=False)
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute("SELECT 1")
                print("✅ Database connection successful!")
            
            # Create tables
            print("Creating database tables...")
            Base.metadata.create_all(self.engine)
            print("✅ Tables created successfully!")
            
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def import_csv_data(self, csv_file):
        """Import materials data from CSV file"""
        print(f"\n📂 Importing data from: {csv_file}")
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            print(f"   Found {len(df)} materials in CSV")
            
            # Clean data
            df = df.where(pd.notnull(df), None)  # Replace NaN with None
            
            imported_count = 0
            updated_count = 0
            error_count = 0
            
            for index, row in df.iterrows():
                try:
                    material_id = row.get('material_id')
                    if not material_id:
                        print(f"   ⚠️ Skipping row {index}: No material_id")
                        continue
                    
                    # Check if material already exists
                    existing = self.session.query(Material).filter_by(
                        material_id=material_id
                    ).first()
                    
                    if existing:
                        material = existing
                        updated_count += 1
                        action = "Updated"
                    else:
                        material = Material()
                        imported_count += 1
                        action = "Imported"
                    
                    # Map CSV columns to database fields
                    material.material_id = material_id
                    material.formula_pretty = row.get('formula_pretty')
                    material.formula_anonymous = row.get('formula_anonymous')
                    material.chemsys = row.get('chemsys')
                    material.crystal_system = row.get('crystal_system')
                    material.space_group = row.get('space_group')
                    material.point_group = row.get('point_group')
                    material.volume = self._safe_float(row.get('volume'))
                    material.density = self._safe_float(row.get('density'))
                    material.nsites = self._safe_int(row.get('nsites'))
                    material.elements = row.get('elements')  # Already comma-separated
                    
                    # Count elements
                    if material.elements:
                        material.nelements = len(material.elements.split(','))
                    
                    # Energy properties
                    material.energy_per_atom = self._safe_float(row.get('energy_per_atom'))
                    material.formation_energy_per_atom = self._safe_float(row.get('formation_energy_per_atom'))
                    material.energy_above_hull = self._safe_float(row.get('energy_above_hull'))
                    material.is_stable = self._safe_bool(row.get('is_stable'))
                    material.theoretical = self._safe_bool(row.get('theoretical'))
                    
                    # Electronic properties
                    material.band_gap = self._safe_float(row.get('band_gap'))
                    material.cbm = self._safe_float(row.get('cbm'))
                    material.vbm = self._safe_float(row.get('vbm'))
                    material.is_gap_direct = self._safe_bool(row.get('is_gap_direct'))
                    
                    # Structure details
                    material.structure_volume = self._safe_float(row.get('structure_volume'))
                    material.structure_num_sites = self._safe_int(row.get('structure_num_sites'))
                    material.structure_formula = row.get('structure_formula')
                    
                    # Metadata
                    material.query_type = row.get('query_type')
                    material.collected_at = self._safe_datetime(row.get('collected_at'))
                    
                    if not existing:
                        self.session.add(material)
                    
                    # Commit every 50 materials
                    if (imported_count + updated_count) % 50 == 0:
                        self.session.commit()
                        print(f"   Progress: {imported_count + updated_count} materials processed...")
                
                except Exception as e:
                    error_count += 1
                    print(f"   ❌ Error processing material {row.get('material_id', 'unknown')}: {e}")
                    self.session.rollback()
                    continue
            
            # Final commit
            self.session.commit()
            
            print(f"   ✅ Import completed:")
            print(f"      - New materials imported: {imported_count}")
            print(f"      - Existing materials updated: {updated_count}")
            print(f"      - Errors: {error_count}")
            
            return imported_count + updated_count
            
        except Exception as e:
            print(f"   ❌ Error importing CSV: {e}")
            self.session.rollback()
            return 0
    
    def import_json_additional_data(self, json_file):
        """Import additional properties from JSON file"""
        print(f"\n📂 Importing additional data from: {json_file}")
        
        try:
            with open(json_file, 'r') as f:
                materials_data = json.load(f)
            
            print(f"   Found {len(materials_data)} materials in JSON")
            
            properties_added = 0
            
            for material_data in materials_data:
                material_id = material_data.get('material_id')
                if not material_id:
                    continue
                
                # Add electronic structure properties if available
                if 'electronic_structure' in material_data:
                    es_data = material_data['electronic_structure']
                    for prop_name, prop_value in es_data.items():
                        if prop_value is not None:
                            self._add_material_property(
                                material_id, prop_name, prop_value, 'electronic_structure'
                            )
                            properties_added += 1
                
                # Add magnetism properties if available
                if 'magnetism' in material_data:
                    mag_data = material_data['magnetism']
                    for prop_name, prop_value in mag_data.items():
                        if prop_value is not None:
                            self._add_material_property(
                                material_id, prop_name, prop_value, 'magnetism'
                            )
                            properties_added += 1
            
            self.session.commit()
            print(f"   ✅ Added {properties_added} additional properties")
            
        except Exception as e:
            print(f"   ❌ Error importing JSON: {e}")
            self.session.rollback()
    
    def _add_material_property(self, material_id, prop_name, prop_value, source_type):
        """Add a material property to the database"""
        
        # Check if property already exists
        existing = self.session.query(MaterialProperty).filter_by(
            material_id=material_id,
            property_name=prop_name,
            source_type=source_type
        ).first()
        
        if not existing:
            prop = MaterialProperty(
                material_id=material_id,
                property_name=prop_name,
                property_value=str(prop_value),
                source_type=source_type
            )
            self.session.add(prop)
    
    def _safe_float(self, value):
        """Safely convert to float"""
        if value is None or value == '' or pd.isna(value):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value):
        """Safely convert to int"""
        if value is None or value == '' or pd.isna(value):
            return None
        try:
            return int(float(value))  # Handle cases like "5.0"
        except (ValueError, TypeError):
            return None
    
    def _safe_bool(self, value):
        """Safely convert to bool"""
        if value is None or value == '' or pd.isna(value):
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        try:
            return bool(int(value))
        except (ValueError, TypeError):
            return None
    
    def _safe_datetime(self, value):
        """Safely convert to datetime"""
        if value is None or value == '' or pd.isna(value):
            return None
        try:
            return pd.to_datetime(value)
        except:
            return None
    
    def verify_import(self):
        """Verify the imported data"""
        print(f"\n📊 VERIFICATION REPORT")
        print("=" * 50)
        
        try:
            # Total materials
            total_materials = self.session.query(Material).count()
            print(f"Total materials in database: {total_materials}")
            
            # Materials by crystal system
            from sqlalchemy import func
            crystal_systems = self.session.query(
                Material.crystal_system,
                func.count(Material.crystal_system)
            ).group_by(Material.crystal_system).all()
            
            print(f"\nMaterials by crystal system:")
            for system, count in crystal_systems:
                print(f"  {system or 'Unknown'}: {count}")
            
            # Materials by query type
            query_types = self.session.query(
                Material.query_type,
                func.count(Material.query_type)
            ).group_by(Material.query_type).all()
            
            print(f"\nMaterials by query type:")
            for qtype, count in query_types:
                print(f"  {qtype or 'Unknown'}: {count}")
            
            # Band gap statistics
            semiconductors = self.session.query(Material).filter(
                Material.band_gap > 0.1,
                Material.band_gap < 5.0
            ).count()
            
            metals = self.session.query(Material).filter(
                Material.band_gap == 0.0
            ).count()
            
            print(f"\nElectronic properties:")
            print(f"  Semiconductors (0.1 < Eg < 5.0 eV): {semiconductors}")
            print(f"  Metals (Eg = 0.0 eV): {metals}")
            
            # Stable materials
            stable = self.session.query(Material).filter(
                Material.is_stable == True
            ).count()
            
            print(f"  Stable materials: {stable}")
            
            # Sample materials
            print(f"\nSample materials:")
            sample_materials = self.session.query(Material).limit(5).all()
            for i, mat in enumerate(sample_materials, 1):
                print(f"  {i}. {mat.material_id} - {mat.formula_pretty} "
                      f"({mat.crystal_system}, Eg={mat.band_gap})")
            
            # Additional properties count
            total_props = self.session.query(MaterialProperty).count()
            print(f"\nAdditional properties stored: {total_props}")
            
        except Exception as e:
            print(f"❌ Error in verification: {e}")

def main():
    """Main import workflow"""
    print("🚀 Materials Project Data → SQL Database Import")
    print("=" * 60)
    
    importer = DataImporter()
    
    # Setup database connection
    if not importer.setup_database_connection():
        return
    
    # Find data files
    data_dir = "mp_data"
    if not os.path.exists(data_dir):
        print(f"❌ Data directory '{data_dir}' not found!")
        print("Please run the data collection script first.")
        return
    
    # Import CSV files
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    if not csv_files:
        print("❌ No CSV files found!")
        return
    
    print(f"📁 Found {len(csv_files)} CSV files:")
    for csv_file in csv_files:
        print(f"   - {os.path.basename(csv_file)}")
    
    total_imported = 0
    
    # Import each CSV file
    for csv_file in csv_files:
        imported = importer.import_csv_data(csv_file)
        total_imported += imported
    
    # Import JSON additional data
    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    for json_file in json_files:
        if 'comprehensive_dataset' in json_file:  # Import the main dataset JSON
            importer.import_json_additional_data(json_file)
            break
    
    # Verify import
    importer.verify_import()
    
    print(f"\n✅ Import completed! Total materials processed: {total_imported}")
    print("\n🔍 You can now query your database:")
    print("   mysql -h dbase.cs.jhu.edu -u FA25_ycao73 -p")
    print("   USE FA25_ycao73;")
    print("   SELECT * FROM materials LIMIT 10;")

if __name__ == "__main__":
    main()