import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

SEARCH_URL = "https://br.indeed.com/jobs?q={term}&start={start}"

# O login do Indeed usa reCAPTCHA (que não funciona em navegador automatizado), então em
# vez de logar, o bot reaproveita o SEU Edge já logado: abre o mesmo perfil, com os cookies.
# >>> Feche TODAS as janelas do Edge antes de rodar (o perfil trava se estiver aberto). <<<
# Se você logou em outro perfil do Edge, troque "Default" por "Profile 1", etc.
EDGE_USER_DATA = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Edge" / "User Data"
EDGE_PROFILE = "Default"

# A 1ª página é pública; da 2ª em diante o Indeed exige login. ~15 vagas por página.
MAX_PAGES = 5

# As vagas ficam embutidas na página nesta variável JavaScript; pegamos a lista "results".
JOBCARDS_JS = """
() => {
  const provider = window.mosaic
    && window.mosaic.providerData
    && window.mosaic.providerData["mosaic-provider-jobcards"];
  if (!provider) return null;
  const model = provider.metaData && provider.metaData.mosaicProviderJobCardsModel;
  return (model && model.results) || null;
}
"""

# Campos úteis de cada vaga do Indeed (a vaga vem com ~110 campos no total):
# Campo                | Tipo  | Significado
# ---------------------|-------|---------------------------------------------------
# jobkey               | str   | identificador único da vaga (usado no link e no dedup)
# title                | str   | título da vaga (ex: "Pessoa Desenvolvedora em Python")
# displayTitle         | str   | título como exibido no card (costuma ser igual a title)
# normTitle            | str   | título normalizado pelo Indeed (ex: "Python")
# company              | str   | nome da empresa (ex: "Cappta")
# truncatedCompany     | str   | nome curto da empresa (para exibição)
# formattedLocation    | str   | localização já formatada (ex: "Remoto", "São Paulo, SP")
# jobLocationCity      | str   | cidade da vaga (ex: "Remoto" quando remota)
# remoteLocation       | bool  | True se a vaga é remota
# snippet              | str   | descrição curta da vaga em HTML (<ul><li>...</li></ul>)
# pubDate              | int   | data de publicação (timestamp epoch em milissegundos)
# createDate           | int   | data de criação do anúncio (timestamp epoch em ms)
# formattedRelativeTime| str   | tempo relativo desde a publicação (ex: "há 21 dias")
# salarySnippet        | dict  | info de salário ({"currency": "", "salaryTextFormatted": ...})
# jobTypes             | list  | tipos de contrato (pode vir vazia [])
# taxonomyAttributes   | list  | atributos classificados (ex: job-types: "Tempo integral")
# companyRating        | float | nota média da empresa no Indeed (ex: 3.4)
# companyReviewCount   | int   | quantidade de avaliações da empresa
# sponsored            | bool  | True se a vaga é um anúncio patrocinado
# urgentlyHiring       | bool  | True se marcada como "contratação urgente"
# link                 | str   | link relativo de clique (/rc/clk?jk=...)
# viewJobLink          | str   | link relativo da vaga (/viewjob?jk=...)
# O link absoluto para abrir a vaga monta-se com:
#   https://br.indeed.com/viewjob?jk=<jobkey>


def coletar_pagina(page, term, start):
    page.goto(SEARCH_URL.format(term=term, start=start), timeout=60000)
    try:
        page.wait_for_function(JOBCARDS_JS, timeout=30000)
        return page.evaluate(JOBCARDS_JS)
    except Exception:
        return None


def fetch_jobs(term, max_pages=MAX_PAGES):
    todas = []
    vistos = set()

    # Stealth() disfarça as "pegadas" do Playwright; ajuda a não disparar o Cloudflare.
    with Stealth().use_sync(sync_playwright()) as p:
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(EDGE_USER_DATA),
                channel="msedge",
                headless=False,
                locale="pt-BR",
                timezone_id="America/Sao_Paulo",
                no_viewport=True,
                args=[
                    f"--profile-directory={EDGE_PROFILE}",
                    "--disable-blink-features=AutomationControlled",
                ],
            )
        except Exception as erro:
            print("[x] Nao consegui abrir o perfil do Edge.")
            print("    Feche TODAS as janelas do Edge (e os processos em segundo plano)")
            print("    e tente de novo.")
            print(f"    Detalhe: {erro}")
            sys.exit(1)

        page = context.new_page()

        for i in range(max_pages):
            jobs = coletar_pagina(page, term, i * 10)
            if not jobs:
                break

            # Guarda só as vagas novas (o Indeed repete algumas entre páginas).
            novos = 0
            for job in jobs:
                chave = job.get("jobkey")
                if chave and chave not in vistos:
                    vistos.add(chave)
                    todas.append(job)
                    novos += 1

            if novos == 0:
                break

        titulo = page.title()
        context.close()
        return todas, titulo


def main():
    term = sys.argv[1] if len(sys.argv) > 1 else "python"

    jobs, titulo = fetch_jobs(term)

    if not jobs:
        print("[x] Nao consegui coletar as vagas.")
        print(f"    Titulo da pagina: {titulo!r}")
        sys.exit(1)

    print(f"[ok] {len(jobs)} vagas encontradas para '{term}':\n")
    for job in jobs[:10]:
        title = job.get("title", "(sem título)")
        company = job.get("company", "(sem empresa)")
        location = job.get("formattedLocation", "")
        print(f" - {title} | {company} | {location}")

    if len(jobs) <= 15:
        print("\n(dica: se esperava mais vagas, confirme que voce esta LOGADO no")
        print(" Indeed nesse perfil do Edge e que o Edge estava fechado ao rodar.)")


if __name__ == "__main__":
    main()
