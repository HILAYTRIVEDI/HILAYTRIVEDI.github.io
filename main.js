const NAV = [['about','01','About'],['work','02','Work'],['experience','03','Experience'],['skills','04','Stack'],['opensource','05','Open source'],['education','06','Education'],['contact','07','Contact']];

const PROJECTS = [
  { kicker:'rtCamp · 2026', title:'Persistent AI memory layer', metric:'32%', metricLabel:'less token usage per task, 80+ engineers',
    summary:'Shipped as an internal Claude Code plugin giving coding agents shared memory, used by 80+ engineers.',
    details:['Cut token usage per task by 32%, measured through LiteLLM per-project usage and Langfuse traces.','Three-tier scoping (org / project / personal), git-backed markdown as source of truth, human-approved promotion.','Deterministic non-LLM reranking, per-subagent model tiers. Codex adapter in progress.'],
    stack:'Claude Code plugins · LiteLLM · Langfuse · Git' },
  { kicker:'rtCamp · 2026', title:'Company knowledge retrieval system', metric:'16 yrs', metricLabel:'of delivery history, queryable by role',
    summary:'Built and run in production the internal knowledge retrieval system over rtCamp\u2019s 16-year delivery history. Self-hosted.',
    details:['Ingestion and chunking pipeline.','Hybrid retrieval pairing a relational store (entity relationships) with a vector store (semantic similarity).','Hashed metadata-tagged content capsules, and answers scoped by role (sales, architecture, engineering).'],
    stack:'Hybrid relational + vector retrieval · pgvector · Self-hosted' },
  { kicker:'Project', title:'Tower of Agents: governed multi-agent platform', metric:'3', metricLabel:'layers: graph, governance, execution',
    summary:'Neo4j content graph with GraphRAG retrieval; LangGraph governance with agent registry, HITL gates, and audit trail; MCP execution layer exposing governed capabilities as an SDK.',
    details:['Neo4j content graph with GraphRAG retrieval.','LangGraph governance with agent registry, HITL gates, and audit trail.','MCP execution layer exposing governed capabilities as an SDK.'],
    stack:'Neo4j · GraphRAG · LangGraph · MCP · Next.js', link:'towerofagents.vercel.app', href:'https://towerofagents.vercel.app' },
  { kicker:'Project', title:'Advoksha: multi-agent legal research', metric:'4', metricLabel:'agents on shared Redis state',
    summary:'Supervisor, Researcher, Linguistic, and Drafter agents on shared Redis state; research grounded in High Court and Supreme Court case law.',
    details:['OCR, regional-language translation, schema-validated contract drafting.','Built from interviews with 15 to 20 practicing lawyers.','Chose a ~32M-parameter BGE model to stay self-hostable and far below ~$250/seat incumbent pricing. Deployed, now archived.'],
    stack:'Next.js · FastAPI · LangGraph · Gemini 2.5 · BGE · Supabase · Redis · Docker', link:'GitHub', href:'https://github.com/HILAYTRIVEDI/advoksha' },
  { kicker:'Project', title:'LessonBuild: human-in-the-loop learning agent', metric:'PDF→', metricLabel:'approved lesson plan, MCQs and report',
    summary:'Turns a PDF into an approved lesson plan, objective-scoped MCQs, retryable feedback, and a personalized report.',
    details:['Postgres checkpointer makes every interrupt durable.','Answer-leak guardrail enforced structurally and verified with an adversarial test.'],
    stack:'TypeScript · LangGraph.js · CopilotKit · Next.js · PostgreSQL · Docker' }
];

const EXPERIENCE = [
  { period:'Aug 2026 to Present', org:'rtCamp (WordPress VIP Gold Agency)', place:'Remote', role:'Technical AI Lead', bullets:[
    'Lead rtCamp\u2019s internal AI initiative, reporting directly to the CTO; technical lead of one of two AI initiative teams. Own planning, proposals, architecture documentation, POC delivery with the team, and stakeholder presentations for org-wide adoption, with client-facing rollout planned after the POC.',
    'Architected the centralized company AI system: a knowledge retrieval layer as the foundation, a persistent memory layer on top, and a single queryable interface for the whole organization.',
    'Evaluated models and agent workflows against deterministic metrics, retiring 5 workflows that did not justify their cost.',
    'Authored the company AI development framework: tooling inventory, governance standards, and agent workflow guidelines.'] },
  { period:'Apr 2025 to Present', org:'rtCamp (WordPress VIP Gold Agency)', place:'Remote', role:'Senior Software Engineer', bullets:[
    'Lead front-end development for one of the largest prop trading firms in the USA, leading the end-to-end revamp of its marketing site.',
    'Senior Developer for Canada\u2019s largest media house.',
    'Pre-sales and growth engineering: own discovery, solution scoping, pricing, and proposals for enterprise leads; onboarded 4 high-ticket clients in one month.',
    'Interview engineering candidates and mentor engineers through internal AI learning initiatives.'] },
  { period:'Jan 2023 to Apr 2025', org:'rtCamp (WordPress VIP Gold Agency)', place:'Remote', role:'Web Engineer', bullets:[
    'Led 8 engineers to ship 200+ landing pages in 6 weeks on a reusable PHP/ACF component system: 32% client sales increase, 200% daily visitor growth.',
    'Built the Gutenberg block system for Canada\u2019s largest media publisher: 90+ mobile / 99 desktop Lighthouse on a multisite network serving millions of readers.',
    'Led the revamp and redesign of a multisite network, increasing daily visits by 23%.',
    'Architected headless multisite networks (GraphQL + Next.js), replicating Gutenberg blocks in Next.js; built a QuickBooks integration from WordPress.'] },
  { period:'Dec 2020 to Jan 2023', org:'Multidots Solutions', place:'Ahmedabad', role:'Full Stack Developer', bullets:[
    'Led the full backend migration of a legacy .NET platform to WordPress VIP (custom plugins, WooCommerce, REST APIs), delivering a 34% post-launch sales increase.',
    'Built an in-house server-side rendered Gutenberg block library (PHP + React) reused across projects, accelerating team delivery.',
    'Modernized legacy PHP codebases and consulted directly with clients on architecture, timelines, and budget.'] },
  { period:'Sep 2020 to Oct 2020', org:'Llychee Inc. (Hong Kong)', place:'Remote', role:'Machine Learning Intern', bullets:[
    'Built ML models for an HR-tech candidate-matching system, including a LinkedIn profile scraper with ML relevance scoring against job descriptions.'] }
];

const SKILLS = [
  ['AI / ML','LLM integration (Claude, Gemini, OpenAI), multi-agent orchestration (LangGraph, LangGraph.js), human-in-the-loop interrupts, RAG and GraphRAG, hybrid relational + vector retrieval, pgvector, Neo4j, BGE / bge-m3 embeddings, structured output, prompt-injection defense, eval design, MCP servers and clients, llama.cpp'],
  ['LLM observability','Langfuse, LiteLLM, OpenTelemetry, cost and usage tracking, eval pipelines'],
  ['Agentic development','Claude Code skills, hooks and plugins, CLAUDE.md / AGENTS.md instruction layers, spec-driven planning with approval gates, model-tier cost optimization, deterministic (non-LLM) metrics, Codex, Copilot'],
  ['Languages','Python, TypeScript, PHP 8+, JavaScript, SQL'],
  ['Backend / infra','FastAPI, NestJS, PostgreSQL (RLS, JSONB), Neo4j, MySQL, Redis, REST, GraphQL, WebSockets, Docker, GitHub Actions, Vercel, Supabase'],
  ['Frontend','React, Next.js App Router, CopilotKit, Tailwind CSS, D3.js, Three.js'],
  ['WordPress VIP','Custom plugin architecture, multisite, headless (WPGraphQL + Next.js), Gutenberg / FSE, SSR blocks, ACF Pro, WooCommerce']
];

const EDUCATION = [
  { period:'Aug 2025 to Dec 2026', title:'Executive Diploma in Machine Learning and AI, IIIT Bangalore', note:'Module credential earned Dec 2025. Coursework: statistics, regression, decision trees, clustering, NLP, neural networks, PySpark.' },
  { period:'2017 to 2021', title:'B.Tech in Computer Engineering, L.J. Institute of Engineering and Technology', note:'CGPA 9.6 / 10' },
  { period:'2022 to 2023', title:'Diploma in Management, Ahmedabad Management Association', note:'' }
];
const GRAPH = {
  hub: ['Hilay Trivedi', 'Technical AI Lead · Senior Software Engineer'],
  clusters: [
    ['AI systems', 'RAG, GraphRAG, multi-agent orchestration', [['Knowledge retrieval', '16-year delivery history, in production', 1], ['Tower of Agents', 'Governed multi-agent platform', 1], ['Advoksha', 'Multi-agent legal research', 1], ['LessonBuild', 'Human-in-the-loop learning agent', 1], ['LangGraph', 'Multi-agent orchestration', 0], ['GraphRAG', 'Neo4j content graph retrieval', 0]]],
    ['Agentic dev', 'Claude Code skills, hooks and plugins', [['AI memory layer', '80+ engineers · 32% less tokens per task', 1], ['Claude Code', 'Skills, hooks and plugins', 0], ['MCP', 'Servers and clients', 0], ['Langfuse + LiteLLM', 'LLM observability', 0]]],
    ['Security', 'Security tooling for AI-written code', [['Security gate', '129+ issues across 23 repositories', 1], ['Semgrep', 'Custom rule pack', 0], ['OWASP Top 10', 'WordPress VIP standards', 0]]],
    ['WordPress', 'Core contributor, releases 5.9 through 7.1', [['WordPress Core', '18+ patches accepted in Core SVN', 1], ['Gutenberg blocks', '90+ mobile / 99 desktop Lighthouse', 1], ['200+ landing pages', 'Shipped in 6 weeks, 32% client sales increase', 1], ['Revision Buster', 'Plugin author (WP-CLI + admin UI)', 0]]],
    ['Backend / infra', 'Python, TypeScript, PHP 8+, SQL', [['FastAPI', 'Backend', 0], ['PostgreSQL', 'RLS, JSONB, pgvector', 0], ['Neo4j', 'Graph database', 0], ['Redis + Docker', 'State and deployment', 0]]],
    ['Frontend', 'React, Next.js App Router', [['Next.js', 'App Router, headless WordPress', 0], ['React', 'Frontend', 0], ['Three.js', 'Renders this graph', 0]]]
  ],
  links: [['Tower of Agents', 'Neo4j'], ['Tower of Agents', 'MCP'], ['Tower of Agents', 'LangGraph'], ['Advoksha', 'FastAPI'], ['Advoksha', 'LangGraph'], ['LessonBuild', 'PostgreSQL'], ['LessonBuild', 'LangGraph'], ['Knowledge retrieval', 'PostgreSQL'], ['GraphRAG', 'Neo4j'], ['AI memory layer', 'Langfuse + LiteLLM'], ['AI memory layer', 'Claude Code'], ['Security gate', 'OWASP Top 10'], ['Security gate', 'Semgrep'], ['Gutenberg blocks', 'Next.js'], ['Gutenberg blocks', 'React']]
};

// ---------- state ----------
const params = new URLSearchParams(location.search);
const CONFIG = {
  layout: params.get('layout') === 'Poster' ? 'B' : 'A',
  customCursor: params.get('cursor') !== '0',
  autoRotate: params.get('rotate') !== '0'
};
const state = { layout: CONFIG.layout, open: {}, active: 'about', showRail: false, wide: false };
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const isA = () => state.layout === 'A';

const outer = $('work'), track = $('track'), prog = $('prog'), rail = $('rail'), posterNav = $('posterNav'), main = $('main');
const ring = $('ring'), dot = $('dot');
let dist = 0, raf = 0, io = null, glEl = null, glWrap = null, glReset = null, renderer = null, cam = null, mats = null, graphR = 0, ro = null;

// ---------- render ----------
function renderNav() {
  const items = NAV.map(([id, num, label]) => ({ id, num, label, on: state.active === id }));
  rail.innerHTML = items.map((n) => `<a href="#${n.id}" style="display:flex;align-items:center;gap:10px;font-size:12px;font-weight:600;color:${n.on ? 'var(--color-accent)' : 'var(--color-text)'}"><span style="display:block;height:2px;background:currentColor;transition:width .35s;width:${n.on ? '28px' : '10px'}"></span><span>${n.num}</span><span>${esc(n.label)}</span></a>`).join('');
  posterNav.innerHTML = items.map((n) => `<a href="#${n.id}" style="flex:1 0 auto;display:flex;gap:8px;align-items:baseline;padding:14px 20px;border-right:2px solid var(--color-divider);font-size:13px;font-weight:600;white-space:nowrap;color:${n.on ? 'var(--color-accent)' : 'var(--color-text)'};box-shadow:${n.on ? 'inset 0 -3px 0 var(--color-accent)' : 'none'}"><span style="font-size:11px">${n.num}</span>${esc(n.label)}</a>`).join('');
}

function renderChrome() {
  const railOn = isA() && state.wide && state.showRail;
  rail.style.opacity = railOn ? '1' : '0';
  rail.style.pointerEvents = railOn ? 'auto' : 'none';
  main.style.paddingLeft = isA() && state.wide ? '200px' : '0px';
  document.querySelectorAll('[data-layout]').forEach((el) => { el.hidden = el.dataset.layout !== state.layout; });
  const on = { background: 'var(--color-text)', color: 'var(--color-bg)' }, off = { background: 'transparent', color: 'var(--color-text)' };
  Object.assign($('swA').style, isA() ? on : off);
  Object.assign($('swB').style, isA() ? off : on);
}

function projectCard(p, i) {
  const open = !!state.open[i];
  return `<article style="flex:0 0 min(500px,84vw);box-sizing:border-box;border-right:2px solid var(--color-divider);padding:28px 28px 28px;display:flex;flex-direction:column;gap:16px;min-height:min(60vh,540px)">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:12px">
    <span style="font-size:13px;font-weight:800;color:var(--color-accent)">W/0${i + 1}</span>
    <span class="tag tag-neutral">${esc(p.kicker)}</span>
  </div>
  <h3 style="margin:0;font-size:clamp(26px,2.4vw,34px);line-height:1.05;letter-spacing:-0.02em">${esc(p.title)}</h3>
  <div style="display:flex;align-items:baseline;gap:12px;flex-wrap:wrap">
    <span style="font-size:clamp(52px,5vw,76px);font-weight:800;letter-spacing:-0.05em;line-height:1;color:var(--color-accent)">${esc(p.metric)}</span>
    <span style="font-size:14px;max-width:22ch">${esc(p.metricLabel)}</span>
  </div>
  <p style="margin:0;font-size:16px;line-height:1.5;text-wrap:pretty">${esc(p.summary)}</p>
  ${open ? `<ul style="margin:0;padding:16px 0 0;list-style:none;display:flex;flex-direction:column;gap:10px;border-top:2px solid var(--color-divider)">${p.details.map((d) => `<li style="font-size:14px;line-height:1.45;display:grid;grid-template-columns:16px 1fr"><span style="color:var(--color-accent);font-weight:800">—</span><span>${esc(d)}</span></li>`).join('')}</ul>` : ''}
  <div style="margin-top:auto;display:flex;flex-direction:column;gap:14px">
    <div style="font-size:12px;line-height:1.5;letter-spacing:0.02em;text-transform:uppercase;font-weight:600">${esc(p.stack)}</div>
    <div style="display:flex;gap:10px;flex-wrap:wrap">
      <button class="btn btn-secondary" data-toggle="${i}" aria-expanded="${open}" style="min-width:140px;justify-content:flex-start;font-family:inherit">${open ? 'Close  −' : 'Details  +'}</button>
      ${p.link ? `<a class="btn btn-ghost" href="${esc(p.href)}" target="_blank" rel="noopener" style="justify-content:flex-start">${esc(p.link)} ↗</a>` : ''}
    </div>
  </div>
</article>`;
}
function renderTrack() { track.innerHTML = PROJECTS.map(projectCard).join(''); }

function renderStatic() {
  renderTrack();
  $('expList').innerHTML = EXPERIENCE.map((e) => `<div data-reveal style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:16px 32px;padding:28px 0;border-top:2px solid var(--color-divider)">
  <div style="display:flex;flex-direction:column;gap:6px">
    <span style="font-size:14px;font-weight:600;color:var(--color-accent-700)">${esc(e.period)}</span>
    <span style="font-size:14px">${esc(e.org)}</span>
    <span style="font-size:12px;text-transform:uppercase;letter-spacing:0.06em">${esc(e.place)}</span>
  </div>
  <div style="grid-column:span 2;min-width:min(100%,240px);display:flex;flex-direction:column;gap:14px">
    <h3 style="margin:0;font-size:clamp(24px,2.2vw,32px);letter-spacing:-0.02em;line-height:1.1">${esc(e.role)}</h3>
    <ul style="margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:10px;max-width:78ch">${e.bullets.map((b) => `<li style="font-size:15px;line-height:1.5;display:grid;grid-template-columns:18px 1fr;text-wrap:pretty"><span style="color:var(--color-accent);font-weight:800">—</span><span>${esc(b)}</span></li>`).join('')}</ul>
  </div>
</div>`).join('');
  $('skillsGrid').innerHTML = SKILLS.map(([cat, items], i) => `<div data-reveal style="padding:24px;border-right:2px solid var(--color-divider);border-bottom:2px solid var(--color-divider);display:flex;flex-direction:column;gap:12px">
  <span style="font-size:12px;font-weight:800;letter-spacing:0.06em;text-transform:uppercase;color:var(--color-accent-700)">0${i + 1} · ${esc(cat)}</span>
  <p style="margin:0;font-size:15px;line-height:1.55;text-wrap:pretty">${esc(items)}</p>
</div>`).join('');
  $('eduList').innerHTML = EDUCATION.map((ed) => `<div data-reveal style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:8px 32px;padding:24px 0;border-top:2px solid var(--color-divider)">
  <span style="font-size:14px;font-weight:600;color:var(--color-accent-700)">${esc(ed.period)}</span>
  <div style="grid-column:span 2;min-width:min(100%,240px);display:flex;flex-direction:column;gap:6px">
    <h3 style="margin:0;font-size:clamp(20px,1.8vw,26px);line-height:1.2">${esc(ed.title)}</h3>
    <span style="font-size:15px;line-height:1.5">${esc(ed.note)}</span>
  </div>
</div>`).join('');
}

// ---------- scroll ----------
function measure() {
  dist = Math.max(0, track.scrollWidth - innerWidth + (state.wide && isA() ? 200 : 0));
  outer.style.height = (dist + innerHeight) + 'px';
}
function tick() {
  const p = Math.min(1, Math.max(0, -outer.getBoundingClientRect().top / (dist || 1)));
  track.style.transform = `translate3d(${-p * dist}px,0,0)`;
  prog.style.transform = `scaleX(${p})`;
  let active = NAV[0][0];
  for (const [id] of NAV) { const el = $(id); if (el && el.getBoundingClientRect().top < innerHeight * 0.4) active = id; }
  const showRail = scrollY > innerHeight * 0.7;
  if (active !== state.active || showRail !== state.showRail) {
    const navChanged = active !== state.active;
    state.active = active; state.showRail = showRail;
    if (navChanged) renderNav();
    renderChrome();
  }
}

// ---------- reveal & counters ----------
function setupReveal() {
  if (!io) io = new IntersectionObserver((ents) => {
    ents.forEach((en) => { if (!en.isIntersecting) return; io.unobserve(en.target); reveal(en.target); });
  }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });
  document.querySelectorAll('[data-reveal],[data-rule],[data-count]').forEach((el) => {
    if (el.dataset.rv || el.closest('[hidden]')) return; el.dataset.rv = '1';
    if (el.getBoundingClientRect().top < innerHeight * 0.92) { if (el.hasAttribute('data-count')) count(el); return; }
    if (el.hasAttribute('data-rule')) { el.style.transformOrigin = 'left'; el.style.transform = 'scaleX(0)'; }
    else if (el.hasAttribute('data-reveal')) { el.style.opacity = '0'; el.style.transform = 'translate3d(0,36px,0)'; }
    io.observe(el);
  });
}
function reveal(el) {
  const sib = el.parentElement ? [...el.parentElement.children].filter((c) => c.hasAttribute('data-reveal')) : [];
  const d = Math.max(0, sib.indexOf(el)) * 70;
  if (el.hasAttribute('data-rule')) { el.style.transition = 'transform 1.1s cubic-bezier(.7,0,.2,1)'; el.style.transform = 'scaleX(1)'; }
  if (el.hasAttribute('data-reveal')) { el.style.transition = `opacity .9s ${d}ms, transform 1s ${d}ms cubic-bezier(.2,.7,.1,1)`; el.style.opacity = '1'; el.style.transform = 'none'; }
  el.querySelectorAll('[data-count]').forEach(count);
  if (el.hasAttribute('data-count')) count(el);
}
function count(el) {
  if (el.dataset.counted) return; el.dataset.counted = '1';
  const to = parseFloat(el.dataset.count), dec = +(el.dataset.dec || 0), t0 = performance.now(), dur = 1400;
  const step = (now) => { const k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 4); el.textContent = (to * e).toFixed(dec); if (k < 1) requestAnimationFrame(step); };
  requestAnimationFrame(step);
}
function intro() {
  if (!document.body.animate) return;
  const vis = (el) => !el.closest('[hidden]');
  [...document.querySelectorAll('[data-intro-line]')].filter(vis).forEach((el, i) => el.animate([{ transform: 'translateY(105%)' }, { transform: 'none' }], { duration: 1100, delay: 120 + i * 110, easing: 'cubic-bezier(.7,0,.2,1)', fill: 'backwards' }));
  [...document.querySelectorAll('[data-intro]')].filter(vis).forEach((el, i) => el.animate([{ opacity: 0, transform: 'translateY(24px)' }, { opacity: 1, transform: 'none' }], { duration: 900, delay: 420 + i * 90, easing: 'cubic-bezier(.2,.7,.1,1)', fill: 'backwards' }));
}

// ---------- cursor ----------
function setupCursor() {
  if (!CONFIG.customCursor || !matchMedia('(pointer:fine)').matches) return;
  const st = document.createElement('style'); st.textContent = '*{cursor:none!important}'; document.head.appendChild(st);
  let mx = -100, my = -100, rx = -100, ry = -100, hover = false;
  addEventListener('mousemove', (e) => {
    mx = e.clientX; my = e.clientY;
    dot.style.opacity = '1'; ring.style.opacity = '1';
    dot.style.transform = `translate3d(${mx}px,${my}px,0)`;
    const h = !!(e.target.closest && e.target.closest('a,button'));
    if (h !== hover) { hover = h; Object.assign(ring.style, h ? { width: '56px', height: '56px', left: '-28px', top: '-28px', background: 'color-mix(in srgb, var(--color-accent) 14%, transparent)' } : { width: '36px', height: '36px', left: '-18px', top: '-18px', background: 'transparent' }); }
  });
  document.addEventListener('mouseleave', () => { dot.style.opacity = '0'; ring.style.opacity = '0'; });
  const loop = () => { rx += (mx - rx) * 0.2; ry += (my - ry) * 0.2; ring.style.transform = `translate3d(${rx}px,${ry}px,0)`; requestAnimationFrame(loop); };
  loop();
}

// ---------- 3D agent graph ----------
const visibleGL = () => [...document.querySelectorAll('[data-gl]')].find((el) => !el.closest('[hidden]')) || null;

async function initGL() {
  let T; try { T = await import('https://unpkg.com/three@0.184.0/build/three.module.js'); } catch (e) { return; }
  const r = new T.WebGLRenderer({ antialias: true, alpha: true });
  r.setPixelRatio(Math.min(2, devicePixelRatio)); r.setClearColor(0x000000, 0);
  r.domElement.style.cssText = 'display:block;width:100%;height:100%;touch-action:pan-y';
  renderer = r;
  const wrap = document.createElement('div'); wrap.style.cssText = 'position:absolute;inset:0';
  const layer = document.createElement('div'); layer.style.cssText = 'position:absolute;inset:0;pointer-events:none;overflow:hidden;font-family:var(--font-body)';
  wrap.appendChild(r.domElement); wrap.appendChild(layer); glWrap = wrap;
  const tip = document.createElement('div'); tip.style.cssText = 'position:absolute;left:0;top:0;max-width:230px;background:var(--color-bg);color:var(--color-text);border:2px solid var(--color-text);padding:8px 10px;opacity:0;transition:opacity .15s;z-index:2000';
  layer.appendChild(tip);
  const scene = new T.Scene(); cam = new T.PerspectiveCamera(32, 1, 0.1, 100); cam.position.set(0, 0, 14);
  scene.add(new T.AmbientLight(0xffffff, 1.4)); const dl = new T.DirectionalLight(0xffffff, 2.2); dl.position.set(4, 6, 8); scene.add(dl);
  const g = new T.Group(); g.name = 'skills_graph'; scene.add(g);
  const M = mats = {
    ink: new T.MeshStandardMaterial({ name: 'ink', color: 0x201e1d, roughness: 0.75, flatShading: true }),
    hub: new T.MeshStandardMaterial({ name: 'hub', color: 0xff9784, roughness: 0.5, flatShading: true }),
    sys: new T.MeshStandardMaterial({ name: 'system', color: 0xff9784, roughness: 0.5, flatShading: true }),
    hot: new T.MeshStandardMaterial({ name: 'hot', color: 0xff9784, roughness: 0.5, flatShading: true }),
    pulse: new T.MeshBasicMaterial({ name: 'pulse', color: 0xff9784 }),
    line: new T.LineBasicMaterial({ name: 'line', color: 0x201e1d, transparent: true, opacity: 0.2 })
  };
  const N = []; const byName = {};
  const addNode = (t, sub, pos, size, mat, tier) => { const n = { t, sub, pos, size, mat, tier }; byName[t] = N.length; N.push(n); return N.length - 1; };
  addNode(GRAPH.hub[0], GRAPH.hub[1], new T.Vector3(), 0.7, M.hub, 0);
  const E = [], key = new Set(), add = (a, b) => { const k = a < b ? a + '-' + b : b + '-' + a; if (a !== b && !key.has(k)) { key.add(k); E.push([a, b]); } };
  const up = new T.Vector3(0, 1, 0), C = GRAPH.clusters.length;
  GRAPH.clusters.forEach(([t, sub, leaves], i) => {
    const a = i / C * Math.PI * 2, cp = new T.Vector3(Math.cos(a) * 3.1, i % 2 ? 0.7 : -0.7, Math.sin(a) * 3.1);
    const ci = addNode(t, sub, cp, 0.36, M.ink, 1); add(0, ci);
    const base = cp.clone().setY(0).normalize(), tan = new T.Vector3(-base.z, 0, base.x);
    leaves.forEach(([lt, ls, shipped], j) => {
      const ang = j / leaves.length * Math.PI * 2 + i;
      const lp = cp.clone().add(base.clone().multiplyScalar(1.9)).add(tan.clone().multiplyScalar(Math.cos(ang) * 1.25)).add(up.clone().multiplyScalar(Math.sin(ang) * 1.25));
      add(ci, addNode(lt, ls, lp, shipped ? 0.24 : 0.15, shipped ? M.sys : M.ink, 2));
    });
    if (i > 0) add(ci, byName[GRAPH.clusters[i - 1][0]]);
  });
  add(byName[GRAPH.clusters[0][0]], byName[GRAPH.clusters[C - 1][0]]);
  GRAPH.links.forEach(([a, b]) => { if (byName[a] != null && byName[b] != null) add(byName[a], byName[b]); });
  const P = N.map((n) => n.pos); graphR = Math.max(...P.map((p) => p.length())) + 0.4;
  const adj = P.map(() => []); E.forEach(([a, b], k) => { adj[a].push(k); adj[b].push(k); });
  const nodes = N.map((n, i) => { const m = new T.Mesh(new T.BoxGeometry(n.size, n.size, n.size), n.mat); m.name = n.t.replace(/[^a-z0-9]+/gi, '_').toLowerCase(); m.position.copy(n.pos); m.rotation.set(i * 0.7, i * 1.3, 0); m.userData = { base: n.mat, idx: i }; g.add(m); return m; });
  const lpos = new Float32Array(E.length * 6); E.forEach(([a, b], k) => { lpos.set([P[a].x, P[a].y, P[a].z, P[b].x, P[b].y, P[b].z], k * 6); });
  const lg = new T.BufferGeometry(); lg.setAttribute('position', new T.BufferAttribute(lpos, 3)); const lines = new T.LineSegments(lg, M.line); lines.name = 'edges'; g.add(lines);
  const pg = new T.BoxGeometry(0.09, 0.09, 0.09);
  const pulses = Array.from({ length: 9 }, (_, i) => { const m = new T.Mesh(pg, M.pulse); m.name = 'signal_' + i; g.add(m); const e = (Math.random() * E.length) | 0; return { m, e, from: E[e][0], t: Math.random(), v: 0.006 + Math.random() * 0.01 }; });
  // persistent labels for hub + domains
  const labels = N.map((n) => { if (n.tier > 1) return null; const el = document.createElement('div'); el.textContent = n.t; el.style.cssText = 'position:absolute;left:0;top:0;white-space:nowrap;font-size:10px;font-weight:800;letter-spacing:0.06em;text-transform:uppercase;padding:2px 6px;transition:opacity .3s;background:var(--color-text);color:var(--color-bg)'; layer.appendChild(el); return el; });
  glTheme();
  const ray = new T.Raycaster(), ndc = new T.Vector2(9, 9);
  glReset = () => { ndc.set(9, 9); tip.style.opacity = '0'; };
  let drag = false, lx = 0, ly = 0, vy = 0, tx = 0.55, hov = null;
  const el = r.domElement;
  el.addEventListener('pointerdown', (e) => { drag = true; lx = e.clientX; ly = e.clientY; el.setPointerCapture(e.pointerId); });
  el.addEventListener('pointerup', () => { drag = false; });
  el.addEventListener('pointerleave', () => { ndc.set(9, 9); });
  el.addEventListener('pointermove', (e) => {
    const b = el.getBoundingClientRect(); ndc.set((e.clientX - b.left) / b.width * 2 - 1, -(e.clientY - b.top) / b.height * 2 + 1);
    if (drag) { vy += (e.clientX - lx) * 0.0016; tx = Math.max(-0.7, Math.min(0.9, tx + (e.clientY - ly) * 0.004)); lx = e.clientX; ly = e.clientY; }
  });
  const tmp = new T.Vector3(), pv = new T.Vector3();
  const proj = (m, w, hh) => { m.getWorldPosition(pv).project(cam); return [(pv.x + 1) / 2 * w, (1 - pv.y) / 2 * hh, pv.z]; };
  const loop = () => {
    requestAnimationFrame(loop);
    if (!glEl || !glEl.isConnected) return;
    const auto = CONFIG.autoRotate && !hov ? 0.0022 : 0;
    vy *= 0.93; g.rotation.y += auto + vy; g.rotation.x += (tx - g.rotation.x) * 0.06;
    ray.setFromCamera(ndc, cam); const hit = ray.intersectObjects(nodes, false)[0]; const hn = hit ? hit.object : null;
    if (hn !== hov) {
      if (hov) hov.material = hov.userData.base; hov = hn;
      if (hn) { if (hn.userData.idx !== 0) hn.material = M.hot; const n = N[hn.userData.idx]; tip.innerHTML = '<div style="font-size:14px;font-weight:800;line-height:1.2">' + n.t + '</div>' + (n.sub ? '<div style="font-size:12px;line-height:1.4;margin-top:4px">' + n.sub + '</div>' : ''); tip.style.opacity = '1'; }
      else tip.style.opacity = '0';
    }
    nodes.forEach((m, i) => { const s = m === hov ? 1.6 : 1; m.scale.lerp(tmp.set(s, s, s), 0.15); m.rotation.y += i === 0 ? 0.008 : 0.003; });
    pulses.forEach((p) => {
      p.t += p.v; if (p.t >= 1) { const [a, b] = E[p.e]; const end = p.from === a ? b : a; const opts = adj[end]; p.e = opts[(Math.random() * opts.length) | 0]; p.from = end; p.t = 0; }
      const [a, b] = E[p.e]; p.m.position.lerpVectors(P[p.from], P[p.from === a ? b : a], p.t);
    });
    r.render(scene, cam);
    const w = layer.clientWidth, hh = layer.clientHeight;
    const hz = proj(nodes[0], w, hh)[2];
    labels.forEach((lb, i) => { if (!lb) return; const [x, y, z] = proj(nodes[i], w, hh); lb.style.transform = 'translate(' + (x + 14) + 'px,' + (y - 10) + 'px)'; lb.style.opacity = nodes[i] === hov ? '0' : (i === 0 || z <= hz ? '1' : '0.25'); lb.style.zIndex = String(Math.round((1 - z) * 1000)); });
    if (hov) { const [x, y] = proj(hov, w, hh); const tx2 = Math.min(x + 18, w - 240); tip.style.transform = 'translate(' + Math.max(8, tx2) + 'px,' + Math.max(8, y - 60) + 'px)'; }
  };
  mountGL();
  loop();
}
function mountGL() {
  glEl = visibleGL();
  if (!glEl || !glWrap) return;
  glEl.appendChild(glWrap); if (glReset) glReset(); observeGL();
}
function observeGL() {
  if (!renderer || !glEl) return;
  if (ro) ro.disconnect();
  const fit = () => { const el = glEl; if (!el) return; const w = el.clientWidth || 1, h = el.clientHeight || 1; renderer.setSize(w, h, false); cam.aspect = w / h; const vf = cam.fov * Math.PI / 360, hf = Math.atan(Math.tan(vf) * w / h); cam.position.z = (graphR || 6) / Math.sin(Math.min(vf, hf)) * 1.05; cam.updateProjectionMatrix(); };
  ro = new ResizeObserver(fit); ro.observe(glEl); fit();
}
function glTheme() {
  const M = mats; if (!M) return;
  const poster = !isA();
  M.hub.color.setHex(poster ? 0x201e1d : 0xff9784); M.sys.color.setHex(poster ? 0xf3f2f2 : 0xff9784); M.hot.color.setHex(poster ? 0xf3f2f2 : 0xff9784); M.pulse.color.setHex(poster ? 0xf3f2f2 : 0xff9784);
  M.line.opacity = poster ? 0.4 : 0.2;
}

// ---------- layout switch ----------
function setLayout(L) {
  if (L === state.layout) return;
  state.layout = L;
  renderChrome();
  mountGL();
  measure(); setupReveal(); intro(); glTheme(); tick();
}

// ---------- boot ----------
renderStatic();
renderNav();
renderChrome();
track.addEventListener('click', (e) => {
  const b = e.target.closest('[data-toggle]'); if (!b) return;
  const i = +b.dataset.toggle; state.open[i] = !state.open[i];
  renderTrack(); measure(); tick();
});
$('swA').addEventListener('click', () => setLayout('A'));
$('swB').addEventListener('click', () => setLayout('B'));
const onResize = () => { state.wide = innerWidth >= 1240; measure(); renderChrome(); tick(); };
addEventListener('scroll', () => { if (!raf) raf = requestAnimationFrame(() => { raf = 0; tick(); }); }, { passive: true });
addEventListener('resize', onResize);
onResize();
setupReveal(); intro(); setupCursor();
initGL();
