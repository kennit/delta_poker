import argparse
import json
import requests
import time

from cmd import Cmd
from fastapi import status
from pathlib import Path


class MyPrompt(Cmd):
    prompt = 'planning_poker> '
    intro = "Welcome to a nice game of Planning Poker!\nType ? to list commands"

    default_config_params = {"max_retries": 5,
                             "show_timeout": 1,
                             "url": "http://localhost:8000"}
    default_keys_set = set(default_config_params.keys())

    def __init__(self, **config_params):
        super().__init__()
        self.username = None

        keys_set = set(config_params.keys())
        common_config_keys = self.default_keys_set.intersection(keys_set)
        difference_config_keys = self.default_keys_set.difference(keys_set)

        if len(difference_config_keys) == 0:
            for config_key, config_value in config_params.items():
                setattr(self, config_key, config_value)
        else:
            if len(difference_config_keys) < len(self.default_keys_set):
                print("Not all parameters found in configuration file.")
                for config_key in common_config_keys:
                    setattr(self, config_key, config_params[config_key])
            print(f"Using default value for {difference_config_keys}")
            for config_key in difference_config_keys:
                setattr(self, config_key,
                        self.default_config_params[config_key])

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
            print(f"{message.capitalize()}")
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
            print(f"{vote_details['vote_count']} voted for {vote_value} "
                  f"story points.\n"
                  f"{json.dumps(vote_details['voters'], indent=4)}\n")

    def get_report(self, inp):
        current_status = 'pending'
        retry_count = 0
        while current_status == 'pending' and retry_count < self.max_retries:
            response = self.send_request(method='get',
                                         route='/issue/show_results')
            if response.status_code == status.HTTP_200_OK:
                response_message = json.loads(response.text)['result_message']
                current_status = response_message['status']
                if current_status == 'done':
                    self.parse_report(response_message['report'])
            else:
                current_status = 'error'
                self.print_error_response(response)
            retry_count += 1
            time.sleep(self.show_timeout)

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
                print("Please add players to the game")
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
        print(f"Buh-bye, {self.username}! And in case I don't see you again, "
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
            print("Please use a more meaningful name")
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
        self.get_report(inp)

    def do_user_count(self, inp):
        """
        Show how many users are registered for the current game
        """
        response = self.send_request(method='get',
                                     route='/user/count')
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            user_count = response_dict['result_message']['user_count']
            if user_count == 1:
                verb = 'is'
            else:
                verb = 'are'
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

    crt_config_params = {}
    config_path = Path('./configs/cli_config.json')

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str,
                        help="Configuration file name")
    args = parser.parse_args()
    if args.config:
        config_path = Path(args.config)

    if config_path.exists():
        with open(config_path) as f:
            try:
                crt_config_params = json.load(f)
            except json.decoder.JSONDecodeError as je:
                print(f"Please make sure config file contains a dict in json "
                      f"format. An example can be found in "
                      f"'./configs/cli_config.json'. {je} was raised.")
    else:
        print(f"Please make sure the path {config_path} is correct and that "
              f"the file exists. Will use default configuration parameters "
              f"this time.")

    MyPrompt(**crt_config_params).cmdloop()
