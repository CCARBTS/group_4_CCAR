
import pandas as pd
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from utils.logger import get_logger
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

logger = get_logger("ccar_model")

# deprecated: get_best_model()
def get_best_model(df1):

    # ----------------------
    # 1. Load and preprocess
    # ----------------------
    # Replace this with your actual DataFrame
    # df1 = pd.read_csv('your_data.csv')
    # Ensure date is datetime
    df1['date'] = pd.to_datetime(df1['date'])
    df1 = df1.sort_values(by='date')

    # Store LabelEncoder map for interpretability
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    df1['country_encoded'] = le.fit_transform(df1['country'])
    country_map = dict(zip(le.classes_, le.transform(le.classes_)))
    inverse_map = dict(zip(le.transform(le.classes_), le.classes_))

    # Shift target 6 weeks back to make future predictions
    df1['most_needs_idx_target'] = df1.groupby('country_encoded')['most_needs_idx'].shift(-26)

    # Create lag features: past 1 and 2 weeks
    df1['lag_1'] = df1.groupby('country_encoded')['most_needs_idx'].shift(1)
    df1['lag_2'] = df1.groupby('country_encoded')['most_needs_idx'].shift(2)
    df1['lag_3'] = df1.groupby('country_encoded')['most_needs_idx'].shift(3)

    # Drop rows where future target is not available
    df1 = df1.dropna(subset=['most_needs_idx_target', 'lag_1', 'lag_2', 'lag_3'])

    # ----------------------
    # 2. Add rolling means and seasonal features
    # ----------------------
    #Stabilizing volatile indicators: window=4 or window=12
    #df1['conflict_rolling_4w'] = df1.groupby('country_encoded')['conflict_norm'].transform(lambda x: x.rolling(window=4, min_periods=1).mean())
    #df1['conflict_rolling_12w'] = df1.groupby('country_encoded')['conflict_norm'].transform(lambda x: x.rolling(window=12, min_periods=1).mean())
    #df1['disaster_rolling_4w'] = df1.groupby('country_encoded')['disaster_norm'].transform(lambda x: x.rolling(window=4, min_periods=1).mean())
    #df1['disaster_rolling_12w'] = df1.groupby('country_encoded')['disaster_norm'].transform(lambda x: x.rolling(window=12, min_periods=1).mean())

    for window in [4, 8, 12, 26]:
        df1[f'rolling_mean_{window}'] = df1.groupby('country_encoded')['most_needs_idx'] \
            .transform(lambda x: x.shift(1).rolling(window=window).mean())

    # Add date-derived and Fourier seasonal features
    df1['month'] = df1['date'].dt.month
    df1['quarter'] = df1['date'].dt.quarter
    df1['dayofweek'] = df1['date'].dt.dayofweek
    #df1['is_weekend'] = int(df1['date'].dt.dayofweek in [5, 6])
    df1['is_weekend'] = df1['date'].dt.dayofweek.isin([5, 6]).astype(int)

    df1 = df1.dropna()

    # ----------------------
    # 3. Train/test split by date (time-aware)
    # ----------------------
    split_date = df1['date'].quantile(0.8)
    train_df = df1[df1['date'] <= split_date]
    test_df = df1[df1['date'] > split_date]


    features = ['country_encoded', #'conflict_norm', 'disaster_norm', 'hdi_norm',
                #'conflict_rolling_4w', 'conflict_rolling_12w', 'disaster_rolling_4w', 'disaster_rolling_12w', 
                'year', 'week_number',
                'month', 'quarter', 'dayofweek', 'is_weekend',
                'lag_1', 'lag_2', 'lag_3', 'rolling_mean_4', 'rolling_mean_8', 'rolling_mean_12', 'rolling_mean_26']
    target = 'most_needs_idx_target'

    X_train = train_df[features]
    y_train = train_df[target]
    X_test = test_df[features]
    y_test = test_df[target]

    # ----------------------
    # 4. Train multiple models
    # ----------------------
    models = {
        #'LinearRegression': LinearRegression(),
        #"Ridge": Ridge(),
        #"Lasso": Lasso(),
        "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42),
        "GradientBoosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
        "AdaBoost": AdaBoostRegressor(n_estimators=100, random_state=42),
        "KNN": KNeighborsRegressor(),
        "SVR": SVR(),
        "DecisionTree": DecisionTreeRegressor(random_state=42),
        "MLP": MLPRegressor(hidden_layer_sizes=(50, 30), max_iter=1000, random_state=42),
        "XGBoost": XGBRegressor(n_estimators=100, random_state=42),
        #"LightGBM": LGBMRegressor(n_estimators=100, random_state=42),
        "CatBoost": CatBoostRegressor(verbose=0, random_state=42)
    }

    results = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        rmse = mean_squared_error(y_test, y_pred, squared=False)
        results[name] = {'model': model, 'rmse': rmse}
        #print(f"{name}: RMSE = {rmse:.4f}")

    # ----------------------
    # 5. Select and use best model
    # ----------------------
    best_model_name = min(results, key=lambda k: results[k]['rmse'])
    best_model = results[best_model_name]['model']

    return best_model, features

#deprecated: predict_future()
def predict_future(df, best_model, features):
    # Store LabelEncoder map for interpretability
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    df['country_encoded'] = le.fit_transform(df['country'])
    country_map = dict(zip(le.classes_, le.transform(le.classes_)))
    inverse_map = dict(zip(le.transform(le.classes_), le.classes_))

    n_weeks = 26  # 6 months ahead
    all_forecasts = []

    # Make sure countries list is clean
    countries = df['country_encoded'].unique()

    for country in countries:
        # Get historical data for the country
        hist = df[df['country_encoded'] == country].copy()
        hist = hist.sort_values('date')
        
        last_date = hist['date'].max()
        future_preds = []

        for i in range(1, n_weeks + 1):
            next_date = last_date + pd.DateOffset(weeks=i)
            
            recent = hist.iloc[-1:].copy()
            next_row = {}

            # Time features
            next_row['date'] = next_date
            next_row['week_number'] = next_date.isocalendar().week
            next_row['year'] = next_date.isocalendar().year
            next_row['month'] = next_date.month
            next_row['quarter'] = next_date.quarter
            next_row['dayofweek'] = next_date.dayofweek
            next_row['is_weekend'] = int(next_date.dayofweek in [5, 6])
            next_row['country_encoded'] = country

            # Lag features
            recent_lags = hist['most_needs_idx']

            next_row['lag_1'] = recent_lags.iloc[-1] if len(recent_lags) >= 1 else None
            next_row['lag_2'] = recent_lags.iloc[-2] if len(recent_lags) >= 2 else None
            next_row['lag_3'] = recent_lags.iloc[-3] if len(recent_lags) >= 3 else None

            # Define rolling window sizes
            rolling_windows = [4, 8, 12, 26]

            # Compute and assign rolling means
            for w in rolling_windows:
                next_row[f'rolling_mean_{w}'] = hist['most_needs_idx'].tail(w).mean() if len(hist) >= w else None

            # Format for model input
            X_input = pd.DataFrame([next_row])
            pred = best_model.predict(X_input[features])[0]

            # Store prediction
            next_row['most_needs_idx'] = pred
            #next_row['model_prediction'] = pred
            future_preds.append(next_row)

            # Update hist for next iteration
            hist = pd.concat([hist, pd.DataFrame([next_row])], ignore_index=True)

        # Save all 26-week forecasts for this country
        all_forecasts.extend(future_preds)

    future_df = pd.DataFrame(all_forecasts)
    future_df['country'] = le.inverse_transform(future_df['country_encoded'])
    future_df = future_df[['date', 'country', 'most_needs_idx']]

    return future_df


def create_sequences(data, sequence_length):
    xs, ys = [], []
    for i in range(len(data) - sequence_length):
        x = data[i:i+sequence_length]
        y = data[i+sequence_length]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)


def model_prediction(full_df):

    full_df = full_df[['date', 'country', 'most_needs_idx']]
    #filter reliable data
    full_df = full_df[full_df['date'] >= '01-01-2018']

    # Initialize result containers
    all_historical_data = []
    all_predicted_past = []
    all_predicted_future = []

    countries = full_df['country'].unique()

    SEQUENCE_LENGTH = 12
    FUTURE_WEEKS = 26

    for country in countries:
        df = full_df[full_df['country'] == country].copy()
        df = df[['date', 'most_needs_idx']].rename(columns={'date': 'ds', 'most_needs_idx': 'y'})
        df = df.sort_values('ds')

        if len(df) <= SEQUENCE_LENGTH + FUTURE_WEEKS:
            print(f"Skipping {country} due to insufficient data.")
            continue

        # Normalize
        scaler = MinMaxScaler()
        df['y_scaled'] = scaler.fit_transform(df[['y']])

        data = df['y_scaled'].values
        X, y = create_sequences(data, SEQUENCE_LENGTH)

        split = int(len(X) * 0.8)
        X_train, y_train = X[:split], y[:split]
        X_test, y_test = X[split:], y[split:]
        dates_test = df['ds'].iloc[SEQUENCE_LENGTH+split:].reset_index(drop=True)

        X_train = X_train[..., np.newaxis]
        X_test = X_test[..., np.newaxis]

        # Model
        model = Sequential()
        model.add(LSTM(64, activation='relu', input_shape=(SEQUENCE_LENGTH, 1)))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mae')
        model.fit(X_train, y_train, epochs=50, batch_size=16, validation_split=0.1, verbose=0)

        # Predict past (test)
        predicted_test = model.predict(X_test)
        predicted_test = scaler.inverse_transform(predicted_test)
        y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))

        # Predict future
        last_sequence = data[-SEQUENCE_LENGTH:]
        future_predictions = []
        current_seq = last_sequence.copy()

        for _ in range(FUTURE_WEEKS):
            pred = model.predict(current_seq[np.newaxis, ..., np.newaxis])
            future_predictions.append(pred[0, 0])
            current_seq = np.append(current_seq[1:], pred[0, 0])
        future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))

        # Historical actuals (last 1 year)
        max_date = df['ds'].max()
        historical_start = max_date - pd.DateOffset(weeks=52)
        historical_df = df[(df['ds'] >= historical_start) & (df['ds'] <= max_date)].copy()
        historical_df['country'] = country

        # Predicted past (test set)
        predicted_past_df = pd.DataFrame({
            'ds': dates_test,
            'yhat': predicted_test.flatten(),
            'country': country
        })

        # Predicted future
        future_dates = pd.date_range(start=max_date + pd.DateOffset(weeks=1), periods=FUTURE_WEEKS, freq='W')
        predicted_future_df = pd.DataFrame({
            'ds': future_dates,
            'yhat': future_predictions.flatten(),
            'country': country
        })

        # Append to global lists
        all_historical_data.append(historical_df)
        all_predicted_past.append(predicted_past_df)
        all_predicted_future.append(predicted_future_df)

    # Final combined dataframes
    historical_data_df = pd.concat(all_historical_data, ignore_index=True)
    predicted_past_df = pd.concat(all_predicted_past, ignore_index=True)
    predicted_future_df = pd.concat(all_predicted_future, ignore_index=True)

    return historical_data_df, predicted_past_df, predicted_future_df



def main():

    logger.info("[ccar_model] Running... ")

    df = pd.read_csv('data/ccar_merged.csv')

    # Combine year and week number to get a datetime column
    df['date'] = pd.to_datetime(df['year'].astype(str) + df['week_number'].astype(str) + '1', format='%G%V%u')

    # Sort by date
    df.sort_values(['country', 'date'], inplace=True)

    #Define new armed conflict feature composed by other two conflict feature
    df['armed_conflict'] = df['num_conflicts_explosions_remote_violence'] + df['num_conflicts_battles']

    #Filter features relevant to the most needs index prediction
    df = df[['year', 'week_number', 'date', 'country', 'armed_conflict', 'num_affected_disaster', 'HDI']]

    #Use log-transform on armed_conflict and num_affected_disaster before scaling to compress outliers
    df['armed_conflict'] = np.log1p(df['armed_conflict'])
    df['num_affected_disaster'] = np.log1p(df['num_affected_disaster'])

    #Replace HDI=0 if missing
    df['HDI'] = df['HDI'].replace(0, np.nan)

    #for Na values: Impute HDI using country average or region
    df['HDI'] = df['HDI'].fillna(df['HDI'].mean())

    #Invert HDI so low HDI = high need
    df['HDI'] = 1 - df['HDI']

    #Normalize all fetures to be 0 to 1 scale
    scaler = MinMaxScaler()
    df[['conflict_norm', 'disaster_norm', 'hdi_norm']] = scaler.fit_transform(
        df[['armed_conflict', 'num_affected_disaster', 'HDI']]
    )

    # Apply weights (adjustable or equal by default)
    w_conflict = 20/50
    w_disaster = 3/50
    w_hdi = 27/50

    #define target variable most needs index
    df['most_needs_idx'] = (
        w_conflict * df['conflict_norm'] +
        w_disaster * df['disaster_norm'] +
        w_hdi * df['hdi_norm']
    )

    df['most_needs_idx'] = df['most_needs_idx'].ewm(span=12, adjust=False).mean()

    df = df[['date', 'country', 'most_needs_idx']]

    #model, features = get_best_model(df)

    #pred_df = predict_future(df, model, features)

    #pred_df.to_csv('data/ccar_prediction.csv', index=False)

    #df.to_csv('data/ccar_historical.csv', index=False)

    historical_data_df, predicted_past_df, predicted_future_df = model_prediction(df)

    historical_data_df = historical_data_df[['ds','y','country']].rename(columns={'ds': 'date', 'y': 'most_needs_idx'})
    historical_data_df.to_csv('data/ccar_historical_data.csv', index=False)
    
    predicted_past_df = predicted_past_df.rename(columns={'ds': 'date', 'yhat': 'most_needs_idx'})
    predicted_past_df.to_csv('data/ccar_predicted_past.csv', index=False)
    
    predicted_future_df = predicted_future_df.rename(columns={'ds': 'date', 'yhat': 'most_needs_idx'})    
    predicted_future_df.to_csv('data/ccar_predicted_future.csv', index=False)

    logger.info("[ccar_model] finshed successfully ")