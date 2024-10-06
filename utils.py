def conditions_arr(conditions):
    return [condition.condition for condition in conditions]


def conditions_dict_arr(conditions):
    return [
        {
            "condition": condition.condition,
            "difficulty_points": condition.difficulty_points,
        }
        for condition in conditions
    ]


def player_conditions_dict(player_conditions):
    return {
        f"p{player_index + 1}": conditions_dict_arr(conditions)
        for player_index, conditions in enumerate(player_conditions)
    }
