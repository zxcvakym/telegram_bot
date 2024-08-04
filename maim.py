import asyncio
import logging
import sys

from app import main

# Точка входу
if __name__ == "__main__":
   logging.basicConfig(level=logging.INFO, stream=sys.stdout)
   asyncio.run(main())
   