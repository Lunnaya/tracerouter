#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

from icmplib import traceroute
import sys

target = str(sys.argv[1])
print(target)
if __name__ == "__main__":
    hops = traceroute(target, count=2, interval=0.05, timeout=2, max_hops=20, fast_mode=False)
    for row in hops:
        print(row.distance, row.address, row.avg_rtt)

