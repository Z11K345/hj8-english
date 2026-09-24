import subprocess, os, re

CD = r'c:\Users\GFQH-GF-ZK\WorkBuddy\2026-09-20-12-23-11\学习助手\chat-app'
out = open(os.path.join(CD, '_cleanup_out.log'), 'w', encoding='utf-8')

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, shell=True, cwd=CD)
    out.write('CMD: ' + cmd + '\nRC=' + str(r.returncode) + '\n')
    out.write(r.stdout + '\n' + r.stderr + '\n' + '='*50 + '\n')
    out.flush()
    return r

# tracked files
r = run('git ls-files')
tracked = r.stdout.splitlines()
# temp patterns: start with underscore, or deploy*.cmd/log
pat = re.compile(r'(^_)|(^deploy(\.cmd|\.log|\d*\.log)$)')
to_remove = [f for f in tracked if pat.match(os.path.basename(f))]
out.write('REMOVING %d files\n' % len(to_remove))
for f in to_remove:
    run('git rm ' + '"' + f + '"')
# also any leftover untracked temp in root (not in git)
for f in os.listdir(CD):
    if pat.match(f) and os.path.isfile(os.path.join(CD, f)):
        try:
            os.remove(os.path.join(CD, f))
            out.write('deleted untracked: ' + f + '\n')
        except Exception as e:
            out.write('del err ' + f + ' ' + str(e) + '\n')
# commit
run('git commit -m "chore: remove temporary debug/deploy scripts"')
# push with retries
for i in range(3):
    rr = run('git push -u origin main')
    if rr.returncode == 0:
        out.write('PUSH RESULT=SUCCESS\n')
        break
else:
    out.write('PUSH RESULT=FAIL\n')
out.close()
print('done')
