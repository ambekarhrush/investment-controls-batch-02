# Investment mandate monitoring

A useful mandate monitor manages breach state instead of sending the same alert on every run. This module replays dated portfolio snapshots through configurable rules and records new, acknowledged and resolved events.

## Demonstrated result

The replay generates **2 new**, **2 acknowledged**, and **2 resolved** breaches. Its final snapshot arrives 30 hours late, so the engine emits one critical stale-data event and suppresses all exposure checks for that snapshot.

```bash
uv run investment-controls mandates
```

Inspect the [event history](outputs/demo/event_history.csv), [current queue](outputs/demo/current_queue.csv), and [webhook-shaped payload](outputs/demo/webhook_payload.json). A production service would store user acknowledgements rather than applying the deterministic demo transition on the second observation.
