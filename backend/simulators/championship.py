import Matches.backend.simulators.match as match
import Matches.backend.db as db
import asyncio
import platform
import random

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def clear_championship_results():
    result = await db.championship_results.delete_many({})
    print(f"Database campionato pulito: {result.deleted_count} record eliminati")

def genera_calendario(teams_dict):
    """Genera il calendario con girone all'italiana (andata e ritorno)"""
    teams = list(teams_dict.keys())
    giornate = {}
    lista = teams[:]

    # Girone di andata (15 giornate)
    for g in range(15):
        matches = []
        for i in range(8):
            casa = lista[i]
            trasferta = lista[15 - i]
            matches.append([casa, trasferta])
        giornate[g + 1] = matches

        # Rotazione (circle method)
        lista = [lista[0]] + [lista[-1]] + lista[1:-1]

    # Girone di ritorno (15 giornate)
    for g in range(15):
        matches = []
        for casa, trasferta in giornate[g + 1]:
            matches.append([trasferta, casa])
        giornate[g + 1 + 15] = matches

    return giornate

async def match_simulation_championship(name_team1, name_team2, team1_perc, team2_perc, giornata, ws_callback=None):
    """
    Simulazione partita specifica per il campionato
    Adattata da match.match_simulation
    """
    if ws_callback:
        await ws_callback({
            "type": "matches",
            "category": "campionato",
            "giornata": giornata,
            "team1": name_team1,
            "team2": name_team2,
            "date": f"Giornata {giornata}",
            "time": "00:00",
            "state": "LIVE",
            "result": "0 : 0",
            "events": []
        })

    # Calcola percentuali
    w = await match.percentage_calculator(team1_perc, team2_perc)

    # Inizializzazione variabili
    win = False
    point1 = 0
    set1 = 0
    point2 = 0
    set2 = 0
    setcounter = 1
    p_max = 0
    result = [""]
    c = 0
    s_end = False
    winner = 0
    events = []
    time = 0
    timeouts = {1: 2, 2: 2}

    while not win:
        await asyncio.sleep(random.uniform(0.1, 0.3))
        time += 60

        # Aggiunta punti
        team = random.choices([1, 2], weights=w, k=1)[0]
        if team == 1:
            point1 += 1
        elif team == 2:
            point2 += 1

        # Timeout ogni 10 punti
        total_points = point1 + point2
        if total_points > 0 and total_points % 10 == 0:
            if point1 < point2 and timeouts[1] > 0:
                events.append(f"Timeout chiamato da {name_team1}")
                timeouts[1] -= 1
            elif point2 < point1 and timeouts[2] > 0:
                events.append(f"Timeout chiamato da {name_team2}")
                timeouts[2] -= 1

        if ws_callback:
            await ws_callback({
                "type": "matches",
                "category": "campionato",
                "giornata": giornata,
                "team1": name_team1,
                "team2": name_team2,
                "date": f"Giornata {giornata}",
                "time": f"{int(time // 60):02d}:{int(time % 60):02d}",
                "state": "LIVE",
                "result": result,
                "events": events
            })

        # Punteggio massimo
        if setcounter <= 4:
            p_max = 25
        elif setcounter == 5:
            p_max = 15

        # Verifica vittoria set
        if point1 >= p_max and point1 - point2 >= 2:
            s_end = True
            set1 += 1
        elif point2 >= p_max and point2 - point1 >= 2:
            set2 += 1
            s_end = True

        # Aggiorna risultato
        line = f"{point1} : {point2}"
        result[c] = line

        if s_end:
            point1 = 0
            point2 = 0
            setcounter += 1
            s_end = False
            timeouts = {1: 2, 2: 2}
            await asyncio.sleep(1)

            if set1 == 3 or set2 == 3:
                win = True
                if set1 == 3:
                    winner = 1
                elif set2 == 3:
                    winner = 2

                if ws_callback:
                    await ws_callback({
                        "type": "matches",
                        "category": "campionato",
                        "giornata": giornata,
                        "team1": name_team1,
                        "team2": name_team2,
                        "date": f"Giornata {giornata}",
                        "time": f"{int(time // 60):02d}:{int(time % 60):02d}",
                        "state": "FINISHED",
                        "result": result,
                        "events": events,
                        "winner": name_team1 if winner == 1 else name_team2
                    })
            else:
                c += 1
                result.append("")

    return winner, result, events

async def single_championship_match(team1, team2, giornata, ws_callback=None):
    """Simula una singola partita di campionato"""
    try:
        team1_perc = match.teams[team1]
        team2_perc = match.teams[team2]

        print(f"DEBUG: Simulazione {team1} vs {team2}, giornata={giornata}, type={type(giornata)}")

        # Usa la funzione specifica per il campionato
        winner, result, events = await match_simulation_championship(
            team1, team2, team1_perc, team2_perc, giornata, ws_callback=ws_callback
        )

        winner_team = team1 if winner == 1 else team2

        await db.championship_results.insert_one({
            "giornata": giornata,
            "team1": team1,
            "team2": team2,
            "risultato": result,
            "eventi": events,
            "winner": winner_team
        })

        return winner_team, result, events

    except Exception as e:
        print(f"Errore in single_championship_match: {e}")
        print(f"Tipo errore: {type(e)}")
        import traceback
        print("Stacktrace completo:")
        traceback.print_exc()
        # In caso di errore, ritorna comunque un vincitore casuale
        winner_team = team1 if random.random() > 0.5 else team2
        return winner_team, [], []

async def run_giornata(giornata_num, partite, ws_callback=None):
    print(f"\n--- Avvio partite Giornata {giornata_num} ---")

    tasks = []
    for team1, team2 in partite:
        print(f"  • {team1} vs {team2}")
        task = single_championship_match(team1, team2, giornata_num, ws_callback=ws_callback)
        tasks.append(task)

    print(f"\nIn corso: {len(tasks)} partite simultanee...")

    # asyncio.gather ATTENDE che tutte le task siano completate prima di continuare
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Conta i risultati
    successi = sum(1 for r in results if not isinstance(r, Exception))
    errori = len(results) - successi

    print(f"\n--- Giornata {giornata_num} completata ---")
    print(f"  ✓ Partite completate: {successi}")
    if errori > 0:
        print(f"  ✗ Errori: {errori}")

    return results

async def run_championship(ws_callback=None, giornate_limit=None):
    try:
        await clear_championship_results()

        calendario = genera_calendario(match.teams)

        # Se giornate_limit è specificato, limita le giornate
        giornate_da_giocare = list(calendario.keys())
        if giornate_limit:
            giornate_da_giocare = giornate_da_giocare[:giornate_limit]

        for giornata_num in giornate_da_giocare:
            print(f"\n{'='*50}")
            print(f"INIZIO GIORNATA {giornata_num}")
            print(f"{'='*50}\n")

            partite = calendario[giornata_num]

            # Attende che TUTTE le partite della giornata siano finite
            await run_giornata(giornata_num, partite, ws_callback=ws_callback)

            print(f"\n{'='*50}")
            print(f"FINE GIORNATA {giornata_num} - Tutte le partite completate")
            print(f"{'='*50}\n")

            # Pausa tra le giornate (solo se non è l'ultima)
            if giornata_num < giornate_da_giocare[-1]:
                print(f"Pausa prima della prossima giornata...\n")
                await asyncio.sleep(5)


    except Exception as e:
        print(f"Errore durante il campionato: {e}")

async def genera_classifica():
    """Genera la classifica del campionato"""
    partite = await db.championship_results.find().to_list(None)

    classifica = {}

    # Inizializza squadre
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

    # Elabora partite
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

        # Assegna punti
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

    # Calcola quozienti
    for team, dati in classifica.items():
        if dati["set_persi"] > 0:
            dati["quoziente_set"] = dati["set_vinti"] / dati["set_persi"]
        else:
            dati["quoziente_set"] = dati["set_vinti"]

        if dati["punti_subiti"] > 0:
            dati["quoziente_punti"] = dati["punti_fatti"] / dati["punti_subiti"]
        else:
            dati["quoziente_punti"] = dati["punti_fatti"]

    # Ordina classifica
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
    # Test con solo 2 giornate
    asyncio.run(run_championship(giornate_limit=2))
