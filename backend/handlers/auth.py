import tornado.web
import tornado.escape
import bcrypt


class BaseHandler(tornado.web.RequestHandler):
    def write_json(self, data, status=200):
        self.set_status(status)
        self.set_header("Content-Type", "application/json")
        self.write(tornado.escape.json_encode(data))
