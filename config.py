import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d.%b.%Y %H:%M:%S')
logger = logging.getLogger(__name__)
