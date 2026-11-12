"""
5 estrellas, a comer — la carta y el generador de pedidos al azar.

Este archivo es la "cocina" del restaurante: aquí viven todos los platos,
sus precios y la lógica que inventa pedidos sorpresa.

Funciona en dos sitios sin cambiar nada:
  * En el navegador, a través de PyScript (MicroPython), desde index.html.
  * En la terminal, con Python normal:  python3 pedido.py  [número de pedidos]

Todos los precios se guardan en céntimos (enteros) para que las cuentas
salgan siempre exactas.
"""

import random

# ---------------------------------------------------------------------------
# LA CARTA
# ---------------------------------------------------------------------------

PIZZA = {
    "nombre": "Pizza a tu gusto",
    "descripcion": "Masa fina, salsa de la casa y mozzarella. Tú eliges el resto.",
    "base": 750,
    "ingredientes": [
        ("Champiñones", 90),
        ("Piña", 100),
        ("Perejil", 40),
        ("Tomate", 70),
        ("Pepperoni", 120),
        ("Cebolla", 60),
    ],
}

TARTA = {
    "nombre": "Tarta de cumpleaños",
    "descripcion": "Bizcocho con fresas, crema de limón y cobertura de chocolate.",
    # (años que se celebran, precio). Más años, más tarta y más velas.
    "tamanos": [(1, 1400), (2, 1600), (3, 1800), (4, 2000)],
}

HELADOS = [
    {"nombre": "Cono de chocolate y fresa", "precio": 300},
    {
        "nombre": "Cono de manzana y vainilla",
        "precio": 320,
        "toppings": [("Galleta", 50), ("Plátano", 50), ("Kiwi", 60), ("Fresa", 60)],
    },
    {"nombre": "Pirulo", "precio": 150},
    {"nombre": "Palo de chocolate con almendras", "precio": 240},
    {"nombre": "Palo de fresa con chocolate", "precio": 220},
]

# Precio por kilo, en céntimos.
FRUTAS = [
    ("Sandía", 220),
    ("Melón", 250),
    ("Mango", 480),
    ("Piña", 300),
    ("Fresas", 550),
    ("Manzana", 240),
    ("Pepino", 160),
    ("Zanahoria", 140),
]

SALSAS = [("Tajín", 60), ("Azúcar", 20), ("Sal", 10)]

# Pesos que se pueden pedir, en gramos.
PESOS = [250, 500, 750, 1000, 1500, 2000]

CLIENTES = [
    "Lucía", "Mateo", "Martina", "Hugo", "Sofía", "Leo", "Valeria", "Daniel",
    "Abuela Carmen", "Tío Paco", "Doña Rosa", "El señor del sombrero",
    "Capitana Pirata", "Un dinosaurio educado", "La vecina del quinto",
]


# ---------------------------------------------------------------------------
# UTILIDADES (pensadas para funcionar también en MicroPython)
# ---------------------------------------------------------------------------

def euros(centimos):
    """1250 -> '12,50 €'"""
    return "{},{:02d} €".format(centimos // 100, centimos % 100)


def kilos(gramos):
    """750 -> '0,75 kg', 1000 -> '1 kg', 1500 -> '1,5 kg'"""
    if gramos % 1000 == 0:
        return "{} kg".format(gramos // 1000)
    texto = "{},{:03d}".format(gramos // 1000, gramos % 1000).rstrip("0")
    return texto + " kg"


def _elige(lista):
    return lista[random.randint(0, len(lista) - 1)]


def _varios(lista, minimo, maximo):
    """Elige entre `minimo` y `maximo` elementos distintos, respetando el orden de la carta."""
    n = random.randint(minimo, min(maximo, len(lista)))
    indices = list(range(len(lista)))
    elegidos = []
    for _ in range(n):
        elegidos.append(indices.pop(random.randint(0, len(indices) - 1)))
    elegidos.sort()
    return [lista[i] for i in elegidos]


def _nombres(extras):
    nombres = [nombre.lower() for nombre, _ in extras]
    if len(nombres) == 1:
        return nombres[0]
    return ", ".join(nombres[:-1]) + " y " + nombres[-1]


def _linea(cantidad, nombre, detalle, unitario):
    return {
        "cantidad": cantidad,
        "nombre": nombre,
        "detalle": detalle,
        "unitario": unitario,
        "importe": cantidad * unitario,
    }


# ---------------------------------------------------------------------------
# GENERADORES DE CADA PLATO
# ---------------------------------------------------------------------------

def pedir_pizza():
    extras = _varios(PIZZA["ingredientes"], 1, 4)
    unitario = PIZZA["base"] + sum(precio for _, precio in extras)
    return _linea(random.randint(1, 2), PIZZA["nombre"], "Con " + _nombres(extras), unitario)


def pedir_tarta():
    anos, precio = _elige(TARTA["tamanos"])
    detalle = "{} {} · {} {}".format(
        anos, "año" if anos == 1 else "años", anos, "vela" if anos == 1 else "velas"
    )
    return _linea(1, TARTA["nombre"], detalle, precio)


def pedir_helado():
    helado = _elige(HELADOS)
    unitario = helado["precio"]
    detalle = ""
    if "toppings" in helado:
        toppings = _varios(helado["toppings"], 0, 3)
        if toppings:
            unitario += sum(precio for _, precio in toppings)
            detalle = "Toppings: " + _nombres(toppings)
        else:
            detalle = "Sin toppings"
    return _linea(random.randint(1, 3), helado["nombre"], detalle, unitario)


def pedir_fruta():
    fruta, precio_kg = _elige(FRUTAS)
    gramos = _elige(PESOS)
    unitario = (precio_kg * gramos + 500) // 1000
    salsas = _varios(SALSAS, 0, 2)
    unitario += sum(precio for _, precio in salsas)
    detalle = kilos(gramos) + " · "
    detalle += ("con " + _nombres(salsas)) if salsas else "al natural"
    return _linea(1, fruta + " para comer ya", detalle, unitario)


SECCIONES = [pedir_pizza, pedir_tarta, pedir_helado, pedir_helado, pedir_fruta]


# ---------------------------------------------------------------------------
# EL PEDIDO COMPLETO
# ---------------------------------------------------------------------------

def generar_pedido(numero=1, hora=""):
    """Inventa un pedido al azar con entre 1 y 4 cosas de la carta."""
    lineas = []
    hay_tarta = False
    for _ in range(random.randint(1, 4)):
        generador = _elige(SECCIONES)
        if generador is pedir_tarta:
            if hay_tarta:  # una tarta por mesa es más que suficiente
                generador = pedir_helado
            hay_tarta = True
        nueva = generador()
        # Si el azar repite exactamente el mismo plato, sumamos cantidades.
        repetida = None
        for linea in lineas:
            if linea["nombre"] == nueva["nombre"] and linea["detalle"] == nueva["detalle"]:
                repetida = linea
        if repetida:
            repetida["cantidad"] += nueva["cantidad"]
            repetida["importe"] = repetida["cantidad"] * repetida["unitario"]
        else:
            lineas.append(nueva)

    return {
        "numero": numero,
        "cliente": _elige(CLIENTES),
        "mesa": random.randint(1, 12),
        "hora": hora,
        "lineas": lineas,
        "total": sum(linea["importe"] for linea in lineas),
    }


def como_texto(p):
    """Devuelve el pedido como una comanda de texto (para la terminal)."""
    ancho = 46
    filas = [
        "=" * ancho,
        "5 ESTRELLAS, A COMER".center(ancho),
        "=" * ancho,
        "Pedido nº {}   Mesa {}   {}".format(p["numero"], p["mesa"], p["hora"]).strip(),
        "Cliente: " + p["cliente"],
        "-" * ancho,
    ]
    for l in p["lineas"]:
        izquierda = "{} x {}".format(l["cantidad"], l["nombre"])
        derecha = euros(l["importe"])
        filas.append(izquierda + derecha.rjust(ancho - len(izquierda)))
        if l["detalle"]:
            filas.append("    " + l["detalle"])
    filas.append("-" * ancho)
    filas.append("TOTAL" + euros(p["total"]).rjust(ancho - 5))
    filas.append("=" * ancho)
    return "\n".join(filas)


if __name__ == "__main__":
    import sys
    import time

    cuantos = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    for i in range(cuantos):
        hora = time.strftime("%H:%M") if hasattr(time, "strftime") else ""
        print(como_texto(generar_pedido(numero=i + 1, hora=hora)))
        print()
