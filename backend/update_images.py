"""Update sweet image URLs in the database to match uploaded images."""
from database import engine
from sqlalchemy import text

# Mapping sweet names (from DB) to image filenames
IMAGE_MAP = {
    "Butter Cookies": "/sweets/butter_cookies.jpg",
    "Choco Chip Cookies": "/sweets/chocochip_cookies.jpg",
    "Chocolate Brownie": "/sweets/chocolate_brownie.jpg",
    "Chocolate Truffle": "/sweets/chocolate_truffle.jpg",
    "Dark Chocolate Bark": "/sweets/dark_chocolate_bark.jpg",
    "Gulab Jamun": "/sweets/gulab_jamun.jpg",
    "Gummy Bears": "/sweets/gummy_bears.jpg",
    "Jalebi": "/sweets/jalebi.webp",
    "Kaju Katli": "/sweets/kaju_katli.jpg",
    "Mango Kulfi": "/sweets/mango_kulfi.jpg",
    "Rasgulla": "/sweets/rasgulla.jpg",
    "Red Velvet Cupcake": "/sweets/red_velvet_cupcake.webp",
    "Sour Worms": "/sweets/sour_worms.jpg",
    "Vanilla Ice Cream Cup": "/sweets/vanilla_icecream_cup.jpg",
    "Wonka Bar": "/sweets/wonka-bar.jpeg",
}

def update_images():
    with engine.connect() as conn:
        updated = 0
        for sweet_name, image_url in IMAGE_MAP.items():
            result = conn.execute(
                text("UPDATE sweet SET image_url = :img WHERE name = :name"),
                {"img": image_url, "name": sweet_name}
            )
            if result.rowcount > 0:
                updated += result.rowcount
                print(f"✓ Updated: {sweet_name} -> {image_url}")
        conn.commit()
        print(f"\n✅ Total updated: {updated} sweets")

if __name__ == "__main__":
    update_images()
