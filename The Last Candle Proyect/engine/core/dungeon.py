"""
engine/core/dungeon.py
M3 — Dungeon Navigator

Genera y gestiona el grafo de salas del dungeon.
Estructura: capas de profundidad, cada sala conecta a 1-3 salas de la capa siguiente.
El jugador solo ve las salas que ha descubierto.

Arquitectura:
    DungeonGraph  →  contiene todas las Room
    Room          →  nodo del grafo, conoce sus conexiones
    RoomType      →  determina qué puede pasar en la sala
    RoomState     →  qué ha hecho el jugador en ella
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import random


# ------------------------------------------------------------------ #
#  Tipos y estados de sala                                             #
# ------------------------------------------------------------------ #

class RoomType(Enum):
    ENTRANCE   = "entrance"    # sala inicial, siempre segura
    COMBAT     = "combat"      # encuentro enemigo
    ELITE      = "elite"       # enemigo fuerte, mejor loot
    EVENT      = "event"       # encuentro narrativo sin combate garantizado
    REST       = "rest"        # hoguera/refugio — recupera HP o Cordura
    TREASURE   = "treasure"    # loot sin combate (poco frecuente)
    BOSS       = "boss"        # jefe de capa — cada N capas
    EXIT       = "exit"        # salida al siguiente nivel


class RoomState(Enum):
    UNKNOWN    = "unknown"     # no descubierta (el jugador no sabe que existe)
    VISIBLE    = "visible"     # el jugador sabe que existe pero no ha entrado
    VISITED    = "visited"     # el jugador ya estuvo aquí
    CLEARED    = "cleared"     # sala resuelta (combate ganado, evento completado)


# Distribución de tipos por capa — se ajusta según profundidad
# formato: {RoomType: peso_relativo}
ROOM_WEIGHTS_NORMAL: dict = {
    RoomType.COMBAT:   45,
    RoomType.EVENT:    20,
    RoomType.REST:     15,
    RoomType.TREASURE: 10,
    RoomType.ELITE:    10,
}

ROOM_WEIGHTS_DEEP: dict = {   # capas 4+, más peligroso
    RoomType.COMBAT:   40,
    RoomType.ELITE:    20,
    RoomType.EVENT:    20,
    RoomType.REST:     10,
    RoomType.TREASURE:  5,
    RoomType.BOSS:      5,    # aparece solo en deep
}


# ------------------------------------------------------------------ #
#  Nombres procedurales de sala                                        #
# ------------------------------------------------------------------ #

ROOM_NAMES: dict[RoomType, list[str]] = {
    RoomType.ENTRANCE: [
        "La Puerta de las Lágrimas",
        "Umbral Sin Nombre",
        "El Primer Paso",
    ],
    RoomType.COMBAT: [
        "Sala de la Podredumbre",
        "Corredor de los Huesos",
        "Antecámara Profanada",
        "El Pozo de las Voces",
        "Galería de los Caídos",
        "Cripta Sin Sello",
        "Cámara del Último Aliento",
        "Pasaje de la Carne Fría",
        "El Umbral Roto",
        "Sala del Silencio Roto",
    ],
    RoomType.ELITE: [
        "Trono del Verdugo",
        "Altar de la Carnicería",
        "Cámara del Señor Menor",
        "El Nido",
        "Santuario Corrompido",
    ],
    RoomType.EVENT: [
        "La Encrucijada",
        "Altar Olvidado",
        "El Espejo Roto",
        "Habitación del Escriba Muerto",
        "Capilla de la Duda",
        "El Susurro en la Pared",
        "Celda del Prisionero",
        "Biblioteca de Ceniza",
    ],
    RoomType.REST: [
        "Rincón de la Vela",
        "Refugio Precario",
        "El Hueco Tibio",
        "Guarida Abandonada",
        "Pequeño Fuego",
    ],
    RoomType.TREASURE: [
        "Almacén Olvidado",
        "Cámara Sellada",
        "El Escondrijo",
        "Bóveda Sin Guardián",
    ],
    RoomType.BOSS: [
        "El Corazón del Dungeon",
        "Cámara del Señor de las Profundidades",
        "Trono del No-Muerto",
        "El Último Umbral",
    ],
    RoomType.EXIT: [
        "Escalera a las Profundidades",
        "El Descenso",
        "Puerta al Siguiente Infierno",
    ],
}

# Iconos por tipo — para el minimapa ASCII
ROOM_ICONS: dict[RoomType, str] = {
    RoomType.ENTRANCE: "▣",
    RoomType.COMBAT:   "☠",
    RoomType.ELITE:    "★",
    RoomType.EVENT:    "?",
    RoomType.REST:     "♨",
    RoomType.TREASURE: "$",
    RoomType.BOSS:     "◈",
    RoomType.EXIT:     "▼",
}

# Colores Rich por tipo — para el minimapa
ROOM_COLORS: dict[RoomType, str] = {
    RoomType.ENTRANCE: "white",
    RoomType.COMBAT:   "red",
    RoomType.ELITE:    "bold red",
    RoomType.EVENT:    "yellow",
    RoomType.REST:     "green",
    RoomType.TREASURE: "bold yellow",
    RoomType.BOSS:     "bold magenta",
    RoomType.EXIT:     "bold cyan",
}


# ------------------------------------------------------------------ #
#  Room — nodo del grafo                                               #
# ------------------------------------------------------------------ #

@dataclass
class Room:
    room_id:     str
    name:        str
    room_type:   RoomType
    depth:       int                          # capa del dungeon (0 = entrada)
    state:       RoomState = RoomState.UNKNOWN

    # Grafo de conexiones
    connections: list[str] = field(default_factory=list)   # room_ids de salidas
    parent_id:   Optional[str] = None                      # de dónde se llega

    # Contenido de la sala — se asigna al generar el dungeon
    enemy_id:    Optional[str] = None    # referencia al content layer
    event_id:    Optional[str] = None
    loot_table:  Optional[str] = None
    flavor_text: str = ""                # descripción atmosférica

    @property
    def icon(self) -> str:
        if self.state == RoomState.UNKNOWN:
            return "░"
        return ROOM_ICONS.get(self.room_type, "?")

    @property
    def color(self) -> str:
        if self.state in (RoomState.VISITED, RoomState.CLEARED):
            return "dim white"
        return ROOM_COLORS.get(self.room_type, "white")

    @property
    def is_dangerous(self) -> bool:
        return self.room_type in (RoomType.COMBAT, RoomType.ELITE, RoomType.BOSS)

    @property
    def display_label(self) -> str:
        """Etiqueta visible según estado de descubrimiento."""
        if self.state == RoomState.UNKNOWN:
            return "???"
        if self.state == RoomState.VISIBLE:
            return f"{self.icon} {self.room_type.value.upper()}"
        return f"{self.icon} {self.name}"


# ------------------------------------------------------------------ #
#  DungeonGraph — el grafo completo de una run                         #
# ------------------------------------------------------------------ #

class DungeonGraph:
    """
    Genera y gestiona el grafo de salas para una run completa.

    Estructura:
        - Capa 0: sala de entrada (1 sala)
        - Capas 1..depth-1: salas normales (2-4 salas por capa)
        - Cada N capas: sala de boss
        - Última capa: salida al siguiente nivel

    El jugador navega de capa en capa eligiendo qué sala visitar.
    Solo ve las salas conectadas a la suya actual.
    """

    def __init__(self, seed: int, total_depth: int = 6, boss_every: int = 3):
        self.seed        = seed
        self.total_depth = total_depth
        self.boss_every  = boss_every
        self.rng         = random.Random(seed)

        self.rooms:        dict[str, Room] = {}
        self.layers:       list[list[str]] = []   # layers[depth] = [room_ids]
        self.current_room: Optional[str]   = None
        self.entrance_id:  Optional[str]   = None

        self._generate()

    # ---------------------------------------------------------------- #
    #  Generación                                                        #
    # ---------------------------------------------------------------- #

    def _make_id(self, depth: int, index: int) -> str:
        return f"r{depth:02d}_{index:02d}"

    def _pick_room_type(self, depth: int, index: int, layer_size: int) -> RoomType:
        """Elige el tipo de sala según profundidad y posición en la capa."""
        # Boss cada N capas (nunca en la capa 0 ni en la última)
        if depth > 0 and depth % self.boss_every == 0 and depth < self.total_depth - 1:
            # Solo una sala boss por capa boss, la primera
            if index == 0:
                return RoomType.BOSS

        # Última capa: solo exits
        if depth == self.total_depth - 1:
            return RoomType.EXIT

        # Garantizar al menos un REST por cada 3 capas normales
        if depth > 0 and depth % 3 == 2 and index == layer_size - 1:
            return RoomType.REST

        weights = ROOM_WEIGHTS_DEEP if depth >= 4 else ROOM_WEIGHTS_NORMAL
        types   = list(weights.keys())
        wvals   = list(weights.values())
        return self.rng.choices(types, weights=wvals, k=1)[0]

    def _pick_name(self, room_type: RoomType) -> str:
        names = ROOM_NAMES.get(room_type, ["Sala Desconocida"])
        return self.rng.choice(names)

    def _pick_flavor(self, room_type: RoomType) -> str:
        flavors: dict[RoomType, list[str]] = {
            RoomType.COMBAT: [
                "El suelo está manchado. Las manchas son recientes.",
                "Algo respiraba aquí. Puede que todavía lo haga.",
                "Las paredes tienen marcas. Arañazos desde adentro.",
            ],
            RoomType.ELITE: [
                "El aire es más denso aquí. Más viejo.",
                "Hay trofeos en las paredes. Son restos humanos.",
                "Una presencia. No la ves, pero sabe que estás aquí.",
            ],
            RoomType.EVENT: [
                "Algo aquí no es lo que parece. O lo es demasiado.",
                "El silencio tiene forma en esta sala.",
                "Hay una decisión que tomar. No hay decisión correcta.",
            ],
            RoomType.REST: [
                "Una pequeña llama. No preguntes de dónde viene el combustible.",
                "Hay espacio para sentarse. El suelo es frío pero no hostil.",
                "Por un momento, algo que se parece a la seguridad.",
            ],
            RoomType.TREASURE: [
                "Alguien escondió esto aquí. No vivió para recuperarlo.",
                "El polvo lleva aquí décadas. El contenido, más.",
            ],
            RoomType.BOSS: [
                "El dungeon converge aquí. Todo este lugar es para llegar a esto.",
                "Lo sientes antes de verlo. Un peso. Una presencia antigua.",
            ],
            RoomType.EXIT: [
                "El descenso continúa. Más profundo. Siempre más profundo.",
                "Las escaleras bajan hacia una oscuridad diferente.",
            ],
            RoomType.ENTRANCE: [
                "La puerta se cierra detrás de ti. No hace ruido.",
            ],
        }
        options = flavors.get(room_type, [""])
        return self.rng.choice(options)

    def _generate(self) -> None:
        """Genera el grafo completo de la run."""
        self.layers = []

        # --- Capa 0: entrada ---
        entrance = Room(
            room_id    = self._make_id(0, 0),
            name       = self._pick_name(RoomType.ENTRANCE),
            room_type  = RoomType.ENTRANCE,
            depth      = 0,
            state      = RoomState.VISITED,   # el jugador empieza aquí
            flavor_text= self._pick_flavor(RoomType.ENTRANCE),
        )
        self.rooms[entrance.room_id] = entrance
        self.layers.append([entrance.room_id])
        self.entrance_id  = entrance.room_id
        self.current_room = entrance.room_id

        # --- Capas 1..total_depth-1 ---
        for depth in range(1, self.total_depth):
            is_boss_layer = (depth % self.boss_every == 0 and depth < self.total_depth - 1)
            is_exit_layer = (depth == self.total_depth - 1)

            if is_boss_layer or is_exit_layer:
                layer_size = 1   # boss y exit: una sola sala
            else:
                layer_size = self.rng.randint(2, 4)

            layer_ids = []
            for i in range(layer_size):
                rtype = self._pick_room_type(depth, i, layer_size)
                room  = Room(
                    room_id    = self._make_id(depth, i),
                    name       = self._pick_name(rtype),
                    room_type  = rtype,
                    depth      = depth,
                    flavor_text= self._pick_flavor(rtype),
                )
                self.rooms[room.room_id] = room
                layer_ids.append(room.room_id)

            self.layers.append(layer_ids)

        # --- Conectar capas ---
        # Cada sala de la capa N conecta a 1-3 salas de la capa N+1
        # Garantía: toda sala de capa N+1 tiene al menos un padre
        for depth_idx in range(len(self.layers) - 1):
            current_layer = self.layers[depth_idx]
            next_layer    = self.layers[depth_idx + 1]

            # Primero: garantizar que cada sala del siguiente nivel
            # tenga al menos una conexión entrante
            next_assigned = {rid: False for rid in next_layer}

            for room_id in current_layer:
                # Número de conexiones salientes: 1 a min(3, tamaño del siguiente nivel)
                max_conn   = min(3, len(next_layer))
                n_conn     = self.rng.randint(1, max_conn)
                targets    = self.rng.sample(next_layer, n_conn)

                for target_id in targets:
                    if target_id not in self.rooms[room_id].connections:
                        self.rooms[room_id].connections.append(target_id)
                    self.rooms[target_id].parent_id = room_id
                    next_assigned[target_id] = True

            # Parchear cualquier sala del siguiente nivel sin padre
            unconnected = [rid for rid, assigned in next_assigned.items() if not assigned]
            for rid in unconnected:
                parent = self.rng.choice(current_layer)
                if rid not in self.rooms[parent].connections:
                    self.rooms[parent].connections.append(rid)
                self.rooms[rid].parent_id = parent

        # --- Revelar las conexiones de la sala inicial ---
        self._reveal_connections(self.entrance_id)

    def _reveal_connections(self, room_id: str) -> None:
        """Marca como VISIBLE todas las salas conectadas desde room_id."""
        for connected_id in self.rooms[room_id].connections:
            room = self.rooms[connected_id]
            if room.state == RoomState.UNKNOWN:
                room.state = RoomState.VISIBLE

    # ---------------------------------------------------------------- #
    #  Navegación                                                        #
    # ---------------------------------------------------------------- #

    def get_current_room(self) -> Room:
        return self.rooms[self.current_room]

    def get_available_moves(self) -> list[Room]:
        """Salas a las que puede moverse el jugador desde la posición actual."""
        current = self.get_current_room()
        return [self.rooms[rid] for rid in current.connections]

    def move_to(self, room_id: str) -> Room:
        """
        Mueve al jugador a una sala conectada.
        Raises ValueError si la sala no es accesible.
        """
        current = self.get_current_room()
        if room_id not in current.connections:
            raise ValueError(f"Sala {room_id} no está conectada desde {self.current_room}")

        self.current_room = room_id
        target = self.rooms[room_id]
        target.state = RoomState.VISITED
        self._reveal_connections(room_id)
        return target

    def clear_current_room(self) -> None:
        """Marca la sala actual como resuelta."""
        self.rooms[self.current_room].state = RoomState.CLEARED

    # ---------------------------------------------------------------- #
    #  Estadísticas                                                      #
    # ---------------------------------------------------------------- #

    @property
    def total_rooms(self) -> int:
        return len(self.rooms)

    @property
    def discovered_rooms(self) -> int:
        return sum(1 for r in self.rooms.values() if r.state != RoomState.UNKNOWN)

    @property
    def cleared_rooms(self) -> int:
        return sum(1 for r in self.rooms.values() if r.state == RoomState.CLEARED)
