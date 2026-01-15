import time
import random

def percentage_calculator(team1, team2):
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


def match_simulation(team1, team2):
    # Richiamo la funzione per rendere le due percentuali uguali a 100 se sommate
    w = percentage_calculator(team1, team2)
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

    while win == False: #Finché nessuno ha ancora vinto
        #Aggiunta randomica di punti basandosi su probabilità
        team = random.choices([1,2], weights=w, k=1)[0]
        if team == 1:
            point1 += 1
            ball = 1
        elif team == 2:
            point2 += 1
            ball = 2

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
            if set1 == 3 or set2 == 3: #Una delle due squadre raggiunge 3 set e vince la partita
                win = True
                if set1 == 3:
                    winner = 1
                elif set2 ==  3:
                    winner = 2
            else: #Nessuno ha ancora vinto, aggiungo un set e continuo
                c += 1
                result.append("")
    print(f"risultato: {result}")
    print(f"vincitore:{winner}")
    return winner
