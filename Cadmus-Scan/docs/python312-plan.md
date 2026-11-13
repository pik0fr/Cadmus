# Lot 1 — Python 3.12

Historical plan. The user's subsequent instruction changes the target to Python
3.13 / NumPy 2.1; see [the current baseline](python313-report.md).

Source: develop, e172c0445bb2cbb6116aaeaae771a3a498b99bf3.
Implement the supplied migration specification in place on migration/python312.

1. Record the real baseline, preserve licenses/resources and isolate development dependencies.
2. Add hardware-free tests first: ScanCapture, serial bytes/text, handshake,
   failure callbacks, settings JSON/NumPy, and synthetic triangulation.
3. Port targeted syntax/imports and serial APIs, preserving G-code and geometry.
   Keep np.matrix. Drain the scan queue using its public API; defer thread redesign.
4. Add Python 3.12 core CI for Windows/Linux/macOS and separate GUI requirements.
5. Run compileall, Ruff, pytest and pip check; record unavailable checks and
   residual legacy failures honestly. Also run dependency-light unittest locally.

The supplied document fixes scope and approach; no Qt migration or hardware validation.
Driver connection lifecycle, camera backends, full GUI/runtime migration and
the incomplete platform_by_lasers calibration require follow-up testing.
