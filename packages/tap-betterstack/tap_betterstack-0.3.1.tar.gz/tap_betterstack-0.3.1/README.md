<div align="center">

# tap-betterstack

<div>
  <a href="https://results.pre-commit.ci/latest/github/reservoir-data/tap-betterstack/main">
    <img alt="pre-commit.ci status" src="https://results.pre-commit.ci/badge/github/reservoir-data/tap-betterstack/main.svg"/>
  </a>
  <a href="https://github.com/reservoir-data/tap-betterstack/blob/main/LICENSE">
    <img alt="License" src="https://img.shields.io/github/license/reservoir-data/tap-betterstack"/>
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;">
  </a>
  <a href="https://pypi.org/p/tap-betterstack/">
    <img alt="Python versions" src="https://img.shields.io/pypi/pyversions/tap-betterstack"/>
  </a>
</div>

Singer tap for [Better Stack](https://betterstack.com). Built with the [Meltano Singer SDK](https://sdk.meltano.com).

</div

## Capabilities

* `catalog`
* `state`
* `discover`
* `about`
* `stream-maps`
* `schema-flattening`
* `batch`

## Settings

| Setting             | Required | Default | Description |
|:--------------------|:--------:|:-------:|:------------|
| token               | True     | None    | API Token for Better Stack |
| start_date          | False    | None    | Earliest datetime to get data from |
| stream_maps         | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). |
| stream_map_config   | False    | None    | User-defined config values to be used within map expressions. |
| flattening_enabled  | False    | None    | 'True' to enable schema flattening and automatically expand nested properties. |
| flattening_max_depth| False    | None    | The max depth to flatten schemas. |
| batch_config        | False    | None    |             |

A full list of supported settings and capabilities is available by running: `tap-betterstack --about`

## Streams

### Supported

* [`monitors`](https://betterstack.com/docs/uptime/api/list-all-existing-monitors/)
* [`monitor_groups`](https://betterstack.com/docs/uptime/api/list-all-existing-monitor-groups/)
* [`heartbeats`](https://betterstack.com/docs/uptime/api/list-all-existing-hearbeats/)
* [`heartbeat_groups`](https://betterstack.com/docs/uptime/api/list-all-existing-heartbeat-groups/)
* [`on_calls`](https://betterstack.com/docs/uptime/api/list-all-existing-on-call-calendars/)
* [`escalation_policies`](https://betterstack.com/docs/uptime/api/list-all-escalation-policies/)
* [`incidents`](https://betterstack.com/docs/uptime/api/list-all-incidents/)
* [`incident_events`](https://betterstack.com/docs/uptime/api/list-of-incident-timeline-events/)
* [`email_integrations`](https://betterstack.com/docs/uptime/api/list-all-email-integrations/)
* [`incoming_webhooks`](https://betterstack.com/docs/uptime/api/list-all-incoming-webhooks/)
* [`status_pages`](https://betterstack.com/docs/uptime/api/list-all-existing-status-pages/)

### Planned (PRs welcome!)

* [`status_page_sections`](https://betterstack.com/docs/uptime/api/list-existing-sections-of-a-status-page/)
* [`status_page_resources`](https://betterstack.com/docs/uptime/api/list-existing-resources-of-a-status-page/)
* [`status_page_reports`](https://betterstack.com/docs/uptime/api/list-existing-reports-on-a-status-page/)
* [`status_page_report_updates`](https://betterstack.com/docs/uptime/api/list-all-existing-status-updates-for-a-status-page-report/)

## Usage

You can easily run `tap-betterstack` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-betterstack --version
tap-betterstack --help
tap-betterstack --config CONFIG --discover > ./catalog.json
```

## Developer Resources

- [ ] `Developer TODO:` As a first step, scan the entire project for the text "`TODO:`" and complete any recommended steps, deleting the "TODO" references once completed.

### Initialize your Development Environment

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # or see https://docs.astral.sh/uv/getting-started/installation/
uv sync
```

### Create and Run Tests

Create tests within the `tests` subfolder and then run:

```bash
uv run pytest
```

You can also test the `tap-betterstack` CLI interface directly using the virtual environment:

```bash
uv run tap-betterstack --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
uv tool install meltano
# Initialize meltano within this directory
cd tap-betterstack
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-betterstack --version
# OR run a test `elt` pipeline:
meltano run tap-betterstack target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
