from pydantic import BaseModel


class Game(BaseModel):
    num_of_players: int
    total_difficulty_points: int
    seed: str | None = None
