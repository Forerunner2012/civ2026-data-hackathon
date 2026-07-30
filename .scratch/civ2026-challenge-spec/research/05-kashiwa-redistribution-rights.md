# URT-Kashiwa redistribution rights

Research output for [ticket 05](../issues/05-kashiwa-redistribution-rights.md). Researched 2026-07-30.
Primary sources only: the dataset's own `LICENSE`, its GitHub repository, the publishing lab's
site, the Creative Commons legal code, and the official APPI translation.

## Summary

**The copyright question is answered and the answer is yes.** URT-Kashiwa is published by
Tsukada Laboratory, The University of Tokyo, under **Creative Commons Attribution 4.0
International (CC BY 4.0)**. That permits redistributing a subset to attendees, offline, for
them to keep permanently, including commercially, with attribution as the only condition. There
is no event-only limitation, no share-alike, no publication embargo, and no research-only
restriction anywhere in the public record.

**The unresolved risk is personal data, not copyright.** CC BY 4.0 expressly does *not* license
privacy or personality rights, and T-Lab has published **no statement at all** about consent,
anonymisation, blurring, or ethics review. The bags contain a front RGB camera topic and GNSS
fixes. Nobody has said whether faces or plates appear or whether anything was blurred. That is
the item a human must close, not an AI.

Two corrections to the ticket's framing, both verified:

- **CIV 2026 is in Miyazaki, Japan** (31 Aug – 4 Sep 2026), not France. Attendees are
  international. GDPR still bites, but via Heex Technologies' establishment in France rather
  than via the venue.
- **The dataset owner is the event's own local host.** Assoc. Prof. Manabu Tsukada is on the
  CIV 2026 organizing committee and is the dataset's corresponding author. Every unknown below
  is one email away, and that email costs nothing.

Blocking status: **unblocked on licence, open on personal data.** Ticket 01's assumption holds.

## Dataset identification

**Confidence: high.** Identified as:

> **URT-Kashiwa Dataset** (Unprotected Right Turn, Kashiwa Campus)
> `https://github.com/tlab-wide/URT-Kashiwa` — repo created 2025-09-24, HEAD
> `e2793edf8ea451cbc98f8a153bbfede8004c199e` (2025-09-24T07:27:08Z), sole branch `main`.

Evidence chain, all primary:

- The GitHub org `tlab-wide` resolves to **"Tsukada Laboratory"** with homepage
  `http://tlab.hongo.wide.ad.jp/` (GitHub org API). The lab's own site carries a matching
  portfolio entry and a release announcement.
- README: collected at the **Kashiwa Campus of the University of Tokyo** on the **Pixkit 3.0**
  platform, **16 routes**, ROS 2 Humble rosbags, Autoware-flavoured topic names
  (`/vehicle/status/...`, `tier4_*_msgs`, `autoware_auto_*_msgs`).
- Distribution is a public Google Drive folder titled "URT Kashiwa Dataset" containing
  **16 subfolders** `final_route_{2..18}`, each holding a single `.mcap` file
  (e.g. `final_route_11_0.mcap`), last modified **27 Aug 2025**.
- The README's RViz step reads `ros2 run rviz2 rviz2 -d civ.rviz` — a config named for CIV.

The team's reading of the acronym is confirmed by the publisher, including the handedness point:

> "The **URT-Kashiwa Dataset** (Unprotected Right Turn, Kashiwa Campus) is a collection of
> driving scenario recordings focused on **unprotected right turns**, a challenging maneuver
> for autonomous vehicles (equivalent to unprotected left turns in Europe)."

**Candidates ruled out.** Not an Autoware Foundation or TIER IV dataset — the Autoware/`tier4_*`
message packages appear only as *build dependencies* for replay, and neither organisation
publishes or hosts it. Not a Kashiwa-no-ha smart-city / CooL4 field-operational-test release
either: CooL4 (RoAD to the L4 Theme 4, ended March 2026) ran a Level-4 bus on **open public
roads** at Kashiwa-no-ha, whereas URT-Kashiwa was recorded on the **university campus** with
staged actors. Different setting, different exposure profile — do not import CooL4's public-road
assumptions into this dataset.

**Timeline worth noting.** The MCAP files were last modified 27 Aug 2025; CIV 2025 ran
1–5 Sep 2025 in Blonay; the public GitHub release landed 24 Sep 2025. So the 2025 hackathon used
this data *before* it was public — the ticket is right that prior reuse proves nothing. It no
longer matters: a public CC BY 4.0 grant now exists and stands on its own.

## 1. Licence name, version, authoritative text

**Creative Commons Attribution 4.0 International (CC BY 4.0).** Authoritative text:
`https://creativecommons.org/licenses/by/4.0/legalcode.en` (plain-text mirror at
`https://creativecommons.org/licenses/by/4.0/legalcode.txt`).

`LICENSE` at the repo root, in full:

> URT Kashiwa Dataset collected in Kashiwa Campus. © 2025 Tsukada Laboratory, The University of Tokyo.
> Contributors: Ehsan Javanmardi, Dongyang Li, Manabu Tsukada
>
> This dataset is licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0) License.
>
> You are free to:
> - Share — copy and redistribute the material in any medium or format
> - Adapt — remix, transform, and build upon the material for any purpose, even commercially.
>
> Under the following terms:
> - Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
>   You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
>
> No additional restrictions — You may not apply legal terms or technological measures that legally restrict others
> from doing anything the license permits.
>
> Full license text: https://creativecommons.org/licenses/by/4.0/

Corroborated in two more places: `README.md` ("This dataset is licensed under the [Creative
Commons Attribution 4.0 International (CC BY 4.0)]"), and machine-readably in `CITATION.cff`
(`license: CC-BY-4.0`). The lab's release post says the same.

**Two cosmetic snags, neither changes the answer.**

1. The `LICENSE` file reproduces the CC **deed summary**, not the legal code. GitHub's licence
   detector therefore reports `spdx_id: NOASSERTION` / "Other" for the repo. The licence is
   named and linked unambiguously, so this is a scanner artifact — but expect any automated
   compliance check in the kit's CI to flag it, and say so in the manifest.
2. `CITATION.cff` still contains the template placeholder
   `url: "https://github.com/<your-org-or-username>/<your-repo>"`. Evidence the release was
   published from a boilerplate. Not a defect in the grant; it is a reason to get the licence
   confirmed in one line of email rather than relying on the paperwork being carefully reviewed.

## 2. Redistribution, event-only vs perpetual, offline copies

**Redistribution to attendees: permitted. Subsets: permitted. Perpetual: yes. Offline: yes.**

Subset redistribution — §2(a)(1):

> Subject to the terms and conditions of this Public License, the Licensor hereby grants You a
> worldwide, royalty-free, non-sublicensable, non-exclusive, irrevocable license to exercise the
> Licensed Rights in the Licensed Material to:
>
>   a. reproduce and Share the Licensed Material, in whole or in part; and
>   b. produce, reproduce, and Share Adapted Material.

"in whole **or in part**" settles the subset question. "Share" is defined in §1(i) as providing
material to the public "by any means or process", which covers USB sticks, SSDs and container
images as readily as a download link.

Attendees are direct licensees, not sub-licensees. The grant is "non-sublicensable", and §2(a)(5):

> a. Offer from the Licensor -- Licensed Material. Every recipient of the Licensed Material
>    automatically receives an offer from the Licensor to exercise the Licensed Rights under the
>    terms and conditions of this Public License.
>
> b. No downstream restrictions. You may not offer or impose any additional or different terms
>    or conditions on, or apply any Effective Technological Measures to, the Licensed Material if
>    doing so restricts exercise of the Licensed Rights by any recipient of the Licensed Material.

**Operative consequence for the kit — flagging because it inverts the natural instinct:**
§2(a)(5)(b) means the organizers **may not** impose an event-only or delete-after-the-event
condition on the Kashiwa material. A hackathon rules document that says "delete the dataset when
the session ends" would itself breach the licence the organizers are relying on. Attendees keep
their copies as of right, from UTokyo directly, not by the organizers' grace.

Perpetuity — §2(a)(1) says "irrevocable", and §6(a):

> This Public License applies for the term of the Copyright and Similar Rights licensed here.
> However, if You fail to comply with this Public License, then Your rights under this Public
> License terminate automatically.

Breach terminates automatically but reinstates on cure within 30 days (§6(b)(1)). The only
realistic breach mode here is dropping the attribution.

**Mirror the data now.** §6(c):

> For the avoidance of doubt, the Licensor may also offer the Licensed Material under separate
> terms or conditions or stop distributing the Licensed Material at any time; however, doing so
> will not terminate this Public License.

T-Lab can pull the Google Drive folder at any moment without warning and without affecting
rights already granted. Rights survive; *access* does not. Take a pinned local copy of all 16
MCAPs, with checksums and the retrieval date, before any further planning depends on them.

## 3. Attribution, share-alike, publication constraints

**Attribution is the only condition. There is no share-alike and no publication constraint.**

§3(a)(1), verbatim:

> If You Share the Licensed Material (including in modified form), You must:
>
>   a. retain the following if it is supplied by the Licensor with the Licensed Material:
>        i. identification of the creator(s) of the Licensed Material and any others designated
>           to receive attribution, in any reasonable manner requested by the Licensor
>           (including by pseudonym if designated);
>       ii. a copyright notice;
>      iii. a notice that refers to this Public License;
>       iv. a notice that refers to the disclaimer of warranties;
>        v. a URI or hyperlink to the Licensed Material to the extent reasonably practicable;
>   b. indicate if You modified the Licensed Material and retain an indication of any previous
>      modifications; and
>   c. indicate the Licensed Material is licensed under this Public License, and include the text
>      of, or the URI or hyperlink to, this Public License.

§3(a)(2) allows satisfying all of this "in any reasonable manner based on the medium", e.g. one
`NOTICE` file shipped in the kit and rendered in the CLI's `--about`.

**No share-alike.** CC BY has no copyleft. The only constraint on downstream licensing is
§3(a)(4):

> If You Share Adapted Material You produce, the Adapter's License You apply must not prevent
> recipients of the Adapted Material from complying with this Public License.

So **attendee submissions may be MIT, Apache-2.0, or kept private**; only the included Kashiwa
material stays under CC BY. A published scoring kit is likewise unconstrained in its own
licensing — it just has to carry the attribution for any Kashiwa material or derivative bundled
with it, and must not use DRM or terms that block recipients from exercising CC BY rights.

**No endorsement** — §2(a)(6):

> Nothing in this Public License constitutes or may be construed as permission to assert or imply
> that You are, or that Your use of the Licensed Material is, connected with, or sponsored,
> endorsed, or granted official status by, the Licensor or others designated to receive
> attribution as provided in Section 3(a)(1)(A)(i).

Practical read: credit UTokyo as the *source of the data*; do not word the kit or the site so the
challenge looks like an official University of Tokyo competition. (Tsukada being local host makes
a co-branding claim easy to secure explicitly if wanted — but ask, don't assume.)

**No publication constraint.** Verified absence across `LICENSE`, `README.md`, `CITATION.cff`,
the lab portfolio page, and the release post: no embargo, no pre-publication review right, no
notify-us clause, no research-only limitation. Note one wording tension — the release post says
the dataset "is available to the research community", which reads restrictively; the licence
actually granted is CC BY 4.0, which is not research-limited and explicitly permits commercial
use. The licence controls. That said, a hackathon "supported by Heex Technologies" is a
commercially-adjacent use of a dataset whose announcement gestures at research — cheap to
neutralise by mentioning the event explicitly in the confirmation email.

Ready-to-use attribution string, assembled from `LICENSE` and `CITATION.cff`:

> URT-Kashiwa Dataset (Unprotected Right Turn, Kashiwa Campus), v1.0.0 (2025-09-24).
> © 2025 Tsukada Laboratory (T-Lab), The University of Tokyo.
> Contributors: Ehsan Javanmardi, Dongyang Li, Manabu Tsukada.
> Source: https://github.com/tlab-wide/URT-Kashiwa
> Licensed under CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/
> Provided "as is", without warranties; see the licence for the full disclaimer.
> Modified for CIV 2026: <state the modifications — subsetting, MCAP re-chunking, blurring, …>

## 4. Do derived artifacts inherit the terms?

**Yes for anything containing the licensed material; format conversion alone is not adaptation;
organizer-authored labels are the genuinely grey case.**

- **Extracted MCAP clips, decimated bags, re-chunked files.** These reproduce the licensed
  material. §2(a)(1)(a) covers them ("in whole or in part") and §3(a) attribution applies on
  redistribution. Pure format/technical work is explicitly *not* adaptation — §2(a)(4):

  > The Licensor authorizes You to exercise the Licensed Rights in all media and formats whether
  > now known or hereafter created, and to make technical modifications necessary to do so. […]
  > For purposes of this Public License, simply making modifications authorized by this Section
  > 2(a)(4) never produces Adapted Material.

  So transcoding rosbag2→MCAP or splitting clips does not create Adapted Material — but you still
  attribute when you share the result.

- **Sampled tables / parquet extracted from the bags.** Same analysis, plus the database limb.
  This matters because Heex and part of the audience sit in the EU, where sui generis database
  rights exist. §4:

  > a. for the avoidance of doubt, Section 2(a)(1) grants You the right to extract, reuse,
  >    reproduce, and Share all or a substantial portion of the contents of the database;
  > […]
  > c. You must comply with the conditions in Section 3(a) if You Share all or a substantial
  >    portion of the contents of the database.

  Extraction into parquet is squarely permitted, with attribution.

- **Sealed ground-truth labels (ticket 03).** Judgement call, flagged as such. "Adapted Material"
  under §1(a) is material "derived from or based upon the Licensed Material and in which the
  Licensed Material is translated, altered, arranged, transformed, or otherwise modified **in a
  manner requiring permission**". A label file that is only `(bag_id, t_start, t_end, event_type)`
  arguably embeds no protected expression from the bags and would be organizer-owned outright; a
  label set that embeds extracted frames, point clouds or trajectories clearly does inherit.
  **This is my inference from the licence text, not something a primary source states.** Cheap
  way to stop caring: publish the label set under CC BY 4.0 anyway, and attribute the source
  dataset in it regardless of which side of the line it falls on. Costs nothing and removes a
  question the event should not be litigating during a three-hour session.

- **Attendee-authored detectors and notebooks.** Independent works, not derivatives of the data.
  Attendees license them however they like (§3(a)(4) only constrains Adapted Material they
  redistribute).

## 5. Personal data — the public record is silent

> ⚠️ **This is the one that needs a human. Verified silence, not verified safety.**

Nothing in any primary source addresses consent, anonymisation, blurring, ethics review, APPI or
GDPR. Confirmed by reading, in full: `LICENSE`, `README.md`, `CITATION.cff` (the repo's only
non-image files), the T-Lab portfolio page, the T-Lab release announcement, and the Drive folder
(16 route folders, one `.mcap` each, no README, no terms, no consent document). The linked demo
video on YouTube (uploaded by Ehsan Javanmardi, 2025-09-23) has an **empty description**. No
accompanying paper was found — arXiv author search returns nothing, and T-Lab's own site search
for "URT" / "right turn" returns only the two dataset posts. There is no methods section
anywhere that could carry an ethics statement.

**What the licence does about this: nothing, deliberately.** §2(b)(1):

> Moral rights, such as the right of integrity, are not licensed under this Public License, nor
> are publicity, privacy, and/or other similar personality rights; however, to the extent
> possible, the Licensor waives and/or agrees not to assert any such rights held by the Licensor
> to the limited extent necessary to allow You to exercise the Licensed Rights, but not otherwise.

A perfect CC BY grant therefore clears copyright and leaves data protection entirely untouched.
"It's CC BY, so we're fine" is not an available conclusion.

**What is documented (verified facts):**

- Recorded at the **Kashiwa Campus of the University of Tokyo** — a university campus, not open
  public roads.
- The release post describes "**controlled interactions**" with "**One pedestrian**", "**One
  opponent vehicle**", "**16 different routes**".
- The bags carry a front RGB camera: `/sensing/camera/traffic_light/image_raw` (plus
  `camera_info`), so faces and plates are technically capturable.
- The bags carry precise positioning: `/sensing/gnss/fix`, `/sensing/gnss/pose`,
  `/sensing/gnss/pose_with_covariance`, IMU, and Autoware localization poses.

**Inference, clearly labelled as such:** a staged pedestrian and a staged opponent vehicle on a
controlled campus most likely means lab members acting to script rather than unwitting members of
the public, and campus GNSS traces do not go near identifiable homes. That is a plausible read of
documented facts — **it is not a consent record and must not be treated as one.** Incidental
bystanders on a working university campus are entirely possible, and the staged pedestrian is
themself an identifiable individual whose face and movements are in the data.

**Legal frame, for the humans who will decide.** Under Japan's APPI (official English translation
at japaneselawtranslation.go.jp), personal information is information relating to a living
individual that identifies them, and Art. 27(1) requires prior consent before providing personal
data to a third party, with Art. 28 adding a distinct consent requirement for provision to a
third party in a foreign country. Under GDPR, images of identifiable individuals are personal
data, and **Heex Technologies is established in France**, so Art. 3(1) reaches its processing
regardless of the event being held in Miyazaki. Whether either regime is engaged depends entirely
on facts nobody has published. **This is a question for counsel and for T-Lab, not for this
document.**

**Cheapest decisive step, and it is available now:** the organizers hold the MCAPs. Decode a
sample of `/sensing/camera/traffic_light/image_raw` frames across several routes and *look*. That
converts the central unknown into an observation in an afternoon. Three outcomes:

- no identifiable faces or plates → note the finding, keep the camera topic, move on;
- identifiable people or plates present → either blur (permitted; blurring is an adaptation and
  must be flagged as a modification under §3(a)(1)(b)) or drop the camera topic from the
  distributed subset. Dropping it is cheap — the URT detector logic runs off velocity, steering,
  gear, GNSS/localization and objects, not RGB — though it costs the visual appeal that makes a
  three-hour hackathon land;
- ambiguous → ask T-Lab, and default to blurring.

Note that T-Lab has already published these frames publicly under CC BY 4.0 itself, which is a
materially different posture from a private transfer. It does not extinguish Heex's own
obligations if Heex further distributes the same material.

## 6. Does this cover newly collected ROS 2 / PX4 data?

**No. Verified: nothing in the public record extends the grant to future recordings.**

CC BY 4.0 §1(f) defines Licensed Material as "the artistic or literary work, database, or other
material **to which the Licensor applied this Public License**". The Licensor applied it to the
16 routes published on 2025-09-24. Future recordings are outside it until separately licensed.

Two relevant data points, both context rather than commitment:

- **T-Lab's pattern is consistent.** Their newer release, RealSim-CP (portfolio dated
  2026-06-15), splits licensing explicitly: MIT for code and tools, **CC BY 4.0 for the dataset**
  via a dedicated `DATA_LICENSE.md` with a required attribution string. Reasonable to *expect*
  the same treatment for new data; not a promise, and not something to plan a freeze around.
- **A same-programme collection event exists.** The JSAE Autonomous Driving AI Challenge 2026
  spin-off, supported by UTokyo's UTmobI including Tsukada Lab, runs a V2X hands-on at the
  **Kashiwa Campus ITS R&R Test Field, 7–9 Sep 2026**, whose programme explicitly includes
  "operation practice and **dataset collection**" with PIXKIT carts. Note the date: **after**
  CIV 2026 (31 Aug – 4 Sep). Any data from it lands too late for the freeze regardless of
  licensing. No licence is stated for it.

Separately, and cross-referencing [ticket 14](../issues/14-bespoke-collection-scope.md): the
**French-city bespoke bags are not UTokyo material at all**. They carry no relationship to CC BY
4.0 and are governed by whatever Heex agrees with its own rig, sites and any filmed third
parties. Those bags are collected on **open public roads in France**, which is a materially
worse personal-data posture than a controlled campus — uninvolved pedestrians, real plates, real
addresses, real GDPR. Do not let the clean CC BY answer for Kashiwa create a halo over data
collected under completely different conditions.

## What remains unknown, and who must confirm it

| # | Unknown | Who confirms | Urgency |
|---|---|---|---|
| 1 | Whether the pedestrian, opponent-vehicle driver and any bystanders consented to public release of their images | **Assoc. Prof. Manabu Tsukada / Ehsan Javanmardi, T-Lab** — `mtsukada@g.ecc.u-tokyo.ac.jp` | **High.** Gates camera-topic inclusion. |
| 2 | Whether any anonymisation or blurring was applied before release | **T-Lab** (and directly observable by inspecting frames) | **High.** Do the frame inspection this week. |
| 3 | Whether faces/plates are actually present in the distributed MCAPs | **Organizers, by inspection** — no external dependency | **High, and self-serve.** |
| 4 | Whether Heex is controller or processor for the redistributed subset, and what GDPR Art. 3(1) requires of it | **Heex counsel / DPO** | Medium. Waits on 3. |
| 5 | Written confirmation of CC BY 4.0 covering the camera imagery specifically, and comfort with an event supported by a commercial sponsor | **T-Lab** | Medium. Cheap insurance against the `NOASSERTION`/template-placeholder sloppiness and the "research community" wording. |
| 6 | Whether future ROS 2 / PX4 data from T-Lab will carry the same licence | **T-Lab** | Low for the freeze — ticket 01 already made Kashiwa the only dependency. |
| 7 | Licensing and personal-data posture of the French-city bespoke bags | **Heex, internally** | Per ticket 14's drop-dead date. |

Items 1, 2, 5 and 6 are a single email to the dataset's corresponding author, **who is also the
CIV 2026 local host**. Send it before the frame inspection so the two run in parallel.

**Do not** write a delete-after-the-event clause into the attendee terms for Kashiwa material —
§2(a)(5)(b) forbids it, and it would put the organizers in breach of the licence they are relying
on. If some component genuinely must not persist, that component cannot be the Kashiwa data
(the sealed label set, being organizer-authored, is a different matter and can carry whatever
terms the organizers choose).

## Sources consulted

Primary — the dataset and its publisher:

- https://github.com/tlab-wide/URT-Kashiwa
- https://raw.githubusercontent.com/tlab-wide/URT-Kashiwa/main/LICENSE (blob `a22d3689af1d7f003d18f88b3f2d6567cccacd78`)
- https://raw.githubusercontent.com/tlab-wide/URT-Kashiwa/main/README.md
- https://raw.githubusercontent.com/tlab-wide/URT-Kashiwa/main/CITATION.cff
- https://api.github.com/repos/tlab-wide/URT-Kashiwa (licence detection: `spdx_id: NOASSERTION`)
- https://api.github.com/orgs/tlab-wide (org name "Tsukada Laboratory", blog `tlab.hongo.wide.ad.jp`)
- https://drive.google.com/drive/folders/1HnDjHkm7w1klh856-SmEVJ6OELNnHj0L?usp=sharing (16 route folders, one `.mcap` each, modified 2025-08-27)
- https://tlab.hongo.wide.ad.jp/portfolio/urt-kashiwa-dataset-unprotected-right-turn-kashiwa-campus/
- https://tlab.hongo.wide.ad.jp/2025/09/29/urt-kashiwa-dataset-released-unprotected-right-turn-kashiwa-campus/
- https://www.youtube.com/watch?v=1Q1ENXNBhKM (demo video, Ehsan Javanmardi, 2025-09-23, empty description)

Primary — licence text:

- https://creativecommons.org/licenses/by/4.0/legalcode.en
- https://creativecommons.org/licenses/by/4.0/legalcode.txt
- https://creativecommons.org/licenses/by/4.0/

Primary — event and programme context:

- https://civ-summerschool.org/ (CIV 2026: Miyazaki, 31 Aug – 4 Sep 2026; hackathon Thu 3 Sep 09:30–12:30; organizing committee incl. Tsukada and Carré)
- https://tlab.hongo.wide.ad.jp/2026/05/22/announcement-cooperative-interactive-vehicles-civ-summer-school-2026/
- https://tlab.hongo.wide.ad.jp/2025/09/08/report-on-civ-summer-school-2025/
- https://tlab.hongo.wide.ad.jp/2026/06/05/ai-challenge-2026-spin-off-v2x-autonomous-driving-hands-on-at-kashiwa-campus/
- https://tlab.hongo.wide.ad.jp/2026/05/29/the-end-of-cool4-five-years-of-cooperative-level-4-autonomous-driving-at-kashiwa-no-ha/

Primary — comparative licensing practice by the same lab:

- https://github.com/tlab-wide/realsim-cp — `LICENSE` (MIT, code/tools) and `DATA_LICENSE.md` (CC BY 4.0, dataset)

Primary — data protection:

- https://www.japaneselawtranslation.go.jp/en/laws/view/4241/en (APPI, official English translation)
- https://www.ppc.go.jp/en/legal/ (Personal Information Protection Commission, Japan)

Negative results (searched, nothing found): arXiv author search for the dataset authors returns
no URT-Kashiwa paper; T-Lab site search for "URT" and "right turn" returns only the two dataset
posts; no consent, ethics, anonymisation, APPI or GDPR statement exists in any published artifact
of this dataset.
