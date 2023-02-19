from shutil import copy, rmtree
from os import remove, listdir
from subprocess import Popen
from zipfile import ZipFile
from urllib import request
from sys import argv, exit


if len(argv) == 3:
    self_path, url, name_version = argv
else:
    print("Updater can't work by itself")
    input()
    exit()

print("<Update tool>")
print()
print("Download...  ('this may take a few minutes')")

request.urlretrieve(url, "UPDATE.zip")
ZipFile("UPDATE.zip").extractall("UPDATE")

print("SUCCESS!")
print("Unpack... ('this may take a few seconds')")

for elem in listdir(f'UPDATE\\{name_version}\\'):
    copy(f'UPDATE\\{name_version}\\{elem}', '.')

print("SUCCESS!")
print("Clear... ('this may take a few seconds')")

remove("UPDATE.zip")
rmtree("UPDATE")

print("SUCCESS!", '\n')
Popen(["Sea_battle.exe"])
input("You can close this window or tap 'enter' \n>>>")
