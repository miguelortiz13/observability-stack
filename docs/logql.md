# 📜 Guía Práctica de LogQL — Consultas de Logs para Microservicios (P4-02)

> Catálogo de consultas en **LogQL** para el motor de logs **Grafana Loki**, enfocado en la inspección, filtrado de errores y análisis cuantitativo de la aplicación **Google Online Boutique**.

---

## 1. Selectores de Flujo (Stream Selectors)

### Consulta 1: Todos los Logs de un Microservicio Específico
* **Propósito:** Inspección general de la salida stdout/stderr de un componente.
* **Expresión LogQL:**
  ```logql
  {namespace="online-boutique", app="frontend"}
  ```
* **Explicación:**
  - Consulta rápida de streams indexados por las etiquetas `namespace` y `app` generadas por Grafana Alloy.

---

### Consulta 2: Logs del Namespace Completo de la Aplicación
* **Propósito:** Vista consolidada del flujo de eventos de los 11 microservicios en tiempo real.
* **Expresión LogQL:**
  ```logql
  {namespace="online-boutique"}
  ```

---

## 2. Filtros de Línea y Búsqueda de Errores (Line Filters)

### Consulta 3: Detección de Errores y Excepciones en el Frontend
* **Propósito:** Filtrado sensible a fallos que contiene palabras clave como `error`, `failed` o `exception`.
* **Expresión LogQL:**
  ```logql
  {namespace="online-boutique", app="frontend"} |= "error" or |= "Error" or |= "failed"
  ```
* **Explicación:**
  - `|=`: Filtro de inclusión de cadena literal (más eficiente que regex).
  - `or`: Permite evaluar múltiples variantes de capitalización.

---

### Consulta 4: Detección de Fallos gRPC en Servicios Backend
* **Propósito:** Identifica códigos de estado gRPC anormales (`Unavailable`, `DeadlineExceeded`, `Internal`) entre microservicios (Go, Python, Java).
* **Expresión LogQL:**
  ```logql
  {namespace="online-boutique"} |~ "(?i)(rpc error|code = Unavailable|code = Internal)"
  ```
* **Explicación:**
  - `|~`: Filtro de expresión regular con flag insensible a mayúsculas `(?i)`.

---

## 3. Parseo Estructurado y Filtrado por Campos (Parser Expressions)

### Consulta 5: Parseo JSON y Filtrado de Códigos HTTP $\ge 500$
* **Propósito:** Inspecciona logs formateados en JSON y filtra cuando la propiedad de respuesta HTTP representa un fallo de servidor.
* **Expresión LogQL:**
  ```logql
  {namespace="online-boutique", app="frontend"} | json | status >= 500
  ```
* **Explicación:**
  - `| json`: Extrae dinámicamente las claves del JSON como etiquetas temporales en tiempo de consulta.
  - `| status >= 500`: Aplica comparación numérica sobre el código de estado devuelto.

---

### Consulta 6: Búsqueda de Logs por Trace ID (Correlación para P4-06)
* **Propósito:** Permite ubicar todos los mensajes de registro emitidos por diferentes pods que comparten el mismo identificador de traza distribuida.
* **Expresión LogQL:**
  ```logql
  {namespace="online-boutique"} |= "trace_id=4bf92f3577b34da6a3ce929d0e0e4736"
  ```

---

## 4. Métricas de Logs (Log Range Aggregations)

### Consulta 7: Tasa de Errores por Segundo por Microservicio
* **Propósito:** Convierte streams de logs en series temporales para graficar la frecuencia de fallas en dashboards de Grafana.
* **Expresión LogQL:**
  ```logql
  sum by (app) (rate({namespace="online-boutique"} |= "error" [5m]))
  ```
* **Explicación:**
  - `[5m]`: Ventana de evaluación temporal.
  - `rate(...)`: Calcula el número de líneas de log con error por segundo.
  - `sum by (app)`: Agrupa los resultados por el nombre del microservicio.

---

### Consulta 8: Top 5 Servicios con Mayor Volumen de Logs de Error en la Última Hora
* **Propósito:** Prioriza qué equipo o microservicio está degradando la estabilidad del sistema durante un incidente.
* **Expresión LogQL:**
  ```logql
  topk(5, sum by (app) (count_over_time({namespace="online-boutique"} |~ "(?i)(error|fatal|exception)" [1h])))
  ```
* **Explicación:**
  - `count_over_time`: Cuenta el total absoluto de líneas que coinciden con el patrón en la ventana de 1 hora.
  - `topk(5, ...)`: Retorna exclusivamente los cinco servicios con el conteo más alto.
