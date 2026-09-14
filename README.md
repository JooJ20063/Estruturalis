# Estruturalis

**Estruturalis** is an academic and open-source structural analysis project written in Python, focused on two-dimensional and three-dimensional framed structures.

The project started as a small educational implementation of the direct stiffness method and is evolving into a modular platform for structural analysis, validation, post-processing, and preliminary structural design studies.

> **Current milestone:** `v0.4.0 — Validated Frame3D Core`
>
> Estruturalis is an academic project under active development.  
> It does not replace professional structural engineering software, independent verification, or the work of a qualified engineer.

---

## Current Capabilities

### Frame2D

Estruturalis currently supports planar framed structures with:

- 3 degrees of freedom per node:
  - `ux`
  - `uy`
  - `rz`
- axial deformation;
- bending;
- nodal loads;
- uniformly distributed loads;
- automatic self-weight;
- load cases;
- load combinations;
- reactions;
- nodal displacements;
- internal forces;
- force envelopes;
- preliminary deflection verification;
- preliminary reinforced-concrete beam design;
- JSON, CSV, TXT and PNG outputs.

---

### Frame3D

The `frame3d` solver supports spatial framed structures with:

- 6 degrees of freedom per node:
  - `ux`
  - `uy`
  - `uz`
  - `rx`
  - `ry`
  - `rz`
- 12-degree-of-freedom 3D frame elements;
- axial deformation;
- bending about both local axes;
- torsion;
- local/global coordinate transformations;
- 3D nodal loads;
- distributed loads in local coordinates;
- distributed loads in global coordinates;
- automatic self-weight;
- load cases;
- linear load combinations;
- 3D reactions;
- translations and rotations;
- local element end forces;
- global 3D equilibrium verification;
- 3D force envelopes;
- displacement and drift reports;
- preliminary beam reports;
- critical column force reports;
- shear and torsion beam reports;
- integrated 3D memorial reports;
- static 3D plots;
- interactive 3D HTML visualization.

---

## Frame3D Validation Status

Starting with `v0.4.0`, the Frame3D core is covered by a consolidated validation pipeline.

Current validation includes:

- integration testing;
- analytical structural mechanics verification;
- multi-element compatibility;
- inclined-member transformations;
- self-weight;
- load combinations;
- non-coplanar spatial structures;
- controlled invalid-model testing;
- global equilibrium verification.

Current automated analytical suite:

```text
10/10 analytical cases passed
```

Current controlled failure suite:

```text
9/9 failure cases passed
```

Consolidated Frame3D validation:

```text
4/4 validation blocks passed
```

Maximum observed relative error in the analytical suite:

```text
2.628713e-09
```

The validation pipeline is executed in GitHub Actions on:

```text
Python 3.11
Python 3.12
```

---

## Installation

Clone the repository:

```bash
git clone git@github.com:JooJ20063/Estruturalis.git
cd Estruturalis
```

### Linux / macOS

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Windows

Create a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Running Frame2D Examples

### Beam with central load

```bash
python app/main.py \
    examples/viga_carga_central.json \
    -o results/viga_carga_central
```

### Frame with self-weight

```bash
python app/main.py \
    examples/portico_peso_proprio.json \
    -o results/portico_peso_proprio
```

### Frame with load combinations

```bash
python app/main.py \
    examples/portico_combinacoes.json \
    -o results/portico_combinacoes
```

---

## Running Frame3D Examples

### Cantilever with nodal load

```bash
python app/main.py \
    examples/viga_3d_console.json \
    -o results/viga_3d_console
```

### Cantilever with distributed load

```bash
python app/main.py \
    examples/viga_3d_console_q.json \
    -o results/viga_3d_console_q
```

### Simple 3D portal frame

```bash
python app/main.py \
    examples/portico_3d_simples.json \
    -o results/portico_3d_simples
```

---

## Running the Frame3D Validation Suite

The recommended command for validating the complete Frame3D structural-analysis core is:

```bash
python scripts/validate_frame3d_core.py
```

This runner executes:

```text
1. Python compilation
2. Frame3D integration validation
3. Frame3D analytical validation
4. Frame3D failure and robustness validation
```

A successful run ends with:

```text
============================================================
CORE FRAME3D VALIDATED: 4/4 blocks passed
============================================================
```

Individual validation suites remain available:

```bash
python scripts/validate_frame3d_examples.py
python scripts/validate_frame3d_analytical.py
python scripts/validate_frame3d_failures.py
```

---

## Frame3D Validation Coverage

The analytical suite currently includes:

1. cantilever with concentrated tip load;
2. cantilever with uniform distributed load;
3. pure torsion;
4. pure axial loading;
5. inclined member with global distributed load;
6. multi-element cantilever;
7. simple portal-frame interaction;
8. self-weight;
9. linear load combination;
10. orthogonal non-coplanar spatial frame.

The failure suite currently verifies rejection of:

1. zero-length elements;
2. insufficient restraints;
3. invalid section area;
4. invalid load-combination references;
5. invalid elastic modulus;
6. invalid torsional constant;
7. zero nodal loads;
8. invalid distributed-load coordinate systems;
9. invalid object references.

---

## Main Frame3D Outputs

Depending on the analysis configuration, Frame3D runs may generate:

```text
resultados.json

envoltoria_3d.json
envoltoria_3d.csv
resumo_envoltoria_3d.txt

deslocamentos_3d.csv
resumo_deslocamentos_3d.txt

dimensionamento_vigas_3d.csv
resumo_dimensionamento_vigas_3d.txt

vigas_cortante_torcao_3d.csv
resumo_vigas_cortante_torcao_3d.txt

pilares_3d.csv
resumo_pilares_3d.txt

memorial_3d.txt

estrutura_3d.png
deformada_3d.png
estrutura_3d_interativa.html
resumo_grafico_3d.txt

resumo_flechas.txt
```

For an initial overview of a 3D analysis, the recommended report is:

```text
memorial_3d.txt
```

---

## Project Architecture

Estruturalis aims to maintain a clear separation between structural mechanics and higher-level features.

Conceptually:

```text
Input / GUI / CLI
        │
        ▼
Application Layer
        │
        ▼
Structural Analysis Core
        │
        ▼
Post-Processing
        │
        ▼
Preliminary Design / Normative Modules
```

The structural-analysis solver should remain independent of graphical interfaces and normative design routines.

---

## Structural Analysis Scope

The current analysis core is primarily based on:

- linear elastic structural analysis;
- small-displacement theory;
- beam/frame elements;
- direct stiffness method.

The project currently focuses on framed structures.

Advanced nonlinear and continuum finite-element formulations are outside the present stable scope.

---

## Current Limitations

Estruturalis remains an academic project and has important limitations.

Among them:

- no complete normative structural design;
- preliminary reinforced-concrete routines remain experimental;
- no complete reinforcement detailing;
- no complete `N + My + Mz` column design verification;
- no material nonlinearity;
- no geometric nonlinearity;
- no plastic-hinge analysis;
- no P-Delta analysis;
- no dynamic analysis;
- no eigenvalue buckling analysis;
- no shell elements;
- no plate elements;
- no solid finite elements;
- no slab module;
- no wall module;
- no complete foundation-design module.

These limitations will be reviewed and formally documented before the first stable release.

---

## Documentation

Project documentation includes:

- [Frame3D documentation](docs/frame3d.md)
- [Development roadmap](ROADMAP.md)
- [Contributing guidelines](CONTRIBUTING.md)
- [Authors](AUTHORS.md)

---

## Development Roadmap

The planned release path is:

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

See [ROADMAP.md](ROADMAP.md) for detailed milestone definitions.

---

## Development Philosophy

Estruturalis follows a simple principle:

> A smaller structural-analysis system whose behavior can be demonstrated is preferable to a larger system whose numerical behavior cannot be verified.

Whenever practical, new functionality should include:

- an example;
- validation;
- regression testing;
- documented assumptions;
- documented limitations;
- readable output.

---

## Contributing

Contributions involving the following areas are welcome:

- bug fixes;
- structural validation;
- analytical reference cases;
- documentation;
- examples;
- post-processing;
- numerical robustness;
- graphical visualization;
- code organization.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

---

## Authors

Estruturalis was created and is currently developed by **José Francisco Nunes Marcondes**.

See [AUTHORS.md](AUTHORS.md) for authorship information.

---

## License

Estruturalis is open-source software distributed under the **GNU General Public License v3.0**.

---

## Technical Disclaimer

Estruturalis is an academic structural engineering project under active development.

Results produced by the software must be independently reviewed and should not be used as the sole basis for structural design, construction decisions, safety assessments, or professional engineering work.

Use of the software does not replace engineering judgment or the responsibility of a qualified professional.