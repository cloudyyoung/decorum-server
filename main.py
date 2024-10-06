from random import randint, seed
from time import time
from fastapi import FastAPI
from decorum_generator import GameGenerator

from models import Game

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/game")
async def game(game: Game):
    seed(game.seed)

    game_generator = GameGenerator(game.num_of_players, game.total_difficulty_points)
    game_generator.generate_conditions()
    conditions = game_generator.pick_conditions()

    return {"game": game}
