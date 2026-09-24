# Checklist de entrega – AgroControl CBA

## ✅ Ya listo en este paquete

- [x] `main.py` funcional (sintaxis correcta, todos los RF y retos de ampliación)
- [x] Carpeta `data/` con JSON de ejemplo (productos, lotes, movimientos, ventas, usuarios)
- [x] `README.md` completo (descripción, ejecución, reglas, modelo de datos, pruebas, autores)
- [x] `.gitignore` configurado
- [x] Repositorio Git con **16 commits** significativos (mínimo exigido: 12)
- [x] Rama `feature/reporte-rotacion` con la mejora de rotación
- [x] Retos de ampliación implementados:
  - Autenticación OPERADOR / INSTRUCTOR
  - Consulta de ventas por fechas
  - Reporte de utilidad estimada (costo unitario)
  - Devolución de ventas
  - Exportación CSV
  - Backup automático de JSON
- [x] `RESPUESTAS_REFLEXION.md` – las 10 preguntas de la guía
- [x] `EVIDENCIAS_PRUEBAS.md` – resultados de PF001 a PF012 + historial Git

## ⚠️ Lo que TÚ debes hacer (no se puede hacer desde aquí)

1. **Subir a GitHub**
   ```bash
   # Crea el repo vacío en GitHub llamado: agrocontrol-cba
   git remote add origin https://github.com/TU_USUARIO/agrocontrol-cba.git
   git push -u origin main
   git push -u origin feature/reporte-rotacion
   ```

2. **Crear Issue** en GitHub  
   Título sugerido: *Agregar reporte de productos con mayor rotación*

3. **Crear Pull Request**  
   Desde `feature/reporte-rotacion` → `main`  
   Describe qué se cambió y cómo se probó.

4. **Capturas de pantalla** (opcional pero recomendado)
   - Login exitoso / fallido
   - Una venta y el reporte de alertas
   - El Issue y el PR en GitHub
   - `git log --oneline --graph --decorate --all`

5. **Entregar al instructor**
   - Este ZIP (o el enlace al repositorio de GitHub)
   - Las capturas del Issue y del PR
   - Las respuestas de reflexión (ya incluidas)

---

**Conclusión:** El código y la documentación local están listos para entrega.  
Solo falta el flujo en GitHub (remote + Issue + PR) y, si el profesor lo pide, las capturas.
