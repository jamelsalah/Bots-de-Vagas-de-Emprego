# Bots de Vagas de Emprego

Bot que busca vagas de emprego automaticamente e as exibe numa página web, com
caixa de busca por termo. Hoje coleta de **três fontes**: **Gupy**, **Indeed** e **LinkedIn**.

> 🚧 **Status:** em desenvolvimento.

Na página dá para **filtrar por fonte e por modelo de trabalho** (remoto/híbrido/presencial/outro),
**paginar** os resultados e **excluir** uma vaga pelo ✕ do card (ela vai para uma _blacklist_ e
não volta a aparecer). Os filtros de fonte são montados dinamicamente a partir do back-end, então
adicionar um bot novo já faz o selo e o filtro aparecerem sozinhos. Só são mantidas as vagas
publicadas nos **últimos 45 dias**.

## Tecnologias

- **Back-end:** Node.js + Express (organizado em MVC)
- **Coletores (scrapers):** Python
  - `bots/gupy.py` — API da Gupy (`requests`)
  - `bots/indeed.py` — Indeed via Playwright + Edge logado
  - `bots/linkedin.py` — API _guest_ do LinkedIn (`requests` + BeautifulSoup, sem login)
- **Front-end:** HTML, CSS e JavaScript (sem framework)

## Como funciona

Cada bot é um motor isolado que recebe um termo e **grava as vagas já no formato padrão**
em `data/<source>.json` (o mesmo "contrato" para toda fonte). Ao buscar, o Node roda
**todos os bots** em paralelo e **une** os arquivos numa base unificada `data/jobs.json`.

Ao abrir, a página lê dessa **base unificada** (`data/jobs.json`), **sem** rodar bot. Só quando
você clica em "Buscar vagas" o servidor executa os bots, refaz a base e devolve os resultados.

```
abrir página   ->  GET /jobs          ->  lê a base unificada (data/jobs.json)
clicar buscar  ->  GET /search?term=  ->  roda os bots -> data/<source>.json -> une em data/jobs.json -> mostra
```

### Formato padrão de vaga (o contrato)

Todo bot grava cada vaga com os mesmos campos, não importa a fonte:

```json
{
  "source": "gupy",                 // ou "indeed", "linkedin" — vira o selo no card
  "id": "11473261",
  "title": "Analista de Compras Júnior",
  "company": "Teclean",
  "description": "texto...",
  "location": "Joinville, Santa Catarina",
  "workplaceType": "on-site",       // remote | hybrid | on-site | other
  "publishedDate": "2026-06-11T11:24:23.826Z",
  "url": "https://..."
}
```

## Estrutura

```
botVagas/
├── bots/
│   ├── gupy.py                 # coletor (motor): API da Gupy -> data/gupy.json
│   ├── indeed.py               # coletor do Indeed (Playwright + Edge) -> data/indeed.json
│   └── linkedin.py             # coletor do LinkedIn (API guest) -> data/linkedin.json
├── src/
│   ├── bots.js                 # registro dos bots disponíveis: ["gupy", "indeed", "linkedin"]
│   ├── models/
│   │   ├── botRunner.js        # ponte: runBot(source, term) roda bots/<source>.py
│   │   ├── jobsData.js         # mergeBots() une os data/<source>.json; readJobs() lê a base
│   │   └── blacklist.js        # vagas excluídas pelo usuário (não voltam a aparecer)
│   ├── controllers/
│   │   └── jobsController.js   # recebe o pedido e responde
│   └── routes.js               # define as rotas /jobs, /search e /blacklist
├── public/
│   ├── index.html              # página com os cards (selo da fonte) e a busca
│   ├── app.js                  # filtros, paginação, exclusão de vaga e render dos cards
│   └── style.css               # estilos
├── data/                       # saída dos bots e base unificada (gitignored)
│   ├── gupy.json               # vagas da Gupy no formato padrão
│   ├── indeed.json             # vagas do Indeed no formato padrão
│   ├── linkedin.json           # vagas do LinkedIn no formato padrão
│   ├── jobs.json               # base unificada da última busca (lida pela página)
│   └── blacklist.json          # vagas excluídas pelo usuário
├── server.js                   # sobe o servidor (porta 2424)
├── package.json
└── requirements.txt
```

## Pré-requisitos

- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/) (v3.8+) — de preferência num ambiente virtual `.venv` na raiz
- Microsoft Edge (apenas para o bot do Indeed)

## Como rodar

```bash
# 1. Instalar dependências do Node
npm install

# 2. Criar o venv e instalar as dependências do Python
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install   # navegadores do Playwright (Indeed)

# 3. Subir o servidor
node server.js
```

Depois, abra **http://localhost:2424** no navegador.

> O Node roda os bots pelo **Python do venv** (caminho fixo `.venv\Scripts\python.exe`):
> a máquina pode ter vários Pythons e o do PATH talvez não tenha as dependências.
> Para testar um bot isolado: `.\.venv\Scripts\python.exe bots\gupy.py "python"`.

## Bot do Indeed (instruções especiais)

O Indeed bloqueia coletas simples (Cloudflare/CAPTCHA), então o `bots/indeed.py` usa o
**Playwright** controlando o **Microsoft Edge** já instalado no Windows. Além disso, o Indeed só
mostra a **1ª página** de resultados sem login; para ver as páginas seguintes é preciso estar
**logado**. Como o login do Indeed usa reCAPTCHA (que não funciona em navegador automatizado), o
bot **reaproveita o seu Edge já logado**, em vez de tentar logar sozinho.

Por isso, antes de rodar o bot do Indeed:

1. **Logue no Indeed pelo Edge normal.** Abra o Edge do dia a dia, acesse o
   [Indeed](https://br.indeed.com/) e faça login (e-mail + código). Confirme que ficou logado.
2. **Feche todas as janelas do Edge.** O perfil fica "travado" enquanto o Edge estiver aberto.
3. **Desative o Edge em segundo plano.** O Edge costuma continuar rodando mesmo fechado. Vá em
   `Configurações → Sistema e desempenho` e **desligue**
   *"Continuar executando apps em segundo plano quando o Microsoft Edge é fechado"*.
   (Alternativa: encerre os processos `msedge.exe` pelo Gerenciador de Tarefas.)

Para rodar o coletor manualmente (usando o Python do ambiente virtual `.venv`):

```powershell
.\.venv\Scripts\python.exe bots\indeed.py "python"
```

> Se vier só ~15 vagas, provavelmente a sessão não estava logada ou o Edge ainda estava aberto.
> Se logou em outro perfil do Edge, ajuste `EDGE_PROFILE` no `bots/indeed.py` (ex.: `"Profile 1"`).

## Bot do LinkedIn

O `bots/linkedin.py` usa a **API _guest_** do LinkedIn (a mesma que a página pública de vagas usa
quando você **não** está logado), então **não precisa de login**. Ela devolve os cards de vaga em
HTML, que o bot lê com **BeautifulSoup** e converte para o formato padrão.

```powershell
.\.venv\Scripts\python.exe bots\linkedin.py "python"
```

> Sem login, o LinkedIn tem um teto de requisições: se vier pouca vaga ou um erro **HTTP 429**,
> é só esperar um pouco ou aumentar o intervalo entre páginas (`time.sleep`) no `bots/linkedin.py`.
> O modelo de trabalho costuma ficar como **"Outro"**, pois o card _guest_ não informa
> remoto/híbrido/presencial de forma explícita.

## Roadmap

- [x] Base de dados de resultados em `data/gupy.json`
- [x] Bot do Indeed (Playwright + Edge logado)
- [x] Formato padrão de vaga compartilhado entre os bots
- [x] Base unificada (`data/jobs.json`) reunindo todas as fontes
- [x] Filtros na página (por fonte e por modelo de trabalho) + paginação
- [x] Excluir vaga pelo card (blacklist)
- [x] Bot do LinkedIn (API guest)
- [ ] Cálculo de compatibilidade das vagas
- [ ] Novas fontes de vagas (ex: Coodesh, Remotar)
- [ ] Detectar o modelo de trabalho das vagas do LinkedIn