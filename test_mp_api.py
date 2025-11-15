#!/usr/bin/env python3
# file: test_mp_api.py

try:
    from mp_api.client import MPRester
    print("✅ mp-api imported successfully!")
    
    # Test basic functionality
    api_key = input("Enter API key (or press Enter to skip): ").strip()
    if api_key:
        with MPRester(api_key) as mpr:
            # Try a simple query
            docs = mpr.materials.summary.search(material_ids=["mp-149"], fields=["material_id", "formula_pretty"])
            if docs:
                print(f"✅ API test successful! Found: {docs[0].material_id} - {docs[0].formula_pretty}")
            else:
                print("⚠️ API connected but no data returned")
    else:
        print("✅ Import test passed, skipping API test")
        
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("\nTry running the simple_materials_collector.py script instead")
except Exception as e:
    print(f"❌ API test failed: {e}")