# Practice labels

This folder is reserved for complete, human-reviewed practice labels for designated participant scoring inputs. A practice pack must use the existing `civ.label-pack/v1alpha1` contract and match the exact source hash in the detected run's manifest. The current scorer has no partial-coverage field, so review and include every relevant event for that exact source or chunk, including signoff for missed-event review, before treating precision, recall, or F1 as complete-reference results.

## Kashiwa warm-up

The first intended practice target is the accepted Kashiwa warm-up product. Use a separately supplied dataset only where its use is authorized, and keep the dataset external and read-only. This repository does not include the source recording or its camera companion.

When a reviewed pack is available, score a detected run with the existing consumer:

```sh
uv run civ score WORKING_DIR --labels practice-labels/kashiwa-warmup/KASHIWA_WARM_UP_PRACTICE_PACK.json
```

`WORKING_DIR` stands for the local detected-run directory. `KASHIWA_WARM_UP_PRACTICE_PACK.json` is an intentionally absent placeholder; no source-bound, human-reviewed pack has been verified or supplied here yet. The command will work only after the exact source and qualifying reviewed pack are available.

Practice labels are for participant self-evaluation. Held-out evaluation truth, sealed organizer packs, review audits, private provenance, source MCAPs, and camera companions remain outside this folder and organizer-only materials remain private. A valid schema or matching hash alone does not establish human review, complete coverage, or permission to publish.

## Future onboarding check

An optional check for a separately supplied chunk folder, matching EventSpec, and reviewed practice pack is recorded in [issue #100](https://github.com/Forerunner2012/civ2026-data-hackathon/issues/100). It is a future idea and is not implemented here.
