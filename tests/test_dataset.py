#!/usr/bin/env python3
import ecmwfapi
import time
import os


def test_dataset():
    while True:
        try:
            c = ecmwfapi.ECMWFDataServer("mars")
            c.retrieve(
                {
                    "dataset": "tigge",
                    "step": "24",
                    "levtype": "sl",
                    "date": "20071001",
                    "time": "00",
                    "origin": "ecmf",
                    "type": "cf",
                    "param": "2t",
                    "target": "tigge.grib",
                }
            )
            assert os.path.getsize("tigge.grib") == 428963
            return

        except ecmwfapi.api.APIException as e:
            print(e)
            msg = str(e)
            if "USER_QUEUED_LIMIT_EXCEEDED" not in msg:
                raise

        time.sleep(120)



if __name__ == "__main__":
    test_dataset()
