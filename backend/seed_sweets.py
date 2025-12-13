from __future__ import annotations

from sqlmodel import Session, select

from database import create_db_and_tables, engine
from models import Sweet


def _default_image_url_for_category(category: str) -> str | None:
    normalized = (category or "").strip().lower().replace(" ", "_")
    mapping: dict[str, str] = {
        "indian": "/sweets/indian.svg",
        "chocolate": "/sweets/chocolate.svg",
        "candy": "/sweets/candy.svg",
        "cake": "/sweets/cake.svg",
        "cookie": "/sweets/cookie.svg",
        "ice_cream": "/sweets/ice_cream.svg",
        "ice-cream": "/sweets/ice_cream.svg",
        "icecream": "/sweets/ice_cream.svg",
    }
    return mapping.get(normalized)

SEED_SWEETS: list[Sweet] = [
    Sweet(name="Gulab Jamun", category="Indian", price=3.99, quantity=50, image_url=_default_image_url_for_category("Indian")),
    Sweet(name="Rasgulla", category="Indian", price=3.49, quantity=60, image_url=_default_image_url_for_category("Indian")),
    Sweet(name="Kaju Katli", category="Indian", price=6.99, quantity=40, image_url=_default_image_url_for_category("Indian")),
    Sweet(name="Jalebi", category="Indian", price=2.99, quantity=80, image_url=_default_image_url_for_category("Indian")),
    Sweet(name="Ladoo", category="Indian", price=2.49, quantity=90, image_url=_default_image_url_for_category("Indian")),
    Sweet(name="Barfi", category="Indian", price=4.49, quantity=55, image_url=_default_image_url_for_category("Indian")),
    Sweet(name="Soan Papdi", category="Indian", price=3.29, quantity=70, image_url=_default_image_url_for_category("Indian")),
    Sweet(name="Mysore Pak", category="Indian", price=4.99, quantity=45, image_url=_default_image_url_for_category("Indian")),

    Sweet(name="Chocolate Truffle", category="Chocolate", price=4.99, quantity=40, image_url=_default_image_url_for_category("Chocolate")),
    Sweet(name="Dark Chocolate Bark", category="Chocolate", price=5.49, quantity=35, image_url=_default_image_url_for_category("Chocolate")),
    Sweet(name="Chocolate Fudge", category="Chocolate", price=4.59, quantity=50, image_url=_default_image_url_for_category("Chocolate")),

    Sweet(name="Gummy Bears", category="Candy", price=2.19, quantity=120, image_url=_default_image_url_for_category("Candy")),
    Sweet(name="Sour Worms", category="Candy", price=2.49, quantity=110, image_url=_default_image_url_for_category("Candy")),
    Sweet(name="Lollipop", category="Candy", price=1.29, quantity=200, image_url=_default_image_url_for_category("Candy")),
    Sweet(name="Caramel Toffee", category="Candy", price=2.79, quantity=95, image_url=_default_image_url_for_category("Candy")),

    Sweet(name="Red Velvet Cupcake", category="Cake", price=3.75, quantity=30, image_url=_default_image_url_for_category("Cake")),
    Sweet(name="Cheesecake Slice", category="Cake", price=4.25, quantity=28, image_url=_default_image_url_for_category("Cake")),
    Sweet(name="Chocolate Brownie", category="Cake", price=3.25, quantity=44, image_url=_default_image_url_for_category("Cake")),

    Sweet(name="Butter Cookies", category="Cookie", price=2.99, quantity=75, image_url=_default_image_url_for_category("Cookie")),
    Sweet(name="Choco Chip Cookies", category="Cookie", price=3.19, quantity=80, image_url=_default_image_url_for_category("Cookie")),

    Sweet(name="Vanilla Ice Cream Cup", category="Ice_Cream", price=2.89, quantity=65, image_url=_default_image_url_for_category("Ice_Cream")),
    Sweet(name="Mango Kulfi", category="Ice_Cream", price=3.39, quantity=55, image_url=_default_image_url_for_category("Ice_Cream")),
]


def seed() -> None:
    create_db_and_tables()

    with Session(engine) as session:
        # Backfill image_url for existing records (created before this feature existed)
        existing_sweets = session.exec(select(Sweet)).all()
        backfilled = 0
        for sweet in existing_sweets:
            if not getattr(sweet, "image_url", None):
                sweet.image_url = _default_image_url_for_category(sweet.category)
                session.add(sweet)
                backfilled += 1

        existing_names = set(session.exec(select(Sweet.name)).all())

        inserted = 0
        for sweet in SEED_SWEETS:
            if sweet.name in existing_names:
                continue
            session.add(sweet)
            inserted += 1

        session.commit()

        total = session.exec(select(Sweet)).all()

    print(f"Inserted: {inserted}")
    print(f"Backfilled image_url for: {backfilled}")
    print(f"Total sweets in DB: {len(total)}")


if __name__ == "__main__":
    seed()
