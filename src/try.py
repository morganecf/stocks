import subprocess

process = subprocess.Popen("ssh blacksun.cs.mcgill.ca", shell=True,
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
output,stderr = process.communicate()
status = process.poll()
print output
