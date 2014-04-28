import random
from Crypto.Hash import SHA256

class Dice(object):
    def __init__(self):
        self.randomBits=64
        self.randomNumber = random.getrandbits(self.randomBits)
        self.randomHash = SHA256.new()
        self.randomHash.update(str(self.randomNumber))
        
    def generate_commitment(self):
        return self.randomHash.hexdigest()

    def committed_roll(self):
        return self.randomNumber

    def calculate_distributed_roll(self, turnCount, playerRolls):
        # Add our roll to the list of shared rolls, append them
        # all with the current turn number, sort them (for deterministic hash)
        # and hash the resulting string.  
        rolls = list(playerRolls)
        rolls.sort()
        turnConcatString = str(turnCount)
        for roll in rolls:
            turnConcatString += str(roll)
        turnConcatHash = SHA256.new()
        turnConcatHash.update(turnConcatString)
        # interpret the hash as an integer, mod 6
        return int(int(turnConcatHash.hexdigest(), base=16) % 6) + 1
    
    def verify_commitment(self, commitment, roll):
        # Verify a particular commitment - returns True if verified
        hasher = SHA256.new()
        hasher.update(str(roll))
        return hasher.hexdigest() == commitment
