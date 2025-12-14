"""Backfill Sweet.image_url values for seeded sweets.

This project serves sweet images from the frontend's public assets
(`frontend/public/sweets`). Older seed/default values used SVG paths that
don't exist in the current frontend, so this script updates existing rows.

Run with DATABASE_URL pointing to your Railway Postgres.
"""

from sqlmodel import Session, select

from database import engine
from models import Sweet


PLACEHOLDER_IMAGE_URLS = {
    "/sweets/indian.svg",
    "/sweets/chocolate.svg",
    "/sweets/candy.svg",
    "/sweets/cake.svg",
    "/sweets/cookie.svg",
    "/sweets/icecream.svg",
}


NAME_TO_IMAGE_URL: dict[str, str] = {
    # Indian sweets
    "Gulab Jamun": "/sweets/gulab_jamun.jpg",
    "Rasgulla": "/sweets/rasgulla.jpg",
    "Jalebi": "/sweets/jalebi.webp",
    "Ladoo": "/sweets/gulab_jamun.jpg",
    "Barfi": "/sweets/kaju_katli.jpg",
    "Kaju Katli": "/sweets/kaju_katli.jpg",
    "Rasmalai": "/sweets/rasgulla.jpg",
    "Mysore Pak": "/sweets/kaju_katli.jpg",

    # Chocolate
    "Dark Chocolate Bar": "/sweets/dark_chocolate_bark.jpg",
    "Milk Chocolate": "/sweets/wonka-bar.jpeg",
    "Chocolate Truffle": "/sweets/chocolate_truffle.jpg",
    "Ferrero Rocher": "/sweets/chocolate_truffle.jpg",
    "Kit Kat": "/sweets/wonka-bar.jpeg",
    "Snickers": "/sweets/wonka-bar.jpeg",

    # Cookies
    "Chocolate Chip Cookies": "/sweets/chocochip_cookies.jpg",
    "Oreo": "/sweets/chocochip_cookies.jpg",
    "Butter Cookies": "/sweets/butter_cookies.jpg",
    "Coconut Cookies": "/sweets/butter_cookies.jpg",

    # Cakes / pastries
    "Black Forest Cake": "/sweets/red_velvet_cupcake.webp",
    "Vanilla Cupcake": "/sweets/red_velvet_cupcake.webp",
    "Red Velvet Cake": "/sweets/red_velvet_cupcake.webp",
    "Chocolate Pastry": "/sweets/chocolate_brownie.jpg",

    # Candy
    "Lollipop": "/sweets/sour_worms.jpg",
    "Gummy Bears": "/sweets/gummy_bears.jpg",
    "Cotton Candy": "/sweets/sour_worms.jpg",
    "Peppermint Candy": "/sweets/sour_worms.jpg",

    # Ice cream
    "Vanilla Ice Cream": "/sweets/vanilla_icecream_cup.jpg",
    "Chocolate Ice Cream": "/sweets/ice_cream.svg",
    "Strawberry Ice Cream": "/sweets/ice_cream.svg",
    "Mango Ice Cream": "/sweets/mango_kulfi.jpg",
}


def should_backfill(image_url: str | None) -> bool:
    if not image_url:
        return True
    return image_url in PLACEHOLDER_IMAGE_URLS


def backfill() -> None:
    updated = 0
    skipped = 0

    with Session(engine) as session:
        sweets = session.exec(select(Sweet)).all()

        for sweet in sweets:
            mapped = NAME_TO_IMAGE_URL.get(sweet.name)
            if not mapped:
                skipped += 1
                continue

            if not should_backfill(sweet.image_url):
                skipped += 1
                continue

            sweet.image_url = mapped
            session.add(sweet)
            updated += 1

        session.commit()

    print(f"✅ Updated image_url for {updated} sweets")
    print(f"ℹ️  Skipped {skipped} sweets")


if __name__ == "__main__":
    backfill()