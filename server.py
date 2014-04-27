import json
import SocketServer
import threading
import sign

settlers_server = None
gp = None

class SettlersNetworkServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True

class SettlersNetworkServerHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        global gp
        signer = sign.Sign()
        public_key = "" # for this particular client
        client_uid = ""
        while True:
            try:
                data = self.rfile.readline().strip()
                if data != "":
                    json_data = json.loads(data)                    
                    if public_key == "":
                        try:
                            split = json.loads(json_data['message'])
                            client_uid = split['uid']
                            if type(split) == dict and 'public_key' in split:
                                public_key = split['public_key']
                                # Respond with our UID
                                self.wfile.write(json.dumps({"success": True, "uid": gp.uid}) + '\n')
                            else:
                                print "Error: client first needs to send public key"
                                self.wfile.write(json.dumps({"success": False}) + '\n')
                                return
                        except Exception, e:
                            print "Error: client failed in sending public key", e
                            self.wfile.write(json.dumps({"success": False}) + '\n')
                            return
                    # We have a public key for this client - verify that it matches
                    # Also verify that this client is not trying to spoof their UID
                    verified = signer.verify(public_key, json_data['signature'], json_data['message'])
                   
                    if not verified:
                        self.wfile.write(json.dumps({"success": False}) + '\n')
                        return
                    
                    # This expected client is who they say they are..
                    verified_message_data = json.loads(json_data['message'])
                    if verified_message_data['uid'] != client_uid:
                        print "UID is not verified"
                        self.wfile.write(json.dumps({"success": False}) + '\n')
                        return
                    # Handle the request
                    if gp is not None:
                        gp.handle_message(verified_message_data)
                else:
                    return
            except Exception, e:
                print "Network exception: ", e
                self.wfile.write(json.dumps({"success": False}) + '\n')
                return

def run_server(hostname, port, gameplay):
    global settlers_server
    global gp
    gp = gameplay
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
