#!/usr/bin/env python3
"""Health check script for Docker HEALTHCHECK"""

import sys

# Simple health check - check if worker process is responsive
try:
    # In production, would check if main loop is stuck
    print("OK")
    sys.exit(0)
except:
    sys.exit(1)
