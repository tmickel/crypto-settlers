import json
import SocketServer
import threading

settlers_server = None

class SettlersNetworkServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True

class SettlersNetworkServerHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        while True:
            try:
                data = self.rfile.readline().strip()
                if data != "":
                    json_data = json.loads(data)
                    print json_data
                    self.wfile.write(data + '\n') # Echo
                else:
                    return
            except Exception, e:
                print "Network exception: ", e
                return

def run_server(hostname, port):
    global settlers_server
    def thread_server():
        global settlers_server
        settlers_server = SettlersNetworkServer((hostname, port),
                                       SettlersNetworkServerHandler)
        settlers_server.serve_forever()
    server_thread = threading.Thread(target=thread_server)
    server_thread.daemon = True
    server_thread.start()

def shutdown_server():
    global settlers_server
    settlers_server.shutdown()
