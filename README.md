<!-- rumdl-disable MD033 MD041 -->
<!-- The responsive brand banner intentionally precedes the heading. -->
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="banner/readme-banner-dark.svg">
    <img alt="Xberg" width="420" src="banner/readme-banner-light.svg">
  </picture>
</p>

# Xberg brand assets

Canonical brand assets for [Xberg](https://xberg.io) and all `xberg-io` projects. Single source of
truth — reference these across READMEs, docs sites, and social channels.

## CDN usage (READMEs, anywhere needing an absolute URL)

Per-package READMEs publish to npm/PyPI/crates, which do not resolve relative repo paths — use the
jsdelivr CDN. Consumers pin the floating major tag `@v1`, never a full version such as `@v1.0.0`:

```text
https://cdn.jsdelivr.net/gh/xberg-io/assets@v1/<path>
```

Top-of-README banner (auto dark/light):

```html
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)"
            srcset="https://cdn.jsdelivr.net/gh/xberg-io/assets@v1/banner/readme-banner-dark.svg">
    <img alt="Xberg" width="420"
         src="https://cdn.jsdelivr.net/gh/xberg-io/assets@v1/banner/readme-banner-light.svg">
  </picture>
</p>
```

## Layout

- `banner/` — README hero banner, light + dark (navbar wordmark, 900×285).
- `logo/` — `wordmark-*` and `symbol-*` (rotated junction), each `light` / `dark` / `mono-black` / `mono-white`.
- `favicon/` — full suite (`favicon.ico`, 16–512 PNG, apple-touch-icon, android-chrome, `site.webmanifest`).
- `social/` — `open-graph-card.png` (1200×630), `github-avatar-512.png`, `x-twitter-header.png`, `linkedin-banner.png`.
- `docs/` — `navbar-logo-{light,dark}.svg`, `footer-logo-{light,dark}.svg`, `docs-logo.svg`, `app-icon.svg`, `hero-logo.svg`, `hero-logo-light.svg`, `loading-mark.svg`.
- `color_tokens.{css,json}`, `logo_usage_rules.md` — palette + usage guidance.

## Releasing

A commit on `main` reaches no consumer until `v1` points at it. To release, tag the new version on
`main`, then move `v1` to the same commit (not the tag object) with a lease:

```sh
git tag -a vX.Y.Z -m "vX.Y.Z" && git push origin vX.Y.Z
prev=$(git ls-remote origin refs/tags/v1 | cut -f1)
git tag -f -a v1 -m "v1 -> vX.Y.Z" 'vX.Y.Z^{}'
git push origin v1 --force-with-lease=refs/tags/v1:"$prev"
```

jsdelivr caches `@v1`; purge each changed file at
`https://purge.jsdelivr.net/gh/xberg-io/assets@v1/<path>`. A breaking change (a renamed or removed
path) gets a new major tag (`v2`) and consumer pin updates instead. Older tags stay served for cache stability.

`scripts/check_brand_assets.py` runs in CI: it rejects SVGs with scripts or `on*` event attributes and
web-manifest icons that do not exist, and warns about brand files that differ from `v1`.

## License

MIT © Kreuzberg, Inc. See [LICENSE](LICENSE).
