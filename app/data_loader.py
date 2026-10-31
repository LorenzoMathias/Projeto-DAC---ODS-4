from __future__ import annotations

from pathlib import Path
import pandas as pd

from .models import SchoolRecord


class CsvLoader:
    @staticmethod
    def load(path: str | Path) -> list[SchoolRecord]:
        csv_path = Path(path)
        df = pd.read_csv(csv_path)
        records: list[SchoolRecord] = []

        for _, row in df.iterrows():
            records.append(
                SchoolRecord(
                    ano=int(row["ano"]),
                    municipio=str(row["municipio"]).strip(),
                    escola=str(row["escola"]).strip(),
                    etapa=str(row["etapa"]).strip(),
                    rede=str(row["rede"]).strip(),
                    matriculas=int(row["matriculas"]),
                    aprovados=int(row["aprovados"]),
                    reprovados=int(row["reprovados"]),
                    evadidos=int(row["evadidos"]),
                    abandono=float(row["abandono"]),
                )
            )

        return records
