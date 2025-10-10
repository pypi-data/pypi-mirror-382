# -*- coding: utf-8 -*-
"""
    RAISE Synthetic Data Generator

    @author: Mikel Hernández Jiménez - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @author: Mikel Catalina Olazaguirre - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @version: 0.1
"""

# import os
# import sys

# path = os.path.abspath(os.path.dirname(__file__))
# if path not in sys.path:
#     sys.path.append(path)
# path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "src")
# if path not in sys.path:
#     sys.path.append(path)

from raise_synthetic_data_generator.config.logger import LogClass
from raise_synthetic_data_generator.utils.paths import (
    prepare_output_folder,
)
from raise_synthetic_data_generator.synthetic_data_generator.generate_synthetic_data import (
    generate_synthetic_data,
)

__all__ = ["LogClass", "prepare_output_folder", "generate_synthetic_data"]
