# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

"""Model object validator"""


def validate_model(obj):
    """Validates the view() call 'model' argument"""
    if not isinstance(obj, str) and not obj.__class__.__name__ == "Model":
        raise TypeError(
            "The view() function's optional model argument requires a QAIRT "
            "Model object or a string file path"
        )
