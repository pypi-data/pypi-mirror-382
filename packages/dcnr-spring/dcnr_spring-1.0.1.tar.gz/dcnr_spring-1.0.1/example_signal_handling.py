#!/usr/bin/env python3
"""
"""

import time
import logging
import spring_pkg as spring

# Setup logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    spring.actuator.register_actuator_component('time', lambda: {
        'status': 'UP'
    })

    print(spring.actuator.is_ok('time'))

if __name__=="__main__":
    main()