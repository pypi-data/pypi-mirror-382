from typing import Optional, Union, List, Dict, Tuple, Any
import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib
matplotlib.use('Agg')
from hyperopt import fmin, tpe, hp, Trials, STATUS_OK
from scipy.interpolate import BSpline
from sklearn.metrics import accuracy_score, roc_auc_score, mean_squared_error

def evaluate_model_performance(model, X_combined, y_train, metric, cached_indices):
    train_idx, val_idx = cached_indices
    X_train, X_val = X_combined[train_idx], X_combined[val_idx]
    y_train_split, y_val = y_train[train_idx], y_train[val_idx]
    
    # Ensure y_val is properly formatted
    y_val = np.asarray(y_val)
    
    model = model.clone()
    model.fit(X_train, y_train_split, X_val, y_val)
    
    if metric == 'auc':
        y_pred = model.predict_proba(X_val)
        n_classes = len(np.unique(y_val))
        if n_classes == 2:
            return roc_auc_score(y_val, y_pred)
        else:
            # For multiclass, use one-vs-rest with macro average
            return roc_auc_score(y_val, y_pred, multi_class='ovr', average='macro')
    elif metric == 'accuracy':
        y_pred = model.predict(X_val)
        return accuracy_score(y_val, y_pred)
    elif metric == 'rmse':
        y_pred = model.predict(X_val)
        return np.sqrt(mean_squared_error(y_val, y_pred))
    else:
        y_pred = model.predict_proba(X_val)
        n_classes = len(np.unique(y_val))
        if n_classes == 2:
            return roc_auc_score(y_val, y_pred)
        else:
            return roc_auc_score(y_val, y_pred, multi_class='ovr', average='macro')

def feature_extraction(input_series_train: Union[Any, List[Any]], 
                      y_train: Union[Any, np.ndarray], 
                      input_series_test: Optional[Union[Any, List[Any]]] = None,
                      initial_features: Optional[Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]] = None,
                      model: Optional[Any] = None, 
                      metric: Optional[str] = None, 
                      val_size: float = 0.2,
                      n_trials: int = 300, 
                      show_progress: bool = True) -> Dict[str, Any]:
    
    if metric is None:
        metric = 'auc'
    
    # Convert input to numpy array
    if isinstance(input_series_train, (list, tuple)):
        # Handle list of arrays/DataFrames
        arrays = [arr.values.astype(np.float32) if hasattr(arr, 'values') else np.asarray(arr, dtype=np.float32) for arr in input_series_train]
        min_shape = min(arr.shape for arr in arrays)
        arrays = [arr[:min_shape[0], :min_shape[1]] if arr.ndim == 2 else arr[:min_shape[0]] for arr in arrays]
        input_series_train = np.stack(arrays, axis=1)
        n_input_series = len(arrays)
        n_time_points = min_shape[1] if len(min_shape) > 1 else min_shape[0]
    else:
        # Single array/DataFrame
        if hasattr(input_series_train, 'values'):
            input_series_train = input_series_train.values.astype(np.float32)
        else:
            input_series_train = np.asarray(input_series_train, dtype=np.float32)
        
        if input_series_train.ndim == 1:
            input_series_train = input_series_train.reshape(1, -1)
        
        if input_series_train.ndim == 3:
            n_input_series = input_series_train.shape[1]
            n_time_points = input_series_train.shape[2]
        else:
            n_input_series = 1
            n_time_points = input_series_train.shape[1]

    # Initialize the feature set that will be fed to the ML model
    if initial_features is not None:
        if isinstance(initial_features, tuple) and len(initial_features) == 2:
            initial_features_train = np.asarray(initial_features[0], dtype=np.float32)
            initial_features_test = np.asarray(initial_features[1], dtype=np.float32)
        else:
            initial_features_train = np.asarray(initial_features, dtype=np.float32)
            initial_features_test = None
        model_features_list = [initial_features_train]
    else:
        initial_features_train, initial_features_test = None, None
        model_features_list = []
    
    # Process target variable
    y_train = np.asarray(y_train).flatten()
    if len(y_train) != input_series_train.shape[0]:
        y_train = y_train[:input_series_train.shape[0]] if len(y_train) > input_series_train.shape[0] else np.concatenate([y_train, np.full(input_series_train.shape[0] - len(y_train), y_train[-1])])
    
    # Ensure target is properly formatted for LightGBM
    unique_targets = np.unique(y_train)
    if len(unique_targets) > 2:
        # For multiclass, ensure labels start from 0 and are consecutive integers
        if not np.array_equal(unique_targets, np.arange(len(unique_targets))):
            # Remap labels to start from 0
            label_map = {old_label: new_label for new_label, old_label in enumerate(unique_targets)}
            y_train = np.array([label_map[label] for label in y_train], dtype=int)
    else:
        # For binary classification, ensure labels are 0 and 1
        if not np.array_equal(unique_targets, [0, 1]):
            y_train = (y_train == unique_targets[1]).astype(int)
    
    # Create default model if none provided (after target processing)
    if model is None:
        from .models import LightGBMModelWrapper
        if metric == 'rmse':
            model = LightGBMModelWrapper('regression')
        else:
            unique_targets = np.unique(y_train)
            if len(unique_targets) > 2:
                model = LightGBMModelWrapper('classification', n_classes=len(unique_targets))
            else:
                model = LightGBMModelWrapper('classification', n_classes=2)
    
    # Track the best score across all patterns
    overall_best_score = float('inf') if metric == 'rmse' else -float('inf')
    
    def generate_bspline_pattern(control_points: List[float], width: int, data_min: float = -1.0, data_max: float = 1.0) -> np.ndarray:
        # Create evaluation points
        x = np.linspace(0, 1, width, dtype=np.float32)
        
        # Create B-spline with 5 control points (degree 3)
        knots = np.array([0, 0, 0, 0, 0.5, 1, 1, 1, 1], dtype=np.float32)
        control_points = np.array(control_points, dtype=np.float32)
        
        # Create B-spline basis
        bspline = BSpline(knots, control_points, 3)
        result = bspline(x).astype(np.float32)
        
        # Scale to data range
        result_min, result_max = result.min(), result.max()
        range_diff = result_max - result_min
        if range_diff > 1e-10:
            result = (result - result_min) * ((data_max - data_min) / range_diff) + data_min
        return result
    
    # Calculate similarity metrics between input series region and pattern
    def calculate_similarity(X_region: np.ndarray, pattern_values: np.ndarray, metric: str) -> np.ndarray:
        diff = X_region - pattern_values
        if metric == 'rmse':
            return np.sqrt((diff * diff).mean(axis=1)).astype(np.float32)
        ss_res = (diff * diff).sum(axis=1)
        ss_tot = ((X_region - X_region.mean(axis=1, keepdims=True)) ** 2).sum(axis=1)
        return (1 - ss_res / (ss_tot + 1e-8)).astype(np.float32)

    # Precompute fixed train/val split indices for consistent, faster scoring
    all_indices = np.arange(input_series_train.shape[0])
    train_idx, val_idx = train_test_split(all_indices, test_size=val_size, random_state=42, stratify=None)
    cached_indices = (train_idx, val_idx)

    def objective(params):
        # Select which input series to extract pattern from (only for multivariate)
        input_series_idx = params['series_index'] if n_input_series > 1 else 0
        similarity_metric = ['rmse', 'r2'][params['similarity_metric']]
        control_points = [params[f'cp{i}'] for i in range(5)]
        selected_input_series = input_series_train[:, input_series_idx, :] if n_input_series > 1 else input_series_train
        pattern_width = params['pattern_width']
        pattern_start = params['pattern_start']
        if pattern_start + pattern_width > n_time_points:
            return {'loss': float('inf'), 'status': STATUS_OK}
        data_min = np.min(selected_input_series)
        data_max = np.max(selected_input_series)
        pattern_region = selected_input_series[:, pattern_start:pattern_start + pattern_width]
        pattern_vals = generate_bspline_pattern(control_points, pattern_width, data_min, data_max)
        new_model_feature = calculate_similarity(pattern_region, pattern_vals, similarity_metric)
        model_feature_set = np.column_stack(model_features_list + [new_model_feature]) if model_features_list else new_model_feature.reshape(-1, 1)
        score = evaluate_model_performance(model, model_feature_set, y_train, metric, cached_indices)
        return {'loss': 1 - score if metric != 'rmse' else score, 'status': STATUS_OK}
    
    # Extract multiple patterns from input series to build the feature set
    extracted_patterns = []
    first_pattern = True
    
    while True:
        space = {
            'similarity_metric': hp.choice('similarity_metric', [0, 1])
        }
        if n_input_series > 1:
            space['series_index'] = hp.randint('series_index', n_input_series)
        for i in range(5):
            space[f'cp{i}'] = hp.uniform(f'cp{i}', -1, 1)
        space['pattern_width'] = hp.randint('pattern_width', 1, n_time_points)
        space['pattern_start'] = hp.randint('pattern_start', 0, n_time_points)
        
        trials = Trials()
        best = fmin(fn=objective, space=space, algo=tpe.suggest, max_evals=n_trials, trials=trials, verbose=show_progress)
        
        best_loss = min([t['result']['loss'] for t in trials.trials])
        current_score = 1 - best_loss if metric != 'rmse' else best_loss
        
        if first_pattern or (metric == 'rmse' and current_score < overall_best_score) or (metric != 'rmse' and current_score > overall_best_score):
            best_params = best
            input_series_idx = best_params.get('series_index', 0)
            similarity_metric = ['rmse', 'r2'][best_params['similarity_metric']]
            control_points = [best_params[f'cp{i}'] for i in range(5)]
            data_min, data_max = np.min(input_series_train), np.max(input_series_train)
            # Extract the corresponding input series data
            selected_input_series = input_series_train[:, input_series_idx, :] if n_input_series > 1 else input_series_train
            
            # Use parameters from trial
            start, width = best_params['pattern_start'], best_params['pattern_width']
            pattern_region = selected_input_series[:, start:start+width]
            
            # Use min/max for consistent pattern scaling
            data_min = np.min(selected_input_series)
            data_max = np.max(selected_input_series)
            pattern_vals = generate_bspline_pattern(control_points, width, data_min, data_max)
            
            extracted_patterns.append({
                'pattern': pattern_vals,
                'start': start,
                'width': width,
                'series_idx': input_series_idx,
                'data_min': data_min,
                'data_max': data_max,
                'similarity_metric': similarity_metric,
                'control_points': control_points
            })
            pattern_feature = calculate_similarity(pattern_region, pattern_vals, similarity_metric)
            model_features_list.append(pattern_feature)
            overall_best_score = current_score
            first_pattern = False
        else:
            break
    
    # Combine all extracted pattern features into the final feature set for the ML model
    model_features = np.column_stack(model_features_list) if model_features_list else np.empty((input_series_train.shape[0], 0))
    
    # Split the feature set for training and validation
    train_features, val_features, y_train, y_val = train_test_split(model_features, y_train, test_size=val_size, random_state=42)
    model.fit(train_features, y_train, val_features, y_val)
    
    # Apply pattern extraction to test data
    test_features = None
    if input_series_test is not None:
        # Process test data the same way as training data
        if isinstance(input_series_test, (list, tuple)):
            # Handle list of arrays/DataFrames
            test_arrays = [arr.values.astype(np.float32) if hasattr(arr, 'values') else np.asarray(arr, dtype=np.float32) for arr in input_series_test]
            min_shape = min(arr.shape for arr in test_arrays)
            test_arrays = [arr[:min_shape[0], :min_shape[1]] if arr.ndim == 2 else arr[:min_shape[0]] for arr in test_arrays]
            input_series_test = np.stack(test_arrays, axis=1)
            test_n_series = len(test_arrays)
        else:
            # Single array/DataFrame
            if hasattr(input_series_test, 'values'):
                input_series_test = input_series_test.values.astype(np.float32)
            else:
                input_series_test = np.asarray(input_series_test, dtype=np.float32)
            
            if input_series_test.ndim == 1:
                input_series_test = input_series_test.reshape(1, -1)
            
            test_n_series = 1 if input_series_test.ndim == 2 else input_series_test.shape[1]
        
        n_test_samples = input_series_test.shape[0]
        n_initial_features = initial_features_train.shape[1] if initial_features_train is not None else 0
        test_features = np.empty((n_test_samples, n_initial_features + len(extracted_patterns)), dtype=np.float32)
        if n_initial_features > 0 and initial_features_test is not None:
            test_features[:, :n_initial_features] = initial_features_test
        
        for i, pattern_info in enumerate(extracted_patterns):
            test_input_series = input_series_test[:, pattern_info['series_idx'], :] if test_n_series > 1 else input_series_test
            test_features[:, n_initial_features+i] = calculate_similarity(
                test_input_series[:, pattern_info['start']:pattern_info['start']+pattern_info['width']], 
                pattern_info['pattern'], 
                pattern_info['similarity_metric']
            )
    
    return {
        'patterns': extracted_patterns,
        'train_features': train_features,
        'test_features': test_features,
        'model': model,
    }
