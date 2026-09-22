#!/usr/bin/env python3
"""
AgroControl CBA
Sistema monolítico para control de producción, inventario y ventas.
Centro de Biotecnología Agropecuaria – CBA | SENA

Incluye:
- Persistencia JSON
- Roles OPERADOR / INSTRUCTOR
- Consulta de ventas por fechas
- Utilidad estimada
- Devolución de ventas
- Exportación CSV
- Backup automático
- Reporte de rotación de productos
"""

import json
import csv
import shutil
from datetime import datetime
from pathlib import Path

# -------------------- CONFIGURACIÓN --------------------
BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
BACKUP_DIR = DATA_DIR / "backups"

RUTAS = {
    "productos": DATA_DIR / "productos.json",
    "lotes": DATA_DIR / "lotes.json",
    "movimientos": DATA_DIR / "movimientos.json",
    "ventas": DATA_DIR / "ventas.json",
    "usuarios": DATA_DIR / "usuarios.json",
}

USUARIOS_INICIALES = [
    {"usuario": "campo", "clave": "campo01", "rol": "OPERADOR", "nombre": "Auxiliar de Campo"},
    {"usuario": "admin", "clave": "cba2026", "rol": "INSTRUCTOR", "nombre": "Instructor Técnico"},
]

# -------------------- ESTADO EN MEMORIA --------------------
productos = []
lotes = []
movimientos = []
ventas = []
usuarios = []
sesion = None  # dict con usuario, rol, nombre


# -------------------- UTILIDADES --------------------
def crear_directorios():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def leer_json(ruta: Path) -> list:
    if not ruta.exists():
        return []
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            contenido = json.load(archivo)
            return contenido if isinstance(contenido, list) else []
    except (json.JSONDecodeError, OSError):
        print(f"  [!] No se pudo leer {ruta.name}. Se usa colección vacía.")
        return []


def respaldar_json():
    """Copia de seguridad de los JSON de datos antes de guardar."""
    try:
        crear_directorios()
        marca = datetime.now().strftime("%Y%m%d_%H%M%S")
        for clave, ruta in RUTAS.items():
            if clave == "usuarios":
                continue
            if ruta.exists():
                destino = BACKUP_DIR / f"{clave}_{marca}.json"
                shutil.copy2(ruta, destino)
        for clave in ("productos", "lotes", "movimientos", "ventas"):
            lista = sorted(BACKUP_DIR.glob(f"{clave}_*.json"), reverse=True)
            for antiguo in lista[8:]:
                antiguo.unlink(missing_ok=True)
    except OSError:
        pass


def escribir_json(ruta: Path, datos: list) -> bool:
    try:
        crear_directorios()
        respaldar_json()
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)
        return True
    except OSError as err:
        print(f"  [!] Error al guardar {ruta.name}: {err}")
        return False


def fecha_hora() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def pedir_texto(msg: str, requerido: bool = True) -> str:
    while True:
        valor = input(msg).strip()
        if valor or not requerido:
            return valor
        print("  [!] Campo obligatorio.")


def pedir_entero(msg: str, minimo=None, maximo=None) -> int:
    while True:
        try:
            n = int(input(msg).strip())
            if minimo is not None and n < minimo:
                print(f"  [!] Debe ser >= {minimo}.")
                continue
            if maximo is not None and n > maximo:
                print(f"  [!] Debe ser <= {maximo}.")
                continue
            return n
        except ValueError:
            print("  [!] Ingrese un entero válido.")


def pedir_decimal(msg: str, minimo=None) -> float:
    while True:
        try:
            n = float(input(msg).strip().replace(",", "."))
            if minimo is not None and n < minimo:
                print(f"  [!] Debe ser >= {minimo}.")
                continue
            return n
        except ValueError:
            print("  [!] Ingrese un número válido.")


def siguiente_id(prefijo: str, coleccion: list, campo: str = "id") -> str:
    if not coleccion:
        return f"{prefijo}0001" if prefijo in ("M", "V") else f"{prefijo}001"
    nums = []
    for item in coleccion:
        val = item.get(campo, "")
        if isinstance(val, str) and val.startswith(prefijo):
            try:
                nums.append(int(val[len(prefijo):]))
            except ValueError:
                pass
    siguiente = max(nums) + 1 if nums else 1
    if prefijo in ("M", "V"):
        return f"{prefijo}{siguiente:04d}"
    return f"{prefijo}{siguiente:03d}"


def es_instructor() -> bool:
    return sesion is not None and sesion.get("rol") == "INSTRUCTOR"


def solo_instructor(accion: str = "esta operación") -> bool:
    if es_instructor():
        return True
    print(f"  [!] Solo el rol INSTRUCTOR puede realizar {accion}.")
    return False


# -------------------- CARGA Y GUARDADO --------------------
def cargar_datos():
    global productos, lotes, movimientos, ventas, usuarios
    crear_directorios()
    productos = leer_json(RUTAS["productos"])
    lotes = leer_json(RUTAS["lotes"])
    movimientos = leer_json(RUTAS["movimientos"])
    ventas = leer_json(RUTAS["ventas"])
    usuarios = leer_json(RUTAS["usuarios"])
    if not usuarios:
        usuarios = [u.copy() for u in USUARIOS_INICIALES]
        escribir_json(RUTAS["usuarios"], usuarios)
    print("  Datos cargados.")


def guardar_datos():
    ok = True
    ok &= escribir_json(RUTAS["productos"], productos)
    ok &= escribir_json(RUTAS["lotes"], lotes)
    ok &= escribir_json(RUTAS["movimientos"], movimientos)
    ok &= escribir_json(RUTAS["ventas"], ventas)
    if ok:
        print("  Información guardada correctamente.")
    else:
        print("  [!] Algunos archivos no se pudieron guardar.")


# -------------------- STOCK --------------------
def obtener_stock(codigo: str) -> int:
    codigo = codigo.upper()
    total = 0
    for mov in movimientos:
        if mov.get("producto_codigo") == codigo:
            if mov.get("tipo") == "ENTRADA":
                total += mov.get("cantidad", 0)
            elif mov.get("tipo") == "SALIDA":
                total -= mov.get("cantidad", 0)
    return total


def hay_stock(codigo: str, cantidad: int) -> bool:
    return obtener_stock(codigo) >= cantidad


# -------------------- AUTENTICACIÓN --------------------
def iniciar_sesion() -> bool:
    global sesion
    print("\n" + "=" * 48)
    print("  ACCESO AL SISTEMA - AGROCONTROL CBA")
    print("=" * 48)
    print("  Credenciales de prueba:")
    print("    campo  / campo01  → OPERADOR")
    print("    admin  / cba2026  → INSTRUCTOR")
    print("-" * 48)

    intentos = 3
    while intentos > 0:
        user = pedir_texto("Usuario: ").lower()
        clave = pedir_texto("Clave: ")
        for u in usuarios:
            if u.get("usuario") == user and u.get("clave") == clave:
                sesion = {
                    "usuario": u["usuario"],
                    "rol": u["rol"],
                    "nombre": u.get("nombre", u["usuario"]),
                }
                print(f"\n  Bienvenido/a {sesion['nombre']} [{sesion['rol']}]")
                return True
        intentos -= 1
        print(f"  [!] Credenciales incorrectas. Quedan {intentos} intento(s).")
    print("  [!] Acceso denegado.")
    return False


# -------------------- PRODUCTOS --------------------
def localizar_producto(codigo: str):
    codigo = codigo.upper()
    for p in productos:
        if p.get("codigo") == codigo:
            return p
    return None


def mostrar_productos(solo_activos: bool = True):
    lista = [p for p in productos if p.get("activo", True)] if solo_activos else productos
    if not lista:
        print("  No hay productos para mostrar.")
        return
    print(f"\n  {'Código':<8} {'Nombre':<22} {'Categoría':<12} {'Unidad':<8} "
          f"{'Precio':>9} {'Costo':>9} {'Stock':>7} {'Mín':>4} {'Est'}")
    print("  " + "-" * 98)
    for p in lista:
        stock = obtener_stock(p["codigo"])
        estado = "A" if p.get("activo", True) else "I"
        costo = p.get("costo_unitario", 0)
        print(f"  {p['codigo']:<8} {p['nombre'][:21]:<22} {p.get('categoria', '')[:11]:<12} "
              f"{p.get('unidad', ''):<8} {p.get('precio', 0):>9,.0f} {costo:>9,.0f} "
              f"{stock:>7} {p.get('stock_minimo', 0):>4} {estado}")


def nuevo_producto():
    print("\n--- NUEVO PRODUCTO ---")
    codigo = pedir_texto("Código (ej. P001): ").upper()
    if localizar_producto(codigo):
        print(f"  [!] El código {codigo} ya está registrado.")
        return
    nombre = pedir_texto("Nombre: ")
    categoria = pedir_texto("Categoría: ")
    unidad = pedir_texto("Unidad de medida: ")
    precio = pedir_decimal("Precio de venta: ", minimo=0.01)
    costo = pedir_decimal("Costo unitario: ", minimo=0.0)
    minimo = pedir_entero("Stock mínimo: ", minimo=0)

    productos.append({
        "codigo": codigo,
        "nombre": nombre,
        "categoria": categoria,
        "unidad": unidad,
        "precio": precio,
        "costo_unitario": costo,
        "stock_minimo": minimo,
        "activo": True,
    })
    guardar_datos()
    print(f"  Producto {codigo} creado.")


def buscar_producto_menu():
    print("\n--- BUSCAR PRODUCTO ---")
    termino = pedir_texto("Código o parte del nombre: ").lower()
    hallados = [
        p for p in productos
        if termino in p.get("codigo", "").lower() or termino in p.get("nombre", "").lower()
    ]
    if not hallados:
        print("  Sin coincidencias.")
        return
    print(f"\n  {'Código':<8} {'Nombre':<25} {'Precio':>10} {'Stock':>8} {'Estado'}")
    print("  " + "-" * 62)
    for p in hallados:
        stock = obtener_stock(p["codigo"])
        estado = "Activo" if p.get("activo", True) else "Inactivo"
        print(f"  {p['codigo']:<8} {p['nombre'][:24]:<25} {p.get('precio', 0):>10,.0f} "
              f"{stock:>8} {estado}")


def editar_producto():
    print("\n--- EDITAR PRODUCTO ---")
    codigo = pedir_texto("Código: ").upper()
    p = localizar_producto(codigo)
    if not p:
        print(f"  [!] Producto {codigo} no encontrado.")
        return
    print(f"  Actual → {p['nombre']} | Precio: {p['precio']} | "
          f"Costo: {p.get('costo_unitario', 0)} | Mín: {p['stock_minimo']}")
    print("  (Deje vacío para conservar el valor)")

    nombre = input("Nuevo nombre: ").strip()
    if nombre:
        p["nombre"] = nombre
    cat = input("Nueva categoría: ").strip()
    if cat:
        p["categoria"] = cat
    uni = input("Nueva unidad: ").strip()
    if uni:
        p["unidad"] = uni
    prec = input("Nuevo precio: ").strip()
    if prec:
        try:
            val = float(prec.replace(",", "."))
            if val > 0:
                p["precio"] = val
            else:
                print("  [!] Precio debe ser > 0. Se conserva el actual.")
        except ValueError:
            print("  [!] Valor no numérico. Se conserva el precio.")
    cost = input("Nuevo costo unitario: ").strip()
    if cost:
        try:
            val = float(cost.replace(",", "."))
            if val >= 0:
                p["costo_unitario"] = val
            else:
                print("  [!] Costo >= 0. Se conserva el actual.")
        except ValueError:
            print("  [!] Valor no numérico. Se conserva el costo.")
    sm = input("Nuevo stock mínimo: ").strip()
    if sm:
        try:
            val = int(sm)
            if val >= 0:
                p["stock_minimo"] = val
            else:
                print("  [!] Stock mínimo >= 0. Se conserva el actual.")
        except ValueError:
            print("  [!] Valor no entero. Se conserva el mínimo.")

    guardar_datos()
    print(f"  Producto {codigo} actualizado.")


def desactivar_producto():
    if not solo_instructor("desactivar productos"):
        return
    print("\n--- DESACTIVAR PRODUCTO ---")
    codigo = pedir_texto("Código: ").upper()
    p = localizar_producto(codigo)
    if not p:
        print(f"  [!] Producto {codigo} no encontrado.")
        return
    if not p.get("activo", True):
        print(f"  El producto {codigo} ya está inactivo.")
        return
    conf = input(f"¿Desactivar '{p['nombre']}'? (s/n): ").strip().lower()
    if conf == "s":
        p["activo"] = False
        guardar_datos()
        print(f"  Producto {codigo} desactivado (historial conservado).")
    else:
        print("  Operación cancelada.")


def submenu_productos():
    while True:
        print("\n----- PRODUCTOS -----")
        print("1. Registrar producto")
        print("2. Listar activos")
        print("3. Listar todos")
        print("4. Buscar")
        print("5. Editar")
        print("6. Desactivar (solo INSTRUCTOR)")
        print("0. Volver")
        op = input("Opción: ").strip()
        if op == "1":
            nuevo_producto()
        elif op == "2":
            mostrar_productos(True)
        elif op == "3":
            mostrar_productos(False)
        elif op == "4":
            buscar_producto_menu()
        elif op == "5":
            editar_producto()
        elif op == "6":
            desactivar_producto()
        elif op == "0":
            break
        else:
            print("  [!] Opción inválida.")


# -------------------- LOTES --------------------
def localizar_lote(id_lote: str):
    id_lote = id_lote.upper()
    for l in lotes:
        if l.get("id_lote") == id_lote:
            return l
    return None


def mostrar_lotes():
    if not lotes:
        print("  No hay lotes registrados.")
        return
    print(f"\n  {'ID':<8} {'Producto':<8} {'Siembra':<14} {'Área m²':>10} "
          f"{'Producido':>10} {'Estado'}")
    print("  " + "-" * 68)
    for l in lotes:
        print(f"  {l['id_lote']:<8} {l.get('producto_codigo', ''):<8} "
              f"{l.get('fecha_siembra', ''):<14} {l.get('area_m2', 0):>10.1f} "
              f"{l.get('cantidad_producida', 0):>10} {l.get('estado', '')}")


def nuevo_lote():
    print("\n--- NUEVO LOTE PRODUCTIVO ---")
    codigo = pedir_texto("Código del producto: ").upper()
    p = localizar_producto(codigo)
    if not p:
        print(f"  [!] No existe el producto {codigo}.")
        return
    if not p.get("activo", True):
        print(f"  [!] El producto {codigo} está inactivo. No se permiten nuevos lotes.")
        return
    id_lote = siguiente_id("L", lotes, "id_lote")
    print(f"  ID asignado: {id_lote}")
    fecha = pedir_texto("Fecha de siembra (YYYY-MM-DD): ")
    area = pedir_decimal("Área (m²): ", minimo=0.01)

    lotes.append({
        "id_lote": id_lote,
        "producto_codigo": codigo,
        "fecha_siembra": fecha,
        "area_m2": area,
        "cantidad_producida": 0,
        "estado": "EN_PRODUCCION",
    })
    guardar_datos()
    print(f"  Lote {id_lote} registrado.")


def cambiar_estado_lote():
    print("\n--- CAMBIAR ESTADO DE LOTE ---")
    id_lote = pedir_texto("ID del lote: ").upper()
    lote = localizar_lote(id_lote)
    if not lote:
        print(f"  [!] Lote {id_lote} no existe.")
        return
    print(f"  Estado actual: {lote.get('estado')}")
    print("  Opciones: EN_PRODUCCION | COSECHADO | CANCELADO")
    nuevo = pedir_texto("Nuevo estado: ").upper()
    if nuevo not in ("EN_PRODUCCION", "COSECHADO", "CANCELADO"):
        print("  [!] Estado no válido.")
        return
    lote["estado"] = nuevo
    guardar_datos()
    print(f"  Lote {id_lote} → {nuevo}.")


def cosechar_lote():
    print("\n--- COSECHAR LOTE ---")
    id_lote = pedir_texto("ID del lote: ").upper()
    lote = localizar_lote(id_lote)
    if not lote:
        print(f"  [!] Lote {id_lote} no existe.")
        return
    if lote.get("estado") == "COSECHADO":
        print(f"  [!] El lote {id_lote} ya fue cosechado. No se permite doble cosecha.")
        return
    if lote.get("estado") == "CANCELADO":
        print(f"  [!] El lote {id_lote} está cancelado.")
        return
    cantidad = pedir_entero("Cantidad producida: ", minimo=1)
    lote["cantidad_producida"] = cantidad
    lote["estado"] = "COSECHADO"

    mov = {
        "id": siguiente_id("M", movimientos),
        "producto_codigo": lote["producto_codigo"],
        "tipo": "ENTRADA",
        "cantidad": cantidad,
        "motivo": f"Cosecha del lote {id_lote}",
        "fecha": fecha_hora(),
    }
    movimientos.append(mov)
    guardar_datos()
    print(f"  Lote {id_lote} cosechado. Entrada {mov['id']} (+{cantidad}).")


def submenu_lotes():
    while True:
        print("\n----- LOTES PRODUCTIVOS -----")
        print("1. Registrar lote")
        print("2. Listar lotes")
        print("3. Cambiar estado")
        print("4. Cosechar lote")
        print("0. Volver")
        op = input("Opción: ").strip()
        if op == "1":
            nuevo_lote()
        elif op == "2":
            mostrar_lotes()
        elif op == "3":
            cambiar_estado_lote()
        elif op == "4":
            cosechar_lote()
        elif op == "0":
            break
        else:
            print("  [!] Opción inválida.")


# -------------------- INVENTARIO --------------------
def registrar_movimiento(tipo: str):
    print(f"\n--- {tipo} DE INVENTARIO ---")
    codigo = pedir_texto("Código de producto: ").upper()
    p = localizar_producto(codigo)
    if not p:
        print(f"  [!] Producto {codigo} no existe.")
        return
    if not p.get("activo", True) and tipo == "ENTRADA":
        print("  [!] Aviso: el producto está inactivo.")
    cantidad = pedir_entero("Cantidad: ", minimo=1)
    if tipo == "SALIDA":
        disponible = obtener_stock(codigo)
        if cantidad > disponible:
            print(f"  [!] Stock insuficiente (disponible: {disponible}).")
            return
    motivo = pedir_texto("Motivo: ")

    mov = {
        "id": siguiente_id("M", movimientos),
        "producto_codigo": codigo,
        "tipo": tipo,
        "cantidad": cantidad,
        "motivo": motivo,
        "fecha": fecha_hora(),
    }
    movimientos.append(mov)
    guardar_datos()
    print(f"  Movimiento {mov['id']} registrado. Stock de {codigo}: {obtener_stock(codigo)}")


def listar_movimientos():
    if not movimientos:
        print("  No hay movimientos.")
        return
    print(f"\n  {'ID':<8} {'Producto':<8} {'Tipo':<8} {'Cant':>6} {'Fecha':<18} {'Motivo'}")
    print("  " + "-" * 78)
    for m in movimientos[-40:]:
        print(f"  {m['id']:<8} {m.get('producto_codigo', ''):<8} {m.get('tipo', ''):<8} "
              f"{m.get('cantidad', 0):>6} {m.get('fecha', ''):<18} {m.get('motivo', '')[:28]}")


def submenu_inventario():
    while True:
        print("\n----- INVENTARIO -----")
        print("1. Entrada manual")
        print("2. Salida manual")
        print("3. Últimos movimientos")
        print("4. Consultar stock")
        print("0. Volver")
        op = input("Opción: ").strip()
        if op == "1":
            registrar_movimiento("ENTRADA")
        elif op == "2":
            registrar_movimiento("SALIDA")
        elif op == "3":
            listar_movimientos()
        elif op == "4":
            codigo = pedir_texto("Código: ").upper()
            p = localizar_producto(codigo)
            if not p:
                print(f"  [!] Producto {codigo} no existe.")
            else:
                print(f"  Stock de {codigo} ({p['nombre']}): {obtener_stock(codigo)} {p.get('unidad', '')}")
        elif op == "0":
            break
        else:
            print("  [!] Opción inválida.")


# -------------------- VENTAS --------------------
def nueva_venta():
    print("\n--- REGISTRAR VENTA ---")
    items = []
    while True:
        codigo = pedir_texto("Código de producto (ENTER para terminar): ", requerido=False).upper()
        if not codigo:
            break
        p = localizar_producto(codigo)
        if not p:
            print(f"  [!] Producto {codigo} no existe.")
            continue
        if not p.get("activo", True):
            print(f"  [!] Producto {codigo} inactivo. No se puede vender.")
            continue
        cantidad = pedir_entero("Cantidad: ", minimo=1)
        if not hay_stock(codigo, cantidad):
            print(f"  [!] Stock insuficiente (disponible: {obtener_stock(codigo)}).")
            continue
        precio = p.get("precio", 0)
        subtotal = cantidad * precio
        items.append({
            "codigo": codigo,
            "cantidad": cantidad,
            "precio_unitario": precio,
            "subtotal": subtotal,
        })
        print(f"  + {cantidad} x {p['nombre']} @ {precio:,.0f} = {subtotal:,.0f}")

    if not items:
        print("  [!] Debe incluir al menos un ítem.")
        return

    resumen = {}
    for it in items:
        resumen[it["codigo"]] = resumen.get(it["codigo"], 0) + it["cantidad"]
    for cod, cant in resumen.items():
        if not hay_stock(cod, cant):
            print(f"  [!] Stock insuficiente para {cod}. Venta cancelada.")
            return

    total = sum(it["subtotal"] for it in items)
    venta = {
        "id": siguiente_id("V", ventas),
        "fecha": fecha_hora(),
        "items": items,
        "total": total,
        "anulada": False,
    }

    for it in items:
        movimientos.append({
            "id": siguiente_id("M", movimientos),
            "producto_codigo": it["codigo"],
            "tipo": "SALIDA",
            "cantidad": it["cantidad"],
            "motivo": f"Venta {venta['id']}",
            "fecha": fecha_hora(),
        })

    ventas.append(venta)
    guardar_datos()
    print(f"\n  Venta {venta['id']} registrada. Total: ${total:,.0f}")
    for it in items:
        print(f"    · {it['codigo']}: {it['cantidad']} x {it['precio_unitario']:,.0f} = {it['subtotal']:,.0f}")


def listar_ventas():
    if not ventas:
        print("  No hay ventas.")
        return
    print(f"\n  {'ID':<8} {'Fecha':<18} {'Ítems':>6} {'Total':>12} {'Estado'}")
    print("  " + "-" * 52)
    for v in ventas:
        n = len(v.get("items", []))
        estado = "ANULADA" if v.get("anulada") else "OK"
        print(f"  {v['id']:<8} {v.get('fecha', ''):<18} {n:>6} {v.get('total', 0):>12,.0f} {estado}")


def detalle_venta():
    id_v = pedir_texto("ID de venta: ").upper()
    for v in ventas:
        if v.get("id") == id_v:
            estado = "ANULADA" if v.get("anulada") else "OK"
            print(f"\n  Venta {v['id']} | {v.get('fecha')} | {estado}")
            print(f"  {'Código':<8} {'Cant':>6} {'P.Unit':>10} {'Subtotal':>12}")
            print("  " + "-" * 40)
            for it in v.get("items", []):
                sub = it.get("subtotal", it["cantidad"] * it["precio_unitario"])
                print(f"  {it['codigo']:<8} {it['cantidad']:>6} {it['precio_unitario']:>10,.0f} {sub:>12,.0f}")
            print(f"  TOTAL: ${v.get('total', 0):,.0f}")
            return
    print(f"  [!] Venta {id_v} no encontrada.")


def ventas_por_fecha():
    print("\n--- VENTAS POR RANGO DE FECHAS ---")
    desde = pedir_texto("Desde (YYYY-MM-DD): ")
    hasta = pedir_texto("Hasta (YYYY-MM-DD): ")
    filtradas = [
        v for v in ventas
        if desde <= v.get("fecha", "")[:10] <= hasta and not v.get("anulada")
    ]
    if not filtradas:
        print("  Sin ventas en el rango indicado.")
        return
    total = 0
    print(f"\n  {'ID':<8} {'Fecha':<18} {'Ítems':>6} {'Total':>12}")
    print("  " + "-" * 48)
    for v in filtradas:
        n = len(v.get("items", []))
        total += v.get("total", 0)
        print(f"  {v['id']:<8} {v.get('fecha', ''):<18} {n:>6} {v.get('total', 0):>12,.0f}")
    print(f"  TOTAL RANGO: ${total:,.0f}  ({len(filtradas)} venta(s))")


def devolver_venta():
    if not solo_instructor("devolver ventas"):
        return
    print("\n--- DEVOLUCIÓN / ANULACIÓN DE VENTA ---")
    id_v = pedir_texto("ID de la venta: ").upper()
    venta = next((v for v in ventas if v.get("id") == id_v), None)
    if not venta:
        print(f"  [!] Venta {id_v} no encontrada.")
        return
    if venta.get("anulada"):
        print(f"  [!] La venta {id_v} ya está anulada.")
        return

    print(f"  Venta {id_v} | Total: ${venta.get('total', 0):,.0f}")
    for it in venta.get("items", []):
        print(f"    · {it['codigo']}: {it['cantidad']} uds")
    conf = input("¿Confirmar devolución completa? (s/n): ").strip().lower()
    if conf != "s":
        print("  Cancelado.")
        return

    for it in venta.get("items", []):
        movimientos.append({
            "id": siguiente_id("M", movimientos),
            "producto_codigo": it["codigo"],
            "tipo": "ENTRADA",
            "cantidad": it["cantidad"],
            "motivo": f"Devolución de venta {id_v}",
            "fecha": fecha_hora(),
        })
    venta["anulada"] = True
    venta["fecha_anulacion"] = fecha_hora()
    guardar_datos()
    print(f"  Venta {id_v} anulada. Inventario reingresado.")


def submenu_consultas_ventas():
    while True:
        print("\n----- CONSULTA DE VENTAS -----")
        print("1. Listar ventas")
        print("2. Detalle de venta")
        print("3. Filtrar por fechas")
        print("4. Devolver venta (solo INSTRUCTOR)")
        print("0. Volver")
        op = input("Opción: ").strip()
        if op == "1":
            listar_ventas()
        elif op == "2":
            detalle_venta()
        elif op == "3":
            ventas_por_fecha()
        elif op == "4":
            devolver_venta()
        elif op == "0":
            break
        else:
            print("  [!] Opción inválida.")


# -------------------- ALERTAS --------------------
def alertas_stock():
    print("\n--- ALERTAS DE STOCK MÍNIMO ---")
    alertas = []
    for p in productos:
        if not p.get("activo", True):
            continue
        stock = obtener_stock(p["codigo"])
        minimo = p.get("stock_minimo", 0)
        if stock <= minimo:
            alertas.append((p, stock, minimo))
    if not alertas:
        print("  Ningún producto por debajo del mínimo.")
        return
    print(f"  {'Código':<8} {'Nombre':<25} {'Stock':>8} {'Mínimo':>8} {'Dif.':>8}")
    print("  " + "-" * 62)
    for p, stock, minimo in alertas:
        print(f"  {p['codigo']:<8} {p['nombre'][:24]:<25} {stock:>8} {minimo:>8} {stock - minimo:>8}")


# -------------------- REPORTES --------------------
def reporte_existencias():
    print("\n--- EXISTENCIAS Y VALOR DE INVENTARIO ---")
    total_valor = 0
    print(f"  {'Código':<8} {'Nombre':<22} {'Stock':>7} {'P.Venta':>9} {'Valor':>12}")
    print("  " + "-" * 62)
    for p in productos:
        if not p.get("activo", True):
            continue
        stock = obtener_stock(p["codigo"])
        if stock <= 0:
            continue
        valor = stock * p.get("precio", 0)
        total_valor += valor
        print(f"  {p['codigo']:<8} {p['nombre'][:21]:<22} {stock:>7} "
              f"{p.get('precio', 0):>9,.0f} {valor:>12,.0f}")
    print("  " + "-" * 62)
    print(f"  VALOR TOTAL INVENTARIO: ${total_valor:,.0f}")


def reporte_ventas():
    print("\n--- RESUMEN DE VENTAS ---")
    activas = [v for v in ventas if not v.get("anulada")]
    if not activas:
        print("  No hay ventas activas.")
        return
    n = len(activas)
    unidades = 0
    ingresos = 0
    for v in activas:
        ingresos += v.get("total", 0)
        for it in v.get("items", []):
            unidades += it.get("cantidad", 0)
    print(f"  Ventas realizadas : {n}")
    print(f"  Unidades vendidas : {unidades}")
    print(f"  Ingresos totales  : ${ingresos:,.0f}")


def ranking_mas_vendidos():
    print("\n--- TOP 3 PRODUCTOS MÁS VENDIDOS ---")
    conteo = {}
    for v in ventas:
        if v.get("anulada"):
            continue
        for it in v.get("items", []):
            cod = it.get("codigo")
            conteo[cod] = conteo.get(cod, 0) + it.get("cantidad", 0)
    if not conteo:
        print("  Sin datos de ventas.")
        return
    orden = sorted(conteo.items(), key=lambda x: x[1], reverse=True)[:3]
    print(f"  {'#':<4} {'Código':<8} {'Nombre':<25} {'Vendidas':>10}")
    print("  " + "-" * 52)
    for i, (cod, cant) in enumerate(orden, 1):
        p = localizar_producto(cod)
        nombre = p["nombre"] if p else "(desconocido)"
        print(f"  {i:<4} {cod:<8} {nombre[:24]:<25} {cant:>10}")


def reporte_utilidad():
    print("\n--- UTILIDAD ESTIMADA ---")
    por_prod = {}
    for v in ventas:
        if v.get("anulada"):
            continue
        for it in v.get("items", []):
            cod = it.get("codigo")
            p = localizar_producto(cod)
            if not p:
                continue
            util = (it.get("precio_unitario", 0) - p.get("costo_unitario", 0)) * it.get("cantidad", 0)
            if cod not in por_prod:
                por_prod[cod] = {"nombre": p["nombre"], "unidades": 0, "utilidad": 0.0}
            por_prod[cod]["unidades"] += it.get("cantidad", 0)
            por_prod[cod]["utilidad"] += util
    if not por_prod:
        print("  Sin datos para calcular utilidad.")
        return
    total = 0
    print(f"  {'Código':<8} {'Nombre':<22} {'Unidades':>9} {'Utilidad':>12}")
    print("  " + "-" * 56)
    for cod, d in sorted(por_prod.items(), key=lambda x: x[1]["utilidad"], reverse=True):
        total += d["utilidad"]
        print(f"  {cod:<8} {d['nombre'][:21]:<22} {d['unidades']:>9} {d['utilidad']:>12,.0f}")
    print("  " + "-" * 56)
    print(f"  UTILIDAD TOTAL ESTIMADA: ${total:,.0f}")


def reporte_rotacion():
    """Productos con mayor rotación (unidades vendidas / stock actual + vendidas)."""
    print("\n--- PRODUCTOS CON MAYOR ROTACIÓN ---")
    datos = {}
    for v in ventas:
        if v.get("anulada"):
            continue
        for it in v.get("items", []):
            cod = it.get("codigo")
            datos[cod] = datos.get(cod, 0) + it.get("cantidad", 0)
    if not datos:
        print("  No hay ventas para calcular rotación.")
        return
    filas = []
    for cod, vendidas in datos.items():
        p = localizar_producto(cod)
        if not p or not p.get("activo", True):
            continue
        stock = obtener_stock(cod)
        base = stock + vendidas
        indice = (vendidas / base) if base > 0 else 0
        filas.append((cod, p["nombre"], vendidas, stock, indice))
    filas.sort(key=lambda x: x[4], reverse=True)
    print(f"  {'Código':<8} {'Nombre':<22} {'Vendidas':>9} {'Stock':>7} {'Índice':>8}")
    print("  " + "-" * 58)
    for cod, nombre, vend, stock, idx in filas[:10]:
        print(f"  {cod:<8} {nombre[:21]:<22} {vend:>9} {stock:>7} {idx:>8.2f}")


def exportar_csv():
    print("\n--- EXPORTAR INVENTARIO A CSV ---")
    ruta = DATA_DIR / f"inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    try:
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow([
                "codigo", "nombre", "categoria", "unidad", "precio", "costo_unitario",
                "stock_actual", "stock_minimo", "valor_inventario", "activo"
            ])
            for p in productos:
                stock = obtener_stock(p["codigo"])
                valor = stock * p.get("precio", 0)
                w.writerow([
                    p.get("codigo"), p.get("nombre"), p.get("categoria"), p.get("unidad"),
                    p.get("precio", 0), p.get("costo_unitario", 0), stock,
                    p.get("stock_minimo", 0), valor,
                    "SI" if p.get("activo", True) else "NO",
                ])
        print(f"  Archivo generado: {ruta}")
        print("  Separador: punto y coma (;)")
    except OSError as e:
        print(f"  [!] Error al exportar: {e}")


def submenu_reportes():
    while True:
        print("\n----- REPORTES -----")
        print("1. Existencias y valor")
        print("2. Resumen de ventas")
        print("3. Top 3 más vendidos")
        print("4. Utilidad estimada")
        print("5. Productos con mayor rotación")
        print("6. Exportar inventario CSV")
        print("0. Volver")
        op = input("Opción: ").strip()
        if op == "1":
            reporte_existencias()
        elif op == "2":
            reporte_ventas()
        elif op == "3":
            ranking_mas_vendidos()
        elif op == "4":
            reporte_utilidad()
        elif op == "5":
            reporte_rotacion()
        elif op == "6":
            exportar_csv()
        elif op == "0":
            break
        else:
            print("  [!] Opción inválida.")


# -------------------- MENÚ PRINCIPAL --------------------
def menu_principal():
    while True:
        rol = sesion.get("rol", "") if sesion else ""
        print(f"\n==================== AGROCONTROL CBA ====================")
        print(f"  Usuario: {sesion.get('nombre', '')} [{rol}]")
        print("----------------------------------------------------------")
        print("1. Gestión de productos")
        print("2. Gestión de lotes productivos")
        print("3. Movimientos de inventario")
        print("4. Registrar venta")
        print("5. Consultar ventas")
        print("6. Alertas de stock")
        print("7. Reportes")
        print("8. Guardar datos")
        print("0. Salir")
        op = input("Seleccione una opción: ").strip()
        if op == "1":
            submenu_productos()
        elif op == "2":
            submenu_lotes()
        elif op == "3":
            submenu_inventario()
        elif op == "4":
            nueva_venta()
        elif op == "5":
            submenu_consultas_ventas()
        elif op == "6":
            alertas_stock()
        elif op == "7":
            submenu_reportes()
        elif op == "8":
            guardar_datos()
        elif op == "0":
            guardar_datos()
            print("\n  Gracias por usar AgroControl CBA. Hasta pronto.")
            break
        else:
            print("  [!] Opción no válida.")


def main():
    print("=" * 52)
    print("  AGROCONTROL CBA - Gestión Productiva")
    print("  Centro de Biotecnología Agropecuaria | SENA")
    print("=" * 52)
    cargar_datos()
    if iniciar_sesion():
        menu_principal()


if __name__ == "__main__":
    main()
