# client/backend.py
# Bevat alle functies voor communicatie met server

# Van ~/PycharmProjects/PythonProjects/BankKasGeldSchool/api/client/old4_fail/bank.py


import copy
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Union, Optional

import requests

from models import *

from imports import *

DEFAULT_CONFIG = """
{
  "request_url": "http://localhost:8000/",
  "cookiejar_location": "cookiejar.json",
  "window_size": [1000, 600],
  "window_edge_margin": [15, 15],
  "theme": "SystemDefaultForReal",
  "font": ["Helvetica", 35],
  "item_separation": ["-", 80],
  "catch_handled_http_exceptions": true,
  "catch_connectivity_error_exceptions": true,
  "use_global_exception_handler": true
}
"""


def load_config(path="config.json", default_config: Union[str, dict] = DEFAULT_CONFIG):
    print(path)
    try:
        with open(path) as f:
            conf = json.load(f)
    except FileNotFoundError as e:
        print(f"{e}\nRestoring {path}")

        # maakt nieuwe configfile aan als het niet te vinden is
        with open(path, "w") as f:
            json.dump(default_config, f) if type(default_config) is dict else f.write(default_config)
        conf = default_config if type(default_config) is dict else json.loads(default_config)

    print(f"Config at `{path}` loaded.")
    return conf


config = load_config()


def restart_program():
    python = sys.executable
    os.execv(python, [python] + sys.argv)


def global_exception_handler(exc_type, exc_value, exc_traceback):
    traceback.print_tb(exc_traceback)
    time.sleep(.1)  # dit is hier zodat de tekst die hier onder DAADWERKELIJK ONDER de tekst hier boven wordt geprint.
    print(f"{exc_type.__name__}: {exc_value}")

    if exc_type is requests.exceptions.ConnectionError:
        if config["catch_connectivity_error_exceptions"] is False:
            return
        pysg.Popup("Verbinding niet mogelijk.\n"
                   "Zorg ervoor dat je verbonden bent met het WiFi netwerk 'De Vrije Ruimte'\n"
                   "Check je connectie en probeer het opnieuw.\n"
                   "Neem AUB contact op met Camillo als dit propleem vaker voorkomt.",
                   title="Connectie Fout", keep_on_top=True, font=config["font"])
    else:
        pysg.Popup(
            f"⚠Er is een onverwachtse fout opgetreden. Neem AUB contact op met Camillo als dit propleem vaker voorkomt."
            f"\nType: {exc_type.__name__}",
            title="ONBEKENDE FOUT", text_color='red', keep_on_top=True, font=config["font"]
        )

    if pysg.popup_yes_no("Opnieuw opstarten?", font=get_font(), keep_on_top=True) == "Yes":
        restart_program()


if config["use_global_exception_handler"]:
    sys.excepthook = global_exception_handler


class Session(requests.Session):
    def request(self, *args, **kwargs):
        response = super().request(*args, **kwargs)
        cookies = requests.utils.dict_from_cookiejar(session.cookies)  # turn cookiejar into dict
        Path(config["cookiejar_location"]).write_text(json.dumps(cookies))  # save them to file as JSON
        return response


session = Session()

# laad cookies (no questions. het werkt.)
with open(config["cookiejar_location"], 'a'):
    pass
with open(config["cookiejar_location"], 'r+') as f:
    content = f.read()
    f.seek(0)
    if content.strip() == "":
        f.write("{}")
        content = "{}"
    session.cookies.update(requests.utils.cookiejar_from_dict(json.loads(content)))  # load cookiejar to current session


def get_font(scale: float = 1, font: Union[tuple, list, str] = None):
    if font is None:
        font = config["font"]
    elif type(font) is str:
        font = font.split(" ")
    font_size = float(font[1])
    result_font = " ".join([
        font[0],
        str(int(font_size * scale))
    ])
    # print("returning font:", result_font)
    return result_font


def check_string_valid_float(string: str):
    try:
        return float(string)
    except ValueError:
        return False


def check_valid_saldo(saldo: float):
    if -7320 > float(saldo) or float(saldo) > 7320:
        pysg.popup("Houd u dat bedrag eventjes realistisch?", font=config["font"], keep_on_top=True,
                   title="Fout")
        return False
    return True


def check_not_good_status(response: requests.Response, catch_handled_http_exceptions=None):
    if catch_handled_http_exceptions is None:
        catch_handled_http_exceptions = config["catch_handled_http_exceptions"]
    if catch_handled_http_exceptions:
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            print(e)
            return False
    else:
        response.raise_for_status()


class Admin:  # todo
    def __init__(self):
        pass

    @staticmethod
    def check_session_valid(catch_handled_http_exceptions=None):
        response = session.get(config["request_url"])

        if check_not_good_status(response, catch_handled_http_exceptions=catch_handled_http_exceptions) is False:
            return False

        return True

    @staticmethod
    def login(login_field: AdminLoginField, catch_handled_http_exceptions=None):
        response = session.post(config["request_url"] + "login",
                                json=login_field.model_dump())
        if check_not_good_status(response, catch_handled_http_exceptions=catch_handled_http_exceptions) is False:
            return False

        return True


class User:
    def __init__(self, data: RawUserData):
        self.data = data

    def set_saldo(self, transaction_details: TransactionField):
        data = transaction_details.model_dump()
        response = session.put(config["request_url"] + "set_saldo", params={"user_id": self.data.user_id},
                               json=data)
        response.raise_for_status()

        self.data.saldo = transaction_details.saldo_after_transaction
        return True

    def rename(self, new_username: str) -> Optional[bool]:
        params = {"user_id": self.data.user_id, "new_username": new_username}
        response = session.put(config["request_url"] + "rename_user", params=params)
        response.raise_for_status()
        if response.status_code == 200:
            self.data.name = new_username
        elif response.status_code == 404:
            return False
        return True

    def refresh_data(self):
        new_data = self.get_user(user_id=self.data.user_id).data
        self.data = new_data

    @staticmethod
    def get_user_exists_by_username(username: str):
        response = session.get(config["request_url"] + "get_user_exists_by_username", params={"username": username})
        return response.json()

    @staticmethod
    def get_user_exists_by_id(user_id: int):
        return session.get(config["request_url"] + "get_user_exists_by_id", params={"user_id": user_id}).json()

    @staticmethod
    def add_user(userdata: AddUser) -> bool:
        response = session.post(config["request_url"] + "add_user", json=userdata.model_dump())
        response.raise_for_status()
        return True

    @staticmethod
    def get_all_userdata():
        return session.get(config["request_url"] + "get_all_userdata").json()

    @classmethod
    def get_user(cls, user_id: int):
        response = session.get(config["request_url"] + "get_userdata", params={"user_id": user_id})
        response.raise_for_status()
        return cls(data=RawUserData(**response.json()))

    @classmethod
    def get_user_by_username(cls, username: str):
        response = session.get(config["request_url"] + "get_userdata_by_username", params={"username": username})
        response.raise_for_status()
        return cls(data=RawUserData(**response.json()))

    @staticmethod
    def get_username_list():
        result = session.get(config["request_url"] + "get_username_list").json()
        print(result)
        return result

    @staticmethod
    def get_transaction_list(user_id: int):
        response = session.get(config["request_url"] + "get_transaction_list", params={"user_id": user_id})
        response.raise_for_status()  # fixme
        return ([
            RawTransactionData(**transaction) for transaction in response.json()
        ])

    @staticmethod
    def generate_transaction(current_money: float, transaction_details: TransactionField):
        params = {"current_money": current_money}
        return session.post(config["request_url"] + "generate_transaction",
                            params=params, json=transaction_details.model_dump()).json()

    @staticmethod
    def delete_user(user_id: int) -> bool:
        response = session.delete(config["request_url"] + "delete_user", params={"user_id": user_id})
        response.raise_for_status()
        return response.status_code == 200


# todo: add to Camillib
def filter_list(search: str, seq: list[str], case_sensitive: bool = False, order_alphabetically: bool = True) -> list:
    if order_alphabetically:
        seq.sort()

    result = []
    for item in seq:
        if item == search:
            result.insert(0, item)
        elif (search in item) if case_sensitive else (search.casefold() in item.casefold()):
            result.append(item)

    return result


def reverse(seq):  # todo: replace with build in function
    t = copy.deepcopy(seq)
    t.reverse()
    return t


def overwrite_dict_with_dict(original_dict: dict, overwriter_dict):
    for key, value in overwriter_dict.items():
        original_dict[key] = value
    return original_dict


def on_exit(message=None) -> None:
    if message is None:
        sys.exit(0)
    else:
        sys.exit(str(message))


def handle_http_exception(func):
    def wrapper(*args, **kwargs):
        output = func(*args, **kwargs)

        ...

        return output

    return wrapper
