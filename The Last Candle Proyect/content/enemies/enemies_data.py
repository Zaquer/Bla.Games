"""
content/enemies/enemies_data.py
Capa de contenido — definiciones de todos los enemigos.

Cada enemigo tiene:
    - Stats base
    - Lista de acciones ponderadas (el engine elige según peso)
    - Arte ASCII para la terminal
    - Profundidad mínima de aparición
"""

ENEMIES: list[dict] = [

    # ------------------------------------------------------------------ #
    #  PROFUNDIDAD 1                                                       #
    # ------------------------------------------------------------------ #

    {
        "id": "ghoul_menor",
        "name": "Ghoul Menor",
        "flavor": "Lo que queda cuando un hombre tiene hambre suficiente tiempo.",
        "depth_min": 1,
        "depth_max": 3,
        "elite": False,
        "hp": 14,
        "damage_min": 3,
        "damage_max": 6,
        "ascii_art": """\
    ░░░░░░░
   ░ ◉  ◉ ░
   ░  ──  ░
   ░ /  \\ ░
    ░░░░░░░
    |    |
   _|_  _|_""",
        "actions": [
            {
                "id": "arañazo",
                "text": "araña salvajemente",
                "weight": 55,
                "dmg_mult": 1.0,
                "sanity_dmg": 0,
                "applies_status": None,
            },
            {
                "id": "mordisco",
                "text": "muerde con dientes podridos",
                "weight": 30,
                "dmg_mult": 1.2,
                "sanity_dmg": 1,
                "applies_status": "BLEEDING",
            },
            {
                "id": "aullido",
                "text": "aúlla hacia la oscuridad",
                "weight": 15,
                "dmg_mult": 0.0,
                "sanity_dmg": 3,
                "applies_status": None,
            },
        ],
        "loot_gold_min": 2,
        "loot_gold_max": 5,
    },

    {
        "id": "esqueleto_profanado",
        "name": "Esqueleto Profanado",
        "flavor": "Alguien se tomó la molestia de levantarlo. Nadie se tomó la de detenerlo.",
        "depth_min": 1,
        "depth_max": 4,
        "elite": False,
        "hp": 10,
        "damage_min": 4,
        "damage_max": 7,
        "ascii_art": """\
     .-.
    (o.o)
     |=|
    __|__
   /|   |\\
    |   |
   _|_ _|_""",
        "actions": [
            {
                "id": "golpe_oseo",
                "text": "golpea con el hueso",
                "weight": 50,
                "dmg_mult": 1.0,
                "sanity_dmg": 0,
                "applies_status": None,
            },
            {
                "id": "lanza_fragmento",
                "text": "lanza un fragmento de hueso",
                "weight": 30,
                "dmg_mult": 0.8,
                "sanity_dmg": 0,
                "applies_status": "BLEEDING",
            },
            {
                "id": "presencia_mortal",
                "text": "emana un frío sobrenatural",
                "weight": 20,
                "dmg_mult": 0.3,
                "sanity_dmg": 2,
                "applies_status": "WEAKENED",
            },
        ],
        "loot_gold_min": 3,
        "loot_gold_max": 6,
    },

    # ------------------------------------------------------------------ #
    #  PROFUNDIDAD 2-3                                                     #
    # ------------------------------------------------------------------ #

    {
        "id": "engendro_sombra",
        "name": "Engendro de Sombra",
        "flavor": "No proyecta sombra. Es la sombra.",
        "depth_min": 2,
        "depth_max": 5,
        "elite": False,
        "hp": 16,
        "damage_min": 4,
        "damage_max": 8,
        "ascii_art": """\
   ~~~~~~~~~
  ~ ●     ● ~
  ~   ~~~   ~
  ~  ~~~~~  ~
   ~~~~~~~~~
    ~     ~
   ~~~   ~~~""",
        "actions": [
            {
                "id": "garra_oscura",
                "text": "hunde una garra de oscuridad",
                "weight": 40,
                "dmg_mult": 1.0,
                "sanity_dmg": 1,
                "applies_status": None,
            },
            {
                "id": "marcar_presa",
                "text": "te señala con un dedo de sombra",
                "weight": 30,
                "dmg_mult": 0.3,
                "sanity_dmg": 0,
                "applies_status": "MARKED",
            },
            {
                "id": "susurro_oscuro",
                "text": "susurra cosas que no deberías saber",
                "weight": 30,
                "dmg_mult": 0.0,
                "sanity_dmg": 4,
                "applies_status": "TERRIFIED",
            },
        ],
        "loot_gold_min": 4,
        "loot_gold_max": 8,
    },

    {
        "id": "cultista_roto",
        "name": "Cultista Roto",
        "flavor": "Creía en algo. Ya no sabe qué. Sigue actuando como si importara.",
        "depth_min": 2,
        "depth_max": 5,
        "elite": False,
        "hp": 18,
        "damage_min": 5,
        "damage_max": 9,
        "ascii_art": """\
   /\\  /\\
  /  \\/  \\
  | ()()|
  |  __  |
  \\ |  | /
   \\|  |/
    |  |""",
        "actions": [
            {
                "id": "daga_ritual",
                "text": "hunde la daga ritual",
                "weight": 40,
                "dmg_mult": 1.0,
                "sanity_dmg": 0,
                "applies_status": "BLEEDING",
            },
            {
                "id": "rezo_maldito",
                "text": "recita un rezo que duele escuchar",
                "weight": 35,
                "dmg_mult": 0.5,
                "sanity_dmg": 3,
                "applies_status": None,
            },
            {
                "id": "ofrenda_de_sangre",
                "text": "se hiere a sí mismo para dañarte",
                "weight": 25,
                "dmg_mult": 1.5,
                "sanity_dmg": 2,
                "applies_status": None,
            },
        ],
        "loot_gold_min": 5,
        "loot_gold_max": 10,
    },

    # ------------------------------------------------------------------ #
    #  ÉLITES (cualquier profundidad, más duros)                           #
    # ------------------------------------------------------------------ #

    {
        "id": "campeon_corrompido",
        "name": "Campeón Corrompido",
        "flavor": "Ganó demasiadas batallas. El dungeon lo reclamó como suyo.",
        "depth_min": 2,
        "depth_max": 6,
        "elite": True,
        "hp": 30,
        "damage_min": 7,
        "damage_max": 12,
        "ascii_art": """\
    [|||]
   /|   |\\
  / | Ω | \\
 /  |___|  \\
    |   |
   /|   |\\
  /_|___|_\\""",
        "actions": [
            {
                "id": "tajo_maestro",
                "text": "ejecuta un tajo de maestro",
                "weight": 35,
                "dmg_mult": 1.2,
                "sanity_dmg": 0,
                "applies_status": None,
            },
            {
                "id": "golpe_aplastante",
                "text": "aplasta con el escudo corrompido",
                "weight": 30,
                "dmg_mult": 1.0,
                "sanity_dmg": 0,
                "applies_status": "STUNNED",
            },
            {
                "id": "grito_de_guerra",
                "text": "lanza un grito de guerra corrupto",
                "weight": 20,
                "dmg_mult": 0.4,
                "sanity_dmg": 3,
                "applies_status": "WEAKENED",
            },
            {
                "id": "ejecutar",
                "text": "intenta una ejecución cuando estás bajo",
                "weight": 15,
                "dmg_mult": 2.0,
                "sanity_dmg": 0,
                "applies_status": None,
            },
        ],
        "loot_gold_min": 12,
        "loot_gold_max": 20,
    },

    # ------------------------------------------------------------------ #
    #  BOSS                                                                #
    # ------------------------------------------------------------------ #

    {
        "id": "señor_profundidades",
        "name": "Señor de las Profundidades",
        "flavor": (
            "No es un monstruo. Es lo que queda cuando un dungeon "
            "lleva suficiente tiempo sin ser desafiado."
        ),
        "depth_min": 3,
        "depth_max": 6,
        "elite": False,
        "boss": True,
        "hp": 55,
        "damage_min": 5,
        "damage_max": 9,
        "ascii_art": """\
  ___________
 /  ●     ●  \\
|   _______   |
|  | _____ |  |
|  ||     ||  |
 \\ ||_____|| /
  \\|_______|/
    |     |
   _|_   _|_""",
        "actions": [
            {
                "id": "aplastamiento",
                "text": "aplasta con todo su peso",
                "weight": 30,
                "dmg_mult": 1.3,
                "sanity_dmg": 1,
                "applies_status": None,
            },
            {
                "id": "grito_del_vacio",
                "text": "emite un grito desde el vacío",
                "weight": 25,
                "dmg_mult": 0.3,
                "sanity_dmg": 5,
                "applies_status": "TERRIFIED",
            },
            {
                "id": "marcar_para_muerte",
                "text": "te marca para la muerte",
                "weight": 20,
                "dmg_mult": 0.5,
                "sanity_dmg": 2,
                "applies_status": "MARKED",
            },
            {
                "id": "drenaje_vital",
                "text": "drena tu fuerza vital",
                "weight": 25,
                "dmg_mult": 1.0,
                "sanity_dmg": 0,
                "applies_status": "WEAKENED",
            },
        ],
        "loot_gold_min": 25,
        "loot_gold_max": 40,
    },

    # ------------------------------------------------------------------ #
    #  NUEVOS ENEMIGOS — EXPANSIÓN 1.1                                     #
    # ------------------------------------------------------------------ #

    # El Sacerdote Corrompido — se cura a sí mismo si lo dejas respirar.
    # Obliga al jugador a jugar agresivo, no defensivo.
    {
        "id": "sacerdote_corrompido",
        "name": "Sacerdote Corrompido",
        "flavor": "Sigue rezando. Solo que ahora no a algo bueno.",
        "depth_min": 2,
        "depth_max": 5,
        "elite": False,
        "hp": 20,
        "damage_min": 4,
        "damage_max": 7,
        "ascii_art": """\
    /\\    /\\
   /  \\  /  \\
  | +  \\/  + |
  |    /\\    |
   \\  /  \\  /
    \\/    \\/
     |    |""",
        "actions": [
            {
                "id": "maldicion_sagrada",
                "text": "lanza una maldición sagrada",
                "weight": 35,
                "dmg_mult": 1.0,
                "sanity_dmg": 2,
                "applies_status": "WEAKENED",
            },
            {
                "id": "rezo_de_cura",
                # Daño 0 — el engine lo interpreta, pero añadimos
                # una flag especial para que el combat_engine lo procese
                "text": "reza en voz alta y sus heridas se cierran",
                "weight": 30,
                "dmg_mult": 0.0,
                "sanity_dmg": 1,
                "applies_status": None,
                "self_heal": 6,        # campo extra procesado en combat_engine
            },
            {
                "id": "toque_profano",
                "text": "te toca con dedos que queman al revés",
                "weight": 35,
                "dmg_mult": 1.2,
                "sanity_dmg": 0,
                "applies_status": "BLEEDING",
            },
        ],
        "loot_gold_min": 6,
        "loot_gold_max": 12,
    },

    # La Larva Abismal — débil al principio, escala con cada turno.
    # El jugador que la ignora o la deja vivir mucho paga caro.
    {
        "id": "larva_abismal",
        "name": "Larva Abismal",
        "flavor": "Pequeña. Pero lleva aquí más tiempo que las piedras.",
        "depth_min": 3,
        "depth_max": 6,
        "elite": False,
        "hp": 12,
        "damage_min": 2,
        "damage_max": 4,
        "ascii_art": """\
   ~-~-~-~-~
  ( o )( o )
   ~-~-~-~-~
    \\  ||  /
     \\_||_/
      |  |
    ~~|  |~~""",
        "actions": [
            {
                "id": "mordisco_larvario",
                "text": "muerde con mandíbulas que no deberían existir",
                "weight": 40,
                "dmg_mult": 1.0,
                "sanity_dmg": 0,
                "applies_status": None,
            },
            {
                "id": "segregacion",
                "text": "segrega un líquido que corroe la armadura",
                "weight": 35,
                "dmg_mult": 0.7,
                "sanity_dmg": 0,
                "applies_status": "WEAKENED",
            },
            {
                "id": "pulso_abismal",
                "text": "emite un pulso del abismo — crece con cada turno",
                "weight": 25,
                "dmg_mult": 0.0,
                "sanity_dmg": 3,
                "applies_status": "TERRIFIED",
                # Flag especial: el combat_engine aumenta daño base con los turnos
                "scales_with_turns": True,
            },
        ],
        "loot_gold_min": 3,
        "loot_gold_max": 7,
    },

    # El Doppelgänger — élite que copia tus stats. Ganarle requiere
    # una estrategia distinta según tu clase.
    {
        "id": "doppelganger",
        "name": "El Doppelgänger",
        "flavor": "Tiene tu cara. La tuya de hace años, cuando aún creías en algo.",
        "depth_min": 3,
        "depth_max": 6,
        "elite": True,
        "hp": 25,
        "damage_min": 5,
        "damage_max": 10,
        "ascii_art": """\
   ┌───────┐
   │ ◈   ◈ │
   │   ─   │
   │ \\___/ │
   └───────┘
     │   │
    _│_  _│_""",
        "actions": [
            {
                "id": "reflejo_de_golpe",
                "text": "replica tu propio movimiento contra ti",
                "weight": 35,
                "dmg_mult": 1.1,
                "sanity_dmg": 2,
                "applies_status": None,
            },
            {
                "id": "robar_fuerza",
                "text": "te roba momentáneamente tu fuerza",
                "weight": 30,
                "dmg_mult": 0.8,
                "sanity_dmg": 0,
                "applies_status": "WEAKENED",
            },
            {
                "id": "grito_de_identidad",
                "text": "grita tu nombre con tu propia voz",
                "weight": 20,
                "dmg_mult": 0.0,
                "sanity_dmg": 5,
                "applies_status": "STUNNED",
            },
            {
                "id": "golpe_especular",
                "text": "ejecuta tu habilidad de clase contra ti",
                "weight": 15,
                "dmg_mult": 1.4,
                "sanity_dmg": 3,
                "applies_status": "MARKED",
            },
        ],
        "loot_gold_min": 15,
        "loot_gold_max": 22,
    },

    # El Centinela Olvidado — boss alternativo. No ataca dos veces seguidas
    # del mismo modo. Patrón semi-predecible que recompensa observar.
    {
        "id": "centinela_olvidado",
        "name": "El Centinela Olvidado",
        "flavor": (
            "Lleva aquí desde antes de que existiera el dungeon. "
            "No sabe qué guarda. Solo sabe guardar."
        ),
        "depth_min": 3,
        "depth_max": 6,
        "elite": False,
        "boss": True,
        "hp": 48,
        "damage_min": 4,
        "damage_max": 8,
        "ascii_art": """\
  ╔═══════╗
  ║ ▓   ▓ ║
  ║   ═   ║
  ║ ╔═══╗ ║
  ╚═╝   ╚═╝
    ║   ║
   ═╩═ ═╩═""",
        "actions": [
            {
                "id": "lanza_de_centinela",
                "text": "atraviesa con la lanza que nunca se oxida",
                "weight": 30,
                "dmg_mult": 1.2,
                "sanity_dmg": 0,
                "applies_status": "BLEEDING",
            },
            {
                "id": "escudo_del_olvido",
                "text": "golpea con el escudo — la vibración paraliza",
                "weight": 25,
                "dmg_mult": 0.9,
                "sanity_dmg": 0,
                "applies_status": "STUNNED",
            },
            {
                "id": "grito_de_alerta",
                "text": "lanza el grito de alerta que nadie oirá",
                "weight": 20,
                "dmg_mult": 0.2,
                "sanity_dmg": 4,
                "applies_status": "TERRIFIED",
            },
            {
                "id": "ejecucion_protocolar",
                "text": "ejecuta el protocolo de eliminación de intrusos",
                "weight": 25,
                "dmg_mult": 1.3,
                "sanity_dmg": 1,
                "applies_status": None,
            },
        ],
        "loot_gold_min": 20,
        "loot_gold_max": 35,
    },
]


def get_enemy_by_id(enemy_id: str) -> dict | None:
    return next((e for e in ENEMIES if e["id"] == enemy_id), None)


def get_enemies_for_depth(depth: int, elite: bool = False, boss: bool = False) -> list[dict]:
    """Devuelve enemigos apropiados para la profundidad dada."""
    return [
        e for e in ENEMIES
        if e["depth_min"] <= depth <= e.get("depth_max", 99)
        and e.get("elite", False) == elite
        and e.get("boss", False) == boss
    ]