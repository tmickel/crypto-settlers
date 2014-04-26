import server
import client
import time
import sys
import sign

def game_init():
    # Generate keys
    signature_verify = sign.Sign()

    # Start a local server for receiving messages from other players
    server_at = raw_input("Starting local server...hostname:port? ")
    hostname, port = server_at.split(':')
    port = int(port)
    if port < 1000 or port > 65535:
        print "Port must be 1000-65535"
        return
    server.run_server(hostname, port)
    
    # And connect to other players' servers to send messages.  This two-way
    # network structure should simplify trying to figure out who we're already
    # connected to, etc.  Each player should just make a connection to each other,
    # so in the end there should be 2*N connections.
    print "Welcome to crypto-settlers!  To begin, enter [ip:port] of each user who will be playing the game."
    player_ips = []
    player_clients = []
    while True:
        ip = raw_input("Player ip:port [or enter to finish]: ")
        if ip == "": break
        player_ips.append(ip)
    print "Connecting..."
    for addr in player_ips:
        ip, port = addr.split(':')
        port = int(port)
        new_client = client.SettlersNetworkClient(ip, port, signature_verify)
        success = new_client.connect()
        # Loop around and try to connect until all players are online
        while not success:
            print "Couldn't connect to ", addr, ", trying again in 2s..."
            time.sleep(2)
            success = new_client.connect()
        # Send public key 
        new_client.send_key()
        # Add connection to a list
        player_clients.append(new_client)
    print "All connected!"

    print "Disconnecting clients..."
    for c in player_clients:
        c.disconnect()

    print "Shutting down local server..."
    server.shutdown_server()
    sys.exit(0)

if __name__ == "__main__":
    game_init()
