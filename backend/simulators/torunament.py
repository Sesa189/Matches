import Matches.backend.simulators.match as match
import random

teams = {
    "Sir Safety Perugia" : 53,
    "Itas Trentino" : 52,
    "Cucine Lube Civitanova" : 52,
    "Modena Volley" : 51,
    "Allianz Milano" : 50,
    "Gas Sales Bluenergy Piacenza" : 51,
    "Vero Volley Monza" : 49,
    "Pallavolo Padova" : 48,
    "Cisterna Volley" : 48,
    "Rana Verona" : 50,
    "Taranto Prisma" : 47,
    "Revivre Cantù" : 47,
    "Pallavolo Cuneo" : 48,
    "Brescia Volley" : 47,
    "Emma Villas Aubay Siena" : 45,
    "Itas Trentino II" : 44
}

ottavi = {}
ottavi_w = {}
quarti = {}
quarti_w = {}
semifinali = {}
semifinali_w = {}
finale= {}
fianle_w = None
c = 0

for x in range(8):
    c += 1
    team1 = random.choice(list(teams.keys()))
    team2 = team1
    while team1 == team2:
        team2 = random.choice(list(teams.keys()))

    print(f"\n{team1} vs {team2}")
    winner = match.match_simulation(teams[team1], teams[team2])

    if winner == 1:
        ottavi_w[team1] = teams[team1]
    elif winner == 2:
        ottavi_w[team2] = teams[team2]

    teams.pop(team1)
    teams.pop(team2)

    ottavi[c] = [team1, team2]

print(f"winners : {ottavi_w}")

for x in ottavi:
    c += 1
    team1 = random.choice(list(ottavi_w.keys()))
    team2 = team1
    while team1 == team2:
        team2 = random.choice(list(ottavi_w.keys()))

    print(f"\n{team1} vs {team2}")
    winner = match.match_simulation(ottavi_w[team1], ottavi_w[team2])

    if winner == 1:
        quarti_w[team1] = ottavi_w[team1]
    elif winner == 2:
        quarti_w[team2] = ottavi_w[team2]

    quarti[c] = [team1, team2]

print(quarti_w)

for x in quarti:
    c += 1
    team1 = random.choice(list(quarti_w.keys()))
    team2 = team1
    while team1 == team2:
        team2 = random.choice(list(quarti_w.keys()))

    print(f"\n{team1} vs {team2}")
    winner = match.match_simulation(quarti_w[team1], quarti_w[team2])

    if winner == 1:
        semifinali_w[team1] = quarti_w[team1]
    elif winner == 2:
        semifinali_w[team2] = quarti_w[team2]

    semifinali[c] = [team1, team2]

print(semifinali_w)



