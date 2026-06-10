import json
import sys

import requests

API_URL = "https://employability-portal.gupy.io/api/v1/jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Origin": "https://portal.gupy.io",
    "Referer": "https://portal.gupy.io/",
}


# Estrutura de cada vaga retornada pela API (dicionário Python).
# Campo                | Tipo  | Significado
# ---------------------|-------|---------------------------------------------------
# id                   | int   | identificador único da vaga
# companyId            | int   | identificador da empresa
# name                 | str   | título da vaga (ex: "Desenvolvedor Back-end Python")
# description          | str   | descrição completa da vaga (texto longo)
# careerPageId         | int   | identificador da página de carreiras da empresa
# careerPageName       | str   | nome exibido da página de carreiras (≈ nome da empresa)
# careerPageLogo       | str   | URL do logo da empresa
# careerPageUrl        | str   | URL da página de carreiras da empresa
# type                 | str   | tipo de contrato (ex: "vacancy_type_effective" = CLT)
# publishedDate        | str   | data/hora de publicação (ISO 8601, ex: "2026-06-09T13:48:11Z")
# applicationDeadline  | str   | data limite para candidatura (ex: "2026-08-07")
# isRemoteWork         | bool  | True se a vaga é remota
# city                 | str   | cidade da vaga (vazio "" quando remota)
# state                | str   | estado da vaga (vazio "" quando remota)
# country              | str   | país da vaga (ex: "Brasil")
# jobUrl               | str   | link direto para se candidatar à vaga
# badges               | dict  | selos da vaga (ex: {"friendlyBadge": True, "isPWD": True})
# workplaceType        | str   | modelo de trabalho: "remote" | "hybrid" | "on-site"
# disabilities         | bool  | True se a vaga é também para pessoas com deficiência (PcD)
# skills               | list  | lista de competências/habilidades (pode vir vazia [])
def fetch_jobs(term):
    jobs = []
    offset = 0
    limit = 100

    while True:
        params = {"jobName": term, "limit": limit, "offset": offset}

        response = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        jobs.extend(data["data"])

        total = data["pagination"]["total"]
        offset += limit
        if offset >= total:
            break

    return jobs


def main():
    # O termo de busca vem como argumento da linha de comando.
    # Ex: python bots/gupy.py "java"   (sem argumento, usa "python")
    term = sys.argv[1] if len(sys.argv) > 1 else "python"

    jobs = fetch_jobs(term)

    # Imprime as vagas como JSON no stdout, para o Node capturar.
    # ensure_ascii=True (padrão) escapa acentos (ex: é), evitando erros
    # de codificação no terminal do Windows. O Node decodifica de volta.
    print(json.dumps(jobs))


if __name__ == "__main__":
    main()
