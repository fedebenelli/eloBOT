# eloBOT
A bot that handles an ELO ranking system between players of a gaming Discord server. Info on how ELO works can be found here https://blog.mackie.io/the-elo-algorithm

This is still a WIP. For the moment the bot is designed to use repl.it as a host server and uptime robot to keep it online (that's the only use of keep_alive and requirements.txt).

In the config.json file 3 parameters must be defined:
-botToken: Discord bot's token obtained from discordapp.com
-gistToken: Token to edit gists, can be created from account settings at github.com
-filesToken: The gist's share code

The stats of players are saved as a json file in a gist, but here is an example of how they're stored:
```json
{
  "stats": {
    "players": [
      {
        "id": "Discord ID",
        "playerName": "Discord Name",
        "games": [
          {
            "gameName": "Battlezone 98 Redux",
            "gameAcro": "bzr",
            "rank": "500",
            "W": "0",
            "T": "0",
            "TM": "0"
          },
          {
            "gameName": "Battlezone: Combat Commander",
            "gameAcro": "bzcc",
            "rank": "500",
            "W": "0",
            "T": "0",
            "TM": "0"
          }
        ]
      }
    ]
  }
}
```

A way to the Discord's server staff to add new games to the list is still in process
