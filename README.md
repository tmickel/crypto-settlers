crypto-settlers
===============

A cryptographically-implemented distributed Settlers of Catan game.  6.857 project/tech demo.  Focus is on implementing cryptographic gameplay.

To run:  start a player as:
python play.py [hostname:port]

The hostname and port will be used to start a local server.  All players must run an accessible server.  An RSA public/private keypair is generated every game for every player to sign messages.  Give a list of other users' hostname:port pairs to play - all players for a particular game should use the same set of players' servers.  All the players connect to each other and a game is played using cryptographic dice rolls, card shuffles, and other neat things.

Have fun!
