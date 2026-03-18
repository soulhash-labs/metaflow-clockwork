# Run-Spec Contract

## Scope

Phase 6 defines the local JSON run-spec contract for MetaFlow Clockwork.

The contract is local-first:

- no live QRBT or gateway calls
- no embedded executable code
- function bindings limited to the engine's registered function catalog

## File Format

Run specs are JSON objects.

Top-level fields:

- `version`
  - optional
  - current supported value: `1`
- `run_id`
  - optional
  - defaults to `metaflow_spec_<file_stem>`
- `request_id`
  - optional
  - defaults to `<run_id>-request`
- `tick_limit`
  - optional
  - defaults to `1`
- `max_recursive_depth`
  - optional
  - defaults to `10`
- `root_tags`
  - required
  - non-empty array

Root tag fields:

- `tag_type`
  - required
  - one of: `cog`, `gear`, `spring`, `pendulum`, `escapement`, `mainspring`, `complication`
- `tag_id`
  - optional
- `data`
  - optional object
- `functions`
  - optional string array
  - names must exist in the engine function registry
- `children`
  - optional array of nested tags
- `tick_rate`
  - optional positive number
  - defaults to `1.0`
- `energy`
  - optional positive number
  - defaults to `100.0`
- `max_recursive_depth`
  - optional non-negative integer
  - defaults to the parent or top-level depth limit

## Known Function Bindings

Current registered function names:

- `soul_match`
- `data_transform`
- `spawn_harmonics`

Unknown function names are rejected during validation.

## Example

```json
{
  "version": 1,
  "tick_limit": 3,
  "root_tags": [
    {
      "tag_type": "gear",
      "data": {
        "frequency": 528
      },
      "functions": ["spawn_harmonics"]
    }
  ]
}
```

## Validation Entry Point

```bash
python3 -m metaflow_clockwork spec-validate ./spec.json
```

The command prints the normalized contract with defaults applied and confirms that registered function bindings can be instantiated into `MetaTag` trees.
