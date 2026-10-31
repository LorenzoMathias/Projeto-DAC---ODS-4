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
        div[data-testid="stHeaderActionElements"],
        div[data-testid="stHeaderActionElements"] *,
        button[kind="header"],
        button[title="Deploy"] {
            display: none !important;
            visibility: hidden !important;
        }
        html, body {
            overflow: auto;
            height: auto;
        }
        .block-container {
            max-width: 100%;
            overflow: visible;
            padding-top: 1.1rem;
        }
        .stApp {
            padding-top: 0.45rem !important;
        }
        .stTitle {
            margin-top: 2.3rem !important;
            margin-bottom: 0.5rem !important;
            padding-top: 0 !important;
            line-height: 1.08 !important;
            overflow: visible !important;
            white-space: normal !important;
            word-break: break-word !important;
            display: block !important;
            min-height: 4rem !important;
        }
        [data-testid="stMarkdownContainer"] h1 button,
        [data-testid="stMarkdownContainer"] h2 button,
        [data-testid="stMarkdownContainer"] h3 button,
        [data-testid="stMarkdownContainer"] h4 button,
        [data-testid="stMarkdownContainer"] h5 button,
        [data-testid="stMarkdownContainer"] h6 button,
        button[data-testid="stLinkCopyButton"],
        a[data-testid="stLinkCopyButton"],
        [data-testid="stLinkCopyButton"],
        [data-testid="stHeadingActionElements"],
        [data-testid="stHeadingActionElements"] *,
        button[title*="Copy"],
        button[title*="copy"],
        button[title*="link"],
        button[title*="Link"],
        button[aria-label*="Copy"],
        button[aria-label*="copy"],
        button[aria-label*="link"],
        button[aria-label*="Link"],
        svg[title*="Copy"],
        svg[title*="copy"],
        svg[aria-label*="Copy"],
        svg[aria-label*="copy"] {
            display: none !important;
            visibility: hidden !important;
            pointer-events: none !important;
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
    ax.set_title("Evolução anual da aprovação", fontsize=24, pad=18, fontweight="bold")
    ax.set_xlabel("Ano", fontweight="bold")
    ax.set_ylabel("Taxa de aprovação (%)", fontweight="bold")
    ax.set_xticks(anos)
    ax.set_xticklabels([str(int(v)) for v in anos], rotation=0)
    ax.set_ylim(0, max(100, max(valores) * 1.2 + 5))
    ax.grid(True, axis="y", linestyle="--", alpha=0.35)
    ax.set_axisbelow(True)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def build_year_range(ano_inicial: str | int | None, ano_final: str | int | None):
    start = None if ano_inicial in (None, "Todos") else int(ano_inicial)
    end = None if ano_final in (None, "Todos", "Ano atual") else int(ano_final)

    if start is not None and end is not None and start > end:
        start, end = end, start

    return start, end


def get_comparison_title(municipio: str | None) -> str:
    if municipio not in (None, "Todos"):
        return f"Taxa de aprovação em {municipio}"
    return "Comparação entre municípios"


def plot_municipality_comparison(df_comp: pd.DataFrame, municipio: str | None = None) -> None:
    fig, ax = plt.subplots(figsize=(10, 4))
    municipios = df_comp["municipio"].tolist()
    valores = df_comp["taxa_aprovacao"].astype(float).tolist()

    if len(municipios) == 1:
        x_positions = [0]
        bar_width = 0.28
        ax.set_xlim(-0.6, 0.6)
    else:
        x_positions = range(len(municipios))
        bar_width = 0.8

    ax.bar(x_positions, valores, color="#5aa9ff", width=bar_width)
    ax.set_title(get_comparison_title(municipio), fontsize=24, pad=18, fontweight="bold")
    ax.set_xlabel("Município", fontweight="bold")
    ax.set_ylabel("Taxa de aprovação (%)", fontweight="bold")
    ax.set_ylim(0, max(100, max(valores) * 1.2 + 5))

    if len(municipios) == 1:
        ax.set_xticks([0])
        ax.set_xticklabels([municipios[0]], rotation=0, ha="center")
    else:
        ax.set_xticks(range(len(municipios)))
        ax.set_xticklabels(municipios, rotation=0, ha="center")

    ax.grid(True, axis="y", linestyle="--", alpha=0.35)
    ax.set_axisbelow(True)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def build_dashboard():
    db = ensure_data_loaded()

    anos = [int(v) for v in db.anos()]
    municipios = ["Todos", *db.municipios()]
    redes = ["Todos", *db.redes()]
    current_year = max(anos) if anos else 2026

    selected_ano_inicial = st.sidebar.selectbox("Ano inicial", ["Todos", *[str(v) for v in anos]])

    valid_end_years = anos
    if selected_ano_inicial not in (None, "Todos"):
        valid_end_years = [v for v in anos if v >= int(selected_ano_inicial)]

    end_options = [("Ano atual", current_year)]
    end_options.extend((str(v), v) for v in valid_end_years if v != current_year)
    selected_ano_final = st.sidebar.selectbox(
        "Ano final",
        end_options,
        format_func=lambda option: option[0],
        index=0,
    )
    selected_ano_final_value = selected_ano_final[1]

    selected_municipio = st.sidebar.selectbox("Município", municipios)
    selected_rede = st.sidebar.selectbox("Rede", redes)

    records = CsvLoader.load(CSV_PATH)
    analytics = EducationAnalytics(records)
    ano_inicial, ano_final = build_year_range(selected_ano_inicial, selected_ano_final_value)

    summary = analytics.summary(
        ano_inicial=ano_inicial,
        ano_final=ano_final,
        municipio=selected_municipio,
        rede=selected_rede,
    )
    filtered = analytics.filter_records(
        ano_inicial=ano_inicial,
        ano_final=ano_final,
        municipio=selected_municipio,
        rede=selected_rede,
    )

    st.title("📚 Análise da Educação em Mato Grosso do Sul", anchor=False)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Escolas", summary["total_escolas"])
    col2.metric("Matrículas", f"{summary['total_matriculas']:,}")
    col3.metric("Taxa de aprovação", f"{summary['taxa_aprovacao_media']:.2f}%")
    col4.metric("Abandono médio", f"{summary['taxa_abandono_media']:.2f}%")

    trend = analytics.yearly_trend(
        municipio=selected_municipio,
        rede=selected_rede,
        ano_inicial=ano_inicial,
        ano_final=ano_final,
    )
    df_trend = pd.DataFrame(trend)

    comp = analytics.municipality_comparison(
        ano_inicial=ano_inicial,
        ano_final=ano_final,
        rede=selected_rede,
    )
    df_comp = pd.DataFrame(comp)
    if selected_municipio not in (None, "Todos"):
        df_comp = df_comp[df_comp["municipio"] == selected_municipio]

    if not df_trend.empty:
        plot_yearly_trend(df_trend)

    if not df_comp.empty:
        plot_municipality_comparison(df_comp, municipio=selected_municipio)

    st.subheader("Dados detalhados", anchor=False)
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
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            height=360,
        )
    else:
        st.info("Nenhum dado encontrado com os filtros selecionados.")


if __name__ == "__main__":
    build_dashboard()
