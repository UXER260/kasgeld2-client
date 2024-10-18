# client/main.py

import datetime
from typing import Union

import backend
import icon
from imports import *

with open('config.json', 'r') as f:
    config = json.load(f)

pysg.set_global_icon(icon.icon)


class UserSelectionWindow(Camillo_GUI_framework.Gui):
    def __init__(self, namelist: list[str] = None,
                 window_title="Kies een persoon", *args, **kwargs):
        self.namelist = namelist
        super().__init__(window_title=window_title, *args, **kwargs)

    def layout(self) -> list[list[pysg.Element]]:
        namelist = self.namelist if self.namelist is not None else [""]
        return [
            [pysg.InputText("", font=self.font, expand_x=True, key='-SEARCH_BAR_FIELD-',
                            enable_events=True), pysg.Button("👤", font=self.font)],
            [pysg.Listbox(namelist, font=self.font, expand_x=True, expand_y=True,
                          enable_events=True, key='-namelist-')],
            [pysg.Button("add", font=self.font, expand_x=True)]
        ]

    def update(self):
        if self.namelist is None:
            self.refresh(namelist_fetch=True)
        super().update()

        if self.event == '-SEARCH_BAR_FIELD-':  # if a letter is typed
            self.refresh(search_for_name=True)  # search feature

        elif self.event == '-namelist-' and self.values['-namelist-']:  # when clicked and list is not emtpy
            username = self.values['-namelist-'][0]
            data = backend.User.get_userdata(username=username, include_transactions=True)
            if data is None:
                pysg.popup(f"Gebruiker met naam '{username}' bestaat niet meer.", title="ERROR",
                           font=self.font, keep_on_top=True)
                self.refresh(namelist_fetch=True)
                return False

            # else...

            user = data["userdata"]
            transaction_list = data["transaction_list"]

            App.set_gui(
                gui=UserOverviewWindow(user=user, transaction_list=transaction_list)
            )
            return

        elif self.event == "add":
            search_bar_field = self.values["-SEARCH_BAR_FIELD-"]
            print(search_bar_field, self.namelist)
            filled_in_username = search_bar_field if search_bar_field and not self.window[
                "-namelist-"].get_list_values() else None
            App.set_gui(gui=AddUserMenu(filled_in_username=filled_in_username))

    def update_search_and_namelist(self, search_for_name: str, namelist: str):
        ...  # todo fixme

    # fixme fix scroll reset na TERUGKNOP gebruiken
    def refresh(self, search_for_name: Union[bool, str] = False, namelist_fetch=False):  # refresh usernamelist
        if search_for_name is True:
            search_for_name = self.values["-SEARCH_BAR_FIELD-"]
        elif type(search_for_name) is str:
            search_for_name = search_for_name
        else:
            search_for_name = None

        if namelist_fetch:
            new_namelist = backend.User.get_username_list()
        else:
            new_namelist = self.namelist

        # print("lists")
        # print(new_namelist)
        # print(self.namelist)
        namelist_changed = new_namelist != self.namelist
        self.namelist = new_namelist

        if search_for_name is not None or namelist_changed:
            print("search_for_name", f"'{search_for_name}'")
            if search_for_name is not None:
                self.window["-SEARCH_BAR_FIELD-"].update(search_for_name)
                self.window["-namelist-"].update(backend.filter_list(search=search_for_name, seq=self.namelist))
            elif namelist_changed:
                self.window["-namelist-"].update(self.namelist)

        # search_for_name = search_for_name if search_for_name else None
        # search_for_name = search_for_name if search_for_name is not None else self.values["-SEARCH_BAR_FIELD-"]
        #
        # if namelist_fetch:
        #     new_namelist = backend.User.get_usernamelist()
        # else:
        #     new_namelist = self.namelist
        #
        # print("aaaa", search_for_name)
        #
        # if len(new_namelist) != len(self.namelist) or namelist_fetch is False:
        #     print("Name list is ge-update")
        #     self.namelist = new_namelist
        #     if search_for_name:
        #         self.window["-namelist-"].update(backend.filter_list(search=search_for_name, seq=self.namelist))
        #         self.window["-SEARCH_BAR_FIELD-"].update(search_for_name)
        #     else:
        #         self.window["-namelist-"].update(self.namelist)

        # new_namelist = backend.User.get_usernamelist()
        # updated = set(new_namelist) - set(self.namelist)
        # print(updated)
        #
        # if self.values and self.values["-SEARCH_BAR_FIELD-"]:
        #     print("A")
        #     self.window['-namelist-'].update(backend.filter_list(self.values["-SEARCH_BAR_FIELD-"], self.namelist))
        #     self.window["-SEARCH_BAR_FIELD-"].update(search_for_name)
        #
        # else:
        #     print("B")
        #     self.window["-namelist-"].update(self.namelist)


class UserOverviewWindow(Camillo_GUI_framework.Gui):
    def __init__(self, user: backend.User, transaction_list: list[backend.RawTransactionData],
                 window_title=None, *args,
                 **kwargs):
        if window_title is None:
            window_title = f"Gebruikersoverzicht - {user.data.name}"
        self.user = user
        self.transaction_list = transaction_list
        self.transaction_preview_list = self.generate_transaction_previews()
        super().__init__(window_title=window_title, *args, **kwargs)

    def generate_transaction_previews(self):
        transaction_preview_list = []
        for transaction in self.transaction_list:
            date = datetime.date.fromtimestamp(transaction.transaction_timestamp)

            # titel + datum = transaction preview
            transaction_preview_list.append(
                f"€{transaction.amount} | {date.day}/{date.month}/{date.year} | {transaction.title}"
            )
        return backend.reverse(transaction_preview_list)

    def layout(self) -> list[list[pysg.Element]]:
        return [
            [pysg.Button(" < ", font=self.font, key="-BACK_BUTTON-"),
             pysg.Text(f"€{self.user.data.saldo}", font=self.font, justification="c", expand_x=True,
                       key="-SALDO-"),
             pysg.Button(" ⚙ ", font=self.font, key="-OPTIONS_BUTTON-")],
            [pysg.Listbox(self.transaction_preview_list, enable_events=True, expand_y=True, expand_x=True,
                          font=self.get_font(scale=0.7), key="-TRANSACTION_PREVIEW_LIST-")],
            [pysg.Button("Verander Saldo", font=self.font, expand_x=True, key="-SET_SALDO_BUTTON-")]]

    def update(self):
        super().update()

        if self.event == "-BACK_BUTTON-":
            App.back_button()
            assert isinstance(App.current_gui(), UserSelectionWindow)
            App.current_gui().refresh()
        elif self.event == pysg.WIN_CLOSE_ATTEMPTED_EVENT:
            # `App.back_button()`  is niet nodig omdat al is ge-called bij `App.update`
            assert isinstance(App.current_gui(), UserSelectionWindow)
            App.current_gui().refresh()

        elif self.event == '-TRANSACTION_PREVIEW_LIST-' and len(
                self.window['-TRANSACTION_PREVIEW_LIST-'].get_indexes()) >= 0:
            # get selected transaction

            if len(self.values['-TRANSACTION_PREVIEW_LIST-']) < 1:
                print("Transactie lijst leeg")
                return False

            transaction = self.transaction_list[-1 - self.window['-TRANSACTION_PREVIEW_LIST-'].get_indexes()[0]]
            App.set_gui(
                gui=TransActionDetailsWindow(transaction=transaction, user=self.user)
            )

        elif self.event == "-SET_SALDO_BUTTON-":
            App.set_gui(
                gui=SetSaldoMenu(user=self.user)
            )

        elif self.event == "-OPTIONS_BUTTON-":
            App.set_gui(OptionsMenu(user=self.user))

    def refresh(self, update_transaction_list=True):
        """
        Update het window met nieuwe gebruikers data
        :param update_transaction_list: Update `self.transaction_list` en `self.transaction_preview_list`
        met data van de server. Vervolgens: `self.window["-TRANSACTION_PREVIEW_LIST-"].update(data van server)`
        """

        self.update_window_title(new_title=f"Gebruikersoverzicht - {self.user.data.name}")

        self.window["-SALDO-"].update(f"€{self.user.data.saldo}")

        if update_transaction_list:
            self.transaction_list = backend.User.get_transaction_list(user_id=self.user.data.user_id)
            self.transaction_preview_list = self.generate_transaction_previews()
            self.window["-TRANSACTION_PREVIEW_LIST-"].update(self.transaction_preview_list)


class TransActionDetailsWindow(Camillo_GUI_framework.Gui):
    def __init__(self, transaction: backend.RawTransactionData, user: backend.User, window_title=None, *args,
                 **kwargs):
        self.transaction = transaction
        self.user = user
        super().__init__(window_title=window_title, *args, **kwargs)

    def update(self):
        super().update()

        if self.event == "-BACK_BUTTON-":
            App.back_button()

    def layout(self) -> list[list[pysg.Element]]:
        now = datetime.datetime.now()
        datetime_string = now.strftime('%d-%m-%Y %H:%M')
        return [
            [pysg.Button(" < ", font=self.font, key="-BACK_BUTTON-")],
            [pysg.Text(config['item_separation'][0] * config['item_separation'][1], justification="c",
                       expand_x=True,
                       font=self.font)],
            [pysg.Text('Datum & Tijd', font=self.get_font(scale=0.7)), pysg.Push(),
             pysg.Text(f"{datetime_string}", font=self.get_font(scale=0.7),
                       key="-TRANSACTION_DATE-TIME-")],
            [pysg.Text(config['item_separation'][0] * config['item_separation'][1], justification="c",
                       expand_x=True,
                       font=self.font)],
            [pysg.Text('Bedrag', font=self.get_font(scale=0.7)), pysg.Push(),
             pysg.Text(self.transaction.amount, font=self.get_font(scale=0.7), key="-AMOUNT-")],
            [pysg.Text(config['item_separation'][0] * config['item_separation'][1], justification="c",
                       expand_x=True,
                       font=self.font)],
            [pysg.Text('Saldo Na Transactie', font=self.get_font(scale=0.7)), pysg.Push(),
             pysg.Text(self.transaction.saldo_after_transaction, font=self.get_font(scale=0.7),
                       key="-SALDO_AFTER_TRANSACTION-")],
            [pysg.Text(config['item_separation'][0] * config['item_separation'][1], justification="c",
                       expand_x=True,
                       font=self.font)],
            [pysg.Text('Beschrijving', font=self.get_font(scale=0.7), justification="c", expand_x=True, )],
            [pysg.Multiline(self.transaction.description, font=self.get_font(scale=0.7), disabled=True,
                            expand_x=True,
                            size=(0, 7),
                            key="-TRANSACTION_DESCRIPTION-")],
        ]


class SetSaldoMenu(Camillo_GUI_framework.Gui):
    def __init__(self, user: backend.User, window_is_popup=False, window_title=None, window_dimensions=None,
                 *args, **kwargs):
        if window_title is None:
            window_title = f"Pas saldo aan - {user.data.name}"
        self.user = user
        super().__init__(window_title=window_title, window_is_popup=window_is_popup,
                         window_dimensions=window_dimensions, *args, **kwargs)

    def layout(self) -> list[list[pysg.Element]]:
        current_date = datetime.date.today().strftime('%d-%m-%Y')
        return [
            [pysg.Text(f"Bedrag*", font=self.font, expand_x=True, expand_y=True), pysg.Push(),
             pysg.DropDown(["-", "+", "op"], "-",
                           tooltip="Of ingevuld bedrag van saldo zal worden afgetrokken '-'(standaard),\nToegevoegd '+',\nof op dat het saldo gelijk aan het bedrag word gezet.",
                           readonly=True, font=self.font, key="-PLUS_MINUS-"),
             pysg.InputText("", font=self.font, size=(15, 0), key='-AMOUNT-')],
            [pysg.Text(f"Titel*", tooltip="Wordt als kop in de transactie lijst weergegeven. Houd deze zeer kort.",
                       font=self.font, expand_x=True, expand_y=True), pysg.Push(),
             pysg.InputText("", font=self.font, size=(15, 0), key="-TRANSACTION_TITLE-")],
            [pysg.Text(f"Aankoop datum", tooltip="Op welke datum deze aankoop is gedaan (JJJJ-MM-DD)", font=self.font,
                       expand_x=True, expand_y=True), pysg.Push(),
             pysg.InputText(current_date, font=self.font, size=(15, 0), key="-PURCHASE_DATE-")],
            [pysg.Text(f"Beschrijving*", tooltip="De beschrijving van van deze aankoop", font=self.font, expand_x=True,
                       expand_y=True)],
            [pysg.Multiline('', font=self.font, expand_x=True, expand_y=True, size=(0, 7),
                            key="-TRANSACTION_DESCRIPTION-")],
            [pysg.HorizontalSeparator()],
            [pysg.Text(f"* vereiste info", font=self.get_font(.7))],
            [pysg.Button("OK", expand_x=True, font=self.font, key="OK")]
        ]

        # return [
        #     [pysg.Text("Bedrag", font=self.font), pysg.Push(),
        #      pysg.DropDown(["-", "+", "op"], "-", readonly=True, font=self.font, key="-PLUS_MINUS-"),
        #      pysg.Text('€', font=self.font), pysg.InputText("", font=self.font, expand_x=True, key='-AMOUNT-')],
        #     [pysg.Text("Titel", font=self.font), pysg.Push(),
        #      pysg.InputText("", font=self.font, expand_x=True, key='-TRANSACTION_TITLE-')],
        #     [pysg.Text("Aankoop datum", font=self.font),
        #      pysg.Button("Selecteer", font=self.font, key="-PURCHASE_DATE_PICK_BUTTON-")],
        #     [pysg.Text("Beschrijving", font=self.font, expand_x=True)],
        #     [pysg.Multiline(font=self.font, expand_x=True, expand_y=True, size=(0, 7),
        #                     key="-TRANSACTION_DESCRIPTION-")],
        #     [pysg.Button("OK", expand_x=True, font=self.font, key="OK")]
        # ]
        #
        # col1 = pysg.Column([
        #     [pysg.Text("Bedrag", font=self.font),
        #      pysg.DropDown(["-", "+", "op"], "-", readonly=True, font=self.font, key="-PLUS_MINUS-",
        #                    tooltip="Of ingevuld bedrag van saldo zal worden afgetrokken '-'(standaard),\nToegevoegd '+',\nof op dat het saldo gelijk aan het bedrag word gezet.")],
        #     [pysg.Text("Titel", font=self.font)],
        #
        # ])
        #
        # col2 = pysg.Column([
        #     [pysg.InputText("", font=self.font, key='-AMOUNT-')],
        #     [pysg.InputText("", font=self.font, expand_x=True, key='-TRANSACTION_TITLE-')],
        # ])
        #
        # return [
        #     [col1, pysg.VerticalSeparator(), col2],
        #     [pysg.HorizontalSeparator()],
        #     [pysg.Text("Beschrijving", font=self.font, expand_x=True)],
        #     [pysg.Multiline(font=self.font, expand_x=True, expand_y=True, size=(0, 7),
        #                     key="-TRANSACTION_DESCRIPTION-")],
        # ]

    def update(self):  # todo match toegevoegde input boxes
        super().update()

        if self.event == "OK":
            if not all(self.values.values()):
                pysg.popup("Vul alle velden in", title="ERROR",
                           font=self.font, keep_on_top=True)
                return

            amount = backend.check_string_valid_float(self.values["-AMOUNT-"])
            if not backend.check_valid_saldo(amount):
                return

            operation = self.values["-PLUS_MINUS-"]  # of je saldo +bedrag, -bedrag of op bedrag wilt zetten
            if operation == "-":
                saldo_after_transaction = self.user.data.saldo - amount
            elif operation == "+":
                saldo_after_transaction = self.user.data.saldo + amount
            else:
                saldo_after_transaction = amount

            transaction_title = self.values["-TRANSACTION_TITLE-"]
            transaction_description = self.values["-TRANSACTION_DESCRIPTION-"]
            purchase_date = (self.values["-PURCHASE_DATE-"])

            transaction_details = backend.TransactionField(
                saldo_after_transaction=saldo_after_transaction,
                title=transaction_title,
                description=transaction_description,
                purchase_date=purchase_date,
            )

            self.user.set_saldo(transaction_details=transaction_details)
            App.back_button()
            # `type(App.current_gui())` MOET `UserOverviewWindow` zijn
            assert isinstance(App.current_gui(), UserOverviewWindow)
            App.current_gui().refresh()  # `current_gui` is veranderd door `back_button`


class AddUserMenu(Camillo_GUI_framework.Gui):
    Camillo_GUI_framework.Gui.default_window_init_args["resizable"] = False

    def __init__(self, window_title: str = "Voeg Gebruiker Toe",
                 filled_in_username=None, window_dimensions=(None, None),
                 *args, **kwargs):
        print(window_dimensions)
        if filled_in_username is None:
            filled_in_username = ''
        self.filled_in_username = filled_in_username
        print("filled_in_username", filled_in_username)
        super().__init__(window_title=window_title, window_dimensions=window_dimensions, *args, **kwargs)

    def layout(self) -> list[list[pysg.Element]]:
        current_date = datetime.date.today().strftime('%d-%m-%Y')

        return [
            [pysg.Text(f"Naam*", font=self.font, expand_x=True, expand_y=True), pysg.Push(),
             pysg.InputText(self.filled_in_username, font=self.font, size=(15, 0), key='-ACCOUNT_NAME-')],
            [pysg.Text(f"Saldo*", font=self.font, expand_x=True, expand_y=True), pysg.Push(),
             pysg.InputText("", font=self.font, size=(15, 0), key='-SALDO-')],
            [pysg.Text(f"Aanmelddatum", tooltip="Sinds wanneer deze leerling leerling op DVR is", font=self.font,
                       expand_x=True, expand_y=True), pysg.Push(),
             pysg.InputText(current_date, font=self.font, size=(15, 0), key="-SIGNUP_DATE-")],
            [pysg.Text(f"Berekendatum",
                       tooltip="Vanaf welk moment het kasgeld is berekend.\n"
                               "(Wanneer leeg gelijk aan aanmelddatum)",
                       font=self.font, expand_x=True, expand_y=True), pysg.Push(),
             pysg.InputText('', font=self.font, size=(15, 0), key="-CALCULATION_START_DATE-")],
            [pysg.HorizontalSeparator()],
            [pysg.Text(f"* vereiste info", font=self.get_font(.7))],
            [pysg.Button("OK", expand_x=True, font=self.font, key="OK")]
        ]

    def update(self):
        super().update()

        if self.event == "OK":
            # voor checken of account name en saldo zijn waardes zijn ingevuld
            values = [key for key in self.values.keys() if self.values[key]]
            if not {"-ACCOUNT_NAME-", "-SALDO-"}.issubset(set(values)):
                return None

            username: str = self.values["-ACCOUNT_NAME-"]
            username = username.capitalize()
            saldo = self.values["-SALDO-"]
            if not backend.check_string_valid_float(saldo):
                return
            if not backend.check_valid_saldo(saldo):
                return

            signup_timestamp = None

            if self.values["-SIGNUP_DATE-"]:
                signup_timestamp = datetime.datetime.strptime(self.values["-SIGNUP_DATE-"], "%d-%m-%Y").timestamp()

            calculation_start_timestamp = None
            if self.values["-CALCULATION_START_DATE-"]:
                calculation_start_timestamp = datetime.datetime.strptime(self.values["-CALCULATION_START_DATE-"], "%d-%m-%Y").timestamp()

            user = backend.AddUser(
                name=username,
                saldo=saldo,
                signup_timestamp=signup_timestamp,
                last_update_timestamp=calculation_start_timestamp

            )
            result = backend.User.add_user(userdata=user)
            if result is None:  # gebruiker bestaat al
                pysg.popup(f"Gebruiker met naam '{username}' bestaat al.\n"
                           f"Kies een andere naam.", title="Gebruiker bestaat al", font=self.font,
                           keep_on_top=True)
                return

            App.back_button()
            assert isinstance(App.current_gui(), UserSelectionWindow)
            App.current_gui().refresh(search_for_name=user.name, namelist_fetch=True)


class OptionsMenu(Camillo_GUI_framework.Gui):
    def __init__(self, user: backend.User, window_is_popup=True, window_dimensions=(None, None),
                 window_title=None,
                 *args, **kwargs):
        if window_title is None:
            window_title = f"Opties - {user.data.name}"
        self.user = user
        super().__init__(window_is_popup=window_is_popup, window_dimensions=window_dimensions,
                         window_title=window_title, *args,
                         **kwargs)

    def layout(self) -> list[list[pysg.Element]]:
        return [
            [pysg.Button("Hernoem", font=self.font, size=(9, 0), key='-RENAME_BUTTON-')],
            [pysg.Button("Verwijder", font=self.font, size=(9, 0), key='-DELETE_BUTTON-')],
        ]

    def update(self):
        super().update()

        if self.event == "-RENAME_BUTTON-":
            self.window.hide()
            new_username = pysg.popup_get_text("Voor nieuwe gebruikersnaam is:", font=self.font,
                                               keep_on_top=True)
            if not new_username:  # fixme
                self.window.un_hide()
                return

            if backend.User.get_user_exists_by_username(username=new_username) is True:
                pysg.popup(f"Gebruiker met naam '{new_username}' bestaat al.\n"
                           f"Kies een andere naam.", title="Gebruiker bestaat al", font=self.font, keep_on_top=True)
                self.window.un_hide()
                return False

            if not self.user.rename(new_username=new_username):
                pysg.popup(f"Gebruiker met de naam '{self.user.data.name}' bestaat niet meer.",
                           title="Gebruiker bestaat niet meer", font=self.font, keep_on_top=True)
            # het is niet meer nodig om nu het window weer tevoorschijn te halen omdat het toch wordt gesloten
            App.back_button()
            assert isinstance(App.current_gui(), UserOverviewWindow)
            App.current_gui().refresh()
            return True

        elif self.event == "-DELETE_BUTTON-":
            self.window.hide()
            delete_user = pysg.popup_yes_no(
                f"Weet je zeker dat je het account `{self.user.data.name}` wilt verwijderen?\n"
                f"Dit kan niet ongedaan worden gemaakt.", title="Verwijder Gebruiker",
                font=self.font, keep_on_top=True)
            if delete_user != "Yes":
                self.window.un_hide()
                return

            if backend.User.delete_user(user_id=self.user.data.user_id) is False:
                pysg.popup(f"Gebruiker met naam '{delete_user}' bestaat niet.\n", title="Gebruiker bestaat niet",
                           font=self.font, keep_on_top=True)
                self.window.un_hide()
                return False

            # het is niet meer nodig om nu het window weer tevoorschijn te halen omdat het toch wordt gesloten

            App.reset_app()
            return True


App = backend.App
App.place_start_gui(UserSelectionWindow)
App.run()
