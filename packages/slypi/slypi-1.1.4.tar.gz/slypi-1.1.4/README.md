## SlyPI
Python Interface for Slycat.

## Description
Slycat is a web application for interactive visualization of ensemble data (see https://github.com/sandialabs/slycat and https://slycat.readthedocs.io/en/latest).  The SlyPI project contains code that enables you to interact with the Slycat web server through a Python interface.  You can query the Slycat server, create Slycat models, and use the code to integrate your own algorithms into the Slycat pipeline.

## Documentation

Full documentation can be found in the docs folder and can be compiled using Sphinx with

```sh
make html
```

The resulting documention can be accessed under build from the file index.html.  You can also
read the compiled version at https://slypi.readthedocs.io/en/latest/index.html.

## Installation
This code is available at https://pypi.org/project/slypi/ and can be installed using

```sh
pip install slypi
```

If you are working behind a proxy, you might also need, e.g.

```sh
pip install slypi --proxy your-proxy:your-port
```

If you are getting SSL certificate errors, you can use:

```sh
pip install slypi --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

Be aware that the last option is insecure.  The better approach is to 
fix your SSL certificate and/or point Python to a copy of the certificate.
This can be done using:

```sh
pip config set global.cert path-to-your-certificate
```

You can also install locally from this repository using:

```sh
pip install -e slypi .
```

Note: that for SlyPI to work, you must have a Slycat server running.  
See https://slycat.readthedocs.io/en/latest/ for details on setting up a server.

## Optional Dependencies

SlyPI uses PyMKS (https://github.com/materialsinnovation/pymks, https://pypi.org/project/pymks/) to compute auto-correlation.  This package doesn't install with versions of Python past 3.11.8, so it is included as an optional dependency.  If you want to use auto-correlation, use

```sh
pip install slypi[auto]
```

## Basic Use

SlyPI can be imported from within a Python file using

    import slypi

Some examples using SlyPI can be found in the SlyPI
source directory.  These can be run using, e.g.

```sh
python -m slypi.util.list_markings
```

In addition, there are two main entry points defined, one for the Slycat Dial-A-Cluster model

```sh
dac_upload_gen
```
and one for the parameter space model

```sh
ps_upload_csv
```

## Kerberos

The --kerberos option relies on a working Kerberos installation on your system.  Sometimes
this will fail.  If you get an error related to Kerberos credentials (e.g. "Couldn't find
Kerberos ticket," or "User not Kerberos authenticated"), try:

```sh
kinit
```

Then re-run the original command.

## Proxies/Certificates

If you are separated from the Slycat server by a proxy, or have not set up a security
certificate, you will have to use the SlyPI proxy settings.  The proxy
settings are available using the flags:

* --http-proxy
* --https-proxy
* --verify
* --no-verify

The proxy flags are by default set to "no proxy".  If you have proxies set in the
environment variables, they will be ignored.  The proxy flags are used as follows
(for example):

```sh
python -m slypi.list_markings --http-proxy http://your.http.proxy --https-proxy https://your.https.proxy
```

The verify flag can be used to pass a security certificate as a command line argument and
the --no-verify flag can be used to ignore the security certificates altogether.

## General Utilities

The simplest examples of interacting with the Slycat server issue
requests for markings and projects, e.g.

```sh
python -m slypi.util.list_markings
python -m slypi.util.list_projects
```

To examine a particular model or project, use

```sh
python -m slypi.util.get_model mid
python -m slypi.util.get_project pid
```

where mid and pid are the hash identifiers for a Slycat model
or project residing on the Slycat server.  These IDs can be extracted
from the URL in the Slycat web browser client, or by using
Info -> Model Details from the browser.

## Creating Models

The SlyPI module provides a command line option for creating Slycat
models.  For example, to create a sample CCA model using random data, use:

```sh
python -m slypi.cca.upload_random
```

To create a sample CCA model from a CSV file, use:

```sh
python -m slypi.cca.upload_csv slycat-data/cars.csv --input Cylinders Displacement Weight Year --output MPG Horsepower Acceleration --project-name "CCA Models"
```

where "slycat-data/cars.csv" is from the slycat-data git repository at
https://github.com/sandialabs/slycat-data.

Note that when a model is created, the URL is given in the console and
can be copied into a web browser to display the model.  The model ID
can also be extracted from this URL (it is the hash at the end of the URL).

## Parameter Space Models

SlyPI also provides a programmatic interface for creating models.  To create
a Parameter Space model from a python script, use the SlyPI module as follows:

```{python}
import slypi.ps.upload_csv as ps_upload_csv

# parameter space file
CARS_FILE = ['../slycat-data/cars.csv']

# input/output columns for cars data file
CARS_INPUT = ['--input-columns', 'Model', 'Cylinders', 'Displacement', 'Weight', 'Year']
CARS_OUTPUT = ['--output-columns', 'MPG', 'Horsepower', 'Acceleration']

# create PS model from cars file
ps_parser = ps_upload_csv.parser()
arguments = ps_parser.parse_args(CARS_FILE + CARS_INPUT + CARS_OUTPUT)
ps_upload_csv.create_model(arguments, ps_upload_csv.log)     

```

A Parameter Space model can also  be created from .csv file using the 
ps_csv script.  From the command line, use:

```sh
python -m slypi.ps.upload_csv slycat-data/cars.csv --input-columns Cylinders Displacement Weight Year --output-columns MPG Horsepower Acceleration --project-name "PS Models"
```

## Dial-A-Cluster (DAC) Models

Dial-A-Cluster models can be loaded using different formats.  The first
format is the generic dial-a-cluster format, described more fully in
the Slycat user manual.

To upload a DAC generic .zip file, use

```sh
dac_upload_gen slycat-data/dial-a-clsuter/weather-dac-gen.zip --project-name "DAC Models"
```

This will create a model from a single .zip file containing the appropriate
folders with the pre-computed distance or PCA matrices.

## Other Models

Currently, SlyPI supports Slycat CCA, DAC, PS, and Videoswarm models.  The only Slycat model type still unsupported is Time Series.  For examples using CCA, DAC, PS, and Videoswarm, see the full documentation.

## Contact
Shawn Martin -- smartin@sandia.gov

## License
Distributed under the Sandia license. See LICENSE file for more information.
