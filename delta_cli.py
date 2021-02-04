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

    def send_request(self, method, route, data=None):
        full_uri = ''.join([self.url, route])
        response = requests.request(method=method, url=full_uri, json=data)
        return response

    def do_voting_system(self, inp):
        """
        Show voting system for the current game
        """
        response = self.send_request(method='get',
                                     route='/voting_system')
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            print(f"{response_dict['message']}")
        elif response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            message = json.loads(response.text)['detail'][0]['msg']
            print(f"{message}")
        else:
            print(f"{response.text}")

    # check username validity locally
    def do_add_player(self, username):
        """
        Add a player to the current game
        """
        if self.username:
            print(f"You are already registered in the game as {self.username}")
        elif len(username) < 4:
            print(f"Please use a more meaningful name")
        else:
            crt_dict = {
                'name': username
            }
            response = self.send_request(method='put',
                                         route='/user/add',
                                         data=crt_dict)
            if response.status_code == status.HTTP_200_OK:
                self.username = username
                print(f"{json.dumps(json.loads(response.text), indent=4)}")
            elif response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
                message = json.loads(response.text)['detail'][0]['msg']
                print(f"{message}")
            else:
                print(f"{response.text}")

    def do_current_issue(self, inp):
        """
        Show issue that players are voting on now
        """
        response = self.send_request(method='get',
                                     route='/issue/current')
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            print(f"Current issue: "
                  f"{response_dict}")
        elif response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            message = json.loads(response.text)['detail'][0]['msg']
            print(f"{message}")
        else:
            print(f"{response.text}")

    # check vote validity on the server
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
            print(f"{json.dumps(response_dict, indent=4)}")
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            print(f"{json.loads(response.text)['detail']}")
        elif response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            message = json.loads(response.text)['detail'][0]['msg']
            print(f"{message}")
        else:
            print(f"{response.text}")

    def do_user_count(self, inp):
        """
        Show how many users are registered for the current game
        """
        response = self.send_request(method='get',
                                     route='/user/count')
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            print(f"Number of registered users for current game: "
                  f"{response_dict['user_count']}")
        elif response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            message = json.loads(response.text)['detail'][0]['msg']
            print(f"{message}")
        else:
            print(f"{response.text}")

    def do_current_players(self, inp):
        """
        Show players that are registered for the current game
        """
        response = self.send_request(method='get',
                                     route='/user/show_all')
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            print(f"Registered players for current game: "
                  f"{response_dict['current_users']}")
        elif response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            message = json.loads(response.text)['detail'][0]['msg']
            print(f"{message}")
        else:
            print(f"{response.text}")

    def do_current_votes(self, inp):
        """
        Show who voted and who still has to vote
        """
        response = self.send_request(method='get',
                                     route='/issue/vote_status')
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            left_to_vote_count = response_dict['left_to_vote']
            if len(left_to_vote_count) == 0:
                print(f"Everybody has voted. You can type show_report "
                      f"to see votes")
            else:
                if len(left_to_vote_count) > 1:
                    verb = "have"
                elif len(left_to_vote_count) == 1:
                    verb = "has"
                print(f"{left_to_vote_count} still {verb} to vote")
        elif response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            message = json.loads(response.text)['detail'][0]['msg']
            print(f"{message}")
        else:
            print(f"{response.text}")

    def do_show_report(self, inp):
        """
        Show vote report for current issue
        """
        response = self.send_request(method='get',
                                     route='/issue/show_results')
        if response.status_code == status.HTTP_200_OK:
            response_dict = json.loads(response.text)
            print(f"{json.dumps(response_dict['report'], indent=4)}")
        elif response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            message = json.loads(response.text)['detail'][0]['msg']
            print(f"{message}")
        else:
            print(f"{response.text}")

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
            print(f"{json.dumps(response_dict, indent=4)}")
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            print(f"{json.loads(response.text)['detail']}")
        elif response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            message = json.loads(response.text)['detail'][0]['msg']
            print(f"{message}")
        else:
            print(f"{response.text}")

    def do_prev_issue(self, inp):
        """
        Jump to previous issue, if there is one (i.e. we are on
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
            print(f"{json.dumps(response_dict, indent=4)}")
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            print(f"{json.loads(response.text)['detail']}")
        elif response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            message = json.loads(response.text)['detail'][0]['msg']
            print(f"{message}")
        else:
            print(f"{response.text}")

    def do_exit(self):
        """Command for exiting planning poker game."""
        print(f"Buh-bye! And in case I don't see you again, "
              f"good afternoon, good evening and good night!")
        return True

    def default(self, inp):
        """
        Use x or q to exit the game. All commands that are
        not implemented will just be printed with a notification
        message.
        """
        if inp == 'x' or inp == 'q':
            return self.do_exit()

        print(f"Haven't found this command: {inp}")

    do_EOF = do_exit


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("-u", "--url", type=str,
                        help="Set poker server url")

    args = parser.parse_args()
    if args.url:
        url = ''.join(['http://', args.url, ':8000'])
    else:
        url = 'http://localhost:8000'

    MyPrompt(url=url).cmdloop()
