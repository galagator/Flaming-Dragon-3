const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const PORT = Number(process.env.PORT || 6060);
const ROOT = __dirname;
const SVELTE_BUILD = path.join(ROOT, 'fd3-web', 'build');
const STATIC_ROOT = fs.existsSync(SVELTE_BUILD) ? SVELTE_BUILD : ROOT;
const MAPPING_PATH = path.join(ROOT, 'actor-photos-raw', 'fd3-actor-mapping.json');
const BACKUP_DIR = path.join(ROOT, 'actor-photos-raw', 'backups');
const PYTHON_BIN = process.env.PYTHON_BIN || '/usr/bin/python3';

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png',
  '.webp': 'image/webp',
  '.svg': 'image/svg+xml',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.md': 'text/markdown; charset=utf-8',
  '.mp4': 'video/mp4',
};

function sendJson(res, status, payload) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(payload, null, 2));
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk;
      if (body.length > 15_000_000) reject(new Error('Request body too large'));
    });
    req.on('end', () => resolve(body));
    req.on('error', reject);
  });
}

function timestamp() {
  return new Date().toISOString().replace(/[-:]/g, '').replace(/T/, '-').replace(/\..+/, '');
}

function countMarkers(mapping) {
  return Object.values(mapping || {}).reduce((total, markers) => total + (Array.isArray(markers) ? markers.length : 0), 0);
}

function perCharacterCounts(mapping) {
  const counts = {};
  Object.values(mapping || {}).forEach(markers => {
    if (!Array.isArray(markers)) return;
    markers.forEach(marker => {
      const char = String(marker.char || '').trim();
      if (char) counts[char] = (counts[char] || 0) + 1;
    });
  });
  return counts;
}

function validateMapping(mapping) {
  if (!mapping || typeof mapping !== 'object' || Array.isArray(mapping)) {
    throw new Error('Mapping must be an object keyed by photo_XX');
  }
  for (const [photo, markers] of Object.entries(mapping)) {
    if (!/^photo_\d{2}$/.test(photo)) throw new Error(`Invalid photo key: ${photo}`);
    if (!Array.isArray(markers)) throw new Error(`Markers for ${photo} must be an array`);
    markers.forEach((marker, idx) => {
      if (typeof marker !== 'object' || marker === null) throw new Error(`${photo}[${idx}] must be an object`);
      if (!Number.isFinite(Number(marker.x)) || !Number.isFinite(Number(marker.y))) throw new Error(`${photo}[${idx}] needs numeric x/y`);
      if (!String(marker.char || '').trim()) throw new Error(`${photo}[${idx}] needs char`);
    });
  }
}

function loadMapping() {
  if (!fs.existsSync(MAPPING_PATH)) return {};
  return JSON.parse(fs.readFileSync(MAPPING_PATH, 'utf8'));
}

function writeMapping(mapping) {
  fs.mkdirSync(path.dirname(MAPPING_PATH), { recursive: true });
  fs.writeFileSync(MAPPING_PATH, JSON.stringify(mapping, null, 2) + '\n');
}

function backupMapping(existing, label = 'pre-save') {
  fs.mkdirSync(BACKUP_DIR, { recursive: true });
  const backupPath = path.join(BACKUP_DIR, `fd3-actor-mapping-${label}-${timestamp()}.json`);
  fs.writeFileSync(backupPath, JSON.stringify(existing || {}, null, 2) + '\n');
  return backupPath;
}

function sortMapping(mapping) {
  const out = {};
  Object.keys(mapping).sort((a, b) => {
    const ai = Number(a.split('_')[1]);
    const bi = Number(b.split('_')[1]);
    return ai - bi;
  }).forEach(key => { out[key] = mapping[key]; });
  return out;
}

function normalizeMapping(mapping) {
  const normalized = {};
  for (const [photo, markers] of Object.entries(mapping || {})) {
    normalized[photo] = markers.map(marker => ({
      x: Number(marker.x),
      y: Number(marker.y),
      char: String(marker.char).trim(),
    }));
  }
  return sortMapping(normalized);
}

function refPrefix(charName) {
  return ({
    'Galen / Ji-lan': 'Galen-Ji-lan',
    'Tony': 'Tony',
    'Yake-oh': 'Yake-oh',
    'Erb Dean': 'Erb_Dean',
    'MAMA': 'MAMA',
    'Trubble': 'Trubble',
    'Slarth': 'Slarth',
    'Zoh-baggo': 'Zoh-baggo',
    'TK-Maxx': 'TK-Maxx',
    'Jasmine': 'Jasmine',
  })[charName] || String(charName || '').replace(/[^A-Za-z0-9_-]+/g, '_');
}

const CHARACTER_NAMES = ['Galen / Ji-lan', 'Tony', 'Yake-oh', 'Erb Dean', 'MAMA', 'Trubble', 'Slarth', 'Zoh-baggo', 'TK-Maxx', 'Jasmine'];
const IMAGE_EXTS = new Set(['.jpg', '.jpeg', '.png', '.webp']);

function listReferences() {
  const refDir = path.join(ROOT, 'character-references');
  const files = fs.existsSync(refDir) ? fs.readdirSync(refDir) : [];
  const grouped = Object.fromEntries(CHARACTER_NAMES.map(name => [name, []]));
  for (const file of files) {
    const ext = path.extname(file).toLowerCase();
    if (!IMAGE_EXTS.has(ext)) continue;
    for (const charName of CHARACTER_NAMES) {
      if (file.startsWith(refPrefix(charName))) {
        grouped[charName].push(`character-references/${file}`);
        break;
      }
    }
  }
  for (const list of Object.values(grouped)) list.sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
  return grouped;
}

function decodeDataUrl(dataUrl) {
  const match = String(dataUrl || '').match(/^data:(image\/(jpeg|png|webp));base64,([A-Za-z0-9+/=\r\n]+)$/);
  if (!match) throw new Error('Expected JPEG/PNG/WebP data URL');
  const ext = match[2] === 'jpeg' ? '.jpg' : `.${match[2]}`;
  return { ext, buffer: Buffer.from(match[3], 'base64') };
}

async function handleReferenceUpload(req, res) {
  try {
    const body = JSON.parse(await readBody(req));
    const charName = String(body.char || '').trim();
    if (!CHARACTER_NAMES.includes(charName)) throw new Error(`Unknown character: ${charName}`);
    const { ext, buffer } = decodeDataUrl(body.dataUrl);
    if (buffer.length < 32) throw new Error('Image payload too small');
    if (buffer.length > 10_000_000) throw new Error('Image payload too large');
    const refDir = path.join(ROOT, 'character-references');
    fs.mkdirSync(refDir, { recursive: true });
    const safeBase = refPrefix(charName);
    const outName = `${safeBase}_manual_${timestamp()}${ext}`;
    const outPath = path.join(refDir, outName);
    fs.writeFileSync(outPath, buffer);
    return sendJson(res, 200, { ok: true, file: outName, url: `character-references/${outName}`, references: listReferences() });
  } catch (e) {
    return sendJson(res, 400, { ok: false, error: e.message });
  }
}

async function handleSave(req, res) {
  try {
    const force = new URL(req.url, `http://localhost:${PORT}`).searchParams.get('force') === '1';
    const incoming = JSON.parse(await readBody(req));
    validateMapping(incoming);

    const existing = loadMapping();
    const incomingMarkers = countMarkers(incoming);
    const existingMarkers = countMarkers(existing);

    if (!force && existingMarkers >= 10 && incomingMarkers < existingMarkers) {
      return sendJson(res, 409, {
        ok: false,
        error: 'Refusing destructive save',
        message: `Incoming mapping has ${incomingMarkers} markers; existing mapping has ${existingMarkers}. Reload from disk first. Deliberate marker deletion requires force=1.`,
        incomingMarkers,
        existingMarkers,
        existingPhotos: Object.keys(existing).length,
        incomingPhotos: Object.keys(incoming).length,
      });
    }

    const backupPath = backupMapping(existing);
    const saved = normalizeMapping(incoming);
    writeMapping(saved);

    return sendJson(res, 200, {
      ok: true,
      forced: force,
      savedPhotos: Object.keys(saved).length,
      savedMarkers: countMarkers(saved),
      incomingMarkers,
      previousMarkers: existingMarkers,
      backupPath,
      perCharacter: perCharacterCounts(saved),
      mapping: saved,
    });
  } catch (e) {
    return sendJson(res, 400, { ok: false, error: e.message });
  }
}

function handleRecrop(res) {
  const cropScript = path.join(ROOT, 'actor-photos-raw', 'recrop.py');
  const proc = spawn(PYTHON_BIN, [cropScript], { cwd: ROOT });
  let output = '';
  proc.stdout.on('data', d => output += d);
  proc.stderr.on('data', d => output += d);
  proc.on('close', code => {
    if (code === 0) {
      const match = output.match(/TOTAL=(\d+)/) || output.match(/(\d+) crops?/);
      const count = match ? Number(match[1]) : null;
      return sendJson(res, 200, { ok: true, count, output: output.trim() });
    }
    return sendJson(res, 500, { ok: false, error: 'Recrop failed', details: output.slice(-2000) });
  });
}

function serveStatic(req, res) {
  let requestPath = new URL(req.url, `http://localhost:${PORT}`).pathname;
  let filePath = requestPath === '/' ? '/index.html' : requestPath;
  filePath = path.normalize(filePath).replace(/^\.\.\//, '');

  const isAsset = /\.[a-zA-Z0-9]+$/.test(filePath) && !filePath.endsWith('.svelte');
  const tryRoots = isAsset ? [STATIC_ROOT, ROOT] : [STATIC_ROOT];
  // For assets, prefer the SvelteKit build first; fall back to project root
  // (character-references/, character-sheets/, *.md files) for non-bundled files.
  // For HTML route paths, only the build is consulted; missing routes get the
  // SPA fallback index.html (SvelteKit handles client-side routing).

  function attempt(idx) {
    if (idx >= tryRoots.length) {
      // Asset: 404
      if (isAsset) {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        return res.end(`Not found: ${filePath}`);
      }
      // HTML route: SPA fallback
      const fallback = path.join(STATIC_ROOT, 'index.html');
      if (!fallback.startsWith(ROOT)) {
        res.writeHead(403);
        return res.end('Forbidden');
      }
      return fs.readFile(fallback, (err, data) => {
        if (err) {
          res.writeHead(500);
          return res.end('Server error');
        }
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
        res.end(data);
      });
    }
    const fullPath = path.join(tryRoots[idx], filePath);
    if (!fullPath.startsWith(ROOT)) {
      res.writeHead(403);
      return res.end('Forbidden');
    }
    fs.readFile(fullPath, (err, data) => {
      if (err) {
        if (err.code === 'ENOENT') return attempt(idx + 1);
        res.writeHead(500);
        return res.end('Server error');
      }
      const ext = path.extname(fullPath).toLowerCase();
      res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream', 'Cache-Control': 'no-store' });
      res.end(data);
    });
  }
  attempt(0);
}

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  const pathname = new URL(req.url, `http://localhost:${PORT}`).pathname;

  if (req.method === 'GET' && pathname === '/api/mapping') {
    try {
      const mapping = loadMapping();
      return sendJson(res, 200, { ok: true, mapping, markers: countMarkers(mapping), perCharacter: perCharacterCounts(mapping) });
    } catch (e) {
      return sendJson(res, 500, { ok: false, error: e.message });
    }
  }

  if (req.method === 'GET' && pathname === '/api/references') {
    try {
      return sendJson(res, 200, { ok: true, references: listReferences(), markers: countMarkers(loadMapping()) });
    } catch (e) {
      return sendJson(res, 500, { ok: false, error: e.message });
    }
  }

  if (req.method === 'POST' && pathname === '/api/references') return handleReferenceUpload(req, res);

  if (req.method === 'POST' && pathname === '/save') return handleSave(req, res);
  if (req.method === 'POST' && pathname === '/recrop') return handleRecrop(res);
  return serveStatic(req, res);
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 FD3 Server running at http://localhost:${PORT}/`);
  console.log(`   Character Studio: http://localhost:${PORT}/character-studio.html`);
  console.log(`   Face Tagger:      http://localhost:${PORT}/actor-photos-raw/face-tagger.html`);
  console.log(`   Python:           ${PYTHON_BIN}`);
});
