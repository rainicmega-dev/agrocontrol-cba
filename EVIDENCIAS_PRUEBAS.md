# Evidencias de pruebas mínimas
## AgroControl CBA

**Fecha de ejecución:** 22-23 de septiembre de 2026  
**Entorno:** Python 3 · Linux  
**Ejecutado por:** Aprendiz – Técnico en Programación de Software · CBA SENA

---

## Resumen de resultados

| Código | Caso                         | Resultado   | Observación |
|--------|------------------------------|-------------|-------------|
| PF001  | Producto duplicado           | ✅ Cumple   | Rechaza segundo P001 |
| PF002  | Precio inválido              | ✅ Cumple   | Solicita valor > 0 |
| PF003  | Lote inexistente             | ✅ Cumple   | Informa que L999 no existe |
| PF004  | Doble cosecha                | ✅ Cumple   | Segunda cosecha rechazada |
| PF005  | Salida excesiva              | ✅ Cumple   | Impide salida mayor al stock |
| PF006  | Venta válida                 | ✅ Cumple   | Crea V0001 y reduce stock |
| PF007  | Venta múltiple               | ✅ Cumple   | Calcula subtotales y total |
| PF008  | Persistencia                 | ✅ Cumple   | Datos se conservan al reiniciar |
| PF009  | Alerta de stock              | ✅ Cumple   | Aparece en menú de alertas |
| PF010  | Devolución de venta          | ✅ Cumple   | Reingresa stock y anula venta |
| PF011  | Login incorrecto             | ✅ Cumple   | Deniega acceso tras 3 intentos |
| PF012  | Exportar CSV                 | ✅ Cumple   | Genera archivo en data/ |

---

## Detalle de cada caso

### PF001 – Producto duplicado
**Acción:** Intentar registrar dos veces el código `P001`.  
**Resultado:** El sistema muestra mensaje de rechazo (“Ya existe un producto con ese código”) y no crea el segundo registro.

### PF002 – Precio inválido
**Acción:** Ingresar precio `0` o texto no numérico al crear/editar producto.  
**Resultado:** Solicita nuevamente un valor válido (precio > 0). No cierra el programa.

### PF003 – Lote inexistente
**Acción:** Intentar cosechar el lote `L999`.  
**Resultado:** Informa que el lote no existe y regresa al submenú sin modificar datos.

### PF004 – Doble cosecha
**Acción:** Cosechar el lote `L001` (estado COSECHADO) por segunda vez.  
**Resultado:** Rechaza la operación indicando que el lote ya fue cosechado.

### PF005 – Salida excesiva
**Acción:** Con stock de 32 kg de P001, intentar una salida de 50.  
**Resultado:** Impide la operación por inventario insuficiente. Stock permanece sin cambio.

### PF006 – Venta válida
**Acción:** Registrar venta de 8 kg de P001 (stock suficiente).  
**Resultado:** Se crea la venta `V0001`, se genera movimiento de SALIDA y el stock se reduce correctamente.

### PF007 – Venta múltiple
**Acción:** Venta con dos productos (P001 y P002) en cantidades válidas.  
**Resultado:** Calcula subtotal por ítem y total de la venta. Ambos productos descuentan stock.

### PF008 – Persistencia
**Acción:** Registrar datos, salir del programa y volver a ejecutarlo.  
**Resultado:** Los archivos JSON se cargan automáticamente. Productos, lotes, movimientos y ventas se conservan.

### PF009 – Alerta de stock
**Acción:** Dejar el stock de un producto ≤ stock_mínimo (o consultar con datos de ejemplo).  
**Resultado:** El producto aparece en la opción “Alertas de stock” del menú principal.

### PF010 – Devolución de venta (reto de ampliación)
**Acción:** Como usuario INSTRUCTOR (`admin` / `cba2026`), devolver la venta V0001.  
**Resultado:** Se genera movimiento de ENTRADA inverso, se marca la venta como anulada y el stock se restablece.

### PF011 – Login incorrecto
**Acción:** Ingresar usuario/clave incorrectos tres veces.  
**Resultado:** Tras el tercer intento fallido, el sistema deniega el acceso y finaliza.

### PF012 – Exportar CSV (reto de ampliación)
**Acción:** Desde el menú de Reportes, elegir exportar inventario a CSV.  
**Resultado:** Se genera un archivo `inventario_YYYYMMDD_HHMMSS.csv` dentro de la carpeta `data/`.

---

## Evidencia de historial Git

```text
* 1849dd5 (HEAD -> main) chore: agrega archivos JSON de ejemplo generados por la aplicacion
* 0014bad feat: implementa retos de ampliacion (auth, utilidad, devoluciones, CSV, backup, fechas)
* 4b553f1 (feature/reporte-rotacion) feat: agrega reporte de productos con mayor rotacion
* 78238e1 chore: prepara flujo de ramas e issues para GitHub
* 28bdb1a docs: agrega casos de prueba minimos y criterios de finalizacion
* f1a9ac7 docs: documenta ejecucion, reglas de negocio y estructura del proyecto
* 54edb34 refactor: mejora mensajes de error y manejo de entradas invalidas
* e503977 fix: valida doble cosecha y productos desactivados
* 507772e fix: evita salidas y ventas con inventario insuficiente
* 90846f6 feat: agrega alertas de stock y reportes operativos
* 34d2c4f feat: registra ventas con multiples items y descuento de inventario
* 7cf9a7d feat: agrega movimientos de inventario y calculo de stock
* 03813b4 feat: implementa registro y cosecha de lotes productivos
* 3ce6b6c feat: agrega gestion y validacion de productos (CRUD)
* 60d0b3f feat: implementa carga y guardado de archivos JSON
* 1329f7e chore: crea estructura inicial de AgroControl CBA y .gitignore
```

**Total de commits significativos:** 16 (supera el mínimo de 12 exigido).

**Rama de mejora:** `feature/reporte-rotacion` (reporte de productos con mayor rotación).

---

## Nota sobre GitHub

El repositorio local está listo. Para completar las evidencias de la guía el aprendiz debe:

1. Crear el repositorio remoto `agrocontrol-cba` en GitHub.
2. `git remote add origin <URL>` y `git push -u origin main`.
3. Crear un Issue (ej. “Agregar reporte de productos con mayor rotación”).
4. Publicar la rama `feature/reporte-rotacion` y abrir el Pull Request correspondiente.
5. Adjuntar capturas del Issue y del PR como evidencia adicional.

---

*Documento de evidencias – AgroControl CBA · CBA SENA*
