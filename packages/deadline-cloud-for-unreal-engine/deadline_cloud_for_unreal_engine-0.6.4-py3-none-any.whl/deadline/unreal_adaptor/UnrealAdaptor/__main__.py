# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import os
import sys
import logging

from openjd.adaptor_runtime import EntryPoint

from .adaptor import UnrealAdaptor

__all__ = ["main"]
_logger = logging.getLogger(__name__)


def main(reentry_exe=None) -> int:
    _logger.info("About to start the UnrealAdaptor")

    package_name = vars(sys.modules[__name__])["__package__"]
    if not package_name:
        raise RuntimeError(f"Must be run as a module. Do not run {__file__} directly")

    timeout_in_seconds = float(os.getenv("ADAPTOR_DAEMON_TIMEOUT_IN_SECONDS", 3600.0))
    try:
        EntryPoint(UnrealAdaptor).start(
            reentry_exe=reentry_exe, timeout_in_seconds=timeout_in_seconds  # type: ignore
        )
    except Exception as e:
        _logger.error(f"Entrypoint failed: {e}")
        return 1

    _logger.info("Done UnrealAdaptor main")
    return 0


if __name__ == "__main__":
    sys.exit(main())
