// Pure, dependency-free catalog discovery. Shared by the website and Node tests.
const collator = new Intl.Collator("en", { sensitivity: "base", numeric: true });
export const DEFAULT_STATE = Object.freeze({
  q: "", category: "", availability: "", demoOnly: false,
  sort: "name", view: "grid"
});
export const SORTS = new Set(["name", "relevance", "category", "creator"]);
export const VIEWS = new Set(["grid", "list"]);

export function normalize(value) {
  return String(value ?? "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("en")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

export function parseFilters(queryString = "") {
  const params = new URLSearchParams(String(queryString).replace(/^\?/, ""));
  const sort = params.get("sort") || DEFAULT_STATE.sort;
  const view = params.get("view") || DEFAULT_STATE.view;
  return {
    q: (params.get("q") || "").slice(0, 120).trim(),
    category: (params.get("category") || "").slice(0, 100),
    availability: (params.get("availability") || "").slice(0, 80),
    demoOnly: params.get("demo") === "1",
    sort: SORTS.has(sort) ? sort : DEFAULT_STATE.sort,
    view: VIEWS.has(view) ? view : DEFAULT_STATE.view
  };
}

export function serializeFilters(state) {
  const params = new URLSearchParams();
  if (state.q?.trim()) params.set("q", state.q.trim().slice(0, 120));
  if (state.category) params.set("category", state.category);
  if (state.availability) params.set("availability", state.availability);
  if (state.demoOnly) params.set("demo", "1");
  if (state.sort && state.sort !== DEFAULT_STATE.sort && SORTS.has(state.sort))
    params.set("sort", state.sort);
  if (state.view === "list") params.set("view", "list");
  return params.toString();
}

function termScore(item, token) {
  const name = normalize(item.name);
  const developer = normalize(item.developer);
  const category = normalize(item.category);
  const description = normalize(item.description);
  const availability = normalize(item.availability);
  if (name === token) return 20;
  if (name.startsWith(token)) return 12;
  if (name.includes(token)) return 9;
  if (category.includes(token)) return 6;
  if (developer.includes(token)) return 5;
  if (availability.includes(token)) return 3;
  if (description.includes(token)) return 2;
  return 0;
}

export function filterCatalog(catalog, state = DEFAULT_STATE) {
  const tokens = normalize(state.q || "").split(" ").filter(Boolean);
  let results = catalog.filter((app) => (
    (!state.category || app.category === state.category) &&
    (!state.availability || app.availability === state.availability) &&
    (!state.demoOnly || Boolean(app.demo_url)) &&
    tokens.every((token) => termScore(app, token) > 0)
  ));
  results = results.slice();
  results.sort((a, b) => {
    if (state.sort === "relevance" && tokens.length) {
      const rankA = tokens.reduce((sum, word) => sum + termScore(a, word), 0);
      const rankB = tokens.reduce((sum, word) => sum + termScore(b, word), 0);
      if (rankA !== rankB) return rankB - rankA;
    }
    if (state.sort === "category") {
      const c = collator.compare(a.category, b.category);
      if (c) return c;
    }
    if (state.sort === "creator") {
      const c = collator.compare(a.developer, b.developer);
      if (c) return c;
    }
    return collator.compare(a.name, b.name);
  });
  return results;
}

export function catalogInsights(catalog) {
  const categories = new Map();
  const availability = new Map();
  const creators = new Set();
  const repositories = new Set();
  let demos = 0;

  for (const app of catalog) {
    categories.set(app.category, (categories.get(app.category) || 0) + 1);
    availability.set(app.availability, (availability.get(app.availability) || 0) + 1);
    creators.add(normalize(app.developer));
    if (app.demo_url) demos += 1;
    try {
      const url = new URL(app.source_url);
      const segments = url.pathname.split("/").filter(Boolean);
      if (url.hostname === "github.com" && segments.length >= 2)
        repositories.add(segments[0].toLowerCase() + "/" + segments[1].toLowerCase());
    } catch { /* Missing sources do not increase repository counts. */ }
  }

  const byCount = (a, b) => b.count - a.count || collator.compare(a.name, b.name);
  return {
    total: catalog.length,
    categoryCount: categories.size,
    creatorLabels: creators.size,
    additionalLinks: demos,
    sourceRepositories: repositories.size,
    categories: [...categories].map(([name, count]) => ({ name, count })).sort(byCount),
    availability: [...availability].map(([name, count]) => ({ name, count })).sort(byCount)
  };
}

export function hasActiveFilters(state) {
  return Boolean(state.q?.trim() || state.category || state.availability ||
    state.demoOnly || (state.sort && state.sort !== "name"));
}
