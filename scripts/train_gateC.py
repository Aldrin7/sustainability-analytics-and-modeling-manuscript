import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import xgboost as xgb
import json
import time

print('=== Loading processed data ===')
X = pd.read_csv('data/processed/X_clean.csv')
y = pd.read_csv('data/processed/y_clean.csv')
print('X shape:', X.shape, 'y shape:', y.shape)

# Sample small subset for quick execution
np.random.seed(42)
idx = np.random.choice(len(X), size=20000, replace=False)
X = X.iloc[idx].reset_index(drop=True)
y = y.iloc[idx].reset_index(drop=True)
print('Sampled X shape:', X.shape, 'y shape:', y.shape)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print('Train:', X_train.shape, 'Test:', X_test.shape)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
joblib.dump(scaler, 'data/processed/scaler.joblib')
X_train_scaled_df = pd.DataFrame(X_train_scaled, columns=X.columns)
X_test_scaled_df = pd.DataFrame(X_test_scaled, columns=X.columns)

seeds = [42]
results = []

baseline_models = {
    'linear_regression': LinearRegression(),
    'ridge': Ridge(alpha=1.0),
    'lasso': Lasso(alpha=0.1)
}

rf_model = RandomForestRegressor(n_estimators=30, max_depth=4, random_state=42)
xgb_model = xgb.XGBRegressor(n_estimators=30, max_depth=3, learning_rate=0.1, random_state=42)

def evaluate_and_save(model_name, model, X_tr, y_tr, X_te, y_te, seed):
    model.random_state = seed
    start = time.time()
    model.fit(X_tr, y_tr)
    fit_time = time.time() - start
    y_pred = model.predict(X_te)
    target_metrics = {}
    for ti, tname in enumerate(y_te.columns):
        y_true = y_te.iloc[:, ti]
        yp = y_pred[:, ti] if y_pred.ndim > 1 else y_pred
        mse = mean_squared_error(y_true, yp)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, yp)
        r2 = r2_score(y_true, yp)
        target_metrics[tname] = {'rmse': float(rmse), 'mae': float(mae), 'r2': float(r2)}
    results.append({'model': model_name, 'seed': seed, 'fit_time_seconds': round(fit_time, 3), 'metrics': target_metrics})
    print(model_name + ' | seed=' + str(seed) + ' | fit=' + str(round(fit_time, 2)) + 's')
    for tname, tm in target_metrics.items():
        print('  ' + tname + ': RMSE=' + str(round(tm['rmse'], 3)) + ' R2=' + str(round(tm['r2'], 3)))

for model_name, model in baseline_models.items():
    for seed in seeds:
        evaluate_and_save(model_name, model, X_train_scaled_df, y_train, X_test_scaled_df, y_test, seed)

joblib.dump(baseline_models, 'data/processed/baselines.joblib')

for model_name, model in [('random_forest', rf_model), ('xgboost', xgb_model)]:
    for seed in seeds:
        evaluate_and_save(model_name, model, X_train_scaled_df, y_train, X_test_scaled_df, y_test, seed)

joblib.dump({'random_forest': rf_model, 'xgboost': xgb_model, 'scalers': scaler}, 'data/processed/trained_models.joblib')

with open('results/logs/gate_c_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print('Gate C COMPLETE')
print('Total model runs:', len(results))
