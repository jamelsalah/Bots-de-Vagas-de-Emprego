// MODEL (ponte): manda o bot Python rodar. O próprio bot grava as vagas em data/gupy.json.
const { execFile } = require("child_process");
const path = require("path");

// Caminho até o script Python (sobe de src/models até a raiz e entra em bots/).
const PYTHON_SCRIPT = path.join(__dirname, "..", "..", "bots", "gupy.py");

function runBot(term) {
  // Promise que resolve quando o bot termina de rodar (e de gravar o JSON).
  return new Promise((resolve, reject) => {
    // Executa: python bots/gupy.py "<termo>"
    execFile("python", [PYTHON_SCRIPT, term], (error) => {
      if (error) {
        return reject(error);
      }
      resolve();
    });
  });
}

module.exports = { runBot };
