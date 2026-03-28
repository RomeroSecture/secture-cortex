import { z } from "zod";

export const productVideoSchema = z.object({
  hookText: z
    .string()
    .default("¿Cuántas veces has dicho 'déjame mirarlo y te digo'?"),
  tagline: z
    .string()
    .default("El copiloto que escucha, cruza y responde"),
  demoTranscription: z
    .array(
      z.object({
        speaker: z.string(),
        text: z.string(),
        speakerIndex: z.number(),
      })
    )
    .default([
      {
        speaker: "Cliente",
        text: "Necesitamos que el módulo de notificaciones también envíe por WhatsApp.",
        speakerIndex: 2,
      },
      {
        speaker: "Laura",
        text: "Entendido. Déjame ver cómo impacta eso al NotificationDispatcher actual.",
        speakerIndex: 1,
      },
      {
        speaker: "Cliente",
        text: "Y que sea para la semana que viene, ¿no?",
        speakerIndex: 2,
      },
    ]),
  demoInsights: z
    .array(
      z.object({
        type: z.enum(["alert", "scope", "suggestion"]),
        title: z.string(),
        body: z.string(),
        confidence: z.number(),
      })
    )
    .default([
      {
        type: "alert",
        title: "Conflicto detectado",
        body: "NotificationDispatcher requiere migración de API v2 → v3 antes de añadir canal WhatsApp.",
        confidence: 87,
      },
      {
        type: "scope",
        title: "Fuera de alcance",
        body: "Integración WhatsApp no está en el sprint actual. Requiere presupuesto adicional.",
        confidence: 92,
      },
      {
        type: "suggestion",
        title: "Alternativa propuesta",
        body: "Canal SMS ya implementado. Activar como solución interim en 2 días.",
        confidence: 78,
      },
    ]),
  features: z
    .array(z.object({ title: z.string(), subtitle: z.string(), accent: z.string() }))
    .default([
      { title: "Transcripción Live", subtitle: "Deepgram Nova-3 con diarización de speakers", accent: "#2ec4a2" },
      { title: "Scope Guardian", subtitle: "Clasifica in-scope / planned / out-of-scope", accent: "#d9a840" },
      { title: "RAG Multi-Agente", subtitle: "4 especialistas analizan cada fragmento", accent: "#a07ed6" },
      { title: "Memoria Acumulativa", subtitle: "Meetings pasados alimentan el contexto", accent: "#3ab897" },
    ]),
  statLatency: z.string().default("<2s"),
  statInsightTime: z.string().default("<10s"),
  statAccuracy: z.string().default("95%"),
  ctaText: z.string().default("Cortex"),
  ctaUrl: z.string().default("secture.com"),
});

export type ProductVideoProps = z.infer<typeof productVideoSchema>;
