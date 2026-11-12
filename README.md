# 5 estrellas, a comer

Web del restaurante (ficticio) **5 estrellas, a comer**: la carta con precios y un
botón de **pedido sorpresa** que genera una comanda al azar usando **Python**.

## Cómo funciona

| Archivo      | Qué hace |
|--------------|----------|
| `index.html` | La página: diseño, secciones y estilos. |
| `pedido.py`  | La "cocina": la carta, los precios (en céntimos) y el generador de pedidos al azar. |
| `main.py`    | El puente con la web: pinta la carta y reacciona al botón. |

Python se ejecuta **dentro del navegador** gracias a [PyScript](https://pyscript.net)
(con MicroPython), así que no hace falta ningún servidor especial: la carta y los
precios salen directamente de `pedido.py`.

## Verla en tu ordenador

PyScript necesita que la página se sirva por HTTP (abrir el archivo con doble clic no basta):

```bash
python3 -m http.server 8000
```

y abre <http://localhost:8000>. También funciona tal cual en GitHub Pages.

## Pedidos desde la terminal

El mismo `pedido.py` sirve con Python normal:

```bash
python3 pedido.py      # un pedido
python3 pedido.py 5    # cinco pedidos
```

## Cambiar la carta o los precios

Edita las listas del principio de `pedido.py` (`PIZZA`, `TARTA`, `HELADOS`, `FRUTAS`,
`SALSAS`). Los precios van en céntimos: `350` son 3,50 €. La web se actualiza sola.
