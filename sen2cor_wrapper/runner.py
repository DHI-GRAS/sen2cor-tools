import os
import time
import subprocess
import logging

from .tools import find_classfiles
from .tools import path_L1C_to_L2A

logger = logging.getLogger(__name__)


def run_sen2cor(inSAFE, resolution):
    """Run sen2cor scene classification for L1C a product"""

    root, SAFEbase = os.path.split(inSAFE)
    L2A_path = path_L1C_to_L2A(inSAFE)

    oldwd = os.getcwd()
    os.chdir(root)
    try:
        cmd = ['L2A_Process', '--resolution', str(resolution), '--sc_only', SAFEbase]
        logger.info('sen2cor command: \'{}\''.format(' '.join(cmd)))
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True)
        for line in iter(p.stdout.readline, ''):
            logger.info(line)
        code = p.wait()
        if code != 0:
            raise subprocess.CalledProcessError(code, cmd)
    finally:
        os.chdir(oldwd)

    waited = 0
    while True and waited < 1800:
        try:
            classfiles = find_classfiles(L2A_path)
            if classfiles:
                break
        except ValueError:
            pass
        if waited == 0:
            logger.info('Waiting for sen2cor to finish.')
        time.sleep(30)
        waited += 30

    return classfiles
