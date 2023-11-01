INITIAL_RATING = 1500
WEIGHT = 400
K_FACTOR = 16

def expected_scores(rating_x, rating_y):
    """
    https://en.wikipedia.org/wiki/Elo_rating_system
    'For each `weight` rating points of advantage over the opponent, 
    the expected score is magnified ten times in comparison to the opponent's expected score.'
    """
    q_x = 10 ** (rating_x / WEIGHT)
    q_y = 10 ** (rating_y / WEIGHT)

    e_x = q_x / (q_x + q_y)
    e_y = q_y / (q_x + q_y)

    return e_x, e_y


def update_ratings(rating_x, rating_y, result_x):
    result_y = 1 - result_x
    e_x, e_y = expected_scores(rating_x, rating_y)

    rating_x_new = rating_x + K_FACTOR * (result_x - e_x)
    rating_y_new = rating_y + K_FACTOR * (result_y - e_y)

    return rating_x_new, rating_y_new

def get_result(goals_x, goals_y, xg_x=None, xg_y=None):
    if goals_x > goals_y:
        return 1
    elif goals_x == goals_y:
        return 0.5
    else:
        return 0