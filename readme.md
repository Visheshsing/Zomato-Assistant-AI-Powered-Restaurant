# 🍽 Zomato Assistant – AI-Powered Restaurant Backend with LangChain & Streamlit

This project provides a powerful AI backend to manage restaurant operations like search, booking, ordering, user authentication, reviews, and more using LangChain and SQLAlchemy. It’s intended to be used as the logic layer for an intelligent Streamlit front-end agent.

---

## 🚀 Features

- 🔍 Search restaurants by name, city, cuisine, or rating
- 📋 View full menus by restaurant
- 📅 Book tables with time, guest count, and preferred table
- 🛵 Place food orders with delivery address and item list
- ❌ Cancel existing bookings or orders
- ✍ Submit and fetch restaurant reviews
- 💬 Access restaurant-specific FAQs
- 🔐 Authenticate users with email/password
- 🌟 Get top-rated restaurants in any city

---

## 🧠 Tech Stack

| Layer        | Technology                            |
|--------------|----------------------------------------|
| Language     | Python 3.10+                           |
| Framework    | Streamlit                              |
| Agent System | LangChain with langchain_google_genai |
| ORM          | SQLAlchemy (automap)                   |
| DB Support   | MySQL (via pymysql driver)           |
| Auth         | passlib (bcrypt hashing)             |
| Secrets Mgmt | python-dotenv                        |
| Logging      | Python logging module                |

---

## 🧱 Project Structure

zomato_assistance/
├── app.py # Streamlit app entrypoint
├── agent.py # LangChain agent that invokes the tools
├── sqltool.py # Database operations and business logic
├── db.sql # SQL dump to initialize the database schema
├── facker.py # Faker script to populate the database with sample data
├── requirements.txt # Python dependencies
├── .env # Environment configuration (DB credentials, etc.)
└── README.md # This documentation



---

## 🔧 Setup Instructions
   - 2️⃣ Create and activate a virtual environment
   - bash
   - Copy
   - Edit
   - python3 -m venv venv
   - source venv/bin/activate  # macOS/Linux
# .\venv\Scripts\activate  # Windows
### 1️⃣ Clone the repository

    bash
    git clone https://github.com/your-username/zomato_assistance.git
    cd zomato_assistance

    3️⃣ Install dependencies
    bash
    Copy
    Edit
    pip install -r requirements.txt 