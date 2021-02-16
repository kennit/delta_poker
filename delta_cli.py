import argparse
import json
import requests

from cmd import Cmd
from fastapi import status


class MyPrompt(Cmd):
    prompt = 'planning_poker> '
    intro = "Welcome! Type ? to list commands"

    def __init__(self, url=None):
        super().__init__()
        self.username = None
        if url:
            self.url = url
        else:
            self.url = 'http://localhost:8000'

    def default(self, inp):
        """
        You can also use x or q to exit the game. All commands that are
        not implemented will just be printed with a notification
        message.
        """
        if inp == 'x' or inp == 'q':
            return self.do_exit()

        print(f"Haven't found this command: {inp}")

    @staticmethod
    def print_error_response(response):
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            print(f"{json.loads(response.text)['detail']}")
        elif response.status_code == status.HTTP_412_PRECONDITION_FAILED:
            print(f"{json.loads(response.text)['detail']}")
        elif response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            message = json.loads(response.text)['detail'][0]['msg']
            print(f"{message}")
        else:
            print(f"{response.text}")

    @staticmethod
    def print_issue(response):
        crt_issue_title = response['result_message']['title']
        crt_issue_description = response['result_message']['description']
        print(f"'{crt_issue_title}' is the current issue.")
        if len(crt_issue_description) > 0:
            print(f"{crt_issue_description}")

    @staticmethod
    def parse_report(report):
        for vote_value, vote_details in report.items():
            print(f"{vote_details['vote_count']} voted for {vote_value}.\n"
                  f"{json.dumps(vote_details['voters'], indent=4)}\n")

    def send_request(self, method, route, params=None, data=None):
        full_uri = ''.join([self.url, route])
        response = requests.request(method=method, url=full_uri,
                                    params=params, json=data)
        return response

    def do_add_player(self, username):
        """
        Add a player to the current game
        """
        current_players = []

        response = self.send_request(method='get',
                                     route='/user/show_all')

        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            current_players = response_dict['result_message']['current_users']
        else:
            self.print_error_response(response)

        if self.username and self.username in current_players:
            print(f"You already have a username in the current game: "
                  f"{self.username}")
        elif len(username) < 4:
            print(f"Please use a more meaningful name")
        else:
            crt_dict = {
                'name': username
            }
            response = self.send_request(method='post',
                                         route='/user/add',
                                         data=crt_dict)
            if response.status_code == status.HTTP_200_OK:
                self.username = username
                print(f"Player {self.username} has been added to the current "
                      f"game")
            else:
                self.print_error_response(response)

    def do_current_dealer(self, inp):
        """
        Show current dealer
        """
        response = self.send_request(method='get',
                                     route='/game/get_dealer')
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            print(f"Current dealer is "
                  f"{response_dict['result_message']['current_dealer']}")
        else:
            self.print_error_response(response)

    def do_current_issue(self, inp):
        """
        Show issue that players are voting on now
        """
        response = self.send_request(method='get',
                                     route='/issue/current')
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            self.print_issue(response_dict)
        else:
            self.print_error_response(response)

    def do_current_players(self, inp):
        """
        Show players that are registered for the current game
        """
        response = self.send_request(method='get',
                                     route='/user/show_all')
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            current_users = response_dict['result_message']['current_users']
            if len(current_users) == 0:
                print(f"Please add players to the game")
            else:
                print(f"Currently playing Planning Poker: "
                      f"{json.dumps(current_users)}")
        else:
            self.print_error_response(response)

    def do_current_votes(self, inp):
        """
        Show if all players voted or who still has to vote
        """
        response = self.send_request(method='get',
                                     route='/issue/vote_status')
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            print(f"{response_dict['result_message']}")
        else:
            self.print_error_response(response)

    def do_exit(self):
        """
        Command for exiting planning poker game
        """

        crt_dict = {
            'name': self.username
        }

        response = self.send_request(method='post',
                                     route='/user/exit',
                                     data=crt_dict)
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            print(f"{response_dict['result_message']['user_exit_status']}")
        else:
            self.print_error_response(response)
        print(f"Buh-bye! And in case I don't see you again, "
              f"good afternoon, good evening and good night!")
        return True

    def do_new_game(self, inp):
        """
        Start new game
        """
        crt_dict = {
            'name': self.username
        }
        response = self.send_request(method='post',
                                     route='/game/new',
                                     data=crt_dict)
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            print(f"{response_dict['result_message']}")
        else:
            self.print_error_response(response)

    def do_next_issue(self, inp):
        """
        Jump to next issue, if there is one (i.e. the current issue
        is the last one and we can go back to programming)
        """

        crt_dict = {
            'name': self.username
        }

        response = self.send_request(method='post',
                                     route='/issue/next',
                                     data=crt_dict)
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            self.print_issue(response_dict)
        else:
            self.print_error_response(response)

    def do_previous_issue(self, inp):
        """
        Jump to previous issue, if there is one (i.e. we are not on
        the first issue)
        """

        crt_dict = {
            'name': self.username
        }

        response = self.send_request(method='post',
                                     route='/issue/previous',
                                     data=crt_dict)
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            self.print_issue(response_dict)
        else:
            self.print_error_response(response)

    def do_remove_player(self, username):
        """
        Remove a player from the current game
        """

        if len(username) < 4:
            print(f"Please use a more meaningful name")
        else:
            params_dict = {
                'username': username
            }
            data_dict = {
                'name': self.username
            }
            response = self.send_request(method='post',
                                         route='/user/remove',
                                         params=params_dict,
                                         data=data_dict)
            if response.status_code == status.HTTP_200_OK:
                response_dict = json.loads(response.text)
                print(f"{response_dict['result_message']}")
            else:
                self.print_error_response(response)

    def do_reset_votes(self, inp):
        """
        Reset votes on current issue
        """
        crt_dict = {
            'name': self.username
        }
        response = self.send_request(method='post',
                                     route='/issue/votes_reset',
                                     data=crt_dict)
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            print(f"{response_dict['result_message']}")
        else:
            self.print_error_response(response)

    def do_show_report(self, inp):
        """
        Show vote report for current issue
        """
        response = self.send_request(method='get',
                                     route='/issue/show_results')
        if response.status_code == status.HTTP_200_OK:
            response_message = json.loads(response.text)['result_message']
            if response_message['status'] == 'pending':
                print(f"{response_message['report']}")
            else:
                self.parse_report(response_message['report'])
        else:
            self.print_error_response(response)

    def do_user_count(self, inp):
        """
        Show how many users are registered for the current game
        """
        response = self.send_request(method='get',
                                     route='/user/count')
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            user_count = response_dict['result_message']['user_count']
            if len(user_count) == 1:
                verb = 'is'
            else:
                verb = 'has'
            print(f"Currently, there {verb} {user_count} registered "
                  f"players")
        else:
            self.print_error_response(response)

    def do_vote_issue(self, vote_value):
        """
        Vote on the current issue with the registered user here
        """
        crt_dict = {
            'name': self.username,
            'vote_value': vote_value
        }
        response = self.send_request(method='put',
                                     route='/issue/vote',
                                     data=crt_dict)
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            print(f"{response_dict['result_message']}")
        else:
            self.print_error_response(response)

    def do_voting_system(self, inp):
        """
        Show voting system for the current game
        """
        response = self.send_request(method='get',
                                     route='/game/voting_system')
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            print(f"{response_dict['result_message']}")
        else:
            self.print_error_response(response)

    do_EOF = do_exit


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("-u", "--url", type=str,
                        help="Set poker server url")

    args = parser.parse_args()
    if args.url:
        url_arg = ''.join(['http://', args.url, ':8000'])
    else:
        url_arg = 'http://localhost:8000'

    MyPrompt(url=url_arg).cmdloop()
