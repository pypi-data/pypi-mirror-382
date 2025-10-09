import gc
import os
from typing import Dict, List, Union, Optional, Any, Tuple
from tqdm import tqdm

import torch
import torch.nn as nn
from torch.amp import autocast
import numpy as np

from .losses import DICELoss, CrossEntropyLoss, FocalLoss, TverskyLoss


class PerformanceModels:
    """
    A class for evaluating the performance of segmentation models.
    
    This class handles model evaluation on test datasets, calculating various
    metrics such as DICE, Jaccard, sensitivity, and specificity.
    """
    
    def __init__(
        self, 
        model: nn.Module, 
        test_dataset: torch.utils.data.DataLoader, 
        config: Dict[str, Any]
    ):
        """
        Initialize the PerformanceModels class.
        
        Args:
            model: The neural network model to evaluate
            test_dataset: DataLoader containing test data
            config: Configuration dictionary with evaluation parameters

        """
        self.model = model
        self.test_dataset = test_dataset
        self.config = config
        
        self.device = torch.device(self.config.get('Device', 'cpu'))
        # Move model to device and set to evaluation mode
        self.model.to(self.device)
        self.model.eval()
        
        # Get loss function
        self.loss_fn = self.loss_handling()
        
        # Run evaluation
        self.evaluate()
    
    def loss_handling(self) -> nn.Module:
        """
        Select and configure the appropriate loss function based on configuration.
        
        Returns:
            The configured loss function
        
        Raises:
            ValueError: If an unknown loss function is specified
        """
        loss_fn = self.config.get('Loss function', 'DICE')

        match loss_fn:
            case 'DICE':
                return DICELoss(
                    smooth=self.config.get('Smooth', 1.0),
                    reduction=self.config.get('Reduction', 'mean')
                )

            case 'CrossEntropy':
                return CrossEntropyLoss(reduction=self.config.get('Reduction', 'mean'))

            case 'Focal':
                return FocalLoss(
                    alpha=self.config.get('Alpha', 0.25),
                    gamma=self.config.get('Gamma', 2.0),
                    reduction=self.config.get('Reduction', 'mean')
                )
            
            case 'Tversky':
                return TverskyLoss(
                    alpha=self.config.get('Alpha', 0.5),
                    beta=self.config.get('Beta', 0.5),
                    smooth=self.config.get('Smooth', 1.0),
                    reduction=self.config.get('Reduction', 'mean')
                )

            case _:
                raise ValueError(f"Unknown loss function: {loss_fn}")
    
    def evaluate(self) -> None:
        """
        Evaluate the model on the test dataset and calculate performance metrics.
        
        This method processes the test dataset, calculates metrics for each batch,
        and aggregates results both globally and per class.
        """
        self.save_results = self.config.get('Save results', False)
        self.smooth = self.config.get('Smooth', 1.0)

        loss_results: List[float] = []

        # Initialize lists for global metrics
        dice_results: List[float] = []
        jaccard_results: List[float] = []
        sensitivity_results: List[float] = []
        specificity_results: List[float] = []

        # Initialize lists for per-class metrics
        is_single_class = isinstance(self.config.get("Single class test"), int)
        num_classes = 1 if is_single_class else self.config.get('Number of classes', 1)

        dice_per_class: List[List[float]] = [[] for _ in range(num_classes)]
        jaccard_per_class: List[List[float]] = [[] for _ in range(num_classes)]
        sensitivity_per_class: List[List[float]] = [[] for _ in range(num_classes)]
        specificity_per_class: List[List[float]] = [[] for _ in range(num_classes)]

        for data_batch in tqdm(self.test_dataset, desc="Testing model's performance"):
            # Unpack batch data (images, ground truth masks)
            images, gt_masks = data_batch

            images = images.to(self.device)
            gt_masks = gt_masks.to(self.device)

            with torch.no_grad():
                # Forward pass with or without mixed precision
                if self.config.get("AMixPre", False):

                    with autocast(self.device.type):
                        y_pred = self.model(images)
                        loss = self.loss_fn(y_pred, gt_masks)
                        loss = loss if not torch.isnan(loss) else torch.tensor(0.0, device=self.device)
                else:
                    y_pred = self.model(images)
                    loss = self.loss_fn(y_pred, gt_masks)
                    loss = loss if not torch.isnan(loss) else torch.tensor(0.0, device=self.device)

                # Class selection
                if is_single_class:
                    class_idx = self.config["Single class test"]
                    y_pred = y_pred[:, class_idx:class_idx+1]
                else:
                    y_pred = y_pred

                y_true = gt_masks.float()
                if self.config.get('Loss function', None) in ['Focal', 'CrossEntropy']:
                    y_pred = torch.sigmoid(y_pred)
                y_pred = y_pred.float()

                # Create mask for valid pixels (ignoring specific values)
                ignore_value = torch.tensor(self.config.get('Ignored value',0.6), device=self.device)
                mask = (y_true != ignore_value).float()

                # Threshold predictions
                y_pred = torch.where(y_pred > 0.5, torch.ones_like(y_pred), torch.zeros_like(y_pred))

                # Calculate batch metrics
                metrics = self._calculate_batch_metrics(y_true, y_pred, mask)
                
                # Extract metrics
                dice_batch, jaccard_batch, sensitivity_batch, specificity_batch = metrics
                dice, jaccard, sensitivity, specificity = self._aggregate_batch_metrics(metrics)

                # Store per-class metrics
                for c in range(num_classes):
                    dice_per_class[c].extend(dice_batch[:, c].tolist())
                    jaccard_per_class[c].extend(jaccard_batch[:, c].tolist())
                    sensitivity_per_class[c].extend(sensitivity_batch[:, c].tolist())
                    specificity_per_class[c].extend(specificity_batch[:, c].tolist())

                # Handle NaN values
                dice = torch.where(torch.isnan(dice), torch.tensor(0.0, device=self.device), dice)
                jaccard = torch.where(torch.isnan(jaccard), torch.tensor(0.0, device=self.device), jaccard)
                sensitivity = torch.where(torch.isnan(sensitivity), torch.tensor(0.0, device=self.device), sensitivity)
                specificity = torch.where(torch.isnan(specificity), torch.tensor(0.0, device=self.device), specificity)

                # Save global metrics
                loss_results.append(loss.item())
                dice_results.extend(dice.tolist())
                jaccard_results.extend(jaccard.tolist())
                sensitivity_results.extend(sensitivity.tolist())
                specificity_results.extend(specificity.tolist())

        # Convert to numpy arrays
        loss_results_np = np.array(loss_results)
        dice_results_np = np.array(dice_results)
        jaccard_results_np = np.array(jaccard_results)
        sensitivity_results_np = np.array(sensitivity_results)
        specificity_results_np = np.array(specificity_results)

        # Convert per-class metrics to numpy arrays
        dice_per_class_np = [np.array(class_results) for class_results in dice_per_class]
        jaccard_per_class_np = [np.array(class_results) for class_results in jaccard_per_class]
        sensitivity_per_class_np = [np.array(class_results) for class_results in sensitivity_per_class]
        specificity_per_class_np = [np.array(class_results) for class_results in specificity_per_class]

        # Print global metrics
        self._print_global_metrics(loss_results_np, dice_results_np, jaccard_results_np, 
                                  sensitivity_results_np, specificity_results_np)

        # Print per-class metrics
        self._print_class_metrics(num_classes, dice_per_class_np, jaccard_per_class_np,
                                 sensitivity_per_class_np, specificity_per_class_np)

        # Save results if requested
        if self.save_results:
            self._save_results(num_classes, loss_results_np, dice_results_np, jaccard_results_np,
                              sensitivity_results_np, specificity_results_np, dice_per_class_np,
                              jaccard_per_class_np, sensitivity_per_class_np, specificity_per_class_np)

        # Clean up memory
        self._cleanup_memory()
    
    def _calculate_batch_metrics(
        self, 
        y_true: torch.Tensor, 
        y_pred: torch.Tensor, 
        mask: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Calculate metrics for a single batch using simplified approach.
        
        Args:
            y_true: Ground truth segmentation masks [B, C, H, W]
            y_pred: Predicted segmentation masks [B, C, H, W]
            mask: Mask of valid pixels [B, C, H, W]
            
        Returns:
            Tuple containing dice, jaccard, sensitivity, and specificity tensors [B, C]
        """
        # Apply mask to both predictions and targets
        y_true_masked = y_true * mask
        y_pred_masked = y_pred * mask
        
        # Calculate confusion matrix components
        tp = torch.sum(y_true_masked * y_pred_masked, dim=(2, 3))
        fp = torch.sum((1 - y_true_masked) * y_pred_masked, dim=(2, 3))
        fn = torch.sum(y_true_masked * (1 - y_pred_masked), dim=(2, 3))
        tn = torch.sum((1 - y_true_masked) * (1 - y_pred_masked), dim=(2, 3))
        
        # Calculate metrics (smooth handles all edge cases automatically!)
        dice_batch = (2 * tp + self.smooth) / (2 * tp + fp + fn + self.smooth)
        jaccard_batch = (tp + self.smooth) / (tp + fp + fn + self.smooth)
        sensitivity_batch = (tp + self.smooth) / (tp + fn + self.smooth)
        specificity_batch = (tn + self.smooth) / (tn + fp + self.smooth)
        
        return dice_batch, jaccard_batch, sensitivity_batch, specificity_batch
    
    def _aggregate_batch_metrics(
        self, 
        metrics: Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Aggregate batch metrics by averaging across the channel dimension.
        
        Args:
            metrics: Tuple of batch metrics (dice, jaccard, sensitivity, specificity)
            
        Returns:
            Tuple of aggregated metrics
        """
        dice_batch, jaccard_batch, sensitivity_batch, specificity_batch = metrics
        
        dice = torch.mean(dice_batch, dim=1)
        jaccard = torch.mean(jaccard_batch, dim=1)
        sensitivity = torch.mean(sensitivity_batch, dim=1)
        specificity = torch.mean(specificity_batch, dim=1)
        
        return dice, jaccard, sensitivity, specificity
    
    def _print_global_metrics(
        self, 
        loss_results: np.ndarray, 
        dice_results: np.ndarray, 
        jaccard_results: np.ndarray,
        sensitivity_results: np.ndarray, 
        specificity_results: np.ndarray
    ) -> None:
        """
        Print global performance metrics.
        
        Args:
            loss_results: Array of loss values
            dice_results: Array of Dice coefficient values
            jaccard_results: Array of Jaccard index values
            sensitivity_results: Array of sensitivity values
            specificity_results: Array of specificity values
        """
        print("\nGlobal Performance Metrics:")
        print(f"Loss mean: {np.mean(loss_results):.5f}, std: {np.std(loss_results):.5f}")
        print(f"Dice Coefficient mean: {np.mean(dice_results):.5f}, std: {np.std(dice_results):.5f}")
        print(f"Jaccard Index mean: {np.mean(jaccard_results):.5f}, std: {np.std(jaccard_results):.5f}")
        print(f"Sensitivity mean: {np.mean(sensitivity_results):.5f}, std: {np.std(sensitivity_results):.5f}")
        print(f"Specificity mean: {np.mean(specificity_results):.5f}, std: {np.std(specificity_results):.5f}")
    
    def _print_class_metrics(
        self, 
        num_classes: int, 
        dice_per_class: List[np.ndarray], 
        jaccard_per_class: List[np.ndarray],
        sensitivity_per_class: List[np.ndarray], 
        specificity_per_class: List[np.ndarray]
    ) -> None:
        """
        Print per-class performance metrics.
        
        Args:
            num_classes: Number of classes
            dice_per_class: List of Dice coefficient arrays per class
            jaccard_per_class: List of Jaccard index arrays per class
            sensitivity_per_class: List of sensitivity arrays per class
            specificity_per_class: List of specificity arrays per class
        """
        print("\nPer-Class Performance Metrics:")
        for c in range(num_classes):
            print(f"\nClass {c}:")
            print(f"Dice mean: {np.mean(dice_per_class[c]):.5f}, std: {np.std(dice_per_class[c]):.5f}")
            print(f"Jaccard mean: {np.mean(jaccard_per_class[c]):.5f}, std: {np.std(jaccard_per_class[c]):.5f}")
            print(f"Sensitivity mean: {np.mean(sensitivity_per_class[c]):.5f}, std: {np.std(sensitivity_per_class[c]):.5f}")
            print(f"Specificity mean: {np.mean(specificity_per_class[c]):.5f}, std: {np.std(specificity_per_class[c]):.5f}")
    
    def _save_results(
        self, 
        num_classes: int, 
        loss_results: np.ndarray, 
        dice_results: np.ndarray, 
        jaccard_results: np.ndarray,
        sensitivity_results: np.ndarray, 
        specificity_results: np.ndarray,
        dice_per_class: List[np.ndarray], 
        jaccard_per_class: List[np.ndarray],
        sensitivity_per_class: List[np.ndarray], 
        specificity_per_class: List[np.ndarray]
    ) -> None:
        """
        Save evaluation results to disk.
        
        Args:
            num_classes: Number of classes
            loss_results: Array of loss values
            dice_results: Array of Dice coefficient values
            jaccard_results: Array of Jaccard index values
            sensitivity_results: Array of sensitivity values
            specificity_results: Array of specificity values
            dice_per_class: List of Dice coefficient arrays per class
            jaccard_per_class: List of Jaccard index arrays per class
            sensitivity_per_class: List of sensitivity arrays per class
            specificity_per_class: List of specificity arrays per class
        """
        drive_dir = self.config.get('drive_dir', '.')
        
        if not os.path.exists(f"{drive_dir}/results"):
            os.makedirs(f"{drive_dir}/results")

        filename_base = f"{drive_dir}/results/{self.config.get('Dataset', '')}_{self.config.get('Model', '')}_{self.config.get('Loss function', 'DICE')}"

        # Save global metrics
        np.save(f"{filename_base}_Loss.npy", loss_results)
        np.save(f"{filename_base}_DICE_global.npy", dice_results)
        np.save(f"{filename_base}_Jaccard_global.npy", jaccard_results)
        np.save(f"{filename_base}_Sensitivity_global.npy", sensitivity_results)
        np.save(f"{filename_base}_Specificity_global.npy", specificity_results)

        # Save per-class metrics
        for c in range(num_classes):
            np.save(f"{filename_base}_DICE_class{c}.npy", dice_per_class[c])
            np.save(f"{filename_base}_Jaccard_class{c}.npy", jaccard_per_class[c])
            np.save(f"{filename_base}_Sensitivity_class{c}.npy", sensitivity_per_class[c])
            np.save(f"{filename_base}_Specificity_class{c}.npy", specificity_per_class[c])
    
    def _cleanup_memory(self) -> None:
        """
        Clean up memory by releasing tensors and running garbage collection.
        """
        gc.collect()
        torch.cuda.empty_cache()