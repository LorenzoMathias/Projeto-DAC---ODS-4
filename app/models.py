from dataclasses import dataclass


@dataclass
class SchoolRecord:
    ano: int
    municipio: str
    escola: str
    etapa: str
    rede: str
    matriculas: int
    aprovados: int
    reprovados: int
    evadidos: int
    abandono: float

    @property
    def taxa_aprovacao(self) -> float:
        if self.matriculas == 0:
            return 0.0
        return (self.aprovados / self.matriculas) * 100

    @property
    def taxa_abandono(self) -> float:
        return self.abandono
