from engine import GameObject, Button, Scene, main_loop, set_scene, close, Text, adapt_values
from sea_battle_asset import Field, State, ShipMoving, SetFieldManager, GameManagerForTwoPlayers
import settings_manager
import update_manager
from sys import exit
import constants

# =================================================== main_menu =======================================================
main_menu = Scene((248, 248, 255))
# title
title = GameObject()
title.add_text(Text("Морской бой", "black", 40))
title.rel_move(0.5, 0.05)
# anchor
anchor = GameObject(State.anchor_img.copy())
anchor.flip(True)
anchor.rel_move(1, 1)
# start game
button_start_game = Button(State.main_menu_button.copy(), command=lambda: set_scene(preparatory_menu_player_1))
button_start_game.add_text(Text("Новая игра", "white", 40), rel_position=(0.1, 0.6))
button_start_game.shift(0, 80)
# settings game
button_open_setting_in_main_menu = Button(State.main_menu_button.copy(), lambda: set_scene(settings_menu))
button_open_setting_in_main_menu.add_text(Text("Настройки", "white", 40), rel_position=(0.1, 0.6))
button_open_setting_in_main_menu.shift(0, 140)
# exit
exit_button_in_main_menu = Button(State.main_menu_button.copy(), command=exit)
exit_button_in_main_menu.add_text(Text("Выход", "white", 40), rel_position=(0.06, 0.6))
exit_button_in_main_menu.shift(0, 200)

main_menu.add_game_objects(
    button_start_game,
    button_open_setting_in_main_menu,
    exit_button_in_main_menu,
    title,
    anchor
)
# ================================================= settings_menu =====================================================
settings_menu = Scene((234, 234, 255))

title = GameObject()
title.add_text(Text("Настройки", "black", 40))
title.rel_move(0.5, 0.05)

info = GameObject()
info.add_text(Text(f"<{constants.VERSION}> by Gray_Advantage", "grey", 40), scale_k=0.5)
info.rel_move(1, 1)


set_check_updates_button = Button(State.background_for_button.copy(), command=lambda: change_value_checking_updates())
values = ("Обновлять", "green", 20) if settings_manager.SETTINGS["check_update"] else ("Не Обновлять", "red", 20)
set_check_updates_button.add_text(Text(*values), rel_position=(0.5, 0.5))
set_check_updates_button.rel_move(0.5, 0.2)


def change_value_checking_updates():
    settings_manager.set_option("check_update", not settings_manager.SETTINGS["check_update"])
    set_check_updates_button.clear_text()
    values_ = ("Обновлять", "green", 20) if settings_manager.SETTINGS["check_update"] else ("Не Обновлять", "red", 20)
    set_check_updates_button.add_text(Text(*values_), rel_position=(0.5, 0.5))


back_button = Button(State.background_for_button.copy(), command=lambda: set_scene(main_menu))
back_button.add_text(Text("Назад", "white", 40), rel_position=(0.5, 0.5))
back_button.rel_move(0.5, 0.9)

settings_menu.add_game_objects(
    title, info,
    back_button,
    set_check_updates_button
)
# =========================================== preparatory_menu_player_1 ===============================================
preparatory_menu_player_1 = Scene((248, 248, 255))

title = GameObject()
title.add_text(Text("Первый игрок", "black", 40))
title.rel_move(0.5, 0.05)

field = Field()
field.rel_move(0.1, 0.6)

ship_4, ship_3_1, ship_3_2, ship_2_1, ship_2_2, ship_2_3, ship_1_1, ship_1_2, shop_1_3, ship_1_4 = (
    ShipMoving(4),
    ShipMoving(3), ShipMoving(3),
    ShipMoving(2), ShipMoving(2), ShipMoving(2),
    ShipMoving(1), ShipMoving(1), ShipMoving(1), ShipMoving(1)
)
set_ship_on_field_manager_1 = SetFieldManager(field, ship_4, ship_3_1, ship_3_2, ship_2_1, ship_2_2, ship_2_3,
                                              ship_1_1, ship_1_2, shop_1_3, ship_1_4)

ship_4.rel_move(0.603, 0.157)

ship_3_1.rel_move(0.576, 0.25)
ship_3_2.rel_move(0.73, 0.25)

ship_2_1.rel_move(0.55, 0.34)
ship_2_2.rel_move(0.65, 0.34)
ship_2_3.rel_move(0.75, 0.34)

ship_1_1.rel_move(0.525, 0.428)
ship_1_2.rel_move(0.58, 0.428)
shop_1_3.rel_move(0.635, 0.428)
ship_1_4.rel_move(0.69, 0.428)

info = GameObject(size=adapt_values(320, 100))
info.add_text(Text("Перетащите мышью корабли на поле.", "black", 25), rel_position=(0.5, 0.3))
info.add_text(Text("Пробел - поворот корабля.", "black", 25), rel_position=(0.5, 0.6))
info.rel_move(0.91, 0.7)

button_ready = Button(State.background_for_button.copy(),
                      command=lambda: set_scene(preparatory_menu_player_2)
                      if set_ship_on_field_manager_1.check_correction_all_ships()
                      else None)
button_back = Button(State.background_for_button.copy(),
                     command=lambda: (set_ship_on_field_manager_1.reset(), set_scene(main_menu)))
button_ready.add_text(Text("Готово", "white", 40), rel_position=(0.5, 0.5))
button_ready.rel_move(0.9, 0.904)
button_back.add_text(Text("Назад", "white", 40), rel_position=(0.5, 0.5))
button_back.rel_move(0.7, 0.904)

preparatory_menu_player_1.add_game_objects(
    title,
    field,
    ship_4,
    ship_3_1, ship_3_2,
    ship_2_1, ship_2_2, ship_2_3,
    ship_1_1, ship_1_2, shop_1_3, ship_1_4,
    set_ship_on_field_manager_1, info,
    button_back, button_ready
)
# =========================================== preparatory_menu_player_2 ===============================================
preparatory_menu_player_2 = Scene((248, 248, 255))

title = GameObject()
title.add_text(Text("Второй игрок", "black", 40))
title.rel_move(0.5, 0.05)

field = Field()
field.rel_move(0.1, 0.6)

ship_4, ship_3_1, ship_3_2, ship_2_1, ship_2_2, ship_2_3, ship_1_1, ship_1_2, shop_1_3, ship_1_4 = (
    ShipMoving(4),
    ShipMoving(3), ShipMoving(3),
    ShipMoving(2), ShipMoving(2), ShipMoving(2),
    ShipMoving(1), ShipMoving(1), ShipMoving(1), ShipMoving(1)
)
set_ship_on_field_manager_2 = SetFieldManager(field, ship_4, ship_3_1, ship_3_2, ship_2_1, ship_2_2, ship_2_3,
                                              ship_1_1, ship_1_2, shop_1_3, ship_1_4)

ship_4.rel_move(0.603, 0.157)

ship_3_1.rel_move(0.576, 0.25)
ship_3_2.rel_move(0.73, 0.25)

ship_2_1.rel_move(0.55, 0.34)
ship_2_2.rel_move(0.65, 0.34)
ship_2_3.rel_move(0.75, 0.34)

ship_1_1.rel_move(0.525, 0.428)
ship_1_2.rel_move(0.58, 0.428)
shop_1_3.rel_move(0.635, 0.428)
ship_1_4.rel_move(0.69, 0.428)

info = GameObject(size=adapt_values(320, 100))
info.add_text(Text("Перетащите мышью корабли на поле.", "black", 25), rel_position=(0.5, 0.3))
info.add_text(Text("Пробел - поворот корабля.", "black", 25), rel_position=(0.5, 0.6))
info.rel_move(0.91, 0.7)

button_ready = Button(State.background_for_button.copy(),
                      command=lambda: (init_game(), set_scene(the_game))
                      if set_ship_on_field_manager_2.check_correction_all_ships() else
                      None)
button_back = Button(State.background_for_button.copy(),
                     command=lambda: (set_ship_on_field_manager_2.reset(), set_scene(preparatory_menu_player_1)))
button_ready.add_text(Text("Готово", "white", 40), rel_position=(0.5, 0.5))
button_ready.rel_move(0.9, 0.904)
button_back.add_text(Text("Назад", "white", 40), rel_position=(0.5, 0.5))
button_back.rel_move(0.7, 0.904)

preparatory_menu_player_2.add_game_objects(
    title,
    field,
    ship_4,
    ship_3_1, ship_3_2,
    ship_2_1, ship_2_2, ship_2_3,
    ship_1_1, ship_1_2, shop_1_3, ship_1_4,
    set_ship_on_field_manager_2, info,
    button_back, button_ready
)
# =================================================== the_game ========================================================
the_game = Scene((248, 248, 255))


def init_game():
    global the_game

    field_1 = Field(lst_ships=set_ship_on_field_manager_1.lst_ships)
    field_1.rel_move(0.05, 0.65)
    field_2 = Field(lst_ships=set_ship_on_field_manager_2.lst_ships)
    field_2.rel_move(0.95, 0.65)

    player_1_icon = GameObject(State.player_1_unselect.copy())
    player_1_icon.rel_move(0.23, 0.03)
    player_2_icon = GameObject(State.player_2_unselect.copy())
    player_2_icon.rel_move(0.77, 0.03)

    menu_button = Button(State.menu_button.copy(), command=lambda: (set_ship_on_field_manager_1.reset(),
                                                                    set_ship_on_field_manager_2.reset(),
                                                                    the_game.clear(),
                                                                    set_scene(main_menu)))

    info_about_winner = GameObject()

    game_manager = GameManagerForTwoPlayers(player_1_icon, player_2_icon, field_1, field_2, info_about_winner)

    the_game.add_game_objects(
        menu_button,
        player_1_icon, player_2_icon,
        field_1, field_2,
        game_manager
    )


# =================================================== main_script =====================================================
def main():
    if settings_manager.SETTINGS["check_update"] is True:
        update_manager.update_to_latest()
    set_scene(main_menu)
    main_loop()
    close()


if __name__ == '__main__':
    main()
