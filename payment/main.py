from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from dotenv import load_dotenv
import os, time, requests
from starlette.requests import Request

load_dotenv()
REDISHOST = os.getenv("REDISHOST")
REDISPORT = int(os.getenv("REDISPORT"))
REDISPASS = os.getenv("REDISPASS")

# This should be a different db as microservices have different dbs generally
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

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    qty: int
    status: str  # pending, completed, refunded

    class Meta:
        database = redis


@app.get('/orders/{pk}')
def get(pk: str):
    return Order.get(pk)


@app.post('/orders')
async def create(request: Request, background_tasks: BackgroundTasks):  # send id, qty
    body = await request.json()

    req = requests.get(f'http://localhost:8000/products/{body["id"]}')
    product = req.json()

    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2 * product['price'],
        total=1.2 * product['price'],
        qty=body['qty'],
        status='pending'
    )
    order.save()

    background_tasks.add_task(order_completed, order)

    return order

# Simulating payment delay
def order_completed(order: Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()