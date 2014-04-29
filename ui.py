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
        self.pieces = pieces
        self.tokens = tokens
        self.robber_pos = self.pieces.index(0)
        
        # for printing ONLY - strings
        self.vertex = ['.'] * 54
        self.edges = ['-'] * 72
        self.pieces_n = [0] + (['12'] * 19)
        self.pieces_t = [0] + (['HLLS'] * 19)
    
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
