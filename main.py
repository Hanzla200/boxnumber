"""Number-base 2048 for desktop and Android."""

from random import choice, random

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.utils import platform


BG = (0.075, 0.09, 0.12, 1)
PANEL = (0.12, 0.14, 0.18, 1)
EMPTY = (0.17, 0.19, 0.22, 1)
TEXT = (0.96, 0.97, 0.95, 1)
MUTED = (0.65, 0.69, 0.71, 1)
ACCENT = (0.43, 0.79, 0.62, 1)
TILE_COLORS = [
    (0.88, 0.78, 0.60, 1), (0.84, 0.67, 0.45, 1),
    (0.86, 0.56, 0.38, 1), (0.83, 0.43, 0.34, 1),
    (0.73, 0.38, 0.47, 1), (0.57, 0.39, 0.61, 1),
    (0.39, 0.48, 0.67, 1), (0.31, 0.60, 0.66, 1),
    (0.32, 0.67, 0.55, 1), (0.58, 0.72, 0.35, 1),
]


class Surface(BoxLayout):
    def __init__(self, color=PANEL, radius=dp(14), **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.01, 0.018, 0.03, 0.3)
            self._shadow = RoundedRectangle(pos=self.pos, size=self.size,
                                            radius=[radius + dp(2)])
            Color(*color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self._shadow.pos = (self.x, self.y - dp(2))
        self._shadow.size = self.size
        self._rect.pos = self.pos
        self._rect.size = self.size


class TileButton(Button):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = TEXT
        self.bold = True
        self.font_size = sp(24)
        with self.canvas.before:
            Color(0, 0, 0, 0.24)
            self.shadow = RoundedRectangle(radius=[dp(10)])
            self.surface_color = Color(*EMPTY)
            self.surface = RoundedRectangle(radius=[dp(10)])
        self.bind(pos=self._sync_surface, size=self._sync_surface,
                  background_color=self._set_surface_color)

    def _sync_surface(self, *_):
        self.shadow.pos = (self.x, self.y - dp(2))
        self.shadow.size = self.size
        self.surface.pos = self.pos
        self.surface.size = self.size

    def _set_surface_color(self, _instance, color):
        self.surface_color.rgba = color

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.ud["2048_start"] = touch.pos
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        start = touch.ud.pop("2048_start", None)
        if start:
            dx = touch.x - start[0]
            dy = touch.y - start[1]
            if max(abs(dx), abs(dy)) > dp(28):
                self.state = "normal"
                if abs(dx) > abs(dy):
                    self.game.move("right" if dx > 0 else "left")
                else:
                    self.game.move("up" if dy > 0 else "down")
                return True
        return super().on_touch_up(touch)


class SquareBoard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grid = GridLayout(cols=4, rows=4, spacing=dp(8), padding=dp(8),
                               size_hint=(None, None))
        self.add_widget(self.grid)
        self.bind(pos=self._fit, size=self._fit)

    def _fit(self, *_):
        side = min(self.width, self.height, dp(560))
        self.grid.size = (side, side)
        self.grid.center = self.center


class GameScreen(BoxLayout):
    def __init__(self, game, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(10),
                         padding=[dp(14), dp(12), dp(14),
                                  dp(68) if platform == "android" else dp(10)], **kwargs)
        self.game = game

        header = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        heading = BoxLayout(orientation="vertical")
        heading.add_widget(Label(text="2048 - YOUR RULES", color=TEXT, bold=True,
                                 font_size=sp(16), halign="left"))
        heading.add_widget(Label(text="MERGE THE NUMBER YOU CHOOSE", color=MUTED,
                                 font_size=sp(9), halign="left"))
        header.add_widget(heading)
        new_button = self.action_button("NEW GAME", ACCENT, (0.06, 0.13, 0.10, 1))
        new_button.size_hint = (None, None)
        new_button.size = (dp(104), dp(42))
        new_button.bind(on_release=lambda *_: self.game.confirm_action(
            "Start a new game?", "Your current board will be cleared.",
            lambda: self.game.new_game(self.selected_base)))
        header.add_widget(new_button)
        exit_button = self.action_button("EXIT", PANEL, TEXT)
        exit_button.size_hint = (None, None)
        exit_button.size = (dp(58), dp(42))
        exit_button.bind(on_release=lambda *_: self.game.confirm_action(
            "Exit 2048?", "Your current board will be closed.", self.game.request_app_exit))
        header.add_widget(exit_button)
        help_button = self.action_button("?", PANEL, TEXT)
        help_button.size_hint = (None, None)
        help_button.size = (dp(38), dp(42))
        help_button.bind(on_release=lambda *_: self.game.show_help())
        header.add_widget(help_button)
        self.add_widget(header)

        self.selected_base = 2
        number_row = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(4))
        number_row.add_widget(Label(text="START TILE", color=MUTED, bold=True,
                                    font_size=sp(9), size_hint_x=None, width=dp(62)))
        self.base_buttons = {}
        for number in range(1, 10):
            button = self.action_button(str(number), PANEL, TEXT)
            button.size_hint = (1, 1)
            button.bind(on_release=lambda _button, n=number: self.choose_base(n))
            self.base_buttons[number] = button
            number_row.add_widget(button)
        self.add_widget(number_row)

        stats = BoxLayout(size_hint_y=None, height=dp(72), spacing=dp(8))
        self.score_text = self.stat_panel(stats, "SCORE", "0")
        self.best_text = self.stat_panel(stats, "BEST", "0")
        self.goal_text = self.stat_panel(stats, "TARGET", "2048")
        self.add_widget(stats)

        self.status = Label(text="Swipe or use arrow keys", color=TEXT, font_size=sp(14),
                            bold=True, size_hint_y=None, height=dp(24))
        self.add_widget(self.status)

        board_area = BoxLayout(size_hint_y=1)
        self.board_surface = Surface(size_hint=(1, 1), color=PANEL, radius=dp(18))
        self.board = SquareBoard()
        self.board_surface.add_widget(self.board)
        board_area.add_widget(self.board_surface)
        self.add_widget(board_area)

        footer = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        if platform == "android":
            footer.add_widget(Widget())
            for symbol, direction in (("↑", "up"), ("←", "left"),
                                      ("↓", "down"), ("→", "right")):
                move_button = self.action_button(symbol, PANEL, TEXT)
                move_button.size_hint = (None, None)
                move_button.size = (dp(38), dp(38))
                move_button.font_size = sp(19)
                move_button.bind(on_release=lambda _button, move=direction:
                                 self.game.move(move))
                footer.add_widget(move_button)
        else:
            self.rule_text = Label(text="Arrow keys or WASD to move", color=MUTED,
                                   font_size=sp(11), halign="left")
            footer.add_widget(self.rule_text)
        undo = self.action_button("UNDO", PANEL, TEXT)
        undo.size_hint = (None, None)
        undo.width = dp(62) if platform == "android" else dp(72)
        undo.bind(on_release=lambda *_: self.game.undo())
        self.undo_button = undo
        footer.add_widget(undo)
        self.add_widget(footer)

        self._build_tiles()

    @staticmethod
    def action_button(text, background, foreground):
        button = Button(text=text, size_hint_y=None, height=dp(40), bold=True,
                        font_size=sp(12), color=foreground, background_normal="",
                        background_down="", background_color=(0, 0, 0, 0))
        with button.canvas.before:
            Color(0.01, 0.018, 0.03, 0.3)
            button._shadow = RoundedRectangle(radius=[dp(10)])
            button._face_color = Color(*background)
            button._face = RoundedRectangle(radius=[dp(10)])
        def sync(widget, *_):
            widget._shadow.pos = (widget.x, widget.y - dp(2))
            widget._shadow.size = widget.size
            widget._face.pos = widget.pos
            widget._face.size = widget.size

        def paint(widget, color):
            widget._face_color.rgba = color

        button.bind(pos=sync, size=sync, background_color=paint)
        sync(button)
        return button

    @staticmethod
    def stat_panel(parent, caption, value):
        panel = Surface(orientation="vertical", padding=dp(5), spacing=0)
        panel.add_widget(Label(text=caption, color=MUTED, font_size=sp(9), bold=True))
        label = Label(text=value, color=TEXT, font_size=sp(19), bold=True)
        panel.add_widget(label)
        parent.add_widget(panel)
        return label

    def _build_tiles(self):
        self.tile_buttons = []
        for index in range(16):
            tile = TileButton(self.game, background_color=EMPTY)
            tile.bind(on_release=lambda _button, i=index: self.game.tap(i))
            self.tile_buttons.append(tile)
            self.board.grid.add_widget(tile)

    def draw(self):
        game = self.game
        for value, button in zip(game.cells, self.tile_buttons):
            button.text = str(value) if value else ""
            button.background_color = self.tile_color(value)
            button.color = (0.18, 0.17, 0.15, 1) if value and self._level(value) < 2 else TEXT
            button.font_size = sp(26 if len(button.text) < 5 else 20 if len(button.text) < 7 else 16)
            button.disabled = game.over
        self.score_text.text = str(game.score)
        self.best_text.text = str(game.best)
        self.goal_text.text = str(game.goal)
        self.status.text = game.message
        self.undo_button.disabled = game.over or game._previous is None
        self._refresh_base_buttons()

    def choose_base(self, number):
        self.selected_base = number
        self._refresh_base_buttons()

    def _refresh_base_buttons(self):
        for number, button in self.base_buttons.items():
            selected = number == self.selected_base
            button.background_color = ACCENT if selected else PANEL
            button.color = (0.06, 0.13, 0.10, 1) if selected else TEXT

    def _level(self, value):
        level = 0
        while value > self.game.base and value % self.game.base == 0:
            value //= 2
            level += 1
        return level

    def tile_color(self, value):
        if not value:
            return EMPTY
        level = 0
        current = value
        while current > self.game.base:
            current //= 2
            level += 1
        return TILE_COLORS[min(level, len(TILE_COLORS) - 1)]

class Number2048App(App):
    title = "2048 - Your Rules"

    def build(self):
        Window.clearcolor = BG
        Window.bind(on_key_down=self.on_key_down)
        self.screen = GameScreen(self)
        self.base = 2
        self.cells = [0] * 16
        self.score = 0
        self.best = 0
        self.over = False
        self.won = False
        self.completed_games = 0
        self.ads = None
        self.message = "Swipe or tap arrows" if platform == "android" else "Arrow keys or WASD to move"
        self._previous = None
        self.goal = 2048
        self.new_game(2)
        if platform == "android":
            from kivy.clock import Clock
            Clock.schedule_once(self.initialize_ads, 1)
        return self.screen

    def initialize_ads(self, _dt):
        try:
            from kivmob import KivMob
            from ads_config import (ADMOB_APP_ID, BANNER_AD_UNIT_ID,
                                    INTERSTITIAL_AD_UNIT_ID)

            self.ads = KivMob(ADMOB_APP_ID)
            self.ads.new_banner(BANNER_AD_UNIT_ID, top_pos=False)
            self.ads.request_banner()
            self.ads.show_banner()
            self.ads.new_interstitial(INTERSTITIAL_AD_UNIT_ID)
            self.ads.request_interstitial()
        except Exception as error:
            print("AdMob initialization failed:", error)

    def on_resume(self):
        if self.ads:
            try:
                self.ads.request_interstitial()
            except Exception as error:
                print("AdMob interstitial reload failed:", error)

    # CUSTOM LOGIC HOOKS: add your extra behavior here; these defaults do nothing.
    def custom_on_new_game(self, base):
        pass

    def custom_on_move(self, direction):
        pass

    def custom_on_exit(self):
        pass

    def request_app_exit(self):
        self.custom_on_exit()
        self.stop()

    def show_help(self):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        content.add_widget(Label(
            text=("Swipe or use arrow keys / WASD to move all tiles. Equal values merge into "
                  "their double. Choose a starting tile from 1 to 9 before starting a new game.\n\n"
                  "Undo restores the previous move."),
            color=TEXT, halign="left", valign="middle", text_size=(dp(300), None)))
        close = GameScreen.action_button("GOT IT", ACCENT, (0.06, 0.13, 0.10, 1))
        popup = Popup(title="HOW TO PLAY", content=content, size_hint=(0.86, 0.5),
                      separator_color=ACCENT)
        close.bind(on_release=popup.dismiss)
        content.add_widget(close)
        popup.open()

    def confirm_action(self, title, message, action):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        content.add_widget(Label(text=message, color=TEXT, halign="center"))
        buttons = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        popup = Popup(title=title, content=content, size_hint=(0.86, 0.34),
                      separator_color=ACCENT)
        cancel = GameScreen.action_button("CANCEL", PANEL, TEXT)
        cancel.bind(on_release=popup.dismiss)
        confirm = GameScreen.action_button("CONTINUE", ACCENT, (0.06, 0.13, 0.10, 1))
        confirm.bind(on_release=lambda *_: (popup.dismiss(), action()))
        buttons.add_widget(cancel)
        buttons.add_widget(confirm)
        content.add_widget(buttons)
        popup.open()

    def new_game(self, base):
        self.base = max(1, min(9, int(base)))
        self.custom_on_new_game(self.base)
        self.goal = self.base * 1024
        self.cells = [0] * 16
        self.score = 0
        self.over = False
        self.won = False
        self._previous = None
        self.message = "Swipe or tap arrows" if platform == "android" else "Arrow keys or WASD to move"
        self.spawn_tile()
        self.spawn_tile()
        if hasattr(self, "screen"):
            self.screen.draw()

    def spawn_tile(self):
        empty = [i for i, value in enumerate(self.cells) if value == 0]
        if empty:
            self.cells[choice(empty)] = self.base * (2 if random() < 0.1 else 1)

    def move(self, direction):
        if self.over:
            return
        old = self.cells[:]
        updated = [0] * 16
        gained = 0
        for line in self._lines(direction):
            packed, score = self._merge([old[i] for i in line])
            gained += score
            for index, value in zip(line, packed):
                updated[index] = value
        if updated == old:
            return
        self.custom_on_move(direction)
        self._previous = (old, self.score, self.won, self.message)
        self.cells = updated
        self.score += gained
        self.best = max(self.best, self.score)
        self.spawn_tile()
        if any(value >= self.goal for value in self.cells) and not self.won:
            self.won = True
            self.over = True
            self.completed_games += 1
            self.message = "You win! Starting a new game..."
        elif not self.has_moves():
            self.over = True
            self.completed_games += 1
            self.message = "No moves left. Starting a new game..."
        else:
            self.message = "Keep merging - target " + str(self.goal)
        self.screen.draw()
        if self.over:
            self.finish_game()

    def finish_game(self):
        if self.ads:
            try:
                self.ads.show_interstitial()
                self.ads.request_interstitial()
            except Exception as error:
                print("AdMob interstitial display failed:", error)
        from kivy.clock import Clock
        Clock.schedule_once(self._auto_restart, 1.5)

    def _auto_restart(self, _dt):
        if self.over:
            self.new_game(self.base)

    def _merge(self, values):
        values = [value for value in values if value]
        output = []
        score = 0
        index = 0
        while index < len(values):
            if index + 1 < len(values) and values[index] == values[index + 1]:
                merged = values[index] * 2
                output.append(merged)
                score += merged
                index += 2
            else:
                output.append(values[index])
                index += 1
        return output + [0] * (4 - len(output)), score

    @staticmethod
    def _lines(direction):
        if direction in ("left", "right"):
            for row in range(4):
                line = [row * 4 + col for col in range(4)]
                yield line if direction == "left" else line[::-1]
        else:
            for col in range(4):
                line = [row * 4 + col for row in range(4)]
                yield line if direction == "up" else line[::-1]

    def has_moves(self):
        if 0 in self.cells:
            return True
        for row in range(4):
            for col in range(4):
                index = row * 4 + col
                if col < 3 and self.cells[index] == self.cells[index + 1]:
                    return True
                if row < 3 and self.cells[index] == self.cells[index + 4]:
                    return True
        return False

    def undo(self):
        if self._previous is None:
            return
        self.cells, self.score, self.won, self.message = self._previous
        self._previous = None
        self.over = False
        self.screen.draw()

    def tap(self, index):
        # Tapping a tile is a harmless hint for users learning the swipe controls.
        self.message = "Swipe or tap arrows to move tiles" if platform == "android" else "Use arrows or WASD to move tiles"
        self.screen.draw()

    def on_key_down(self, _window, key, _scancode, codepoint, _modifiers):
        direction = {273: "up", 274: "down", 275: "right", 276: "left"}.get(key)
        if not direction:
            direction = {"w": "up", "s": "down", "d": "right", "a": "left"}.get(codepoint)
        if direction:
            self.move(direction)
            return True
        return False


if __name__ == "__main__":
    Number2048App().run()
