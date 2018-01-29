# coding=utf-8
import os

name = "MainKitsu.py"

kill = "pkill -f %s" % name

os.system("echo Kaikyudev1! | sudo -S %s" % kill)
#Exception os.system("sudo pkill -f bash")
os.system("sudo nohup python3 %s" % name)
