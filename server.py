#!/usr/bin/env python

import argparse
import http.server
import os

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    storagedir=None
    storageprefix="storage"
 
    def translate_path(self, path):
        
        print("XX Translate.. " + path)
        path = super().translate_path(path)
        if self.storagedir:
            path = path.replace(os.path.join(os.getcwd(),self.storageprefix),self.storagedir)       
        print("XXto "+path)
        return path
            
    def do_PUT(self):
        path = self.translate_path(self.path)
        if not path.startswith(os.path.join(os.getcwd(),self.storageprefix)):
            self.send_response(405, "Method Not Allowed")
            self.wfile.write("PUT not allowed outside of storage.\n".encode())
            self.end_headers()
            return
        else:
            try:
                os.makedirs(os.path.dirname(path))
            except FileExistsError: pass
            length = int(self.headers['Content-Length'])
            with open(path, 'wb') as f:
                f.write(self.rfile.read(length))
            self.send_response(201, "Created")
            self.end_headers() 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', '-b', default='127.0.0.1', metavar='ADDRESS',
                        help='Specify alternate bind address '
                             '[default: all interfaces]')
    parser.add_argument('port', action='store',
                        default=8000, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
    parser.add_argument('--storage', type=str, metavar="STORAGEDIR",
                        help="Specify a read/write storage directory. It will be available under ../#storage/file")
    args = parser.parse_args()

    HTTPRequestHandler.storagedir = args.storage
    
    http.server.test(HandlerClass=HTTPRequestHandler, port=args.port, bind=args.bind)
