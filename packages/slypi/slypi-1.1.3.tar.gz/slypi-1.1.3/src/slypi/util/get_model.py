#!/bin/env python
# Copyright (c) 2013, 2018 National Technology and Engineering Solutions of Sandia, LLC . Under the terms of Contract
# DE-NA0003525 with National Technology and Engineering Solutions of Sandia, LLC, the U.S. Government
# retains certain rights in this software.

import pprint
import slypi

parser = slypi.ArgumentParser("Get model details from Slycat server.")
parser.add_argument("mid", help="The ID of the model to retrieve")
arguments = parser.parse_args()

connection = slypi.connect(arguments)
model = connection.get_model(arguments.mid)
pprint.pprint(model)
