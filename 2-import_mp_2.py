#!/usr/bin/env python3
# file: modern_import_mp_data.py

import os
import json
import pandas as pd
from datetime import datetime
from typing import Optional
import glob
import numpy as np
# SQLAlchemy 2.0 imports
from sqlalchemy import create_engine, String, Float, Integer, Boolean, DateTime, Text, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import select

# Database configuration
DB_CONFIG = {
    'host': 'dbase.cs.jhu.edu',
    'user': 'FA25_ycao73',
    'password': 'Mel62w66gA',
    'database': 'FA25_ycao73_db',
    'charset': 'utf8mb4'
}

# Modern SQLAlchemy 2.0 Base class
class Base(DeclarativeBase):
    pass

# Modern SQLAlchemy 2.0 Material model
class Material(Base):
    __tablename__ = 'materials'
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Basic identifiers
    material_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    formula_pretty: Mapped[str] = mapped_column(String(200), nullable=False)
    formula_anonymous: Mapped[Optional[str]] = mapped_column(String(200))
    chemsys: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Structure information
    crystal_system: Mapped[Optional[str]] = mapped_column(String(50))
    space_group: Mapped[Optional[str]] = mapped_column(String(100))
    point_group: Mapped[Optional[str]] = mapped_column(String(50))
    volume: Mapped[Optional[float]] = mapped_column(Float)
    density: Mapped[Optional[float]] = mapped_column(Float)
    nsites: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Elements (stored as comma-separated string)
    elements: Mapped[Optional[str]] = mapped_column(Text)
    nelements: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Energy properties
    energy_per_atom: Mapped[Optional[float]] = mapped_column(Float)
    formation_energy_per_atom: Mapped[Optional[float]] = mapped_column(Float)
    energy_above_hull: Mapped[Optional[float]] = mapped_column(Float)
    is_stable: Mapped[Optional[bool]] = mapped_column(Boolean)
    theoretical: Mapped[Optional[bool]] = mapped_column(Boolean)
    
    # Electronic properties
    band_gap: Mapped[Optional[float]] = mapped_column(Float)
    cbm: Mapped[Optional[float]] = mapped_column(Float)
    vbm: Mapped[Optional[float]] = mapped_column(Float)
    is_gap_direct: Mapped[Optional[bool]] = mapped_column(Boolean)
    
    # Structure details
    structure_volume: Mapped[Optional[float]] = mapped_column(Float)
    structure_num_sites: Mapped[Optional[int]] = mapped_column(Integer)
    structure_formula: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Metadata
    query_type: Mapped[Optional[str]] = mapped_column(String(100))
    collected_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    
    def __repr__(self) -> str:
        return f"Material(id={self.material_id!r}, formula={self.formula_pretty!r}, crystal_system={self.crystal_system!r})"

class MaterialProperty(Base):
    __tablename__ = 'material_properties'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    material_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    property_name: Mapped[str] = mapped_column(String(100), nullable=False)
    property_value: Mapped[Optional[str]] = mapped_column(Text)
    source_type: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_material_property', 'material_id', 'property_name'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
    )
    
    def __repr__(self) -> str:
        return f"MaterialProperty(material_id={self.material_id!r}, property={self.property_name!r})"

class ModernDataImporter:
    def __init__(self):
        self.engine = None
    
    def setup_database_connection(self):
        """Setup database connection using SQLAlchemy 2.0"""
        
        connection_string = (
            f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['host']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"
        )
        
        print(f"🔗 Connecting to database: {DB_CONFIG['host']}/{DB_CONFIG['database']}")
        
        try:
            # Create engine with SQLAlchemy 2.0 configuration
            self.engine = create_engine(
                connection_string,
                echo=False,  # Set to True for SQL debugging
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            # Test connection using modern syntax
            with Session(self.engine) as session:
                # Simple test query
                result = session.execute(select(1))
                test_value = result.scalar()
                print(f"✅ Database connection successful! Test result: {test_value}")
            
            # Create tables
            print("🏗️  Creating database tables...")
            Base.metadata.create_all(self.engine)
            print("✅ Tables created successfully!")
            
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print(f"   Connection details: {DB_CONFIG['user']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}")
            return False
    
    def test_database_access(self):
        """Test database operations using SQLAlchemy 2.0 syntax"""
        print("\n🔍 Testing database access...")
        
        try:
            with Session(self.engine) as session:
                # Check current database
                # Fix 1: Use text() for raw SQL
                from sqlalchemy import text
                result = session.execute(text("SELECT DATABASE()"))
                current_db = result.scalar()
                print(f"   Current database: {current_db}")
                
                # Check existing materials count
                # existing_count = session.query(Material).count()
                from sqlalchemy import func
                stmt = select(func.count(Material.id))
                existing_count = session.scalar(stmt)
                print(f"   Existing materials: {existing_count}")
                
                # Show sample if any exist
                if existing_count > 0:
                    sample_materials = session.query(Material).limit(3).all()
                    print(f"   Sample existing materials:")
                    for mat in sample_materials:
                        print(f"     - {mat}")
                
                return True
                
        except Exception as e:
            print(f"   ❌ Database test failed: {e}")
            return False
    
    def import_csv_data(self, csv_file):
        """Import materials data using SQLAlchemy 2.0 Session"""
        print(f"\n📂 Importing data from: {os.path.basename(csv_file)}")
        
        try:
            # Read and prepare CSV data
            df = pd.read_csv(csv_file)
            print(f"   📊 Found {len(df)} materials in CSV")
            
            # Clean data
            df = df.replace({pd.NA: None, pd.NaT: None})  # Handle pandas NA/NaT
            df = df.where(pd.notnull(df), None)
            df = df.replace([np.inf, -np.inf, np.nan], None)    
            imported_count = 0
            updated_count = 0
            error_count = 0
            
            # Use modern Session context manager
            with Session(self.engine) as session:
                for index, row in df.iterrows():
                    try:
                        material_id = row.get('material_id')
                        if not material_id:
                            error_count += 1
                            print(f"   ⚠️  Skipping row {index}: missing material_id")
                            continue
                        
                        # Check if material exists using modern query syntax
                        stmt = select(Material).where(Material.material_id == material_id)
                        existing = session.scalars(stmt).first()
                        
                        if existing:
                            material = existing
                            updated_count += 1
                            print(f"   🔄 Updating: {material_id}")
                        else:
                            material = Material()
                            imported_count += 1
                            print(f"   ➕ Adding: {material_id}")
                        
                        # Map CSV data to Material object
                        self._populate_material_from_row(material, row)
                        
                        if not existing:
                            session.add(material)
                        
                        # Commit in batches
                        if (imported_count + updated_count) % 25 == 0:
                            session.commit()
                            print(f"   ⏳ Progress: {imported_count + updated_count} materials processed...")
                    
                    except Exception as e:
                        error_count += 1
                        print(f"   ❌ Error processing row {index}: {str(e)[:100]}...")
                        session.rollback()
                        continue
                
                # Final commit
                try:
                    session.commit()
                    print(f"   ✅ Import completed:")
                    print(f"      📈 New materials imported: {imported_count}")
                    print(f"      🔄 Existing materials updated: {updated_count}")
                    print(f"      ❌ Errors: {error_count}")
                except Exception as e:
                    print(f"   ❌ Final commit failed: {e}")
                    session.rollback()
                    return 0
            
            return imported_count + updated_count
            
        except Exception as e:
            print(f"   ❌ Error importing CSV: {e}")
            return 0
    
    def _populate_material_from_row(self, material: Material, row: pd.Series):
        """Populate Material object from CSV row data"""
        
        # Basic identifiers
        material.material_id = row.get('material_id')
        material.formula_pretty = row.get('formula_pretty')
        material.formula_anonymous = row.get('formula_anonymous')
        material.chemsys = row.get('chemsys')
        
        # Structure information
        material.crystal_system = row.get('crystal_system')
        material.space_group = row.get('space_group')
        material.point_group = row.get('point_group')
        material.volume = self._safe_float(row.get('volume'))
        material.density = self._safe_float(row.get('density'))
        material.nsites = self._safe_int(row.get('nsites'))
        material.elements = row.get('elements')
        
        # Count elements
        if material.elements:
            try:
                material.nelements = len(material.elements.split(','))
            except:
                material.nelements = None
        
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
    
    def _safe_float(self, value) -> Optional[float]:
        """Safely convert to float"""
        if value is None or value == '' or pd.isna(value):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value) -> Optional[int]:
        """Safely convert to int"""
        if value is None or value == '' or pd.isna(value):
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _safe_bool(self, value) -> Optional[bool]:
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
    
    def _safe_datetime(self, value) -> Optional[datetime]:
        """Safely convert to datetime"""
        if value is None or value == '' or pd.isna(value):
            return None
        try:
            return pd.to_datetime(value).to_pydatetime()
        except:
            return None
    
    # def verify_import(self):
    #     """Verify imported data using modern SQLAlchemy syntax"""
    #     print(f"\n📊 VERIFICATION REPORT")
    #     print("=" * 60)
        
    #     try:
    #         with Session(self.engine) as session:
    #             # Total materials count
    #             total_count = session.query(Material).count()
    #             print(f"📈 Total materials in database: {total_count}")
                
    #             if total_count == 0:
    #                 print("⚠️  No materials found in database!")
    #                 return
                
    #             # Sample materials
    #             print(f"\n🔬 Sample materials:")
    #             sample_stmt = select(Material).limit(5)
    #             sample_materials = session.scalars(sample_stmt).all()
                
    #             for i, mat in enumerate(sample_materials, 1):
    #                 print(f"   {i}. {mat}")
                
    #             # Statistics by crystal system
    #             print(f"\n🔍 Materials by crystal system:")
    #             crystal_systems = session.query(
    #                 Material.crystal_system,
    #                 session.query(Material).filter(
    #                     Material.crystal_system == Material.crystal_system
    #                 ).count().label('count')
    #             ).group_by(Material.crystal_system).limit(5).all()
                
    #             # Alternative approach for counting
    #             from sqlalchemy import func
    #             crystal_counts = session.query(
    #                 Material.crystal_system,
    #                 func.count(Material.crystal_system)
    #             ).group_by(Material.crystal_system).limit(5).all()
                
    #             for system, count in crystal_counts:
    #                 print(f"   {system or 'Unknown'}: {count}")
                
    #             # Query type distribution
    #             print(f"\n📋 Materials by query type:")
    #             query_counts = session.query(
    #                 Material.query_type,
    #                 func.count(Material.query_type)
    #             ).group_by(Material.query_type).all()
                
    #             for qtype, count in query_counts:
    #                 print(f"   {qtype or 'Unknown'}: {count}")
                
    #             # Electronic properties summary
    #             semiconductor_count = session.query(Material).filter(
    #                 Material.band_gap > 0.1,
    #                 Material.band_gap < 5.0
    #             ).count()
                
    #             metal_count = session.query(Material).filter(
    #                 Material.band_gap == 0.0
    #             ).count()
                
    #             stable_count = session.query(Material).filter(
    #                 Material.is_stable == True
    #             ).count()
                
    #             print(f"\n⚡ Electronic properties:")
    #             print(f"   🔌 Semiconductors (0.1 < Eg < 5.0 eV): {semiconductor_count}")
    #             print(f"   🔗 Metals (Eg = 0.0 eV): {metal_count}")
    #             print(f"   ⚖️  Stable materials: {stable_count}")
                
    #     except Exception as e:
    #         print(f"❌ Error in verification: {e}")
    #         import traceback
    #         traceback.print_exc()

    def verify_import(self):
        """Verify imported data using modern SQLAlchemy syntax"""
        print(f"\n📊 VERIFICATION REPORT")
        print("=" * 60)
        
        try:
            with Session(self.engine) as session:
                # Total materials count
                from sqlalchemy import func 
                stmt = select(func.count(Material.id))
                total_count = session.scalar(stmt)
                print(f"📈 Total materials in database: {total_count}")
                
                if total_count == 0:
                    print("⚠️  No materials found in database!")
                    return
                
                # Sample materials
                print(f"\n🔬 Sample materials:")
                stmt = select(Material).limit(5)
                sample_materials = session.scalars(stmt).all()
                
                for i, mat in enumerate(sample_materials, 1):
                    print(f"   {i}. {mat}")
                
                # Statistics by crystal system - FIXED
                print(f"\n🔍 Materials by crystal system:")
                stmt = select(
                    Material.crystal_system,
                    func.count(Material.crystal_system).label('count')
                ).group_by(Material.crystal_system).order_by(func.count(Material.crystal_system).desc())
                
                crystal_counts = session.execute(stmt).all()
                
                for system, count in crystal_counts:
                    print(f"   {system or 'Unknown'}: {count}")
                
                # Query type distribution
                print(f"\n📋 Materials by query type:")
                stmt = select(
                    Material.query_type,
                    func.count(Material.query_type).label('count')
                ).group_by(Material.query_type)
                
                query_counts = session.execute(stmt).all()
                
                for qtype, count in query_counts:
                    print(f"   {qtype or 'Unknown'}: {count}")
                
                # Electronic properties summary
                print(f"\n⚡ Electronic properties:")
                
                # Semiconductors
                stmt = select(func.count(Material.id)).where(
                    Material.band_gap > 0.1,
                    Material.band_gap < 5.0
                )
                semiconductor_count = session.scalar(stmt)
                
                # Metals (zero band gap)
                stmt = select(func.count(Material.id)).where(
                    Material.band_gap == 0.0
                )
                metal_count = session.scalar(stmt)
                
                # Insulators (large band gap)
                stmt = select(func.count(Material.id)).where(
                    Material.band_gap >= 5.0
                )
                insulator_count = session.scalar(stmt)
                
                # Stable materials
                stmt = select(func.count(Material.id)).where(
                    Material.is_stable == True
                )
                stable_count = session.scalar(stmt)
                
                print(f"   🔌 Semiconductors (0.1 < Eg < 5.0 eV): {semiconductor_count}")
                print(f"   🔗 Metals (Eg = 0.0 eV): {metal_count}")
                print(f"   🧱 Insulators (Eg >= 5.0 eV): {insulator_count}")
                print(f"   ⚖️  Stable materials: {stable_count}")
                
                # Band gap statistics
                print(f"\n📊 Band gap statistics:")
                stmt = select(
                    func.min(Material.band_gap).label('min_bg'),
                    func.max(Material.band_gap).label('max_bg'),
                    func.avg(Material.band_gap).label('avg_bg')
                ).where(Material.band_gap.is_not(None))
                
                bg_stats = session.execute(stmt).first()
                if bg_stats:
                    print(f"   Min band gap: {bg_stats.min_bg:.3f} eV")
                    print(f"   Max band gap: {bg_stats.max_bg:.3f} eV")
                    print(f"   Avg band gap: {bg_stats.avg_bg:.3f} eV")
                
                # Formation energy statistics
                print(f"\n🔋 Formation energy statistics:")
                stmt = select(
                    func.min(Material.formation_energy_per_atom).label('min_fe'),
                    func.max(Material.formation_energy_per_atom).label('max_fe'),
                    func.avg(Material.formation_energy_per_atom).label('avg_fe')
                ).where(Material.formation_energy_per_atom.is_not(None))
                
                fe_stats = session.execute(stmt).first()
                if fe_stats:
                    print(f"   Min formation energy: {fe_stats.min_fe:.3f} eV/atom")
                    print(f"   Max formation energy: {fe_stats.max_fe:.3f} eV/atom")
                    print(f"   Avg formation energy: {fe_stats.avg_fe:.3f} eV/atom")
                
                # Element distribution
                print(f"\n🧪 Element distribution:")
                stmt = select(
                    Material.nelements,
                    func.count(Material.nelements).label('count')
                ).where(Material.nelements.is_not(None)).group_by(Material.nelements).order_by(Material.nelements)
                
                element_counts = session.execute(stmt).all()
                
                for n_elements, count in element_counts:
                    element_type = {
                        1: "Elemental",
                        2: "Binary", 
                        3: "Ternary",
                        4: "Quaternary"
                    }.get(n_elements, f"{n_elements}-component")
                    
                    print(f"   {element_type} ({n_elements} elements): {count}")
                
                # Most common formulas
                print(f"\n🧮 Most common formulas:")
                stmt = select(
                    Material.formula_pretty,
                    func.count(Material.formula_pretty).label('count')
                ).group_by(Material.formula_pretty).order_by(func.count(Material.formula_pretty).desc()).limit(5)
                
                formula_counts = session.execute(stmt).all()
                
                for formula, count in formula_counts:
                    print(f"   {formula}: {count}")
                    
        except Exception as e:
            print(f"❌ Error in verification: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main import workflow using SQLAlchemy 2.0"""
    print("🚀 Materials Project Data → SQL Database Import (SQLAlchemy 2.0)")
    print("=" * 70)
    
    importer = ModernDataImporter()
    
    # Setup database connection
    if not importer.setup_database_connection():
        print("\n💡 Troubleshooting tips:")
        print("1. Ensure you're connected to JHU network/VPN")
        print("2. Verify database credentials are correct")
        print("3. Check if pymysql is installed: pip install pymysql")
        print("4. Test manual connection: mysql -h dbase.cs.jhu.edu -u FA25_ycao73 -p")
        return
    
    # Test database access
    if not importer.test_database_access():
        print("❌ Database access test failed")
        return
    
    # Find and import CSV files
    data_dir = "mp_data"
    if not os.path.exists(data_dir):
        print(f"❌ Data directory '{data_dir}' not found!")
        print("Please run the data collection script first.")
        return
    
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    if not csv_files:
        print("❌ No CSV files found in mp_data directory!")
        return
    
    print(f"\n📁 Found {len(csv_files)} CSV files:")
    for csv_file in csv_files:
        print(f"   📄 {os.path.basename(csv_file)}")
    
    # Import comprehensive dataset first, then others
    comprehensive_files = [f for f in csv_files if 'comprehensive_dataset' in f]
    other_files = [f for f in csv_files if 'comprehensive_dataset' not in f]
    
    total_imported = 0
    
    # Import files
    all_files = comprehensive_files + other_files
    for i, csv_file in enumerate(all_files, 1):
        print(f"\n📥 Processing file {i}/{len(all_files)}")
        imported = importer.import_csv_data(csv_file)
        total_imported += imported
    
    # Verify the import
    importer.verify_import()
    
    # Final summary
    print(f"\n🎉 Import completed!")
    print(f"📊 Total materials processed: {total_imported}")
    
    if total_imported > 0:
        print(f"\n🔍 Next steps - Query your database:")
        print(f"   mysql -h dbase.cs.jhu.edu -u FA25_ycao73 -p")
        print(f"   USE FA25_ycao73_db;")
        print(f"   SELECT COUNT(*) FROM materials;")
        print(f"   SELECT material_id, formula_pretty, crystal_system, band_gap FROM materials LIMIT 10;")
        print(f"\n📈 Example queries:")
        print(f"   -- Find semiconductors")
        print(f"   SELECT * FROM materials WHERE band_gap BETWEEN 1.0 AND 3.0;")
        print(f"   -- Group by crystal system")
        print(f"   SELECT crystal_system, COUNT(*) FROM materials GROUP BY crystal_system;")

if __name__ == "__main__":
    main()