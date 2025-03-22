from fastapi import FastAPI, BackgroundTasks, Request
import json, random, time
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List

from pathlib import Path
from producer import KafkaProducer
from pymongo import MongoClient
app = FastAPI()
kafka_producer = KafkaProducer()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")



# Event Types
events = [
    'click', 'view', 'purchase', 'add_to_cart', 'wishlist_add', 'wishlist_remove',
    'search', 'filter', 'sort', 'compare', 'review', 'rate', 'recommend', 'share',
    'subscribe', 'return', 'refund', 'cancel_order', 'checkout', 'payment'
]

def generate_user_event():
    return {
        "user_id": random.randint(1, 100),
        "event": random.choice(events),
        "product_id": random.randint(1000, 9999),
        "timestamp": time.time(),
        "device": random.choice(['mobile', 'desktop', 'tablet']),
        "location": random.choice(['USA', 'UK', 'India', 'Canada', 'Germany']),
        "category": random.choice(['electronics', 'fashion', 'home_appliances', 'sports', 'books']),
        "price": round(random.uniform(10, 1000), 2),
        "discount": random.randint(0, 50),
        "stock": random.randint(0, 500),
        "payment_method": random.choice(['credit_card', 'paypal', 'debit_card', 'crypto', 'net_banking']),
        "loyalty_points": random.randint(0, 1000),
        "session_duration": round(random.uniform(0.5, 60), 2),
        "referrer": random.choice(['google', 'facebook', 'instagram', 'direct', 'email_campaign']),
        "customer_segment": random.choice(['new', 'returning', 'loyal']),
        "abandoned_cart": random.choice([True, False]),
        "rating": round(random.uniform(1, 5), 1)
    }

def generate_and_send_events():
    data = [generate_user_event() for _ in range(100)]
    print(data[0])
    kafka_producer.produce(**data)
    print(len(data))

client = MongoClient("mongodb+srv://kmsumanth:sumanth@cluster0.v3laq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["ecommerce"]
collection = db["recommendations"]

# API Route to Get All Recommendations
@app.get("/recommendations", response_model=List[dict])
def get_all_recommendations():
    recommendations = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB ObjectId
    return recommendations

# API Route to Get Recommendations for a Specific User
@app.get("/recommend/{user_id}", response_model=dict)
def get_user_recommendations(user_id: int):
    user_recommendation = collection.find_one({"user_id": user_id}, {"_id": 0})
    if user_recommendation:
        return user_recommendation
    return {"message": "No recommendations found for this user."}

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/user_interactions")
async def trigger_event_generation(background_tasks: BackgroundTasks):
    background_tasks.add_task(generate_and_send_events)
    return {"message": "User interactions are being generated and sent!"}

if __name__=="__main__":
    import uvicorn
    uvicorn.run('app:app',host='0.0.0.0',port=5000)