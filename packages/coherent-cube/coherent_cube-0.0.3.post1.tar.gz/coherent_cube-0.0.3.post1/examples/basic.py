from time import sleep
from coherent_cube import CoherentCube

l = CoherentCube("COM5")
l.power = 10
l.on()
sleep(10)
l.off()