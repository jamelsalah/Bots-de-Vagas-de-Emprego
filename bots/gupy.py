import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

API_URL = "https://employability-portal.gupy.io/api/v1/jobs" # Url do gupy
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Origin": "https://portal.gupy.io",
    "Referer": "https://portal.gupy.io/",
}
DATA_FILE = Path(__file__).parent.parent / "data" / "gupy.json" # Caminho da base de dados
DIAS_LIMITE = 45  # só mantém vagas publicadas nos últimos 45 dias



def main():
    term = sys.argv[1] if len(sys.argv) > 1 else "python" #pega o termo na linha de comando
    jobs = []

    fetch_jobs(term, jobs)  #busca as vagas cruas
    normalizeJobs(jobs) #sanitiza as vagas cruas
    filter_recent(jobs) #mantém só os últimos 45 dias
    save_data(term, jobs) #salva as vagas limpas na base de dados

    
    print(f"{len(jobs)} vagas salvas em {DATA_FILE}")# Imprime status e quantidade de vagas buscadas.



def fetch_jobs(term, jobs):
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



def normalizeJobs(rawJobs):  # Traduz as vagas cruas da Gupy para o FORMATO PADRÃO
   
    jobs = []

    for job in rawJobs:
        if job.get("isRemoteWork"):
            location = "Remoto"
        else:
            partes = [job.get("city"), job.get("state")]
            location = ", ".join(p for p in partes if p)

        jobs.append({
            "source": "gupy",
            "id": str(job.get("id")),
            "title": job.get("name"),
            "company": job.get("careerPageName"),
            "description": job.get("description") or "",
            "location": location,
            "workplaceType": job.get("workplaceType"),
            "publishedDate": job.get("publishedDate"),
            "url": job.get("jobUrl"),
        })
    
    rawJobs.clear()
    rawJobs[:] = jobs


def parse_date(value):  # ISO 8601 -> datetime com fuso (UTC); None se não der pra ler
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def filter_recent(jobs):  # Mantém só as vagas dos últimos DIAS_LIMITE dias (MUTA no lugar)
    limite = datetime.now(timezone.utc) - timedelta(days=DIAS_LIMITE)

    recentes = []
    for job in jobs:
        data = parse_date(job.get("publishedDate"))
        if data is None or data >= limite:   # sem data legível -> mantém
            recentes.append(job)

    jobs.clear()
    jobs[:] = recentes


def save_data(term, jobs):  # Monta o registro e grava direto na base de dados (data/gupy.json).
   
    payload = {
        "source": "gupy",
        "term": term,
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "jobs": [job for job in jobs],
    }
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as arquivo:
        json.dump(payload, arquivo, ensure_ascii=False, indent=2)




if __name__ == "__main__":
    main()



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
