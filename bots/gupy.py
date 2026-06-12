import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

API_URL = "https://employability-portal.gupy.io/api/v1/jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Origin": "https://portal.gupy.io",
    "Referer": "https://portal.gupy.io/",
}

# Caminho da base de dados (sobe de bots/ até a raiz e entra em data/).
DATA_FILE = Path(__file__).parent.parent / "data" / "gupy.json"


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


def normalize(job):
    # Traduz uma vaga crua da Gupy para o FORMATO PADRÃO (o "contrato" que todo
    # bot fala). Assim o Node e o front-end não precisam saber de onde a vaga veio.
    if job.get("isRemoteWork"):
        location = "Remoto"
    else:
        partes = [job.get("city"), job.get("state")]
        location = ", ".join(p for p in partes if p)

    return {
        "source": "gupy",
        "id": str(job.get("id")),
        "title": job.get("name"),
        "company": job.get("careerPageName"),
        "description": job.get("description") or "",
        "location": location,
        "workplaceType": job.get("workplaceType"),
        "publishedDate": job.get("publishedDate"),
        "url": job.get("jobUrl"),
    }


def save_data(term, jobs):
    # Monta o registro e grava direto na base de dados (data/gupy.json).
    # Quem lê esse arquivo é o servidor Node — nada de vagas vai para o terminal.
    payload = {
        "source": "gupy",
        "term": term,
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "jobs": [normalize(job) for job in jobs],
    }
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as arquivo:
        json.dump(payload, arquivo, ensure_ascii=False, indent=2)


def main():
    # O termo de busca vem como argumento da linha de comando.
    # Ex: python bots/gupy.py "java"   (sem argumento, usa "python")
    term = sys.argv[1] if len(sys.argv) > 1 else "python"

    jobs = fetch_jobs(term)
    save_data(term, jobs)

    # Apenas uma linha de status (NÃO imprime as vagas).
    print(f"{len(jobs)} vagas salvas em {DATA_FILE}")


if __name__ == "__main__":
    main()
