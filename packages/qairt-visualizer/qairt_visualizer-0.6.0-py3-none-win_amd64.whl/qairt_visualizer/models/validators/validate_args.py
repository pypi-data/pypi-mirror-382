# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

"""Generic function argument validator"""

import inspect
from functools import wraps


def validate_args(validators):
    """Validates a function's arguments"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_args = inspect.signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()

            for name, validator in validators.items():
                value = bound_args.arguments.get(name)
                if value is not None:
                    validator(value)

            return func(*bound_args.args, **bound_args.kwargs)

        return wrapper

    return decorator
