from Matches.backend.db import matches
from Matches.backend.handlers.auth import BaseHandler


class LoadMatchHandler(BaseHandler):
    async def get(self):
        cursor = matches.find()
        print("c",cursor)
        out = []
        async for t in cursor:
            out.append({
                "id": str(t["_id"]),
                "team1" : t["team1"],
                "team2": t["team2"],
                "date": t["date"],
                "time": t["time"],
                "result": t["result"]
            })

        return self.write_json({"data": out})

