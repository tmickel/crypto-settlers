import string

def uid_to_friendly(uid, all_uids):
    """Converts a UID to player N"""
    position = sorted(all_uids).index(uid)
    return position + 1

def board_piece_to_friendly(num):
    """Maps unique numbers 0->18 to different kinds of board piece:
       -1 desert
       -4 fields (grain)
       -4 forests (lumber)
       -4 pastures (wool)
       -3 mountains (ore)
       -3 hills (brick)"""    
    if num == 0: return "DSRT"
    if num > 0 and num <= 4: return "FIEL"
    if num >= 5 and num <= 8: return "FRST"
    if num >= 9 and num <= 12: return "PSTR"
    if num >= 13 and num <= 15: return "MNTS"
    if num >= 16 and num <= 18: return "HLLS"

def board_token_to_friendly(num):
    """Maps unique numbers 0->17 to value at which dice roll will gain
       the resource on that token:
       -The desert always has no token
       -1 #2
       -2 #3
       -2 #4
       -2 #5
       -2 #6
       -No #7 (this is the robber)
       -2 #8
       -2 #9
       -2 #10
       -2 #11
       -1 #12"""
    if num == 0: return 2
    if num == 1 or num == 2: return 3
    if num == 3 or num == 4: return 4
    if num == 5 or num == 6: return 5
    if num == 7 or num == 8: return 6
    if num == 9 or num == 10: return 8
    if num == 11 or num == 12: return 9
    if num == 13 or num == 14: return 10
    if num == 15 or num == 16: return 11
    if num == 17: return 12

class UIBoard(object):
    def __init__(self, pieces, tokens):
        """Pieces is a shuffled list, 0-18.  Tokens is a shuffled list matched
           to the pieces, 0-17 (desert has no token to start, can have robber)."""
        # for printing ONLY - strings
        self.vertex = ['.'] * 54
        self.edges = ['-'] * 72
        self.pieces = pieces
        self.tokens = tokens

        self.pieces_n = [0] + (['12'] * 19) # Dummy - this is overriden by format methods
        self.pieces_t = [0] + (['HLLS'] * 19)
        
        # actual game state
        self.robber_pos = self.pieces.index(0)
        self.game_vertex = ['.'] * 54
        self.game_edges = ['-'] * 72
    

    # Vertex-edge adjacencies: used to check if house building is valid
    vertex_edge_adjacencies = [
        'a': ['a', 'b'],
        'b': ['a', 'c'],
        'c': ['d', 'f'],
        'd': ['d', 'b', 'g'],
        'e': ['h', 'e'],
        'f': ['e', '19'],
        'g': ['l', 'i'],
        'h': ['i', 'f', 'm'],
        'i': ['g', 'j', 'n'],
        'j': ['j', 'h', 'o'],
        'k': ['19', 'k', 'p'],
        'l': ['k', 'q'],
        'm': ['l', 't'],
        'n': ['m', 'u', 'r'],
        'o': ['r', 'n', 'v'],
        'p': ['o', 's', 'w'],
        'q': ['s', 'p', 'x'],
        'r': ['q', 'y'],
        's': ['t', 'C', 'z'],
        't': ['z', 'u', 'D'],
        'u': ['v', 'E', 'A'],
        'v': ['w', 'A', 'F'],
        'w': ['x', 'B', 'G'],
        'x': ['y', 'B', 'H'],
        'y': ['K', 'C'],
        'z': ['D', 'I', 'L'],
        'A': ['I', 'M', 'E'],
        'B': ['F', 'J', 'N'],
        'C': ['J', 'G', 'O'],
        'D': ['H', 'P'],
        'E': ['K', 'T'],
        'F': ['Q', 'L', 'U'],
        'G': ['M', 'R', 'V'],
        'H': ['R', 'N', 'W'],
        'I': ['O', 'S', 'X'],
        'J': ['P', 'Y', 'S'],
        'K': ['T', '1'],
        'L': ['U', 'Z', '2'],
        'M': ['Z', '3', 'V'],
        'N': ['W', '0', '4'],
        'O': ['0', 'X', '5'],
        'P': ['Y', '6'],
        'Q': ['1', '7'],
        'R': ['7', '10', '2'],
        'S': ['11', '3', '8'],
        'T': ['8', '4', '12'],
        'U': ['13', '9', '5'],
        'V': ['9', '6'],
        'W': ['10', '14'],
        'X': ['14', '16', '11'],
        'Y': ['15', '17', '12'],
        'Z': ['15', '13'],
        '0': ['16', '18'],
        '1': ['18', '17']
    ]
    
    # Hex-vertex adjacencies: used to determine who to award resources to
    hex_vertex_adjacencies = [
        '0': ['a', 'b', 'd', 'e', 'i', 'j'],
        '1': ['c', 'd', 'i', 'h', 'n', 'o'],
        '2': ['e', 'f', 'k', 'p', 'q', 'j'],
        '3': ['g', 'h', 'n', 'm', 's', 't'],
        '4': ['n', 'o', 'u', 't', 'z', 'A'],
        '5': ['i', 'j', 'p', 'o', 'u', 'v'],
        '6': ['p', 'q', 'v', 'w', 'B', 'C'],
        '7': ['k', 'l', 'r', 'q', 'w', 'x'],
        '8': ['y', 's', 't', 'z', 'E', 'F'],
        '9': ['F', 'z', 'A', 'G', 'M', 'L'],
        '10': ['G', 'H', 'A', 'B', 'u', 'v'],
        '11': ['H', 'N', 'O', 'I', 'B', 'C'],
        '12': ['w', 'x', 'D', 'C', 'I', 'J'],
        '13': ['K', 'E', 'F', 'L', 'Q', 'R'],
        '14': ['G', 'H', 'N', 'M', 'S', 'T'],
        '15': ['O', 'I', 'J', 'P', 'U', 'V'],
        '16': ['L', 'R', 'W', 'X', 'S', 'M'],
        '17': ['N', 'O', 'T', 'U', 'Y', 'Z'],
        '18': ['S', 'T', 'X', 'Y', '0', '1']
    ]
    
    def print_board_edge_reference(self):
        print "SHOWING EDGE REFERENCE:"
        self.format_board(['.'] * 54, list(string.ascii_lowercase) + list(string.ascii_uppercase) + range(20),
        self.pieces, self.tokens)
        self.print_board()
    
    def print_vertex_reference(self):
        print "SHOWING VERTEX REFERENCE:"
        self.format_board(list(string.ascii_lowercase) + list(string.ascii_uppercase) + range(2), ['-'] * 72,
        self.pieces, self.tokens)
        self.print_board()
    
    def print_hex_reference(self):
        print "SHOWING HEXAGON REFERENCE:"
        self.format_board(['.'] * 54, ['-'] * 72, self.pieces, self.tokens)
        self.pieces_t = ['    '] * 19
        self.pieces_n = [str(n).rjust(2) for n in range(19)]
        self.print_board()
    
    def print_actual_board(self):
        self.format_board(self.game_vertex, self.game_edges, self.pieces, self.tokens)
        
    def vertex_friendly_to_id(self, f):
        """Convert a user/friendly-represented vertex to one we can use easily internally"""
        friendly_vertices = list(string.ascii_lowercase) + list(string.ascii_uppercase) + range(2)
        return friendly_vertices.index(f)
    
    def edge_friendly_to_id(self, f):
        """Convert a user/friendly-represented edge to one we can use easily internally"""
        friendly_edges = list(string.ascii_lowercase) + list(string.ascii_uppercase) + range(20)
        return friendly_edges.index(f)
    
    # Useful public methods - for player IO
    def set_vertex(self, f, player):
        """Place player number on vertex (build a house)"""
        self.game_vertex[self.vertex_friendly_to_id(f)] = player
    
    def set_edge(self, f, player):
        """Place player number on edge (build a road)"""
        self.game_edge[self.edge_friendly_to_id(f)] = player
    
    def get_vertex(self, f):
        """Return who is on vertex f"""
        return self.game_vertex[self.vertex_friendly_to_id(f)]
    
    def get_edge(self, f):
        """Returns who is on edge f"""
        return self.game_edge[self.edge_friendly_to_id(f)]
    
    def edge_adjacent_vertices(self, f):
        """Given vertex f, return list of adjacent vertices"""
        vertices = []
        for vertex, edges in self.vertex_edge_adjacencies:
            if f in edges:
                vertices.append(vertex)
        return vertices
        
    # Edge-to-edge adjacencies - an edge is adjacent to an edge if it's adjacent
    # to a vertex which is adjacent to that edge (for road building)

    def edge_adjacent_edges(self, f):
        e_a_v = self.edge_adjacent_vertices(f)
        e_a_e = []
        for v in e_a_v:
            e_a_e.extend(self.vertex_edge_adjacencies[v])
        return e_a_e
    
    def can_build_road(self, f, player):
        """Returns whether player can build road on edge f"""
        edge_index = self.edge_friendly_to_id(f)
        if self.game_edge[edge_index] != '-':
            return False # already occupied
        adjacent_vertices = self.edge_adjacent_vertices(f)
        # adjacent vertices either have nothing or player
        has_adjacent_settlement = False
        for a_v in adjacent_vertices:
            if a_v != '.':
                if a_v != player:
                    return False
                else:
                    has_adjacent_settlement = True
        # must be adjacent to another road
        adjacent_edges = self.edge_adjacent_edges(f)
        has_adjacent_road = False
        for a_e in adjacent_edges:
            if self.get_edge(a_e) == player:
                has_adjacent_road = True
        return has_adjacent_road or has_adjacent_settlement:
    
    def can_build_house(self, f, player):
        """Returns whether player can build house on vertex f"""
        vertex_index = self.vertex_friendly_to_id(f)
        if self.game_vertex[vertex_index] != '.':
            return False # already occupied
        adjacent_edges = self.vertex_edge_adjacencies[f]
        for a in adjacent_edges:
            if self.get_edge(a) == player:
                # We own this edge.  Anyone on the other end of it?
                e_a_v = self.edge_adjacent_vertices(a)
                for v in e_a_v:
                    if self.get_vertex(f) != '.':
                        return False # Too close to another settlement
                # We have an adjacent edge and the attached vertex is empty - can build
                return True
        return False
    
    def resources_owed(self, n):
        """What resources are owed on a particular dice roll?"""
    
    
    
    # Format/print methods
    def format_board(self, vertices, edges, pieces, tokens):
        self.vertex = vertices
        self.edges = edges
        self.pieces_n = [str(board_token_to_friendly(t)).rjust(2) for t in tokens]
        if self.robber_pos == self.pieces.index(0):
            # Robber on the desert, insert it!
            self.pieces_n.insert(self.robber_pos, "RB") # Insert robber token at proper location for the desert
        else:
            # Robber on some other position, replace it
            self.pieces_n[self.robber_pos] = "RB"
        self.pieces_t = [board_piece_to_friendly(p) for p in pieces]

    def print_board(self):
        # Call with format_board first....
        # original ASCII art credit:
        # http://boardgamestogo.com/settlers_pbem.htm
        board = """
                                  >-----<
                                 /~~~~~~~\\
                                /~~~~~~~~~\\
                         >-----<~~~~~~~~~~~>-----<
                        /~~~~~~~\\~~~~~~~~~/~~~~~~~\\
                       /~~~~~~~~~\\*~~~~~*/~~~~~~~~~\\
                >-----<~~~~~~~~~~~%s--%s--%s~~~~~~~~~~~>-----<
               /~~~~~~~\\~~~~~~~~~/       \\~~~~~~~~~/~~~~~~~\\
              /~~~~~~~~~\\~~~~~~~%s    %s    %s~~~~~~~/~~~~~~~~~\\
       >-----<~~~~~~~~~~*%s--%s--%s   %s    %s--%s--%s*~~~~~~~~~~>-----<
      /~~~~~~~\\~~~~~~~~~/       \\         /       \\~~~~~~~~~/~~~~~~~\\
     /~~~~~~~~~\\~~~~~~*%s   %s     %s     %s    %s    %s*~~~~~~/~~~~~~~~~\\
    <~~~~~~~~~~~%s--%s--%s   %s    %s--%s--%s   %s     %s--%s--%s~~~~~~~~~~~>
     \\~~~~~~~~~/       \\         /       \\         /       \\~~~~~~~~~/
      \\~~~~~~~%s    %s    %s      %s    %s    %s     %s    %s    %s~~~~~~~/
       >-----%s   %s    %s--%s--%s   %s    %s--%s--%s    %s   %s-----<
      /~~~~~~~%s         %s       %s         %s       %s         %s~~~~~~~\\
     /~~~~~~~~~\\       /    %s    \\       /    %s    \\       /~~~~~~~~~\\
    <~~~~~~~~~~*%s--%s--%s    %s    %s--%s--%s    %s     %s--%s--%s*~~~~~~~~~~>
     \\~~~~~~~~~%s        %s          %s       %s         %s       %s~~~~~~~~~/
      \\~~~~~~*/   %s     \\       /    %s    \\       /   %s    \\*~~~~~~/
       >-----%s   %s    %s--%s--%s    %s    %s--%s--%s     %s   %s-----<
      /~~~~~~~%s         %s       %s          %s       %s         %s~~~~~~~\\
     /~~~~~~~~~\\       /   %s    \\       /    %s    \\       /~~~~~~~~~\\
    <~~~~~~~~~~~%s--%s--%s    %s   %s--%s--%s    %s   %s--%s--%s~~~~~~~~~~~>
     \\~~~~~~~~~%s       %s         %s       %s          %s        %s~~~~~~~~~/
      \\~~~~~~~/    %s   \\       /     %s   \\       /    %s    \\~~~~~~~/
       >-----%s   %s   %s--%s--%s     %s   %s--%s--%s     %s    %s----<
      /~~~~~~*%s         %s       %s         %s        %s          %s*~~~~~~\\
     /~~~~~~~~~\\       /   %s    \\       /    %s    \\       /~~~~~~~~~\\
    <~~~~~~~~~~*%s--%s--%s   %s     %s--%s--%s   %s    %s--%s--%s*~~~~~~~~~>
     \\~~~~~~~~~/~~~~~~~%s         %s      %s         %s~~~~~~~\\~~~~~~~~~/
      \\~~~~~~~/~~~~~~~~~\\        /    %s   \\        /~~~~~~~~~\\~~~~~~~/
       >-----< ~~~~~~~~~~%s--%s--%s    %s   %s--%s--%s~~~~~~~~~~~>-----<
              \\~~~~~~~~~/*~~~~~*%s         %s*~~~~~*\\~~~~~~~~~/
               \\~~~~~~~/~~~~~~~~~\\        /~~~~~~~~~\\~~~~~~~/
                >-----<~~~~~~~~~~~%s--%s--%s~~~~~~~~~~~>-----<
                       \\~~~~~~~~~/~~~~~~~\\~~~~~~~~~/
                        \\~~~~~~~/~~~~~~~~~\\~~~~~~~/
                         >-----<~~~~~~~~~~~>-----<
                                \\~~~~~~~~~/
                                 \\~~~~~~~/
                                  >-----<

        """ 
        
        n=(self.vertex[0], self.edges[0], self.vertex[1],
        self.edges[1], self.pieces_n[0], self.edges[2],    
        self.vertex[2], self.edges[3], self.vertex[3], self.pieces_t[0], self.vertex[4], self.edges[4], self.vertex[5], 
        self.edges[5], self.pieces_n[1], self.edges[6], self.edges[7], self.pieces_n[2], self.edges[71],
        self.vertex[6], self.edges[8], self.vertex[7], self.pieces_t[1], self.vertex[8], self.edges[9], self.vertex[9], self.pieces_t[2],self.vertex[10], self.edges[10], self.vertex[11],  
        self.edges[11], self.pieces_n[3], self.edges[12], self.edges[13], self.pieces_n[5], self.edges[14], self.edges[15], self.pieces_n[7], self.edges[16],
        self.vertex[12], self.pieces_t[3], self.vertex[13], self.edges[17], self.vertex[14], self.pieces_t[5], self.vertex[15], self.edges[18], self.vertex[16], self.pieces_t[7], self.vertex[17],
        self.edges[19], self.edges[20], self.edges[21], self.edges[22], self.edges[23], self.edges[24],
        self.pieces_n[4], self.pieces_n[6],
        self.vertex[18], self.edges[25], self.vertex[19], self.pieces_t[4], self.vertex[20], self.edges[26], self.vertex[21], self.pieces_t[6], self.vertex[22], self.edges[27], self.vertex[23],
        self.edges[28], self.edges[29], self.edges[30], self.edges[31], self.edges[32], self.edges[33],
        self.pieces_n[8], self.pieces_n[10], self.pieces_n[12],
        self.vertex[24], self.pieces_t[8], self.vertex[25], self.edges[34], self.vertex[26], self.pieces_t[10], self.vertex[27], self.edges[35], self.vertex[28], self.pieces_t[12], self.vertex[29],
        self.edges[36], self.edges[37], self.edges[38], self.edges[39], self.edges[40], self.edges[41],
        self.pieces_n[9], self.pieces_n[11],
        self.vertex[30], self.edges[42], self.vertex[31], self.pieces_t[9], self.vertex[32], self.edges[43], self.vertex[33], self.pieces_t[11], self.vertex[34], self.edges[44], self.vertex[35],
        self.edges[45], self.edges[46], self.edges[47], self.edges[48], self.edges[49], self.edges[50],
        self.pieces_n[13], self.pieces_n[14], self.pieces_n[15],
        self.vertex[36], self.pieces_t[13], self.vertex[37], self.edges[51], self.vertex[38], self.pieces_t[14], self.vertex[39], self.edges[52], self.vertex[40], self.pieces_t[15], self.vertex[41],
        self.edges[53], self.edges[54], self.edges[55], self.edges[56], self.edges[57], self.edges[58],
        self.pieces_n[16], self.pieces_n[17],
        self.vertex[42], self.edges[59], self.vertex[43], self.pieces_t[16], self.vertex[44], self.edges[60], self.vertex[45], self.pieces_t[17], self.vertex[46], self.edges[61], self.vertex[47],
        self.edges[62], self.edges[63], self.edges[64], self.edges[65],
        self.pieces_n[18],
        self.vertex[48], self.edges[66], self.vertex[49], self.pieces_t[18], self.vertex[50], self.edges[67], self.vertex[51],
        self.edges[68], self.edges[69],
        self.vertex[52], self.edges[70], self.vertex[53])
        
        print board % n
