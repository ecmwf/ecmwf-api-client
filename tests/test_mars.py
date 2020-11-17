#!/usr/bin/env python3
import ecmwfapi

def test_mars():
   c = ecmwfapi.ECMWFService("mars")
   c.execute({"date": "2000-01-01"}, "mars.grib")

if __name__ == "__main__":
    test_mars()
