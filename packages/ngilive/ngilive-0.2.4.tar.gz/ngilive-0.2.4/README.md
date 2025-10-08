# NGILIVE SDK

## Usage

Useful library to develop against the NGI Live API.

It helps you get access to the API by doing all the difficult auth things.

Additionally it provides nice type hinted bindings for the API endpoints,
so you can follow code completion instead of reading documentation!

```python
from ngilive import API

api = API()


sensor_response = api.query_sensors(
    20190539,
    logger="IK50",
    unit="V",
)
```

The first time you run it, you will see an output like this in your terminal.
Perform the log in as prompted, and you will not see it again until your access has
expired.

```
[18:41:13] ngilive.auth INFO: Please complete the authentication in your browser: https://keycloak.ngiapi.no/auth/...
```

## Example Queries

#### Query Sensor Metadata

```python
from ngilive import API

api = API()


sensor_response = api.query_sensors(
    20190539,
    logger="IK50",
    unit="V",
)
```

Example response:

```json
{
  "sensors": [
    {
      "name": "18V_IK50",
      "unit": "V",
      "logger": "IK50",
      "type": "zBat18V",
      "pos": {
        "north": null,
        "east": null,
        "mash": null,
        "coordinateSystem": {
          "authority": "EPSG",
          "srid": null
        }
      }
    },
    {
      "name": "3V_IK50",
      "unit": "V",
      "logger": "IK50",
      "type": "zBat3V",
      "pos": {
        "north": null,
        "east": null,
        "mash": null,
        "coordinateSystem": {
          "authority": "EPSG",
          "srid": null
        }
      }
    }
  ]
}
```

#### Query datapoints

```python
datapoints = api.query_datapoints(
    project_number=20190539,
    start=datetime.now(tz=UTC) - timedelta(days=1),
    end=datetime.now(tz=UTC),
    logger="IK50",
    unit="V",
)
```

## Authentication

#### Authorization Code

You can use this library to obtain an access token and call the API.
It will open the browser for you, and ask you to log in to geohub.

The below example is useful if you want to control the HTTP client yourself, for
example using `requests` or `httpx` libraries.

```python
import httpx

from ngilive.auth import AuthorizationCode

auth = AuthorizationCode()
access_token = auth.get_token()

response = httpx.get(
    "http://api.test.ngilive.no/projects/20190539/sensors",
    headers={"Authorization": f"Bearer {access_token}"},
)
```

#### Client Credentials

This example uses client_id and client secret instead of signing in
in the browser. It is useful in cases where an automatic job should
call the API, which cannot log in via the browser. For other usecases,
use AuthorizationCode instead.

You can also use the ClientCredentials helper to get an access token
like in the above Authorization code example.

```python
from ngilive import API
from ngilive.auth import ClientCredentials

auth = ClientCredentials(
    client_id="data-api-test-client",
    client_secret="<client secret>",
)

api = API(auth=auth)

# Now you can query the API without logging in
# sensor_response = api.query_sensors(20190539)
```
