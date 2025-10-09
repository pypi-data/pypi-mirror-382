######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.10.1+obcheckpoint(0.2.8);ob(v1)                                                   #
# Generated on 2025-10-08T21:13:44.486198                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.event_logger


class DebugEventLogger(metaflow.event_logger.NullEventLogger, metaclass=type):
    @classmethod
    def get_worker(cls):
        ...
    ...

class DebugEventLoggerSidecar(object, metaclass=type):
    def __init__(self):
        ...
    def process_message(self, msg):
        ...
    ...

