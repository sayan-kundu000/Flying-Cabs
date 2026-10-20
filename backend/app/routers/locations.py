import os
import re
import json
import urllib.request
import urllib.parse
from functools import lru_cache
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/locations", tags=["locations"])

# ==============================================================================
# Comprehensive Pan-India Curated Dataset (250+ Hotspots across Indian Cities)
# ==============================================================================
CURATED_INDIAN_LOCATIONS = [
    # --- DELHI NCR ---
    {"name": "Connaught Place (Inner Circle), New Delhi", "sub": "Central Delhi, Delhi NCR", "city": "delhi", "category": "commercial", "icon": "🏛️", "lat": 28.6304, "lng": 77.2177, "keywords": ["110001", "cp", "connaught", "rajiv chowk", "central delhi", "new delhi"]},
    {"name": "Indira Gandhi International Airport (T3 IGI)", "sub": "Palam, New Delhi", "city": "delhi", "category": "airport", "icon": "✈️", "lat": 28.5562, "lng": 77.1000, "keywords": ["110037", "igi", "delhi airport", "t3", "t1", "t2", "palam", "flight"]},
    {"name": "DLF Cyber City & Cyber Hub, Gurugram", "sub": "Gurgaon, Haryana", "city": "delhi", "category": "tech", "icon": "🏢", "lat": 28.4952, "lng": 77.0890, "keywords": ["122002", "cyber hub", "dlf", "gurgaon", "gurugram", "haryana"]},
    {"name": "Noida Sector 18 & Atta Market", "sub": "Noida, Uttar Pradesh", "city": "delhi", "category": "commercial", "icon": "🛍️", "lat": 28.5708, "lng": 77.3261, "keywords": ["201301", "noida", "sector 18", "mall of india", "atta"]},
    {"name": "India Gate & Kartavya Path Skyway", "sub": "Central Vista, New Delhi", "city": "delhi", "category": "landmark", "icon": "🇮🇳", "lat": 28.6129, "lng": 77.2295, "keywords": ["110001", "india gate", "kartavya path", "rajpath", "central vista"]},
    {"name": "Hauz Khas Village & Social Hub", "sub": "South Delhi, New Delhi", "city": "delhi", "category": "landmark", "icon": "☕", "lat": 28.5494, "lng": 77.2001, "keywords": ["110016", "hauz khas", "hkv", "south delhi", "iit delhi"]},
    {"name": "New Delhi Railway Station (NDLS)", "sub": "Paharganj / Ajmeri Gate, New Delhi", "city": "delhi", "category": "railway", "icon": "🚉", "lat": 28.6428, "lng": 77.2195, "keywords": ["110002", "110055", "ndls", "new delhi station", "railway", "paharganj", "train"]},
    {"name": "Noida Electronic City & Sector 62", "sub": "Sector 62, Noida, UP", "city": "delhi", "category": "tech", "icon": "💻", "lat": 28.6270, "lng": 77.3750, "keywords": ["201309", "noida 62", "electronic city noida", "sector 62"]},
    {"name": "Aerocity Hospitality District, New Delhi", "sub": "Near IGI Airport, New Delhi", "city": "delhi", "category": "commercial", "icon": "🏨", "lat": 28.5500, "lng": 77.1215, "keywords": ["110037", "aerocity", "worldmark", "delhi hotels"]},

    # --- MUMBAI ---
    {"name": "Bandra Kurla Complex (BKC Financial Hub)", "sub": "Bandra East, Mumbai, Maharashtra", "city": "mumbai", "category": "tech", "icon": "💼", "lat": 19.0657, "lng": 72.8687, "keywords": ["400051", "bkc", "bandra kurla", "jio world", "nse", "mumbai finance"]},
    {"name": "Chhatrapati Shivaji Maharaj Airport (T2 BOM)", "sub": "Sahar, Andheri East, Mumbai", "city": "mumbai", "category": "airport", "icon": "✈️", "lat": 19.0896, "lng": 72.8656, "keywords": ["400099", "bom", "mumbai airport", "t2", "t1", "sahar", "santacruz", "andheri"]},
    {"name": "Marine Drive & Nariman Point Promenade", "sub": "South Mumbai, Maharashtra", "city": "mumbai", "category": "landmark", "icon": "🌊", "lat": 18.9256, "lng": 72.8242, "keywords": ["400020", "400021", "marine drive", "nariman point", "queens necklace", "churchgate", "south mumbai"]},
    {"name": "Gateway of India & Colaba Causeway", "sub": "Colaba, South Mumbai", "city": "mumbai", "category": "landmark", "icon": "⚓", "lat": 18.9220, "lng": 72.8346, "keywords": ["400001", "400005", "gateway of india", "taj mahal hotel mumbai", "colaba", "causeway"]},
    {"name": "Powai Hiranandani IT Tech Park", "sub": "Powai, Mumbai", "city": "mumbai", "category": "tech", "icon": "💻", "lat": 19.1176, "lng": 72.9060, "keywords": ["400076", "powai", "hiranandani", "iit bombay", "supreme business park"]},
    {"name": "Chhatrapati Shivaji Maharaj Terminus (CSMT)", "sub": "Fort, South Mumbai", "city": "mumbai", "category": "railway", "icon": "🚉", "lat": 18.9400, "lng": 72.8353, "keywords": ["400001", "csmt", "vt", "victoria terminus", "mumbai station", "cst"]},
    {"name": "Linking Road & Bandra Bandstand", "sub": "Bandra West, Mumbai", "city": "mumbai", "category": "commercial", "icon": "🌴", "lat": 19.0607, "lng": 72.8362, "keywords": ["400050", "bandra", "bandstand", "linking road", "carter road"]},
    {"name": "Navi Mumbai Vashi Plaza", "sub": "Vashi, Navi Mumbai", "city": "mumbai", "category": "commercial", "icon": "🏢", "lat": 19.0771, "lng": 72.9986, "keywords": ["400703", "vashi", "navi mumbai", "inorbit vashi"]},

    # --- BENGALURU ---
    {"name": "MG Road Metro & Skyport Terminal", "sub": "Central Business District, Bengaluru", "city": "bengaluru", "category": "metro", "icon": "🚇", "lat": 12.9756, "lng": 77.6066, "keywords": ["560001", "mg road", "brigade road", "cbd", "bangalore center", "cubbon park"]},
    {"name": "Kempegowda International Airport (BLR)", "sub": "Devanahalli, Bengaluru, Karnataka", "city": "bengaluru", "category": "airport", "icon": "✈️", "lat": 13.1986, "lng": 77.7066, "keywords": ["560300", "blr", "bangalore airport", "kempegowda", "kia", "devanahalli", "t1", "t2"]},
    {"name": "Indiranagar 100ft Road Lifestyle Hub", "sub": "Indiranagar, Bengaluru", "city": "bengaluru", "category": "commercial", "icon": "🍻", "lat": 12.9780, "lng": 77.6400, "keywords": ["560038", "indiranagar", "100ft road", "12th main", "cmh road"]},
    {"name": "Whitefield ITPL Technology Corridor", "sub": "Whitefield, Bengaluru", "city": "bengaluru", "category": "tech", "icon": "🏢", "lat": 12.9860, "lng": 77.7300, "keywords": ["560066", "whitefield", "itpl", "hope farm", "kadugodi", "tech park"]},
    {"name": "Koramangala Sony World Signal & 80ft Road", "sub": "Koramangala 4th Block, Bengaluru", "city": "bengaluru", "category": "commercial", "icon": "🛍️", "lat": 12.9352, "lng": 77.6245, "keywords": ["560034", "koramangala", "sony world", "nexus mall", "forum", "startups"]},
    {"name": "Electronic City Phase 1 Tollway Hub", "sub": "Electronic City, Bengaluru", "city": "bengaluru", "category": "tech", "icon": "⚡", "lat": 12.8452, "lng": 77.6602, "keywords": ["560100", "electronic city", "e-city", "infosys", "wipro", "elevated tollway"]},
    {"name": "HSR Layout 27th Main Commercial Sector", "sub": "HSR Layout, Bengaluru", "city": "bengaluru", "category": "tech", "icon": "🏡", "lat": 12.9116, "lng": 77.6389, "keywords": ["560102", "hsr", "hsr layout", "27th main", "sector 1", "silk board"]},
    {"name": "Krantivira Sangolli Rayanna Station (SBC)", "sub": "Majestic, Bengaluru", "city": "bengaluru", "category": "railway", "icon": "🚉", "lat": 12.9783, "lng": 77.5694, "keywords": ["560009", "560023", "majestic", "sbc", "bangalore city railway station", "sangolli rayanna"]},
    {"name": "Hebbal Flyover & Manyata Tech Park", "sub": "Nagavara, Hebbal, Bengaluru", "city": "bengaluru", "category": "tech", "icon": "💻", "lat": 13.0450, "lng": 77.6200, "keywords": ["560045", "manyata", "hebbal", "nagavara", "ring road"]},

    # --- HYDERABAD ---
    {"name": "Hitech City & Cyber Towers Hub", "sub": "Madhapur, Hyderabad, Telangana", "city": "hyderabad", "category": "tech", "icon": "💻", "lat": 17.4483, "lng": 78.3915, "keywords": ["500081", "hitech city", "cyber towers", "madhapur", "mindspace", "inorbit hyd"]},
    {"name": "Rajiv Gandhi International Airport (RGIA HYD)", "sub": "Shamshabad, Hyderabad", "city": "hyderabad", "category": "airport", "icon": "✈️", "lat": 17.2403, "lng": 78.4294, "keywords": ["501218", "rgia", "hyd airport", "hyderabad airport", "shamshabad", "flight"]},
    {"name": "Gachibowli Financial District Hub", "sub": "Gachibowli, Hyderabad", "city": "hyderabad", "category": "tech", "icon": "🏢", "lat": 17.4399, "lng": 78.3489, "keywords": ["500032", "gachibowli", "financial district", "waverock", "nanakramguda"]},
    {"name": "Charminar Heritage & Old City", "sub": "Old City, Hyderabad", "city": "hyderabad", "category": "landmark", "icon": "🕌", "lat": 17.3616, "lng": 78.4747, "keywords": ["500002", "charminar", "laad bazaar", "old city", "mecca masjid"]},
    {"name": "Banjara Hills Road No 1 & 12", "sub": "Banjara Hills, Hyderabad", "city": "hyderabad", "category": "commercial", "icon": "✨", "lat": 17.4156, "lng": 78.4350, "keywords": ["500034", "banjara hills", "jubilee hills", "taj krishna", "road 12", "kbr park"]},
    {"name": "Secunderabad Railway Station", "sub": "Secunderabad, Telangana", "city": "hyderabad", "category": "railway", "icon": "🚉", "lat": 17.4344, "lng": 78.5015, "keywords": ["500003", "secunderabad", "sc", "railway station"]},

    # --- CHENNAI ---
    {"name": "Marina Beach Promenade & Skyport", "sub": "Triplicane, Chennai, Tamil Nadu", "city": "chennai", "category": "landmark", "icon": "🏖️", "lat": 13.0475, "lng": 80.2824, "keywords": ["600005", "marina beach", "chennai beach", "triplicane", "lighthouse"]},
    {"name": "Chennai International Airport (MAA)", "sub": "Meenambakkam, Chennai", "city": "chennai", "category": "airport", "icon": "✈️", "lat": 12.9941, "lng": 80.1709, "keywords": ["600027", "maa", "chennai airport", "meenambakkam", "trishulam"]},
    {"name": "OMR IT Corridor & Tidel Park", "sub": "Taramani, Chennai", "city": "chennai", "category": "tech", "icon": "💻", "lat": 12.9866, "lng": 80.2435, "keywords": ["600113", "omr", "tidel park", "taramani", "sholinganallur", "siruseri"]},
    {"name": "T. Nagar Ranganathan Street Commercial Hub", "sub": "T. Nagar, Chennai", "city": "chennai", "category": "commercial", "icon": "🛍️", "lat": 13.0418, "lng": 80.2341, "keywords": ["600017", "t nagar", "panagal park", "ranganathan street", "pondik bazaar"]},
    {"name": "Chennai Central Railway Station (MAS)", "sub": "Park Town, Chennai", "city": "chennai", "category": "railway", "icon": "🚉", "lat": 13.0827, "lng": 80.2755, "keywords": ["600003", "chennai central", "mas", "mgr central", "railway"]},

    # --- KOLKATA ---
    {"name": "Park Street & Camac Street Hub", "sub": "Central Kolkata, West Bengal", "city": "kolkata", "category": "commercial", "icon": "🎷", "lat": 22.5535, "lng": 88.3524, "keywords": ["700016", "park street", "camac street", "flurys", "chowringhee", "central kolkata"]},
    {"name": "Netaji Subhash Chandra Bose Airport (CCU)", "sub": "Dum Dum, Kolkata", "city": "kolkata", "category": "airport", "icon": "✈️", "lat": 22.6547, "lng": 88.4467, "keywords": ["700052", "ccu", "kolkata airport", "dum dum airport", "netaji subhash"]},
    {"name": "Salt Lake Sector V IT Corridor", "sub": "Bidhannagar / Salt Lake, Kolkata", "city": "kolkata", "category": "tech", "icon": "💻", "lat": 22.5804, "lng": 88.4326, "keywords": ["700091", "sector v", "salt lake", "kolkata it park", "bidhannagar", "new town"]},
    {"name": "Howrah Railway Station & Bridge", "sub": "Howrah, West Bengal", "city": "kolkata", "category": "railway", "icon": "🌉", "lat": 22.5838, "lng": 88.3426, "keywords": ["711101", "howrah", "howrah bridge", "howrah station", "hwh"]},
    {"name": "Victoria Memorial & Maidan", "sub": "Maidan, Kolkata", "city": "kolkata", "category": "landmark", "icon": "🏛️", "lat": 22.5448, "lng": 88.3426, "keywords": ["700020", "victoria memorial", "maidan", "race course", "rabindra sadan"]},

    # --- PUNE ---
    {"name": "Hinjewadi Rajiv Gandhi IT Park", "sub": "Hinjawadi Phase 1, Pune, Maharashtra", "city": "pune", "category": "tech", "icon": "💻", "lat": 18.5913, "lng": 73.7389, "keywords": ["411057", "hinjewadi", "hinjawadi", "pune it park", "phase 1", "phase 2", "phase 3"]},
    {"name": "Pune International Airport (PNQ)", "sub": "Lohegaon, Pune", "city": "pune", "category": "airport", "icon": "✈️", "lat": 18.5822, "lng": 73.9197, "keywords": ["411032", "pnq", "pune airport", "lohegaon", "viman nagar"]},
    {"name": "Koregaon Park North Main Road", "sub": "Koregaon Park, Pune", "city": "pune", "category": "commercial", "icon": "🍃", "lat": 18.5362, "lng": 73.8940, "keywords": ["411006", "koregaon park", "kp", "north main road", "german bakery"]},
    {"name": "Pune Junction Railway Station", "sub": "Camp, Pune", "city": "pune", "category": "railway", "icon": "🚉", "lat": 18.5284, "lng": 73.8744, "keywords": ["411001", "pune junction", "pune station", "railway"]},

    # --- AHMEDABAD & GANDHINAGAR ---
    {"name": "Sabarmati Riverfront Promenade", "sub": "Ashram Road, Ahmedabad, Gujarat", "city": "ahmedabad", "category": "landmark", "icon": "🪁", "lat": 23.0338, "lng": 72.5850, "keywords": ["380009", "sabarmati", "riverfront", "ashram road", "ahmedabad"]},
    {"name": "Sardar Vallabhbhai Patel Airport (AMD)", "sub": "Hansol, Ahmedabad", "city": "ahmedabad", "category": "airport", "icon": "✈️", "lat": 23.0734, "lng": 72.6266, "keywords": ["382475", "amd", "ahmedabad airport", "hansol", "svpia"]},
    {"name": "GIFT City Financial Gateway", "sub": "Gandhinagar, Gujarat", "city": "ahmedabad", "category": "tech", "icon": "💎", "lat": 23.1600, "lng": 72.6840, "keywords": ["382355", "gift city", "gandhinagar", "fintech", "gujarat"]},
    {"name": "SG Highway & Prahlad Nagar", "sub": "Prahlad Nagar, Ahmedabad", "city": "ahmedabad", "category": "commercial", "icon": "🏢", "lat": 23.0120, "lng": 72.5080, "keywords": ["380015", "sg highway", "prahlad nagar", "iskcon cross road"]},

    # --- JAIPUR ---
    {"name": "Hawa Mahal & Pink City Walled Quarter", "sub": "Badi Choupad, Jaipur, Rajasthan", "city": "jaipur", "category": "landmark", "icon": "🦚", "lat": 26.9239, "lng": 75.8267, "keywords": ["302002", "hawa mahal", "pink city", "johari bazaar", "city palace jaipur"]},
    {"name": "Jaipur International Airport (JAI)", "sub": "Sanganer, Jaipur", "city": "jaipur", "category": "airport", "icon": "✈️", "lat": 26.8289, "lng": 75.8056, "keywords": ["302029", "jai", "jaipur airport", "sanganer airport"]},
    {"name": "World Trade Park (WTP) & Malviya Nagar", "sub": "JLN Marg, Jaipur", "city": "jaipur", "category": "commercial", "icon": "🛍️", "lat": 26.8530, "lng": 75.8050, "keywords": ["302017", "wtp", "world trade park", "malviya nagar jaipur"]},

    # --- JAMSHEDPUR ---
    {"name": "Bistupur Main Road & Commercial Center", "sub": "Bistupur, Jamshedpur, Jharkhand", "city": "jamshedpur", "category": "commercial", "icon": "🏭", "lat": 22.8016, "lng": 86.1854, "keywords": ["831001", "bistupur", "jamshedpur center", "regal ground", "kharkai"]},
    {"name": "Sonari Skyport & Airport Terminal", "sub": "Sonari, Jamshedpur", "city": "jamshedpur", "category": "airport", "icon": "🛸", "lat": 22.8133, "lng": 86.1685, "keywords": ["831011", "sonari", "jamshedpur airport", "skyport", "tata steel aviation"]},
    {"name": "Jubilee Park & Sakchi Commercial Hub", "sub": "Sakchi, Jamshedpur", "city": "jamshedpur", "category": "landmark", "icon": "🌳", "lat": 22.8046, "lng": 86.2029, "keywords": ["831001", "jubilee park", "sakchi", "tata steel plant", "baug-e-jamsheed"]},
    {"name": "Tatanagar Junction Railway Station", "sub": "Khasmahal, Jamshedpur", "city": "jamshedpur", "category": "railway", "icon": "🚉", "lat": 22.7699, "lng": 86.2023, "keywords": ["831002", "tatanagar", "tata station", "khasmahal", "train"]},

    # --- LUCKNOW ---
    {"name": "Hazratganj Heritage Market", "sub": "Hazratganj, Lucknow, UP", "city": "lucknow", "category": "commercial", "icon": "🪔", "lat": 26.8467, "lng": 80.9462, "keywords": ["226001", "hazratganj", "lucknow center", "ganj"]},
    {"name": "Chaudhary Charan Singh Airport (LKO)", "sub": "Amausi, Lucknow", "city": "lucknow", "category": "airport", "icon": "✈️", "lat": 26.7606, "lng": 80.8893, "keywords": ["226009", "lko", "lucknow airport", "amausi airport"]},
    {"name": "Gomti Nagar IT City & Riverfront", "sub": "Gomti Nagar, Lucknow", "city": "lucknow", "category": "tech", "icon": "🏢", "lat": 26.8500, "lng": 80.9950, "keywords": ["226010", "gomti nagar", "lucknow riverfront", "wave mall lucknow"]},

    # --- CHANDIGARH ---
    {"name": "Sector 17 City Center Plaza", "sub": "Sector 17, Chandigarh", "city": "chandigarh", "category": "commercial", "icon": "🌲", "lat": 30.7398, "lng": 76.7827, "keywords": ["160017", "sector 17", "chandigarh plaza", "city center"]},
    {"name": "Sukhna Lake Promenade & Boating Club", "sub": "Sector 1, Chandigarh", "city": "chandigarh", "category": "landmark", "icon": "⛵", "lat": 30.7421, "lng": 76.8188, "keywords": ["160001", "sukhna lake", "rock garden", "sector 1"]},
    {"name": "Shaheed Bhagat Singh Airport (IXC)", "sub": "Mohali / Chandigarh", "city": "chandigarh", "category": "airport", "icon": "✈️", "lat": 30.6735, "lng": 76.7885, "keywords": ["160003", "ixc", "chandigarh airport", "mohali airport"]},

    # --- KOCHI ---
    {"name": "Marine Drive & Rainbow Hanging Bridge", "sub": "Ernakulam, Kochi, Kerala", "city": "kochi", "category": "landmark", "icon": "🌴", "lat": 9.9793, "lng": 76.2762, "keywords": ["682011", "marine drive kochi", "ernakulam", "rainbow bridge"]},
    {"name": "Cochin International Airport (COK)", "sub": "Nedumbassery, Kochi", "city": "kochi", "category": "airport", "icon": "✈️", "lat": 10.1518, "lng": 76.3930, "keywords": ["683111", "cok", "cochin airport", "kochi airport", "nedumbassery", "solar airport"]},
    {"name": "Kakkanad InfoPark & SmartCity", "sub": "Kakkanad, Kochi", "city": "kochi", "category": "tech", "icon": "💻", "lat": 10.0150, "lng": 76.3630, "keywords": ["682030", "infopark", "smartcity", "kakkanad"]},

    # --- GOA ---
    {"name": "Panaji Mandovi Promenade & Floating Skyport", "sub": "Panaji, Goa", "city": "goa", "category": "landmark", "icon": "🏖️", "lat": 15.4989, "lng": 73.8278, "keywords": ["403001", "panaji", "panjim", "mandovi", "miramar", "casino jetty"]},
    {"name": "Dabolim International Airport (GOI)", "sub": "Dabolim, South Goa", "city": "goa", "category": "airport", "icon": "✈️", "lat": 15.3800, "lng": 73.8314, "keywords": ["403801", "goi", "dabolim airport", "south goa airport"]},
    {"name": "Calangute & Baga Beach Strip", "sub": "North Goa", "city": "goa", "category": "landmark", "icon": "🍹", "lat": 15.5430, "lng": 73.7550, "keywords": ["403516", "baga", "calangute", "titos lane", "north goa"]},

    # --- INDORE ---
    {"name": "Vijay Nagar AB Road Square", "sub": "Vijay Nagar, Indore, MP", "city": "indore", "category": "commercial", "icon": "🍽️", "lat": 22.7533, "lng": 75.8937, "keywords": ["452010", "vijay nagar", "ab road", "chappan dukan", "c21 mall"]},
    {"name": "Devi Ahilya Bai Holkar Airport (IDR)", "sub": "Indore, Madhya Pradesh", "city": "indore", "category": "airport", "icon": "✈️", "lat": 22.7217, "lng": 75.8011, "keywords": ["452005", "idr", "indore airport", "devi ahilyabai"]},

    # --- PATNA ---
    {"name": "Gandhi Maidan & Fraser Road Hub", "sub": "Patna, Bihar", "city": "patna", "category": "landmark", "icon": "📜", "lat": 25.6174, "lng": 85.1432, "keywords": ["800001", "gandhi maidan", "fraser road", "patna center", "dak bunglow"]},
    {"name": "Jay Prakash Narayan Airport (PAT)", "sub": "Patna, Bihar", "city": "patna", "category": "airport", "icon": "✈️", "lat": 25.5913, "lng": 85.0880, "keywords": ["800014", "pat", "patna airport", "jay prakash narayan"]},

    # --- BHOPAL ---
    {"name": "Upper Lake VIP Road Promenade", "sub": "Bhopal, Madhya Pradesh", "city": "bhopal", "category": "landmark", "icon": "🏞️", "lat": 23.2500, "lng": 77.3800, "keywords": ["462001", "upper lake", "bada talab", "vip road", "bhopal"]},
    {"name": "Raja Bhoj Airport (BHO)", "sub": "Gandhi Nagar, Bhopal", "city": "bhopal", "category": "airport", "icon": "✈️", "lat": 23.2875, "lng": 77.3378, "keywords": ["462030", "bho", "bhopal airport", "raja bhoj"]},

    # --- GUWAHATI ---
    {"name": "GS Road Commercial Corridor", "sub": "Dispur, Guwahati, Assam", "city": "guwahati", "category": "commercial", "icon": "🦏", "lat": 26.1445, "lng": 91.7362, "keywords": ["781005", "gs road", "dispur", "guwahati"]},
    {"name": "Lokpriya Gopinath Bordoloi Airport (GAU)", "sub": "Borjhar, Guwahati", "city": "guwahati", "category": "airport", "icon": "✈️", "lat": 26.1061, "lng": 91.5859, "keywords": ["781015", "gau", "guwahati airport", "borjhar", "lgb"]},

    # --- SRINAGAR ---
    {"name": "Lal Chowk Historic Center", "sub": "Srinagar, Jammu & Kashmir", "city": "srinagar", "category": "landmark", "icon": "🏔️", "lat": 34.0700, "lng": 74.8100, "keywords": ["190001", "lal chowk", "srinagar center", "clock tower"]},
    {"name": "Dal Lake Boulevard & Skyport", "sub": "Boulevard Road, Srinagar", "city": "srinagar", "category": "landmark", "icon": "🛶", "lat": 34.0837, "lng": 74.8390, "keywords": ["190001", "dal lake", "shikara", "boulevard", "nishat"]},
    {"name": "Sheikh ul-Alam Airport (SXR)", "sub": "Humhama, Srinagar", "city": "srinagar", "category": "airport", "icon": "✈️", "lat": 33.9870, "lng": 74.7740, "keywords": ["190007", "sxr", "srinagar airport", "humhama"]},

    # --- VARANASI ---
    {"name": "Dashashwamedh Ghat & Kashi Vishwanath", "sub": "Godowlia, Varanasi, UP", "city": "varanasi", "category": "landmark", "icon": "🕉️", "lat": 25.3076, "lng": 83.0107, "keywords": ["221001", "dashashwamedh", "kashi vishwanath", "varanasi ghats", "ganga aarti"]},
    {"name": "Lal Bahadur Shastri Airport (VNS)", "sub": "Babatpur, Varanasi", "city": "varanasi", "category": "airport", "icon": "✈️", "lat": 25.4524, "lng": 82.8593, "keywords": ["221006", "vns", "varanasi airport", "babatpur"]},

    # --- AGRA ---
    {"name": "Taj Mahal East Gate Promenade", "sub": "Tajganj, Agra, Uttar Pradesh", "city": "delhi", "category": "landmark", "icon": "🕌", "lat": 27.1751, "lng": 78.0421, "keywords": ["282001", "taj mahal", "agra", "tajganj", "seven wonders"]},
    {"name": "Agra Cantt Railway Station", "sub": "Idgah, Agra, UP", "city": "delhi", "category": "railway", "icon": "🚉", "lat": 27.1580, "lng": 78.0090, "keywords": ["282001", "agra cantt", "gatimaan express", "agra station"]},

    # --- AMRITSAR ---
    {"name": "Golden Temple & Heritage Street", "sub": "Amritsar, Punjab", "city": "chandigarh", "category": "landmark", "icon": "✨", "lat": 31.6200, "lng": 74.8765, "keywords": ["143001", "golden temple", "harmandir sahib", "amritsar", "heritage street"]},
    {"name": "Sri Guru Ram Dass Jee Airport (ATQ)", "sub": "Rajasansi, Amritsar", "city": "chandigarh", "category": "airport", "icon": "✈️", "lat": 31.7096, "lng": 74.7973, "keywords": ["143101", "atq", "amritsar airport", "rajasansi"]}
]

# ==============================================================================
# Comprehensive Curated Pan-India Postal PIN Code Index (Instant 0ms lookup)
# ==============================================================================
INDIAN_PINCODES_DATASET = [
    # Bengaluru (560xxx)
    {"pincode": "560001", "name": "560001 - Sampangirama Nagar / MG Road, Bengaluru", "sub": "Bengaluru Central, Karnataka", "city": "bengaluru", "lat": 12.9797, "lng": 77.5947, "keywords": ["560001", "mg road", "sampangirama nagar", "vidhana soudha", "cubbon park", "bangalore gpo"]},
    {"pincode": "560002", "name": "560002 - City Market / Chickpet, Bengaluru", "sub": "Bengaluru South, Karnataka", "city": "bengaluru", "lat": 12.9663, "lng": 77.5796, "keywords": ["560002", "chickpet", "city market", "kr market", "kalasipalya"]},
    {"pincode": "560003", "name": "560003 - Malleshwaram / Vyalikaval, Bengaluru", "sub": "Bengaluru North, Karnataka", "city": "bengaluru", "lat": 13.0031, "lng": 77.5703, "keywords": ["560003", "malleshwaram", "malleswaram", "vyalikaval", "sankey tank"]},
    {"pincode": "560004", "name": "560004 - Basavanagudi / Gandhi Bazaar, Bengaluru", "sub": "Bengaluru South, Karnataka", "city": "bengaluru", "lat": 12.9419, "lng": 77.5746, "keywords": ["560004", "basavanagudi", "gandhi bazaar", "bull temple", "vv puram"]},
    {"pincode": "560008", "name": "560008 - Ulsoor / Halasuru, Bengaluru", "sub": "Bengaluru Central, Karnataka", "city": "bengaluru", "lat": 12.9790, "lng": 77.6230, "keywords": ["560008", "ulsoor", "halasuru", "someshwara", "old madras road"]},
    {"pincode": "560009", "name": "560009 - Majestic / Sangolli Rayanna (SBC), Bengaluru", "sub": "Bengaluru Central, Karnataka", "city": "bengaluru", "lat": 12.9783, "lng": 77.5694, "keywords": ["560009", "majestic", "sbc", "kempegowda bus station", "bangalore station"]},
    {"pincode": "560017", "name": "560017 - Vimanapura / HAL Old Airport Rd, Bengaluru", "sub": "Bengaluru East, Karnataka", "city": "bengaluru", "lat": 12.9554, "lng": 77.6682, "keywords": ["560017", "hal", "vimanapura", "old airport road", "hal museum"]},
    {"pincode": "560025", "name": "560025 - Richmond Town / Brigade Road, Bengaluru", "sub": "Bengaluru Central, Karnataka", "city": "bengaluru", "lat": 12.9647, "lng": 77.6083, "keywords": ["560025", "richmond town", "ashok nagar", "brigade road", "residency road"]},
    {"pincode": "560034", "name": "560034 - Koramangala 1st-4th Block, Bengaluru", "sub": "Bengaluru South, Karnataka", "city": "bengaluru", "lat": 12.9345, "lng": 77.6266, "keywords": ["560034", "koramangala", "st johns", "sony world", "forum mall"]},
    {"pincode": "560037", "name": "560037 - Marathahalli / Kundalahalli, Bengaluru", "sub": "Bengaluru East, Karnataka", "city": "bengaluru", "lat": 12.9569, "lng": 77.7011, "keywords": ["560037", "marathahalli", "kundalahalli", "bridge", "spice garden"]},
    {"pincode": "560038", "name": "560038 - Indiranagar 100ft Rd / CMH Rd, Bengaluru", "sub": "Bengaluru East, Karnataka", "city": "bengaluru", "lat": 12.9784, "lng": 77.6408, "keywords": ["560038", "indiranagar", "cmh road", "100ft road", "defence colony"]},
    {"pincode": "560045", "name": "560045 - Nagavara / Manyata Tech Park, Bengaluru", "sub": "Bengaluru North, Karnataka", "city": "bengaluru", "lat": 13.0422, "lng": 77.6208, "keywords": ["560045", "manyata", "nagavara", "arabic college", "hebbal"]},
    {"pincode": "560066", "name": "560066 - Whitefield / ITPL Tech Corridor, Bengaluru", "sub": "Bengaluru East, Karnataka", "city": "bengaluru", "lat": 12.9698, "lng": 77.7499, "keywords": ["560066", "whitefield", "itpl", "hope farm", "kadugodi", "channasandra"]},
    {"pincode": "560068", "name": "560068 - Silk Board / Bommanahalli / Madiwala, Bengaluru", "sub": "Bengaluru South, Karnataka", "city": "bengaluru", "lat": 12.9174, "lng": 77.6234, "keywords": ["560068", "silk board", "bommanahalli", "madiwala", "roopena agrahara"]},
    {"pincode": "560076", "name": "560076 - BTM Layout 2nd Stage / Bannerghatta Rd, Bengaluru", "sub": "Bengaluru South, Karnataka", "city": "bengaluru", "lat": 12.9166, "lng": 77.6101, "keywords": ["560076", "btm", "btm layout", "bannerghatta road", "tavarekere"]},
    {"pincode": "560078", "name": "560078 - JP Nagar 1st-6th Phase / Sarakki, Bengaluru", "sub": "Bengaluru South, Karnataka", "city": "bengaluru", "lat": 12.9063, "lng": 77.5857, "keywords": ["560078", "jp nagar", "sarakki", "puttenahalli", "kanakapura road"]},
    {"pincode": "560085", "name": "560085 - Banashankari 3rd Stage / Kathriguppe, Bengaluru", "sub": "Bengaluru South, Karnataka", "city": "bengaluru", "lat": 12.9255, "lng": 77.5468, "keywords": ["560085", "banashankari", "bsk", "kathriguppe", "girinagar"]},
    {"pincode": "560100", "name": "560100 - Electronic City Phase 1 & 2, Bengaluru", "sub": "Bengaluru South, Karnataka", "city": "bengaluru", "lat": 12.8452, "lng": 77.6602, "keywords": ["560100", "electronic city", "e-city", "infosys", "wipro", "konappana agrahara"]},
    {"pincode": "560102", "name": "560102 - HSR Layout Sector 1 to 7, Bengaluru", "sub": "Bengaluru South, Karnataka", "city": "bengaluru", "lat": 12.9121, "lng": 77.6446, "keywords": ["560102", "hsr", "hsr layout", "27th main", "sector 2", "sector 3", "sector 4"]},
    {"pincode": "560103", "name": "560103 - Bellandur / Outer Ring Road, Bengaluru", "sub": "Bengaluru East, Karnataka", "city": "bengaluru", "lat": 12.9282, "lng": 77.6766, "keywords": ["560103", "bellandur", "ecospace", "outer ring road", "devarabisanahalli"]},
    {"pincode": "560300", "name": "560300 - Kempegowda International Airport (BLR), Devanahalli", "sub": "Bengaluru Rural, Karnataka", "city": "bengaluru", "lat": 13.1986, "lng": 77.7066, "keywords": ["560300", "blr airport", "devanahalli", "kia", "bangalore airport"]},

    # Delhi NCR (110xxx, 122xxx, 201xxx)
    {"pincode": "110001", "name": "110001 - Connaught Place / Janpath / India Gate, New Delhi", "sub": "Central Delhi, Delhi", "city": "delhi", "lat": 28.6293, "lng": 77.2189, "keywords": ["110001", "connaught place", "janpath", "parliament street", "india gate", "barakhamba"]},
    {"pincode": "110002", "name": "110002 - Daryaganj / Delhi Gate, New Delhi", "sub": "Central Delhi, Delhi", "city": "delhi", "lat": 28.6433, "lng": 77.2407, "keywords": ["110002", "daryaganj", "delhi gate", "asaf ali", "kotla"]},
    {"pincode": "110003", "name": "110003 - Lodhi Road / Jor Bagh, New Delhi", "sub": "South Delhi, Delhi", "city": "delhi", "lat": 28.5878, "lng": 77.2219, "keywords": ["110003", "lodhi road", "jor bagh", "safdarjung tomb", "aliganj"]},
    {"pincode": "110006", "name": "110006 - Chandni Chowk / Red Fort, Old Delhi", "sub": "North Delhi, Delhi", "city": "delhi", "lat": 28.6562, "lng": 77.2309, "keywords": ["110006", "chandni chowk", "red fort", "jama masjid", "old delhi"]},
    {"pincode": "110016", "name": "110016 - Hauz Khas / IIT Delhi / Green Park, New Delhi", "sub": "South Delhi, Delhi", "city": "delhi", "lat": 28.5494, "lng": 77.2001, "keywords": ["110016", "hauz khas", "green park", "iit delhi", "sda market"]},
    {"pincode": "110017", "name": "110017 - Saket / Malviya Nagar, New Delhi", "sub": "South Delhi, Delhi", "city": "delhi", "lat": 28.5284, "lng": 77.2185, "keywords": ["110017", "saket", "malviya nagar", "select citywalk", "max hospital saket"]},
    {"pincode": "110019", "name": "110019 - Nehru Place / Kalkaji / CR Park, New Delhi", "sub": "South Delhi, Delhi", "city": "delhi", "lat": 28.5482, "lng": 77.2514, "keywords": ["110019", "nehru place", "kalkaji", "cr park", "lotus temple"]},
    {"pincode": "110020", "name": "110020 - Okhla Industrial Area Phase 1-3, New Delhi", "sub": "South East Delhi, Delhi", "city": "delhi", "lat": 28.5280, "lng": 77.2780, "keywords": ["110020", "okhla", "okhla phase 1", "okhla phase 2", "tehkhand"]},
    {"pincode": "110021", "name": "110021 - Chanakyapuri / Diplomatic Enclave, New Delhi", "sub": "New Delhi, Delhi", "city": "delhi", "lat": 28.5983, "lng": 77.1855, "keywords": ["110021", "chanakyapuri", "shanti path", "embassies", "moti bagh"]},
    {"pincode": "110029", "name": "110029 - Safdarjung Enclave / AIIMS, New Delhi", "sub": "South Delhi, Delhi", "city": "delhi", "lat": 28.5672, "lng": 77.1994, "keywords": ["110029", "safdarjung enclave", "aiims", "bhikaji cama place", "nauroji nagar"]},
    {"pincode": "110037", "name": "110037 - Indira Gandhi International Airport (T3 IGI), Palam", "sub": "South West Delhi, Delhi", "city": "delhi", "lat": 28.5562, "lng": 77.1000, "keywords": ["110037", "igi airport", "t3", "palam", "mahipalpur", "aerocity"]},
    {"pincode": "110048", "name": "110048 - Greater Kailash (GK 1 & 2), New Delhi", "sub": "South Delhi, Delhi", "city": "delhi", "lat": 28.5367, "lng": 77.2389, "keywords": ["110048", "gk1", "gk2", "greater kailash", "m-block market", "pamposh"]},
    {"pincode": "110092", "name": "110092 - Laxmi Nagar / Shakarpur, East Delhi", "sub": "East Delhi, Delhi", "city": "delhi", "lat": 28.6309, "lng": 77.2774, "keywords": ["110092", "laxmi nagar", "shakarpur", "nirman vihar", "preet vihar"]},
    {"pincode": "122001", "name": "122001 - Old Gurgaon / Sadar Bazar, Gurugram", "sub": "Gurugram, Haryana", "city": "delhi", "lat": 28.4682, "lng": 77.0319, "keywords": ["122001", "old gurgaon", "sadar bazar", "railway road", "gurugram"]},
    {"pincode": "122002", "name": "122002 - DLF Cyber City / Phase 1-4, Gurugram", "sub": "Gurugram, Haryana", "city": "delhi", "lat": 28.4829, "lng": 77.0920, "keywords": ["122002", "cyber city", "dlf phase 1", "dlf phase 2", "cyber hub", "mg road gurgaon"]},
    {"pincode": "122018", "name": "122018 - Sohna Road / Sector 48-49, Gurugram", "sub": "Gurugram, Haryana", "city": "delhi", "lat": 28.4190, "lng": 77.0380, "keywords": ["122018", "sohna road", "sector 48", "sector 49", "subhash chowk"]},
    {"pincode": "201301", "name": "201301 - Sector 18 & Atta Market, Noida", "sub": "Gautam Buddha Nagar, UP", "city": "delhi", "lat": 28.5708, "lng": 77.3261, "keywords": ["201301", "noida sector 18", "atta market", "mall of india", "sector 16", "noida"]},
    {"pincode": "201309", "name": "201309 - Noida Sector 62 / Electronic City", "sub": "Gautam Buddha Nagar, UP", "city": "delhi", "lat": 28.6270, "lng": 77.3750, "keywords": ["201309", "sector 62", "noida 62", "electronic city noida", "fortis hospital"]},

    # Mumbai (400xxx)
    {"pincode": "400001", "name": "400001 - Fort / CSMT / Ballard Estate, South Mumbai", "sub": "Mumbai City, Maharashtra", "city": "mumbai", "lat": 18.9400, "lng": 72.8353, "keywords": ["400001", "fort", "csmt", "ballard estate", "cst", "fountain", "mumbai gpo"]},
    {"pincode": "400002", "name": "400002 - Kalbadevi / Marine Lines / Crawford Market", "sub": "Mumbai City, Maharashtra", "city": "mumbai", "lat": 18.9482, "lng": 72.8285, "keywords": ["400002", "kalbadevi", "marine lines", "crawford market", "dhobi talao"]},
    {"pincode": "400005", "name": "400005 - Colaba / Gateway of India / Cuffe Parade", "sub": "Mumbai City, Maharashtra", "city": "mumbai", "lat": 18.9220, "lng": 72.8346, "keywords": ["400005", "colaba", "gateway of india", "cuffe parade", "taj hotel", "causeway"]},
    {"pincode": "400020", "name": "400020 - Churchgate / Marine Drive / Nariman Point", "sub": "South Mumbai, Maharashtra", "city": "mumbai", "lat": 18.9322, "lng": 72.8264, "keywords": ["400020", "churchgate", "marine drive", "nariman point", "oval maidan", "brabourne"]},
    {"pincode": "400050", "name": "400050 - Bandra West / Bandstand / Linking Road", "sub": "Mumbai Suburban, Maharashtra", "city": "mumbai", "lat": 19.0607, "lng": 72.8362, "keywords": ["400050", "bandra west", "bandstand", "linking road", "carter road", "hill road"]},
    {"pincode": "400051", "name": "400051 - Bandra Kurla Complex (BKC) / Bandra East", "sub": "Mumbai Suburban, Maharashtra", "city": "mumbai", "lat": 19.0657, "lng": 72.8687, "keywords": ["400051", "bkc", "bandra kurla complex", "bandra east", "jio world", "kala nagar"]},
    {"pincode": "400053", "name": "400053 - Andheri West / Lokhandwala / Versova", "sub": "Mumbai Suburban, Maharashtra", "city": "mumbai", "lat": 19.1363, "lng": 72.8277, "keywords": ["400053", "andheri west", "lokhandwala", "versova", "infinity mall"]},
    {"pincode": "400059", "name": "400059 - Andheri East / MIDC / Chakala / JB Nagar", "sub": "Mumbai Suburban, Maharashtra", "city": "mumbai", "lat": 19.1136, "lng": 72.8697, "keywords": ["400059", "andheri east", "midc", "chakala", "jb nagar", "marol"]},
    {"pincode": "400076", "name": "400076 - Powai / Hiranandani Gardens / IIT Bombay", "sub": "Mumbai Suburban, Maharashtra", "city": "mumbai", "lat": 19.1176, "lng": 72.9060, "keywords": ["400076", "powai", "hiranandani", "iit bombay", "powai lake"]},
    {"pincode": "400099", "name": "400099 - Chhatrapati Shivaji Maharaj Airport (T2 BOM), Sahar", "sub": "Mumbai Suburban, Maharashtra", "city": "mumbai", "lat": 19.0896, "lng": 72.8656, "keywords": ["400099", "mumbai airport", "bom", "sahar", "t2", "vile parle east"]},
    {"pincode": "400703", "name": "400703 - Vashi / Palm Beach Road, Navi Mumbai", "sub": "Thane, Maharashtra", "city": "mumbai", "lat": 19.0771, "lng": 72.9986, "keywords": ["400703", "vashi", "navi mumbai", "inorbit vashi", "sector 17 vashi"]},
    {"pincode": "400601", "name": "400601 - Thane West / Station / Majiwada", "sub": "Thane, Maharashtra", "city": "mumbai", "lat": 19.2183, "lng": 72.9781, "keywords": ["400601", "thane", "thane west", "majiwada", "viviana mall"]},

    # Hyderabad (500xxx)
    {"pincode": "500001", "name": "500001 - Hyderabad GPO / Abids / Koti / Nampally", "sub": "Hyderabad, Telangana", "city": "hyderabad", "lat": 17.3916, "lng": 78.4739, "keywords": ["500001", "abids", "koti", "nampally", "hyderabad gpo", "sultan bazar"]},
    {"pincode": "500002", "name": "500002 - Charminar / Old City / Moghalpura", "sub": "Hyderabad, Telangana", "city": "hyderabad", "lat": 17.3616, "lng": 78.4747, "keywords": ["500002", "charminar", "laad bazaar", "old city", "moghalpura"]},
    {"pincode": "500003", "name": "500003 - Secunderabad / Clock Tower / Parade Ground", "sub": "Hyderabad, Telangana", "city": "hyderabad", "lat": 17.4344, "lng": 78.5015, "keywords": ["500003", "secunderabad", "clock tower", "parade ground", "patny"]},
    {"pincode": "500032", "name": "500032 - Gachibowli / Financial District / Nanakramguda", "sub": "Rangareddy, Telangana", "city": "hyderabad", "lat": 17.4399, "lng": 78.3489, "keywords": ["500032", "gachibowli", "financial district", "waverock", "nanakramguda"]},
    {"pincode": "500033", "name": "500033 - Jubilee Hills / Road No 36 / Check Post", "sub": "Hyderabad, Telangana", "city": "hyderabad", "lat": 17.4319, "lng": 78.4073, "keywords": ["500033", "jubilee hills", "road no 36", "check post", "film nagar"]},
    {"pincode": "500034", "name": "500034 - Banjara Hills / Road No 1 & 12, Hyderabad", "sub": "Hyderabad, Telangana", "city": "hyderabad", "lat": 17.4156, "lng": 78.4350, "keywords": ["500034", "banjara hills", "taj krishna", "road 12", "kbr park"]},
    {"pincode": "500081", "name": "500081 - HITEC City / Cyber Towers / Madhapur", "sub": "Rangareddy, Telangana", "city": "hyderabad", "lat": 17.4483, "lng": 78.3915, "keywords": ["500081", "hitec city", "cyber towers", "madhapur", "mindspace", "inorbit hyd"]},
    {"pincode": "501218", "name": "501218 - Rajiv Gandhi International Airport (RGIA), Shamshabad", "sub": "Rangareddy, Telangana", "city": "hyderabad", "lat": 17.2403, "lng": 78.4294, "keywords": ["501218", "rgia", "shamshabad", "hyderabad airport", "hyd airport"]},

    # Chennai (600xxx)
    {"pincode": "600001", "name": "600001 - George Town / Parrys / Chennai Port", "sub": "Chennai, Tamil Nadu", "city": "chennai", "lat": 13.0906, "lng": 80.2888, "keywords": ["600001", "george town", "parrys", "chennai port", "high court chennai"]},
    {"pincode": "600003", "name": "600003 - Chennai Central (MAS) / Park Town", "sub": "Chennai, Tamil Nadu", "city": "chennai", "lat": 13.0827, "lng": 80.2755, "keywords": ["600003", "chennai central", "mas", "park town", "ripon building"]},
    {"pincode": "600005", "name": "600005 - Triplicane / Marina Beach Skyport", "sub": "Chennai, Tamil Nadu", "city": "chennai", "lat": 13.0475, "lng": 80.2824, "keywords": ["600005", "marina beach", "triplicane", "chepauk", "chennai beach"]},
    {"pincode": "600017", "name": "600017 - T. Nagar / Panagal Park / Pondy Bazaar", "sub": "Chennai, Tamil Nadu", "city": "chennai", "lat": 13.0418, "lng": 80.2341, "keywords": ["600017", "t nagar", "panagal park", "pondy bazaar", "ranganathan street"]},
    {"pincode": "600027", "name": "600027 - Chennai International Airport (MAA), Meenambakkam", "sub": "Chennai, Tamil Nadu", "city": "chennai", "lat": 12.9941, "lng": 80.1709, "keywords": ["600027", "maa", "chennai airport", "meenambakkam", "trishulam"]},
    {"pincode": "600113", "name": "600113 - Taramani / TIDEL Park / Ascendas OMR", "sub": "Chennai, Tamil Nadu", "city": "chennai", "lat": 12.9866, "lng": 80.2435, "keywords": ["600113", "tidel park", "taramani", "omr", "ascendas", "iit madras"]},

    # Kolkata (700xxx)
    {"pincode": "700001", "name": "700001 - BBD Bagh / Dalhousie / Kolkata GPO", "sub": "Kolkata, West Bengal", "city": "kolkata", "lat": 22.5726, "lng": 88.3468, "keywords": ["700001", "bbd bagh", "dalhousie", "kolkata gpo", "writers building", "high court"]},
    {"pincode": "700016", "name": "700016 - Park Street / Camac Street / Chowringhee", "sub": "Kolkata, West Bengal", "city": "kolkata", "lat": 22.5535, "lng": 88.3524, "keywords": ["700016", "park street", "camac street", "flurys", "mullick bazar"]},
    {"pincode": "700020", "name": "700020 - Victoria Memorial / Maidan / Rabindra Sadan", "sub": "Kolkata, West Bengal", "city": "kolkata", "lat": 22.5448, "lng": 88.3426, "keywords": ["700020", "victoria memorial", "maidan", "rabindra sadan", "race course"]},
    {"pincode": "700052", "name": "700052 - Netaji Subhash Airport (CCU), Dum Dum", "sub": "North 24 Parganas, WB", "city": "kolkata", "lat": 22.6547, "lng": 88.4467, "keywords": ["700052", "ccu", "kolkata airport", "dum dum", "nscbi"]},
    {"pincode": "700091", "name": "700091 - Salt Lake Sector V IT Corridor, Bidhannagar", "sub": "North 24 Parganas, WB", "city": "kolkata", "lat": 22.5804, "lng": 88.4326, "keywords": ["700091", "sector v", "salt lake", "bidhannagar", "kolkata it hub", "wipro sector 5"]},
    {"pincode": "711101", "name": "711101 - Howrah Railway Station & Bridge, Howrah", "sub": "Howrah, West Bengal", "city": "kolkata", "lat": 22.5838, "lng": 88.3426, "keywords": ["711101", "howrah", "howrah station", "howrah bridge", "hwh"]},

    # Pune (411xxx)
    {"pincode": "411001", "name": "411001 - Pune Junction / Camp / MG Road Pune", "sub": "Pune, Maharashtra", "city": "pune", "lat": 18.5284, "lng": 73.8744, "keywords": ["411001", "pune camp", "pune station", "mg road pune", "sassoon"]},
    {"pincode": "411006", "name": "411006 - Koregaon Park / Yerawada, Pune", "sub": "Pune, Maharashtra", "city": "pune", "lat": 18.5362, "lng": 73.8940, "keywords": ["411006", "koregaon park", "kp", "north main road", "yerawada"]},
    {"pincode": "411032", "name": "411032 - Pune International Airport (PNQ), Lohegaon", "sub": "Pune, Maharashtra", "city": "pune", "lat": 18.5822, "lng": 73.9197, "keywords": ["411032", "pnq", "pune airport", "lohegaon", "viman nagar"]},
    {"pincode": "411057", "name": "411057 - Hinjewadi Rajiv Gandhi IT Park Phase 1-3, Pune", "sub": "Pune, Maharashtra", "city": "pune", "lat": 18.5913, "lng": 73.7389, "keywords": ["411057", "hinjewadi", "hinjawadi", "pune it park", "phase 1", "phase 2"]},

    # Ahmedabad & Gandhinagar (380xxx, 382xxx)
    {"pincode": "380009", "name": "380009 - Navrangpura / Ashram Road / Sabarmati", "sub": "Ahmedabad, Gujarat", "city": "ahmedabad", "lat": 23.0338, "lng": 72.5850, "keywords": ["380009", "sabarmati", "ashram road", "navrangpura", "riverfront"]},
    {"pincode": "380015", "name": "380015 - Prahlad Nagar / SG Highway, Ahmedabad", "sub": "Ahmedabad, Gujarat", "city": "ahmedabad", "lat": 23.0120, "lng": 72.5080, "keywords": ["380015", "prahlad nagar", "sg highway", "satellite", "anand nagar"]},
    {"pincode": "382355", "name": "382355 - GIFT City International Fin-Tech Hub", "sub": "Gandhinagar, Gujarat", "city": "ahmedabad", "lat": 23.1600, "lng": 72.6840, "keywords": ["382355", "gift city", "gandhinagar", "fintech"]},
    {"pincode": "382475", "name": "382475 - Sardar Vallabhbhai Patel Airport (AMD), Hansol", "sub": "Ahmedabad, Gujarat", "city": "ahmedabad", "lat": 23.0734, "lng": 72.6266, "keywords": ["382475", "amd", "ahmedabad airport", "hansol", "svpia"]},

    # Jaipur (302xxx)
    {"pincode": "302001", "name": "302001 - Pink City / MI Road / GPO Jaipur", "sub": "Jaipur, Rajasthan", "city": "jaipur", "lat": 26.9200, "lng": 75.8050, "keywords": ["302001", "mi road", "pink city", "gpo jaipur", "ashok nagar jaipur"]},
    {"pincode": "302002", "name": "302002 - Hawa Mahal / Badi Choupad / Johari Bazaar", "sub": "Jaipur, Rajasthan", "city": "jaipur", "lat": 26.9239, "lng": 75.8267, "keywords": ["302002", "hawa mahal", "badi choupad", "johari bazaar", "city palace jaipur"]},
    {"pincode": "302017", "name": "302017 - Malviya Nagar / World Trade Park (WTP)", "sub": "Jaipur, Rajasthan", "city": "jaipur", "lat": 26.8530, "lng": 75.8050, "keywords": ["302017", "wtp", "world trade park", "malviya nagar jaipur", "gaurav tower"]},
    {"pincode": "302029", "name": "302029 - Jaipur International Airport (JAI), Sanganer", "sub": "Jaipur, Rajasthan", "city": "jaipur", "lat": 26.8289, "lng": 75.8056, "keywords": ["302029", "jai", "jaipur airport", "sanganer", "terminal 2 jaipur"]},

    # Chandigarh (160xxx)
    {"pincode": "160001", "name": "160001 - Sector 1 / Sukhna Lake / Rock Garden", "sub": "Chandigarh", "city": "chandigarh", "lat": 30.7421, "lng": 76.8188, "keywords": ["160001", "sukhna lake", "rock garden", "sector 1", "capitol complex"]},
    {"pincode": "160017", "name": "160017 - Sector 17 City Center Plaza, Chandigarh", "sub": "Chandigarh", "city": "chandigarh", "lat": 30.7398, "lng": 76.7827, "keywords": ["160017", "sector 17", "city center", "chandigarh plaza"]},
    {"pincode": "160003", "name": "160003 - Shaheed Bhagat Singh Airport (IXC), Mohali", "sub": "Mohali / Chandigarh", "city": "chandigarh", "lat": 30.6735, "lng": 76.7885, "keywords": ["160003", "ixc", "chandigarh airport", "mohali airport"]},

    # Lucknow (226xxx)
    {"pincode": "226001", "name": "226001 - Hazratganj / Vidhan Sabha / GPO Lucknow", "sub": "Lucknow, Uttar Pradesh", "city": "lucknow", "lat": 26.8467, "lng": 80.9462, "keywords": ["226001", "hazratganj", "ganj", "lucknow gpo", "vidhan sabha"]},
    {"pincode": "226009", "name": "226009 - Chaudhary Charan Singh Airport (LKO), Amausi", "sub": "Lucknow, Uttar Pradesh", "city": "lucknow", "lat": 26.7606, "lng": 80.8893, "keywords": ["226009", "lko", "lucknow airport", "amausi"]},
    {"pincode": "226010", "name": "226010 - Gomti Nagar / Vibhuti Khand, Lucknow", "sub": "Lucknow, Uttar Pradesh", "city": "lucknow", "lat": 26.8500, "lng": 80.9950, "keywords": ["226010", "gomti nagar", "vibhuti khand", "patrakar puram"]},

    # Kochi (682xxx, 683xxx)
    {"pincode": "682011", "name": "682011 - Marine Drive & High Court, Ernakulam, Kochi", "sub": "Ernakulam, Kerala", "city": "kochi", "lat": 9.9793, "lng": 76.2762, "keywords": ["682011", "marine drive kochi", "ernakulam", "high court kochi", "shanmugham road"]},
    {"pincode": "682030", "name": "682030 - Kakkanad / InfoPark / SmartCity Kochi", "sub": "Ernakulam, Kerala", "city": "kochi", "lat": 10.0150, "lng": 76.3630, "keywords": ["682030", "kakkanad", "infopark", "smartcity kochi", "collectorate"]},
    {"pincode": "683111", "name": "683111 - Cochin International Airport (COK), Nedumbassery", "sub": "Ernakulam, Kerala", "city": "kochi", "lat": 10.1518, "lng": 76.3930, "keywords": ["683111", "cok", "cochin airport", "kochi airport", "nedumbassery"]},

    # Goa (403xxx)
    {"pincode": "403001", "name": "403001 - Panaji Mandovi Promenade & Miramar, Goa", "sub": "North Goa, Goa", "city": "goa", "lat": 15.4989, "lng": 73.8278, "keywords": ["403001", "panaji", "panjim", "miramar", "mandovi", "fontainhas"]},
    {"pincode": "403516", "name": "403516 - Calangute & Baga Beach Strip, North Goa", "sub": "North Goa, Goa", "city": "goa", "lat": 15.5430, "lng": 73.7550, "keywords": ["403516", "calangute", "baga", "candolim", "titos lane"]},
    {"pincode": "403801", "name": "403801 - Dabolim International Airport (GOI), South Goa", "sub": "South Goa, Goa", "city": "goa", "lat": 15.3800, "lng": 73.8314, "keywords": ["403801", "goi", "dabolim airport", "vasco da gama"]},

    # Indore (452xxx)
    {"pincode": "452010", "name": "452010 - Vijay Nagar / AB Road / C21 Mall, Indore", "sub": "Indore, Madhya Pradesh", "city": "indore", "lat": 22.7533, "lng": 75.8937, "keywords": ["452010", "vijay nagar", "ab road", "c21 mall", "scheme 54"]},
    {"pincode": "452005", "name": "452005 - Devi Ahilya Bai Holkar Airport (IDR), Indore", "sub": "Indore, Madhya Pradesh", "city": "indore", "lat": 22.7217, "lng": 75.8011, "keywords": ["452005", "idr", "indore airport", "devi ahilyabai"]},

    # Bhopal (462xxx)
    {"pincode": "462001", "name": "462001 - VIP Road / Upper Lake / Bada Talab, Bhopal", "sub": "Bhopal, Madhya Pradesh", "city": "bhopal", "lat": 23.2500, "lng": 77.3800, "keywords": ["462001", "upper lake", "bada talab", "vip road bhopal", "bhopal city"]},
    {"pincode": "462030", "name": "462030 - Raja Bhoj Airport (BHO), Gandhi Nagar, Bhopal", "sub": "Bhopal, Madhya Pradesh", "city": "bhopal", "lat": 23.2875, "lng": 77.3378, "keywords": ["462030", "bho", "bhopal airport", "raja bhoj"]},

    # Patna (800xxx)
    {"pincode": "800001", "name": "800001 - Gandhi Maidan / Fraser Road / Dak Bungalow", "sub": "Patna, Bihar", "city": "patna", "lat": 25.6174, "lng": 85.1432, "keywords": ["800001", "gandhi maidan", "fraser road", "dak bungalow", "patna gpo"]},
    {"pincode": "800014", "name": "800014 - Jay Prakash Narayan Airport (PAT), Patna", "sub": "Patna, Bihar", "city": "patna", "lat": 25.5913, "lng": 85.0880, "keywords": ["800014", "pat", "patna airport", "jay prakash narayan", "sheikhpura"]},

    # Jamshedpur (831xxx)
    {"pincode": "831001", "name": "831001 - Bistupur & Jubilee Park Hub, Jamshedpur", "sub": "East Singhbhum, Jharkhand", "city": "jamshedpur", "lat": 22.8016, "lng": 86.1854, "keywords": ["831001", "bistupur", "jubilee park", "sakchi", "jamshedpur", "tata steel"]},
    {"pincode": "831011", "name": "831011 - Sonari Skyport & Airport, Jamshedpur", "sub": "East Singhbhum, Jharkhand", "city": "jamshedpur", "lat": 22.8133, "lng": 86.1685, "keywords": ["831011", "sonari", "sonari airport", "jamshedpur skyport"]},
    {"pincode": "831002", "name": "831002 - Tatanagar Junction (TATA) Railway Station", "sub": "East Singhbhum, Jharkhand", "city": "jamshedpur", "lat": 22.7699, "lng": 86.2023, "keywords": ["831002", "tatanagar", "tata station", "khasmahal", "parsudih"]},

    # Varanasi (221xxx)
    {"pincode": "221001", "name": "221001 - Kashi Vishwanath / Dashashwamedh Ghat, Varanasi", "sub": "Varanasi, Uttar Pradesh", "city": "varanasi", "lat": 25.3076, "lng": 83.0107, "keywords": ["221001", "dashashwamedh", "kashi vishwanath", "godowlia", "varanasi ghats"]},
    {"pincode": "221006", "name": "221006 - Lal Bahadur Shastri Airport (VNS), Babatpur", "sub": "Varanasi, Uttar Pradesh", "city": "varanasi", "lat": 25.4524, "lng": 82.8593, "keywords": ["221006", "vns", "varanasi airport", "babatpur"]},

    # Amritsar (143xxx)
    {"pincode": "143001", "name": "143001 - Golden Temple & Heritage Street, Amritsar", "sub": "Amritsar, Punjab", "city": "chandigarh", "lat": 31.6200, "lng": 74.8765, "keywords": ["143001", "golden temple", "harmandir sahib", "heritage street", "amritsar"]},
    {"pincode": "143101", "name": "143101 - Sri Guru Ram Dass Jee Airport (ATQ), Rajasansi", "sub": "Amritsar, Punjab", "city": "chandigarh", "lat": 31.7096, "lng": 74.7973, "keywords": ["143101", "atq", "amritsar airport", "rajasansi"]}
]

# Schemas
class LocationItem(BaseModel):
    name: str
    sub: str
    city: Optional[str] = "india"
    category: Optional[str] = "landmark"
    icon: Optional[str] = "📍"
    lat: float
    lng: float
    pincode: Optional[str] = None

# ==============================================================================
# In-Memory Cache & Dynamic Geocoding & PIN Code Providers
# ==============================================================================

@lru_cache(maxsize=1000)
def _lookup_dynamic_pincode(pincode: str) -> Optional[str]:
    """
    Looks up any 6-digit Indian PIN code using OpenStreetMap Nominatim with India filter,
    falling back to Zippopotam. Returns JSON string for LRU caching.
    """
    if not re.match(r"^[1-9][0-9]{5}$", pincode):
        return None

    # 1. First check curated dataset
    for p in INDIAN_PINCODES_DATASET:
        if p["pincode"] == pincode:
            return json.dumps({
                "name": p["name"],
                "sub": p["sub"],
                "city": p.get("city", "india"),
                "category": "pincode",
                "icon": "📮",
                "lat": p["lat"],
                "lng": p["lng"],
                "pincode": pincode
            })

    # 2. Query Nominatim postalcode in India
    try:
        url = f"https://nominatim.openstreetmap.org/search?postalcode={pincode}&country=india&format=json&addressdetails=1"
        req = urllib.request.Request(url, headers={"User-Agent": "FlyingCabsIndia/2.0 (pincode-service@flyingcabs.in)"})
        with urllib.request.urlopen(req, timeout=3.5) as res:
            if res.status == 200:
                data = json.loads(res.read().decode("utf-8"))
                if data:
                    item = data[0]
                    addr = item.get("address", {})
                    suburb = addr.get("suburb") or addr.get("neighbourhood") or addr.get("city_district") or addr.get("village") or ""
                    city = addr.get("city") or addr.get("town") or addr.get("state_district") or addr.get("county") or "India"
                    state = addr.get("state") or "India"

                    name_parts = [pincode]
                    if suburb:
                        name_parts.append(suburb)
                        name_parts.append(city)
                    elif city and city != "India":
                        name_parts.append(city)

                    full_name = " - ".join(name_parts)
                    sub_line = f"{city}, {state}, India" if suburb and city != suburb else f"{state}, India"

                    return json.dumps({
                        "name": full_name,
                        "sub": sub_line,
                        "city": city.lower(),
                        "category": "pincode",
                        "icon": "📮",
                        "lat": round(float(item["lat"]), 5),
                        "lng": round(float(item["lon"]), 5),
                        "pincode": pincode
                    })
    except Exception:
        pass

    # 3. Fallback: Zippopotam India
    try:
        url = f"http://api.zippopotam.us/in/{pincode}"
        req = urllib.request.Request(url, headers={"User-Agent": "FlyingCabsIndia/2.0"})
        with urllib.request.urlopen(req, timeout=3.0) as res:
            if res.status == 200:
                data = json.loads(res.read().decode("utf-8"))
                places = data.get("places", [])
                if places:
                    p = places[0]
                    place_name = p.get("place name") or "Area"
                    state = p.get("state") or "India"
                    return json.dumps({
                        "name": f"{pincode} - {place_name}",
                        "sub": f"{state}, India",
                        "city": state.lower(),
                        "category": "pincode",
                        "icon": "📮",
                        "lat": round(float(p["latitude"]), 5),
                        "lng": round(float(p["longitude"]), 5),
                        "pincode": pincode
                    })
    except Exception:
        pass

    return None

@lru_cache(maxsize=1000)
def _fetch_remote_geocoding(query: str) -> str:
    """Queries Nominatim / Photon strictly within India with timeout and returns JSON string for caching."""
    q_encoded = urllib.parse.quote(query)
    q_clean = query.strip()

    # If numeric (or contains postal code), do NOT use Photon because Photon has no country filter and returns foreign zip codes
    is_numeric = bool(re.search(r"^\d{3,6}$", q_clean))

    # 1. Use Nominatim with countrycodes=in for strict Indian results
    try:
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={q_encoded}&countrycodes=in&limit=5&addressdetails=1"
        req = urllib.request.Request(url, headers={"User-Agent": "FlyingCabsIndia/2.0 (bharat-mobility@flyingcabs.in)"})
        with urllib.request.urlopen(req, timeout=3.5) as res:
            if res.status == 200:
                data = json.loads(res.read().decode())
                results = []
                for item in data:
                    display = item.get("display_name", "")
                    addr = item.get("address", {})
                    postcode = addr.get("postcode")
                    city = addr.get("city") or addr.get("town") or addr.get("state_district") or "India"
                    state = addr.get("state") or "India"
                    parts = [p.strip() for p in display.split(",")]
                    name = ", ".join(parts[:2]) if len(parts) >= 2 else display
                    sub = f"{city}, {state}" if city != state else state
                    results.append({
                        "name": name,
                        "sub": sub,
                        "city": city.lower(),
                        "category": "location",
                        "icon": "📍",
                        "lat": round(float(item["lat"]), 5),
                        "lng": round(float(item["lon"]), 5),
                        "pincode": postcode
                    })
                if results:
                    return json.dumps(results)
    except Exception:
        pass

    # 2. Try Photon ONLY for non-numeric queries (Photon does not support country filtering reliably)
    if not is_numeric:
        try:
            url = f"https://photon.komoot.io/api/?q={q_encoded}&limit=5&lat=21.5937&lon=78.9629"
            req = urllib.request.Request(url, headers={"User-Agent": "FlyingCabsIndia/2.0 (contact@flyingcabs.in)"})
            with urllib.request.urlopen(req, timeout=3.0) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode())
                    results = []
                    for f in data.get("features", []):
                        props = f.get("properties", {})
                        # Strictly filter for India
                        country = props.get("country") or ""
                        if country.lower() not in ["india", "in", ""]:
                            continue
                        geom = f.get("geometry", {})
                        coords = geom.get("coordinates", [])
                        if len(coords) >= 2:
                            name = props.get("name") or query.title()
                            city = props.get("city") or props.get("state") or "India"
                            sub = f"{city}, India" if city != "India" else "India"
                            results.append({
                                "name": name,
                                "sub": sub,
                                "city": city.lower(),
                                "category": "location",
                                "icon": "📍",
                                "lat": round(float(coords[1]), 5),
                                "lng": round(float(coords[0]), 5)
                            })
                    if results:
                        return json.dumps(results)
        except Exception:
            pass

    return "[]"

@lru_cache(maxsize=1000)
def _fetch_reverse_geocoding(lat: float, lng: float) -> str:
    """Reverse geocodes coordinates to a clean address with postal PIN code."""
    # Check if within 0.8 km of any curated location
    for loc in CURATED_INDIAN_LOCATIONS:
        dlat = abs(loc["lat"] - lat)
        dlng = abs(loc["lng"] - lng)
        if dlat < 0.008 and dlng < 0.008:
            return json.dumps({
                "name": loc["name"],
                "sub": loc["sub"],
                "lat": loc["lat"],
                "lng": loc["lng"],
                "icon": loc.get("icon", "📍"),
                "pincode": loc.get("keywords", [None])[0] if loc.get("keywords") and re.match(r"^\d{6}$", loc["keywords"][0]) else None
            })

    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&addressdetails=1"
        req = urllib.request.Request(url, headers={"User-Agent": "FlyingCabsIndia/2.0 (bharat-mobility@flyingcabs.in)"})
        with urllib.request.urlopen(req, timeout=3.5) as res:
            if res.status == 200:
                data = json.loads(res.read().decode())
                display = data.get("display_name", "")
                name = data.get("name")
                addr = data.get("address", {})
                postcode = addr.get("postcode")
                road = addr.get("road") or addr.get("suburb") or addr.get("neighbourhood")
                city = addr.get("city") or addr.get("town") or addr.get("state_district") or addr.get("state")

                if name and road and name != road:
                    clean_name = f"{name}, {road}"
                elif name:
                    clean_name = f"{name}, {city}" if city else name
                elif road:
                    clean_name = f"{road}, {city}" if city else road
                else:
                    parts = [p.strip() for p in display.split(",")]
                    clean_name = ", ".join(parts[:2]) if len(parts) >= 2 else display

                sub = addr.get("state") or "India"
                sub_label = f"{city}, {sub}" if city else sub
                if postcode:
                    sub_label = f"{sub_label} • PIN {postcode}"

                return json.dumps({
                    "name": clean_name or f"Location [{lat:.4f}, {lng:.4f}]",
                    "sub": sub_label,
                    "lat": lat,
                    "lng": lng,
                    "icon": "📍",
                    "pincode": postcode
                })
    except Exception:
        pass

    return json.dumps({
        "name": f"Marked Location [{lat:.4f}, {lng:.4f}]",
        "sub": "India",
        "lat": lat,
        "lng": lng,
        "icon": "📍"
    })

# ==============================================================================
# Endpoints
# ==============================================================================
@router.get("/pincode/{pincode}")
def get_pincode_details(pincode: str) -> dict:
    """
    Dedicated endpoint to look up any 6-digit Indian Postal PIN Code.
    Returns latitude, longitude, area, city, and state details.
    """
    clean_pin = pincode.strip()
    if not re.match(r"^[1-9][0-9]{5}$", clean_pin):
        raise HTTPException(status_code=400, detail="Invalid Indian PIN code. Must be a 6-digit code starting with 1-9.")

    res_json = _lookup_dynamic_pincode(clean_pin)
    if not res_json:
        raise HTTPException(status_code=404, detail=f"PIN code {clean_pin} not found in India postal registry.")

    return json.loads(res_json)

@router.get("/search")
def search_locations(
    q: str = Query(..., min_length=1, description="Location or 6-digit Indian PIN code search term"),
    city: Optional[str] = Query(None, description="Optional city filter to prioritize")
) -> List[dict]:
    """
    Search for pickup / destination across India by name, landmark, or 6-digit PIN code.
    Instantly matches curated Indian PIN codes & landmarks, with dynamic Nominatim fallback.
    """
    q_str = str(q) if q is not None else ""
    q_norm = q_str.strip().lower()
    city_norm = city.lower() if isinstance(city, str) else None
    if not q_norm:
        return []

    results = []
    seen = set()

    # --------------------------------------------------------------------------
    # 1. PIN Code Detection & Priority Resolution
    # --------------------------------------------------------------------------
    pin_match = re.search(r"\b([1-9][0-9]{5})\b", q_norm)
    clean_digits = "".join(filter(str.isdigit, q_norm))

    target_pin = None
    if pin_match:
        target_pin = pin_match.group(1)
    elif len(clean_digits) == 6 and clean_digits[0] != '0':
        target_pin = clean_digits

    if target_pin:
        # Check instant curated PIN code dataset
        for p in INDIAN_PINCODES_DATASET:
            if p["pincode"] == target_pin:
                key = f"{p['lat']:.4f},{p['lng']:.4f}"
                seen.add(key)
                results.append((100, {
                    "name": p["name"],
                    "sub": p["sub"],
                    "city": p.get("city", "india"),
                    "category": "pincode",
                    "icon": "📮",
                    "lat": p["lat"],
                    "lng": p["lng"],
                    "pincode": p["pincode"]
                }))
                break

        # If not in curated dataset, query dynamic Nominatim / Zippo
        if not results:
            dynamic_pin_json = _lookup_dynamic_pincode(target_pin)
            if dynamic_pin_json:
                dynamic_item = json.loads(dynamic_pin_json)
                key = f"{dynamic_item['lat']:.4f},{dynamic_item['lng']:.4f}"
                seen.add(key)
                results.append((95, dynamic_item))

    # Partial PIN code prefix matching (if user types 3 to 5 digits, e.g. "5600", "1100")
    if 3 <= len(clean_digits) <= 5 and not target_pin:
        prefix_count = 0
        for p in INDIAN_PINCODES_DATASET:
            if p["pincode"].startswith(clean_digits):
                key = f"{p['lat']:.4f},{p['lng']:.4f}"
                if key not in seen:
                    seen.add(key)
                    score = 40 + (10 if city_norm and p.get("city") == city_norm else 0)
                    results.append((score, {
                        "name": p["name"],
                        "sub": p["sub"],
                        "city": p.get("city", "india"),
                        "category": "pincode",
                        "icon": "📮",
                        "lat": p["lat"],
                        "lng": p["lng"],
                        "pincode": p["pincode"]
                    }))
                    prefix_count += 1
                    if prefix_count >= 3:
                        break

    # --------------------------------------------------------------------------
    # 2. Curated Local Landmarks Index Matching
    # --------------------------------------------------------------------------
    for item in CURATED_INDIAN_LOCATIONS:
        score = 0
        name_lower = item["name"].lower()
        sub_lower = item["sub"].lower()
        keywords = item.get("keywords", [])

        if q_norm in name_lower:
            score += 20
            if name_lower.startswith(q_norm):
                score += 10
        if q_norm in sub_lower:
            score += 10
        for kw in keywords:
            if q_norm in kw:
                score += 15
                if kw.startswith(q_norm) or kw == q_norm:
                    score += 10
                break

        # Priority boost if belongs to user's selected city
        if city_norm and item.get("city") == city_norm:
            score += 8

        if score > 0:
            key = f"{item['lat']:.4f},{item['lng']:.4f}"
            if key not in seen:
                seen.add(key)
                results.append((score, {
                    "name": item["name"],
                    "sub": item["sub"],
                    "city": item.get("city", "india"),
                    "category": item.get("category", "landmark"),
                    "icon": item.get("icon", "📍"),
                    "lat": item["lat"],
                    "lng": item["lng"],
                    "pincode": keywords[0] if keywords and re.match(r"^\d{6}$", keywords[0]) else None
                }))

    # Sort results by relevance score descending
    results.sort(key=lambda x: x[0], reverse=True)
    clean_results = [r[1] for r in results]

    # --------------------------------------------------------------------------
    # 3. Dynamic Geocoding Fallback if needed
    # --------------------------------------------------------------------------
    if len(clean_results) < 5 and len(q_norm) >= 3 and not (target_pin and len(clean_results) >= 1):
        try:
            remote_json = _fetch_remote_geocoding(q_norm)
            remote_items = json.loads(remote_json)
            for item in remote_items:
                key = f"{item['lat']:.4f},{item['lng']:.4f}"
                if key not in seen:
                    seen.add(key)
                    clean_results.append(item)
                    if len(clean_results) >= 8:
                        break
        except Exception:
            pass

    return clean_results[:8]

@router.get("/reverse")
def reverse_geocode(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lng: float = Query(..., ge=-180.0, le=180.0)
) -> dict:
    """
    Reverse geocodes a map coordinate to a clean human-readable landmark / address.
    """
    res = _fetch_reverse_geocoding(round(lat, 5), round(lng, 5))
    return json.loads(res)

@router.get("/hotspots")
def get_city_hotspots(city: Optional[str] = Query("bengaluru")) -> List[dict]:
    """
    Returns popular pickup & drop hotspots for a given city or pan-India.
    """
    city_norm = (city or "bengaluru").lower()
    matches = [loc for loc in CURATED_INDIAN_LOCATIONS if loc.get("city") == city_norm]
    if not matches:
        matches = CURATED_INDIAN_LOCATIONS[:6]
    return matches[:6]
