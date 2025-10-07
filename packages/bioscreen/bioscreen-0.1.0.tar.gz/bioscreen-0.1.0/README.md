# bioscreen

[![PyPI version](https://badge.fury.io/py/bioscreen.svg)](https://badge.fury.io/py/bioscreen)
[![CI](https://github.com/yourusername/bioscreen/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/bioscreen/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/yourusername/bioscreen/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/bioscreen)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A biosecurity screening library for AI protein design tools. Provides simple APIs to flag potentially hazardous protein design requests before processing.

## ⚠️ Version 0.1.0 - Infrastructure Release

This is an infrastructure setup release with minimal functionality. The core screening logic will be implemented in future versions. This release establishes:

- ✅ Package structure and build system
- ✅ Type-safe API design
- ✅ Comprehensive test suite
- ✅ CI/CD pipeline
- ✅ Code quality tooling (Black, Ruff, mypy)

**Current behavior:** All sequences are flagged as `RiskLevel.GREEN` with no actual screening performed.

## Installation

```bash
pip install bioscreen
```

## Quick Start

```python
from bioscreen import ProteinScreener, RiskLevel

# Initialize the screener
screener = ProteinScreener()

# Screen a protein sequence
result = screener.screen_protein("MKTAYIAKQRQISFVKSHFSRQ")

print(f"Flagged: {result.flagged}")
print(f"Risk Level: {result.risk_level}")
print(f"Reason: {result.reason}")
# Output:
# Flagged: False
# Risk Level: RiskLevel.GREEN
# Reason: v0.1.0: No screening rules implemented yet
```