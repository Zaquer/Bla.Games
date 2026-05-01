"""
engine/systems/event_engine.py
M4 — Event Engine

Ejecuta eventos narrativos contra el estado del jugador.
No contiene ningún texto ni historia — eso vive en content/events/events_data.py.

Responsabilidades:
    - Filtrar qué opciones son visibles para el jugador actual
    - Aplicar consecuencias al player
    - Renderizar el evento en terminal usando el UI Renderer
    - Devolver un EventResult con lo que ocurrió (para logging y flags)
"""

from dataclasses import dataclass, field
from typing import Optional
import random

from engine.ui.renderer import (
    console,
    show_room_header,
    show_narrative,
    show_message,
    get_player_input,
    pause,
    clear,
    C,
)
from rich.text import Text
from rich.rule import Rule


# ------------------------------------------------------------------ #
#  Resultado de evento — para logging y encadenamiento futuro          #
# ------------------------------------------------------------------ #

@dataclass
class EventResult:
    event_id:       str
    choice_id:      str
    hp_delta:       int = 0
    sanity_delta:   int = 0
    gold_delta:     int = 0
    flags_set:      dict  = field(default_factory=dict)
    flags_cleared:  list  = field(default_factory=list)
    outcome_text:   str   = ""


# ------------------------------------------------------------------ #
#  Helpers de visibilidad                                              #
# ------------------------------------------------------------------ #

def _choice_is_visible(choice: dict, player_flags: dict) -> bool:
    """Una opción es visible si el jugador cumple sus condiciones."""
    vis = choice.get("visible_if", {})

    required = vis.get("required_flags", [])
    if any(not player_flags.get(f) for f in required):
        return False

    forbidden = vis.get("forbidden_flags", [])
    if any(player_flags.get(f) for f in forbidden):
        return False

    return True


def _get_visible_choices(event: dict, player_flags: dict) -> list[dict]:
    """Filtra y devuelve solo las opciones visibles para el jugador actual."""
    return [c for c in event["choices"] if _choice_is_visible(c, player_flags)]


# ------------------------------------------------------------------ #
#  Renderer de evento                                                  #
# ------------------------------------------------------------------ #

def _render_choices(choices: list[dict]) -> None:
    """Muestra las opciones numeradas con sus tags especiales."""
    console.print()
    for i, choice in enumerate(choices, 1):
        line = Text()
        line.append(f"  {i}  ", style="bold white")

        tag = choice.get("tag")
        if tag:
            line.append(f"{tag} ", style="bold yellow")

        line.append(choice["text"], style="white")
        console.print(line)
    console.print()


def _render_consequences_feedback(result: EventResult) -> None:
    """Muestra el feedback de stats tras aplicar consecuencias."""
    deltas = []
    if result.hp_delta != 0:
        sign  = "+" if result.hp_delta > 0 else ""
        color = C["success"] if result.hp_delta > 0 else C["danger"]
        deltas.append((f"{sign}{result.hp_delta} HP", color))

    if result.sanity_delta != 0:
        sign  = "+" if result.sanity_delta > 0 else ""
        color = C["success"] if result.sanity_delta > 0 else C["sanity_high"]
        deltas.append((f"{sign}{result.sanity_delta} Cordura", color))

    if result.gold_delta != 0:
        sign  = "+" if result.gold_delta > 0 else ""
        deltas.append((f"{sign}{result.gold_delta} oro", C["gold"]))

    if result.flags_set:
        for flag in result.flags_set:
            deltas.append((f"⚑ {flag}", C["flag"]))

    if not deltas:
        return

    console.print()
    line = Text()
    line.append("  ", style="")
    for i, (text, color) in enumerate(deltas):
        line.append(text, style=color)
        if i < len(deltas) - 1:
            line.append("  ·  ", style="dim white")
    console.print(line)
    console.print()


# ------------------------------------------------------------------ #
#  Motor de ejecución                                                  #
# ------------------------------------------------------------------ #

def run_event(event: dict, player, dungeon=None) -> EventResult:
    """
    Ejecuta un evento completo:
    1. Renderiza nombre y flavor text
    2. Filtra opciones visibles para este jugador
    3. Espera input válido
    4. Aplica consecuencias al player
    5. Muestra resultado narrativo
    6. Devuelve EventResult

    Si no hay ninguna opción visible (edge case), resuelve automáticamente
    con la primera opción sin condiciones como fallback.
    """
    clear()
    show_room_header(event["name"], depth=0)   # depth se sobreescribe desde el caller
    show_narrative(event["flavor_text"])
    pause(0.5)

    # Obtener opciones visibles
    visible = _get_visible_choices(event, player.flags)

    # Fallback: si no hay opciones visibles, tomar la primera sin condiciones
    if not visible:
        visible = [event["choices"][0]]

    # Mostrar opciones al jugador
    _render_choices(visible)

    # Input con validación
    while True:
        raw = get_player_input("¿Qué haces?")
        if raw.strip().isdigit():
            idx = int(raw.strip()) - 1
            if 0 <= idx < len(visible):
                chosen = visible[idx]
                break
        show_message("Opción inválida.", style=C["danger"])

    # Construir resultado
    cons = chosen.get("consequences", {})
    result = EventResult(
        event_id      = event["id"],
        choice_id     = chosen["id"],
        hp_delta      = cons.get("hp", 0),
        sanity_delta  = cons.get("sanity", 0),
        gold_delta    = cons.get("gold", 0),
        flags_set     = cons.get("set_flags", {}),
        flags_cleared = cons.get("clear_flags", []),
        outcome_text  = cons.get("outcome", ""),
    )

    # Aplicar consecuencias al player
    if result.hp_delta > 0:
        player.heal(result.hp_delta)
    elif result.hp_delta < 0:
        player.take_damage(abs(result.hp_delta))

    if result.sanity_delta > 0:
        player.restore_sanity(result.sanity_delta)
    elif result.sanity_delta < 0:
        player.lose_sanity(abs(result.sanity_delta))

    player.gold += result.gold_delta

    for flag, value in result.flags_set.items():
        player.set_flag(flag, value)

    for flag in result.flags_cleared:
        player.flags.pop(flag, None)

    # Mostrar resultado narrativo
    console.print()
    console.print(Rule(style="dim white"))
    show_narrative(result.outcome_text)
    pause(0.6)
    _render_consequences_feedback(result)
    pause(0.8)

    return result


# ------------------------------------------------------------------ #
#  Selector de evento para una sala                                    #
# ------------------------------------------------------------------ #

def pick_event_for_room(room, player) -> Optional[dict]:
    """
    Elige un evento apropiado para la sala actual.
    Prioriza eventos no vistos aún (sin flag de haberlos completado).
    Si la sala tiene event_id asignado, lo usa directamente.
    Si no, elige uno elegible aleatoriamente.
    """
    from content.events.events_data import get_event_by_id, get_eligible_events

    # Si la sala tiene evento asignado explícitamente, usarlo
    if room.event_id:
        event = get_event_by_id(room.event_id)
        if event:
            return event

    # Elegir aleatoriamente entre los elegibles
    eligible = get_eligible_events(room.depth, player.flags)
    if not eligible:
        return None

    return random.choice(eligible)
