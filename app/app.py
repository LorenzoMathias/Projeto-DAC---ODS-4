from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.analytics import EducationAnalytics
from app.data_loader import CsvLoader
from app.database import EducationDatabase

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DB_PATH = DATA_DIR / "educacao_ms.db"
CSV_PATH = DATA_DIR / "educacao_ms_sample.csv"

st.set_page_config(
    page_title="Educação MS",
    page_icon="📚",
    layout="wide",
    menu_items={},
)

st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {display: none;}
        html, body {
            overflow: auto;
            height: auto;
        }
        .block-container {
            max-width: 100%;
            overflow: visible;
            padding-top: 0.75rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def ensure_data_loaded() -> EducationDatabase:
    db = EducationDatabase(DB_PATH)
    if not db.has_data():
        records = CsvLoader.load(CSV_PATH)
        db.save_records(records)
    return db


def plot_yearly_trend(df_trend: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(12, 4))
    anos = df_trend["ano"].astype(int).tolist()
    valores = df_trend["taxa_aprovacao"].astype(float).tolist()

    ax.plot(anos, valores, color="#5aa9ff", marker="o", linewidth=2.5)
    ax.set_title("Evolução anual da aprovação", fontsize=24, pad=18)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Taxa de aprovação (%)")
    ax.set_xticks(anos)
    ax.set_xticklabels([str(int(v)) for v in anos], rotation=0)
    ax.set_ylim(0, max(100, max(valores) * 1.2 + 5))
    ax.grid(True, axis="y", linestyle="--", alpha=0.35)
    ax.set_axisbelow(True)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def plot_municipality_comparison(df_comp: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 4))
    municipios = df_comp["municipio"].tolist()
    valores = df_comp["taxa_aprovacao"].astype(float).tolist()

    ax.bar(municipios, valores, color="#5aa9ff")
    ax.set_title("Comparação entre municípios", fontsize=24, pad=18)
    ax.set_xlabel("Município")
    ax.set_ylabel("Taxa de aprovação (%)")
    ax.set_ylim(0, max(100, max(valores) * 1.2 + 5))
    ax.set_xticklabels(municipios, rotation=0, ha="center")
    ax.grid(True, axis="y", linestyle="--", alpha=0.35)
    ax.set_axisbelow(True)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def build_dashboard():
    db = ensure_data_loaded()

    anos = ["Todos", *[str(v) for v in db.anos()]]
    municipios = ["Todos", *db.municipios()]
    redes = ["Todos", *db.redes()]

    selected_ano = st.sidebar.selectbox("Ano", anos)
    selected_municipio = st.sidebar.selectbox("Município", municipios)
    selected_rede = st.sidebar.selectbox("Rede", redes)

    summary = db.get_summary(
        ano=selected_ano,
        municipio=selected_municipio,
        rede=selected_rede,
    )

    records = CsvLoader.load(CSV_PATH)
    analytics = EducationAnalytics(records)
    filtered = analytics.filter_records(
        ano=selected_ano,
        municipio=selected_municipio,
        rede=selected_rede,
    )

    st.title("📚 Análise da Educação em Mato Grosso do Sul")
    st.caption("DAC 4º semestre • ODS 4: Educação de Qualidade")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Escolas", summary["total_escolas"])
    col2.metric("Matrículas", f"{summary['total_matriculas']:,}")
    col3.metric("Taxa de aprovação", f"{summary['taxa_aprovacao_media']:.2f}%")
    col4.metric("Abandono médio", f"{summary['taxa_abandono_media']:.2f}%")

    trend = db.yearly_trend(municipio=selected_municipio, rede=selected_rede)
    df_trend = pd.DataFrame(trend)
    comp = db.municipality_comparison(ano=selected_ano, rede=selected_rede)
    df_comp = pd.DataFrame(comp)

    if not df_trend.empty:
        plot_yearly_trend(df_trend)

    if not df_comp.empty:
        plot_municipality_comparison(df_comp)

    st.subheader("Dados detalhados")
    if filtered:
        df = pd.DataFrame(
            [
                {
                    "Ano": r.ano,
                    "Município": r.municipio,
                    "Escola": r.escola,
                    "Etapa": r.etapa,
                    "Rede": r.rede,
                    "Matrículas": r.matriculas,
                    "Aprovados": r.aprovados,
                    "Reprovados": r.reprovados,
                    "Evadidos": r.evadidos,
                    "Abandono": r.abandono,
                    "Taxa de aprovação": round(r.taxa_aprovacao, 2),
                }
                for r in filtered
            ]
        )
        st.dataframe(df, width="stretch")
    else:
        st.info("Nenhum dado encontrado com os filtros selecionados.")


if __name__ == "__main__":
    build_dashboard()
