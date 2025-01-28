# client/backend.py
# Bevat alle functies voor communicatie met server
from __future__ import annotations

# Gebaseerd op ~/PycharmProjects/PythonProjects/BankKasGeldSchool/api/client/old4_fail/bank.py


import copy
import time
import traceback
from pathlib import Path
from typing import Union
from unidecode import unidecode
import PySimpleGUI as pysg
import Camillo_GUI_framework
import requests

import system
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
                pysg.popup_quick("Gegevens komen niet overeen", auto_close_duration=1, non_blocking=True,
                                 no_titlebar=True, background_color="red", title="Fout", font=self.font,
                                 keep_on_top=True)
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
        System.check_updates(note_no_updates=False)
        # als nieuwe update beschikbaar en gedownload was,
        # dan zal dit programma nu herstarten en alle code hieronder niet meer worden ge-execute

        valid_session = Admin.check_session_valid()
        if valid_session is False:
            if cls.login_prompt(restart_on_success=False) is False:
                return False

        # als het None is dan niet inloggen, maar direct naar kies menu waar gebruiker wordt verteld dat geen connectie
        # todo check of deze comment nog actueel is
        super().on_run()

    @classmethod
    def error_handler(cls, error: Exception):
        if not isinstance(error, Exception):
            return

        if isinstance(error, requests.exceptions.ConnectionError):
            pysg.Popup(
                "Verbinding niet (meer) beschikbaar.\n"
                "Zorg ervoor dat je verbonden bent met het WiFi netwerk 'De Vrije Ruimte'\n\n"
                "Check je connectie en probeer het opnieuw.", title="Geen verbinding""",
                keep_on_top=True,
                font=config["font"])
            return

        System.report_crash()

        if isinstance(error, requests.exceptions.HTTPError):
            print(error.response.content)
            print(error.response.status_code)
            status_code = error.response.status_code

            error_specification = "in de server" if status_code == 500 else "bij het communiceren met de server"
            error_title = "Fout in server bij handeling" if status_code == 500 else \
                "Communicatiefout met server bij handeling"

            pysg.Popup(
                f"⚠Een onverwachte fout trad op {error_specification}, waardoor het verzoek niet kon worden voldaan.\n"
                "Neem AUB contact op met Camillo.\n\n"
                f"Fout: {error.response.reason}\n"
                f"Type: {error.__class__.__name__}""",
                title=error_title,
                text_color="red", keep_on_top=True,
                font=config["font"]
            )

        else:
            pysg.Popup(
                f"⚠Er is een programmafout opgetreden.\n"
                f"Neem contact op met Camillo\n\n"
                f"Type: {error.__class__.__name__}\n"
                f"Beschrijving:\n{str(error)}",
                title=f"Onbekende programmafout", text_color="red", keep_on_top=True, font=config["font"]
            )

    @classmethod
    def run(cls):
        cls.on_run()

        while cls.active:
            if not config["use_global_exception_handler"]:
                cls.update()
                continue

            try:
                cls.update()
            except Exception as e:
                cls.error_handler(e)


def restart_program():
    python = sys.executable
    os.execv(python, [python] + sys.argv)


class Session(requests.Session):
    def request(self, *args, **kwargs):
        # print("REQUEST", *args)
        response = super().request(*args, **kwargs)
        cookies = requests.utils.dict_from_cookiejar(session.cookies)  # turn cookiejar into dict
        Path(config["cookiejar_location"]).write_text(json.dumps(cookies))  # save them to file as JSON
        return response


session = Session()

cookie_jar = load_config(path=config["cookiejar_location"], except_decode_error=True, fallback_restore="{}")
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
        response.raise_for_status()

        return response.json()

    def fetch_saldo_after_transaction(self, transaction_id: int, catch_handled_http_exceptions=None):
        params = {"user_id": self.data.user_id, "transaction_id": transaction_id}
        response = session.get(config["request_url"] + "get_saldo_after_transaction", params=params)
        response.raise_for_status()
        response.json()

    def fetch_and_update_saldo(self):
        new_saldo = self.fetch_saldo()
        if new_saldo is None:
            return None

        self.data.saldo = new_saldo
        return self.data.saldo

    def rename(self, new_username: str, catch_handled_http_exceptions=None) -> Optional[bool]:
        params = {"user_id": self.data.user_id, "new_username": new_username}
        response = session.put(config["request_url"] + "rename_user", params=params)
        status = good_status(response, catch_handled_http_exceptions=catch_handled_http_exceptions)
        # todo gebruik deze logica meer in code
        if status is True:
            self.data.name = new_username
            return True
        return status

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
            raise ValueError(
                "Alleen één van de velden 'user_id' en 'username' invullen, niet beide en niet geen van beide")

        params = {"user_id": user_id, "username": username, "include_transactions": include_transactions}
        # print(params)

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
        response.raise_for_status()
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
        # return True if good_status(
        # response, catch_handled_http_exceptions=catch_handled_http_exceptions) is True else False


class System:
    @classmethod
    def check_updates(cls, note_no_updates=True):  # todo implementeer knop in instellingen GUI
        pysg.popup_no_buttons(
            "Op updates controleren ...",
            font=get_font(scale=0.75),
            title="Controleren op updates ...",
            auto_close=True, auto_close_duration=1,
            non_blocking=True)

        current_version = system.get_current_version_number()
        new_version = system.check_update_available(return_newest_version_number=True)
        if not new_version:
            if not note_no_updates:
                return False
            pysg.popup_ok(
                "Programma is up-to-date.\n"
                f"Huidige versie: v{current_version}\n"
                "Informatie over huidige update:\n"
                "<nog niet geïmplementeerd>\n"
                "Camillo\n\n",
                font=get_font(scale=0.75),
                title="Geen updates beschikbaar",
                keep_on_top=True)
            return False

        pysg.popup_ok(
            "Updates staan klaar.\n"
            f"Huidige versie: v{current_version}\n"
            f"Nieuwe versie: v{new_version}\n\n"
            "Informatie over update:\n"
            "<nog niet geïmplementeerd>\n"
            "Camillo\n\n"
            "installatie starten",
            font=get_font(scale=0.75),
            title="Updates beschikbaar",
            keep_on_top=True)

        pysg.popup_no_buttons(
            "Updates installeren ...",
            font=get_font(scale=0.75),
            auto_close=True, auto_close_duration=1,
            non_blocking=True)

        merge_latest_update_success = system.merge_latest_repo(fetch=True)
        if not merge_latest_update_success:
            pysg.popup_ok(
                "Er was een probleem bij het toepassen van de update.\n"
                "Probeer het later opnieuw.",
                font=get_font(scale=0.75),
                title="Bijwerken niet voltooid",
                keep_on_top=True)
            return False

        print(current_version, new_version, new_version != current_version)  # debug todo
        pysg.popup_no_buttons(
            "Updates geïnstalleerd.\n"
            f"Bijgewerk naar versie: v{new_version}\n\n"
            "Programma herstart over 2 seconden ...",
            font=get_font(scale=0.75),
            title="Bijwerken voltooid", non_blocking=False, auto_close=True,
            auto_close_duration=2)

        restart_program()

    @classmethod
    def report_crash(cls, description: str | None = None):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        # program_data = {"globals": globals(), "locals": locals()}
        crash_report = {
            'description': description,
            'timestamp': int(time.time()),
            'filename': exc_traceback.tb_frame.f_code.co_filename,
            'lineno': exc_traceback.tb_lineno,
            'name': exc_traceback.tb_frame.f_code.co_name,
            'type': exc_type.__name__,
            'message': str(exc_value),
            'traceback': traceback.format_exc().replace(os.getcwd(), "<WORKING_DIR>")
            # 'program_data': program_data
        }
        success = System.send_crashreport(crash_report=crash_report)
        if not success:
            pysg.Popup(
                "Crash reportage kon niet worden verzonden",
                title="Crash reportage is niet verzonden",
                keep_on_top=True,
                font=config["font"])
            return False
        return True

    @classmethod
    def send_crashreport(cls, crash_report):
        response = session.post(config["request_url"] + "report_crash",
                                json=crash_report)
        response.raise_for_status()
        return response.status_code == 200


# todo: add to Camillib
def filter_list(search: str, seq: list[str], unicodify=True,
                order_alphabetically: bool = True) -> list:
    if order_alphabetically:
        seq.sort()

    result = []
    for item in seq:
        search_, item_ = unidecode(search).casefold(), unidecode(item).casefold()
        # str.casefold() = Berend -> berend
        if item == search:
            result.insert(0, item)
        elif (search in item) if not unicodify else (search_ in item_):
            # unidecode() = Lóa -> Loa
            result.append(item)
    # unidecode() + str.casefold() = Daniël -> daniel
    return result


def reverse(seq):  # todo: replace with build in function
    t = copy.deepcopy(seq)
    t.reverse()
    return t


def overwrite_dict_with_dict(original_dict: dict, overwriter_dict):
    for key, value in overwriter_dict.items():
        original_dict[key] = value
    return original_dict


# def on_exit(message=None) -> None:
#     if message is None:
#         sys.exit(0)
#     else:
#         sys.exit(str(message))


def handle_http_exception(func):
    def wrapper(*args, **kwargs):
        output = func(*args, **kwargs)

        ...

        return output

    return wrapper
