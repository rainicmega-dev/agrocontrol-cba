#!/usr/bin/env python3
"""
AgroControl CBA
Sistema monolítico de gestión productiva, inventario y ventas.
Centro de Biotecnología Agropecuaria – CBA | SENA
"""

from pathlib import Path

# Rutas base
BASE = Path(__file__).resolve().parent
DATA = BASE / "data"

def menu_principal():
    while True:
        print("\n========== AGROCONTROL CBA ==========")
        print("1. Gestión de productos")
        print("2. Gestión de lotes productivos")
        print("3. Movimientos de inventario")
        print("4. Registrar venta")
        print("5. Consultar ventas")
        print("6. Alertas de stock")
        print("7. Reportes")
        print("8. Guardar datos")
        print("0. Salir")
        opcion = input("Seleccione una opción: ").strip()
        if opcion == "0":
            print("  Hasta pronto.")
            break
        else:
            print("  [!] Módulo aún no implementado.")

def main():
    print("=" * 50)
    print("  AGROCONTROL CBA")
    print("  Centro de Biotecnología Agropecuaria | SENA")
    print("=" * 50)
    DATA.mkdir(parents=True, exist_ok=True)
    menu_principal()

if __name__ == "__main__":
    main()
