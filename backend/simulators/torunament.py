import Matches.backend.simulators.match as match
import random
import Matches.backend.db as db
import asyncio

ottavi = {}
ottavi_w = {}
quarti = {}
quarti_w = {}
semifinali = {}
semifinali_w = {}
finale= {}
finale_w = {}
c = 0

async def clear_tournament_results():
    result = await db.tournament_results.delete_many({})

asyncio.run(clear_tournament_results())

async def round(pre, dic, rng):
    post = {}
    c = 0
    stage = ""
    if rng == 8:
        stage = "ottavi"
    elif rng == 4:
        stage = "quarti"
    elif rng == 2:
        stage = "semifinali"
    elif rng == 1:
        stage = "finale"
    for x in range(rng):
        c += 1
        team1 = random.choice(list(pre.keys()))
        team2 = team1
        while team1 == team2:
            team2 = random.choice(list(pre.keys()))

        print(f"\n{team1} vs {team2}")
        winner, result, events = match.match_simulation(pre[team1], pre[team2], True)

        if winner == 1:
            post[team1] = pre[team1]
        elif winner == 2:
            post[team2] = pre[team2]

        pre.pop(team1)
        pre.pop(team2)

        if winner == 1:
            winner_team = team1
        elif winner == 2:
            winner_team = team2

        await db.tournament_results.insert_one({"stage": stage, "team1": team1, "team2": team2, "risultato" : result, "eventi" : events,  "winner": winner_team})

        dic[c] = [team1, team2]

    print(f"winners : {post}")
    return post

async def run_tournament():
    print("\n-----------ottavi-------------")
    ottavi = await round(match.teams, ottavi_w, 8)
    print("\n-----------quarti-------------")
    quarti = await round(ottavi, quarti_w, 4)
    print("\n-----------semifinali-------------")
    semifinali = await round(quarti, semifinali_w, 2)
    print("\n-----------finale-------------")
    finale = await round(semifinali, finale_w, 1)

asyncio.run(run_tournament())
