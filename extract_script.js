const fs = require('fs'), os = require('os'), path = require('path'), cp = require('child_process');
const NODE = 'C:/Users/GFQH-GF-ZK/.workbuddy/binaries/node/versions/24.14.0/node.exe';
const file = process.argv[2];
const html = fs.readFileSync(file, 'utf8');
const re = /<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g;
let m, last = null, n = 0;
while ((m = re.exec(html)) !== null) { last = m[1]; n++; }
if (!last) { console.log('NO INLINE SCRIPT'); process.exit(1); }
const tmp = path.join(os.tmpdir(), '_chk_' + Date.now() + '.js');
fs.writeFileSync(tmp, last, 'utf8');
console.log('inline scripts: ' + n + ' | last len: ' + last.length);
try {
  cp.execFileSync(NODE, ['--check', tmp], { stdio: 'inherit' });
  console.log('SYNTAX OK');
} catch (e) {
  console.log('SYNTAX FAIL');
} finally {
  try { fs.unlinkSync(tmp); } catch (e) {}
}
