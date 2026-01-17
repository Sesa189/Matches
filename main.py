import json
import sys
import asyncio
from backend.db import tournament_results, championship_results

# FIX PER WINDOWS - deve essere all'inizio prima di qualsiasi altra cosa
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import logging
from backend.db import matches
import tornado.web
import tornado.websocket
import backend.simulators.tournament as tournament
import backend.simulators.championship as championship
import backend.simulators.match as match


BROKER = "test.mosquitto.org"
#TOPIC = "volley/matches/#"

clients = set()
tournament_task = None  # Task globale per il torneo
championship_task = None  # Task globale per il campionato
championship_calendar = None

async def broadcast_to_clients(message):
    """Invia messaggi solo ai client attivi"""
    disconnected = set()
    for c in list(clients):
        try:
            if c.ws_connection:  # Verifica che la connessione sia ancora aperta
                await c.write_message(json.dumps(message))
        except Exception as e:
            print(f"Errore invio messaggio: {e}")
            disconnected.add(c)

    # Rimuovi client disconnessi
    clients.difference_update(disconnected)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class MatchDetailHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("match.html")

class WSHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    async def open(self):
        global tournament_task, championship_task, championship_calendar
        print("WebSocket aperto")
        clients.add(self)

        if championship_calendar is None:
            print("Genero calendario campionato")
            championship_calendar = championship.genera_calendario(match.teams)

        await self.write_message(json.dumps({
            "type": "calendario",
            "category": "campionato",
            "data": championship_calendar
        }))

        # Avvia il torneo solo se non è già in esecuzione
        if tournament_task is None or tournament_task.done():
            print("Avvio nuovo torneo...")
            tournament_task = asyncio.create_task(tournament.run_tournament(broadcast_to_clients))
        else:
            print("Torneo già in esecuzione, client aggiunto agli spettatori")

        # Avvia il campionato solo se non è già in esecuzione
        if championship_task is None or championship_task.done():
            print("Avvio nuovo campionato (prime 3 giornate)...")
            championship_task = asyncio.create_task(championship.run_championship(broadcast_to_clients, giornate_limit=3))
        else:
            print("Campionato già in esecuzione, client aggiunto agli spettatori")

    def on_close(self):
        print("WebSocket chiuso")
        clients.remove(self)

    async def load_tournament(self):
        out = []
        async for t in tournament_results.find():
            out.append({
                "team1": t["team1"],
                "team2": t["team2"],
                "date": t.get("date", ""),
                "time": t.get("time", ""),
                "result": " ".join(t["risultato"]) if isinstance(t["risultato"], list) else t["risultato"],
                "state": "FINISHED"
            })

        await self.write_message({
            "type": "matches",
            "category": "torneo",
            "data": out
        })

    async def load_championship(self):
        out = []
        async for c in championship_results.find():
            out.append({
                "team1": c["team1"],
                "team2": c["team2"],
                "date": f"Giornata {c['giornata']}",
                "time": "",
                "result": " ".join(c["risultato"]),
                "state": "FINISHED"
            })

        await self.write_message({
            "type": "matches",
            "category": "campionato",
            "data": out
        })


    async def load_matches(self):
        cursor = matches.find()
        print("c", cursor)
        out = []
        async for t in cursor:
            out.append({
                "type": "matches",
                "category": "torneo",
                "id": str(t["_id"]),
                "team1": t["team1"],
                "team2": t["team2"],
                "date": t["date"],
                "time": t["time"],
                "result": t["result"],
                "state": t["state"]
            })

        print(out)

        return self.write_message({"type":"matches","data": out})


'''
async def mqtt_listener():

    logging.info("Connessione al broker MQTT...")

    async with aiomqtt.Client(BROKER) as client:
        await client.subscribe(TOPIC)
        logging.info(f"Iscritto al topic: {TOPIC}")

        async for message in client.messages:
            payload = message.payload.decode()
            data = json.loads(payload)

            ws_message = json.dumps({
                "type": "sensor",
                "data": data
            })

            # inoltro ai client WebSocket
            for c in list(clients):
                c.write_message(ws_message)
'''

async def main():
    logging.basicConfig(level=logging.INFO)

    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/ws", WSHandler),
            (r"/match.html", MatchDetailHandler),
        ],
        template_path="./static",
        static_path="./static",
    )

    app.listen(8888)
    print("Server Tornado avviato su http://0.0.0.0:8888")

    #asyncio.create_task(mqtt_listener())

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
