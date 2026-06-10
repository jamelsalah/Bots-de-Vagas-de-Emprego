# Bots de Vagas de Emprego

Bot que busca vagas de emprego automaticamente e as exibe numa página web, com
caixa de busca por termo. A primeira fonte implementada é a **Gupy**.

> 🚧 **Status:** em desenvolvimento.

## Tecnologias

- **Back-end:** Node.js + Express (organizado em MVC)
- **Coletor (scraper):** Python
- **Front-end:** HTML, CSS e JavaScript (sem framework)

## Como funciona

A página chama o servidor Node, que executa o scraper Python sob demanda. O Python
coleta as vagas e devolve em JSON, que o Node entrega de volta para a página montar
os cards.

```
[Página] --/buscar?termo=--> [Express] --executa--> [Python] --JSON--> [Página]
```

## Estrutura

```
botVagas/
├── bots/
│   └── gupy.py                 # coletor (motor): busca na Gupy e imprime JSON
├── src/
│   ├── models/gupyModel.js     # ponte que executa o Python
│   ├── controllers/
│   │   └── vagasController.js  # recebe o pedido e responde
│   └── rotas.js                # define a rota /buscar
├── public/
│   └── index.html              # página com os cards e a busca
├── dados/                      # cache e configurações (uso futuro)
├── server.js                   # sobe o servidor (porta 3333)
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

Depois, abra **http://localhost:3333** no navegador.

## Roadmap

- [ ] Filtros na página (por modelo de trabalho, por palavra)
- [ ] Cálculo de compatibilidade das vagas
- [ ] Cache de resultados na pasta `dados/`
- [ ] Novas fontes de vagas (ex: Coodesh, Remotar)
- [ ] Armazenamento persistente (Supabase)
