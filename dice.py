import random

class Dice(object):
    def __init__(self):
        self.randomBits=32
        self.randomNumber = random.getrandbits(self.randomBits)
        self.randomHash = SHA256.new()
        self.randomHash.update(randomNumber)
        
    def firstRound():
        return self.randomHash

    def secondRound():
        return self.randomNumber

    def thirdRound(turnCount, playersRolls):
        playersRolls.append(randomNumber)
        playersRolls.sort()

        turnConcatString = str(turnCount)
        for i in xrange(playersRolls):
            turnConcat = turnConcat + str(playersRolls[i])

        turnConcatInt = int(turnConcatString)

        turnConcatIntHash = SHA256.new()
        turnConcatIntHash.update(turnConcatInt)

        return turnConcatIntHash % 6
        
