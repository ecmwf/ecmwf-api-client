# ecmwf-api-client

Python client for the [ECMWF Web API](https://confluence.ecmwf.int/display/WEBAPI). Two entry points:

- **`ECMWFDataServer`** — retrieve IFS research experiments.
- **`ECMWFService`** — access [MARS](https://confluence.ecmwf.int/display/WEBAPI/Access+MARS), ECMWF's Meteorological Archival and Retrieval System, for authorized users.

## What this client is for

- **IFS research experiments** — available anonymously, or with registered access for a better quality of service.
- **MARS archive access** — for authorized users; see [Access MARS](https://confluence.ecmwf.int/display/WEBAPI/Access+MARS) for who can access it and how.

## Looking for public datasets?

The **ECMWF Public Datasets Service** (TIGGE, S2S, ERA-Interim, and others) has been decommissioned. See the [decommissioning notice](https://confluence.ecmwf.int/display/DAC/Decommissioning+of+ECMWF+Public+Datasets+Service) for where each dataset moved — in short: TIGGE and S2S to the [ECMWF Data Store (ECDS)](https://ecds.ecmwf.int/), reanalyses to the [Climate Data Store (CDS)](https://cds.climate.copernicus.eu/), and real-time open forecast data is available via [ecmwf-opendata](https://github.com/ecmwf/ecmwf-opendata).

## Installation

```
$ pip install ecmwf-api-client
```

or with conda:

```
$ conda install -c conda-forge ecmwf-api-client
```

## Configure

### Anonymous access (default)

No configuration needed. Anonymous access works only for the IFS research experiments, with a lower quality of service. For everything else, and for a better quality of service, use registered access.

### Registered access (recommended)

- Register with ECMWF at https://www.ecmwf.int.
- Retrieve your API key at https://api.ecmwf.int/v1/key/ (see [Install ECMWF API Key](https://confluence.ecmwf.int/display/WEBAPI/Install+ECMWF+API+Key) for details, including key expiry and renewal).
- Save the key to `$HOME/.ecmwfapirc` (Unix/Linux/macOS) or `C:\Users\<USERNAME>\.ecmwfapirc` (Windows):

  ```
  {
      "url"   : "https://api.ecmwf.int/v1",
      "key"   : "XXXXXXXXXXXXXXXXXXXXXX",
      "email" : "john.smith@example.com"
  }
  ```

- Alternatively, point the environment variable `ECMWF_API_RC_FILE` to a file of your choice (takes priority over `.ecmwfapirc`).
- Or set `ECMWF_API_KEY`, `ECMWF_API_URL`, `ECMWF_API_EMAIL` directly in the environment (takes priority over `ECMWF_API_RC_FILE`).
- Or pass the values directly in code: `ECMWFDataServer(url=..., key=..., email=...)` or `ECMWFService("mars", url=..., key=..., email=...)`.

## Retrieving IFS research experiments

Use `ECMWFDataServer`:

```python
from ecmwfapi import ECMWFDataServer

server = ECMWFDataServer()
server.retrieve({
    # ... request parameters ...
})
```

Don't write the request by hand. Open the experiment's page (for example https://apps.ecmwf.int/ifs-experiments/rd/gkzp/), select what you need, and the site generates the exact request to paste into `retrieve({...})`.

## Accessing MARS

For MARS access, follow [Access MARS](https://confluence.ecmwf.int/display/WEBAPI/Access+MARS). The recommended way is the `mars` command wrapper script provided there, which runs MARS requests from a file. The wrapper is built on this package's `ECMWFService` class.

## Retrieving efficiently

Both IFS experiments and the MARS archive are stored on tape, so retrievals can be slow and large. Before submitting big requests, read [Retrieval efficiency](https://confluence.ecmwf.int/display/WEBAPI/Retrieval+efficiency) — it explains how to check the cost of a request first, how to structure requests around tapes, and the request limits. The [Web API FAQ](https://confluence.ecmwf.int/display/WEBAPI/Web+API+FAQ) covers monitoring requests and common errors.

## Logging

By default, log messages are printed to `stdout`. To use your own logging:

```python
import logging
from ecmwfapi import ECMWFDataServer

logging.basicConfig(level=logging.INFO)

def my_logging_function(msg):
    logging.info(msg)

server = ECMWFDataServer(log=my_logging_function)
```

## License

Copyright 2019 European Centre for Medium-Range Weather Forecasts (ECMWF)
Licensed under the Apache License, Version 2.0 (the “License”); you may not use this file except in compliance with the License. You may obtain a copy of the License at

> http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an “AS IS” BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
In applying this licence, ECMWF does not waive the privileges and immunities granted to it by virtue of its status as an intergovernmental organisation nor does it submit to any jurisdiction.
