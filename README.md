# Raven Prism Community App Directory

**An independent, community-maintained directory of software built for Raven Prism.**

> Not affiliated with, endorsed by, or maintained by Raven Resonance. This is a directory of links, **not** an app store, an official compatibility list, or a quality certification.

## Browse

Browse individually identified applications with links to their public sources. This is not a claim about the total number of Raven applications. Event-created apps may not have public repositories or downloadable releases. Two experiences may share one repository.

### Current directory

<!-- BEGIN GENERATED APPS -->
| Application | Category | Developer | Public availability |
| --- | --- | --- | --- |
| [Agent HUD (Raven)](<https://github.com/RBraga01/agent-hud/tree/master/platforms/raven>) | Productivity | RBraga01 | Source code |
| [Art Studio](<https://github.com/RavenResonance/raven-starter-project/tree/main/examples/art_studio>) | Official examples | Raven Resonance | Official example |
| [BlinkSnap](<https://github.com/srcJin/raven-blink-snap>) | Camera & vision | srcJin | Source code |
| [Clear Cue](<https://github.com/JwongtheCodyBoy/raven-starter-project_realityhack2026>) | Accessibility | JwongtheCodyBoy | Source code |
| [Counter / Stopwatch](<https://github.com/RavenResonance/raven-starter-project/tree/main/examples/counter>) | Official examples | Raven Resonance | Official example |
| [Cue](<https://github.com/mjoisgreat/Cue-raven>) | Productivity | mjoisgreat | Source code |
| [DOOMed Prism](<https://github.com/RBraga01/DOOMed-Prism>) | Games | RBraga01 | Source code |
| [DreamLens / Gradient](<https://github.com/Jshengdev/Gradient>) | Developer tools | Jshengdev | Source code |
| [Ease](<https://github.com/srcJin/raven-ease>) | Wellness | srcJin | Source code |
| [EgoGaze](<https://github.com/srcJin/raven-ego-gaze>) | Research | srcJin | Source code |
| [Fireworks Experience](<https://github.com/amirmohideen/raven-ar-glass-experiences-mit/tree/main/fireworks_experience>) | Creative & art | Amir Mohideen | Source code |
| [Hello World](<https://github.com/RavenResonance/raven-starter-project/tree/main/examples/hello_world>) | Official examples | Raven Resonance | Official example |
| [Nail AR](<https://github.com/jayasrisng/nail-AR>) | Guides & learning | jayasrisng | Source code |
| [Nevermore Halloween](<https://github.com/RBraga01/GlassPlay>) | Creative & art | RBraga01 / GlassPlay | Downloadable release |
| [OverBlaster](<https://github.com/OverLord-Labs/OverBlaster-Raven>) | Games | OverLord Labs | Source code |
| [R-EYE-DER](<https://github.com/thejellyshroom/r-eye-der>) | Camera & vision | thejellyshroom | Source code |
| [Raven Muse Control](<https://github.com/ImJustHenry/Raven-Muse-Control>) | Media | ImJustHenry | Source code |
| [Raven Pet](<https://github.com/ofranken/RavenPrismTamagotchi>) | Companions | ofranken | Source code |
| [Raven Reach](<https://github.com/ImJustHenry/Raven-Reach>) | Accessibility | ImJustHenry | Source code |
| [Simple AI App](<https://github.com/RavenResonance/raven-starter-project/tree/main/examples/simple_ai_app>) | Official examples | Raven Resonance | Official example |
| [Snake](<https://github.com/amirmohideen/raven-ar-glass-experiences-mit/tree/main/snake_game>) | Games | Amir Mohideen | Source code |
| [Webtoon XR](<https://github.com/shreyaadani/WebtoonXR>) | Media | Shreyaa Dani | Source code |
<!-- END GENERATED APPS -->

### Other ways to browse

- **Searchable website:** [docs/index.html](docs/index.html). Enable GitHub Pages from the `docs/` directory **only after maintainer review**.
- **Machine-readable catalog:** [JSON](data/apps.json) · [CSV](data/apps.csv).
- **Unverified discovery leads:** [docs/UNVERIFIED_LEADS.md](docs/UNVERIFIED_LEADS.md).
- **Google Sheets mirror:** [Raven Prism Community App Directory](https://docs.google.com/spreadsheets/d/1zpmI-z8rMLl50vsgDA0O8s4FfXIWPjRvKly5hzH-t14/edit) — same approved entries, A–Z, with short clickable links. The Sheet is generated from the approved GitHub catalog by the [sync workflow](docs/SHEETS_SYNC.md); a fresh repository needs its own Actions credential.

## Contribute

Know of an application that is missing? [Suggest an app](.github/ISSUE_TEMPLATE/suggest-app.yml) or open a pull request updating `data/apps.json`. See [CONTRIBUTING.md](CONTRIBUTING.md) and the [data schema](docs/SCHEMA.md).

## What the availability labels mean

- **Official example:** a public sample from Raven Resonance's starter project.
- **Source code:** a public source repository; it does **not** imply the application can be installed or runs on physical hardware.
- **Downloadable release:** a public downloadable release exists; it has not been independently certified here.

We do not assign performance, safety, compatibility or on-device verification ratings without transparent public evidence and a well-defined scope.

## Intellectual property and editorial independence

This repository hosts original catalog descriptions and links, not copies of third-party projects. The Raven Framework has its own separate proprietary license. Application code, game assets, comics, audio, videos, models and trademarks remain under their respective owners' terms. Read the [publication policy](docs/PUBLICATION_POLICY.md).

Before making this repository public, complete the [publication checklist](docs/PUBLIC_RELEASE_CHECKLIST.md), including GitHub branch protections, anonymous access verification and one successful Google Sheets synchronization.

## Security and community policy

See [SECURITY.md](SECURITY.md), [community conduct](CODE_OF_CONDUCT.md),
[CONTRIBUTING.md](CONTRIBUTING.md) and [NOTICE.md](NOTICE.md) for the
security reporting process, submission rules and external licenses.

## Publishing and governance

The directory is maintained from the reviewed GitHub catalog. Public launch
requires a protected `main` branch, a successful CI run, the Google Sheets
publisher's repository secret and an enabled GitHub Pages site. Follow the
[public-release checklist](docs/PUBLIC_RELEASE_CHECKLIST.md) and the
[importable main ruleset](docs/release/main-ruleset.json).

## Maintainer workflow

```bash
python scripts/build_site.py
python scripts/validate_catalog.py
```

Keep `docs/apps.json`, `data/apps.csv` and the generated README table in sync with `data/apps.json`.

**Independent community project. No affiliation with Raven Resonance.**
