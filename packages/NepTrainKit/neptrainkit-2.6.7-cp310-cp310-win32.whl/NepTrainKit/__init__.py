#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/11/28 12:52
# @Author  :
# @email    : 1747193328@qq.com


# start delvewheel patch
def _delvewheel_patch_1_11_2():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'neptrainkit.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_2()
del _delvewheel_patch_1_11_2
# end delvewheel patch

import sys
from pathlib import Path
from loguru import logger
sys.path.append(str(Path(__file__).resolve().parent))
from NepTrainKit import src_rc

try:
    # Actual if statement not needed, but keeps code inspectors more happy
    if __nuitka_binary_dir is not None: # type: ignore  
        is_nuitka_compiled = True
    else:
        is_nuitka_compiled = False
except NameError:
    is_nuitka_compiled = False

if is_nuitka_compiled:
    logger.add("./Log/{time:%Y-%m}.log",
               level="DEBUG",
                )
    module_path = Path("./").resolve()
else:
    module_path = Path(__file__).resolve().parent
