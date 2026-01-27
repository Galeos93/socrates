- fix frontend as a result!
Problem: no limit or quality assessment on knowledge units.
Problem or enhancement: the question generated must not hallucinate and asks things non related to the knowledge unit.

como entra aquí el tema de Comet:

- Assess if answer is correct
- Assess if questions are relevant


# TBD

- Meter user feedback [ongoing]
- Meter experimentación de prompts
- Handle errors if learningplan not found
- Añadir source claims...
- Quitar morralla
    - La barra de arriba sirve para algo?
    - El icono de usuario sirve para algo?
- Borrar preguntas IGUALES a mano
- Hay preguntas muy parecidas, seguramente de un mismo knowledge unit, hay que ver por qué --> Importante
- Mejorar el "hint" de socrates a no ser que se le alimente con la respuesta correcta
- El parseo del PDF es tremendamente lento
- Revisar que tal son los knowledges generados
- Comprobar que la dificultad verdaderamente se ajusta con el mastery

# Plan

Phase 1 — Lock the Narrative (Days 1–2)

Freeze scope and define the one-sentence story

Clearly state why evaluation is hard and why Opik is essential

Define 4 evaluation surfaces:

OCR quality

KnowledgeUnit extraction

Question quality

Answer assessment

Document evaluation strategy in docs/opik_evaluation.md

Phase 2 — Opik Integration (Days 3–6) (Most Important)

Day 3

Add Opik tracing to all LLM steps

Capture prompts, inputs, outputs, metadata

Day 4

Upgrade all LLM judges to output structured float metrics

Log metrics consistently to Opik

Create dashboards per evaluation surface

Day 5

Run controlled prompt experiments (not user A/B tests)

Compare prompt variants on same inputs using judges

Show metric deltas in Opik experiments

Day 6

Add lightweight user feedback (question quality, assessment fairness)

Log feedback to Opik

Correlate user feedback with judge metrics

Phase 3 — Evidence & Storytelling (Days 7–9)

Day 7

Clean README and docs

Add architecture + evaluation diagrams

Explain tradeoffs and limitations honestly

Day 8

Record 4–6 min demo video

App flow

Opik traces

Dashboards

One experiment walkthrough

Day 9

Create ≤10-slide deck

Problem → system → evaluation → Opik → results

Emphasize measurement, not features

Phase 4 — Polish & Submit (Days 10–12)

Day 10

Review project as a judge

Cut anything unclear or redundant

Day 11

Visual polish: dashboards, screenshots, metric names

Day 12

Submit:

Repo

Live app

Video

Slides

Close with: “Evaluation is a first-class feature.”