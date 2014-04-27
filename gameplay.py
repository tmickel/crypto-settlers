# Main logic for game play.
# Once play.py has successfully negotiated network connections with
# all other specified players, gameplay.py is invoked to run the main logic
# of the game as well as the input/output loop.

import time

class Gameplay():
    def __init__(self, uid):
        self.client_connections = []
        self.phase = 0
        self.uid = uid
        self.players_ready = {}

    def setup_client_connections(self, client_connections):
        """Receive connected clients from the network initializer."""
        self.client_connections = client_connections
        self.players_ready = {c.their_uid: False for c in self.client_connections}
    
    def broadcast_message(self, message):
        """Broadcast a message to all other players.  No response is given."""
        for c in self.client_connections:
            if not c.send_data(message):
                print "Something is wrong!  Player returned an error."
    
    def send_message(self, uid, message):
        """Send a message to a particular UID.  No response is given."""
        for c in self.client_connections:
            if c.their_uid == uid:
                if not c.send_data(message):
                    print "Something is wrong!  Player returned an error."
                return
    
    def handle_message(self, message):
        """Receive a message from another player.  No response is required."""
        if 'ready' in message:
            # Welcome phase - mark this player as ready
            self.players_ready[message['uid']] = message['ready']
            # Resend the welcome message to this client, just in case they just
            # became ready...
            self.send_message(message['uid'], {'ready': True})   
    
    def run(self):
        """Run the game.  This function should not return until we are finished."""
        print "entering run"
        while True:
            if self.phase == 0:
                # Welcome phase.  Tell all the other players our unique ID
                self.broadcast_message({'ready': True})
                print "Waiting for all players to be ready..."
                while not all(self.players_ready.values()):
                    time.sleep(1)
                    print "..."
                print "Ready to play!  Starting game in 3 seconds..."
                time.sleep(3)
                self.phase += 1
            elif self.phase == 1:
                # Board negotiation phase.  We shuffle the board pieces...
                print "Negotiating board..."
                return
                