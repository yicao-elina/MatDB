import sys
import json
from google import genai

API_KEY = "AIzaSyDULwfDBOZvXeUSMS1Snyg4RG9KSxj1WMs"

client = genai.Client(api_key=API_KEY)

def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except Exception as e:
        print(f"Error: invalid JSON input: {e}")
        sys.exit(1)

    question = (data.get("question") or "").strip()
    if not question:
        print("Error: empty question")
        sys.exit(1)

    prompt = f"""
    You are an expert SQL generator for MySQL.

    Database schema:
    CREATE TABLE materials (
    -- Primary Key
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    material_id VARCHAR(50) UNIQUE NOT NULL, 
    formula_pretty VARCHAR(200) NOT NULL,
    formula_anonymous VARCHAR(200),
    chemsys VARCHAR(200), 
    crystal_system VARCHAR(50),
    space_group VARCHAR(100),
    point_group VARCHAR(50), 
    volume FLOAT,
    density FLOAT,
    nsites INT,
    elements TEXT,
    nelements INT,
    energy_per_atom FLOAT,
    formation_energy_per_atom FLOAT,
    energy_above_hull FLOAT, 
    is_stable BOOLEAN,
    theoretical BOOLEAN,
    band_gap FLOAT, 
    cbm FLOAT,
    vbm FLOAT,
    is_gap_direct BOOLEAN, 
    structure_volume FLOAT,   
    structure_num_sites INT, 
    structure_formula VARCHAR(200),        
    query_type VARCHAR(100), 
    collected_at DATETIME, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_material_id (material_id),
    INDEX idx_formula (formula_pretty),
    INDEX idx_crystal_system (crystal_system),
    INDEX idx_band_gap (band_gap),
    INDEX idx_stable (is_stable),
    INDEX idx_elements (elements),
    INDEX idx_query_type (query_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO materials VALUES (1,'mp-149','Si','A','Si','Cubic','NULL','m-3m',40.33,2.313,2,'Si',1,-8.774,0.0,0.0,'1','0',0.611,6.227,5.617,'0',40.33,2,'Si','specific_ids','2025-11-15 11:56:43','2025-11-15 18:32:23','2025-11-20 01:42:36',)
INSERT INTO materials VALUES (2,'mp-13','Fe','A','Fe','Cubic','NULL','mmm',23.468,7.903,2,'Fe',1,-8.47,0.0,0.0,'1','0',0.0,'NULL','NULL','0',23.468,2,'Fe','specific_ids','2025-11-15 11:56:43','2025-11-15 18:32:23','2025-11-20 01:42:36',)
INSERT INTO materials VALUES (3,'mp-390','TiO2','AB2','O-Ti','Tetragonal','NULL','4/mmm',68.784,3.856,6,'O,Ti',2,-9.439,-3.508,0.0,'1','0',2.059,3.953,1.894,'0',68.784,6,'TiO2','specific_ids','2025-11-15 11:56:43','2025-11-15 18:32:23','2025-11-20 01:42:36',)
INSERT INTO materials VALUES (4,'mp-2534','GaAs','AB','As-Ga','Cubic','NULL','-43m',47.532,5.053,2,'As,Ga',2,-13.521,-0.446,0.0,'1','0',0.186,2.857,2.67,'1',47.532,2,'GaAs','specific_ids','2025-11-15 11:56:43','2025-11-15 18:32:23','2025-11-20 01:42:36',)
INSERT INTO materials VALUES (5,'mp-22526','LiCoO2','ABC2','Co-Li-O','Trigonal','NULL','-3m',31.734,5.121,4,'Co,Li,O',3,-6.48,-1.746,0.0,'1','0',0.662,4.489,3.826,'0',31.734,4,'LiCoO2','specific_ids','2025-11-15 11:56:43','2025-11-15 18:32:23','2025-11-20 01:42:37',)
INSERT INTO materials VALUES (6,'mp-1143','Al2O3','A2B3','Al-O','Trigonal','NULL','-3m',87.42,3.873,10,'Al,O',2,-7.894,-3.427,0.0,'1','0',5.854,11.664,5.81,'1',87.42,10,'Al2O3','specific_ids','2025-11-15 11:56:43','2025-11-15 18:32:23','2025-11-20 01:42:37',)
INSERT INTO materials VALUES (7,'mp-804','GaN','AB','Ga-N','Hexagonal','NULL','6mm',45.728,6.081,4,'Ga,N',2,-10.956,-0.67,0.0,'1','0',1.726,5.12,3.394,'1',45.728,4,'GaN','specific_ids','2025-11-15 11:56:43','2025-11-15 18:32:23','2025-11-20 01:42:37',)
INSERT INTO materials VALUES (8,'mp-1265','MgO','AB','Mg-O','Cubic','NULL','m-3m',18.443,3.629,2,'Mg,O',2,-6.328,-3.038,0.0,'1','0',4.429,7.013,2.584,'1',18.443,2,'MgO','specific_ids','2025-11-15 11:56:43','2025-11-15 18:32:23','2025-11-20 01:42:37',)
INSERT INTO materials VALUES (9,'mp-571','TiNi','AB','Ni-Ti','Cubic','NULL','m-3m',26.679,6.632,2,'Ni,Ti',2,-7.185,-0.347,0.048,'0','0',0.0,'NULL','NULL','0',26.679,2,'TiNi','specific_ids','2025-11-15 11:56:43','2025-11-15 18:32:23','2025-11-20 01:42:37',)
INSERT INTO materials VALUES (10,'mp-1000','BaTe','AB','Ba-Te','Cubic','NULL','m-3m',89.094,4.938,2,'Ba,Te',2,-4.535,-2.004,0.0,'1','0',1.593,3.638,2.045,'0',89.094,2,'BaTe','specific_ids','2025-11-15 11:56:43','2025-11-15 18:32:23','2025-11-20 01:42:37',)
INSERT INTO materials VALUES (11,'mp-1244933','Si','NULL','NULL','Triclinic','NULL','1',1793.76,2.6,100,'Si',1,'NULL',0.349,0.349,'0','NULL',0.0,'NULL','NULL','NULL','NULL','NULL','NULL','elements_Si','2025-11-15 11:56:45','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (12,'mp-1120447','Si','NULL','NULL','Triclinic','NULL','1',163.065,2.288,8,'Si',1,'NULL',0.373,0.373,'0','NULL',0.0,'NULL','NULL','NULL','NULL','NULL','NULL','elements_Si','2025-11-15 11:56:45','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (13,'mp-1244971','Si','NULL','NULL','Triclinic','NULL','1',1921.07,2.428,100,'Si',1,'NULL',0.317,0.317,'0','NULL',0.003,'NULL','NULL','NULL','NULL','NULL','NULL','elements_Si','2025-11-15 11:56:45','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (14,'mp-1244990','Si','NULL','NULL','Triclinic','NULL','1',1750.97,2.663,100,'Si',1,'NULL',0.366,0.366,'0','NULL',0.0,'NULL','NULL','NULL','NULL','NULL','NULL','elements_Si','2025-11-15 11:56:45','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (15,'mp-1245242','Si','NULL','NULL','Triclinic','NULL','1',1915.22,2.435,100,'Si',1,'NULL',0.317,0.317,'0','NULL',0.0,'NULL','NULL','NULL','NULL','NULL','NULL','elements_Si','2025-11-15 11:56:45','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (16,'mp-1245041','Si','NULL','NULL','Triclinic','NULL','1',1918.19,2.431,100,'Si',1,'NULL',0.31,0.31,'0','NULL',0.028,'NULL','NULL','NULL','NULL','NULL','NULL','elements_Si','2025-11-15 11:56:45','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (17,'mp-1403870','Si','NULL','NULL','Triclinic','NULL','1',174.108,2.143,8,'Si',1,'NULL',1.251,1.251,'0','NULL',0.0,'NULL','NULL','NULL','NULL','NULL','NULL','elements_Si','2025-11-15 11:56:45','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (18,'mp-644693','Si','NULL','NULL','Triclinic','NULL','1',174.108,2.143,8,'Si',1,'NULL',0.415,0.415,'0','NULL',0.0,'NULL','NULL','NULL','NULL','NULL','NULL','elements_Si','2025-11-15 11:56:45','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (19,'mp-676011','Si','NULL','NULL','Triclinic','NULL','1',159.131,2.345,8,'Si',1,'NULL',0.447,0.447,'0','NULL',0.0,'NULL','NULL','NULL','NULL','NULL','NULL','elements_Si','2025-11-15 11:56:45','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (20,'mp-988210','Si','NULL','NULL','Triclinic','NULL','1',174.108,2.143,8,'Si',1,'NULL',1.96,1.96,'0','NULL',0.0,'NULL','NULL','NULL','NULL','NULL','NULL','elements_Si','2025-11-15 11:56:45','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (21,'mp-1079297','Si','NULL','NULL','Monoclinic','NULL','2/m',167.231,2.231,8,'Si',1,'NULL',0.082,0.082,'0','NULL',0.274,'NULL','NULL','NULL','NULL','NULL','NULL','elements_Si','2025-11-15 11:56:45','2025-11-15 18:32:23','2025-11-20 01:42:36',)
INSERT INTO materials VALUES (22,'mp-1204046','Si','NULL','NULL','Tetragonal','NULL','4/mmm',2445.07,2.022,106,'Si',1,'NULL',0.179,0.179,'0','NULL',0.151,'NULL','NULL','NULL','NULL','NULL','NULL','elements_Si','2025-11-15 11:56:45','2025-11-15 18:32:23','2025-11-20 01:42:36',)
INSERT INTO materials VALUES (23,'mp-1056579','Si','NULL','NULL','Tetragonal','NULL','4/mmm',13.979,3.336,1,'Si',1,'NULL',0.484,0.484,'0','NULL',0.0,'NULL','NULL','NULL','NULL','NULL','NULL','elements_Si','2025-11-15 11:56:45','2025-11-15 18:32:23','2025-11-20 01:42:36',)
INSERT INTO materials VALUES (24,'mp-999200','Si','NULL','NULL','Tetragonal','NULL','4/mmm',85.035,2.194,4,'Si',1,'NULL',0.117,0.117,'0','NULL',0.44,'NULL','NULL','NULL','NULL','NULL','NULL','elements_Si','2025-11-15 11:56:45','2025-11-15 18:32:23','2025-11-20 01:42:36',)
INSERT INTO materials VALUES (25,'mp-92','Si','NULL','NULL','Tetragonal','NULL','4/mmm',29.9,3.12,2,'Si',1,'NULL',0.289,0.289,'0','NULL',0.0,'NULL','NULL','NULL','NULL','NULL','NULL','elements_Si','2025-11-15 11:56:45','2025-11-15 18:32:23','2025-11-20 01:42:36',)
INSERT INTO materials VALUES (26,'mp-32800','Ac2S3','NULL','NULL','Tetragonal','NULL','-42m','NULL','NULL','NULL','Ac,S',2,'NULL',-2.493,0.0,'1','1',2.296,7.098,4.801,'0','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:34',)
INSERT INTO materials VALUES (27,'mp-866101','AcCrO3','NULL','NULL','Cubic','NULL','m-3m','NULL','NULL','NULL','Ac,Cr,O',3,'NULL',-3.139,0.0,'1','1',2.003,8.257,6.254,'0','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:34',)
INSERT INTO materials VALUES (28,'mp-1183053','AcGaO3','NULL','NULL','Cubic','NULL','m-3m','NULL','NULL','NULL','Ac,Ga,O',3,'NULL',-3.063,0.0,'1','1',2.896,8.182,5.286,'0','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:34',)
INSERT INTO materials VALUES (29,'mp-861867','AcI3','NULL','NULL','Hexagonal','NULL','6/mmm','NULL','NULL','NULL','Ac,I',2,'NULL',-1.801,0.0,'1','1',2.589,2.273,-0.316,'0','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:34',)
INSERT INTO materials VALUES (30,'mp-567334','Ag(BCl)6','NULL','NULL','Cubic','NULL','m-3','NULL','NULL','NULL','Ag,B,Cl',3,'NULL',-0.737,0.0,'1','0',2.703,3.093,0.391,'1','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:34',)
INSERT INTO materials VALUES (31,'mp-560328','Ag15P4S16Cl3','NULL','NULL','Cubic','NULL','-43m','NULL','NULL','NULL','Ag,Cl,P,S',4,'NULL',-0.482,0.0,'1','0',1.289,3.457,2.168,'0','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:34',)
INSERT INTO materials VALUES (32,'mp-1215118','Ag16HgAs4S15','NULL','NULL','Monoclinic','NULL','2','NULL','NULL','NULL','Ag,As,Hg,S',4,'NULL',-0.294,0.006,'0','1',1.11,3.578,2.468,'1','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:34',)
INSERT INTO materials VALUES (33,'mp-1247866','Ag2B8O13','NULL','NULL','Monoclinic','NULL','2','NULL','NULL','NULL','Ag,B,O',3,'NULL',-2.503,0.007,'0','1',2.932,3.61,0.677,'0','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:34',)
INSERT INTO materials VALUES (34,'mp-759792','Ag2B8O13','NULL','NULL','Triclinic','NULL','1','NULL','NULL','NULL','Ag,B,O',3,'NULL',-2.499,0.012,'0','1',2.858,3.939,1.081,'0','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:34',)
INSERT INTO materials VALUES (35,'mp-559071','Ag2Bi2S3Cl2','NULL','NULL','Triclinic','NULL','-1','NULL','NULL','NULL','Ag,Bi,Cl,S',4,'NULL',-0.748,0.005,'0','0',1.637,4.621,2.984,'0','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:34',)
INSERT INTO materials VALUES (36,'mp-556345','Ag2BrNO3','NULL','NULL','Orthorhombic','NULL','mmm','NULL','NULL','NULL','Ag,Br,N,O',4,'NULL',-0.655,0.02,'0','0',1.605,2.208,0.603,'0','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (37,'mp-1199990','Ag2C4I3N','NULL','NULL','Orthorhombic','NULL','mmm','NULL','NULL','NULL','Ag,C,I,N',4,'NULL',0.873,1.093,'0','1',1.089,1.442,0.352,'0','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (38,'mp-574486','Ag2CN2','NULL','NULL','Monoclinic','NULL','2/m','NULL','NULL','NULL','Ag,C,N',3,'NULL',0.268,0.268,'0','0',1.004,2.978,1.975,'1','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (39,'mp-680067','Ag2CSNClO4','NULL','NULL','Monoclinic','NULL','2/m','NULL','NULL','NULL','Ag,C,Cl,N,O,S',6,'NULL',-0.246,0.897,'0','0',2.532,3.465,0.933,'1','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (40,'mp-1196546','Ag2Ge(S2O7)3','NULL','NULL','Trigonal','NULL','-3','NULL','NULL','NULL','Ag,Ge,O,S',4,'NULL',-1.6,0.0,'1','0',2.807,2.971,0.164,'0','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (41,'mp-554988','Ag2Ge2O5','NULL','NULL','Monoclinic','NULL','2/m','NULL','NULL','NULL','Ag,Ge,O',3,'NULL',-1.485,0.058,'0','0',1.04,2.667,1.626,'0','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (42,'mp-861942','Ag2GePbS4','NULL','NULL','Orthorhombic','NULL','mm2','NULL','NULL','NULL','Ag,Ge,Pb,S',4,'NULL',-0.55,0.0,'1','0',1.37,4.99,3.62,'0','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (43,'mp-1202797','Ag2H12C3S3(BrN3)2','NULL','NULL','Monoclinic','NULL','2/m','NULL','NULL','NULL','Ag,Br,C,H,N,S',6,'NULL',-0.434,0.036,'0','1',2.777,2.737,-0.04,'1','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (44,'mp-723002','Ag2H12S(NO)4','NULL','NULL','Tetragonal','NULL','-42m','NULL','NULL','NULL','Ag,H,N,O,S',5,'NULL',-0.78,0.027,'0','0',2.951,2.706,-0.245,'1','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:35',)
INSERT INTO materials VALUES (45,'mp-778019','Ag2H16O9','NULL','NULL','Monoclinic','NULL','2/m','NULL','NULL','NULL','Ag,H,O',3,'NULL',-1.096,0.077,'0','1',2.53,1.603,-0.927,'1','NULL','NULL','NULL','semiconductors','2025-11-15 11:56:53','2025-11-15 18:32:23','2025-11-20 01:42:35',)

    User request (in English):
    {question}

    Task:
    1. Generate a single MySQL SELECT query that answers the user's request.
    2. Do NOT use DROP/DELETE/UPDATE/INSERT.
    3. Return ONLY the SQL code, no explanation.
    """.strip()

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = (response.text or "").strip()
        if not text:
            print("Error: LLM returned empty text")
            sys.exit(1)
        if "`" in text:
            text = text.replace('`', '')
        if text[0:3] == 'sql':
            text = text[3:]
        print(text)
    except Exception as e:
        print(f"Error: exception while calling LLM: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
