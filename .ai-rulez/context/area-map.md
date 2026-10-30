---
type: Concept
title: Area Map
x-ai-rulez:
  kind: context
  id: area-map
  metadata:
    priority: high
---

## Area Map

Static brand files, no build. Consumers load them from `cdn.jsdelivr.net/gh/xberg-io/assets@<tag>/<path>`: every consumer, docs-theme included, pins the floating major `@v1`.

- Every served path is a public interface: never rename, move or delete one; add a new file instead.
- A commit on `main` reaches no consumer until a tag points at it. A release tags `vX.Y.Z` and moves `v1` to it, which changes every consumer at once; a breaking change gets a new tag (`v2`) and consumer pin updates.
- `logo_usage_rules.md` and `color_tokens.{css,json}` are the brand rules and palette.
