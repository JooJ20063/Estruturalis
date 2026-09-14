# Contributing to Estruturalis

Thank you for your interest in contributing to Estruturalis.

Estruturalis is an academic and open-source structural engineering project developed with an emphasis on small, testable, reviewable and well-documented changes.

Because the project performs structural calculations, numerical correctness and explicit engineering assumptions are particularly important.

---

## Areas of Contribution

Contributions may include:

- bug fixes;
- analytical validation cases;
- external benchmark comparisons;
- new structural examples;
- documentation improvements;
- numerical robustness improvements;
- post-processing improvements;
- report improvements;
- visualization improvements;
- performance improvements;
- code organization;
- test coverage;
- new structural-analysis features;
- preliminary design modules.

---

## Development Principles

Whenever reasonably possible, a new feature should include:

- a clear purpose;
- an example;
- automated validation;
- regression coverage;
- documented assumptions;
- documented limitations;
- readable output.

New functionality should not silently change previously validated behavior.

---

## Structural Analysis and Design Separation

Estruturalis intentionally separates:

```text
Structural Analysis Core
        │
        ▼
Post-Processing
        │
        ▼
Preliminary Design / Normative Modules
```

Structural-analysis code should not depend on preliminary reinforced-concrete design routines.

Normative or design modules should consume structural-analysis results rather than modifying solver mechanics.

The future GUI must also remain separated from structural-analysis formulas.

---

## Recommended Git Workflow

Start from an updated `main` branch:

```bash
git checkout main
git pull origin main
```

Create a dedicated branch:

```bash
git checkout -b descriptive-branch-name
```

Examples:

```text
fix-frame3d-transformation
add-frame3d-validation-case
improve-displacement-report
document-local-axis-convention
```

Keep changes focused whenever possible.

---

## Before Making Changes

If your contribution affects structural mechanics, first identify:

- which formulation is changing;
- which existing validation cases may be affected;
- what analytical or independent reference will be used;
- whether the change modifies public model conventions.

Changes to solver mechanics require stronger justification than purely presentational changes.

---

## Required Validation

Before opening a pull request, run:

```bash
python -m compileall app core io_module plots scripts
```

For changes that may affect Frame3D behavior, run the complete Frame3D core validation:

```bash
python scripts/validate_frame3d_core.py
```

This currently executes:

```text
Python compilation
Frame3D integration validation
Frame3D analytical validation
Frame3D robustness/failure validation
```

A successful run must end with:

```text
CORE FRAME3D VALIDATED: 4/4 blocks passed
```

---

## Individual Frame3D Validation Suites

The validation components may also be executed independently:

```bash
python scripts/validate_frame3d_examples.py
```

```bash
python scripts/validate_frame3d_analytical.py
```

```bash
python scripts/validate_frame3d_failures.py
```

Use individual suites during development when appropriate, but run the consolidated validation before submitting solver-related changes.

---

## Representative Smoke Tests

It is also useful to manually run representative analyses.

### Frame2D

```bash
python app/main.py \
    examples/viga_carga_central.json \
    -o results/test_frame2d
```

### Frame3D

```bash
python app/main.py \
    examples/portico_3d_simples.json \
    -o results/test_frame3d
```

---

## Analytical Validation Requirements

New solver behavior should preferably be validated against one or more of:

1. a closed-form analytical solution;
2. an independently derived stiffness-method solution;
3. a trusted academic reference problem;
4. a recognized structural-analysis program.

External software comparison alone should not replace analytical validation when a practical analytical solution exists.

---

## Numerical Tolerances

Do not arbitrarily loosen validation tolerances to make a failing test pass.

If a tolerance must change, explain:

- why the previous tolerance was inappropriate;
- the numerical behavior observed;
- why the new tolerance is justified.

Structural regression tests should detect meaningful solver changes while allowing ordinary floating-point error.

---

## Failure and Robustness Tests

Invalid structural models should fail clearly and predictably.

When adding validation rules, consider adding a corresponding case to:

```text
scripts/validate_frame3d_failures.py
```

A valid controlled-failure test should verify that:

- the process exits with a non-zero status;
- the expected error condition is reported;
- a successful analysis is not incorrectly announced.

---

## Pull Request Scope

Prefer small and focused pull requests.

A good pull request should have:

- a clear objective;
- a descriptive title;
- minimal unrelated changes;
- readable code;
- appropriate tests;
- updated documentation when necessary.

Avoid mixing unrelated changes such as:

```text
solver modification
+
report redesign
+
large documentation rewrite
+
unrelated cleanup
```

Separate these into independent pull requests whenever practical.

---

## Pull Request Description

For structural or numerical changes, describe:

```text
What changed?
Why was it necessary?
Which formulation is affected?
How was it validated?
What are the numerical results?
Were existing results changed?
```

If the change intentionally modifies previous numerical behavior, state this explicitly.

---

## Coding Style

Prefer:

- clear names;
- short focused functions;
- explicit units where relevant;
- type hints where practical;
- readable mathematical implementation;
- comments explaining non-obvious engineering decisions.

Avoid comments that merely repeat the code.

Comments are most useful when they explain:

- structural assumptions;
- sign conventions;
- coordinate transformations;
- derivation choices;
- numerical safeguards.

---

## Structural Conventions

Current major conventions include:

### Frame2D

Degrees of freedom:

```text
ux
uy
rz
```

### Frame3D

Degrees of freedom:

```text
ux
uy
uz
rx
ry
rz
```

Frame3D local end forces are reported in the local coordinate system of each element.

Do not change:

- degree-of-freedom ordering;
- local-axis construction;
- sign conventions;
- result field names;

without explicit discussion, documentation, migration consideration and regression testing.

These conventions are expected to become formally frozen before `v1.0.0`.

---

## Examples

Example input files belong in:

```text
examples/
```

Examples should:

- have descriptive names;
- represent one clear structural purpose;
- avoid unnecessary complexity;
- be usable in validation whenever possible.

Invalid-model examples intended for robustness testing may also live in the examples/test infrastructure where appropriate.

---

## Generated Results

Generated results should normally be written under:

```text
results/
```

Do not commit generated analysis output unless it serves a deliberate documentation, fixture or regression purpose.

---

## Documentation

When adding or changing functionality, review whether the following require updates:

```text
README.md
ROADMAP.md
CONTRIBUTING.md
AUTHORS.md
docs/frame3d.md
examples/
generated report descriptions
```

Changes to public model behavior should always be documented.

---

## Reports

Generated engineering reports should clearly distinguish, where applicable:

- calculated values;
- minimum values;
- maximum values;
- adopted values;
- warnings;
- unsupported conditions.

Preliminary routines must state their assumptions and limitations.

---

## Preliminary Design Modules

Preliminary structural-design routines must never be described as complete professional design verification unless they genuinely reach that level and are independently validated.

Use explicit terminology such as:

```text
preliminary
experimental
unsupported
validated
```

where appropriate.

---

## Error Handling

Prefer clear engineering error messages over raw low-level exceptions.

For example, prefer:

```text
Model is unstable or contains insufficient restraints.
```

over exposing an unexplained matrix-factorization error.

Internal exceptions may still be useful during debugging, but user-facing behavior should become progressively clearer as the project matures.

---

## Continuous Integration

GitHub Actions currently validates the project on supported Python versions.

A pull request should not be merged when required CI checks are failing unless the failure is understood and deliberately addressed.

Do not bypass validation simply to obtain a green workflow.

---

## Compatibility

Avoid unnecessary changes to existing input files and output schemas.

Before `v1.0.0`, some interfaces may still evolve, but compatibility should already be treated seriously.

Breaking changes should be:

- intentional;
- documented;
- justified;
- tested.

---

## Security and Safety

Do not add code that executes arbitrary input as Python.

Input files should be treated as data.

Structural calculations should fail safely when input is malformed, incomplete or unsupported.

---

## Commit Messages

Use concise messages that describe the change.

Examples:

```text
validate spatial Frame3D assembly
fix global distributed load transformation
document Frame3D local axes
add invalid material regression test
```

Avoid vague messages such as:

```text
changes
fix stuff
update
```

---

## Submitting the Pull Request

After validation:

```bash
git status
git diff --check
```

Commit:

```bash
git add .
git commit -m "clear description of the change"
```

Push:

```bash
git push -u origin descriptive-branch-name
```

Then open a pull request targeting:

```text
main
```

---

## Technical Disclaimer

Estruturalis is an academic structural engineering project under active development.

Contributions are welcome, but practical use of generated results requires independent verification and the technical responsibility of a qualified professional.