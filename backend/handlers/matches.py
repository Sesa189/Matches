from Matches.backend.db import matches
from Matches.backend.handlers.auth import BaseHandler


class MatchHandler(BaseHandler):
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

        print(out)

        return self.write_json({"items": out})

