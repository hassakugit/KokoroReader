# app/voice_data.py

def get_formatted_voice_list():
    """
    Returns a list of voices sorted by:
    1. English First
    2. Then by Region/Gender
    """
    
    # Raw data mapping
    # Format: ID: (Name, Language, Region, Gender)
    raw_voices = {
        # --- American English ---
        "af_bella":   ("Bella", "English", "American", "Female"),
        "af_sarah":   ("Sarah", "English", "American", "Female"),
        "af_nicole":  ("Nicole", "English", "American", "Female"),
        "af_sky":     ("Sky",    "English", "American", "Female"),
        "af_alloy":   ("Alloy",  "English", "American", "Female"),
        "af_aoede":   ("Aoede",  "English", "American", "Female"),
        "af_jessica": ("Jessica","English", "American", "Female"),
        "af_kore":    ("Kore",   "English", "American", "Female"),
        "af_river":   ("River",  "English", "American", "Female"),
        "am_adam":    ("Adam",   "English", "American", "Male"),
        "am_michael": ("Michael","English", "American", "Male"),
        "am_echo":    ("Echo",   "English", "American", "Male"),
        "am_eric":    ("Eric",   "English", "American", "Male"),
        "am_fenrir":  ("Fenrir", "English", "American", "Male"),
        "am_liam":    ("Liam",   "English", "American", "Male"),
        "am_onyx":    ("Onyx",   "English", "American", "Male"),
        "am_puck":    ("Puck",   "English", "American", "Male"),
        "am_santa":   ("Santa",  "English", "American", "Male"),

        # --- British English ---
        "bf_emma":     ("Emma",     "English", "British", "Female"),
        "bf_isabella": ("Isabella", "English", "British", "Female"),
        "bf_alice":    ("Alice",    "English", "British", "Female"),
        "bf_lily":     ("Lily",     "English", "British", "Female"),
        "bm_george":   ("George",   "English", "British", "Male"),
        "bm_lewis":    ("Lewis",    "English", "British", "Male"),
        "bm_daniel":   ("Daniel",   "English", "British", "Male"),
        "bm_fable":    ("Fable",    "English", "British", "Male"),

        # --- Other Languages ---
        "jf_alpha":    ("Alpha",    "Japanese", "Japan", "Female"),
        "jf_gongitsune": ("Gongitsune", "Japanese", "Japan", "Female"),
        "jf_nezumi":   ("Nezumi",   "Japanese", "Japan", "Female"),
        "jf_tebukuro": ("Tebukuro", "Japanese", "Japan", "Female"),
        "jm_kumo":     ("Kumo",     "Japanese", "Japan", "Male"),
        
        "zf_xiaobei":  ("Xiaobei",  "Chinese", "China", "Female"),
        "zf_xiaoni":   ("Xiaoni",   "Chinese", "China", "Female"),
        "zf_xiaoxiao": ("Xiaoxiao", "Chinese", "China", "Female"),
        "zf_xiaoyi":   ("Xiaoyi",   "Chinese", "China", "Female"),
        
        "ef_dora":     ("Dora",     "Spanish", "Spain", "Female"),
        "em_alex":     ("Alex",     "Spanish", "Spain", "Male"),
        "em_santa":    ("Santa",    "Spanish", "Spain", "Male"),
        
        "ff_siwis":    ("Siwis",    "French", "France", "Female"),
        
        "it_aladin":   ("Aladin",   "Italian", "Italy", "Male"),
        
        "pf_dora":     ("Dora",     "Portuguese", "Brazil", "Female"),
        "pm_alex":     ("Alex",     "Portuguese", "Brazil", "Male"),
        "pm_santa":    ("Santa",    "Portuguese", "Brazil", "Male"),
    }

    formatted_list = []
    
    for vid, (name, lang, region, gender) in raw_voices.items():
        label = f"[{lang} - {region} - {gender}] {name}"
        # Priority for sorting: English=0, Others=1
        sort_priority = 0 if lang == "English" else 1
        
        formatted_list.append({
            "id": vid,
            "label": label,
            "sort_key": (sort_priority, lang, region, gender, name)
        })

    # Sort based on the composite key
    formatted_list.sort(key=lambda x: x["sort_key"])
    
    return formatted_list

# Helper to validate IDs
VALID_VOICE_IDS = [v["id"] for v in get_formatted_voice_list()]