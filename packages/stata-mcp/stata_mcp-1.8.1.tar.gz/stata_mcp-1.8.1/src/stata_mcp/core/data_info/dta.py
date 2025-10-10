#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam (谭淞)
# @Email  : sepinetam@gmail.com
# @File   : dta.py

from pathlib import Path

import pandas as pd

from ._base import DataInfoBase


class DtaDataInfo(DataInfoBase):
    def _read_data(self) -> pd.DataFrame:
        """
        Read Stata dta file into pandas DataFrame.

        Returns:
            pd.DataFrame: The data from the Stata file

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file is not a valid Stata file
        """
        # Convert to Path object if it's a string
        file_path = Path(self.data_path)

        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(f"Stata file not found: {file_path}")

        # Check if it's a .dta file
        if file_path.suffix.lower() != '.dta':
            raise ValueError(f"File must have .dta extension, got: {file_path.suffix}")

        try:
            # Read the Stata file
            # Using read_stata with convert_categoricals=False to avoid converting labels to categories
            # This preserves the original data structure without converting value labels
            df = pd.read_stata(
                file_path,
                convert_categoricals=False,  # disable change data to mapped str.
                convert_dates=True,
                convert_missing=False,
                preserve_dtypes=True
            )
            return df

        except Exception as e:
            raise ValueError(f"Error reading Stata file {file_path}: {str(e)}")
