import json
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# API "guest" do LinkedIn: a mesma que a página pública de vagas usa quando você NÃO está
# logado. Em vez de JSON, ela devolve PEDAÇOS DE HTML (uma lista de cards <li>).
SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "pt-BR,pt;q=0.9",
}
DATA_FILE = Path(__file__).parent.parent / "data" / "linkedin.json"  # Caminho da base de dados
DIAS_LIMITE = 45  # só mantém vagas publicadas nos últimos 45 dias
PASSO = 25        # o LinkedIn devolve as vagas de 25 em 25 (paginação via "start")


def main():
    term = sys.argv[1] if len(sys.argv) > 1 else "python"  # pega o termo na linha de comando
    jobs = []

    fetch_jobs(term, jobs)   # busca os cards crus (BeautifulSoup) — pagina e deduplica
    normalizeJobs(jobs)      # traduz cada card pro FORMATO PADRÃO
    filter_recent(jobs)      # mantém só os últimos 45 dias
    save_data(term, jobs)    # salva as vagas limpas na base de dados

    print(f"{len(jobs)} vagas salvas em {DATA_FILE}")  # Imprime status e quantidade.


def fetch_jobs(term, jobs):
    vistos = set()
    start = 0

    while True:
        # f_TPR=r3888000 => filtra no próprio LinkedIn os últimos 45 dias (45*86400 segundos).
        params = {
            "keywords": term,
            "location": "Brazil",
            "f_TPR": f"r{DIAS_LIMITE * 86400}",
            "start": start,
        }
        response = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()

        sopa = BeautifulSoup(response.text, "html.parser")
        cards = sopa.select("div.base-card")
        if not cards:
            break  # página vazia => acabou

        # Guarda só os cards novos (o LinkedIn repete vagas entre páginas).
        novos = 0
        for card in cards:
            chave = card.get("data-entity-urn")  # ex.: "urn:li:jobPosting:4012345678"
            if chave and chave not in vistos:
                vistos.add(chave)
                jobs.append(card)
                novos += 1

        if novos == 0:
            break  # só vieram repetidas => acabou

        start += PASSO
        time.sleep(1)  # respira entre páginas pra não tomar bloqueio (HTTP 429)


def detectWorkplaceType(texto):  # Infere o modelo de trabalho varrendo o texto do card
    texto = texto.lower()

    if any(t in texto for t in ["remoto", "remote", "home office", "home-office"]):
        return "remote"
    if any(t in texto for t in ["híbrido", "hibrido", "hybrid"]):
        return "hybrid"
    if any(t in texto for t in ["presencial", "on-site", "on site", "onsite"]):
        return "on-site"
    return "other"


def texto_de(card, seletor):  # Pega o texto de um seletor dentro do card (ou "" se não achar)
    elemento = card.select_one(seletor)
    return elemento.get_text(strip=True) if elemento else ""


def normalizeJobs(rawJobs):  # Traduz os cards crus do LinkedIn para o FORMATO PADRÃO
    jobs = []

    for card in rawJobs:
        title = texto_de(card, ".base-search-card__title")
        company = texto_de(card, ".base-search-card__subtitle")
        location = texto_de(card, ".job-search-card__location")

        # id: o número no fim do "data-entity-urn" (urn:li:jobPosting:<id>).
        urn = card.get("data-entity-urn") or ""
        id_vaga = urn.split(":")[-1] if urn else None

        # url: o link "cheio" do card; tiramos os parâmetros de rastreio (?...).
        link = card.select_one("a.base-card__full-link")
        url = link.get("href").split("?")[0] if link and link.get("href") else None

        # publishedDate: a <time> traz só a data (ex.: "2026-06-10"); viramos ISO com fuso UTC
        # pro filter_recent comparar sem erro (data "ingênua" vs data "com fuso").
        time_tag = card.select_one("time")
        published = None
        if time_tag and time_tag.get("datetime"):
            try:
                published = datetime.fromisoformat(
                    time_tag["datetime"]
                ).replace(tzinfo=timezone.utc).isoformat()
            except ValueError:
                published = None

        jobs.append({
            "source": "linkedin",
            "id": id_vaga,
            "title": title,
            "company": company,
            "description": "",  # decisão do Jamel: sem descrição (evita request extra/429)
            "location": location,
            "workplaceType": detectWorkplaceType(f"{title} {location}"),
            "publishedDate": published,
            "url": url,
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


def save_data(term, jobs):  # Monta o registro e grava direto na base (data/linkedin.json).
    payload = {
        "source": "linkedin",
        "term": term,
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "jobs": [job for job in jobs],
    }
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as arquivo:
        json.dump(payload, arquivo, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
