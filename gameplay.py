# Main logic for game play.
# Once play.py has successfully negotiated network connections with
# all other specified players, gameplay.py is invoked to run the main logic
# of the game as well as the input/output loop.

import random
import time
import board
import dice
import ui

# To do for code for Wednesday:
# -finish up turn order
# -players choose two houses and two roads to start
# -making the bank with resources
# -a basic turn, with resource distribution

# -trading and the robber

# to do: winner determination, development cards

class Gameplay(object):
    def __init__(self, uid):
        self.client_connections = []
        self.phase = 0
        self.uid = uid
        self.players_ready = {}
        self.die_rolls = {}
        self.die_turn_count = 0
        self.shuffle_turn_count = 0
        self.shuffle_rolls = {}
        self.all_uids = []
        self.player_number = -1
        self.turn_order_first = None
        self.ui_board = None
        self.initialization_round = 0
        self.init_rounds = {}

    def setup_client_connections(self, client_connections):
        """Receive connected clients from the network initializer."""
        self.client_connections = client_connections
        self.players_ready = {c.their_uid: False for c in 
                              self.client_connections} # For welcoming
    
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
        if 'shuffle_suggestion' in message:
            # Save the player's board suggestion
            s_t = int(message['shuffle_turn'])
            if s_t not in self.shuffle_rolls:
                self.shuffle_rolls[s_t] = {c.their_uid: [None, None] for c in self.client_connections}
            self.shuffle_rolls[s_t][message['uid']][0] = message['shuffle_suggestion']
        if 'shuffle_keyiv' in message:
            # Save the player's board key/iv - AFTER all suggestions
            s_t = int(message['shuffle_turn'])
            self.shuffle_rolls[s_t][message['uid']][1] = message['shuffle_keyiv']
        if 'die_commit' in message:
            d_t = int(message['die_turn'])
            # Save the player's die commitment
            if d_t not in self.die_rolls:
                self.die_rolls[d_t] = {c.their_uid: [None, None] for c in self.client_connections} 
            self.die_rolls[d_t][message['uid']][0] = message['die_commit']
        if 'die_roll' in message:
            # Save the player's die roll
            d_t = int(message['die_turn'])
            self.die_rolls[d_t][message['uid']][1] = message['die_roll']
        if 'initialization_round' in message:
            self.init_rounds[message['initialization_round']] = (message['uid'], message['house_place'], message['road_place'])       
    
    def run(self):
        """Run the game.  This function should not return until we are finished."""
        while True:
            if self.phase == 0: self.welcome_run()
            elif self.phase == 1: self.board_negotiation_run()
            elif self.phase == 2: self.turn_order_run()
            elif self.phase == 3: self.initial_placement_run()
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
        self.all_uids = [c.their_uid for c in self.client_connections] + [self.uid]
        self.player_number = ui.uid_to_friendly(self.uid, self.all_uids)
        print "You are player", self.player_number
        time.sleep(3)
        self.phase += 1
        
    def run_public_shuffle(self, suggestion, encrypt_fun, decrypt_fun):
        if self.shuffle_turn_count not in self.shuffle_rolls:
            self.shuffle_rolls[self.shuffle_turn_count] = {c.their_uid: [False, []] for c in self.client_connections} #[shuffle, [key, iv]]
            self.shuffle_rolls[self.shuffle_turn_count][self.uid] = [False, []]
        # Consistent negotiation order across clients
        negotiate_order = sorted(list(self.all_uids))
        my_key = None
        my_iv = None
        i = 0 # Current client
        for uid in negotiate_order:
            # Wait for the i-th player with UID to suggest their shuffle.
            # If we are the i-th player, suggest a shuffle. 
            if uid == self.uid:
                # We need to generate and send out the initial shuffle.
                print "Our turn to shuffle..."
                # Use the previous player's suggestion if it exists, or 1-19.
                old_shuffle = suggestion if i == 0 else self.shuffle_rolls[self.shuffle_turn_count][negotiate_order[i-1]][0]
                shuffle_suggestion, my_key, my_iv = encrypt_fun(old_shuffle)
                self.shuffle_rolls[self.shuffle_turn_count][self.uid] = [shuffle_suggestion, [my_key, my_iv]]
                self.broadcast_message({'shuffle_suggestion': shuffle_suggestion, 'shuffle_turn': self.shuffle_turn_count})
            while self.shuffle_rolls[self.shuffle_turn_count][uid][0] == False:
                print "Waiting for someone else to shuffle..."
                time.sleep(2)
            i += 1
        print "All shuffles given.  Sharing keys..."
        # Take the last broadcasted shuffle.  Decrypt it in reverse order using everyone's keys...
        self.broadcast_message({"shuffle_keyiv": (my_key, my_iv), 'shuffle_turn': self.shuffle_turn_count})
        decided_shuffle = self.shuffle_rolls[self.shuffle_turn_count][negotiate_order[-1]][0]
        
        while not all([a[1] for a in self.shuffle_rolls[self.shuffle_turn_count].values()]):
            time.sleep(2)
        
        # We have all the information needed for the agreed-upon shuffle.
        # Decrypt!
        for i in range(len(negotiate_order)):
            j = len(negotiate_order) - i - 1 # Index of player, last->first
            # Decrypt the shuffle using the key, IV given by j
            key, iv = self.shuffle_rolls[self.shuffle_turn_count][negotiate_order[j]][1]
            decided_shuffle = decrypt_fun(decided_shuffle, key, iv)
        
        decided_shuffle = [int(k) for k in decided_shuffle]
        # Basic sanity check - if this fails the first person to suggest the
        # shuffle was lying, and we all quit the game.
        assert len(decided_shuffle) == len(suggestion)
        for card in suggestion:
            assert card in decided_shuffle
        self.shuffle_turn_count += 1
        return decided_shuffle
    
    def board_negotiation_run(self):
        """Board negotiation phase.  We shuffle the board pieces..."""
        print "Negotiating board..."
        self.decided_board = self.run_public_shuffle(range(19), board.board_shuffle_and_encrypt, board.board_decrypt)
        time.sleep(3)
        print "Negotiating board roll values..."
        self.decided_board_roll_values = self.run_public_shuffle(range(18), board.board_shuffle_and_encrypt, board.board_decrypt)
                
        self.ui_board = ui.UIBoard(self.decided_board, self.decided_board_roll_values)
        self.ui_board.print_hex_reference()
        self.ui_board.print_vertex_reference()
        self.ui_board.print_board_edge_reference()
        
        self.phase += 1
    
    def run_die_roll(self):
        if self.die_turn_count not in self.die_rolls:
            self.die_rolls[self.die_turn_count] = {c.their_uid: [None, None] for c in self.client_connections} # [commitment, roll]
        die = dice.Dice()
        commit = die.generate_commitment()
        self.die_rolls[self.die_turn_count][self.uid] = [commit, None]
        self.broadcast_message({'die_commit': commit, 'die_turn': self.die_turn_count})
        while not all([a[0] for a in self.die_rolls[self.die_turn_count].values()]):
            time.sleep(2) # Wait to collect everyone's commitment
        rollnum = die.committed_roll()
        self.broadcast_message({'die_roll': rollnum, 'die_turn': self.die_turn_count})
        self.die_rolls[self.die_turn_count][self.uid][1] = rollnum
        while not all([a[1] for a in self.die_rolls[self.die_turn_count].values()]):
            time.sleep(2) # Wait to collect everyone's roll
        # Verify everyone's commitment matched their rolls.  If not, someone's lying.
        for roll in self.die_rolls[self.die_turn_count].values():
            assert die.verify_commitment(roll[0], roll[1])
        # Calculate and return the die roll, agreed upon
        final_roll = die.calculate_distributed_roll(self.die_turn_count, [r[1] for r in self.die_rolls[self.die_turn_count].values()])
        assert final_roll >= 1 and final_roll <= 6
        self.die_turn_count += 1
        return final_roll

    def turn_order_run(self):
        """Detemine the turn order of the players by rolling the distributed dice.
           We roll the dice once for each player in UID order..."""
        print "Determining turn order!"
        die_order = sorted([c.their_uid for c in self.client_connections] + [self.uid])
        die_results = {}
        max_roll = -1
        max_roller = None
        while True:
            die_results = {}
            for current_uid in die_order:
                roll = self.run_die_roll() + self.run_die_roll() # Collect 2 die results per UID
                die_results[current_uid] = roll
            # Determine the winner - largest die roller.
            for uid, roll in die_results.iteritems():
                if roll > max_roll:
                    max_roll = roll
                    max_roller = uid
            # OK, but does this roll appear more than once?
            if die_results.values().count(max_roll) > 1:
                print "Highest roller was a tie, trying rolls again"
                continue
            break
        print "Turn order determined!"
        self.turn_order_first = max_roller
        print "Player", ui.uid_to_friendly(max_roller, self.all_uids), "goes first."
        self.phase += 1
    
    def house_place(self, initial_case=False):
        while True:
            hin = raw_input("Please tell me a vertex to place a house or ! for vertex reference: ")
            if hin == "!":
                self.ui_board.print_vertex_reference()
                continue
            if self.ui_board.can_build_house(hin, ui.uid_to_friendly(self.uid, self.all_uids), initial_case):
                print "OK!  Attempting to build a house there..."
                return hin
            print "Can't seem to build a house there... are you sure it's open and not too close to others?"
        
    def road_place(self):
        while True:
            hin = raw_input("Please tell me an edge to place a road or ! for edge reference: ")
            if hin == "!":
                self.ui_board.print_board_edge_reference()
                continue
            if self.ui_board.can_build_road(hin, ui.uid_to_friendly(self.uid, self.all_uids)):
                print "OK!  Attempting to build a road there..."
                return hin
            print "Can't seem to build a road there... are you sure it's open, attached to other roads/houses?"
    
    def initial_placement_run(self):
        """Allow players to place original two houses and two roads"""
        # Order:  start with self.turn_order_first, proceed to everyone in UID
        # order.  Then start with the last person, going back to self.t_o_f...
        self.placement_order = [self.turn_order_first] # add the first person
        for u in sorted(self.all_uids): # add everyone after the first person
            if u > self.turn_order_first:
                self.placement_order.append(u)
        for u in sorted(self.all_uids): # add everyone before the first person
            if u < self.turn_order_first:
                self.placement_order.append(u)
        for u in sorted(self.all_uids)[::-1]: # add everyone before the first person, reverse order
            if u < self.turn_order_first:
                self.placement_order.append(u)
        for u in sorted(self.all_uids)[::-1]: # add everyone after the first person, reverse order
            if u > self.turn_order_first:
                self.placement_order.append(u)
        self.placement_order.append(self.turn_order_first)
        
        print "Starting game initial placement..."
        time.sleep(5)
        
        self.initialization_round = 0
        for i in range(len(self.placement_order)):
            self.initialization_round = i
            players_turn = self.placement_order[self.initialization_round]
            if players_turn == self.uid:
                # Our turn!
                h = self.house_place(True)
                self.ui_board.set_vertex(h, ui.uid_to_friendly(self.uid, self.all_uids)) # set up the vertex for road checking
                r = self.road_place()
                self.broadcast_message({"initialization_round": self.initialization_round, "house_place": h, "road_place": r})
                self.init_rounds[self.initialization_round] = (self.uid, h, r)
            else:
                print "Waiting for another player to go!"
            while self.initialization_round not in self.init_rounds:
                time.sleep(1)
            # Verify the player's placements
            rnd = self.init_rounds[self.initialization_round]
            assert rnd[0] == players_turn # It was actually that player's turn
            if rnd[0] != self.uid:
                assert self.ui_board.can_build_house(rnd[1], ui.uid_to_friendly(rnd[0], self.all_uids), True)
                self.ui_board.set_vertex(rnd[1], ui.uid_to_friendly(rnd[0], self.all_uids))
                print "setting vertex ", rnd[1], "to player"
            self.ui_board.print_actual_board()
            assert self.ui_board.can_build_road(rnd[2], ui.uid_to_friendly(rnd[0], self.all_uids))
            # Looks all good - we didn't crash the game for a cheater.  Update our board and proceed.
            self.ui_board.set_edge(rnd[2], ui.uid_to_friendly(rnd[0], self.all_uids))
            print "The new board:"
            self.ui_board.print_actual_board()
        self.phase += 1
        