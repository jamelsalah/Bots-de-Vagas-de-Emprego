// ============================================================
// DADOS: estado da exibição (filtros + paginação)
// ============================================================
const PAGE_SIZE = 50;             // cards por página
let allJobs = [];                 // base completa vinda do servidor (nunca filtrada)
let viewJobs = [];                // base já filtrada/ordenada que será paginada
let currentPage = 1;              // página atual da exibição
let activeSources = new Set();    // fontes ligadas (vazio = todas)
let activeModes = new Set();      // modelos ligados (vazio = todos)

// ============================================================
// FUNÇÕES: cada uma atua sobre os dados acima
// ============================================================

// Traduz o código do modelo de trabalho para texto e classe de cor
function translateMode(type) {
  if (type === "remote")  return { text: "Remoto",     cssClass: "mode-remote" };
  if (type === "hybrid")  return { text: "Híbrido",    cssClass: "mode-hybrid" };
  if (type === "on-site") return { text: "Presencial", cssClass: "mode-onsite" };
  return { text: "Outro", cssClass: "mode-other" };
}

// Transforma a data "2026-06-09T13:48:11Z" em "09/06/2026"
function formatDate(isoDate) {
  return new Date(isoDate).toLocaleDateString("pt-BR");
}

// Deixa o nome da fonte bonito para o selo: "gupy" -> "Gupy"
function sourceLabel(source) {
  if (!source) return "";
  return source[0].toUpperCase() + source.slice(1);
}

// Cores das fontes: marcas conhecidas + cor estável gerada do nome (novas fontes).
const SOURCE_COLORS = { gupy: "#d6336c", indeed: "#2557a7", linkedin: "#0a66c2" };

function sourceColor(source) {
  if (SOURCE_COLORS[source]) return SOURCE_COLORS[source];
  let soma = 0;
  for (let i = 0; i < source.length; i++) soma += source.charCodeAt(i);
  return `hsl(${soma % 360}, 55%, 45%)`; // matiz derivado do nome
}

// Monta os botões do filtro de fonte ("Todas" + uma por bot cadastrado no backend).
function buildSourceFilters(sources) {
  const group = document.getElementById("source-filters");
  let html = '<button class="filter-btn active" data-axis="source" data-value="all">Todas</button>';
  for (const source of (sources || [])) {
    html += `<button class="filter-btn" data-axis="source" data-value="${source}">${sourceLabel(source)}</button>`;
  }
  group.innerHTML = html;
}

// Monta o HTML de UM card a partir de UMA vaga (formato padrão)
function createCard(job) {
  const mode = translateMode(job.workplaceType);

  // Pré-monta os textos opcionais (resumo e data) antes de jogar no template.
  let description = "";
  if (job.description) {
    description = job.description.slice(0, 180) + "...";
  }

  let publishedInfo = "";
  if (job.publishedDate) {
    publishedInfo = "Publicada em " + formatDate(job.publishedDate);
  }

  const card = document.createElement("div");
  card.className = "job-card " + mode.cssClass;
  card.innerHTML = `
    <div class="card-header">
      <h2 class="job-title">${job.title}</h2>
      <div class="header-actions">
        <span class="mode-badge">${mode.text}</span>
        <button class="delete-btn" data-source="${job.source}" data-id="${job.id}" title="Excluir vaga">✕</button>
      </div>
    </div>
    <p class="company">
      <span class="source-badge" style="background: ${sourceColor(job.source)}">${sourceLabel(job.source)}</span>
      ${job.company}
    </p>
    <p class="job-location">${job.location || ""}</p>
    <p class="job-description">${description}</p>
    <div class="card-footer">
      <span class="date">${publishedInfo}</span>
      <a class="job-link" href="${job.url}" target="_blank">Ver vaga →</a>
    </div>
  `;
  return card;
}

// Desenha na tela a lista de vagas recebida (limpando o que havia antes).
function renderJobs(jobsList) {
  const container = document.getElementById("jobs-list");
  container.innerHTML = ""; // limpa os cards antigos

  jobsList.map(job => {
    container.appendChild(createCard(job));
  });
}

// Comparador: mais recentes primeiro (publishedDate decrescente).
function byNewest(a, b) {
  return new Date(b.publishedDate) - new Date(a.publishedDate);
}

// Filtra a base pelos dois eixos (AND). Dentro de um eixo, conjunto vazio = "todos";
// senão a vaga passa se o conjunto contém o seu valor (multisseleção: vários ligados).
function applyFilter() {
  viewJobs = allJobs.filter(job =>
    (activeSources.size === 0 || activeSources.has(job.source)) &&
    (activeModes.size === 0 || activeModes.has(job.workplaceType))
  ).sort(byNewest);

  currentPage = 1;
  renderPage();
}

// Clique num filtro: liga/desliga o valor no eixo, ajusta os destaques e reaplica.
function setFilter(axis, value, button) {
  const selected = axis === "source" ? activeSources : activeModes;

  if (value === "all") {
    selected.clear();                // "Todas/Todos" limpa o eixo
  } else if (selected.has(value)) {
    selected.delete(value);          // já ligado -> desliga
  } else {
    selected.add(value);             // desligado -> liga
  }

  // Destaque: "Todas/Todos" aceso quando nada selecionado; senão, os escolhidos.
  for (const btn of button.parentElement.children) {
    const v = btn.dataset.value;
    let isActive = selected.has(v);
    if (v === "all") isActive = selected.size === 0;
    btn.classList.toggle("active", isActive);
  }

  applyFilter();
}

// Desenha a página atual: fatia viewJobs, renderiza os cards e a barra de páginas.
function renderPage() {
  const totalPages = Math.max(1, Math.ceil(viewJobs.length / PAGE_SIZE));
  if (currentPage > totalPages) currentPage = totalPages;

  const start = (currentPage - 1) * PAGE_SIZE;
  renderJobs(viewJobs.slice(start, start + PAGE_SIZE));
  renderPaginationButtons(totalPages);
}

// Monta o HTML dos botões UMA vez e coloca nas duas barras (topo e rodapé).
function renderPaginationButtons(totalPages) {
  let html = "";
  if (totalPages > 1) {
    let noPrev = "";
    if (currentPage === 1) noPrev = "disabled";

    let noNext = "";
    if (currentPage === totalPages) noNext = "disabled";

    html += `<button class="page-btn" data-page="${currentPage - 1}" ${noPrev}>‹ Anterior</button>`;
    for (let n = 1; n <= totalPages; n++) {
      let isActive = "";
      if (n === currentPage) isActive = "active";
      html += `<button class="page-btn ${isActive}" data-page="${n}">${n}</button>`;
    }
    html += `<button class="page-btn" data-page="${currentPage + 1}" ${noNext}>Próxima ›</button>`;
  }

  document.getElementById("pagination-top").innerHTML = html;
  document.getElementById("pagination").innerHTML = html;
}

// Vai para a página n (chamada pelos botões), redesenha e rola ao topo da lista.
function goToPage(n) {
  currentPage = n;
  renderPage();
  document.getElementById("jobs-list").scrollIntoView({ behavior: "smooth", block: "start" });
}

// Carrega as vagas na base e reinicia a visualização do zero:
// guarda a base completa, zera os filtros e manda renderizar.
function resetView(jobs) {
  allJobs = jobs;
  activeSources.clear();
  activeModes.clear();
  document.querySelectorAll(".filter-btn").forEach(b => b.classList.toggle("active", b.dataset.value === "all"));
  applyFilter();
}

// Resumo da busca: repõe o termo na caixa e escreve a contagem no contador.
function showSummary(data) {
  const jobs = data.jobs || [];
  const counter = document.getElementById("jobs-count");

  // Se a base de dados guardou o termo, repõe na caixa de busca.
  if (data.term) {
    document.getElementById("search-input").value = data.term;
  }

  // Base vazia: avisa no contador (o resetView limpa lista e paginação).
  if (jobs.length === 0) {
    counter.textContent = "Nenhuma vaga salva ainda — clique em Buscar";
    return;
  }

  let text = jobs.length + " vagas";
  if (data.fetchedAt) {
    text += " · atualizado em " + new Date(data.fetchedAt).toLocaleString("pt-BR");
  }
  counter.textContent = text;
}

// Ao abrir a página: lê as vagas já salvas na base de dados (NÃO rebusca).
async function loadData() {
  const response = await fetch("/jobs");
  const data = await response.json();

  buildSourceFilters(data.sources); // monta os botões de fonte a partir do backend
  showSummary(data);                // resumo no contador (+ repõe o termo)
  resetView(data.jobs || []);       // base + render (limpa sozinho quando vazio)
}

// Botão: rebusca na fonte com o termo digitado, salva na base de dados e mostra.
async function searchJobs() {
  const term = document.getElementById("search-input").value || "python";
  const button = document.getElementById("search-button");

  button.disabled = true;
  button.textContent = "Buscando...";
  document.getElementById("jobs-count").textContent = "buscando...";

  try {
    const response = await fetch("/search?term=" + encodeURIComponent(term));
    const data = await response.json();
    buildSourceFilters(data.sources); // monta os botões de fonte a partir do backend
    showSummary(data);                // resumo no contador (+ repõe o termo)
    resetView(data.jobs || []);       // base + render
  } catch (error) {
    document.getElementById("jobs-count").textContent = "Erro ao buscar. O servidor está rodando?";
  }

  button.disabled = false;
  button.textContent = "Buscar vagas";
}

// Exclui uma vaga: manda para a blacklist no servidor e some na hora da tela.
async function excludeJob(source, id) {
  await fetch("/blacklist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source, id }),
  });

  // Tira da base local e redesenha (filtros e paginação se reajustam sozinhos).
  allJobs = allJobs.filter((job) => !(job.source === source && String(job.id) === String(id)));
  applyFilter();
  document.getElementById("jobs-count").textContent = allJobs.length + " vagas";
}

// ============================================================
// INIT: liga os eventos (sem onclick no HTML) e carrega os dados
// ============================================================
function init() {
  // Busca: clique no botão dispara a rebusca.
  document.getElementById("search-button").addEventListener("click", searchJobs);

  // Filtros: um listener no container cobre os dois eixos (source/mode).
  // Cada botão carrega data-axis e data-value; clique fora de botão é ignorado.
  document.getElementById("filters").addEventListener("click", (event) => {
    const button = event.target.closest(".filter-btn");
    if (!button) return;
    setFilter(button.dataset.axis, button.dataset.value, button);
  });

  // Paginação: um listener em cada barra (topo e rodapé) lê o data-page do botão.
  document.querySelectorAll(".pagination").forEach((bar) => {
    bar.addEventListener("click", (event) => {
      const button = event.target.closest(".page-btn");
      if (!button || button.disabled) return;
      goToPage(Number(button.dataset.page));
    });
  });

  // Lixeira: um listener delegado na lista cobre todos os cards (atuais e futuros).
  document.getElementById("jobs-list").addEventListener("click", (event) => {
    const button = event.target.closest(".delete-btn");
    if (!button) return;
    excludeJob(button.dataset.source, button.dataset.id);
  });

  // Por fim, carrega a base de dados já salva (sem rebuscar).
  loadData();
}

init();
