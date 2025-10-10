# Copyright (c) 2021 National Technology and Engineering Solutions of Sandia, LLC.  
# Under the terms of Contract DE-NA0003525 with National Technology and Engineering 
# Solutions of Sandia, LLC, the U.S. Government retains certain rights in this software.

# This module contains code to convert a file formats, in particular to output movies
# in mp4 Slycat readable format.

# standard library imports
import os
from pathlib import Path

# for writing mp4
import imageio

# for exporting images
from PIL import Image
from matplotlib import cm

# 3rd party imports
import numpy as np
import pandas as pd

# materials knowledge system
# for exporting images
from matplotlib import cm

# local imports
import slypi

# defaults for user arguments
JPG_QUALITY = 95
VIDEO_FPS = 25

# functions for jpg convert specific operations
# class must be named Plugin
class Plugin(slypi.ensemble.PluginTemplate):

    # initialize jpg convert command line argument parser
    def __init__(self):

        # describe jpg convert plugin
        description = "The convert plugin provides support for the converting between " + \
                      "different file formats."

        # set up parser
        super().__init__(description=description)

    # add any extra command line arguments
    def add_args(self):

        self.parser.add_argument("--suffix", default="", 
                                 help="Suffix to describe output file(s), "
                                      'e.g. "--suffix phase_field".  The suffix name is included in the name '
                                      "of any output file.")

        self.parser.add_argument("--binary", action="store_true", help="Converts field "
                                                                       "variable to binary by clipping anything less than 0 to 0 and anyting "
                                                                       "greater than 0 to 1.")

        self.parser.add_argument("--color-scale", nargs=2, type=float, help="Gives the color "
                                                                            "scale for the field variable when creating jpg or mp4, e.g. "
                                                                            '"--color-scale 0 1" for min color value of 0 and max color value of 1. '
                                                                            "Note that values above and below the color scale are automatically clipped.")

        self.parser.add_argument("--output-format", help="The output format options "
                                                         'recognized by the convert plugin include: "npy" -- saves the '
                                                         'field variable for a single timestep to a numpy array; "sim.npy" -- '
                                                         'saves the field variable for every timestep in a simulation to a 3D '
                                                         'numpy array; "rd.npy" -- saves the reduced dimensional representation '
                                                         'to a numpy array (can be either a time step matrix or a 3D full simulation '
                                                         'matrix); "jpg" -- saves a .jpg image of the field variable for a single '
                                                         'timestep; "mp4" -- saves a .mp4 movie of the field variable for every timestep '
                                                         'in a simulation.')

        self.parser.add_argument("--output-quality", type=int, default=JPG_QUALITY,
                                 help="Quality of jpg image, as a number between 1 and 95 (only relevant "
                                      "if outputing images, defaults to %s)." % str(JPG_QUALITY))

        self.parser.add_argument("--video-fps", type=float, default=VIDEO_FPS,
                                 help="Number of frames per second for video creation, defaults to %s)." %
                                      str(VIDEO_FPS))

        self.parser.add_argument("--write-raw-video", action="store_true", help="Create a video using the provided images unprocessed.")

    # check arguments, error if incorrect input
    def check_args(self, args):

        # check .jpg output_quality
        if args.output_quality < 1 or args.output_quality > 95:
            self.log.error("Quality option --output-quality must be between 1 and 95.  " +
                           "Please try again.")
            raise ValueError("output quality must be between 1 and 95.")

        # check fps is > 0
        if args.video_fps <= 0:
            self.log.error("Video frames per second --video-fps must be > 0.")
            raise ValueError("video fps must be > 0.")

    # initialize any local variables from command line arguments
    def init(self, args):

        # save args for later use
        self.args = args

    # make binary version of matrix
    def _binary(self, data):

        data[data < 0] = 0
        data[data > 0] = 1

        return data

    # clip matrix values and scale matrix to [0,1] 
    def _scale_matrix(self, point_data):
        
        # default to scaling to min/max of data
        point_data_min = point_data.min()
        point_data_max = point_data.max()
        
        # color-scale is provided clip data and use color scale for min/max
        if self.args.color_scale is not None:

            # clip data to min and max of color scale
            point_data[point_data < self.args.color_scale[0]] = self.args.color_scale[0]
            point_data[point_data > self.args.color_scale[1]] = self.args.color_scale[1]

            # use color scale for min and max to scale
            point_data_min = self.args.color_scale[0]
            point_data_max = self.args.color_scale[1]

        # scale data to [0,1] for image creation
        point_data = point_data - point_data_min    
        if point_data_min < point_data_max:
            point_data = point_data/(point_data_max - point_data_min)
        
        return point_data, point_data_min, point_data_max

    # convert matrix to mp4 frame
    def _matrix_to_mp4(self, data):

        # scale matrix to [0,1]
        point_data_out, _, _ = self._scale_matrix(data)

        # convert to image and remove alpha
        return np.delete(np.uint8(cm.jet(point_data_out) * 255), 3, 2)

    # read npy and sim.npy (also npy) formats
    def read_file(self, file_in, file_type=None):

        # check file extension, if not provided
        if file_type is None:

            # npy file type
            if file_in.endswith('.npy'):
                file_type = 'npy'
            
            if file_in.endswith('.npz'):
                file_type = 'npz'

            if file_in.endswith('.png'):
                file_type = 'png'

        # check if we have npy or sim.npy
        if file_type == 'npy':
            
            # read npy file
            try:
                data = np.load(file_in)
            except ValueError:
                self.log.error("Could not read " + file_in + " as a .npy file.")
                raise ValueError("Could not read " + file_in + " as a .npy file.")

        # is it .npz?
        elif file_type == 'npz':

            # read npz file
            try:
                data = np.load(file_in)
                data = data['arr_0']
            except ValueError:
                self.log.error("Could not read " + file_in + " as a .npy file.")
                raise ValueError("Could not read " + file_in + " as a .npy file.")

        # is it an image file?
        elif file_type == 'png':

            try:
                img = Image.open(file_in)
                data = np.array(img)
            except ValueError:
                self.log.error("Could not read " + file_in + "as a .png file.")
                raise ValueError("Could not read " + file_in + " as a .png file.")
            
        # otherwise default to mesh
        else:
            data = super().read_file(file_in, file_type)

        return data

    # write out .npy format or .jpg
    def write_file(self, data, file_out, file_type=None):

        # check for npy output format with color scale
        if file_type=='npy':
            if self.args.color_scale is not None:
                self.log.error("Can't use --color-scale with .npy output.")
                raise ValueError("can't use --color-scale with .npy output.")

        # infer file type, if not provided
        if file_type is None:

            if file_out.endswith('.npy'):
                file_type = 'npy'

            if file_out.endswith('.npz'):
                file_type = 'npz'

            if file_out.endswith('.jpg'):
                file_type = 'jpg'

        # check for npy or jpg file output (data is matrix format)
        if file_type in ['npy', 'npz', 'jpg']:

            # convert to binary, if requested
            if self.args.binary:
                data = self._binary(data)

            # write out field variable as npy, npz or jpg
            if file_type == "npy":

                # save as numpy
                np.save(file_out, data)
            
            # write out field variable as npz
            elif file_type == "npz":

                # save as compressed numpy
                np.savez_compressed(file_out, np.asarray(data, dtype=np.float16))

            # for jpg we need to scale data and use a colormap
            elif file_type == "jpg":

                # is it already RGB?
                if len(data.shape) == 3:
                    img = Image.fromarray(data.astype(np.uint8), 'RGB')
                    img.save(file_out, quality=self.args.output_quality)
                
                else:
                    # convert to [0,1]
                    data, _, _ = self._scale_matrix(data)
                    
                    # convert to standard jet color map image
                    img = Image.fromarray(np.uint8(cm.jet(data) * 255))

                    # save image
                    img.convert("RGB").save(file_out, quality=self.args.output_quality)

        else:

            # default to meshio output
            super().write_file(data, file_out, file_type=file_type)

    # over-riding convert_files to generate sim.npy and mp4 files
    def convert_files(self, file_list, output_dir, output_type, input_type=None):

        # check for dakota tabular.dat file
        if len(file_list) == 1:
            if file_list[0].endswith(".dat") or input_type == "dat":
                if output_type == "csv":

                    # read tabular.dat file
                    df = pd.read_csv(file_list[0], sep=r'\s+')

                    # pre-pend workdir.x as identification column
                    eval_id = df['%eval_id']
                    file_path = os.path.split(file_list[0])[0]
                    workdirs = [os.path.join(file_path, 'workdir.' + str(id))
                                for id in eval_id]
                    df.insert(0, column='', value=workdirs)
                    
                    # save as tabular.csv file
                    root = os.path.split(file_list[0])[1][:-4]
                    output_file = Path(os.path.join(output_dir, root + '.csv')).as_posix()
                    df.to_csv(output_file, index=False)

                    return [output_file]

        # check for sim.npy or mp4
        if output_type == "sim.npy" or output_type == "mp4":

            # go through file list and load data
            file_data = []
            num_files = len(file_list)
            for file_to_add in file_list:

                point_data_out = imageio.imread(file_to_add)

                # convert to binary, if requested
                if self.args.binary:
                    point_data_out = self._binary(point_data_out)

                # make sure we only have at most one 3D matrix
                matrix_dim = len(point_data_out.shape)

                # add as matrix
                if output_type == "sim.npy":

                    # check that it's 2D matrix:
                    if matrix_dim == 2:
                        file_data.append(point_data_out)

                    # otherwise keep data the same
                    else:
                        file_data = point_data_out

                # add as jet colormap image
                else:

                    # convert each frame for 2D
                    if matrix_dim == 2:

                        # convert to mp4 frame
                        file_data.append(self._matrix_to_mp4(point_data_out))

                    # check if frame is RGB
                    elif point_data_out.shape[2] == 3:

                        # keep data the same
                        file_data.append(point_data_out)
                    
                    else:

                        # convert all frames for 3D
                        for i in range(point_data_out.shape[0]):
                            file_data.append(self._matrix_to_mp4(point_data_out[i, :, :]))

            # create file name by combining root file names with field variable
            if num_files > 1:

                # get common file prefix
                common_prefix = os.path.basename(os.path.commonprefix(file_list))

                # remove trailing zeros, if they exist
                common_prefix = common_prefix.rstrip('0')

                # join to output directory and add field variable
                file_out = Path(os.path.join(output_dir, common_prefix +
                                self.args.suffix + "." + output_type)).as_posix()

            # if one file, change extension to output type
            else:

                file_name = os.path.basename(file_list[0])

                # check for .sim.npy file (very likely)
                if file_name.endswith('.sim.npy'):
                    file_root, file_ext = file_name.split('.sim.npy')

                # otherwise split normally
                else:
                    file_root, file_ext = os.path.splitext(file_name)

                file_out = Path(os.path.join(output_dir, file_root + "." + 
                                             output_type)).as_posix()

            # write out as sim.npy
            if output_type == "sim.npy":
                np.save(file_out, np.asarray(file_data))

            # write out as mp4
            else:

                # open a video writer with web browser codecs
                writer = imageio.get_writer(file_out, format="FFMPEG", mode="I", 
                    fps=self.args.video_fps, output_params=['-force_key_frames', 
                    '0.0,0.04,0.08']) #, '-vcodec', 'libx264', '-acodec', 'aac'])

                # write frames to movie
                if not self.args.write_raw_video:
                    for i in range(len(file_data)):
                        writer.append_data(file_data[i])
                else:
                    # add raw files to imageio video writer
                    for f in file_list:
                        writer.append_data(imageio.imread(f))

                writer.close()

            # must return a list of files written
            return [file_out]

        else:
        
            # revert to 1-1 file conversion
            return super().convert_files(file_list, output_dir, output_type, input_type=input_type)


# if called from the command line display plugin specific command line arguments
if __name__ == "__main__":
    plugin = Plugin()
    plugin.parser.parse_args()
