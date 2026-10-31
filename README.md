# Projeto DAC - ODS 4

Projeto acadêmico da disciplina de DAC (4º semestre) focado em analisar indicadores educacionais da rede pública de Mato Grosso do Sul, com base em dados históricos e filtros analíticos.

## Objetivo

- Carregar dados educacionais em CSV
- Organizar os dados em classes e estruturas de dados
- Persistir as informações em banco SQLite
- Exibir indicadores e filtros por município, ano e rede
- Permitir análise da evolução da educação em MS

## Tecnologias

- Python
- Streamlit
- SQLite
- Pandas
- Matplotlib
- Orientação a Objetos

## Como executar

1. Crie o ambiente virtual:

   python -m venv .venv
   source .venv/bin/activate

2. Instale as dependências:

   pip install -r requirements.txt

3. Inicie a aplicação:

   streamlit run app/app.py

4. Acesse o endereço exibido no terminal.

## Estrutura do projeto

- `app/` - código fonte da aplicação
- `data/` - arquivos CSV de exemplo
