# Queue and background jobs

Work that is slow, retryable, or triggered by an event belongs in the queue, not in the
web request.

## Writing a job

- Extend HumHub's queue job base class (an active-job style class). For long work use
  the long-running variant if the installed version offers one. Verify class names.
- Keep job properties small and serializable: ids and scalars, not model instances.
- Reload models inside `run()`. A job may execute minutes later.
- Make jobs **idempotent**. They can be retried or run twice.
- Do not use the web user. Pass the user id explicitly if the job acts on behalf of
  someone, and re-check permission.

## Enqueueing

Push a job from a controller, service or event handler through the queue component.
Do not enqueue inside an open database transaction that may still roll back; enqueue
after commit.

## Failure handling

- Log with context (job class, ids), not secrets or personal data.
- Distinguish permanent failures (do not retry) from transient ones (retry).
- Outbound HTTP from jobs needs timeouts and bounded retries.

## Where this meets federation

Delivery of federated activities and processing of inbox requests run as queue jobs.
The protocol rules (what to retry, ordering, idempotency on activity ids) are in
[messaging-and-side-effects](messaging-and-side-effects.md); the job wiring follows this file.
