# ENCS4380 Dynamic Characteristics Interactive Toolkit — Team T19

ENCS4380 Interfacing Techniques, Birzeit University. Instructor: Dr. Wasel Ghanem.

An interactive browser toolkit for understanding sensor dynamics through live controls, response plots, and parameter-estimation challenges.

## Current status

Repository setup and module planning are complete. Module 1 has started with a Python function in `python/first_order.py` that computes the zero-initial-condition step response at one time point. Its reference values at t = 0, tau, and 3*tau and its input validation have been checked in a Python interpreter. Browser integration, plots, and the rest of Module 1 are not implemented yet. GitHub Pages has not yet been configured or verified; there is no confirmed live website link.

## Technology decision

- Python executes inside the visitor's browser using Pyodide or PyScript.
- HTML and CSS provide the responsive interface.
- Browser plotting and any necessary JavaScript integration will support live controls and plots.
- The runtime and plotting-library versions will be selected and pinned during implementation.
- The site must run on GitHub Pages without a backend server, Binder, or login. Flask and Django are not part of the deployment.

Python is the agreed implementation language for the numerical models. Required response plots use the lecture's closed-form formulas. A numerical ODE solver is an optional bonus, except where a simulation is used to support the required state-space panel.

## Modules and ownership

| Module | Scope | Tracking issue | Owner |
| --- | --- | --- | --- |
| 1 | First-order time response: step, ramp, lag, and log-error plot | [#1](../../issues/1) | To be assigned by the team |
| 2 | First-order frequency response: sines, Bode plots, and dynamic error | [#2](../../issues/2) | To be assigned by the team |
| 3 | Second-order response, poles, state-space matrices, and phase plane | [#3](../../issues/3) | To be assigned by the team |
| 4 | Guess the sensor: hidden parameters, noise, hints, and scoring | [#4](../../issues/4) | To be assigned by the team |

The full four-member roster, GitHub usernames, and agreed module owners will be recorded once confirmed. Every member must contribute from their own account and be able to explain their code and equations.

## Schedule

| Date (2026) | Deliverable |
| --- | --- |
| 3 November | Checkpoint 1: GitHub Pages live and Module 1 working |
| 9 November | Checkpoint 2: Modules 2 and 3 working |
| 12 November | All four modules; release tagged `v1.0`; submit the Pages link on the course page |
| 15–16 November | Group demos: 10 minutes plus questions |

Each checkpoint is a five-minute check in the lab. The brief specifies a five-point deduction for each missed checkpoint.

## Setup checklist

- [x] Create the public repository using the required naming pattern.
- [x] Create one GitHub Issue per module.
- [ ] Add all team members as collaborators.
- [ ] Add the instructor using `ghanem@staff.birzeit.edu` through repository Settings → Collaborators.
- [ ] Agree on module owners and assign the issues.
- [ ] Implement Module 1 and publish the static site from `main`.
- [ ] Verify the live link on a phone and desktop; record it here.
- [ ] Add screenshots as modules are implemented.

## Validation

The completed page must display each expected result, its computed result, and a pass/fail indicator. Use tolerances appropriate for the rounded reference values.

| Check | Expected result |
| --- | --- |
| First-order step | At tau: approximately 0.632 KA; at 3 tau: approximately 0.95 KA |
| tau = 0.2 s, input sin(2t) | Normalized amplitude ratio approximately 0.93; phase lag 21.8 degrees |
| Up to 100 Hz, at most 5% dynamic error | Maximum tau approximately 0.52 ms; phase lag approximately 9.3 degrees at 50 Hz |
| Second-order zeta = 0.5 | Overshoot approximately 16.3% |
| Second-order zeta = 1 | No overshoot |
| m = 1, b = 2, k = 4 | Eigenvalues and poles: -1 ± j1.732; zeta = 0.5; omega_n = 2 rad/s |

Each module also needs a “Predict, then check” interaction. All controls must work, plots must update live, and layouts must support both phone and desktop screens.

## Course references

- ENCS4380 Homework 1: Dynamic Characteristics Interactive Toolkit, released 29 October 2026.
- Static and Dynamic Characteristics lecture slides.
- State-Space Modeling notes, 2026 edition: Example 3, Sections 6 and 7.1; Section 8 for the optional Micromouse simulation bonus. Obtain and confirm this exact reference before reusing its code.

## AI assistance

ChatGPT assisted with interpreting the homework, comparing browser implementation options, preparing repository documentation and module issue checklists, and writing and checking the initial Python step-response function. Update this disclosure as development proceeds. Team members remain responsible for checking the mathematics, verifying behavior, and explaining the submitted work.
