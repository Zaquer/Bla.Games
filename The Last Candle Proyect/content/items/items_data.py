"""
content/items/items_data.py
Capa de contenido — definiciones de todos los items.

Cada item tiene:
    type:       consumable | equipment | relic
    slot:       weapon | armor | trinket | None (consumables/relics)
    effects:    modificadores de stats al equipar/usar
    cursed:     si True, no se puede desequipar
    on_use:     función de efecto para consumibles (referenciada por id)
    flavor:     texto de lore
"""

ITEMS: dict[str, dict] = {

    # ------------------------------------------------------------------ #
    #  CONSUMIBLES                                                         #
    # ------------------------------------------------------------------ #

    "pocion_sangre": {
        "id":       "pocion_sangre",
        "name":     "Poción de Sangre",
        "type":     "consumable",
        "slot":     None,
        "flavor":   "No es sangre de animal. Tampoco es del todo humana.",
        "cursed":   False,
        "use_effect": {
            "hp":     12,
            "sanity": -2,
            "gold":   0,
            "set_flags": {},
            "description": "Recuperas 12 HP. Pierdes 2 de Cordura.",
        },
        "equip_effect": None,
        "value": 8,
    },

    "vendaje_sucio": {
        "id":       "vendaje_sucio",
        "name":     "Vendaje Sucio",
        "type":     "consumable",
        "slot":     None,
        "flavor":   "Ya curó a alguien antes. Puede que otra vez.",
        "cursed":   False,
        "use_effect": {
            "hp":     5,
            "sanity": 0,
            "gold":   0,
            "set_flags": {},
            "remove_status": "BLEEDING",
            "description": "Recuperas 5 HP. Elimina BLEEDING.",
        },
        "equip_effect": None,
        "value": 4,
    },

    "antidoto_amargo": {
        "id":       "antidoto_amargo",
        "name":     "Antídoto Amargo",
        "type":     "consumable",
        "slot":     None,
        "flavor":   "El sabor te hace desear haber tomado el veneno.",
        "cursed":   False,
        "use_effect": {
            "hp":     0,
            "sanity": 0,
            "gold":   0,
            "set_flags": {},
            "remove_status": "WEAKENED",
            "description": "Elimina WEAKENED y TERRIFIED.",
        },
        "equip_effect": None,
        "value": 5,
    },

    "fragmento_cordura": {
        "id":       "fragmento_cordura",
        "name":     "Fragmento de Cordura",
        "type":     "consumable",
        "slot":     None,
        "flavor":   "Un pedazo de espejo. Ves en él algo que reconoces. Por ahora.",
        "cursed":   False,
        "use_effect": {
            "hp":     -2,
            "sanity": 8,
            "gold":   0,
            "set_flags": {},
            "description": "Recuperas 8 de Cordura. Pierdes 2 HP.",
        },
        "equip_effect": None,
        "value": 7,
    },

    "vela_negra": {
        "id":       "vela_negra",
        "name":     "Vela Negra",
        "type":     "consumable",
        "slot":     None,
        "flavor":   "Ilumina lo que no debería verse. Oscurece lo que sí.",
        "cursed":   False,
        "use_effect": {
            "hp":     0,
            "sanity": -3,
            "gold":   12,
            "set_flags": {"usó_vela_negra": True},
            "description": "Revelas un tesoro oculto: +12 oro. Pierdes 3 Cordura.",
        },
        "equip_effect": None,
        "value": 3,
    },

    # ------------------------------------------------------------------ #
    #  ARMAS                                                               #
    # ------------------------------------------------------------------ #

    "espada_oxidada": {
        "id":       "espada_oxidada",
        "name":     "Espada Oxidada",
        "type":     "equipment",
        "slot":     "weapon",
        "flavor":   "Ha matado antes. El óxido es de sangre vieja.",
        "cursed":   False,
        "use_effect": None,
        "equip_effect": {
            "strength": +2,
            "description": "+2 Fuerza",
        },
        "value": 10,
    },

    "daga_traidora": {
        "id":       "daga_traidora",
        "name":     "Daga Traidora",
        "type":     "equipment",
        "slot":     "weapon",
        "flavor":   "Ligera. Rápida. El nombre es una advertencia.",
        "cursed":   False,
        "use_effect": None,
        "equip_effect": {
            "strength": +1,
            "agility":  +2,
            "description": "+1 Fuerza, +2 Agilidad",
        },
        "value": 14,
    },

    "hacha_maldita": {
        "id":       "hacha_maldita",
        "name":     "Hacha Maldita",
        "type":     "equipment",
        "slot":     "weapon",
        "flavor":   "Pesa más de lo que debería. Corta más de lo que debería. No preguntes.",
        "cursed":   True,
        "use_effect": None,
        "equip_effect": {
            "strength":    +4,
            "sanity_max":  -3,
            "description": "+4 Fuerza, -3 Cordura máxima [MALDITA — no se puede desequipar]",
        },
        "value": 0,
    },

    "lanza_del_hereje": {
        "id":       "lanza_del_hereje",
        "name":     "Lanza del Hereje",
        "type":     "equipment",
        "slot":     "weapon",
        "flavor":   "Usada en un ritual que salió mal. O bien. Depende de quién lo mida.",
        "cursed":   False,
        "use_effect": None,
        "equip_effect": {
            "strength": +2,
            "arcane":   +3,
            "description": "+2 Fuerza, +3 Arcano",
        },
        "value": 18,
    },

    # ------------------------------------------------------------------ #
    #  ARMADURA                                                            #
    # ------------------------------------------------------------------ #

    "cota_rota": {
        "id":       "cota_rota",
        "name":     "Cota Rota",
        "type":     "equipment",
        "slot":     "armor",
        "flavor":   "Tiene agujeros. Antes no los tenía.",
        "cursed":   False,
        "use_effect": None,
        "equip_effect": {
            "hp_max":     +4,
            "description": "+4 HP máximo",
        },
        "value": 9,
    },

    "manto_del_penitente": {
        "id":       "manto_del_penitente",
        "name":     "Manto del Penitente",
        "type":     "equipment",
        "slot":     "armor",
        "flavor":   "Lleva cosidas las confesiones de los que lo usaron antes.",
        "cursed":   False,
        "use_effect": None,
        "equip_effect": {
            "hp_max":      +2,
            "sanity_max":  +4,
            "description": "+2 HP máximo, +4 Cordura máxima",
        },
        "value": 15,
    },

    "piel_del_traidor": {
        "id":       "piel_del_traidor",
        "name":     "Piel del Traidor",
        "type":     "equipment",
        "slot":     "armor",
        "flavor":   "Ligera. No preguntes de quién es.",
        "cursed":   True,
        "use_effect": None,
        "equip_effect": {
            "hp_max":     +6,
            "agility":    +2,
            "strength":   -1,
            "description": "+6 HP máximo, +2 Agilidad, -1 Fuerza [MALDITA]",
        },
        "value": 0,
    },

    # ------------------------------------------------------------------ #
    #  RELIQUIAS / TRINKETS                                                #
    # ------------------------------------------------------------------ #

    "ojo_de_cristal": {
        "id":       "ojo_de_cristal",
        "name":     "Ojo de Cristal",
        "type":     "equipment",
        "slot":     "trinket",
        "flavor":   "Ve cosas que tú no ves. A veces te lo cuenta.",
        "cursed":   False,
        "use_effect": None,
        "equip_effect": {
            "agility":    +2,
            "description": "+2 Agilidad",
        },
        "value": 12,
    },

    "diente_del_ahorcado": {
        "id":       "diente_del_ahorcado",
        "name":     "Diente del Ahorcado",
        "type":     "equipment",
        "slot":     "trinket",
        "flavor":   "Trae suerte. Del tipo equivocado.",
        "cursed":   False,
        "use_effect": None,
        "equip_effect": {
            "strength":   +1,
            "agility":    +1,
            "sanity_max": -2,
            "description": "+1 Fuerza, +1 Agilidad, -2 Cordura máxima",
        },
        "value": 10,
    },

    "reliquia_del_vacio": {
        "id":       "reliquia_del_vacio",
        "name":     "Reliquia del Vacío",
        "type":     "equipment",
        "slot":     "trinket",
        "flavor":   "Pulsa. Está caliente. No hay fuente de calor.",
        "cursed":   True,
        "use_effect": None,
        "equip_effect": {
            "arcane":     +4,
            "strength":   +2,
            "hp_max":     -4,
            "description": "+4 Arcano, +2 Fuerza, -4 HP máximo [MALDITA]",
        },
        "value": 0,
    },

    "moneda_de_la_muerte": {
        "id":       "moneda_de_la_muerte",
        "name":     "Moneda de la Muerte",
        "type":     "equipment",
        "slot":     "trinket",
        "flavor":   "No tiene cara ni cruz. Solo dos caras iguales que no reconoces.",
        "cursed":   False,
        "use_effect": None,
        "equip_effect": {
            "description": "Al entrar en una sala de combate: 30% de crit en el primer ataque",
            # efecto especial gestionado por combat_engine al detectar este item
            "combat_entry_crit_chance": 0.30,
        },
        "value": 16,
    },

    # ------------------------------------------------------------------ #
    #  NUEVOS ITEMS — EXPANSIÓN 1.1                                        #
    # ------------------------------------------------------------------ #

    "elixir_del_azar": {
        "id":       "elixir_del_azar",
        "name":     "Elixir del Azar",
        "type":     "consumable",
        "slot":     None,
        "flavor":   "Dos frascos idénticos. Solo quedaba uno. El otro mató a alguien.",
        "cursed":   False,
        "use_effect": {
            "hp": 0, "sanity": 0, "gold": 0,
            "set_flags": {},
            "gamble": True,
            "description": "50%: +14 HP  /  50%: -10 HP. Sin término medio.",
        },
        "equip_effect": None,
        "value": 5,
    },

    "ceniza_de_moneda": {
        "id":       "ceniza_de_moneda",
        "name":     "Ceniza de Moneda",
        "type":     "consumable",
        "slot":     None,
        "flavor":   "El oro quemado cura. No preguntes la conversión.",
        "cursed":   False,
        "use_effect": {
            "hp": 0, "sanity": 0, "gold": -10,
            "set_flags": {},
            "gold_to_hp": True,
            "description": "Quema 10 de oro → +8 HP y +3 Cordura.",
        },
        "equip_effect": None,
        "value": 2,
    },

    "aguja_del_marcador": {
        "id":       "aguja_del_marcador",
        "name":     "Aguja del Marcador",
        "type":     "equipment",
        "slot":     "weapon",
        "flavor":   "No mata. Señala. Lo que viene después mata.",
        "cursed":   False,
        "use_effect": None,
        "equip_effect": {
            "strength": -1, "agility": +3,
            "description": "-1 Fuerza, +3 Agilidad. Ataques básicos aplican MARKED.",
            "attack_applies_marked": True,
        },
        "value": 14,
    },

    "cota_del_martir": {
        "id":       "cota_del_martir",
        "name":     "Cota del Mártir",
        "type":     "equipment",
        "slot":     "armor",
        "flavor":   "Cada grieta es una historia. Las suyas son todas de supervivencia.",
        "cursed":   False,
        "use_effect": None,
        "equip_effect": {
            "hp_max": +3,
            "description": "+3 HP máximo. Reduce daño recibido en 2 cuando HP < 40%.",
            "low_hp_defense": True,
        },
        "value": 13,
    },

    "collar_de_dientes": {
        "id":       "collar_de_dientes",
        "name":     "Collar de Dientes",
        "type":     "equipment",
        "slot":     "trinket",
        "flavor":   "No todos son de animales. Ninguno fue dado voluntariamente.",
        "cursed":   True,
        "use_effect": None,
        "equip_effect": {
            "strength": +2, "sanity_max": -4,
            "description": "+2 Fuerza, -4 Cordura máxima. +2 Cordura por baja. [MALDITA]",
            "kill_restores_sanity": 2,
        },
        "value": 0,
    },

    "lagrima_del_abismo": {
        "id":       "lagrima_del_abismo",
        "name":     "Lágrima del Abismo",
        "type":     "consumable",
        "slot":     None,
        "flavor":   "Alguien lloró esto. Probablemente algo que no debería llorar.",
        "cursed":   False,
        "use_effect": {
            "hp": 4, "sanity": 4, "gold": 0,
            "set_flags": {"usó_lágrima": True},
            "remove_all_status": True,
            "description": "+4 HP, +4 Cordura. Elimina todos los estados alterados.",
        },
        "equip_effect": None,
        "value": 20,
    },
}


# ------------------------------------------------------------------ #
#  Helpers                                                             #
# ------------------------------------------------------------------ #

def get_item(item_id: str) -> dict | None:
    return ITEMS.get(item_id)


def get_items_by_type(item_type: str) -> list[dict]:
    return [i for i in ITEMS.values() if i["type"] == item_type]


def get_items_by_slot(slot: str) -> list[dict]:
    return [i for i in ITEMS.values() if i.get("slot") == slot]


# Loot tables actualizadas con nuevos items
LOOT_TABLES: dict[str, list[str]] = {
    "treasure_shallow": [
        "vendaje_sucio", "vendaje_sucio",
        "espada_oxidada", "cota_rota",
        "fragmento_cordura", "pocion_sangre",
        "ojo_de_cristal", "diente_del_ahorcado",
        "aguja_del_marcador", "ceniza_de_moneda",
        "elixir_del_azar",
    ],
    "treasure_deep": [
        "pocion_sangre", "pocion_sangre",
        "daga_traidora", "lanza_del_hereje",
        "manto_del_penitente", "cota_del_martir",
        "hacha_maldita", "piel_del_traidor",
        "reliquia_del_vacio", "moneda_de_la_muerte",
        "collar_de_dientes", "lagrima_del_abismo",
        "antidoto_amargo", "vela_negra", "aguja_del_marcador",
    ],
    "combat_drop": [
        "vendaje_sucio", "vendaje_sucio", "vendaje_sucio",
        "pocion_sangre", "pocion_sangre",
        "antidoto_amargo", "antidoto_amargo",
        "fragmento_cordura", "espada_oxidada",
        "elixir_del_azar", "ceniza_de_moneda",
    ],
    "elite_drop": [
        "daga_traidora", "lanza_del_hereje",
        "manto_del_penitente", "ojo_de_cristal",
        "moneda_de_la_muerte", "hacha_maldita",
        "pocion_sangre", "fragmento_cordura",
        "aguja_del_marcador", "cota_del_martir",
        "collar_de_dientes", "lagrima_del_abismo",
    ],
}