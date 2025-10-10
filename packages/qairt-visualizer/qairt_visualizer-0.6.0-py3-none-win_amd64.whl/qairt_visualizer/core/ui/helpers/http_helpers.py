# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

"""HTTP related helpers"""

from typing import Dict, List, Optional, Union
from urllib.parse import parse_qs


def extract_query_params(
    query_string: str, params_list: Optional[List[str]] = None
) -> Union[Dict[str, str], Dict[str, List[str]]]:
    """Extracts query parameters from a given query parameter string and returns a dict

    :param query_string: The query string key from the environ dictionary
    :param params_list: The list of parameters that needs to be
            fetched from the query string

    :return: A dictionary containing the parameters and their values
            as requested in the params list, or a dictionary containing all the key value
            pairs present in the query_string(if no params list is provided)

    :raise: Raises KeyError in case of missing parameter in the query string
    """
    parsed_query_params = parse_qs(query_string)
    param_values: Dict[str, str] = {}

    if params_list:
        for param in params_list:
            param_values[param] = parsed_query_params[param][0]

    return param_values or parsed_query_params
