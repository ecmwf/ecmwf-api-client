#!/usr/bin/env python3
import ecmwfapi
import time


def test_mars():
    while True:
        try:
            c = ecmwfapi.ECMWFService("mars")
            c.execute({"date": "2000-01-01"}, "mars.grib")
            return
        except ecmwfapi.api.APIException as e:
            print(e)
            msg = str(e)
            if "USER_QUEUED_LIMIT_EXCEEDED" not in msg:
                raise

        time.sleep(120)


if __name__ == "__main__":
    test_mars()
