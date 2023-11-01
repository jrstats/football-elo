from helpers.elo import expected_scores


def get_latest_elos(elo):
    return (
        elo
        .loc[lambda df: df["score"].notna()]
        .groupby("team")
        ["elo_team_post"]
        .last()
    )


def predict(elo, team_x, team_y):
    latest_elos = get_latest_elos(elo)
    elo_x = latest_elos[team_x]
    elo_y = latest_elos[team_y]
    return expected_scores(elo_x, elo_y)