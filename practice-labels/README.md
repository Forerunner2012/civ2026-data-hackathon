# Practice labels

This folder is reserved for complete, human-reviewed practice labels for designated participant scoring inputs. A practice pack must use the existing `civ.label-pack/v1alpha1` contract and match the exact source hash in the detected run's manifest. The current scorer has no partial-coverage field, so review and include every relevant event for that exact source or chunk, including signoff for missed-event review, before treating precision, recall, or F1 as complete-reference results.

## Kashiwa warm-up

The accepted Kashiwa warm-up product is the first designated practice target. Use a separately supplied dataset only where its use is authorized, and keep the dataset external and read-only. This repository does not include the source recording or its camera companion.

Complete local practice reviews and consumer qualification are recorded in [issue #117](https://github.com/Forerunner2012/civ2026-data-hackathon/issues/117). This does not establish participant availability or permission to distribute the packs. No real label JSON is tracked here.

After [installing the participant CLI](../docs/setup.md), score a detected run only when your session supplies its matching complete pack:

```sh
civ score WORKING_DIR --labels SUPPLIED_PRACTICE_PACK.json
```

`WORKING_DIR` is your detected-run directory; replace `SUPPLIED_PRACTICE_PACK.json` with the real local pack path announced for that exact source and event definition. Do not infer a pack filename or distribution schedule from this reserved folder. Keep supplied labels read-only.

Practice labels are for participant self-evaluation. Held-out evaluation truth, sealed organizer packs, review audits, private provenance, source MCAPs, and camera companions remain outside this folder and organizer-only materials remain private. A valid schema or matching hash alone does not establish human review, complete coverage, or permission to publish.

## Future onboarding check

An optional check for a separately supplied chunk folder, matching EventSpec, and reviewed practice pack is recorded in [issue #100](https://github.com/Forerunner2012/civ2026-data-hackathon/issues/100). It is a future idea and is not implemented here.
