import time
import datetime
import random
import asyncio

# Verisone iniziale
'''
async def percentage_calculator(team1, team2):
    # Questa funzione serve ad assicurarsi che le due percentuali di vittoria siano 100 se sommate

    if team1 + team2 <= 100: # Se la somma è minore di 100
        # Faccio la differenza tra le due percentuali
        diff = (team1 if team1 >= team2 else team2) - (team2 if team1 >= team2 else team1)
        # Aggiungo metà della differenza ad entrambe le percentuali
        team1 += team1 + diff/2
        team2 += team2 + diff/2
        # Ottengo il totale
        tot = team1 + team2
        while tot <= 100: # Finché il totale è minore di 100 aggiungo ogni volta 1 ad entrambe le percentuali
            team1 += 1
            team2 += 1
            tot = team1 + team2

    if team1 + team2 >= 100: # Se la somma è maggiore di 100
        tot = team1 + team2
        while tot >= 100: # Finché il totale è maggiore di 100 tolgo ogni volta 1 ad entrambe le percentuali
            team1 -= 1
            team2 -= 1
            tot = team1 + team2
        if tot != 100: # Se il totale non è ancora uguale a 100
            # Calcolo la differenza
            diff = (team1 if team1 >= team2 else team2) - (team2 if team1 >= team2 else team1)
            # Aggiungo metà della differenza ad entrambe le percentuali
            team1 += team1 + diff/2
            team2 += team2 + diff/2
    return [team1, team2]
'''

async def percentage_calculator(team1, team2):
    # Assicura che le percentuali sommino a 100
    tot = team1 + team2
    team1 = team1 * 100 / tot
    team2 = team2 * 100 / tot
    return [team1, team2]

def generate_match_id(category, stage, team1, team2):
        return f"{category}_{stage}_{team1}_{team2}".replace(" ", "_").lower()


async def match_simulation(name_team1, name_team2, team1, team2, stage, categoria, ws_callback=None):

    match_id = generate_match_id(
        "torneo",
        stage,
        name_team1,
        name_team2
    )

    stage_to_number = {
        "ottavi": 8,
        "quarti": 4,
        "semifinali": 2,
        "finale": 1
    }

    if ws_callback:
        await ws_callback({
            "type": "matches",
            "category": categoria,
            "number": stage_to_number[stage],
            "team1": name_team1,
            "team2": name_team2,
            "date": datetime.datetime.now().strftime("%d/%m/%Y"),
            "time": "00:00",
            "state": "LIVE",
            "result": "0 : 0",
            "events": [],
            "matchId": match_id
        })

    # Richiamo la funzione per rendere le due percentuali uguali a 100 se sommate
    w = await percentage_calculator(team1, team2)
    # La prima battuta viene assegnata randomicamente (50/50, come il lancio della moneta delle vere partite)
    ball = random.randint(1,2)
    # Inizializzazione di tutte le variabili
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

    while win == False: #Finché nessuno ha ancora vinto
        await asyncio.sleep(random.uniform(0.3, 0.6))
        time += 60

        #Aggiunta randomica di punti basandosi su probabilità
        team = random.choices([1,2], weights=w, k=1)[0]
        if team == 1:
            point1 += 1
            ball = 1
        elif team == 2:
            point2 += 1
            ball = 2

        # verifica timeout ogni 10 punti totali nel set
        total_points = point1 + point2
        if total_points > 0 and total_points % 10 == 0:
            # timeout della squadra in svantaggio
            if point1 < point2 and timeouts[1] > 0:
                events.append(f"Timeout chiamato da {team1}")
                await asyncio.sleep(3)
                timeouts[1] -= 1
            elif point2 < point1 and timeouts[2] > 0:
                events.append(f"Timeout chiamato da {team2}")
                await asyncio.sleep(3)
                timeouts[2] -= 1

        if ws_callback:
            await ws_callback({
                "type": "matches",
                "category": categoria,
                "number": stage_to_number[stage],
                "team1": name_team1,
                "team2": name_team2,
                "date": datetime.datetime.now().strftime("%d/%m/%Y"),
                "time": f"{int(time // 60):02d}:{int(time % 60):02d}:{int((time%1)*60):02d}",
                "state": "LIVE",
                "result": result,
                "events": events,
                "matchId": match_id
            })

        #Nei primi 4 set punteggio massimo a 25, nel quinto a 15
        if setcounter <= 4:
            p_max = 25
        elif setcounter == 5:
            ball = random.randint(1, 2)
            p_max = 15

        #Se si supera il punteggio massimo con un vantaggio di almeno 2 punti si vince un set
        if point1 >= p_max and point1-point2 >= 2:
            s_end = True
            set1 += 1
        elif point2 >= p_max and point2-point1 >= 2:
            set2 += 1
            s_end = True

        #Creo una stringa col risultato del set e la aggiungo alla lista result
        line = f"{point1} : {point2}"
        result[c] = line

        if s_end == True: #Appena finito un set
            point1 = 0
            point2 = 0
            setcounter += 1
            s_end = False
            timeouts = {1: 2, 2: 2}
            await asyncio.sleep(3)

            if set1 == 3 or set2 == 3: #Una delle due squadre raggiunge 3 set e vince la partita
                win = True
                if set1 == 3:
                    winner = 1
                elif set2 ==  3:
                    winner = 2

                if ws_callback:
                    await ws_callback({
                        "type": "matches",
                        "category": categoria,
                        "number": stage_to_number[stage],
                        "team1": name_team1,
                        "team2": name_team2,
                        "date": datetime.datetime.now().strftime("%d/%m/%Y"),
                        "time": f"{int(time // 60):02d}:{int(time % 60):02d}:{int((time%1)*60):02d}",
                        "state": "FINISHED",
                        "result": result,
                        "events": events,
                        "winner": team1 if winner == 1 else team2,
                        "matchId": match_id
                    })
            else: #Nessuno ha ancora vinto, aggiungo un set e continuo
                c += 1
                result.append("")

    print(f"risultato: {result}")
    print(f"vincitore:{winner}")
    return winner, result, events

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
    "Delta Group Porto Viro" : 44
}
