from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
import redis

from src.services.get_accidents import get_accidents as get_accidents_service
from src.database.redis_con import get_redis


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def get_accidents(redis: redis.StrictRedis = Depends(get_redis)):
    return get_accidents_service(redis)
