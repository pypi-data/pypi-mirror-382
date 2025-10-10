# SPDX-FileCopyrightText: 2025 ModelCloud.ai
# SPDX-FileCopyrightText: 2025 qubitium@modelcloud.ai
# SPDX-License-Identifier: Apache-2.0
# Contact: qubitium@modelcloud.ai, x.com/qubitium

from __future__ import annotations

import sys
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from setup_utils import MODULE_SOURCES, collect_build_config


EXTENSION = Extension(
    name="pcre_ext_c",
    sources=MODULE_SOURCES,
    **collect_build_config(),
)

setup(ext_modules=[EXTENSION], cmdclass={"build_ext": build_ext})
