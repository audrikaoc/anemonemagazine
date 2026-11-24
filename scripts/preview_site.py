#!/usr/bin/env python3
"""Serve the generated site locally with browser caching disabled."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / 'docs'
ADDRESS = ('127.0.0.1', 8017)


class PreviewHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()


if __name__ == '__main__':
    handler = partial(PreviewHandler, directory=DOCS)
    with ThreadingHTTPServer(ADDRESS, handler) as server:
        print(f'Anemone preview at http://{ADDRESS[0]}:{ADDRESS[1]}/', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
