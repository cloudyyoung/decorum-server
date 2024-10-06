from random import seed, choices
import string
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
    seed(None)

    if not game.seed:
        game.seed = "".join(choices(string.ascii_letters + string.digits, k=4)).upper()

    seed(game.seed)

    game_generator = GameGenerator(game.num_of_players, game.total_difficulty_points)
    game_generator.generate_conditions()
    conditions = game_generator.pick_conditions()

    seed(None)

    return {"game": game}
