// MODEL (ponte): executa o bot Python e devolve as vagas já em objeto JS.
const { execFile } = require("child_process");
const path = require("path");

// Caminho até o script Python (sobe de src/models até a raiz e entra em coletor/).
const SCRIPT_PYTHON = path.join(__dirname, "..", "..", "bots", "gupy.py");

function coletarVagas(termo) {
  // Envolvemos em uma Promise para poder usar "await" no controller.
  return new Promise((resolve, reject) => {
    // Executa: python coletor/gupy.py "<termo>"
    // maxBuffer aumentado porque a resposta (com descrições) é grande.
    const opcoes = { maxBuffer: 10 * 1024 * 1024 };

    execFile("python", [SCRIPT_PYTHON, termo], opcoes, (erro, stdout) => {
      if (erro) {
        return reject(erro);
      }
      try {
        // O Python imprimiu JSON; aqui transformamos em objeto JavaScript.
        resolve(JSON.parse(stdout));
      } catch (e) {
        reject(e);
      }
    });
  });
}

module.exports = { coletarVagas };
