import asyncio
import logging
import sys
import os
from time import sleep
from typing import Any, Dict, List, Optional, Tuple

import requests
import json
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns


LEAGUES = {
    "Russia": "https://1xstavka.ru/line/football/225733-russia-premier-league",
    # "England": "https://1xstavka.ru/line/Football/88637-England-Premier-League/",
    # "France": "https://1xstavka.ru/line/Football/12821-France-Ligue-1/",
    # "Germany": "https://1xstavka.ru/line/Football/96463-Germany-Bundesliga/",
    # "Spain": "https://1xstavka.ru/line/Football/127733-Spain-La-Liga/",
    # "Netherlands": "https://1xstavka.ru/line/Football/2018750-Netherlands-Eredivisie/",
    # "Championship": "https://1xstavka.ru/line/Football/105759-England-Championship/",
    # "Turkey": "https://1xstavka.ru/line/Football/11113-Turkey-SuperLiga/",
    # "Italy": "https://1xstavka.ru/line/Football/110163-Italy-Serie-A/",
    # "Portugal": "https://1xstavka.ru/line/Football/118663-Portugal-Primeira-Liga/",
    # "UEFA_1": "https://1xstavka.ru/line/Football/118587-UEFA-Champions-League/",
    # "UEFA_2": "https://1xstavka.ru/line/Football/118593-UEFA-Europa-League/",
}


def process_matches(matches: List[Any]) -> Tuple[List[str], List[float]]:
    result = {}

    for match_info in matches:
        home_team = match_info["homeTeam"]["name"]
        away_team = match_info["awayTeam"]["name"]
        match_url = match_info["url"]

        if home_team in result or away_team in result:
            continue

        for offer in match_info["offers"]:
            if offer["name"] == "Победа 1-й команды" and "price" in offer:
                result[home_team] = float(offer["price"])
            elif offer["name"] == "Победа 2-й команды" and "price" in offer:
                result[away_team] = float(offer["price"])

    sorted_teams = sorted(result.items(), key=lambda x: x[1])
    return [x[0] for x in sorted_teams], [x[1] for x in sorted_teams]


def plot_bar(labels: List[str], values: List[float], f_name: str) -> None:
    fig, ax = plt.subplots(figsize=(6, 8))
    bars = ax.barh(labels, values)

    ax.set_xlim(0, round(max(values)) + 1)

    # plt.savefig(f"./project2/{f_name}", dpi=300)
    plt.savefig(f"{f_name}", dpi=300)


def parse_league(league_name: str) -> bool:
    if league_name not in LEAGUES:
        return False

    response = requests.get(LEAGUES[league_name])
    soup = BeautifulSoup(response.text, "lxml")

    all_matches = json.loads(
        "".join(soup.find("script", {"type": "application/ld+json"}).contents)
    )

    teams_names, team_chanses = process_matches(all_matches)

    plot_bar(teams_names, team_chanses, f"{league_name}.png")
    # print(teams_names)
    # print(team_chanses)

    return True


if __name__ == "__main__":
    with open("status.txt", "w") as f:
        if parse_league(sys.argv[1]):
            f.write("success")
        else:
            f.write("error")
