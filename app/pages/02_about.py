"""About & methodology page."""

from __future__ import annotations

import streamlit as st

from app.utils.i18n import language_selector, t

language_selector()

st.title(t("about.title"))

st.markdown(f"### {t('about.what_is_act_header')}")
st.write(t("about.what_is_act_body"))

st.markdown(f"### {t('about.methodology_header')}")
st.write(t("about.methodology_body"))

st.markdown(f"### {t('about.limitations_header')}")
st.write(t("about.limitations_body"))

st.markdown(f"### {t('about.author_header')}")
st.write(t("about.author_body"))
st.markdown(
    "- LinkedIn: [linkedin.com/in/aramzakzuk](https://linkedin.com/in/aramzakzuk)  \n"
    "- Web: [alejandrozakzuk.com](https://alejandrozakzuk.com)"
)
