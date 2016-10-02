import subprocess
import time

subprocess.check_output("git remote update", shell=True)
time.sleep(5)
result = subprocess.check_output("git remote update", shell=True)
# print result
time.sleep(5)
if result.find('can be fast-forwarded') > 0:
    subprocess.check_output("git pull origin", shell=True)
    print "Atualizado"
