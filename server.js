// Ponto de partida do servidor: sobe o Express e liga as peças.
const express = require("express");
const path = require("path");
const routes = require("./src/routes");

const app = express();
const PORT = 2424;

// VIEW: serve os arquivos estáticos da pasta "public" (o index.html).
app.use(express.static(path.join(__dirname, "public")));

app.use(routes);

const server = app.listen(PORT, () => {
  console.log(`Servidor no ar! Abra http://localhost:${PORT} no navegador.`);
});

// Aviso amigável caso a porta já esteja sendo usada por outro programa.
server.on("error", (error) => {
  if (error.code === "EADDRINUSE") {
    console.error(`A porta ${PORT} já está em uso. Mude a PORTA em server.js e tente de novo.`);
  } else {
    console.error(error);
  }
});
