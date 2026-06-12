// MODEL (ponte): roda um bot Python pelo nome. O próprio bot grava data/<source>.json.
const { execFile } = require("child_process");
const path = require("path");

// Python do venv (caminho FIXO): a máquina tem vários Pythons e o "python" do PATH
// pode não ter as dependências. Sobe de src/models até a raiz e entra em .venv.
const PYTHON = path.join(__dirname, "..", "..", ".venv", "Scripts", "python.exe");

function runBot(source, term) {
  // Monta o caminho do script: bots/<source>.py
  const script = path.join(__dirname, "..", "..", "bots", `${source}.py`);

  return new Promise((resolve, reject) => {
    execFile(PYTHON, [script, term], (error) => {
      if (error) {
        return reject(error);
      }
      resolve();
    });
  });
}

module.exports = { runBot };
