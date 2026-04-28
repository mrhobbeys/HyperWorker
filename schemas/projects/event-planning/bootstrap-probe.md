# Bootstrap Probe — event-planning

> Read by the executor at `hw bootstrap` time. The probe enumerates the event surfaces (registration, vendor list, attendee list) against the registration platform. See `core/SUBSTRATE.md` §Bootstrap Inventory Sweep.

## Probe shape — schema-declared stub (pending first project)

Event-planning probes are platform-specific and v5.1.1 ships this as a documented stub. Until the first event-planning project surfaces the canonical probe, the shape is:

```yaml
probe_method: "schema-declared-stub-pending-registration-platform"
expected_schema_declarations:
  - registration_platform:
      type: enum
      values: [eventbrite, luma, hopin, custom]
      required: true
  - probe_implementation:
      eventbrite: "GET /v3/events/{event_id}/attendees/ (paginated)"
      luma:       "GET /public/v1/event/get?api_id={event_id}"
      hopin:      "GET /api/v1/events/{event_id}/registrations"
      custom:     "operator-declared CSV import shape"
```

For v5.1.1, the agent at bootstrap asks the operator to manually attest the event scope: confirmed event ID, expected attendee count band, vendor list, and venue. The agent emits:

```
bootstrap.probe_skipped
  reason: "event-planning probe is stubbed pending first-project empirical signal; operator manually attested event details at bootstrap"
```

## When the probe is implemented

The first event-planning project bootstrapped under v5.1.1 produces empirical signal that nails down the canonical probe. This file gets rewritten with the canonical implementation when that lands. Until then, manual attestation is the documented path.

## Operator manual attestation shape

The conversation should produce structured attestation:

```
Event: <name>
  Date(s): <YYYY-MM-DD or range>
  Venue: <name + address> | virtual + platform
  Expected attendance: <number band>
  Registration platform: <eventbrite | luma | hopin | custom>
  Confirmed vendors: <list>
  Outstanding vendors: <list>
```

The agent records this attestation as the `declared` set; PROJECT.md §Scope is written from it.
