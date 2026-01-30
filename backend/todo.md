- fix frontend as a result!
Problem: no limit or quality assessment on knowledge units.
Problem or enhancement: the question generated must not hallucinate and asks things non related to the knowledge unit.

como entra aquí el tema de Comet:

- Assess if answer is correct
- Assess if questions are relevant


# TBD

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

## Day 1 (28 January) [DONE]

Experimentation with opik -> Focus on KU Generation

## Day 2 (29 January) [DONE]

Add source claims to knowledge units (no estoy seguro de que aporte valor, pero sería bueno tenerlo para redondear el modelo, Y mejorar el prompt) [NOPE]

## Day 3 (30 January)

Arreglar hint de Socrates: Ahora mismo no puedo obtener la respuesta directamente [DONE]
Borrar cosas de la UI que no aportan nada [DONE]
Mejorar performance de parseo PDF (quizas imagen es muy pesada? puedo tambier usar asincronimso) [DONE]
Intentar mejorar la métrica de redundancy... --> Not a priority for demo! [NOPE]

Intentar crear una dashboard de learning plan para poder continuar con el estudio
Borrar cosas de la UI que no aportan nada (mantener dashboard, etc???)

## Day 4 (31 January)

Revisar calidad de knowledge units -> Not a priority for demo! [NOPE]
Intentar crear una dashboard de learning plan para poder continuar con el estudio
Borrar cosas de la UI que no aportan nada (mantener dashboard, etc???)

Intentar crear una dashboard de learning plan para poder continuar con el estudio
Borrar cosas de la UI que no aportan nada (mantener dashboard, etc???)

## Day 5 (1 February)

Intentar crear una dashboard de learning plan para poder continuar con el estudio

## Day 6 (2 February)

DEMO time!

## Day 7 (3 February)

README and documentation creation.

## Day 8 (4 February)

Demo video recording.

## Day 9 (5 February)

Slide deck creation.

## Day 10 (6 February)

Final review and polish.

## Day 11 (7 February)

Visual polish: dashboards, screenshots, metric names.

## Day 12 (8 February)

SUBMIT THE SOLUTION!


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


Add this?

🥇 1. Learning Plan Dashboard (HIGH impact, LOW complexity)

Why it matters

Makes your system feel like a product, not a demo

Judges instantly understand value

Minimum viable version

List learning plans

Show:

% mastery overall

Last study session

“Continue learning” button

Key message to judges

“You always resume exactly where you left off.”