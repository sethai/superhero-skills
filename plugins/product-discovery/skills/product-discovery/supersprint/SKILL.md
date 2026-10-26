---
name: supersprint
description: Run Supersprint from product context to an evidence-supported decision, routing specialists and showing a growing discovery tree. Use when starting, resuming or reviewing a Supersprint cycle.
metadata:
  ready_to_publish: "true"
---

# Supersprint

Lead the cycle: goal -> signals -> opportunities -> ideas -> experiments -> observed results -> decision. Keep the tree visible as the work develops, not only at the end.

Respond and produce all artifacts in the user's conversation language.

## Intake and resume

Read `references/intake-and-routing.md` first. Minimum input is product context and a problem, direction or decision to investigate; a short conversation brief is sufficient. An existing outcome, metrics, transcripts and completed research are optional inputs, not an admission checklist.

Resolve the product folder and cycle from the conversation or workspace. Ask only if ambiguity materially changes the destination or work. Read project instructions, brief, entry point, current state and active-stage artifacts before raw files. Reuse accepted choices. Resume the actual waiting point instead of replaying all stages.

For a new cycle use `assets/state-template.json` under `supersprint/<cycle>/`. Choose a meaningful cycle name from context; do not overwrite an existing cycle. Store input references, separate stage Markdown files, analyses and `tree/` here. Keep raw sources unchanged and executable code in the skill/code repository, not a knowledge vault.

The router owns the cycle state and material decision history. Specialists own their native analysis artifacts; import their findings with source paths and review status instead of requiring them to rewrite shared state. Existing state formats are supported: preserve fields and IDs, adding a tree projection if needed rather than migrating everything.

## Progress through the cycle

1. **Goal:** identify whose behavior should change, how it relates to a business priority and how it could be measured. Reuse a suitable brief outcome. If missing, help define it; when evidence is insufficient, keep an explicit working direction or research question. Unknown baseline, target or deadline stays unknown. A measurement window is not a delivery deadline.
2. **Signals:** distinguish available inputs, completed analysis and enough evidence for the next decision. Reuse current relevant analyses. Name gaps, contradictions, source versions and limits. Missing signal categories do not require filling every folder. Suggest the smallest research that can change the decision; allow consciously proceeding with stated uncertainty.
3. **Opportunities:** formulate user needs/problems in natural user language. Compare importance, plausible goal contribution and evidence. Recommend a focus; record the user's selection or existing delegation. Keep alternatives and rationale. A need is not a proposed feature.
4. **Ideas:** compare distinct approaches by fit, potential and constraints. Describe the concrete mechanism. Keep user-selected ideas; do not impose a fixed number or reopen an accepted gate without a material reason.
5. **Experiments:** use `experiment-design` on the selected ideas and relevant evidence. The assumption belongs inside the experiment's hypothesis, not a separate tree layer, stage or duplicated list. Explain hypothesis, concrete method/action and observable change. Preserve the portfolio; recommend a next test without selecting it for the user. Expected change is directional by default; the human judges sufficiency unless numerical criteria were supplied or requested.
6. **Results:** register actual observations, scope, execution and review status. A plan, role-play or synthetic case is not customer evidence. Read results in the context of what the method tests; clicks, use, payment and repeat purchase answer different questions.
7. **Decision:** record develop, revise, discard or research further, with supporting evidence, uncertainty, next action and owner. A cycle ends with a supported decision, not necessarily a build. Keep production implementation as a subsequent scoped task.

Ask one consequential question at a time when a choice is needed. Previously authorized work and delegated choices do not need repeated approval. Preserve specialist review gates where applicable; presenting proposals or opening a diagram does not accept them.

## Specialist routing

The plugin includes all six specialists listed below. Discover them by skill name in the host, including its plugin namespace when required, and read the relevant specialist before using it. Resolve bundled resources relative to each skill directory; no personal vault or development-repository path is required. Pass the agreed question, decision, segment, selected input paths, constraints, destination and return condition. Use only the route that addresses an actual gap:

| Gap | Specialist |
|---|---|
| Patterns and measurements in supplied data | `data-analysis` |
| Themes and evidenced needs in transcripts | `affinity-mapping` |
| New conversations need a screener and guide | `interview-plan` |
| Public accounts of customer experience | `customer-research` |
| Competitive, secondary or research evidence | `desk-research` |
| Concrete tests for selected ideas | `experiment-design` |

If a specialist is unavailable, report the missing capability and choose a feasible scoped fallback. Do not pretend it ran. Separate agents are optional only when available and authorized; routing normally means following the specialist within this conversation.

## Grow, save and show the tree

Read `references/progressive-tree.md` before the first tree update. After a meaningful new proposal, analysis finding, selection, test plan or supplied result, and at every stage transition:

1. Save the stage narrative and state, maintaining stable IDs, source references, review and selection status. Record what materially changed and why.
2. Project only existing work into the tree. Save/refresh the same `tree/tree.html` and `tree/tree.mmd`; snapshot significant structural changes with the state. Do not prefill future branches.
3. Show the updated tree to the user now, using the host's visible built-in browser and reusing its tab when supported. Say briefly what was added or changed and the current next step. Do not wait for the full cycle to finish.

Run the bundled renderer after updating the state/projection:

```sh
python3 <skill-directory>/scripts/render_tree.py <cycle>/state.json --output <cycle>/tree/tree.html --snapshot
```

The renderer accepts both a new state's `nodes`/`edges` and an existing `tree.projection_path` graph. Set a new `tree.revision` for material changes before requesting a snapshot. A cosmetic change can rerender without `--snapshot`. See the reference for node fields, localization and links.

Main axis: goal -> opportunities -> ideas -> experiments -> real results -> decision. Put signals in a supporting area below the axis with evidence links, not before the goal as a process step. Selected paths stay clearly framed; recommendations and temporary inspection have different treatments. Each layer gets a short node summary, a few sentences in the click preview and a prominent full-source link. Experiment previews retain hypothesis, practical method and measurement, not the full protocol.

Use the accepted SF neutral style: `references/html-style.md` and the packaged `assets/html-style.css`. Different artifacts may use different layouts while keeping this visual family. The renderer is offline and self-contained.

If browser policy blocks access, save the artifacts, provide the file link and a concise change summary or inline Mermaid fallback. State that automatic preview was not confirmed; do not bypass the block through another browser, protocol or local server. Text-only user preferences take precedence.

Miro/FigJam is optional. Check an available integration and access, remember the user's target and update only the managed region where supported. Never let external-board availability block the local state/tree. Do not overwrite manual board changes without reconciliation.

## Source changes and handoff

On resume, check state and view revisions plus relevant source changes. Preserve previous results and choices; mark affected conclusions for review rather than silently treating them as current. Do not count the same interview, person or event twice because several reports cite it.

End a working turn with the updated tree link, the meaningful change, the current stage and one concrete next action or unresolved choice. Keep dates, execution status and evidence limits honest. Tree updates happen while the agent works in the conversation; do not claim independent background automation.
