"""
engine/ui/map_renderer.py
Renderiza el grafo del dungeon como minimapa en la terminal usando Rich.

Diseño visual:
    - Cada capa = una fila horizontal
    - Salas = nodos con icono y nombre corto
    - Conexiones = líneas ASCII entre nodos
    - Sala actual = destacada con borde
    - Salas desconocidas = bloques grises
"""

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich import box

from engine.core.dungeon import (
    DungeonGraph, Room, RoomType, RoomState,
    ROOM_ICONS, ROOM_COLORS,
)

console = Console()


# ------------------------------------------------------------------ #
#  Leyenda                                                             #
# ------------------------------------------------------------------ #

def _render_legend() -> Text:
    legend = Text()
    legend.append("  Leyenda: ", style="dim white")
    items = [
        ("☠", "red",          "Combate"),
        ("★", "bold red",     "Élite"),
        ("?", "yellow",       "Evento"),
        ("♨", "green",        "Descanso"),
        ("$", "bold yellow",  "Tesoro"),
        ("◈", "bold magenta", "Jefe"),
        ("▼", "bold cyan",    "Salida"),
        ("▣", "white",        "Entrada"),
    ]
    for icon, color, label in items:
        legend.append(f"{icon} ", style=color)
        legend.append(f"{label}  ", style="dim white")
    return legend


# ------------------------------------------------------------------ #
#  Render de un nodo individual                                        #
# ------------------------------------------------------------------ #

def _node_text(room: Room, is_current: bool) -> Text:
    """Genera el texto de un nodo del mapa."""
    t = Text()

    if room.state == RoomState.UNKNOWN:
        t.append(" ░░░ ", style="dim white")
        return t

    icon  = ROOM_ICONS.get(room.room_type, "?")
    color = ROOM_COLORS.get(room.room_type, "white")

    if room.state in (RoomState.VISITED, RoomState.CLEARED):
        color = "dim white"

    if is_current:
        t.append(f"[{icon}]", style=f"bold reverse {color}")
    else:
        t.append(f" {icon} ", style=color)

    return t


def _node_label(room: Room, is_current: bool) -> Text:
    """Nombre corto del nodo (máx ~14 chars)."""
    t = Text()

    if room.state == RoomState.UNKNOWN:
        t.append("   ???   ", style="dim white")
        return t

    name = room.name if len(room.name) <= 14 else room.name[:12] + "…"
    color = ROOM_COLORS.get(room.room_type, "white")

    if room.state in (RoomState.VISITED, RoomState.CLEARED):
        color = "dim white"

    style = f"bold {color}" if is_current else color
    t.append(f" {name} ", style=style)
    return t


# ------------------------------------------------------------------ #
#  Render del mapa completo                                            #
# ------------------------------------------------------------------ #

def render_dungeon_map(dungeon: DungeonGraph, show_all: bool = False) -> None:
    """
    Renderiza el minimapa completo del dungeon capa por capa.

    show_all=True: modo debug, muestra todas las salas (ignora el fog of war).
    show_all=False: solo muestra salas descubiertas.
    """
    console.print()

    lines: list[Text] = []

    for depth_idx, layer in enumerate(dungeon.layers):
        # --- Fila de iconos ---
        icon_row = Text()
        icon_row.append(f"  {depth_idx:>2}  ", style="dim white")

        for i, room_id in enumerate(layer):
            room       = dungeon.rooms[room_id]
            is_current = (room_id == dungeon.current_room)

            if not show_all and room.state == RoomState.UNKNOWN:
                icon_row.append(" ░ ", style="dim white")
            else:
                icon_row.append_text(_node_text(room, is_current))

            # Separador entre nodos de la misma capa
            if i < len(layer) - 1:
                icon_row.append("  ", style="dim white")

        lines.append(icon_row)

        # --- Fila de nombres ---
        name_row = Text()
        name_row.append("       ", style="dim white")

        for i, room_id in enumerate(layer):
            room = dungeon.rooms[room_id]
            if not show_all and room.state == RoomState.UNKNOWN:
                name_row.append("  ···  ", style="dim white")
            else:
                name_row.append_text(_node_label(room, room_id == dungeon.current_room))
            if i < len(layer) - 1:
                name_row.append(" ", style="dim white")

        lines.append(name_row)

        # --- Conectores hacia la siguiente capa ---
        if depth_idx < len(dungeon.layers) - 1:
            conn_row = Text()
            conn_row.append("       ", style="dim white")

            for i, room_id in enumerate(layer):
                room = dungeon.rooms[room_id]
                has_visible_conn = any(
                    dungeon.rooms[cid].state != RoomState.UNKNOWN
                    for cid in room.connections
                ) or show_all

                if room.state != RoomState.UNKNOWN and has_visible_conn:
                    conn_row.append("  │  ", style="dim white")
                else:
                    conn_row.append("     ", style="dim white")

                if i < len(layer) - 1:
                    conn_row.append("  ", style="dim white")

            lines.append(conn_row)
            lines.append(Text())   # línea en blanco entre capas

    # --- Ensamblar en panel ---
    content = Text()
    for line in lines:
        content.append_text(line)
        content.append("\n")

    content.append("\n")
    content.append_text(_render_legend())

    # Stats del dungeon
    stats = Text()
    stats.append(
        f"\n  Salas: {dungeon.discovered_rooms}/{dungeon.total_rooms} descubiertas  "
        f"· {dungeon.cleared_rooms} resueltas",
        style="dim white"
    )
    content.append_text(stats)

    console.print(Panel(
        content,
        title="[dim white]— Mapa del Dungeon —[/dim white]",
        border_style="dim white",
        box=box.SIMPLE_HEAVY,
    ))
    console.print()


# ------------------------------------------------------------------ #
#  Render de elección de sala                                          #
# ------------------------------------------------------------------ #

def render_room_choices(dungeon: DungeonGraph) -> list[tuple[str, Room]]:
    """
    Muestra las salas disponibles desde la posición actual como opciones numeradas.
    Devuelve lista de (key, Room) para que main.py pueda procesar la elección.
    """
    moves   = dungeon.get_available_moves()
    choices = []

    console.print("  [dim white]Caminos disponibles:[/dim white]\n")

    for i, room in enumerate(moves, 1):
        key   = str(i)
        icon  = ROOM_ICONS.get(room.room_type, "?")
        color = ROOM_COLORS.get(room.room_type, "white")

        if room.state in (RoomState.VISITED, RoomState.CLEARED):
            color = "dim white"

        label = Text()
        label.append(f"  {key}  ", style="bold white")
        label.append(f"{icon} ", style=color)

        if room.state == RoomState.UNKNOWN:
            label.append("Camino desconocido", style="dim white")
        elif room.state == RoomState.VISIBLE:
            label.append(f"{room.room_type.value.upper()}", style=color)
            label.append(f"  — {room.name}", style="dim white")
        else:
            label.append(f"{room.name}", style=color)
            label.append(f"  [ya visitada]", style="dim white")

        console.print(label)
        choices.append((key, room))

    console.print()
    return choices
