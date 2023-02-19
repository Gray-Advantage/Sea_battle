import os
import sys
import pygame
import constants

pygame.init()

screen_size = pygame.display.Info().current_w, pygame.display.Info().current_h

if constants.FULL_SCREEN_MODE is True:
    screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode(constants.SCREEN_SIZE)

pygame.display.set_caption(constants.TITLE_OF_GAME)


# ======================================================================================================================
class Matrix:
    def __init__(self, lst, count_col, count_row):
        self._matrix = []
        self.all_objects = lst
        for i in range(count_row):
            self._matrix.append(lst[count_col * i: (count_col * i) + count_col])

    def width(self):
        return len(self._matrix[0])

    def height(self):
        return len(self._matrix)

    def get_cell(self, x, y):
        if 0 <= x < self.width() and 0 <= y < self.height():
            return self._matrix[y][x]
        return None

    def __iter__(self):
        return iter(self.all_objects)


class Events:
    def __init__(self, events: list[pygame.event.Event] = None):
        self.events = events if events is not None else []

        self.mouse_position = self[pygame.MOUSEMOTION].pos if pygame.MOUSEMOTION in self else (0, 0)

    def update(self):
        self.mouse_position = self[pygame.MOUSEMOTION].pos if pygame.MOUSEMOTION in self else self.mouse_position

    def __call__(self, new_events: list[pygame.event.Event] = None):
        self.events = new_events if new_events is not None else []
        self.update()

    def __contains__(self, item: pygame.event.Event):
        return item in [event.type for event in self.events]

    def __iter__(self):
        return iter(self.events)

    def __getitem__(self, item: pygame.event.Event):
        if item in self:
            for event in self:
                if event.type == item:
                    return event
        return None

    def __str__(self):
        return f"Events<[{self.events}]>"


class Text:
    def __init__(self, text, color, size, bold=False, italic=False, underline=False):
        if constants.FONT_NAME is None:
            self.font_name = pygame.font.get_default_font()
        else:
            self.font_name = pygame.font.match_font(constants.FONT_NAME)
        self.text = text
        self.color = color
        self.size = size
        self.bold = bold
        self.underline = underline
        self.italic = italic

    def render(self):
        font = pygame.font.Font(self.font_name, self.size)
        font.set_bold(self.bold)
        font.set_italic(self.italic)
        font.set_underline(self.underline)
        return font.render(self.text, False, self.color)


class Image:
    @staticmethod
    def load(path_to_sours: str, scale_k: int = 1) -> pygame.Surface:
        surface = pygame.image.load(resource_path(path_to_sours))
        surface = pygame.transform.scale(surface, (surface.get_width() * scale_k, surface.get_height() * scale_k))
        cur_width, cur_height = surface.get_size()
        if not constants.FULL_SCREEN_MODE:
            if constants.SCREEN_SIZE != screen_size:
                return pygame.transform.scale(surface, (
                    round(constants.SCREEN_SIZE[0] * cur_width / screen_size[0], 3),
                    round(constants.SCREEN_SIZE[1] * cur_height / screen_size[1], 3)
                ))
        return surface


class GameObject(pygame.sprite.Sprite):
    def __init__(self, surface: pygame.Surface = None, size=(0, 0)):
        super().__init__()
        self.image = surface if surface is not None else pygame.Surface(size, flags=pygame.SRCALPHA)
        self._orig_image = self.image.copy()
        self.rect: pygame.rect.Rect = self.image.get_rect()

    def step_to(self, x_pos, y_pos, speed=1):
        if abs(self.rect.x - x_pos) < speed:
            self.rect.x = x_pos
        if abs(self.rect.y - y_pos) < speed:
            self.rect.y = y_pos
        if self.rect.x != x_pos or self.rect.y != y_pos:
            dist_x, dist_y = x_pos - self.rect.x, y_pos - self.rect.y
            step_x, step_y = dist_x / speed, dist_y / speed
            self.rect.x += step_x
            self.rect.y += step_y

    def move(self, x: int, y: int) -> None:
        self.rect.x, self.rect.y = adapt_values(self.rect.x + x, self.rect.y + y)

    def rel_move(self, rel_x: float = 0, rel_y: float = 0) -> None:
        x = (pygame.display.get_window_size()[0] - self.image.get_width()) * rel_x
        y = (pygame.display.get_window_size()[1] - self.image.get_height()) * rel_y
        self.rect.x, self.rect.y = x, y

    def shift(self, delta_x: int, delta_y: int) -> None:
        delta = adapt_values(delta_x, delta_y)
        self.rect.x, self.rect.y = self.rect.x + delta[0], self.rect.y + delta[1]

    def add_text(self, text: Text, position: tuple[int, int] = None, rel_position: tuple[int, int] = None, scale_k=1):
        text_img = text.render()
        text_img = pygame.transform.scale(text_img, (text_img.get_width() * scale_k, text_img.get_height() * scale_k))
        text_img = pygame.transform.scale(text_img, adapt_values(text_img.get_width(), text_img.get_height()))
        text_width, text_height = text_img.get_size()
        self_width, self_height = self.rect.size if self.image.get_size() != (0, 0) else text_img.get_size()
        x, y = (0, 0)
        if rel_position is not None:
            x, y = (self_width - text_width) * rel_position[0], (self_height - text_height) * rel_position[1]
        if position is not None:
            x, y = x + position[0], y + position[1]
        if self.image.get_size() == (0, 0):
            self.image = pygame.Surface(text_img.get_size(), flags=pygame.SRCALPHA)
        self.image.blit(text_img, (x, y))

    def clear_text(self):
        self.image = self._orig_image.copy()

    def on_add_in_scene(self, scene):
        pass

    def update(self, event: Events) -> None:
        pass

    def flip(self, flip_x=False, flip_y=False):
        self.image = pygame.transform.flip(self.image, flip_x, flip_y)


class GameObjectContainer:
    def __init__(self):
        self.lst_game_objects: list[GameObject] = []


class Button(GameObject):
    def __init__(self, surface=None, command=None):
        super().__init__(surface)
        self._is_hover = False
        self._last_mouse_down = False
        self._command = command

    def update(self, event) -> None:
        mouse_hover = self.rect.collidepoint(event.mouse_position)
        mouse_down = pygame.MOUSEBUTTONDOWN in event
        mouse_up = pygame.MOUSEBUTTONUP in event

        if mouse_hover and mouse_down and not self._last_mouse_down:
            self._last_mouse_down = True
            self.mouse_click(event)
        elif self._last_mouse_down and not mouse_up:
            self.mouse_hold(event)
        elif self._last_mouse_down and mouse_up:
            self._last_mouse_down = False
            self.mouse_release(event)

        if mouse_hover and not self._is_hover:
            self.mouse_hover(event)
            self._is_hover = True
        elif not mouse_hover and self._is_hover:
            self._is_hover = False
            self.mouse_leave(event)

    def mouse_hover(self, event):
        if constants.DEBUG_MODE:
            print(self, "mouse_hover")

    def mouse_leave(self, event):
        if constants.DEBUG_MODE:
            print(self, "mouse_leave")

    def mouse_click(self, event):
        if constants.DEBUG_MODE:
            print(self, "mouse_click")
        if self._command is not None:
            self._command()

    def mouse_hold(self, event):
        if constants.DEBUG_MODE:
            print(self, "mouse_hold")

    def mouse_release(self, event):
        if constants.DEBUG_MODE:
            print(self, "mouse_release")


class Scene:
    def __init__(self, color: tuple[int, int, int] = (0, 0, 0)):
        self.game_objects_group = pygame.sprite.Group()
        self.color = color

    def add_game_objects(self, *new_game_objects: list[GameObject | GameObjectContainer]):
        for new_game_object in new_game_objects:
            if isinstance(new_game_object, GameObject):
                self.game_objects_group.add(new_game_object)
                new_game_object.on_add_in_scene(self)
            else:
                self.add_game_objects(*new_game_object.lst_game_objects)
                for elem in new_game_object.lst_game_objects:
                    elem.on_add_in_scene(self)

    def clear(self):
        self.game_objects_group.empty()

    def update(self, *args, **kwargs):
        screen.fill(self.color)
        self.game_objects_group.draw(screen)
        self.game_objects_group.update(*args, **kwargs)
# ======================================================================================================================


_scene: Scene = Scene((50, 60, 70))


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def adapt_values(x: int, y: int) -> tuple[int, int]:
    if constants.FULL_SCREEN_MODE:
        return screen_size[0] / constants.SCREEN_SIZE[0] * x, screen_size[1] / constants.SCREEN_SIZE[1] * y
    return x, y


def distance(position_1, position_2):
    delta_x = abs(position_1[0] - position_2[0])
    delta_y = abs(position_1[1] - position_2[1])
    return (delta_x ** 2 + delta_y ** 2) ** 0.5


def set_scene(new_scene: Scene):
    global _scene
    _scene = new_scene


def close():
    pygame.quit()


def main_loop():
    events = Events()
    clock = pygame.time.Clock()
    pygame.event.set_blocked(None)
    pygame.event.set_allowed([
        pygame.QUIT,
        pygame.MOUSEMOTION,
        pygame.MOUSEBUTTONDOWN,
        pygame.MOUSEBUTTONUP,
        pygame.KEYDOWN,
        pygame.WINDOWENTER,
        pygame.WINDOWLEAVE
    ])

    while True:
        events(pygame.event.get())

        if pygame.QUIT in events or (pygame.KEYDOWN in events and events[pygame.KEYDOWN].key == pygame.K_ESCAPE):
            break

        _scene.update(events)
        pygame.display.flip()

        clock.tick(constants.FPS if constants.FPS is not None else 0)

        if constants.DEBUG_MODE:
            pygame.display.set_caption(f"{constants.TITLE_OF_GAME}  <{clock.get_fps()}>")
