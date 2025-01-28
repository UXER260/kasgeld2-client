# Created by camillodejong at 14/08/2024 00:29

# DEZE FILE IS BEDOELD GEÏMPORTEERD ZIJN VANAF `main.py` (OM PROGRAMMA TE KUNNEN HERSTARTEN)

import os
import sys

import PySimpleGUI


def restart_program():
    python = sys.executable
    os.execv(python, [python] + sys.argv)


def get_current_version_number(remote=False):
    if remote:
        # Get the commit count for the remote branch
        return int(os.popen("git rev-list --count origin/master").read())

    return int(os.popen("git rev-list --count HEAD").read())


def fetch_changes():  # Fetch the latest changes from the remote repository
    print(os.popen("git fetch --verbose origin").read(), "aaa")


def check_update_available(return_newest_version_number=False) -> bool | int:
    """
    Zorg ervoor dat is ge-fetched voor gebruik
    """
    # if fetch is True:  # fixme fetch is niet meer nodig, gebruik get version number functie voor vergelijking
    #     fetch_changes()

    # Get the latest commit hash on the local and remote branches
    # local_hash = os.popen("git rev-parse HEAD").read()
    # remote_hash = os.popen("git rev-parse origin/master").read()

    # print("local hash ", local_hash.strip())
    # print("remote hash", remote_hash.strip())

    local_version = get_current_version_number(remote=False)
    remote_version = get_current_version_number(remote=True)

    print("local version ", local_version)
    print("remote version", remote_version)

    if local_version == remote_version:
        print("Your local repository is up-to-date.")
        return False

    print("New version available.")
    if return_newest_version_number:
        return remote_version
    return True


def merge_latest_repo(fetch=True):  # update if available
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
    update_available = check_update_available()
    if not update_available:
        return False
    merged_latest_update = merge_latest_repo(fetch=fetch)
    if not merged_latest_update:
        return False
    print("Done updating. Restarting...")
    restart_program()
