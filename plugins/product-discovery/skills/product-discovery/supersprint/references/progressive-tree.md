# Progressive tree contract

The tree is the visible working memory of the cycle. Update it during the conversation and show it after material work, not only at completion. Preserve the same artifact path and browser tab where possible.

## What appears when

| Work completed | Visible update |
|---|---|
| Initial problem/direction only | Show the working question in the page context; do not invent a finished goal |
| Goal proposed or adopted | Add the goal with proposed/provisional/accepted status |
| Signals analyzed | Add evidenced signal summaries in the supporting area below the main axis |
| Opportunity candidates written | Add candidates with evidence links; none is selected merely because shown |
| Focus selected | Emphasize the selected opportunity and path, retaining alternatives |
| Ideas developed/selected | Add actual ideas and distinguish proposals from selections |
| Tests designed | Connect ideas directly to tests, with hypothesis, method/action and expected measurement inside the test |
| Real observations supplied | Add observed results with their provenance and review status |
| Decision reached | Add the actual decision and next action; preserve remaining uncertainty |

A rerender is not a new decision. Do not ask permission just to refresh a reversible view. Show the change before moving into a new stage so the human can follow the developing structure. Preserve previously authorized choices; do not treat an example of formatting as a selected branch.

## State and graph

The router writes the project's state, not the renderer. For new cycles use `assets/state-template.json`: store localized actual node/edge records in `nodes` and `edges`. Existing cycles may retain a separate graph at `state.tree.projection_path`; the renderer reads it without migrating or rewriting the state.

Each node has:

- Stable `id` and `type`: `goal`, `opportunity`, `idea`, `experiment`, `signal`, `result`, or `decision`.
- `title` (or existing `label`), `summary`, `status`, optional localized `status_label`.
- `preview_blocks`: a short list of localized `{label, body}` objects. Use a few sentences for context, not the complete source document.
- `artifact_path` or `source_path`: a cycle-relative source document path, or a safe HTTP(S) source URL.
- Optional `selected` and `recommended` booleans; for existing cycles selection IDs in state take precedence when present.
- An experiment may instead have `card: {title, hypothesis, experiment, observable}`. Its preview uses these three concise fields. Keep full explanations in its source plan.

Edges have `source`, `target` node IDs and a relation `type`; evidence/reference relations must remain distinguishable from the main structural links. Renderer validation rejects dangling edges and duplicate IDs. Do not include assumption nodes: the hypothesis belongs inside the test. Keep history/internal assumption IDs in existing state if needed.

Populate all labels, summaries, previews and statuses in the user's language. Optional `tree_ui` in state or graph overrides renderer interface labels for languages beyond the bundled English/Polish defaults. Provide full translations when using another language.

## Export and show

After saving a material change, increment `state.tree.revision`, set its current paths and use:

```sh
python3 <skill-directory>/scripts/render_tree.py <cycle>/state.json --output <cycle>/tree/tree.html --snapshot
```

The script validates and generates HTML plus sibling `tree.mmd`. With `--snapshot`, it writes `snapshots/rNNNN/` containing state, normalized graph, Mermaid and hash manifest. Existing different snapshots are never replaced; an identical retry is safe. Raw source files are not duplicated in every snapshot. If a view export fails, retain the state, name the stale view and retry without replaying decisions.

Open/refresh the HTML through the host's built-in visible browser, reusing the existing tab when supported. Report what changed (for example, new opportunities or a selected idea), current stage and next step. A saved file/editor open is not proof of successful preview. Respect browser policy; if blocked, give the local link plus an inline Mermaid or concise tree update. Do not use an alternate route to evade the restriction.

The main axis starts with the goal. Signals sit below it, attached as evidence. Keep a strong frame on the selected path and a distinct recommended-test style. Clicking a node only inspects it. Export PDF when requested using an appropriate PDF workflow; do not label an HTML print stylesheet as a verified PDF export.

## Boundaries

Do not prefill later stages or simulate user/customer results. A source quote supports a rationale, not proof that a proposed solution works. Preserve provisional goals, pending synthesis reviews, unstarted experiments and missing results visibly. Board synchronization remains optional and capability-dependent.
