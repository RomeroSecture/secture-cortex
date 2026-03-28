import React from "react";
import { Composition } from "remotion";
import { ProductVideo } from "./components/ProductVideo";
import { productVideoSchema } from "./types";

export const Root: React.FC = () => {
  return (
    <>
      <Composition
        id="ProductVideo"
        component={ProductVideo}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
        schema={productVideoSchema}
        defaultProps={{
          hookText: "¿Cuántas veces has dicho 'déjame mirarlo y te digo'?",
          tagline: "El copiloto que escucha, cruza y responde",
          demoTranscription: [
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
          ],
          demoInsights: [
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
          ],
          features: [
            { title: "Transcripción Live", subtitle: "Deepgram Nova-3 con diarización de speakers", accent: "#2ec4a2" },
            { title: "Scope Guardian", subtitle: "Clasifica in-scope / planned / out-of-scope", accent: "#d9a840" },
            { title: "RAG Multi-Agente", subtitle: "4 especialistas analizan cada fragmento", accent: "#a07ed6" },
            { title: "Memoria Acumulativa", subtitle: "Meetings pasados alimentan el contexto", accent: "#3ab897" },
          ],
          statLatency: "<2s",
          statInsightTime: "<10s",
          statAccuracy: "95%",
          ctaText: "Cortex",
          ctaUrl: "secture.com",
        }}
      />
    </>
  );
};
