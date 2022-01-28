# ecmwf-api-client

# Installation

Install via pip with:

> $ pip install ecmwf-api-client

# Configure

## Anonymous access (default, not recommended)

Anonymous access is the default type of access, with no configuration needed.

However, anonymous access is only available for a limited set of datasets, and comes with a much lower quality of service. For access to all the available datasets, and an improved quality of service, please use registered access (see below).

## Registered access (recommended)

* Register with ECMWF at https://apps.ecmwf.int/registration/.
* Login at https://apps.ecmwf.int/auth/login/.
* Retrieve you API access key at https://api.ecmwf.int/v1/key/.

   Note that the API access key expires in 1 year. You will receive an email to the registered email address 1 month before the expiration date with the renewal instructions. To check the expiry date of your current key, log into www.ecmwf.int, and go to https://api.ecmwf.int/v1/key/.

* Copy and paste the information on this page into the file $HOME/.ecmwfapirc (Unix/Linux) or %USERPROFILE%\\.ecmwfapirc (Windows: usually in C:\\Users\\\<USERNAME\>\\.ecmwfapirc).

   Your $HOME/.ecmwfapirc (Unix/Linux) or %USERPROFILE%\\.ecmwfapirc (Windows) should look something like this:
   ```
   {
       "url"   : "https://api.ecmwf.int/v1",
       "key"   : "XXXXXXXXXXXXXXXXXXXXXX",
       "email" : "john.smith@example.com"
   }
   ```
   
# Example

You can test this small python script to retrieve TIGGE data:
```
#!/usr/bin/env python
from ecmwfapi import ECMWFDataServer

# To run this example, you need an API key
# available from https://api.ecmwf.int/v1/key/

server = ECMWFDataServer()
server.retrieve({
    'origin'    : "ecmf",
    'levtype'   : "sfc",
    'number'    : "1",
    'expver'    : "prod",
    'dataset'   : "tigge",
    'step'      : "0/6/12/18",
    'area'      : "70/-130/30/-60",
    'grid'      : "2/2",
    'param'     : "167",
    'time'      : "00/12",
    'date'      : "2014-11-01",
    'type'      : "pf",
    'class'     : "ti",
    'target'    : "tigge_2014-11-01_0012.grib"
})
```

# Logging

Logging messages by default are emitted to `stdout` using Python's `print` statement.

To change that behaviour, one can define their own logging function and use it like so:

```
import logging
from ecmwfapi import ECMWFDataServer

logging.basicConfig(level=logging.INFO)

def my_logging_function(msg):
    logging.info(msg)

server = ECMWFDataServer(log=my_logging_function)
```

# License

Copyright 2019 European Centre for Medium-Range Weather Forecasts (ECMWF)
Licensed under the Apache License, Version 2.0 (the “License”); you may not use this file except in compliance with the License. You may obtain a copy of the License at

> http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an “AS IS” BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
In applying this licence, ECMWF does not waive the privileges and immunities granted to it by virtue of its status as an intergovernmental organisation nor does it submit to any jurisdiction.
