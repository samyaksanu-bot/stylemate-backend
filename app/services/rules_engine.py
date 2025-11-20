"""
RULE ENGINE FOR STYLEMATE V1
Generates outfit templates based on:
- skin tone (non-offensive bucket categories)
- body proportions
- occasion
"""

def skin_tone_palette(tone: str):
    """
    Returns color families that flatter each skin tone,
    based on global fashion guidelines.
    NEVER uses offensive wording.
    """
    palettes = {
        "very_light": ["soft beige", "pastel blue", "sage", "rose", "light navy"],
        "light": ["olive", "earth brown", "sky blue", "warm grey", "marine"],
        "medium": ["forest green", "rust", "charcoal", "navy", "deep teal"],
        "dark": ["burgundy", "emerald", "mustard", "midnight blue", "burnt orange"],
        "unknown": ["black", "white", "navy", "grey"]  # universal safe palette
    }
    return palettes.get(tone, palettes["unknown"])


def occasion_rules(occasion: str):
    """
    Defines silhouette + item guidelines based on user-selected occasion.
    """
    rules = {
        "Office": {
            "tops": ["structured shirt", "tailored blouse", "light knit"],
            "bottoms": ["straight trousers", "ankle chinos", "pencil skirt"],
            "shoes": ["loafers", "minimal sneakers", "formal flats"],
        },
        "Date": {
            "tops": ["soft knit", "fitted tee", "light blouse"],
            "bottoms": ["slim jeans", "flow skirt", "straight trousers"],
            "shoes": ["clean sneakers", "ankle boots", "loafers"]
        },
        "Party": {
            "tops": ["bold shirt", "satin top", "statement tee"],
            "bottoms": ["black jeans", "relaxed trousers", "mini skirt"],
            "shoes": ["boots", "chunky sneakers", "dress shoes"]
        },
        "Casual": {
            "tops": ["crew tee", "relaxed shirt", "hoodie"],
            "bottoms": ["jeans", "cargo pants", "joggers"],
            "shoes": ["sneakers", "slip-ons"]
        },
        "Wedding Guest": {
            "tops": ["dress shirt", "festive kurta", "light blazer"],
            "bottoms": ["formal trousers", "ethnic bottom"],
            "shoes": ["formal shoes", "mojaris"]
        },
        "Travel": {
            "tops": ["overshirt", "graphic tee", "sweatshirt"],
            "bottoms": ["travel joggers", "cargo pants", "shorts"],
            "shoes": ["comfortable sneakers", "slip-ons"]
        }
    }
    return rules.get(occasion, rules["Casual"])  # fallback


def generate_recommendations_for_features(features: dict, occasion: str):
    """
    MAIN RULE ENGINE
    Creates 5 outfit templates using:
    - skin tone palette
    - occasion rules
    - proportions
    """

    tone = features.get("skin_tone", {}).get("tone", "unknown")
    color_palette = skin_tone_palette(tone)

    occ_rules = occasion_rules(occasion)

    # Create 5 outfit templates
    templates = []
    for i in range(5):
        templates.append({
            "top": occ_rules["tops"][i % len(occ_rules["tops"])],
            "bottom": occ_rules["bottoms"][i % len(occ_rules["bottoms"])],
            "shoes": occ_rules["shoes"][i % len(occ_rules["shoes"])],
            "recommended_colors": color_palette[:3]  # top 3 colors
        })

    return templates

