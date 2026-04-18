"""Minimal i18n helper for the ClinAI Classifier UI.

Usage:
    from app.utils.i18n import t, language_selector

    lang = language_selector()   # renders sidebar selector, returns "en" | "es"
    st.title(t("classifier.title"))

Translations live in a single nested dict keyed by dotted paths. If a key
is missing for the selected language, the English fallback is returned.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES: dict[str, str] = {"en": "English", "es": "Español"}

TRANSLATIONS: dict[str, dict[str, Any]] = {
    "en": {
        "app": {
            "title": "ClinAI Classifier",
            "subtitle": "EU AI Act for Healthcare AI",
            "author_byline": "by Aram Zakzuk, MD | Clinical AI Specialist",
            "language_label": "Language",
            "loading_backend": "Starting classification backend…",
            "backend_timeout": "Backend did not become ready in time.",
            "mode_label": "Mode",
            "mode_demo": "Demo (pre-computed)",
            "mode_byok": "Classify my own system",
            "mode_demo_help": "Explore the tool with curated examples — no API key needed.",
            "mode_byok_help": "Paste your Anthropic API key to classify any AI system.",
            "api_key_label": "Anthropic API key",
            "api_key_placeholder": "sk-ant-…",
            "api_key_help": "Get one at console.anthropic.com. Your key is sent once per classification and never stored.",
            "api_key_missing": "Add your Anthropic API key in the sidebar to run a custom classification.",
            "privacy_note": "Privacy: your key is used for a single call to Claude and is discarded. Not logged, not persisted.",
        },
        "demo": {
            "title": "Explore curated examples",
            "intro": "Pick any example below to see its full EU AI Act classification — risk level, legal basis, compliance checklist and PDF audit report. All results are pre-computed, no API key needed.",
            "run_button": "View classification",
            "selected_example": "Selected example",
            "cta_byok_header": "Want to classify your own system?",
            "cta_byok_body": "Switch the sidebar mode to '{mode}' and paste your Anthropic API key.",
        },
        "classifier": {
            "title": "Classify an AI system under the EU AI Act",
            "intro": "Describe your AI system and obtain its EU AI Act risk classification with legal basis, compliance checklist and a downloadable audit report.",
            "load_example": "Load an example",
            "example_placeholder": "— select an example —",
            "system_name": "System name",
            "description": "Description",
            "description_help": "Between 50 and 3000 characters. Describe what the system does, its clinical context, and intended users.",
            "intended_purpose": "Intended purpose",
            "data_inputs": "Data inputs",
            "data_inputs_help": "Select all that apply. You can also type custom values.",
            "outputs_produced": "Outputs produced (comma-separated)",
            "deployment_context": "Deployment context",
            "affects_clinical_decision": "Affects clinical decisions",
            "submit": "Classify",
            "submitting": "Analysing against EU AI Act provisions…",
            "result_header": "Classification result",
            "empty_prompt": "Fill in the form and press Classify to see the result.",
            "error_title": "Classification error",
        },
        "card": {
            "risk_level": "Risk level",
            "confidence": "Confidence",
            "samd_flag": "SaMD",
            "conformity_assessment": "Conformity assessment",
            "notified_body": "Notified body",
            "yes": "Yes",
            "no": "No",
            "annex_iii": "Annex III categories",
            "article_5": "Article 5 prohibitions triggered",
            "legal_basis": "Legal basis",
            "clinical_notes": "Clinical notes (physician commentary)",
            "none": "None",
        },
        "checklist": {
            "title": "Compliance checklist",
            "mandatory": "Mandatory",
            "recommended": "Recommended",
            "conditional": "Conditional",
            "article": "Article",
            "requirement": "Requirement",
            "priority": "Priority",
            "deadline": "Deadline",
            "empty": "No requirements attached.",
        },
        "pdf": {
            "generate": "Generate PDF report",
            "download": "Download PDF",
            "generating": "Generating audit report…",
            "ready": "Report ready. Click below to download.",
            "error": "Could not generate PDF report.",
        },
        "about": {
            "title": "About & methodology",
            "what_is_act_header": "What is the EU AI Act",
            "what_is_act_body": "Regulation (EU) 2024/1689 sets the first horizontal legal framework for AI in the Union. For healthcare, it sits on top of MDR/IVDR obligations and brings specific requirements around risk management, transparency, human oversight and post-market monitoring.",
            "methodology_header": "Methodology",
            "methodology_body": "Two-stage classification: (1) a Claude-based regulatory agent produces a structured output grounded on the Act; (2) a static rules engine validates the output and, when in doubt, escalates the risk level — it never downgrades.",
            "limitations_header": "Limitations",
            "limitations_body": "This tool does not provide legal advice and is not a conformity assessment. It is an open-source aid for HealthTech teams to surface regulatory context early.",
            "author_header": "Author",
            "author_body": "Aram Zakzuk, MD — Clinical AI Specialist | Health Informatics | HealthTech Consultant.",
        },
        "regulatory": {
            "title": "EU AI Act — Regulatory reference",
            "search": "Search articles or keywords",
            "annex_header": "Annex III — High-risk categories",
            "article5_header": "Article 5 — Prohibited practices",
            "source": "Source",
            "no_match": "No entries match your search.",
        },
    },
    "es": {
        "app": {
            "title": "ClinAI Classifier",
            "subtitle": "Reglamento Europeo de IA para sistemas sanitarios",
            "author_byline": "por Aram Zakzuk, MD | Especialista en IA clínica",
            "language_label": "Idioma",
            "loading_backend": "Iniciando el motor de clasificación…",
            "backend_timeout": "El backend no respondió a tiempo.",
            "mode_label": "Modo",
            "mode_demo": "Demo (precalculado)",
            "mode_byok": "Clasificar mi propio sistema",
            "mode_demo_help": "Explora la herramienta con ejemplos curados — sin clave API.",
            "mode_byok_help": "Pega tu clave de Anthropic para clasificar cualquier sistema de IA.",
            "api_key_label": "Clave API de Anthropic",
            "api_key_placeholder": "sk-ant-…",
            "api_key_help": "Consíguela en console.anthropic.com. Tu clave se envía una vez por clasificación y nunca se almacena.",
            "api_key_missing": "Añade tu clave API de Anthropic en la barra lateral para hacer una clasificación personalizada.",
            "privacy_note": "Privacidad: tu clave se usa en una única llamada a Claude y luego se descarta. No se registra ni se persiste.",
        },
        "demo": {
            "title": "Explora ejemplos curados",
            "intro": "Elige cualquier ejemplo para ver su clasificación completa bajo el EU AI Act — nivel de riesgo, base legal, checklist de cumplimiento e informe PDF. Todos los resultados están precalculados, sin necesidad de clave API.",
            "run_button": "Ver clasificación",
            "selected_example": "Ejemplo seleccionado",
            "cta_byok_header": "¿Quieres clasificar tu propio sistema?",
            "cta_byok_body": "Cambia el modo en la barra lateral a '{mode}' y pega tu clave API de Anthropic.",
        },
        "classifier": {
            "title": "Clasificar un sistema de IA según el Reglamento Europeo de IA",
            "intro": "Describe tu sistema de IA y obtén su clasificación de riesgo bajo el EU AI Act con base legal, checklist de cumplimiento e informe de auditoría descargable.",
            "load_example": "Cargar un ejemplo",
            "example_placeholder": "— selecciona un ejemplo —",
            "system_name": "Nombre del sistema",
            "description": "Descripción",
            "description_help": "Entre 50 y 3000 caracteres. Describe qué hace el sistema, su contexto clínico y los usuarios previstos.",
            "intended_purpose": "Finalidad prevista",
            "data_inputs": "Datos de entrada",
            "data_inputs_help": "Selecciona todos los que apliquen. También puedes escribir valores personalizados.",
            "outputs_produced": "Salidas producidas (separadas por coma)",
            "deployment_context": "Contexto de despliegue",
            "affects_clinical_decision": "Afecta decisiones clínicas",
            "submit": "Clasificar",
            "submitting": "Analizando contra las disposiciones del EU AI Act…",
            "result_header": "Resultado de la clasificación",
            "empty_prompt": "Rellena el formulario y pulsa Clasificar para ver el resultado.",
            "error_title": "Error de clasificación",
        },
        "card": {
            "risk_level": "Nivel de riesgo",
            "confidence": "Confianza",
            "samd_flag": "SaMD (producto sanitario)",
            "conformity_assessment": "Evaluación de conformidad",
            "notified_body": "Organismo notificado",
            "yes": "Sí",
            "no": "No",
            "annex_iii": "Categorías del Anexo III",
            "article_5": "Prohibiciones del Artículo 5 activadas",
            "legal_basis": "Base legal",
            "clinical_notes": "Notas clínicas (comentario del médico)",
            "none": "Ninguna",
        },
        "checklist": {
            "title": "Checklist de cumplimiento",
            "mandatory": "Obligatorio",
            "recommended": "Recomendado",
            "conditional": "Condicional",
            "article": "Artículo",
            "requirement": "Requisito",
            "priority": "Prioridad",
            "deadline": "Plazo",
            "empty": "No hay requisitos asociados.",
        },
        "pdf": {
            "generate": "Generar informe PDF",
            "download": "Descargar PDF",
            "generating": "Generando informe de auditoría…",
            "ready": "Informe listo. Haz clic abajo para descargar.",
            "error": "No se pudo generar el informe PDF.",
        },
        "about": {
            "title": "Acerca de & metodología",
            "what_is_act_header": "Qué es el EU AI Act",
            "what_is_act_body": "El Reglamento (UE) 2024/1689 establece el primer marco legal horizontal para la IA en la Unión. En el ámbito sanitario se suma al MDR/IVDR e introduce requisitos específicos sobre gestión de riesgos, transparencia, supervisión humana y vigilancia post-comercialización.",
            "methodology_header": "Metodología",
            "methodology_body": "Clasificación en dos etapas: (1) un agente regulatorio basado en Claude produce una salida estructurada fundamentada en el Reglamento; (2) un motor de reglas estáticas valida la salida y, ante la duda, escala el nivel de riesgo — nunca lo rebaja.",
            "limitations_header": "Limitaciones",
            "limitations_body": "Esta herramienta no constituye asesoramiento legal ni es una evaluación de conformidad. Es una ayuda open-source para que los equipos HealthTech anticipen el contexto regulatorio.",
            "author_header": "Autor",
            "author_body": "Aram Zakzuk, MD — Especialista en IA clínica | Informática sanitaria | Consultor HealthTech.",
        },
        "regulatory": {
            "title": "EU AI Act — Referencia regulatoria",
            "search": "Buscar artículos o palabras clave",
            "annex_header": "Anexo III — Categorías de alto riesgo",
            "article5_header": "Artículo 5 — Prácticas prohibidas",
            "source": "Fuente",
            "no_match": "Ninguna entrada coincide con tu búsqueda.",
        },
    },
}


def _get_nested(d: dict[str, Any], path: str) -> Any | None:
    parts = path.split(".")
    cur: Any = d
    for p in parts:
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


_LANG_KEY = "language"


def get_language() -> str:
    """Return current language code from session state (defaults to English)."""
    lang = st.session_state.get(_LANG_KEY, DEFAULT_LANGUAGE)
    return lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def t(key: str) -> str:
    """Translate a dotted key. Falls back to English, then to the key itself."""
    lang = get_language()
    value = _get_nested(TRANSLATIONS.get(lang, {}), key)
    if value is None and lang != DEFAULT_LANGUAGE:
        value = _get_nested(TRANSLATIONS[DEFAULT_LANGUAGE], key)
    return value if isinstance(value, str) else key


def _on_language_change() -> None:
    """Callback: copy the widget value into the canonical session key."""
    selected_label = st.session_state.get("_language_selector")
    for code, label in SUPPORTED_LANGUAGES.items():
        if label == selected_label:
            st.session_state[_LANG_KEY] = code
            return


def language_selector(location: str = "sidebar") -> str:
    """Render a language selector bound to `st.session_state['language']`.

    Args:
        location: "sidebar" (default) or "main".

    Returns:
        Selected language code ("en" or "es").
    """
    if _LANG_KEY not in st.session_state:
        st.session_state[_LANG_KEY] = DEFAULT_LANGUAGE

    current_code = get_language()
    labels = [SUPPORTED_LANGUAGES[c] for c in SUPPORTED_LANGUAGES]
    current_label = SUPPORTED_LANGUAGES[current_code]

    # Initialise widget state on first run so the selectbox shows the right value.
    if "_language_selector" not in st.session_state:
        st.session_state["_language_selector"] = current_label

    target = st.sidebar if location == "sidebar" else st
    target.selectbox(
        TRANSLATIONS[current_code]["app"]["language_label"],
        options=labels,
        key="_language_selector",
        on_change=_on_language_change,
    )
    return get_language()
