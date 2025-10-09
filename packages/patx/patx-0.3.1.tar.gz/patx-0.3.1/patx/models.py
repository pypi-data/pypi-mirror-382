import numpy as np
import lightgbm as lgb

class LightGBMModelWrapper:
    def __init__(self, task_type='classification', n_classes=None):
        params = {
            'learning_rate': 0.1, 'max_depth': 3, 'num_iterations': 100,
            'random_state': 42, 'num_threads': 1, 'force_col_wise': True,
            'verbosity': -1, 'early_stopping_rounds': 10, 'data_sample_strategy': 'goss'
        }
        if task_type == 'classification':
            if n_classes == 2:
                params.update({'objective': 'binary', 'metric': 'auc'})
            else:
                params.update({'objective': 'multiclass', 'metric': 'multi_logloss'})
                if n_classes: params['num_class'] = n_classes
        else:
            params.update({'objective': 'regression', 'metric': 'rmse'})
        self.params = params
        self.booster = None
    
    def fit(self, X_train, y_train, X_val=None, y_val=None):
        train_data = lgb.Dataset(X_train, label=y_train)
        valid_sets = [lgb.Dataset(X_val, label=y_val, reference=train_data)] if X_val is not None and y_val is not None else []
        self.booster = lgb.train(self.params, train_data, valid_sets=valid_sets, callbacks=[lgb.early_stopping(10, verbose=False)] if valid_sets else None)
        return self
    
    def predict(self, X):
        preds = self.booster.predict(X)
        if self.params.get('objective') == 'multiclass':
            return np.argmax(preds, axis=1)
        elif self.params.get('objective') == 'binary':
            return (preds > 0.5).astype(int)
        return preds
    
    def predict_proba(self, X):
        preds = self.booster.predict(X)
        return np.column_stack([1 - preds, preds])[:, 1] if self.params.get('objective') == 'binary' else preds
    
    def clone(self):
        # Determine task type from objective
        objective = self.params.get('objective', 'binary')
        if objective == 'regression':
            task_type = 'regression'
            n_classes = None
        elif objective == 'binary':
            task_type = 'classification'
            n_classes = 2
        else:  # multiclass
            task_type = 'classification'
            n_classes = self.params.get('num_class')
        return LightGBMModelWrapper(task_type, n_classes)
    
    def __repr__(self):
        objective = self.params.get('objective', 'binary')
        if objective == 'regression':
            return "LightGBMRegressor(metric='rmse')"
        elif objective == 'binary':
            return "LightGBMClassifier(objective='binary', metric='auc')"
        else:
            n_classes = self.params.get('num_class', 'unknown')
            return f"LightGBMClassifier(objective='multiclass', num_class={n_classes})"