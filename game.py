import collections
import json
import os
import time

from enum import Enum
from pydantic import BaseModel
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

RESULTS_PATH = './results'


class User(BaseModel):
    name: str
    old_name: Optional[Union[str, None]]


class UserAuth(User):
    is_dealer: bool


class UserVote(User):
    vote_value: str


class Issue(BaseModel):
    title: str
    description: Optional[str] = None
    votes: Optional[List[Dict]] = []


class VotingSystem(Enum):
    fibonacci = ["0", "1", "2", "3", "5", "8",
                 "13", "21", "34", "55", "89", "?", "coffee"]
    modified_fibonacci = ["0", "1/2", "1", "2", "3",
                          "5", "8", "20", "40", "100", "?", "coffee"]
    t_shirt_sizes = ["xxs", "xs", "s", "m", "l", "xl", "xxl", "?", "coffee"]
    powers_of_two = ["0", "1", "2", "4", "8", "16", "32", "64", "?", "coffee"]


class Game:

    def __init__(self, voting_system: List):
        self.voting_system = voting_system
        self.issues_list = []
        self.users = {}
        self.dealer = None
        self.current_issue_index = 0

    @property
    def get_dealer(self):
        return self.dealer

    @property
    def get_current_issue(self):
        return self.issues_list[self.current_issue_index]

    def add_issue(self, title: str, description: Optional[str] = None):
        self.issues_list.append(Issue(title=title, description=description))

    def add_user(self, username: str):
        user = UserAuth(name=username, is_dealer=self.get_dealer is None)
        self.users[username] = user
        if self.get_dealer is None:
            self.dealer = username

    def aggregate_votes(self) -> Dict:
        results_dict = collections.defaultdict(lambda: [])
        crt_issue_votes = self.get_current_issue.votes
        for vote in crt_issue_votes:
            results_dict[vote.vote_value].append(vote.name)
        return results_dict

    def count_votes(self, vote_value_sort=True) -> Dict:
        vote_results = {}
        for vote, voters in self.aggregate_votes().items():
            vote_results[vote] = {
                'vote_count': len(voters),
                'voters': voters
            }
        if vote_value_sort:
            return {k: v for k, v in sorted(vote_results.items(),
                                            key=lambda x: x[0])}
        else:
            return {k: v for k, v in sorted(vote_results.items(),
                                            key=lambda x: x[1]['vote_count'])}

    def dump_results(self):
        filename = os.path.join(RESULTS_PATH, str(time.time()))
        with open(filename, 'w') as f:
            json.dump(self.count_votes(), f)

    def exit_game(self, user: User) -> str:
        if user.name in self.users:
            del self.users[user.name]
        else:
            return f"Couldn't find user {user.name}"
        if self.dealer and self.get_dealer == user.name:
            self.dealer = None
            return f"Deleted dealer {user.name}"
        return f"Deleted user {user.name}"

    def get_current_initial_issue(self) -> Issue:
        crt_issue = self.get_current_issue.dict(exclude_unset=True)
        return crt_issue

    def get_number_of_votes(self) -> int:
        return len(self.issues_list[self.current_issue_index].votes)

    def left_to_vote(self) -> List:
        crt_issue = self.issues_list[self.current_issue_index]
        crt_votes = [x.name for x in crt_issue.votes]
        return [user.name for user in self.users.values()
                if user.name not in crt_votes]

    def new_game(self, user: User) -> bool:
        if self.dealer and user.name == self.dealer:
            self.issues_list = []
            self.users = {}
            self.dealer = None
            self.current_issue_index = 0
            return True
        else:
            return False

    def remove_player(self, user: User, username: str) -> Dict:
        if username == user.name:
            return {'result_message': f"Can't delete own user. Choose another "
                                      f"player to remove"}
        if self.dealer and self.dealer == user.name:
            print(f"{self.dealer} is removing {user.name}")
            if username in self.users:
                del self.users[username]
                return {'result_message': f"Successfully removed {username}"}
            else:
                return {'result_message': f"Couldn't find {username} as a "
                                          f"player"}
        else:
            return {'result_message': f"Only the dealer ({self.get_dealer}) "
                                      f"can remove players. If there is no "
                                      f"dealer, please add one."}

    def reset_votes(self, user: User) -> bool:
        if self.get_dealer and user.name == self.get_dealer:
            crt_issue = self.get_current_initial_issue()
            self.issues_list[self.current_issue_index] = \
                Issue(**crt_issue)
            return True
        else:
            return False

    def set_next_issue(self, user: User) -> int:
        if self.dealer and user.name == self.dealer and \
                self.current_issue_index < len(self.issues_list) - 1:
            self.current_issue_index += 1
        return self.current_issue_index

    def set_previous_issue(self, user: User) -> int:
        if self.dealer and user.name == self.dealer and \
                self.current_issue_index > 0:
            self.current_issue_index -= 1
        return self.current_issue_index

    def set_voting_system(self, voting_system: str):
        self.voting_system = VotingSystem[voting_system].value

    def show_users(self) -> Dict:
        return self.users

    def vote_issue(self, user_vote: UserVote):
        self.issues_list[self.current_issue_index].votes.append(user_vote)
