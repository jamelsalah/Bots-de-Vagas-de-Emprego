# Bots de Vagas de Emprego

Bot que busca vagas de emprego automaticamente e as exibe numa página web, com
caixa de busca por termo. A primeira fonte implementada é a **Gupy**.

> 🚧 **Status:** em desenvolvimento.

## Tecnologias

- **Back-end:** Node.js + Express (organizado em MVC)
- **Coletor (scraper):** Python
- **Front-end:** HTML, CSS e JavaScript (sem framework)

## Como funciona

Ao abrir, a página lê as vagas já salvas na **base de dados** (`data/gupy.json`), **sem** rodar o
scraper. Só quando você clica em "Buscar vagas" o servidor executa o scraper Python,
**atualiza a base de dados** e devolve os resultados.

```
abrir página   ->  GET /jobs          ->  lê a base de dados (data/gupy.json)
clicar buscar  ->  GET /search?term=  ->  [Python] coleta -> salva na base de dados -> mostra
```

## Estrutura

```
botVagas/
├── bots/
│   ├── gupy.py                 # coletor (motor): busca na Gupy e imprime JSON
│   └── indeed.py               # coletor do Indeed (via Playwright + Edge logado)
├── src/
│   ├── models/
│   │   ├── gupyModel.js        # ponte que executa o Python
│   │   └── jobsData.js         # lê/grava a base de dados de vagas (data/gupy.json)
│   ├── controllers/
│   │   └── jobsController.js   # recebe o pedido e responde
│   └── routes.js               # define as rotas /jobs e /search
├── public/
│   └── index.html              # página com os cards e a busca
├── data/
│   └── gupy.json               # base de dados da última busca
├── server.js                   # sobe o servidor (porta 2424)
├── package.json
└── requirements.txt
```

## Pré-requisitos

- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/) (v3.8+) acessível no PATH

## Como rodar

```bash
# 1. Instalar dependências do Node
npm install

# 2. Instalar dependências do Python
pip install -r requirements.txt

# 3. Subir o servidor
node server.js
```

Depois, abra **http://localhost:2424** no navegador.

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

## Roadmap

- [ ] Filtros na página (por modelo de trabalho, por palavra)
- [ ] Cálculo de compatibilidade das vagas
- [x] Base de dados de resultados em `data/gupy.json`
- [x] Bot do Indeed (Playwright + Edge logado)
- [ ] Novas fontes de vagas (ex: Coodesh, Remotar)