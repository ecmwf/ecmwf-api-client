#!/usr/bin/env python
#
# (C) Copyright 2012-2013 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0. 
# In applying this licence, ECMWF does not waive the privileges and immunities 
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

from ecmwfapi import ECMWFDataServer

# To run this example, you need an API key 
# available from https://api.ecmwf.int/v1/key/

server = ECMWFDataServer()
server.retrieve({
    'dataset' : 'tigge',
    'step'    : '24',
    'number'  : 'all',
    'levtype' : 'sl',
    'date'    : '20071001',
    'time'    : '00',
    'origin'  : 'all',
    'type'    : 'pf',
    'param'   : 'tp',
    'area'    : '70/-130/30/-60',
    'grid'    : '2/2',
    'target'  : 'data.grib'
})
