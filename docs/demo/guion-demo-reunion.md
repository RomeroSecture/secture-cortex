# Guion de Demo — Reunión Simulada con Secture Cortex

**Duración total**: ~10 minutos
**Objetivo**: Demostrar cómo Secture Cortex genera insights en tiempo real durante una reunión con cliente, cruzando la transcripción con documentación del proyecto.

---

## Setup Previo

### Participantes
| Persona | Rol |
|---|---|
| **Antonio** | PM de RetailMax (el cliente) |
| **Gonzalo** | Tech Lead de Secture (la consultora) |

### Contexto de la reunión
Reunión mensual de seguimiento del proyecto "MiTienda" (plataforma e-commerce). Estamos en marzo 2026, en medio de la Fase 2 del proyecto. El cliente tiene varias preocupaciones y peticiones nuevas.

### Preparación del sistema
1. Crear proyecto "MiTienda - RetailMax" en Cortex
2. Subir los 5 documentos PDF de contexto:
   - `01-arquitectura-tecnica.pdf`
   - `02-contrato-alcance.pdf`
   - `03-acta-reunion-enero.pdf`
   - `04-servicios-secture.pdf`
   - `05-deuda-tecnica.pdf`
3. Verificar que todos están en estado "indexed" (verde)
4. Iniciar nueva reunión
5. Activar captura de audio

### Tips para la demo
- Hablar claro y pausado (Deepgram necesita audio limpio)
- Dejar ~5 segundos entre escenas para que el RAG procese
- Si un insight no aparece, continuar — el sistema prioriza calidad sobre cantidad
- El guion es una guía, no un script exacto — hablar natural

---

## ESCENA 1: Saludo y Estado del Proyecto (1 min)

> **Objetivo**: Warm-up. El sistema empieza a buffear transcripción. Establecer contexto.

**Gonzalo**:
> "Buenos días Antonio. Te cuento, el dashboard de analytics ya tiene los reportes básicos de ventas y tráfico funcionando. Estamos ahora cerrando la personalización de ofertas. Vamos bien de tiempos."

**Antonio**:
> "Vale, bien. Pero necesito ver números concretos pronto, porque internamente me están presionando con los resultados de Fase 2. ¿Vamos a llegar a todo lo que quedamos?"

**Qué debería pasar en Cortex**:
- La transcripción aparece en tiempo real en el panel izquierdo
- El conversation agent detecta el topic: "analytics, fase 2, presión interna"
- Posible insight de contexto: referencia al compromiso de Gonzalo (15 Feb) del acta de enero

---

## ESCENA 2: "Queremos Notificaciones Push" (1.5 min)

> **Objetivo**: Disparar ALERT + SCOPE. El cliente pide algo que está frozen.

**Antonio**:
> "Mira Gonzalo, hay algo urgente. Los usuarios no abren los emails de confirmación de pedido, estamos en un 15% de apertura. Eso es ridículo. Necesitamos push notifications ya, tanto en web como en el móvil."

**Gonzalo**:
> "Sí, es un problema real. Las tasas de apertura de email en e-commerce están cayendo en toda la industria. Déjame explicarte dónde estamos con el módulo de notificaciones porque hay contexto técnico importante..."

*(Pausa 5-10 segundos para que Cortex procese)*

**Insights esperados en el panel derecho**:

| Tipo | Agente | Contenido esperado |
|------|--------|-------------------|
| 🔴 ALERT | Tech Lead | NotificationModule está FROZEN hasta v3.0 (Q4 2026). No se puede modificar. |
| 🔵 SCOPE | PM | Push notifications pospuestas a Fase 3 según decisión del 15/01/2026 |
| 🟢 SUGGESTION | Dev | NotificationModule acoplado a SMTP. Requiere refactor (Channel Adapter pattern) antes de agregar push |
| 📋 Decision | Conversation | Cliente solicita cambio de canal de notificaciones |

---

## ESCENA 3: "Necesitamos App Móvil" (1.5 min)

> **Objetivo**: Disparar SCOPE (exclusión contractual) + COMMERCIAL (oportunidad).

**Antonio**:
> "Y ya que hablamos de móvil... nuestra competencia, ShopExpress, ya tiene app nativa. Estamos perdiendo clientes por esto. Necesitamos una app para iOS y Android como mínimo para el tercer trimestre."

**Gonzalo**:
> "Es un tema que tenemos identificado en el roadmap. Lo que pasa es que hay que tener en cuenta el alcance contractual actual para definir bien cómo lo abordamos..."

*(Pausa 5-10 segundos)*

**Insights esperados**:

| Tipo | Agente | Contenido esperado |
|------|--------|-------------------|
| 🔵 SCOPE | PM | App nativa iOS/Android es exclusión explícita del contrato actual. Requiere contrato separado. |
| 🔵 SCOPE | PM | Change request >20h necesita addendum contractual firmado |
| 💼 COMMERCIAL | Commercial | Oportunidad: Secture ofrece squads dedicados para desarrollo móvil |
| 📋 Commitment | Conversation | Deadline detectado: "mínimo para el tercer trimestre" |

---

## ESCENA 4: "Los Pagos Fallan" (1.5 min)

> **Objetivo**: Disparar ALERT de tech debt conocida. Problema real que el sistema ya tiene documentado.

**Antonio**:
> "Otra cosa que me preocupa mucho. Esta semana tuvimos varios reportes de clientes a los que les falló el pago. Algunos dicen que les cobró pero no les confirmó el pedido. Eso no puede pasar, Gonzalo."

**Gonzalo**:
> "¿Cuántos casos habéis detectado exactamente? Es algo que tenemos identificado en el backlog técnico, déjame darte contexto..."

*(Pausa 5-10 segundos)*

**Insights esperados**:

| Tipo | Agente | Contenido esperado |
|------|--------|-------------------|
| 🔴 ALERT | Tech Lead | Deuda técnica CRÍTICA: PaymentModule sin circuit breaker. Timeout 10s de Stripe sin retry automático. |
| 🟢 SUGGESTION | Dev | Se estima 2-3% de transacciones fallidas en picos. Solución: circuit breaker + idempotency key. Esfuerzo: 3-5 días |
| 🔵 SCOPE | PM | Fix de pagos es scope actual (P1), priorizado en sprint actual según acta 15/01 |
| 📋 Action Item | Conversation | "Investigar casos de cobro sin confirmación" |

---

## ESCENA 5: "Seguridad y GDPR" (1.5 min)

> **Objetivo**: Disparar ALERT de seguridad + COMMERCIAL (servicios de Secture).

**Antonio**:
> "Con todo lo que está pasando con hackeos y multas por datos, necesito que me digáis cómo estamos de seguridad. Sobre todo con los datos de pago de los clientes y el GDPR."

**Gonzalo**:
> "Buena pregunta. A nivel de pagos estamos bien porque Stripe gestiona los datos de tarjeta, los datos PCI nunca tocan nuestros servidores. Pero hay un par de cosas que debemos mejorar..."

*(Pausa 5-10 segundos)*

**Insights esperados**:

| Tipo | Agente | Contenido esperado |
|------|--------|-------------------|
| 🔴 ALERT | Tech Lead | JWT sin refresh tokens — riesgo de seguridad. Tokens de 24h como workaround (TD-002) |
| 💼 COMMERCIAL | Commercial | Secture ofrece auditoría de código, pentesting web/API y compliance GDPR/LOPD |
| 💼 COMMERCIAL | Commercial | SOC-as-a-Service 24/7 disponible para monitorización continua |
| 📋 Question | Conversation | Pregunta detectada: "¿cómo estamos de seguridad?" |

---

## ESCENA 6: "Integración con SAP" (1.5 min)

> **Objetivo**: Disparar SCOPE (exclusión) + COMMERCIAL (upsell data services).

**Antonio**:
> "Una última cosa importante. Estamos implementando SAP en las tiendas físicas y necesitamos que el e-commerce se conecte con SAP. El inventario tiene que estar sincronizado en tiempo real. No puede ser que un cliente compre online algo que ya se vendió en tienda."

**Gonzalo**:
> "Totalmente, la sincronización de inventario es fundamental para una estrategia omnichannel. Déjame contarte qué opciones tenemos..."

*(Pausa 5-10 segundos)*

**Insights esperados**:

| Tipo | Agente | Contenido esperado |
|------|--------|-------------------|
| 🔵 SCOPE | PM | Integraciones ERP (SAP) son exclusión explícita del contrato actual |
| 💼 COMMERCIAL | Commercial | Secture Data & Analytics: integración de datos, ML pipelines, análisis predictivo de inventario |
| 🟢 SUGGESTION | Dev | Alternativa dentro de scope: API batch de sincronización de stock con reconciliación periódica |
| 📋 Decision | Conversation | Decisión implícita: necesidad de inventario omnichannel |

---

## ESCENA 7: "Rate Limiting para Black Friday" (1 min)

> **Objetivo**: Disparar ALERT por conflicto con decisión histórica documentada.

**Antonio**:
> "Ah, y para Black Friday vamos a necesitar mucha más capacidad. El año pasado la web se cayó y perdimos ventas. Necesitamos aguantar mínimo 500 peticiones por segundo."

**Gonzalo**:
> "Sí, Black Friday es el pico crítico del año. Hay que planificarlo bien porque implica escalar varias capas de la infraestructura..."

*(Pausa 5-10 segundos)*

**Insights esperados**:

| Tipo | Agente | Contenido esperado |
|------|--------|-------------------|
| 🔴 ALERT | Tech Lead | Rate limiting fijado en 100 req/s por decisión del 15/01/2026. Cambio evaluable Q3. Aumentar requiere escalar DB, Redis y ECS. |
| 🔵 SCOPE | PM | Cambio de 100 a 500 req/s requiere análisis de impacto en toda la infraestructura |
| 📋 Commitment | Conversation | Compromiso del cliente: "mínimo 500 peticiones por segundo" |

---

## CIERRE (30 segundos)

> **Objetivo**: Generar action items y decision tracking.

**Antonio**:
> "Vale, entonces yo me encargo de priorizar internamente lo de la app móvil y la integración con SAP. Y quedamos en que vosotros revisáis lo de los pagos esta semana, ¿correcto?"

**Gonzalo**:
> "Hecho. Lo de pagos lo priorizamos en el sprint de esta semana. Y te preparo una propuesta para la app móvil y la auditoría de seguridad."

*(El sistema debería detectar los action items y commitments del cierre)*

**Insights esperados**:

| Tipo | Agente | Contenido esperado |
|------|--------|-------------------|
| 📋 Action Item | Conversation | Antonio: priorizar app móvil y SAP internamente |
| 📋 Action Item | Conversation | Gonzalo: revisar pagos esta semana + propuesta app y auditoría |
| 📋 Decision | Conversation | Decisión: priorizar fix de pagos esta semana |

---

## Después de la Demo

Al finalizar la reunión (botón "Terminar reunión"), el sistema genera automáticamente:
1. **Acta de reunión** (minutes) — resumen, decisiones, action items
2. **Handoff** — paquete de contexto para la próxima reunión
3. **Sprint Impact** — nuevas peticiones, esfuerzo estimado, stories afectadas
4. **Email de seguimiento** — borrador profesional para enviar al cliente
5. **Briefing interno** — resumen para el equipo que no estuvo en la reunión
6. **Retrospectiva** — métricas de la reunión (duración, ratio scope, insights generados)

Estos documentos se pueden mostrar como cierre de la demo para demostrar el valor post-meeting.

---

## Checklist Pre-Demo

- [ ] Docker Compose levantado y healthy (db, backend, frontend)
- [ ] API keys configuradas (Deepgram, Groq, Jina)
- [ ] Usuario creado con rol tech_lead
- [ ] Proyecto "MiTienda - RetailMax" creado
- [ ] 5 PDFs subidos y en estado "indexed"
- [ ] Audio del navegador habilitado (micrófono)
- [ ] Deepgram API con créditos disponibles
- [ ] Dos speakers diferentes (para diarización)
- [ ] Pantalla en modo oscuro para mejor visibilidad
- [ ] Red estable (WebSocket necesita conexión continua)
