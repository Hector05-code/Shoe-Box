#!/usr/bin/env python3
"""
Sistema de Gestión de Inventario
Aplicación de consola para administrar productos con base de datos SQLite
"""

# Importaciones del sistema
import sqlite3  # Base de datos SQLite integrada en Python
import os  # Operaciones del sistema operativo (no utilizado actualmente)
from colorama import init, Fore, Style  # Biblioteca para colores en terminal

# Inicializar colorama para colores en terminal
# autoreset=True restablece colores automáticamente después de cada print
init(autoreset=True)

# Configuración de la base de datos
# Nombre del archivo de base de datos SQLite
DB_NAME = "inventario.db"


def crear_base_datos():
    """Crear la base de datos y tabla productos si no existen"""
    # Establecer conexión con la base de datos SQLite
    # Si el archivo no existe, SQLite lo creará automáticamente
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Crear tabla productos con estructura definida
    # IF NOT EXISTS evita errores si la tabla ya existe
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ID único autoincrementable
            nombre TEXT NOT NULL,                   -- Nombre obligatorio del producto
            descripcion TEXT,                       -- Descripción opcional
            cantidad INTEGER NOT NULL,              -- Stock actual (obligatorio)
            precio REAL NOT NULL,                   -- Precio del producto (obligatorio)
            categoria TEXT                          -- Categoría opcional para clasificación
        )
    """
    )

    # Confirmar cambios en la base de datos
    conn.commit()
    # Cerrar conexión para liberar recursos
    conn.close()


def agregar_producto():
    """Registrar un nuevo producto en el inventario"""
    print(f"\n{Fore.CYAN}=== AGREGAR NUEVO PRODUCTO ==={Style.RESET_ALL}")

    try:
        # Validación de entrada: el nombre es obligatorio
        nombre = input("Nombre del producto: ").strip()
        if not nombre:
            print(f"{Fore.RED}Error: El nombre es obligatorio{Style.RESET_ALL}")
            return

        # Recolección de datos del producto
        # strip() elimina espacios en blanco al inicio y final
        descripcion = input("Descripción (opcional): ").strip()
        # Conversión de tipos con validación automática (ValueError si falla)
        cantidad = int(input("Cantidad en stock: "))
        precio = float(input("Precio: $"))
        categoria = input("Categoría (opcional): ").strip()

        # Establecer nueva conexión para esta operación
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Inserción parametrizada para prevenir inyección SQL
        # Los ? son marcadores de posición que SQLite reemplaza de forma segura
        cursor.execute(
            """
            INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria)
            VALUES (?, ?, ?, ?, ?)
        """,
            (nombre, descripcion, cantidad, precio, categoria),
        )

        # Confirmar la transacción en la base de datos
        conn.commit()
        conn.close()

        print(f"{Fore.GREEN}✓ Producto agregado exitosamente{Style.RESET_ALL}")

    except ValueError:
        # Manejo específico de errores de conversión de tipos
        print(
            f"{Fore.RED}Error: Cantidad y precio deben ser números válidos{Style.RESET_ALL}"
        )
    except Exception as e:
        # Manejo general de otros errores inesperados
        print(f"{Fore.RED}Error al agregar producto: {e}{Style.RESET_ALL}")


def mostrar_productos():
    """Visualizar todos los productos del inventario"""
    print(f"\n{Fore.CYAN}=== INVENTARIO DE PRODUCTOS ==={Style.RESET_ALL}")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Consulta SELECT para obtener todos los productos
    # ORDER BY id organiza los resultados por ID de forma ascendente
    cursor.execute("SELECT * FROM productos ORDER BY id")
    productos = cursor.fetchall()  # fetchall() obtiene todos los registros
    conn.close()

    # Verificar si hay productos en la base de datos
    if not productos:
        print(f"{Fore.YELLOW}No hay productos registrados{Style.RESET_ALL}")
        return

    # Crear encabezado de tabla con formato columnar
    # Los números después de < definen el ancho de cada columna
    print(
        f"\n{Fore.WHITE}{'ID':<4} {'Nombre':<20} {'Descripción':<25} {'Cantidad':<10} {'Precio':<10} {'Categoría':<15}{Style.RESET_ALL}"
    )
    print("-" * 90)  # Línea separadora

    # Iterar sobre cada producto y mostrar en formato de tabla
    for producto in productos:
        # Desempaquetar tupla de datos del producto
        id_prod, nombre, desc, cantidad, precio, categoria = producto
        # Manejar valores nulos mostrando "N/A" en lugar de None
        desc = desc or "N/A"
        categoria = categoria or "N/A"
        # Formatear precio con 2 decimales usando :.2f
        print(
            f"{id_prod:<4} {nombre:<20} {desc:<25} {cantidad:<10} ${precio:<9.2f} {categoria:<15}"
        )


def actualizar_producto():
    """Actualizar información de un producto existente"""
    print(f"\n{Fore.CYAN}=== ACTUALIZAR PRODUCTO ==={Style.RESET_ALL}")

    try:
        id_producto = int(input("ID del producto a actualizar: "))

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Verificar que el producto existe antes de intentar actualizarlo
        # fetchone() devuelve None si no encuentra el registro
        cursor.execute("SELECT * FROM productos WHERE id = ?", (id_producto,))
        producto = cursor.fetchone()

        if not producto:
            print(
                f"{Fore.RED}Error: No existe un producto con ID {id_producto}{Style.RESET_ALL}"
            )
            conn.close()
            return

        # Mostrar información actual del producto
        print(f"\nProducto actual: {producto[1]}")
        print("Deja en blanco para mantener el valor actual")

        # Lógica de actualización con valores por defecto
        # Si el usuario no ingresa nada, se mantiene el valor actual
        nombre = input(f"Nuevo nombre [{producto[1]}]: ").strip() or producto[1]

        # Manejo especial para descripción (puede ser None en la BD)
        descripcion = input(f"Nueva descripción [{producto[2] or 'N/A'}]: ").strip()
        if not descripcion and producto[2]:
            descripcion = producto[2]

        # Para campos numéricos: validar entrada o mantener valor actual
        cantidad_input = input(f"Nueva cantidad [{producto[3]}]: ").strip()
        cantidad = int(cantidad_input) if cantidad_input else producto[3]

        precio_input = input(f"Nuevo precio [{producto[4]}]: ").strip()
        precio = float(precio_input) if precio_input else producto[4]

        # Manejo de categoría similar a descripción
        categoria = input(f"Nueva categoría [{producto[5] or 'N/A'}]: ").strip()
        if not categoria and producto[5]:
            categoria = producto[5]

        # Actualización con consulta parametrizada
        # UPDATE modifica solo el registro que coincide con el ID
        cursor.execute(
            """
            UPDATE productos 
            SET nombre = ?, descripcion = ?, cantidad = ?, precio = ?, categoria = ?
            WHERE id = ?
        """,
            (nombre, descripcion, cantidad, precio, categoria, id_producto),
        )

        conn.commit()
        conn.close()

        print(f"{Fore.GREEN}✓ Producto actualizado exitosamente{Style.RESET_ALL}")

    except ValueError:
        # Error al convertir ID, cantidad o precio a números
        print(
            f"{Fore.RED}Error: ID, cantidad y precio deben ser números válidos{Style.RESET_ALL}"
        )
    except Exception as e:
        print(f"{Fore.RED}Error al actualizar producto: {e}{Style.RESET_ALL}")


def eliminar_producto():
    """Eliminar un producto del inventario"""
    print(f"\n{Fore.CYAN}=== ELIMINAR PRODUCTO ==={Style.RESET_ALL}")

    try:
        id_producto = int(input("ID del producto a eliminar: "))

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Verificar existencia del producto y obtener su nombre para confirmación
        # Solo necesitamos el nombre para mostrar al usuario
        cursor.execute("SELECT nombre FROM productos WHERE id = ?", (id_producto,))
        producto = cursor.fetchone()

        if not producto:
            print(
                f"{Fore.RED}Error: No existe un producto con ID {id_producto}{Style.RESET_ALL}"
            )
            conn.close()
            return

        # Solicitar confirmación explícita antes de eliminar
        # Esto previene eliminaciones accidentales
        confirmacion = (
            input(f"¿Confirmar eliminación de '{producto[0]}'? (s/N): ").strip().lower()
        )

        if confirmacion == "s":
            # DELETE elimina permanentemente el registro
            # WHERE asegura que solo se elimine el producto específico
            cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
            conn.commit()
            print(f"{Fore.GREEN}✓ Producto eliminado exitosamente{Style.RESET_ALL}")
        else:
            # Cualquier respuesta que no sea 's' cancela la operación
            print(f"{Fore.YELLOW}Operación cancelada{Style.RESET_ALL}")

        conn.close()

    except ValueError:
        print(f"{Fore.RED}Error: El ID debe ser un número válido{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error al eliminar producto: {e}{Style.RESET_ALL}")


def buscar_producto():
    """Buscar productos por ID, nombre o categoría"""
    print(f"\n{Fore.CYAN}=== BUSCAR PRODUCTO ==={Style.RESET_ALL}")
    print("1. Buscar por ID")
    print("2. Buscar por nombre")
    print("3. Buscar por categoría")

    try:
        opcion = input("\nSelecciona una opción (1-3): ").strip()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Algoritmo de búsqueda: diferentes estrategias según el tipo
        if opcion == "1":
            # Búsqueda exacta por ID (clave primaria)
            id_producto = int(input("ID del producto: "))
            cursor.execute("SELECT * FROM productos WHERE id = ?", (id_producto,))
            productos = cursor.fetchall()

        elif opcion == "2":
            # Búsqueda parcial por nombre usando LIKE
            # %texto% permite encontrar coincidencias parciales
            nombre = input("Nombre del producto: ").strip()
            cursor.execute(
                "SELECT * FROM productos WHERE nombre LIKE ?", (f"%{nombre}%",)
            )
            productos = cursor.fetchall()

        elif opcion == "3":
            # Búsqueda parcial por categoría
            categoria = input("Categoría: ").strip()
            cursor.execute(
                "SELECT * FROM productos WHERE categoria LIKE ?", (f"%{categoria}%",)
            )
            productos = cursor.fetchall()

        else:
            print(f"{Fore.RED}Opción no válida{Style.RESET_ALL}")
            conn.close()
            return

        conn.close()

        # Mostrar resultados de búsqueda
        if productos:
            print(f"\n{Fore.GREEN}Productos encontrados:{Style.RESET_ALL}")
            # Reutilizar formato de tabla de mostrar_productos()
            print(
                f"\n{Fore.WHITE}{'ID':<4} {'Nombre':<20} {'Descripción':<25} {'Cantidad':<10} {'Precio':<10} {'Categoría':<15}{Style.RESET_ALL}"
            )
            print("-" * 90)

            for producto in productos:
                id_prod, nombre, desc, cantidad, precio, categoria = producto
                desc = desc or "N/A"
                categoria = categoria or "N/A"
                print(
                    f"{id_prod:<4} {nombre:<20} {desc:<25} {cantidad:<10} ${precio:<9.2f} {categoria:<15}"
                )
        else:
            print(f"{Fore.YELLOW}No se encontraron productos{Style.RESET_ALL}")

    except ValueError:
        # Error específico para búsqueda por ID
        print(f"{Fore.RED}Error: El ID debe ser un número válido{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error en la búsqueda: {e}{Style.RESET_ALL}")


def reporte_stock_bajo():
    """Generar reporte de productos con stock bajo"""
    print(f"\n{Fore.CYAN}=== REPORTE DE STOCK BAJO ==={Style.RESET_ALL}")

    try:
        limite = int(input("Límite de stock: "))

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Consulta filtrada: productos con cantidad <= límite especificado
        # ORDER BY cantidad ordena de menor a mayor stock (más críticos primero)
        cursor.execute(
            "SELECT * FROM productos WHERE cantidad <= ? ORDER BY cantidad", (limite,)
        )
        productos = cursor.fetchall()
        conn.close()

        if productos:
            print(
                f"\n{Fore.RED}Productos con stock igual o menor a {limite}:{Style.RESET_ALL}"
            )
            # Formato de tabla reducido (sin descripción para mayor claridad)
            print(
                f"\n{Fore.WHITE}{'ID':<4} {'Nombre':<20} {'Cantidad':<10} {'Precio':<10} {'Categoría':<15}{Style.RESET_ALL}"
            )
            print("-" * 65)

            for producto in productos:
                id_prod, nombre, desc, cantidad, precio, categoria = producto
                categoria = categoria or "N/A"
                # Código de colores para alertas visuales:
                # Rojo para stock 0 (crítico), amarillo para stock bajo
                color = Fore.RED if cantidad == 0 else Fore.YELLOW
                print(
                    f"{color}{id_prod:<4} {nombre:<20} {cantidad:<10} ${precio:<9.2f} {categoria:<15}{Style.RESET_ALL}"
                )
        else:
            print(f"{Fore.GREEN}No hay productos con stock bajo{Style.RESET_ALL}")

    except ValueError:
        print(f"{Fore.RED}Error: El límite debe ser un número válido{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error al generar reporte: {e}{Style.RESET_ALL}")


def mostrar_menu():
    """Mostrar el menú principal de la aplicación"""
    print(f"\n{Fore.BLUE}{'='*50}")
    print(f"{Fore.BLUE}    SISTEMA DE GESTIÓN DE INVENTARIO")
    print(f"{Fore.BLUE}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}1.{Style.RESET_ALL} Agregar producto")
    print(f"{Fore.WHITE}2.{Style.RESET_ALL} Ver todos los productos")
    print(f"{Fore.WHITE}3.{Style.RESET_ALL} Actualizar producto")
    print(f"{Fore.WHITE}4.{Style.RESET_ALL} Eliminar producto")
    print(f"{Fore.WHITE}5.{Style.RESET_ALL} Buscar producto")
    print(f"{Fore.WHITE}6.{Style.RESET_ALL} Reporte de stock bajo")
    print(f"{Fore.WHITE}7.{Style.RESET_ALL} Salir")
    print(f"{Fore.BLUE}{'-'*50}{Style.RESET_ALL}")


def main():
    """Función principal de la aplicación"""
    # Inicializar base de datos al comenzar la aplicación
    crear_base_datos()

    print(
        f"{Fore.GREEN}¡Bienvenido al Sistema de Gestión de Inventario!{Style.RESET_ALL}"
    )

    # Bucle principal de la aplicación
    # Se ejecuta hasta que el usuario seleccione salir (opción 7)
    while True:
        mostrar_menu()

        try:
            opcion = input(
                f"\n{Fore.CYAN}Selecciona una opción (1-7): {Style.RESET_ALL}"
            ).strip()

            # Estructura de control: mapeo de opciones a funciones
            # Cada opción ejecuta una función específica del sistema
            if opcion == "1":
                agregar_producto()
            elif opcion == "2":
                mostrar_productos()
            elif opcion == "3":
                actualizar_producto()
            elif opcion == "4":
                eliminar_producto()
            elif opcion == "5":
                buscar_producto()
            elif opcion == "6":
                reporte_stock_bajo()
            elif opcion == "7":
                # Opción de salida: termina el bucle principal
                print(
                    f"{Fore.GREEN}¡Gracias por usar el sistema de inventario!{Style.RESET_ALL}"
                )
                break
            else:
                # Validación de entrada: manejar opciones inválidas
                print(
                    f"{Fore.RED}Opción no válida. Por favor, selecciona una opción del 1 al 7.{Style.RESET_ALL}"
                )

        except KeyboardInterrupt:
            # Manejo elegante de Ctrl+C: permite al usuario salir limpiamente
            print(f"\n{Fore.YELLOW}Operación cancelada por el usuario{Style.RESET_ALL}")
            break
        except Exception as e:
            # Captura de errores inesperados para evitar que la aplicación se cierre
            print(f"{Fore.RED}Error inesperado: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    # Punto de entrada del programa
    # Solo se ejecuta cuando el archivo se ejecuta directamente
    # (no cuando se importa como módulo)
    main()
