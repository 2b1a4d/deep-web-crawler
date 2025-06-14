import os

"""
在本机上，使用已有的环境运行主从式系统
多机分布式系统，配置便携式环境后，使用bat脚本运行
"""

os.system('start cmd.exe /C python Master.py')
os.system('start cmd.exe /C python Slave.py')
