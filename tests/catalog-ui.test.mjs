import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  DEFAULT_STATE, normalize, parseFilters, serializeFilters,
  filterCatalog, catalogInsights, hasActiveFilters
} from "../docs/catalog-core.mjs";

const apps = JSON.parse(readFileSync(new URL("../data/apps.json", import.meta.url), "utf8"));
const appHtml = readFileSync(new URL("../docs/index.html", import.meta.url), "utf8");
const appScript = readFileSync(new URL("../docs/app.mjs", import.meta.url), "utf8");

test("normalization ignores accents, case and punctuation", () => {
  assert.equal(normalize("ÁI / Raven-Glass"), "ai raven glass");
  assert.equal(normalize("R-EYE-DER"), "r eye der");
  assert.equal(normalize("MÜSE"), "muse");
});

test("multi-word search matches across name, category, author and description", () => {
  const data = [
    { name:"Blink Photo",category:"Camera",developer:"Artist",description:"gaze controlled camera",availability:"Source code",demo_url:"" },
    { name:"Snake",category:"Games",developer:"Dev",description:"head control",availability:"Source code",demo_url:"" }
  ];
  assert.deepEqual(filterCatalog(data,{ q:"CAMÉRA gaze" }).map(x=>x.name), ["Blink Photo"]);
  assert.deepEqual(filterCatalog(data,{ q:"snake" }).map(x=>x.name), ["Snake"]);
  assert.deepEqual(filterCatalog(data,{ q:"unknown term" }), []);
});

test("combined availability, category and demo filters work as intersection", () => {
  const demo = apps.find(x=>Boolean(x.demo_url));
  assert.ok(demo);
  const results = filterCatalog(apps,{
    category: demo.category, availability: demo.availability, demoOnly:true
  });
  assert.ok(results.some(x=>x.id===demo.id));
  for(const app of results) {
    assert.equal(app.category,demo.category);
    assert.equal(app.availability,demo.availability);
    assert.ok(app.demo_url);
  }
});

test("name sort retains alphabetical consistency with the Google Sheet", () => {
  const results=filterCatalog([...apps].reverse(),DEFAULT_STATE);
  assert.deepEqual(results.map(x=>x.name),apps.map(x=>x.name));
});

test("sort by creator and category is stable and reproducible", () => {
  const creator=filterCatalog(apps,{sort:"creator"});
  const category=filterCatalog(apps,{sort:"category"});
  for (let i=1;i<creator.length;i++)
    assert.ok(creator[i-1].developer.localeCompare(creator[i].developer,"en",{sensitivity:"base"})<=0);
  for (let i=1;i<category.length;i++)
    assert.ok(category[i-1].category.localeCompare(category[i].category,"en",{sensitivity:"base"})<=0);
});

test("relevance ranks a name match above a description-only match", () => {
  const fixture=[
    {name:"Other app",category:"Games",developer:"Dev",description:"blink operation"},
    {name:"BlinkSnap",category:"Camera",developer:"Dev",description:"photo"}
  ];
  const res=filterCatalog(fixture,{q:"blink",sort:"relevance"});
  assert.equal(res[0].name,"BlinkSnap");
});

test("URL parameters round-trip and unknown values fall back safely", () => {
  const state={q:"camera gaze",category:"Camera & vision",availability:"Source code",
    demoOnly:true,sort:"creator",view:"list"};
  assert.deepEqual(parseFilters(serializeFilters(state)),state);
  const unknown=parseFilters("?sort=evil&view=bad&demo=0");
  assert.equal(unknown.sort,"name");
  assert.equal(unknown.view,"grid");
  assert.equal(unknown.demoOnly,false);
});

test("default state produces a clean shareable URL and active-filter test", () => {
  assert.equal(serializeFilters(DEFAULT_STATE),"");
  assert.equal(hasActiveFilters(DEFAULT_STATE),false);
  assert.equal(hasActiveFilters({...DEFAULT_STATE,demoOnly:true}),true);
});

test("insights count exact catalog evidence without invented traffic data", () => {
  const data=catalogInsights(apps);
  assert.equal(data.total,apps.length);
  assert.equal(data.additionalLinks,apps.filter(x=>x.demo_url).length);
  assert.equal(data.categoryCount,new Set(apps.map(x=>x.category)).size);
  assert.equal(data.creatorLabels,new Set(apps.map(x=>normalize(x.developer))).size);
  assert.equal(data.categories.reduce((s,c)=>s+c.count,0),apps.length);
  assert.equal(data.availability.reduce((s,c)=>s+c.count,0),apps.length);
  assert.ok(data.sourceRepositories>0);
  assert.ok(data.sourceRepositories<=apps.length);
  assert.equal(Object.hasOwn(data,"popularity"),false);
  assert.equal(Object.hasOwn(data,"users"),false);
});

test("category insights are ordered by count and tie broken by name", () => {
  const rows=catalogInsights(apps).categories;
  for(let i=1;i<rows.length;i++){
    assert.ok(rows[i-1].count>=rows[i].count);
    if(rows[i-1].count===rows[i].count)
      assert.ok(rows[i-1].name.localeCompare(rows[i].name,"en",{sensitivity:"base"})<=0);
  }
});

test("app UI uses safe DOM text methods with no tracking libraries", () => {
  assert.match(appScript,/textContent/);
  assert.doesNotMatch(appScript,/innerHTML|outerHTML|document\.write/);
  assert.match(appScript,/\.rel = "noopener noreferrer"/);
  assert.match(appScript,/\.protocol !== "https:"/);
  assert.doesNotMatch(appScript,/GoogleAnalytics|gtag\(|hotjar|mixpanel|localStorage/);
  assert.match(appHtml,/type="module" src="\.\/app\.mjs"/);
});

test("all filters have labels, loading state and accessible clear/retry controls", () => {
  const required=[
    "search","category-filter","availability-filter","sort-filter",
    "demo-filter","cards","active-filters","results-count","retry-load",
    "clear-search","reset-filters","share-search","view-grid","view-list"
  ];
  for(const id of required) assert.ok(appHtml.includes('id="'+id+'"'),"missing "+id);
  assert.match(appHtml,/aria-live="polite"/);
  assert.match(appHtml,/aria-busy="true"/);
  assert.match(appHtml,/Skip to applications/);
});
