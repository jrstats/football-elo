def season_str_to_int(season):
    return int(season.split("-")[0])

def season_int_to_str(year):
    return f"{year}-{year+1}"

def get_last_season_str(season):
    this_season_int = season_str_to_int(season)
    return season_int_to_str(this_season_int-1)