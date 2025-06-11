from langchain.tools import tool
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import urllib.parse
from dotenv import load_dotenv
from passlib.context import CryptContext
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = urllib.parse.quote(os.getenv("DB_PASSWORD"))
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base = automap_base()
Base.prepare(engine, reflect=True)

# Mapped tables
Restaurant = Base.classes.restaurants
Menu = Base.classes.menus
Booking = Base.classes.bookings
Table = Base.classes.tables
Order = Base.classes.orders
OrderItem = Base.classes.order_items
FAQ = Base.classes.faqs
Review = Base.classes.reviews
User = Base.classes.users

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def model_to_dict(row):
    """Convert SQLAlchemy model instance to dictionary."""
    return {column.name: getattr(row, column.name) for column in row._table_.columns}

class RestaurantAssistantTools:
    def __init__(self, session):
        self.session = session

    def get_restaurant_by_name(self, name: str, city: str = None):
        name_lower = name.lower()
        query = self.session.query(Restaurant).filter(func.lower(Restaurant.name).like(f"%{name_lower}%"))
        if city:
            city_lower = city.lower()
            query = query.filter(func.lower(Restaurant.city).like(f"%{city_lower}%"))
        return query.first()

    def get_menu_item_by_name(self, restaurant_id: int, item_name: str):
        item_name_lower = item_name.lower()
        return self.session.query(Menu).filter_by(restaurant_id=restaurant_id).filter(
            func.lower(Menu.item_name).like(f"%{item_name_lower}%")
        ).first()

    def search_restaurants(self, name: str = None, city: str = None, cuisine: str = None, min_rating: float = None):
        query = self.session.query(Restaurant)
        if name:
            query = query.filter(func.lower(Restaurant.name).like(f"%{name.lower()}%"))
        if city:
            query = query.filter(func.lower(Restaurant.city).like(f"%{city.lower()}%"))
        if cuisine:
            query = query.filter(func.lower(Restaurant.cuisine).like(f"%{cuisine.lower()}%"))
        if min_rating:
            query = query.filter(Restaurant.rating >= min_rating)
        return [model_to_dict(r) for r in query.all()]

    def get_menu(self, restaurant_name: str, city: str = None):
        restaurant = self.get_restaurant_by_name(restaurant_name, city)
        if not restaurant:
            return {"error": "Restaurant not found"}
        items = self.session.query(Menu).filter_by(restaurant_id=restaurant.id).all()
        return [model_to_dict(i) for i in items]

    def get_available_tables(self, restaurant_name: str, city: str = None):
        restaurant = self.get_restaurant_by_name(restaurant_name, city)
        if not restaurant:
            return {"error": "Restaurant not found"}
        tables = self.session.query(Table).filter_by(restaurant_id=restaurant.id, is_available=True).all()
        return [model_to_dict(t) for t in tables]

    def book_table(self, restaurant_name: str, customer_name: str, booking_time: str,
                   contact_number: str, num_people: int, table_number: int, city: str = None):
        try:
            restaurant = self.get_restaurant_by_name(restaurant_name, city)
            if not restaurant:
                return {"error": "Restaurant not found"}
            
            table = self.session.query(Table).filter_by(restaurant_id=restaurant.id, table_number=table_number).first()
            if not table:
                return {"error": "Table not found"}

            try:
                booking_dt = datetime.strptime(booking_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return {"error": "Invalid booking_time format. Use 'YYYY-MM-DD HH:MM:SS'"}

            booking = Booking(
                restaurant_id=restaurant.id,
                table_id=table.id,
                customer_name=customer_name,
                booking_time=booking_dt,
                contact_number=contact_number,
                num_people=num_people,
                status="booked"
            )
            self.session.add(booking)
            self.session.commit()
            logger.info(f"Booked table {table_number} at {restaurant_name} for {customer_name} at {booking_time}")
            return {"message": "Table booked successfully", "booking_id": booking.id}
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error booking table: {e}")
            return {"error": str(e)}

    def place_order(self, restaurant_name: str, customer_name: str, items: list,
                    delivery_address: str, contact_number: str, city: str = None):
        try:
            restaurant = self.get_restaurant_by_name(restaurant_name, city)
            if not restaurant:
                return {"error": "Restaurant not found"}

            order = Order(
                restaurant_id=restaurant.id,
                customer_name=customer_name,
                delivery_address=delivery_address,
                contact_number=contact_number,
                status="pending"
            )
            self.session.add(order)
            self.session.flush()

            total = 0
            for item in items:
                menu_item = self.get_menu_item_by_name(restaurant.id, item["name"])
                if not menu_item:
                    self.session.rollback()
                    return {"error": f"Menu item '{item['name']}' not found"}
                quantity = item["quantity"]
                total += menu_item.price * quantity
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=menu_item.id,
                    quantity=quantity,
                    item_price=menu_item.price
                )
                self.session.add(order_item)

            order.total_amount = total
            self.session.commit()
            logger.info(f"Placed order {order.id} at {restaurant_name} for {customer_name}, total ${total}")
            return {"message": "Order placed", "order_id": order.id}
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error placing order: {e}")
            return {"error": str(e)}

    def cancel_order(self, order_id: int):
        try:
            order = self.session.query(Order).filter_by(id=order_id).first()
            if not order:
                return {"error": "Order not found"}
            order.status = "cancelled"
            self.session.commit()
            logger.info(f"Cancelled order {order_id}")
            return {"message": "Order cancelled"}
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error cancelling order: {e}")
            return {"error": str(e)}

    def cancel_booking(self, booking_id: int):
        try:
            booking = self.session.query(Booking).filter_by(id=booking_id).first()
            if not booking:
                return {"error": "Booking not found"}
            booking.status = "cancelled"
            self.session.commit()
            logger.info(f"Cancelled booking {booking_id}")
            return {"message": "Booking cancelled"}
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error cancelling booking: {e}")
            return {"error": str(e)}

    def submit_review(self, restaurant_name: str, customer_name: str, rating: int, comment: str, city: str = None):
        try:
            restaurant = self.get_restaurant_by_name(restaurant_name, city)
            if not restaurant:
                return {"error": "Restaurant not found"}
            review = Review(
                restaurant_id=restaurant.id,
                customer_name=customer_name,
                rating=rating,
                comment=comment
            )
            self.session.add(review)
            self.session.commit()
            logger.info(f"Review submitted for {restaurant_name} by {customer_name}")
            return {"message": "Review submitted successfully"}
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error submitting review: {e}")
            return {"error": str(e)}

    def get_faqs(self, restaurant_name: str, city: str = None):
        restaurant = self.get_restaurant_by_name(restaurant_name, city)
        if not restaurant:
            return {"error": "Restaurant not found"}
        faqs = self.session.query(FAQ).filter_by(restaurant_id=restaurant.id).all()
        return [model_to_dict(f) for f in faqs]

    def authenticate_user(self, email: str, password: str):
        try:
            user = self.session.query(User).filter_by(email=email).first()
            if user and pwd_context.verify(password, user.password):
                logger.info(f"User {email} logged in successfully")
                return {"message": "Login successful", "user_id": user.id}
            return {"error": "Invalid email or password"}
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return {"error": str(e)}

    def get_top_restaurants(self, city: str = None, limit: int = 5):
        """Get top N restaurants by rating in a given city (if provided)."""
        try:
            query = self.session.query(Restaurant)
            if city:
                query = query.filter(func.lower(Restaurant.city).like(f"%{city.lower()}%"))
            query = query.order_by(Restaurant.rating.desc()).limit(limit)
            top_restaurants = query.all()
            return [model_to_dict(r) for r in top_restaurants]
        except Exception as e:
            logger.error(f"Error fetching top restaurants: {e}")
            return {"error": str(e)}

# Shared session for agent
shared_session = session