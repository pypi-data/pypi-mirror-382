# SPDX-FileCopyrightText: 2025 cswimr <copyright@csw.im>
# SPDX-License-Identifier: MPL-2.0

from importlib.util import find_spec

if not find_spec("pydantic"):
    msg = "pydantic is not installed, but the `tidegear.pydantic` module was imported! Did you install tidegear with the `pydantic` extra?"
    raise ImportError(msg)

from .basemodel import BaseModel, CogModel
from .httpurl import HttpUrl

__all__ = ["BaseModel", "CogModel", "HttpUrl"]
