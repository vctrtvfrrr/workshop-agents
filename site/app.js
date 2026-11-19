const PAGES = {
  guia: { title: "Guia do participante", file: "content/guia-do-participante.md" },
  prompt: { title: "Esqueleto do prompt", file: "content/esqueleto-do-prompt.md" },
  mensagens: { title: "Mensagens de teste", file: "content/mensagens.md" },
};
const DEFAULT_ROUTE = "guia";

const contentElement = document.getElementById("content");
const tocElement = document.getElementById("toc");
const markdownCache = new Map();

function currentRoute() {
  const route = location.hash.replace(/^#\/?/, "");
  return PAGES[route] ? route : DEFAULT_ROUTE;
}

function slugify(text) {
  return text
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

async function loadMarkdown(file) {
  if (!markdownCache.has(file)) {
    const response = await fetch(file, { cache: "no-cache" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    markdownCache.set(file, await response.text());
  }
  return markdownCache.get(file);
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const scratch = document.createElement("textarea");
    scratch.value = text;
    scratch.setAttribute("readonly", "");
    scratch.style.position = "fixed";
    scratch.style.opacity = "0";
    document.body.appendChild(scratch);
    scratch.select();
    document.execCommand("copy");
    scratch.remove();
  }
}

function addCopyButtons() {
  contentElement.querySelectorAll("pre").forEach((pre) => {
    const wrapper = document.createElement("div");
    wrapper.className = "code-block";
    pre.replaceWith(wrapper);
    wrapper.appendChild(pre);

    const button = document.createElement("button");
    button.type = "button";
    button.className = "copy-button";
    button.textContent = "Copiar";
    button.addEventListener("click", async () => {
      await copyText(pre.innerText.replace(/\n$/, ""));
      button.textContent = "Copiado ✓";
      button.classList.add("copied");
      setTimeout(() => {
        button.textContent = "Copiar";
        button.classList.remove("copied");
      }, 1800);
    });
    wrapper.appendChild(button);
  });
}

function wrapTables() {
  contentElement.querySelectorAll("table").forEach((table) => {
    const wrapper = document.createElement("div");
    wrapper.className = "table-wrap";
    table.replaceWith(wrapper);
    wrapper.appendChild(table);
  });
}

function buildTableOfContents() {
  tocElement.replaceChildren();
  contentElement.querySelectorAll("h2").forEach((heading) => {
    heading.id = slugify(heading.textContent);
    const link = document.createElement("a");
    link.href = `#/${currentRoute()}`;
    link.textContent = heading.textContent;
    link.addEventListener("click", (event) => {
      event.preventDefault();
      heading.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    const item = document.createElement("li");
    item.appendChild(link);
    tocElement.appendChild(item);
  });
  document.body.classList.toggle("has-toc", tocElement.children.length > 1);
}

function highlightActiveTab(route) {
  document.querySelectorAll("[data-route]").forEach((tab) => {
    const active = tab.dataset.route === route;
    tab.classList.toggle("active", active);
    if (active) tab.setAttribute("aria-current", "page");
    else tab.removeAttribute("aria-current");
  });
}

async function render() {
  const route = currentRoute();
  const page = PAGES[route];
  highlightActiveTab(route);
  document.title = `${page.title} · Detetive de Golpes`;
  try {
    const markdown = await loadMarkdown(page.file);
    contentElement.innerHTML = marked.parse(markdown);
    wrapTables();
    addCopyButtons();
    buildTableOfContents();
  } catch (error) {
    contentElement.innerHTML = `<p class="error">Não foi possível carregar o conteúdo (${error.message}). Recarregue a página.</p>`;
    tocElement.replaceChildren();
  }
  window.scrollTo({ top: 0 });
}

window.addEventListener("hashchange", render);
render();
