# Copyright (c) 2021 National Technology and Engineering Solutions of Sandia, LLC.  
# Under the terms of Contract DE-NA0003525 with National Technology and Engineering 
# Solutions of Sandia, LLC, the U.S. Government retains certain rights in this software.

# This is a plugin that provides support for converting dimension
# reduction results to Parameter Space format.  In particular
# it is to be called using the --expand option from table.py.

# S. Martin
# 4/21/2021


# standard library imports
import argparse
import csv
import os

# 3rd party imports
import numpy as np
import pandas as pd
from PIL import Image

# auto-correlation
try:
    import pymks
except ImportError:
    pymks = None

# local imports
from slypi.ensemble import utilities
import slypi


# functions for specific operations
# class must be named Plugin
class Plugin(slypi.ensemble.PluginTemplate):

    # initialize command line argument parser
    def __init__(self):

        # describe plugin
        description = "The parameter space plugin provides the ability to convert " + \
            "dimension reduction results to Slycat Parameter Space " + \
            "format."

        # set up parser
        super().__init__(description=description)

    # add any extra command line arguments
    def add_args(self):

        self.parser.add_argument("--num-coords", type=int, default=2, help="Number of coordinates " +
            "from input files to include in .csv output file.")

        self.parser.add_argument("--remove-expand-col", action="store_true", default=False,
            help="Remove the expanded column when writing out parameter space file.")

        self.parser.add_argument("--include-original-index", action="store_true", default=False,
            help="Add original (repeated) index to expanded output .csv file.")

        self.parser.add_argument("--binary", action="store_true", help="Converts field "
            "variable to binary by clipping anything less than 0 to 0 and anyting "
            "greater than 0 to 1.")

        self.parser.add_argument("--auto-correlate", action="store_true", help="Performs "
            "auto-correlation as a pre-processing for dimension reduction (note this option "
            "requires the --binary flag to be used).")

        self.parser.add_argument("--scale", action="store_true", help="Scale values to [-0.5,0.5].")

    # check arguments, error if incorrect input
    def check_args(self, args):

        if args.num_coords is not None:
            if args.num_coords < 2:
                self.log.error("Number of coordinates to output must be >= 2.")
                raise ValueError("number of coordinates to output must be >= 2 (see " +
                                 "slypi.ensemble.plugins.parameter_space --help).")

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

            # check that binary option is enabled
            if not args.binary:
                self.log.error("Auto-correlation requires binary input, please use --binary " +
                               "and try again.")
                raise ValueError("auto-correlation requires binary flag (see " +
                                 "slypi.ensemble.plugins.vs --help.")
            

    # initialize any local variables from command line arguments
    def init(self, args):

        # save args for later use
        self.args = args

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

    # over-ride file read, accept .jpg or .rd.npy files
    def read_file(self, file_in, file_type=None):

        # is it an npy file?
        if file_in.endswith('npy'):

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
            
        elif file_in.endswith('.png'):

            try:
                img = Image.open(file_in)
                data = np.array(img)
            except ValueError:
                self.log.error("Could not read " + file_in + "as a .png file.")
                raise ValueError("Could not read " + file_in + " as a .png file.")
            
        else:
            self.log.error("The parameter space plugin accepts only .png, .rd.npy or .npz files.")
            raise TypeError("parameter space plugin accepts only .png, .rd.npy or .npz files.")
        
        self.log.info("Read file " + file_in + ".")
        
        return data

    # write out .npy format
    def write_file(self, data, file_out, file_type=None):

        # infer file type, if not provided
        if file_type is None:
            if file_out.endswith('.npy'):
                file_type = 'npy'
            elif file_out.endswith('.npz'):
                file_type = 'npz'

        # check for npy file output (data is matrix format)
        if file_type == 'npy':
            np.save(file_out, data)
        
        elif file_type == 'npz':
            np.savez(file_out, data)

        else:

            # default to meshio output
            super().write_file(data, file_out, file_type=file_type)
    
    # over-riding expand to generate videoswarm input files
    def expand(self, table, header, file_list, **kwargs):
        """
        Outputs the Parameter Space input file from a set of .rd.npy files.

        Optional arguments include (see also table.py options):
            output_dir -- output directory
            csv_out -- file name for csv output
            csv_no_index -- do not include pandas index in movies.csv
            csv_index_header -- use this header name for index column
            csv_headers -- output only these columns to movies.csv

        Other arguments passed via kwargs are ignored.
        """
        
        # decode extra arguments
        output_dir = kwargs.get("output_dir")
        csv_out = kwargs.get("csv_out")
        csv_no_index = kwargs.get("csv_no_index", False)
        csv_index_header = kwargs.get("csv_index_header", None)
        csv_headers = kwargs.get("csv_headers", None)

        # put csv_out in output directory
        csv_out = os.path.join(output_dir, csv_out)

        # file_list is in order of table, expecting .rd.npy files
        reduced_coords = []
        for file_name in file_list:
            
            # read file
            data = self.read_file(file_name)

            # check that data is at least two dimensional
            if data.shape[1] < 2:
                self.log.error("Data in " + file_name + " contains less than " +
                               "two dimensions.")
                raise ValueError("reduced dimension data must have at least two dimensions.")
            
            # check that number of dimension is not too large
            if data.shape[1] < self.args.num_coords:
                self.log.warning("Data in " + file_name + " contains less than " +
                                 "requested number of dimensions to output -- defaulting " +
                                 "to " + str(data.shape[1]) + " dimensions.")
                self.args.num_coords = data.shape[1]

            # collate data (each .rd.npy file contains time steps 
            # per simulation as rows and reduced data as columns)
            reduced_coords.append(data[:,0:self.args.num_coords])

        # convert reduced coords into list per dimension
        reduced_coords_per_dim = [[] for i in range(self.args.num_coords)]
        for i in range(self.args.num_coords):
            for j in range(len(reduced_coords)):
                reduced_coords_per_dim[i].append(reduced_coords[j][:,i])

        # keep track of original index
        original_index = []
        for j in range(len(reduced_coords)):
            original_index.append((j+1) * np.ones(reduced_coords[j].shape[0]))

        # write out files
        self._output_PS_files(table, header, reduced_coords_per_dim,
            original_index, csv_out, csv_no_index, csv_index_header, csv_headers)

    # write out Parameter Space files
    def _output_PS_files(self, meta_data, expand_header, reduced_coords_per_dim, 
        original_index, csv_out, csv_no_index, csv_index_header, csv_headers):
        
        # remove expanded column, if requested
        if self.args.remove_expand_col:
            meta_data.table = meta_data.table.drop(expand_header, axis=1)

        # add a new column for each requested dimension
        for i in range(self.args.num_coords):

            # for 1st dimension, expand table
            if i == 0:

                # add either original index + first dimension column
                if self.args.include_original_index:
                    expanded_data = utilities.explode(self.log, meta_data,
                        'Original Index', original_index)
                    expanded_data.add_col(np.concatenate(reduced_coords_per_dim[i]).tolist(),
                        expand_header + " Dimension " + str(i+1))

                # or just first dimension column
                else:
                    expanded_data = utilities.explode(self.log, meta_data,
                        expand_header + " Dimension " + str(i+1), reduced_coords_per_dim[i])

            # for other dimensions, just add column
            else:
                expanded_data.add_col(np.concatenate(reduced_coords_per_dim[i]).tolist(),
                    expand_header + " Dimension " + str(i+1))

        # write out .csv file
        expanded_data.to_csv(csv_out, index=csv_no_index, 
                              index_label=csv_index_header,
                              cols=csv_headers)

# if called from the command line display plugin specific command line arguments
if __name__ == "__main__":

    parameter_space = Plugin()
    parameter_space.parser.parse_args()