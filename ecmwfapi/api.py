#
# (C) Copyright 2012-2013 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

# make the python3-like print behave in python 2
from __future__ import print_function

import json
import os
import sys
import time
import traceback
import textwrap
from contextlib import closing

# python 2 and 3 compatible urllib and httplib imports
try:
    from urllib.parse import urlparse
    from urllib.parse import urljoin
    from urllib.error import HTTPError, URLError
    from urllib.request import (
        HTTPRedirectHandler,
        Request,
        build_opener,
        urlopen,
        addinfourl,
    )
    from http.client import BadStatusLine
except ImportError:
    from urlparse import urlparse
    from urlparse import urljoin
    from urllib2 import HTTPError, URLError
    from urllib2 import HTTPRedirectHandler, Request, build_opener, urlopen, addinfourl
    from httplib import BadStatusLine

try:
    import ssl
except ImportError:
    sys.exit("Python socket module was not compiled with SSL support. Aborting...")


VERSION = "1.6.3"


DEFAULT_RCFILE_PATH = "~/.ecmwfapirc"
ANONYMOUS_APIKEY_VALUES = (
    "anonymous",
    "https://api.ecmwf.int/v1",
    "anonymous@ecmwf.int",
)


class APIKeyNotFoundError(Exception):
    pass


class APIKeyFetchError(Exception):
    pass


def get_apikey_values_from_environ():
    apikey_values = (
        os.getenv("ECMWF_API_KEY"),
        os.getenv("ECMWF_API_URL"),
        os.getenv("ECMWF_API_EMAIL"),
    )

    if not any(apikey_values):
        raise APIKeyNotFoundError("ERROR: No API key found in the environment")
    elif not all(apikey_values):
        raise APIKeyFetchError("ERROR: Incomplete API key found in the environment")
    else:
        return apikey_values


def get_apikey_values_from_rcfile(rcfile_path):
    rcfile_path = os.path.normpath(os.path.expanduser(rcfile_path))

    try:
        with open(rcfile_path) as f:
            apikey = json.load(f)
    except FileNotFoundError as e:
        raise APIKeyNotFoundError(str(e))
    except IOError as e:  # Failed reading from file
        raise APIKeyFetchError(str(e))
    except ValueError:  # JSON decoding failed
        raise APIKeyFetchError(
            "ERROR: Missing or malformed API key in '%s'" % rcfile_path
        )
    except Exception as e:  # Unexpected error
        raise APIKeyFetchError(str(e))
    else:
        try:
            return (apikey["key"], apikey["url"], apikey["email"])
        except:
            raise APIKeyFetchError(
                "ERROR: Missing or malformed API key in '%s'" % rcfile_path
            )


def get_apikey_values():
    """Get the API key values in Python tuple format either directly from the
    environment, or from a file. If no API key is found, fall back to anonymous
    access.

    The complete workflow is the following:

    - Step 1: the environment is checked for variables ECMWF_API_KEY,
        ECMWF_API_URL, ECMWF_API_EMAIL.
        * If all found, and not empty, return their values in Python tuple
            format. 
        * If only some found, and not empty, assume an incomplete API key, and
            raise APIKeyFetchError.
        * If none found, or found but empty, assume no API key available in the
            environment, and continue to the next step.

    - Step 2: the environment is checked for variable ECMWF_API_RC_FILE, meant
        to point to a user defined API key file.
        * If found, but pointing to a file not found, raise APIKeyNotFoundError.
        * If found, and the file it points to exists, but cannot not be read, or
            contains an invalid API key, raise APIKeyFetchError.
        * If found, and the file it points to exists, can be read, and contains
            a valid API key, return the API key in Python tuple format.
        * If not found, or empty, assume no user provided API key file and
            continue to the next step.

    - Step 3: try the default ~/.ecmwfapirc file.
        * Same as step 2, except for when ~/.ecmwfapirc is not found, where we
            continue to the next step.

    - Step 4: No API key found, so fall back to anonymous access.

    Returns:
        Pyhon tuple with the API key token, url, and email.

    Raises:
        APIKeyFetchError: If an API key is found, but invalid.
        APIKeyNotFound: When ECMWF_API_RC_FILE is defined, but pointing to a
            file that does not exist.
    """
    try:
        return get_apikey_values_from_environ()
    except APIKeyNotFoundError:
        env_rcfile_path = os.getenv("ECMWF_API_RC_FILE")
        if env_rcfile_path:
            return get_apikey_values_from_rcfile(env_rcfile_path)
        else:
            try:
                return get_apikey_values_from_rcfile(DEFAULT_RCFILE_PATH)
            except APIKeyNotFoundError:
                return ANONYMOUS_APIKEY_VALUES


class RetryError(Exception):
    def __init__(self, code, text):
        self.code = code
        self.text = text

    def __str__(self):
        return "%d %s" % (self.code, self.text)


class APIException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def robust(func):
    def wrapped(self, *args, **kwargs):
        max_tries = tries = 10
        delay = 60  # retry delay
        last_error = None
        while tries > 0:
            try:
                return func(self, *args, **kwargs)
            except HTTPError as e:
                if self.verbose:
                    self.log("WARNING: HTTPError received %s" % e)
                if e.code < 500 or e.code in (501,):  # 501: not implemented
                    raise
                last_error = e
            except BadStatusLine as e:
                if self.verbose:
                    self.log("WARNING: BadStatusLine received %s" % e)
                last_error = e
            except URLError as e:
                if self.verbose:
                    self.log("WARNING: URLError received %s %s" % (e.errno, e))
                last_error = e
            except APIException:
                raise
            except RetryError as e:
                if self.verbose:
                    self.log("WARNING: HTTP received %s" % e.code)
                    self.log(e.text)
                last_error = e
            except:
                if self.verbose:
                    self.log("Unexpected error: %s" % sys.exc_info()[0])
                    self.log(traceback.format_exc())
                raise
            self.log("Error contacting the WebAPI, retrying in %d seconds ..." % delay)
            time.sleep(delay)
            tries -= 1
        # if all retries have been exhausted, raise the last exception caught
        self.log("Could not contact the WebAPI after %d tries, failing !" % max_tries)
        raise last_error

    return wrapped


def get_api_url(url):
    parsed_uri = urlparse(url)
    return "{uri.scheme}://{uri.netloc}/{apiver}/".format(
        uri=parsed_uri, apiver=parsed_uri.path.split("/")[1]
    )


class Ignore303(HTTPRedirectHandler):

    """Handler to automatically follow redirects.

    Mainly implement when the API moved from http to https.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if code in [301, 302]:
            # We want the posts to work even if we are redirected
            try:
                # Python < 3.4
                data = req.get_data()
            except AttributeError:
                # Python >= 3.4
                data = req.data

            try:
                # Python < 3.4
                origin_req_host = req.get_origin_req_host()
            except AttributeError:
                # Python >= 3.4
                origin_req_host = req.origin_req_host

            return Request(
                newurl,
                data=data,
                headers=req.headers,
                origin_req_host=origin_req_host,
                unverifiable=True,
            )
        return None

    def http_error_303(self, req, fp, code, msg, headers):
        return addinfourl(fp, headers, req.get_full_url(), code)


def no_log(msg):
    pass


def print_with_timestamp(msg):
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print("%s %s" % (t, msg))


class Connection(object):
    def __init__(
        self, url, email=None, key=None, verbose=False, quiet=False, log=no_log
    ):
        self.url = url
        self.email = email
        self.key = key
        self.retry = 5
        self.location = None
        self.done = False
        self.value = True
        self.offset = 0
        self.verbose = verbose
        self.quiet = quiet
        self.log = log
        self.status = None

    @robust
    def call(self, url, payload=None, method="GET"):
        # Ensure full url
        url = urljoin(self.url, url)

        if self.verbose:
            self.log("Calling method %s on %s" % (method, url))

        headers = {
            "Accept": "application/json",
            "From": self.email,
            "X-ECMWF-KEY": self.key,
        }

        opener = build_opener(Ignore303)

        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        url = "%s?offset=%d&limit=500" % (url, self.offset)
        req = Request(url=url, data=data, headers=headers)
        if method:
            req.get_method = lambda: method

        error = False
        try:
            try:
                res = opener.open(req)
            except HTTPError as e:
                # It seems that some version of urllib2 are buggy
                if e.code <= 299:
                    res = e
                else:
                    raise
        except HTTPError as e:
            if self.verbose:
                self.log(e)
            error = True
            res = e
            # 429: Too many requests
            # 502: Proxy Error
            # 503: Service Temporarily Unavailable
            if e.code == 429 or e.code >= 500:
                raise RetryError(e.code, e.read())

        self.retry = int(res.headers.get("Retry-After", self.retry))
        code = res.code
        if code in [201, 202]:
            self.location = urljoin(url, res.headers.get("Location", self.location))

        if self.verbose:
            self.log("Response code: %s" % code)
            self.log("Response Content-Type: %s" % res.headers.get("Content-Type"))
            self.log("Response Content-Length: %s" % res.headers.get("Content-Length"))
            self.log("Response Location: %s" % res.headers.get("Location"))

        body = res.read().decode("utf-8")
        res.close()

        if code in [204]:
            self.last = None
            return None
        else:
            try:
                self.last = json.loads(body)
            except Exception as e:
                self.last = {"error": "%s: %s" % (e, body)}
                error = True

        if self.verbose:
            self.log("Response content: %s" % json.dumps(self.last, indent=4))

        self.status = self.last.get("status", self.status)

        if self.verbose:
            self.log("Status %s" % self.status)

        if "messages" in self.last:
            for n in self.last["messages"]:
                if not self.quiet:
                    self.log(n)
                self.offset += 1

        if code == 200 and self.status == "complete":
            self.value = self.last
            self.done = True
            if isinstance(self.value, dict) and "result" in self.value:
                self.value = self.value["result"]

        if code in [303]:
            self.value = self.last
            self.done = True

        if "error" in self.last:
            raise APIException("ecmwf.API error 1: %s" % (self.last["error"],))

        if error:
            raise APIException("ecmwf.API error 2: %s" % (res,))

        return self.last

    def submit(self, url, payload):
        self.call(url, payload, "POST")

    def POST(self, url, payload):
        return self.call(url, payload, "POST")

    def GET(self, url):
        return self.call(url, None, "GET")

    def wait(self):
        if self.verbose:
            self.log("Sleeping %s second(s)" % (self.retry))
        time.sleep(self.retry)
        self.call(self.location, None, "GET")

    def ready(self):
        return self.done

    def result(self):
        return self.value

    def cleanup(self):
        try:
            if self.location:
                self.call(self.location, None, "DELETE")
        except:
            pass


class APIRequest(object):
    def __init__(
        self,
        url,
        service,
        email=None,
        key=None,
        log=no_log,
        quiet=False,
        verbose=False,
        news=True,
    ):
        self.url = url
        self.service = service
        self.log = log
        self.quiet = quiet
        self.verbose = verbose

        self.connection = Connection(
            url, email=email, key=key, quiet=quiet, verbose=verbose, log=log
        )

        self.log("ECMWF API python library %s" % (VERSION,))
        self.log("ECMWF API at %s" % (self.url,))

        user = self.connection.call("%s/%s" % (self.url, "who-am-i"))

        if os.getenv("GITHUB_ACTION") is None:
            self.log("Welcome %s" % (user["full_name"] or "user '%s'" % user["uid"],))

        general_info = self.connection.call("%s/%s" % (self.url, "info")).get("info")
        self.show_info(general_info, user["uid"])

        service_specific_info = self.connection.call(
            "%s/%s/%s" % (self.url, self.service, "info")
        ).get("info")
        self.show_info(service_specific_info, user["uid"])

        if news:
            try:
                news = self.connection.call(
                    "%s/%s/%s" % (self.url, self.service, "news")
                )
                for n in news["news"].split("\n"):
                    self.log(n)
            except:
                pass

    def _bytename(self, size):
        prefix = {"": "K", "K": "M", "M": "G", "G": "T", "T": "P", "P": "E"}
        l = ""
        size = size * 1.0
        while 1024 < size:
            l = prefix[l]
            size = size / 1024
        s = ""
        if size > 1:
            s = "s"
        return "%g %sbyte%s" % (size, l, s)

    @robust
    def _transfer(self, url, path, size):
        start = time.time()
        existing_size = 0
        req = Request(url)

        if os.path.exists(path):
            mode = "ab"
            existing_size = os.path.getsize(path)
            req.add_header("Range", "bytes=%s-" % existing_size)
        else:
            mode = "wb"

        self.log(
            "Transfering %s into %s" % (self._bytename(size - existing_size), path)
        )
        self.log("From %s" % (url,))

        bytes_transferred = 0
        with open(path, mode) as f:
            with closing(urlopen(req)) as http:
                while True:
                    chunk = http.read(1048576)  # 1MB chunks
                    if not chunk:
                        break
                    f.write(chunk)
                    bytes_transferred += len(chunk)

        end = time.time()

        if end > start:
            transfer_rate = bytes_transferred / (end - start)
            self.log("Transfer rate %s/s" % self._bytename(transfer_rate))

        return existing_size + bytes_transferred

    def execute(self, request, target=None):
        status = None

        self.connection.submit("%s/%s/requests" % (self.url, self.service), request)
        self.log("Request submitted")
        self.log("Request id: " + self.connection.last.get("name"))
        if self.connection.status != status:
            status = self.connection.status
            self.log("Request is %s" % (status,))

        while not self.connection.ready():
            if self.connection.status != status:
                status = self.connection.status
                self.log("Request is %s" % (status,))
            self.connection.wait()

        if self.connection.status != status:
            status = self.connection.status
            self.log("Request is %s" % (status,))

        result = self.connection.result()
        if target:
            if os.path.exists(target):
                # Empty the target file, if it already exists, otherwise the
                # transfer below might be fooled into thinking we're resuming
                # an interrupted download.
                open(target, "w").close()

            size = -1
            tries = 0
            while size != result["size"] and tries < 10:
                size = self._transfer(
                    urljoin(self.url, result["href"]), target, result["size"]
                )
                if size != result["size"] and tries < 10:
                    tries += 1
                    self.log("Transfer interrupted, resuming in 60s...")
                    time.sleep(60)
                else:
                    break

            assert size == result["size"]

        self.connection.cleanup()

        return result

    def show_info(self, info, uid):
        n = 0
        if "message" in info:
            self.log("")
            n += 1
            for m in textwrap.wrap(info["message"]):
                self.log(m)

        if uid in info.get("user_messages", {}):
            self.log("")
            n += 1
            for m in textwrap.wrap(info["user_messages"][uid]):
                self.log(m)

        if n:
            self.log("")


class ECMWFDataServer(object):
    def __init__(
        self, url=None, key=None, email=None, verbose=False, log=print_with_timestamp
    ):
        if url is None or key is None or email is None:
            key, url, email = get_apikey_values()

        self.url = url
        self.key = key
        self.email = email
        self.verbose = verbose
        self.log = log

    def retrieve(self, req):
        target = req.get("target")
        dataset = req.get("dataset")
        c = APIRequest(
            self.url,
            "datasets/%s" % (dataset,),
            email=self.email,
            key=self.key,
            log=self.log,
            verbose=self.verbose,
        )
        c.execute(req, target)


class ECMWFService(object):
    def __init__(
        self,
        service,
        url=None,
        key=None,
        email=None,
        verbose=False,
        log=print_with_timestamp,
        quiet=False,
    ):
        if url is None or key is None or email is None:
            key, url, email = get_apikey_values()

        self.service = service
        self.url = url
        self.key = key
        self.email = email
        self.verbose = verbose
        self.quiet = quiet
        self.log = log

    def execute(self, req, target):
        c = APIRequest(
            self.url,
            "services/%s" % (self.service,),
            email=self.email,
            key=self.key,
            log=self.log,
            verbose=self.verbose,
            quiet=self.quiet,
        )
        c.execute(req, target)
        self.log("Done")
