import logging

from fastapi import Body
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Query
from fastapi import status
from game import User
from game import UserVote
from game import Game
from game import VotingSystem
from typing import Dict
from typing import Optional

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)

app = FastAPI()
game = Game(VotingSystem['fibonacci'].value)


@app.get("/")
def greet_users():
    return "Welcome to a friendly game of Planning Poker"


@app.get("/game/get_dealer")
def dealer_user() -> Dict:
    return {"result_message": {"current_dealer": game.get_dealer}}


@app.post("/game/new")
def start_new_game(user: User = Body(...)) -> Dict:
    new_game_started = game.new_game(user)
    if new_game_started:
        return {"result_message": f"Started new game using voting system "
                                  f"'{game.voting_system}' is selected"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=("Only the dealer can start a new game. If "
                    "there is no dealer, please add one."))


@app.get("/game/voting_system")
def get_voting_system() -> Dict:
    return {
        "result_message": f"Voting system '{game.voting_system}' is selected"}


@app.put("/issue/add")
def add_issue(title: str = Body(...),
              description: Optional[str] = Body(None)) -> Dict:
    game.add_issue(title=title, description=description)
    return {"result_message": f"Issue '{title}' was added"}


@app.get("/issue/current")
def current_issue():
    try:
        crt_issue = game.get_current_issue
        return {"result_message": crt_issue}
    except IndexError as e:
        logger.error(f"Found {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please add issues to the game")


@app.post("/issue/next")
def go_to_next_issue(user: User = Body(...)) -> Dict:
    _ = game.set_next_issue(user)
    return {"result_message": game.get_current_issue}


@app.post("/issue/previous")
def go_to_previous_issue(user: User = Body(...)) -> Dict:
    _ = game.set_previous_issue(user)
    return {"result_message": game.get_current_issue}


@app.get("/issue/show_results")
def show_results() -> Dict:
    if len(game.left_to_vote()) == 0:
        if game.report_queue.qsize() == 0:
            game.report_queue.put("dump_request")
            game.dump_issue_results()
        try:
            vote_distribution = game.count_votes()
            return {"result_message": {
                        "status": "done",
                        "report": vote_distribution
                        }
                    }
        except IndexError as e:
            logger.error(f"Found {e}")
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail="Please add issues to the game"
            )
    else:
        return {"result_message": {
                    "status": "pending",
                    "report": f"Left to vote: {game.left_to_vote()}"
                    }
                }


@app.get("/issue/vote_status")
def get_issue_votes():
    try:
        left_to_vote_count = game.left_to_vote()
    except IndexError as e:
        logger.error(f"Found {e}")
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Please add issues to the game"
        )
    if len(left_to_vote_count) == 0:
        if len(game.users) == 0:
            return {"result_message": ("Players need to be registered in ",
                                       "order to vote")}
        return {"result_message": ("Every registered player has voted. ",
                                   "You can type show_report to see votes")}
    if len(left_to_vote_count) > 1:
        verb = "have"
    elif len(left_to_vote_count) == 1:
        verb = "has"
    return {"result_message": f"{left_to_vote_count} still {verb} to vote"}


@app.put("/issue/vote")
def add_user_vote(user_vote: UserVote = Body(...)):
    crt_users = [user.name for user in game.users.values()]
    if user_vote.name not in crt_users:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=f"Please add the user '{user_vote.name}' to the game")

    if user_vote.vote_value not in game.voting_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Please select a vote from the current voting system: "
                   f"{game.voting_system}")

    vote_status = game.vote_issue(user_vote=user_vote)
    crt_issue = game.get_current_issue
    if vote_status:
        return {"result_message": f"{user_vote.name}'s "
                                  f"'{user_vote.vote_value}' "
                                  f"was registered on "
                                  f"{crt_issue.dict()['title']}"}
    else:
        return {"result_message": f"{user_vote.name} already voted on "
                                  f"{crt_issue.dict()['title']}"}


@app.post("/issue/votes_reset")
def reset_votes(user: User = Body(...)):
    votes_reset = game.reset_votes(user)
    if votes_reset:
        return {"result_message": f"Reset votes on issue "
                                  f"{game.get_current_issue}"}
    else:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=("Only the dealer can reset votes. ",
                    "If there is no dealer, please add one."))


@app.post("/user/add")
def add_user(user: User = Body(...)) -> Dict:
    game.add_user(user.name)
    return {"result_message": f"User '{user.name}' was added"}


@app.get("/user/count")
def count_users() -> Dict:
    return {"result_message": {"user_count": len(game.users)}}


@app.post("/user/exit")
def user_exit(user: User = Body(...)) -> Dict:
    user_exit_status = game.exit_game(user)
    return {"result_message": {"user_exit_status": user_exit_status}}


@app.post("/user/remove")
def remove_user(user: User = Body(...), username: str = Query(...)) -> Dict:
    result_dict = game.remove_player(user, username)
    return result_dict


@app.get("/user/show_all")
def show_all_users() -> Dict:
    return {"result_message": {
        "current_users": [x.name for x in game.show_users().values()]
    }}
