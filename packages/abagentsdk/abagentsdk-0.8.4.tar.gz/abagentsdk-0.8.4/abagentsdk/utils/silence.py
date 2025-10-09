# abagentsdk/utils/silence.py
from __future__ import annotations

import io
import os
import re
import sys
from typing import Iterable

# Set env BEFORE any heavy libs load
os.environ.setdefault("GRPC_VERBOSITY", "ERROR")
os.environ.setdefault("GRPC_LOG_SEVERITY_OVERRIDE", "ERROR")
os.environ.setdefault("ABSL_LOGGING_STDERR_THRESHOLD", "3")  # ERROR
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("GLOG_minloglevel", "3")
os.environ.setdefault("FLAGS_minloglevel", "3")

# Patterns to drop from stderr
_DEFAULT_PATTERNS = (
    r"All log messages before absl::InitializeLog\(\) is called are written to STDERR",
    r"alts_credentials\.cc:\d+\] ALTS creds ignored\. Not running on GCP and untrusted ALTS is not enabled\.",
)

class _FilteringStderr(io.TextIOBase):
    def __init__(self, wrapped: io.TextIOBase, patterns: Iterable[str]):
        self._wrapped = wrapped
        self._regexes = [re.compile(p) for p in patterns]

    def write(self, s: str) -> int:
        lines = s.splitlines(True)  # keep \n
        kept = []
        for ln in lines:
            if any(rx.search(ln) for rx in self._regexes):
                continue  # drop noisy line
            kept.append(ln)
        if not kept:
            return len(s)
        return self._wrapped.write("".join(kept))

    def flush(self) -> None:
        return self._wrapped.flush()

def install_stderr_filter(patterns: Iterable[str] = _DEFAULT_PATTERNS) -> None:
    """Install a process-wide stderr filter to hide noisy native logs."""
    if getattr(sys, "_abz_stderr_filtered", False):
        return
    sys.stderr = _FilteringStderr(sys.stderr, patterns)  # type: ignore
    setattr(sys, "_abz_stderr_filtered", True)

def reduce_absl_logging() -> None:
    """Ask absl (if present) to only emit ERROR+."""
    try:
        from absl import logging as _absl_logging  # type: ignore
        _absl_logging.set_verbosity(_absl_logging.ERROR)
        _absl_logging.set_stderrthreshold("error")
    except Exception:
        pass

def install_silence() -> None:
    """One-shot setup to reduce logs + filter stderr."""
    install_stderr_filter()
    reduce_absl_logging()
