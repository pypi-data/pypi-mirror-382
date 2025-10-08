# abagent/utils/silence.py
from __future__ import annotations
import os

def silence_native_logs() -> None:
    os.environ.setdefault("GRPC_VERBOSITY", "ERROR")
    os.environ.setdefault("GRPC_LOG_SEVERITY_OVERRIDE", "ERROR")
    os.environ.setdefault("ABSL_LOGGING_STDERR_THRESHOLD", "3")
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
    os.environ.setdefault("GLOG_minloglevel", "3")
    os.environ.setdefault("FLAGS_minloglevel", "3")
    try:
        from absl import logging as absl_logging
        absl_logging.set_verbosity(absl_logging.ERROR)
        absl_logging.set_stderrthreshold("error")
    except Exception:
        pass
