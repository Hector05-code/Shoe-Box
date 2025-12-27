from fastapi import FastAPI
from api import clientes, detalle_ventas, empleados, movimientos, productos, variantes, ventas
from servicio_escaner import servicio_inventario, servicio_venta

app = FastAPI(debug=True)

app.include_router(clientes.endpoint)
app.include_router(detalle_ventas.endpoint)
app.include_router(empleados.endpoint)
app.include_router(movimientos.endpoint)
app.include_router(productos.endpoint)
app.include_router(variantes.endpoint)
app.include_router(ventas.endpoint)

app.include_router(servicio_inventario.endpoint)
app.include_router(servicio_venta.endpoint)