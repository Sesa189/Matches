import tornado.escape
from bson import ObjectId
from backend.db import tasks
from datetime import datetime

class MatchHandler:
    async def get(self):
        cursor = tasks.find()
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

        return self.write_json({"items": out})