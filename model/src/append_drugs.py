"""
Append additional real Philippine drugs to the existing database.
Reads data/ph_drug_database.jsonl and writes an expanded version.
Uses PHP as currency code to avoid encoding issues; post-processing can replace with peso sign.
"""

import json
import os

NEW_OTC_DRUGS = [
    {
        "drug_id": "PH-OTC-021", "generic_name": "Acetylcysteine",
        "drug_class": "Mucolytic", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Fluimucil", "manufacturer": "Zambon", "form": "200mg sachet / 600mg effervescent"},
            {"brand": "Acetylcysteine Generic", "manufacturer": "Various", "form": "200mg sachet"}
        ],
        "ph_price_estimates": {"generic_per_sachet": "PHP 15.00 - PHP 30.00", "branded_per_sachet": "PHP 35.00 - PHP 60.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["thick mucus", "bronchitis", "COPD"],
        "dosage_adult": "200 mg 2-3 times daily (as mucolytic).",
        "dosage_pediatric": "As directed by pediatrician.",
        "intake_instructions": "Dissolve effervescent tablet in water. Drink immediately after mixing.",
        "onset_of_action": "30 minutes",
        "side_effects_common": ["nausea", "stomach upset", "mouth sores", "skin rash"],
        "side_effects_serious": ["severe allergic reaction", "bronchospasm (rare in asthmatics)"],
        "contraindications": ["hypersensitivity to acetylcysteine"],
        "drug_interactions": ["nitroglycerin (may cause hypotension and headache)"],
        "overdose_note": "Overdose may cause severe GI upset. Seek medical advice.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category B - consult OB-GYN",
        "full_text": "Acetylcysteine (Fluimucil) is an OTC mucolytic for thick mucus and bronchitis."
    },
    {
        "drug_id": "PH-OTC-022", "generic_name": "Bisacodyl",
        "drug_class": "Laxative (stimulant)", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Dulcolax", "manufacturer": "Sanofi", "form": "5mg tablet"},
            {"brand": "Bisacodyl Generic", "manufacturer": "Various", "form": "5mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 3.00 - PHP 8.00", "branded_per_tablet": "PHP 10.00 - PHP 18.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["constipation", "bowel preparation before procedures"],
        "dosage_adult": "5-10 mg once daily at bedtime.",
        "dosage_pediatric": "Consult pediatrician. Children 4-10 years: 5 mg at bedtime.",
        "intake_instructions": "Swallow whole with water. Do not take with milk or antacids.",
        "onset_of_action": "6-12 hours",
        "side_effects_common": ["stomach cramps", "diarrhea", "nausea"],
        "side_effects_serious": ["severe dehydration", "electrolyte imbalance"],
        "contraindications": ["intestinal obstruction", "acute abdominal conditions", "severe dehydration"],
        "drug_interactions": ["antacids (enteric coating may dissolve early)", "diuretics"],
        "overdose_note": "Overdose may cause severe diarrhea and electrolyte loss. Seek medical advice.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Bisacodyl (Dulcolax) is an OTC stimulant laxative for constipation."
    },
    {
        "drug_id": "PH-OTC-023", "generic_name": "Simethicone",
        "drug_class": "Antiflatulent", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Mylicon", "manufacturer": "J&J", "form": "40mg chewable tablet / drops"},
            {"brand": "Simethicone Generic", "manufacturer": "Various", "form": "40mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 3.00 - PHP 6.00", "branded_per_tablet": "PHP 8.00 - PHP 15.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["gas", "bloating", "abdominal discomfort"],
        "dosage_adult": "40-125 mg after meals and at bedtime.",
        "dosage_pediatric": "Infants: 20 mg drops as directed.",
        "intake_instructions": "Chew tablets thoroughly before swallowing.",
        "onset_of_action": "Minutes",
        "side_effects_common": ["none typically"],
        "side_effects_serious": ["allergic reaction (rare)"],
        "contraindications": ["hypersensitivity to simethicone"],
        "drug_interactions": ["none significant"],
        "overdose_note": "Overdose is generally harmless. Seek medical advice if concerned.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Simethicone (Mylicon) is an OTC antiflatulent for gas and bloating."
    },
    {
        "drug_id": "PH-OTC-024", "generic_name": "Miconazole (topical)",
        "drug_class": "Antifungal (topical)", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Micozole", "manufacturer": "Unilab", "form": "2% cream"},
            {"brand": "Daktarin", "manufacturer": "J&J", "form": "2% cream / powder"},
            {"brand": "Miconazole Generic", "manufacturer": "Various", "form": "2% cream"}
        ],
        "ph_price_estimates": {"generic_per_tube": "PHP 50.00 - PHP 100.00", "branded_per_tube": "PHP 120.00 - PHP 200.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["athlete's foot", "jock itch", "ringworm", "oral thrush (gel)"],
        "dosage_adult": "Apply to affected area 2 times daily for 2-4 weeks.",
        "dosage_pediatric": "Consult pediatrician.",
        "intake_instructions": "Clean and dry area before applying. Continue 1-2 weeks after symptoms clear.",
        "onset_of_action": "Few days",
        "side_effects_common": ["local irritation", "burning", "redness"],
        "side_effects_serious": ["severe allergic reaction (rare)"],
        "contraindications": ["hypersensitivity to miconazole"],
        "drug_interactions": ["warfarin (rare systemic absorption interaction)"],
        "overdose_note": "Topical overdose is unlikely. Seek medical advice if large amounts ingested.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Miconazole (Micozole, Daktarin) is an OTC topical antifungal for athlete's foot and ringworm."
    },
    {
        "drug_id": "PH-OTC-025", "generic_name": "Chlorhexidine Gluconate",
        "drug_class": "Antiseptic (topical/oral)", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Bactidol", "manufacturer": "Unilab", "form": "oral rinse / gargle"},
            {"brand": "Chlorhexidine Generic", "manufacturer": "Various", "form": "solution"}
        ],
        "ph_price_estimates": {"generic_per_bottle": "PHP 60.00 - PHP 120.00", "branded_per_bottle": "PHP 120.00 - PHP 250.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["oral hygiene", "mouth sores", "preoperative skin disinfection", "wound cleansing"],
        "dosage_adult": "Gargle 15 mL for 30 seconds twice daily.",
        "dosage_pediatric": "Consult pediatrician before use in children.",
        "intake_instructions": "Do not swallow. Avoid eating or drinking for 30 minutes after use.",
        "onset_of_action": "Immediate (antiseptic effect)",
        "side_effects_common": ["temporary taste disturbance", "tooth staining (with prolonged use)", "mouth irritation"],
        "side_effects_serious": ["severe allergic reaction (rare)"],
        "contraindications": ["hypersensitivity to chlorhexidine"],
        "drug_interactions": ["none significant"],
        "overdose_note": "Ingestion may cause GI upset. Seek medical advice if swallowed in large amounts.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category B - consult OB-GYN",
        "full_text": "Chlorhexidine (Bactidol) is an OTC antiseptic oral rinse for mouth hygiene and sore throat gargle."
    },
    {
        "drug_id": "PH-OTC-026", "generic_name": "Benzoyl Peroxide",
        "drug_class": "Antiacne (topical)", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "PanOxyl", "manufacturer": "GSK", "form": "5% / 10% gel"},
            {"brand": "Benzoyl Peroxide Generic", "manufacturer": "Various", "form": "5% gel"}
        ],
        "ph_price_estimates": {"generic_per_tube": "PHP 80.00 - PHP 150.00", "branded_per_tube": "PHP 200.00 - PHP 350.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["mild to moderate acne", "pimples", "blackheads"],
        "dosage_adult": "Apply thin layer to affected areas once or twice daily.",
        "dosage_pediatric": "Consult pediatrician for children under 12.",
        "intake_instructions": "For external use only. Avoid contact with eyes and mouth. May bleach fabrics.",
        "onset_of_action": "4-6 weeks for noticeable improvement",
        "side_effects_common": ["skin dryness", "peeling", "redness", "burning sensation"],
        "side_effects_serious": ["severe allergic reaction (rare)", "excessive skin irritation"],
        "contraindications": ["hypersensitivity to benzoyl peroxide"],
        "drug_interactions": ["tretinoin (may increase irritation)", "other topical acne products"],
        "overdose_note": "Topical overdose increases skin irritation. Do not apply to large areas.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Benzoyl Peroxide (PanOxyl) is an OTC topical antiacne gel for pimples and blackheads."
    },
    {
        "drug_id": "PH-OTC-027", "generic_name": "Calamine",
        "drug_class": "Topical Anti-itch / Astringent", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Calamine Lotion Generic", "manufacturer": "Various", "form": "lotion"},
            {"brand": "Caladryl", "manufacturer": "Pfizer", "form": "lotion"}
        ],
        "ph_price_estimates": {"generic_per_bottle": "PHP 40.00 - PHP 80.00", "branded_per_bottle": "PHP 100.00 - PHP 180.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["itchy skin", "mild sunburn", "insect bites", "chickenpox"],
        "dosage_adult": "Apply to affected area as needed.",
        "dosage_pediatric": "Consult pediatrician.",
        "intake_instructions": "Shake well before use. For external use only.",
        "onset_of_action": "Immediate cooling relief",
        "side_effects_common": ["skin dryness", "mild stinging"],
        "side_effects_serious": ["severe allergic reaction (rare)"],
        "contraindications": ["hypersensitivity to calamine or zinc oxide"],
        "drug_interactions": ["none significant"],
        "overdose_note": "Topical overdose is unlikely. Avoid applying to open wounds.",
        "storage": "Store below 30C. Shake well before use.",
        "pregnancy_category": "Category A - generally safe",
        "full_text": "Calamine lotion is an OTC topical anti-itch and astringent for insect bites, sunburn, and mild rashes."
    },
    {
        "drug_id": "PH-OTC-028", "generic_name": "Mebendazole",
        "drug_class": "Anthelmintic", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Antiox", "manufacturer": "Unilab", "form": "500mg chewable tablet / suspension"},
            {"brand": "Mebendazole Generic", "manufacturer": "Various", "form": "500mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 15.00 - PHP 30.00", "branded_per_tablet": "PHP 35.00 - PHP 60.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["pinworm", "roundworm", "hookworm", "whipworm infections"],
        "dosage_adult": "500 mg as a single dose. May repeat after 2 weeks if needed.",
        "dosage_pediatric": "Same as adult for children over 2 years. Consult pediatrician for younger children.",
        "intake_instructions": "Chew tablet thoroughly. Can be taken with or without food.",
        "onset_of_action": "24-48 hours",
        "side_effects_common": ["stomach pain", "diarrhea", "nausea"],
        "side_effects_serious": ["severe allergic reaction", "bone marrow suppression (rare with prolonged use)"],
        "contraindications": ["pregnancy (especially first trimester)", "hypersensitivity to mebendazole"],
        "drug_interactions": ["cimetidine (may increase levels)", "carbamazepine", "phenytoin"],
        "overdose_note": "Overdose may cause severe abdominal pain and diarrhea. Seek medical advice.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - contraindicated in first trimester; consult OB-GYN",
        "full_text": "Mebendazole (Antiox) is an OTC anthelmintic for pinworm and roundworm infections."
    },
    {
        "drug_id": "PH-OTC-029", "generic_name": "Zinc Oxide (topical)",
        "drug_class": "Topical Skin Protectant", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Desitin", "manufacturer": "J&J", "form": "cream / ointment"},
            {"brand": "Calmoseptine", "manufacturer": "Calmoseptine Inc.", "form": "ointment"},
            {"brand": "Zinc Oxide Generic", "manufacturer": "Various", "form": "ointment"}
        ],
        "ph_price_estimates": {"generic_per_tube": "PHP 40.00 - PHP 80.00", "branded_per_tube": "PHP 120.00 - PHP 250.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["diaper rash", "minor skin irritations", "sunburn", "chapped skin"],
        "dosage_adult": "Apply to affected area as needed.",
        "dosage_pediatric": "Apply thin layer to diaper area with every diaper change.",
        "intake_instructions": "For external use only. Clean and dry skin before application.",
        "onset_of_action": "Immediate protective barrier",
        "side_effects_common": ["none typically"],
        "side_effects_serious": ["allergic reaction (rare)"],
        "contraindications": ["hypersensitivity to zinc oxide"],
        "drug_interactions": ["none significant"],
        "overdose_note": "Topical overdose is harmless. Do not ingest.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category A - safe",
        "full_text": "Zinc Oxide (Desitin, Calmoseptine) is an OTC topical protectant for diaper rash and minor skin irritations."
    },
    {
        "drug_id": "PH-OTC-030", "generic_name": "Sodium Chloride Nasal Spray",
        "drug_class": "Nasal Decongestant / Cleanser", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Nasaline", "manufacturer": "Various", "form": "nasal spray"},
            {"brand": "Saline Nasal Spray Generic", "manufacturer": "Various", "form": "nasal spray"}
        ],
        "ph_price_estimates": {"generic_per_bottle": "PHP 80.00 - PHP 150.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["nasal congestion", "dry nasal passages", "sinus rinsing", "allergy relief"],
        "dosage_adult": "1-2 sprays into each nostril as needed.",
        "dosage_pediatric": "Consult pediatrician for infants.",
        "intake_instructions": "Tilt head slightly forward. Spray gently into nostril while breathing in.",
        "onset_of_action": "Immediate relief",
        "side_effects_common": ["mild nasal stinging", "sneezing"],
        "side_effects_serious": ["none typically"],
        "contraindications": ["none significant"],
        "drug_interactions": ["none significant"],
        "overdose_note": "Overuse is harmless. Do not share bottle to avoid contamination.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category A - safe",
        "full_text": "Sodium Chloride Nasal Spray (Nasaline) is an OTC saline nasal decongestant and cleanser for dry or congested nasal passages."
    },
    {
        "drug_id": "PH-OTC-031", "generic_name": "Paracetamol + Caffeine",
        "drug_class": "Analgesic / Antipyretic (combination)", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Bioflu", "manufacturer": "Unilab", "form": "tablet"},
            {"brand": "Neozep Forte", "manufacturer": "Unilab", "form": "tablet"},
            {"brand": "Paracetamol + Caffeine Generic", "manufacturer": "Various", "form": "tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 4.00 - PHP 8.00", "branded_per_tablet": "PHP 8.00 - PHP 15.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["headache", "migraine", "fever", "body pain"],
        "dosage_adult": "1 tablet every 6 hours as needed. Maximum: 4 tablets/day.",
        "dosage_pediatric": "Not recommended for children under 12.",
        "intake_instructions": "Take with food. Avoid other caffeine sources.",
        "onset_of_action": "30 minutes",
        "side_effects_common": ["nervousness", "insomnia", "stomach upset"],
        "side_effects_serious": ["liver damage (at high doses)", "severe allergic reaction"],
        "contraindications": ["severe liver disease", "hypersensitivity to paracetamol or caffeine"],
        "drug_interactions": ["warfarin", "other caffeine products", "MAOIs"],
        "overdose_note": "Overdose may cause severe liver damage and caffeine toxicity. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Paracetamol + Caffeine (Bioflu, Neozep Forte) is an OTC combination analgesic for headache and migraine."
    },
    {
        "drug_id": "PH-OTC-032", "generic_name": "Iron Supplements (Ferrous Sulfate)",
        "drug_class": "Mineral Supplement", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Sangobion", "manufacturer": "Merk", "form": "capsule"},
            {"brand": "Ferose", "manufacturer": "Unilab", "form": "tablet"},
            {"brand": "Ferrous Sulfate Generic", "manufacturer": "Various", "form": "tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 3.00 - PHP 8.00", "branded_per_tablet": "PHP 10.00 - PHP 20.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["iron deficiency anemia", "fatigue", "pallor", "weakness"],
        "dosage_adult": "1 tablet daily or as directed by physician.",
        "dosage_pediatric": "As directed by pediatrician.",
        "intake_instructions": "Take with vitamin C (e.g., orange juice) for better absorption. Avoid tea, coffee, or milk within 2 hours.",
        "onset_of_action": "2-4 weeks (hemoglobin rise)",
        "side_effects_common": ["constipation", "dark stools", "stomach upset", "nausea"],
        "side_effects_serious": ["severe allergic reaction (rare)", "iron overload"],
        "contraindications": ["hemochromatosis", "hemosiderosis", "thalassemia"],
        "drug_interactions": ["antacids", "levothyroxine", "certain antibiotics"],
        "overdose_note": "Overdose is dangerous in children. Keep ALL iron supplements away from children. Seek emergency care if child ingests tablets.",
        "storage": "Store below 30C. Keep out of reach of children.",
        "pregnancy_category": "Category A - safe within recommended doses",
        "full_text": "Iron supplements (Sangobion, Ferose) are OTC mineral supplements for iron deficiency anemia."
    },
    {
        "drug_id": "PH-OTC-033", "generic_name": "Folic Acid",
        "drug_class": "Vitamin Supplement", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Folvite", "manufacturer": "Various", "form": "tablet"},
            {"brand": "Folic Acid Generic", "manufacturer": "Various", "form": "400mcg / 5mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 2.00 - PHP 5.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["folate deficiency", "pregnancy supplementation", "anemia"],
        "dosage_adult": "400-800 mcg daily; 5 mg daily for deficiency.",
        "dosage_pediatric": "As directed by pediatrician.",
        "intake_instructions": "May be taken with or without food.",
        "onset_of_action": "N/A (nutritional supplement)",
        "side_effects_common": ["none typically"],
        "side_effects_serious": ["allergic reaction (rare)"],
        "contraindications": ["vitamin B12 deficiency without correction (may mask anemia)"],
        "drug_interactions": ["methotrexate", "phenytoin", "sulfasalazine"],
        "overdose_note": "Overdose is generally harmless. Seek medical advice if concerned.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category A - essential in pregnancy",
        "full_text": "Folic Acid is an OTC vitamin supplement essential for pregnancy and folate deficiency anemia."
    },
    {
        "drug_id": "PH-OTC-034", "generic_name": "Vitamin B Complex",
        "drug_class": "Vitamin Supplement", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Neurobion", "manufacturer": "Merk", "form": "tablet"},
            {"brand": "Neurogen-E", "manufacturer": "Unilab", "form": "tablet"},
            {"brand": "Vitamin B Complex Generic", "manufacturer": "Various", "form": "tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 3.00 - PHP 8.00", "branded_per_tablet": "PHP 15.00 - PHP 30.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["nerve pain", "neuropathy", "fatigue", "poor appetite", "mouth sores"],
        "dosage_adult": "1 tablet daily.",
        "dosage_pediatric": "As directed by pediatrician.",
        "intake_instructions": "Take after meals.",
        "onset_of_action": "N/A (nutritional supplement)",
        "side_effects_common": ["bright yellow urine (from B2)", "mild stomach upset"],
        "side_effects_serious": ["allergic reaction (rare)"],
        "contraindications": ["hypersensitivity to any B vitamin component"],
        "drug_interactions": ["levodopa (B6 may reduce effect)"],
        "overdose_note": "Overdose is generally harmless. Seek medical advice if concerned.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category A - safe",
        "full_text": "Vitamin B Complex (Neurobion, Neurogen-E) is an OTC vitamin supplement for nerve health and fatigue."
    },
    {
        "drug_id": "PH-OTC-035", "generic_name": "Hydrocortisone + Miconazole (topical)",
        "drug_class": "Corticosteroid + Antifungal (combination)", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Daktacort", "manufacturer": "J&J", "form": "cream"},
            {"brand": "Hydrocortisone + Miconazole Generic", "manufacturer": "Various", "form": "cream"}
        ],
        "ph_price_estimates": {"generic_per_tube": "PHP 80.00 - PHP 150.00", "branded_per_tube": "PHP 200.00 - PHP 350.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["fungal skin infections with inflammation", "athlete's foot with redness", "jock itch"],
        "dosage_adult": "Apply thin layer to affected area twice daily for 2-4 weeks.",
        "dosage_pediatric": "Consult pediatrician before use on children.",
        "intake_instructions": "For external use only. Clean and dry area before applying.",
        "onset_of_action": "Few days for symptom relief",
        "side_effects_common": ["local irritation", "burning", "skin thinning (with prolonged use)"],
        "side_effects_serious": ["severe allergic reaction (rare)", "systemic steroid effects (with excessive use)"],
        "contraindications": ["hypersensitivity to hydrocortisone or miconazole", "bacterial or viral skin infections"],
        "drug_interactions": ["other topical medications"],
        "overdose_note": "Topical overdose increases skin thinning and systemic absorption. Do not apply to large areas.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Hydrocortisone + Miconazole cream (Daktacort) is an OTC topical combination for fungal skin infections with inflammation."
    },
    {
        "drug_id": "PH-OTC-036", "generic_name": "Permethrin (topical)",
        "drug_class": "Antiparasitic (topical)", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Elimite", "manufacturer": "Various", "form": "5% cream / lotion"},
            {"brand": "Permethrin Generic", "manufacturer": "Various", "form": "5% cream"}
        ],
        "ph_price_estimates": {"generic_per_bottle": "PHP 80.00 - PHP 150.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["scabies", "head lice", "body lice"],
        "dosage_adult": "Apply to entire body from neck down. Leave for 8-14 hours, then wash off. Repeat after 7 days if needed.",
        "dosage_pediatric": "Consult pediatrician for infants under 2 months.",
        "intake_instructions": "For external use only. Avoid eyes, mouth, and broken skin. Wash bedding and clothing after treatment.",
        "onset_of_action": "24-48 hours",
        "side_effects_common": ["mild burning or stinging", "skin redness", "itching"],
        "side_effects_serious": ["severe allergic reaction (rare)"],
        "contraindications": ["hypersensitivity to permethrin", "infants under 2 months"],
        "drug_interactions": ["none significant"],
        "overdose_note": "Topical overdose increases skin irritation. Do not swallow.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category B - consult OB-GYN",
        "full_text": "Permethrin (Elimite) is an OTC topical antiparasitic for scabies and lice."
    },
    {
        "drug_id": "PH-OTC-037", "generic_name": "Chloramphenicol (eye drops)",
        "drug_class": "Antibiotic (ophthalmic)", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Chloramex", "manufacturer": "Various", "form": "0.5% eye drops"},
            {"brand": "Chloramphenicol Eye Drops Generic", "manufacturer": "Various", "form": "0.5% eye drops"}
        ],
        "ph_price_estimates": {"generic_per_bottle": "PHP 50.00 - PHP 100.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["bacterial conjunctivitis", "eye infection", "sore eyes"],
        "dosage_adult": "1-2 drops into affected eye every 4-6 hours.",
        "dosage_pediatric": "As directed by pediatrician.",
        "intake_instructions": "For ophthalmic use only. Do not touch dropper tip to eye.",
        "onset_of_action": "24-48 hours",
        "side_effects_common": ["temporary stinging", "blurred vision after application"],
        "side_effects_serious": ["severe allergic reaction", "bone marrow suppression (rare with prolonged use)"],
        "contraindications": ["hypersensitivity to chloramphenicol"],
        "drug_interactions": ["none significant"],
        "overdose_note": "Overdose is unlikely with eye drops. Seek medical advice if swallowed.",
        "storage": "Store below 25C. Do not freeze.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Chloramphenicol eye drops (Chloramex) are an OTC ophthalmic antibiotic for bacterial conjunctivitis."
    },
    {
        "drug_id": "PH-OTC-038", "generic_name": "Carboxymethylcellulose (eye drops)",
        "drug_class": "Artificial Tears / Lubricant", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Refresh Tears", "manufacturer": "Allergan", "form": "eye drops"},
            {"brand": "Systane", "manufacturer": "Alcon", "form": "eye drops"},
            {"brand": "Carboxymethylcellulose Generic", "manufacturer": "Various", "form": "eye drops"}
        ],
        "ph_price_estimates": {"generic_per_bottle": "PHP 80.00 - PHP 150.00", "branded_per_bottle": "PHP 200.00 - PHP 400.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["dry eyes", "eye irritation", "computer vision syndrome"],
        "dosage_adult": "1-2 drops into each eye as needed.",
        "dosage_pediatric": "As directed by pediatrician.",
        "intake_instructions": "For ophthalmic use only. Do not touch dropper tip to eye.",
        "onset_of_action": "Immediate relief",
        "side_effects_common": ["temporary blurred vision", "mild stinging"],
        "side_effects_serious": ["severe allergic reaction (rare)"],
        "contraindications": ["hypersensitivity to carboxymethylcellulose"],
        "drug_interactions": ["none significant"],
        "overdose_note": "Overdose is harmless. Do not swallow.",
        "storage": "Store below 30C. Discard 1 month after opening.",
        "pregnancy_category": "Category A - safe",
        "full_text": "Carboxymethylcellulose eye drops (Refresh Tears, Systane) are OTC artificial tears for dry eyes."
    },
    {
        "drug_id": "PH-OTC-039", "generic_name": "Lactulose",
        "drug_class": "Osmotic Laxative", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Duphalac", "manufacturer": "Abbott", "form": "syrup"},
            {"brand": "Lactulose Generic", "manufacturer": "Various", "form": "syrup"}
        ],
        "ph_price_estimates": {"generic_per_bottle": "PHP 150.00 - PHP 250.00", "branded_per_bottle": "PHP 300.00 - PHP 450.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["constipation", "hepatic encephalopathy"],
        "dosage_adult": "15-30 mL daily. Adjust dose based on response.",
        "dosage_pediatric": "As directed by pediatrician.",
        "intake_instructions": "May be taken with or without food. Drink plenty of water.",
        "onset_of_action": "24-48 hours",
        "side_effects_common": ["bloating", "gas", "abdominal cramps", "diarrhea"],
        "side_effects_serious": ["severe dehydration (with excessive doses)", "electrolyte imbalance"],
        "contraindications": ["galactosemia", "intestinal obstruction"],
        "drug_interactions": ["antacids", "other laxatives"],
        "overdose_note": "Overdose causes severe diarrhea and electrolyte imbalance. Seek medical advice.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category B - consult OB-GYN",
        "full_text": "Lactulose (Duphalac) is an OTC osmotic laxative for constipation."
    },
    {
        "drug_id": "PH-OTC-040", "generic_name": "Sucralfate",
        "drug_class": "Gastroprotective Agent", "rx_status": "OTC", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Carafate", "manufacturer": "Various", "form": "1g tablet / suspension"},
            {"brand": "Sucralfate Generic", "manufacturer": "Various", "form": "1g tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 15.00 - PHP 30.00", "branded_per_tablet": "PHP 40.00 - PHP 70.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["gastric ulcer", "duodenal ulcer", "GERD"],
        "dosage_adult": "1 g 4 times daily (1 hour before meals and at bedtime).",
        "dosage_pediatric": "As directed by pediatrician.",
        "intake_instructions": "Take 1 hour before meals and at bedtime. Do not take within 30 minutes of antacids.",
        "onset_of_action": "1-2 hours",
        "side_effects_common": ["constipation", "dry mouth", "nausea"],
        "side_effects_serious": ["severe allergic reaction (rare)"],
        "contraindications": ["hypersensitivity to sucralfate"],
        "drug_interactions": ["antacids", "cimetidine", "digoxin", "fluoroquinolones"],
        "overdose_note": "Overdose may cause constipation. Seek medical advice.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category B - consult OB-GYN",
        "full_text": "Sucralfate (Carafate) is an OTC gastroprotective agent for gastric and duodenal ulcers."
    },
]

NEW_RX_DRUGS = [
    {
        "drug_id": "PH-RX-021", "generic_name": "Clarithromycin",
        "drug_class": "Macrolide Antibiotic", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Klacid", "manufacturer": "Abbott", "form": "500mg tablet / suspension"},
            {"brand": "Clarithromycin Generic", "manufacturer": "Various", "form": "500mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 25.00 - PHP 45.00", "branded_per_tablet": "PHP 70.00 - PHP 130.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["respiratory infections", "skin infections", "H. pylori eradication (in combination)", "atypical mycobacterial infections"],
        "dosage_adult": "As prescribed by physician. Typical: 500 mg every 12 hours.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take with food to reduce stomach upset. Do not refrigerate suspension.",
        "onset_of_action": "1-2 hours",
        "side_effects_common": ["nausea", "diarrhea", "stomach pain", "altered taste"],
        "side_effects_serious": ["liver damage", "severe allergic reaction", "QT prolongation", "C. difficile colitis"],
        "contraindications": ["hypersensitivity to clarithromycin or other macrolides", "severe liver disease", "history of QT prolongation"],
        "drug_interactions": ["statins", "warfarin", "theophylline", "carbamazepine", "colchicine"],
        "overdose_note": "Overdose may cause severe GI symptoms and cardiac arrhythmias. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN; avoid in first trimester if possible",
        "full_text": "Clarithromycin (Klacid) is a prescription macrolide antibiotic. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-022", "generic_name": "Cefuroxime",
        "drug_class": "Cephalosporin Antibiotic", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Zinnat", "manufacturer": "GSK", "form": "250mg / 500mg tablet"},
            {"brand": "Cefuroxime Generic", "manufacturer": "Various", "form": "500mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 25.00 - PHP 45.00", "branded_per_tablet": "PHP 70.00 - PHP 130.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["respiratory infections", "sinusitis", "UTIs", "skin infections", "Lyme disease"],
        "dosage_adult": "As prescribed by physician. Typical: 250-500 mg every 12 hours.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take with food to improve absorption. Complete full course.",
        "onset_of_action": "1-2 hours",
        "side_effects_common": ["diarrhea", "nausea", "vomiting", "headache"],
        "side_effects_serious": ["severe allergic reaction", "C. difficile colitis", "seizures (rare)"],
        "contraindications": ["cephalosporin allergy"],
        "drug_interactions": ["probenecid", "oral contraceptives (may reduce efficacy)", "antacids"],
        "overdose_note": "Overdose may cause nausea and seizures. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category B - consult OB-GYN",
        "full_text": "Cefuroxime (Zinnat) is a prescription cephalosporin antibiotic. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-023", "generic_name": "Cotrimoxazole",
        "drug_class": "Sulfonamide Antibiotic", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Bactrim", "manufacturer": "Roche", "form": "400/80mg tablet / suspension"},
            {"brand": "Cotrimoxazole Generic", "manufacturer": "Various", "form": "tablet / suspension"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 8.00 - PHP 18.00", "branded_per_tablet": "PHP 25.00 - PHP 50.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["UTIs", "respiratory infections", "traveler's diarrhea", "Pneumocystis pneumonia (PCP)", "toxoplasmosis prophylaxis"],
        "dosage_adult": "As prescribed by physician. Typical: 1 tablet every 12 hours.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take with food and plenty of water to reduce stomach upset.",
        "onset_of_action": "1-4 hours",
        "side_effects_common": ["nausea", "vomiting", "diarrhea", "skin rash", "photosensitivity"],
        "side_effects_serious": ["Stevens-Johnson syndrome", "agranulocytosis", "severe allergic reaction", "hyperkalemia"],
        "contraindications": ["sulfonamide allergy", "severe liver or kidney disease", "megaloblastic anemia due to folate deficiency", "pregnancy near term"],
        "drug_interactions": ["warfarin", "phenytoin", "methotrexate", "ACE inhibitors", "ARBs"],
        "overdose_note": "Overdose may cause nausea, vomiting, and bone marrow suppression. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category D - contraindicated near term; consult OB-GYN",
        "full_text": "Cotrimoxazole (Bactrim) is a prescription sulfonamide antibiotic. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-024", "generic_name": "Fluconazole",
        "drug_class": "Antifungal (systemic)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Diflucan", "manufacturer": "Pfizer", "form": "150mg capsule / IV"},
            {"brand": "Fluconazole Generic", "manufacturer": "Various", "form": "150mg capsule"}
        ],
        "ph_price_estimates": {"generic_per_capsule": "PHP 50.00 - PHP 90.00", "branded_per_capsule": "PHP 150.00 - PHP 280.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["vaginal yeast infection", "oral thrush", "systemic candidiasis", "cryptococcal meningitis (in combination)", "fungal nail infections"],
        "dosage_adult": "As prescribed by physician. Typical for vaginal yeast: 150 mg single dose.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "May be taken with or without food.",
        "onset_of_action": "24 hours (symptom relief); full clearance may take days to weeks",
        "side_effects_common": ["nausea", "headache", "stomach pain", "skin rash"],
        "side_effects_serious": ["severe liver damage", "QT prolongation", "severe allergic reaction"],
        "contraindications": ["hypersensitivity to fluconazole", "concurrent use with cisapride", "pregnancy (high-dose or long-term)"],
        "drug_interactions": ["warfarin", "phenytoin", "statins", "cyclosporine", "oral contraceptives"],
        "overdose_note": "Overdose may cause hallucinations and severe liver damage. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN; high-dose contraindicated in pregnancy",
        "full_text": "Fluconazole (Diflucan) is a prescription systemic antifungal. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-025", "generic_name": "Sertraline",
        "drug_class": "Selective Serotonin Reuptake Inhibitor (SSRI)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Zoloft", "manufacturer": "Pfizer", "form": "50mg / 100mg tablet"},
            {"brand": "Sertraline Generic", "manufacturer": "Various", "form": "50mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 15.00 - PHP 30.00", "branded_per_tablet": "PHP 50.00 - PHP 100.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["major depressive disorder", "generalized anxiety disorder", "panic disorder", "OCD", "PTSD", "social anxiety disorder"],
        "dosage_adult": "As prescribed by physician. Typical starting: 50 mg once daily.",
        "dosage_pediatric": "As prescribed by pediatric psychiatrist.",
        "intake_instructions": "Take with or without food, preferably in the morning. Do not stop abruptly.",
        "onset_of_action": "2-4 weeks for clinical effect",
        "side_effects_common": ["nausea", "diarrhea", "insomnia", "drowsiness", "sexual dysfunction", "dry mouth"],
        "side_effects_serious": ["serotonin syndrome", "suicidal thoughts (young adults)", "hyponatremia", "severe allergic reaction"],
        "contraindications": ["MAOI use within 14 days", "pimozide", "hypersensitivity to sertraline"],
        "drug_interactions": ["MAOIs", "tramadol", "other SSRIs/SNRIs", "warfarin", "pimozide"],
        "overdose_note": "Overdose may cause severe serotonin syndrome, seizures, and cardiac arrhythmias. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN; risk in third trimester",
        "full_text": "Sertraline (Zoloft) is a prescription SSRI antidepressant. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-026", "generic_name": "Escitalopram",
        "drug_class": "Selective Serotonin Reuptake Inhibitor (SSRI)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Lexapro", "manufacturer": "Lundbeck", "form": "10mg / 20mg tablet"},
            {"brand": "Escitalopram Generic", "manufacturer": "Various", "form": "10mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 15.00 - PHP 30.00", "branded_per_tablet": "PHP 50.00 - PHP 100.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["major depressive disorder", "generalized anxiety disorder"],
        "dosage_adult": "As prescribed by physician. Typical starting: 10 mg once daily.",
        "dosage_pediatric": "As prescribed by pediatric psychiatrist.",
        "intake_instructions": "Take with or without food, at the same time each day. Do not stop abruptly.",
        "onset_of_action": "1-2 weeks for initial improvement; 4-6 weeks for full effect",
        "side_effects_common": ["nausea", "headache", "insomnia", "fatigue", "sexual dysfunction"],
        "side_effects_serious": ["serotonin syndrome", "suicidal thoughts (young adults)", "hyponatremia", "severe allergic reaction"],
        "contraindications": ["MAOI use within 14 days", "pimozide", "hypersensitivity to escitalopram"],
        "drug_interactions": ["MAOIs", "tramadol", "other SSRIs/SNRIs", "warfarin", "NSAIDs (bleeding risk)"],
        "overdose_note": "Overdose may cause severe serotonin syndrome and seizures. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Escitalopram (Lexapro) is a prescription SSRI for depression and anxiety. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-027", "generic_name": "Lorazepam",
        "drug_class": "Benzodiazepine (Controlled Substance)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Ativan", "manufacturer": "Pfizer", "form": "1mg / 2mg tablet"},
            {"brand": "Lorazepam Generic", "manufacturer": "Various", "form": "1mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 10.00 - PHP 20.00", "branded_per_tablet": "PHP 30.00 - PHP 60.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["anxiety disorders", "insomnia", "status epilepticus (IV)", "sedation before procedures"],
        "dosage_adult": "As prescribed by physician. Typical: 0.5-2 mg 2-3 times daily for anxiety.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take as directed. Do not stop abruptly due to withdrawal and seizure risk.",
        "onset_of_action": "20-60 minutes",
        "side_effects_common": ["drowsiness", "dizziness", "weakness", "memory problems"],
        "side_effects_serious": ["respiratory depression", "severe confusion", "dependence and withdrawal", "suicidal thoughts"],
        "contraindications": ["acute narrow-angle glaucoma", "severe respiratory insufficiency", "sleep apnea", "hypersensitivity to benzodiazepines"],
        "drug_interactions": ["alcohol", "opioids", "other CNS depressants", "antihistamines"],
        "overdose_note": "Overdose causes severe sedation, respiratory depression, and coma. This is a medical emergency. Call 911.",
        "storage": "Store in a secure place. Controlled substance under RA 9165.",
        "pregnancy_category": "Category D - risk to fetus; consult OB-GYN immediately",
        "full_text": "Lorazepam (Ativan) is a prescription controlled benzodiazepine for anxiety. Strictly regulated under RA 9165."
    },
    {
        "drug_id": "PH-RX-028", "generic_name": "Enalapril",
        "drug_class": "Angiotensin-Converting Enzyme Inhibitor (ACE-I)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Renitec", "manufacturer": "Merck", "form": "5mg / 10mg / 20mg tablet"},
            {"brand": "Enalapril Generic", "manufacturer": "Various", "form": "5mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 5.00 - PHP 12.00", "branded_per_tablet": "PHP 20.00 - PHP 40.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["hypertension", "heart failure", "asymptomatic left ventricular dysfunction"],
        "dosage_adult": "As prescribed by physician. Typical starting: 5 mg once daily.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take at the same time each day. May be taken with or without food.",
        "onset_of_action": "1 hour; 2-4 weeks for full blood pressure control",
        "side_effects_common": ["dry cough", "dizziness", "fatigue", "headache"],
        "side_effects_serious": ["angioedema", "severe hypotension", "acute kidney injury", "hyperkalemia"],
        "contraindications": ["pregnancy (second and third trimesters)", "history of angioedema with ACE inhibitors", "bilateral renal artery stenosis"],
        "drug_interactions": ["potassium supplements", "NSAIDs", "lithium", "diuretics"],
        "overdose_note": "Overdose causes severe hypotension. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category D - contraindicated in 2nd and 3rd trimesters",
        "full_text": "Enalapril (Renitec) is a prescription ACE inhibitor for hypertension and heart failure. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-029", "generic_name": "Valsartan",
        "drug_class": "Angiotensin II Receptor Blocker (ARB)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Diovan", "manufacturer": "Novartis", "form": "80mg / 160mg tablet"},
            {"brand": "Valsartan Generic", "manufacturer": "Various", "form": "80mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 10.00 - PHP 20.00", "branded_per_tablet": "PHP 40.00 - PHP 80.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["hypertension", "heart failure", "post-myocardial infarction"],
        "dosage_adult": "As prescribed by physician. Typical starting: 80 mg once daily.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "May be taken with or without food.",
        "onset_of_action": "2 hours; 2-4 weeks for full effect",
        "side_effects_common": ["dizziness", "fatigue", "headache", "back pain"],
        "side_effects_serious": ["hyperkalemia", "acute kidney injury", "severe hypotension", "angioedema (rare)"],
        "contraindications": ["pregnancy (second and third trimesters)", "bilateral renal artery stenosis", "hypersensitivity to valsartan"],
        "drug_interactions": ["potassium supplements", "NSAIDs", "lithium", "other antihypertensives"],
        "overdose_note": "Overdose causes hypotension and tachycardia. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category D - contraindicated in 2nd and 3rd trimesters",
        "full_text": "Valsartan (Diovan) is a prescription ARB for hypertension and heart failure. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-030", "generic_name": "Hydrochlorothiazide",
        "drug_class": "Thiazide Diuretic", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Esidrix", "manufacturer": "Merck", "form": "25mg tablet"},
            {"brand": "Hydrochlorothiazide Generic", "manufacturer": "Various", "form": "25mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 3.00 - PHP 8.00", "branded_per_tablet": "PHP 12.00 - PHP 25.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["hypertension", "edema", "nephrolithiasis (calcium stones)"],
        "dosage_adult": "As prescribed by physician. Typical: 12.5-25 mg once daily.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take in the morning to avoid nighttime urination. May be taken with or without food.",
        "onset_of_action": "2 hours (diuretic effect); 3-4 days for blood pressure control",
        "side_effects_common": ["frequent urination", "dizziness", "low blood pressure", "electrolyte imbalance"],
        "side_effects_serious": ["severe hyponatremia", "severe hypokalemia", "pancreatitis", "severe allergic reaction"],
        "contraindications": ["anuria", "sulfonamide allergy", "severe kidney disease"],
        "drug_interactions": ["lithium", "digoxin", "NSAIDs", "corticosteroids", "other antihypertensives"],
        "overdose_note": "Overdose causes severe dehydration and electrolyte imbalance. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category B - consult OB-GYN; not recommended for pregnancy-induced hypertension",
        "full_text": "Hydrochlorothiazide (Esidrix) is a prescription thiazide diuretic for hypertension and edema. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-031", "generic_name": "Simvastatin",
        "drug_class": "HMG-CoA Reductase Inhibitor (Statin)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Zocor", "manufacturer": "Merck", "form": "10mg / 20mg / 40mg tablet"},
            {"brand": "Simvastatin Generic", "manufacturer": "Various", "form": "10mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 8.00 - PHP 18.00", "branded_per_tablet": "PHP 30.00 - PHP 70.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["high cholesterol", "dyslipidemia", "cardiovascular disease prevention"],
        "dosage_adult": "As prescribed by physician. Typical starting: 10-20 mg once daily at bedtime.",
        "dosage_pediatric": "As prescribed by pediatrician for familial hypercholesterolemia (adolescents 10-17 years).",
        "intake_instructions": "Take in the evening. May be taken with or without food. Avoid grapefruit juice.",
        "onset_of_action": "2 weeks (cholesterol reduction); 4 weeks for full effect",
        "side_effects_common": ["muscle aches", "headache", "nausea", "constipation"],
        "side_effects_serious": ["rhabdomyolysis", "liver damage", "diabetes risk (long-term)"],
        "contraindications": ["active liver disease", "pregnancy", "breastfeeding", "concurrent use with strong CYP3A4 inhibitors"],
        "drug_interactions": ["erythromycin", "clarithromycin", "grapefruit juice", "other statins", "fibrates", "warfarin"],
        "overdose_note": "Overdose may worsen muscle and liver side effects. Seek medical advice.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category X - contraindicated in pregnancy",
        "full_text": "Simvastatin (Zocor) is a prescription statin for high cholesterol. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-032", "generic_name": "Rosuvastatin",
        "drug_class": "HMG-CoA Reductase Inhibitor (Statin)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Crestor", "manufacturer": "AstraZeneca", "form": "5mg / 10mg / 20mg tablet"},
            {"brand": "Rosuvastatin Generic", "manufacturer": "Various", "form": "10mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 12.00 - PHP 25.00", "branded_per_tablet": "PHP 50.00 - PHP 120.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["high cholesterol", "dyslipidemia", "cardiovascular disease prevention"],
        "dosage_adult": "As prescribed by physician. Typical starting: 5-10 mg once daily.",
        "dosage_pediatric": "As prescribed by pediatrician for familial hypercholesterolemia.",
        "intake_instructions": "Take at any time of day. May be taken with or without food. Avoid grapefruit juice.",
        "onset_of_action": "2 weeks (cholesterol reduction); 4 weeks for full effect",
        "side_effects_common": ["muscle aches", "headache", "nausea", "abdominal pain"],
        "side_effects_serious": ["rhabdomyolysis", "liver damage", "diabetes risk (long-term)"],
        "contraindications": ["active liver disease", "pregnancy", "breastfeeding", "severe kidney disease", "hypersensitivity to rosuvastatin"],
        "drug_interactions": ["cyclosporine", "gemfibrozil", "warfarin", "antacids"],
        "overdose_note": "Overdose may worsen muscle and liver side effects. Seek medical advice.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category X - contraindicated in pregnancy",
        "full_text": "Rosuvastatin (Crestor) is a prescription statin for high cholesterol. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-033", "generic_name": "Gliclazide",
        "drug_class": "Sulfonylurea Antidiabetic", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Diamicron", "manufacturer": "Servier", "form": "80mg tablet"},
            {"brand": "Gliclazide Generic", "manufacturer": "Various", "form": "80mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 8.00 - PHP 18.00", "branded_per_tablet": "PHP 25.00 - PHP 50.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["Type 2 Diabetes Mellitus"],
        "dosage_adult": "As prescribed by physician. Typical starting: 40-80 mg daily with breakfast.",
        "dosage_pediatric": "Not recommended for children.",
        "intake_instructions": "Take with breakfast. Do not skip meals to avoid hypoglycemia.",
        "onset_of_action": "4-6 hours",
        "side_effects_common": ["hypoglycemia", "weight gain", "dizziness", "headache"],
        "side_effects_serious": ["severe hypoglycemia", "hemolytic anemia (in G6PD deficiency)", "allergic reaction"],
        "contraindications": ["Type 1 Diabetes", "diabetic ketoacidosis", "severe kidney or liver disease", "sulfonamide allergy"],
        "drug_interactions": ["alcohol (disulfiram-like reaction and hypoglycemia)", "beta-blockers", "NSAIDs", "warfarin"],
        "overdose_note": "Overdose causes severe hypoglycemia. Consume sugar and seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN; insulin preferred in pregnancy",
        "full_text": "Gliclazide (Diamicron) is a prescription sulfonylurea for Type 2 Diabetes. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-034", "generic_name": "Sitagliptin",
        "drug_class": "Dipeptidyl Peptidase-4 (DPP-4) Inhibitor", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Januvia", "manufacturer": "Merck", "form": "100mg tablet"},
            {"brand": "Sitagliptin Generic", "manufacturer": "Various", "form": "100mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 20.00 - PHP 40.00", "branded_per_tablet": "PHP 80.00 - PHP 150.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["Type 2 Diabetes Mellitus"],
        "dosage_adult": "As prescribed by physician. Typical: 100 mg once daily.",
        "dosage_pediatric": "Not recommended for children.",
        "intake_instructions": "May be taken with or without food.",
        "onset_of_action": "1-4 hours (glucose lowering effect)",
        "side_effects_common": ["upper respiratory infection", "headache", "stomach upset", "nasal congestion"],
        "side_effects_serious": ["pancreatitis", "severe allergic reaction (angioedema, rash)", "kidney problems"],
        "contraindications": ["hypersensitivity to sitagliptin"],
        "drug_interactions": ["insulin", "sulfonylureas (increased hypoglycemia risk)", "certain HIV medications"],
        "overdose_note": "Overdose may cause hypoglycemia. Seek medical advice.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category B - consult OB-GYN",
        "full_text": "Sitagliptin (Januvia) is a prescription DPP-4 inhibitor for Type 2 Diabetes. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-035", "generic_name": "Insulin Glargine",
        "drug_class": "Antidiabetic Hormone (Injectable)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Lantus", "manufacturer": "Sanofi", "form": "100 IU/mL vial / pen"},
            {"brand": "Insulin Glargine Generic", "manufacturer": "Various", "form": "100 IU/mL vial"}
        ],
        "ph_price_estimates": {"generic_per_vial": "PHP 600.00 - PHP 1,000.00", "branded_per_vial": "PHP 1,200.00 - PHP 2,000.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["Type 1 Diabetes", "Type 2 Diabetes (when oral agents insufficient)", "gestational diabetes"],
        "dosage_adult": "As prescribed by physician. Dose is highly individualized based on blood glucose monitoring.",
        "dosage_pediatric": "As prescribed by pediatric endocrinologist.",
        "intake_instructions": "Subcutaneous injection once daily at the same time. Rotate injection sites. Monitor blood sugar regularly.",
        "onset_of_action": "1-2 hours (onset); peakless / flat profile over 24 hours",
        "side_effects_common": ["hypoglycemia", "weight gain", "injection site reactions", "lipodystrophy"],
        "side_effects_serious": ["severe hypoglycemia (unconsciousness, seizures)", "allergic reaction", "hypokalemia"],
        "contraindications": ["hypoglycemia", "hypersensitivity to insulin glargine or excipients"],
        "drug_interactions": ["beta-blockers (mask hypoglycemia symptoms)", "corticosteroids", "thyroid hormones", "alcohol"],
        "overdose_note": "Insulin overdose causes severe hypoglycemia and can be fatal. Consume fast-acting sugar and seek emergency care immediately.",
        "storage": "Unopened: refrigerate 2-8C. Opened vials/pen: room temperature up to 28C for 28 days. Do not freeze.",
        "pregnancy_category": "Category C - consult OB-GYN; insulin is standard in pregnancy",
        "full_text": "Insulin Glargine (Lantus) is a prescription long-acting injectable antidiabetic. Requires a doctor's prescription and injection training."
    },
    {
        "drug_id": "PH-RX-036", "generic_name": "Carbamazepine",
        "drug_class": "Antiepileptic / Mood Stabilizer", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Tegretol", "manufacturer": "Novartis", "form": "200mg tablet / suspension"},
            {"brand": "Carbamazepine Generic", "manufacturer": "Various", "form": "200mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 8.00 - PHP 18.00", "branded_per_tablet": "PHP 25.00 - PHP 50.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["epilepsy", "trigeminal neuralgia", "bipolar disorder"],
        "dosage_adult": "As prescribed by physician. Dose varies; typical starting: 100-200 mg twice daily.",
        "dosage_pediatric": "As prescribed by pediatric neurologist.",
        "intake_instructions": "Take with food to reduce stomach upset. Do not stop abruptly.",
        "onset_of_action": "Days to weeks for mood stabilization; immediate for some seizure types",
        "side_effects_common": ["dizziness", "drowsiness", "nausea", "blurred vision"],
        "side_effects_serious": ["Stevens-Johnson syndrome", "agranulocytosis", "liver damage", "severe allergic reaction"],
        "contraindications": ["bone marrow suppression", "MAOI use within 14 days", "hypersensitivity to carbamazepine"],
        "drug_interactions": ["warfarin", "oral contraceptives (reduces efficacy)", "other antiepileptics", "grapefruit juice", "erythromycin", "clarithromycin"],
        "overdose_note": "Overdose causes severe CNS depression, seizures, and cardiac arrhythmias. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category D - risk of neural tube defects; consult OB-GYN immediately; folic acid supplementation recommended",
        "full_text": "Carbamazepine (Tegretol) is a prescription antiepileptic and mood stabilizer. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-037", "generic_name": "Valproic Acid",
        "drug_class": "Antiepileptic / Mood Stabilizer", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Depakine", "manufacturer": "Sanofi", "form": "200mg / 500mg tablet / syrup"},
            {"brand": "Valproic Acid Generic", "manufacturer": "Various", "form": "500mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 10.00 - PHP 20.00", "branded_per_tablet": "PHP 30.00 - PHP 60.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["epilepsy", "bipolar disorder", "migraine prophylaxis"],
        "dosage_adult": "As prescribed by physician. Typical starting: 250 mg twice daily.",
        "dosage_pediatric": "As prescribed by pediatric neurologist.",
        "intake_instructions": "Take with food to reduce stomach upset. Do not crush extended-release tablets.",
        "onset_of_action": "Days to weeks for mood stabilization",
        "side_effects_common": ["nausea", "stomach upset", "tremor", "weight gain", "hair loss"],
        "side_effects_serious": ["liver damage (especially in children under 2)", "pancreatitis", "thrombocytopenia", "severe allergic reaction"],
        "contraindications": ["pregnancy (unless essential for seizure control)", "liver disease", "urea cycle disorders", "hypersensitivity to valproic acid"],
        "drug_interactions": ["aspirin", "carbapenem antibiotics", "lamotrigine", "warfarin", "other antiepileptics"],
        "overdose_note": "Overdose causes severe CNS depression and cerebral edema. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category X - contraindicated in pregnancy for non-seizure indications; high risk of neural tube defects; consult OB-GYN immediately",
        "full_text": "Valproic Acid (Depakine) is a prescription antiepileptic and mood stabilizer. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-038", "generic_name": "Salmeterol + Fluticasone",
        "drug_class": "Long-Acting Beta-2 Agonist + Inhaled Corticosteroid", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Seretide", "manufacturer": "GSK", "form": "50/250mcg or 50/500mcg Accuhaler / Evohaler"},
            {"brand": "Salmeterol + Fluticasone Generic", "manufacturer": "Various", "form": "inhaler"}
        ],
        "ph_price_estimates": {"generic_per_inhaler": "PHP 400.00 - PHP 700.00", "branded_per_inhaler": "PHP 1,000.00 - PHP 1,800.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["asthma maintenance", "COPD"],
        "dosage_adult": "As prescribed by physician. Typical: 1 puff twice daily.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Rinse mouth after each use to prevent oral thrush. Do not use for acute relief.",
        "onset_of_action": "Days to weeks for full benefit; salmeterol onset ~20 minutes",
        "side_effects_common": ["oral thrush", "hoarseness", "throat irritation", "tremor", "headache"],
        "side_effects_serious": ["pneumonia (in COPD patients)", "adrenal suppression (high doses)", "severe allergic reaction"],
        "contraindications": ["hypersensitivity to salmeterol or fluticasone", "status asthmaticus"],
        "drug_interactions": ["beta-blockers", "ketoconazole", "ritonavir"],
        "overdose_note": "Overdose may cause tremor, tachycardia, and Cushing's syndrome features. Seek emergency care.",
        "storage": "Store below 30C. Keep inhaler away from heat and direct sunlight.",
        "pregnancy_category": "Category C - consult OB-GYN; benefits may outweigh risks in uncontrolled asthma",
        "full_text": "Salmeterol + Fluticasone (Seretide) is a prescription combination inhaler for asthma and COPD maintenance. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-039", "generic_name": "Budesonide",
        "drug_class": "Inhaled Corticosteroid", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Pulmicort", "manufacturer": "AstraZeneca", "form": "200mcg Turbuhaler / nebule"},
            {"brand": "Budesonide Generic", "manufacturer": "Various", "form": "inhaler / nebule"}
        ],
        "ph_price_estimates": {"generic_per_inhaler": "PHP 300.00 - PHP 600.00", "branded_per_inhaler": "PHP 800.00 - PHP 1,500.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["asthma maintenance", "COPD"],
        "dosage_adult": "As prescribed by physician. Typical: 1-2 puffs twice daily.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Rinse mouth after each use to prevent oral thrush. Do not swallow.",
        "onset_of_action": "24 hours (clinical effect); may take 1-2 weeks for full benefit",
        "side_effects_common": ["oral thrush", "hoarseness", "throat irritation", "cough"],
        "side_effects_serious": ["adrenal suppression (high doses)", "pneumonia (in COPD patients)", "severe allergic reaction"],
        "contraindications": ["hypersensitivity to budesonide", "status asthmaticus"],
        "drug_interactions": ["ketoconazole", "ritonavir", "other CYP3A4 inhibitors"],
        "overdose_note": "Overdose may cause Cushing's syndrome features. Seek medical advice.",
        "storage": "Store below 30C. Keep inhaler away from heat and direct sunlight.",
        "pregnancy_category": "Category B - consult OB-GYN; benefits may outweigh risks in uncontrolled asthma",
        "full_text": "Budesonide (Pulmicort) is a prescription inhaled corticosteroid for asthma maintenance. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-040", "generic_name": "Diclofenac",
        "drug_class": "NSAID / Analgesic", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Voltaren", "manufacturer": "Novartis", "form": "50mg tablet / 75mg SR / gel"},
            {"brand": "Diclofenac Generic", "manufacturer": "Various", "form": "50mg tablet / gel"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 5.00 - PHP 12.00", "branded_per_tablet": "PHP 15.00 - PHP 30.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["pain", "inflammation", "arthritis", "dysmenorrhea", "muscle sprains"],
        "dosage_adult": "As prescribed by physician. Typical: 50 mg 2-3 times daily after meals.",
        "dosage_pediatric": "Not recommended for children under 14 years.",
        "intake_instructions": "Take with food to reduce stomach upset. Do not lie down for 30 minutes after taking.",
        "onset_of_action": "30 minutes",
        "side_effects_common": ["stomach upset", "heartburn", "nausea", "dizziness"],
        "side_effects_serious": ["GI bleeding", "kidney damage", "liver damage", "severe allergic reaction"],
        "contraindications": ["peptic ulcer disease", "severe kidney or liver disease", "aspirin-sensitive asthma", "third trimester pregnancy"],
        "drug_interactions": ["aspirin", "warfarin", "other NSAIDs", "methotrexate", "lithium"],
        "overdose_note": "Overdose may cause severe GI bleeding and kidney failure. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - avoid in third trimester; consult OB-GYN",
        "full_text": "Diclofenac (Voltaren) is a prescription NSAID for pain and inflammation. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-041", "generic_name": "Domperidone",
        "drug_class": "Dopamine Antagonist (Prokinetic / Antiemetic)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Motilium", "manufacturer": "Janssen", "form": "10mg tablet / suspension"},
            {"brand": "Domperidone Generic", "manufacturer": "Various", "form": "10mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 5.00 - PHP 12.00", "branded_per_tablet": "PHP 15.00 - PHP 30.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["nausea and vomiting", "gastroparesis", "GERD (adjunct)"],
        "dosage_adult": "As prescribed by physician. Typical: 10 mg 3 times daily before meals.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take 15-30 minutes before meals. Do not take with grapefruit juice.",
        "onset_of_action": "30-60 minutes",
        "side_effects_common": ["dry mouth", "headache", "stomach cramps", "diarrhea"],
        "side_effects_serious": ["QT prolongation / arrhythmia", "severe allergic reaction", "galactorrhea (milk production)"],
        "contraindications": ["prolactinoma", "GI bleeding or obstruction", "severe liver disease", "history of QT prolongation"],
        "drug_interactions": ["ketoconazole", "erythromycin", "other QT-prolonging drugs", "antacids"],
        "overdose_note": "Overdose may cause severe cardiac arrhythmias. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Domperidone (Motilium) is a prescription prokinetic and antiemetic. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-042", "generic_name": "Ondansetron",
        "drug_class": "5-HT3 Receptor Antagonist (Antiemetic)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Zofran", "manufacturer": "GSK", "form": "4mg / 8mg tablet / ODT / IV"},
            {"brand": "Ondansetron Generic", "manufacturer": "Various", "form": "4mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 15.00 - PHP 30.00", "branded_per_tablet": "PHP 50.00 - PHP 100.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["nausea and vomiting (chemotherapy, postoperative, radiation)", "hyperemesis gravidarum"],
        "dosage_adult": "As prescribed by physician. Typical: 4-8 mg every 8 hours as needed.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take with or without food. ODT: place on tongue and let dissolve.",
        "onset_of_action": "30 minutes",
        "side_effects_common": ["headache", "constipation", "dizziness", "fatigue"],
        "side_effects_serious": ["QT prolongation / arrhythmia", "serotonin syndrome (rare)", "severe allergic reaction"],
        "contraindications": ["hypersensitivity to ondansetron", "concurrent use with apomorphine"],
        "drug_interactions": ["tramadol", "other serotonergic drugs", "QT-prolonging drugs"],
        "overdose_note": "Overdose may cause severe constipation and cardiac arrhythmias. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category B - consult OB-GYN; commonly used for hyperemesis gravidarum",
        "full_text": "Ondansetron (Zofran) is a prescription antiemetic for nausea and vomiting. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-043", "generic_name": "Allopurinol",
        "drug_class": "Xanthine Oxidase Inhibitor", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Zyloric", "manufacturer": "GSK", "form": "100mg / 300mg tablet"},
            {"brand": "Allopurinol Generic", "manufacturer": "Various", "form": "100mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 5.00 - PHP 12.00", "branded_per_tablet": "PHP 15.00 - PHP 35.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["gout", "hyperuricemia", "kidney stone prevention (uric acid stones)", "tumor lysis syndrome prophylaxis"],
        "dosage_adult": "As prescribed by physician. Typical starting: 100 mg once daily; may titrate up.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take after meals with plenty of water. Stay well hydrated.",
        "onset_of_action": "Days to weeks for uric acid reduction",
        "side_effects_common": ["nausea", "diarrhea", "skin rash", "drowsiness"],
        "side_effects_serious": ["Stevens-Johnson syndrome", "toxic epidermal necrolysis", "severe allergic reaction", "liver damage"],
        "contraindications": ["hypersensitivity to allopurinol", "asymptomatic hyperuricemia (without gout)"],
        "drug_interactions": ["azathioprine", "mercaptopurine", "warfarin", "theophylline", "ampicillin / amoxicillin (increased rash risk)"],
        "overdose_note": "Overdose may cause severe GI upset and liver damage. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Allopurinol (Zyloric) is a prescription xanthine oxidase inhibitor for gout. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-044", "generic_name": "Colchicine",
        "drug_class": "Anti-gout Agent", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Colsalide", "manufacturer": "Europharma", "form": "0.5mg tablet"},
            {"brand": "Colchicine Generic", "manufacturer": "Various", "form": "0.5mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 10.00 - PHP 20.00", "branded_per_tablet": "PHP 30.00 - PHP 60.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["acute gout attacks", "gout prophylaxis", "familial Mediterranean fever"],
        "dosage_adult": "As prescribed by physician. Typical for acute gout: 1.2 mg at first sign, then 0.6 mg 1 hour later.",
        "dosage_pediatric": "As prescribed by pediatrician for familial Mediterranean fever.",
        "intake_instructions": "Take with or without food. Do not exceed maximum daily dose.",
        "onset_of_action": "24-48 hours (pain relief for acute gout)",
        "side_effects_common": ["nausea", "vomiting", "diarrhea", "abdominal pain"],
        "side_effects_serious": ["bone marrow suppression", "muscle damage (rhabdomyolysis when combined with statins)", "severe allergic reaction"],
        "contraindications": ["severe kidney or liver disease", "blood disorders", "hypersensitivity to colchicine"],
        "drug_interactions": ["clarithromycin", "erythromycin", "statins", "cyclosporine", "verapamil", "diltiazem"],
        "overdose_note": "Overdose is life-threatening: severe GI bleeding, bone marrow suppression, multi-organ failure. Seek emergency care immediately.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Colchicine (Colsalide) is a prescription anti-gout agent for acute gout attacks and prophylaxis. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-045", "generic_name": "Erythromycin",
        "drug_class": "Macrolide Antibiotic", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Erythrocin", "manufacturer": "Abbott", "form": "250mg / 500mg tablet / suspension"},
            {"brand": "Erythromycin Generic", "manufacturer": "Various", "form": "500mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 8.00 - PHP 18.00", "branded_per_tablet": "PHP 25.00 - PHP 50.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["respiratory infections", "skin infections", "atypical mycobacterial infections", "gastroparesis (prokinetic)", "pertussis"],
        "dosage_adult": "As prescribed by physician. Typical: 250-500 mg every 6 hours.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take with food to reduce stomach upset. Do not refrigerate suspension.",
        "onset_of_action": "1-2 hours",
        "side_effects_common": ["nausea", "diarrhea", "stomach pain", "vomiting"],
        "side_effects_serious": ["QT prolongation / arrhythmia", "liver damage", "severe allergic reaction", "C. difficile colitis"],
        "contraindications": ["hypersensitivity to erythromycin", "severe liver disease", "history of QT prolongation", "concurrent use with cisapride or pimozide"],
        "drug_interactions": ["warfarin", "carbamazepine", "theophylline", "statins", "verapamil", "digoxin"],
        "overdose_note": "Overdose may cause severe GI symptoms and cardiac arrhythmias. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category B - consult OB-GYN",
        "full_text": "Erythromycin (Erythrocin) is a prescription macrolide antibiotic. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-046", "generic_name": "Tamsulosin",
        "drug_class": "Alpha-1 Adrenergic Blocker", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Harnal", "manufacturer": "Yamanouchi", "form": "0.4mg modified-release capsule"},
            {"brand": "Tamsulosin Generic", "manufacturer": "Various", "form": "0.4mg capsule"}
        ],
        "ph_price_estimates": {"generic_per_capsule": "PHP 15.00 - PHP 30.00", "branded_per_capsule": "PHP 50.00 - PHP 100.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["benign prostatic hyperplasia (BPH)", "urinary retention due to prostate enlargement"],
        "dosage_adult": "As prescribed by physician. Typical: 0.4 mg once daily after the same meal each day.",
        "dosage_pediatric": "Not indicated for children.",
        "intake_instructions": "Take 30 minutes after the same meal each day. Swallow whole; do not crush or chew.",
        "onset_of_action": "2 weeks for symptom improvement; 4-6 weeks for full effect",
        "side_effects_common": ["dizziness", "lightheadedness (especially on standing)", "headache", "nasal congestion", "retrograde ejaculation"],
        "side_effects_serious": ["severe hypotension", "priapism (rare)", "severe allergic reaction"],
        "contraindications": ["hypersensitivity to tamsulosin", "severe liver disease"],
        "drug_interactions": ["other alpha-blockers", "PDE5 inhibitors (e.g., sildenafil - increased hypotension risk)", "cimetidine"],
        "overdose_note": "Overdose causes severe hypotension. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category B - not indicated for women; consult OB-GYN if accidental exposure during pregnancy",
        "full_text": "Tamsulosin (Harnal) is a prescription alpha-blocker for benign prostatic hyperplasia (BPH). Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-047", "generic_name": "Methylprednisolone",
        "drug_class": "Corticosteroid (Systemic)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Medrol", "manufacturer": "Pfizer", "form": "4mg / 16mg tablet"},
            {"brand": "Methylprednisolone Generic", "manufacturer": "Various", "form": "4mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 8.00 - PHP 18.00", "branded_per_tablet": "PHP 25.00 - PHP 50.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["inflammatory conditions", "allergic reactions", "asthma exacerbations", "autoimmune disorders", "spinal cord injury (high-dose protocol)"],
        "dosage_adult": "As prescribed by physician. Dose varies widely by condition.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take with food to reduce stomach irritation. Do not stop abruptly if used long-term.",
        "onset_of_action": "1-2 hours",
        "side_effects_common": ["increased appetite", "weight gain", "mood changes", "insomnia", "stomach upset"],
        "side_effects_serious": ["adrenal suppression (long-term use)", "osteoporosis", "diabetes", "severe infections", "Cushing's syndrome"],
        "contraindications": ["systemic fungal infections", "live vaccines (while on high doses)", "hypersensitivity"],
        "drug_interactions": ["NSAIDs (increased GI bleeding risk)", "warfarin", "diuretics", "vaccines"],
        "overdose_note": "Overdose may cause severe fluid retention, high blood pressure, and electrolyte imbalance. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Methylprednisolone (Medrol) is a prescription systemic corticosteroid for inflammation and autoimmune conditions. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-048", "generic_name": "Captopril",
        "drug_class": "Angiotensin-Converting Enzyme Inhibitor (ACE-I)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Capoten", "manufacturer": "Bristol-Myers Squibb", "form": "25mg / 50mg tablet"},
            {"brand": "Captopril Generic", "manufacturer": "Various", "form": "25mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 5.00 - PHP 12.00", "branded_per_tablet": "PHP 20.00 - PHP 40.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["hypertension", "heart failure", "diabetic nephropathy", "post-myocardial infarction"],
        "dosage_adult": "As prescribed by physician. Typical starting: 12.5-25 mg 2-3 times daily.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take 1 hour before meals. May be taken with food if stomach upset occurs.",
        "onset_of_action": "15 minutes; 2-4 weeks for full blood pressure control",
        "side_effects_common": ["dry cough", "dizziness", "fatigue", "loss of taste", "rash"],
        "side_effects_serious": ["angioedema", "severe hypotension", "acute kidney injury", "hyperkalemia"],
        "contraindications": ["pregnancy (second and third trimesters)", "history of angioedema with ACE inhibitors", "bilateral renal artery stenosis"],
        "drug_interactions": ["potassium supplements", "NSAIDs", "lithium", "diuretics"],
        "overdose_note": "Overdose causes severe hypotension. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category D - contraindicated in 2nd and 3rd trimesters",
        "full_text": "Captopril (Capoten) is a prescription ACE inhibitor for hypertension and heart failure. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-049", "generic_name": "Atenolol",
        "drug_class": "Beta-1 Selective Blocker", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Tenormin", "manufacturer": "AstraZeneca", "form": "50mg / 100mg tablet"},
            {"brand": "Atenolol Generic", "manufacturer": "Various", "form": "50mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 3.00 - PHP 8.00", "branded_per_tablet": "PHP 15.00 - PHP 30.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["hypertension", "angina", "post-myocardial infarction"],
        "dosage_adult": "As prescribed by physician. Typical: 50-100 mg once daily.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take at the same time each day. May be taken with or without food.",
        "onset_of_action": "1 hour; 1-2 weeks for full blood pressure control",
        "side_effects_common": ["fatigue", "cold hands and feet", "dizziness", "bradycardia (slow heart rate)"],
        "side_effects_serious": ["severe bradycardia", "heart block", "worsening heart failure", "bronchospasm (less likely than non-selective beta-blockers)"],
        "contraindications": ["severe bradycardia", "heart block", "cardiogenic shock", "uncontrolled asthma"],
        "drug_interactions": ["verapamil", "diltiazem", "other beta-blockers", "clonidine (rebound hypertension if stopped)"],
        "overdose_note": "Overdose causes severe bradycardia and hypotension. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category D - contraindicated in 2nd and 3rd trimesters; consult OB-GYN",
        "full_text": "Atenolol (Tenormin) is a prescription beta-1 selective blocker for hypertension and angina. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-050", "generic_name": "Ceftriaxone",
        "drug_class": "Cephalosporin Antibiotic (Injectable)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Rocephin", "manufacturer": "Roche", "form": "1g / 2g vial (IM/IV)"},
            {"brand": "Ceftriaxone Generic", "manufacturer": "Various", "form": "1g vial"}
        ],
        "ph_price_estimates": {"generic_per_vial": "PHP 80.00 - PHP 150.00", "branded_per_vial": "PHP 250.00 - PHP 450.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["severe respiratory infections", "meningitis", "sepsis", "complicated UTIs", "gonorrhea", "typhoid fever"],
        "dosage_adult": "As prescribed by physician. Typical: 1-2 g once daily IM or IV.",
        "dosage_pediatric": "As prescribed by pediatrician. Not recommended for neonates with hyperbilirubinemia.",
        "intake_instructions": "Administered by healthcare professional as IM or IV injection.",
        "onset_of_action": "1-2 hours",
        "side_effects_common": ["pain at injection site", "diarrhea", "nausea", "rash"],
        "side_effects_serious": ["severe allergic reaction", "biliary sludge / pseudolithiasis", "C. difficile colitis", "hemolytic anemia"],
        "contraindications": ["cephalosporin allergy", "neonates with hyperbilirubinemia", "hypersensitivity to ceftriaxone calcium precipitates"],
        "drug_interactions": ["calcium-containing IV solutions (precipitation risk in neonates)", "warfarin", "aminoglycosides"],
        "overdose_note": "Overdose may cause severe neurological symptoms and seizures. Seek emergency care.",
        "storage": "Store below 30C. Protect from light.",
        "pregnancy_category": "Category B - consult OB-GYN",
        "full_text": "Ceftriaxone (Rocephin) is a prescription injectable cephalosporin antibiotic for severe infections. Requires a doctor's prescription and healthcare administration."
    },
    {
        "drug_id": "PH-RX-041", "generic_name": "Fluoxetine",
        "drug_class": "Selective Serotonin Reuptake Inhibitor (SSRI)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Prozac", "manufacturer": "Eli Lilly", "form": "20mg capsule"},
            {"brand": "Fluoxetine Generic", "manufacturer": "Various", "form": "20mg capsule"}
        ],
        "ph_price_estimates": {"generic_per_capsule": "PHP 12.00 - PHP 25.00", "branded_per_capsule": "PHP 40.00 - PHP 80.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["major depressive disorder", "obsessive-compulsive disorder", "panic disorder", "bulimia nervosa"],
        "dosage_adult": "As prescribed by physician. Typical starting: 20 mg once daily.",
        "dosage_pediatric": "As prescribed by pediatric psychiatrist.",
        "intake_instructions": "Take in the morning. May be taken with or without food. Do not stop abruptly.",
        "onset_of_action": "1-2 weeks for initial improvement; 4-6 weeks for full effect",
        "side_effects_common": ["nausea", "insomnia", "anxiety", "sexual dysfunction", "dry mouth"],
        "side_effects_serious": ["serotonin syndrome", "suicidal thoughts (young adults)", "severe allergic reaction"],
        "contraindications": ["MAOI use within 14 days", "pimozide", "hypersensitivity to fluoxetine"],
        "drug_interactions": ["MAOIs", "tramadol", "warfarin", "other SSRIs/SNRIs"],
        "overdose_note": "Overdose may cause severe serotonin syndrome and seizures. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN; risk in third trimester",
        "full_text": "Fluoxetine (Prozac) is a prescription SSRI antidepressant. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-042", "generic_name": "Quetiapine",
        "drug_class": "Atypical Antipsychotic", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Seroquel", "manufacturer": "AstraZeneca", "form": "25mg / 100mg / 200mg tablet"},
            {"brand": "Quetiapine Generic", "manufacturer": "Various", "form": "25mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 15.00 - PHP 30.00", "branded_per_tablet": "PHP 50.00 - PHP 100.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["schizophrenia", "bipolar disorder", "major depressive disorder (adjunct)"],
        "dosage_adult": "As prescribed by physician. Typical starting: 25 mg twice daily, titrated up.",
        "dosage_pediatric": "As prescribed by pediatric psychiatrist.",
        "intake_instructions": "Take with food to reduce dizziness. Do not stop abruptly.",
        "onset_of_action": "1-2 weeks for initial effect",
        "side_effects_common": ["drowsiness", "dizziness", "dry mouth", "weight gain", "constipation"],
        "side_effects_serious": ["neuroleptic malignant syndrome", "severe allergic reaction", "diabetes risk"],
        "contraindications": ["hypersensitivity to quetiapine"],
        "drug_interactions": ["CNS depressants", "alcohol", "antihypertensives", "CYP3A4 inducers/inhibitors"],
        "overdose_note": "Overdose causes severe CNS depression and hypotension. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Quetiapine (Seroquel) is a prescription atypical antipsychotic for schizophrenia and bipolar disorder."
    },
    {
        "drug_id": "PH-RX-043", "generic_name": "Ondansetron",
        "drug_class": "5-HT3 Receptor Antagonist (Anti-emetic)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Zofran", "manufacturer": "GSK", "form": "4mg / 8mg tablet / IV"},
            {"brand": "Ondansetron Generic", "manufacturer": "Various", "form": "4mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 20.00 - PHP 40.00", "branded_per_tablet": "PHP 60.00 - PHP 120.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["nausea", "vomiting", "chemotherapy-induced nausea", "post-operative nausea"],
        "dosage_adult": "As prescribed by physician. Typical: 4-8 mg every 8 hours.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take with or without food. For IV: administered by healthcare professional.",
        "onset_of_action": "30 minutes (oral); minutes (IV)",
        "side_effects_common": ["headache", "constipation", "dizziness", "fatigue"],
        "side_effects_serious": ["QT prolongation / arrhythmia", "serotonin syndrome (rare)", "severe allergic reaction"],
        "contraindications": ["hypersensitivity to ondansetron", "congenital long QT syndrome"],
        "drug_interactions": ["QT-prolonging drugs", "tramadol", "SSRIs/SNRIs"],
        "overdose_note": "Overdose may cause severe serotonin syndrome and cardiac arrhythmias. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category B - consult OB-GYN",
        "full_text": "Ondansetron (Zofran) is a prescription anti-emetic for nausea and vomiting. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-044", "generic_name": "Domperidone",
        "drug_class": "Dopamine Antagonist (Prokinetic)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Motilium", "manufacturer": "J&J", "form": "10mg tablet"},
            {"brand": "Domperidone Generic", "manufacturer": "Various", "form": "10mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 8.00 - PHP 15.00", "branded_per_tablet": "PHP 25.00 - PHP 45.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["nausea", "vomiting", "gastroparesis", "GERD"],
        "dosage_adult": "As prescribed by physician. Typical: 10 mg 3-4 times daily before meals.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take 15-30 minutes before meals. Do not take with grapefruit juice.",
        "onset_of_action": "30-60 minutes",
        "side_effects_common": ["dry mouth", "headache", "stomach cramps", "diarrhea"],
        "side_effects_serious": ["QT prolongation / arrhythmia", "galactorrhea", "severe allergic reaction"],
        "contraindications": ["prolactinoma", "gastrointestinal hemorrhage", "mechanical bowel obstruction"],
        "drug_interactions": ["ketoconazole", "erythromycin", "other QT-prolonging drugs"],
        "overdose_note": "Overdose may cause severe QT prolongation and seizures. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Domperidone (Motilium) is a prescription prokinetic for nausea and vomiting."
    },
    {
        "drug_id": "PH-RX-045", "generic_name": "Allopurinol",
        "drug_class": "Xanthine Oxidase Inhibitor", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Zyloric", "manufacturer": "GSK", "form": "100mg / 300mg tablet"},
            {"brand": "Allopurinol Generic", "manufacturer": "Various", "form": "100mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 8.00 - PHP 18.00", "branded_per_tablet": "PHP 25.00 - PHP 50.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["gout", "hyperuricemia", "kidney stones (urate)"],
        "dosage_adult": "As prescribed by physician. Typical starting: 100 mg daily, titrated up.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take after meals to reduce stomach upset. Drink plenty of water.",
        "onset_of_action": "Days to weeks (uric acid reduction)",
        "side_effects_common": ["nausea", "diarrhea", "skin rash", "drowsiness"],
        "side_effects_serious": ["Stevens-Johnson syndrome", "toxic epidermal necrolysis", "severe allergic reaction", "liver damage"],
        "contraindications": ["hypersensitivity to allopurinol"],
        "drug_interactions": ["azathioprine", "mercaptopurine", "warfarin", "theophylline"],
        "overdose_note": "Overdose may cause severe rash and liver damage. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Allopurinol (Zyloric) is a prescription xanthine oxidase inhibitor for gout."
    },
    {
        "drug_id": "PH-RX-046", "generic_name": "Colchicine",
        "drug_class": "Anti-inflammatory (microtubule inhibitor)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Colcrys", "manufacturer": "Takeda", "form": "0.5mg / 0.6mg tablet"},
            {"brand": "Colchicine Generic", "manufacturer": "Various", "form": "0.5mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 20.00 - PHP 40.00", "branded_per_tablet": "PHP 60.00 - PHP 120.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["acute gout attacks", "familial Mediterranean fever"],
        "dosage_adult": "As prescribed by physician. Typical for acute gout: 1.2 mg at first sign, then 0.6 mg 1 hour later.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take at first sign of gout flare. Do not exceed prescribed dose.",
        "onset_of_action": "Hours (symptom relief)"
        ,
        "side_effects_common": ["nausea", "vomiting", "diarrhea", "stomach pain"],
        "side_effects_serious": ["bone marrow suppression", "muscle damage", "severe allergic reaction"],
        "contraindications": ["severe kidney disease", "severe liver disease", "hypersensitivity to colchicine"],
        "drug_interactions": ["clarithromycin", "erythromycin", "ketoconazole", "statins", "verapamil"],
        "overdose_note": "Overdose is life-threatening. Causes severe GI bleeding, bone marrow suppression, and multi-organ failure. Seek emergency care immediately.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Colchicine (Colcrys) is a prescription anti-inflammatory for acute gout attacks."
    },
    {
        "drug_id": "PH-RX-047", "generic_name": "Propranolol",
        "drug_class": "Beta-Blocker (non-selective)", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Inderal", "manufacturer": "AstraZeneca", "form": "10mg / 40mg / 80mg tablet"},
            {"brand": "Propranolol Generic", "manufacturer": "Various", "form": "40mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 5.00 - PHP 12.00", "branded_per_tablet": "PHP 20.00 - PHP 40.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["hypertension", "angina", "arrhythmia", "migraine prophylaxis", "tremor", "anxiety"],
        "dosage_adult": "As prescribed by physician. Typical: 40 mg twice daily for hypertension.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take with food. Do not stop abruptly due to rebound hypertension.",
        "onset_of_action": "1-2 hours (blood pressure); days to weeks for migraine prophylaxis",
        "side_effects_common": ["fatigue", "dizziness", "cold hands/feet", "bradycardia", "insomnia"],
        "side_effects_serious": ["severe bradycardia", "heart block", "bronchospasm", "severe hypotension"],
        "contraindications": ["asthma", "severe bradycardia", "heart block", "hypersensitivity to propranolol"],
        "drug_interactions": ["other antihypertensives", "digoxin", "NSAIDs", "insulin"],
        "overdose_note": "Overdose causes severe bradycardia, hypotension, and bronchospasm. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Propranolol (Inderal) is a prescription beta-blocker for hypertension, angina, and migraine prophylaxis."
    },
    {
        "drug_id": "PH-RX-048", "generic_name": "Digoxin",
        "drug_class": "Cardiac Glycoside", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Lanoxin", "manufacturer": "GSK", "form": "0.25mg tablet / 0.5mg/2mL ampule"},
            {"brand": "Digoxin Generic", "manufacturer": "Various", "form": "0.25mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 8.00 - PHP 18.00", "branded_per_tablet": "PHP 25.00 - PHP 50.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["heart failure", "atrial fibrillation"],
        "dosage_adult": "As prescribed by physician. Dose is highly individualized based on blood levels.",
        "dosage_pediatric": "As prescribed by pediatric cardiologist.",
        "intake_instructions": "Take at the same time each day. May be taken with or without food. Regular blood monitoring required.",
        "onset_of_action": "30 minutes - 2 hours (oral); 5-30 minutes (IV)",
        "side_effects_common": ["nausea", "vomiting", "diarrhea", "loss of appetite", "visual disturbances (yellow/green halos)"],
        "side_effects_serious": ["digoxin toxicity (arrhythmias)", "severe bradycardia", "heart block"],
        "contraindications": ["ventricular fibrillation", "hypersensitivity to digoxin"],
        "drug_interactions": ["amiodarone", "verapamil", "quinidine", "diuretics", "beta-blockers"],
        "overdose_note": "Digoxin overdose is life-threatening. Causes severe arrhythmias. Seek emergency care immediately.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Digoxin (Lanoxin) is a prescription cardiac glycoside for heart failure and atrial fibrillation."
    },
    {
        "drug_id": "PH-RX-049", "generic_name": "Spironolactone",
        "drug_class": "Potassium-Sparing Diuretic / Aldosterone Antagonist", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Aldactone", "manufacturer": "Pfizer", "form": "25mg / 100mg tablet"},
            {"brand": "Spironolactone Generic", "manufacturer": "Various", "form": "25mg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 8.00 - PHP 18.00", "branded_per_tablet": "PHP 25.00 - PHP 50.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["heart failure", "edema", "ascites", "hypertension", "hirsutism (in PCOS)"],
        "dosage_adult": "As prescribed by physician. Typical: 25-100 mg once daily.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take with food. Monitor potassium levels regularly.",
        "onset_of_action": "2-3 days (diuretic effect); weeks for heart failure benefit",
        "side_effects_common": ["hyperkalemia", "gynecomastia (in males)", "menstrual irregularities", "dizziness"],
        "side_effects_serious": ["severe hyperkalemia", "severe hyponatremia", "acute kidney injury"],
        "contraindications": ["hyperkalemia", "severe kidney disease", "Addison's disease"],
        "drug_interactions": ["potassium supplements", "ACE inhibitors", "ARBs", "NSAIDs"],
        "overdose_note": "Overdose causes severe hyperkalemia and dehydration. Seek emergency care.",
        "storage": "Store below 30C.",
        "pregnancy_category": "Category C - consult OB-GYN",
        "full_text": "Spironolactone (Aldactone) is a prescription potassium-sparing diuretic for heart failure and edema."
    },
    {
        "drug_id": "PH-RX-050", "generic_name": "Levothyroxine",
        "drug_class": "Thyroid Hormone", "rx_status": "Rx", "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Synthroid", "manufacturer": "Abbott", "form": "25mcg / 50mcg / 100mcg tablet"},
            {"brand": "Levothyroxine Generic", "manufacturer": "Various", "form": "50mcg tablet"}
        ],
        "ph_price_estimates": {"generic_per_tablet": "PHP 8.00 - PHP 15.00", "branded_per_tablet": "PHP 25.00 - PHP 50.00", "source": "Mercury Drug / Generics Pharmacy (2024-2025 estimate)"},
        "indications": ["hypothyroidism", "goiter", "thyroid cancer (suppressive therapy)"],
        "dosage_adult": "As prescribed by physician. Dose is highly individualized based on TSH levels.",
        "dosage_pediatric": "As prescribed by pediatric endocrinologist.",
        "intake_instructions": "Take on an empty stomach, 30-60 minutes before breakfast. Take with water only.",
        "onset_of_action": "Days to weeks (symptom improvement); 4-6 weeks for full effect",
        "side_effects_common": ["weight loss", "nervousness", "tremor", "headache", "insomnia"],
        "side_effects_serious": ["thyrotoxicosis (overdose)", "chest pain", "arrhythmias", "osteoporosis (long-term high dose)"],
        "contraindications": ["untreated hyperthyroidism", "acute myocardial infarction", "hypersensitivity to levothyroxine"],
        "drug_interactions": ["calcium supplements", "iron supplements", "antacids", "warfarin", "cholestyramine"],
        "overdose_note": "Overdose causes thyrotoxicosis: chest pain, arrhythmias, seizures. Seek emergency care.",
        "storage": "Store below 30C. Protect from moisture.",
        "pregnancy_category": "Category A - essential in pregnancy; dose may need adjustment",
        "full_text": "Levothyroxine (Synthroid) is a prescription thyroid hormone for hypothyroidism."
    },
]

if __name__ == "__main__":
    db_path = "data/ph_drug_database.jsonl"
    existing = []
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    existing.append(json.loads(line))

    combined = existing + NEW_OTC_DRUGS + NEW_RX_DRUGS

    with open(db_path, "w", encoding="utf-8") as f:
        for rec in combined:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    otc = sum(1 for d in combined if d["rx_status"] == "OTC")
    rx = sum(1 for d in combined if d["rx_status"] == "Rx")
    print(f"[SUCCESS] Expanded {db_path} to {len(combined)} drug records.")
    print(f"          OTC: {otc}")
    print(f"          Rx:  {rx}")
