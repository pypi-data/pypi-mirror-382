# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

from dataclasses import dataclass
from enum import Enum


@dataclass
class ProductInfo:
    """
    Basic information about a product.
    """

    name: str
    registry: str


class Product(Enum):
    """
    Products which can be accessed using a core client.
    """

    BOULDER_OPAL = ProductInfo(name="boulder-opal", registry="BOULDER_OPAL")

    FIRE_OPAL = ProductInfo(name="fire-opal", registry="FIRE_OPAL")
