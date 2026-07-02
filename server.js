const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8199;
const ROOT = __dirname; // FD3 project root
const MAPPING_PATH = path.join(ROOT, 'actor-photos-raw', 'fd3-actor-mapping.json');

const MIME = {
  '.html': 'text/html',
  '.json': 'application/json',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.md': 'text/markdown',
  '.mp4': 'video/mp4',
};

const server = http.createServer((req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // POST /save — write mapping JSON
  if (req.method === 'POST' && req.url === '/save') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        fs.mkdirSync(path.dirname(MAPPING_PATH), { recursive: true });
        fs.writeFileSync(MAPPING_PATH, JSON.stringify(data, null, 2));
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ saved: Object.keys(data).length, path: MAPPING_PATH }));
      } catch (e) {
        res.writeHead(400);
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  // Static file serving
  let filePath = req.url === '/' ? '/character-studio.html' : req.url;
  // Clean the path
  filePath = path.normalize(filePath).replace(/^\.\.\//, '');
  const fullPath = path.join(ROOT, filePath);

  // Security: ensure within ROOT
  if (!fullPath.startsWith(ROOT)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }

  const ext = path.extname(fullPath).toLowerCase();
  const contentType = MIME[ext] || 'application/octet-stream';

  fs.readFile(fullPath, (err, data) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404);
        res.end(`Not found: ${filePath}`);
      } else {
        res.writeHead(500);
        res.end('Server error');
      }
      return;
    }
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 FD3 Server running at:`);
  console.log(`   http://localhost:${PORT}/character-studio.html`);
  console.log(`   http://localhost:${PORT}/actor-photos-raw/face-tagger.html`);
  console.log(`   Press Ctrl+C to stop`);
});
