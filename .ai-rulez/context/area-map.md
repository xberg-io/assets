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

Static brand files, no build. Consumers load them from `cdn.jsdelivr.net/gh/xberg-io/assets@<tag>/<path>`: org READMEs and docs sites pin `@v1`, docs-theme pins `@v1.0.0`.

- Every served path is a public interface: never rename, move or delete one; add a new file instead.
- A commit on `main` reaches no consumer until a tag points at it. Moving `v1` changes every consumer at once; a breaking change gets a new tag (`v2`) and consumer pin updates.
- `logo_usage_rules.md` and `color_tokens.{css,json}` are the brand rules and palette.
