# Copyright (c) 2013, 2018 National Technology and Engineering Solutions of Sandia, LLC. 
# Under the terms of Contract DE-NA0003525 with National Technology and Engineering 
# Solutions of Sandia, LLC, the U.S. Government retains certain rights in this software.

# This script creates a Python distribution wheel for the Slycat python interface, 
# now called slypi, formerly called slycat-web-client.  When run, it copies the latest 
# version of the slycat/web/client files (from the slycat repo) into slypi directory 
# (see note below) before it constructs the pip installable module.
#
# NOTE: 
# 1. You need to have the slycat directory (from github) available as ../slycat
# in order to run the setup.py file (see additional note below).
# 
# S. Martin
# 11/9/2023

# To publish to PyPi, perform the following steps:
#
# $ rm -rf dist
# $ python -m build --sdist --wheel
# $ twine upload dist/*
#
# To publish to testpypi, use:
#
# $ twine upload --repository-url https://test.pypi.org/legacy/ dist/*
#
# The first step builds the distribution, and the second step
# uploads to PyPi.  To install the package from another computer use:
#
# $ pip install slpyi
#
# To install from testpypi, use:
#
# $ pip install --extra-index-url https://testpypi.python.org/pypi slpyi
#   --upgrade --trusted-host testpypi.python.org --proxy wwwproxy.sandia.gov:80
#
# To install locally, use (from this directory):
#
# $ pip install -e .

from shutil import copyfile

# copy slycat.darray and slycat csv parser code into slypi directory. This
# makes slypi a Python package without other Slycat dependencies.
copyfile('../slycat/packages/slycat/darray.py', 'src/slypi/darray.py')
copyfile('../slycat/web-server/plugins/slycat-video-swarm/vs-parse-files.py', 'src/slypi/vs/vs_parse_files.py')

from setuptools import setup

if __name__ == "__main__":
    setup()

# import slypi
# VERSION = slypi.__version__

# # get README.md
# import pathlib

# # directory containing this file
# HERE = pathlib.Path(__file__).parent

# # text of the web-client-readme.txt file
# README = (HERE / "README.md").read_text()

# # create distribution
# import setuptools

# # create Python distribution wheel
# from setuptools import setup

# setup(
#     name="slypi",
#     version=VERSION,
#     description="Slycat python interface utilties for interacting with the Slycat " +
#                 "data analysis and visualization server.",
#     long_description=README,
#     long_description_content_type="text/markdown",
#     url="https://github.com/sandialabs/slypi",
#     author="Shawn Martin",
#     author_email="smartin@sandia.gov",
#     license="Sandia",
#     classifiers=[
#         "Programming Language :: Python :: 3",
#         "Programming Language :: Python :: 3.11",
#     ],
#     packages=setuptools.find_packages(),
#     include_package_data=True,
#     install_requires=["requests", "requests-kerberos",
#                       "numpy", "scikit-learn", 
#                       "pandas", "meshio", "imageio[ffmpeg]",
#                       "matplotlib", "ipyparallel",
#                       "umap-learn", "pyarrow"],
#     entry_points={
#         "console_scripts": [
#             "ps_upload_csv=slypi.ps.upload_csv:main",
#             "dac_upload_gen=slycat.dac.upload_gen:main"
#         ]
#     },
# )
