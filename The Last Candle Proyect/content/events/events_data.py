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