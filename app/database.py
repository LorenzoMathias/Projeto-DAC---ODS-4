from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import SchoolRecord


class EducationDatabase:
    def __init__(self, db_path: str | Path = "data/educacao_ms.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS school_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ano INTEGER NOT NULL,
                    municipio TEXT NOT NULL,
                    escola TEXT NOT NULL,
                    etapa TEXT NOT NULL,
                    rede TEXT NOT NULL,
                    matriculas INTEGER NOT NULL,
                    aprovados INTEGER NOT NULL,
                    reprovados INTEGER NOT NULL,
                    evadidos INTEGER NOT NULL,
                    abandono REAL NOT NULL
                )
                """
            )
            conn.commit()

    def save_records(self, records: list[SchoolRecord]) -> None:
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO school_records (
                    ano, municipio, escola, etapa, rede,
                    matriculas, aprovados, reprovados, evadidos, abandono
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        r.ano,
                        r.municipio,
                        r.escola,
                        r.etapa,
                        r.rede,
                        r.matriculas,
                        r.aprovados,
                        r.reprovados,
                        r.evadidos,
                        r.abandono,
                    )
                    for r in records
                ],
            )
            conn.commit()

    def has_data(self) -> bool:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS total FROM school_records").fetchone()
            return (row["total"] or 0) > 0

    def anos(self) -> list[int]:
        with self._connect() as conn:
            rows = conn.execute("SELECT DISTINCT ano FROM school_records ORDER BY ano").fetchall()
            return [int(r["ano"]) for r in rows]

    def municipios(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT municipio FROM school_records ORDER BY municipio"
            ).fetchall()
            return [str(r["municipio"]) for r in rows]

    def redes(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute("SELECT DISTINCT rede FROM school_records ORDER BY rede").fetchall()
            return [str(r["rede"]) for r in rows]

    def get_summary(self, ano: int | str | None = None, municipio: str | None = None, rede: str | None = None) -> dict:
        where_clauses = []
        values = []

        if ano not in (None, "Todos"):
            where_clauses.append("ano = ?")
            values.append(int(ano))
        if municipio not in (None, "Todos"):
            where_clauses.append("municipio = ?")
            values.append(municipio)
        if rede not in (None, "Todos"):
            where_clauses.append("rede = ?")
            values.append(rede)

        where_sql = ""
        if where_clauses:
            where_sql = " WHERE " + " AND ".join(where_clauses)

        query = f"""
            SELECT
                COUNT(*) AS total_escolas,
                SUM(matriculas) AS total_matriculas,
                SUM(aprovados) AS total_aprovados,
                SUM(reprovados) AS total_reprovados,
                SUM(evadidos) AS total_evadidos,
                AVG((aprovados * 100.0) / NULLIF(matriculas, 0)) AS taxa_aprovacao_media,
                AVG(abandono) AS taxa_abandono_media
            FROM school_records
            {where_sql}
        """

        with self._connect() as conn:
            row = conn.execute(query, values).fetchone()

        total_escolas = int(row["total_escolas"] or 0)
        total_matriculas = int(row["total_matriculas"] or 0)
        total_aprovados = int(row["total_aprovados"] or 0)
        total_reprovados = int(row["total_reprovados"] or 0)
        total_evadidos = int(row["total_evadidos"] or 0)
        taxa_aprovacao = float(row["taxa_aprovacao_media"] or 0.0)
        taxa_abandono = float(row["taxa_abandono_media"] or 0.0)

        return {
            "total_escolas": total_escolas,
            "total_matriculas": total_matriculas,
            "total_aprovados": total_aprovados,
            "total_reprovados": total_reprovados,
            "total_evadidos": total_evadidos,
            "taxa_aprovacao_media": round(taxa_aprovacao, 2),
            "taxa_abandono_media": round(taxa_abandono, 2),
        }

    def yearly_trend(self, municipio: str | None = None, rede: str | None = None) -> list[dict]:
        where_clauses = []
        values = []

        if municipio not in (None, "Todos"):
            where_clauses.append("municipio = ?")
            values.append(municipio)
        if rede not in (None, "Todos"):
            where_clauses.append("rede = ?")
            values.append(rede)

        where_sql = ""
        if where_clauses:
            where_sql = " WHERE " + " AND ".join(where_clauses)

        query = f"""
            SELECT
                ano,
                AVG((aprovados * 100.0) / NULLIF(matriculas, 0)) AS taxa_aprovacao,
                AVG(abandono) AS abandono_medio
            FROM school_records
            {where_sql}
            GROUP BY ano
            ORDER BY ano
        """

        with self._connect() as conn:
            rows = conn.execute(query, values).fetchall()

        return [
            {
                "ano": int(row["ano"]),
                "taxa_aprovacao": round(float(row["taxa_aprovacao"] or 0.0), 2),
                "abandono_medio": round(float(row["abandono_medio"] or 0.0), 2),
            }
            for row in rows
        ]

    def municipality_comparison(self, ano: int | str | None = None, rede: str | None = None) -> list[dict]:
        where_clauses = []
        values = []

        if ano not in (None, "Todos"):
            where_clauses.append("ano = ?")
            values.append(int(ano))
        if rede not in (None, "Todos"):
            where_clauses.append("rede = ?")
            values.append(rede)

        where_sql = ""
        if where_clauses:
            where_sql = " WHERE " + " AND ".join(where_clauses)

        query = f"""
            SELECT
                municipio,
                AVG((aprovados * 100.0) / NULLIF(matriculas, 0)) AS taxa_aprovacao,
                AVG(abandono) AS abandono_medio
            FROM school_records
            {where_sql}
            GROUP BY municipio
            ORDER BY taxa_aprovacao DESC
        """

        with self._connect() as conn:
            rows = conn.execute(query, values).fetchall()

        return [
            {
                "municipio": row["municipio"],
                "taxa_aprovacao": round(float(row["taxa_aprovacao"] or 0.0), 2),
                "abandono_medio": round(float(row["abandono_medio"] or 0.0), 2),
            }
            for row in rows
        ]
