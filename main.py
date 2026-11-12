"""
Puente entre la cocina (pedido.py) y la página web.

PyScript ejecuta este archivo con MicroPython dentro del navegador:
pinta la carta con sus precios y prepara el botón que simula pedidos para el cocinero.
"""

import random

from pyscript import document, when, window
from pyscript.ffi import to_js

import pedido
from pedido import euros

# MicroPython en el navegador arranca siempre con la misma semilla:
# la mezclamos con el reloj para que cada visita dé pedidos distintos.
random.seed(int(window.Date.now()) % 1000000007)

contador = {"numero": random.randint(101, 480)}


def fila(nombre, precio, nota=""):
    nota_html = '<span class="plato__nota">{}</span>'.format(nota) if nota else ""
    return (
        '<li class="plato">'
        '<span class="plato__nombre">{}{}</span>'
        '<span class="plato__puntos" aria-hidden="true"></span>'
        '<span class="plato__precio">{}</span>'
        "</li>"
    ).format(nombre, nota_html, precio)


def chips(opciones, prefijo="+ "):
    return '<ul class="chips">{}</ul>'.format(
        "".join(
            '<li class="chip">{} <span>{}{}</span></li>'.format(nombre, prefijo, euros(precio))
            for nombre, precio in opciones
        )
    )


def pintar(id_, html):
    document.getElementById(id_).innerHTML = html


def pintar_carta():
    p = pedido.PIZZA
    pintar(
        "carta-pizza",
        '<ul class="platos">{}</ul><p class="etiqueta">Ingredientes extra</p>{}'.format(
            fila(p["nombre"], euros(p["base"]), p["descripcion"]), chips(p["ingredientes"])
        ),
    )

    t = pedido.TARTA
    tamanos = [
        ("{} {}".format(anos, "año" if anos == 1 else "años"), precio)
        for anos, precio in t["tamanos"]
    ]
    pintar(
        "carta-tarta",
        '<p class="descripcion">{}</p><p class="etiqueta">Elige los años que cumple</p>{}'.format(
            t["descripcion"], chips(tamanos, prefijo="")
        ),
    )

    filas = []
    for h in pedido.HELADOS:
        filas.append(fila(h["nombre"], euros(h["precio"])))
    html = '<ul class="platos">{}</ul>'.format("".join(filas))
    con_toppings = [h for h in pedido.HELADOS if "toppings" in h][0]
    html += '<p class="etiqueta">Toppings para el {}</p>{}'.format(
        con_toppings["nombre"].lower(), chips(con_toppings["toppings"])
    )
    pintar("carta-helados", html)

    filas = [fila(nombre + "*", euros(precio) + " / kg") for nombre, precio in pedido.FRUTAS]
    html = '<ul class="platos platos--dos">{}</ul>'.format("".join(filas))
    html += '<p class="etiqueta">*Salsas para añadir</p>{}'.format(chips(pedido.SALSAS))
    pintar("carta-frutas", html)


def hora_actual():
    ahora = window.Date.new()
    return "{:02d}:{:02d}".format(int(ahora.getHours()), int(ahora.getMinutes()))


def pintar_comanda(p):
    lineas = []
    for l in p["lineas"]:
        detalle = '<span class="linea__detalle">{}</span>'.format(l["detalle"]) if l["detalle"] else ""
        unitario = (
            '<span class="linea__detalle">{} × {}</span>'.format(l["cantidad"], euros(l["unitario"]))
            if l["cantidad"] > 1
            else ""
        )
        lineas.append(
            '<li class="linea">'
            '<span class="linea__cantidad">{}×</span>'
            '<span class="linea__texto"><strong>{}</strong>{}{}</span>'
            '<span class="linea__importe">{}</span>'
            "</li>".format(l["cantidad"], l["nombre"], detalle, unitario, euros(l["importe"]))
        )

    unidades = sum(l["cantidad"] for l in p["lineas"])
    html = (
        '<header class="comanda__cabecera">'
        '<p class="comanda__marca">5 estrellas, a comer</p>'
        '<dl class="comanda__datos">'
        "<div><dt>Pedido</dt><dd>nº {numero}</dd></div>"
        "<div><dt>Mesa</dt><dd>{mesa}</dd></div>"
        "<div><dt>Hora</dt><dd>{hora}</dd></div>"
        "</dl>"
        '<p class="comanda__cliente">Para: <strong>{cliente}</strong></p>'
        "</header>"
        '<ol class="comanda__lineas">{lineas}</ol>'
        '<footer class="comanda__pie">'
        '<span>Total · {unidades} {palabra}</span>'
        '<span class="comanda__total">{total}</span>'
        "</footer>"
        '<p class="comanda__gracias">★ ★ ★ ★ ★ &nbsp;¡Que aproveche!</p>'
    ).format(
        numero=p["numero"],
        mesa=p["mesa"],
        hora=p["hora"],
        cliente=p["cliente"],
        lineas="".join(lineas),
        unidades=unidades,
        palabra="cosa" if unidades == 1 else "cosas",
        total=euros(p["total"]),
    )

    comanda = document.getElementById("comanda")
    comanda.classList.remove("comanda--vacia")
    comanda.classList.remove("comanda--entra")
    comanda.innerHTML = html
    # Forzamos un reflow para que la animación de entrada se repita.
    _ = comanda.offsetWidth
    comanda.classList.add("comanda--entra")
    # En el móvil la comanda queda debajo del botón: la acercamos a la vista.
    if int(window.innerWidth) <= 600:
        comanda.scrollIntoView(to_js({"behavior": "smooth", "block": "center"}))


@when("click", "#boton-pedido")
def nuevo_pedido(event):
    p = pedido.generar_pedido(numero=contador["numero"], hora=hora_actual())
    contador["numero"] += 1
    pintar_comanda(p)


pintar_carta()

boton = document.getElementById("boton-pedido")
boton.disabled = False
boton.querySelector(".boton__texto").textContent = "Simular un pedido"
document.getElementById("estado-python").textContent = "Python listo: esperando pedidos"
document.body.classList.add("python-listo")

# Avisamos a la página para que guarde todo y funcione sin conexión.
window.cocinaLista()
