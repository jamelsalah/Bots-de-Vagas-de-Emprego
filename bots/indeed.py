import sys

from playwright.sync_api import sync_playwright

# Página de busca do Indeed Brasil. O termo vai no parâmetro ?q=.
SEARCH_URL = "https://br.indeed.com/jobs?q={term}"

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


def fetch_jobs(term):
    with sync_playwright() as p:
        # Usamos o Microsoft Edge já instalado no Windows (channel="msedge"): é Chromium
        # de verdade e evita o bug de "side-by-side" do Chromium baixado pelo Playwright.
        # headless=False (janela visível) ajuda a passar pelo anti-robô do Indeed.
        browser = p.chromium.launch(channel="msedge", headless=False)
        context = browser.new_context(
            locale="pt-BR",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        page.goto(SEARCH_URL.format(term=term), timeout=60000)

        # Espera o JS das vagas existir na página (Cloudflare pode demorar uns segundos).
        try:
            page.wait_for_function(JOBCARDS_JS, timeout=30000)
            jobs = page.evaluate(JOBCARDS_JS)
        except Exception:
            jobs = None

        titulo = page.title()
        browser.close()
        return jobs, titulo


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


if __name__ == "__main__":
    main()
