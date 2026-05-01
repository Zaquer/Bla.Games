# The Last Candle

> *Un nuevo condenado despierta.*

Text-RPG roguelike de dark fantasy para terminal. Cada run es un aventurero diferente que desciende por un dungeon generado proceduralmente. No hay meta-progresión. Cuando mueres, mueres.

---

## Instalación

**Requisitos:** Python 3.10+

```bash
# 1. Clona o descarga el proyecto
cd the-last-candle

# 2. Instala la única dependencia
pip install -r requirements.txt

# 3. Arranca
python main.py
```

---

## Cómo se juega

### Navegación
En cada sala verás el mapa del dungeon y las opciones de movimiento.

| Tecla | Acción |
|-------|--------|
| `1-4` | Moverte a una sala conectada |
| `i`   | Abrir inventario |
| `m`   | Ver mapa completo |
| `q`   | Abandonar la run |

### Tipos de sala

| Icono | Tipo | Descripción |
|-------|------|-------------|
| `☠`  | Combate | Encuentro con enemigo |
| `★`  | Élite | Enemigo fuerte, mejor loot |
| `?`  | Evento | Decisión narrativa con consecuencias |
| `♨`  | Descanso | Recupera HP o Cordura |
| `$`  | Tesoro | Loot sin combate |
| `◈`  | Jefe | Boss de capa |
| `▼`  | Salida | Descenso al siguiente nivel |

### Combate

| Acción | Efecto |
|--------|--------|
| `1` Atacar | Daño basado en Fuerza + RNG |
| `2` Habilidad | Habilidad única de tu clase (con coste) |
| `3` Defender | Reduce el próximo golpe en AGI puntos |

**Estados alterados:** `BLEEDING` (-2 HP/turno), `MARKED` (+25% daño recibido), `STUNNED` (pierdes turno), `WEAKENED` (-2 FUE), `TERRIFIED` (-1 COR/turno).

### Clases

| Clase | Habilidad | Estilo |
|-------|-----------|--------|
| **Soldado Roto** | Golpe Desesperado (×1.4 daño, -2 COR) | Alto HP, fuerza bruta |
| **Hereje** | Maldición Menor (aplica MARKED, -3 HP propios) | Bajo HP, alto Arcano |
| **Ladrón** | Golpe Bajo (crit garantizado, ×1.5 si MARKED) | Alta agilidad, esquiva |
| **Flagelante** | Penitencia (-3 HP propios → ×1.8 daño) | Riesgo/recompensa extremo |

### Inventario
Límite de **6 items**. Cuando está lleno, debes tirar algo para recoger algo nuevo.

- **Consumibles:** úsalos desde el inventario (`u1`, `u2`...)
- **Equipamiento:** equípalo en un slot (`e1`, `e2`...); reemplaza el anterior
- **Items malditos ⛧:** se equipan pero no se pueden quitar. Mueres con ellos.

---

## Estructura del proyecto

```
last_candle/
├── main.py                          # Punto de entrada
├── requirements.txt
├── save/
│   └── runs.json                    # Historial de runs (se crea automáticamente)
├── engine/
│   ├── core/
│   │   ├── player.py                # M1 — Stats, flags, clases
│   │   ├── dungeon.py               # M3 — Generación procedural del grafo
│   │   └── run_manager.py           # M7 — Ciclo de run, persistencia
│   ├── systems/
│   │   ├── combat_engine.py         # M5 — Combate por turnos
│   │   ├── event_engine.py          # M4 — Motor de eventos narrativos
│   │   └── inventory.py             # M6 — Inventario, equipo, loot
│   └── ui/
│       ├── renderer.py              # M2 — Toda la capa Rich
│       └── map_renderer.py          # M3 — Minimapa ASCII
└── content/
    ├── enemies/
    │   └── enemies_data.py          # 6 enemigos con acciones ponderadas
    ├── events/
    │   └── events_data.py           # 10 eventos narrativos con flags
    └── items/
        └── items_data.py            # 16 items (consumibles, equipo, malditos)
```

---

## Expandir el juego

### Añadir un enemigo
En `content/enemies/enemies_data.py`, añade una entrada al dict `ENEMIES` siguiendo la estructura existente. El `combat_engine` lo recogerá automáticamente.

### Añadir un evento
En `content/events/events_data.py`, añade una entrada a la lista `EVENTS`. Puedes usar `required_flags` y `forbidden_flags` para que solo aparezca en ciertas condiciones.

### Añadir un item
En `content/items/items_data.py`, añade una entrada al dict `ITEMS` y referénciala en las `LOOT_TABLES` que corresponda.

---

## Sistema de flags

Las decisiones del jugador dejan flags que afectan eventos futuros. Algunos ejemplos:

- `marcado_por_el_vacio` (clase Hereje) → desbloquea opciones exclusivas en el Altar y el Espejo
- `conoce_la_verdad_del_dungeon` (leer la Biblioteca de Ceniza) → opción especial en el Escriba Muerto y la Voz en la Oscuridad
- `deuda_con_lo_innombrable` (pactar con el Susurro) → se puede saldar en el Pozo Sin Fondo
- `liberó_al_prisionero` → opción de honrar al Desertor
- `pactó_con_el_susurro` → mención en la pantalla de muerte final

---

*Construido con Python + [Rich](https://github.com/Textualize/rich)*
