# Created by camillodejong at 14/08/2024 00:29
# DEZE FILE IS BEDOELD GEÏMPORTEERD ZIJN VANAF `main.py` (OM PROGRAMMA TE KUNNEN HERSTARTEN)


from imports import *


def get_current_branch():
    return os.popen(f"git rev-parse --abbrev-ref HEAD").read().strip()


branch = get_current_branch()


def restart_program():
    python = sys.executable
    os.execv(python, [python] + sys.argv)


def fetch_changes():
    print(os.popen("git fetch --verbose origin").read())


def get_local_version_number() -> int:
    """Get local commit count (int)"""
    return int(os.popen("git rev-list --count HEAD").read())


def get_remote_version_number(fetch=True) -> int:
    """Get remote commit count (int), optionally fetch first"""
    if fetch:
        fetch_changes()
    return int(os.popen(f"git rev-list --count origin/{branch}").read())


def get_local_hash() -> str:
    return os.popen("git rev-parse HEAD").read().strip()


def get_remote_hash(fetch=True) -> str:
    if fetch:
        fetch_changes()
    return os.popen(f"git rev-parse origin/{branch}").read().strip()


def check_update_available(fetch=True, return_version=False) -> bool | int:
    """
    Check if an update is available by comparing commit hashes.
    Returns:
      - False if up to date
      - True if update available and return_version=False
      - remote version number if return_version=True
    """
    remote_hash = get_remote_hash(fetch=fetch)
    local_hash = get_local_hash()
    print(f"Local hash: {local_hash}")
    print(f"Remote hash: {remote_hash}")

    if local_hash == remote_hash:
        print("Your local repository is up-to-date.")
        return False

    print("New version available.")
    if return_version:
        return get_remote_version_number(fetch=False)
    return True


def merge_latest_repo(fetch=True) -> bool:
    """Reset local repo to remote master HEAD"""
    if fetch:
        fetch_changes()
    print("Merging latest changes...")
    output = os.popen(f"git reset --hard origin/{branch}").read()
    print(output)
    return True


def update_requirements(requirements_file=None):
    if requirements_file is None:
        requirements_file = config["requirements_file_path"]
    print(f"Installing requirements from {requirements_file}...")
    os.system(f'pip3 install -r "{requirements_file}"')


def deploy_latest_update(fetch=True):
    """
    Deploy update if available:
    - Check update
    - Merge latest repo
    - Install requirements
    - Restart program
    """
    if not check_update_available(fetch=fetch):
        return False

    if not merge_latest_repo(fetch=False):
        print("Failed to merge latest repo.")
        return False

    update_requirements()
    print("Done updating. Restarting...")
    restart_program()
    return None
