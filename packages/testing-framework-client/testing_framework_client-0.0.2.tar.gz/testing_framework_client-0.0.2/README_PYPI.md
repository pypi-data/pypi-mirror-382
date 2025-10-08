# Spirii Testing Framework Client

Python client library for interacting with the **Testing Framework public endpoints**.  
Handles authentication, automatic token refresh, and provides convenient methods for common endpoints.

## Installation

Install directly from PyPi:

```bash
pip install testing-framework-client
```

Create a .env file in the root of the project if it is not there and then add:
```sh
TESTING_FRAMEWORK_BASE_URL=https://testing-framework.spirii.dk
```


## Usage

```python
from datetime import datetime, timedelta, UTC

from testing_framework_client.client import (
    Unit,
    DistributionStrategy,
    TFClient,
)
TEST_CHARGER = 1234

# TFClient will automatically use your .env and persisted tokens
client = TFClient()

# Get chargebox
chargebox = client.get_chargebox(TEST_CHARGER)

# Get connector
connector = client.get_connector(TEST_CHARGER, 1)

# Set limit
valid_to = datetime.now(UTC) + timedelta(hours=1)
client.set_charge_limit(
    limit=7.0,
    unit=Unit.W,
    valid_to=valid_to,
    chargebox_id=TEST_CHARGER,
    connector_id=1,
    distribution_strategy=DistributionStrategy.HOLD,
)

# Clear limit
valid_to = datetime.now(UTC) + timedelta(hours=1)
client.clear_charge_limit(chargebox_id=TEST_CHARGER, connector_id=1)

```
