"""
main.py
Punto de entrada del juego — M1 + M2 + M3 integrados.
Loop de navegación real por el dungeon.
"""

import random

from engine.core.player import PlayerClass, CLASS_DEFINITIONS, create_player
from engine.core.dungeon import DungeonGraph, RoomType, RoomState
from engine.ui.renderer import (
    console,
    show_title_screen,
    show_class_selection,
    show_player_hud,
    show_room_header,
    show_narrative,
    show_event_choices,
    get_player_input,
    show_message,
    pause,
    clear,
    ASCII_CANDLE,
    C,
)
from engine.ui.map_renderer import render_dungeon_map, render_room_choices


# ------------------------------------------------------------------ #
#  Selección de clase                                                  #
# ------------------------------------------------------------------ #

def select_class() -> PlayerClass:
    show_class_selection(CLASS_DEFINITIONS)
    classes = list(PlayerClass)
    while True:
        raw = get_player_input("Elige tu condena [1-4]")
        if raw.strip().isdigit():
            idx = int(raw.strip()) - 1
            if 0 <= idx < len(classes):
                return classes[idx]
        show_message("Número inválido.", style=C["danger"])


# ------------------------------------------------------------------ #
#  Secuencia de intro                                                  #
# ------------------------------------------------------------------ #

def intro_sequence(player) -> None:
    clear()
    console.print(ASCII_CANDLE)
    pause(0.8)

    show_room_header("La Puerta de las Lágrimas", depth=0)

    for line in [
        "La lluvia no cesa. Nunca cesa aquí.",
        f"Te llaman {player.display_name}. Por ahora.",
        "Delante: una puerta de piedra. Detrás: nada que valga la pena salvar.",
        "La vela que llevas es lo único que separa este lugar de la oscuridad total.",
    ]:
        show_narrative(line)
        pause(0.5)

    show_event_choices([
        ("1", "Empujar la puerta y entrar."),
        ("2", "Examinar los grabados en la piedra."),
        ("3", "Dudar. Solo un momento."),
    ])
    choice = get_player_input()

    if choice == "2":
        show_narrative(
            "Los grabados muestran figuras que entran a esta puerta. "
            "Ninguna sale. Alguien los grabó igualmente."
        )
        player.lose_sanity(1)
        show_message("Pierdes 1 de Cordura.", style=C["sanity_high"])
        pause(1.0)
    elif choice == "3":
        show_narrative("La duda no te salva. Solo te hace más consciente de lo que viene.")
        pause(1.0)

    show_narrative("Entras.")
    pause(0.5)


# ------------------------------------------------------------------ #
#  Handlers de sala — stubs hasta que lleguen M4 y M5                 #
# ------------------------------------------------------------------ #

def handle_combat(player, room, dungeon: DungeonGraph) -> bool:
    """Combate real — usa el Combat Engine (M5)."""
    from engine.systems.combat_engine import run_combat
    survived = run_combat(player, room, dungeon)
    if not survived:
        # Registrar causa de muerte para el RunManager
        # El combat_engine ya dejó al jugador con hp/sanity <= 0
        # Guardamos el tipo de sala como pista de causa
        player.set_flag("_death_room_type", room.room_type.value)
    return survived


def handle_rest(player, room, dungeon: DungeonGraph) -> None:
    """Sala de descanso — el jugador elige qué recuperar."""
    clear()
    show_room_header(room.name, depth=room.depth)
    show_narrative(room.flavor_text)
    pause(0.6)

    show_event_choices([
        ("1", f"Descansar — recupera {4} HP  [{player.hp}/{player.hp_max}]"),
        ("2", f"Meditar  — recupera {3} Cordura  [{player.sanity}/{player.sanity_max}]"),
        ("3", "Ignorar el refugio y seguir."),
    ])
    choice = get_player_input()

    if choice == "1":
        healed = player.heal(4)
        show_message(f"Recuperas {healed} HP.", style=C["hp_high"])
    elif choice == "2":
        restored = player.restore_sanity(3)
        show_message(f"Recuperas {restored} de Cordura.", style=C["sanity_high"])
    else:
        show_narrative("No te permites el lujo del descanso.")

    dungeon.clear_current_room()
    pause(0.8)


def handle_treasure(player, room, dungeon: DungeonGraph) -> None:
    """Sala de tesoro real — usa el Inventory System (M6)."""
    from engine.systems.inventory import handle_treasure_room
    handle_treasure_room(player, room, dungeon)


def handle_event(player, room, dungeon: DungeonGraph) -> None:
    """Evento narrativo — usa el Event Engine (M4)."""
    from engine.systems.event_engine import pick_event_for_room, run_event

    event = pick_event_for_room(room, player)

    if event is None:
        # Fallback mínimo si no hay ningún evento elegible
        clear()
        show_room_header(room.name, depth=room.depth)
        show_narrative(room.flavor_text)
        show_narrative("No hay nada aquí. O hay demasiado para verlo.")
        pause(1.0)
    else:
        run_event(event, player, dungeon)

    dungeon.clear_current_room()

def handle_exit(player, room) -> None:
    """Sala de salida — fin del nivel actual."""
    clear()
    show_room_header(room.name, depth=room.depth)
    show_narrative(room.flavor_text)
    pause(0.6)
    show_narrative("El dungeon continúa. Siempre continúa.")
    pause(1.0)


# ------------------------------------------------------------------ #
#  Dispatcher de sala                                                  #
# ------------------------------------------------------------------ #

ROOM_HANDLERS = {
    RoomType.COMBAT:   handle_combat,
    RoomType.ELITE:    handle_combat,
    RoomType.BOSS:     handle_combat,
    RoomType.REST:     handle_rest,
    RoomType.TREASURE: handle_treasure,
    RoomType.EVENT:    handle_event,
    RoomType.EXIT:     lambda p, r, d: handle_exit(p, r),
    RoomType.ENTRANCE: lambda p, r, d: None,
}


def enter_room(player, room, dungeon: DungeonGraph) -> bool:
    """
    Ejecuta el handler de la sala actual.
    Devuelve False si el jugador muere, True en cualquier otro caso.
    """
    handler = ROOM_HANDLERS.get(room.room_type)
    if handler is None:
        return True

    result = handler(player, room, dungeon)
    player.rooms_explored += 1
    player.depth = max(player.depth, room.depth)

    # Los handlers de combate devuelven bool; el resto None
    if result is False:
        return False
    return True


# ------------------------------------------------------------------ #
#  Loop de navegación principal                                        #
# ------------------------------------------------------------------ #

def navigation_loop(player, dungeon: DungeonGraph) -> None:
    """
    Loop principal: muestra mapa → muestra opciones → el jugador elige
    → entra en la sala → repite hasta muerte o salida.
    """
    while player.is_alive:
        current = dungeon.get_current_room()

        # ¿Llegamos a la salida?
        if current.room_type == RoomType.EXIT:
            enter_room(player, current, dungeon)
            break

        # Mostrar mapa + HUD
        clear()
        render_dungeon_map(dungeon)
        show_player_hud(player)
        pause(0.2)

        # Obtener movimientos disponibles
        moves = dungeon.get_available_moves()
        if not moves:
            show_message("No hay salidas. El dungeon te ha atrapado.", style=C["danger"])
            break

        # Mostrar opciones de movimiento + comandos extra
        choices = render_room_choices(dungeon)
        valid_keys = {k for k, _ in choices}

        show_event_choices([("m", "Ver mapa"), ("i", "Inventario"), ("q", "Abandonar run")])
        raw = get_player_input("¿A dónde vas?")
        key = raw.strip().lower()

        if key == "q":
            show_message("Abandonas. La oscuridad te acepta.", style=C["muted"])
            break

        if key == "m":
            clear()
            render_dungeon_map(dungeon, show_all=False)
            get_player_input("Pulsa Enter para continuar")
            continue

        if key == "i":
            from engine.systems.inventory import show_inventory_screen, handle_inventory_action
            while True:
                action = show_inventory_screen(player)
                if action is None:
                    break
                handle_inventory_action(player, action)
            continue

        if key not in valid_keys:
            show_message("Opción inválida.", style=C["danger"])
            continue

        # Mover al jugador
        chosen_room = next(r for k, r in choices if k == key)
        dungeon.move_to(chosen_room.room_id)

        # Entrar en la sala
        survived = enter_room(player, chosen_room, dungeon)
        if not survived:
            return   # muerte — se gestiona en main()


# ------------------------------------------------------------------ #
#  Main con RunManager (M7)                                            #
# ------------------------------------------------------------------ #

def run_game_loop(run_manager) -> tuple[bool, str]:
    """
    Ejecuta una run completa.
    Devuelve (es_muerte, causa).
    """
    from engine.ui.renderer import show_title_screen

    # Selección de clase
    player_class = select_class()
    player       = create_player(player_class)
    show_message(f"Has elegido: {player.display_name}", style=C["class_name"])
    pause(1.0)

    # HUD inicial
    clear()
    show_player_hud(player)
    get_player_input("Pulsa Enter para comenzar")

    # Intro narrativa
    intro_sequence(player)

    # Iniciar run en el manager
    run_manager.start_run(player)

    # Generar dungeon
    dungeon = DungeonGraph(seed=run_manager.seed, total_depth=6)
    show_message(f"Seed: {run_manager.seed}", style=C["muted"])
    pause(0.6)

    # Loop de navegación — la causa de muerte se detecta aquí
    cause   = "abandoned"
    victory = False

    navigation_loop(player, dungeon)

    if not player.is_alive:
        # Determinar causa de muerte
        room_type = player.get_flag("_death_room_type", "combat")
        if player.sanity <= 0:
            cause = "sanity"
        elif room_type == "boss":
            cause = "killed_by:el Señor de las Profundidades"
        elif room_type == "elite":
            cause = "killed_by:un Campeón Corrompido"
        else:
            cause = "killed_by:una criatura del dungeon"
    else:
        # Llegó a la salida
        victory = True
        cause   = "victory"

    run_manager.end_run(player, cause=cause, victory=victory)
    return not victory, cause


def main():
    from engine.core.run_manager import RunManager, show_run_history
    from engine.ui.renderer import show_title_screen

    show_title_screen()
    pause(1.0)
    show_message("Otro condenado. Otra vela.", style="italic dim white")
    pause(1.5)

    # Menú de inicio
    console.print()
    console.print("  [bold white]1[/bold white]  Nueva run")
    console.print("  [bold white]2[/bold white]  Ver historial")
    console.print("  [bold white]q[/bold white]  Salir")
    console.print()

    while True:
        raw = get_player_input("").strip().lower()
        if raw in ("1", "2", "q"):
            break

    if raw == "q":
        return
    if raw == "2":
        show_run_history()
        get_player_input("Pulsa Enter para continuar")
        main()
        return

    # Loop de runs
    while True:
        run_manager = RunManager()
        is_death, cause = run_game_loop(run_manager)
        action = run_manager.show_end_screen(is_death=is_death)

        if action == "r":
            continue        # nueva run, nuevo RunManager
        elif action == "h":
            show_run_history()
            get_player_input("Pulsa Enter para continuar")
            continue
        else:
            break           # salir

    show_message("La vela se apaga.", style="italic dim white")
    pause(1.0)


if __name__ == "__main__":
    main()