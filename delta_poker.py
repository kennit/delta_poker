from fastapi import Body
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import status
from game import User
from game import UserVote
from game import Game
from game import VotingSystem
from typing import Dict
from typing import Optional

app = FastAPI()
game = Game(VotingSystem['fibonacci'].value)


# # TODO only the admin can set the voting system
# @app.put("/voting_system")
# def set_voting_system(voting_system: str) -> Dict:
#     game.set_voting_system(voting_system)
#     return {"message": f"Voting system '{game.voting_system}' is selected"}

@app.get("/")
def greet_users():
    return "Welcome to a friendly game of Planning Poker"


@app.get("/voting_system")
def get_voting_system() -> Dict:
    global game
    return {"message": f"Voting system '{game.voting_system}' is selected"}


@app.put("/issue/add")
def add_issue(title: str = Body(...),
              description: Optional[str] = Body(None)) -> Dict:
    global game
    game.add_issue(title=title, description=description)
    return {"message": f"Issue '{title}' was added"}


@app.get("/issue/current")
def current_issue():
    global game
    return game.get_current_issue()


@app.put("/user/add")
def add_user(user: User = Body(...)) -> Dict:
    global game
    game.add_user(user.name)
    return {"message": f"User '{user.name}' was added"}


@app.get("/user/count")
def add_user() -> Dict:
    global game
    return {"user_count": len(game.users)}


@app.get("/user/show_all")
def show_all_users() -> Dict:
    global game
    return {"current_users": game.show_users()}


@app.put("/issue/vote")
def user_vote(user_vote: UserVote = Body(...)):
    global game
    crt_users = [user.name for user in game.users]
    if user_vote.name not in crt_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Please add the user '{user_vote.name}' to the game")

    if user_vote.vote_value not in game.voting_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Please select a vote from the current voting system: "
                   f"{game.voting_system}")

    game.vote_issue(user_vote=user_vote)
    crt_issue = game.get_current_issue()
    return {"message": f"{user_vote.name}'s '{user_vote.vote_value}' "
                       f"was registered on {crt_issue['title']}"}


@app.get("/issue/vote_status")
def get_issue_votes():
    return {"long_status": f"On issue {game.get_current_issue()['title']} "
                           f"Voted: {game.get_number_of_votes()} "
                           f"Left to vote: {game.left_to_vote()} "
                           f"out of {len(game.users)}",
            "left_to_vote": game.left_to_vote(),
            "voted": game.get_number_of_votes()}


@app.get("/issue/show_results")
def show_results() -> Dict:
    global game
    if len(game.left_to_vote()) == 0:
        return {"status": "done",
                "report": game.get_current_issue_results()
                }
    else:
        return {"status": "pending",
                "report": f"Left to vote: {game.left_to_vote()}"}


@app.post("/issue/previous")
def go_to_previous_issue(user: User = Body(...)) -> Dict:
    _ = game.set_previous_issue(user)
    return game.get_current_issue()


@app.post("/issue/next")
def go_to_next_issue(user: User = Body(...)) -> Dict:
    _ = game.set_next_issue(user)
    return game.get_current_issue()
