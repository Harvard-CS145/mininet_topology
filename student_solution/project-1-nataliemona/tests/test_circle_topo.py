#!/usr/bin/python3
import json
import os
import sys

from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))
os.chdir(d)

def test_circle_topology():
	print("Testing circle topology")

	print("Topology Unit Tests")
	with open("topology/p4app_circle.json") as f:
		print("Unit Test 1: Link Count")
		topo = json.load(f)
		assert len(topo['topology']['links']) == 6
		print("Test passed")

		print("Unit Test 2: Switch Count")
		assert (len(topo['topology']['switches'])) == 3
		print("Test passed")

		print("Unit Test 3: Host Count")
		assert len(topo['topology']['hosts']) == 3
		print("Test passed")

	print("Controller Unit Tests")
	host_ips = []
	hosts = []
	for i in range(1, 4):
		hosts += ['h{0}'.format(i)]
		host_ips += ['10.0.0.{0}'.format(i)]

	print("Unit Test 4: Ping mesh")
	print("(might take a while)")
	c = 0
	for h in hosts:
		for ip in host_ips:
			assert (" 0% packet loss" in os.popen('mx {0} ping -c 1 {1}'.format(h, ip)).read())
			c += 1
			print(int(c * 100.0 / (16 * 16)),'% complete.', end='\r', flush=True)

	print("")
	print("Test passed")

if __name__ == '__main__':
	test_circle_topology()
