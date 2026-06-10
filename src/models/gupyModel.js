// MODEL (ponte): executa o bot Python e devolve as vagas já em objeto JS.
const { execFile } = require("child_process");
const path = require("path");

// Caminho até o script Python (sobe de src/models até a raiz e entra em bots/).
const PYTHON_SCRIPT = path.join(__dirname, "..", "..", "bots", "gupy.py");

function collectJobs(term) {
  // Envolvemos em uma Promise para poder usar "await" no controller.
  return new Promise((resolve, reject) => {
    // Executa: python bots/gupy.py "<termo>"
    // maxBuffer aumentado porque a resposta (com descrições) é grande.
    const options = { maxBuffer: 10 * 1024 * 1024 };

    execFile("python", [PYTHON_SCRIPT, term], options, (error, stdout) => {
      if (error) {
        return reject(error);
      }
      try {
        // O Python imprimiu JSON; aqui transformamos em objeto JavaScript.
        resolve(JSON.parse(stdout));
      } catch (parseError) {
        reject(parseError);
      }
    });
  });
}

module.exports = { collectJobs };
