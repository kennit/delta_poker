import argparse
import json
import requests
import sys

from fastapi import status

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str,
                        help="Set filename from which to add_issues")
    parser.add_argument("-u", "--url", type=str,
                        help="Set poker server url")
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="Verbosity")

    args = parser.parse_args()
    if args.filename:
        issues_filename = args.filename
    else:
        print("Please add filename")
        sys.exit(0)
    if args.url:
        url = args.url
    else:
        url = 'http://localhost:8000'

    # read issues
    with open(issues_filename) as f:
        issues_list = json.load(fp=f)

    # add issue(s)
    for crt_issue in issues_list:
        try:
            response = requests.put('/'.join([url, 'issue/add']),
                                    json=crt_issue)
        except requests.exceptions.ConnectionError as ce:
            print(f"Server might not be running, or is not accesible from "
                  f"this network: {ce}")
            sys.exit(0)
        if response.status_code == status.HTTP_200_OK:
            if args.verbose:
                response_dict = json.loads(response.text)
                print(f"{json.dumps(json.loads(response.text), indent=4)}")
        else:
            print(f"Received {response.status_code} from server")
