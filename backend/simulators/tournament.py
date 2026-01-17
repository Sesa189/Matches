import backend.simulators.match as match
import random
import backend.db as db
import asyncio
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

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

async def single_match(team1, team2, team1_perc, team2_perc, stage, ws_callback=None):
    winner, result, events = await match.match_simulation(
        team1, team2, team1_perc, team2_perc, stage, "torneo", ws_callback=ws_callback)

    if winner == 1:
        winner_perc = team1_perc
        winner_team = team1
    elif winner == 2:
        winner_perc = team2_perc
        winner_team = team2
    else:
        winner_team = None
        winner_perc = None

    await db.tournament_results.insert_one({
        "stage": stage,
        "team1": team1,
        "team2": team2,
        "risultato" : result,
        "eventi" : events,
        "winner": winner_team
    })

    return winner_team, winner_perc

async def round(pre, dic, rng, ws_callback):
    post = {}
    c = 0
    stage = ""
    matches = []

    if rng == 8:
        stage = "ottavi"
    elif rng == 4:
        stage = "quarti"
    elif rng == 2:
        stage = "semifinali"
    elif rng == 1:
        stage = "finale"

    pre_copy = pre.copy()

    for x in range(rng):
        c += 1
        team1 = random.choice(list(pre_copy.keys()))
        team2 = team1
        while team1 == team2:
            team2 = random.choice(list(pre_copy.keys()))

        print(f"\n{team1} vs {team2}")

        team1_perc = pre_copy[team1]
        team2_perc = pre_copy[team2]

        match_task = single_match(
            team1, team2,
            team1_perc, team2_perc,
            stage,
            ws_callback=ws_callback
        )
        matches.append(match_task)

        pre_copy.pop(team1)
        pre_copy.pop(team2)

        dic[c] = [team1, team2]

    winners = await asyncio.gather(*matches)

    for tm, tm_perc in winners:
        post[tm] = tm_perc

    print(f"winners : {post}")
    return post

async def run_tournament(ws_callback=None):
    await clear_tournament_results()
    print("\n-----------ottavi-------------")
    ottavi = await round(match.teams, ottavi_w, 8, ws_callback=ws_callback)
    print("\n-----------quarti-------------")
    quarti = await round(ottavi, quarti_w, 4, ws_callback=ws_callback)
    print("\n-----------semifinali-------------")
    semifinali = await round(quarti, semifinali_w, 2, ws_callback=ws_callback)
    print("\n-----------finale-------------")
    finale = await round(semifinali, finale_w, 1, ws_callback=ws_callback)

if __name__ == "__main__":
    asyncio.run(run_tournament())
