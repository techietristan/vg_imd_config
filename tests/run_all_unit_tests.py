import subprocess

subprocess.run(['coverage', 'xml'])
subprocess.run(['coverage', 'run', '-m', 'unittest', 'discover'])