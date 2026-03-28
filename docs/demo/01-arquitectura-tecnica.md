# Arquitectura Técnica — MiTienda E-Commerce Platform

**Proyecto**: MiTienda — Plataforma E-Commerce para RetailMax S.L.
**Versión**: 2.1.0 (Fase 2)
**Fecha**: Marzo 2026
**Autor**: Gonzalo López, Tech Lead — Secture

---

## Stack Tecnológico

### Frontend
- **React 18** con **Next.js 14** (App Router, Server Components)
- **Tailwind CSS v3** para estilos
- **Zustand** para estado global (carrito, sesión)
- **React Query** para cache de datos del servidor
- Hosting: AWS Amplify (CDN + SSR)

### Backend
- **Node.js 20 LTS** con **Express 4.18**
- Monolito modular (6 módulos, ver sección Módulos)
- API REST con documentación OpenAPI 3.0
- **TypeScript** strict mode en todo el backend
- Hosting: AWS ECS (containers Docker)

### Base de Datos
- **PostgreSQL 15** en AWS RDS (db.r6g.large)
- **Redis 7** en AWS ElastiCache (cache de sesiones y catálogo)
- **RabbitMQ 3.12** para colas de procesamiento asíncrono

### Infraestructura
- AWS ECS Fargate (containers sin servidor)
- AWS RDS PostgreSQL (multi-AZ para alta disponibilidad)
- AWS ElastiCache Redis (cluster mode)
- AWS S3 (assets estáticos, imágenes de productos)
- AWS CloudFront (CDN)
- Kong API Gateway (rate limiting, auth, logging)

---

## Módulos del Sistema

### 1. AuthModule
Gestión de autenticación y autorización.
- JWT con bcrypt para hashing de contraseñas
- Roles: admin, staff, customer
- Middleware de autenticación en todas las rutas protegidas
- FIXME: JWT sin refresh tokens. Las sesiones expiran cada 2 horas y fuerzan re-login al usuario. Se usa un workaround temporal con tokens de larga duración (24h) que representa un riesgo de seguridad.

### 2. CatalogModule
Gestión del catálogo de productos.
- CRUD de productos con categorías jerárquicas (hasta 3 niveles)
- Filtros por precio, categoría, marca, valoración
- Búsqueda de productos: actualmente usa **SQL LIKE** queries
- Pendiente migración a Elasticsearch para búsqueda full-text y faceted search
- Número actual de productos: 8,500 SKUs activos
- HACK: Cache en memoria con TTL manual de 5 minutos para listados. Sin integración con Redis. Performance degrada significativamente con más de 10,000 productos por queries N+1 en la relación productos-categorías.

### 3. OrderModule
Procesamiento de pedidos y checkout.
- Estados del pedido: pending → paid → processing → shipped → delivered → completed
- También: cancelled, refunded, failed
- Carrito persistido en Redis (TTL 7 días)
- Checkout en 3 pasos: dirección → pago → confirmación
- **Dependencia crítica**: OrderModule depende de PaymentModule para procesar pagos y de NotificationModule para enviar confirmaciones. Esta cadena de dependencias (OrderModule → PaymentModule → NotificationModule) es el flujo más crítico del sistema.

### 4. PaymentModule
Procesamiento de pagos con Stripe.
- **Stripe SDK v12** con Stripe Elements en frontend
- Métodos soportados: tarjeta crédito/débito, Bizum (pendiente)
- Timeout de conexión a Stripe: **10 segundos**
- TODO: Implementar circuit breaker en la conexión con Stripe SDK. Actualmente no hay retry automático cuando Stripe falla o responde con timeout. Esto causa pérdida de transacciones en picos de tráfico estimada en un 2-3% de intentos de pago. El OrderModule queda en estado "pending" y el usuario no recibe confirmación aunque en algunos casos Stripe sí procesa el cobro.
- Webhooks de Stripe configurados para payment_intent.succeeded y payment_intent.failed
- Impacto de la deuda técnica: afecta directamente a OrderModule y NotificationModule

### 5. NotificationModule — FROZEN
**ESTADO: FROZEN hasta v3.0 (Q4 2026). No se permite ninguna modificación.**

Módulo de notificaciones actualmente acoplado a email/SMTP.
- Usa nodemailer con servidor SMTP de Amazon SES
- Tipos de notificación: confirmación de pedido, envío, entrega, recuperación de carrito
- Templates HTML hardcodeados en el código
- **No soporta push notifications** (ni web push ni mobile push)
- **No soporta SMS**
- El módulo está acoplado directamente al protocolo SMTP y no tiene abstracción de canales
- Para agregar push o SMS requiere un refactor mayor: crear una capa de abstracción de canales (Channel Adapter pattern) y migrar los templates a un sistema de plantillas dinámico
- Decisión de congelar tomada en reunión del 15 de enero de 2026 por el equipo técnico

### 6. AnalyticsModule
Reportes y métricas del negocio.
- FIXME: Scripts SQL manuales ejecutados por cron jobs cada 24 horas
- Sin pipeline ETL automatizado
- Los datos tienen hasta 24 horas de retraso
- Reportes disponibles: ventas diarias, productos más vendidos, tasa de conversión, valor medio de pedido
- Dashboard en desarrollo (Fase 2): React + Recharts
- Test coverage: 12% — el más bajo de todos los módulos
- Pendiente integración con Google Analytics 4 (decisión reunión enero 2026)

---

## API Gateway — Kong

- Rate limiting global: **100 peticiones por segundo** (decisión firme tomada el 15 de enero de 2026)
- Esta configuración es evaluable en Q3 2026 si las métricas de tráfico lo justifican
- Autenticación: JWT validation en Kong
- Logging: todos los requests logueados en CloudWatch
- CORS configurado para dominios de producción

---

## Decisiones Arquitectónicas (ADRs)

### ADR-003: Monolito Modular
Se decidió mantener la arquitectura como monolito modular en lugar de migrar a microservicios. Motivo: el equipo es de 4 personas y la complejidad operativa de microservicios no se justifica hasta alcanzar un volumen de 50,000 pedidos/mes. Volumen actual: 12,000 pedidos/mes.

### ADR-005: Stripe como Procesador de Pagos
Se eligió Stripe por su cobertura en España, soporte para Bizum (pendiente activación), y porque gestiona datos PCI-DSS sin que los datos de tarjeta toquen nuestros servidores.

### ADR-007: No Migrar a Microservicios
Migración a microservicios **NO aprobada**. Se mantiene monolito modular hasta v3.0 como mínimo. El coste de refactoring, la complejidad de orquestación y la necesidad de observabilidad distribuida no se justifican con el volumen actual.

### ADR-009: Rate Limiting Fijo
El rate limiting se fija en 100 req/s como medida de protección. Cualquier cambio requiere análisis de capacidad de la infraestructura (RDS, ElastiCache, ECS scaling policies). Evaluable en Q3 2026.

---

## Diagrama de Dependencias entre Módulos

```
AuthModule ←── [todos los módulos dependen de auth]
     │
CatalogModule ──→ (independiente, solo lee de DB)
     │
OrderModule ──→ PaymentModule ──→ NotificationModule
     │                               (FROZEN)
     └──→ CatalogModule (consulta stock)

AnalyticsModule ──→ (lee de todas las tablas, solo lectura)
```

La cadena OrderModule → PaymentModule → NotificationModule es el flujo crítico del sistema. Un fallo en cualquier eslabón afecta la experiencia de compra del usuario final.
