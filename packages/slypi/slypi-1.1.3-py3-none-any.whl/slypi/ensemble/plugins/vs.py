# Copyright (c) 2021 National Technology and Engineering Solutions of Sandia, LLC.  
# Under the terms of Contract DE-NA0003525 with National Technology and Engineering 
# Solutions of Sandia, LLC, the U.S. Government retains certain rights in this software.

# This is a plugin that provides support for converting time-aligned
# dimension reduction to VideoSwarm format.  To be called using
# the --expand option from table.py.  When calling from table.py use
# a dummy value for --csv-out.

# S. Martin
# 3/23/2021


# standard library imports
import csv
import os
from pathlib import Path

# 3rd party imports
import numpy as np

# image manipulation
import imageio
from PIL import Image

# auto-correlation
try:
    import pymks
except ImportError:
    pymks = None

# local imports
import slypi.ensemble as ensemble


# functions for specific operations
# class must be named Plugin
class Plugin(ensemble.PluginTemplate):

    # initialize command line argument parser
    def __init__(self):

        # describe plugin
        description = "The videoswarm plugin provides the ability to convert " + \
            "time-aligned dimension reduction algorithms to Slycat VideoSwarm " + \
            "format."

        # set up parser
        super().__init__(description=description)

    # add any extra command line arguments
    def add_args(self):

        self.parser.add_argument("--remove-expand-col", action="store_true", default=False,
            help="Remove the expanded column when writing out videoswarm files.")
        
        # arguments to specify time scale
        self.parser.add_argument("--video-fps", type=float, default=25,
            help="Video frames per second, must be > 0, defaults to 25.")

        self.parser.add_argument("--binary", action="store_true", help="Converts field "
            "variable to binary by clipping anything less than 0 to 0 and anyting "
            "greater than 0 to 1.")

        self.parser.add_argument("--auto-correlate", action="store_true", help="Performs "
            "auto-correlation as a pre-processing for dimension reduction (note this option "
            "requires the --binary flag to be used).")

        self.parser.add_argument("--scale", action="store_true", help="Scale values to [-0.5,0.5].")

    # check arguments, error if incorrect input
    def check_args(self, args):

        if args.video_fps is not None:
            if args.video_fps <= 0:
                self.log.error("Video frames per second must be > 0.")
                raise ValueError("video frames per second must be > 0 (see " +
                                 "slypi.ensemble.plugins.vs --help).")

        # check that binary is active if auto-correlate is selected
        if args.auto_correlate:

            # check if pymks is available
            if not pymks:
                self.log.error("The pymks module has not been installed, " + 
                                 "cannot perform auto-correlation. " +
                                 "Use pip install slypi[auto].")
                raise ValueError("The pymks module has not been installed, " + 
                                 "cannot perform auto-correlation. " +
                                 "Use pip install slypi[auto].")
            
            # check that binary flag is also present
            if not args.binary:
                self.log.error("Auto-correlation requires binary input, please use --binary " +
                               "and try again.")
                raise ValueError("auto-correlation requires binary flag (see " +
                                 "slypi.ensemble.plugins.vs --help.")

    # initialize any local variables from command line arguments
    def init(self, args):

        # save args for later use
        self.args = args

    # over-ride file read, accept .jpg or .rd.npy files
    def read_file(self, file_in, file_type=None):

        # is it an rd.npy file?
        if file_in.endswith('.rd.npy'):

            # read npy file
            try:
                data = np.load(file_in)
            except ValueError:
                self.log.error("Could not read " + file_in + " as a .npy file.")
                raise ValueError("could not read " + file_in + " as a .npy file.")

        # is it .npz?
        elif file_in.endswith('.npz'):

            # read npz file
            try:
                data = np.load(file_in)
                data = data['arr_0']
            except ValueError:
                self.log.error("Could not read " + file_in + " as a .npy file.")
                raise ValueError("could not read " + file_in + " as a .npy file.")

        elif file_in.endswith('.jpg'):

            # read .jpg file and reshape into vector
            data = imageio.imread(file_in)

        elif file_in.endswith('.png'):

            try:
                img = Image.open(file_in)
                data = np.array(img)
            except ValueError:
                self.log.error("Could not read " + file_in + "as a .png file.")
                raise ValueError("Could not read " + file_in + " as a .png file.")

        else:
            self.log.error("The videoswarm plugin accepts only .png, .jpg or .rd.npy files.")
            raise TypeError("videoswarm plugin accepts only .png, .jpg or .rd.npy files.")
        
        self.log.info("Read file " + file_in + ".")

        return data

    # write out .npy format
    def write_file(self, data, file_out, file_type=None):

        # infer file type, if not provided
        if file_type is None:
            if file_out.endswith('.npy'):
                file_type = 'npy'

        # check for npy file output (data is matrix format)
        if file_type == 'npy':
            np.save(file_out, data)
            
        else:

            # default to meshio output
            super().write_file(data, file_out, file_type=file_type)

    # convert from 3 channel image to numpy 
    def _convert_img (self, data):

        if len(data.shape) == 3:

            # convert to black and white image then numpy array
            img = Image.fromarray(data).convert('L')
            data = np.array(img)

        return data

    # scale values between [0,1]
    def _scale(self, data):

        min = data.min()
        max = data.max()

        data = (data - min)/(max - min) - 0.5

        return data

    # make binary version of matrix
    def _binary(self, data):

        data[data < 0] = 0
        data[data > 0] = 1

        return data

    # perform pre-processing on jpg data (n,n,3)
    def preprocess (self, data, flatten=True):
        
        # if image, convert to matrix using jet map
        data = self._convert_img(data)

        # scale data, if requested
        if self.args.scale:
            data = self._scale(data)

        # convert to binary, if requested
        if self.args.binary:
            data = self._binary(data)

        # do auto-correlation, if requested
        if self.args.auto_correlate:
            
            # set up hat basis for pymks
            p_basis = pymks.bases.PrimitiveBasis(n_states=2)

            # check if this data is 2D
            if len(data.shape) == 2:

                # keep rows and columns
                num_rows, num_cols = data.shape

                # add extra dimension for 2D
                data = np.expand_dims(data, axis=0)
            
            # do auto-correlation with pymks (use binary data)
            space_stats = pymks.stats.correlate(data, p_basis, 
                                                periodic_axes=(0, 1), 
                                                correlations=[(0, 0)])

            # re-shape each time step into vector
            space_stats_vec = np.reshape(space_stats,[space_stats.shape[0],
                                         space_stats.shape[1] * space_stats.shape[2],
                                         space_stats.shape[-1]])
            data_vec = np.squeeze(space_stats_vec)

            # re-shape to 2D if we don't want flattened data
            if not flatten:

                data_vec = np.reshape(data_vec, (num_rows, num_cols))
        
        else:

            # default behaviour is to reshape matrix into one simulation per row
            if flatten:

                if len(data.shape) == 2:
                    data_vec = np.reshape(data, [data.shape[0] * data.shape[1]])

                else:
                    data_vec = np.reshape(data, [data.shape[0], 
                                        data.shape[1] * data.shape[2]])

            # otherwise, keep as matrix
            else:
                data_vec = data
                
        # make sure there are no singleton dimensions
        data_vec = np.squeeze(data_vec)
        
        return data_vec

    # over-riding expand to generate videoswarm input files
    def expand(self, table, header, file_list, **kwargs):
        """
        Outputs the videoswarm input files from a set of .rd.npy files.

        Optional arguments include (see also table.py options):
            output_dir -- output diredtory
            csv_out -- csv file to output
            csv_no_index -- do not include pandas index in movies.csv
            csv_index_header -- use this header name for index column
            csv_headers -- output only these columns to movies.csv

        Other arguments passed via kwargs are ignored.
        """

        # decode extra arguments
        output_dir = kwargs.get("output_dir", "")
        csv_no_index = kwargs.get("csv_no_index", False)
        csv_out = kwargs.get("csv_out", None)
        csv_index_header = kwargs.get("csv_index_header", None)
        csv_headers = kwargs.get("csv_headers", None)

        # videoswarm input files are of the form:

        # movies.csv -- .csv metadata file with column containing file links
        # movies.trajectories -- .csv file containing one row of time
        #                         points followed by x-coordinates over simulations
        # movies.xcoords -- .csv file containing one column per
        #                    simulation of x-coordinates over time
        # movies.ycoords -- .csv file containing one column per 
        #                    simulation of y-coordinates over time

        # coordinates are scaled to lie in [0,1]^2

        # file_list is in order of table, expecting .rd.npy files
        xcoords = []
        ycoords = []
        for file_name in file_list:
            
            # read file
            data = self.read_file(file_name)

            # check that data is at least two dimensional
            if data.shape[1] < 2:
                self.log.error("Data in " + file_name + " contains less than " +
                               "two dimensions.")
                raise ValueError("reduced dimension data must have at least two dimensions.")
            
            # collate data (each .rd.npy file contains time steps 
            # per simulation as rows and reduced data as columns)
            xcoords.append(data[:,0])
            ycoords.append(data[:,1])

        # transpose xcoords, ycoords 
        xcoords = np.array(xcoords).transpose()
        ycoords = np.array(ycoords).transpose()

        # scale coords to lie in [0,1]^2
        xcoords, ycoords = self._scale_coords(xcoords, ycoords)

        # write out videoswarm files
        self._output_VS_files(table, header, xcoords, ycoords, 
            output_dir, csv_out, csv_no_index, csv_index_header, csv_headers)

    # scale coordinates for VideoSwarm interface
    def _scale_coords (self, xcoords, ycoords):

        # get range for x
        min_x = np.amin(xcoords)
        max_x = np.amax(xcoords)

        # get range for y
        min_y = np.amin(ycoords)
        max_y = np.amax(ycoords)

        # scale coordinates to be in [0,1]^2
        # if constant assign value of 1/2
        xcoords = (xcoords - min_x)
        if max_x > min_x:
            xcoords = xcoords / (max_x - min_x)
        else:
            xcoords = xcoords + 0.5

        ycoords = (ycoords - min_y)
        if max_y > min_y:
            ycoords = ycoords / (max_y - min_y)
        else:
            ycoords = ycoords + 0.5

        return xcoords, ycoords

    # write out VideoSwarm files
    def _output_VS_files(self, meta_data, expand_header, xcoords, ycoords, 
        output_dir, csv_out, csv_no_index, csv_index_header, csv_headers):

        # remove expanded column, if requested
        if self.args.remove_expand_col:
            meta_data.table = meta_data.table.drop(expand_header, axis=1)

        # write out movies.csv file
        movies_out = os.path.join(output_dir, csv_out)
        meta_data.to_csv(movies_out, index=csv_no_index, 
            index_label=csv_index_header, cols=csv_headers)

        # use samae root as csv_out
        csv_root = os.path.splitext(os.path.basename(csv_out))[0]

        # write out movies.xcoords file (use only float precision)
        xcoords_file_name = Path(os.path.join(output_dir, csv_root + '.xcoords')).as_posix()
        with open(xcoords_file_name, 'w', newline='', encoding='utf-8') as xcoords_file:
            csv_xcoords_file = csv.writer(xcoords_file)
            for i in xcoords.tolist():
                csv_xcoords_file.writerow(['{:f}'.format(x) for x in i])
        self.log.info("Saved file " + xcoords_file_name + ".")

        # write out movies.xcoords file (use only float precision)
        ycoords_file_name = Path(os.path.join(output_dir, csv_root + '.ycoords')).as_posix()
        with open(ycoords_file_name, 'w', newline='', encoding='utf-8') as ycoords_file:
            csv_ycoords_file = csv.writer(ycoords_file)
            for i in ycoords.tolist():
                csv_ycoords_file.writerow(['{:f}'.format(y) for y in i])
        self.log.info("Saved file " + ycoords_file_name + ".")

        # add time to first row of xcoords to make trajectories
        num_frames, num_movies = xcoords.shape
        vid_duration = num_frames / float(self.args.video_fps)
        time_row = np.linspace(0, vid_duration, num=num_frames)
        traj = np.ones((num_movies + 1, num_frames))
        traj[0, :] = time_row
        traj[1:, :] = xcoords.transpose()

        # write out movies.trajectories
        traj_file_name = Path(os.path.join(output_dir, csv_root + '.trajectories')).as_posix()
        with open(traj_file_name, 'w', newline='', encoding='utf-8') as traj_file:
            csv_traj_file = csv.writer(traj_file)
            for i in traj.tolist():
                csv_traj_file.writerow(['{:f}'.format(t) for t in i])

        self.log.info("Saved file " + traj_file_name + ".")

# if called from the command line display plugin specific command line arguments
if __name__ == "__main__":

    videoswarm = Plugin()
    videoswarm.parser.parse_args()