"""
Recommender system for mapping outfit templates
to real products from the database.
"""

import random
from sqlmodel import select
from app.db.session import get_session_sync
from app.db.models import Product


def fetch_products_by_tags(tags: list[str]):
    """
    Fetches products whose tags match any of the desired tags.
    If no match found, returns random fallback items.
    """
    with get_session_sync() as session:
        stmt = select(Product)
        all_products = session.exec(stmt).all()

    # Filter products
    results = []
    for p in all_products:
        for tag in tags:
            if tag.lower() in p.tags.lower():
                results.append(p)
                break

    # If empty, fallback to random 10 products
    if not results:
        random.shuffle(all_products)
        return all_products[:10]

    return results


def pick_random_product(products):
    """
    Return a random product from the list.
    """
    if not products:
        return None
    return random.choice(products)


def map_templates_to_products(templates: list[dict]):
    """
    Convert rule-engine templates to real product picks.
    Each template returns:
    - top product
    - bottom product
    - shoes product
    - color recommendation
    """

    final = []

    for t in templates:
        # Convert template to product search tags
        tags_top = [t["top"]]
        tags_bottom = [t["bottom"]]
        tags_shoes = [t["shoes"]]

        # Fetch products
        top_options = fetch_products_by_tags(tags_top)
        bottom_options = fetch_products_by_tags(tags_bottom)
        shoe_options = fetch_products_by_tags(tags_shoes)

        final.append({
            "top": pick_random_product(top_options),
            "bottom": pick_random_product(bottom_options),
            "shoes": pick_random_product(shoe_options),
            "recommended_colors": t["recommended_colors"]
        })

    return [convert_product_response(o) for o in final]


def convert_product_response(block):
    """
    Convert SQLModel objects into JSON-friendly format.
    """

    def format_prod(p):
        if p is None:
            return None
        return {
            "id": p.id,
            "name": p.name,
            "image_url": p.image_url,
            "price": p.price,
            "category": p.category,
            "color": p.color,
            "tags": p.tags,
            "link": p.link
        }

    return {
        "top": format_prod(block["top"]),
        "bottom": format_prod(block["bottom"]),
        "shoes": format_prod(block["shoes"]),
        "recommended_colors": block["recommended_colors"]
    }


