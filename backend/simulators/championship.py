import Matches.backend.simulators.match as match
import Matches.backend.db as db
import asyncio

async def clear_championship_results():
    result = await db.championship_results.delete_many({})

asyncio.run(clear_championship_results())

def genera_calendario(teams_dict):
    teams = list(teams_dict.keys())
    giornate = {}
    lista = teams[:]

    for g in range(16):
        matches = []
        for i in range(8):
            casa = lista[i]
            trasferta = lista[15 - i]
            matches.append([casa, trasferta])
        giornate[g + 1] = matches

        # Rotazione (circle method)
        lista = [lista[0]] + [lista[-1]] + lista[1:-1]

    for g in range(15):
        matches = []
        for casa, trasferta in giornate[g + 1]:
            matches.append([trasferta, casa])
        giornate[g + 1 + (15)] = matches

    return giornate


calendario = genera_calendario(match.teams)

for giornata, partite in calendario.items():
    print(giornata, partite)

async def championship_result():
    for giornata in list(calendario.keys()):
        for partita in calendario[giornata]:
            winner_team, result, events = match.match_simulation(match.teams[partita[0]], match.teams[partita[1]], False)
            await db.championship_results.insert_one({"giornata": giornata, "team1": partita[0], "team2": partita[1], "risultato" : result, "eventi" : events,  "winner": winner_team})

asyncio.run(championship_result())

import Matches.backend.db as db
import Matches.backend.simulators.match as match

async def genera_classifica():
    # Recupero tutte le partite simulate
    partite = await db.championship_results.find().to_list(None)

    # Dizionario classifica
    classifica = {}

    # Inizializzo tutte le squadre
    for team in match.teams.keys():
        classifica[team] = {
            "punti": 0,
            "vittorie": 0,
            "sconfitte": 0,
            "set_vinti": 0,
            "set_persi": 0,
            "punti_fatti": 0,
            "punti_subiti": 0,
            "quoziente_set": 0,
            "quoziente_punti": 0
        }

    # Elaborazione partite
    for p in partite:
        team1 = p["team1"]
        team2 = p["team2"]
        risultato = p["risultato"]
        winner = p["winner"]
        events = p["eventi"]

        set1 = 0
        set2 = 0
        for r in p["risultato"]:
            p1, p2 = map(int, r.split(" : "))
            if p1 > p2:
                set1 += 1
            else:
                set2 += 1

        # Aggiorno set
        classifica[team1]["set_vinti"] += set1
        classifica[team1]["set_persi"] += set2
        classifica[team2]["set_vinti"] += set2
        classifica[team2]["set_persi"] += set1

        # Aggiorno punti fatti/subiti (se presenti negli eventi)
        if "punti_team1" in events and "punti_team2" in events:
            classifica[team1]["punti_fatti"] += events["punti_team1"]
            classifica[team1]["punti_subiti"] += events["punti_team2"]
            classifica[team2]["punti_fatti"] += events["punti_team2"]
            classifica[team2]["punti_subiti"] += events["punti_team1"]

        # Assegno punti classifica
        if winner == team1:
            classifica[team1]["vittorie"] += 1
            classifica[team2]["sconfitte"] += 1

            if risultato == "3-2":
                classifica[team1]["punti"] += 2
                classifica[team2]["punti"] += 1
            else:
                classifica[team1]["punti"] += 3

        else:
            classifica[team2]["vittorie"] += 1
            classifica[team1]["sconfitte"] += 1

            if risultato == "3-2":
                classifica[team2]["punti"] += 2
                classifica[team1]["punti"] += 1
            else:
                classifica[team2]["punti"] += 3

    # Calcolo quozienti
    for team, dati in classifica.items():
        # Quoziente set
        if dati["set_persi"] > 0:
            dati["quoziente_set"] = dati["set_vinti"] / dati["set_persi"]
        else:
            dati["quoziente_set"] = dati["set_vinti"]  # evita divisione per zero

        # Quoziente punti
        if dati["punti_subiti"] > 0:
            dati["quoziente_punti"] = dati["punti_fatti"] / dati["punti_subiti"]
        else:
            dati["quoziente_punti"] = dati["punti_fatti"]

    # Ordinamento classifica secondo criteri ufficiali
    classifica_ordinata = sorted(
        classifica.items(),
        key=lambda x: (
            -x[1]["punti"],
            -x[1]["quoziente_set"],
            -x[1]["quoziente_punti"],
            -(x[1]["set_vinti"] - x[1]["set_persi"]),
            -x[1]["set_vinti"]
        )
    )

    return classifica_ordinata

import asyncio

async def main():
    classifica = await genera_classifica()
    for pos, (team, dati) in enumerate(classifica, start=1):
        print(pos, team, dati)

asyncio.run(main())
