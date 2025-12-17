def venta():
    codigo = input("Escanee el código: ")
    talla = input("Talla: ")
    cantidad = int(input("Cantidad: "))

    cursor.execute("""
        SELECT i.stock, p.id_producto
        FROM inventario i
        JOIN producto p ON i.id_producto = p.id_producto
        WHERE p.codigo_barra=%s AND i.talla=%s
    """, (codigo, talla))

    fila = cursor.fetchone()

    if not fila or fila[0] < cantidad:
        print("Stock insuficiente")
        return

    stock, id_producto = fila

    cursor.execute(
        "UPDATE inventario SET stock = stock - %s WHERE id_producto=%s AND talla=%s",
        (cantidad, id_producto, talla)
    )

    cursor.execute(
        "INSERT INTO movimiento (id_producto, talla, tipo_movimiento, cantidad) VALUES (%s,%s,'VENTA',%s)",
        (id_producto, talla, cantidad)
    )

    conexion.commit()
    print("Venta realizada")
