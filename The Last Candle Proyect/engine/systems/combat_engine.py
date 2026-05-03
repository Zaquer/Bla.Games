"""
engine/systems/combat_engine.py
M5 — Combat Engine

Sistema de combate por turnos con:
    - Fórmula de daño basada en stats (no puro RNG)
    - Estados alterados con duración
    - Habilidades de clase con costes reales
    - Dodge basado en agilidad
    - Críticos con efecto narrativo
    - UI rica: arte ASCII del enemigo, barras de HP, log de combate
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import random

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns
from rich.rule import Rule
from rich import box

from engine.ui.renderer import (
    show_narrative, show_message, get_player_input,
    pause, clear, C, console,
    show_room_header, show_player_hud,
)

# ------------------------------------------------------------------ #
#  Estados alterados                                                   #
# ------------------------------------------------------------------ #

STATUS_COLORS: dict[str, str] = {
    "BLEEDING":  "red",
    "MARKED":    "magenta",
    "STUNNED":   "yellow",
    "WEAKENED":  "dim red",
    "TERRIFIED": "bold red",
}

STATUS_LABELS: dict[str, str] = {
    "BLEEDING":  "⚡ Sangrando",
    "MARKED":    "◎ Marcado",
    "STUNNED":   "✕ Aturdido",
    "WEAKENED":  "↓ Debilitado",
    "TERRIFIED": "☠ Aterrorizado",
}


@dataclass
class StatusEffect:
    name:     str
    duration: int   # turnos restantes (-1 = permanente hasta combate)

    @property
    def label(self) -> str:
        return STATUS_LABELS.get(self.name, self.name)

    @property
    def color(self) -> str:
        return STATUS_COLORS.get(self.name, "white")


# ------------------------------------------------------------------ #
#  Estado del combate                                                  #
# ------------------------------------------------------------------ #

@dataclass
class CombatState:
    player:           object             # Player instance
    enemy_def:        dict               # definición del enemigo desde enemies_data
    enemy_hp:         int
    enemy_hp_max:     int
    enemy_statuses:   list[StatusEffect] = field(default_factory=list)
    player_statuses:  list[StatusEffect] = field(default_factory=list)
    turn:             int = 1
    combat_log:       list[str] = field(default_factory=list)
    player_defending: bool = False       # acción de defensa activa este turno

    def get_enemy_status(self, name: str) -> Optional[StatusEffect]:
        return next((s for s in self.enemy_statuses if s.name == name), None)

    def get_player_status(self, name: str) -> Optional[StatusEffect]:
        return next((s for s in self.player_statuses if s.name == name), None)

    def apply_status_to_enemy(self, name: str, duration: int = 2) -> None:
        existing = self.get_enemy_status(name)
        if existing:
            existing.duration = max(existing.duration, duration)
        else:
            self.enemy_statuses.append(StatusEffect(name, duration))

    def apply_status_to_player(self, name: str, duration: int = 2) -> None:
        existing = self.get_player_status(name)
        if existing:
            existing.duration = max(existing.duration, duration)
        else:
            self.player_statuses.append(StatusEffect(name, duration))

    def tick_statuses(self) -> list[str]:
        """Aplica efectos de estados y reduce duración. Devuelve mensajes de log."""
        messages = []

        # Sangrado del jugador
        if ps := self.get_player_status("BLEEDING"):
            self.player.take_damage(2)
            messages.append(f"[red]Sangras — pierdes 2 HP.[/red]")

        # Sangrado del enemigo
        if es := self.get_enemy_status("BLEEDING"):
            self.enemy_hp = max(0, self.enemy_hp - 2)
            messages.append(f"[red]{self.enemy_def['name']} sangra — pierde 2 HP.[/red]")

        # Terror del jugador
        if pt := self.get_player_status("TERRIFIED"):
            self.player.lose_sanity(1)
            messages.append(f"[bold red]El terror drena tu cordura — pierdes 1.[/bold red]")

        # Decrementar duraciones y eliminar expirados
        for s in self.enemy_statuses:
            s.duration -= 1
        for s in self.player_statuses:
            s.duration -= 1
        self.enemy_statuses  = [s for s in self.enemy_statuses  if s.duration > 0]
        self.player_statuses = [s for s in self.player_statuses if s.duration > 0]

        return messages

    def log(self, msg: str) -> None:
        self.combat_log.append(msg)


# ------------------------------------------------------------------ #
#  Fórmulas de combate                                                 #
# ------------------------------------------------------------------ #

def _roll_damage(base_min: int, base_max: int, mult: float, rng: random.Random) -> int:
    """Daño base con multiplicador. Mínimo 1."""
    raw = rng.randint(base_min, base_max)
    return max(1, int(raw * mult))


def _player_damage(player, rng: random.Random, crit: bool = False) -> tuple[int, bool]:
    """
    Calcula daño del jugador.
    Devuelve (daño, fue_crítico).
    Crit: 10% base + 2% por punto de agilidad.
    """
    crit_chance = 0.10 + player.agility * 0.02
    is_crit     = crit or rng.random() < crit_chance

    variance = rng.randint(-2, 3)
    dmg      = max(1, player.strength + variance)

    if is_crit:
        dmg = int(dmg * 1.5)

    return dmg, is_crit


def _enemy_damage(enemy_def: dict, mult: float, rng: random.Random) -> int:
    return _roll_damage(enemy_def["damage_min"], enemy_def["damage_max"], mult, rng)


def _player_dodges(player, rng: random.Random) -> bool:
    """Probabilidad de esquivar basada en agilidad. Máx 40%."""
    dodge_chance = min(0.40, player.agility * 0.05)
    return rng.random() < dodge_chance


# ------------------------------------------------------------------ #
#  Definiciones de habilidades de clase                                #
# ------------------------------------------------------------------ #

ABILITIES: dict[str, dict] = {
    "golpe_desesperado": {
        "display":     "Golpe Desesperado",
        "description": "Daño ×1.4 — cuesta 2 Cordura",
        "dmg_mult":    1.4,
        "cost_sanity": 2,
        "cost_hp":     0,
        "forced_crit": False,
        "applies_status_enemy": None,
    },
    "maldicion_menor": {
        "display":     "Maldición Menor",
        "description": "Daño ×0.8 + aplica MARKED al enemigo — cuesta 3 HP",
        "dmg_mult":    0.8,
        "cost_sanity": 0,
        "cost_hp":     3,
        "forced_crit": False,
        "applies_status_enemy": "MARKED",
    },
    "golpe_bajo": {
        "display":     "Golpe Bajo",
        "description": "Daño ×1.0 — crit garantizado. +50% daño si el enemigo está MARKED",
        "dmg_mult":    1.0,
        "cost_sanity": 0,
        "cost_hp":     0,
        "forced_crit": True,
        "applies_status_enemy": None,
    },
    "penitencia": {
        "display":     "Penitencia",
        "description": "Te infligues 3 HP → daño ×1.8",
        "dmg_mult":    1.8,
        "cost_sanity": 0,
        "cost_hp":     3,
        "forced_crit": False,
        "applies_status_enemy": None,
    },
    # Habilidad genérica por si el player no tiene ninguna registrada
    "ataque_basico": {
        "display":     "Ataque Básico",
        "description": "Daño ×1.0 — sin coste",
        "dmg_mult":    1.0,
        "cost_sanity": 0,
        "cost_hp":     0,
        "forced_crit": False,
        "applies_status_enemy": None,
    },
}


# ------------------------------------------------------------------ #
#  Renderizado de combate                                              #
# ------------------------------------------------------------------ #

def _render_enemy_panel(state: CombatState) -> Panel:
    """Panel izquierdo: arte ASCII + HP + estados del enemigo."""
    enemy  = state.enemy_def
    hp_pct = state.enemy_hp / state.enemy_hp_max

    # Barra de HP del enemigo
    bar_width = 14
    filled    = round(hp_pct * bar_width)
    empty     = bar_width - filled
    hp_color  = "bold red" if hp_pct > 0.35 else "dim red"

    content = Text()
    content.append(f"\n{enemy['ascii_art']}\n\n", style="dim white")
    content.append(f"  {enemy['name']}\n", style="bold red")
    content.append(f"  {enemy['flavor']}\n\n", style="italic dim white")
    content.append("  HP  ", style="dim white")
    content.append("█" * filled, style=hp_color)
    content.append("░" * empty,  style="dim white")
    content.append(f"  {state.enemy_hp}/{state.enemy_hp_max}\n", style=hp_color)

    if state.enemy_statuses:
        content.append("\n  ", style="")
        for s in state.enemy_statuses:
            content.append(f"{s.label}({s.duration}) ", style=s.color)
        content.append("\n")

    return Panel(content, border_style="dim red", box=box.SIMPLE_HEAVY)


def _render_player_status_bar(state: CombatState) -> Text:
    """Línea compacta con estados del jugador."""
    if not state.player_statuses:
        return Text()
    line = Text()
    line.append("  Tu estado: ", style="dim white")
    for s in state.player_statuses:
        line.append(f"{s.label}({s.duration}) ", style=s.color)
    return line


def _render_combat_screen(state: CombatState) -> None:
    """Pantalla completa de combate."""
    clear()
    console.print(Rule(f"[dim white]— Turno {state.turn} —[/dim white]", style="dim white"))
    console.print()

    # Panel enemigo
    console.print(_render_enemy_panel(state))

    # Estado del jugador
    player = state.player
    hp_pct  = player.hp / player.hp_max
    san_pct = player.sanity / player.sanity_max

    bar_w = 10
    hp_bar  = "█" * round(hp_pct * bar_w)  + "░" * (bar_w - round(hp_pct * bar_w))
    san_bar = "█" * round(san_pct * bar_w) + "░" * (bar_w - round(san_pct * bar_w))

    hp_col  = C["hp_high"]  if hp_pct  > 0.35 else C["hp_low"]
    san_col = C["sanity_high"] if san_pct > 0.35 else C["sanity_low"]

    stats = Text()
    stats.append(f"\n  {player.display_name}  ", style="bold cyan")
    stats.append(f"HP ", style="dim white")
    stats.append(hp_bar, style=hp_col)
    stats.append(f" {player.hp}/{player.hp_max}  ", style=hp_col)
    stats.append(f"COR ", style="dim white")
    stats.append(san_bar, style=san_col)
    stats.append(f" {player.sanity}/{player.sanity_max}  ", style=san_col)
    stats.append(f"ORO {player.gold}", style=C["gold"])

    if state.player_statuses:
        stats.append("\n  ", style="")
        for s in state.player_statuses:
            stats.append(f"{s.label}({s.duration}) ", style=s.color)

    console.print(stats)

    # Últimas líneas del log de combate (máx 4)
    if state.combat_log:
        console.print()
        console.print(Rule(style="dim white"))
        for line in state.combat_log[-4:]:
            console.print(f"  {line}")

    console.print()


def _render_action_menu(state: CombatState) -> list[tuple[str, str]]:
    """
    Muestra el menú de acciones y devuelve las opciones disponibles.
    Formato: lista de (key, acción_id)
    """
    player   = state.player
    stunned  = state.get_player_status("STUNNED") is not None
    weakened = state.get_player_status("WEAKENED") is not None

    options = []
    menu    = Text()
    menu.append("  Acciones:\n", style="dim white")

    if stunned:
        menu.append("  [Aturdido — pierdes este turno]\n", style="yellow")
        console.print(menu)
        return []

    # 1. Atacar
    str_effective = max(1, player.strength - (2 if weakened else 0))
    menu.append("  1  ", style="bold white")
    menu.append("Atacar", style="white")
    menu.append(f"  (FUE {str_effective}, crit {min(40, 10 + player.agility * 2)}%)\n", style="dim white")
    options.append(("1", "attack"))

    # 2. Habilidad de clase
    if player.abilities:
        ab_id   = player.abilities[0]
        ab_def  = ABILITIES.get(ab_id, ABILITIES["ataque_basico"])
        cost_str = ""
        if ab_def["cost_sanity"]:
            cost_str += f"-{ab_def['cost_sanity']} COR"
        if ab_def["cost_hp"]:
            cost_str += f"  -{ab_def['cost_hp']} HP"
        menu.append("  2  ", style="bold white")
        menu.append(f"{ab_def['display']}", style=C["ability"])
        menu.append(f"  {ab_def['description']}", style="dim white")
        if cost_str:
            menu.append(f"  [{cost_str}]", style="dim red")
        menu.append("\n")
        options.append(("2", "ability"))

    # 3. Defender
    menu.append("  3  ", style="bold white")
    menu.append("Defender", style="white")
    menu.append(f"  (reduce próximo golpe en {player.agility} pts + +10% dodge)\n", style="dim white")
    options.append(("3", "defend"))

    console.print(menu)
    return options


# ------------------------------------------------------------------ #
#  Resolución de acciones                                              #
# ------------------------------------------------------------------ #

def _resolve_player_attack(state: CombatState, rng: random.Random,
                            ability_id: Optional[str] = None) -> None:
    player   = state.player
    weakened = state.get_player_status("WEAKENED") is not None

    # Obtener definición de habilidad
    if ability_id:
        ab = ABILITIES.get(ability_id, ABILITIES["ataque_basico"])
    else:
        ab = ABILITIES["ataque_basico"]

    # Costes de la habilidad
    if ab["cost_sanity"] > 0:
        player.lose_sanity(ab["cost_sanity"])
    if ab["cost_hp"] > 0:
        player.take_damage(ab["cost_hp"])

    # Daño base
    str_effective = max(1, player.strength - (2 if weakened else 0))
    dmg, is_crit  = _player_damage(player, rng, crit=ab["forced_crit"])

    # Aplicar multiplicador de habilidad
    dmg = max(1, int(dmg * ab["dmg_mult"]))

    # Bonus si enemigo está MARKED y es golpe_bajo
    if ability_id == "golpe_bajo" and state.get_enemy_status("MARKED"):
        dmg = int(dmg * 1.5)
        state.log(f"[magenta]¡Objetivo marcado! Daño aumentado.[/magenta]")

    # Bonus general por MARKED (+25%)
    if state.get_enemy_status("MARKED") and ability_id != "golpe_bajo":
        dmg = int(dmg * 1.25)

    state.enemy_hp = max(0, state.enemy_hp - dmg)

    # Aplicar estado al enemigo si la habilidad lo tiene
    if ab["applies_status_enemy"]:
        state.apply_status_to_enemy(ab["applies_status_enemy"])
        state.log(f"[{STATUS_COLORS[ab['applies_status_enemy']]}]"
                  f"Aplicas {STATUS_LABELS[ab['applies_status_enemy']]} al enemigo.[/]")

    # Aguja del Marcador: ataques básicos aplican MARKED automáticamente
    if not ability_id:
        weapon_id = player.equipment.get("weapon")
        if weapon_id:
            from content.items.items_data import get_item as _gi
            weapon = _gi(weapon_id)
            if weapon and weapon.get("equip_effect", {}).get("attack_applies_marked"):
                state.apply_status_to_enemy("MARKED", duration=2)
                state.log(f"[magenta]Aguja del Marcador — MARKED aplicado.[/magenta]")

    # Collar de Dientes: si el enemigo cae, restaura cordura
    if state.enemy_hp <= 0:
        trinket_id = player.equipment.get("trinket")
        if trinket_id:
            from content.items.items_data import get_item as _gi2
            trinket = _gi2(trinket_id)
            restore = trinket.get("equip_effect", {}).get("kill_restores_sanity", 0) if trinket else 0
            if restore:
                gained = player.restore_sanity(restore)
                state.log(f"[cyan]Collar de Dientes — +{gained} Cordura.[/cyan]")

    # Log
    crit_str = "  [bold yellow]¡CRÍTICO![/bold yellow]" if is_crit else ""
    ab_name  = ab["display"] if ability_id else "Ataque"
    state.log(f"[{C['warning']}]▶ {ab_name}[/{C['warning']}] → "
              f"[bold]{dmg}[/bold] de daño.{crit_str}")


def _resolve_enemy_action(state: CombatState, rng: random.Random) -> None:
    player  = state.player
    enemy   = state.enemy_def

    # Elegir acción ponderada
    actions = enemy["actions"]
    weights = [a["weight"] for a in actions]
    action  = rng.choices(actions, weights=weights, k=1)[0]

    # El boss tiende a usar acciones más duras cuando está bajo de HP
    if state.enemy_hp / state.enemy_hp_max < 0.3 and enemy.get("boss"):
        heavy = [a for a in actions if a["dmg_mult"] >= 1.2]
        if heavy:
            action = rng.choice(heavy)

    # Dodge
    if _player_dodges(player, rng):
        state.log(f"[{C['success']}]◀ {enemy['name']} — {action['text']}.[/{C['success']}]  "
                  f"[{C['success']}]¡Esquivas![/{C['success']}]")
        return

    # Daño físico
    if action["dmg_mult"] > 0:
        # Larva Abismal: escala daño con el turno actual
        turn_mult = 1.0
        if action.get("scales_with_turns"):
            turn_mult = 1.0 + (state.turn - 1) * 0.15
            if turn_mult > 1.0:
                state.log(f"[dim red]La larva crece con cada turno (×{turn_mult:.1f}).[/dim red]")

        dmg = _enemy_damage(enemy, action["dmg_mult"] * turn_mult, rng)

        # Cap sistémico: ningún golpe puede superar el 55% del HP máximo.
        # Evita one-shots desde HP completo — el jugador siempre tiene al menos
        # un turno para reaccionar.
        dmg_cap = max(1, int(player.hp_max * 0.55))
        dmg = min(dmg, dmg_cap)

        # Reducir si el jugador está defendiendo
        if state.player_defending:
            dmg = max(1, dmg - player.agility)
            state.log(f"[dim white]Defensa reduce el golpe.[/dim white]")

        # Cota del Mártir: -2 daño cuando HP < 40%
        armor_id = player.equipment.get("armor")
        if armor_id:
            from content.items.items_data import get_item as _gi3
            armor = _gi3(armor_id)
            if armor and armor.get("equip_effect", {}).get("low_hp_defense"):
                if player.hp / player.hp_max < 0.40:
                    dmg = max(1, dmg - 2)
                    state.log(f"[dim white]Cota del Mártir absorbe 2 de daño.[/dim white]")

        player.take_damage(dmg)
        state.log(f"[{C['danger']}]◀ {enemy['name']} {action['text']}[/{C['danger']}] → "
                  f"[bold]{dmg}[/bold] de daño.")
    else:
        state.log(f"[{C['danger']}]◀ {enemy['name']} {action['text']}.[/{C['danger']}]")

    # Curación propia del enemigo (Sacerdote Corrompido)
    if action.get("self_heal", 0) > 0:
        healed = min(action["self_heal"], state.enemy_hp_max - state.enemy_hp)
        state.enemy_hp += healed
        state.log(f"[green]◀ {enemy['name']} se cura {healed} HP.[/green]")

    # Daño de cordura
    if action["sanity_dmg"] > 0:
        player.lose_sanity(action["sanity_dmg"])
        state.log(f"[{C['sanity_low']}]Pierdes {action['sanity_dmg']} de Cordura.[/{C['sanity_low']}]")

    # Aplicar estado al jugador
    if action["applies_status"]:
        state.apply_status_to_player(action["applies_status"])
        sname = action["applies_status"]
        state.log(f"[{STATUS_COLORS[sname]}]"
                  f"{STATUS_LABELS[sname]} aplicado.[/{STATUS_COLORS[sname]}]")


# ------------------------------------------------------------------ #
#  Loop principal de combate                                           #
# ------------------------------------------------------------------ #

def run_combat(player, room, dungeon=None) -> bool:
    """
    Ejecuta un combate completo.
    Devuelve True si el jugador sobrevive, False si muere.
    """
    from content.enemies.enemies_data import get_enemies_for_depth

    rng      = random.Random()
    is_elite = room.room_type.value == "elite"
    is_boss  = room.room_type.value == "boss"

    # Seleccionar enemigo apropiado
    if is_boss:
        pool = get_enemies_for_depth(room.depth, boss=True)
    elif is_elite:
        pool = get_enemies_for_depth(room.depth, elite=True)
    else:
        pool = get_enemies_for_depth(room.depth, elite=False, boss=False)

    # Fallback: si no hay enemigos en el pool para esta profundidad,
    # tomar cualquier no-élite no-boss
    if not pool:
        from content.enemies.enemies_data import ENEMIES
        pool = [e for e in ENEMIES if not e.get("elite") and not e.get("boss")]

    enemy_def = rng.choice(pool)

    # Inicializar estado de combate
    state = CombatState(
        player      = player,
        enemy_def   = enemy_def,
        enemy_hp    = enemy_def["hp"],
        enemy_hp_max= enemy_def["hp"],
    )

    # Intro de combate
    clear()
    show_room_header(room.name, depth=room.depth)
    show_narrative(room.flavor_text)
    pause(0.5)
    show_narrative(f"{enemy_def['name']} emerge de la oscuridad.")
    show_narrative(f"{enemy_def['flavor']}")
    pause(0.8)

    # ---------------------------------------------------------------- #
    #  Loop de turnos                                                   #
    # ---------------------------------------------------------------- #
    while state.enemy_hp > 0 and player.is_alive:

        state.player_defending = False
        _render_combat_screen(state)

        # Menú de acciones
        options = _render_action_menu(state)

        # Turno perdido si aturdido
        if not options:
            state.log(f"[yellow]{player.display_name} está aturdido y pierde el turno.[/yellow]")
            # Quitar STUNNED (se manejó en tick)
        else:
            # Input del jugador
            valid = {k for k, _ in options}
            while True:
                raw = get_player_input("Acción").strip()
                if raw in valid:
                    break
                show_message("Opción inválida.", style=C["danger"])

            action_type = next(act for k, act in options if k == raw)

            if action_type == "attack":
                _resolve_player_attack(state, rng)
            elif action_type == "ability":
                ab_id = player.abilities[0] if player.abilities else None
                _resolve_player_attack(state, rng, ability_id=ab_id)
            elif action_type == "defend":
                state.player_defending = True
                state.log(f"[dim white]{player.display_name} se prepara para el golpe.[/dim white]")

        # Comprobar muerte del enemigo antes del contraataque
        if state.enemy_hp <= 0:
            break

        # Acción del enemigo
        _resolve_enemy_action(state, rng)

        # Tick de estados al final del turno
        tick_msgs = state.tick_statuses()
        for msg in tick_msgs:
            state.log(msg)

        state.turn += 1

    # ---------------------------------------------------------------- #
    #  Resolución del combate                                           #
    # ---------------------------------------------------------------- #
    _render_combat_screen(state)

    if not player.is_alive:
        pause(0.5)
        show_message(f"{enemy_def['name']} te ha matado.", style=C["dead"])
        pause(1.0)
        return False

    # Victoria
    loot_gold = rng.randint(enemy_def["loot_gold_min"], enemy_def["loot_gold_max"])
    player.gold  += loot_gold
    player.kills += 1
    if dungeon:
        dungeon.clear_current_room()

    console.print()
    console.print(Rule(style="dim white"))
    show_message(f"{enemy_def['name']} ha caído.", style=C["success"])

    pause(0.3)
    show_message(f"+{loot_gold} monedas malditas.", style=C["gold"])

    # Drop de item — élites y boss siempre dropean, normales con 30%
    from engine.systems.inventory import pickup_item, roll_loot, _handle_full_inventory
    from content.items.items_data import get_item as _get_item

    drop_table  = "elite_drop" if is_elite or is_boss else "combat_drop"
    drop_chance = 1.0 if (is_elite or is_boss) else 0.30
    if rng.random() < drop_chance:
        item_id = roll_loot(room.depth, drop_table)
        if item_id:
            item = _get_item(item_id)
            if item:
                console.print()
                console.print(f"  [dim white]Encuentra entre los restos:[/dim white] [cyan]{item['name']}[/cyan]")
                console.print(f"  [italic dim white]{item['flavor']}[/italic dim white]")
                console.print()
                console.print("  [bold white]1[/bold white]  Recoger")
                console.print("  [bold white]2[/bold white]  Dejar")
                choice = get_player_input().strip()
                if choice == "1":
                    ok, msg = pickup_item(player, item_id)
                    if not ok and msg == "INVENTARIO_LLENO":
                        _handle_full_inventory(player, item_id)
                    else:
                        show_message(msg, style=C["success"])

    # Bonus de cordura al sobrevivir (pequeño)
    san_gain = rng.randint(0, 2)
    if san_gain:
        player.restore_sanity(san_gain)
        show_message(f"+{san_gain} Cordura — sigues en pie.", style=C["sanity_high"])

    pause(1.0)
    return True