import mysql.connector
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

# Connect to MySQL (update credentials)
db = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="Vish@8840",
    database="zomato"
)

cursor = db.cursor()

# Clear tables to avoid duplicates (optional, careful on prod!)
tables_to_clear = ['order_items', 'orders', 'bookings', 'menus', 'reviews', 'faqs', 'tables', 'users', 'restaurants']
for tbl in tables_to_clear:
    cursor.execute(f"DELETE FROM {tbl}")
db.commit()

def insert_restaurants(n=1000):
    print("Inserting restaurants...")
    cuisines = ['Italian', 'Chinese', 'Indian', 'Mexican', 'French', 'Japanese', 'Mediterranean', 'Thai', 'American']
    for _ in range(n):
        name = fake.company()
        address = fake.address().replace('\n', ', ')
        city = fake.city()
        state = fake.state()
        zipcode = fake.zipcode()
        cuisine = random.choice(cuisines)
        rating = round(random.uniform(1.0, 5.0), 1)
        phone = fake.phone_number()
        opening_hours = "Mon-Sun 10:00 AM - 10:00 PM"
        avg_cost = random.randint(10, 100) * 10
        image_url = fake.image_url(width=640, height=480)
        
        cursor.execute("""
            INSERT INTO restaurants (name, address, city, state, zipcode, cuisine, rating, phone, opening_hours, avg_cost_for_two, image_url)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (name, address, city, state, zipcode, cuisine, rating, phone, opening_hours, avg_cost, image_url))
    db.commit()

def insert_users(n=500):
    print("Inserting users...")
    for _ in range(n):
        name = fake.name()
        email = fake.unique.email()
        phone = fake.phone_number()
        password = fake.password(length=12)
        cursor.execute("""
            INSERT INTO users (name, email, phone, password)
            VALUES (%s,%s,%s,%s)
        """, (name, email, phone, password))
    db.commit()

def insert_tables_per_restaurant(max_tables=10):
    print("Inserting tables...")
    cursor.execute("SELECT id FROM restaurants")
    restaurant_ids = [row[0] for row in cursor.fetchall()]
    for rid in restaurant_ids:
        num_tables = random.randint(1, max_tables)
        for tnum in range(1, num_tables+1):
            capacity = random.choice([2, 4, 6, 8])
            is_available = 1
            cursor.execute("""
                INSERT INTO tables (restaurant_id, table_number, capacity, is_available)
                VALUES (%s,%s,%s,%s)
            """, (rid, tnum, capacity, is_available))
    db.commit()

def insert_menus_per_restaurant(max_items=20):
    print("Inserting menus...")
    categories = ['Appetizer', 'Main Course', 'Dessert', 'Beverage']
    cursor.execute("SELECT id FROM restaurants")
    restaurant_ids = [row[0] for row in cursor.fetchall()]
    for rid in restaurant_ids:
        num_items = random.randint(5, max_items)
        for _ in range(num_items):
            item_name = fake.word().capitalize() + " " + random.choice(['Soup','Salad','Pizza','Pasta','Burger','Sushi','Steak'])
            category = random.choice(categories)
            price = round(random.uniform(5.0, 50.0), 2)
            description = fake.sentence(nb_words=10)
            availability = random.choice([0, 1])
            cursor.execute("""
                INSERT INTO menus (restaurant_id, item_name, category, price, description, availability)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (rid, item_name, category, price, description, availability))
    db.commit()

def insert_bookings(n=1000):
    print("Inserting bookings...")
    cursor.execute("SELECT id FROM restaurants")
    restaurant_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT id, restaurant_id, capacity FROM tables")
    tables = cursor.fetchall()  # [(id, restaurant_id, capacity), ...]

    status_choices = ['booked', 'cancelled', 'completed']

    for _ in range(n):
        restaurant_id = random.choice(restaurant_ids)
        # Find tables of this restaurant
        tables_for_rest = [t for t in tables if t[1] == restaurant_id]
        if not tables_for_rest:
            continue
        table = random.choice(tables_for_rest)
        table_id = table[0]
        capacity = table[2]

        customer_name = fake.name()
        booking_time = fake.date_time_between(start_date='-1y', end_date='now')
        contact_number = fake.phone_number()
        num_people = random.randint(1, capacity)
        status = random.choices(status_choices, weights=[0.7, 0.2, 0.1])[0]
        cancellation_reason = None
        cancelled_at = None
        if status == 'cancelled':
            cancellation_reason = fake.sentence()
            cancelled_at = booking_time + timedelta(hours=random.randint(1, 72))
        cursor.execute("""
            INSERT INTO bookings (restaurant_id, table_id, customer_name, booking_time, contact_number, num_people, status, cancellation_reason, cancelled_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (restaurant_id, table_id, customer_name, booking_time, contact_number, num_people, status, cancellation_reason, cancelled_at))
    db.commit()

def insert_orders(n=1000):
    print("Inserting orders...")
    cursor.execute("SELECT id FROM restaurants")
    restaurant_ids = [row[0] for row in cursor.fetchall()]
    status_choices = ['pending', 'completed', 'cancelled']

    for _ in range(n):
        restaurant_id = random.choice(restaurant_ids)
        customer_name = fake.name()
        order_time = fake.date_time_between(start_date='-1y', end_date='now')
        total_amount = round(random.uniform(20.0, 200.0), 2)
        status = random.choices(status_choices, weights=[0.6, 0.3, 0.1])[0]
        delivery_address = fake.address().replace('\n', ', ')
        contact_number = fake.phone_number()
        cancellation_reason = None
        cancelled_at = None
        if status == 'cancelled':
            cancellation_reason = fake.sentence()
            cancelled_at = order_time + timedelta(hours=random.randint(1, 72))
        cursor.execute("""
            INSERT INTO orders (restaurant_id, customer_name, order_time, total_amount, status, delivery_address, contact_number, cancellation_reason, cancelled_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (restaurant_id, customer_name, order_time, total_amount, status, delivery_address, contact_number, cancellation_reason, cancelled_at))
    db.commit()

def insert_order_items():
    print("Inserting order items...")
    cursor.execute("SELECT id FROM orders")
    order_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT id FROM menus WHERE availability = 1")
    menu_item_ids = [row[0] for row in cursor.fetchall()]

    for order_id in order_ids:
        num_items = random.randint(1, 5)
        selected_items = random.sample(menu_item_ids, min(num_items, len(menu_item_ids)))
        for menu_item_id in selected_items:
            quantity = random.randint(1, 3)
            # We need price of menu item
            cursor.execute("SELECT price FROM menus WHERE id = %s", (menu_item_id,))
            price = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO order_items (order_id, menu_item_id, quantity, item_price)
                VALUES (%s,%s,%s,%s)
            """, (order_id, menu_item_id, quantity, price))
    db.commit()

def insert_reviews(n=1000):
    print("Inserting reviews...")
    cursor.execute("SELECT id FROM restaurants")
    restaurant_ids = [row[0] for row in cursor.fetchall()]
    for _ in range(n):
        restaurant_id = random.choice(restaurant_ids)
        customer_name = fake.name()
        rating = random.randint(1, 5)
        comment = fake.sentence(nb_words=15)
        review_time = fake.date_time_between(start_date='-1y', end_date='now')
        cursor.execute("""
            INSERT INTO reviews (restaurant_id, customer_name, rating, comment, review_time)
            VALUES (%s,%s,%s,%s,%s)
        """, (restaurant_id, customer_name, rating, comment, review_time))
    db.commit()

def insert_faqs():
    print("Inserting FAQs...")
    cursor.execute("SELECT id FROM restaurants")
    restaurant_ids = [row[0] for row in cursor.fetchall()]
    
    faq_samples = [
    ("What are your opening hours?", "We are open daily from 10:00 AM to 10:00 PM."),
    ("Do you offer vegetarian options?", "Yes, we have a variety of vegetarian dishes."),
    ("Is parking available?", "Yes, free parking is available for customers."),
    ("Do you accept credit cards?", "Yes, all major credit cards are accepted."),
    ("Do you accept reservations?", "Yes, you can book a table via our website or phone."),
    ("Is there outdoor seating?", "Yes, we have a beautiful outdoor patio."),
    ("Are pets allowed?", "Pets are welcome in our outdoor seating area."),
    ("Do you provide Wi-Fi?", "Free Wi-Fi is available for all customers."),
    ("Are gluten-free dishes available?", "Yes, we offer gluten-free options."),
    ("Do you have a kids' menu?", "Yes, we offer a special menu for children."),
    ("Can I order takeout?", "Yes, takeout orders can be placed online or by phone."),
    ("Do you offer delivery?", "We partner with local delivery services."),
    ("Are you wheelchair accessible?", "Yes, our restaurant is fully accessible."),
    ("Do you have vegan options?", "Yes, several vegan dishes are available."),
    ("Do you cater private events?", "Yes, contact us for event bookings."),
    ("What is your cancellation policy?", "Reservations can be cancelled up to 2 hours in advance."),
    ("Is gratuity included?", "No, gratuity is not included and is optional."),
    ("Do you allow BYOB (bring your own bottle)?", "No, we do not allow outside beverages."),
    ("Are there any ongoing promotions?", "Check our website for current offers."),
    ("What COVID-19 measures do you follow?", "We follow all local guidelines for safety and sanitation."),
]

    for rid in restaurant_ids:
        num_faqs = random.randint(1, 4)
        for _ in range(num_faqs):
            q, a = random.choice(faq_samples)
            cursor.execute("""
                INSERT INTO faqs (restaurant_id, question, answer)
                VALUES (%s,%s,%s)
            """, (rid, q, a))
    db.commit()


if __name__ == "__main__":
    insert_restaurants(1000)
    insert_users(500)
    insert_tables_per_restaurant(10)
    insert_menus_per_restaurant(20)
    insert_bookings(1000)
    insert_orders(1000)
    insert_order_items()
    insert_reviews(1000)
    insert_faqs()
    print("Data generation completed!")
    cursor.close()
    db.close()