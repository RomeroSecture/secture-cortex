# Registro de Deuda Técnica — Proyecto MiTienda

**Proyecto**: MiTienda E-Commerce — RetailMax S.L.
**Última actualización**: Marzo 2026
**Responsable**: Laura García, Tech Lead — Secture

---

## Resumen

| Severidad | Items | Esfuerzo Total Estimado |
|-----------|-------|------------------------|
| CRÍTICA | 2 | 8-11 días |
| MEDIA | 3 | 10-14 días |
| BAJA | 2 | 4-6 días |
| **Total** | **7** | **22-31 días** |

---

## Items de Deuda Técnica

### TD-001 — PaymentModule: Sin Circuit Breaker [CRÍTICA]

**Módulo afectado**: PaymentModule
**Dependencias impactadas**: OrderModule, NotificationModule
**Fecha detectada**: Noviembre 2025

**Descripción**: TODO: Implementar circuit breaker en la conexión con Stripe SDK. La integración actual con Stripe tiene un timeout de 10 segundos y **no implementa retry automático**. Cuando Stripe falla o responde lento, la transacción se pierde silenciosamente. El OrderModule queda en estado "pending" indefinidamente.

**Impacto**:
- Se estima que un **2-3% de transacciones fallan** en picos de tráfico (Black Friday, rebajas) por timeouts no reintentados
- Algunos clientes reportan que **se les cobró pero no recibieron confirmación** porque Stripe procesó el pago pero el webhook no se procesó correctamente tras el timeout
- Pérdida estimada: €3,000-5,000/mes en temporada alta por carritos abandonados post-error

**Solución propuesta**: Implementar patrón Circuit Breaker con Opossum.js. Configurar retry con backoff exponencial (3 intentos, 1s/2s/4s). Agregar idempotency key en todas las llamadas a Stripe para evitar cobros duplicados. Implementar reconciliación periódica Stripe vs. base de datos.

**Esfuerzo estimado**: 3-5 días desarrollo + 2 días testing
**Prioridad**: P1 — afecta ingresos directamente
**Estado**: Pendiente — priorizado para sprint actual

---

### TD-002 — AuthModule: JWT sin Refresh Tokens [CRÍTICA]

**Módulo afectado**: AuthModule
**Dependencias impactadas**: Todos los módulos (auth es transversal)
**Fecha detectada**: Septiembre 2025

**Descripción**: FIXME: El sistema de autenticación usa JWT sin refresh tokens. Los access tokens tienen una expiración de **2 horas**. Cuando expiran, el usuario es forzado a re-hacer login completo, perdiendo el estado de la sesión (carrito, filtros, formularios).

**Workaround actual**: Como medida temporal, se extendió la duración del access token a **24 horas**. Esto es un **riesgo de seguridad** porque un token robado da acceso prolongado sin posibilidad de revocación inmediata.

**Impacto**:
- Riesgo de seguridad: tokens de larga duración sin mecanismo de revocación
- UX degradada: re-login frecuente para usuarios activos
- Incompatible con requisitos de compliance GDPR para sesiones sensibles

**Solución propuesta**: Implementar flujo completo de refresh tokens. Access token con TTL de 15 minutos, refresh token con TTL de 7 días en httpOnly cookie. Endpoint `/auth/refresh` para renovación transparente. Blacklist de tokens revocados en Redis.

**Esfuerzo estimado**: 2-3 días desarrollo + 1 día testing
**Prioridad**: P1 — riesgo de seguridad
**Estado**: Pendiente

---

### TD-003 — CatalogModule: Queries N+1 y Sin Cache [MEDIA]

**Módulo afectado**: CatalogModule
**Fecha detectada**: Octubre 2025

**Descripción**: El listado de productos con categorías ejecuta queries N+1. Para un listado de 50 productos, se ejecutan 51 queries SQL (1 para productos + 1 por producto para cargar la categoría). No hay cache de Redis implementado para el catálogo.

HACK: Como workaround se implementó un cache en memoria del proceso Node.js con TTL manual de 5 minutos. Esto no escala en un entorno multi-instancia (cada instancia ECS tiene su propia cache) y consume memoria del proceso.

**Impacto**:
- Performance degrada significativamente con más de **10,000 productos** (actualmente 8,500 SKUs)
- Tiempo de respuesta del listado: 800ms (aceptable) pero proyectado a 2.5s con 15,000 productos
- Cache inconsistente entre instancias del backend

**Solución propuesta**: Implementar eager loading con JOINs para categorías. Migrar cache a Redis con invalidación por eventos. Evaluar migración a Elasticsearch para búsqueda full-text y faceted search.

**Esfuerzo estimado**: 3-4 días desarrollo (incluye migración a Elasticsearch)
**Prioridad**: P2 — degradará cuando el catálogo crezca
**Estado**: Pendiente — planificado para sprint 4 de Fase 2

---

### TD-004 — NotificationModule: Acoplamiento SMTP [MEDIA]

**Módulo afectado**: NotificationModule (FROZEN)
**Fecha detectada**: Enero 2026

**Descripción**: El módulo de notificaciones está directamente acoplado al protocolo SMTP via nodemailer. No existe una capa de abstracción de canales. Los templates de email están hardcodeados como strings HTML en el código fuente.

**Impacto**:
- **Imposible agregar push notifications o SMS** sin un refactor mayor
- Templates de email difíciles de mantener y sin preview
- No hay logging de entregas ni métricas de apertura propias (depende de Amazon SES)

**Solución propuesta**: Implementar Channel Adapter pattern. Crear interfaz NotificationChannel con implementaciones para Email, WebPush, SMS. Migrar templates a sistema de plantillas (Handlebars o similar). Agregar queue con RabbitMQ para envío asíncrono con retry.

**Esfuerzo estimado**: 5-7 días desarrollo + 2 días testing
**Prioridad**: P2 — bloqueante para Fase 3 (push notifications)
**Estado**: FROZEN — no se trabajará hasta v3.0 (Q4 2026)
**Nota**: Decisión tomada en reunión del 15 de enero de 2026. El módulo permanece congelado para evitar regresiones en el flujo crítico de confirmación de pedidos.

---

### TD-005 — CatalogModule: Búsqueda con SQL LIKE [MEDIA]

**Módulo afectado**: CatalogModule
**Fecha detectada**: Agosto 2025

**Descripción**: La búsqueda de productos usa queries `WHERE name ILIKE '%término%'`. No soporta búsqueda fuzzy, corrección ortográfica, sinónimos ni relevancia.

**Impacto**:
- Los usuarios no encuentran productos si escriben con faltas de ortografía
- Sin ranking de relevancia — resultados ordenados por fecha
- No soporta búsqueda por especificaciones técnicas ni descripciones

**Solución propuesta**: Migrar a Elasticsearch. Configurar analizadores para español. Implementar búsqueda fuzzy con sugerencias "did you mean?".

**Esfuerzo estimado**: 4-5 días desarrollo
**Prioridad**: P2
**Estado**: Pendiente — parte del plan de migración de TD-003

---

### TD-006 — AnalyticsModule: Scripts SQL Manuales [BAJA]

**Módulo afectado**: AnalyticsModule
**Fecha detectada**: Diciembre 2025

**Descripción**: FIXME: Los reportes de analytics se generan mediante scripts SQL ejecutados por cron jobs cada 24 horas. No hay pipeline ETL automatizado. Los datos de los dashboards tienen hasta 24 horas de retraso.

**Impacto**:
- Datos no son en tiempo real (retraso de hasta 24h)
- Scripts frágiles que fallan silenciosamente si el schema cambia
- Test coverage del módulo: **12%** — el más bajo del sistema

**Solución propuesta**: Implementar pipeline ETL con dbt (data build tool). Ejecutar transformaciones cada hora. Agregar tests de datos. Alerting en caso de fallo.

**Esfuerzo estimado**: 3-4 días
**Prioridad**: P3
**Estado**: En diseño como parte de Fase 2

---

### TD-007 — Testing: Coverage Inconsistente [BAJA]

**Módulo afectado**: Todos
**Fecha detectada**: Enero 2026

**Descripción**: El test coverage global es del 62%, por debajo del objetivo del 70%. Distribución por módulo:

| Módulo | Coverage | Objetivo |
|--------|----------|----------|
| AuthModule | 78% | 80% |
| CatalogModule | 71% | 70% ✅ |
| OrderModule | 68% | 80% |
| PaymentModule | 65% | 80% |
| NotificationModule | 45% | 70% |
| AnalyticsModule | 12% | 70% |

**Impacto**: Riesgo de regresiones no detectadas, especialmente en PaymentModule y NotificationModule.

**Esfuerzo estimado**: 3-4 días para llevar todos los módulos al 70%
**Prioridad**: P3
**Estado**: Se irá mejorando de forma incremental
