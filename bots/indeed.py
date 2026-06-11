import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

# Página de busca do Indeed Brasil. O termo vai em ?q= e a paginação em &start=.
SEARCH_URL = "https://br.indeed.com/jobs?q={term}&start={start}"

# Reaproveitamos o SEU Edge já logado no Indeed. O login do Indeed exige reCAPTCHA,
# que NÃO funciona em navegador automatizado — então o login é feito por você no Edge
# normal, e aqui o bot abre o MESMO perfil (com os cookies de login já gravados),
# pulando o login inteiro. Assim o reCAPTCHA nunca é acionado.
#
#   >>> IMPORTANTE: feche TODAS as janelas do Edge antes de rodar o bot. <<<
#   (o perfil fica "travado" enquanto o Edge estiver aberto; se o Edge continua
#    rodando em segundo plano, desligue em: Configurações > Sistema e desempenho >
#    "Continuar executando apps em segundo plano quando o Microsoft Edge é fechado".)
#
# Se você logou em outro perfil do Edge, troque "Default" por "Profile 1", etc.
EDGE_USER_DATA = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Edge" / "User Data"
EDGE_PROFILE = "Default"

# Quantas páginas percorrer (cada página traz ~15 vagas). 5 páginas ≈ 75 vagas.
# A 1ª página é pública; da 2ª em diante o Indeed exige estar logado (vem do perfil).
MAX_PAGES = 5

# O Indeed bloqueia requests "secos" (Cloudflare/CAPTCHA), então usamos um
# navegador Chromium de verdade via Playwright. As vagas ficam embutidas numa
# variável JavaScript da própria página: window.mosaic.providerData.
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

# Estrutura de cada vaga retornada pelo Indeed (dicionário Python).
# A vaga vem com ~110 campos; abaixo só os úteis para o nosso projeto.
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
    # Abre uma página de resultados e devolve a lista de vagas (ou None se não vier).
    page.goto(SEARCH_URL.format(term=term, start=start), timeout=60000)
    try:
        page.wait_for_function(JOBCARDS_JS, timeout=30000)
        return page.evaluate(JOBCARDS_JS)
    except Exception:
        return None


def fetch_jobs(term, max_pages=MAX_PAGES):
    todas = []
    vistos = set()  # jobkeys já coletados, para não repetir vagas entre páginas

    # Mantemos os mascaramentos: Stealth() disfarça as "pegadas" do Playwright
    # (navigator.webdriver, plugins, WebGL...) em toda página criada, ajudando a
    # não disparar o "Security Check" do Cloudflare durante a paginação.
    with Stealth().use_sync(sync_playwright()) as p:
        # Abre o Edge usando o SEU perfil (que já tem o login do Indeed).
        # channel="msedge" usa o Edge instalado; --disable-blink-features=AutomationControlled
        # remove o sinal mais óbvio de automação.
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

        # Percorre as páginas: start = 0, 10, 20, ... (mesma aba).
        for i in range(max_pages):
            start = i * 10
            jobs = coletar_pagina(page, term, start)

            # Página vazia: fim dos resultados, bloqueio, ou sessão não logada.
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

            # Nenhuma vaga nova nesta página: chegamos ao fim dos resultados.
            if novos == 0:
                break

        titulo = page.title()
        context.close()
        return todas, titulo


def main():
    # O termo de busca vem como argumento. Ex: python bots/indeed.py "python"
    term = sys.argv[1] if len(sys.argv) > 1 else "python"

    jobs, titulo = fetch_jobs(term)

    # Diagnóstico: se não achamos as vagas, provavelmente fomos bloqueados.
    if not jobs:
        print("[x] Nao consegui coletar as vagas.")
        print(f"    Titulo da pagina: {titulo!r}")
        sys.exit(1)

    # Funcionou: imprime um resumo para validarmos a coleta (Fase 1).
    print(f"[ok] {len(jobs)} vagas encontradas para '{term}':\n")

    for job in jobs[:10]:
        title = job.get("title", "(sem título)")
        company = job.get("company", "(sem empresa)")
        location = job.get("formattedLocation", "")
        print(f" - {title} | {company} | {location}")

    # Dica: se veio só ~15 (uma página), a sessão pode não estar logada.
    if len(jobs) <= 15:
        print("\n(dica: se esperava mais vagas, confirme que voce esta LOGADO no")
        print(" Indeed nesse perfil do Edge e que o Edge estava fechado ao rodar.)")


if __name__ == "__main__":
    main()
