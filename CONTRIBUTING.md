# Team contribution guide

## Before implementation

1. The repository owner adds the other three team members through Settings → Collaborators and invites the instructor using ghanem@staff.birzeit.edu, as specified in the homework. Invitations must be accepted.
2. Agree on one owner for each module, record the four-member roster in README, and assign issues #1–#4. Do not infer ownership from who created an issue.
3. Obtain the exact State-Space Modeling notes (2026 edition), alongside the lecture slides and homework brief.
4. Keep this repository public and separate from the Micromouse robot firmware repository.

## Contributing work

- Work from your own GitHub account. Each member's real contributions must appear in the commit history.
- Link changes to the relevant module issue.
- For changes developed in parallel, use a short branch such as module-1-time-response and open a pull request into main. Check the change before merging.
- Use commit messages that describe the actual work. Do not mark a checklist item complete until its behavior has been verified.
- Keep numerical models in Python. Run them in the browser with the selected Pyodide/PyScript runtime; HTML/CSS and any necessary JavaScript handle browser integration.
- Pin browser runtime and external library versions when selected. Do not add a backend service or login requirement.
- Use the lecture's closed-form responses for required response plots. State input amplitude, initial conditions, units, and gain normalization.
- Keep files readable enough for their author to explain every equation and line of code in the demo.

## Suggested application layout

Create these files when their implementation begins; this guide does not claim that they already exist:

| Path | Purpose |
| --- | --- |
| index.html | Application entry point at the repository root |
| assets/css/styles.css | Responsive page styling |
| assets/js/ | Browser runtime and plotting integration, if needed |
| python/ | Python numerical models and application logic |
| docs/screenshots/ | Verified screenshots for README |

## Before considering a module complete

- Verify its issue's acceptance criteria.
- Check reference calculations independently and display expected, computed, and pass/fail values in the page.
- State tolerances for rounded reference values.
- Test controls and plots on desktop and phone layouts.
- Check the Predict, then check interaction.
- Add a screenshot and record module ownership in README.
- Update the AI assistance disclosure to describe tools actually used. Never include credentials or tokens in commits.

## GitHub Pages setup

Configure this after the application has a working root index.html:

1. Open Settings → Pages.
2. Choose Deploy from a branch.
3. Select main and / (root), then Save.
4. Wait for the Pages deployment to succeed.
5. Open the URL GitHub actually provides on both desktop and phone, and record the verified URL in README.

The .nojekyll file is included so Pages can serve the static files without Jekyll processing. It does not activate Pages or publish an application by itself.

## Delivery

- 3 November 2026: working Module 1 on the live Pages link.
- 9 November 2026: working Modules 2 and 3.
- 12 November 2026: all four modules, release tagged v1.0, and Pages link submitted on the course page.
- 15–16 November 2026: group demos.

No application or deployment has been implemented as part of repository setup.
