#!/usr/bin/env python

### beware! this might be full of bugs and security holes


import argparse
import http.server
import os
import subprocess

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    storagedir=None
    storageprefix="storage"
 
    def translate_path(self, path):
        path = super().translate_path(path)
        if self.storagedir:
            path = os.path.normpath(path.replace(os.path.join(os.getcwd(), self.storageprefix, ''), self.storagedir))
        return path
            
    def do_PUT(self):
        path = self.translate_path(self.path)
        print("PUT  "+ self.path +' '+path )
        if not self.path.startswith("/" + self.storageprefix):
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
            subprocess.call('cd "{}"; git pull origin master2; git add "{}"; git commit -m "openJSCAD autocommit"; git push origin master:master2'.format(self.storagedir,path), shell=True)
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
