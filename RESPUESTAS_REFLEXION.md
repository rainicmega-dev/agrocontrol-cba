# Respuestas a las preguntas de reflexión
## AgroControl CBA – Guía del Aprendiz

**Programa:** Técnico en Programación de Software  
**Centro:** Biotecnología Agropecuaria – CBA | SENA  
**Trimestre:** Segundo

---

### 1. ¿Por qué AgroControl CBA sigue siendo una aplicación monolítica aunque tenga varios módulos lógicos?

Porque toda la lógica (productos, lotes, inventario, ventas, reportes, autenticación) vive en un único archivo (`main.py`) y se ejecuta como un solo proceso. Los “módulos” son solo agrupaciones lógicas de funciones, no módulos o servicios independientes desplegados por separado. No hay separación en capas de red, ni microservicios, ni múltiples procesos.

### 2. ¿Qué ventaja ofrece calcular el stock a partir de movimientos y no modificar directamente un campo stock?

La principal ventaja es la **trazabilidad e integridad**. Cada entrada o salida queda registrada con fecha, motivo e identificador. El stock se deriva de la suma de movimientos, por lo que siempre es posible reconstruir el historial y detectar inconsistencias. Si se modificara un campo `stock` directamente, se podría alterar el inventario sin dejar rastro y sería más fácil introducir errores o discrepancias.

### 3. ¿Qué riesgo existe si una venta descuenta inventario antes de verificar todos sus productos?

El riesgo es dejar el inventario en un estado inconsistente. Si se descuenta el primer producto y luego se detecta que el segundo no tiene stock suficiente, habría que revertir el descuento ya aplicado. En un sistema sin transacciones, esa reversión puede fallar o olvidarse, generando stock negativo o datos incorrectos. Por eso el sistema valida **todos** los ítems antes de registrar cualquier movimiento de salida.

### 4. ¿Qué diferencia existe entre desactivar un producto y eliminarlo físicamente?

- **Desactivar:** el producto deja de estar disponible para nuevos lotes y ventas, pero se conserva en el historial (movimientos y ventas pasadas siguen siendo legibles y coherentes).
- **Eliminar físicamente:** se borra el registro. Eso rompería la integridad referencial: las ventas y movimientos que apuntan a ese código quedarían sin producto asociado y los reportes históricos se volverían incompletos o erróneos.

### 5. ¿Qué problema resuelve la persistencia JSON frente al ejercicio anterior?

Resuelve la **pérdida de información al cerrar el programa**. Sin persistencia, todos los datos viven solo en memoria y se pierden al terminar la ejecución. Con JSON, los datos se guardan en disco y se recuperan automáticamente al iniciar de nuevo, permitiendo continuidad entre sesiones.

### 6. ¿Qué información debería incluir un buen mensaje de commit?

Debe indicar **qué** se cambió y **por qué** (o la intención). Se recomienda el formato convencional:
- Prefijo: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`
- Descripción breve y clara en presente o infinitivo
- Ejemplo: `feat: agrega reporte de productos con mayor rotacion`

Evitar mensajes genéricos como “cambios”, “update” o “arreglos”.

### 7. ¿Cuál es la finalidad de trabajar una mejora en una rama diferente a main?

Aislar el desarrollo de la nueva funcionalidad sin afectar la rama principal estable. Permite:
- Probar la mejora de forma independiente
- Revisar el código antes de integrarlo
- Mantener `main` siempre funcional
- Facilitar la colaboración y el uso de Pull Requests

### 8. ¿Qué aporta un Pull Request incluso cuando el proyecto es académico?

Aporta práctica del flujo profesional de desarrollo: revisión de cambios, descripción de lo implementado, evidencia de pruebas y registro histórico de cómo se integró una mejora. Aunque no haya un equipo real, el aprendiz aprende a documentar, justificar y formalizar la integración de código, habilidades útiles en entornos laborales.

### 9. ¿Qué partes del sistema serían candidatas a convertirse en módulos separados en una evolución futura?

- Persistencia (lectura/escritura JSON o futura base de datos)
- Autenticación y gestión de usuarios/roles
- Cálculo de stock e inventario
- Lógica de ventas y devoluciones
- Generación de reportes
- Capa de interfaz (consola → web o GUI)

Separarlos facilitaría el mantenimiento, las pruebas unitarias y una eventual migración a arquitectura por capas o servicios.

### 10. ¿Qué limitaciones tendría JSON si el sistema creciera y fuera usado simultáneamente por varias personas?

- **Concurrencia:** varios usuarios escribiendo el mismo archivo pueden sobrescribir cambios (no hay bloqueo ni transacciones).
- **Rendimiento:** al crecer el volumen de datos, cargar y guardar todo el archivo en cada operación se vuelve lento.
- **Consultas:** no hay índices ni consultas eficientes; todo se filtra en memoria.
- **Integridad:** no hay restricciones de clave foránea ni validaciones a nivel de almacenamiento.
- **Escalabilidad:** no es adecuado para acceso multiusuario concurrente ni para despliegues distribuidos.

En ese escenario sería necesario migrar a una base de datos (SQLite, PostgreSQL, etc.) con control de transacciones y acceso concurrente.

---

*Documento elaborado como evidencia de la Guía del Aprendiz – AgroControl CBA.*
