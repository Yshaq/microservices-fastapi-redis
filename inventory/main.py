from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from dotenv import load_dotenv
import os

load_dotenv()
REDISHOST = os.getenv("REDISHOST")
REDISPORT = int(os.getenv("REDISPORT"))
REDISPASS = os.getenv("REDISPASS")

redis = get_redis_connection(
    host=REDISHOST,
    port=REDISPORT,
    password=REDISPASS,
    decode_responses=True
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

class Product(HashModel):
    name: str
    price: float
    qty: int

    class Meta:
        database = redis

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/products")
def all():
    return [format(pk) for pk in Product.all_pks()]

def format(pk: str):
    product = Product.get(pk)
    return {
        "pk": product.pk,
        "name": product.name,
        "price": product.price,
        "qty": product.qty
    }

@app.post("/products")
def create(product: Product):
    return product.save()

@app.get("/products/{pk}")
def get(pk: str):
    return Product.get(pk)

@app.delete("/products/{pk}")
def delete(pk: str):
    return Product.delete(pk)

