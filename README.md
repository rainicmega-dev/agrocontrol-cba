# AgroControl CBA

**Sistema monolítico de gestión de producción, inventario y ventas**

Centro de Biotecnología Agropecuaria – CBA  
Servicio Nacional de Aprendizaje – SENA  
Facatativá, Cundinamarca

## Descripción

AgroControl CBA es una aplicación de consola en Python que permite administrar:

- Productos comercializables (precio, costo unitario y stock mínimo)
- Lotes productivos asociados a cultivos
- Movimientos de inventario (entradas y salidas)
- Ventas de uno o varios ítems
- Devoluciones / anulación de ventas
- Alertas de stock bajo
- Reportes de existencias, ventas, ranking, utilidad y rotación
- Exportación de inventario a CSV
- Autenticación con roles OPERADOR e INSTRUCTOR
- Respaldo automático de archivos JSON

La información se almacena en archivos JSON locales. El stock se calcula a partir de los movimientos (no se guarda como campo estático).

## Tecnologías

- Python 3 (módulos estándar: `json`, `csv`, `shutil`, `datetime`, `pathlib`)
- JSON para persistencia
- Git / GitHub para control de versiones

No se emplean bases de datos, frameworks web ni librerías externas.

## Estructura

```
agrocontrol_cba/
├── main.py
├── data/
│   ├── productos.json
│   ├── lotes.json
│   ├── movimientos.json
│   ├── ventas.json
│   ├── usuarios.json
│   └── backups/
├── README.md
└── .gitignore
```

## Requisitos

Python 3.8 o superior.

## Ejecución

```bash
cd agrocontrol_cba
python main.py
```

### Credenciales

| Usuario | Clave    | Rol        |
|---------|----------|------------|
| campo   | campo01  | OPERADOR   |
| admin   | cba2026  | INSTRUCTOR |

- **OPERADOR**: productos, lotes, inventario, ventas y reportes.
- **INSTRUCTOR**: todo lo anterior + desactivar productos y devolver ventas.

## Menú principal

```
1. Gestión de productos
2. Gestión de lotes productivos
3. Movimientos de inventario
4. Registrar venta
5. Consultar ventas
6. Alertas de stock
7. Reportes
8. Guardar datos
0. Salir
```

## Reglas de negocio

1. Códigos de producto y lote únicos, almacenados en mayúscula.
2. Producto desactivado conserva historial; no permite nuevos lotes ni ventas.
3. Stock se calcula desde movimientos de inventario.
4. Salidas y ventas no pueden generar stock negativo.
5. Un lote solo se cosecha una vez; al cosechar genera entrada automática.
6. Toda venta debe tener al menos un ítem válido.
7. El precio de venta se toma del precio vigente y se guarda en el detalle.
8. Toda modificación se persiste inmediatamente en JSON (con backup previo).
9. Identificadores secuenciales: M0001, V0001, L001, etc.

## Retos de ampliación incluidos

| Funcionalidad              | Descripción                                      |
|----------------------------|--------------------------------------------------|
| Ventas por fechas          | Filtro por rango YYYY-MM-DD                      |
| Utilidad estimada          | (precio − costo) × cantidad vendida              |
| Devolución de ventas       | Reingreso de inventario (solo INSTRUCTOR)        |
| Exportar CSV               | Inventario completo a archivo CSV                |
| Backup automático          | Copia de JSON antes de cada guardado             |
| Autenticación + roles      | Login OPERADOR / INSTRUCTOR                      |
| Reporte de rotación        | Índice de rotación de productos                  |

## Modelo de datos

### Producto
```json
{
  "codigo": "P001",
  "nombre": "Tomate chonto",
  "categoria": "Hortalizas",
  "unidad": "kg",
  "precio": 4200,
  "costo_unitario": 2100,
  "stock_minimo": 15,
  "activo": true
}
```

### Lote
```json
{
  "id_lote": "L001",
  "producto_codigo": "P001",
  "fecha_siembra": "2026-07-20",
  "area_m2": 85.0,
  "cantidad_producida": 40,
  "estado": "COSECHADO"
}
```

### Movimiento
```json
{
  "id": "M0001",
  "producto_codigo": "P001",
  "tipo": "ENTRADA",
  "cantidad": 40,
  "motivo": "Cosecha del lote L001",
  "fecha": "2026-09-10 09:15"
}
```

### Venta
```json
{
  "id": "V0001",
  "fecha": "2026-09-10 11:00",
  "items": [
    {"codigo": "P001", "cantidad": 8, "precio_unitario": 4200, "subtotal": 33600}
  ],
  "total": 33600,
  "anulada": false
}
```

## Flujo Git sugerido

```bash
git log --oneline --graph --decorate --all
```

1. Crear repositorio remoto `agrocontrol-cba`
2. `git remote add origin <URL>`
3. `git push -u origin main`
4. Crear Issue (ej. “Agregar reporte de productos con mayor rotación”)
5. Rama `feature/reporte-rotacion`
6. Commit de la mejora y Pull Request hacia `main`

## Pruebas mínimas

| Código | Caso                    | Resultado esperado                          |
|--------|-------------------------|---------------------------------------------|
| PF001  | Producto duplicado      | Rechaza el segundo registro                 |
| PF002  | Precio inválido         | Solicita valor válido                       |
| PF003  | Lote inexistente        | Informa que no existe                       |
| PF004  | Doble cosecha           | Segunda operación rechazada                 |
| PF005  | Salida excesiva         | Impide la operación                         |
| PF006  | Venta válida            | Crea venta y reduce stock                   |
| PF007  | Venta múltiple          | Calcula subtotales y total                  |
| PF008  | Persistencia            | Datos se conservan al reiniciar             |
| PF009  | Alerta de stock         | Aparece en reporte de alertas               |
| PF010  | Devolución de venta     | Reingresa inventario y anula la venta       |
| PF011  | Login incorrecto        | Deniega acceso tras 3 intentos              |
| PF012  | Exportar CSV            | Genera archivo en carpeta data/             |

## Autores

Aprendices – Técnico en Programación de Software  
Segundo trimestre – Centro de Biotecnología Agropecuaria (CBA)

## Licencia

Uso educativo – SENA
