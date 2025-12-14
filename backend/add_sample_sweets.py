"""
Script to populate the database with sample sweets.
Run this to add initial sweets inventory to your database.
"""
from sqlmodel import Session, select
from database import engine
from models import Sweet

def add_sample_sweets():
    """Add sample sweets to the database."""

    name_to_image_url = {
        "Gulab Jamun": "/sweets/gulab_jamun.jpg",
        "Rasgulla": "/sweets/rasgulla.jpg",
        "Jalebi": "/sweets/jalebi.webp",
        "Ladoo": "/sweets/gulab_jamun.jpg",
        "Barfi": "/sweets/kaju_katli.jpg",
        "Kaju Katli": "/sweets/kaju_katli.jpg",
        "Rasmalai": "/sweets/rasgulla.jpg",
        "Mysore Pak": "/sweets/kaju_katli.jpg",
        "Dark Chocolate Bar": "/sweets/dark_chocolate_bark.jpg",
        "Milk Chocolate": "/sweets/wonka-bar.jpeg",
        "Chocolate Truffle": "/sweets/chocolate_truffle.jpg",
        "Ferrero Rocher": "/sweets/chocolate_truffle.jpg",
        "Kit Kat": "/sweets/wonka-bar.jpeg",
        "Snickers": "/sweets/wonka-bar.jpeg",
        "Chocolate Chip Cookies": "/sweets/chocochip_cookies.jpg",
        "Oreo": "/sweets/chocochip_cookies.jpg",
        "Butter Cookies": "/sweets/butter_cookies.jpg",
        "Coconut Cookies": "/sweets/butter_cookies.jpg",
        "Black Forest Cake": "/sweets/red_velvet_cupcake.webp",
        "Vanilla Cupcake": "/sweets/red_velvet_cupcake.webp",
        "Red Velvet Cake": "/sweets/red_velvet_cupcake.webp",
        "Chocolate Pastry": "/sweets/chocolate_brownie.jpg",
        "Lollipop": "/sweets/sour_worms.jpg",
        "Gummy Bears": "/sweets/gummy_bears.jpg",
        "Cotton Candy": "/sweets/sour_worms.jpg",
        "Peppermint Candy": "/sweets/sour_worms.jpg",
        "Vanilla Ice Cream": "/sweets/vanilla_icecream_cup.jpg",
        "Chocolate Ice Cream": "/sweets/ice_cream.svg",
        "Strawberry Ice Cream": "/sweets/ice_cream.svg",
        "Mango Ice Cream": "/sweets/mango_kulfi.jpg",
    }
    
    sample_sweets = [
        # Indian Sweets
        {"name": "Gulab Jamun", "category": "Indian", "price": 50.0, "quantity": 100, "image_url": name_to_image_url["Gulab Jamun"]},
        {"name": "Rasgulla", "category": "Indian", "price": 45.0, "quantity": 80, "image_url": name_to_image_url["Rasgulla"]},
        {"name": "Jalebi", "category": "Indian", "price": 40.0, "quantity": 120, "image_url": name_to_image_url["Jalebi"]},
        {"name": "Ladoo", "category": "Indian", "price": 60.0, "quantity": 90, "image_url": name_to_image_url["Ladoo"]},
        {"name": "Barfi", "category": "Indian", "price": 70.0, "quantity": 75, "image_url": name_to_image_url["Barfi"]},
        {"name": "Kaju Katli", "category": "Indian", "price": 150.0, "quantity": 50, "image_url": name_to_image_url["Kaju Katli"]},
        {"name": "Rasmalai", "category": "Indian", "price": 80.0, "quantity": 60, "image_url": name_to_image_url["Rasmalai"]},
        {"name": "Mysore Pak", "category": "Indian", "price": 90.0, "quantity": 65, "image_url": name_to_image_url["Mysore Pak"]},
        
        # Chocolate Sweets
        {"name": "Dark Chocolate Bar", "category": "Chocolate", "price": 120.0, "quantity": 100, "image_url": name_to_image_url["Dark Chocolate Bar"]},
        {"name": "Milk Chocolate", "category": "Chocolate", "price": 100.0, "quantity": 150, "image_url": name_to_image_url["Milk Chocolate"]},
        {"name": "Chocolate Truffle", "category": "Chocolate", "price": 200.0, "quantity": 40, "image_url": name_to_image_url["Chocolate Truffle"]},
        {"name": "Ferrero Rocher", "category": "Chocolate", "price": 250.0, "quantity": 80, "image_url": name_to_image_url["Ferrero Rocher"]},
        {"name": "Kit Kat", "category": "Chocolate", "price": 50.0, "quantity": 200, "image_url": name_to_image_url["Kit Kat"]},
        {"name": "Snickers", "category": "Chocolate", "price": 40.0, "quantity": 180, "image_url": name_to_image_url["Snickers"]},
        
        # Cookies & Biscuits
        {"name": "Chocolate Chip Cookies", "category": "Cookies", "price": 80.0, "quantity": 120, "image_url": name_to_image_url["Chocolate Chip Cookies"]},
        {"name": "Oreo", "category": "Cookies", "price": 30.0, "quantity": 200, "image_url": name_to_image_url["Oreo"]},
        {"name": "Butter Cookies", "category": "Cookies", "price": 60.0, "quantity": 100, "image_url": name_to_image_url["Butter Cookies"]},
        {"name": "Coconut Cookies", "category": "Cookies", "price": 70.0, "quantity": 90, "image_url": name_to_image_url["Coconut Cookies"]},
        
        # Cakes & Pastries
        {"name": "Black Forest Cake", "category": "Cake", "price": 500.0, "quantity": 20, "image_url": name_to_image_url["Black Forest Cake"]},
        {"name": "Vanilla Cupcake", "category": "Cake", "price": 40.0, "quantity": 150, "image_url": name_to_image_url["Vanilla Cupcake"]},
        {"name": "Red Velvet Cake", "category": "Cake", "price": 600.0, "quantity": 15, "image_url": name_to_image_url["Red Velvet Cake"]},
        {"name": "Chocolate Pastry", "category": "Cake", "price": 80.0, "quantity": 100, "image_url": name_to_image_url["Chocolate Pastry"]},
        
        # Candies
        {"name": "Lollipop", "category": "Candy", "price": 10.0, "quantity": 300, "image_url": name_to_image_url["Lollipop"]},
        {"name": "Gummy Bears", "category": "Candy", "price": 50.0, "quantity": 200, "image_url": name_to_image_url["Gummy Bears"]},
        {"name": "Cotton Candy", "category": "Candy", "price": 30.0, "quantity": 100, "image_url": name_to_image_url["Cotton Candy"]},
        {"name": "Peppermint Candy", "category": "Candy", "price": 20.0, "quantity": 250, "image_url": name_to_image_url["Peppermint Candy"]},
        
        # Ice Cream
        {"name": "Vanilla Ice Cream", "category": "Ice Cream", "price": 60.0, "quantity": 80, "image_url": name_to_image_url["Vanilla Ice Cream"]},
        {"name": "Chocolate Ice Cream", "category": "Ice Cream", "price": 70.0, "quantity": 75, "image_url": name_to_image_url["Chocolate Ice Cream"]},
        {"name": "Strawberry Ice Cream", "category": "Ice Cream", "price": 65.0, "quantity": 70, "image_url": name_to_image_url["Strawberry Ice Cream"]},
        {"name": "Mango Ice Cream", "category": "Ice Cream", "price": 80.0, "quantity": 60, "image_url": name_to_image_url["Mango Ice Cream"]},
    ]
    
    with Session(engine) as session:
        added_count = 0
        skipped_count = 0
        
        for sweet_data in sample_sweets:
            try:
                # Check if sweet already exists
                statement = select(Sweet).where(Sweet.name == sweet_data["name"])
                existing = session.exec(statement).first()
                
                if existing:
                    print(f"⚠️  Skipping '{sweet_data['name']}' - already exists")
                    skipped_count += 1
                    continue
                
                # Add new sweet
                sweet = Sweet(**sweet_data)
                session.add(sweet)
                session.commit()  # Commit each sweet individually
                added_count += 1
                print(f"✅ Added: {sweet_data['name']} - {sweet_data['category']} - ₹{sweet_data['price']}")
            except Exception as e:
                session.rollback()  # Rollback on error
                print(f"❌ Error adding '{sweet_data['name']}': {str(e)}")
                skipped_count += 1
        
        print(f"\n{'='*60}")
        print(f"✅ Successfully added {added_count} sweets")
        print(f"⚠️  Skipped {skipped_count} duplicates")
        print(f"{'='*60}")

if __name__ == "__main__":
    add_sample_sweets()
