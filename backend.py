# client/backend.py
# Bevat alle functies voor communicatie met server
from __future__ import annotations

# Van ~/PycharmProjects/PythonProjects/BankKasGeldSchool/api/client/old4_fail/bank.py


import copy
from pathlib import Path
from typing import Union
from unidecode import unidecode
import PySimpleGUI as pysg
import Camillo_GUI_framework
import requests

from models import *

from imports import *


class AdminLoginMenu(Camillo_GUI_framework.Gui):
    def __init__(self, window_dimensions=(None, None), window_is_popup=True,
                 window_title="Voer gegevens in",
                 restart_on_success=True,
                 *args, **kwargs):
        super().__init__(window_dimensions=window_dimensions,
                         window_is_popup=window_is_popup, window_title=window_title, *args,
                         **kwargs)
        self.restart_on_success = restart_on_success

    def layout(self) -> list[list[pysg.Element]]:
        return [
            [pysg.Text("email:", font=self.font), pysg.Push()],
            [pysg.InputText("", font=self.font, size=(18, 0), key='-EMAIL-')],
            [pysg.Text("password:", font=self.font), pysg.Push()],
            [pysg.InputText("", font=self.font, size=(18, 0), password_char="•", key='-PASSWORD-')],
            [pysg.VPush()],
            [pysg.Button("OK", expand_x=True, font=self.font)]
        ]

    def set_window(self, *args, **kwargs):
        super().set_window(*args, **kwargs)
        self.window["-PASSWORD-"].bind('<Enter>', "<HoverPassword>")
        self.window["-PASSWORD-"].bind('<Leave>', "<UnHoverPassword>")

    def update(self):
        super().update()

        if self.event == "-PASSWORD-<HoverPassword>":  # Geeft wachtwoord weer bij hover over input
            self.window["-PASSWORD-"].update(password_char="")

        elif self.event == "-PASSWORD-<UnHoverPassword>":
            self.window["-PASSWORD-"].update(password_char="•")

        if self.event == "OK" and all(self.values):
            login_field = AdminLoginField(email=self.values["-EMAIL-"], password=self.values["-PASSWORD-"])
            succes = Admin.login(login_field=login_field)
            if not succes:
                # pysg.popup_quick("Gegevens komen niet overeen", auto_close_duration=1, non_blocking=True,
                #                  no_titlebar=True, background_color="red", title="Fout", font=self.font,
                #                  keep_on_top=True)
                return False
            else:
                # App.back_button()
                # assert isinstance(App.current_gui(), UserSelectionWindow)
                # App.current_gui().refresh(namelist_fetch=True)
                # # App.current_gui().refresh(search_name="")
                # pysg.popup_no_buttons("succes!", non_blocking=True, auto_close=True, auto_close_duration=.75,
                #                       no_titlebar=True, font=self.font)
                # return True
                self.menu.reset_app()
                pysg.popup_no_buttons("succes!", non_blocking=True, auto_close=True, auto_close_duration=.5,
                                      no_titlebar=True, font=self.font, keep_on_top=True)

    def on_close(self):
        App.active = False


class App(Camillo_GUI_framework.App):

    @classmethod
    def login_prompt(cls, restart_on_success=True):
        if pysg.popup_yes_no("Log in voor toegang", title="De inlog is verlopen",
                             font=get_font(), keep_on_top=True) == "Yes":

            cls.set_gui(gui=AdminLoginMenu(restart_on_success=restart_on_success))
            return True
        else:
            cls.active = False
            return False

    @classmethod
    def on_run(cls):
        import updater
        updater.deploy_latest_update()
        # als nieuwe update beschikbaar en gedownload was,
        # dan zal dit programma nu herstarten en alle code hieronder niet meer worden ge-execute

        valid_session = Admin.check_session_valid()
        if valid_session is False:
            if cls.login_prompt(restart_on_success=False) is False:
                return False

        # als het None is dan niet inloggen maar direct naar kies menu waar gebruiker word verteld dat geen connectie
        super().on_run()

    @classmethod
    def run(cls):
        cls.on_run()
        while cls.active:
            if not config["use_global_exception_handler"]:
                cls.update()
            else:
                try:
                    cls.update()
                except requests.exceptions.ConnectionError:
                    pysg.Popup("Verbinding niet (meer) mogelijk.\n"
                               "Zorg ervoor dat je verbonden bent met het WiFi netwerk 'De Vrije Ruimte'\n\n"
                               "Check je connectie en probeer het opnieuw.", title="Geen verbinding",
                               keep_on_top=True,
                               font=config["font"])

                except requests.exceptions.HTTPError as e:
                    print(e.response.content)
                    print(e.response.status_code)
                    pysg.Popup(
                        f"⚠Er is een onverwachtse fout opgetreden. Neem AUB contact op met Camillo als dit propleem vaker voorkomt."
                        f"\n\nFout: {e.response.reason}"
                        f"\nType: {e.__class__.__name__}",
                        title=f"ONBEKENDE FOUT", text_color="red", keep_on_top=True, font=config["font"]
                    )
                except Exception as e:
                    pysg.Popup(
                        f"⚠Er is een onverwachtse fout opgetreden. Neem AUB contact op met Camillo als dit propleem vaker voorkomt."
                        f"\n\nType: {e.__class__.__name__}",
                        title=f"ONBEKENDE FOUT", text_color="red", keep_on_top=True, font=config["font"]
                    )


def restart_program():
    python = sys.executable
    os.execv(python, [python] + sys.argv)


class Session(requests.Session):
    def request(self, *args, **kwargs):
        print("REQUEST", *args)
        response = super().request(*args, **kwargs)
        cookies = requests.utils.dict_from_cookiejar(session.cookies)  # turn cookiejar into dict
        Path(config["cookiejar_location"]).write_text(json.dumps(cookies))  # save them to file as JSON
        return response


session = Session()

cookie_jar = load_config(path=config["cookiejar_location"], default_config="{}")
session.cookies.update(requests.utils.cookiejar_from_dict(cookie_jar))  # load cookiejar to current session


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
        return float(string.replace(',', '.'))
    except ValueError:
        return False


def check_valid_saldo(saldo: float):
    if -7320 > float(saldo) or float(saldo) > 7320:
        pysg.popup("Houd u dat bedrag eventjes realistisch?", font=config["font"], keep_on_top=True,
                   title="Fout")
        return False
    return True


def good_status(response: requests.Response, catch_handled_http_exceptions: Optional[bool] = None,
                restart_on_unauthorized=True):
    # assert restart_on_unauthorized is not True
    """
    Checkt of status code goed is van response.
    :param response: Response om te controleren
    :type response: requests.Response
    :param catch_handled_http_exceptions:
    :type catch_handled_http_exceptions:
    :return: None wanneer sessie ongeldig is, True wanneer alles goed is en False wanneer er iets niet goed is
    :rtype: bool | None
    """
    catch_handled_http_exceptions = catch_handled_http_exceptions if catch_handled_http_exceptions is not None else \
        config["catch_handled_http_exceptions"]
    # print("catch_handled_http_exceptions", catch_handled_http_exceptions, config["catch_handled_http_exceptions"])
    # print(f"CONTENT {response.content}", response.status_code)
    fout = False
    error = None
    if catch_handled_http_exceptions:
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("CONTENT:", response.content)
            error = e
            fout = True
    else:
        response.raise_for_status()

    if fout:
        if response.status_code == 404:
            print("url bestaat niet")
            return None

        elif response.status_code == 401:
            print("Ongeautoriseerd")
            if restart_on_unauthorized is True:
                restart_program()  # fixme todo vervang met App.reset_app()
            return False

        elif response.status_code == 500:
            raise error

        return False

    if response.status_code == 200:
        return True
    else:
        print("Goed gekeurde status, maar niet gelijk aan 200")
        return False


class Admin:  # todo
    def __init__(self):
        pass

    @staticmethod
    def check_session_valid(catch_handled_http_exceptions=None, restart_on_unauthorized=False):
        try:
            return good_status(session.get(config["request_url"]),
                               catch_handled_http_exceptions=catch_handled_http_exceptions,
                               restart_on_unauthorized=restart_on_unauthorized)
        except requests.exceptions.ConnectionError:
            return None

    @staticmethod
    def login(login_field: AdminLoginField, catch_handled_http_exceptions=None, restart_on_unauthorized=False):
        response = session.post(config["request_url"] + "login", json=login_field.model_dump())
        return good_status(response, catch_handled_http_exceptions=catch_handled_http_exceptions,
                           restart_on_unauthorized=restart_on_unauthorized) is True


class User:
    def __init__(self, data: RawUserData):
        self.data = data

    def set_saldo(self, transaction_details: TransactionField):
        data = transaction_details.model_dump()
        response = session.post(config["request_url"] + "add_transaction", params={"user_id": self.data.user_id},
                               json=data)
        print(transaction_details)
        response.raise_for_status()

        self.fetch_and_update_saldo()
        return True

    def fetch_saldo(self, catch_handled_http_exceptions=None) -> str | None:
        params = {"user_id": self.data.user_id}
        response = session.get(config["request_url"] + "get_saldo", params=params)
        print(response.content)
        # if good_status(response, catch_handled_http_exceptions=catch_handled_http_exceptions) is not True:
        #     return None

        return response.json()

    def fetch_saldo_after_transaction(self, transaction_id: int, catch_handled_http_exceptions=None) -> str | None:
        params = {"user_id": self.data.user_id, "transaction_id": transaction_id}
        response = session.get(config["request_url"] + "get_saldo_after_transaction", params=params)
        if good_status(response, catch_handled_http_exceptions=catch_handled_http_exceptions) is not True:
            return None

        return response.json()

    def fetch_and_update_saldo(self):
        new_saldo = self.fetch_saldo()
        if new_saldo is None:
            return None

        self.data.saldo = new_saldo
        return self.data.saldo

    def rename(self, new_username: str, catch_handled_http_exceptions=None) -> Optional[bool]:
        params = {"user_id": self.data.user_id, "new_username": new_username}
        response = session.put(config["request_url"] + "rename_user", params=params)
        if good_status(response, catch_handled_http_exceptions=catch_handled_http_exceptions) is not True:
            return False

        self.data.name = new_username
        return True

    # def refresh_data(self):
    #     new_data = self.get_userdata(user_id=self.data.user_id).data
    #     self.data = new_data

    @staticmethod
    def generate_transaction_object_list(raw_data: dict):
        return [RawTransactionData(**transaction) for transaction in raw_data]

    @staticmethod
    def get_user_exists_by_username(username: str, catch_handled_http_exceptions=None):
        response = session.get(config["request_url"] + "get_user_exists_by_username", params={"username": username})
        status = good_status(response, catch_handled_http_exceptions=catch_handled_http_exceptions)
        return status if status in [False, None] else response.json()

    @staticmethod
    def get_user_exists_by_id(user_id: int):
        return session.get(config["request_url"] + "get_user_exists_by_id", params={"user_id": user_id}).json()

    @staticmethod
    def add_user(userdata: UserSignupData, catch_handled_http_exceptions=None) -> bool | None:
        print(userdata.model_dump())
        response = session.post(config["request_url"] + "add_user", json=userdata.model_dump())
        status = good_status(response, catch_handled_http_exceptions=catch_handled_http_exceptions)
        if status is True:
            return True

        if response.status_code == 409:  # conflict met bestaande gebruiker
            return None
        else:
            return False

    @staticmethod
    def get_all_userdata():
        return session.get(config["request_url"] + "get_all_userdata").json()

    @classmethod
    def get_userdata(cls, user_id: int = None, username: str = None,
                     include_transactions=False, catch_handled_http_exceptions=None):

        if [user_id, username].count(None) != 1:
            raise ValueError("Minimaal EN maximaal één van de waarden `user_id` en `username` moeten ingevuld zijn.\n"
                             "Niet beide, niet niet beide niet.")

        params = {"user_id": user_id, "username": username, "include_transactions": include_transactions}

        response = session.get(config["request_url"] + "get_userdata", params=params)
        status = good_status(response, catch_handled_http_exceptions=catch_handled_http_exceptions)
        if not status:
            return status

        response_json = response.json()
        return {
            "userdata": cls(data=RawUserData(**response_json["raw_userdata"])),
            "transaction_list": cls.generate_transaction_object_list(response_json["transaction_list"])
        }

    @staticmethod
    def get_username_list(catch_handled_http_exceptions=None, restart_on_unauthorized=True):
        response = session.get(config["request_url"] + "get_username_list")
        return response.json() if good_status(response, restart_on_unauthorized=restart_on_unauthorized,
                                              catch_handled_http_exceptions=catch_handled_http_exceptions) is True \
            else ["Geen geldige verbinding"]

    @classmethod
    def get_transaction_list(cls, user_id: int, catch_handled_http_exceptions=None):
        response = session.get(config["request_url"] + "get_transaction_list", params={"user_id": user_id})
        if good_status(response, catch_handled_http_exceptions=catch_handled_http_exceptions) is not True:
            return False
        return cls.generate_transaction_object_list(response.json())

    # @staticmethod
    # def generate_transaction(current_money: float, transaction_details: TransactionField):
    #     params = {"current_money": current_money}
    #     return session.post(config["request_url"] + "generate_transaction",
    #                         params=params, json=transaction_details.model_dump()).json()

    @staticmethod
    def delete_user(user_id: int, catch_handled_http_exceptions=None) -> bool:
        response = session.delete(config["request_url"] + "delete_user", params={"user_id": user_id})
        status = good_status(response, catch_handled_http_exceptions=catch_handled_http_exceptions)
        return status if status in [False, None] else True
        # return True if good_status(response, catch_handled_http_exceptions=catch_handled_http_exceptions) is True else False


# todo: add to Camillib
def filter_list(search: str, seq: list[str], case_sensitive: bool = False, unicodify=True,
                order_alphabetically: bool = True) -> list:
    if order_alphabetically:
        seq.sort()

    if unicodify:
        seq = [unidecode(item) for item in seq]

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
