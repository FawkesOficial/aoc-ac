#!/usr/bin/env python3

import json
import requests
from datetime import datetime


THRESHOLD    = 60 # The maximum ammount of time between submissions, in seconds, to consider whether or not someone is cheating. Default is 60
MAX_SUS_DAYS = 2  # The maximum ammount of days to mark someone as a cheater. Default is 2


def get_leaderboard_data(leaderboard_id: int, year: int, auth_cookie: str) -> dict:
    leaderboard_r = requests.get(f"https://adventofcode.com/{year}/leaderboard/private/view/{leaderboard_id}.json", cookies={"session": auth_cookie})

    return leaderboard_r.json() if leaderboard_r.ok else None

# def save_leaderboard_data() -> None:
#     with open("leaderboard_data.json", "w") as f:
#        json.dump(data, f)

# def load_leaderboard_data() -> dict:
#     with open("leaderboard_data.json", "r") as f:
#         data = json.load(f)

#     return data

def get_submissions(leaderboard_data: dict) -> dict:
    submissions = {}

    for member_id, info in leaderboard_data["members"].items():
        sub = {}
        for day, star_info in info["completion_day_level"].items():
            if len(star_info.keys()) == 2:
                sub[day] = star_info['2']['get_star_ts'] - star_info['1']['get_star_ts']

        submissions[info["name"]] = sub

    return submissions

def get_cheaters(submissions: dict) -> list[dict]:
    cheaters = []
    for name, day_sub_time in submissions.items():
        sus_days = [(day, time) for day, time in day_sub_time.items() if int(time) < THRESHOLD]

        sus_days.sort(key=lambda x:int(x[0]))
            
        if len(sus_days) > MAX_SUS_DAYS:
            cheaters.append({"name": name, "sus_days": sus_days})
    
    return cheaters

def get_clean_leaderboard(leaderboard_data: dict, cheaters: list) -> list:
    cheaters_names = [cheater["name"] for cheater in cheaters]
    clean_leaderboard = [(player["name"], player["local_score"]) for player in leaderboard_data["members"].values() if player["name"] not in cheaters_names]
    clean_leaderboard.sort(key= lambda x:int(x[1]), reverse=True)

    return clean_leaderboard

def print_cheaters_info(cheaters: list) -> None:
    cheater_count = 0
    for cheater in cheaters:
        cheater_count += 1
        print()
        print("="*(len(cheater["name"])+22))
        print(f"{cheater['name']} is probably cheating!")
        print("="*(len(cheater["name"])+22))

        for day, time in cheater["sus_days"]:
            print(f"Submit time for day {day} was {time}s!")

    print("\nTotal cheaters:", cheater_count)

def print_leaderboard_without_cheaters(leaderboard_data: dict, top: int = -1) -> None:
    print()
    print("-"*29)
    print("Leaderboard without cheaters:")
    print("-"*29)

    for i, player in enumerate(leaderboard_data, start=0):
        print(f"{i+1}) {player[1]} {player[0]}")

        if i+1 == top:
            break


def main():

    cookie = input("[?] Please enter your AoC cookie: ")
    year = int(input(f"[?] Please specify the year(press enter for {datetime.now().year}): "))
    year = year if year != "" else datetime.now().year
    leaderboard_id = int(input("[?] Please enter the ID of the leaderboard: "))
    
    leaderboard_data = get_leaderboard_data(leaderboard_id=leaderboard_id, year=year, auth_cookie=cookie)
    
    submissions = get_submissions(leaderboard_data)

    cheaters = get_cheaters(submissions)

    clean_leaderboard = get_clean_leaderboard(leaderboard_data, cheaters)

    print_cheaters_info(cheaters)
    print_leaderboard_without_cheaters(clean_leaderboard, top=-1) # -1 to show all players, 10 to show "top 10", etc...


if __name__ in "__main__":
    main()