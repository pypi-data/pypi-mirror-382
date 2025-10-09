import os
import numpy as np
from tqdm import tqdm
from typing import Optional, Union, Dict, Any, Tuple, List
import warnings
import datetime

import torch
from torch_geometric.loader import DataLoader
from torch_geometric.data import Data
from .gnn import GREANet
from .features import smiles_to_graph

from ...base import BaseMolecularPredictor

class GREAMolecularPredictor(BaseMolecularPredictor):
    """This predictor implements a GNN model based on Graph Rationalization
    for molecular property prediction tasks.
    """

    def __init__(
        self,
        num_tasks: int = 1,
        task_type: str = "classification",
        gamma: float = 0.4,
        num_layer: int = 5,
        emb_dim: int = 300,
        gnn_type: str = "gin-virtual",
        drop_ratio: float = 0.5,
        norm_layer: str = "batch_norm",
        batch_size: int = 32,
        epochs: int = 100,
        learning_rate: float = 0.001,
        weight_decay: float = 0.0,
        patience: int = 50,
        device: Optional[str] = None,
        use_lr_scheduler: bool = True,
        scheduler_factor: float = 0.5,
        scheduler_patience: int = 5,
        grad_clip_value: Optional[float] = None,
        verbose: bool = False,
        model_name: str = "GREApredictor",
        criterion = None,
    ):
        super().__init__()

        # Model hyperparameters
        self.num_tasks = num_tasks
        self.task_type = task_type
        self.num_layer = num_layer
        self.gamma = gamma
        self.emb_dim = emb_dim
        self.gnn_type = gnn_type
        self.drop_ratio = drop_ratio
        self.norm_layer = norm_layer

        # Training parameters
        self.batch_size = batch_size
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.patience = patience
        self.use_lr_scheduler = use_lr_scheduler
        self.scheduler_factor = scheduler_factor
        self.scheduler_patience = scheduler_patience
        self.grad_clip_value = grad_clip_value
        self.criterion = criterion if criterion is not None else self._load_default_criterion()

        # Set device
        self.device = (
            torch.device(device)
            if device
            else torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        )

        # Initialize model
        self.model = GREANet(
            num_tasks=self.num_tasks,
            num_layer=self.num_layer,
            gamma=self.gamma,
            emb_dim=self.emb_dim,
            gnn_type=self.gnn_type,
            drop_ratio=self.drop_ratio,
            norm_layer=self.norm_layer,
        ).to(self.device)

        self.fitting_loss = []
        self.fitting_loss_mean = float("inf")
        self.fitting_epoch = 0
        self.verbose = verbose
        self.model_name = model_name

    @staticmethod
    def _get_param_names() -> List[str]:
        """Get parameter names for the estimator.

        Returns
        -------
        List[str]
            List of parameter names that can be used for model configuration.
        """
        return [
            # Model hyperparameters
            "num_tasks",
            "task_type",
            "num_layer",
            "gamma",
            "emb_dim",
            "gnn_type",
            "drop_ratio",
            "norm_layer",
            # Training parameters
            "batch_size",
            "epochs",
            "learning_rate",
            "weight_decay",
            "patience",
            "device",
            "grad_clip_value",
            "criterion",
            # Scheduler parameters
            "use_lr_scheduler",
            "scheduler_factor",
            "scheduler_patience",
        ]

    def setup_optimizers(self) -> Tuple[torch.optim.Optimizer, Optional[Any]]:
        """Setup optimization components including optimizer and learning rate scheduler.

        Returns
        -------
        Tuple[optim.Optimizer, Optional[Any]]
            A tuple containing:
            - The configured optimizer
            - The learning rate scheduler (if enabled, else None)

        Notes
        -----
        The scheduler returned can be either _LRScheduler or ReduceLROnPlateau,
        hence we use Any as the type hint instead of optim.lr_scheduler._LRScheduler
        """
        optimizer = torch.optim.Adam(
            self.model.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay
        )
        if self.grad_clip_value is not None:
            for group in optimizer.param_groups:
                group.setdefault("max_norm", self.grad_clip_value)
                group.setdefault("norm_type", 2.0)

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

    def _convert_to_pytorch_data(self, X, y=None):
        """Convert numpy arrays to PyTorch data format.

        Should be implemented by child classes to handle specific molecular
        representations (e.g., SMILES to graphs, conformers to graphs, etc.)
        """

        pyg_graph_list = []
        for idx, smiles in enumerate(tqdm(X, desc="Converting molecules to graphs")):
            if y is not None:
                properties = y[idx]
            else:
                properties = None
            graph = smiles_to_graph(smiles, properties)
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

            if graph["y"] is not None:
                g.y = torch.from_numpy(graph["y"])
                del graph["y"]

            try:
                g.fp = torch.tensor(graph["fp"], dtype=torch.int8).view(1, -1)
                del graph["fp"]
            except:
                pass

            pyg_graph_list.append(g)

        return pyg_graph_list

    def fit(self, X: List[str], y: Optional[Union[List, np.ndarray]]) -> "GREAMolecularPredictor":
        """Fit the model to the data.

        Parameters
        ----------
        X : list of SMILES strings
            Input molecular structures as SMILES strings
        y : array-like,
            Target values for property prediction
        Returns
        -------
        self : object
            Fitted estimator
        """
        self.model = self.model.to(self.device)
        # Setup training
        optimizer, scheduler = self.setup_optimizers()
        cnt_wait = 0

        # Convert molecular data to PyTorch Geometric format
        X, y = self._validate_inputs(X, y)
        dataset = self._convert_to_pytorch_data(X, y)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=False)

        # Initialize best model state
        self.fitting_loss = []
        self.fitting_loss_mean = float("inf")
        self.fitting_epoch = 0
        best_param_vector = None

        # Training loop
        for epoch in range(self.epochs):
            # Train for one epoch
            losses = self.train_epoch(loader, optimizer)
            loss_mean = np.mean(losses)
            if scheduler:
                scheduler.step()

            # Update best model
            if loss_mean < self.fitting_loss_mean:
                self.fitting_epoch = epoch
                self.fitting_loss = losses
                self.fitting_loss_mean = loss_mean
                best_param_vector = torch.nn.utils.parameters_to_vector(self.model.parameters())
                cnt_wait = 0
            else:
                cnt_wait += 1
                if cnt_wait > self.patience:
                    break

        if best_param_vector is not None:
            torch.nn.utils.vector_to_parameters(best_param_vector, self.model.parameters())

        self.is_fitted_ = True
        return self

    def predict(self, X: List[str]) -> Dict[str, np.ndarray]:
        """Make predictions using the fitted model.

        Parameters
        ----------
        X : List[str]
            List of SMILES strings to make predictions for

        Returns
        -------
        Dict[str, np.ndarray]
            Dictionary containing:
                - 'prediction': Model predictions (shape: [n_samples, n_tasks])
                - 'confidence': Prediction confidences (shape: [n_samples, n_tasks])
                - 'variance': Prediction variances (shape: [n_samples, n_tasks])

        """
        self._check_is_fitted()

        # Convert to PyTorch Geometric format and create loader
        X, _ = self._validate_inputs(X)
        dataset = self._convert_to_pytorch_data(X)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=False)

        # Make predictions
        self.model.eval()
        predictions = []
        confidences = []
        variances = []
        with torch.no_grad():
            for batch in loader:
                batch = batch.to(self.device)
                out = self.model(batch)
                predictions.append(out["prediction"].cpu().numpy())
                confidences.append(out["confidence"].cpu().numpy())
                variances.append(out["variance"].cpu().numpy())

        return {
            "prediction": np.concatenate(predictions, axis=0),
            "confidence": np.concatenate(confidences, axis=0),
            "variance": np.concatenate(variances, axis=0),
        }

    def train_epoch(self, train_loader, optimizer):
        """Training logic for one epoch.

        Args:
            train_loader: DataLoader containing training data
            optimizer: Optimizer instance for model parameter updates

        Returns:
            list: List of loss values for each training step
        """
        self.model.train()
        losses = []

        iterator = (
            tqdm(train_loader, desc="Training", leave=False)
            if self.verbose
            else train_loader
        )

        for batch in iterator:
            batch = batch.to(self.device)
            optimizer.zero_grad()

            # Forward pass and loss computation
            loss = self.model.compute_loss(batch, self.criterion)

            # Backward pass
            loss.backward()

            # Compute gradient norm if gradient clipping is enabled
            if self.grad_clip_value is not None:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip_value)

            optimizer.step()

            losses.append(loss.item())

            # Update progress bar if using tqdm
            if self.verbose:
                iterator.set_postfix({"loss": f"{loss.item():.4f}"})

        return losses

    def save_model(self, path: str) -> None:
        """Save the model to disk.

        Parameters
        ----------
        path : str
            Path where to save the model
        """
        if not self.is_fitted_:
            raise ValueError("Model must be fitted before saving")

        if not path.endswith((".pt", ".pth")):
            raise ValueError("Save path should end with '.pt' or '.pth'")

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

        model_name = os.path.splitext(os.path.basename(path))[0]
        save_dict = {
            "model_state_dict": self.model.state_dict(),
            "hyperparameters": self.get_params(),
            "fitting_epoch": self.fitting_epoch,
            "fitting_loss": self.fitting_loss,
            "fitting_loss_mean": self.fitting_loss_mean,
            "model_name": model_name,
            "date_saved": datetime.datetime.now().isoformat(),
            "version": getattr(self, "__version__", "1.0.0"),
        }
        torch.save(save_dict, path)

    def load_model(self, path: str, repo: Optional[str] = None) -> "GREAMolecularPredictor":
        """Load a saved model from disk or download from HuggingFace hub.

        Parameters
        ----------
        path : str
            Path to the saved model file or desired local path for downloaded model
        repo : str, optional
            HuggingFace model repository ID (e.g., 'username/model-name')
            If provided and local path doesn't exist, will attempt to download from hub

        Returns
        -------
        self : GREAMolecularPredictor
            Updated model instance with loaded weights and parameters

        Raises
        ------
        FileNotFoundError
            If the model file doesn't exist locally and no repo is provided,
            or if download from repo fails
        ValueError
            If the saved file is corrupted or incompatible
        """
        # First try to load from local path
        if os.path.exists(path):
            try:
                checkpoint = torch.load(path, map_location=self.device)
            except Exception as e:
                raise ValueError(f"Error loading model from {path}: {str(e)}")

        # If local file doesn't exist and repo is provided, try downloading
        elif repo is not None:
            try:
                from huggingface_hub import hf_hub_download
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

                # Download from HuggingFace using specified parameters
                model_name = os.path.splitext(os.path.basename(path))[0]
                downloaded_path = hf_hub_download(
                    repo_id=repo,
                    filename=model_name,
                    local_dir=os.path.dirname(path),
                    local_dir_use_symlinks=False,
                )

                # Load the downloaded model
                checkpoint = torch.load(downloaded_path, map_location=self.device)

            except Exception as e:
                if os.path.exists(path):
                    os.remove(path)  # Clean up partial downloads
                raise FileNotFoundError(
                    f"Failed to download model from repository '{repo}': {str(e)}"
                )

        # If neither local file exists nor repo provided
        else:
            raise FileNotFoundError(f"No model file found at '{path}' and no repository provided")

        try:
            # Validate checkpoint contents
            required_keys = {
                "model_state_dict",
                "hyperparameters",
                "fitting_loss",
                "fitting_epoch",
                "model_name",
            }
            if not all(key in checkpoint for key in required_keys):
                missing_keys = required_keys - set(checkpoint.keys())
                raise ValueError(f"Checkpoint missing required keys: {missing_keys}")

            # Validate compatibility of hyperparameters
            for key, value in checkpoint["hyperparameters"].items():
                if hasattr(self, key) and getattr(self, key) != value:
                    warnings.warn(
                        f"Loaded model has different {key} ({value}) "
                        f"than current instance ({getattr(self, key)}). "
                        "Updating to match loaded model."
                    )
                    setattr(self, key, value)

            # Update model state
            if not hasattr(self, 'model') or self.model is None:
                raise ValueError("Model not initialized. Please initialize model before loading weights.")
            
            try:
                self.model.load_state_dict(checkpoint["model_state_dict"])
            except Exception as e:
                raise ValueError(f"Failed to load model state dict: {str(e)}")

            # Update training state
            self.fitting_epoch = checkpoint.get("fitting_epoch", 0)
            self.fitting_loss = checkpoint.get("fitting_loss", float("inf"))
            self.model_name = checkpoint['model_name']
            self.is_fitted_ = True

            # Move model to correct device
            self.model = self.model.to(self.device)

            print(f"Model successfully loaded from {'repository' if repo else 'local path'}")
            return self

        except Exception as e:
            raise ValueError(f"Error loading model checkpoint: {str(e)}")

        finally:
            # Clean up any temporary files
            if repo is not None and os.path.exists(downloaded_path) and downloaded_path != path:
                try:
                    os.remove(downloaded_path)
                except Exception:
                    pass
