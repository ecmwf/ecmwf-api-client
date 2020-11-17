#!/usr/bin/env python3
import ecmwfapi
import time
import os


def test_mars():
    while True:
        try:
            c = ecmwfapi.ECMWFService("mars")
            c.execute({"date": "2000-01-01"}, "mars.grib")
            assert os.path.getsize("mars.grib") == 1238868

            return
        except ecmwfapi.api.APIException as e:
            print(e)
            msg = str(e)
            if "USER_QUEUED_LIMIT_EXCEEDED" not in msg:
                raise

        time.sleep(120)



if __name__ == "__main__":
    test_mars()
