while True:
    print("\n1. Entrada")
    print("2. Salida")
    print("3. Venta")
    print("4. Salir")

    op = input("Opción: ")

    if op == "1":
        entrada()
    elif op == "2":
        salida()
    elif op == "3":
        venta()
    elif op == "4":
        break
