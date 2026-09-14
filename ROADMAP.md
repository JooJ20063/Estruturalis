# Estruturalis Roadmap

This document describes the planned development path of Estruturalis from the current validated structural-analysis core toward the first stable release.

The roadmap is intentionally milestone-driven rather than date-driven.

Estruturalis is developed as an academic and open-source structural engineering project. Priorities may change as validation results, architectural decisions, new requirements, and available development time evolve.

---

# Current Status

Current development baseline:

```text
v0.4.0 — Validated Frame3D Core
```

The following major components are already available:

- 2D frame analysis;
- 3D frame analysis;
- direct stiffness method;
- nodal loads;
- distributed loads;
- local and global load coordinates;
- self-weight;
- load cases;
- linear load combinations;
- reactions;
- displacements;
- rotations;
- local element forces;
- global equilibrium verification;
- 2D and 3D graphical output;
- interactive 3D visualization;
- envelopes;
- structural reports;
- preliminary design/reporting modules;
- analytical Frame3D validation;
- failure and robustness validation;
- continuous integration on multiple Python versions.

The Frame3D basic structural mechanics validation stage was completed in `v0.4.0`.

---

# Development Principles

Estruturalis should evolve through small, testable and reviewable increments.

Whenever reasonably possible, every new structural feature should include:

- a documented example;
- automated validation;
- regression tests;
- explicit assumptions;
- explicit limitations;
- clear output;
- compatibility with the existing analysis core.

New functionality should not silently break previously validated behavior.

Structural analysis, post-processing, normative design and graphical interfaces should remain architecturally separated.

---

# Version Roadmap

```text
v0.4.0
Validated Frame3D Core
    │
    ▼
v0.5.0
Documentation & Post-Processing Consolidation
    │
    ▼
v0.6.0
Preliminary Design & Normative Layer Consolidation
    │
    ▼
v0.7.0
CLI, Packaging & Distribution
    │
    ▼
v0.7.5
Graphical User Interface
    │
    ▼
v0.8.0
Extended Validation & Regression Hardening
    │
    ▼
v0.9.0
API, Input Schema & Architecture Freeze
    │
    ▼
v1.0.0-rc.1
First Release Candidate
    │
    ▼
v1.0.0
First Stable Release
```

---

# v0.4.0 — Validated Frame3D Core

**Status: COMPLETE**

The purpose of `v0.4.0` was to establish a trustworthy numerical baseline for three-dimensional frame analysis.

## Completed

- Frame3D analytical validation suite;
- cantilever validation;
- distributed-load validation;
- pure axial validation;
- pure torsion validation;
- inclined-member validation;
- global/local transformation validation;
- multi-element compatibility validation;
- portal-frame validation;
- self-weight validation;
- load-combination validation;
- non-coplanar spatial-frame validation;
- global equilibrium verification;
- controlled failure tests;
- consolidated Frame3D validation runner;
- GitHub Actions integration.

Current analytical validation:

```text
10/10 analytical cases passed
```

Current robustness validation:

```text
9/9 failure cases passed
```

Current consolidated validation:

```text
4/4 validation blocks passed
```

Continuous integration:

```text
Python 3.11 — PASS
Python 3.12 — PASS
```

Maximum observed relative error in the analytical Frame3D suite:

```text
2.628713e-09
```

---

# v0.5.0 — Documentation & Post-Processing Consolidation

**Status: PLANNED**

The objective of `v0.5.0` is to transform the validated analysis core into a consistently documented and easier-to-understand engineering package.

This release should focus primarily on consolidation rather than adding major new structural formulations.

## Documentation

- rewrite and consolidate public documentation;
- document Frame2D conventions;
- document Frame3D conventions;
- document global axes;
- document local element axes;
- document degree-of-freedom ordering;
- document force and moment sign conventions;
- document reaction conventions;
- document distributed-load conventions;
- document supported units;
- document material definitions;
- document section definitions;
- document support definitions;
- document load cases;
- document load combinations;
- document self-weight behavior;
- document analysis limitations.

## Input documentation

Create a complete description of the current JSON input format.

Documentation should include:

- nodes;
- elements;
- materials;
- sections;
- supports;
- nodal loads;
- distributed loads;
- load cases;
- load combinations;
- analysis type;
- self-weight configuration.

Representative example files should be explicitly documented.

## Post-processing

Consolidate the existing output system.

Goals:

- standardize CSV field names;
- standardize TXT reports;
- standardize JSON output;
- improve output directory organization;
- improve report readability;
- clearly separate:
  - calculated values;
  - minimum values;
  - maximum values;
  - adopted values;
- review 2D/3D output consistency.

## Reports

Review and consolidate:

- displacement reports;
- drift reports;
- deflection reports;
- internal-force summaries;
- envelopes;
- integrated memorials;
- graphical summaries.

## Validation documentation

Create formal documentation describing:

- analytical reference equations;
- validation methodology;
- adopted numerical tolerances;
- expected numerical precision;
- known solver limitations.

## Independent comparison

Perform at least one external comparison against:

- a recognized structural analysis program;
- a trusted academic implementation;
- or a published reference problem.

This comparison should not replace analytical validation.

It should act as an additional independent verification layer.

## Project maintenance

- create/update `CHANGELOG.md`;
- review duplicated modules;
- remove dead code;
- remove unused imports;
- improve naming consistency;
- reduce unnecessary warnings;
- improve developer documentation.

## Exit criteria

`v0.5.0` should be released when:

- the public documentation describes the supported analysis workflow;
- structural conventions are documented;
- post-processing outputs are reasonably standardized;
- validation assumptions are documented;
- no major documentation gap requires reading solver source code to understand basic behavior.

---

# v0.6.0 — Preliminary Design & Normative Layer Consolidation

**Status: PLANNED**

The objective of `v0.6.0` is to organize and improve the existing preliminary design and normative functionality without mixing it with the validated structural-analysis core.

Structural analysis and structural design must remain separate layers.

## Architecture

Target conceptual separation:

```text
Structural Analysis Core
        │
        ▼
Post-Processing
        │
        ▼
Design / Normative Modules
```

Normative modules must consume structural-analysis results without embedding normative logic inside the solver.

## Normative organization

- organize normative parameters into dedicated modules;
- improve NBR-related code organization;
- clearly identify configurable parameters;
- separate normative constants from solver mechanics;
- improve normative report structure.

## Beam design

Improve preliminary beam verification for:

- flexure;
- minimum reinforcement;
- maximum reinforcement;
- governing reinforcement;
- biaxial moment reporting where applicable.

## Shear

Implement or improve preliminary checks for:

- shear demand;
- preliminary concrete contribution;
- preliminary transverse reinforcement requirements;
- explicit validity limits.

## Torsion

Implement preliminary torsional verification.

Clearly document:

- assumptions;
- simplified procedures;
- unsupported interactions.

## Columns

Expand preliminary column reporting.

Study and progressively introduce:

```text
N + My + Mz
```

interaction.

Initial implementations may remain explicitly experimental.

## Serviceability

Improve:

- deflection verification;
- displacement limits;
- drift reporting;
- serviceability combination handling.

## Mandatory limitation policy

Every preliminary design routine must explicitly state whether it is:

```text
experimental
preliminary
validated
unsupported
```

No preliminary routine should be presented as a replacement for professional structural design software.

## Exit criteria

`v0.6.0` should provide a coherent preliminary design layer while maintaining strict separation from the structural analysis solver.

---

# v0.7.0 — CLI, Packaging & Distribution

**Status: PLANNED**

The purpose of `v0.7.0` is to make Estruturalis easier to install and operate outside the development environment.

## Command-line interface

Target interface:

```bash
estruturalis --help
estruturalis --version
estruturalis model.json
estruturalis model.json -o results/
```

Study/add options such as:

```bash
--no-plots
--no-html
--validate-only
--quiet
```

## CLI behavior

Define stable process exit codes.

Example:

```text
0   successful analysis
1+  analysis/input/application failure
```

Error messages should be readable and should avoid exposing raw internal exceptions whenever a clear engineering error can be reported.

## Packaging

Introduce or consolidate:

```text
pyproject.toml
```

Target installation:

```bash
pip install .
```

A later public package distribution may allow:

```bash
pip install estruturalis
```

## Dependencies

- audit runtime dependencies;
- separate development dependencies where appropriate;
- document supported Python versions;
- run `pip check` in CI;
- minimize unnecessary dependencies.

## Experimental executable

Study PyInstaller or another distribution method.

Possible output:

```text
Estruturalis executable
```

This is desirable but not necessarily mandatory for the release.

## Installation documentation

Create instructions for:

- Linux;
- Windows;
- virtual environments;
- Python installation;
- project execution;
- troubleshooting.

## Exit criteria

A user unfamiliar with the repository internals should be able to install Estruturalis and run a documented structural example from the command line.

---

# v0.7.5 — Graphical User Interface

**Status: PLANNED**

`v0.7.5` is reserved specifically for the first usable Estruturalis graphical user interface.

The objective is not to build a complete CAD system.

The objective is:

> Allow a user to create, edit, analyze and inspect an Estruturalis model without manually editing JSON files.

## Architectural requirement

The GUI must remain separated from structural mechanics.

Target architecture:

```text
┌─────────────────────────┐
│           GUI           │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Application / Services  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Structural Analysis Core│
└─────────────────────────┘
```

The GUI must not contain independent structural-analysis formulas.

It should operate through the same model and analysis interfaces used by CLI workflows.

## Project management

GUI should support:

- create project;
- open project;
- save project;
- save as;
- project metadata;
- recent projects.

## Model editor

Allow editing of:

- nodes;
- elements;
- materials;
- sections;
- supports;
- nodal loads;
- distributed loads;
- load cases;
- load combinations.

## Structural table editor

A table-based model editor is sufficient for the first GUI release.

The first GUI does not require full CAD-style drawing.

## Visualization

Provide visual representation of:

- nodes;
- elements;
- supports;
- nodal loads;
- distributed loads;
- node IDs;
- element IDs;
- global axes.

## 3D visualization

Integrate existing 3D visualization capabilities where practical.

Allow:

- orbit;
- zoom;
- pan;
- structure visualization;
- deformed shape visualization.

## Analysis control

Provide GUI actions for:

```text
Validate Model
Run Analysis
Open Results
```

## Results

Display:

- nodal displacements;
- rotations;
- reactions;
- internal forces;
- equilibrium status;
- structural warnings.

## Reports

Allow access to generated:

- JSON;
- CSV;
- TXT;
- PNG;
- HTML;
- memorials.

## GUI scope exclusions

The first GUI does not require:

- full CAD capabilities;
- BIM integration;
- finite-element mesh editing;
- reinforcement drawing;
- advanced snapping;
- parametric architectural modeling;
- professional drafting tools.

These may be explored in future versions.

## Exit criteria

A user should be able to create and analyze a representative 2D or 3D frame without directly editing the JSON file.

---

# v0.8.0 — Extended Validation & Regression Hardening

**Status: PLANNED**

The objective of `v0.8.0` is to substantially expand the evidence that Estruturalis behaves correctly across a wider range of structural configurations.

## Target validation expansion

The current validation suite should grow from the initial cases toward approximately:

```text
30–50+ reference structural problems
```

The exact number is not a release requirement by itself.

Coverage quality is more important than raw test count.

## Frame2D validation

Expand coverage for:

- simply supported beams;
- fixed-fixed beams;
- cantilevers;
- continuous beams;
- portal frames;
- inclined members;
- asymmetric frames;
- axial/bending interaction;
- distributed loads;
- load combinations;
- self-weight.

## Frame3D validation

Expand coverage for:

- members aligned with X;
- members aligned with Y;
- members aligned with Z;
- arbitrary inclined members;
- biaxial bending;
- bending + torsion;
- axial + bending;
- axial + torsion;
- spatial frames;
- hyperstatic spatial systems;
- multiple load coordinate systems;
- self-weight;
- load combinations;
- multi-story configurations.

## External validation

Compare representative results with established structural-analysis software or trusted academic benchmarks.

Comparisons should include:

- reactions;
- displacements;
- rotations;
- internal forces.

## Failure testing

Expand controlled invalid-model coverage.

Candidate cases:

- duplicate IDs;
- missing materials;
- missing sections;
- missing nodes;
- invalid data types;
- NaN values;
- infinite values;
- empty models;
- disconnected structures;
- singular systems;
- structural mechanisms;
- invalid Poisson ratio;
- malformed combinations;
- unsupported analysis types.

## Numerical robustness

Study:

- matrix conditioning;
- tolerance sensitivity;
- very stiff members;
- very flexible members;
- large coordinate values;
- small coordinate values;
- mixed-scale models.

## Continuous integration

Target matrix may include:

```text
Python 3.11
Python 3.12
Python 3.13
```

when dependencies permit.

Study CI on:

```text
Linux
Windows
```

## Exit criteria

The solver should have broad regression coverage and no known critical numerical issue within its documented formulation scope.

---

# v0.9.0 — API, Input Schema & Architecture Freeze

**Status: PLANNED**

`v0.9.0` is the stabilization release before the first release candidate.

Major architectural changes should become increasingly restricted after this point.

## Input Schema v1

Define and document:

```text
Estruturalis Input Schema v1
```

The schema should formally define:

- nodes;
- elements;
- materials;
- sections;
- supports;
- loads;
- load cases;
- combinations;
- analysis configuration;
- metadata.

## Compatibility objective

Files valid for Estruturalis 1.0 should ideally remain compatible throughout the `1.x` series.

Incompatible schema redesigns should generally require a future major release.

## Structural conventions freeze

Freeze and formally document:

- degree-of-freedom ordering;
- local axes;
- global axes;
- force signs;
- moment signs;
- rotations;
- element-end conventions;
- units;
- result naming;
- reaction conventions.

## Public API

Identify the supported internal/public interfaces for:

- loading models;
- validating models;
- running analyses;
- accessing results;
- generating reports.

Avoid requiring consumers to import arbitrary internal implementation modules.

## Error model

Standardize:

- validation errors;
- solver errors;
- input errors;
- unsupported-feature errors;
- output errors.

## Project structure review

Perform final architecture cleanup before RC.

## Deprecation policy

Introduce a basic policy for features that may need future replacement.

## Exit criteria

`v0.9.0` should represent a nearly frozen architecture.

After this release, development toward 1.0 should prioritize:

```text
bug fixes
documentation
validation
compatibility
release preparation
```

rather than major redesign.

---

# v1.0.0-rc.1 — First Release Candidate

**Status: FUTURE**

A release candidate means:

> The project is believed to be technically suitable for v1.0.0 and is now undergoing final stabilization.

No major new feature should be introduced after the first RC unless necessary to resolve a critical release blocker.

## Required state

### Structural core

Frame2D and Frame3D must have no known critical errors within their documented formulation assumptions.

### Validation

All core validation suites must pass.

### CI

All officially supported environments must pass.

### Documentation

Documentation must cover:

- installation;
- model creation;
- structural conventions;
- examples;
- CLI;
- GUI;
- result interpretation;
- limitations;
- validation methodology.

### Input stability

Input Schema v1 must be frozen.

### Versioning

The application should report:

```text
1.0.0-rc.1
```

### Release candidate cycle

Possible sequence:

```text
v1.0.0-rc.1
v1.0.0-rc.2
v1.0.0-rc.3
```

Additional release candidates should only be created when necessary.

---

# v1.0.0 — First Stable Release

**Status: FUTURE**

`v1.0.0` represents the first stable public baseline of Estruturalis.

It does not mean that every possible structural-analysis or design feature exists.

It means that the functionality declared stable is:

- documented;
- validated;
- regression-tested;
- intentionally versioned;
- supported by stable model conventions.

## Stable scope target

The stable 1.0 structural-analysis scope should include:

### Frame2D

- axial deformation;
- bending;
- nodal loads;
- distributed loads;
- self-weight;
- load cases;
- combinations;
- reactions;
- displacements;
- internal forces;
- equilibrium verification.

### Frame3D

- axial deformation;
- biaxial bending;
- torsion;
- local/global transformations;
- nodal loads;
- local distributed loads;
- global distributed loads;
- self-weight;
- load cases;
- combinations;
- reactions;
- translations;
- rotations;
- internal local forces;
- spatial assembly;
- equilibrium verification.

### Tooling

- stable CLI;
- documented installation;
- usable GUI;
- stable input schema;
- standardized output;
- validation suite;
- CI;
- examples;
- reports.

---

# Analysis Assumptions for the 1.0 Series

Unless explicitly expanded in future development, the 1.0 structural-analysis core is expected to remain based primarily on:

```text
linear elastic structural analysis
small-displacement theory
beam/frame elements
direct stiffness method
```

Features that are not implemented must be clearly documented.

Potential examples include:

```text
material nonlinearity
geometric nonlinearity
plastic hinges
P-Delta analysis
dynamic analysis
eigenvalue buckling
shell elements
solid finite elements
```

The exact limitations must be reviewed before the first release candidate.

---

# Features Not Required for v1.0.0

The following features are not considered mandatory for the first stable release:

- complete reinforced-concrete code implementation;
- complete reinforcement detailing;
- BIM integration;
- shell finite elements;
- plate finite elements;
- solid finite elements;
- advanced nonlinear analysis;
- dynamic analysis;
- seismic analysis;
- professional CAD system;
- complete foundation-design suite.

These may be developed in future minor or major releases.

---

# Future Structural Elements

After the core 1.0 architecture is stable, future development may explore:

- truss elements;
- grids;
- slabs;
- plates;
- walls;
- footings;
- grade beams;
- raft foundations;
- pile caps;
- shell elements;
- additional finite-element formulations.

The priority remains maintaining a reliable bar/frame analysis core before significantly expanding the element library.

---

# Development Priority After v0.4.0

Immediate priorities are:

1. documentation consolidation;
2. post-processing consolidation;
3. roadmap and public project cleanup;
4. incremental normative/design improvements;
5. packaging and CLI preparation;
6. GUI preparation;
7. expanded independent validation.

---

# Development Cadence Note

Estruturalis development may temporarily proceed at a reduced pace while other research and software projects receive higher priority.

The roadmap therefore defines technical milestones rather than fixed release dates.

Maintenance, bug fixes and critical validation improvements may continue independently of major feature development.

---

# Version Summary

| Version | Main Milestone | Status |
|---|---|---|
| `v0.4.0` | Validated Frame3D Core | Complete |
| `v0.5.0` | Documentation & Post-Processing Consolidation | Planned |
| `v0.6.0` | Preliminary Design & Normative Consolidation | Planned |
| `v0.7.0` | CLI, Packaging & Distribution | Planned |
| `v0.7.5` | Graphical User Interface | Planned |
| `v0.8.0` | Extended Validation & Regression Hardening | Planned |
| `v0.9.0` | API, Input Schema & Architecture Freeze | Planned |
| `v1.0.0-rc.1` | First Release Candidate | Future |
| `v1.0.0` | First Stable Release | Future |

---

# Long-Term Goal

The long-term objective of Estruturalis is not simply to accumulate structural-analysis features.

The project should remain:

```text
understandable
testable
documented
reproducible
academically useful
architecturally maintainable
```

A smaller validated structural-analysis system is preferable to a larger system whose numerical behavior cannot be demonstrated.

Every major expansion should preserve the validation baseline established during the development of the Frame2D and Frame3D cores.