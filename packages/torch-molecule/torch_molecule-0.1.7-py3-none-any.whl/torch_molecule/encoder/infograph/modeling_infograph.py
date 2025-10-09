import numpy as np
from tqdm import tqdm
from typing import Optional, Union, Dict, Any, Tuple, List, Literal

import torch
from torch_geometric.loader import DataLoader
from torch_geometric.data import Data

from .model import GNN
from ..constant import GNN_ENCODER_MODELS, GNN_ENCODER_READOUTS, GNN_ENCODER_PARAMS
from ...base import BaseMolecularEncoder
from ...utils import graph_from_smiles

ALLOWABLE_ENCODER_MODELS = GNN_ENCODER_MODELS
ALLOWABLE_ENCODER_READOUTS = GNN_ENCODER_READOUTS

class InfoGraphMolecularEncoder(BaseMolecularEncoder):
    """This encoder implements a InfoGraph for molecular representation learning.

    InfoGraph: Unsupervised and Semi-supervised Graph-Level Representation Learning via Mutual Information Maximization (ICLR 2020)

    References
    ----------
    - Paper: https://arxiv.org/abs/1908.01000 
    - Code: https://github.com/sunfanyunn/InfoGraph/tree/master/unsupervised

    Parameters
    ----------
    lw_prior : float, default=0.
        Weight for prior loss term.
    embedding_dim : int, default=160
        Dimension of final graph embedding. Must be divisible by num_layer.
    num_layer : int, default=5
        Number of GNN layers.
    drop_ratio : float, default=0.5
        Dropout probability.
    norm_layer : str, default="batch_norm"
        Type of normalization layer to use. One of ["batch_norm", "layer_norm", "instance_norm", "graph_norm", "size_norm", "pair_norm"].
    encoder_type : str, default="gin-virtual"
        Type of GNN architecture to use. One of ["gin-virtual", "gcn-virtual", "gin", "gcn"].
    readout : str, default="sum"
        Method for aggregating node features to obtain graph-level representations. One of ["sum", "mean", "max"].
    batch_size : int, default=128
        Number of samples per batch for training.
    epochs : int, default=500
        Maximum number of training epochs.
    learning_rate : float, default=0.001
        Learning rate for optimizer.
    grad_clip_value : float, optional
        Maximum norm of gradients for gradient clipping.
    weight_decay : float, default=0.0
        L2 regularization strength.
    use_lr_scheduler : bool, default=False
        Whether to use a learning rate scheduler.
    scheduler_factor : float, default=0.5
        Factor by which to reduce the learning rate when plateau is detected.
    scheduler_patience : int, default=5
        Number of epochs with no improvement after which learning rate will be reduced.
    verbose : str, default="none"
        Whether to display progress info. Options are: "none", "progress_bar", "print_statement". If any other, "none" is automatically chosen.
    device : Optional[Union[torch.device, str]], default=None
        Device to run the model on (CPU or GPU).
    model_name : str, default="InfoGraphMolecularEncoder"
        Name identifier for the model.
    """
    def __init__(
        self, 
        lw_prior: float = 0., 
        embedding_dim: int = 160, 
        num_layer: int = 5, 
        drop_ratio: float = 0.5, 
        norm_layer: str = "batch_norm", 
        encoder_type: str = "gin-virtual", 
        readout: str = "sum", 
        batch_size: int = 128, 
        epochs: int = 500, 
        learning_rate: float = 0.001, 
        grad_clip_value: Optional[float] = None, 
        weight_decay: float = 0.0, 
        use_lr_scheduler: bool = False, 
        scheduler_factor: float = 0.5, 
        scheduler_patience: int = 5, 
        *,
        device: Optional[Union[torch.device, str]] = None,
        model_name: str = "InfoGraphMolecularEncoder",
        verbose: str = "none", 
    ):
        super().__init__(device=device, model_name=model_name, verbose=verbose)
        
        self.lw_prior = lw_prior
        self.embedding_dim = embedding_dim
        self.num_layer = num_layer
        self.drop_ratio = drop_ratio
        self.norm_layer = norm_layer
        self.encoder_type = encoder_type
        self.readout = readout
        self.batch_size = batch_size
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.grad_clip_value = grad_clip_value
        self.weight_decay = weight_decay
        self.use_lr_scheduler = use_lr_scheduler
        self.scheduler_factor = scheduler_factor
        self.scheduler_patience = scheduler_patience
        self.fitting_loss = list()
        self.fitting_epoch = 0
        self.model_class = GNN

        if self.encoder_type not in ALLOWABLE_ENCODER_MODELS:
            raise ValueError(f"Invalid encoder_model: {self.encoder_type}. Currently only {ALLOWABLE_ENCODER_MODELS} are supported.")
        if self.readout not in ALLOWABLE_ENCODER_READOUTS:
            raise ValueError(f"Invalid encoder_readout: {self.readout}. Currently only {ALLOWABLE_ENCODER_READOUTS} are supported.")

        if self.lw_prior == 0:
            self.use_prior = False
        else:
            self.use_prior = True
        
        assert self.embedding_dim % self.num_layer == 0, "embedding_dim must be divisible by num_layer for InfographMolecularEncoder"

    @staticmethod
    def _get_param_names() -> List[str]:
        """Get parameter names for the estimator.

        Returns
        -------
        List[str]
            List of parameter names that can be used for model configuration.
        """
        params = GNN_ENCODER_PARAMS.copy()
        params.remove("hidden_size")
        params = params + ["embedding_dim", 'use_prior', 'lw_prior']
        return params
    

    def _get_model_params(self, checkpoint: Optional[Dict] = None) -> Dict[str, Any]:
        params = [
            "num_layer", "embedding_dim", "drop_ratio", "norm_layer", "encoder_type", "readout", "use_prior",
        ]        
        if checkpoint is not None:
            if "hyperparameters" not in checkpoint:
                raise ValueError("Checkpoint missing 'hyperparameters' key")
            return {k: checkpoint["hyperparameters"][k] for k in params}
    
        return {k: getattr(self, k) for k in params}
    
    def _convert_to_pytorch_data(self, X):
        """Convert numpy arrays to PyTorch Geometric data format.
        """
        if self.verbose == "progress_bar":
            iterator = tqdm(enumerate(X), desc="Converting molecules to graphs", total=len(X))
        elif self.verbose == "print_statement":
            print("Converting molecules to graphs, preparing data for training...")
            iterator = enumerate(X)
        else:
            iterator = enumerate(X)

        pyg_graph_list = []
        for idx, smiles_or_mol in iterator:
            graph = graph_from_smiles(smiles_or_mol, None)
            g = Data()
            g.num_nodes = graph["num_nodes"]
            g.edge_index = torch.from_numpy(graph["edge_index"])

            del graph["num_nodes"]
            del graph["edge_index"]

            if graph["edge_feat"] is not None:
                g.edge_attr = torch.from_numpy(graph["edge_feat"])
                del graph["edge_feat"]

            if graph["node_feat"] is not None:
                g.x = torch.from_numpy(graph["node_feat"])
                del graph["node_feat"]

            pyg_graph_list.append(g)

        return pyg_graph_list
    
    def _setup_optimizers(self) -> Tuple[torch.optim.Optimizer, Optional[Any]]:
        """Setup optimization components including optimizer and learning rate scheduler.
        """
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay)
        scheduler = None
        if self.use_lr_scheduler:
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
                optimizer,
                mode="min",
                factor=self.scheduler_factor,
                patience=self.scheduler_patience,
                min_lr=1e-6,
                cooldown=0,
                eps=1e-8,
            )
        return optimizer, scheduler
    
    def fit(
        self,
        X_train: List[str],
    ) -> "InfoGraphMolecularEncoder":
        """Fit the model to the training data with optional validation set.

        Parameters
        ----------
        X_train : List[str]
            Training set input molecular structures as SMILES strings
        Returns
        -------
        self : InfoGraphMolecularEncoder
            Fitted estimator
        """
        
        self._initialize_model(self.model_class)
        self.model.initialize_parameters()
        optimizer, scheduler = self._setup_optimizers()
        
        # Prepare datasets and loaders
        X_train, _ = self._validate_inputs(X_train, return_rdkit_mol=True)
        train_dataset = self._convert_to_pytorch_data(X_train)
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=0
        )
        self.fitting_loss = []

        total_steps = self.epochs * len(train_loader)        
        global_pbar = None
        if self.verbose == "progress_bar": 
            global_pbar = tqdm(total=total_steps, desc="Training Progress")

        for epoch in range(self.epochs):
            # Training phase
            train_losses = self._train_epoch(train_loader, optimizer, epoch, global_pbar)
            self.fitting_loss.append(np.mean(train_losses).item())
            if scheduler:
                scheduler.step(np.mean(train_losses).item())
        if global_pbar is not None:
            global_pbar.close()
        self.fitting_epoch = epoch
        self.is_fitted_ = True
        return self

    def _train_epoch(self, train_loader, optimizer, epoch, global_pbar=None):
        """Training logic for one epoch.

        Args:
            train_loader: DataLoader containing training data
            optimizer: Optimizer instance for model parameter updates

        Returns:
            list: List of loss values for each training step
        """
        self.model.train()
        losses = []

        for step, batch in enumerate(train_loader):
            batch = batch.to(self.device)
            optimizer.zero_grad()
            local_global_loss, prior_loss = self.model.compute_loss(batch, self.lw_prior)
            loss = local_global_loss + prior_loss
            loss.backward()
            if self.grad_clip_value is not None:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip_value)
            optimizer.step()
            losses.append(loss.item())
            log_dict = {
                    "Epoch": f"{epoch+1}/{self.epochs}",
                    "Step": f"{step+1}/{len(train_loader)}",
                    "Loss": f"{loss.item():.4f}",
                    "Local/Global": f"{local_global_loss.item():.4f}",
                    "Prior": f"{prior_loss.item():.4f}"
                }
            if global_pbar is not None:
                global_pbar.set_postfix(log_dict)
                global_pbar.update(1)
            if self.verbose == "print_statement":
                print(log_dict)

        return losses

    def encode(self, X: List[str], return_type: Literal["np", "pt"] = "pt") -> Union[np.ndarray, torch.Tensor]:
        """Encode molecules into vector representations.

        Parameters
        ----------
        X : List[str]
            List of SMILES strings
        return_type : Literal["np", "pt"], default="pt"
            Return type of the representations

        Returns
        -------
        representations : ndarray or torch.Tensor
            Molecular representations
        """
        self._check_is_fitted()

        # Convert to PyTorch Geometric format and create loader
        X, _ = self._validate_inputs(X, return_rdkit_mol=True)
        dataset = self._convert_to_pytorch_data(X)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=False)

        if self.model is None:
            raise RuntimeError("Model not initialized")

        # Generate encodings
        self.model = self.model.to(self.device)
        self.model.eval()
        encodings = []
        with torch.no_grad():
            for batch in tqdm(loader, disable=self.verbose != "progress_bar"):
                batch = batch.to(self.device)
                out = self.model(batch)
                encodings.append(out["graph"].cpu())

        # Concatenate and convert to requested format
        encodings = torch.cat(encodings, dim=0)
        return encodings if return_type == "pt" else encodings.numpy()