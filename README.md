# Bots de Vagas de Emprego

Bot que busca vagas de emprego automaticamente e as exibe numa página web, com
caixa de busca por termo. A primeira fonte implementada é a **Gupy**.

> 🚧 **Status:** em desenvolvimento.

## Tecnologias

- **Back-end:** Node.js + Express (organizado em MVC)
- **Coletor (scraper):** Python
- **Front-end:** HTML, CSS e JavaScript (sem framework)

## Como funciona

Ao abrir, a página lê as vagas já salvas no **cache** (`dados/gupy.json`), **sem** rodar o
scraper. Só quando você clica em "Buscar vagas" o servidor executa o scraper Python,
**atualiza o cache** e devolve os resultados.

```
abrir página   ->  GET /jobs          ->  lê o cache (dados/gupy.json)
clicar buscar  ->  GET /search?term=  ->  [Python] coleta -> salva no cache -> mostra
```

## Estrutura

```
botVagas/
├── bots/
│   └── gupy.py                 # coletor (motor): busca na Gupy e imprime JSON
├── src/
│   ├── models/
│   │   ├── gupyModel.js        # ponte que executa o Python
│   │   └── jobsCache.js        # lê/grava o cache de vagas (dados/gupy.json)
│   ├── controllers/
│   │   └── jobsController.js   # recebe o pedido e responde
│   └── routes.js               # define as rotas /jobs e /search
├── public/
│   └── index.html              # página com os cards e a busca
├── dados/
│   └── gupy.json               # cache da última busca
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

## Roadmap

- [ ] Filtros na página (por modelo de trabalho, por palavra)
- [ ] Cálculo de compatibilidade das vagas
- [x] Cache de resultados em `dados/gupy.json`
- [ ] Novas fontes de vagas (ex: Coodesh, Remotar)