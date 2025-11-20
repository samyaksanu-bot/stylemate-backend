from sqlmodel import Session
from app.db.session import create_db_and_tables, engine
from app.db.models import Product
import uuid


def seed_products():
    sample_products = [
        {
            "name": "White Structured Shirt",
            "image_url": "https://example.com/shirt1.jpg",
            "price": 1499,
            "category": "top",
            "color": "white",
            "tags": "structured shirt office minimal",
            "link": "#"
        },
        {
            "name": "Navy Slim Chinos",
            "image_url": "https://example.com/chinos1.jpg",
            "price": 1799,
            "category": "bottom",
            "color": "navy",
            "tags": "chinos smart casual office",
            "link": "#"
        },
        {
            "name": "Formal Brown Loafers",
            "image_url": "https://example.com/shoes1.jpg",
            "price": 2499,
            "category": "shoes",
            "color": "brown",
            "tags": "loafers formal office",
            "link": "#"
        },
        {
            "name": "Black Jeans",
            "image_url": "https://example.com/jeans.jpg",
            "price": 1299,
            "category": "bottom",
            "color": "black",
            "tags": "jeans casual party",
            "link": "#"
        },
        {
            "name": "Beige Overshirt",
            "image_url": "https://example.com/overshirt.jpg",
            "price": 2199,
            "category": "top",
            "color": "beige",
            "tags": "overshirt travel casual",
            "link": "#"
        }
    ]

    create_db_and_tables()

    with Session(engine) as session:
        for p in sample_products:
            prod = Product(
                id=str(uuid.uuid4()),
                name=p["name"],
                image_url=p["image_url"],
                price=p["price"],
                category=p["category"],
                color=p["color"],
                tags=p["tags"],
                link=p["link"]
            )
            session.add(prod)

        session.commit()
        print("Seeded sample products successfully!")


if __name__ == "__main__":
    seed_products()




