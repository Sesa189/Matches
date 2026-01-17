import backend.simulators.match as match
import backend.db as db
import asyncio
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def clear_championship_results():
    result = await db.championship_results.delete_many({})
    print(f"Database campionato pulito: {result.deleted_count} record eliminati")


def genera_calendario(teams_dict):
    teams = list(teams_dict.keys())
    giornate = {}
    lista = teams[:]

    for g in range(15):
        matches = []
        for i in range(8):
            casa = lista[i]
            trasferta = lista[15 - i]
            matches.append([casa, trasferta])
        giornate[g + 1] = matches

        lista = [lista[0]] + [lista[-1]] + lista[1:-1]

    for g in range(15):
        matches = []
        for casa, trasferta in giornate[g + 1]:
            matches.append([trasferta, casa])
        giornate[g + 1 + 15] = matches

    return giornate


async def single_match(team1, team2, team1_perc, team2_perc, giornata, ws_callback=None):
    winner, result, events = await match.match_simulation(
        team1, team2, team1_perc, team2_perc, giornata, "campionato", ws_callback=ws_callback
    )

    if winner == 1:
        winner_team = team1
    elif winner == 2:
        winner_team = team2
    else:
        winner_team = None

    await db.championship_results.insert_one({
        "giornata": giornata,
        "team1": team1,
        "team2": team2,
        "risultato": result,
        "eventi": events,
        "winner": winner_team
    })

    return winner_team, result, events


async def run_giornata(giornata_num, partite, ws_callback=None):
    print(f"\n--- Avvio partite Giornata {giornata_num} ---")

    matches = []
    for team1, team2 in partite:
        print(f"  • {team1} vs {team2}")

        team1_perc = match.teams[team1]
        team2_perc = match.teams[team2]

        match_task = single_match(
            team1, team2,
            team1_perc, team2_perc,
            giornata_num,
            ws_callback=ws_callback
        )
        matches.append(match_task)

    print(f"\nIn corso: {len(matches)} partite simultanee...")

    results = await asyncio.gather(*matches, return_exceptions=True)

    successi = 0
    errori = 0
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            errori += 1
            print(f"  ✗ ERRORE partita {i + 1}: {type(r).__name__}: {r}")
            import traceback
            traceback.print_exception(type(r), r, r.__traceback__)
        else:
            successi += 1

    print(f"\n--- Giornata {giornata_num} completata ---")
    print(f"  ✓ Partite completate: {successi}")
    if errori > 0:
        print(f"  ✗ Errori: {errori}")

    return results


async def run_championship(ws_callback=None, giornate_limit=None):
    await clear_championship_results()

    calendario = genera_calendario(match.teams)

    giornate_da_giocare = list(calendario.keys())
    if giornate_limit:
        giornate_da_giocare = giornate_da_giocare[:giornate_limit]

    for giornata_num in giornate_da_giocare:
        print(f"\n{'=' * 50}")
        print(f"INIZIO GIORNATA {giornata_num}")
        print(f"{'=' * 50}\n")

        partite = calendario[giornata_num]

        await run_giornata(giornata_num, partite, ws_callback=ws_callback)

        print(f"\n{'=' * 50}")
        print(f"FINE GIORNATA {giornata_num} - Tutte le partite completate")
        print(f"{'=' * 50}\n")

        if giornata_num < giornate_da_giocare[-1]:
            print(f"Pausa prima della prossima giornata...\n")
            await asyncio.sleep(5)


async def genera_classifica():
    partite = await db.championship_results.find().to_list(None)

    classifica = {}

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

    for p in partite:
        team1 = p["team1"]
        team2 = p["team2"]
        risultato = p["risultato"]
        winner = p["winner"]

        set1 = 0
        set2 = 0
        for r in risultato:
            p1, p2 = map(int, r.split(" : "))
            classifica[team1]["punti_fatti"] += p1
            classifica[team1]["punti_subiti"] += p2
            classifica[team2]["punti_fatti"] += p2
            classifica[team2]["punti_subiti"] += p1

            if p1 > p2:
                set1 += 1
            else:
                set2 += 1

        classifica[team1]["set_vinti"] += set1
        classifica[team1]["set_persi"] += set2
        classifica[team2]["set_vinti"] += set2
        classifica[team2]["set_persi"] += set1

        if winner == team1:
            classifica[team1]["vittorie"] += 1
            classifica[team2]["sconfitte"] += 1

            if set1 == 3 and set2 == 2:  # 3-2
                classifica[team1]["punti"] += 2
                classifica[team2]["punti"] += 1
            else:
                classifica[team1]["punti"] += 3
        else:
            classifica[team2]["vittorie"] += 1
            classifica[team1]["sconfitte"] += 1

            if set2 == 3 and set1 == 2:  # 3-2
                classifica[team2]["punti"] += 2
                classifica[team1]["punti"] += 1
            else:
                classifica[team2]["punti"] += 3

    for team, dati in classifica.items():
        if dati["set_persi"] > 0:
            dati["quoziente_set"] = dati["set_vinti"] / dati["set_persi"]
        else:
            dati["quoziente_set"] = dati["set_vinti"]

        if dati["punti_subiti"] > 0:
            dati["quoziente_punti"] = dati["punti_fatti"] / dati["punti_subiti"]
        else:
            dati["quoziente_punti"] = dati["punti_fatti"]

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


if __name__ == "__main__":
    asyncio.run(run_championship(giornate_limit=2))