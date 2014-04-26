import json
import SocketServer
import threading
import sign

settlers_server = None

class SettlersNetworkServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True

class SettlersNetworkServerHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        signer = sign.Sign()
        while True:
            public_key = "" # for this particular client
            try:
                data = self.rfile.readline().strip()
                if data != "":
                    json_data = json.loads(data)
                    
                    if public_key == "":
                        try:
                            split = json.loads(json_data['message'])
                            if type(split) == dict and 'public_key' in split:
                                public_key = split['public_key']
                            else:
                                print "Error: client first needs to send public key"
                                self.wfile.write(json.dumps({"success": False}) + '\n')
                                return
                        except Exception, e:
                            print "Error: client failed in sending public key"
                            self.wfile.write(json.dumps({"success": False}) + '\n')
                            return
                    # We have a public key for this client - verify that it matches
                    verified = signer.verify(public_key, json_data['signature'], json_data['message'])
                   
                    if not verified:
                        self.wfile.write(json.dumps({"success": False}) + '\n')
                        return

                    verified_message_data = json.loads(json_data['message'])
                    print verified_message_data
                    # Handle the request
                    self.wfile.write(json.dumps({"success": True}) + '\n')
                else:
                    return
            except Exception, e:
                print "Network exception: ", e
                self.wfile.write(json.dumps({"success": False}) + '\n')
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
