# Copyright (c) 2013, 2018 National Technology and Engineering Solutions of Sandia, LLC . Under the terms of Contract
# DE-NA0003525 with National Technology and Engineering Solutions of Sandia, LLC, the U.S. Government
# retains certain rights in this software.

# This script reads a local videoswarm format consisting of a .csv, .xcoords, .ycoords,
# and .trajectories files.  These files are the same files that are selected using the "local"
# option in the videoswarm wizard.

import os
import urllib.parse as urlparse
import numpy as np

import slypi

# slycat parsers
import slypi.pandas_util
import slypi.vs.vs_parse_files as vs_parse

# parse command line arguments
def parser():

    parser = slypi.ArgumentParser(description=
        "Create Slycat VideoSwarm model from local format (.csv, .xcoords, .ycoords, .trajectories) files.")

    # required named arguments
    required = parser.add_argument_group('required arguments')

    # input files
    required.add_argument("--csv-file", help="Input .csv file.", required=True)
    required.add_argument("--xcoords-file", help="Input .xcoords file.", required=True)
    required.add_argument("--ycoords-file", help="Input .ycoords file.", required=True)
    required.add_argument("--traj-file", help="Input .trajectories file.", required=True)

    # video column
    required.add_argument("--video-column", help="Header name of video column.", required=True)

    # options to modify video column link
    parser.add_argument("--video-hostname", default=None, 
        help="Optionally override the hostname for the video column.")
    parser.add_argument("--strip", type=int, default=None, 
        help="Optionally strip N prefix directories from the video URLs.")

    # model and project names/descriptions
    parser.add_argument("--marking", default="mna", 
        help="Marking type.  Default: %(default)s")
    parser.add_argument("--model-description", default="", 
        help="New model description.  Default: %(default)s")
    parser.add_argument("--model-name", default="SlyPI VS Model", 
        help="New model name.  Default: %(default)s")
    parser.add_argument("--project-description", default="", 
        help="New project description.  Default: %(default)s")
    parser.add_argument("--project-name", required=True, 
        help="New project name.")

    return parser

# logging is just printing to the screen
def log (msg):
    print(msg)

# create VS model, arguments include the command line connection parameters
# and project/model information
def upload_model (arguments, csv_data, xcoords_data, ycoords_data, traj_data, links, log):

    # setup a connection to the Slycat Web Server.
    connection = slypi.connect(arguments)

    # create a new project to contain our model.
    pid = connection.find_or_create_project(arguments.project_name, arguments.project_description)

    # create the new, empty model.
    mid = connection.post_project_models(pid, "VS", 
        arguments.model_name, arguments.marking, arguments.model_description)

    # upload model table as movies.meta
    log('Uploading table data ...')
    connection.put_model_arrayset(mid, "movies.meta")
    connection.put_model_arrayset_array(mid, "movies.meta", 0, 
        csv_data['dimensions'], csv_data['attributes'])
    for index in range(len(csv_data['data'])):
        values = [np.asarray(csv_data['data'][index])]
        connection.put_model_arrayset_data(mid, "movies.meta", "0/%s/..." % index, values)

    # upload movie links as movies.links
    attributes = [dict(name="value", type="string")]
    dimensions = [dict(name="row", end=int(len(links)))]
    connection.put_model_arrayset(mid, "movies.links")
    connection.put_model_arrayset_array(mid, "movies.links", 0, dimensions, attributes)
    connection.put_model_arrayset_data(mid, "movies.links", "0/.../...", [np.asarray(links)])

    # upload x-coords
    log('Uploading coordinates ...')
    connection.put_model_arrayset(mid, "movies.xcoords")
    connection.put_model_arrayset_array(mid, "movies.xcoords", 0,
        xcoords_data['dimensions'], xcoords_data['attributes'])
    connection.put_model_arrayset_data(mid, "movies.xcoords", "0/.../...", [xcoords_data['data']])

    # upload y-coords
    connection.put_model_arrayset(mid, "movies.ycoords")
    connection.put_model_arrayset_array(mid, "movies.ycoords", 0,
        ycoords_data['dimensions'], ycoords_data['attributes'])
    connection.put_model_arrayset_data(mid, "movies.ycoords", "0/.../...", [ycoords_data['data']])

    # upload trajectories
    log('Uploading trajectories ...')
    connection.put_model_arrayset(mid, "movies.trajectories")
    connection.put_model_arrayset_array(mid, "movies.trajectories", 0,
        traj_data['dimensions'], traj_data['attributes'])
    connection.put_model_arrayset_data(mid, "movies.trajectories", "0/.../...", [traj_data['data']])

    # note that this model was loaded via push script
    connection.put_model_parameter(mid, "vs-loading-parms", ["Uploaded"])
    
    # Signal that we're done uploading data to the model.  This lets Slycat Web
    # Server know that it can start computation.
    connection.post_model_finish(mid)

    # Wait until the model is ready.
    connection.join_model(mid)

    return mid

# check arguments and create model, returns URL to model
def create_model (arguments, log):

    # check that input files exist
    for file in [arguments.csv_file, arguments.xcoords_file, 
                 arguments.ycoords_file, arguments.traj_file]:
        if not os.path.isfile(file):
            log("Input file " + file + " does not exist.")
            raise ValueError("Input file " + file + " does not exist.")
    
    # load csv file
    log('Reading .csv file ...')
    attributes, dimensions, data, csv_read_error = \
        slypi.pandas_util.parse_file(arguments.csv_file, file_name=True)

    # check for warnings/errors
    for i in range(len(csv_read_error)):
        if csv_read_error[i]["type"] == "warning":
            log("Warning: " + csv_read_error[i]["message"])
        else:
            log("Error: " + csv_read_error[i]["message"])
            raise ValueError(csv_read_error[i]["message"])

    # get column names/types
    column_names = [attribute["name"] for attribute in attributes]
    column_types = [attribute["type"] for attribute in attributes]

    # check that video column input is in headers
    if arguments.video_column not in column_names:
        log('Video column "' + arguments.video_column + '" not found in input file.')
        raise ValueError('Video column "' + arguments.video_column + '" not found in input file.')

    # get video index in csv
    video_index = column_names.index(arguments.video_column)

    # check that video column has strings
    if column_types[video_index] != "string":
        log('Video column "' + arguments.video_column + '" does not contain strings.')
        raise ValueError('Video column "' + arguments.video_column + '" does not contain strings.')

    # replace video URL hostnames, if requested
    if arguments.video_hostname is not None:

        # replace file://cluster with file://hostname
        modified = []
        for uri in data[video_index]:
            uri = urlparse.urlparse(uri)
            path = uri.path
            uri = "file://%s%s" % (arguments.video_hostname, path)
            modified.append(uri)
            data[video_index] = modified

    # strip prefix directories, if requested
    if arguments.strip is not None:

            # strip prefixes
            modified = []
            for uri in data[video_index]:
                uri = urlparse.urlparse(uri)
                hostname = uri.netloc
                path = '/'.join(uri.path.split('/')[arguments.strip + 1:])
                uri = "file://%s/%s" % (hostname, path)
                modified.append(uri)
                data[video_index] = modified

    # consolidate csv file
    csv_data = {'attributes': attributes, 'dimensions': dimensions, 'data': data}

    # finalize video links
    video_links = data[video_index]

    # load .xcoords file as a string
    log('Reading .xcoords file ...')
    with open(arguments.xcoords_file, 'r') as file:
        mat_file = file.read()

    # parse .xcoords file
    attributes, dimensions, data = vs_parse.parse_mat_file(mat_file)
    xcoords_data = {'attributes': attributes, 'dimensions': dimensions, 'data': data}

    # check that .xccords file has the same number of points as the csv file
    if dimensions[1]['end'] != csv_data['dimensions'][0]['end']:
        log('Different number of points in .xcoords file and .csv file.')
        raise ValueError('Different number of points in .xcoords file and .csv file.')
    
    # load .ycoords file as a string
    log('Reading .yxcoords file ...')
    with open(arguments.ycoords_file, 'r') as file:
        mat_file = file.read()

    # parse .ycoords file
    attributes, dimensions, data = vs_parse.parse_mat_file(mat_file)
    ycoords_data = {'attributes': attributes, 'dimensions': dimensions, 'data': data}
    
    # check that .yccords file has the same number of points as the csv file
    if dimensions[1]['end'] != csv_data['dimensions'][0]['end']:
        log('Different number of points in .xcoords file and .csv file.')
        raise ValueError('Different number of points in .xcoords file and .csv file.')
    
    # check that .xcoords and .ycoords files have the same number of time steps
    if dimensions[0]['end'] != xcoords_data['dimensions'][0]['end']:
        log('Different number of time steps in .xcoords file and .ycoords file.')
        raise ValueError('Different number of time steps in .xcoords file and .ycoords file.')

    # load .trajectories file
    log('Reading .trajectories file ...')
    with open(arguments.traj_file, 'r') as file:
        mat_file = file.read()

    # parse .trajectories file
    attributes, dimensions, data = vs_parse.parse_mat_file(mat_file)
    traj_data = {'attributes': attributes, 'dimensions': dimensions, 'data': data}

    # check number of trajectories
    if dimensions[0]['end'] != xcoords_data['dimensions'][1]['end']+1:
        log('Different number of trajectories than points in coordinates files.')
        raise ValueError('Different number of trajectories than points in coordinates files.')

    # check number of time steps in trajectories
    if dimensions[1]['end'] != xcoords_data['dimensions'][0]['end']:
        log('Different number of time steps in coordinate files and .trajectories file.')
        raise ValueError('Different number of time steps in coordinate files and .trajectories file.')

    # echo inputs to user
    log('Input .csv file: ' + arguments.csv_file)
    log('Input .xcoords file: ' + arguments.xcoords_file)
    log('Input .ycoords file: ' + arguments.ycoords_file)
    log('Input .trajectories file: ' + arguments.traj_file)
    log('Input video column name: ' + arguments.video_column)
    if arguments.video_hostname is not None:
        log('Video hostname: ' + str(arguments.video_hostname))
    if arguments.strip is not None:
        log('Stripped ' + str(arguments.strip) + ' prefixes from video column.')
    if arguments.strip is not None or arguments.video_hostname is not None:
        log('First new video link: ' + csv_data['data'][video_index][0])

    # report on number of points and time steps
    log('Found ' + str(csv_data['dimensions'][0]['end']) + ' data points and ' +
        str(xcoords_data['dimensions'][0]['end']) + ' time steps.')

    # upload model
    mid = upload_model (arguments, csv_data, xcoords_data, ycoords_data, traj_data, video_links, log)

    # supply direct link to model
    host = arguments.host
    if arguments.port:
        host = host + ":" + arguments.port
    url = host + "/models/" + mid
    log("Your new model is located at %s" % url)
    log('***** VideoSwarm Model Successfully Created *****')

    # return url
    return url

# main entry point
def main():

    # set up argument parser
    vs_parser = parser()  

    # get user arguments
    arguments = vs_parser.parse_args()

    # check arguments and create model
    url = create_model(arguments, log)

# command line version
if __name__ == "__main__":

    main()
