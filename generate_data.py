"""
generate_data.py
-----------------
Builds a SQLite database (ecommerce.db) from schema.sql and populates it
with ~2 years of realistic, randomly generated e-commerce data:
    - 250 customers
    - 8 categories, 60 products
    - ~1,500 orders
    - ~4,000 order line items

Run: python generate_data.py
"""

import sqlite3
import random
from datetime import date, timedelta

random.seed(42)  # reproducible results

DB_PATH = "ecommerce.db"
SCHEMA_PATH = "schema.sql"

# ------------------------------------------------------------------
# Reference data
# ------------------------------------------------------------------

FIRST_NAMES = ["Aarav","Vivaan","Aditya","Priya","Ananya","Diya","Kabir","Ishaan",
               "Meera","Rohan","Sanya","Kunal","Neha","Arjun","Pooja","Karan",
               "Riya","Aman","Simran","Yash","Tanvi","Nikhil","Sara","Dev","Anika"]
LAST_NAMES = ["Sharma","Verma","Gupta","Iyer","Reddy","Nair","Singh","Patel",
              "Mehta","Chopra","Malhotra","Rao","Kapoor","Joshi","Bhat"]

CITIES_STATES = [
    ("Mumbai","Maharashtra"), ("Delhi","Delhi"), ("Bengaluru","Karnataka"),
    ("Hyderabad","Telangana"), ("Chennai","Tamil Nadu"), ("Kolkata","West Bengal"),
    ("Pune","Maharashtra"), ("Ahmedabad","Gujarat"), ("Jaipur","Rajasthan"),
    ("Lucknow","Uttar Pradesh"), ("Chandigarh","Chandigarh"), ("Surat","Gujarat"),
]

SEGMENTS = ["Consumer","Corporate","Small Business"]

CATEGORIES = ["Electronics","Home & Kitchen","Apparel","Sports & Fitness",
              "Books & Stationery","Beauty & Personal Care","Toys & Games","Furniture"]

PRODUCTS_BY_CATEGORY = {
    "Electronics": ["Wireless Earbuds","Bluetooth Speaker","Smartwatch","Power Bank 10000mAh",
                    "USB-C Charger","Laptop Stand","Webcam HD","Mechanical Keyboard"],
    "Home & Kitchen": ["Non-stick Pan","Electric Kettle","Air Fryer","Mixer Grinder",
                       "Vacuum Flask","Dinner Set 24pc","LED Table Lamp"],
    "Apparel": ["Cotton T-Shirt","Denim Jeans","Running Shoes","Formal Shirt",
                "Winter Jacket","Casual Sneakers"],
    "Sports & Fitness": ["Yoga Mat","Dumbbell Set 10kg","Resistance Bands","Skipping Rope",
                          "Cricket Bat","Badminton Racket"],
    "Books & Stationery": ["Notebook Pack of 5","Gel Pen Set","Sketchbook A4","Desk Organizer",
                            "Fiction Novel","Self-help Book"],
    "Beauty & Personal Care": ["Face Wash","Moisturizer 200ml","Hair Serum","Sunscreen SPF50",
                                "Electric Trimmer","Perfume 100ml"],
    "Toys & Games": ["Building Blocks Set","Remote Control Car","Puzzle 1000pc","Board Game",
                      "Soft Toy Bear","Drawing Kit"],
    "Furniture": ["Office Chair","Study Table","Bookshelf 5-tier","Bean Bag",
                  "Bedside Table","Shoe Rack"],
}

START_DATE = date(2024, 1, 1)
END_DATE = date(2025, 12, 31)


def random_date(start: date, end: date) -> date:
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


def build_schema(conn):
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())


def generate_customers(n=250):
    customers = []
    for cid in range(1, n + 1):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        city, state = random.choice(CITIES_STATES)
        signup = random_date(START_DATE, END_DATE - timedelta(days=30))
        segment = random.choices(SEGMENTS, weights=[0.6, 0.2, 0.2])[0]
        email = name.lower().replace(" ", ".") + f"{cid}@example.com"
        customers.append((cid, name, email, city, state, signup.isoformat(), segment))
    return customers


def generate_categories():
    return [(i + 1, cat) for i, cat in enumerate(CATEGORIES)]


def generate_products(categories):
    products = []
    pid = 1
    cat_name_to_id = {name: i + 1 for i, name in enumerate(CATEGORIES)}
    for cat_name, items in PRODUCTS_BY_CATEGORY.items():
        cat_id = cat_name_to_id[cat_name]
        for item in items:
            unit_cost = round(random.uniform(100, 4000), 2)
            markup = random.uniform(1.3, 2.2)
            unit_price = round(unit_cost * markup, 2)
            products.append((pid, item, cat_id, unit_price, unit_cost))
            pid += 1
    return products


def generate_orders_and_items(customers, products, n_orders=1500):
    orders = []
    items = []
    order_item_id = 1

    # Give some customers more orders than others (realistic skew)
    customer_ids = [c[0] for c in customers]
    weights = [random.random() ** 2 for _ in customer_ids]  # skewed towards fewer big buyers

    for oid in range(1, n_orders + 1):
        cust_id = random.choices(customer_ids, weights=weights)[0]
        # order date must be after customer signup
        signup = next(c[5] for c in customers if c[0] == cust_id)
        signup_date = date.fromisoformat(signup)
        order_date = random_date(signup_date, END_DATE)

        status = random.choices(
            ["Completed", "Cancelled", "Returned"],
            weights=[0.85, 0.08, 0.07]
        )[0]

        ship_state = next(c[4] for c in customers if c[0] == cust_id)

        orders.append((oid, cust_id, order_date.isoformat(), status, ship_state))

        # 1-5 line items per order
        n_items = random.randint(1, 5)
        chosen_products = random.sample(products, n_items)
        for prod in chosen_products:
            qty = random.randint(1, 4)
            price_at_sale = prod[3]  # unit_price at time of generation
            items.append((order_item_id, oid, prod[0], qty, price_at_sale))
            order_item_id += 1

    return orders, items


def main():
    conn = sqlite3.connect(DB_PATH)
    build_schema(conn)

    customers = generate_customers()
    categories = generate_categories()
    products = generate_products(categories)
    orders, items = generate_orders_and_items(customers, products)

    conn.executemany(
        "INSERT INTO customers VALUES (?,?,?,?,?,?,?)", customers
    )
    conn.executemany(
        "INSERT INTO categories VALUES (?,?)", categories
    )
    conn.executemany(
        "INSERT INTO products VALUES (?,?,?,?,?)", products
    )
    conn.executemany(
        "INSERT INTO orders VALUES (?,?,?,?,?)", orders
    )
    conn.executemany(
        "INSERT INTO order_items VALUES (?,?,?,?,?)", items
    )

    conn.commit()

    print(f"Database built: {DB_PATH}")
    print(f"  customers:   {len(customers)}")
    print(f"  categories:  {len(categories)}")
    print(f"  products:    {len(products)}")
    print(f"  orders:      {len(orders)}")
    print(f"  order_items: {len(items)}")

    conn.close()


if __name__ == "__main__":
    main()
