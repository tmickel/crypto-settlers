if __name__ == "__main__":
    print "Welcome to crypto-settlers!  To begin, enter the IP address of each user who will be playing the game."
    player_ips = []
    while True:
        ip = raw_input("IP address [or enter to finish]: ")
        if ip == "": break
        player_ips.append(ip)
    print "Connecting..."
