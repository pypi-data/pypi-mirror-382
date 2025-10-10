from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer

from contextlib import contextmanager
from functools import partial
from threading import Thread
from time import sleep
from urllib.request import urlopen, Request


class RequestHandler(BaseHTTPRequestHandler):
    routes = (
        ('get', '/hello', 'hello'),
    )

    def __init__(self, *a, **k):
        self.map = dict(
            get  = dict(),
            post = dict(),
        )
        for meth, path, func in self.routes:
            self.map[meth][path] = getattr(self, func)
        self.map['post']['/shutdown'] = self.shutdown
        super().__init__(*a, **k)

    def hello(self):
        return HTTPStatus.OK, 'Hi there'

    def shutdown(self):
        setattr(self.server, '_BaseServer__shutdown_request', True)
        return 200, 'shuting down'

    def not_found(self):
        return HTTPStatus.NOT_FOUND, f'{self.command} {self.path} Not Found'

    def response(self, code, body):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(body.encode())

    @property
    def body(self):
        size = int(self.headers['Content-Length'])
        return self.rfile.read(size).decode()

    def do_GET(self):
        print(f'GET {self.path}\n{self.headers}')
        route = self.map['get'].get(self.path, self.not_found)
        code, body = route()
        self.response(code, body)

    def do_POST(self):
        print(f'POST {self.path}\n{self.headers}\n{self.body}')
        route = self.map['post'].get(self.path, self.not_found)
        code, body = route()
        self.response(code, body)


class Server:
    '''Generic HTTP server.

    Intended to be used as a mock for testing puposes.
    '''
    def __init__(self, Handler=RequestHandler):
        self.Handler = Handler

    def serve(self, adr='localhost', port=7777):
        server = HTTPServer((adr, port), self.Handler)
        print(f'Listening on {adr}:{port} ...\n')
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        server.server_close()


def request(url, method='GET'):
    resp = urlopen(Request(url, method=method))
    code = resp.code
    text = resp.read().decode('utf-8')
    return code, text


@contextmanager
def serve(Handler, adr='localhost', port=7777):
    server = Server(Handler)
    thread = Thread(
        target = partial(server.serve, adr=adr, port=port),
        daemon = True,
    )
    thread.start()
    sleep(1)

    yield

    code, text = request(f'http://{adr}:{port}/shutdown', 'POST')
    assert code == 200
    thread.join()
