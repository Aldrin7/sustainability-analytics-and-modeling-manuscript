import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
import json

# Load raw data
df = pd.read_csv('data/processed/cars_dataset.csv')
print('Raw data shape:', df.shape)

# Step 1: Handle missing values
print('=== STEP 1: Missing values ===')
df_processed = df.copy()
num_cols = df_processed.select_dtypes(include=[np.number]).columns
imputer = SimpleImputer(strategy='median')
df_processed[num_cols] = imputer.fit_transform(df_processed[num_cols])

cat_cols = df_processed.select_dtypes(include=['object', 'category']).columns
for col in cat_cols:
    mode_val = df_processed[col].mode()
    df_processed[col] = df_processed[col].fillna(mode_val[0] if len(mode_val) > 0 else 'Unknown')

bool_cols = df_processed.select_dtypes(include=['bool']).columns
for col in bool_cols:
    mode_val = df_processed[col].mode()
    df_processed[col] = df_processed[col].fillna(mode_val[0] if len(mode_val) > 0 else False)

print('After imputation:', df_processed.shape)
print('Remaining missing:', df_processed.isnull().sum().sum())

with open('data/processed/gate_b_meta.json', 'w') as f:
    json.dump({'step': 'missing_imputation'}, f)

print('Step 1 complete')
print('Step 2: Feature engineering')

# Step 2: Feature engineering
print('\n=== STEP 2: Feature engineering ===')

# Derived features
df_processed['vehicle_age_derived'] = 2026 - df_processed['vehicle_year']
df_processed['fuel_cost_index'] = df_processed['annual_driving_km'] / 100 * df_processed['fuel_consumption_combined_l_100km'] * 1.5
df_processed['emission_intensity'] = df_processed['co2_emissions_g_km'] / (df_processed['engine_power_hp'] + 1)
df_processed['efficiency_ratio'] = df_processed['engine_efficiency_score'] / (df_processed['engine_displacement_cc'] + 1)
df_processed['feature_density'] = df_processed['total_feature_count'] / (df_processed['length_mm'] + 1)
df_processed['performance_density'] = df_processed['combined_system_power_hp'] / (df_processed['curb_weight_kg'] + 1)
df_processed['co2_per_km'] = df_processed['co2_emissions_g_km'] / (df_processed['annual_driving_km'] + 1) * 1000
df_processed['green_score_ratio'] = df_processed['environmental_score'] / (df_processed['co2_emissions_g_km'] + 1)
df_processed['acceleration_per_power'] = df_processed['zero_to_100_kmh_seconds'] / (df_processed['engine_power_hp'] + 1)

print('After feature engineering:', df_processed.shape)
with open('data/processed/gate_b_meta.json', 'w') as f:
    json.dump({'step': 'feature_engineering'}, f)

print('Step 2 complete')

# Step 3: Feature selection
print('\n=== STEP 3: Feature selection ===')
target_cols = ['environmental_score', 'green_vehicle_score', 'fuel_efficiency_score', 'co2_emissions_g_km']
print('Target columns:', target_cols)

drop_cols = ['vehicle_id', 'listing_id', 'seller_id', 'dealer_id', 'brand_id', 'manufacturer_id', 'model_id']
info_cols = ['listing_quality_score', 'image_quality_score', 'vehicle_presentation_score', 'listing_completeness_score']

feature_cols = [c for c in df_processed.columns if c not in drop_cols + info_cols]

print('Total features before selection:', len(feature_cols))

# Check correlations and remove highly correlated features
num_features = df_processed[feature_cols].select_dtypes(include=[np.number]).columns
corr_matrix = df_processed[num_features].corr().abs()
upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
high_corr = [(col, row) for col in upper.columns for row in upper.index if upper.loc[row, col] > 0.95]

print('Highly correlated pairs (>0.95):', len(high_corr))

to_drop = set()
for col, row in high_corr[:200]:
    if col not in to_drop and row not in to_drop:
        to_drop.add(col)

print('Features to drop due to correlation:', len(to_drop))
feature_cols = [c for c in feature_cols if c not in to_drop]

print('Features after correlation filter:', len(feature_cols))

with open('data/processed/gate_b_meta.json', 'w') as f:
    json.dump({'step': 'feature_selection', 'dropped_corr_count': len(to_drop)}, f)

print('Step 3 complete')

# Step 4: Prepare X and y
print('\n=== STEP 4: Prepare X and y ===')
X = df_processed[feature_cols].copy()
y = df_processed[target_cols].copy()
print('X shape:', X.shape)
print('y shape:', y.shape)

with open('data/processed/gate_b_meta.json', 'w') as f:
    json.dump({'step': 'X_y_ready', 'X_shape': list(X.shape), 'y_shape': list(y.shape)}, f)

print('Step 4 complete')

# Step 5: Save
print('\n=== STEP 5: Save outputs ===')
X.to_csv('data/processed/X_clean.csv', index=False)
y.to_csv('data/processed/y_clean.csv', index=False)

with open('data/processed/preprocessing_meta.json', 'w') as f:
    json.dump({
        'features': feature_cols,
        'targets': target_cols,
        'X_shape': list(X.shape),
        'y_shape': list(y.shape)
    }, f, indent=2)

print('Saved X_clean.csv, y_clean.csv, preprocessing_meta.json')
print('\n=== Gate B COMPLETE ===')
