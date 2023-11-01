

def plot_team(elo_df, team):
    (
        elo_df
        .loc[lambda df: df["team"] == team]
        .set_index(["season", "game_number"])
        ["elo_team_post"]
        .plot()
    )

def plot_many(elo_df, teams):
    # TODO: doesn't seem to put indexes together properly if tenure is misaligned
    (
        elo_df
        .loc[lambda df: df["team"].isin(teams)]
        .set_index(["season", "game_number"])
        .groupby("team")
        ["elo_team_post"]
        .plot()
    )

def plot_all(elo_df):
    (
        elo_df
        .set_index(["season", "game_number"])
        .groupby("team")
        ["elo_team_post"]
        .plot()
    )