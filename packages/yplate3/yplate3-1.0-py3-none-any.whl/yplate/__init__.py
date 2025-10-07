from http.server import BaseHTTPRequestHandler, HTTPServer
import os

class Yplate:
    def __init__(self):
        self.routes = {}

    def route(self, path):
        def decorator(func):
            self.routes[path] = func
            return func
        return decorator

    def run(self, host="127.0.0.1", port=8080):
        app = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path in app.routes:
                    try:
                        response = app.routes[self.path]()
                        self.send_response(200)
                        self.send_header("Content-type", "text/html; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(response.encode())
                    except Exception as e:
                        self.send_response(500)
                        self.end_headers()
                        self.wfile.write(f"<h1>500 Internal Server Error</h1><pre>{e}</pre>".encode())
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(f"<h1>404 Not Found</h1><p>Страница не найдена</p>")

        print(f"🚀 Yplate сервер запущен: http://{host}:{port}")
        HTTPServer((host, port), Handler).serve_forever()
