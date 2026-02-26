"""
core/disease_info.py — Disease knowledge base for all 38 PlantVillage classes.

Usage:
    from core.disease_info import get_disease_info, SEVERITY_CONFIG, DISEASE_INFO
"""

from __future__ import annotations

# ── Severity display config ────────────────────────────────────────────────────
SEVERITY_CONFIG: dict[str, dict] = {
    "none":     {"label": "✅ Healthy",           "color": "#16a34a", "bg": "#dcfce7"},
    "medium":   {"label": "⚠️ Moderate Severity", "color": "#d97706", "bg": "#fef3c7"},
    "high":     {"label": "🔴 High Severity",      "color": "#dc2626", "bg": "#fee2e2"},
    "critical": {"label": "🚨 Critical",           "color": "#7c3aed", "bg": "#ede9fe"},
}

# ── Full disease knowledge base ────────────────────────────────────────────────
DISEASE_INFO: dict[str, dict] = {
    "Apple___Apple_scab": {
        "crop": "Apple", "disease": "Apple Scab",
        "cause": [
            "Caused by the fungus Venturia inaequalis.",
            "Overwinters in fallen infected leaves and releases spores in spring during wet weather. Cool (10–20°C), rainy spring conditions favour rapid spread.",
        ],
        "treatment": [
            "Plant resistant apple varieties (e.g., Liberty, Freedom).",
            "Rake and destroy fallen leaves every autumn to break the cycle.",
            "Apply fungicides (captan, myclobutanil) starting at bud-break and repeat every 7–14 days during wet periods.",
        ],
        "severity": "medium",
    },
    "Apple___Black_rot": {
        "crop": "Apple", "disease": "Black Rot",
        "cause": [
            "Caused by Botryosphaeria obtusa (anamorph: Diplodia seriata).",
            "Enters through wounds, pruning cuts, or fire blight lesions. Mummified fruit left on the tree are the primary inoculum source.",
        ],
        "treatment": [
            "Prune out dead, cankered, or diseased wood and destroy it.",
            "Remove all mummified fruit from the tree and ground before spring.",
            "Apply copper-based or captan fungicide sprays during the growing season.",
        ],
        "severity": "high",
    },
    "Apple___Cedar_apple_rust": {
        "crop": "Apple", "disease": "Cedar Apple Rust",
        "cause": [
            "Caused by Gymnosporangium juniperi-virginianae, requiring two alternate hosts — apple and Eastern red cedar or juniper — to complete its lifecycle.",
            "Orange gelatinous spore horns on junipers release spores in spring that infect apple leaves.",
        ],
        "treatment": [
            "Remove nearby Eastern red cedar or juniper trees if feasible.",
            "Plant rust-resistant apple varieties.",
            "Apply myclobutanil, sulfur, or immunox sprays from pink stage of bud development through petal fall.",
        ],
        "severity": "medium",
    },
    "Apple___healthy": {
        "crop": "Apple", "disease": "Healthy",
        "cause": ["No disease detected. The plant appears healthy."],
        "treatment": [
            "Continue regular watering, fertilisation, and canopy management.",
            "Monitor weekly for early signs of scab, rust, or mites.",
            "Apply a preventive copper spray at dormant stage each season.",
        ],
        "severity": "none",
    },
    "Blueberry___healthy": {
        "crop": "Blueberry", "disease": "Healthy",
        "cause": ["No disease detected. Plant appears healthy."],
        "treatment": [
            "Maintain soil pH between 4.5 and 5.5 for optimal growth.",
            "Keep mulch layer 5–10 cm deep to retain moisture and suppress weeds.",
            "Scout for mummy berry and leaf spot every two weeks during the growing season.",
        ],
        "severity": "none",
    },
    "Cherry_(including_sour)___Powdery_mildew": {
        "crop": "Cherry", "disease": "Powdery Mildew",
        "cause": [
            "Caused by Podosphaera clandestina.",
            "Spreads via airborne conidia; favoured by warm days (18–28°C), cool nights, and high humidity — but does NOT require free water on leaf surfaces.",
        ],
        "treatment": [
            "Improve air circulation through proper pruning and canopy management.",
            "Apply sulphur, potassium bicarbonate, or sterol-inhibiting fungicides (myclobutanil) at first sign.",
            "Remove and destroy heavily infected shoots and leaves.",
        ],
        "severity": "medium",
    },
    "Cherry_(including_sour)___healthy": {
        "crop": "Cherry", "disease": "Healthy",
        "cause": ["No disease detected. Plant appears healthy."],
        "treatment": [
            "Prune for open canopy to allow airflow and light penetration.",
            "Apply dormant copper spray to prevent bacterial canker and leaf spot.",
            "Maintain consistent irrigation to avoid stress-related susceptibility.",
        ],
        "severity": "none",
    },
    "Corn_(maize)___Cercospora_leaf_spot_Gray_leaf_spot": {
        "crop": "Corn (Maize)", "disease": "Gray Leaf Spot (Cercospora Leaf Spot)",
        "cause": [
            "Caused by Cercospora zeae-maydis.",
            "Favoured by warm temperatures (25–30°C), high humidity, and extended leaf wetness. Spreads from infected crop residue left in the field.",
        ],
        "treatment": [
            "Plant resistant corn hybrids.",
            "Rotate crops — avoid planting maize on the same land two years consecutively.",
            "Apply strobilurin or triazole fungicides at tasseling stage when disease pressure is high.",
        ],
        "severity": "high",
    },
    "Corn_(maize)___Common_rust_": {
        "crop": "Corn (Maize)", "disease": "Common Rust",
        "cause": [
            "Caused by Puccinia sorghi.",
            "Spores are windborne and travel long distances; favoured by cool, humid conditions (16–23°C). Secondary spread occurs rapidly under these conditions.",
        ],
        "treatment": [
            "Plant resistant corn hybrids (most commercial field corn is adequately resistant).",
            "Apply fungicides (propiconazole, azoxystrobin) on sweet corn or seed corn when rust pustules appear on lower leaves before tasseling.",
        ],
        "severity": "medium",
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "crop": "Corn (Maize)", "disease": "Northern Leaf Blight",
        "cause": [
            "Caused by Setosphaeria turcica (anamorph Exserohilum turcicum).",
            "Survives in infected crop debris; spores spread by wind and rain splash. Cool, wet weather (18–27°C) promotes disease development.",
        ],
        "treatment": [
            "Use resistant hybrids with Ht1, Ht2, or Ht3 resistance genes.",
            "Rotate crops and manage residue by tillage.",
            "Apply foliar fungicides at VT/R1 growth stage when conditions are favourable.",
        ],
        "severity": "high",
    },
    "Corn_(maize)___healthy": {
        "crop": "Corn (Maize)", "disease": "Healthy",
        "cause": ["No disease detected. Plant appears healthy."],
        "treatment": [
            "Ensure adequate nitrogen fertilisation at V6 stage.",
            "Scout frequently for rust pustules, leaf blight lesions, and corn earworm.",
            "Maintain proper plant spacing for airflow.",
        ],
        "severity": "none",
    },
    "Grape___Black_rot": {
        "crop": "Grape", "disease": "Black Rot",
        "cause": [
            "Caused by Guignardia bidwellii.",
            "Overwinters in mummified berries and infected canes. Spores release during rainy spring periods and infect young shoots, leaves and fruit.",
        ],
        "treatment": [
            "Remove all mummified berries and infected canes during winter pruning.",
            "Apply myclobutanil or mancozeb fungicides from bud-break through veraison.",
            "Ensure good canopy airflow by leaf removal and shoot positioning.",
        ],
        "severity": "high",
    },
    "Grape___Esca_(Black_Measles)": {
        "crop": "Grape", "disease": "Esca (Black Measles)",
        "cause": [
            "A wood disease complex caused by multiple fungi including Phaeomoniella chlamydospora and Phaeoacremonium species.",
            "Enters through pruning wounds; can remain latent for years before symptoms appear.",
        ],
        "treatment": [
            "Apply wound sealants (Bordeaux paste) immediately after pruning.",
            "Remove and destroy severely infected wood.",
            "Delay pruning until late in the dormant season to reduce infection risk.",
            "No curative treatment exists; prevention is critical.",
        ],
        "severity": "high",
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "crop": "Grape", "disease": "Leaf Blight (Isariopsis Leaf Spot)",
        "cause": [
            "Caused by Isariopsis clavispora (now reclassified as Pseudocercospora vitis).",
            "Spreads via conidia under warm, humid conditions. Primarily a late-season disease.",
        ],
        "treatment": [
            "Apply copper-based or mancozeb fungicides preventively.",
            "Remove infected leaves and improve canopy ventilation.",
            "Avoid excessive nitrogen which promotes dense, susceptible foliage.",
        ],
        "severity": "medium",
    },
    "Grape___healthy": {
        "crop": "Grape", "disease": "Healthy",
        "cause": ["No disease detected. Plant appears healthy."],
        "treatment": [
            "Apply a dormant copper spray for disease prevention.",
            "Monitor for powdery mildew and downy mildew from bud-break.",
            "Perform shoot thinning to maintain open canopy structure.",
        ],
        "severity": "none",
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "crop": "Orange", "disease": "Huanglongbing (Citrus Greening)",
        "cause": [
            "Caused by the bacterium Candidatus Liberibacter asiaticus, transmitted by the Asian citrus psyllid (Diaphorina citri).",
            "One of the most destructive citrus diseases worldwide — there is currently NO cure.",
        ],
        "treatment": [
            "Immediately remove and destroy infected trees to prevent spread.",
            "Control Asian citrus psyllid populations with systemic insecticides (imidacloprid, dimethoate).",
            "Plant certified disease-free nursery stock.",
            "Report suspected infections to the local agricultural authority immediately.",
        ],
        "severity": "critical",
    },
    "Peach___Bacterial_spot": {
        "crop": "Peach", "disease": "Bacterial Spot",
        "cause": [
            "Caused by Xanthomonas arboricola pv. pruni.",
            "Spreads by rain splash and wind; favoured by warm, wet weather. Enters through stomata and wounds.",
        ],
        "treatment": [
            "Plant resistant peach varieties.",
            "Apply copper-based bactericides from shuck split through late summer, following a regular spray program.",
            "Avoid wetting foliage when irrigating.",
        ],
        "severity": "medium",
    },
    "Peach___healthy": {
        "crop": "Peach", "disease": "Healthy",
        "cause": ["No disease detected. Plant appears healthy."],
        "treatment": [
            "Apply dormant copper spray for bacterial spot and leaf curl prevention.",
            "Thin fruit to 15–20 cm spacing to improve air circulation.",
            "Scout for peach leaf curl and brown rot from bud swell.",
        ],
        "severity": "none",
    },
    "Pepper,_bell___Bacterial_spot": {
        "crop": "Bell Pepper", "disease": "Bacterial Spot",
        "cause": [
            "Caused by Xanthomonas euvesicatoria.",
            "Spreads rapidly in warm (24–30°C), wet conditions via water splash. Seeds can carry the pathogen.",
        ],
        "treatment": [
            "Use certified pathogen-free seed or treat seed with hot water (50°C for 25 min).",
            "Apply copper bactericides routinely throughout the season.",
            "Avoid working in the field when plants are wet.",
            "Rotate crops — do not plant peppers or tomatoes in the same field for 2+ years.",
        ],
        "severity": "medium",
    },
    "Pepper,_bell___healthy": {
        "crop": "Bell Pepper", "disease": "Healthy",
        "cause": ["No disease detected. Plant appears healthy."],
        "treatment": [
            "Maintain consistent soil moisture to prevent blossom drop.",
            "Scout weekly for aphids, thrips, and bacterial spot lesions.",
            "Apply balanced fertilisation — avoid excess nitrogen near fruiting.",
        ],
        "severity": "none",
    },
    "Potato___Early_blight": {
        "crop": "Potato", "disease": "Early Blight",
        "cause": [
            "Caused by Alternaria solani.",
            "Survives in infected plant debris and soil. Favoured by warm days (24–29°C) and heavy dew or rain. Older leaves are most susceptible.",
        ],
        "treatment": [
            "Plant certified disease-free seed tubers.",
            "Apply fungicides (chlorothalonil, mancozeb, azoxystrobin) preventively from early canopy closure.",
            "Rotate crops and destroy plant debris after harvest.",
            "Maintain adequate potassium nutrition to reduce plant stress.",
        ],
        "severity": "medium",
    },
    "Potato___Late_blight": {
        "crop": "Potato", "disease": "Late Blight",
        "cause": [
            "Caused by Phytophthora infestans — the same pathogen responsible for the Irish Potato Famine.",
            "Thrives in cool (10–20°C), wet conditions. Can destroy an entire field within days if uncontrolled.",
        ],
        "treatment": [
            "Plant resistant varieties when available.",
            "Apply fungicides (mancozeb, cymoxanil + mancozeb, metalaxyl) on a 5–7 day schedule during high-risk periods.",
            "Eliminate cull piles and volunteer potatoes.",
            "Haul crop immediately after onset of disease to minimise spread.",
        ],
        "severity": "critical",
    },
    "Potato___healthy": {
        "crop": "Potato", "disease": "Healthy",
        "cause": ["No disease detected. Plant appears healthy."],
        "treatment": [
            "Hill soil around stems at 15–20 cm emergence to protect developing tubers.",
            "Scout regularly for Colorado potato beetle and aphids.",
            "Apply preventive fungicides before canopy closure in wet-season regions.",
        ],
        "severity": "none",
    },
    "Raspberry___healthy": {
        "crop": "Raspberry", "disease": "Healthy",
        "cause": ["No disease detected. Plant appears healthy."],
        "treatment": [
            "Remove floricanes (second-year canes) immediately after harvest.",
            "Monitor for raspberry cane borer and spur blight.",
            "Apply lime-sulphur dormant spray to reduce fungal inoculum.",
        ],
        "severity": "none",
    },
    "Soybean___healthy": {
        "crop": "Soybean", "disease": "Healthy",
        "cause": ["No disease detected. Plant appears healthy."],
        "treatment": [
            "Apply seed treatment fungicides (thiram, metalaxyl) to protect seedlings.",
            "Scout for sudden death syndrome and soybean cyst nematode.",
            "Rotate with a non-legume crop to reduce soil-borne pathogen buildup.",
        ],
        "severity": "none",
    },
    "Squash___Powdery_mildew": {
        "crop": "Squash", "disease": "Powdery Mildew",
        "cause": [
            "Caused by Podosphaera xanthii (formerly Sphaerotheca fuliginea).",
            "Spreads via airborne spores; unlike most fungi, does NOT require surface moisture. Favoured by high humidity and temperatures of 20–30°C.",
        ],
        "treatment": [
            "Apply potassium bicarbonate, neem oil, or sulphur sprays at first sign of whitish patches.",
            "Use resistant squash varieties.",
            "Avoid overhead irrigation; improve air circulation through plant spacing.",
            "Remove and destroy heavily infected leaves.",
        ],
        "severity": "medium",
    },
    "Strawberry___Leaf_scorch": {
        "crop": "Strawberry", "disease": "Leaf Scorch",
        "cause": [
            "Caused by Diplocarpon earlianum.",
            "Spreads by rain splash from infected leaves. Overwintering occurs in dead leaves left in the planting. Cool, wet spring weather promotes rapid spread.",
        ],
        "treatment": [
            "Remove and destroy old infected leaves after harvest.",
            "Apply fungicides (captan, thiram) from early spring through harvest.",
            "Ensure good air circulation and avoid excessive nitrogen.",
            "Renovate beds annually after fruiting.",
        ],
        "severity": "medium",
    },
    "Strawberry___healthy": {
        "crop": "Strawberry", "disease": "Healthy",
        "cause": ["No disease detected. Plant appears healthy."],
        "treatment": [
            "Renovate beds after harvest by mowing, fertilising, and thinning.",
            "Scout for two-spotted spider mites and Botrytis grey mould.",
            "Maintain straw mulch to prevent fruit contact with soil.",
        ],
        "severity": "none",
    },
    "Tomato___Bacterial_spot": {
        "crop": "Tomato", "disease": "Bacterial Spot",
        "cause": [
            "Caused by Xanthomonas vesicatoria and related species.",
            "Transmitted via infected seed, transplants, and rain splash. The bacterium infects leaves, stems, and fruit, causing water-soaked lesions that turn brown.",
        ],
        "treatment": [
            "Use certified disease-free seed; treat seed with hot water if uncertain.",
            "Apply copper-based bactericides + mancozeb from transplanting through the season.",
            "Practice crop rotation of at least 2 years with non-solanaceous crops.",
            "Avoid working in the crop when foliage is wet.",
        ],
        "severity": "medium",
    },
    "Tomato___Early_blight": {
        "crop": "Tomato", "disease": "Early Blight",
        "cause": [
            "Caused by Alternaria solani.",
            "Survives in infected crop debris. Characteristic 'target spot' lesions with concentric rings appear first on older, lower leaves. Favoured by warm (24–29°C) temperatures and alternating wet/dry conditions.",
        ],
        "treatment": [
            "Rotate crops; avoid planting tomatoes or potatoes in the same position for 3 years.",
            "Remove lower leaves showing lesions to slow spread.",
            "Apply chlorothalonil, mancozeb, or copper sprays preventively.",
            "Mulch to reduce soil-splash inoculum onto leaves.",
        ],
        "severity": "medium",
    },
    "Tomato___Late_blight": {
        "crop": "Tomato", "disease": "Late Blight",
        "cause": [
            "Caused by Phytophthora infestans.",
            "Spreads explosively under cool (10–20°C), wet conditions via airborne sporangia. Can destroy a crop within a week if unchecked.",
        ],
        "treatment": [
            "Apply preventive fungicides (mancozeb, chlorothalonil, cymoxanil) before infection occurs.",
            "Destroy affected plants immediately — do not compost them.",
            "Avoid overhead irrigation; water at soil level in the morning.",
            "Plant resistant varieties where available.",
        ],
        "severity": "critical",
    },
    "Tomato___Leaf_Mold": {
        "crop": "Tomato", "disease": "Leaf Mold",
        "cause": [
            "Caused by Passalora fulva (formerly Cladosporium fulvum).",
            "Strictly a humid-environment disease — requires >85% relative humidity. Predominantly a problem in greenhouses or tunnel-grown tomatoes.",
        ],
        "treatment": [
            "Reduce greenhouse/tunnel humidity using ventilation; target RH below 85%.",
            "Apply copper or chlorothalonil sprays at first symptom.",
            "Space plants adequately and stake/prune for airflow through the canopy.",
            "Plant mold-resistant varieties.",
        ],
        "severity": "medium",
    },
    "Tomato___Septoria_leaf_spot": {
        "crop": "Tomato", "disease": "Septoria Leaf Spot",
        "cause": [
            "Caused by Septoria lycopersici.",
            "Survives in crop debris and on solanaceous weeds. Spreads by rain splash. Small circular spots with dark borders and light centres appear first on lower leaves.",
        ],
        "treatment": [
            "Remove and destroy infected lower leaves as soon as spotted.",
            "Apply chlorothalonil, mancozeb, or copper fungicides on a 7–10 day schedule.",
            "Stake plants and mulch to reduce splash from soil.",
            "Avoid overhead irrigation.",
        ],
        "severity": "medium",
    },
    "Tomato___Spider_mites_Two-spotted_spider_mite": {
        "crop": "Tomato", "disease": "Two-Spotted Spider Mite",
        "cause": [
            "Caused by the mite Tetranychus urticae, not a fungus or bacterium.",
            "Thrives in hot (over 30°C), dry conditions. Populations can double in less than a week. Leaves show stippling, bronzing, and webbing.",
        ],
        "treatment": [
            "Apply miticides (abamectin, bifenazate, spiromesifen) — rotate actives to prevent resistance.",
            "Introduce predatory mites (Phytoseiulus persimilis) as biological control.",
            "Spray the undersides of leaves where mites feed.",
            "Avoid broad-spectrum insecticides that kill natural predators.",
        ],
        "severity": "high",
    },
    "Tomato___Target_Spot": {
        "crop": "Tomato", "disease": "Target Spot",
        "cause": [
            "Caused by Corynespora cassiicola.",
            "Favoured by warm, wet conditions. Produces circular lesions with concentric rings like a target. Can affect leaves, stems and fruit.",
        ],
        "treatment": [
            "Apply fungicides (chlorothalonil, azoxystrobin) at first sign.",
            "Prune lower foliage and stake plants to improve air circulation.",
            "Avoid overhead irrigation.",
            "Rotate crops with non-solanaceous families.",
        ],
        "severity": "medium",
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "crop": "Tomato", "disease": "Yellow Leaf Curl Virus (TYLCV)",
        "cause": [
            "Caused by Tomato yellow leaf curl virus, transmitted exclusively by the silverleaf whitefly (Bemisia tabaci).",
            "No cure once a plant is infected. The virus causes severe stunting, leaf puckering, yellowing, and yield loss.",
        ],
        "treatment": [
            "Control whitefly populations immediately with imidacloprid, thiamethoxam, or insecticidal soap.",
            "Use reflective silver mulch to deter whiteflies.",
            "Remove and bag infected plants — do NOT leave in field.",
            "Plant TYLCV-resistant or tolerant tomato varieties.",
            "Install fine mesh insect screens in nurseries to raise clean transplants.",
        ],
        "severity": "critical",
    },
    "Tomato___Tomato_mosaic_virus": {
        "crop": "Tomato", "disease": "Tomato Mosaic Virus (ToMV)",
        "cause": [
            "Caused by Tomato mosaic virus (ToMV), spread by mechanical contact — tools, hands, clothing, infected seeds.",
            "Extremely stable: can survive in dry tobacco products, soil, and on surfaces for years.",
        ],
        "treatment": [
            "Remove and destroy infected plants immediately.",
            "Disinfect tools with 10% bleach or 70% alcohol between plants.",
            "Wash hands thoroughly before handling plants.",
            "Plant virus-resistant tomato varieties (Tm-2² gene resistance).",
            "Do not smoke near plants — tobacco products can carry ToMV.",
        ],
        "severity": "high",
    },
    "Tomato___healthy": {
        "crop": "Tomato", "disease": "Healthy",
        "cause": ["No disease detected. Plant appears healthy."],
        "treatment": [
            "Maintain consistent watering at soil level to prevent blossom-end rot and disease splash.",
            "Scout weekly for early/late blight, spider mites, and whitefly.",
            "Apply balanced fertiliser with adequate calcium to prevent blossom-end rot.",
        ],
        "severity": "none",
    },
}


def get_disease_info(class_name: str) -> dict:
    """
    Return rich disease info for a given class name.
    Gracefully falls back for unknown classes (works with any dataset).
    """
    if class_name in DISEASE_INFO:
        return DISEASE_INFO[class_name]

    # Fallback: parse class name into crop / disease
    if "___" in class_name:
        crop_raw, disease_raw = class_name.split("___", 1)
    else:
        parts = class_name.split("_")
        crop_raw    = parts[0]
        disease_raw = "_".join(parts[1:]) if len(parts) > 1 else class_name

    crop    = crop_raw.replace("_", " ").strip("()")
    disease = disease_raw.replace("_", " ").title()

    return {
        "crop": crop,
        "disease": disease,
        "cause": [
            f"The exact cause for '{disease}' on {crop} is still being researched.",
            "It may involve fungal, bacterial, viral, or environmental factors.",
        ],
        "treatment": [
            "Isolate affected plants immediately to prevent further spread.",
            "Remove and safely dispose of visibly infected leaves or plant parts.",
            "Consult your local agricultural extension office or KVK for diagnosis.",
            "Consider sending a sample to a plant pathology lab for confirmation.",
        ],
        "severity": "medium",
    }
