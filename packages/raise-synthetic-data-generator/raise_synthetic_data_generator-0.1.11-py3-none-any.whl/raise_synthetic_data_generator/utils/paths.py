# -*- coding: utf-8 -*-
"""
    RAISE Synthetic Data Generator

    @author: Mikel Hernández Jiménez - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @author: Mikel Catalina Olazaguirre - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @version: 0.1
"""

# ============================================
# IMPORTS
# ============================================

# Stdlib imports
from typing import Optional, Union
from pathlib import Path
from datetime import datetime
import re
import os


# ============================================
# GLOBAL CONSTANTS
# ============================================


# ============================================
# CLASSES
# ============================================


# ============================================
# PUBLIC METHODS
# ============================================


def prepare_output_folder(
    output_dir: Optional[Union[str, Path]], run_name: Optional[str]
) -> Path:
    """
    Creates (if it doesn't exist) the output directory to save synthetic data and related objects.

    Args:
        output_dir (Optional[Union[str, Path]]): The base directory path in which the output folder
        will be created. If None, uses current working directory.

        run_name (Optional[str]): The name of the specific run/output subfolder.
        If None, a timestamp-based name is generated.

    Returns:
        Path: The full Path object pointing to the created output folder.

    Raises:
        OSError: If the directory cannot be created due to an OS error.
    """
    # Create output dir if it does not exists
    if output_dir is None:
        output_dir = os.getcwd()
    base = Path(output_dir).expanduser().resolve()
    try:
        base.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Failed to create base directory {base}: {e}")
        raise

    # Create output folder if it does not exists
    if run_name is None:
        run_name = datetime.now().strftime("run-%Y%m%d-%H%M%S")
    # Sanitize run_name to allow only safe characters
    run_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", run_name)
    output_folder = base / run_name
    try:
        output_folder.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Failed to create output folder {output_folder}: {e}")
        raise
    return output_folder


# ============================================
# PRIVATE METHODS
# ============================================


# ============================================
# MAIN BLOCK
# ============================================
