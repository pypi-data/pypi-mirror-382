import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Normal
import numpy as np

class SmoothBuckets(nn.Module):
    """
    This is a Torch Module that implements smooth bucketing.
    It Generalizes both deterministic bucketing and percetile based normalization,
    while remaining differentiable and handling NaNs gracefully.   

    Args:
    numerical_features_sample: Supports torch.Tensor or np.ndarray or pd.DataFrame

    num_buckets: Number of buckets per feature to use, this affects the number of parameters but not the output shape.
        Default: ``5``.

    eps: Epsilon value to add to stds to prevent division by zero.
        Default: ``1e-5``.

    dropout: Dropout rate to apply to the output.
        Default: ``0.1``.

    device: Device to use for the module.
        Default: ``None``.

    
    Usage::
        class MyModel(nn.Module):
            # numerical_features_sample can be a pd.DataFrame or torch.Tensor or np.ndarray
            def __init__(self, numerical_features_sample, num_buckets=5, dropout=0.1):
                super().__init__()
                self.input_normalizer = SmoothBuckets(numerical_features_sample, num_buckets, dropout=dropout)
            
            def forward(self, x):
                x = self.input_normalizer(x)
                # rest of the model
    """    
    def __init__(self, numerical_features_sample, num_buckets=5, eps=1e-5, dropout=0.1, device=None):
        super(SmoothBuckets, self).__init__()
        if isinstance(numerical_features_sample, np.ndarray):
            pass
        elif isinstance(numerical_features_sample, torch.Tensor):
            numerical_features_sample = numerical_features_sample.cpu().numpy()
            if device is None:
                device = numerical_features_sample.device
        elif "DataFrame" in str(type(numerical_features_sample)):
            try:
                numerical_features_sample = numerical_features_sample.to_numpy()
            except:
                raise ValueError("numerical_features_sample must be a torch.Tensor or np.ndarray or pd.DataFrame")
        else:
            raise ValueError("numerical_features_sample must be a torch.Tensor or np.ndarray or pd.DataFrame")

        self.num_buckets = num_buckets
        self.num_features = numerical_features_sample.shape[1]
        self.eps = eps
        device = device or "cpu"

        initial_means, initial_stds = self.get_initial_means_and_stds(numerical_features_sample, num_buckets)
        initial_means = initial_means.astype(np.float32)
        initial_stds = initial_stds.astype(np.float32)
        
        #this is not trainable, making it trainable would fail on features with large value ranges due to LR and/or regularization
        self.means = nn.Parameter(torch.tensor(initial_means).unsqueeze(0).to(device), requires_grad=False)
        self.stds = nn.Parameter(torch.tensor(initial_stds+self.eps).unsqueeze(0).to(device), requires_grad=False)
        self.arange = nn.Parameter(torch.arange(self.num_buckets, device=device).unsqueeze(0).unsqueeze(0), requires_grad=False)
        
        #this is trainable and scale free
        self.means_mul = nn.Parameter(torch.zeros_like(self.means).to(device), requires_grad=True)
        self.stds_mul = nn.Parameter(torch.zeros_like(self.stds).to(device), requires_grad=True)

        #the initial guess for NaNs is like mean inputation, but it is learnable
        self.nan_replacements = nn.Parameter(torch.tensor(np.nanmean(numerical_features_sample, axis=0)).unsqueeze(0).to(device), requires_grad=False)
        self.nan_replacements_mul = nn.Parameter(torch.zeros_like(self.nan_replacements).to(device), requires_grad=True)
        self.initial_features_stds = nn.Parameter(torch.tensor(np.nanstd(numerical_features_sample, axis=0)).unsqueeze(0).to(device), requires_grad=False)
        

        self.layer_norm = nn.LayerNorm(self.num_features * (self.num_buckets+1), device=device)
        self.dropout = nn.Dropout(dropout)
        self.linear_to_num_features = nn.Linear(self.num_features * (self.num_buckets + 1), self.num_features, device=device)
        self.pos_elu = lambda x: F.elu(x-1) + 1
        

    def get_initial_means_and_stds(self, data, num_buckets):
        all_nan = np.all(np.isnan(data), axis=0)
        qs = np.linspace(1 / (num_buckets + 1), num_buckets / (num_buckets + 1), num_buckets)
        means = np.nanquantile(data, qs, axis=0).T
        buckets_idx = np.arange(num_buckets)
        before_idx = np.maximum(buckets_idx - 1, 0)
        after_idx = np.minimum(buckets_idx + 1, num_buckets - 1)
        div = np.where((buckets_idx == 0) | (buckets_idx == num_buckets - 1), 1, 2)
        stds = (means[:, after_idx] - means[:, before_idx]) / div
        means[all_nan] = 0
        stds[all_nan] = 1
        return means, stds

    def compute_bucket_share(self,means, stds, x):
        """
        Compute the density of x given means and stds.
        means: (1, num_features, num_buckets)
        stds: (1, num_features, num_buckets)
        x: (num_samples, num_features)
        returns: (num_samples, num_features, num_buckets)
        """
        x = x.unsqueeze(-1)
        normal = Normal(loc=means, scale=stds)
        log_densities = normal.log_prob(x)
        bucket_share = torch.softmax(log_densities, dim=-1)
        return bucket_share


    def forward(self, x):
        batch_size = x.shape[0]
        x = torch.where(torch.isnan(x), self.nan_replacements*(self.nan_replacements_mul*self.initial_features_stds+1), x) #much better than mean imputation and moves logic from the pipeline to the model

        means = self.means * (self.means_mul + 1)
        stds = self.stds * self.pos_elu(self.stds_mul+1)
        bucket_share = self.compute_bucket_share(means, stds, x) #softmax(bucket_share) is the same is regular bucketing if stds==EPS
        
        #here we add an the "percentile" feature for each numerical input
        approximated_percentiles = (bucket_share*self.arange).sum(dim=-1) / self.num_buckets
        
        
        x = torch.cat([bucket_share.view(batch_size, -1), approximated_percentiles.view(batch_size, -1)-0.5], dim=-1)
        x = self.layer_norm(x)
        x = self.dropout(x)
        x = self.linear_to_num_features(x)
        return x

