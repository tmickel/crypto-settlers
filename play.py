import server
import client
import time
import sys

def game_init():
    server_at = raw_input("Starting local server...hostname:port? ")
    hostname, port = server_at.split(':')
    port = int(port)
    if port < 1000 or port > 65535:
        print "Port must be 1000-65535"
        return
    server.run_server(hostname, port)
    print "Welcome to crypto-settlers!  To begin, enter [ip:port] of each user who will be playing the game."
    player_ips = []
    player_clients = []
    while True:
        ip = raw_input("Player ip:port [or enter to finish]: ")
        if ip == "": break
        player_ips.append(ip)
    print player_ips
    print "Connecting..."
    for addr in player_ips:
        ip, port = addr.split(':')
        port = int(port)
        new_client = client.SettlersNetworkClient(ip, port)
        success = new_client.connect()
        while not success:
            print "Couldn't connect to ", addr, ", trying again in 2s..."
            time.sleep(2)
            success = new_client.connect()
        new_client.send_data({"msg": "hello!"})
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
