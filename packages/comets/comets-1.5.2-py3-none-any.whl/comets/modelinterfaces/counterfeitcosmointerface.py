# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ..core.modelinterface import ModelInterface
from ..utilities import get_logger


class CounterfeitCosmoInterface:
    """
    Counterfeit CosmoInterface that will return an explicit error message if the user try to use the CosmoInterface without csm.
    """

    def __init__(
        self,
        simulator_path,
        **kwargs,
    ):
        logger = get_logger(__name__)
        logger.error(
            "Import csm failed. Please make sure that you are executing your code in a context that has access to the"
            " Studio’s python wrappers. This can be done by either:\n\n"
            " - Using the Cosmo Tech Terminal.\n"
            " - Using the command “csm exec [python3|ipython|jupyter-lab]” in a regular terminal."
        )
        custom_error = ImportError(
            "Cannot load the CosmoInterface. Please refer to the log for more information."
        )
        raise custom_error from None
