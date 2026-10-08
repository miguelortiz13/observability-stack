# 📊 Guía Práctica de PromQL — 10 Consultas de Producción (P4-01)

> Catálogo de consultas PromQL organizadas bajo las metodologías **USE** (recursos de infraestructura), **RED** (servicios de aplicación) y **SRE** (presupuestos de error y disponibilidad).

---

## 1. Métricas de Infraestructura y Nodos (Método USE: Utilization, Saturation, Errors)

### Consulta 1: Porcentaje de Utilización de CPU por Nodo
* **Propósito:** Mide el tiempo de procesador en modos no ociosos (`user`, `system`, `iowait`, etc.) para detectar saturación de cómputo en los nodos de Kubernetes.
* **Expresión PromQL:**
  ```promql
  100 - (avg by (node) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
  ```
* **Explicación:**
  - `node_cpu_seconds_total{mode="idle"}`: Contador acumulativo de segundos en reposo.
  - `rate(...[5m])`: Calcula la derivada por segundo en una ventana deslizante de 5 minutos.
  - `avg by (node)`: Promedia los núcleos de cada nodo físico o virtual.
  - `100 - ...`: Invierte la fracción de inactividad para obtener el porcentaje de uso.
* **Umbral Recomendado:** Advertencia si $> 80\%$, Crítico si $> 90\%$ por más de 10 minutos.

---

### Consulta 2: Porcentaje de Memoria RAM Utilizada por Nodo
* **Propósito:** Evalúa la presión de memoria real del nodo considerando la memoria disponible efectiva (incluyendo buffers y cachés recuperables).
* **Expresión PromQL:**
  ```promql
  (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100
  ```
* **Explicación:**
  - `node_memory_MemAvailable_bytes`: Memoria que el kernel de Linux puede asignar inmediatamente sin entrar en swap.
  - Se resta del total para obtener la memoria en uso real y se normaliza a escala de 0 a 100%.
* **Umbral Recomendado:** Crítico si $> 85\%$ (riesgo inminente de expulsión de pods por `NodeMemoryPressure` o invocación de `OOMKiller`).

---

### Consulta 3: Porcentaje de Espacio en Disco Utilizado (Root Mountpoint)
* **Propósito:** Monitorea la ocupación del sistema de archivos raíz (`/`) donde se almacenan las capas de imágenes de Docker y los logs efímeros de contenedores.
* **Expresión PromQL:**
  ```promql
  (node_filesystem_size_bytes{mountpoint="/", fstype!="rootfs"} - node_filesystem_free_bytes{mountpoint="/", fstype!="rootfs"}) 
  / node_filesystem_size_bytes{mountpoint="/", fstype!="rootfs"} * 100
  ```
* **Explicación:**
  - Filtra por `mountpoint="/"` y descarta alias duplicados de `rootfs`.
  - Mide la relación entre espacio libre y total asignado al disco del nodo.
* **Umbral Recomendado:** Alerta si $> 80\%$ de ocupación.

---

## 2. Salud de Cargas de Trabajo y Pods en Kubernetes

### Consulta 4: Detección de Contenedores en CrashLoopBackOff o Reinicios Frecuentes
* **Propósito:** Identifica pods inestables que fallan periódicamente debido a pánicos, configuraciones inválidas o OOMKilled.
* **Expresión PromQL:**
  ```promql
  sum by (namespace, pod) (increase(kube_pod_container_status_restarts_total[1h])) > 0
  ```
* **Explicación:**
  - `increase(...[1h])`: Calcula el incremento absoluto en el contador de reinicios en la última hora.
  - `> 0`: Filtra únicamente los pods que sufrieron al menos un reinicio reciente.
* **Acción de Guardia:** Inspeccionar `kubectl describe pod <pod>` y `kubectl logs <pod> --previous`.

---

### Consulta 5: Porcentaje de CPU Utilizada respecto al Límite Configurado
* **Propósito:** Detecta qué contenedores se encuentran cerca de ser limitados por el kernel (*CPU throttling* por CFS).
* **Expresión PromQL:**
  ```promql
  sum by (namespace, pod, container) (rate(container_cpu_usage_seconds_total{container!=""}[5m]))
  /
  sum by (namespace, pod, container) (container_spec_cpu_limit{container!=""}) * 100
  ```
* **Explicación:**
  - Divide la tasa de consumo de CPU entre el límite máximo de CPU especificado en el manifiesto (`spec.containers[*].resources.limits.cpu`).
* **Umbral Recomendado:** Alerta si $> 90\%$ de forma sostenida (indica estrangulamiento de CPU).

---

### Consulta 6: Porcentaje de Memoria Working Set vs. Límite de Memoria (Riesgo de OOM)
* **Propósito:** Anticipa la terminación prematura de pods por falta de memoria antes de que el kernel invoque `SIGKILL` (Exit Code 137).
* **Expresión PromQL:**
  ```promql
  sum by (namespace, pod, container) (container_memory_working_set_bytes{container!=""})
  /
  sum by (namespace, pod, container) (container_spec_memory_limit_bytes{container!=""}) * 100
  ```
* **Explicación:**
  - `container_memory_working_set_bytes`: Métrica real utilizada por el OOM-Killer de Kubernetes para decidir qué contenedor terminar.
* **Umbral Recomendado:** Crítico si $> 95\%$.

---

## 3. Métricas de Microservicios (Método RED: Rate, Errors, Duration)

### Consulta 7: Tasa de Peticiones por Segundo (RPS - Rate)
* **Propósito:** Visualiza el rendimiento y demanda de tráfico entrante por microservicio en Online Boutique.
* **Expresión PromQL:**
  ```promql
  sum by (service) (rate(http_requests_total[5m]))
  ```
* **Explicación:**
  - Agrupa por etiqueta `service` (`frontend`, `cartservice`, `checkoutservice`, etc.).
  - Calcula la velocidad media de llamadas HTTP/gRPC por segundo.

---

### Consulta 8: Porcentaje de Tasa de Errores HTTP 5xx (Errors)
* **Propósito:** Mide la fracción porcentual de solicitudes que resultan en fallos de servidor (HTTP 500, 502, 503, 504).
* **Expresión PromQL:**
  ```promql
  (
    sum by (service) (rate(http_requests_total{status=~"5.."}[5m]))
    /
    sum by (service) (rate(http_requests_total[5m]))
  ) * 100
  ```
* **Explicación:**
  - Expresión regular `status=~"5.."` selecciona todas las respuestas HTTP de la familia 500.
  - Normaliza la tasa de errores respecto al volumen total de tráfico del microservicio.
* **Umbral Recomendado:** Alerta si $> 1\%$ (impacto directo en el SLI de disponibilidad).

---

### Consulta 9: Latencia Percentil 95 ($P_{95}$) y Percentil 99 ($P_{99}$) (Duration)
* **Propósito:** Identifica degradaciones en los tiempos de respuesta que afectan a los usuarios de la cola de distribución (evita el engaño del promedio).
* **Expresión PromQL ($P_{95}$):**
  ```promql
  histogram_quantile(0.95, sum by (le, service) (rate(http_request_duration_seconds_bucket[5m])))
  ```
* **Expresión PromQL ($P_{99}$):**
  ```promql
  histogram_quantile(0.99, sum by (le, service) (rate(http_request_duration_seconds_bucket[5m])))
  ```
* **Explicación:**
  - Interpola la función `histogram_quantile` sobre los cubos acumulativos (`le`) calculados en los últimos 5 minutos.
* **Umbral SLO:** $P_{95} \le 200\text{ms}$ y $P_{99} \le 500\text{ms}$ para el frontend.

---

## 4. Ingeniería SRE y Presupuestos de Error (Error Budget Burn Rate)

### Consulta 10: Tasa de Consumo del Presupuesto de Error (Burn Rate a 1 Hora)
* **Propósito:** Alerta multi-ventana para Google SRE Workbook. Evalúa si el ritmo de errores actual agotará el 100% del Error Budget en un período crítico.
* **Objetivo de Nivel de Servicio (SLO):** $99.9\%$ de disponibilidad mensual ($\text{Error Budget} = 0.1\% = 0.001$).
* **Expresión PromQL:**
  ```promql
  (
    sum(rate(http_requests_total{status=~"5.."}[1h]))
    /
    sum(rate(http_requests_total[1h]))
  )
  /
  (1 - 0.999)
  ```
* **Explicación:**
  - $\text{Burn Rate} = 1$: El presupuesto se consumirá exactamente en 30 días (ritmo nominal).
  - $\text{Burn Rate} = 14.4$: Se consumirá el $2\%$ del presupuesto mensual en 1 hora (alerta de página inmediata / severidad 1).
  - Permite priorizar incidentes según el impacto directo en los compromisos comerciales (SLAs).
