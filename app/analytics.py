from __future__ import annotations

from .models import SchoolRecord


class EducationAnalytics:
    def __init__(self, records: list[SchoolRecord]) -> None:
        self.records = records

    def filter_records(self, ano: int | str | None = None, municipio: str | None = None, rede: str | None = None) -> list[SchoolRecord]:
        filtered = self.records

        if ano not in (None, "Todos"):
            filtered = [r for r in filtered if r.ano == int(ano)]
        if municipio not in (None, "Todos"):
            filtered = [r for r in filtered if r.municipio == municipio]
        if rede not in (None, "Todos"):
            filtered = [r for r in filtered if r.rede == rede]

        return filtered

    def summary(self, ano: int | str | None = None, municipio: str | None = None, rede: str | None = None) -> dict:
        filtered = self.filter_records(ano=ano, municipio=municipio, rede=rede)

        total_matriculas = sum(r.matriculas for r in filtered)
        total_aprovados = sum(r.aprovados for r in filtered)
        total_reprovados = sum(r.reprovados for r in filtered)
        total_evadidos = sum(r.evadidos for r in filtered)

        approv_rate = (total_aprovados / total_matriculas * 100) if total_matriculas else 0.0
        drop_rate = (sum(r.abandono for r in filtered) / len(filtered)) if filtered else 0.0

        return {
            "total_escolas": len({r.escola for r in filtered}),
            "total_matriculas": total_matriculas,
            "total_aprovados": total_aprovados,
            "total_reprovados": total_reprovados,
            "total_evadidos": total_evadidos,
            "taxa_aprovacao_media": round(approv_rate, 2),
            "taxa_abandono_media": round(drop_rate, 2),
        }

    def yearly_trend(self, municipio: str | None = None, rede: str | None = None) -> list[dict]:
        registros = self.filter_records(municipio=municipio, rede=rede)
        por_ano: dict[int, list[SchoolRecord]] = {}

        for record in registros:
            por_ano.setdefault(record.ano, []).append(record)

        result = []
        for ano in sorted(por_ano):
            items = por_ano[ano]
            total_matriculas = sum(i.matriculas for i in items)
            total_aprovados = sum(i.aprovados for i in items)
            abandono_medio = sum(i.abandono for i in items) / len(items) if items else 0.0
            taxa = (total_aprovados / total_matriculas * 100) if total_matriculas else 0.0
            result.append({"ano": ano, "taxa_aprovacao": round(taxa, 2), "abandono_medio": round(abandono_medio, 2)})

        return result

    def municipality_comparison(self, ano: int | str | None = None, rede: str | None = None) -> list[dict]:
        registros = self.filter_records(ano=ano, rede=rede)
        por_municipio: dict[str, list[SchoolRecord]] = {}

        for record in registros:
            por_municipio.setdefault(record.municipio, []).append(record)

        result = []
        for municipio in sorted(por_municipio):
            items = por_municipio[municipio]
            total_matriculas = sum(i.matriculas for i in items)
            total_aprovados = sum(i.aprovados for i in items)
            abandono_medio = sum(i.abandono for i in items) / len(items) if items else 0.0
            taxa = (total_aprovados / total_matriculas * 100) if total_matriculas else 0.0
            result.append({"municipio": municipio, "taxa_aprovacao": round(taxa, 2), "abandono_medio": round(abandono_medio, 2)})

        return sorted(result, key=lambda item: item["taxa_aprovacao"], reverse=True)
