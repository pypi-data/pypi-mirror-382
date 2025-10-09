from typing import Optional, Union, List, Dict, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from hyperopt import fmin, tpe, hp, Trials, STATUS_OK
from scipy.interpolate import BSpline
from sklearn.metrics import accuracy_score, roc_auc_score, mean_squared_error

def generate_bspline_pattern(control_points: List[float], width: int, data_min: float, data_max: float) -> np.ndarray:
    n_cp = len(control_points)
    degree = 3
    x = np.linspace(0, 1, width)
    knots = np.concatenate([np.zeros(degree + 1), np.linspace(0, 1, n_cp - degree + 1)[1:-1], np.ones(degree + 1)])
    bspline = BSpline(knots, np.array(control_points), degree)
    pattern = bspline(x)
    result_min, result_max = pattern.min(), pattern.max()
    range_diff = result_max - result_min
    return (pattern - result_min) * ((data_max - data_min) / range_diff) + data_min if range_diff > 1e-10 else pattern

def calculate_similarity(X_region: np.ndarray, pattern: np.ndarray, metric: str) -> np.ndarray:
    if metric == 'rmse':
        rmse = np.sqrt(((X_region - pattern) ** 2).mean(axis=1))
        return np.exp(-rmse / (np.abs(X_region).max() + 1e-8))
    X_centered, pattern_centered = X_region - X_region.mean(axis=1, keepdims=True), pattern - pattern.mean()
    numerator = (X_centered * pattern_centered).sum(axis=1)
    denominator = np.sqrt((X_centered ** 2).sum(axis=1) * (pattern_centered ** 2).sum())
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(denominator > 1e-8, numerator / denominator, 0.0)

def _convert_to_3d_array(input_series: Union[Any, List[Any]]) -> np.ndarray:
    if isinstance(input_series, np.ndarray) and input_series.ndim == 3:
        return input_series
    if isinstance(input_series, (list, tuple)):
        arrays = [arr.values if isinstance(arr, (pd.DataFrame, pd.Series)) else np.asarray(arr) for arr in input_series]
        arrays = [arr.reshape(-1, 1) if arr.ndim == 1 else arr for arr in arrays]
        n_samples = min(arr.shape[0] for arr in arrays)
        n_time_points = min(arr.shape[1] for arr in arrays)
        arrays = [arr[:n_samples, :n_time_points].astype(np.float32) for arr in arrays]
        return np.stack(arrays, axis=1)
    arr = input_series.values if isinstance(input_series, (pd.DataFrame, pd.Series)) else np.asarray(input_series)
    arr = arr.reshape(-1, 1) if arr.ndim == 1 else arr
    return arr.astype(np.float32).reshape(arr.shape[0], 1, arr.shape[1])

def pattern_to_features(input_series: Union[Any, List[Any]], 
                       control_points: List[float], 
                       pattern_width: int, 
                       pattern_start: int, 
                       series_index: int = 0,
                       data_min: float = -1.0, 
                       data_max: float = 1.0, 
                       similarity_metric: str = 'r2') -> np.ndarray:
    input_3d = _convert_to_3d_array(input_series)
    selected_series = input_3d[:, series_index, :]
    pattern = generate_bspline_pattern(control_points, pattern_width, data_min, data_max)
    X_region = selected_series[:, pattern_start:pattern_start + pattern_width]
    return calculate_similarity(X_region, pattern, similarity_metric)

def evaluate_model_performance(model, X_combined, y_train, metric, cached_indices):
    train_idx, val_idx = cached_indices
    X_train, X_val = X_combined[train_idx], X_combined[val_idx]
    y_train_split, y_val = y_train[train_idx], np.asarray(y_train[val_idx])
    model = model.clone()
    model.fit(X_train, y_train_split, X_val, y_val)
    
    if metric == 'accuracy':
        return accuracy_score(y_val, model.predict(X_val))
    if metric == 'rmse':
        return np.sqrt(mean_squared_error(y_val, model.predict(X_val)))
    y_pred = model.predict_proba(X_val)
    n_classes = len(np.unique(y_val))
    return roc_auc_score(y_val, y_pred) if n_classes == 2 else roc_auc_score(y_val, y_pred, multi_class='ovr', average='macro')

def feature_extraction(input_series_train: Union[Any, List[Any]], 
                      y_train: Union[Any, np.ndarray], 
                      input_series_test: Optional[Union[Any, List[Any]]] = None,
                      initial_features: Optional[Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]] = None,
                      model: Optional[Any] = None, 
                      metric: Optional[str] = None, 
                      val_size: float = 0.2,
                      n_trials: int = 300, 
                      n_control_points: int = 5,
                      show_progress: bool = True) -> Dict[str, Any]:
    
    if isinstance(input_series_train, (list, tuple)):
        arrays = []
        for arr in input_series_train:
            arr_np = arr.values if isinstance(arr, (pd.DataFrame, pd.Series)) else np.asarray(arr)
            arrays.append(arr_np.reshape(-1, 1) if arr_np.ndim == 1 else arr_np)
        n_samples = min(arr.shape[0] for arr in arrays)
        n_time_points = min(arr.shape[1] for arr in arrays)
        arrays = [arr[:n_samples, :n_time_points] for arr in arrays]
        input_series_train = np.stack(arrays, axis=1)
        n_input_series = len(arrays)
    else:
        input_series_train = input_series_train.values if isinstance(input_series_train, (pd.DataFrame, pd.Series)) else np.asarray(input_series_train)
        input_series_train = input_series_train.reshape(-1, 1) if input_series_train.ndim == 1 else input_series_train
        n_input_series = 1
        n_time_points = input_series_train.shape[1]

    # Debug: Print shapes
    if show_progress:
        print(f"Input shape: {input_series_train.shape} (n_samples={input_series_train.shape[0]}, n_series={n_input_series}, n_time_points={n_time_points})")
    
    if initial_features is not None:
        if isinstance(initial_features, tuple) and len(initial_features) == 2:
            initial_features_train = initial_features[0].values if isinstance(initial_features[0], pd.DataFrame) else np.asarray(initial_features[0])
            initial_features_test = initial_features[1].values if isinstance(initial_features[1], pd.DataFrame) else np.asarray(initial_features[1])
        else:
            initial_features_train = initial_features.values if isinstance(initial_features, pd.DataFrame) else np.asarray(initial_features)
            initial_features_test = None
        initial_features_train = initial_features_train.reshape(-1, 1) if initial_features_train.ndim == 1 else initial_features_train
        initial_features_test = initial_features_test.reshape(-1, 1) if initial_features_test is not None and initial_features_test.ndim == 1 else initial_features_test
        model_features_list = [initial_features_train]
        if show_progress:
            print(f"Initial features: train={initial_features_train.shape}, test={initial_features_test.shape if initial_features_test is not None else None}")
    else:
        initial_features_train, initial_features_test, model_features_list = None, None, []
    
    y_train = np.asarray(y_train).flatten()
    y_train = y_train[:input_series_train.shape[0]] if len(y_train) > input_series_train.shape[0] else (np.concatenate([y_train, np.full(input_series_train.shape[0] - len(y_train), y_train[-1])]) if len(y_train) != input_series_train.shape[0] else y_train)
    
    if metric != 'rmse':
        unique_targets = np.unique(y_train)
        if len(unique_targets) > 2 and not np.array_equal(unique_targets, np.arange(len(unique_targets))):
            label_map = {old_label: new_label for new_label, old_label in enumerate(unique_targets)}
            y_train = np.array([label_map[label] for label in y_train], dtype=int)
        elif len(unique_targets) == 2 and not np.array_equal(unique_targets, [0, 1]):
            y_train = (y_train == unique_targets[1]).astype(int)
    
    if model is None:
        from .models import LightGBMModelWrapper
        unique_targets = np.unique(y_train)
        model = LightGBMModelWrapper('regression') if metric == 'rmse' else LightGBMModelWrapper('classification', n_classes=len(unique_targets) if len(unique_targets) > 2 else 2)
    
    overall_best_score = float('inf') if metric == 'rmse' else -float('inf')
    
    # Precompute fixed train/val split indices for consistent, faster scoring
    all_indices = np.arange(input_series_train.shape[0])
    train_idx, val_idx = train_test_split(all_indices, test_size=val_size, random_state=42, stratify=None)
    cached_indices = (train_idx, val_idx)

    def objective(params):
        input_series_idx = params.get('series_index', 0)
        similarity_metric = ['rmse', 'r2'][params['similarity_metric']]
        control_points = [params[f'cp{i}'] for i in range(n_control_points)]
        pattern_width, pattern_start = params['pattern_width'], params['pattern_start']
        if pattern_start + pattern_width > n_time_points:
            return {'loss': float('inf'), 'status': STATUS_OK}
        selected_input_series = input_series_train[:, input_series_idx, :]
        new_model_feature = pattern_to_features(input_series_train, control_points, pattern_width, pattern_start, input_series_idx, np.min(selected_input_series), np.max(selected_input_series), similarity_metric)
        model_feature_set = np.column_stack(model_features_list + [new_model_feature]) if model_features_list else new_model_feature.reshape(-1, 1)
        score = evaluate_model_performance(model, model_feature_set, y_train, metric, cached_indices)
        return {'loss': (1 - score) if metric != 'rmse' else score, 'status': STATUS_OK}
    
    # Extract multiple patterns from input series to build the feature set
    extracted_patterns = []
    first_pattern = True
    
    while True:
        space = {'similarity_metric': hp.choice('similarity_metric', [0, 1])}
        if n_input_series > 1:
            space['series_index'] = hp.randint('series_index', n_input_series)
        for i in range(n_control_points):
            space[f'cp{i}'] = hp.uniform(f'cp{i}', 0, 1)
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
            control_points = [best_params[f'cp{i}'] for i in range(n_control_points)]
            start, width = best_params['pattern_start'], best_params['pattern_width']
            selected_input_series = input_series_train[:, input_series_idx, :] if n_input_series > 1 else input_series_train
            data_min, data_max = np.min(selected_input_series), np.max(selected_input_series)
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
            pattern_feature = pattern_to_features(input_series_train, control_points, width, start, input_series_idx, data_min, data_max, similarity_metric)
            model_features_list.append(pattern_feature)
            overall_best_score = current_score
            first_pattern = False
        else:
            break
    
    # Combine all extracted pattern features into the final feature set for the ML model
    # Note: initial features are already in model_features_list if provided
    model_features = np.column_stack(model_features_list) if model_features_list else np.empty((input_series_train.shape[0], 0))
    
    # Split the feature set for training and validation
    train_features, val_features, y_train_split, y_val = train_test_split(model_features, y_train, test_size=val_size, random_state=42)
    
    # Create a completely fresh model and train it on the final extracted features
    from .models import LightGBMModelWrapper
    if metric == 'rmse':
        final_model = LightGBMModelWrapper('regression')
    else:
        unique_targets = np.unique(y_train)
        if len(unique_targets) > 2:
            final_model = LightGBMModelWrapper('classification', n_classes=len(unique_targets))
        else:
            final_model = LightGBMModelWrapper('classification', n_classes=2)
    
    if show_progress and metric == 'rmse':
        print(f"Training final model: X_train={train_features.shape}, y_train range=[{y_train_split.min():.2f}, {y_train_split.max():.2f}]")
        print(f"Features range: [{train_features.min():.3f}, {train_features.max():.3f}]")
    
    final_model.fit(train_features, y_train_split, val_features, y_val)
    
    if show_progress and metric == 'rmse':
        # Test prediction on training data to verify model
        test_pred = final_model.predict(train_features[:5])
        print(f"Test predictions on first 5 train samples: {test_pred}")
        print(f"Actual y values: {y_train_split[:5]}")
    
    # Return the full training features (not just the split used for model training)
    train_features = model_features
    
    test_features = None
    if input_series_test is not None:
        if isinstance(input_series_test, (list, tuple)):
            test_arrays = []
            for arr in input_series_test:
                arr_np = arr.values if isinstance(arr, (pd.DataFrame, pd.Series)) else np.asarray(arr)
                test_arrays.append(arr_np.reshape(-1, 1) if arr_np.ndim == 1 else arr_np)
            n_test_samples = min(arr.shape[0] for arr in test_arrays)
            n_test_time_points = min(arr.shape[1] for arr in test_arrays)
            test_arrays = [arr[:n_test_samples, :n_test_time_points] for arr in test_arrays]
            input_series_test_np = np.stack(test_arrays, axis=1)
        else:
            input_series_test_np = input_series_test.values if isinstance(input_series_test, (pd.DataFrame, pd.Series)) else np.asarray(input_series_test)
            input_series_test_np = input_series_test_np.reshape(-1, 1) if input_series_test_np.ndim == 1 else input_series_test_np
        
        n_test_samples = input_series_test_np.shape[0]
        n_initial_features = initial_features_train.shape[1] if initial_features_train is not None else 0
        test_features = np.empty((n_test_samples, n_initial_features + len(extracted_patterns)), dtype=np.float32)
        if n_initial_features > 0 and initial_features_test is not None:
            test_features[:, :n_initial_features] = initial_features_test
        for i, pattern_info in enumerate(extracted_patterns):
            test_features[:, n_initial_features+i] = pattern_to_features(
                input_series_test, 
                pattern_info['control_points'], 
                pattern_info['width'], 
                pattern_info['start'], 
                pattern_info['series_idx'], 
                pattern_info['data_min'], 
                pattern_info['data_max'], 
                pattern_info['similarity_metric']
            )
    
    return {
        'patterns': extracted_patterns,
        'train_features': train_features,
        'test_features': test_features,
        'model': final_model,
    }
