# Blueprint manifest

`src/specle/blueprints/manifest` is an append-only record of release provenance. It is a blueprint document only: Specle never installs it into `.agents/` and does not use it as runtime or target state.

## Entry format

Each line records one managed resource:

```text
<version>:skill/<skill>/<path>:<sha256>
<version>:policies/<document>:<sha256>
```

The line identity is its version and path. An existing line is never updated or duplicated. A different checksum for the same identity is an error.

## Release preparation

After changing the package version, generate release entries with:

```text
uv run specle manifest src/specle/blueprints/manifest
```

The command reads `specle.__version__`, which resolves the installed distribution version through `importlib.metadata`, scans the packaged managed inventory, and appends only entries absent from the manifest. Commit the version update and generated manifest together before releasing.

## Provenance queries

Filter entries by version to recover that release's complete managed inventory. Comparing the same path across versions shows checksum changes. Its first occurrence identifies when a resource appeared; its absence after an earlier occurrence identifies when it retired.
