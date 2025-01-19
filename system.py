# Created by camillodejong at 14/08/2024 00:29

# DEZE FILE IS BEDOELD GEÏMPORTEERD ZIJN VANAF `main.py` (OM PROGRAMMA TE KUNNEN HERSTARTEN)

import os
import sys

import PySimpleGUI


def restart_program():
    python = sys.executable
    os.execv(python, [python] + sys.argv)


def get_current_version_number(fetch=False):
    """
    Zorg ervoor dat is ge-fetched voor gebruik
    """
    if fetch is True:
        fetch_changes()

    return int(os.popen("git rev-list --count HEAD").read())


def fetch_changes():  # Fetch the latest changes from the remote repository
    print(os.popen("git fetch --verbose origin").read(), "aaa")


def check_update_available(fetch=False, return_newest_version_number=False, fetch_for_newest_version_number=False) -> bool | int:
    """
    Zorg ervoor dat is ge-fetched voor gebruik
    """
    if fetch is True:
        fetch_changes()

    # Get the latest commit hash on the local and remote branches
    local_hash = os.popen("git rev-parse HEAD").read()
    remote_hash = os.popen("git rev-parse origin/master").read()

    print(local_hash)
    print(remote_hash)

    if local_hash == remote_hash:
        print("Your local repository is up-to-date.")
        return False

    print("New version available.")
    if return_newest_version_number:
        return get_current_version_number(fetch_for_newest_version_number)
    return True


def merge_latest_repo(fetch=False):  # update if available
    """
    Zorg ervoor dat is ge-fetched voor gebruik
    """
    if fetch is True:
        fetch_changes()
    print("Merging latest changes...")

    # todo gebruik voor dev
    # print(os.popen("git merge origin/master").read())

    # todo gebruik vóór installeren op raspberry schoolserver!!!!!!!!
    print(os.popen("git reset --hard origin/master").read())
    return True


def deploy_latest_update(fetch=True):
    """
    Zorg ervoor dat is ge-fetched voor gebruik
    """
    # TODO maak checken voor update en update installeren apart
    update_available = check_update_available(fetch=fetch)
    if not update_available:
        return False
    merged_latest_update = merge_latest_repo()
    if not merged_latest_update:
        return False
    print("Done updating. Restarting...")
    restart_program()
