// Ponto de partida do servidor: sobe o Express e liga as peças.
const express = require("express");
const path = require("path");
const rotas = require("./src/rotas");

const app = express();
const PORTA = 3333;

// VIEW: serve os arquivos estáticos da pasta "public" (o index.html).
app.use(express.static(path.join(__dirname, "public")));

// CONTROLLER: as rotas que respondem a pedidos de dados (ex: /buscar).
app.use(rotas);

const servidor = app.listen(PORTA, () => {
  console.log(`Servidor no ar! Abra http://localhost:${PORTA} no navegador.`);
});

// Aviso amigável caso a porta já esteja sendo usada por outro programa.
servidor.on("error", (erro) => {
  if (erro.code === "EADDRINUSE") {
    console.error(`A porta ${PORTA} já está em uso. Mude a PORTA em server.js e tente de novo.`);
  } else {
    console.error(erro);
  }
});
