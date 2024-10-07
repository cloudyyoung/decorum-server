from contextlib import asynccontextmanager
from datetime import datetime
from random import seed, choices
import string
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from decorum_generator import GameGenerator
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from os import getenv

from models import Game
from utils import conditions_dict_arr, player_conditions_dict


load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    MONGO_DB_URI = getenv("MONGO_DB_URI")
    mongo_client = MongoClient(MONGO_DB_URI, server_api=ServerApi("1"))
    app.mongodb = mongo_client.decorum

    yield

    mongo_client.close()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


def get_decorum_db():
    return app.mongodb


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/games")
async def game(game: Game, decorum_database=Depends(get_decorum_db)):
    seed(None)

    if not game.seed:
        game.seed = "".join(choices(string.ascii_letters + string.digits, k=8)).upper()

    seed(game.seed)
    game_generator = GameGenerator(game.num_of_players, game.total_difficulty_points)
    game_generator.generate_conditions()
    game_generator.pick_conditions()
    seed(None)

    game_doc = {
        **game.dict(),
        "starting_house": game_generator.starting_house.dict(),
        "solution_house": game_generator.solution_house.dict(),
        "conditions": conditions_dict_arr(game_generator.conditions),
        "players_conditions": player_conditions_dict(game_generator.players_conditions),
        "created_at": datetime.now(),
    }
    inserted_game = decorum_database.games.insert_one(game_doc)

    response = {
        "id": str(inserted_game.inserted_id),
        **game.dict(),
        "created_at": game_doc["created_at"],
    }
    return response


@app.get("/games/{game_id}")
async def get_game(game_id: str, decorum_database=Depends(get_decorum_db)):
    if not ObjectId.is_valid(game_id):
        raise HTTPException(status_code=400, detail="Invalid game ID")

    game_doc = decorum_database.games.find_one({"_id": ObjectId(game_id)})

    if not game_doc:
        raise HTTPException(status_code=404, detail="Game not found")

    response = {
        "id": str(game_doc["_id"]),
        "num_of_players": game_doc["num_of_players"],
        "total_difficulty_points": game_doc["total_difficulty_points"],
        "seed": game_doc["seed"],
        "created_at": game_doc["created_at"],
    }
    return response


@app.get("/games/{game_id}/{player_id}")
async def get_player_conditions(
    game_id: str, player_id: str, decorum_database=Depends(get_decorum_db)
):
    if not ObjectId.is_valid(game_id):
        raise HTTPException(status_code=400, detail="Invalid game ID")

    game_doc = decorum_database.games.find_one({"_id": ObjectId(game_id)})

    if not game_doc:
        raise HTTPException(status_code=404, detail="Game not found")

    player_conditions = game_doc["players_conditions"][player_id]
    house = game_doc["starting_house"]

    if not player_conditions:
        raise HTTPException(status_code=404, detail="Player not found")

    response = {"player_id": player_id, "conditions": player_conditions, "house": house}
    return response
