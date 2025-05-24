# client/Camillo_GUI_framework
# Zelf gemaakt framework voor user interface
from typing import Optional, Union

import backend
from imports import *

pysg.theme(config["theme"])


class App:
    start_gui: type["Gui"] = None
    default_start_gui_init_kwargs = None
    active = True
    guis: list["Gui"] = []

    @classmethod
    def delete_gui(cls, index: int):
        cls.guis[index].window.close()
        del cls.guis[index]

    @classmethod
    def clear_all_guis(cls, skip_current_gui=False):
        len_ = max(0, len(cls.guis) - 1 if skip_current_gui is True else 0)
        for _ in range(len_):
            cls.delete_gui(index=0)

    @classmethod
    def reset_app(cls, restart=False, start_gui_init_kwargs: Optional[dict] = None) -> None:
        """
        App herstart als cls.start_gui None is of als param restart True is,
        anders sluit alle Guis en opent cls.start_gui
        :param start_gui_init_kwargs: start_gui.__init__(**start_gui_init_kwargs).
        Zal gelijk aan cls.default_start_gui_init_args wanneer None
        :type start_gui_init_kwargs: dict
        :param restart: Of app moet herstarten
        :type restart: bool
        :return: None
        :rtype: None
        """

        if cls.start_gui is not None or restart is True:
            cls.set_start_gui(start_gui_init_kwargs=start_gui_init_kwargs)
            cls.clear_all_guis(skip_current_gui=True)
        else:
            python = sys.executable
            os.execv(python, [python] + sys.argv)

    @classmethod
    def place_start_gui(cls, start_gui: type["Gui"], start_gui_init_kwargs: Optional[dict] = None) -> None:
        """
        :param start_gui: start_gui zal starten nadat in `Gui.update()` self.current_gui None is
        én wanneer App.restart_app() waar param restart False is
        :type start_gui: type[Gui]
        :param start_gui_init_kwargs: start_gui.__init__(**start_gui_init_kwargs).
        :type start_gui_init_kwargs:
        :return: None
        :rtype: None
        """
        assert not isinstance(start_gui, Gui), ValueError(
            "start_gui mag niet een instance zijn van Gui. Alleen een type.")

        if start_gui_init_kwargs is None:
            start_gui_init_kwargs = {}

        cls.start_gui = start_gui
        cls.default_start_gui_init_kwargs = start_gui_init_kwargs

    @classmethod
    def set_start_gui(cls, start_gui_init_kwargs: Optional[dict] = None):
        if start_gui_init_kwargs is None and cls.default_start_gui_init_kwargs is not None:
            start_gui_init_kwargs = cls.default_start_gui_init_kwargs
        elif start_gui_init_kwargs is None:
            start_gui_init_kwargs = {}

        cls.set_gui(cls.start_gui(**start_gui_init_kwargs))

    @classmethod
    def current_gui(cls):
        if len(cls.guis) > 0:
            return cls.guis[-1]
        return None

    @classmethod
    def previous_gui(cls):
        return cls.guis[-2]

    @classmethod
    def set_gui(cls, gui: "Gui"):
        """
        :param gui: A class that inherited from the `Gui` class
        """

        cls.guis.append(gui)
        cls.current_gui().menu = cls

    @classmethod
    def calculate_new_window_pos(cls, gui_old: "Gui", gui_new: "Gui"):
        new_pos_x = int(
            gui_old.window.current_location(more_accurate=True)[0] + gui_old.window.size[0] / 2 - gui_new.window.size[
                0] / 2)
        new_pos_y = int(
            gui_old.window.current_location(more_accurate=True)[1] + gui_old.window.size[1] / 2 - gui_new.window.size[
                1] / 2)
        return new_pos_x, new_pos_y

    @classmethod
    # prompt
    def exit_prompt(cls):
        exit_program = pysg.popup_yes_no("Afsluiten?", title="", keep_on_top=True, font=backend.get_font())
        if exit_program == "Yes":
            cls.active = False
            # backend.sys.exit(0)
        print("gebruiker wilde niet afsluiten")
        return False

    @classmethod
    def back_button(cls, refresh=False, *refresh_args, **refresh_kwargs):  # fixme verplaats naar `Gui` class
        # gaat een gui terug in de `guis` lijst en verwijdert de vorige gui uit de list
        # werkt alleen als oude window niet was gesloten
        if len(cls.guis) <= 1:
            cls.exit_prompt()
            return False

        window_root = cls.current_gui().window.TKroot
        window_root.unbind('<FocusIn>')
        window_root.unbind('<FocusOut>')

        if not cls.current_gui().window_is_popup:
            new_pos_x, new_pos_y = cls.calculate_new_window_pos(gui_new=cls.previous_gui(), gui_old=cls.current_gui())
            cls.previous_gui().window.move(new_pos_x, new_pos_y)

        cls.previous_gui().window.un_hide()  # un-hide voor het geval dat de window was ge-hide
        cls.delete_gui(-1)  # wat eerst `cls.previous_gui()` was, is nu dezelfde als `cls.current_gui()`

        if refresh is True:
            cls.current_gui().refresh(*refresh_args, **refresh_kwargs)

    @classmethod
    def update(cls):
        if not cls.guis:
            cls.active = False
        cls.current_gui().update()

    @classmethod
    def on_run(cls):
        if not cls.start_gui:
            assert cls.current_gui() is not None, \
                "Make sure either `App.current_gui` or `App.start_gui` is properly set before running."
        if cls.current_gui() is None:
            cls.set_start_gui()
        cls.active = True

    @classmethod
    def run(cls):
        cls.on_run()
        while cls.active is True:
            cls.update()


class Gui:
    default_window_init_args = {"finalize": True, "enable_close_attempted_event": True, "resizable": True}

    def __init__(self, window_title="No Title", font=None,
                 window_dimensions=None, keep_on_top=None,
                 window_is_popup=False,
                 window_init_args_overwrite: dict = None):

        self.focused = True
        self.window_is_popup = window_is_popup
        if keep_on_top is None and window_is_popup:
            keep_on_top = True
        elif keep_on_top is True:
            keep_on_top = True
        self.keep_on_top = keep_on_top
        if window_init_args_overwrite is None:
            window_init_args_overwrite = {}
        self.overwritten_window_args = backend.overwrite_dict_with_dict(
            original_dict=self.default_window_init_args.copy(),
            overwriter_dict=window_init_args_overwrite
        )

        if window_dimensions is None:
            window_dimensions = config["window_size"]
        if font is None:
            font = backend.get_font()

        self.window: Optional[pysg.Window] = None
        self.menu: Optional[App] = None

        self.window_title = window_title
        self.window_dimensions = window_dimensions
        self.font = font

        self.event = None
        self.values = None

        self.set_window(old_gui=App.current_gui() if App.current_gui() else None)

    def update_window_title(self, new_title: str):
        self.window.set_title(title=new_title)
        self.window_title = new_title

    def get_font(self, scale: Union[float, int] = 1):
        """
        Zonder argumenten identiek aan `backend.get_font()`
        """
        return backend.get_font(scale=scale, font=self.font)

    def layout(self) -> list[list[pysg.Element]]:
        return [
            [pysg.InputText(self.window_title, font=self.font, enable_events=True)]
        ]

    def set_window(self, old_gui, close_old_window: bool = False):
        layout = self.layout()

        if old_gui is not None:
            if self.window_dimensions == (None, None):
                self.window = pysg.Window(keep_on_top=self.keep_on_top, title=self.window_title,
                                          size=self.window_dimensions,
                                          layout=self.layout(),
                                          **self.overwritten_window_args)
                self.window.hide()

                new_pos_x, new_pos_y = App.calculate_new_window_pos(gui_new=self, gui_old=old_gui)

                self.window.move(new_pos_x, new_pos_y)
                self.window.un_hide()

            else:
                new_pos_x = int(old_gui.window.current_location(more_accurate=True)[0] +
                                old_gui.window.size[0] / 2 - self.window_dimensions[0] / 2)
                new_pos_y = int(old_gui.window.current_location(more_accurate=True)[1] +
                                old_gui.window.size[1] / 2 - self.window_dimensions[1] / 2)

                self.window = pysg.Window(title=self.window_title, size=self.window_dimensions,
                                          location=(new_pos_x, new_pos_y), layout=self.layout(),
                                          **self.overwritten_window_args)

            if not self.window_is_popup:
                if close_old_window:
                    old_gui.window.close()
                else:
                    old_gui.window.hide()

        else:
            self.window = pysg.Window(title=self.window_title, size=self.window_dimensions, layout=layout,
                                      **self.overwritten_window_args)

        # window_root = self.window.TKroot
        # window_root.bind('<FocusIn>', self.__on_focused_in)
        # window_root.bind('<FocusOut>', self.__on_focused_out)

    def __on_focused_in(self, *_):
        if not self.focused:
            self.focused = True
            # print("focus", self.focused, self.__class__.__name__)

    def __on_focused_out(self, *_):
        if self.focused:
            self.focused = False
            # print("focus", self.focused, self.__class__.__name__)

    def refresh(self, *args, **kwargs):  # kan worden gebruikt om elementen in window te refreshen
        pass

    def update(self):
        self.event, self.values = self.window.read()
        if self.event == pysg.WIN_CLOSE_ATTEMPTED_EVENT:
            self.on_close()
            self.menu.back_button()

        return self.event, self.values

    def on_close(self):
        pass
