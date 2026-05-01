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
        "damage_min": 8,
        "damage_max": 14,
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
