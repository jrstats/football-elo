

def plot_team(elo_df, team):
    (
        elo_df
        .loc[lambda df: df["team"] == team]
        .set_index("datetime")
        ["elo_team_post"]
        .plot()
    )