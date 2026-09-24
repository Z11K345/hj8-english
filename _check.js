const fs = require('fs');
const vm = require('vm');
const f = 'exam.html';
const html = fs.readFileSync(f, 'utf8');
// 提取所有 <script>...</script> 内联块（不带 src 的）
const re = /<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g;
let m, n = 0, errs = 0;
while ((m = re.exec(html)) !== null) {
  const code = m[1].trim();
  if (!code) continue; // 外部 src，跳过
  n++;
  try {
    new vm.Script(code, { filename: 'inline-' + n + '.js' });
    console.log('inline script #' + n + ' 语法 OK，长度', code.length);
  } catch (e) {
    errs++;
    console.log('inline script #' + n + ' 语法错误:', e.message);
  }
}
console.log('共检查内联脚本', n, '个，错误', errs, '个');
fs.writeFileSync('_check_result.txt', 'inline=' + n + ' errs=' + errs + '\n', 'utf8');
process.exit(errs ? 1 : 0);
