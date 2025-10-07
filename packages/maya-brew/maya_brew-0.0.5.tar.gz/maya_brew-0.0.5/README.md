# maya-brew

> **Status: Pre-Alpha** – Interfaces are experimental and may change without notice. Pin exact versions if using in
> automation.

What you need after a long day of wrestling with Maya Python.

[![Super-Linter](https://github.com/mortenbohne/maya-brew/actions/workflows/linter.yml/badge.svg)](https://github.com/marketplace/actions/super-linter)

---

## Overview

`maya-brew` aims to provide safer, more structured interaction patterns when scripting or tooling inside Autodesk Maya.

Goals:

- Reduce foot‑guns when using Python inside Maya
- Offer utilities that behave well with Maya’s quirks

## Background

`maya-brew` draws inspiration from some of the ergonomic goals that motivated
[PyMEL](https://github.com/LumaPictures/pymel): making Maya’s Python interface feel more “Pythonic,” safer, and more
discoverable. PyMEL historically provided rich object wrappers around nodes, attributes, and other scene elements;
for many workflows this improved readability and reduced boilerplate.

However, over time several practical factors led to the decision to start a lightweight alternative instead of
extending PyMEL itself:

- Scope & Complexity: PyMEL’s dynamic wrapping and layered abstractions can introduce startup overhead, indirection, and
  occasional debugging friction.
- Historical Churn: A long evolution, multiple contributors, and some legacy design choices make selective modernization
  non‑trivial.
- Maintenance & Momentum: While still usable, PyMEL no longer appears to have the same pace of active development or
  broad community push it once did.
- Adoption Fit: Many pipelines only need a thin set of safety/ergonomic helpers—not a full object layer over
  `maya.cmds`.

### Acknowledgment

PyMEL significantly influenced how many technical artists approach Maya scripting, and this project stands on that
conceptual foundation. `maya-brew` simply narrows the focus: take the useful ergonomic ideas, shed the heavy wrapping,
and keep to the canonical APIs.
