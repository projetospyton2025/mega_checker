def check_games(user_games, winning_numbers):
    results = []
    winning_numbers_set = set(winning_numbers)

    for game in user_games:
        game_set = set(map(int, game.split(",")))
        matched = game_set.intersection(winning_numbers_set)
        results.append({
            "game": game,
            "matched": len(matched),
            "numbers": list(matched),
        })
    return results
