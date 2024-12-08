from uuid import uuid4

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
import redis

from src.services.get_accidents import get_accidents as get_accidents_service
from src.database.redis_con import get_redis
from src.schemas import RoadReport, Status, StatusRequest


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/update")
def update_accidents(redis: redis.StrictRedis = Depends(get_redis)):
    accidents_list = get_accidents_service(redis)
    for accident in accidents_list:
        if redis.exists(accident[0]):
            continue
        redis.hset(accident[0], mapping=accident[1])


@app.get("/")
def get_accidents(redis: redis.StrictRedis = Depends(get_redis)):
    keys = redis.keys()
    accidents_list = []
    for key in keys:
        data = [key, redis.hgetall(key)]
        accidents_list.append(data)
    return accidents_list


@app.post("/")
def create_road_report(
    report: RoadReport, redis: redis.StrictRedis = Depends(get_redis)
):
    report_data = {
        "incident_type": report.incident_type,
        "time": report.time,
        "latitude": report.location.latitude,
        "longitude": report.location.longitude,
        "severity": report.severity,
        "description": report.description,
        "source": "user",
        "status": "new",
    }

    report_id = str(uuid4())

    # Сохраняем данные в Redis в хеш
    redis.hset(report_id, mapping=report_data)

    # Возвращаем успешный ответ
    return {"message": "Report successfully saved", "report_id": report_id}


@app.put("/update_status/{report_id}")
def update_status(
    report_id: str,
    status: StatusRequest,  # Принимаем новый статус
    redis: redis.StrictRedis = Depends(get_redis),
):
    # Проверяем, существует ли ключ в Redis
    if not redis.exists(report_id):
        print("Report not found")

    # Обновляем только статус
    redis.hset(report_id, "status", status.status)
