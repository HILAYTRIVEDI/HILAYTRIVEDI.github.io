// Blog renderer. Data: blog/index.json (manifest, built by tools/blog.py) + blog/posts/<slug>.json.
// Posts are structured blocks, never raw HTML: every string is escaped, and only a small inline
// syntax (**bold**, *italic*, `code`, [text](url)) is turned into markup.
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const $ = (id) => document.getElementById(id);
const SLUG_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

const fmtDate = (d) => new Date(d + 'T00:00:00').toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
const safeUrl = (u) => (/^(https?:|mailto:|\/|\.{1,2}\/|#)/i.test(u) || !/^[a-z][a-z0-9+.-]*:/i.test(u)) ? u : '#';

function inline(text) {
  return String(text ?? '').split(/(`[^`]+`)/g).map((part, i) => {
    if (i % 2) return `<code>${esc(part.slice(1, -1))}</code>`;
    return esc(part)
      .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, t, u) => {
        const href = safeUrl(u.replace(/&amp;/g, '&'));
        const ext = /^https?:/i.test(href);
        return `<a href="${esc(href)}"${ext ? ' target="_blank" rel="noopener"' : ''}>${t}</a>`;
      })
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/(^|[^*])\*([^*\s][^*]*)\*/g, '$1<em>$2</em>');
  }).join('');
}

const BLOCKS = {
  p: (b) => `<p>${inline(b.text)}</p>`,
  h2: (b) => `<h2 id="${esc(slug(b.text))}">${inline(b.text)}</h2>`,
  h3: (b) => `<h3>${inline(b.text)}</h3>`,
  list: (b) => { const t = b.ordered ? 'ol' : 'ul'; return `<${t}>${b.items.map((it) => `<li>${inline(it)}</li>`).join('')}</${t}>`; },
  code: (b) => `<pre${b.lang ? ` data-lang="${esc(b.lang)}"` : ''}><code>${esc(b.code)}</code></pre>`,
  quote: (b) => `<blockquote><p style="margin:0">${inline(b.text)}</p>${b.cite ? `<footer>— ${inline(b.cite)}</footer>` : ''}</blockquote>`,
  callout: (b) => `<div class="callout">${inline(b.text)}</div>`,
  image: (b) => `<figure><img src="${esc(safeUrl(b.src))}" alt="${esc(b.alt)}" loading="lazy">${b.caption ? `<figcaption>${inline(b.caption)}</figcaption>` : ''}</figure>`,
  hr: () => '<hr>'
};
const slug = (s) => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

async function getJSON(url) {
  const r = await fetch(url, { cache: 'no-cache' });
  if (!r.ok) throw new Error(r.status);
  return r.json();
}

// ---------- index page ----------
async function initIndex() {
  const list = $('list'), q = $('q'), chips = $('chips'), count = $('count');
  let posts = [];
  try { posts = (await getJSON('index.json')).posts || []; } catch (e) { list.innerHTML = '<li class="b-empty">Could not load posts.</li>'; return; }
  const params = new URLSearchParams(location.search);
  let tag = params.get('tag') || '';
  const tags = [...new Set(posts.flatMap((p) => p.tags))].sort();
  q.value = params.get('q') || '';

  const render = () => {
    const term = q.value.trim().toLowerCase();
    const shown = posts.filter((p) => (!tag || p.tags.includes(tag)) &&
      (!term || (p.title + ' ' + p.summary + ' ' + p.tags.join(' ')).toLowerCase().includes(term)));
    chips.innerHTML = ['', ...tags].map((t) => `<button class="b-chip" data-tag="${esc(t)}" aria-pressed="${t === tag}">${t ? esc(t) : 'All'}</button>`).join('');
    count.textContent = `${shown.length} of ${posts.length} post${posts.length === 1 ? '' : 's'}`;
    list.innerHTML = shown.length ? shown.map((p) => `<li class="b-row"><a href="post.html?p=${encodeURIComponent(p.slug)}">
      <time datetime="${esc(p.date)}">${esc(fmtDate(p.date))}</time>
      <div><h2>${esc(p.title)}</h2><p>${inline(p.summary.replace(/\[([^\]]+)\]\([^)\s]+\)/g, '$1'))}</p></div>
      <div class="b-side"><span>${p.readingMinutes} min read</span><span class="b-tags">${p.draft ? '<span class="tag b-draft">Draft</span>' : ''}${p.tags.map((t) => `<span class="tag tag-neutral">${esc(t)}</span>`).join('')}</span></div>
    </a></li>`).join('') : `<li class="b-empty">${posts.length ? 'No posts match.' : 'No posts yet. Check back soon.'}</li>`;
    const u = new URLSearchParams(); if (tag) u.set('tag', tag); if (term) u.set('q', q.value.trim());
    history.replaceState(null, '', u.toString() ? '?' + u : location.pathname);
  };
  chips.addEventListener('click', (e) => { const b = e.target.closest('[data-tag]'); if (!b) return; tag = b.dataset.tag; render(); });
  q.addEventListener('input', render);
  if (!tags.length) chips.hidden = true;
  render();
}

// ---------- post page ----------
async function initPost() {
  const s = new URLSearchParams(location.search).get('p') || '';
  const art = $('post');
  const fail = (msg) => { document.title = 'Post not found · Hilay Trivedi'; art.innerHTML = `<div class="b-empty">${esc(msg)} <a href="./">Back to all posts →</a></div>`; };
  if (!SLUG_RE.test(s)) return fail('No such post.');
  let post, manifest = { posts: [] };
  try { [post, manifest] = await Promise.all([getJSON(`posts/${s}.json`), getJSON('index.json').catch(() => ({ posts: [] }))]); }
  catch (e) { return fail('No such post.'); }

  document.title = `${post.title} · Hilay Trivedi`;
  const md = document.querySelector('meta[name=description]'); if (md) md.content = post.summary;
  const words = post.blocks.map((b) => [b.text, b.code, b.caption, ...(b.items || [])].join(' ')).join(' ').split(/\s+/).filter(Boolean).length;
  const mins = Math.max(1, Math.round(words / 220));
  art.innerHTML = `<header class="p-head">
      <div class="b-tags">${post.draft ? '<span class="tag b-draft">Draft</span>' : ''}${post.tags.map((t) => `<a class="tag tag-accent" href="./?tag=${encodeURIComponent(t)}" style="text-decoration:none">${esc(t)}</a>`).join('')}</div>
      <h1>${esc(post.title)}</h1>
      <div class="p-sub"><span>${esc(fmtDate(post.date))}</span>${post.updated ? `<span>Updated ${esc(fmtDate(post.updated))}</span>` : ''}<span>${mins} min read</span><span style="margin-left:auto">${esc(post.author || 'Hilay Trivedi')}</span></div>
    </header>
    <div class="p-body">${post.blocks.map((b) => (BLOCKS[b.type] || (() => ''))(b)).join('')}</div>`;

  const list = manifest.posts || [], i = list.findIndex((p) => p.slug === s);
  if (i !== -1 && list.length > 1) {
    const newer = list[i - 1], older = list[i + 1];
    const link = (p, lbl) => p ? `<a href="post.html?p=${encodeURIComponent(p.slug)}"><span>${lbl}</span><strong>${esc(p.title)}</strong></a>` : '<span></span>';
    art.insertAdjacentHTML('beforeend', `<nav class="p-pager" aria-label="More posts">${link(older, '← Older')}${link(newer, 'Newer →')}</nav>`);
  }
}

if (document.body.dataset.page === 'post') initPost();
else if (document.body.dataset.page === 'index') initIndex();
