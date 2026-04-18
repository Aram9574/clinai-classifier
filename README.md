---
title: ClinAI Classifier - EU AI Act para IA en Salud
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8501
pinned: true
license: mit
tags:
  - healthcare
  - clinical-ai
  - eu-ai-act
  - compliance
  - medical
  - regulation
  - cdss
  - samd
  - healthtech
  - medtech
---

<div align="center">

# 🏥 ClinAI Classifier

### Clasifica tu sistema de IA sanitario bajo el EU AI Act en segundos

*Construido por un médico. Para equipos que construyen IA en salud.*

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-FF4B4B.svg)](https://streamlit.io/)
[![Claude API](https://img.shields.io/badge/Claude-sonnet--4--5-8A2BE2.svg)](https://www.anthropic.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

**[🚀 Pruébalo en vivo →](https://huggingface.co/spaces/aram1585/clinai-classifier)**

</div>

---

## El problema que resuelve

El EU AI Act lleva meses en boca de todo el mundo en HealthTech.

Pero la mayoría de los análisis tienen el mismo problema: los escribe alguien que conoce la regulación pero nunca ha estado en un servicio de urgencias. O alguien que ha hecho guardias, pero no ha leído el reglamento.

El resultado es divulgación correcta pero inútil para quien tiene que tomar decisiones reales.

Cada semana me encuentro con equipos que están construyendo herramientas de IA que acabarán sentadas entre un paciente y una decisión médica. La mayoría no sabe si su predictor de sepsis es un sistema de alto riesgo bajo el Anexo III. No sabe si su chatbot para pacientes necesita una notificación de transparencia del Artículo 50. No sabe si su herramienta de puntuación de elegibilidad cruza la línea de prohibición del Artículo 5.

No es falta de voluntad. Es falta de herramientas accesibles con criterio clínico real.

**ClinAI Classifier cierra esa brecha.**

---

## Qué hace

Describe tu sistema de IA sanitario en lenguaje natural. En menos de 10 segundos obtienes:

```
✅  Nivel de riesgo EU AI Act  →  PROHIBITED / HIGH_RISK / LIMITED_RISK / MINIMAL_RISK
✅  Categorías del Anexo III aplicables
✅  Flags de prácticas prohibidas (Artículo 5)
✅  Base legal con artículos específicos citados
✅  Lista de requisitos de cumplimiento por prioridad
✅  Flag SaMD (Software as a Medical Device)
✅  Informe PDF descargable listo para auditoría
```

---

## Ejemplos reales

| Sistema de IA | Clasificación | Base legal |
|---|---|---|
| Predictor de reingreso a UCI a 30 días usado en el alta | 🔴 `HIGH_RISK` + SaMD | Art. 6, Anexo III §5; MDR |
| Resumen NLP de notas clínicas anonimizadas para investigación | 🟡 `LIMITED_RISK` | Art. 50 transparencia |
| Puntuación de elegibilidad para prestaciones sanitarias por autoridad pública | ⛔ `PROHIBITED` | Art. 5(1)(c) |
| Dashboard de wearable mostrando pasos y sueño al usuario | 🟢 `MINIMAL_RISK` | Art. 95 código voluntario |
| Sistema de recomendación de tratamiento oncológico para oncólogos | 🔴 `HIGH_RISK` + SaMD | Art. 6, Anexo III §5; MDR/IVDR |

---

## Cómo funciona por dentro

El clasificador usa un **pipeline de dos etapas** diseñado para ser conservador por defecto.

```
Descripción del sistema
        │
        ▼
┌───────────────────┐
│  Agente Claude    │  ← System prompt de experto regulatorio + clínico
│  (clasificación   │    Devuelve: riesgo, Anexo III, Art. 5, base legal,
│   estructurada)   │    confianza, notas clínicas, flag SaMD
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Motor de reglas  │  ← Validación estática contra JSON regulatorios curados
│  (validación)     │    Aplica invariante: NUNCA degrada la clasificación
└───────────────────┘
        │
        ▼
Clasificación final + checklist + PDF
```

**Invariante de no-degradación:** el motor de reglas solo puede escalar una clasificación hacia mayor riesgo, nunca reducirla. Si el agente dice `LIMITED_RISK` y las reglas detectan un patrón de alto riesgo, el resultado final es `HIGH_RISK`. Al revés nunca ocurre. En regulación sanitaria, errar hacia el lado conservador no es opcional.

---

## Stack

| Capa | Tecnología |
|---|---|
| UI | Streamlit 1.32 |
| API | FastAPI + Python 3.11 |
| IA | Claude claude-sonnet-4-5 (Anthropic) |
| Validación | Motor de reglas + JSON EU AI Act curados |
| PDF | WeasyPrint + Jinja2 |
| Deploy | Docker · Hugging Face Spaces |
| Tests | pytest |

---

## Instalación local

```bash
# Clonar
git clone https://github.com/aramzakzuk/clinai-classifier.git
cd clinai-classifier

# Instalar dependencias
pip install -r requirements.txt

# Configurar entorno
cp .env.example .env
# Añade tu ANTHROPIC_API_KEY en .env
```

```bash
# Terminal 1 — Backend
python -m backend.main

# Terminal 2 — UI
streamlit run app/main.py
```

Backend en `http://localhost:8000` · UI en `http://localhost:8501`

---

## Estructura del proyecto

```
clinai-classifier/
├── app/                        # UI Streamlit
│   ├── main.py
│   ├── components/             # Tarjetas de riesgo, checklist, PDF export
│   ├── pages/                  # Clasificador, About, Guía regulatoria
│   └── utils/
├── backend/                    # API FastAPI
│   ├── main.py
│   ├── data/                   # JSON regulatorios EU AI Act curados
│   │   ├── eu_ai_act_article_5.json
│   │   ├── eu_ai_act_annex_iii.json
│   │   └── compliance_checklists.json
│   ├── models/                 # Schemas Pydantic
│   ├── routers/                # Endpoints: /classify /report /health
│   ├── services/               # Agente Claude, motor de reglas, PDF
│   └── tests/
├── docs/
│   ├── METHODOLOGY.md
│   ├── LIMITATIONS.md
│   └── EXAMPLES.md
├── templates/                  # Plantillas PDF
├── REGULATORY_REFERENCE.md
└── README.md
```

---

## Tests

```bash
pytest backend/tests/
```

La suite cubre: motor de reglas (escalado, carveout médico, invariante de no-degradación), endpoint de clasificación y generador PDF.

---

## Base regulatoria

Todas las clasificaciones están fundamentadas en el texto publicado del [Reglamento (UE) 2024/1689 — EU AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj).

Mapeado de referencia rápida de artículos relevantes para salud en [`REGULATORY_REFERENCE.md`](./REGULATORY_REFERENCE.md).

---

## Limitaciones

ClinAI Classifier es una herramienta de apoyo a la decisión. **No es asesoramiento jurídico.**

No reemplaza a un Organismo Notificado ni a un profesional regulatorio cualificado. Las salidas del modelo pueden ser inconsistentes. El clasificador no cubre obligaciones GPAI (Art. 51+) ni evalúa conformidad MDR/IVDR en profundidad. Todos los resultados requieren revisión humana antes de cualquier acción de cumplimiento.

Declaración completa en [`docs/LIMITATIONS.md`](./docs/LIMITATIONS.md).

---

## Contribuciones

Las contribuciones son bienvenidas, especialmente de clínicos, profesionales regulatorios e ingenieros que trabajan en SaMD. Abre un issue antes de enviar cambios significativos.

Son particularmente valiosos: casos de prueba basados en despliegues reales, refinamientos a los JSON regulatorios y correcciones de clasificaciones incorrectas.

---

## Autor

**Aram Zakzuk, MD**
Clinical AI Specialist · Health Informatics · HealthTech Consultant

`CDSS` `SaMD` `EU AI Act` `MDR` `Machine Learning aplicado a medicina`

[![LinkedIn](https://img.shields.io/badge/LinkedIn-aramzakzuk-0077B5?logo=linkedin)](https://linkedin.com/in/aramzakzuk)
[![Web](https://img.shields.io/badge/Web-alejandrozakzuk.com-000000?logo=safari)](https://alejandrozakzuk.com)

---

## Licencia

MIT — ver [`LICENSE`](./LICENSE)
