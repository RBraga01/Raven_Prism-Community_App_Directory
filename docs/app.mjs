import {
  DEFAULT_STATE, parseFilters, serializeFilters,
  filterCatalog, catalogInsights, hasActiveFilters
} from "./catalog-core.mjs";

const $ = (id) => document.getElementById(id);
const elements = {
  form: $("search-form"), search: $("search"), clearSearch: $("clear-search"), submitSearch: $("submit-search"),
  category: $("category-filter"), availability: $("availability-filter"),
  sort: $("sort-filter"), demo: $("demo-filter"),
  reset: $("reset-filters"), count: $("results-count"),
  cards: $("cards"), active: $("active-filters"),
  viewGrid: $("view-grid"), viewList: $("view-list"),
  categoryChart: $("category-chart"),
  availabilityBreakdown: $("availability-breakdown"),
  error: $("load-error"), retry: $("retry-load"),
  share: $("share-search")
};
let state = parseFilters(window.location.search);
let apps = [];
let loaded = false;

function create(tag, className = "", text = "") {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (text) el.textContent = text;
  return el;
}

function publicLink(label, url, className = "") {
  const a = create("a", className, label);
  // URLs are validated in CI; repeat scheme and credential checks at render time.
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== "https:" || parsed.username || parsed.password)
      throw new Error("Unsafe public link");
    a.href = parsed.href;
  } catch {
    a.href = "#directory";
    a.setAttribute("aria-disabled", "true");
  }
  a.target = "_blank";
  a.rel = "noopener noreferrer";
  return a;
}

function syncURL() {
  const url = new URL(window.location.href);
  url.search = serializeFilters(state);
  window.history.replaceState(null, "", url.pathname + url.search + url.hash);
}

function updateState(patch, scrollToResults = false) {
  state = { ...state, ...patch };
  syncURL();
  updateControls();
  if (loaded) renderResults();
  if (scrollToResults) $("directory").scrollIntoView({ behavior: "auto" });
}

function updateControls() {
  if (elements.search.value !== state.q) elements.search.value = state.q;
  elements.clearSearch.hidden = !state.q;
  elements.category.value = state.category;
  elements.availability.value = state.availability;
  elements.sort.value = state.sort;
  elements.demo.checked = state.demoOnly;
  elements.reset.hidden = !hasActiveFilters(state);
  elements.viewGrid.setAttribute("aria-pressed", String(state.view === "grid"));
  elements.viewList.setAttribute("aria-pressed", String(state.view === "list"));
}

function supplementalLabel(url) {
  try {
    const path = new URL(url).pathname.toLowerCase();
    if (path.includes("/releases/")) return "Release";
    if (path.endsWith(".mp4")) return "Watch video";
    if (url.includes("youtube.com") || url.includes("youtu.be")) return "Watch video";
    if (url.includes("devpost.com")) return "Project page";
  } catch { /* Validation prevents unsafe URLs in approved catalog entries. */ }
  return "More details";
}

function createCard(app) {
  const card = create("article", "app-card");
  const top = create("div", "app-card-top");
  top.append(
    create("span", "category-tag", app.category),
    create("span", "availability-tag", app.availability)
  );
  const h3 = create("h3");
  h3.append(publicLink(app.name, app.source_url));
  const creator = create("div", "creator", "By " + app.developer);
  const description = create("p", "description", app.description);
  const links = create("div", "card-links");
  links.append(publicLink("View source", app.source_url));
  if (app.demo_url) links.append(publicLink(supplementalLabel(app.demo_url) + "", app.demo_url));
  card.append(top, h3, creator, description, links);
  return card;
}

function activeChip(label, patch) {
  const button = create("button", "", label + " ×");
  button.type = "button";
  button.setAttribute("aria-label", "Remove " + label + " filter");
  button.addEventListener("click", () => updateState(patch));
  return button;
}

function renderActiveFilters() {
  const chips = [];
  if (state.q) chips.push(activeChip("Search: " + state.q, { q: "" }));
  if (state.category) chips.push(activeChip(state.category, { category: "" }));
  if (state.availability) chips.push(activeChip(state.availability, { availability: "" }));
  if (state.demoOnly) chips.push(activeChip("Additional public link", { demoOnly: false }));
  elements.active.replaceChildren(...chips);
  elements.active.hidden = chips.length === 0;
}

function renderResults() {
  const found = filterCatalog(apps, state);
  elements.cards.classList.toggle("list", state.view === "list");
  elements.cards.setAttribute("aria-busy", "false");
  elements.count.replaceChildren(
    document.createTextNode(found.length + " of " + apps.length + " applications"),
    create("small", "", found.length === apps.length ? " · Browse all" : " · Matching filters")
  );
  renderActiveFilters();
  if (found.length === 0) {
    const empty = create("div", "empty");
    const title = create("strong", "", "No matches found");
    const detail = create("p", "", "Try a different keyword or remove a filter.");
    const reset = create("button", "outline-link", "Clear filters");
    reset.type = "button";
    reset.addEventListener("click", () => updateState({ ...DEFAULT_STATE, view: state.view }));
    empty.append(title, detail, reset);
    elements.cards.replaceChildren(empty);
    return;
  }
  const fragment = document.createDocumentFragment();
  found.forEach((item) => fragment.append(createCard(item)));
  elements.cards.replaceChildren(fragment);
}

function renderInsights() {
  const info = catalogInsights(apps);
  $("metric-apps").textContent = String(info.total);
  $("metric-categories").textContent = String(info.categoryCount);
  $("metric-creators").textContent = String(info.creatorLabels);
  $("metric-demos").textContent = String(info.additionalLinks);

  elements.categoryChart.replaceChildren();
  const max = Math.max(1, ...info.categories.map((item) => item.count));
  for (const item of info.categories) {
    const b = create("button", "bar-item");
    b.type = "button";
    b.setAttribute("aria-label", "View " + item.count + " applications in " + item.name);
    const caption = create("span", "bar-caption");
    caption.append(create("span", "", item.name), create("strong", "", String(item.count)));
    const track = create("span", "bar-track");
    const fill = create("span", "bar-fill");
    fill.style.width = (100 * item.count / max).toFixed(1) + "%";
    fill.setAttribute("aria-hidden", "true");
    track.append(fill);
    b.append(caption, track);
    b.addEventListener("click", () => updateState({ category: item.name, q: "", availability: "", demoOnly: false, sort: "name" }, true));
    elements.categoryChart.append(b);
  }

  elements.availabilityBreakdown.replaceChildren();
  for (const item of info.availability) {
    const line = create("div", "breakdown-line");
    line.append(create("span", "", item.name), create("strong", "", String(item.count)));
    elements.availabilityBreakdown.append(line);
  }
  const repoLine = create("div", "breakdown-line");
  repoLine.append(
    create("span", "", "Distinct GitHub source repositories"),
    create("strong", "", String(info.sourceRepositories))
  );
  elements.availabilityBreakdown.append(repoLine);
}

function setUpControls() {
  elements.search.addEventListener("input", () => updateState({ q: elements.search.value }));
  elements.form.addEventListener("submit", (event) => {
    event.preventDefault();
    updateState({ q: elements.search.value }, true);
  });
  elements.clearSearch.addEventListener("click", () => {
    updateState({ q: "" });
    elements.search.focus();
  });
  elements.category.addEventListener("change", () => updateState({ category: elements.category.value }));
  elements.availability.addEventListener("change", () => updateState({ availability: elements.availability.value }));
  elements.sort.addEventListener("change", () => updateState({ sort: elements.sort.value }));
  elements.demo.addEventListener("change", () => updateState({ demoOnly: elements.demo.checked }));
  elements.reset.addEventListener("click", () => updateState({ ...DEFAULT_STATE, view: state.view }));
  elements.viewGrid.addEventListener("click", () => updateState({ view: "grid" }));
  elements.viewList.addEventListener("click", () => updateState({ view: "list" }));
  elements.retry.addEventListener("click", loadCatalog);
  document.querySelectorAll("[data-search]").forEach((button) =>
    button.addEventListener("click", () => {
      updateState({ q: button.dataset.search }, true);
      elements.search.focus({ preventScroll: true });
    })
  );
  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      elements.search.focus();
      elements.search.select();
    }
    if (event.key === "Escape" && document.activeElement === elements.search && state.q) {
      updateState({ q: "" });
    }
  });
  elements.share.addEventListener("click", async () => {
    const url = window.location.href;
    const original = elements.share.textContent;
    try {
      if (!navigator.clipboard?.writeText) throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText(url);
      elements.share.textContent = "Link copied ✓";
    } catch {
      // Direct user action; prompt is only a fallback for browsers without Clipboard API.
      window.prompt("Copy this filtered directory link:", url);
      elements.share.textContent = "Copy filtered link";
    }
    window.setTimeout(() => { elements.share.textContent = original; }, 2000);
  });
  window.addEventListener("popstate", () => {
    state = parseFilters(window.location.search);
    updateControls();
    if (loaded) renderResults();
  });
  updateControls();
}

async function loadCatalog() {
  elements.error.hidden = true;
  elements.cards.hidden = false;
  elements.cards.setAttribute("aria-busy", "true");
  elements.count.textContent = "Loading the directory…";
  try {
    const response = await fetch("./apps.json", { cache: "no-cache" });
    if (!response.ok) throw new Error("Catalog HTTP " + response.status);
    const data = await response.json();
    if (!Array.isArray(data) || data.some((app) =>
      !app || typeof app.name !== "string" ||
      typeof app.category !== "string" ||
      typeof app.source_url !== "string"
    )) throw new Error("Invalid catalog data");
    apps = data;
    loaded = true;
    const info = catalogInsights(apps);
    const allCategories = create("option", "", "All categories");
    allCategories.value = "";
    elements.category.replaceChildren(allCategories);
    for (const item of [...info.categories].sort((a, b) => a.name.localeCompare(b.name, "en"))) {
      const option = create("option", "", item.name + " (" + item.count + ")");
      option.value = item.name;
      elements.category.append(option);
    }
    if (state.category && !info.categories.some((item) => item.name === state.category))
      state.category = "";
    if (state.availability && !info.availability.some((item) => item.name === state.availability))
      state.availability = "";
    syncURL();
    updateControls();
    renderInsights();
    renderResults();
  } catch {
    loaded = false;
    elements.cards.hidden = true;
    elements.cards.setAttribute("aria-busy", "false");
    elements.count.textContent = "Directory unavailable";
    elements.error.hidden = false;
  }
}

setUpControls();
loadCatalog();
