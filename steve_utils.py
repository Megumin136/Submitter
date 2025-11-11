import argparse
import getpass
import os

try:
    import requests
except ModuleNotFoundError:
    print("Please install the 'requests' library: pip install requests")
    exit(1)

BASE_URL = f"https://stevec.pythonanywhere.com/assignments"
KEY_URL = f"{BASE_URL}/api-key"
PASS_URL = f"{BASE_URL}/password"


def request_submit(student_id, group_id, password, filename, assignment):
    try:
        files = {
            "file": open(filename, "rb")
        }
    except FileNotFoundError:
        print("File not found")
        exit(1)

    data = {"student_id": student_id,
            "password": password,
            "assignment": assignment}
    if group_id is not None:
        data["group_id"] = group_id

    response = requests.post(BASE_URL,
                             data=data,
                             files=files)
    print(response.text)

def request_change_password(student_id, current_password, new_password):
    response = requests.post(PASS_URL,
                             json={"student_id": student_id,
                                   "current_password": current_password,
                                   "new_password": new_password
                                   })
    print(response.text)


def request_api_key(student_id, password):
    response = requests.post(KEY_URL,
                             json={"student_id": student_id,
                                   "password": password
                                   })
    print(response.text)


def get_password(prompt):
    password = getpass.getpass(prompt).strip()
    if len(password) == 0:
        print("Password cannot be empty.")
        exit(1)
    else:
        return password


def run_api_key(student_id):
    if student_id is None:
        print("Student ID is required.")
        exit(1)
    password = get_password("Password: ")

    request_api_key(student_id, password)


def run_change_password(student_id):
    if student_id is None:
        print("Student ID is required.")
        exit(1)
    password = get_password("Password: ")
    new_password = get_password("New Password: ")
    if password == new_password:
        print("New password matches your old password.")
        exit(1)

    new_password_confirm = get_password("Repeat Password: ")
    if new_password != new_password_confirm:
        print("Passwords do not match.")
        exit(1)

    request_change_password(student_id, password, new_password)

def run_submit(student_id, group_id, file_path, assignment):
    if student_id is None:
        print("Student ID is required.")
        exit(1)

    if file_path is None or not os.path.exists(file_path):
        print("File path does not exist.")
        exit(1)

    if assignment is None:
        print("Assignment name is required.")
        exit(1)

    password = get_password("Password: ")
    request_submit(student_id, group_id, password, file_path, assignment)


def main(args):
    match args.command:
        case "password":
            run_change_password(args.student_id)
        case "submit":
            run_submit(args.student_id, args.group_id, args.file, args.assignment)
        case "api_key":
            run_api_key(args.student_id)
        case _:
            print("Unknown command.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utils for Steve's SETU modules")
    parser.add_argument("command", choices=["password", "submit", "api_key"])
    parser.add_argument("--file", "-f", help="File to submit", default=None)
    parser.add_argument("--student_id", "-s", help="Student ID", default=None)
    parser.add_argument("--group_id", "-g", help="Group ID", default=None)
    parser.add_argument("--assignment", "-a", help="Assignment name", default=None)

    main(parser.parse_args())
