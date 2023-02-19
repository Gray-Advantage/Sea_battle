from engine import GameObject, Button, Image, GameObjectContainer, Events, Matrix, distance, adapt_values, Text
import constants
import pygame


class Field(GameObjectContainer):
    def __init__(self, position=(0, 0), cells_block=True, lst_ships=[]):
        super().__init__()
        self.x, self.y = position
        self.game_manager = None
        for y in range(10):
            for x in range(10):
                cell = Cell(x, y, self)
                cell.block = cells_block
                cell.rect.x = (cell.image.get_width()) * x + self.x
                cell.rect.y = (cell.image.get_height()) * y + self.y
                self.lst_game_objects.append(cell)
        self.matrix = Matrix(self.lst_game_objects, 10, 10)
        cell = self.lst_game_objects[-1]
        self.width, self.height = (cell.rect.x - self.x) + cell.rect.width, (cell.rect.y - self.y) + cell.rect.height
        self.lst_ships = self.transform_moving_ship_to_ship(lst_ships)
        self.health = sum([ship.long for ship in self.lst_ships])

    def transform_moving_ship_to_ship(self, lst_ships):
        answer = []
        for ship in lst_ships:
            answer.append(Ship(ship.direction, ship.long, ship.set_cell, self))
        return answer

    def set_block(self, mode):
        for cell in self.matrix:
            cell.block = mode

    def click(self, cell):
        if self.game_manager:
            self.game_manager.click(cell)

    def rel_move(self, rel_x: float = 0, rel_y: float = 0) -> None:
        x = (pygame.display.get_window_size()[0] - self.width) * rel_x
        y = (pygame.display.get_window_size()[1] - self.height) * rel_y
        self.move(x, y)

    def move(self, x, y):
        delta_x, delta_y = x - self.x, y - self.y
        self.shift(delta_x, delta_y)

    def shift(self, delta_x, delta_y):
        self.x, self.y = self.x + delta_x, self.y + delta_y
        for game_object in self.lst_game_objects:
            game_object.rect.x += delta_x
            game_object.rect.y += delta_y


class Cell(Button):
    def __init__(self, x, y, field):
        self.x, self.y = x, y

        self.field = field
        self.block = True
        self.is_empty = True
        super().__init__(State.cell_empty)

    def position(self):
        return self.x, self.y

    def mouse_hover(self, event):
        if not self.block and self.is_empty:
            self.image = State.cell_green.copy()

    def mouse_leave(self, event):
        if self.is_empty:
            self.image = State.cell_empty.copy()

    def mouse_click(self, event):
        if not self.block and self.is_empty:
            self.field.click(self)

    def hit(self):
        self.is_empty = False
        self.image = State.cell_hit.copy()

    def miss(self):
        self.is_empty = False
        self.image = State.cell_miss.copy()

    def __repr__(self):
        return f"Cell<{self.x, self.y}>"


class ShipMoving(Button):
    def __init__(self, long: int, is_intact: bool = True):
        if is_intact:
            if long == 1:
                img = State.ship_1_intact.copy()
            elif long == 2:
                img = State.ship_2_intact.copy()
            elif long == 3:
                img = State.ship_3_intact.copy()
            else:
                img = State.ship_4_intact.copy()
        else:
            if long == 1:
                img = State.ship_1_destroyed.copy()
            elif long == 2:
                img = State.ship_2_destroyed.copy()
            elif long == 3:
                img = State.ship_3_destroyed.copy()
            else:
                img = State.ship_4_destroyed.copy()

        super().__init__(img)

        self.set_cell: Cell = None
        self.direction = 0
        self._image_rotation = 0
        self.long = long
        self.start_position = (0, 0)
        self.is_on_mouse = False
        self.delta_position_to_mouse = (0, 0)
        self.field_manager = None

    def set_field_manager(self, manager):
        self.field_manager = manager

    def center_first_cell(self):
        if self.direction == 0:
            x = (self.rect.width / self.long / 2) + self.rect.x
            y = (self.rect.height / 2) + self.rect.y
        elif self.direction == 1:
            x = (self.rect.width / 2) + self.rect.x
            y = (self.rect.height / self.long / 2) + self.rect.y
        elif self.direction == 2:
            x = self.rect.width - (self.rect.width / self.long / 2) + self.rect.x
            y = (self.rect.height / 2) + self.rect.y
        else:
            x = (self.rect.width / 2) + self.rect.x
            y = self.rect.height - (self.rect.height / self.long / 2) + self.rect.y
        return x, y

    def rotate(self, mode: int):
        self.direction = mode
        while self._image_rotation != self.direction:
            self.image = pygame.transform.rotate(self.image, -90)
            self._image_rotation = (self._image_rotation + 1) % 4
            self.rect.width, self.rect.height = self.rect.height, self.rect.width

    def on_add_in_scene(self, scene):
        self.start_position = self.rect.x, self.rect.y

    def mouse_click(self, event: Events):
        self.is_on_mouse = True
        self.delta_position_to_mouse = self.rect.x - event.mouse_position[0], self.rect.y - event.mouse_position[1]

    def mouse_hold(self, event):
        self.rect.x = event.mouse_position[0] + self.delta_position_to_mouse[0]
        self.rect.y = event.mouse_position[1] + self.delta_position_to_mouse[1]
        if self.field_manager:
            self.field_manager.set_ship_tracking(self)

    def mouse_release(self, event):
        self.is_on_mouse = False
        if self.field_manager:
            self.field_manager.del_ship_tracking()
        if not self.set_cell:
            self.rotate(0)

    def update(self, event) -> None:
        super().update(event)
        if not self.is_on_mouse:
            if self.set_cell:
                if self.direction == 2:
                    cell_ = self.field_manager.field.matrix.get_cell(self.set_cell.x - self.long + 1, self.set_cell.y)
                elif self.direction == 3:
                    cell_ = self.field_manager.field.matrix.get_cell(self.set_cell.x, self.set_cell.y - self.long + 1)
                else:
                    cell_ = self.set_cell
                delta = adapt_values(3, 3)
                self.step_to(cell_.rect.x + delta[0], cell_.rect.y + delta[1], speed=5)
            else:
                self.step_to(*self.start_position, speed=5)
        else:
            if pygame.KEYDOWN in event and event[pygame.KEYDOWN].key == pygame.K_SPACE:
                self.rotate((self.direction + 1) % 4)


class SetFieldManager(GameObject):
    def __init__(self, field: Field, *tracking_ship: tuple[ShipMoving]):
        super().__init__()
        self.field: Field = field
        self._ship_tracking: ShipMoving = None
        self.lst_ships: list[ShipMoving] = tracking_ship
        for ship in tracking_ship:
            ship.set_field_manager(self)

    def set_ship_tracking(self, ship) -> None:
        self._ship_tracking = ship

    def del_ship_tracking(self) -> None:
        self._ship_tracking = None

    def get_nearest_cell(self) -> Cell:
        center_ship = list(self._ship_tracking.center_first_cell())
        answer_cell, dist = None, float("inf")
        for cell in self.field.matrix:
            center_of_cell = cell.rect.center
            if distance(center_of_cell, center_ship) < dist:
                dist = distance(center_of_cell, center_ship)
                answer_cell = cell
        return answer_cell, dist

    @staticmethod
    def cells_for_ship(near_cell: Cell, ship, field) -> list[Cell]:
        direction, long = ship.direction, ship.long
        answer = []
        for y in range(*([1] if direction % 2 == 0 else [0, long] if direction == 1 else [0, -long, -1])):
            for x in range(*([1] if direction % 2 == 1 else [0, long] if direction == 0 else [0, -long, -1])):
                cell = field.matrix.get_cell(near_cell.x + x, near_cell.y + y)
                if cell:
                    answer.append(cell)
        return answer

    @staticmethod
    def cells_local_ship(near_cell: Cell, ship, field) -> list[Cell]:
        cells_of_ship, local_cells = SetFieldManager.cells_for_ship(near_cell, ship, field), []
        for cell in cells_of_ship:
            for delta_y in range(-1, 2):
                for delta_x in range(-1, 2):
                    temp_cell = field.matrix.get_cell(cell.x + delta_x, cell.y + delta_y)
                    if temp_cell is not None and temp_cell not in cells_of_ship and temp_cell not in local_cells:
                        local_cells.append(temp_cell)
        return local_cells

    def color_ship_on_board(self, near_cell: Cell, is_green: bool = True) -> None:
        for cell in self.cells_for_ship(near_cell, self._ship_tracking, self.field):
            cell.image = State.cell_green if is_green else State.cell_red

    def check_borders(self, near_cell) -> bool:
        return len(self.cells_for_ship(near_cell, self._ship_tracking, self.field)) == self._ship_tracking.long

    def check_other_ships(self, near_cell) -> bool:
        cells_of_ship = SetFieldManager.cells_for_ship(near_cell, self._ship_tracking, self.field)
        ship_cells, local_cells = [], SetFieldManager.cells_local_ship(near_cell, self._ship_tracking, self.field)
        for ship in self.lst_ships:
            if ship.set_cell is not None and ship is not self._ship_tracking:
                ship_cells.extend(self.cells_for_ship(ship.set_cell, ship, self.field))
        return len((set(local_cells) | set(cells_of_ship)) & set(ship_cells)) == 0

    def check_correction_all_ships(self):
        for ship in self.lst_ships:
            if not ship.set_cell:
                return False
        return True

    def reset(self):
        for ship in self.lst_ships:
            ship.rotate(0)
            ship.set_cell = None
            ship.rect.x, self.rect.y = ship.start_position

    def update(self, event: Events) -> None:
        for cell in self.field.matrix:
            cell.image = State.cell_empty

        if self._ship_tracking:
            cell, dist = self.get_nearest_cell()
            can_set = all([self.check_borders(cell), dist < 100, self.check_other_ships(cell)])
            if can_set:
                self._ship_tracking.set_cell = cell
                self.color_ship_on_board(cell)
            else:
                self._ship_tracking.set_cell = None
                self.color_ship_on_board(cell, False)


class GameManagerForTwoPlayers(GameObject):
    def __init__(self,
                 player_1_img: GameObject,
                 player_2_img: GameObject,
                 field_1: Field, field_2: Field,
                 text: GameObject):
        super().__init__()
        self.text = text
        self.scene = None

        self.player_1 = player_1_img
        self.player_2 = player_2_img

        self.field_1 = field_1
        self.field_2 = field_2

        self.field_1.game_manager = self
        self.field_2.game_manager = self

        self.lst_ships_1 = self.field_1.lst_ships
        self.lst_ships_2 = self.field_2.lst_ships

        self.is_first_turn = False
        self.next_move()

    def on_add_in_scene(self, scene):
        self.scene = scene

    def next_move(self):
        self.is_first_turn = not self.is_first_turn

        self.player_1.image = State.player_1_select.copy() if self.is_first_turn else State.player_1_unselect.copy()
        self.player_2.image = State.player_2_unselect.copy() if self.is_first_turn else State.player_2_select.copy()
        self.field_1.set_block(self.is_first_turn)
        self.field_2.set_block(not self.is_first_turn)

    def click(self, cell):
        lst_ships = self.lst_ships_2 if self.is_first_turn else self.lst_ships_1
        for ship in lst_ships:
            if cell in ship.cells:
                cell.hit()
                ship.hit()
                break
        else:
            cell.miss()
            self.next_move()
        if self.field_1.health == 0 or self.field_2.health == 0:
            if self.is_first_turn and self.field_2.health == 0:
                self.text.add_text(Text("Первый игрок одержал победу", "black", 30))
                for ship in self.lst_ships_1:
                    ship.go_to_cell()
            elif not self.is_first_turn and self.field_1.health == 0:
                self.text.add_text(Text("Второй игрок одержал победу", "black", 30))
                for ship in self.lst_ships_2:
                    ship.go_to_cell()
            self.text.rel_move(0.5, 0.05)
            self.field_1.set_block(True)
            self.field_2.set_block(True)
            self.scene.add_game_objects(self.text)

    def open(self, cell):
        cell.miss()


class Ship(GameObject):
    def __init__(self, direction, long, first_cell, field):
        self.long = long
        self.direction = direction
        self.first_cell = first_cell
        self.field = field
        self._image_rotation = 0
        self.init_image()
        self.rotate(self.direction)
        self.cells = SetFieldManager.cells_for_ship(self.first_cell, self, field)
        self.health = self.long

    def init_image(self):
        if self.long == 1:
            image = State.ship_1_intact.copy()
        elif self.long == 2:
            image = State.ship_2_intact.copy()
        elif self.long == 3:
            image = State.ship_3_intact.copy()
        else:
            image = State.ship_4_intact.copy()
        super().__init__(image)

    def rotate(self, mode: int):
        self.direction = mode
        while self._image_rotation != self.direction:
            self.image = pygame.transform.rotate(self.image, -90)
            self._image_rotation = (self._image_rotation + 1) % 4
            self.rect.width, self.rect.height = self.rect.height, self.rect.width

    def go_to_cell(self):
        self.field.game_manager.scene.add_game_objects(self)
        if self.direction == 2:
            cell_ = self.field.matrix.get_cell(self.first_cell.x - self.long + 1, self.first_cell.y)
        elif self.direction == 3:
            cell_ = self.field.matrix.get_cell(self.first_cell.x, self.first_cell.y - self.long + 1)
        else:
            cell_ = self.field.matrix.get_cell(self.first_cell.x, self.first_cell.y)
        delta = adapt_values(3, 3)
        self.rect.x, self.rect.y = cell_.rect.x + delta[0], cell_.rect.y + delta[1]

    def hit(self):
        self.health -= 1
        self.field.health -= 1
        if self.health == 0:
            self._image_rotation = 0
            if self.long == 1:
                self.image = State.ship_1_destroyed.copy()
            elif self.long == 2:
                self.image = State.ship_2_destroyed.copy()
            elif self.long == 3:
                self.image = State.ship_3_destroyed.copy()
            else:
                self.image = State.ship_4_destroyed.copy()
            self.rotate(self.direction)
            lst_local_cells = SetFieldManager.cells_local_ship(self.first_cell, self, self.field)
            for cell in lst_local_cells:
                self.field.game_manager.open(cell)
            self.go_to_cell()


class State:
    cell_empty = Image.load(f"{constants.PATH_TO_DATA}/cell_empty.png")
    cell_miss = Image.load(f"{constants.PATH_TO_DATA}/cell_miss.png")
    cell_hit = Image.load(f"{constants.PATH_TO_DATA}/cell_hit.png")
    cell_green = Image.load(f"{constants.PATH_TO_DATA}/cell_green.png")
    cell_red = Image.load(f"{constants.PATH_TO_DATA}/cell_red.png")

    anchor_img = Image.load(f"{constants.PATH_TO_DATA}/anchor.png", 1.5)
    main_menu_button = Image.load(f"{constants.PATH_TO_DATA}/main_menu_button.png")
    menu_button = Image.load(f"{constants.PATH_TO_DATA}/menu_button.png")
    background_for_button = Image.load(f"{constants.PATH_TO_DATA}/background_for_button.png")

    ship_1_destroyed = Image.load(f"{constants.PATH_TO_DATA}/ship_1_destroyed.png")
    ship_2_destroyed = Image.load(f"{constants.PATH_TO_DATA}/ship_2_destroyed.png")
    ship_3_destroyed = Image.load(f"{constants.PATH_TO_DATA}/ship_3_destroyed.png")
    ship_4_destroyed = Image.load(f"{constants.PATH_TO_DATA}/ship_4_destroyed.png")

    ship_1_intact = Image.load(f"{constants.PATH_TO_DATA}/ship_1_intact.png")
    ship_2_intact = Image.load(f"{constants.PATH_TO_DATA}/ship_2_intact.png")
    ship_3_intact = Image.load(f"{constants.PATH_TO_DATA}/ship_3_intact.png")
    ship_4_intact = Image.load(f"{constants.PATH_TO_DATA}/ship_4_intact.png")

    player_1_unselect = Image.load(f"{constants.PATH_TO_DATA}/player_1_unselect.png")
    player_2_unselect = Image.load(f"{constants.PATH_TO_DATA}/player_2_unselect.png")
    player_1_select = Image.load(f"{constants.PATH_TO_DATA}/player_1_select.png")
    player_2_select = Image.load(f"{constants.PATH_TO_DATA}/player_2_select.png")
