from datetime import datetime
from random import seed, choices
import string
from fastapi import FastAPI
from decorum_generator import GameGenerator
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from os import getenv

from models import Game


load_dotenv()

app = FastAPI()

MONGO_DB_URI = getenv("MONGO_DB_URI")
mongo_client = MongoClient(MONGO_DB_URI, server_api=ServerApi("1"))
mongo_database = mongo_client.decorum


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/game")
async def game(game: Game):
    seed(None)

    if not game.seed:
        game.seed = "".join(choices(string.ascii_letters + string.digits, k=8)).upper()

    seed(game.seed)
    game_generator = GameGenerator(game.num_of_players, game.total_difficulty_points)
    game_generator.generate_conditions()
    game_generator.pick_conditions()
    seed(None)

    game_row = {
        **game.dict(),
        "starting_house": game_generator.starting_house.dict(),
        "solution_house": game_generator.solution_house.dict(),
        "conditions": conditions_arr(game_generator.conditions),
        "players_conditions": player_conditions_dict(game_generator.players_conditions),
        "created_at": datetime.now(),
    }
    inserted_game = mongo_database.games.insert_one(game_row)
    
    response = {
        "id": str(inserted_game.inserted_id),
        **game.dict(),
    }
    return response


def conditions_arr(conditions):
    return [
        {
            "condition": condition.condition,
            "difficulty_points": condition.difficulty_points,
        }
        for condition in conditions
    ]


def player_conditions_dict(player_conditions):
    return {
        f"p{player_index + 1}": conditions_arr(conditions)
        for player_index, conditions in enumerate(player_conditions)
    }
