# Acta de Reunión — Seguimiento Mensual Proyecto MiTienda

**Fecha**: 15 de enero de 2026
**Hora**: 10:00 – 11:15 CET
**Lugar**: Videollamada (Google Meet)
**Referencia**: MiTienda-MEET-2026-01

---

## Asistentes

| Nombre | Rol | Empresa |
|--------|-----|---------|
| Gonzalo López | Tech Lead | Secture |
| Pedro García | Director Comercial | Secture |
| Antonio Romero | Project Manager | RetailMax |
| María Torres | CTO | RetailMax |

---

## Agenda

1. Estado de la Fase 2
2. Revisión de incidencias abiertas
3. Planificación de funcionalidades pendientes
4. Discusión sobre Fase 3
5. Varios

---

## Resumen de Discusión

### 1. Estado de la Fase 2
Gonzalo presentó el avance del primer mes de la Fase 2. Se han completado los cimientos del dashboard de analytics con los reportes básicos de ventas diarias y tráfico. La personalización de ofertas está en fase de diseño.

Antonio preguntó si el ritmo actual permite completar todos los entregables de la Fase 2 a tiempo. Gonzalo confirmó que el burn rate está en línea: 110 horas consumidas de un presupuesto de 120h/mes, con margen para contingencias.

### 2. Revisión de Incidencias
María Torres mencionó que algunos clientes finales han reportado problemas con la confirmación de pedidos. Gonzalo explicó que está relacionado con el timeout del PaymentModule contra Stripe y que es un tema de deuda técnica conocido que requiere implementar un circuit breaker. Se acordó priorizar este fix en el sprint actual.

### 3. Discusión sobre Push Notifications
Antonio solicitó que se implementen push notifications lo antes posible porque las tasas de apertura de emails de confirmación son muy bajas (solo 15%). María apoyó la solicitud indicando que la competencia (ShopExpress) ya ofrece notificaciones push.

Tras análisis técnico, Gonzalo explicó que el NotificationModule está actualmente acoplado al protocolo SMTP/email y que agregar push notifications requiere un refactor significativo del módulo: crear una capa de abstracción de canales, implementar Web Push API y configurar un servicio de push (Firebase Cloud Messaging o similar).

**Decisión**: Las push notifications se posponen a la **Fase 3 (Q4 2026)**. El NotificationModule queda **FROZEN** — no se permite ninguna modificación hasta v3.0 para evitar introducir regresiones en el flujo crítico de confirmación de pedidos. Esta decisión fue consensuada por todo el equipo técnico.

### 4. Rate Limiting
María preguntó si es posible aumentar el rate limiting actual de 100 peticiones por segundo, anticipando el crecimiento del tráfico.

**Decisión**: El rate limiting se mantiene en **100 req/s** como medida de protección. Aumentarlo requiere un análisis de capacidad de toda la infraestructura (RDS, ElastiCache, ECS scaling policies, Kong). Se evaluará en **Q3 2026** si las métricas de tráfico lo justifican. Gonzalo advirtió que subir el rate limiting sin escalar la base de datos podría causar degradación en cascada.

### 5. Sistema de Descuentos
Antonio presentó la necesidad de un sistema de descuentos para campañas comerciales. Gonzalo explicó las limitaciones técnicas.

**Decisión**: El sistema de descuentos soportará solo **descuentos por porcentaje** (10%, 20%, etc.), NO descuentos de monto fijo (€5, €10). Motivo: el modelo de datos actual de Stripe Coupons está configurado para porcentajes y cambiar a monto fijo requiere migrar los price objects, lo cual afecta a los cálculos de impuestos. Se implementará en el sprint 3 de Fase 2.

### 6. Analytics
Se discutió qué plataforma de analytics usar.

**Decisión**: Se usará **Google Analytics 4** para métricas de comportamiento de usuario, no se desarrollará una plataforma de analytics propia. Motivo: costes de desarrollo y mantenimiento. El dashboard interno se limitará a métricas de negocio (ventas, conversión, AOV).

### 7. API Pública para Partners
Antonio mencionó que RetailMax tiene interés futuro en abrir una API para que partners (marketplaces, comparadores de precios) accedan al catálogo.

**Pendiente**: Definir SLA para la API pública, mecanismo de autenticación (OAuth2), y límites de uso. Se revisará cuando haya un partner confirmado.

---

## Decisiones Tomadas

| # | Decisión | Responsable | Fecha |
|---|----------|-------------|-------|
| D1 | Push notifications pospuestas a Fase 3 (Q4 2026) | Gonzalo López | 15/01/2026 |
| D2 | NotificationModule FROZEN hasta v3.0 | Gonzalo López | 15/01/2026 |
| D3 | Rate limiting se mantiene en 100 req/s, evaluable Q3 | Gonzalo López | 15/01/2026 |
| D4 | Descuentos solo por porcentaje, no monto fijo | Gonzalo López | 15/01/2026 |
| D5 | Analytics con Google Analytics 4, no plataforma propia | Antonio Romero | 15/01/2026 |

---

## Compromisos Adquiridos

| # | Compromiso | Responsable | Fecha límite |
|---|-----------|-------------|--------------|
| C1 | No habrá cambios en catálogo base hasta cerrar Fase 2 | Antonio Romero (RetailMax) | Jun 2026 |
| C2 | Entrega del primer dashboard de analytics | Gonzalo López (Secture) | 15 Feb 2026 |
| C3 | Propuesta comercial para Fase 3 | Pedro García (Secture) | Mar 2026 |
| C4 | Priorizar fix de timeout en PaymentModule | Gonzalo López (Secture) | Sprint actual |

---

## Preguntas Abiertas

1. ¿RetailMax necesita soporte multi-idioma en Q2 o puede esperar a Fase 3?
2. ¿Qué proveedor de SMS consideran para las notificaciones de Fase 3?
3. ¿Hay un partner confirmado para la API pública?

---

## Próxima Reunión

**Fecha propuesta**: 15 de marzo de 2026, 10:00 CET
**Agenda tentativa**: Estado dashboard analytics, revisión fix pagos, discusión presupuesto Fase 3
