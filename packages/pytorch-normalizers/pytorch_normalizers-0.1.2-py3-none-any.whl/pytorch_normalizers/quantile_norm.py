import torch
import torch.nn as nn
import numpy as np

class QuantileNorm(nn.Module):
    """
    A quantile normalizer that uses incremental updates to maintain a running quantile distribution.

    Args:
        numerical_features_sample: A sample of numerical features to initialize the quantile normalizer.
        num_buckets: Number of buckets to use for quantile normalization.
        step_size: Step size for incremental updates.
        eps: Small value to avoid division by zero.
        device: Device to use for the module.

    Usage::
        class MyModel(nn.Module):
            # numerical_features_sample can be a pd.DataFrame or torch.Tensor or np.ndarray
            def __init__(self, numerical_features_sample, num_buckets=9):
                super().__init__()
                self.input_normalizer = QuantileNorm(numerical_features_sample, num_buckets)
            
            def forward(self, x):
                x = self.input_normalizer(x)
                # rest of the model

    """
    def __init__(self, numerical_features_sample, num_buckets: int, step_size: float = 0.01, eps: float = 1e-5, device=None):
        super(QuantileNorm, self).__init__()
        if num_buckets < 2:
            raise ValueError("num_buckets must be >= 2")
        self.num_buckets = num_buckets
        self.step_size = step_size
        self.eps = eps
        device = device or "cpu"


        if isinstance(numerical_features_sample, torch.Tensor):
            sample = numerical_features_sample.to(device).float()
            if device is None:
                device = numerical_features_sample.device
        elif isinstance(numerical_features_sample, np.ndarray):
            sample = torch.from_numpy(numerical_features_sample).to(device).float()
        elif "DataFrame" in str(type(numerical_features_sample)):
            sample = torch.from_numpy(numerical_features_sample.values).to(device).float()
        else:
            raise ValueError("numerical_features_sample must be np.ndarray, torch.Tensor, or pd.DataFrame")

        self.dims = sample.shape[1]
        self.register_buffer('probs', torch.linspace(1 / (num_buckets + 1), num_buckets / (num_buckets + 1), num_buckets))
        
        means = torch.nanmean(sample, dim=0)
        diff = sample - means.unsqueeze(0)
        diff[torch.isnan(diff)] = 0.0
        count = torch.sum(~torch.isnan(sample), dim=0).float()
        var = torch.sum(diff ** 2, dim=0) / torch.clamp(count, min=1.0)
        stds = torch.sqrt(var) + self.eps

        normalized = (sample - means.unsqueeze(0)) / stds.unsqueeze(0)
        init_quantiles = torch.quantile(normalized, self.probs, dim=0).t()  # Transpose to (dims, num_buckets)
        self.register_buffer('quantiles', init_quantiles)
        
        #this is not trainable, just moving the scale so the default step_size makes sense on non outlier data
        self.register_buffer('initial_means', means)
        self.register_buffer('initial_stds', stds)

    def forward(self, x):
        if x.dim() != 2 or x.shape[1] != self.dims:
            raise ValueError("Expected input shape (batch_size, dims)")
        x = (x - self.initial_means) / self.initial_stds
        if self.training:
            batch_quantiles = torch.quantile(x, self.probs, dim=0).t()  # (dims, num_buckets)
            quantiles_to_use = batch_quantiles
            
            # Update running quantiles using the incremental shift
            below = x.unsqueeze(-1) < self.quantiles.unsqueeze(0)  # (batch, dims, num_buckets)
            fraction_below = below.float().mean(dim=0)  # (dims, num_buckets)
            update = self.step_size * (self.probs.view(1, -1) - fraction_below)  # (dims, num_buckets)
            self.quantiles += update
            # Sort to maintain order
            self.quantiles = torch.sort(self.quantiles, dim=-1).values
        else:
            quantiles_to_use = self.quantiles
        
        # Expand for batch compatibility in searchsorted
        qs_exp = quantiles_to_use.unsqueeze(0).expand(x.size(0), -1, -1).contiguous()  # (batch, dims, num_buckets)
        ps_exp = self.probs.view(1, 1, -1).expand(x.size(0), self.dims, -1)  # (batch, dims, num_buckets)
        v = x.unsqueeze(-1)  # (batch, dims, 1)
        idx = torch.searchsorted(qs_exp, v).squeeze(-1)  # (batch, dims)
        
        left_idx = torch.clamp(idx - 1, min=0, max=self.num_buckets - 1)
        right_idx = torch.clamp(idx, min=0, max=self.num_buckets - 1)
        
        left_idx_exp = left_idx.unsqueeze(-1)
        right_idx_exp = right_idx.unsqueeze(-1)
        
        q_left = torch.gather(qs_exp, 2, left_idx_exp).squeeze(-1)
        q_right = torch.gather(qs_exp, 2, right_idx_exp).squeeze(-1)
        p_left = torch.gather(ps_exp, 2, left_idx_exp).squeeze(-1)
        p_right = torch.gather(ps_exp, 2, right_idx_exp).squeeze(-1)
        
        denom = q_right - q_left + self.eps
        out = p_left + (x - q_left) * (p_right - p_left) / denom
        
        # Handle extrapolation for values below lowest bucket
        mask_low = (idx == 0) & (x < q_left)
        if mask_low.any():
            diff_low = torch.abs(x[mask_low] - q_left[mask_low])
            tanh_low = torch.tanh(diff_low)
            out[mask_low] = p_left[mask_low] - p_left[mask_low] * tanh_low
        
        # Handle extrapolation for values above highest bucket
        mask_high = (idx == self.num_buckets) & (x > q_right)
        if mask_high.any():
            diff_high = torch.abs(x[mask_high] - q_right[mask_high])
            tanh_high = torch.tanh(diff_high)
            out[mask_high] = p_right[mask_high] + (1 - p_right[mask_high]) * tanh_high
        
        # out = torch.clamp(out, min=0.0, max=1.0)
        return out