"""
content/events/events_data.py
Capa de contenido puro — definiciones de todos los eventos narrativos.

El Event Engine no sabe nada de estas historias.
Este archivo es donde vive la narrativa; events_engine.py es donde vive la lógica.

Estructura de un evento:
    id              → clave única
    name            → nombre de sala (puede coincidir con room.name)
    flavor_text     → descripción atmosférica inicial
    conditions      → cuándo puede aparecer este evento
    choices[]       → opciones del jugador
        id              → clave única dentro del evento
        text            → texto visible al jugador
        tag             → etiqueta visual opcional: "[CLASE]", "[PELIGRO]", etc.
        visible_if      → condiciones para que la opción sea visible
        consequences    → qué pasa al elegirla
            hp          → delta de vida (negativo = daño)
            sanity      → delta de cordura (negativo = pérdida)
            gold        → delta de oro
            set_flags   → dict de flags a activar
            clear_flags → lista de flags a eliminar
            outcome     → texto de resultado
            alt_outcome → texto alternativo (usado con RNG o flags)
"""

EVENTS: list[dict] = [

    # ------------------------------------------------------------------ #
    #  ALTAR OLVIDADO                                                      #
    # ------------------------------------------------------------------ #
    {
        "id": "altar_olvidado",
        "name": "Altar Olvidado",
        "flavor_text": (
            "Un altar de piedra negra en el centro de la sala. "
            "No tiene inscripciones. Nunca las tuvo. "
            "Hay manchas secas en la base que no son de vino."
        ),
        "conditions": {
            "min_depth": 1,
            "forbidden_flags": [],
            "required_flags": [],
        },
        "choices": [
            {
                "id": "rezar",
                "text": "Rezar. Por inercia, más que por fe.",
                "tag": None,
                "visible_if": {
                    "required_flags": [],
                    "forbidden_flags": ["marcado_por_el_vacio", "altar_profanado"],
                },
                "consequences": {
                    "hp": 0,
                    "sanity": -2,
                    "gold": 0,
                    "set_flags": {"rezó_al_vacío": True},
                    "clear_flags": [],
                    "outcome": (
                        "Las palabras salen solas. Vacías. "
                        "El altar no responde. Algo en ti sospecha que nunca lo hará."
                    ),
                },
            },
            {
                "id": "profanar",
                "text": "Romper el altar. Por si acaso.",
                "tag": None,
                "visible_if": {
                    "required_flags": [],
                    "forbidden_flags": ["altar_profanado"],
                },
                "consequences": {
                    "hp": -2,
                    "sanity": 2,
                    "gold": 8,
                    "set_flags": {"altar_profanado": True},
                    "clear_flags": [],
                    "outcome": (
                        "Golpeas la piedra hasta que algo cede. "
                        "Detrás había un hueco. Monedas. "
                        "Alguien también pensó que era un buen escondite."
                    ),
                },
            },
            {
                "id": "pacto_oscuro",
                "text": "Ofrecer sangre al vacío que habita la piedra.",
                "tag": "[MARCADO]",
                "visible_if": {
                    "required_flags": ["marcado_por_el_vacio"],
                    "forbidden_flags": [],
                },
                "consequences": {
                    "hp": -4,
                    "sanity": 0,
                    "gold": 0,
                    "set_flags": {"pacto_con_el_altar": True, "el_vacío_escucha": True},
                    "clear_flags": [],
                    "outcome": (
                        "La piedra bebe. Lentamente, con algo que se parece a la gratitud. "
                        "No sientes nada. Eso es lo que te preocupa."
                    ),
                },
            },
            {
                "id": "ignorar",
                "text": "Ignorarlo. Algunas cosas es mejor no tocar.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": 0,
                    "gold": 0,
                    "set_flags": {},
                    "clear_flags": [],
                    "outcome": "Pasas de largo. El altar no te sigue con la mirada. Casi seguro.",
                },
            },
        ],
    },

    # ------------------------------------------------------------------ #
    #  EL PRISIONERO                                                       #
    # ------------------------------------------------------------------ #
    {
        "id": "el_prisionero",
        "name": "Celda del Prisionero",
        "flavor_text": (
            "Hay alguien encadenado a la pared. Vivo, aunque no parece que eso le importe. "
            "Te mira con ojos que ya han visto demasiado para pedir ayuda."
        ),
        "conditions": {
            "min_depth": 1,
            "required_flags": [],
            "forbidden_flags": ["liberó_al_prisionero", "mató_al_prisionero"],
        },
        "choices": [
            {
                "id": "liberar",
                "text": "Romper las cadenas. Aunque ralentice el avance.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": 3,
                    "gold": 0,
                    "set_flags": {"liberó_al_prisionero": True, "tiene_aliado_potencial": True},
                    "clear_flags": [],
                    "outcome": (
                        "Las cadenas ceden. El prisionero no dice gracias. "
                        "Solo: 'Sé dónde están las salidas. Si sobrevives, búscame.' "
                        "Desaparece en la oscuridad antes de que puedas responder."
                    ),
                },
            },
            {
                "id": "interrogar",
                "text": "Preguntar qué sabe antes de decidir.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": 0,
                    "gold": 0,
                    "set_flags": {"interrogó_al_prisionero": True},
                    "clear_flags": [],
                    "outcome": (
                        "Habla. Con dificultad, pero habla. "
                        "Hay un camino en la capa siguiente que evita la sala principal. "
                        "No te dice cómo sabe esto. Tú tampoco preguntas."
                    ),
                },
            },
            {
                "id": "matar",
                "text": "Terminar con su sufrimiento. Una sola vez no costará nada.",
                "tag": "[ACTO IRREVERSIBLE]",
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": -4,
                    "gold": 3,
                    "set_flags": {"mató_al_prisionero": True, "tiene_sangre_inocente": True},
                    "clear_flags": [],
                    "outcome": (
                        "Rápido. Limpio. Tenía algo en el bolsillo. "
                        "Te dices que era lo más humano. "
                        "La siguiente vez que te lo digas, lo creerás menos."
                    ),
                },
            },
            {
                "id": "dejar",
                "text": "Dejarlo. No es tu problema.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": -1,
                    "gold": 0,
                    "set_flags": {"abandonó_al_prisionero": True},
                    "clear_flags": [],
                    "outcome": (
                        "Sigues. Sus ojos te siguen también, "
                        "aunque ya no puedas verlos."
                    ),
                },
            },
        ],
    },

    # ------------------------------------------------------------------ #
    #  EL ESPEJO ROTO                                                      #
    # ------------------------------------------------------------------ #
    {
        "id": "el_espejo_roto",
        "name": "El Espejo Roto",
        "flavor_text": (
            "Un espejo de cuerpo entero, agrietado pero entero. "
            "Tu reflejo está ahí. "
            "Se mueve un momento antes que tú."
        ),
        "conditions": {
            "min_depth": 2,
            "required_flags": [],
            "forbidden_flags": ["espejo_destruido"],
        },
        "choices": [
            {
                "id": "mirar",
                "text": "Mirarte. Necesitas saber qué ves.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": -3,
                    "gold": 0,
                    "set_flags": {"vio_su_reflejo": True},
                    "clear_flags": [],
                    "outcome": (
                        "Tu reflejo sonríe. Tú no. "
                        "Cuando apartas la vista, en el cristal hay escrito algo. "
                        "No reconoces la letra, pero es tu caligrafía."
                    ),
                },
            },
            {
                "id": "destruir",
                "text": "Romperlo. Siete años de mala suerte no pueden ser peores que esto.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": -1,
                    "sanity": 2,
                    "gold": 0,
                    "set_flags": {"espejo_destruido": True},
                    "clear_flags": [],
                    "outcome": (
                        "El cristal cede. Tu reflejo no grita. "
                        "Solo te mira hasta el último fragmento. "
                        "El silencio que queda es mejor."
                    ),
                },
            },
            {
                "id": "hablar",
                "text": "Hablarle. Preguntar qué sabe.",
                "tag": "[HEREJE]",
                "visible_if": {
                    "required_flags": ["marcado_por_el_vacio"],
                    "forbidden_flags": [],
                },
                "consequences": {
                    "hp": 0,
                    "sanity": -1,
                    "gold": 0,
                    "set_flags": {"habló_con_su_reflejo": True, "el_reflejo_sabe": True},
                    "clear_flags": [],
                    "outcome": (
                        "Responde. Con tu voz, pero con otras palabras. "
                        "Te dice que el jefe del nivel no es lo que parece. "
                        "Te dice que tú tampoco."
                    ),
                },
            },
            {
                "id": "ignorar",
                "text": "Apartar la vista y seguir. No necesitas esto.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": 0,
                    "gold": 0,
                    "set_flags": {"ignoró_el_espejo": True},
                    "clear_flags": [],
                    "outcome": "Bien hecho. Algunos umbrales es mejor no cruzarlos.",
                },
            },
        ],
    },

    # ------------------------------------------------------------------ #
    #  BIBLIOTECA DE CENIZA                                                #
    # ------------------------------------------------------------------ #
    {
        "id": "biblioteca_ceniza",
        "name": "Biblioteca de Ceniza",
        "flavor_text": (
            "Estanterías hasta el techo. Todos los libros quemados, "
            "excepto uno. Está abierto en la última página."
        ),
        "conditions": {
            "min_depth": 2,
            "required_flags": [],
            "forbidden_flags": [],
        },
        "choices": [
            {
                "id": "leer",
                "text": "Leer la última página.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": ["leyó_el_libro"]},
                "consequences": {
                    "hp": 0,
                    "sanity": -2,
                    "gold": 0,
                    "set_flags": {"leyó_el_libro": True, "conoce_la_verdad_del_dungeon": True},
                    "clear_flags": [],
                    "outcome": (
                        "El texto describe este dungeon. Con detalle. "
                        "Describe también a alguien que llega a esta sala y lee este libro. "
                        "La descripción coincide contigo en todo menos en una cosa. "
                        "Esa cosa no entiendes qué significa."
                    ),
                },
            },
            {
                "id": "quemar",
                "text": "Quemarlo. Si sobrevivió a algo, es peligroso.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": 1,
                    "gold": 0,
                    "set_flags": {"quemó_el_libro": True},
                    "clear_flags": [],
                    "outcome": (
                        "Arde rápido. Demasiado rápido. "
                        "En el humo crees ver palabras, pero decides que no."
                    ),
                },
            },
            {
                "id": "llevarlo",
                "text": "Guardarlo. El conocimiento tiene precio.",
                "tag": None,
                "visible_if": {
                    "required_flags": [],
                    "forbidden_flags": ["lleva_el_libro"],
                },
                "consequences": {
                    "hp": 0,
                    "sanity": -1,
                    "gold": 0,
                    "set_flags": {
                        "lleva_el_libro": True,
                        "conoce_la_verdad_del_dungeon": True,
                        "leyó_el_libro": True,
                    },
                    "clear_flags": [],
                    "outcome": (
                        "Lo guardas sin leerlo. O eso te dices. "
                        "Pero ya sabes lo que ponía en la última página. "
                        "No recuerdas haberla leído."
                    ),
                },
            },
        ],
    },

    # ------------------------------------------------------------------ #
    #  EL SUSURRO EN LA PARED                                              #
    # ------------------------------------------------------------------ #
    {
        "id": "susurro_en_la_pared",
        "name": "El Susurro en la Pared",
        "flavor_text": (
            "La pared respira. O algo detrás de ella. "
            "Una voz, si puede llamarse así, dice tu nombre. "
            "Tu nombre verdadero. El que no usas."
        ),
        "conditions": {
            "min_depth": 3,
            "required_flags": [],
            "forbidden_flags": ["pactó_con_el_susurro"],
        },
        "choices": [
            {
                "id": "responder",
                "text": "Responder. ¿Qué quieres?",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": -3,
                    "gold": 0,
                    "set_flags": {"respondió_al_susurro": True},
                    "clear_flags": [],
                    "outcome": (
                        "El susurro dice: 'Lo mismo que tú.' "
                        "No elabora. La pared deja de respirar. "
                        "Ahora tú respiras un poco más rápido."
                    ),
                },
            },
            {
                "id": "pactar",
                "text": "Negociar. Si sabe tu nombre, sabe cosas.",
                "tag": None,
                "visible_if": {
                    "required_flags": [],
                    "forbidden_flags": ["rezó_al_vacío"],
                },
                "consequences": {
                    "hp": -3,
                    "sanity": 0,
                    "gold": 15,
                    "set_flags": {"pactó_con_el_susurro": True, "deuda_con_lo_innombrable": True},
                    "clear_flags": [],
                    "outcome": (
                        "El acuerdo se sella sin palabras. "
                        "Aparece oro en tus manos, del tipo que no pregunta de dónde viene. "
                        "Algo en tu pecho se siente diferente. Como si ya no fuera tuyo del todo."
                    ),
                },
            },
            {
                "id": "ignorar_susurro",
                "text": "Taparte los oídos y seguir.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": -1,
                    "gold": 0,
                    "set_flags": {"ignoró_el_susurro": True},
                    "clear_flags": [],
                    "outcome": (
                        "La voz no insiste. Eso también es inquietante."
                    ),
                },
            },
            {
                "id": "atacar_pared",
                "text": "Golpear la pared. Lo que sea que esté ahí, que salga.",
                "tag": "[ABRAZA EL DOLOR]",
                "visible_if": {
                    "required_flags": ["abraza_el_dolor"],
                    "forbidden_flags": [],
                },
                "consequences": {
                    "hp": -5,
                    "sanity": 4,
                    "gold": 0,
                    "set_flags": {"golpeó_la_pared": True},
                    "clear_flags": [],
                    "outcome": (
                        "Golpeas hasta que los nudillos sangran. El susurro calla. "
                        "El dolor es limpio. El silencio también."
                    ),
                },
            },
        ],
    },

    # ------------------------------------------------------------------ #
    #  HABITACIÓN DEL ESCRIBA MUERTO                                       #
    # ------------------------------------------------------------------ #
    {
        "id": "escriba_muerto",
        "name": "Habitación del Escriba Muerto",
        "flavor_text": (
            "Un hombre muerto sobre un escritorio, pluma en mano. "
            "Lleva muerto semanas. La tinta de su última frase todavía está húmeda."
        ),
        "conditions": {
            "min_depth": 1,
            "required_flags": [],
            "forbidden_flags": [],
        },
        "choices": [
            {
                "id": "leer_nota",
                "text": "Leer lo que estaba escribiendo.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": ["leyó_la_nota"]},
                "consequences": {
                    "hp": 0,
                    "sanity": -1,
                    "gold": 0,
                    "set_flags": {"leyó_la_nota": True},
                    "clear_flags": [],
                    "outcome": (
                        "La nota dice: 'Ya sé que estás aquí. "
                        "Llevo días esperando. No tengas prisa.' "
                        "La tinta es de hoy."
                    ),
                },
            },
            {
                "id": "rebuscar",
                "text": "Rebuscar en sus pertenencias.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": 0,
                    "gold": 6,
                    "set_flags": {"robó_al_escriba": True},
                    "clear_flags": [],
                    "outcome": (
                        "Monedas, un sello de cera, dos velas. "
                        "Nada que explique qué hacía aquí. "
                        "O por qué sonríe."
                    ),
                },
            },
            {
                "id": "continuar_escritura",
                "text": "Continuar lo que estaba escribiendo.",
                "tag": "[CONOCE LA VERDAD]",
                "visible_if": {
                    "required_flags": ["conoce_la_verdad_del_dungeon"],
                    "forbidden_flags": [],
                },
                "consequences": {
                    "hp": 0,
                    "sanity": 2,
                    "gold": 0,
                    "set_flags": {"completó_el_manuscrito": True},
                    "clear_flags": [],
                    "outcome": (
                        "Las palabras salen solas. Como si ya supieras qué faltaba. "
                        "Cuando terminas, el escriba ya no sonríe. "
                        "Eso es mejor."
                    ),
                },
            },
        ],
    },

    # ------------------------------------------------------------------ #
    #  LA HOGUERA DEL DESERTOR                                             #
    # ------------------------------------------------------------------ #
    {
        "id": "hoguera_desertor",
        "name": "La Hoguera del Desertor",
        "flavor_text": (
            "Una pequeña hoguera. Alguien la encendió hace poco. "
            "Hay un cadáver junto a ella — un soldado, con su propia espada clavada. "
            "No hay señales de lucha."
        ),
        "conditions": {
            "min_depth": 1,
            "required_flags": [],
            "forbidden_flags": [],
        },
        "choices": [
            {
                "id": "calentar",
                "text": "Sentarse y calentarse. Solo un momento.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 3,
                    "sanity": 2,
                    "gold": 0,
                    "set_flags": {"descansó_junto_al_muerto": True},
                    "clear_flags": [],
                    "outcome": (
                        "El calor es real. El silencio también. "
                        "No preguntas por qué eligió esto. "
                        "Quizás lo entiendes demasiado bien."
                    ),
                },
            },
            {
                "id": "registrar",
                "text": "Registrar el cadáver.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": ["robó_al_desertor"]},
                "consequences": {
                    "hp": 0,
                    "sanity": -1,
                    "gold": 9,
                    "set_flags": {"robó_al_desertor": True},
                    "clear_flags": [],
                    "outcome": (
                        "Llevaba más de lo esperado para un desertor. "
                        "Una carta sin terminar. No la lees. "
                        "O eso te dices."
                    ),
                },
            },
            {
                "id": "seguir_su_camino",
                "text": "Apagar la hoguera y seguir. Nadie debería encontrar esto.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": 1,
                    "gold": 0,
                    "set_flags": {"apagó_la_hoguera": True},
                    "clear_flags": [],
                    "outcome": "La oscuridad vuelve. Más justa que la luz.",
                },
            },
            {
                "id": "honrar",
                "text": "Sacarle la espada. Merece descansar.",
                "tag": "[LIBERASTE AL PRISIONERO]",
                "visible_if": {
                    "required_flags": ["liberó_al_prisionero"],
                    "forbidden_flags": [],
                },
                "consequences": {
                    "hp": 0,
                    "sanity": 3,
                    "gold": 0,
                    "set_flags": {"honró_al_desertor": True},
                    "clear_flags": [],
                    "outcome": (
                        "Lo haces despacio. Con cuidado. "
                        "No sabes por qué importa, pero importa."
                    ),
                },
            },
        ],
    },

    # ------------------------------------------------------------------ #
    #  EL POZO SIN FONDO                                                   #
    # ------------------------------------------------------------------ #
    {
        "id": "pozo_sin_fondo",
        "name": "El Pozo Sin Fondo",
        "flavor_text": (
            "Un pozo en el centro de la sala. "
            "Tiras una piedra. No oyes que llegue al fondo. "
            "Pero algo oye la piedra."
        ),
        "conditions": {
            "min_depth": 2,
            "required_flags": [],
            "forbidden_flags": ["tiró_al_pozo"],
        },
        "choices": [
            {
                "id": "mirar",
                "text": "Asomarse al borde y mirar.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": -3,
                    "gold": 0,
                    "set_flags": {"miró_al_pozo": True},
                    "clear_flags": [],
                    "outcome": (
                        "No ves el fondo. Pero ves algo que sube. "
                        "Muy despacio. Te apartas antes de que llegue."
                    ),
                },
            },
            {
                "id": "tirar_oro",
                "text": "Tirar una moneda. Por si acaso.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": 2,
                    "gold": -3,
                    "set_flags": {"tiró_al_pozo": True},
                    "clear_flags": [],
                    "outcome": (
                        "La moneda cae en silencio. "
                        "Unos segundos después, escuchas dos monedas chocando contra el suelo "
                        "detrás de ti. No hay nadie."
                    ),
                },
            },
            {
                "id": "tirar_algo",
                "text": "Tirar algo que no quieres recordar.",
                "tag": "[DEUDA PENDIENTE]",
                "visible_if": {
                    "required_flags": ["deuda_con_lo_innombrable"],
                    "forbidden_flags": [],
                },
                "consequences": {
                    "hp": 0,
                    "sanity": 4,
                    "gold": 0,
                    "set_flags": {"saldó_la_deuda": True},
                    "clear_flags": ["deuda_con_lo_innombrable"],
                    "outcome": (
                        "El pozo acepta. "
                        "Algo en tu pecho que llevaba apretado se afloja. "
                        "No preguntes el precio de este alivio."
                    ),
                },
            },
            {
                "id": "ignorar_pozo",
                "text": "Rodearlo y no mirar atrás.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": 0,
                    "gold": 0,
                    "set_flags": {},
                    "clear_flags": [],
                    "outcome": "Lo rodeás. No miras atrás. Eso ya es algo.",
                },
            },
        ],
    },

    # ------------------------------------------------------------------ #
    #  LOS DOS CAMINOS                                                     #
    # ------------------------------------------------------------------ #
    {
        "id": "los_dos_caminos",
        "name": "La Encrucijada",
        "flavor_text": (
            "La galería se divide en dos. "
            "Por la izquierda: silencio absoluto. "
            "Por la derecha: un sonido que podría ser respiración. "
            "O podría ser el viento. No hay viento aquí."
        ),
        "conditions": {
            "min_depth": 1,
            "required_flags": [],
            "forbidden_flags": [],
        },
        "choices": [
            {
                "id": "izquierda",
                "text": "Ir por donde hay silencio.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": -1,
                    "gold": 6,
                    "set_flags": {"eligió_el_silencio": True},
                    "clear_flags": [],
                    "outcome": (
                        "El silencio era real. Y en él, algo brillaba. "
                        "Monedas. De alguien que también eligió el silencio "
                        "y no volvió para contarlo."
                    ),
                },
            },
            {
                "id": "derecha",
                "text": "Ir hacia la respiración.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": -3,
                    "sanity": 2,
                    "gold": 0,
                    "set_flags": {"eligió_la_respiración": True},
                    "clear_flags": [],
                    "outcome": (
                        "Era viento. Frío, desde una grieta en la roca. "
                        "Pero la grieta es demasiado pequeña para que viniera solo el viento. "
                        "El arañazo en tu brazo ya lo sabía."
                    ),
                },
            },
            {
                "id": "esperar",
                "text": "Esperar a que algo se decida por ti.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": -1,
                    "sanity": -2,
                    "gold": 0,
                    "set_flags": {"esperó_en_la_encrucijada": True},
                    "clear_flags": [],
                    "outcome": (
                        "Esperas. Nada se decide. "
                        "El frío sí. El frío siempre se decide."
                    ),
                },
            },
        ],
    },

    # ------------------------------------------------------------------ #
    #  EL NIÑO PERDIDO                                                     #
    # ------------------------------------------------------------------ #
    {
        "id": "nino_perdido",
        "name": "La Voz en la Oscuridad",
        "flavor_text": (
            "Una voz. Pequeña. Llama desde la oscuridad. "
            "Dice que está perdida. Dice que tiene miedo. "
            "Suena exactamente como debería sonar."
        ),
        "conditions": {
            "min_depth": 2,
            "required_flags": [],
            "forbidden_flags": ["encontró_la_voz"],
        },
        "choices": [
            {
                "id": "acercarse",
                "text": "Acercarse a la voz.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": -6,
                    "sanity": -2,
                    "gold": 0,
                    "set_flags": {"encontró_la_voz": True, "la_voz_mintió": True},
                    "clear_flags": [],
                    "outcome": (
                        "No era un niño. "
                        "Nunca lo fue. "
                        "Lo que era te alcanza antes de que puedas reaccionar."
                    ),
                },
            },
            {
                "id": "ignorar_voz",
                "text": "Ignorarla. En una dungeon, las voces mienten.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": -2,
                    "gold": 0,
                    "set_flags": {"encontró_la_voz": True, "ignoró_la_voz": True},
                    "clear_flags": [],
                    "outcome": (
                        "La voz llora. Cada vez más fuerte. "
                        "Luego se detiene. "
                        "El silencio que sigue es peor que el llanto."
                    ),
                },
            },
            {
                "id": "responder_voz",
                "text": "Responder desde donde estás. Sin acercarte.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": -2,
                    "sanity": 1,
                    "gold": 0,
                    "set_flags": {"encontró_la_voz": True, "respondió_con_cautela": True},
                    "clear_flags": [],
                    "outcome": (
                        "La voz calla. Un segundo. "
                        "Luego dice, con tu mismo tono: '¿Eso es todo lo que tienes?' "
                        "Algo te roza en la oscuridad y se aleja."
                    ),
                },
            },
            {
                "id": "trampa",
                "text": "Tender una trampa y esperar.",
                "tag": "[CONOCES EL DUNGEON]",
                "visible_if": {
                    "required_flags": ["conoce_la_verdad_del_dungeon"],
                    "forbidden_flags": [],
                },
                "consequences": {
                    "hp": 0,
                    "sanity": 0,
                    "gold": 8,
                    "set_flags": {"encontró_la_voz": True, "atrapó_a_la_voz": True},
                    "clear_flags": [],
                    "outcome": (
                        "Era exactamente lo que esperabas. "
                        "Lo que queda después sirve para algo. "
                        "No preguntes para qué."
                    ),
                },
            },
        ],
    },

    # ------------------------------------------------------------------ #
    #  EL REENCUENTRO                                                       #
    #  Usa: tiene_aliado_potencial (prisionero liberado)                    #
    #  Primera vez que ese flag tiene consecuencias reales.                 #
    # ------------------------------------------------------------------ #
    {
        "id": "el_reencuentro",
        "name": "El Reencuentro",
        "flavor_text": (
            "Una figura en las sombras. "
            "La reconoces — es el prisionero que liberaste. "
            "Parece que encontró un camino. "
            "Parece que te estaba esperando."
        ),
        "conditions": {
            "min_depth": 2,
            "required_flags": ["tiene_aliado_potencial"],
            "forbidden_flags": ["usó_al_aliado"],
        },
        "choices": [
            {
                "id": "ir_juntos",
                "text": "Ofrecerle ir juntos. Dos sobreviven mejor que uno.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 8,
                    "sanity": 5,
                    "gold": 0,
                    "set_flags": {"usó_al_aliado": True, "fue_con_el_aliado": True},
                    "clear_flags": [],
                    "outcome": (
                        "Camináis juntos un trecho. "
                        "Conoce el dungeon mejor que tú. "
                        "Os separan en el siguiente cruce, pero antes te vendó las heridas "
                        "y te contó dónde estaban las trampas."
                    ),
                },
            },
            {
                "id": "pedirle_informacion",
                "text": "Preguntarle qué sabe del dungeon antes de seguir solos.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": 3,
                    "gold": 10,
                    "set_flags": {"usó_al_aliado": True, "tiene_mapa_mental": True},
                    "clear_flags": [],
                    "outcome": (
                        "Habla rápido. Hay un depósito en la siguiente capa, "
                        "y una sala que conviene evitar a toda costa. "
                        "También tiene monedas que no necesita. "
                        "Las acepta quien las necesita más."
                    ),
                },
            },
            {
                "id": "seguir_solo",
                "text": "Decirle que cada uno va por su cuenta.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": -1,
                    "gold": 0,
                    "set_flags": {"usó_al_aliado": True, "rechazó_al_aliado": True},
                    "clear_flags": [],
                    "outcome": (
                        "Asiente. No parece sorprendido. "
                        "Desaparece en la oscuridad sin mirar atrás. "
                        "Probablemente sea lo más sensato."
                    ),
                },
            },
        ],
    },

    # ------------------------------------------------------------------ #
    #  EL ECO DE LO QUE HICISTE                                            #
    #  Usa: tiene_sangre_inocente + abandonó_al_prisionero                 #
    #  Solo aparece si el jugador tomó decisiones oscuras.                  #
    # ------------------------------------------------------------------ #
    {
        "id": "eco_de_lo_que_hiciste",
        "name": "El Eco",
        "flavor_text": (
            "No hay nada en esta sala. "
            "Solo un charco de agua en el suelo que refleja algo "
            "que no está encima de él."
        ),
        "conditions": {
            "min_depth": 2,
            "required_flags": [],
            "forbidden_flags": ["vio_el_eco"],
        },
        "choices": [
            {
                "id": "mirar_el_reflejo",
                "text": "Mirar lo que muestra el charco.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": -2,
                    "gold": 0,
                    "set_flags": {"vio_el_eco": True},
                    "clear_flags": [],
                    "outcome": (
                        "Ves lo que hiciste. "
                        "No lo que crees que hiciste — lo que realmente ocurrió. "
                        "La diferencia es pequeña. "
                        "Eso es lo peor."
                    ),
                },
            },
            {
                "id": "mirar_culpa",
                "text": "Mirar. Lo mereces.",
                "tag": "[SANGRE INOCENTE]",
                "visible_if": {
                    "required_flags": ["tiene_sangre_inocente"],
                    "forbidden_flags": [],
                },
                "consequences": {
                    "hp": -3,
                    "sanity": 5,
                    "gold": 0,
                    "set_flags": {"vio_el_eco": True, "asumió_la_culpa": True},
                    "clear_flags": ["tiene_sangre_inocente"],
                    "outcome": (
                        "Lo miras hasta que duele. "
                        "No se borra. Pero algo en ti se asienta. "
                        "La culpa que se mira de frente pesa menos que la que se evita."
                    ),
                },
            },
            {
                "id": "romper_el_charco",
                "text": "Pisarlo. No necesitas ver eso.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": 1,
                    "gold": 0,
                    "set_flags": {"vio_el_eco": True, "rompió_el_eco": True},
                    "clear_flags": [],
                    "outcome": (
                        "El agua se dispersa. La imagen desaparece. "
                        "Lo que hiciste no."
                    ),
                },
            },
        ],
    },

    # ------------------------------------------------------------------ #
    #  EL MERCADER SIN ROSTRO                                              #
    #  Aparece en cualquier profundidad. Compra cosas raras.               #
    #  Primera vez que el oro tiene un uso narrativo más allá de items.    #
    # ------------------------------------------------------------------ #
    {
        "id": "mercader_sin_rostro",
        "name": "El Mercader Sin Rostro",
        "flavor_text": (
            "Hay alguien sentado junto a una vela. "
            "Vende cosas. No tiene cara — solo un lienzo en blanco "
            "donde debería haber una. "
            "Esto no te sorprende tanto como debería."
        ),
        "conditions": {
            "min_depth": 1,
            "required_flags": [],
            "forbidden_flags": ["trató_con_el_mercader"],
        },
        "choices": [
            {
                "id": "comprar_calma",
                "text": "Comprar calma. (15 oro → +8 Cordura)",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": 8,
                    "gold": -15,
                    "set_flags": {"trató_con_el_mercader": True},
                    "clear_flags": [],
                    "outcome": (
                        "Te entrega un frasco de nada. "
                        "Lo bebes. Sabe a silencio. "
                        "Funciona de todos modos."
                    ),
                },
            },
            {
                "id": "comprar_fuerza",
                "text": "Comprar fuerza prestada. (20 oro → +10 HP)",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 10,
                    "sanity": -2,
                    "gold": -20,
                    "set_flags": {"trató_con_el_mercader": True, "fuerza_prestada": True},
                    "clear_flags": [],
                    "outcome": (
                        "Lo que te entrega no es un objeto. "
                        "Es una sensación. "
                        "Vitalidad que no era tuya. "
                        "Alguien en algún lugar acaba de sentirse peor."
                    ),
                },
            },
            {
                "id": "vender_recuerdo",
                "text": "Venderle algo que no quieres recordar.",
                "tag": "[LADRÓN]",
                "visible_if": {
                    "required_flags": [],
                    "forbidden_flags": [],
                    # Opción estética para el Ladrón, pero visible para todos
                    # — el Ladrón tiene más práctica vendiendo lo que no es suyo
                },
                "consequences": {
                    "hp": 0,
                    "sanity": 4,
                    "gold": 18,
                    "set_flags": {"trató_con_el_mercader": True, "vendió_un_recuerdo": True},
                    "clear_flags": [],
                    "outcome": (
                        "Acepta. Te paga. "
                        "Unos pasos después intentas recordar qué vendiste "
                        "y no puedes. "
                        "Eso también es un servicio."
                    ),
                },
            },
            {
                "id": "ignorar_mercader",
                "text": "Ignorarlo y seguir.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": 0,
                    "gold": 0,
                    "set_flags": {"trató_con_el_mercader": True},
                    "clear_flags": [],
                    "outcome": (
                        "No reacciona. "
                        "Cuando miras atrás, ya no está. "
                        "La vela tampoco."
                    ),
                },
            },
        ],
    },

    # ------------------------------------------------------------------ #
    #  EL SUEÑO LÚCIDO                                                     #
    #  depth 3+. Evento de clase — cada clase tiene una opción exclusiva.  #
    #  El Soldado Roto y el Ladrón por fin tienen presencia narrativa.     #
    # ------------------------------------------------------------------ #
    {
        "id": "sueno_lucido",
        "name": "El Sueño Lúcido",
        "flavor_text": (
            "El dungeon desaparece un momento. "
            "Estás en algún lugar que reconoces — antes de todo esto. "
            "Sabes que es un sueño. "
            "También sabes que cuando despiertes algo habrá cambiado."
        ),
        "conditions": {
            "min_depth": 3,
            "required_flags": [],
            "forbidden_flags": ["tuvo_el_sueño"],
        },
        "choices": [
            {
                "id": "quedarse_en_el_sueño",
                "text": "Quedarse. Solo un poco más.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 6,
                    "sanity": 6,
                    "gold": 0,
                    "set_flags": {"tuvo_el_sueño": True, "eligió_quedarse": True},
                    "clear_flags": [],
                    "outcome": (
                        "Descansas de verdad por primera vez. "
                        "Cuando despiertas, el dungeon sigue igual. "
                        "Tú, no del todo."
                    ),
                },
            },
            {
                "id": "sueño_soldado",
                "text": "Recordar por qué empezaste. Usarlo.",
                "tag": "[SOLDADO]",
                "visible_if": {
                    "required_flags": [],
                    "forbidden_flags": ["marcado_por_el_vacio", "abraza_el_dolor"],
                },
                "consequences": {
                    "hp": 4,
                    "sanity": 0,
                    "gold": 0,
                    "set_flags": {"tuvo_el_sueño": True, "recordó_el_origen": True},
                    "clear_flags": [],
                    "outcome": (
                        "Recuerdas el rostro de alguien. "
                        "No su nombre — eso lo perdiste hace tiempo. "
                        "Pero el rostro es suficiente. "
                        "Te despiertas con los puños apretados y el paso firme."
                    ),
                },
            },
            {
                "id": "sueño_hereje",
                "text": "Hablar con lo que vive en el sueño.",
                "tag": "[HEREJE]",
                "visible_if": {
                    "required_flags": ["marcado_por_el_vacio"],
                    "forbidden_flags": [],
                },
                "consequences": {
                    "hp": -2,
                    "sanity": 0,
                    "gold": 0,
                    "set_flags": {
                        "tuvo_el_sueño": True,
                        "habló_con_el_vacío_en_sueños": True,
                    },
                    "clear_flags": [],
                    "outcome": (
                        "Está ahí. Como siempre. "
                        "Te dice algo que no puedes repetir. "
                        "Cuando despiertas, sabes exactamente qué hay en la siguiente sala. "
                        "No sabes cómo lo sabes."
                    ),
                },
            },
            {
                "id": "sueño_flagelante",
                "text": "Convertir el dolor del sueño en combustible.",
                "tag": "[FLAGELANTE]",
                "visible_if": {
                    "required_flags": ["abraza_el_dolor"],
                    "forbidden_flags": [],
                },
                "consequences": {
                    "hp": -4,
                    "sanity": 8,
                    "gold": 0,
                    "set_flags": {"tuvo_el_sueño": True, "dolor_convertido": True},
                    "clear_flags": [],
                    "outcome": (
                        "En el sueño te golpeas contra las paredes "
                        "hasta que el dolor se vuelve claridad. "
                        "Despiertas sangrando. "
                        "La mente, sin embargo, está quieta."
                    ),
                },
            },
        ],
    },

    # ------------------------------------------------------------------ #
    #  EL JUICIO                                                           #
    #  depth 4+. Evento de convergencia — usa flags acumulados.            #
    #  El dungeon recuerda lo que hiciste.                                 #
    # ------------------------------------------------------------------ #
    {
        "id": "el_juicio",
        "name": "La Sala del Juicio",
        "flavor_text": (
            "Una sala circular. En el centro, una balanza de piedra. "
            "Los platillos se mueven solos. "
            "No hay nadie más aquí, pero alguien te está mirando."
        ),
        "conditions": {
            "min_depth": 4,
            "required_flags": [],
            "forbidden_flags": ["fue_juzgado"],
        },
        "choices": [
            {
                "id": "juicio_aceptar",
                "text": "Acercarse a la balanza. Dejar que decida.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 0,
                    "sanity": -3,
                    "gold": 0,
                    "set_flags": {"fue_juzgado": True, "aceptó_el_juicio": True},
                    "clear_flags": [],
                    "outcome": (
                        "La balanza se inclina. "
                        "No ves hacia qué lado. "
                        "Eso también es una respuesta."
                    ),
                },
            },
            {
                "id": "juicio_culpable",
                "text": "Declararte culpable antes de que lo haga ella.",
                "tag": "[SANGRE INOCENTE]",
                "visible_if": {
                    "required_flags": ["tiene_sangre_inocente"],
                    "forbidden_flags": [],
                },
                "consequences": {
                    "hp": -5,
                    "sanity": 8,
                    "gold": 0,
                    "set_flags": {
                        "fue_juzgado": True,
                        "se_declaró_culpable": True,
                    },
                    "clear_flags": ["tiene_sangre_inocente"],
                    "outcome": (
                        "La balanza se detiene. "
                        "Como si no esperara eso. "
                        "El dolor es real. "
                        "La cordura que recuperas también."
                    ),
                },
            },
            {
                "id": "juicio_inocente",
                "text": "Declararte inocente. Sostener la mirada.",
                "tag": None,
                "visible_if": {
                    "required_flags": [],
                    "forbidden_flags": ["tiene_sangre_inocente", "mató_al_prisionero"],
                },
                "consequences": {
                    "hp": 5,
                    "sanity": 5,
                    "gold": 0,
                    "set_flags": {"fue_juzgado": True, "se_declaró_inocente": True},
                    "clear_flags": [],
                    "outcome": (
                        "La balanza no se mueve. "
                        "Quizás eso sea ganar. "
                        "Quizás la balanza no funciona y esto no significa nada. "
                        "De cualquier modo, el camino sigue."
                    ),
                },
            },
            {
                "id": "juicio_ignorar",
                "text": "Pasar por delante sin mirar. No reconoces su autoridad.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": -2,
                    "sanity": -2,
                    "gold": 5,
                    "set_flags": {"fue_juzgado": True, "ignoró_el_juicio": True},
                    "clear_flags": [],
                    "outcome": (
                        "La balanza se vuelca al pasar. "
                        "Algo cae al suelo — monedas. "
                        "De dónde venían, no prefieres saberlo."
                    ),
                },
            },
        ],
    },

    # ------------------------------------------------------------------ #
    #  EL ÚLTIMO ESPEJO                                                    #
    #  depth 5. Evento final antes del boss.                               #
    #  Usa casi todo lo acumulado. Sin opciones incorrectas.               #
    # ------------------------------------------------------------------ #
    {
        "id": "el_ultimo_espejo",
        "name": "El Último Espejo",
        "flavor_text": (
            "Otro espejo. Pero este no está roto. "
            "Y tu reflejo eres tú — exactamente tú, "
            "con todo lo que llevas encima. "
            "Dice: 'Queda una sala.'"
        ),
        "conditions": {
            "min_depth": 5,
            "required_flags": [],
            "forbidden_flags": ["vio_el_último_espejo"],
        },
        "choices": [
            {
                "id": "prepararse",
                "text": "Prepararte. Lo que sea que venga, lo recibes.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 4,
                    "sanity": 4,
                    "gold": 0,
                    "set_flags": {"vio_el_último_espejo": True, "entró_preparado": True},
                    "clear_flags": [],
                    "outcome": (
                        "El reflejo asiente. "
                        "Por primera vez en todo el dungeon, "
                        "algo te mira sin querer algo a cambio."
                    ),
                },
            },
            {
                "id": "preguntar_al_reflejo",
                "text": "Preguntarle si hay algo al otro lado.",
                "tag": None,
                "visible_if": {
                    "required_flags": [],
                    "forbidden_flags": ["espejo_destruido"],
                },
                "consequences": {
                    "hp": 0,
                    "sanity": 3,
                    "gold": 0,
                    "set_flags": {
                        "vio_el_último_espejo": True,
                        "sabe_lo_que_hay_al_otro_lado": True,
                    },
                    "clear_flags": [],
                    "outcome": (
                        "Responde: 'Lo mismo que aquí, pero sin ti.' "
                        "No es una amenaza. "
                        "Tampoco un consuelo. "
                        "Es la única respuesta honesta que has recibido."
                    ),
                },
            },
            {
                "id": "romper_este_espejo",
                "text": "Romperlo. Ya rompiste el otro.",
                "tag": "[ESPEJO DESTRUIDO]",
                "visible_if": {
                    "required_flags": ["espejo_destruido"],
                    "forbidden_flags": [],
                },
                "consequences": {
                    "hp": -1,
                    "sanity": 6,
                    "gold": 0,
                    "set_flags": {
                        "vio_el_último_espejo": True,
                        "rompió_ambos_espejos": True,
                    },
                    "clear_flags": [],
                    "outcome": (
                        "Cae diferente. Sin resistencia. "
                        "Como si también lo estuviera esperando. "
                        "Los fragmentos no reflejan nada. "
                        "Por fin."
                    ),
                },
            },
            {
                "id": "dar_la_vuelta",
                "text": "Darle la espalda y entrar ya.",
                "tag": None,
                "visible_if": {"required_flags": [], "forbidden_flags": []},
                "consequences": {
                    "hp": 2,
                    "sanity": 0,
                    "gold": 0,
                    "set_flags": {"vio_el_último_espejo": True},
                    "clear_flags": [],
                    "outcome": (
                        "No necesitas un espejo para saber quién eres. "
                        "O ya no te importa saberlo. "
                        "Ambas son respuestas válidas a estas alturas."
                    ),
                },
            },
        ],
    },

]


def get_event_by_id(event_id: str) -> dict | None:
    return next((e for e in EVENTS if e["id"] == event_id), None)


def get_eligible_events(depth: int, player_flags: dict) -> list[dict]:
    """
    Devuelve todos los eventos que pueden aparecer dado el estado actual del jugador.
    """
    eligible = []
    for event in EVENTS:
        cond = event.get("conditions", {})

        if depth < cond.get("min_depth", 0):
            continue

        required = cond.get("required_flags", [])
        if any(not player_flags.get(f) for f in required):
            continue

        forbidden = cond.get("forbidden_flags", [])
        if any(player_flags.get(f) for f in forbidden):
            continue

        eligible.append(event)

    return eligible