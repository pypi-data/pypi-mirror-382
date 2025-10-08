## meter-lib — Usage Guide

### Overview

`meter-lib` is a lightweight helper library for sending metering events to the Litewave backend and for looking up a customer account by `tenant_id`.

### Requirements

- Python 3.10+

### Installation

```bash
pip install meter-lib
```

### Parameters Required

```
tenant_id,
device_id,
meter_id,
total_usage,
start_time,
end_time
```

### Quickstart

```python
from meter_lib import post_meter_usage

tenant_id = "tenant_123"
device_id = "us-east-ing1"
meter_id = "document.basic.page"

result = post_meter_usage(
    tenant_id=tenant_id,
    device_id=device_id,
    meter_id=meter_id,
    total_usage=24,  # integer units as defined by your meter
)
```

### For AI enabled

```python
from meter_lib import post_meter_usage

tenant_id = "tenant_123"
device_id = "us-east-ing1"
meter_id = "chat.on.time_hours"
start_time = 1759791552000 # Timestamp in milliseconds

result = post_meter_usage(
  tenant_id=tenant_id,
  device_id=device_id,
  meter_id=meter_id,
  start_time= start_time # Timestamp in milliseconds
)

```

### For AI disabled

```python
from meter_lib import post_meter_usage

tenant_id = "tenant_123"
device_id = "us-east-ing1"
meter_id = "chat.on.time_hours"
end_time = 1779799552000 # Timestamp in milliseconds

result = post_meter_usage(
  tenant_id=tenant_id,
  device_id=device_id,
  meter_id=meter_id,
  end_time= end_time # Timestamp in milliseconds
)
```

```python
if result is None:
    print("Failed to post meter usage event")
else:
    print("Event accepted:", result)
```

### Error Handling

- `post_meter_usage` returns `None` for network errors or non-success HTTP statuses.
- Prefer explicit checks for `None` and add retries or backoff in your application layer if needed.

### API Reference

#### post_meter_usage(tenant_id: str, device_id: str, meter_id: str, total_usage: int) -> dict | None

- **Description**: Posts a metering event for a device and meter under a given tenant.
- **Headers**:
  - `x-tenant-id`: the tenant identifier (string)
  - `x-device-id`: the device identifier (string)
- **Payload (JSON)**:
  - `meter_id` (string)
  - `total_usage` (integer)
  - `customer_id` (string) — auto-filled by the library.`
- **Returns**: The backend JSON response (`dict`) on success, otherwise `None`.
- **Timeout**: 10 seconds.
- **Notes**:
  - If the customer lookup fails, the call is skipped and `None` is returned.
  - This function is synchronous and will block until the request completes or times out.

### List Of Meters:
- meter_id: "page.processed.basic"
  name: "Basic Document Scanning"
  type: "volume"
  description: "Total number of basic pages processed"

- meter_id: "page.processed.advanced"
  name: "Advanced Document Scanning"
  type: "volume"
  description: "Total number of advanced pages processed"

- meter_id: "report.generated.small"
  name: "Small Report Generation"
  type: "volume"
  description: "Total number of small reports generated"

- meter_id: "report.generated.medium"
  name: "Medium Report Generation"
  type: "volume"
  description: "Total number of medium reports generated"

- meter_id: "report.generated.large"
  name: "Large Report Generation"
  type: "volume"
  description: "Total number of large reports generated"

- meter_id: "report.generated.dataquery"
  name: "Data Query Report Generation"
  type: "volume"
  description: "Total number of data query reports generated"

- meter_id: "report.generated.insights"
  name: "Insights Report Generation"
  type: "volume"
  description: "Total number of insights reports generated"

- meter_id: "rule.executed.small"
  name: "Small Rule Execution"
  type: "volume"
  description: "Total number of rules executed with runtime less than 1 minute"

- meter_id: "rule.executed.medium"
  name: "Medium Rule Execution"
  type: "volume"
  description: "Total number of rules executed with runtime between 1 and 3 minutes"

- meter_id: "rule.executed.large"
  name: "Large Rule Execution"
  type: "volume"
  description: "Total number of rules executed with runtime greater than 4 minutes"

- meter_id: "chat.on.time_hours"
  name: "Litewave AI Assistant Usage (Hours)"
  type: "performance"
  description: "Total active chat usage time in hours"

- meter_id: "chat.query.time_secs"
  name: "Litewave AI Assistant Query Time (Seconds)"
  type: "performance"
  description: "Total time spent per query in seconds"

- meter_id: "document.storage.size_gb"
  name: "Document Storage Size"
  type: "volume"
  description: "Total document storage consumed in GB"

- meter_id: "template.processed.small"
  name: "Small Template Processing"
  type: "volume"
  description: "Total number of small templates processed"

- meter_id: "template.processed.medium"
  name: "Medium Template Processing"
  type: "volume"
  description: "Total number of medium templates processed"

- meter_id: "template.processed.large"
  name: "Large Template Processing"
  type: "volume"
  description: "Total number of large templates processed"

- meter_id: "template.processed.count"
  name: "Template Licensing Count"
  type: "volume"
  description: "Total number of licensed templates processed"

- meter_id: "template.licensed.total"
  name: "Yearly Template Setup"
  type: "volume"
  description: "Total yearly template setup count"

### Troubleshooting

- Confirm your `tenant_id`, `device_id`, and `meter_id` values are correct.

### Support

- Homepage: `https://github.com/aiorch/meter-lib`
- Issues: `https://github.com/aiorch/meter-lib/issues`
