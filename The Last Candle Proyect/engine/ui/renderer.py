"""
engine/ui/renderer.py
M2 — UI Renderer
Toda la capa visual del juego usando Rich.
Un solo punto de verdad para colores, paneles y arte ASCII.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.rule import Rule
from rich.prompt import Prompt
from rich import box
from rich.padding import Padding
import time

# ------------------------------------------------------------------ #
#  Instancia global de consola                                         #
# ------------------------------------------------------------------ #
console = Console()

# ------------------------------------------------------------------ #
#  Paleta de colores — tema oscuro / dark fantasy                      #
# ------------------------------------------------------------------ #
C = {
    "title":        "bold white",
    "subtitle":     "dim white",
    "hp_high":      "#c0392b",      # rojo oscuro — vida
    "hp_low":       "#7f0000",      # rojo muy oscuro — vida crítica
    "sanity_high":  "#2980b9",      # azul — cordura
    "sanity_low":   "#1a3a5c",      # azul oscuro — cordura crítica
    "gold":         "#f39c12",      # ámbar — oro
    "lore":         "italic dim white",
    "danger":       "bold red",
    "warning":      "yellow",
    "success":      "bold green",
    "muted":        "dim white",
    "class_name":   "bold cyan",
    "flag":         "dim cyan",
    "depth":        "bold magenta",
    "border":       "dim white",
    "prompt":       "bold white",
    "stat_label":   "dim white",
    "stat_value":   "white",
    "ability":      "bold yellow",
    "dead":         "bold red",
    "broken":       "bold red",
    "stressed":     "yellow",
    "calm":         "dim white",
}

# ------------------------------------------------------------------ #
#  Arte ASCII                                                          #
# ------------------------------------------------------------------ #

ASCII_TITLE = """
[dim white]
  ████████╗██╗  ██╗███████╗    ██╗      █████╗ ███████╗████████╗
  ╚══██╔══╝██║  ██║██╔════╝    ██║     ██╔══██╗██╔════╝╚══██╔══╝
     ██║   ███████║█████╗      ██║     ███████║███████╗   ██║   
     ██║   ██╔══██║██╔══╝      ██║     ██╔══██║╚════██║   ██║   
     ██║   ██║  ██║███████╗    ███████╗██║  ██║███████║   ██║   
     ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝   

                ██████╗ █████╗ ███╗   ██╗██████╗ ██╗     ███████╗
               ██╔════╝██╔══██╗████╗  ██║██╔══██╗██║     ██╔════╝
               ██║     ███████║██╔██╗ ██║██║  ██║██║     █████╗  
               ██║     ██╔══██║██║╚██╗██║██║  ██║██║     ██╔══╝  
               ╚██████╗██║  ██║██║ ╚████║██████╔╝███████╗███████╗
                ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚══════╝
[/dim white]"""

ASCII_SKULL = """[dim white]
    ░░░░░░░░░
  ░░  ░░░░  ░░
  ░░  ░░░░  ░░
    ░░░░░░░░░
      ░░░░░
    ░░░░░░░░░[/dim white]"""

ASCII_CANDLE = """[dim yellow]
       )
      ) \\
     / ) (
     \\(_)/
   .-'-.
  /|6 6|\\
 | | - | |
  \\|-=-|/
   '---'[/dim yellow]"""

ASCII_FLAME = "[bold yellow]🕯[/bold yellow]"

# ------------------------------------------------------------------ #
#  Helpers de barra de progreso                                        #
# ------------------------------------------------------------------ #

def _build_bar(current: int, maximum: int, width: int = 12,
               color_high: str = "", color_low: str = "") -> Text:
    """Genera una barra tipo ████░░░░ con color dinámico."""
    ratio   = current / maximum if maximum > 0 else 0
    filled  = round(ratio * width)
    empty   = width - filled
    color   = color_high if ratio > 0.35 else color_low

    bar = Text()
    bar.append("█" * filled, style=color)
    bar.append("░" * empty,  style="dim white")
    return bar


def _hp_bar(hp: int, hp_max: int) -> Text:
    return _build_bar(hp, hp_max, color_high=C["hp_high"], color_low=C["hp_low"])


def _sanity_bar(sanity: int, sanity_max: int) -> Text:
    return _build_bar(sanity, sanity_max, color_high=C["sanity_high"], color_low=C["sanity_low"])


# ------------------------------------------------------------------ #
#  Pantallas principales                                               #
# ------------------------------------------------------------------ #

def show_title_screen() -> None:
    """Pantalla de título con arte ASCII y tagline."""
    console.clear()
    console.print(ASCII_TITLE)
    console.print(
        Padding(
            Text("— Un nuevo condenado despierta —", style="italic dim white", justify="center"),
            (0, 0, 2, 0)
        )
    )
    console.print(Rule(style="dim white"))


def show_death_screen(player) -> None:
    """Pantalla de muerte. Debe doler."""
    console.clear()
    time.sleep(0.5)
    console.print()
    console.print(ASCII_SKULL)
    console.print()

    msg = Text(justify="center")
    msg.append(f"\n  {player.display_name.upper()} HA MUERTO\n", style="bold red")
    msg.append(f"\n  Salas exploradas: {player.rooms_explored}", style="dim white")
    msg.append(f"\n  Criaturas caídas: {player.kills}", style="dim white")
    msg.append(f"\n  Profundidad:      {player.depth}", style="dim white")
    msg.append("\n\n  La vela se apaga.\n", style="italic dim white")

    console.print(Panel(msg, border_style="dim red", box=box.HEAVY))
    console.print()


def show_class_selection(class_definitions: dict) -> None:
    """Muestra la tabla de selección de clase."""
    console.print()
    console.print(Rule("— Elige tu condena —", style="dim white"))
    console.print()

    table = Table(
        box=box.SIMPLE_HEAVY,
        border_style="dim white",
        header_style="bold dim white",
        show_lines=True,
        expand=False,
    )
    table.add_column("#",           style="dim white",  width=3,  justify="center")
    table.add_column("Clase",       style="bold cyan",  width=18)
    table.add_column("HP",          style=C["hp_high"], width=5,  justify="center")
    table.add_column("Cordura",     style=C["sanity_high"], width=7, justify="center")
    table.add_column("Fuerza",      style="white",      width=7,  justify="center")
    table.add_column("Agilidad",    style="white",      width=8,  justify="center")
    table.add_column("Arcano",      style="magenta",    width=7,  justify="center")
    table.add_column("Lore",        style="italic dim white", width=45)

    from engine.core.player import PlayerClass
    for i, pc in enumerate(PlayerClass, 1):
        d = class_definitions[pc]
        table.add_row(
            str(i),
            d["display_name"],
            str(d["hp_max"]),
            str(d["sanity_max"]),
            str(d["strength"]),
            str(d["agility"]),
            str(d["arcane"]),
            d["lore"],
        )

    console.print(table)
    console.print()


def show_player_hud(player) -> None:
    """
    HUD principal del jugador.
    Muestra stats, barras de HP/Cordura, oro, profundidad y flags activos.
    """
    # --- Columna izquierda: identidad ---
    identity = Text()
    identity.append(f"  {player.display_name.upper()}\n", style=C["class_name"])
    identity.append(f"  {player.lore}\n\n", style=C["lore"])
    identity.append(f"  Profundidad: ", style=C["stat_label"])
    identity.append(f"{'▼' * player.depth if player.depth else '—'}\n", style=C["depth"])
    identity.append(f"  Salas:       ", style=C["stat_label"])
    identity.append(f"{player.rooms_explored}\n", style=C["stat_value"])
    identity.append(f"  Bajas:       ", style=C["stat_label"])
    identity.append(f"{player.kills}\n", style=C["stat_value"])

    # --- Columna central: stats vitales ---
    vitals = Text()
    vitals.append("  VIDA        ", style=C["stat_label"])
    vitals.append_text(_hp_bar(player.hp, player.hp_max))
    vitals.append(f"  {player.hp}/{player.hp_max}", style=C["hp_high"])

    hp_label = f"  [{player.hp_level.upper()}]\n"
    hp_style = C["danger"] if player.hp_level == "moribundo" else C["muted"]
    vitals.append(hp_label, style=hp_style)

    vitals.append("\n  CORDURA     ", style=C["stat_label"])
    vitals.append_text(_sanity_bar(player.sanity, player.sanity_max))
    vitals.append(f"  {player.sanity}/{player.sanity_max}", style=C["sanity_high"])

    san_label = f"  [{player.stress_level.upper()}]\n"
    san_style = C["broken"] if player.stress_level == "quebrado" else \
                C["stressed"] if player.stress_level == "al_limite" else C["muted"]
    vitals.append(san_label, style=san_style)

    vitals.append("\n  ORO         ", style=C["stat_label"])
    vitals.append(f"{player.gold} monedas malditas\n", style=C["gold"])

    # --- Columna derecha: stats de combate + habilidades ---
    combat = Text()
    combat.append("  FUERZA   ", style=C["stat_label"])
    combat.append(f"{player.strength:>3}\n", style=C["stat_value"])
    combat.append("  AGILIDAD ", style=C["stat_label"])
    combat.append(f"{player.agility:>3}\n", style=C["stat_value"])
    combat.append("  ARCANO   ", style=C["stat_label"])
    combat.append(f"{player.arcane:>3}\n\n", style=C["stat_value"])

    if player.abilities:
        combat.append("  HABILIDADES\n", style=C["stat_label"])
        for ab in player.abilities:
            combat.append(f"  ✦ {ab}\n", style=C["ability"])

    if player.flags:
        combat.append("\n  FLAGS ACTIVOS\n", style=C["stat_label"])
        for k, v in player.flags.items():
            combat.append(f"  ⚑ {k}\n", style=C["flag"])

    # --- Ensamblar en columnas ---
    panel_id     = Panel(identity, border_style="dim white", box=box.SIMPLE)
    panel_vitals = Panel(vitals,   border_style="dim white", box=box.SIMPLE)
    panel_combat = Panel(combat,   border_style="dim white", box=box.SIMPLE)

    console.print(Columns([panel_id, panel_vitals, panel_combat], equal=False))


# ------------------------------------------------------------------ #
#  Mensajes de juego                                                   #
# ------------------------------------------------------------------ #

def show_room_header(room_name: str, depth: int) -> None:
    depth_str = f"▼ Profundidad {depth}" if depth else "▼ Entrada"
    console.print(Rule(f"[dim white]{depth_str}[/dim white]", style="dim white"))
    console.print(f"\n  [bold white]{room_name}[/bold white]\n")


def show_narrative(text: str) -> None:
    """Texto narrativo descriptivo — aparece letra a letra para tensión."""
    console.print(f"  [italic dim white]{text}[/italic dim white]\n")


def show_event_choices(choices: list[tuple[str, str]]) -> None:
    """
    Muestra opciones de evento.
    choices: lista de (key, descripción) ej: [("1", "Avanzar"), ("2", "Huir")]
    """
    console.print()
    for key, desc in choices:
        console.print(f"  [{C['warning']}]{key}[/{C['warning']}]  {desc}")
    console.print()


def get_player_input(prompt_text: str = "¿Qué haces?") -> str:
    return Prompt.ask(f"\n  [bold white]{prompt_text}[/bold white]")


def show_combat_action(actor: str, action: str, damage: int = 0,
                       is_player: bool = True) -> None:
    """Línea de log de combate."""
    color = C["warning"] if is_player else C["danger"]
    dmg_str = f" → [bold]{damage}[/bold] de daño" if damage else ""
    console.print(f"  [{color}]{'▶' if is_player else '◀'} {actor}[/{color}]  {action}{dmg_str}")


def show_message(text: str, style: str = "white") -> None:
    console.print(f"\n  [{style}]{text}[/{style}]\n")


def pause(seconds: float = 1.0) -> None:
    time.sleep(seconds)


def clear() -> None:
    console.clear()
