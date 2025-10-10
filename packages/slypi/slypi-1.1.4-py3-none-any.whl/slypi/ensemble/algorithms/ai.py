# Copyright (c) 2021 National Technology and Engineering Solutions of Sandia, LLC.  
# Under the terms of Contract DE-NA0003525 with National Technology and Engineering 
# Solutions of Sandia, LLC, the U.S. Government retains certain rights in this software.

# This module contains ai/ml algorithms for use with slypi.

# S. Martin
# 1/12/2025

# auto-encoder
import torch
import torch.multiprocessing as mp

import time
import warnings

# types of autoencoders
MODEL_TYPES = ["MLP", "var"]

# auto-encoder training defaults
BATCH_SIZE = 64
EPOCHS = 10
LEARNING_RATE = 1e-3
MLP_ARCH = [512,128]
NUM_PROCESSES = 1


class TorchDataset(torch.utils.data.Dataset):
    """
    This class contains a torch dataset constructor that converts a numpy
    array with rows as points to a torch dataset for use with the 
    auto-encoder.

    :Example:

    .. code-block:: python

        # initialize a random dataset, 100 data points in 10 dimensions
        random_data = numpy.random.rand (100,10)

        # convert to a torch dataset
        torch_data = TorchDataset(random_data)

        # put data in a torch dataloader using a batch size of 10
        data_loader = torch.utils.data.DataLoader(torch_data, batch_size=10, shuffle=True)

    """

    # stores a numpy array as a torch tensor
    def __init__(self, X):        
        self.X = torch.from_numpy(X)

    # number of samples
    def __len__(self):
        return self.X.size()[0]

    # get item
    def __getitem__(self, index):
        return self.X[index,:]


class MLP(torch.nn.Module):
    """
    This class contains a basic MLP auto-encoder that can be used for dimension 
    reduction.  The class implements only the pytorch architecture for a model.
    """

    # initialize the network using the input dimension and bottleneck dimension
    def __init__(self, input_dim, bottleneck_dim, arch=MLP_ARCH):
        
        super().__init__()

        # keep track of network architecture
        self.num_inputs = input_dim
        self.num_dim = bottleneck_dim

        # encoder/decoder layers
        self.encoder_arch = [self.num_inputs] + arch
        self.decoder_arch = [self.num_dim] + arch[::-1]
        self.num_layers = len(self.encoder_arch) - 1

        # set up architecture
        self._init_encoder()
        self._init_decoder()

    # define encoder layers (num_inputs -> MLP -> num_dim)
    def _init_encoder(self):

        # append hidden layers
        self.encoder_layers = torch.nn.ModuleList()
        for k in range(self.num_layers):
            self.encoder_layers.append(
                torch.nn.Linear(self.encoder_arch[k], self.encoder_arch[k+1]))

        # bottleneck layer
        self.bottleneck_layer = torch.nn.Linear(self.encoder_arch[-1], self.num_dim)

    # define decoder layers (num_dim -> reverse MLP -> num_inputs)
    def _init_decoder(self):        

        # append hidden layers
        self.decoder_layers = torch.nn.ModuleList()
        for k in range(self.num_layers):
            self.decoder_layers.append(
                torch.nn.Linear(self.decoder_arch[k], self.decoder_arch[k+1]))
        
        # reconstruction layer
        self.reconstruction_layer = torch.nn.Linear(self.decoder_arch[-1], self.num_inputs)

    # execute encoder
    def _encoder(self, data):

        # initial encoder layers
        for layer in self.encoder_layers:
            data = torch.nn.functional.relu(layer(data))

        # bottleneck layer
        bottleneck = self.bottleneck_layer(data)

        return bottleneck

    # execute decoder
    def _decoder(self, data):

        # decoder
        for layer in self.decoder_layers:
            data = torch.nn.functional.relu(layer(data))

        return torch.tanh(self.reconstruction_layer(data))

    # auto-encoder architecture definition for pytorch
    def forward(self, data):

        # encode-decode
        bottleneck = self._encoder(data)
        reconstruction = self._decoder(bottleneck)

        return reconstruction

    # return reduced data using encoder on numpy array
    def encoder(self, data):

        # convert numpy array to torch format
        torch_data = torch.from_numpy(data.astype(np.float32))

        # get bottleneck layer
        bottleneck = self._encoder(torch_data)

        # convert back to numpy array
        return bottleneck.data.numpy()

    # return reconstructed data using decoder on numpy array
    def decoder(self, data):

        # convet numpy array to torch format
        torch_data = torch.from_numpy(data.astype(np.float32))

        # reconstruct data using decoder
        recon = self._decoder(torch_data)

        # convert back to numpy array
        return recon.data.numpy()


# variational autoencoder architecture
class VAE(torch.nn.Module):
    """
    This class contains a basic variational auto-encoder that can be used for dimension 
    reduction.  The class implements only the pytorch architecture for a model.
    """

    # initialize network using input, bottleneck dimension
    def __init__(self, input_dim, bottleneck_dim):

        super().__init__()

        # network architecture
        self.input_dim = input_dim
        self.bottleneck_dim = bottleneck_dim

        # set up architecture
        self._init_encoder()
        self._init_decoder()

    # encoder architecture
    def _init_encoder(self):

        self.fc1 = torch.nn.Linear(self.input_dim, 500)
        self.fc21 = torch.nn.Linear(500, self.bottleneck_dim)
        self.fc22 = torch.nn.Linear(500, self.bottleneck_dim)
    
    # decoder architecture
    def _init_decoder(self):

        self.fc3 = torch.nn.Linear(self.bottleneck_dim, 500)
        self.fc4 = torch.nn.Linear(500, self.input_dim)

    # execute encoder (using torch data)
    def _encode(self, x):

        h1 = torch.nn.functional.relu(self.fc1(x))
        return self.fc21(h1), self.fc22(h1)

    # execute decoder (using torch data)
    def _decode(self, z):
    
        h3 = torch.nn.functional.relu(self.fc3(z))
        return torch.sigmoid(self.fc4(h3))

    # reparameterize for variational layer
    def _reparameterize(self, mu, logvar):
        std = torch.exp(0.5*logvar)
        eps = torch.randn_like(std)
        return mu + eps*std

    # execute auto-encoder (torch data)
    def forward(self, x):
        mu, logvar = self._encode(x)
        z = self._reparameterize(mu, logvar)
        return self._decode(z), mu, logvar

    # return reduced data using encoder on numpy array
    def encoder(self, data):

        # convert numpy array to torch format
        torch_data = torch.from_numpy(data.astype(np.float32))

        # get bottleneck layer (variational)
        mu, logvar = self._encode(torch_data)

        # re-parameterize
        bottleneck = self._reparameterize(mu, logvar)

        # convert back to numpy array
        return bottleneck.data.numpy()

    # return reconstructed data using decoder on numpy array
    def decoder(self, data):

        # convet numpy array to torch format
        torch_data = torch.from_numpy(data.astype(np.float32))

        # reconstruct data using decoder
        recon = self._decode(torch_data)

        # convert back to numpy array
        return recon.data.numpy()


class AutoEncoder(torch.nn.Module):
    """
    This class is a factory class defines and trains a pytorch auto-encoder model.
    The class implements the basic functions expected from the DimensionReduction 
    class, including fit, partial_fit, and transform.
    """

    # initialize auto-encoder with user parameters
    def __init__(self, log, num_dim=NUM_DIM, batch_size=None,
            learning_rate=LEARNING_RATE, epochs=None, num_processes=NUM_PROCESSES,
            model_type='MLP'):

        super().__init__()

        # number of encoder output neurons
        self.num_dim = num_dim

        # set default batch size
        self.batch_size = batch_size
        if self.batch_size is None:
            self.batch_size = BATCH_SIZE

        # learning rate for training
        self.learning_rate = learning_rate

        # set default epochs
        self.epochs = epochs
        if self.epochs is None:
            self.epochs = EPOCHS

        # use multiprocessing
        self.num_processes = num_processes
        if self.num_processes is None:
            self.num_processes = NUM_PROCESSES

        # use calling function log for output
        self.log = log

        # model type for autoencoder
        self.model_type = model_type

        # actual autencoder model has not been initialized
        self.model = None

    # variational reconstruction + KL divergence losses summed over all elements and batch
    def _var_loss(self, recon_x, x, mu, logvar):

        BCE = torch.nn.functional.binary_cross_entropy(recon_x, x, reduction='sum')

        # see Appendix B from VAE paper:
        # Kingma and Welling. Auto-Encoding Variational Bayes. ICLR, 2014
        # https://arxiv.org/abs/1312.6114
        # 0.5 * sum(1 + log(sigma^2) - mu^2 - sigma^2)
        KLD = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())

        return BCE + KLD

    # train auto-encoder (can be called in parallel)
    def _train(self, rank, model, model_type, device, data_loader, 
        optimizer, scheduler, epochs):

        # for MLP use mean square error loss
        if model_type == 'MLP':
            criterion = torch.nn.MSELoss()

        # train auto-encoder
        model.train()
        for epoch in range(epochs):
            for batch_idx, data in enumerate(data_loader):

                # zero gradients
                optimizer.zero_grad()

                # re-construct data & compute loss
                if model_type == 'MLP':
                    recon = model(data.to(device))
                    loss = criterion(recon.to(device), data)
                elif model_type == 'var':
                    recon, mu, logvar = model(data.to(device))
                    loss = self._var_loss(recon.to(device), data, mu, logvar)
                
                # do back-propagation
                loss.backward()
                optimizer.step()

                # using print because we are in a thread
                if batch_idx % 10 == 0:
                    print('Process {} -- Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                        rank, epoch, batch_idx * len(data), len(data_loader.dataset),
                        100. * batch_idx / len(data_loader), loss.item()))

            # adjust optimization parameters
            scheduler.step(loss.item())

    # define and fit auto-encoder
    def fit(self, data):

        # check batch size
        num_data, num_inputs = data.shape
        if self.batch_size > num_data:
            warnings.warn("Batch size exceeds number of data points -- resetting to " +
                          "number data points.")
            self.batch_size = num_data

        # convert data to torch format
        torch_data = TorchDataset(data.astype(np.float32))
        
        # set up encoder/decoder layers/optimizer
        if self.model is None:

            if self.model_type == 'MLP':
                self.model = MLP(num_inputs, self.num_dim)
            
            elif self.model_type == 'var':
                self.model = VAE(num_inputs, self.num_dim)

            # use Adam optimizer
            self.optimizer = torch.optim.AdamW(self.parameters(),
                                               lr=self.learning_rate,
                                               weight_decay=1e-5)

            # use reduce on stall scheduler
            self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, patience=50)

        # use CUDA, if available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # share model between processes
        self.model.to(device)
        self.model.share_memory()

        # time training 
        t0 = time.time()

        processes = []
        for rank in range(self.num_processes):

            # partition data per process
            data_loader = torch.utils.data.DataLoader(
                dataset=torch_data,
                sampler=torch.utils.data.distributed.DistributedSampler(
                    dataset=torch_data,
                    num_replicas=self.num_processes,
                    rank=rank
                ),
                batch_size=self.batch_size,
            )

            # launch processes
            process = mp.Process(target=self._train, 
                args=(rank, self.model, self.model_type, device, 
                    data_loader, self.optimizer, self.scheduler, self.epochs))
            process.start()
            processes.append(process)

        # collect results
        for process in processes:
            process.join()

        self.log.info("Training Time: %s" % str(timedelta(seconds=time.time()-t0)))

    # perform dimension reduction
    def transform(self, data):
        
        # get reduced data from encoder
        return self.model.encoder(data)

    # inverse transofmr
    def inverse_transform(self, data):

        recon = self.model.decoder(data)

        return recon


class AI:

    # init parser
    def _init_parser(self):

        # auto-encoder parameters

        # model type
        self.parser.add_argument("--model-type", choices=MODEL_TYPES,
            help="Type of auto-encoder.  Options are: {%s}." % ", ".join(MODEL_TYPES))

        # number of epochs
        self.parser.add_argument("--epochs", type=int, help="Number of epochs "
            "to use for training auto-encoder.")

        # batch size
        self.parser.add_argument("--batch-size", type=int, help="Batch size "
            "for training auto-encoder.")

        # MLP architecture
        self.parser.add_argument('--MLP-arch', type=int, nargs='+', help="Integers specifying "
            "size of hidden layers in the MLP.")

        # number of processors
        self.parser.add_argument("--num-processes", type=int, help="Number of processes to "
            "use for training auto-encoder.")
        
    # check parameters for valid values
    def _check_args(self, args):

        # check for specific auto-encoder arguments
        if args.algorithm == "auto-encoder":

            # check epochs >= 1
            if args.epochs is not None:
                if args.epochs < 1:
                    self.log.error("Epochs must be >= 1.")
                    raise ValueError("epochs must be >= 1.")
            
            # check batch-siae >= 1
            if args.batch_size is not None:
                if args.batch_size < 1:
                    self.log.error("Batch size must be >= 1.")
                    raise ValueError("batch size must be >= 1.")

            # check number of process is >= 1
            if args.num_processes is not None:
                if args.num_processes < 1:
                    self.log.error("Number of processes must be >= 1.")
                    raise ValueError("number of prodesses must be >= 1.")

            # check that MLP layer sizes are >= 1
            if args.MLP_arch is not None:
                for layer_size in args.MLP_arch:
                    if layer_size < 1:
                        self.log.error("MLP architecture layer sizes must be >= 1.")
                        raise ValueError("MLP architecture layer sizes must be >= 1.") 
                    
    # set parameters using arguments
    def _set_parms(self, args):

        # auto-encoder arguments
        if args.model_type is None:
            self.model_parms["model_type"] = MODEL_TYPES[0]
        else:
            self.model_parms["model_type"] = args.model_type
        self.model_parms["epochs"] = args.epochs
        self.model_parms["batch_size"] = args.batch_size
        self.model_parms["num_processes"] = args.num_processes


    # add particular algorithm to end of model list
    def _init_algorithm(self, num_dim):

        if self.model_parms["algorithm"] == "auto-encoder":
            self.model.append(AutoEncoder(self.log, num_dim = num_dim,
                                          model_type=self.model_parms["model_type"],
                                          epochs=self.model_parms["epochs"],
                                          batch_size = self.model_parms["batch_size"],
                                          num_processes=self.model_parms["num_processes"]))
            
    # perform incremental dimension reduction
    def partial_fit(self, data, time_step=0):
        """
        Train an incremental model using samples.

        Args:
            data (array): data with points as rows
            time_step (int): model time step
        """

        if self.model_parms["algorithm"] == "auto-encoder":
            self.model[time_step].fit(data)
        
        