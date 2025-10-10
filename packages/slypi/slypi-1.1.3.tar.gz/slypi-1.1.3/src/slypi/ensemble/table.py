# Copyright (c) 2021 National Technology and Engineering Solutions of Sandia, LLC.  
# Under the terms of Contract DE-NA0003525 with National Technology and Engineering 
# Solutions of Sandia, LLC, the U.S. Government retains certain rights in this software.

# This script contains for code manipulating ensemble .csv files, including 
# creation from input decks, joining multiple tables, and expanding
# a table according to rules provided by plugin.

# S. Martin
# 3/23/2021

# standard library imports
import logging
import sys
import os

# 3rd party imports

# local imports
import slypi.ensemble as ensemble
from slypi.ensemble.utilities import Table as EnsembleTable
from slypi.ensemble.utilities import combine as ensemble_combine
from slypi.ensemble import ArgumentError

# set up argument parser
def init_parser():

    # define our own version of the slypi.ensemble parser
    description = "Creates/manipulates files from ensemble data set."
    parser = ensemble.ArgumentParser (description=description)

    # major csv options (must choose one)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--create', action="store_true", help="Create ensemble file "
                        "from simulation input decks.")
    group.add_argument("--join", nargs="+", help="List of slypi.ensemble files to join horizontally " +
                        "(first column is assumed to be index).")
    group.add_argument("--concat", nargs="+", help="List of slypi.ensemble files to join vertically " +
                        "(all column headers must be identical).")
    group.add_argument('--expand', help='Expand links in input file to include data in table.  Uses '
                        'plugin to expand links.')
    group.add_argument('--convert-uris', nargs=1, help="Converts columns from the given table to " +
                       "URIs, columns are specified using --uri-cols, and conversion is " +
                       "specified using --uri-root.")
    group.add_argument('--convert', nargs=1, help="Convert a slypi.ensemble table to " +
                        "a final Slycat table (remove source index).")

    # create/join csv from ensemble specifier and input files
    parser.add_argument("--ensemble", help="Directory or directories to include in ensemble, "
                        "specified using the Python like %%d[::] notation described above.")
    parser.add_argument("--input-files", help="Files per ensemble directory to use as input "
                        "for metadata, specified using %%d[::] notation.  Note that these "
                        "files will be pre-fixed by the ensemble directories.")
    parser.add_argument("--input-header", help='Name to assign input file header, e.g. "Input Deck"')

    # create specific option
    parser.add_argument("--input-format", help="Format for input files.  Optional, inferred "
                        "from file extension if not provided.")

    # join specific options
    parser.add_argument("--ignore-index", action="store_true", default=False, help="Ignore "
                        "index column when joining tables.")
    parser.add_argument("--no-index", action="store_true", default=False, help="No index present " +
                        "in input file, join rows without error checking (note that no output " +
                        "index is written, over-riding --no-output-index).")
    
    # URI conversion information
    parser.add_argument("--uri-cols", nargs="+", help="Columns with file points to convert to URIs.")
    parser.add_argument("--uri-root", help="Root name of URI used to transform file " +
                        "pointers in output file when joining files.  Note that this " +
                        "will only work if the file pointers have a common root.  All paths in " +
                        "this case will be converted to unix paths.")

    # concat specific options
    parser.add_argument("--add-origin-col", help="Add a column containing the data origin. " +
                        "This flag gives the new column name.")
    parser.add_argument("--origin-col-names", nargs="+", help="Names to use for origin column, " +
                        "one per file to concatenate (defaults to file names).")

    # expand specific options
    parser.add_argument("--expand-header", help="Table column to expand (either name or index).")

    # output file information
    parser.add_argument("--output-dir", help="Output directory for any files produced.")
    parser.add_argument("--output-file", help="File name of output file.")
    parser.add_argument("--output-no-index", action="store_false", default=True,
                        help="Do not output the index column.")
    parser.add_argument("--output-index-header", default=None, help="Index header name for output file " +
                        "(default is None).")
    parser.add_argument("--output-headers", nargs='*', help="Output only the given headers to " +
                        "the output file (defaults to all headers).")
    parser.add_argument("--exclude-output-headers", nargs='*', help="Exclude the given headers from " +
                        "the output file.")

    # over-write if file exists
    parser.add_argument("--over-write", action="store_true", help="Over-write output "
                        "file if already present.")

    return parser

# check arguments for create option
def check_create_arguments(ensemble_spec=None, input_files=None, input_header=None):

    # make sure the ensemble argument is present
    if ensemble_spec is None:
        raise ArgumentError("Ensemble directories are required.  Please use --ensemble on " +
                            "command line, or ensemble_spec= in API and try again.")
    
    # make sure the input argument is present
    if input_files is None:
        raise ArgumentError("Input files are required.  Please use --input-files on command line, " +
                  "or input_files= in API and try again.")

    # make sure the input file header is present
    if input_header is None:
        raise ArgumentError("Input header is required.  Please use --input-header on command line, " +
                  "or input_header= in API and try again.")

# check arguments for join
def check_join_arguments(join, ensemble_spec=None, input_files=None, input_header=None,
                         ignore_index=None, no_index=None, output_no_index=None):
    
    # if only one csv file, must specify ensemble parameters
    if len(join) == 1:

        if ensemble_spec is None or \
           input_files is None or \
           input_header is None:

            raise ArgumentError("If only using one input file, you must specify --ensemble " +
                                "arguments on the command line, or ensemble_spec= in the API.  " +
                                "Please use --ensemble, --input-files, --input-header and try again. ")
    
    # if ignoring index column you can't output index
    if ignore_index:
        if output_no_index:
            raise ArgumentError("If --ignore-index is set, you must also set --output-no-index (" +
                                "or equivalent in API).")

    # if using no-index, you can't use --ignore-index
    if no_index:
        if ignore_index:
            raise ArgumentError("You can't use --ignore-index (on the command line, " +
                                "or ignore_index= in the API) with --no-index.")
# check arguments for concat
def check_concat_arguments(concat, origin_col_names=None, add_origin_col=None):

    # if origin names provided, check that there are same number of files
    if origin_col_names is not None:
        
        # check that user request an origin column
        if add_origin_col is None:
            raise ArgumentError("Must use --add-origin-col on command line, or " +
                                "add_origin_col= in API if providing origin column names.")

        # check for matching origin names and files to concatenate
        if len(origin_col_names) != len(concat):
            raise ArgumentError("Number of --origin-col-names on command line, or " +
                                "origin_col_names= in API does not match number of files " +
                                "to concatenate.")

# check argumetns for expand
def check_expand_arguments(expand_header=None):

    # check that column to expand is provided
    if expand_header is None:
        raise ArgumentError("Please specify --expand-header on command line, or expand_header= " +
                            "in API and try again.")

# check arguments for convert
def check_convert_arguments():

    pass

# check convert-uri-cols arguments
def check_convert_uri_arguments(uri_cols=None, uri_root=None):

    # check that uri-root and convert-cols are both present
    if not (uri_cols and uri_root):
       raise ArgumentError("Must specify both --uri-cols and --uri-root on " +
                           "command line, or uri_cols= and uri_root= in API.")

# check arguments, API version
def check_API_arguments(output_dir=None, output_file=None, create=None,
                        join=None, concat=None, expand=None, convert=None,
                        convert_uris=None, ensemble_spec=None, input_files=None,
                        input_header=None, ignore_index=None, no_index=None, 
                        output_no_index=None, origin_col_names=None, add_origin_col=None, 
                        expand_header=None, uri_cols=None, uri_root=None):
    
    # make sure the output directory is present
    if output_dir is None:
        raise ArgumentError("Output directory must be specified.  Please use --output-dir on " +
                            "command line, or output_dir= in API and try again.")

    # make sure the output argument is present
    if output_file is None:
        raise ArgumentError("Name of output file is required.  Please use --output-file on " +
                            "command line, or output_file= in API and try again.")
    
    # check create options
    if create:
        check_create_arguments(ensemble_spec=ensemble_spec, input_files=input_files, 
                               input_header=input_header)
    
    # check join options
    if join is not None:
        check_join_arguments(join, ensemble_spec=ensemble_spec, input_files=input_files,
                            input_header=input_header, ignore_index=ignore_index,
                            no_index=no_index, output_no_index=output_no_index)
        
    # check concat option
    if concat is not None:
        check_concat_arguments(concat, origin_col_names=origin_col_names, 
                               add_origin_col=add_origin_col)

    # check expand option
    if expand is not None:
        check_expand_arguments(expand_header=expand_header)

    # check convert option
    if convert is not None:
        check_convert_arguments()

    # check convert-uri option
    if convert_uris is not None:
        check_convert_uri_arguments(uri_cols=uri_cols, uri_root=uri_root)

# check command arguments, command line version
def check_CLI_arguments(args):

    # pass through to API check
    check_API_arguments(output_dir=args.output_dir, output_file=args.output_file,
                        create=args.create, join=args.join, concat=args.concat, expand=args.expand,
                        convert=args.convert, convert_uris=args.convert_uris,
                        ensemble_spec=args.ensemble, input_files=args.input_files,
                        input_header=args.input_header, ignore_index=args.ignore_index,
                        no_index=args.no_index, output_no_index=args.output_no_index, 
                        origin_col_names=args.origin_col_names, add_origin_col=args.add_origin_col, 
                        expand_header=args.expand_header, uri_cols=args.uri_cols, 
                        uri_root=args.uri_root)
    
# create .csv file
def create_csv(args, log, plugin):

    # create ensemble table
    ensemble_table = EnsembleTable(log, ensemble_spec=args.ensemble, 
        file_spec=args.input_files, header=args.input_header)
    ensemble_dirs = ensemble_table.get_col(args.input_header)

    # quit if no directories found
    num_ensemble_dirs = len(ensemble_dirs)
    if num_ensemble_dirs == 0:
        log.error("No ensemble directories found.  " +
                  "Please identify existing directories and try again.")
        sys.exit(1)
    else:
        log.info("Found %d ensemble directory(ies)." % num_ensemble_dirs)
        
    # go through each directory and read input files
    input_data = []
    for i in range(num_ensemble_dirs):

        # find files in directory
        files_to_read = ensemble_table.files(ensemble_dirs[i])
        log.info("Found %d file(s) in ensemble directory %s." % 
            (len(files_to_read), ensemble_dirs[i]))
        
        # print warning if no files found for input
        if files_to_read == []:
            log.error("No files to read, please provide existing files for input.")
            sys.exit(1)

        # read input files
        input_data.append(plugin.read_input_deck(files_to_read, file_type=args.input_format))
    
    # combine all input data headers
    input_headers = []
    for i in range(num_ensemble_dirs):
        if input_data[i]:
            for key in input_data[i].keys():
                if key not in input_headers:
                    input_headers.append(key)
    
    # create table using input data headers
    for header in input_headers:

        # create column for a given header
        input_col = []
        for i in range(num_ensemble_dirs):
            if header in input_data[i]:
                input_col.append(input_data[i][header])
            else:

                # use empty strings if no data
                input_col.append('')
        
        # check if we should add this column
        if args.output_headers is not None:
            if len(args.output_headers) > 0:
                if header not in args.output_headers:
                    continue

        # check if we should exclude this column
        if args.exclude_output_headers is not None:
            if len(args.output_headers) > 0:
                if header in args.exclude_output_headers:
                    continue

        # add column to table
        ensemble_table.add_col(input_col, header)
    
    # write out table
    csv_out = os.path.join(args.output_dir, args.output_file)
    ensemble_table.to_csv(csv_out, index=args.output_no_index, 
                          index_label=args.output_index_header, 
                          cols=args.output_headers,
                          exc_cols=args.exclude_output_headers)

# join csv files using API, not including uri convert
def join_csv(join_tables, ensemble_spec=None, input_files=None, input_header=None,
             ignore_index=False, no_index=False, output_dir=None, output_file=None, 
             output_no_index=None, output_index_header=None, output_headers=None,
             exclude_output_headers=None, log=None):
    """
    Joins files containing tables, either slypi intermediate format 
    (with an index column), or standard CSV tables.  The arguments are all optional,
    supporting different ways to combine tables.  Further descriptions of the
    arguments and their interactions can be found using table.py --help 
    (under the --join option).

    Args:
        join_tables (list): file names of tables to join
        ensemble_spec (string): directory or directories to include in ensemble.
        input_files (string): files per ensemble directory to use as input.
        input_header (string): name to assign input file header in table
        ignore_index (bool): ignore index (first) column when joining tables
        no_index (bool): join tables without using index (first) column
        output_dir (string): directory to output combined table
        output_file (string): output file name (extension agnostic)
        output_no_index (bool): do not output index column (if not using ignore_index)
        output_index_header (string): index header name
        output_headers (list): list of strings of headers to output
        exclude_output_headers (list): list of strings of headers to exclude
        log (object): logger function, if not supplied will output to screen

    Returns:
        Writes a combined table to the requested file.

    Note: Does not check for over-writes or existence of directories.

    :Example:

    .. code-block:: python

        from slypi.ensemble.table import join_csv

        join_csv (join_tables=[os.path.join(test_data_dir, 'metadata.csv'), 
                               os.path.join(convert_dir, 'end-state.csv'),
                               os.path.join(convert_dir, 'movies.csv')],
                  output_headers=['mobility_coefficients-1', 'mobility_coefficients-2', 
                                  'composition_distribution-1', 'End State', 'Movie'],
                  output_dir=output_dir, output_file='ps-no-index-api.csv',
                  no_index=True)
    """

    # double check arguments, in case user is coming directly through API
    check_API_arguments(join=join_tables, ensemble_spec=ensemble_spec, input_files=input_files,
                        input_header=input_header, ignore_index=ignore_index, no_index=no_index,
                        output_dir=output_dir, output_file=output_file,
                        output_no_index=output_no_index)

    # start up log (to screen), if not given
    if log is None:
        ensemble.init_logger()
        log = logging.getLogger("ensemble.table.join_csv")
        log.debug("Started join_csv.")
    
    # if no-index is used, we will also avoid writing an index
    if no_index:
        output_no_index=False

    # create ensemble table for each .csv file
    ensemble_tables = []
    for csv_file in join_tables:
        ensemble_tables.append(EnsembleTable(log, csv_file=csv_file, no_index=no_index))

    # create extra column if user is using --ensemble
    if ensemble_spec is not None:
        ensemble_tables.append(EnsembleTable(log, ensemble_spec=ensemble_spec, 
            file_spec=input_files, header=input_header))
    

    # combine tables
    combined_table = ensemble_combine(log, ensemble_tables, 
                                      ignore_index=ignore_index, no_index=no_index)
    
    # write out combined table
    csv_out = os.path.join(output_dir, output_file)
    combined_table.to_csv(csv_out, index=output_no_index, 
                          index_label=output_index_header,
                          cols=output_headers, 
                          exc_cols=exclude_output_headers)

# join csv files
def join_csv_CLI(args, log):
    
    # pass through to API version
    join_csv(args.join, ensemble_spec=args.ensemble, input_files=args.input_files,
             input_header=args.input_header, ignore_index=args.ignore_index,
             no_index=args.no_index, output_dir=args.output_dir, output_file=args.output_file, 
             output_no_index=args.output_no_index, output_index_header=args.output_index_header,
             output_headers=args.output_headers, exclude_output_headers=args.exclude_output_headers,
             log=log)

# concat csv files
def concat_csv(args, log):

    # create ensemble table for each .csv file
    ensemble_tables = []
    for csv_file in args.concat:
        ensemble_tables.append(EnsembleTable(log, csv_file=csv_file))

    # check that column headers are identical
    headers = list(ensemble_tables[0].table)
    headers_identical = True
    for table in ensemble_tables:
        if list(table.table) != headers:
            headers_identical = False

    # quit if headers are not identical
    if not headers_identical:
        log.error("Table headers are not identical, cannot concatenate tables.")
        sys.exit(1)

    # concatenate tables
    concat_table = ensemble.concat(log, ensemble_tables)

    # create origin column, if requested
    origin_col = []
    for i in range(len(ensemble_tables)):

        # use given origin names if provided
        if args.origin_col_names is not None:
            origin_col += [args.origin_col_names[i]] * ensemble_tables[i].table.shape[0]

        # otherwise, use file names
        else:
            origin_col += [args.concat[i]] * ensemble_tables[i].table.shape[0]

    # add origin column to concatenated table
    concat_table.add_col(origin_col, args.add_origin_col)

    # write out new table
    csv_out = os.path.join(args.output_dir, args.output_file)
    concat_table.to_csv(csv_out, index=args.output_no_index, 
                          index_label=args.output_index_header,
                          cols=args.output_headers,
                          exc_cols=args.exclude_output_headers)
    
# expand csv file
def expand_csv(args, log, plugin):

    # read main table
    table_to_expand = EnsembleTable(log, csv_file=args.expand)

    # check if column exists
    col_to_expand = table_to_expand.get_col(args.expand_header)
    
    # get files to expand, count files per specifier
    files_to_expand = []
    missing_files = False
    multiple_files = False
    for file_spec in col_to_expand:

        # get files for specifier
        expand_files = table_to_expand.files(file_spec)

        # do the references files exist?
        if len(expand_files) == 0:
            missing_files = True

        # do the references point to multiple files?
        if len(expand_files) > 1:
            multiple_files = True

        # if only one file, make into a string instead of a list
        if len(expand_files) == 1:
            expand_files = expand_files[0]
        
        files_to_expand.append(expand_files)
    
    # if there are missing files, error out
    if missing_files:
        log.error("Column to expand does not reference existing files.")
        sys.exit(1)

    # for multiple files, expand columns but do not read files
    if multiple_files:

        # explode table
        exploded_table = ensemble.explode(log, table_to_expand, 
            args.expand_header, files_to_expand)

        # write out table
        csv_out = os.path.join(args.output_dir, args.output_file)
        exploded_table.to_csv(csv_out, index=args.output_no_index, 
                              index_label=args.output_index_header,
                              cols=args.output_headers,
                              exc_cols=args.exclude_output_headers)

    # otherwise use plugin to read files and expand
    # (plugin can also write additional files, if desired)
    else:

        plugin.expand(table_to_expand, args.expand_header, files_to_expand, 
            output_dir=args.output_dir, csv_out=args.output_file, csv_no_index=args.output_no_index, 
            csv_index_header=args.output_index_header, csv_headers=args.output_headers)

# convert uri columns, API
def convert_uris(table_csv, uri_cols=None, uri_root=None, 
                 output_dir=None, output_file=None, 
                 output_headers=None, exclude_output_headers=None, 
                 log=None):
    """
    Converts file pointers in a table to URIs given a URI root name.

    Args:
        table_csv (string): file names of table to use
        uri_cols (list): list of header names to convert in table
        uri_root (string): uri root path for conversion
        output_dir (string): directory to output combined table
        output_file (string): output file name (extension agnostic)
        output_headers (list): list of strings of headers to output
        exclude_output_headers (list): list of strings of headers to exclude
        log (object): logger function, if none supplied will output to screen

    Returns:
        Writes a new table with the URI conversions.

    Note: Does not check for over-writes or existence of directories.
    
    :Example:

    .. code-block:: python

        from slypi.ensemble.table import convert_uris

        convert_uris(os.path.join(output_dir, 'ps-no-index.sly'),
                    uri_cols=['End State', 'Movie'],
                    uri_root=uri_root_out,
                    output_dir=output_dir, 
                    output_file='ps-uri-convert-api.csv')
    """

    # double check arguments, in case calling from command line
    check_API_arguments(convert_uris=table_csv, uri_cols=uri_cols, uri_root=uri_root,
                        output_dir=output_dir, output_file=output_file)

    # start up log (to screen), if not given
    if log is None:
        ensemble.init_logger()
        log = logging.getLogger("ensemble.table.convert_uris")
        log.debug("Started convert_uris.")

    # read main table
    table_to_convert = EnsembleTable(log, csv_file=table_csv, no_index=True)

    # convert uris
    table_to_convert.convert_cols(uri_cols, uri_root)

    # write out converted table
    csv_out = os.path.join(output_dir, output_file)
    table_to_convert.to_csv(csv_out, index=False,
                            cols=output_headers, 
                            exc_cols=exclude_output_headers)
    
# convert uri columns in a table, command line
def convert_uris_CLI(args, log):

    # pass through to API version
    convert_uris(args.convert_uris[0], uri_cols=args.uri_cols, 
                 uri_root=args.uri_root, output_dir=args.output_dir,
                 output_file=args.output_file, output_headers=args.output_headers,
                 exclude_output_headers=args.exclude_output_headers, log=log)

# convert slypi.ensemble intermediate csv to normal csv
def convert_csv(args, log, plugin):

    # create ensemble table for each .csv file
    table_to_convert = EnsembleTable(log, csv_file=args.convert[0])

    # save to csv without index column
    table_to_convert.to_csv(args.output_file, args.output_dir, index=False)

# creates a .csv file for remaining ensemble tools to use as input
# call from Python using arg_list
def table(arg_list=None):

    # initialize parser 
    parser = init_parser()

    # parse arguments
    if arg_list is not None:

        # parse in case called with arg_list
        args, arg_list = parser.parse_args(arg_list)

    else:

        # command line parser
        args, arg_list = parser.parse_args()

    # start logger
    ensemble.init_logger(log_file=args.log_file, log_level=args.log_level)
    log = logging.getLogger("ensemble.table")
    log.debug("Started table.")

    # check arguments
    check_CLI_arguments(args)
    
    # import and initialize plugin
    plugin, unknown_args = ensemble.plugin(args.plugin, arg_list)

    # check for un-recognized arguments
    if len(unknown_args) > 0:
        log.error("Unrecognized arguments: %s.  Please try again." % str(unknown_args))
        sys.exit(1)
    
    # check if output directory exists
    if not os.path.exists(args.output_dir):
        log.warning("Output directory does not exist -- creating directory: " + 
                    args.output_dir)
        os.makedirs(args.output_dir)

    # check if output file exists
    csv_out = os.path.join(args.output_dir, args.output_file)
    if os.path.isfile(csv_out):
        if not args.over_write:
            log.error("Output file already exists, use --over-write if you " +
                "want to over-write file.")
            sys.exit(1)

    # create csv
    if args.create:
        create_csv(args, log, plugin)
    
    # join csv
    elif args.join is not None:
        join_csv_CLI(args, log)

    # concatenate csv
    elif args.concat is not None:
        concat_csv(args, log)

    # expand csv
    elif args.expand is not None:
        expand_csv(args, log, plugin)

    # convert uri columns
    elif args.convert_uris is not None:
        convert_uris_CLI(args, log)

    # convert to final version csv
    elif args.convert is not None:
        convert_csv(args, log, plugin)

# entry point for command line call
if __name__ == "__main__":
    table()
