# Contrato de Servicios y Alcance del Proyecto — MiTienda

**Cliente**: RetailMax S.L. (CIF: B-12345678)
**Proveedor**: Secture Tecnología S.L.
**Proyecto**: MiTienda — Plataforma E-Commerce
**Fecha de firma**: 1 de enero de 2025
**Duración**: 24 meses (hasta 31 de diciembre de 2026)
**Referencia contrato**: SECT-2025-0042

---

## Resumen Ejecutivo

Secture desarrolla y mantiene la plataforma de e-commerce "MiTienda" para RetailMax S.L., una cadena retail con 50 tiendas físicas en España que busca digitalizar su canal de ventas. El proyecto se ejecuta en 3 fases con entregables definidos, presupuesto fijo por fase y un modelo de horas mensuales con techo.

---

## Fases del Proyecto

### Fase 1 — Fundación (Enero – Diciembre 2025) ✅ COMPLETADA

Entregables completados:
- Catálogo de productos online con gestión de categorías
- Carrito de compra persistente con integración Redis
- Checkout completo con pasarela de pago Stripe
- Sistema de autenticación y gestión de usuarios
- Panel de administración básico
- Despliegue en infraestructura AWS

**Presupuesto Fase 1**: 100h/mes × 12 meses × €80/h = €96,000
**Horas consumidas**: 1,150h de 1,200h (95.8% de utilización)
**Estado**: Entregada y aceptada por RetailMax en Diciembre 2025

### Fase 2 — Crecimiento (Enero – Junio 2026) 🔄 EN CURSO

Entregables planificados:
1. **Dashboard de analytics** — Reportes de ventas, tráfico y conversión en tiempo real
2. **Reportes gerenciales** — Exportación a PDF/Excel, reportes programados por email
3. **Personalización de ofertas** — Motor de recomendaciones basado en historial de compra
4. **Sistema de descuentos** — Códigos de descuento por porcentaje (limitación técnica: no soporta descuento de monto fijo por modelo de datos de Stripe)

**Presupuesto Fase 2**: 120h/mes × 6 meses × €85/h = €61,200
**Horas consumidas a fecha**: 340h de 720h totales (47.2% del presupuesto consumido al 50% del tiempo)
**Burn rate**: En línea con lo planificado. Margen de 40h para contingencias.

### Fase 3 — Expansión (Julio – Diciembre 2026) 📋 PLANIFICADA

Entregables planificados (pendiente contratación formal):
- **App móvil nativa** iOS y Android (requiere contrato separado)
- **Sistema de push notifications** web y mobile
- **Programa de fidelización** con puntos y niveles
- **Multi-idioma** (español, catalán, inglés)

**Presupuesto estimado**: Por definir. Requiere nuevo contrato.
**Estado**: En negociación. Pedro Ruiz (Secture) preparando propuesta comercial.

---

## Exclusiones Explícitas del Contrato

Las siguientes funcionalidades están **explícitamente excluidas** del alcance contractual actual y requieren contratación independiente:

1. **Integraciones ERP** (SAP, Oracle, Microsoft Dynamics u otros sistemas de gestión empresarial). Cualquier integración con sistemas ERP requiere un proyecto independiente con análisis de viabilidad, desarrollo de conectores y testing de integración.

2. **App nativa iOS/Android**. El desarrollo móvil nativo requiere un contrato separado con presupuesto y equipo dedicado. No está incluido en ninguna fase del contrato actual.

3. **Marketplace multi-vendor**. La funcionalidad de marketplace con múltiples vendedores implica un rediseño fundamental de la arquitectura y modelo de negocio.

4. **Soporte 24/7**. El contrato actual cubre soporte L1/L2 en horario laboral (lunes a viernes, 9:00-18:00 CET). El soporte 24/7 requiere un contrato de SLA extendido.

5. **Migración de datos desde sistemas legacy**. La carga inicial de catálogo fue incluida en Fase 1, pero futuras migraciones masivas de datos no están cubiertas.

---

## Gestión de Cambios (Change Requests)

### Procedimiento
- Cualquier cambio o adición de funcionalidad que supere las **20 horas de desarrollo** requiere un **addendum contractual** firmado por ambas partes.
- Cambios menores (<20h) se gestionan dentro del presupuesto mensual con aprobación del PM de RetailMax.
- Los change requests deben documentarse con: descripción, justificación, estimación de horas, impacto en el roadmap, y riesgos.

### Change Requests Aprobados en Fase 2
| # | Descripción | Horas | Estado |
|---|-------------|-------|--------|
| CR-001 | Integración Google Analytics 4 | 15h | Aprobado, en desarrollo |
| CR-002 | Widget de chat (Intercom) | 8h | Aprobado, completado |

---

## Acuerdo de Nivel de Servicio (SLA)

### Disponibilidad
- **Uptime garantizado**: 99.5% mensual (excluye ventanas de mantenimiento programado)
- **Ventanas de mantenimiento**: Martes 02:00-04:00 CET (pre-acordadas)
- **Penalizaciones**: 5% descuento en factura mensual por cada 0.1% bajo el SLA

### Tiempos de Respuesta a Incidencias
| Prioridad | Descripción | Tiempo Respuesta | Tiempo Resolución |
|-----------|-------------|-----------------|-------------------|
| P1 - Crítica | Sistema caído, sin servicio | < 2 horas | < 8 horas |
| P2 - Alta | Funcionalidad core degradada | < 8 horas | < 24 horas |
| P3 - Media | Bug no bloqueante | < 24 horas | < 5 días laborables |
| P4 - Baja | Mejora cosmética | < 48 horas | Siguiente sprint |

### Horario de Soporte
- Lunes a viernes: 9:00 – 18:00 CET
- Guardias P1: Accesible por teléfono de emergencia (solo para caídas totales)

---

## Renovación y Terminación

- **Renovación automática** por períodos de 6 meses salvo notificación escrita con **60 días** de antelación antes del vencimiento
- Cualquiera de las partes puede resolver el contrato con 90 días de preaviso
- En caso de resolución: Secture entrega todo el código fuente, documentación y accesos
- Propiedad intelectual: Todo el código desarrollado es propiedad de RetailMax S.L.

---

## Métricas de Seguimiento del Proyecto

| Métrica | Objetivo | Actual (Mar 2026) |
|---------|----------|-------------------|
| Horas consumidas Fase 2 | ≤720h | 340h (47%) |
| Velocidad sprint | 80h/sprint | 78h/sprint |
| Bugs críticos abiertos | 0 | 1 (PaymentModule timeout) |
| Uptime último mes | ≥99.5% | 99.7% |
| Test coverage global | ≥70% | 62% |
| Satisfacción cliente (NPS) | ≥8 | 8.2 |
