from helpers.elo import get_result, update_ratings, INITIAL_RATING
from helpers.matches import season_str_to_int, season_int_to_str, get_last_season_str
import pandas as pd
import numpy as np
import glom


def transform_home_away(matches):
    matches_h = (
        matches
        .assign(team=lambda df: df["Home"])
        .assign(opponent=lambda df: df["Away"])
        .assign(venue="home")
        .assign(team_g=lambda df: df["Score"].str.split("–").str.get(0))
        .assign(opponent_g=lambda df: df["Score"].str.split("–").str.get(1))
        .assign(team_xg=lambda df: df["xG"])
        .assign(opponent_xg=lambda df: df["xG.1"])
    )
    matches_a = (
        matches
        .assign(team=lambda df: df["Away"])
        .assign(opponent=lambda df: df["Home"])
        .assign(venue="away")
        .assign(team_g=lambda df: df["Score"].str.split("–").str.get(1))
        .assign(opponent_g=lambda df: df["Score"].str.split("–").str.get(0))
        .assign(team_xg=lambda df: df["xG.1"])
        .assign(opponent_xg=lambda df: df["xG"])
    )

    home_away = (
        pd.concat([matches_h, matches_a])
        .assign(game_number=lambda df: df.groupby(["team", "season"])["datetime"].rank(method="first", ascending=True).astype(int))
        .sort_values(["season", "game_number"])
    )

    return home_away


def get_game_dates(home_away):
    game_dates = (
        home_away
        .groupby(["season", "game_number"], as_index=False)
        ["datetime"]
        .min()
    )

    return game_dates


def empty_elo_dict(home_away):
    all_seasons = (
        home_away
        [["team", "season"]]
        .drop_duplicates()
        .groupby("team")
        ["season"]
        .apply(list)
    )

    elo_dict = {}
    for team, seasons in all_seasons.items():
        elo_dict[team] = {s: [{} for i in range(38)] for s in seasons}

    return elo_dict


def calculate_elo_dict(elo_dict, home_away):
    # TODO: Improve this and data structure

    home_away = home_away.sort_values(["season", "game_number"])

    for i, row in home_away.iterrows():
        try:
            team_past_season = row["season"]
            team_past_games = glom.glom(elo_dict, f"{row['team']}.{team_past_season}", default=[{}])
            team_past_game_number = max([i for i, game in enumerate(team_past_games) if game != {}])
        except ValueError:
            try:
                team_past_season = get_last_season_str(row["season"])
                team_past_games = glom.glom(elo_dict, f"{row['team']}.{team_past_season}", default=[{}])
                team_past_game_number = max([i for i, game in enumerate(team_past_games) if game != {}])
            except ValueError:
                team_past_game_number = None

        try:
            opponent_past_season = row["season"]
            opponent_past_games = glom.glom(elo_dict, f"{row['opponent']}.{opponent_past_season}", default=[{}])
            team_past_game_number = max([i for i, game in enumerate(team_past_games) if game != {}])
        except ValueError:
            try:
                opponent_past_season = get_last_season_str(row["season"])
                opponent_past_games = glom.glom(elo_dict, f"{row['opponent']}.{opponent_past_season}", default=[{}])
                team_past_game_number = max([i for i, game in enumerate(team_past_games) if game != {}])
            except ValueError:
                opponent_past_game_number = None

        # print(row["team"], row["season"], row["game_number"], team_past_season, team_past_game_number)

        elo_team_pre = glom.glom(elo_dict, f"{row['team']}.{team_past_season}.{str(team_past_game_number)}.elo_team_post", default=INITIAL_RATING)
        elo_opponent_pre = glom.glom(elo_dict, f"{row['opponent']}.{opponent_past_season}.{str(opponent_past_game_number)}.elo_team_post", default=INITIAL_RATING)
        result = get_result(row["team_g"], row["opponent_g"])
        elo_team_post, elo_opponent_post = update_ratings(elo_team_pre, elo_opponent_pre, result)
        elo_dict[row["team"]][row["season"]][row["game_number"] - 1] = {
            "team_g": row["team_g"],
            "opponent": row["opponent"],
            "opponent_g": row["opponent_g"],
            "team_xg": row["team_xg"],
            "opponent_xg": row["opponent_xg"],
            "elo_team_pre": elo_team_pre,
            "elo_opponent_pre": elo_opponent_pre,
            "elo_team_post": elo_team_post,
            "elo_opponent_post": elo_opponent_post
        }

        if (i % 99) == 0:
            ...
            # print(row["team"], row["season"], row["game_number"], team_past_season, team_past_game_number)

    return elo_dict


def transform_elo(elo_dict, game_dates):
    elo_json = (
        pd.DataFrame([elo_dict])
        .melt()
        .rename({"variable": "team", "value": "elo_json"}, axis=1)
    )

    elo_df = (
        pd.concat([elo_json, pd.json_normalize(elo_json["elo_json"])], axis=1)
        .drop(["elo_json"], axis=1)
        .melt(id_vars=["team"])
        .rename({"variable": "season"}, axis=1)
        .explode("value")
        .assign(game_number=lambda df: df.groupby(["team", "season"]).cumcount() + 1)
        .reset_index(drop=True)
    )

    elo_df = (
        pd.concat([elo_df, pd.json_normalize(elo_df["value"])], axis=1)
    )

    elo_df = (
        elo_df
        .assign(score=lambda df: df["team"] + " " + df["team_g"].astype(str) + "-" + df["opponent_g"].astype(str) + " " + df["opponent"])
        .drop(["opponent", "opponent_g", "team_g"], axis=1)
        [["team", "season", "game_number", "score", "elo_team_pre", "elo_team_post"]]
        # .loc[lambda df: df["score"].notna()]
        .merge(game_dates, how="left", on=["season", "game_number"])
        .sort_values(["team", "season", "game_number"])
    )
    return elo_df


def matches_to_elo(matches):
    home_away = transform_home_away(matches)
    game_dates = get_game_dates(home_away)

    elo_dict = empty_elo_dict(home_away)
    elo_dict = calculate_elo_dict(elo_dict, home_away)
    elo_df = transform_elo(elo_dict, game_dates)

    return elo_df
