def entrada():
    codigo = input("Escanee el código: ")
    talla = input("Talla: ")
    cantidad = int(input("Cantidad: "))

    cursor.execute(
        "SELECT id_producto FROM producto WHERE codigo_barra = %s",
        (codigo,)
    )
    producto = cursor.fetchone()

    if not producto:
        print("Producto no existe")
        return

    id_producto = producto[0]

    cursor.execute(
        "SELECT stock FROM inventario WHERE id_producto=%s AND talla=%s",
        (id_producto, talla)
    )
    fila = cursor.fetchone()

    if fila:
        cursor.execute(
            "UPDATE inventario SET stock = stock + %s WHERE id_producto=%s AND talla=%s",
            (cantidad, id_producto, talla)
        )
    else:
        cursor.execute(
            "INSERT INTO inventario (id_producto, talla, stock) VALUES (%s,%s,%s)",
            (id_producto, talla, cantidad)
        )

    cursor.execute(
        "INSERT INTO movimiento (id_producto, talla, tipo_movimiento, cantidad) VALUES (%s,%s,'ENTRADA',%s)",
        (id_producto, talla, cantidad)
    )

    conexion.commit()
    print("Entrada registrada")
