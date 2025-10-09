import os
import numpy as np
from tqdm import tqdm
from typing import Optional, Union, Dict, Any, Tuple, List, Callable, Literal
import warnings

import torch
from torch_geometric.loader import DataLoader
from torch_geometric.data import Data

from .architecture import GNN
from ...base import BaseMolecularPredictor
from ...utils import graph_from_smiles
from ...utils.search import (
    DEFAULT_GNN_SEARCH_SPACES,
    suggest_parameter,
    ParameterSpec,
    ParameterType,
    parse_list_params,
)

class GNNMolecularPredictor(BaseMolecularPredictor):
    """This predictor implements a GNN model for molecular property prediction tasks.
    """
    def __init__(
        self,
        # model parameters
        num_tasks: int = 1,
        task_type: str = "classification",
        num_layer: int = 5,
        emb_dim: int = 300,
        gnn_type: str = "gin-virtual",
        drop_ratio: float = 0.5,
        norm_layer: str = "batch_norm",
        graph_pooling: str = "sum",
        # augmented features
        augmented_feature: Optional[list[Literal["morgan", "maccs"]]] = ["morgan", "maccs"],
        # training parameters
        batch_size: int = 128,
        epochs: int = 500,
        loss_criterion: Optional[Callable] = None,
        evaluate_criterion: Optional[Union[str, Callable]] = None,
        evaluate_higher_better: Optional[bool] = None,
        learning_rate: float = 0.001,
        grad_clip_value: Optional[float] = None,
        weight_decay: float = 0.0,
        patience: int = 50,
        # scheduler
        use_lr_scheduler: bool = True,
        scheduler_factor: float = 0.5,
        scheduler_patience: int = 5,
        # others
        device: Optional[str] = None,
        verbose: bool = False,
        model_name: str = "GNNMolecularPredictor",
    ): 
        super().__init__(num_tasks=num_tasks, task_type=task_type, model_name=model_name, device=device)
        # Model hyperparameters
        self.num_layer = num_layer
        self.emb_dim = emb_dim
        self.gnn_type = gnn_type
        self.drop_ratio = drop_ratio
        self.norm_layer = norm_layer
        self.graph_pooling = graph_pooling
        # Augmented features
        if augmented_feature is not None:
            valid_augmented_feature = {"morgan", "maccs"}
            invalid_fps = set(augmented_feature) - valid_augmented_feature
            if invalid_fps:
                raise ValueError(
                    f"Invalid augmented types: {invalid_fps}. "
                    f"Valid options are: {list(valid_augmented_feature)}"
                )
        self.augmented_feature = augmented_feature
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
        self.loss_criterion = loss_criterion if loss_criterion is not None else self._load_default_criterion()
        self._setup_evaluation(evaluate_criterion, evaluate_higher_better)

        self.fitting_loss = []
        self.fitting_epoch = 0
        self.verbose = verbose
        self.model_class = GNN

    @staticmethod
    def _get_param_names() -> List[str]:
        """Get parameter names for the estimator.

        Returns
        -------
        List[str]
            List of parameter names that can be used for model configuration.
        """
        return [
            # Model Hyperparameters
            "num_tasks",
            "task_type",
            "num_layer",
            "emb_dim",
            "gnn_type",
            "drop_ratio",
            "norm_layer",
            "graph_pooling",
            # Augmented Features
            "augmented_feature",
            # Training Parameters
            "batch_size",
            "epochs",
            "learning_rate",
            "weight_decay",
            "patience",
            "grad_clip_value",
            "loss_criterion",
            # Evaluation Parameters
            "evaluate_name",
            "evaluate_criterion",
            "evaluate_higher_better",
            # Scheduler Parameters
            "use_lr_scheduler",
            "scheduler_factor",
            "scheduler_patience",
            # Other Parameters
            "fitting_epoch",
            "fitting_loss",
            "device",
            "verbose"
        ]
    
    def _get_model_params(self, checkpoint: Optional[Dict] = None) -> Dict[str, Any]:
        """Get model parameters either from checkpoint or current instance.
        
        Parameters
        ----------
        checkpoint : Optional[Dict]
            Checkpoint containing model hyperparameters
            
        Returns
        -------
        Dict[str, Any]
            Dictionary of model parameters
            
        Raises
        ------
        ValueError
            If checkpoint contains invalid parameters
        """
        if checkpoint is not None:
            if "hyperparameters" not in checkpoint:
                raise ValueError("Checkpoint missing 'hyperparameters' key")
                
            hyperparameters = checkpoint["hyperparameters"]
            
            # Define required parameters
            required_params = {
                "num_tasks", "num_layer", "emb_dim", "gnn_type",
                "drop_ratio", "norm_layer", "graph_pooling", 'augmented_feature'
            }
            
            # Validate parameters
            # invalid_params = set(hyperparameters.keys()) - required_params
            
            # Get parameters with fallback to instance values
            return {
                "num_tasks": hyperparameters.get("num_tasks", self.num_tasks),
                "num_layer": hyperparameters.get("num_layer", self.num_layer),
                "emb_dim": hyperparameters.get("emb_dim", self.emb_dim),
                "gnn_type": hyperparameters.get("gnn_type", self.gnn_type),
                "drop_ratio": hyperparameters.get("drop_ratio", self.drop_ratio),
                "norm_layer": hyperparameters.get("norm_layer", self.norm_layer),
                "graph_pooling": hyperparameters.get("graph_pooling", self.graph_pooling),
                "augmented_feature": hyperparameters.get("augmented_feature", self.augmented_feature)
            }
        else:
            # Use current instance parameters
            return {
                "num_tasks": self.num_tasks,
                "num_layer": self.num_layer,
                "emb_dim": self.emb_dim,
                "gnn_type": self.gnn_type,
                "drop_ratio": self.drop_ratio,
                "norm_layer": self.norm_layer,
                "graph_pooling": self.graph_pooling,
                "augmented_feature": self.augmented_feature
            }
        
    def _convert_to_pytorch_data(self, X, y=None):
        """Convert numpy arrays to PyTorch Geometric data format.
        """
        if self.verbose:
            iterator = tqdm(enumerate(X), desc="Converting molecules to graphs", total=len(X))
        else:
            iterator = enumerate(X)

        pyg_graph_list = []
        for idx, smiles in iterator:
            if y is not None:
                properties = y[idx]
            else:
                properties = None
            graph = graph_from_smiles(smiles, properties, self.augmented_feature)
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
   
            if graph["morgan"] is not None:
                g.morgan = torch.tensor(graph["morgan"], dtype=torch.int8).view(1, -1)
                del graph["morgan"]
            
            if graph["maccs"] is not None:
                g.maccs = torch.tensor(graph["maccs"], dtype=torch.int8).view(1, -1)
                del graph["maccs"]

            pyg_graph_list.append(g)

        return pyg_graph_list
    
    def _setup_optimizers(self) -> Tuple[torch.optim.Optimizer, Optional[Any]]:
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
    
    def _get_default_search_space(self):
        """Get the default hyperparameter search space.
        
        Returns
        -------
        Dict[str, ParameterSpec]
            Dictionary mapping parameter names to their search space specifications
        """
        return DEFAULT_GNN_SEARCH_SPACES

    def autofit(
        self,
        X_train: List[str],
        y_train: Optional[Union[List, np.ndarray]],
        X_val: Optional[List[str]] = None,
        y_val: Optional[Union[List, np.ndarray]] = None,
        X_unlbl: Optional[List[str]] = None,
        search_parameters: Optional[Dict[str, ParameterSpec]] = None,
        n_trials: int = 10,
    ) -> "GNNMolecularPredictor":
        """Automatically find the best hyperparameters using Optuna optimization."""
        import optuna
        # Default search parameters
        default_search_parameters = self._get_default_search_space()
        if search_parameters is None:
            search_parameters = default_search_parameters
        else:
            # Validate search parameter keys
            invalid_params = set(search_parameters.keys()) - set(default_search_parameters.keys())
            if invalid_params:
                raise ValueError(
                    f"Invalid search parameters: {invalid_params}. "
                    f"Valid parameters are: {list(default_search_parameters.keys())}"
                )
                
        if self.verbose:
            all_params = set(self._get_param_names())
            searched_params = set(search_parameters.keys())
            non_searched_params = all_params - searched_params
            
            print("\nParameter Search Configuration:")
            print("-" * 50)
            
            print("\n Parameters being searched:")
            for param in sorted(searched_params):
                spec = search_parameters[param]
                if spec.param_type == ParameterType.CATEGORICAL:
                    print(f"  • {param}: {spec.value_range}")
                else:
                    print(f"  • {param}: [{spec.value_range[0]}, {spec.value_range[1]}]")
                    
            print("\n Fixed parameters (not being searched):")
            for param in sorted(non_searched_params):
                value = getattr(self, param, "N/A")
                print(f"  • {param}: {value}")
            
            print("\n" + "-" * 50)

            print(f"\nStarting hyperparameter optimization using {self.evaluate_name} metric")
            print(f"Direction: {'maximize' if self.evaluate_higher_better else 'minimize'}")
            print(f"Number of trials: {n_trials}")

        # Variables to track best state
        best_score = float('-inf') if self.evaluate_higher_better else float('inf')
        best_state_dict = None
        best_trial_params = None
        best_loss = None
        best_epoch = None
        
        def objective(trial):
            nonlocal best_score, best_state_dict, best_trial_params, best_loss, best_epoch
            
            # Define hyperparameters to optimize using the parameter specifications
            params = {}
            for param_name, param_spec in search_parameters.items():
                try:
                    params[param_name] = suggest_parameter(trial, param_name, param_spec)
                except Exception as e:
                    print(f"Error suggesting parameter {param_name}: {str(e)}")
                    return float('inf')
            
            try:
                # Update model parameters and train
                if "augmented_feature" in params:
                    params['augmented_feature'] = parse_list_params(params['augmented_feature'])
                self.set_params(**params)
                self.fit(X_train, y_train, X_val, y_val, X_unlbl)
                
                # Get evaluation score
                eval_data = (X_val if X_val is not None else X_train)
                eval_labels = (y_val if y_val is not None else y_train)
                eval_results = self.predict(eval_data)
                score = float(self.evaluate_criterion(eval_labels, eval_results['prediction']))
                
                # Update best state if current score is better
                is_better = (
                    score > best_score if self.evaluate_higher_better 
                    else score < best_score
                )
                
                if is_better:
                    best_score = score
                    best_state_dict = {
                        'model': self.model.state_dict(),
                        'architecture': self._get_model_params()
                    }
                    best_trial_params = params.copy()
                    best_loss = self.fitting_loss.copy()  # Added .copy() for safety
                    best_epoch = self.fitting_epoch
                
                if self.verbose:
                    print(
                        f"Trial {trial.number}: {self.evaluate_name} = {score:.4f} "
                        f"({'better' if is_better else 'worse'} than best = {best_score:.4f})"
                    )
                    print("Current parameters:")
                    for param_name, value in params.items():
                        print(f"  {param_name}: {value}")
                
                # Return score (negated if higher is better, since Optuna minimizes)
                return -score if self.evaluate_higher_better else score
                
            except Exception as e:
                print(f"Trial {trial.number} failed with error: {str(e)}")
                return float('inf')
        
        # Create study with optional output control
        optuna.logging.set_verbosity(
            optuna.logging.INFO if self.verbose else optuna.logging.WARNING
        )
        
        # Create and run study
        study = optuna.create_study(
            direction="minimize",
            study_name=f"{self.model_name}_optimization"
        )
        
        # try:
        study.optimize(
            objective,
            n_trials=n_trials,
            catch=(Exception,),
            show_progress_bar=self.verbose
        )
        
        if best_state_dict is not None:
            self.set_params(**best_trial_params)
            # Initialize model with saved architecture parameters
            self._initialize_model(self.model_class, self.device)
            # Load the saved state dict
            self.model.load_state_dict(best_state_dict['model'])
            self.fitting_loss = best_loss
            self.fitting_epoch = best_epoch
            self.is_fitted_ = True
            
            if self.verbose:
                print(f"\nOptimization completed successfully:")
                print(f"Best {self.evaluate_name}: {best_score:.4f}")
    
                eval_data = (X_val if X_val is not None else X_train)
                eval_labels = (y_val if y_val is not None else y_train)
                eval_results = self.predict(eval_data)
                score = float(self.evaluate_criterion(eval_labels, eval_results['prediction']))
                print('post score is: ', score)

                print("\nBest parameters:")
                for param, value in best_trial_params.items():
                    param_spec = search_parameters[param]
                    print(f"  {param}: {value} (type: {param_spec.param_type.value})")
                
                # Print optimization statistics
                print("\nOptimization statistics:")
                print(f"  Number of completed trials: {len(study.trials)}")
                print(f"  Number of pruned trials: {len(study.get_trials(states=[optuna.trial.TrialState.PRUNED]))}")
                print(f"  Number of failed trials: {len(study.get_trials(states=[optuna.trial.TrialState.FAIL]))}")
            else:
                raise RuntimeError("No successful trials completed during optimization")
                
        # except KeyboardInterrupt:
        #     print("\nOptimization interrupted by user. Saving best results so far...")
        #     if best_state_dict is not None:
        #         self.set_params(**best_trial_params)
        #         # CHANGE: Use same restoration logic here
        #         self._initialize_model(self.model_class, self.device)
        #         self.model.load_state_dict(best_state_dict['model'])
        #         self.fitting_loss = best_loss
        #         self.fitting_epoch = best_epoch
        #         self.is_fitted_ = True
        
        return self
    
    def fit(
        self,
        X_train: List[str],
        y_train: Optional[Union[List, np.ndarray]],
        X_val: Optional[List[str]] = None,
        y_val: Optional[Union[List, np.ndarray]] = None,
        X_unlbl: Optional[List[str]] = None,
    ) -> "GNNMolecularPredictor":
        """Fit the model to the training data with optional validation set.

        Parameters
        ----------
        X_train : List[str]
            Training set input molecular structures as SMILES strings
        y_train : Union[List, np.ndarray]
            Training set target values for property prediction
        X_val : List[str], optional
            Validation set input molecular structures as SMILES strings.
            If None, training data will be used for validation
        y_val : Union[List, np.ndarray], optional
            Validation set target values. Required if X_val is provided
        X_unlbl : List[str], optional
            Unlabeled set input molecular structures as SMILES strings.
            
        Returns
        -------
        self : GNNMolecularPredictor
            Fitted estimator
        """
        if (X_val is None) != (y_val is None):
            raise ValueError(
                "Both X_val and y_val must be provided for validation. "
                f"Got X_val={X_val is not None}, y_val={y_val is not None}"
            )

        self._initialize_model(self.model_class, self.device)
        self.model.initialize_parameters()
        self.model = self.model.to(self.device)
        optimizer, scheduler = self._setup_optimizers()
        
        # Prepare datasets and loaders
        X_train, y_train = self._validate_inputs(X_train, y_train)
        train_dataset = self._convert_to_pytorch_data(X_train, y_train)
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=0
        )

        if X_val is None or y_val is None:
            val_loader = train_loader
            warnings.warn(
                "No validation set provided. Using training set for validation. "
                "This may lead to overfitting.",
                UserWarning
            )
        else:
            X_val, y_val = self._validate_inputs(X_val, y_val)
            val_dataset = self._convert_to_pytorch_data(X_val, y_val)
            val_loader = DataLoader(
                val_dataset,
                batch_size=self.batch_size,
                shuffle=False,
                num_workers=0
            )

        # Initialize training state
        self.fitting_loss = []
        self.fitting_epoch = 0
        best_state_dict = None
        best_eval = float('-inf') if self.evaluate_higher_better else float('inf')
        cnt_wait = 0

        for epoch in range(self.epochs):
            # Training phase
            train_losses = self._train_epoch(train_loader, optimizer)
            self.fitting_loss.append(np.mean(train_losses))

            # Validation phase
            current_eval = self._evaluation_epoch(val_loader)
            
            if scheduler:
                scheduler.step(current_eval)
            
            # Model selection (check if current evaluation is better)
            is_better = (
                current_eval > best_eval if self.evaluate_higher_better
                else current_eval < best_eval
            )
            
            if is_better:
                self.fitting_epoch = epoch
                best_eval = current_eval
                best_state_dict = self.model.state_dict()
                cnt_wait = 0
            else:
                cnt_wait += 1
                if cnt_wait > self.patience:
                    if self.verbose:
                        print(f"Early stopping triggered after {epoch} epochs")
                    break
            
            if self.verbose and epoch % 10 == 0:
                print(
                    f"Epoch {epoch}: Loss = {np.mean(train_losses):.4f}, "
                    f"{self.evaluate_name} = {current_eval:.4f}, "
                    f"Best {self.evaluate_name} = {best_eval:.4f}"
                )

        # Restore best model
        if best_state_dict is not None:
            self.model.load_state_dict(best_state_dict)
        else:
            warnings.warn(
                "No improvement was achieved during training. "
                "The model may not be fitted properly.",
                UserWarning
            )

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

        """
        self._check_is_fitted()

        # Convert to PyTorch Geometric format and create loader
        X, _ = self._validate_inputs(X)
        dataset = self._convert_to_pytorch_data(X)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=False)

        if self.model is None:
            raise RuntimeError("Model not initialized")
        # Make predictions
        self.model = self.model.to(self.device)
        self.model.eval()
        predictions = []
        with torch.no_grad():
            for batch in tqdm(loader, disable=not self.verbose):
                batch = batch.to(self.device)
                out = self.model(batch)
                predictions.append(out["prediction"].cpu().numpy())
        return {
            "prediction": np.concatenate(predictions, axis=0),
        }

    def _evaluation_epoch(
        self,
        loader: DataLoader,
    ) -> float:
        """Evaluate the model on given data.
        
        Parameters
        ----------
        loader : DataLoader
            DataLoader containing evaluation data
        train_losses : List[float]
            Training losses from current epoch
            
        Returns
        -------
        float
            Evaluation metric value (adjusted for higher/lower better)
        """
        self.model.eval()
        y_pred_list = []
        y_true_list = []
        
        with torch.no_grad():
            for batch in loader:
                batch = batch.to(self.device)
                out = self.model(batch)
                y_pred_list.append(out["prediction"].cpu().numpy())
                y_true_list.append(batch.y.cpu().numpy())
        
        y_pred = np.concatenate(y_pred_list, axis=0)
        y_true = np.concatenate(y_true_list, axis=0)
        
        # Compute metric
        metric_value = float(self.evaluate_criterion(y_true, y_pred))
        
        # Adjust metric value based on higher/lower better
        return metric_value

    def _train_epoch(self, train_loader, optimizer):
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
            loss = self.model.compute_loss(batch, self.loss_criterion)

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