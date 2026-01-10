import time
import random

def match_simulation(w):
    ball = random.randint(1,2)
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
            else: #Nessuno ha ancora vinto, aggiungo un set e continuo
                c += 1
                result.append("")
    print(result)

teams = [
    {"name": "Sir Safety Perugia", "weight": 53},
    {"name": "Itas Trentino", "weight": 52},
    {"name": "Cucine Lube Civitanova", "weight": 52},
    {"name": "Modena Volley", "weight": 51},
    {"name": "Allianz Milano", "weight": 50},
    {"name": "Gas Sales Bluenergy Piacenza", "weight": 51},
    {"name": "Vero Volley Monza", "weight": 49},
    {"name": "Pallavolo Padova", "weight": 48},
    {"name": "Cisterna Volley", "weight": 48},
    {"name": "Rana Verona", "weight": 50},
    {"name": "Taranto Prisma", "weight": 47},
    {"name": "Revivre Cantù", "weight": 47},
    {"name": "Pallavolo Cuneo", "weight": 48},
    {"name": "Brescia Volley", "weight": 47}
]

match_simulation([53, 47])