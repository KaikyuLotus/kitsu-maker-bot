# coding=utf-8
import os

name = "LastFMTest.py"

kill = "pkill -f %s" % name

os.system("echo Kaikyudev1! | sudo -S %s" % kill)
os.system("sudo python3 %s" % name)
