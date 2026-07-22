# CLI Reference

Set the entrypoint once for a session:

```bash
PIO="<skill-dir>/scripts/pio.py"
```

Inspect and initialize:

```bash
python3 "$PIO" inspect --project .
python3 "$PIO" init --project . --name "Example" --objective "Ship the approved product"
```

Persist loop progress:

```bash
python3 "$PIO" transition clarify --project .
python3 "$PIO" log --project . --type decision --actor main --message "Use SQLite"
python3 "$PIO" compact --project .
python3 "$PIO" status --project .
```

Create and guard a role:

```bash
python3 "$PIO" add-role implementation --project .
python3 "$PIO" set-policy implementation --project . --allow 'src/**' --allow 'tests/**' --forbid 'src/secrets/**'
python3 "$PIO" baseline implementation --project .
# Dispatch or execute bounded work here.
python3 "$PIO" audit implementation --project .
```

Validate gates:

```bash
python3 "$PIO" validate --project . --stage structure
python3 "$PIO" validate --project . --stage ready
python3 "$PIO" validate --project . --stage complete
```

`validate` and `audit` return exit code `1` when evidence is incomplete or a boundary is violated. Contract errors return exit code `2`.
