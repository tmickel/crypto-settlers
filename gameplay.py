# Main logic for game play.
# Once play.py has successfully negotiated network connections with
# all other specified players, gameplay.py is invoked to run the main logic
# of the game as well as the input/output loop.

import random
import time
import board

class Gameplay(object):
    def __init__(self, uid):
        self.client_connections = []
        self.phase = 0
        self.uid = uid
        self.players_ready = {}
        self.players_state = {}

    def setup_client_connections(self, client_connections):
        """Receive connected clients from the network initializer."""
        self.client_connections = client_connections
        self.players_ready = {c.their_uid: False for c in 
                              self.client_connections} # For welcoming
        self.players_state = {c.their_uid: [False, []] for c in self.client_connections} #[board, [key, iv]]
        self.players_state[self.uid] = [False, []] # for board negotiation
    
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
        if 'board_suggestion' in message:
            # Save the player's board suggestion
            self.players_state[message['uid']][0] = message['board_suggestion']
        if 'board_keyiv' in message:
            # Save the player's board key/iv - AFTER all suggestions
            self.players_state[message['uid']][1] = message['board_keyiv']
    
    def run(self):
        """Run the game.  This function should not return until we are finished."""
        while True:
            if self.phase == 0: self.welcome_run()
            elif self.phase == 1: self.board_negotiation_run()
            else:
                time.sleep(10)
                return

    def welcome_run(self):
        """Welcome phase.  Tell all the other players that we're ready to play."""
        self.broadcast_message({'ready': True})
        print "Waiting for all players to be ready..."
        while not all(self.players_ready.values()):
            time.sleep(1)
            print "..."
        print "Ready to play!  Starting game in 3 seconds..."
        time.sleep(3)
        self.phase += 1
    
    def board_negotiation_run(self):
        """Board negotiation phase.  We shuffle the board pieces..."""
        print "Negotiating board..."
        # Consistent negotiation order across clients
        negotiate_order = sorted([c.their_uid for c in self.client_connections] + [self.uid])
        my_key = None
        my_iv = None
        i = 0 # Current client
        for uid in negotiate_order:
            # Wait for the i-th player with UID to suggest their board.
            # If we are the i-th player, suggest a board. 
            if uid == self.uid:
                # We need to generate and send out the initial board.
                print "Our turn to shuffle the board..."
                # Use the previous player's suggestion if it exists, or 1-19.
                old_board = range(19) if i == 0 else self.players_state[negotiate_order[i-1]][0]
                board_suggestion, my_key, my_iv = board.board_shuffle_and_encrypt(old_board)
                self.players_state[self.uid] = [board_suggestion, [my_key, my_iv]]
                self.broadcast_message({'board_suggestion': board_suggestion})
            while self.players_state[uid][0] == False:
                print "Waiting for someone else to shuffle the board..."
                time.sleep(2)
            i += 1
        print "All board shuffles given.  Sharing keys..."
        # Take the last broadcasted board.  Decrypt it in reverse order using everyone's keys...
        self.broadcast_message({"board_keyiv": (my_key, my_iv)})
        self.decided_board = self.players_state[negotiate_order[-1]][0]
        
        while not all([a[1] for a in self.players_state.values()]):
            time.sleep(2)
        
        # We have all the information needed for the agreed-upon shuffled board.
        # Decrypt!
        for i in range(len(negotiate_order)):
            j = len(negotiate_order) - i - 1 # Index of player, last->first
            # Decrypt the board decided_board using the key, IV given by j
            key, iv = self.players_state[negotiate_order[j]][1]
            self.decided_board = board.board_decrypt(self.decided_board, key, iv)
        
        self.decided_board = [int(k) for k in self.decided_board]
        # Basic sanity check - if this fails the first person to suggest the
        # board was lying, and we all quit the game.
        assert len(self.decided_board) == 19
        for card in range(19):
            assert card in self.decided_board
        
        print "The decided board is:", self.decided_board
        self.phase += 1
