# delta_poker

A small Python3 application for Agile teams that want to use poker planning
for estimating workload. The app consists of:
- a server for running the game
- a CLI that can be used by Team Members to have a user-friendly interface

# Requirements
1. This step is required for Admin/Scrum Master/Product Owner. For running both
   the server and the CLI, you need to install the libraries from
`requirements.txt`:
```commandline
pip3 install -r requirements.txt
```

2. This step is required for each Team Member that is involved in development
   (and testing)
For running just the CLI, you need to install the libraries from 
`cli_requirements.txt`:
```commandline
pip3 install -r cli_requirements.txt
```

# Steps for playing planning poker:
1. Start server (by Admin/Scrum Master/Product Owner)
2. Add current issues (by Scrum Master/Product Owner)
3. Each player starts the CLI (by each Team Member)

# Start server

For starting the server such that it can be accessed from your network, you
need to run:
```commandline
uvicorn delta_poker:app --host=0.0.0.0
```

Now you can visit in your browser ```http://$host:8000/``` where `host` is the
IP address or the domain name of the server and you should see the following
message:
```"Welcome to a friendly game of Planning Poker"```

# Add current issues

For adding the issues for the current game, you can run from the `examples`
directory (if you are on the same machine as the server):
```commandline
python3 add_issues.py -f issues_list.json
```
where `issues_list.json` is a JSON file that contains issues to be voted on, in
the following format:
```json
[
  {
    "title": "Title of issue",
    "description": "Description of issue"
  }
]
```

If you want to add issues from another machine, you can specify the URL for the
server that hosts the game:
```commandline
python3 add_issues.py -f issues_list.json -u ip_address:ip_port
```
where `ip_address` is the IP address or the domain name of the server.

# Play the game
Each Team Member can start the CLI by running
```commandline
python3 delta_cli.py
```
All the next commands are assumed to be run in the CLI.

Each player can run `help` see which commands are available and documented.

To see the voting system to be used in the game, a user can run
```commandline
show_voting_system
```

The first Team Member to be registered as a player (i.e. run
`add_player username` first) will be "dealer" and can move between issues to be
voted on.

Each player should run
```commandline
add_player my_player_name
```
such that they can be registered in the game.

For displaying the current issue, a player should run
```commandline
current_issue
```

For voting on the current issue, a player should run
```commandline
vote_issue vote_value
```
where `vote_value` should be a value in the list returned by
`show_voting_system`

For showing the number of players in the game, any Team Member can run
```commandline
user_count
```

For showing the current players, any Team Member can run
```commandline
show_current_players
```

For showing the current status of voting, any Team Member can run
```commandline
show_current_votes
```

For showing the final report on the current issue (i.e. after all players
voted), any Team Member can run
```commandline
show_report
```