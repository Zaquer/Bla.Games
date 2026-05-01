"""
engine/core/player.py
M1 — Player Manager
Gestiona el estado completo del jugador durante una run.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class PlayerClass(Enum):
    SOLDADO_ROTO   = "soldado_roto"
    HEREJE         = "hereje"
    LADRON         = "ladron"
    FLAGELANTE     = "flagelante"


# Definición base de cada clase: stats iniciales y descripción de lore
CLASS_DEFINITIONS: dict = {
    PlayerClass.SOLDADO_ROTO: {
        "display_name": "Soldado Roto",
        "lore":         "Sirvió a un rey que ya no existe. Ahora solo sirve a la deuda.",
        "hp_max":       22,
        "sanity_max":   14,
        "strength":     6,   # daño base en combate
        "agility":      3,   # probabilidad de esquivar
        "arcane":       1,   # potencia de habilidades mágicas/oscuras
        "gold":         5,
        "starting_flags": {},
        "starting_ability": "golpe_desesperado",  # habilidad única de clase
    },
    PlayerClass.HEREJE: {
        "display_name": "Hereje",
        "lore":         "Quemaron su fe. Lo que quedó es peor.",
        "hp_max":       14,
        "sanity_max":   10,
        "strength":     3,
        "agility":      2,
        "arcane":       8,
        "gold":         2,
        "starting_flags": {"marcado_por_el_vacio": True},
        "starting_ability": "maldicion_menor",
    },
    PlayerClass.LADRON: {
        "display_name": "Ladrón",
        "lore":         "Robó al hombre equivocado. Ahora ese hombre lo persigue.",
        "hp_max":       16,
        "sanity_max":   18,
        "strength":     4,
        "agility":      7,
        "arcane":       2,
        "gold":         12,
        "starting_flags": {},
        "starting_ability": "golpe_bajo",
    },
    PlayerClass.FLAGELANTE: {
        "display_name": "Flagelante",
        "lore":         "Busca el dolor como otros buscan el oro. Lo encuentra siempre.",
        "hp_max":       20,
        "sanity_max":   8,
        "strength":     5,
        "agility":      2,
        "arcane":       4,
        "gold":         0,
        "starting_flags": {"abraza_el_dolor": True},
        "starting_ability": "penitencia",
    },
}


@dataclass
class Player:
    """
    Estado completo del jugador para una run.
    Cuando hp <= 0 o sanity <= 0, la run termina.
    """
    player_class:   PlayerClass
    display_name:   str
    lore:           str

    # Stats base (no cambian durante la run, son el techo)
    hp_max:         int
    sanity_max:     int
    strength:       int
    agility:        int
    arcane:         int

    # Stats actuales (cambian durante la run)
    hp:             int = field(init=False)
    sanity:         int = field(init=False)
    gold:           int = 0

    # Inventario y habilidades
    inventory:      list  = field(default_factory=list)
    abilities:      list  = field(default_factory=list)
    equipment:      dict  = field(default_factory=dict)   # slot -> item_id

    # Sistema de flags: decisiones y consecuencias persistentes dentro de la run
    flags:          dict  = field(default_factory=dict)

    # Tracking de run
    rooms_explored: int   = 0
    kills:          int   = 0
    depth:          int   = 0   # nivel de profundidad en el dungeon

    def __post_init__(self):
        self.hp     = self.hp_max
        self.sanity = self.sanity_max

    # ------------------------------------------------------------------ #
    #  Propiedades de estado                                               #
    # ------------------------------------------------------------------ #

    @property
    def is_alive(self) -> bool:
        return self.hp > 0 and self.sanity > 0

    @property
    def hp_percent(self) -> float:
        return self.hp / self.hp_max

    @property
    def sanity_percent(self) -> float:
        return self.sanity / self.sanity_max

    @property
    def stress_level(self) -> str:
        """Etiqueta narrativa del estado mental — afecta diálogos y eventos."""
        if self.sanity_percent >= 0.75:
            return "sereno"
        elif self.sanity_percent >= 0.50:
            return "inquieto"
        elif self.sanity_percent >= 0.25:
            return "al_limite"
        else:
            return "quebrado"

    @property
    def hp_level(self) -> str:
        """Etiqueta narrativa del estado físico."""
        if self.hp_percent >= 0.75:
            return "sano"
        elif self.hp_percent >= 0.50:
            return "herido"
        elif self.hp_percent >= 0.25:
            return "malherido"
        else:
            return "moribundo"

    # ------------------------------------------------------------------ #
    #  Modificadores de stats                                              #
    # ------------------------------------------------------------------ #

    def take_damage(self, amount: int) -> int:
        """Aplica daño físico. Devuelve daño real recibido."""
        actual = min(amount, self.hp)
        self.hp -= actual
        return actual

    def heal(self, amount: int) -> int:
        """Cura HP sin superar el máximo. Devuelve cantidad real curada."""
        actual = min(amount, self.hp_max - self.hp)
        self.hp += actual
        return actual

    def lose_sanity(self, amount: int) -> int:
        """Pierde cordura. Devuelve cantidad real perdida."""
        actual = min(amount, self.sanity)
        self.sanity -= actual
        return actual

    def restore_sanity(self, amount: int) -> int:
        """Recupera cordura sin superar el máximo."""
        actual = min(amount, self.sanity_max - self.sanity)
        self.sanity += actual
        return actual

    # ------------------------------------------------------------------ #
    #  Inventario                                                          #
    # ------------------------------------------------------------------ #

    def add_item(self, item_id: str) -> None:
        self.inventory.append(item_id)

    def remove_item(self, item_id: str) -> bool:
        if item_id in self.inventory:
            self.inventory.remove(item_id)
            return True
        return False

    def has_item(self, item_id: str) -> bool:
        return item_id in self.inventory

    # ------------------------------------------------------------------ #
    #  Flags                                                               #
    # ------------------------------------------------------------------ #

    def set_flag(self, key: str, value=True) -> None:
        self.flags[key] = value

    def has_flag(self, key: str) -> bool:
        return bool(self.flags.get(key, False))

    def get_flag(self, key: str, default=None):
        return self.flags.get(key, default)


# ------------------------------------------------------------------ #
#  Factory                                                             #
# ------------------------------------------------------------------ #

def create_player(player_class: PlayerClass) -> Player:
    """Instancia un Player a partir de su clase. Punto de entrada principal."""
    definition = CLASS_DEFINITIONS[player_class]
    player = Player(
        player_class  = player_class,
        display_name  = definition["display_name"],
        lore          = definition["lore"],
        hp_max        = definition["hp_max"],
        sanity_max    = definition["sanity_max"],
        strength      = definition["strength"],
        agility       = definition["agility"],
        arcane         = definition["arcane"],
        gold          = definition["gold"],
    )
    # Flags iniciales de clase
    for k, v in definition["starting_flags"].items():
        player.set_flag(k, v)
    # Habilidad inicial
    player.abilities.append(definition["starting_ability"])
    return player
