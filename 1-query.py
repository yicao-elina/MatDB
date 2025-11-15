#!/usr/bin/env python3
# file: fixed_comprehensive_mp_query_v2.py

import os
import json
import pandas as pd
from datetime import datetime
from mp_api.client import MPRester
import time

class FixedMPQuerier:
    """Fixed Materials Project data querier with proper Element handling"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.output_dir = "mp_data"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def test_connection_and_show_fields(self):
        """Test API connection and show correct available fields"""
        try:
            with MPRester(self.api_key) as mpr:
                # Test with a simple query
                docs = mpr.materials.summary.search(
                    material_ids=["mp-149"], 
                    fields=["material_id", "formula_pretty"]
                )
                
                if docs:
                    print("✅ API connection successful!")
                    print(f"Test result: {docs[0].material_id} - {docs[0].formula_pretty}")
                    
                    # Show available fields categorized
                    available_fields = mpr.materials.summary.available_fields
                    print(f"\n📋 Available summary fields ({len(available_fields)}):")
                    
                    # Categorize fields for better understanding
                    basic_fields = [f for f in available_fields if f in [
                        'material_id', 'formula_pretty', 'formula_anonymous', 'chemsys',
                        'elements', 'nelements', 'nsites', 'volume', 'density'
                    ]]
                    
                    structure_fields = [f for f in available_fields if f in [
                        'structure', 'symmetry', 'density_atomic'
                    ]]
                    
                    energy_fields = [f for f in available_fields if f in [
                        'energy_per_atom', 'formation_energy_per_atom', 'energy_above_hull',
                        'uncorrected_energy_per_atom', 'is_stable'
                    ]]
                    
                    electronic_fields = [f for f in available_fields if f in [
                        'band_gap', 'cbm', 'vbm', 'efermi', 'is_gap_direct', 'is_metal'
                    ]]
                    
                    print(f"  Basic: {basic_fields}")
                    print(f"  Structure: {structure_fields}")
                    print(f"  Energy: {energy_fields}")
                    print(f"  Electronic: {electronic_fields}")
                    
                    return True
                else:
                    print("❌ API connected but no data returned")
                    return False
                    
        except Exception as e:
            print(f"❌ API connection failed: {e}")
            return False
    
    def _convert_elements_to_strings(self, elements):
        """Convert Element objects to strings"""
        if not elements:
            return []
        
        try:
            # Handle different types of element representations
            string_elements = []
            for element in elements:
                if hasattr(element, 'symbol'):
                    # It's an Element object
                    string_elements.append(element.symbol)
                elif hasattr(element, '__str__'):
                    # It's something that can be converted to string
                    string_elements.append(str(element))
                else:
                    # Fallback
                    string_elements.append(str(element))
            return string_elements
        except Exception as e:
            print(f"Warning: Could not convert elements {elements}: {e}")
            return [str(elem) for elem in elements]
    
    def _safe_json_serialize(self, obj):
        """Safely serialize objects to JSON, handling pymatgen objects"""
        if obj is None:
            return None
        
        try:
            # Try direct serialization first
            json.dumps(obj)
            return obj
        except TypeError:
            # Handle special cases
            if hasattr(obj, 'as_dict'):
                # Pymatgen objects with as_dict method
                return obj.as_dict()
            elif hasattr(obj, '__dict__'):
                # Objects with __dict__
                return obj.__dict__
            else:
                # Convert to string as fallback
                return str(obj)
    
    def query_specific_materials(self, material_ids):
        """Query specific materials by their IDs using correct field names"""
        print(f"\n🔍 Querying {len(material_ids)} specific materials...")
        
        try:
            with MPRester(self.api_key) as mpr:
                # Use only valid fields
                fields = [
                    "material_id", "formula_pretty", "formula_anonymous",
                    "symmetry", "volume", "density", "nsites", "elements", 
                    "structure", "band_gap", "formation_energy_per_atom", 
                    "energy_above_hull", "is_stable", "theoretical", 
                    "energy_per_atom", "chemsys", "cbm", "vbm", "is_gap_direct"
                ]
                
                docs = mpr.materials.summary.search(
                    material_ids=material_ids,
                    fields=fields
                )
                
                print(f"✅ Retrieved {len(docs)} materials")
                
                # Convert to dictionaries
                materials = []
                for doc in docs:
                    material = self._doc_to_dict(doc)
                    material["query_type"] = "specific_ids"
                    materials.append(material)
                
                return materials
                
        except Exception as e:
            print(f"❌ Error querying specific materials: {e}")
            return []
    
    def query_by_elements(self, elements, limit=50):
        """Query materials containing specific elements"""
        print(f"\n🔍 Querying materials containing {elements}...")
        
        try:
            with MPRester(self.api_key) as mpr:
                fields = [
                    "material_id", "formula_pretty", "symmetry",
                    "volume", "density", "nsites", "elements", "band_gap",
                    "formation_energy_per_atom", "energy_above_hull", "is_stable"
                ]
                
                docs = mpr.materials.summary.search(
                    elements=elements,
                    fields=fields
                )
                
                # Limit results
                if len(docs) > limit:
                    docs = docs[:limit]
                
                print(f"✅ Retrieved {len(docs)} materials")
                
                materials = []
                for doc in docs:
                    material = self._doc_to_dict(doc)
                    material["query_type"] = f"elements_{'-'.join(elements)}"
                    materials.append(material)
                
                return materials
                
        except Exception as e:
            print(f"❌ Error querying by elements: {e}")
            return []
    
    def query_semiconductors(self, band_gap_range=(0.5, 4.0), limit=100):
        """Query semiconductor materials"""
        print(f"\n🔍 Querying semiconductors with band gap {band_gap_range[0]}-{band_gap_range[1]} eV...")
        
        try:
            with MPRester(self.api_key) as mpr:
                fields = [
                    "material_id", "formula_pretty", "symmetry",
                    "elements", "band_gap", "formation_energy_per_atom",
                    "energy_above_hull", "is_stable", "theoretical",
                    "is_gap_direct", "cbm", "vbm"
                ]
                
                docs = mpr.materials.summary.search(
                    band_gap=band_gap_range,
                    fields=fields
                )
                
                # Limit results
                if len(docs) > limit:
                    docs = docs[:limit]
                
                print(f"✅ Retrieved {len(docs)} semiconductor materials")
                
                materials = []
                for doc in docs:
                    material = self._doc_to_dict(doc)
                    material["query_type"] = "semiconductors"
                    materials.append(material)
                
                return materials
                
        except Exception as e:
            print(f"❌ Error querying semiconductors: {e}")
            return []
    
    def query_stable_materials(self, energy_above_hull_max=0.1, limit=100):
        """Query thermodynamically stable materials"""
        print(f"\n🔍 Querying stable materials (E_hull < {energy_above_hull_max} eV)...")
        
        try:
            with MPRester(self.api_key) as mpr:
                fields = [
                    "material_id", "formula_pretty", "symmetry",
                    "elements", "formation_energy_per_atom", "energy_above_hull",
                    "is_stable", "band_gap"
                ]
                
                docs = mpr.materials.summary.search(
                    energy_above_hull=(0, energy_above_hull_max),
                    fields=fields
                )
                
                # Limit results
                if len(docs) > limit:
                    docs = docs[:limit]
                
                print(f"✅ Retrieved {len(docs)} stable materials")
                
                materials = []
                for doc in docs:
                    material = self._doc_to_dict(doc)
                    material["query_type"] = "stable_materials"
                    materials.append(material)
                
                return materials
                
        except Exception as e:
            print(f"❌ Error querying stable materials: {e}")
            return []
    
    def get_additional_properties_safely(self, material_ids, max_materials=5):
        """Get additional properties with proper limiting"""
        print(f"\n🔍 Getting additional properties for {min(len(material_ids), max_materials)} materials...")
        
        # Strictly limit to prevent over-fetching
        limited_ids = material_ids[:max_materials]
        additional_data = {}
        
        try:
            with MPRester(self.api_key) as mpr:
                # Get electronic structure data with explicit material_ids
                try:
                    print(f"  Fetching electronic structure for: {limited_ids}")
                    electronic_docs = mpr.materials.electronic_structure.search(
                        material_ids=limited_ids,
                        fields=["material_id", "band_gap", "cbm", "vbm", "is_gap_direct"]
                    )
                    
                    for doc in electronic_docs:
                        if doc.material_id not in additional_data:
                            additional_data[doc.material_id] = {}
                        additional_data[doc.material_id]["electronic_structure"] = {
                            "cbm": getattr(doc, 'cbm', None),
                            "vbm": getattr(doc, 'vbm', None),
                            "is_gap_direct": getattr(doc, 'is_gap_direct', None)
                        }
                    
                    print(f"  ✅ Got electronic structure for {len(electronic_docs)} materials")
                except Exception as e:
                    print(f"  ⚠️ Electronic structure data error: {e}")
                
                return additional_data
                
        except Exception as e:
            print(f"❌ Error getting additional properties: {e}")
            return {}
    
    def _doc_to_dict(self, doc):
        """Convert MPRester document to dictionary with proper Element handling"""
        # Handle elements properly - convert Element objects to strings
        elements_list = getattr(doc, 'elements', [])
        elements_strings = self._convert_elements_to_strings(elements_list)
        
        material = {
            'material_id': getattr(doc, 'material_id', None),
            'formula_pretty': getattr(doc, 'formula_pretty', None),
            'formula_anonymous': getattr(doc, 'formula_anonymous', None),
            'chemsys': getattr(doc, 'chemsys', None),
            'volume': getattr(doc, 'volume', None),
            'density': getattr(doc, 'density', None),
            'nsites': getattr(doc, 'nsites', None),
            'elements': elements_strings,  # Now safe for JSON serialization
            'band_gap': getattr(doc, 'band_gap', None),
            'formation_energy_per_atom': getattr(doc, 'formation_energy_per_atom', None),
            'energy_above_hull': getattr(doc, 'energy_above_hull', None),
            'energy_per_atom': getattr(doc, 'energy_per_atom', None),
            'is_stable': getattr(doc, 'is_stable', None),
            'theoretical': getattr(doc, 'theoretical', None),
            'cbm': getattr(doc, 'cbm', None),
            'vbm': getattr(doc, 'vbm', None),
            'is_gap_direct': getattr(doc, 'is_gap_direct', None),
            'collected_at': datetime.now().isoformat()
        }
        
        # Handle symmetry (replaces crystal_system and space_group)
        if hasattr(doc, 'symmetry') and doc.symmetry:
            try:
                symmetry = doc.symmetry
                material['crystal_system'] = getattr(symmetry, 'crystal_system', None)
                material['space_group'] = str(getattr(symmetry, 'space_group', None)) if hasattr(symmetry, 'space_group') else None
                material['point_group'] = getattr(symmetry, 'point_group', None)
            except Exception as e:
                print(f"Warning: Could not extract symmetry info: {e}")
                material['crystal_system'] = None
                material['space_group'] = None
                material['point_group'] = None
        
        # Handle structure - convert to serializable format
        if hasattr(doc, 'structure') and doc.structure:
            try:
                # Don't include full structure in main data (too large)
                # Just store basic structure info
                structure = doc.structure
                material['structure_info'] = {
                    'lattice_volume': float(structure.volume) if hasattr(structure, 'volume') else None,
                    'num_sites': len(structure.sites) if hasattr(structure, 'sites') else None,
                    'formula': str(structure.composition.reduced_formula) if hasattr(structure, 'composition') else None
                }
            except Exception as e:
                print(f"Warning: Could not extract structure info: {e}")
                material['structure_info'] = None
        
        return material
    
    def save_data(self, materials, filename_prefix):
        """Save materials data with proper serialization handling"""
        if not materials:
            print("No materials to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{filename_prefix}_{timestamp}"
        
        # Save JSON with safe serialization
        json_file = os.path.join(self.output_dir, f"{base_filename}.json")
        try:
            # Use custom serializer for JSON
            with open(json_file, 'w') as f:
                json.dump(materials, f, indent=2, default=self._safe_json_serialize)
            print(f"   ✅ JSON: {json_file}")
        except Exception as e:
            print(f"   ❌ JSON save failed: {e}")
        
        # Save CSV (flattened)
        csv_file = os.path.join(self.output_dir, f"{base_filename}.csv")
        try:
            csv_data = []
            for material in materials:
                row = material.copy()
                
                # Handle elements - now they're already strings
                if 'elements' in row and row['elements']:
                    row['elements'] = ','.join(row['elements'])  # Convert list to comma-separated string
                
                # Handle structure_info
                if 'structure_info' in row and row['structure_info']:
                    structure_info = row['structure_info']
                    row['structure_volume'] = structure_info.get('lattice_volume')
                    row['structure_num_sites'] = structure_info.get('num_sites')
                    row['structure_formula'] = structure_info.get('formula')
                    row.pop('structure_info')  # Remove the nested dict
                
                # Remove any remaining complex objects
                for key, value in list(row.items()):
                    if isinstance(value, (dict, list)) and key != 'elements':
                        row.pop(key)
                
                csv_data.append(row)
            
            df = pd.DataFrame(csv_data)
            df.to_csv(csv_file, index=False)
            print(f"   ✅ CSV: {csv_file}")
            
        except Exception as e:
            print(f"   ❌ CSV save failed: {e}")
        
        print(f"💾 Saved {len(materials)} materials")
        return json_file, csv_file

def main():
    """Main execution function with fixed Element handling"""
    
    print("🚀 Fixed Comprehensive Materials Project Data Query (v2)")
    print("=" * 70)
    
    # Get API key
    api_key = os.getenv('MP_API_KEY')
    if not api_key:
        api_key = input("Enter your Materials Project API key: ")
    
    querier = FixedMPQuerier(api_key)
    
    # Test connection and show fields
    if not querier.test_connection_and_show_fields():
        print("Cannot proceed without valid API connection")
        return
    
    all_materials = []
    
    try:
        # Query 1: Specific important materials
        print(f"\n{'='*70}")
        print("QUERY 1: Specific Important Materials")
        print('='*70)
        
        important_materials = [
            "mp-149",   # Si
            "mp-13",    # Al  
            "mp-22526", # NaCl
            "mp-1143",  # TiO2
            "mp-390",   # Al2O3
            "mp-2534",  # GaAs
            "mp-804",   # ZnS
            "mp-1265",  # GaN
            "mp-571",   # MgO
            "mp-1000"   # Fe2O3
        ]
        
        specific_materials = querier.query_specific_materials(important_materials)
        all_materials.extend(specific_materials)
        
        if specific_materials:
            querier.save_data(specific_materials, "specific_materials")
            
            # Show sample of what we got
            print(f"\n📋 Sample of specific materials:")
            for i, mat in enumerate(specific_materials[:5]):
                elements = ', '.join(mat['elements']) if mat['elements'] else 'N/A'
                print(f"   {i+1}. {mat['material_id']} - {mat['formula_pretty']} "
                      f"(Elements: {elements})")
        
        # Query 2: Silicon-containing materials
        print(f"\n{'='*70}")
        print("QUERY 2: Silicon-containing Materials")
        print('='*70)
        
        si_materials = querier.query_by_elements(["Si"], limit=15)
        all_materials.extend(si_materials)
        
        if si_materials:
            querier.save_data(si_materials, "silicon_materials")
        
        # Query 3: Semiconductors
        print(f"\n{'='*70}")
        print("QUERY 3: Semiconductor Materials")
        print('='*70)
        
        semiconductors = querier.query_semiconductors(band_gap_range=(1.0, 3.0), limit=20)
        all_materials.extend(semiconductors)
        
        if semiconductors:
            querier.save_data(semiconductors, "semiconductors")
        
        # Remove duplicates
        unique_materials = {}
        for material in all_materials:
            mat_id = material.get('material_id')
            if mat_id and mat_id not in unique_materials:
                unique_materials[mat_id] = material
        
        final_materials = list(unique_materials.values())
        
        # Save final combined dataset
        if final_materials:
            print(f"\n{'='*70}")
            print("FINAL RESULTS")
            print('='*70)
            
            querier.save_data(final_materials, "comprehensive_dataset")
            
            # Summary
            print(f"\n📊 SUMMARY:")
            print(f"   Total unique materials: {len(final_materials)}")
            
            # Show sample materials
            print(f"\n📋 Sample materials collected:")
            for i, material in enumerate(final_materials[:10]):
                crystal_sys = material.get('crystal_system', 'Unknown')
                band_gap = material.get('band_gap', 'N/A')
                elements = ', '.join(material.get('elements', [])) if material.get('elements') else 'N/A'
                print(f"   {i+1:2d}. {material['material_id']} - {material['formula_pretty']} "
                      f"({crystal_sys}, Eg={band_gap}, Elements: {elements})")
            
            if len(final_materials) > 10:
                print(f"   ... and {len(final_materials) - 10} more materials")
            
            print(f"\n✅ Data collection completed successfully!")
            print(f"📁 Check the '{querier.output_dir}' directory for all output files")
        else:
            print("❌ No materials were collected")
        
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()