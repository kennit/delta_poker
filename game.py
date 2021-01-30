from enum import Enum
from pydantic import BaseModel
from typing import Dict
from typing import List
from typing import Optional


class User(BaseModel):
    name: str


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
        self.issues_list = []
        self.users = []
        self.voting_system = voting_system
        self.current_issue_index = 0

    def set_voting_system(self, voting_system: str):
        self.voting_system = VotingSystem[voting_system].value

    def add_issue(self, title: str, description: Optional[str] = None):
        self.issues_list.append(Issue(title=title, description=description))

    def add_user(self, username: str):
        user = UserAuth(name=username, is_dealer=len(self.users) == 0)
        self.users.append(user)

    def show_users(self):
        return self.users

    def vote_issue(self, user_vote: UserVote):
        self.issues_list[self.current_issue_index].votes.append(user_vote)

    def get_number_of_votes(self):
        return len(self.issues_list[self.current_issue_index].votes)

    def left_to_vote(self):
        crt_issue = self.issues_list[self.current_issue_index]
        crt_votes = [x.name for x in crt_issue.votes]
        return [user.name for user in self.users if user.name not in crt_votes]

    def set_previous_issue(self):
        if self.current_issue_index > 0:
            self.current_issue_index -= 1
        return self.current_issue_index

    def set_next_issue(self):
        if self.current_issue_index < len(self.issues_list):
            self.current_issue_index += 1
        return self.current_issue_index

    def get_current_issue(self):
        return self.issues_list[self.current_issue_index]
