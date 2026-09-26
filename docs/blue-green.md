# Blue/green deployment with automatic rollback

Production runs two copies of `frontend` and `course-service`, labelled
`version: blue` and `version: green`. Only one colour gets traffic.

| Object | What it does |
|---|---|
| `frontend-blue`, `frontend-green` | Deployments, 2 replicas each |
| `course-service-blue`, `course-service-green` | Deployments, 2 replicas each |
| Service `frontend` (LoadBalancer) and `course-service` | Public. Selector `version` = the LIVE colour. **This is the traffic switch.** |
| Service `frontend-preview` and `course-service-preview` | ClusterIP only. Selector `version` = the IDLE colour, for testing |

The templates are in `kubernetes/production/bluegreen/`. The pipeline renders
them with `envsubst`, one colour at a time.

## What `04 - Deploy to Production (Blue/Green)` does

1. Reads the live colour from `service/frontend` and picks the other one as idle.
2. Deploys the new SHA tagged images to the idle colour and waits for the rollout.
3. Points the preview services at the idle colour and smoke tests it through
   `kubectl port-forward` (health, colour and version, JWT login, real `/courses`
   calls, 401 without a token). If this fails the run stops and users never see it.
4. Swaps: one `kubectl patch` on each public Service selector.
5. Watches for 3 minutes: real API calls through the public IP, ready pods, and
   the Prometheus 5xx rate. Too many errors means step 6.
6. Automatic rollback: patches the selectors back to the old colour, which is
   still running, and fails the run with the reason. Optional Discord message.

## Try it

* Normal release: push to `main`. CI, staging and staging tests run first.
* Demo faults: Actions > 04 > Run workflow, give the live image SHA and pick
  `broken-api` (caught by the smoke test) or `late-errors` (passes the smoke
  test, caught by the watch, rolled back automatically).
* Watch it from your laptop: `./scripts/bluegreen-traffic.sh <public-ip>`
* See which colour answers: `http://<public-ip>/colour` and `/api/courses/health`
