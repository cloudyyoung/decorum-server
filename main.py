from random import randint, seed
from time import time
from fastapi import FastAPI
from decorum_generator import ConditionsGenerator, House

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/house")
async def house():
    now = time()
    seed(now)

    house = House()
    house.get_random()

    conditions = ConditionsGenerator.generate_all_conditions(house)
    return {
        "message": "House",
        "conditions": conditions,
        "house": house,
        "timestamp": now,
    }
