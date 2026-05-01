"""
engine/systems/inventory.py
M6 — Inventory System

Gestiona el inventario del jugador:
    - Recoger items (con límite de capacidad)
    - Equipar / desequipar (respetando maldiciones y slots)
    - Usar consumibles
    - Pantalla de inventario con Rich
    - Aplicar/retirar efectos de equipo sobre el player
"""

from typing import Optional
import random

from rich.console import Console
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.rule import Rule
from rich import box

from engine.ui.renderer import (
    console, show_narrative, show_message,
    get_player_input, pause, clear, C,
)
from content.items.items_data import get_item, LOOT_TABLES

INVENTORY_MAX = 6   # límite de items en bolsa (sin contar equipado)


# ------------------------------------------------------------------ #
#  Aplicar / retirar efectos de equipo sobre el player                #
# ------------------------------------------------------------------ #

def _apply_equip_effect(player, effect: dict, sign: int = 1) -> None:
    """
    Aplica (sign=+1) o retira (sign=-1) los efectos de un equipo al player.
    Ajusta también hp/sanity actuales si los máximos cambian.
    """
    if not effect:
        return

    for stat, delta in effect.items():
        if stat == "description" or not isinstance(delta, (int, float)):
            continue

        actual_delta = int(delta * sign)

        if stat == "strength":
            player.strength  = max(1, player.strength  + actual_delta)
        elif stat == "agility":
            player.agility   = max(0, player.agility   + actual_delta)
        elif stat == "arcane":
            player.arcane    = max(0, player.arcane    + actual_delta)
        elif stat == "hp_max":
            player.hp_max    = max(1, player.hp_max    + actual_delta)
            # Si sube el máximo, sube también el actual; si baja, recortar
            player.hp        = max(1, min(player.hp + actual_delta, player.hp_max))
        elif stat == "sanity_max":
            player.sanity_max = max(1, player.sanity_max + actual_delta)
            player.sanity     = max(1, min(player.sanity + actual_delta, player.sanity_max))


# ------------------------------------------------------------------ #
#  Equipar / desequipar                                               #
# ------------------------------------------------------------------ #

def equip_item(player, item_id: str) -> tuple[bool, str]:
    """
    Equipa un item del inventario del jugador.
    Devuelve (éxito, mensaje).
    """
    item = get_item(item_id)
    if not item or item["type"] != "equipment":
        return False, "No se puede equipar ese item."

    slot = item["slot"]
    if not slot:
        return False, "Este item no tiene slot de equipo."

    # Desequipar el item actual en ese slot (si lo hay)
    if slot in player.equipment:
        current_id = player.equipment[slot]
        current    = get_item(current_id)
        if current and current.get("cursed"):
            return False, f"[{current['name']}] está maldito — no puedes quitártelo."
        # Retirar efectos del item anterior
        if current and current.get("equip_effect"):
            _apply_equip_effect(player, current["equip_effect"], sign=-1)
        # Devolver al inventario
        player.inventory.append(current_id)

    # Equipar nuevo item
    player.equipment[slot] = item_id
    player.inventory.remove(item_id)

    # Aplicar efectos
    if item.get("equip_effect"):
        _apply_equip_effect(player, item["equip_effect"], sign=+1)

    curse_str = "  [bold red][MALDITA — no podrás quitártela][/bold red]" if item["cursed"] else ""
    return True, f"Equipas [{item['name']}].{curse_str}"


def unequip_item(player, slot: str) -> tuple[bool, str]:
    """
    Desequipa el item del slot indicado y lo devuelve al inventario.
    """
    if slot not in player.equipment:
        return False, "No tienes nada equipado en ese slot."

    item_id = player.equipment[slot]
    item    = get_item(item_id)

    if item and item.get("cursed"):
        return False, f"[{item['name']}] está maldita. Tendrás que morir con ella."

    if item and item.get("equip_effect"):
        _apply_equip_effect(player, item["equip_effect"], sign=-1)

    del player.equipment[slot]

    if len(player.inventory) < INVENTORY_MAX:
        player.inventory.append(item_id)
        return True, f"Desequipas [{item['name']}] y lo guardas."
    else:
        return True, f"Desequipas [{item['name']}] pero el inventario está lleno. Lo pierdes."


# ------------------------------------------------------------------ #
#  Usar consumibles                                                    #
# ------------------------------------------------------------------ #

def use_item(player, item_id: str) -> tuple[bool, str]:
    """
    Usa un consumible del inventario.
    Devuelve (éxito, mensaje de resultado).
    """
    if item_id not in player.inventory:
        return False, "No tienes ese item."

    item = get_item(item_id)
    if not item or item["type"] != "consumable":
        return False, "Este item no se puede usar directamente."

    effect = item.get("use_effect", {})
    msgs   = []

    hp_delta     = effect.get("hp", 0)
    sanity_delta = effect.get("sanity", 0)
    gold_delta   = effect.get("gold", 0)

    if hp_delta > 0:
        gained = player.heal(hp_delta)
        msgs.append(f"+{gained} HP")
    elif hp_delta < 0:
        player.take_damage(abs(hp_delta))
        msgs.append(f"{hp_delta} HP")

    if sanity_delta > 0:
        gained = player.restore_sanity(sanity_delta)
        msgs.append(f"+{gained} Cordura")
    elif sanity_delta < 0:
        player.lose_sanity(abs(sanity_delta))
        msgs.append(f"{sanity_delta} Cordura")

    if gold_delta:
        player.gold += gold_delta
        msgs.append(f"+{gold_delta} oro" if gold_delta > 0 else f"{gold_delta} oro")

    # Flags
    for flag, val in effect.get("set_flags", {}).items():
        player.set_flag(flag, val)

    # Eliminar estados alterados (solo fuera de combate por ahora)
    remove_status = effect.get("remove_status")

    # Eliminar item del inventario tras uso
    player.inventory.remove(item_id)

    result_str = "  ·  ".join(msgs) if msgs else "Sin efecto."
    return True, f"Usas [{item['name']}] → {result_str}"


# ------------------------------------------------------------------ #
#  Recoger items                                                       #
# ------------------------------------------------------------------ #

def pickup_item(player, item_id: str) -> tuple[bool, str]:
    """
    Añade un item al inventario.
    Si está lleno, ofrece tirar algo (se gestiona desde la UI).
    """
    if len(player.inventory) >= INVENTORY_MAX:
        return False, "INVENTARIO_LLENO"

    player.inventory.append(item_id)
    item = get_item(item_id)
    name = item["name"] if item else item_id
    return True, f"Recoges [{name}]."


def roll_loot(depth: int, table_key: str = "treasure_shallow") -> Optional[str]:
    """Elige un item aleatorio de la loot table apropiada."""
    if depth >= 3 and "treasure" in table_key:
        table_key = "treasure_deep"
    table = LOOT_TABLES.get(table_key, [])
    return random.choice(table) if table else None


# ------------------------------------------------------------------ #
#  Pantalla de inventario                                             #
# ------------------------------------------------------------------ #

def _item_row_text(item_id: str, index: int, equipped_slots: dict) -> Text:
    item    = get_item(item_id)
    if not item:
        return Text(f"  {index}  {item_id} [desconocido]", style="dim white")

    t = Text()
    t.append(f"  {index}  ", style="bold white")

    # Color por tipo
    color = {
        "consumable": "green",
        "equipment":  "cyan",
        "relic":      "magenta",
    }.get(item["type"], "white")

    if item.get("cursed"):
        color = "bold red"

    t.append(f"{item['name']}", style=color)

    if item.get("cursed"):
        t.append(" [MALDITA]", style="dim red")

    # Efecto corto
    effect_desc = ""
    if item["type"] == "consumable" and item.get("use_effect"):
        effect_desc = item["use_effect"].get("description", "")
    elif item.get("equip_effect"):
        effect_desc = item["equip_effect"].get("description", "")

    if effect_desc:
        t.append(f"  —  {effect_desc}", style="dim white")

    t.append(f"\n     {item['flavor']}", style="italic dim white")
    return t


def _equipment_panel(player) -> Text:
    slots = {"weapon": "Arma", "armor": "Armadura", "trinket": "Reliquia"}
    t = Text()
    t.append("  EQUIPADO\n\n", style="dim white")
    for slot_id, slot_name in slots.items():
        t.append(f"  {slot_name:10}", style="dim white")
        item_id = player.equipment.get(slot_id)
        if item_id:
            item  = get_item(item_id)
            name  = item["name"] if item else item_id
            color = "bold red" if item and item.get("cursed") else "cyan"
            t.append(f"{name}", style=color)
            if item and item.get("cursed"):
                t.append(" ⛧", style="dim red")
        else:
            t.append("—", style="dim white")
        t.append("\n")
    return t


def show_inventory_screen(player) -> Optional[str]:
    """
    Muestra la pantalla de inventario completa.
    Devuelve la acción elegida: 'equip:N', 'use:N', 'drop:N', o None.
    """
    clear()
    console.print(Rule("[dim white]— Inventario —[/dim white]", style="dim white"))
    console.print()

    # Panel de stats actuales
    stats = Text()
    stats.append("  Stats actuales:  ", style="dim white")
    stats.append(f"FUE {player.strength}  ", style="white")
    stats.append(f"AGI {player.agility}  ", style="white")
    stats.append(f"ARC {player.arcane}  ", style="white")
    stats.append(f"HP {player.hp}/{player.hp_max}  ", style=C["hp_high"])
    stats.append(f"COR {player.sanity}/{player.sanity_max}  ", style=C["sanity_high"])
    stats.append(f"ORO {player.gold}", style=C["gold"])
    console.print(stats)
    console.print()

    # Equipo actual
    console.print(Panel(_equipment_panel(player), border_style="dim white",
                        box=box.SIMPLE, title="[dim white]Equipo[/dim white]"))

    # Inventario
    if not player.inventory:
        console.print("  [dim white]Inventario vacío.[/dim white]\n")
    else:
        console.print(f"  [dim white]Bolsa ({len(player.inventory)}/{INVENTORY_MAX}):[/dim white]\n")
        for i, item_id in enumerate(player.inventory, 1):
            console.print(_item_row_text(item_id, i, player.equipment))
            console.print()

    # Menú de acciones
    console.print(Rule(style="dim white"))
    console.print()
    console.print("  [bold white]e[N][/bold white]  Equipar item (ej: e1)")
    console.print("  [bold white]u[N][/bold white]  Usar consumible (ej: u2)")
    console.print("  [bold white]d[N][/bold white]  Tirar item (ej: d3)")
    console.print("  [bold white]q[/bold white]     Cerrar inventario")
    console.print()

    raw = get_player_input("Acción").strip().lower()

    if raw == "q":
        return None

    if len(raw) >= 2 and raw[0] in ("e", "u", "d") and raw[1:].isdigit():
        cmd = raw[0]
        idx = int(raw[1:]) - 1
        if 0 <= idx < len(player.inventory):
            return f"{cmd}:{idx}"
        show_message("Número de item inválido.", style=C["danger"])
        return show_inventory_screen(player)

    show_message("Comando inválido.", style=C["danger"])
    return show_inventory_screen(player)


def handle_inventory_action(player, action: str) -> None:
    """Procesa una acción de inventario devuelta por show_inventory_screen."""
    if not action:
        return

    cmd, idx_str = action.split(":")
    idx     = int(idx_str)
    item_id = player.inventory[idx]
    item    = get_item(item_id)

    if cmd == "e":
        ok, msg = equip_item(player, item_id)
        show_message(msg, style=C["success"] if ok else C["danger"])
        pause(0.8)
    elif cmd == "u":
        if item and item["type"] != "consumable":
            show_message("Solo puedes usar consumibles. Para equipar, usa 'e'.", style=C["danger"])
        else:
            ok, msg = use_item(player, item_id)
            show_message(msg, style=C["success"] if ok else C["danger"])
        pause(0.8)
    elif cmd == "d":
        name = item["name"] if item else item_id
        player.inventory.pop(idx)
        show_message(f"Tiras [{name}]. No habrá vuelta atrás.", style=C["muted"])
        pause(0.8)


# ------------------------------------------------------------------ #
#  Handler de sala de tesoro — reemplaza el stub en main.py           #
# ------------------------------------------------------------------ #

def handle_treasure_room(player, room, dungeon) -> None:
    """
    Sala de tesoro completa:
    - Genera loot según profundidad
    - Ofrece al jugador recogerlo
    - Gestiona inventario lleno
    """
    from engine.ui.renderer import show_room_header
    clear()
    show_room_header(room.name, depth=room.depth)
    show_narrative(room.flavor_text)
    pause(0.6)

    # Generar loot: oro siempre + 1-2 items
    gold_found = random.randint(4, 8) * room.depth
    player.gold += gold_found
    show_message(f"Encuentras {gold_found} monedas malditas.", style=C["gold"])
    pause(0.4)

    # Item(s) encontrado(s)
    table = "treasure_shallow" if room.depth < 3 else "treasure_deep"
    n_items = random.randint(1, 2)
    found_items = []
    seen = set()
    for _ in range(n_items):
        item_id = roll_loot(room.depth, table)
        if item_id and item_id not in seen:
            found_items.append(item_id)
            seen.add(item_id)

    for item_id in found_items:
        item = get_item(item_id)
        if not item:
            continue

        name  = item["name"]
        curse = "  [bold red][MALDITA][/bold red]" if item.get("cursed") else ""
        desc  = ""
        if item["type"] == "consumable" and item.get("use_effect"):
            desc = item["use_effect"].get("description", "")
        elif item.get("equip_effect"):
            desc = item["equip_effect"].get("description", "")

        console.print()
        console.print(f"  [cyan]Encuentras:[/cyan] [bold]{name}[/bold]{curse}")
        console.print(f"  [italic dim white]{item['flavor']}[/italic dim white]")
        if desc:
            console.print(f"  [dim white]{desc}[/dim white]")
        console.print()

        # Preguntar si recoge
        console.print("  [bold white]1[/bold white]  Recoger")
        console.print("  [bold white]2[/bold white]  Dejar aquí")

        choice = get_player_input().strip()
        if choice == "1":
            ok, msg = pickup_item(player, item_id)
            if not ok and msg == "INVENTARIO_LLENO":
                _handle_full_inventory(player, item_id)
            else:
                show_message(msg, style=C["success"])
        else:
            show_narrative("Lo dejas. Alguien más lo encontrará.")

    pause(0.5)
    dungeon.clear_current_room()


def _handle_full_inventory(player, new_item_id: str) -> None:
    """Gestiona el caso de inventario lleno al intentar recoger un item."""
    new_item = get_item(new_item_id)
    show_message(
        f"El inventario está lleno ({INVENTORY_MAX}/{INVENTORY_MAX}). "
        f"¿Qué tiras para quedarte [{new_item['name'] if new_item else new_item_id}]?",
        style=C["warning"],
    )
    console.print()

    for i, item_id in enumerate(player.inventory, 1):
        item = get_item(item_id)
        name = item["name"] if item else item_id
        console.print(f"  [bold white]{i}[/bold white]  {name}")

    console.print(f"  [bold white]0[/bold white]  Dejar el nuevo item")
    console.print()

    while True:
        raw = get_player_input("¿Qué tiras?").strip()
        if raw == "0":
            show_narrative("Dejas el item donde estaba.")
            return
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(player.inventory):
                dropped    = player.inventory.pop(idx)
                dropped_it = get_item(dropped)
                dropped_name = dropped_it["name"] if dropped_it else dropped
                player.inventory.append(new_item_id)
                show_message(
                    f"Tiras [{dropped_name}] y recoges [{new_item['name'] if new_item else new_item_id}].",
                    style=C["success"],
                )
                return
        show_message("Opción inválida.", style=C["danger"])
