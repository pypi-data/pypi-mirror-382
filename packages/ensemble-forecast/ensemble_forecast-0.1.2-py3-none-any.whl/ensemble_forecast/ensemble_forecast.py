import pandas as pd
import numpy as np
import warnings
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.exponential_smoothing.ets import ETSModel
from pmdarima.arima import auto_arima
from tbats import TBATS, BATS
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import mean_squared_error, mean_absolute_error
import itertools
import concurrent.futures

warnings.filterwarnings('ignore')

class EnsembleForecast:
    """
    Ensemble Forecasting package for combining multiple time series models such as 
    ARIMA, SARIMA, Croston, Holt, and Holt-Winters . 
    It supports automatic model selection, ensembling, optimization, 
    and robust handling of missing or irregular data.

    Parameters
    ----------
    datetime_col : str, default 'Month_Year'
        Name of the datetime column in the dataset.

    datetime_type : str, default 'M'
        Type of datetime aggregation:
        'M' = Monthly, 'Y' = Yearly, 'D' = Daily.

    forecast_span : int, default 18
        Number of future periods to forecast.

    value_col : str, default 'Movement'
        Column containing numeric values to forecast.

    test_size : float, default 0.2
        Fraction of data to reserve for testing (between 0 and 1).

    error_metric : str, default 'mape'
        Error metric for model evaluation.
        Options: 'rmse', 'mape', 'smape', 'mae', 'mse'.

    top_models : int, default None
        Number of top-performing models to use for ensemble.
        If None, only the best single model is used.

    ensemble_weights : list, default None
        List of weights for ensemble models. 
        If None, all selected models are equally weighted.

    optimization : str, default None
        Optimization method for final forecast blending.
        Options: 'mean', 'median', 'mode', or None.

    optimization_length : int, default 12
        Number of recent periods used for optimization (e.g., 3, 6, or 12).

    optimization_ratio : str, default "70:30"
        Ratio for blending ensemble forecast with historical optimization (e.g., "70:30", "75:25").

    null_fill_method : str, int, or float, default None
        Method or value to handle missing data.
        Options: 'ffill', 'bfill', 'mean', 'median', 'zero', 'interpolate', None,
        or a custom numeric value (e.g., 0, 100).

    parallel_processing : bool, default False
        If True, models are trained in parallel to speed up execution.

    model_list : list, default 
        ['ARIMA', 'SARIMA', 'Croston', 'Holt', 'HoltWinters', 'ETS', 
        'AutoARIMA', 'Naive', 'SeasonalNaive']
        List of models to include in the ensemble.
        Additional supported models: 'TBATS', 'BATS', 'Theta', 'Prophet', 'LSTM', 'NeuralNetwork'.

    enable_logging : bool, default False
        If True, detailed logs of each step are printed and/or stored.

    forecast_capping : bool, default False
        If True, forecasts are capped at zero (no negatives) 
        and limited to the maximum observed historical value.

    fallback_strategy : str, default 'zero'
        Strategy to use if a model fails to produce forecasts.
        Options:
            '3_mean', '6_mean', '12_mean', 
            '3_median', '6_median', '12_median', 
            'last_value', 'zero'.
    """

    def __init__(self, datetime_col='Month_Year', datetime_type='M', forecast_span=18,
                 value_col='Movement', test_size=0.2, error_metric='rmse',
                 top_models=None, ensemble_weights=None, optimization=None, optimization_length=12, optimization_ratio='70:30', null_fill_method=None, parallel_processing=False,
                 model_list=['ARIMA', 'SARIMA', 'Croston', 'Holt', 'HoltWinters'], enable_logging=True, forecast_capping=False, forecast_fallback_strategy='zero'):
        self.datetime_col = datetime_col
        self.datetime_type = datetime_type.upper()
        self.forecast_span = forecast_span
        self.value_col = value_col
        self.test_size = test_size
        self.error_metric = error_metric.lower()
        self.top_models = top_models
        self.ensemble_weights = ensemble_weights
        self.optimization = optimization
        self.optimization_length = optimization_length
        self.optimization_ratio = optimization_ratio
        self.model_list = model_list
        self.null_fill_method = null_fill_method
        self.parallel_processing = parallel_processing
        self.enable_logging = enable_logging
        self.forecast_capping = forecast_capping
        self.fallback_strategy = forecast_fallback_strategy

        # Initialize model results storage
        self.model_results = {}
        self.best_model = None
        self.ensemble_forecast = None
        self.final_forecast = None
        
        # Initialize logging system
        self.logs = []
        self._log_session_start()
        
        # Validate inputs
        self._validate_inputs()

        # Validate fallback strategy
        self._validate_fallback_strategy()

        # Validate null fill method
        self._validate_null_fill_method()
    
    def _log(self, message, level='INFO', print_msg=True):
        """Add a log entry with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        self.logs.append(log_entry)
        
        if print_msg and self.enable_logging:
            print(f"[{level}] {message}")

    def _log_session_start(self):
        """Log the start of a forecasting session"""
        self._log("=" * 60, print_msg=False)
        self._log(f"Ensemble Forecast Session Started", level='SESSION', print_msg=False)
        self._log(f"Parameters: datetime_type={self.datetime_type}, forecast_span={self.forecast_span}, "
                 f"error_metric={self.error_metric}, models={self.model_list}", print_msg=False)
        self._log("=" * 60, print_msg=False)

    def _validate_inputs(self):
        """Validate input parameters"""
        self._log("Validating input parameters...", print_msg=False)
        if self.datetime_type.upper() not in ['M', 'Y', 'D']:
            error_message = "datetime_type must be 'M' (monthly), 'Y' (yearly), or 'D' (daily)"
            self._log(error_message, level='ERROR')
            raise ValueError(error_message)
        
        if not 0 < self.test_size < 1:
            error_message = "test_size must be between 0 and 1"
            self._log(error_message, level='ERROR')
            raise ValueError(error_message)
        
        if self.error_metric.lower() not in ['rmse', 'mape', 'smape', 'mae', 'mse']:
            error_message = "error_metric must be one of: 'rmse', 'mape', 'smape', 'mae', 'mse'"
            self._log(error_message, level='ERROR')
            raise ValueError(error_message)
        
        # --- MODEL LIST VALIDATION ---
        valid_models = {
            'ARIMA', 'SARIMA', 'Croston', 'Holt', 'HoltWinters', 'ETS',
            'AutoARIMA', 'Naive', 'SeasonalNaive', 'TBATS', 'BATS',
            'Theta', 'Prophet', 'LSTM', 'NeuralNetwork'
        }

        if not self.model_list or not isinstance(self.model_list, (list, tuple)) or len(self.model_list) == 0:
            error_message = "model_list cannot be empty and must be a list or tuple with at least one model."
            self._log(error_message, level='ERROR')
            raise ValueError(error_message)

        # Check for invalid model names
        invalid_models = [m for m in self.model_list if m not in valid_models]
        if invalid_models:
            msg = f"Invalid model(s) in model_list: {invalid_models}. Allowed models are: {sorted(valid_models)}"
            self._log(msg, level='ERROR')
            raise ValueError(msg)

        # --- MODEL LIST VALIDATION ---
        if not self.model_list or not isinstance(self.model_list, (list, tuple)) or len(self.model_list) == 0:
            error_message = "model_list cannot be empty and must be a list or tuple with at least one model."
            self._log(error_message, level='ERROR')
            raise ValueError(error_message)

        # --- TOP MODELS VALIDATION ---
        if self.top_models is not None:
            if not isinstance(self.top_models, int) or self.top_models <= 0:
                msg = f"top_models must be a positive integer, got: {self.top_models}"
                self._log(msg, level='ERROR')
                raise ValueError(msg)

            if self.top_models > len(self.model_list):
                msg = (
                    f"top_models ({self.top_models}) cannot exceed the number of models in model_list "
                    f"({len(self.model_list)})."
                )
                self._log(msg, level='ERROR')
                raise ValueError(msg)
        
        # --- ENSEMBLE WEIGHTS VALIDATION ---
        if self.top_models is not None:
            if self.ensemble_weights is None:
                # Default equal weights if user didn't specify
                equal_weight = round(1 / self.top_models, 4)
                self.ensemble_weights = [equal_weight] * self.top_models
                self._log(
                    f"No ensemble_weights provided. Defaulting to equal weights: {self.ensemble_weights}",
                    level='INFO',
                    print_msg=False
                )
            else:
                # Type check
                if not isinstance(self.ensemble_weights, (list, tuple)):
                    raise TypeError("ensemble_weights must be a list or tuple of numeric values.")

                # Length check
                if len(self.ensemble_weights) != self.top_models:
                    msg = (
                        f"Length of ensemble_weights ({len(self.ensemble_weights)}) "
                        f"must equal top_models ({self.top_models})."
                    )
                    self._log(msg, level='ERROR')
                    raise ValueError(msg)

                # Sum normalization check
                total = sum(self.ensemble_weights)
                if not abs(total - 1.0) < 1e-6:
                    self._log(
                        f"Ensemble weights sum to {total:.4f}. Normalizing to 1.0 automatically.",
                        level='WARNING',
                        print_msg=False
                    )
                    self.ensemble_weights = [w / total for w in self.ensemble_weights]       
        
        if self.top_models is not None and self.top_models > len(self.model_list):
            self._log(
                f"top_models ({self.top_models}) is greater than the number of models in model_list "
                f"({len(self.model_list)}). Setting top_models to None (best single model).",
                level='WARNING',
                print_msg=False
            )
            self.top_models = None

        # --- OPTIMIZATION VALIDATIONS ---
        if self.optimization is not None:
            valid_optimizations = ['mean', 'median', 'mode']
            if self.optimization.lower() not in valid_optimizations:
                msg = (
                    f"Invalid optimization '{self.optimization}'. "
                    f"Valid options are {valid_optimizations} or None."
                )
                self._log(msg, level='ERROR')
                raise ValueError(msg)

            # optimization_length check
            if not isinstance(self.optimization_length, int) or self.optimization_length <= 0:
                msg = "optimization_length must be a positive integer (e.g., 3, 6, 12)."
                self._log(msg, level='ERROR')
                raise ValueError(msg)

            # optimization_ratio format check
            if not isinstance(self.optimization_ratio, str) or ':' not in self.optimization_ratio:
                msg = (
                    "optimization_ratio must be a string in the format 'X:Y' (e.g., '70:30')."
                )
                self._log(msg, level='ERROR')
                raise ValueError(msg)

            try:
                parts = self.optimization_ratio.split(':')
                forecast_w, opt_w = float(parts[0]), float(parts[1])
                total = forecast_w + opt_w
                if abs(total - 100) > 1e-6:
                    msg = f"optimization_ratio values must sum to 100 (current sum: {total})."
                    self._log(msg, level='ERROR')
                    raise ValueError(msg)
            except Exception:
                msg = (
                    "Invalid optimization_ratio format. Expected 'X:Y' where X and Y are numbers "
                    "that sum to 100 (e.g., '70:30')."
                )
                self._log(msg, level='ERROR')
                raise ValueError(msg)

    def _validate_null_fill_method(self):
        """Validate the null_fill_method parameter."""
        valid_methods = ['ffill', 'bfill', 'mean', 'median', 'zero', 'interpolate', None, 'none']

        # Check if it's a numeric value
        if isinstance(self.null_fill_method, (int, float)):
            return  # valid custom numeric fill

        if isinstance(self.null_fill_method, str) and self.null_fill_method.strip().lower() == 'none':
            self.null_fill_method = None
            return
        
        # If not numeric, validate string/None
        if self.null_fill_method not in valid_methods:
            error_msg = (
                f"Invalid null_fill_method: {self.null_fill_method}. "
                f"Choose from {valid_methods[:-1]} or provide a numeric value."
            )
            self._log(error_msg, level='ERROR')
            raise ValueError(error_msg)

        # Convert string 'none' → None for consistency
        if isinstance(self.null_fill_method, str) and self.null_fill_method.lower() == 'none':
            self.null_fill_method = None
  
    def _validate_fallback_strategy(self):
        """Validate fallback strategy parameter"""
        valid_strategies = ['3_mean', '6_mean', '12_mean', 
                        '3_median', '6_median', '12_median',
                        'last_value', 'zero']
        if self.fallback_strategy not in valid_strategies:
            error_msg = f"fallback_strategy must be one of: {valid_strategies}"
            self._log(error_msg, level='ERROR')
            raise ValueError(error_msg)

    def _prepare_datetime(self, df):
        """
        Convert the datetime column to pandas datetime/period type and aggregate
        the value column based on the specified datetime_type.

        Supports different datetime formats (US/UK) and pandas Period types.

        Supported datetime_type: 'D' (day), 'M' (month), 'Y' (year), 'Q' (quarter)
        """
        self._log("Preparing datetime column...", print_msg=False)
        df = df.copy()

        if self.datetime_col not in df.columns:
            raise ValueError(f"Column '{self.datetime_col}' not found in DataFrame.")

        # Convert to datetime
        # dayfirst=True ensures UK format (DD/MM/YYYY) is correctly parsed
        # pandas will also infer US format if dayfirst=False
        try:
            df[self.datetime_col] = pd.to_datetime(df[self.datetime_col], dayfirst=True, errors='raise', infer_datetime_format=True)
        except Exception as e:
            raise ValueError(f"Error parsing datetime column '{self.datetime_col}': {e}")

        # Map datetime_type to pandas period
        period_map = {'D':'D', 'M':'M', 'Y':'Y'}
        agg_period = period_map.get(self.datetime_type.upper())
        if agg_period is None:
            raise ValueError(f"Invalid datetime_type '{self.datetime_type}'. Supported: {list(period_map.keys())}")

        # Convert to period and aggregate
        df[self.datetime_col] = df[self.datetime_col].dt.to_period(agg_period)
        df = df.groupby(self.datetime_col, as_index=False)[self.value_col].agg('sum', min_count=1)

        # Sort
        df = df.sort_values(self.datetime_col).reset_index(drop=True)

        self._log(f"Datetime preparation complete. Data spans from {df[self.datetime_col].min()} to {df[self.datetime_col].max()}.", print_msg=False)
        return df

    def _handle_missing_values(self, df):
        """Handle missing datetimes and missing values in the value column."""
        df = df.copy()
        min_dt = df[self.datetime_col].min()
        max_dt = df[self.datetime_col].max()
        
        # Create full datetime index according to self.datetime_type
        if self.datetime_type == 'M':
            all_times = pd.period_range(min_dt, max_dt, freq='M')
        elif self.datetime_type == 'Y':
            all_times = pd.period_range(min_dt, max_dt, freq='Y')
        elif self.datetime_type == 'D':
            all_times = pd.period_range(min_dt, max_dt, freq='D')
        else:
            raise ValueError('Invalid datetime_type')
        
        df = df.set_index(self.datetime_col)
        df = df.reindex(all_times)
        df = df.reset_index()
        df.rename(columns={'index': self.datetime_col}, inplace=True)
        
        null_count = df[self.value_col].isnull().sum()
        if null_count > 0:
            msg = f'{null_count} missing values found in {self.value_col}. Applying {self.null_fill_method} method.'
            self._log(msg, level='WARNING')
            
            # Fill missing values as per null_fill_method
            if self.null_fill_method == 'ffill':
                df[self.value_col] = df[self.value_col].fillna(method='ffill')
            elif self.null_fill_method == 'bfill':
                df[self.value_col] = df[self.value_col].fillna(method='bfill')
            elif self.null_fill_method == 'mean':
                df[self.value_col] = df[self.value_col].fillna(df[self.value_col].mean(skipna=True))
            elif self.null_fill_method == 'median':
                df[self.value_col] = df[self.value_col].fillna(df[self.value_col].median(skipna=True))
            elif self.null_fill_method == 'zero':
                df[self.value_col] = df[self.value_col].fillna(0)
            elif self.null_fill_method == 'interpolate':
                df[self.value_col] = df[self.value_col].interpolate(method='linear', limit_direction='both')
            elif isinstance(self.null_fill_method, (int, float)):  # custom numeric fill
                df[self.value_col] = df[self.value_col].fillna(self.null_fill_method)
                self._log(f"Filled missing values with custom value: {self.null_fill_method}", print_msg=False)
            elif self.null_fill_method is None or str(self.null_fill_method).lower() == 'none':
                if df[self.value_col].isnull().any():
                    error_msg = f'Missing values found in {self.value_col}. Please specify a null_fill_method.'
                    self._log(error_msg, level='ERROR')
                    raise ValueError(error_msg)
            else:
                error_msg = "Invalid null_fill_method. Choose from 'ffill', 'bfill', 'mean', 'median', 'zero', 'interpolate', numeric value, or None."
                self._log(error_msg, level='ERROR')
                raise ValueError(error_msg)
        
        return df

    def _calculate_errors(self, actual, predicted):
        """Calculate various error metrics"""
        errors = {}
        
        # Remove any NaN values
        mask = ~(np.isnan(actual) | np.isnan(predicted))
        actual_clean = actual[mask]
        predicted_clean = predicted[mask]
        
        if len(actual_clean) == 0:
            return {metric: np.inf for metric in ['rmse', 'mape', 'smape', 'mae', 'mse']}
        
        errors['mse'] = mean_squared_error(actual_clean, predicted_clean)
        errors['rmse'] = np.sqrt(errors['mse'])
        errors['mae'] = mean_absolute_error(actual_clean, predicted_clean)
        
        # MAPE (Mean Absolute Percentage Error)
        with np.errstate(divide='ignore', invalid='ignore'):
            mape = np.mean(np.abs((actual_clean - predicted_clean) / actual_clean)) * 100
            errors['mape'] = mape if not np.isnan(mape) else np.inf
        
        # SMAPE (Symmetric Mean Absolute Percentage Error)
        with np.errstate(divide='ignore', invalid='ignore'):
            smape = np.mean(2 * np.abs(actual_clean - predicted_clean) / 
                           (np.abs(actual_clean) + np.abs(predicted_clean))) * 100
            errors['smape'] = smape if not np.isnan(smape) else np.inf
        
        return errors
    
    def _fit_arima(self, train_data, test_data):
        """Fit ARIMA model with automatic order selection"""
        try:
            self._log("Fitting ARIMA model...", print_msg=False)
            # Simple grid search for ARIMA parameters
            best_aic = np.inf
            best_order = None
            best_model = None
            
            # Test different orders
            orders = [(p, d, q) for p in range(3) for d in range(2) for q in range(3)]
            
            for order in orders:
                try:
                    model = ARIMA(train_data, order=order)
                    fitted_model = model.fit()
                    if fitted_model.aic < best_aic:
                        best_aic = fitted_model.aic
                        best_order = order
                        best_model = fitted_model
                except:
                    continue
            
            if best_model is None:
                self._log("ARIMA fitting failed - no valid model found", level='WARNING', print_msg=False)
                return None, np.inf, None
            
            # Make predictions on test set
            test_pred = best_model.forecast(steps=len(test_data))
            
            # Calculate errors
            errors = self._calculate_errors(test_data.values, test_pred)

            self._log(f"ARIMA fitted successfully. Order: {best_order}, AIC: {best_aic:.2f}, "
                     f"{self.error_metric.upper()}: {errors[self.error_metric]:.4f}", print_msg=False)
            
            return best_model, errors[self.error_metric], test_pred
            
        except Exception as e:
            self._log(f"ARIMA fitting error: {str(e)}", level='ERROR', print_msg=False)
            return None, np.inf, None
    
    def _fit_sarima(self, train_data, test_data):
        """Fit SARIMA model with automatic parameter selection"""
        try:
            self._log("Fitting SARIMA model...", print_msg=False)
            # Determine seasonality based on datetime_type
            if self.datetime_type == 'M':
                seasonal_period = 12
            elif self.datetime_type == 'Y':
                seasonal_period = 1  # No seasonality for yearly data
            else:  # Daily
                seasonal_period = 7
            
            if seasonal_period == 1 or len(train_data) < 2 * seasonal_period:
                self._log("Insufficient data for seasonality, falling back to ARIMA", print_msg=False)
                return self._fit_arima(train_data, test_data)
            
            best_aic = np.inf
            best_order = None
            best_seasonal_order = None
            best_model = None
            
            # Test different orders (simplified grid search)
            orders = [(p, d, q) for p in range(2) for d in range(2) for q in range(2)]
            seasonal_orders = [(P, D, Q, seasonal_period) for P in range(2) for D in range(2) for Q in range(2)]
            
            for order in orders[:6]:  # Limit search to prevent long runtime
                for seasonal_order in seasonal_orders[:4]:
                    try:
                        model = SARIMAX(train_data, order=order, seasonal_order=seasonal_order)
                        fitted_model = model.fit(disp=False)
                        if fitted_model.aic < best_aic:
                            best_aic = fitted_model.aic
                            best_order = order
                            best_seasonal_order = seasonal_order
                            best_model = fitted_model
                    except:
                        continue
            
            if best_model is None:
                self._log("SARIMA fitting failed - no valid model found", level='WARNING', print_msg=False)
                return None, np.inf, None
            
            # Make predictions on test set
            test_pred = best_model.forecast(steps=len(test_data))
            
            # Calculate errors
            errors = self._calculate_errors(test_data.values, test_pred)
            
            self._log(f"SARIMA fitted successfully. Order: {best_order}, Seasonal: {best_seasonal_order}, "
                     f"AIC: {best_aic:.2f}, {self.error_metric.upper()}: {errors[self.error_metric]:.4f}", 
                     print_msg=False)
            
            return best_model, errors[self.error_metric], test_pred
            
        except Exception as e:
            return None, np.inf, None
    
    def _fit_croston(self, train_data, test_data):
        """Fit Croston's method for intermittent demand"""
        self._log("Fitting Croston's method...", print_msg=False)
        try:
            # Simple Croston's method implementation
            alpha = 0.3  # Smoothing parameter
            
            # Identify non-zero demands
            non_zero_indices = np.where(train_data > 0)[0]
            
            if len(non_zero_indices) < 2:
                self._log("Croston fitting failed - insufficient non-zero demands", level='WARNING', print_msg=False)
                return None, np.inf, None
            
            # Initialize
            z = train_data.iloc[non_zero_indices[0]]  # First non-zero demand
            x = non_zero_indices[0] + 1  # First interval
            
            # Update estimates
            for i in range(1, len(non_zero_indices)):
                current_demand = train_data.iloc[non_zero_indices[i]]
                current_interval = non_zero_indices[i] - non_zero_indices[i-1]
                
                z = alpha * current_demand + (1 - alpha) * z
                x = alpha * current_interval + (1 - alpha) * x
            
            # Forecast
            forecast_value = z / x if x > 0 else 0
            test_pred = np.full(len(test_data), forecast_value)
            
            # Calculate errors
            errors = self._calculate_errors(test_data.values, test_pred)
            
            # Store model parameters for later use
            model_params = {'z': z, 'x': x, 'forecast_value': forecast_value}
            
            self._log(f"Croston fitted successfully. Forecast value: {forecast_value:.2f}, "
                     f"{self.error_metric.upper()}: {errors[self.error_metric]:.4f}", print_msg=False)
            
            return model_params, errors[self.error_metric], test_pred
            
        except Exception as e:
            self._log(f"Croston fitting error: {str(e)}", level='ERROR', print_msg=False)
            return None, np.inf, None
    
    def _fit_holt(self, train_data, test_data):
        """Fit Holt's linear trend method"""
        try:
            self._log("Fitting Holt model...", print_msg=False)
            model = ExponentialSmoothing(train_data, trend='add')
            fitted_model = model.fit()
            
            # Make predictions on test set
            test_pred = fitted_model.forecast(steps=len(test_data))
            
            # Calculate errors
            errors = self._calculate_errors(test_data.values, test_pred)
            
            self._log(f"Holt fitted successfully. {self.error_metric.upper()}: {errors[self.error_metric]:.4f}", 
                     print_msg=False)
            
            return fitted_model, errors[self.error_metric], test_pred
            
        except Exception as e:
            self._log(f"Holt fitting error: {str(e)}", level='ERROR', print_msg=False)
            return None, np.inf, None
    
    def _fit_holt_winters(self, train_data, test_data):
        """Fit Holt-Winters exponential smoothing"""
        try:
            self._log("Fitting Holt-Winters model...", print_msg=False)
            # Determine seasonality
            if self.datetime_type == 'M':
                seasonal_periods = 12
            elif self.datetime_type == 'Y':
                seasonal_periods = 1
            else:  # Daily
                seasonal_periods = 7
            
            if seasonal_periods == 1 or len(train_data) < 2 * seasonal_periods:
                # Fall back to Holt if insufficient data for seasonality
                self._log("Insufficient data for seasonality, falling back to Holt", print_msg=False)
                return self._fit_holt(train_data, test_data)
            
            model = ExponentialSmoothing(
                train_data, 
                trend='add', 
                seasonal='add', 
                seasonal_periods=seasonal_periods
            )
            fitted_model = model.fit()
            
            # Make predictions on test set
            test_pred = fitted_model.forecast(steps=len(test_data))
            
            # Calculate errors
            errors = self._calculate_errors(test_data.values, test_pred)
            
            return fitted_model, errors[self.error_metric], test_pred
            
        except Exception as e:
            return None, np.inf, None
    
    def _fit_ets(self, train_data, test_data):
        """Fit ETS (Error, Trend, Seasonality) model"""
        try:
            self._log("Fitting ETS model...", print_msg=False)
            
            # Determine seasonal periods
            if self.datetime_type == 'M':
                seasonal_periods = 12
            elif self.datetime_type == 'Y':
                seasonal_periods = 1
            else:
                seasonal_periods = 7
            
            # Try different ETS configurations
            best_aic = np.inf
            best_model = None
            
            if seasonal_periods == 1 or len(train_data) < 2 * seasonal_periods:
                # No seasonality
                configs = [
                    {'error': 'add', 'trend': 'add', 'seasonal': None},
                    {'error': 'mul', 'trend': 'add', 'seasonal': None},
                    {'error': 'add', 'trend': None, 'seasonal': None}
                ]
            else:
                # With seasonality
                configs = [
                    {'error': 'add', 'trend': 'add', 'seasonal': 'add', 'seasonal_periods': seasonal_periods},
                    {'error': 'add', 'trend': 'add', 'seasonal': 'mul', 'seasonal_periods': seasonal_periods},
                    {'error': 'mul', 'trend': 'add', 'seasonal': 'add', 'seasonal_periods': seasonal_periods}
                ]
            
            for config in configs:
                try:
                    model = ETSModel(train_data, **config)
                    fitted_model = model.fit(disp=False)
                    if fitted_model.aic < best_aic:
                        best_aic = fitted_model.aic
                        best_model = fitted_model
                except:
                    continue
            
            if best_model is None:
                self._log("ETS fitting failed - no valid model found", level='WARNING', print_msg=False)
                return None, np.inf, None
            
            # Make predictions
            test_pred = best_model.forecast(steps=len(test_data))
            errors = self._calculate_errors(test_data.values, test_pred)
            
            self._log(f"ETS fitted successfully. AIC: {best_aic:.2f}, "
                    f"{self.error_metric.upper()}: {errors[self.error_metric]:.4f}", print_msg=False)
            
            return best_model, errors[self.error_metric], test_pred
            
        except Exception as e:
            self._log(f"ETS fitting error: {str(e)}", level='ERROR', print_msg=False)
            return None, np.inf, None

    def _fit_auto_arima(self, train_data, test_data):
        """Fit Auto ARIMA (pmdarima) model with automatic parameter selection"""
        try:
            self._log("Fitting Auto ARIMA model...", print_msg=False)
            
            # Determine seasonality
            if self.datetime_type == 'M':
                m = 12
            elif self.datetime_type == 'Y':
                m = 1
            else:
                m = 7
            
            # Fit auto_arima
            model = auto_arima(
                train_data,
                seasonal=True if m > 1 and len(train_data) >= 2*m else False,
                m=m,
                stepwise=True,
                suppress_warnings=True,
                error_action='ignore',
                trace=False,
                maxiter=10
            )
            
            # Make predictions
            test_pred = model.predict(n_periods=len(test_data))
            errors = self._calculate_errors(test_data.values, test_pred)
            
            self._log(f"Auto ARIMA fitted successfully. Order: {model.order}, "
                    f"Seasonal Order: {model.seasonal_order}, "
                    f"{self.error_metric.upper()}: {errors[self.error_metric]:.4f}", print_msg=False)
            
            return model, errors[self.error_metric], test_pred
            
        except Exception as e:
            self._log(f"Auto ARIMA fitting error: {str(e)}", level='ERROR', print_msg=False)
            return None, np.inf, None

    def _fit_tbats(self, train_data, test_data):
        """Fit TBATS (Trigonometric seasonality, Box-Cox transformation, ARMA errors, Trend, Seasonal)"""
        try:
            # Lazy import
            try:
                from tbats import TBATS
            except ImportError:
                self._log("tbats package not installed. Install with: pip install tbats", level='ERROR', print_msg=False)
                return None, np.inf, None
            
            self._log("Fitting TBATS model...", print_msg=False)
            
            # Determine seasonal periods
            if self.datetime_type == 'M':
                seasonal_periods = [12] if len(train_data) >= 36 else None  # Need 3 years minimum
            elif self.datetime_type == 'Y':
                seasonal_periods = None
            else:
                seasonal_periods = [7] if len(train_data) >= 21 else None  # Need 3 weeks minimum
            
            # Check if we have enough data
            if seasonal_periods is None:
                self._log(f"TBATS skipped - insufficient data ({len(train_data)} periods) or no seasonality", 
                        level='WARNING', print_msg=False)
                return None, np.inf, None
            
            # Check for variance in data
            if train_data.std() < 0.01:
                self._log("TBATS skipped - data has very low variance", level='WARNING', print_msg=False)
                return None, np.inf, None
            
            # Fit TBATS with timeout protection
            model = TBATS(
                seasonal_periods=seasonal_periods, 
                use_box_cox=False,  # Disable Box-Cox to avoid errors with zeros/negatives
                use_trend=True,
                use_arma_errors=True,
                show_warnings=False,
                n_jobs=1
            )
            
            fitted_model = model.fit(train_data.values)
            
            # Make predictions
            test_pred = fitted_model.forecast(steps=len(test_data))
            
            # Check if forecast is valid
            if np.any(np.isnan(test_pred)) or np.any(np.isinf(test_pred)):
                self._log("TBATS produced invalid forecasts (NaN or Inf)", level='WARNING', print_msg=False)
                return None, np.inf, None
            
            errors = self._calculate_errors(test_data.values, test_pred)
            
            self._log(f"TBATS fitted successfully. "
                    f"{self.error_metric.upper()}: {errors[self.error_metric]:.4f}", print_msg=False)
            
            return fitted_model, errors[self.error_metric], test_pred
            
        except Exception as e:
            self._log(f"TBATS fitting error: {str(e)}", level='WARNING', print_msg=False)
            return None, np.inf, None

    def _fit_bats(self, train_data, test_data):
        """Fit BATS (Box-Cox transformation, ARMA errors, Trend, Seasonal)"""
        try:
            # Lazy import
            try:
                from tbats import BATS
            except ImportError:
                self._log("tbats package not installed. Install with: pip install tbats", level='ERROR', print_msg=False)
                return None, np.inf, None
            
            self._log("Fitting BATS model...", print_msg=False)
            
            # Determine seasonal periods
            if self.datetime_type == 'M':
                seasonal_periods = [12] if len(train_data) >= 36 else None
            elif self.datetime_type == 'Y':
                seasonal_periods = None
            else:
                seasonal_periods = [7] if len(train_data) >= 21 else None
            
            # Check if we have enough data
            if seasonal_periods is None:
                self._log(f"BATS skipped - insufficient data ({len(train_data)} periods) or no seasonality", 
                        level='WARNING', print_msg=False)
                return None, np.inf, None
            
            # Check for variance
            if train_data.std() < 0.01:
                self._log("BATS skipped - data has very low variance", level='WARNING', print_msg=False)
                return None, np.inf, None
            
            # Fit BATS
            model = BATS(
                seasonal_periods=seasonal_periods, 
                use_box_cox=False,  # Disable Box-Cox
                use_trend=True,
                use_arma_errors=True,
                show_warnings=False,
                n_jobs=1
            )
            
            fitted_model = model.fit(train_data.values)
            
            # Make predictions
            test_pred = fitted_model.forecast(steps=len(test_data))
            
            # Check if forecast is valid
            if np.any(np.isnan(test_pred)) or np.any(np.isinf(test_pred)):
                self._log("BATS produced invalid forecasts (NaN or Inf)", level='WARNING', print_msg=False)
                return None, np.inf, None
            
            errors = self._calculate_errors(test_data.values, test_pred)
            
            self._log(f"BATS fitted successfully. "
                    f"{self.error_metric.upper()}: {errors[self.error_metric]:.4f}", print_msg=False)
            
            return fitted_model, errors[self.error_metric], test_pred
            
        except Exception as e:
            self._log(f"BATS fitting error: {str(e)}", level='WARNING', print_msg=False)
            return None, np.inf, None

    def _fit_theta(self, train_data, test_data):
        """Fit Theta method (simple and effective for short-term forecasting)"""
        try:
            self._log("Fitting Theta model...", print_msg=False)
            
            # Theta method implementation
            n = len(train_data)
            
            # Calculate trend (theta line with theta=2)
            x = np.arange(n)
            coeffs = np.polyfit(x, train_data.values, 1)
            trend = np.polyval(coeffs, x)
            
            # Detrend
            detrended = train_data.values - trend
            
            # Simple exponential smoothing on detrended series
            alpha = 0.5
            ses = [detrended[0]]
            for val in detrended[1:]:
                ses.append(alpha * val + (1 - alpha) * ses[-1])
            
            # Forecast
            last_trend_value = coeffs[0] * n + coeffs[1]
            trend_slope = coeffs[0]
            
            test_pred = []
            for i in range(1, len(test_data) + 1):
                trend_forecast = last_trend_value + trend_slope * i
                level_forecast = ses[-1]
                test_pred.append(trend_forecast + level_forecast)
            
            test_pred = np.array(test_pred)
            errors = self._calculate_errors(test_data.values, test_pred)
            
            # Store parameters for later use
            model_params = {
                'coeffs': coeffs,
                'ses_last': ses[-1],
                'alpha': alpha,
                'n': n
            }
            
            self._log(f"Theta fitted successfully. "
                    f"{self.error_metric.upper()}: {errors[self.error_metric]:.4f}", print_msg=False)
            
            return model_params, errors[self.error_metric], test_pred
            
        except Exception as e:
            self._log(f"Theta fitting error: {str(e)}", level='ERROR', print_msg=False)
            return None, np.inf, None

    def _fit_naive(self, train_data, test_data):
        """Fit Naive forecasting method (last value carried forward)"""
        try:
            self._log("Fitting Naive model...", print_msg=False)
            
            # Naive forecast: use last observed value
            last_value = train_data.iloc[-1]
            test_pred = np.full(len(test_data), last_value)
            
            errors = self._calculate_errors(test_data.values, test_pred)
            
            # Store for later use
            model_params = {'last_value': last_value}
            
            self._log(f"Naive fitted successfully. Last value: {last_value:.2f}, "
                    f"{self.error_metric.upper()}: {errors[self.error_metric]:.4f}", print_msg=False)
            
            return model_params, errors[self.error_metric], test_pred
            
        except Exception as e:
            self._log(f"Naive fitting error: {str(e)}", level='ERROR', print_msg=False)
            return None, np.inf, None

    def _fit_seasonal_naive(self, train_data, test_data):
        """Fit Seasonal Naive forecasting method"""
        try:
            self._log("Fitting Seasonal Naive model...", print_msg=False)
            
            # Determine seasonal period
            if self.datetime_type == 'M':
                period = 12
            elif self.datetime_type == 'Y':
                period = 1
            else:
                period = 7
            
            if period == 1 or len(train_data) < period:
                # Fall back to naive if no seasonality
                return self._fit_naive(train_data, test_data)
            
            # Use values from same season in previous year
            test_pred = []
            for i in range(len(test_data)):
                idx = len(train_data) - period + (i % period)
                if idx >= 0 and idx < len(train_data):
                    test_pred.append(train_data.iloc[idx])
                else:
                    test_pred.append(train_data.iloc[-1])
            
            test_pred = np.array(test_pred)
            errors = self._calculate_errors(test_data.values, test_pred)
            
            model_params = {'period': period, 'train_data': train_data}
            
            self._log(f"Seasonal Naive fitted successfully. Period: {period}, "
                    f"{self.error_metric.upper()}: {errors[self.error_metric]:.4f}", print_msg=False)
            
            return model_params, errors[self.error_metric], test_pred
            
        except Exception as e:
            self._log(f"Seasonal Naive fitting error: {str(e)}", level='ERROR', print_msg=False)
            return None, np.inf, None

    def _fit_prophet(self, train_data, test_data):
        """Fit Prophet model for time series forecasting"""
        try:
            # Lazy import
            try:
                from prophet import Prophet
            except ImportError:
                self._log("prophet not installed. Install with: pip install prophet", level='ERROR', print_msg=False)
                return None, np.inf, None
            
            self._log("Fitting Prophet model...", print_msg=False)
            
            # Get the actual datetime index from full_data
            # Since train_data is a Series extracted from full_data, we need to get its index
            train_dates = train_data.index
            
            # Prepare data in Prophet format (ds: date, y: value)
            # Convert Period to Timestamp if necessary
            if hasattr(train_dates[0], 'to_timestamp'):
                dates = train_dates.to_timestamp()
            else:
                dates = pd.to_datetime(train_dates)
            
            train_df = pd.DataFrame({
                'ds': dates,
                'y': train_data.values
            })
            
            # Initialize and fit Prophet
            model = Prophet(
                yearly_seasonality=True if self.datetime_type == 'M' and len(train_data) >= 24 else False,
                weekly_seasonality=True if self.datetime_type == 'D' and len(train_data) >= 14 else False,
                daily_seasonality=False,
                seasonality_mode='additive',
                changepoint_prior_scale=0.05
            )
            
            # Suppress Prophet's verbose output
            import logging
            logging.getLogger('prophet').setLevel(logging.ERROR)
            
            model.fit(train_df)
            
            # Make predictions
            future = model.make_future_dataframe(periods=len(test_data), freq='MS')
            forecast = model.predict(future)
            test_pred = forecast['yhat'].values[-len(test_data):]
            
            # Calculate errors
            errors = self._calculate_errors(test_data.values, test_pred)
            
            self._log(f"Prophet fitted successfully. "
                    f"{self.error_metric.upper()}: {errors[self.error_metric]:.4f}", print_msg=False)
            
            return model, errors[self.error_metric], test_pred
            
        except Exception as e:
            self._log(f"Prophet fitting error: {str(e)}", level='WARNING', print_msg=False)
            return None, np.inf, None

    def _fit_lstm(self, train_data, test_data):
        """Fit LSTM neural network for time series forecasting"""
        try:
            # Lazy import
            try:
                import tensorflow as tf
                from tensorflow import keras
                from tensorflow.keras.models import Sequential
                from tensorflow.keras.layers import LSTM, Dense, Dropout
                # Suppress TensorFlow warnings
                tf.get_logger().setLevel('ERROR')
            except ImportError:
                self._log("tensorflow not installed. Install with: pip install tensorflow", level='ERROR', print_msg=False)
                return None, np.inf, None
            
            self._log("Fitting LSTM model...", print_msg=False)
            
            # Check minimum data requirement
            if len(train_data) < 20:
                self._log("LSTM skipped - insufficient data (need at least 20 periods)", level='WARNING', print_msg=False)
                return None, np.inf, None
            
            # Prepare data for LSTM
            lookback = min(12, len(train_data) // 3)  # Use 12 or 1/3 of data as lookback
            
            # Scale data
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_data = scaler.fit_transform(train_data.values.reshape(-1, 1))
            
            # Create sequences
            X, y = [], []
            for i in range(lookback, len(scaled_data)):
                X.append(scaled_data[i-lookback:i, 0])
                y.append(scaled_data[i, 0])
            
            X, y = np.array(X), np.array(y)
            X = X.reshape((X.shape[0], X.shape[1], 1))
            
            if len(X) < 10:
                self._log("LSTM skipped - insufficient sequences after preparation", level='WARNING', print_msg=False)
                return None, np.inf, None
            
            # Build LSTM model
            model = Sequential([
                LSTM(50, activation='relu', return_sequences=True, input_shape=(lookback, 1)),
                Dropout(0.2),
                LSTM(50, activation='relu'),
                Dropout(0.2),
                Dense(1)
            ])
            
            model.compile(optimizer='adam', loss='mse')
            
            # Train model (suppress output)
            model.fit(X, y, epochs=50, batch_size=16, verbose=0, validation_split=0.1)
            
            # Make predictions on test set
            # Use last lookback points from training data
            last_sequence = scaled_data[-lookback:]
            test_pred = []
            
            for _ in range(len(test_data)):
                current_seq = last_sequence.reshape((1, lookback, 1))
                pred = model.predict(current_seq, verbose=0)[0, 0]
                test_pred.append(pred)
                # Update sequence
                last_sequence = np.append(last_sequence[1:], [[pred]], axis=0)
            
            # Inverse transform predictions
            test_pred = scaler.inverse_transform(np.array(test_pred).reshape(-1, 1)).flatten()
            
            # Calculate errors
            errors = self._calculate_errors(test_data.values, test_pred)
            
            # Store model and scaler
            model_params = {
                'model': model,
                'scaler': scaler,
                'lookback': lookback
            }
            
            self._log(f"LSTM fitted successfully. Lookback: {lookback}, "
                    f"{self.error_metric.upper()}: {errors[self.error_metric]:.4f}", print_msg=False)
            
            return model_params, errors[self.error_metric], test_pred
            
        except Exception as e:
            self._log(f"LSTM fitting error: {str(e)}", level='WARNING', print_msg=False)
            return None, np.inf, None

    def _fit_neural_network(self, train_data, test_data):
        """Fit Multi-Layer Perceptron (MLP) neural network for time series forecasting"""
        try:
            self._log("Fitting Neural Network (MLP) model...", print_msg=False)
            
            # Check minimum data requirement
            if len(train_data) < 15:
                self._log("Neural Network skipped - insufficient data (need at least 15 periods)", 
                        level='WARNING', print_msg=False)
                return None, np.inf, None
            
            # Prepare features: use lagged values as features
            lookback = min(6, len(train_data) // 4)
            
            # Create feature matrix
            X, y = [], []
            for i in range(lookback, len(train_data)):
                X.append(train_data.values[i-lookback:i])
                y.append(train_data.values[i])
            
            X, y = np.array(X), np.array(y)
            
            if len(X) < 10:
                self._log("Neural Network skipped - insufficient samples after preparation", 
                        level='WARNING', print_msg=False)
                return None, np.inf, None
            
            # Scale data
            scaler_X = MinMaxScaler()
            scaler_y = MinMaxScaler()
            
            X_scaled = scaler_X.fit_transform(X)
            y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).flatten()
            
            # Build MLP model
            model = MLPRegressor(
                hidden_layer_sizes=(100, 50, 25),
                activation='relu',
                solver='adam',
                max_iter=500,
                early_stopping=True,
                validation_fraction=0.1,
                random_state=42,
                verbose=False
            )
            
            model.fit(X_scaled, y_scaled)
            
            # Make predictions on test set
            last_sequence = train_data.values[-lookback:]
            test_pred = []
            
            for _ in range(len(test_data)):
                current_seq = last_sequence[-lookback:].reshape(1, -1)
                current_seq_scaled = scaler_X.transform(current_seq)
                pred_scaled = model.predict(current_seq_scaled)[0]
                pred = scaler_y.inverse_transform([[pred_scaled]])[0, 0]
                test_pred.append(pred)
                # Update sequence
                last_sequence = np.append(last_sequence, pred)
            
            test_pred = np.array(test_pred)
            
            # Calculate errors
            errors = self._calculate_errors(test_data.values, test_pred)
            
            # Store model and scalers
            model_params = {
                'model': model,
                'scaler_X': scaler_X,
                'scaler_y': scaler_y,
                'lookback': lookback
            }
            
            self._log(f"Neural Network fitted successfully. Lookback: {lookback}, "
                    f"Hidden layers: (100, 50, 25), "
                    f"{self.error_metric.upper()}: {errors[self.error_metric]:.4f}", print_msg=False)
            
            return model_params, errors[self.error_metric], test_pred
            
        except Exception as e:
            self._log(f"Neural Network fitting error: {str(e)}", level='WARNING', print_msg=False)
            return None, np.inf, None

    def _predict_ets(self, full_series):
        """Predict using ETS on full dataset"""
        try:
            if self.datetime_type == 'M':
                seasonal_periods = 12
            elif self.datetime_type == 'Y':
                seasonal_periods = 1
            else:
                seasonal_periods = 7
            
            best_aic = np.inf
            best_model = None
            
            if seasonal_periods == 1 or len(full_series) < 2 * seasonal_periods:
                configs = [
                    {'error': 'add', 'trend': 'add', 'seasonal': None},
                    {'error': 'mul', 'trend': 'add', 'seasonal': None},
                    {'error': 'add', 'trend': None, 'seasonal': None}
                ]
            else:
                configs = [
                    {'error': 'add', 'trend': 'add', 'seasonal': 'add', 'seasonal_periods': seasonal_periods},
                    {'error': 'add', 'trend': 'add', 'seasonal': 'mul', 'seasonal_periods': seasonal_periods},
                    {'error': 'mul', 'trend': 'add', 'seasonal': 'add', 'seasonal_periods': seasonal_periods}
                ]
            
            for config in configs:
                try:
                    model = ETSModel(full_series, **config)
                    fitted_model = model.fit(disp=False)
                    if fitted_model.aic < best_aic:
                        best_aic = fitted_model.aic
                        best_model = fitted_model
                except:
                    continue
            
            if best_model is None:
                self._log("ETS prediction failed - no valid model found", level='WARNING', print_msg=False)
                return self._apply_fallback(full_series)
            
            return best_model.forecast(steps=self.forecast_span)
            
        except Exception as e:
            self._log(f"ETS prediction failed: {e}", level='WARNING', print_msg=False)
            return self._apply_fallback(full_series)
        
    def _predict_auto_arima(self, full_series):
        """Predict using Auto ARIMA on full dataset"""
        try:
            if self.datetime_type == 'M':
                m = 12
            elif self.datetime_type == 'Y':
                m = 1
            else:
                m = 7
            
            model = auto_arima(
                full_series,
                seasonal=True if m > 1 and len(full_series) >= 2*m else False,
                m=m,
                stepwise=True,
                suppress_warnings=True,
                error_action='ignore',
                trace=False,
                maxiter=10
            )
            
            return model.predict(n_periods=self.forecast_span)
            
        except Exception as e:
            self._log(f"Auto ARIMA prediction failed: {e}", level='WARNING', print_msg=False)
            return self._apply_fallback(full_series)

    def _predict_tbats(self, full_series):
        """Predict using TBATS on full dataset"""
        try:
            from tbats import TBATS
            
            if self.datetime_type == 'M':
                seasonal_periods = [12] if len(full_series) >= 36 else None
            elif self.datetime_type == 'Y':
                seasonal_periods = None
            else:
                seasonal_periods = [7] if len(full_series) >= 21 else None
            
            if seasonal_periods is None or full_series.std() < 0.01:
                return np.zeros(self.forecast_span)
            
            model = TBATS(
                seasonal_periods=seasonal_periods, 
                use_box_cox=False,
                use_trend=True,
                show_warnings=False,
                n_jobs=1
            )
            fitted_model = model.fit(full_series.values)
            forecast = fitted_model.forecast(steps=self.forecast_span)
            
            if np.any(np.isnan(forecast)) or np.any(np.isinf(forecast)):
                self._log("TBATS produced invalid forecasts (NaN or Inf)", level='WARNING', print_msg=False)
                return self._apply_fallback(full_series)
            
            return forecast
            
        except Exception as e:
            self._log(f"TBATS prediction failed: {e}", level='WARNING', print_msg=False)
            return self._apply_fallback(full_series)

    def _predict_bats(self, full_series):
        """Predict using BATS on full dataset"""
        try:
            from tbats import BATS
            
            if self.datetime_type == 'M':
                seasonal_periods = [12] if len(full_series) >= 36 else None
            elif self.datetime_type == 'Y':
                seasonal_periods = None
            else:
                seasonal_periods = [7] if len(full_series) >= 21 else None
            
            if seasonal_periods is None or full_series.std() < 0.01:
                self._log("BATS skipped - insufficient data or no seasonality", level='WARNING', print_msg=False)
                return self._apply_fallback(full_series)
            
            model = BATS(
                seasonal_periods=seasonal_periods, 
                use_box_cox=False,
                use_trend=True,
                show_warnings=False,
                n_jobs=1
            )
            fitted_model = model.fit(full_series.values)
            forecast = fitted_model.forecast(steps=self.forecast_span)
            
            if np.any(np.isnan(forecast)) or np.any(np.isinf(forecast)):
                self._log("BATS produced invalid forecasts (NaN or Inf)", level='WARNING', print_msg=False)
                return self._apply_fallback(full_series)
            
            return forecast
            
        except Exception as e:
            self._log(f"BATS prediction failed: {e}", level='WARNING', print_msg=False)
            return self._apply_fallback(full_series)

    def _predict_theta(self, full_series):
        """Predict using Theta method on full dataset"""
        try:
            n = len(full_series)
            x = np.arange(n)
            coeffs = np.polyfit(x, full_series.values, 1)
            trend = np.polyval(coeffs, x)
            detrended = full_series.values - trend
            
            alpha = 0.5
            ses = [detrended[0]]
            for val in detrended[1:]:
                ses.append(alpha * val + (1 - alpha) * ses[-1])
            
            last_trend_value = coeffs[0] * n + coeffs[1]
            trend_slope = coeffs[0]
            
            forecast = []
            for i in range(1, self.forecast_span + 1):
                trend_forecast = last_trend_value + trend_slope * i
                level_forecast = ses[-1]
                forecast.append(trend_forecast + level_forecast)
            
            return np.array(forecast)
            
        except Exception as e:
            self._log(f"Theta prediction failed: {e}", level='WARNING', print_msg=False)
            return self._apply_fallback(full_series)

    def _predict_naive(self, full_series):
        """Predict using Naive method on full dataset"""
        last_value = full_series.iloc[-1]
        return np.full(self.forecast_span, last_value)

    def _predict_seasonal_naive(self, full_series):
        """Predict using Seasonal Naive on full dataset"""
        try:
            if self.datetime_type == 'M':
                period = 12
            elif self.datetime_type == 'Y':
                period = 1
            else:
                period = 7
            
            if period == 1 or len(full_series) < period:
                return self._predict_naive(full_series)
            
            forecast = []
            for i in range(self.forecast_span):
                idx = len(full_series) - period + (i % period)
                if idx >= 0 and idx < len(full_series):
                    forecast.append(full_series.iloc[idx])
                else:
                    forecast.append(full_series.iloc[-1])
            
            return np.array(forecast)
            
        except Exception as e:
            self._log(f"Seasonal Naive prediction failed: {e}", level='WARNING', print_msg=False)
            return self._apply_fallback(full_series)

    def _predict_prophet(self, full_series):
        """Predict using Prophet on full dataset"""
        try:
            from prophet import Prophet
            import logging
            logging.getLogger('prophet').setLevel(logging.ERROR)
            
            # Get actual dates from the index
            dates = full_series.index
            
            # Convert Period to Timestamp if necessary
            if hasattr(dates[0], 'to_timestamp'):
                dates = dates.to_timestamp()
            else:
                dates = pd.to_datetime(dates)
            
            # Prepare data
            train_df = pd.DataFrame({
                'ds': dates,
                'y': full_series.values
            })
            
            # Fit model
            model = Prophet(
                yearly_seasonality=True if self.datetime_type == 'M' and len(full_series) >= 24 else False,
                weekly_seasonality=True if self.datetime_type == 'D' and len(full_series) >= 14 else False,
                daily_seasonality=False,
                seasonality_mode='additive',
                changepoint_prior_scale=0.05
            )
            model.fit(train_df)
            
            # Make forecast
            future = model.make_future_dataframe(periods=self.forecast_span, freq='MS')
            forecast = model.predict(future)
            
            return forecast['yhat'].values[-self.forecast_span:]
            
        except Exception as e:
            self._log(f"Prophet prediction failed: {e}", level='WARNING', print_msg=False)
            return self._apply_fallback(full_series)

    def _predict_neural_network(self, full_series):
        """Predict using Neural Network (MLP) on full dataset"""
        try:
            if len(full_series) < 15:
                return np.zeros(self.forecast_span)
            
            # Prepare data
            lookback = min(6, len(full_series) // 4)
            
            X, y = [], []
            for i in range(lookback, len(full_series)):
                X.append(full_series.values[i-lookback:i])
                y.append(full_series.values[i])
            
            X, y = np.array(X), np.array(y)
            
            if len(X) < 10:
                return np.zeros(self.forecast_span)
            
            # Scale data
            scaler_X = MinMaxScaler()
            scaler_y = MinMaxScaler()
            
            X_scaled = scaler_X.fit_transform(X)
            y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).flatten()
            
            # Train model
            model = MLPRegressor(
                hidden_layer_sizes=(100, 50, 25),
                activation='relu',
                solver='adam',
                max_iter=500,
                early_stopping=True,
                validation_fraction=0.1,
                random_state=42,
                verbose=False
            )
            
            model.fit(X_scaled, y_scaled)
            
            # Generate forecast
            last_sequence = full_series.values[-lookback:]
            forecast = []
            
            for _ in range(self.forecast_span):
                current_seq = last_sequence[-lookback:].reshape(1, -1)
                current_seq_scaled = scaler_X.transform(current_seq)
                pred_scaled = model.predict(current_seq_scaled)[0]
                pred = scaler_y.inverse_transform([[pred_scaled]])[0, 0]
                forecast.append(pred)
                last_sequence = np.append(last_sequence, pred)
            
            return np.array(forecast)
            
        except Exception as e:
            self._log(f"Neural Network prediction failed: {e}", level='WARNING', print_msg=False)
            return self._apply_fallback(full_series)
    
    def _predict_lstm(self, full_series):
        """Predict using LSTM on full dataset"""
        try:
            import tensorflow as tf
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            tf.get_logger().setLevel('ERROR')
            
            if len(full_series) < 20:
                self._log(f"LSTM skipped - insufficient data ie {len(full_series)} (need at least 20 periods)", level='WARNING', print_msg=False)
                return np.zeros(self.forecast_span)
            
            # Prepare data
            lookback = min(12, len(full_series) // 3)
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_data = scaler.fit_transform(full_series.values.reshape(-1, 1))
            
            # Create sequences
            X, y = [], []
            for i in range(lookback, len(scaled_data)):
                X.append(scaled_data[i-lookback:i, 0])
                y.append(scaled_data[i, 0])
            
            X, y = np.array(X), np.array(y)
            X = X.reshape((X.shape[0], X.shape[1], 1))
            
            if len(X) < 10:
                self._log(f"LSTM skipped - insufficient sequences after preparation ie {len(X)}", level='WARNING', print_msg=False)
                return np.zeros(self.forecast_span)
            
            # Build and train model
            model = Sequential([
                LSTM(50, activation='relu', return_sequences=True, input_shape=(lookback, 1)),
                Dropout(0.2),
                LSTM(50, activation='relu'),
                Dropout(0.2),
                Dense(1)
            ])
            
            model.compile(optimizer='adam', loss='mse')
            model.fit(X, y, epochs=50, batch_size=16, verbose=0, validation_split=0.1)
            
            # Generate forecast
            last_sequence = scaled_data[-lookback:]
            forecast = []
            
            for _ in range(self.forecast_span):
                current_seq = last_sequence.reshape((1, lookback, 1))
                pred = model.predict(current_seq, verbose=0)[0, 0]
                forecast.append(pred)
                last_sequence = np.append(last_sequence[1:], [[pred]], axis=0)
            
            # Inverse transform
            forecast = scaler.inverse_transform(np.array(forecast).reshape(-1, 1)).flatten()
            
            return forecast
            
        except Exception as e:
            self._log(f"LSTM prediction failed: {e}", level='WARNING', print_msg=False)
            return self._apply_fallback(full_series)

    def _predict_neural_network(self, full_series):
        """Predict using Neural Network (MLP) on full dataset"""
        try:
            if len(full_series) < 15:
                return np.zeros(self.forecast_span)
            
            # Prepare data
            lookback = min(6, len(full_series) // 4)
            
            X, y = [], []
            for i in range(lookback, len(full_series)):
                X.append(full_series.values[i-lookback:i])
                y.append(full_series.values[i])
            
            X, y = np.array(X), np.array(y)
            
            if len(X) < 10:
                return np.zeros(self.forecast_span)
            
            # Scale data
            scaler_X = MinMaxScaler()
            scaler_y = MinMaxScaler()
            
            X_scaled = scaler_X.fit_transform(X)
            y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).flatten()
            
            # Train model
            model = MLPRegressor(
                hidden_layer_sizes=(100, 50, 25),
                activation='relu',
                solver='adam',
                max_iter=500,
                early_stopping=True,
                validation_fraction=0.1,
                random_state=42,
                verbose=False
            )
            
            model.fit(X_scaled, y_scaled)
            
            # Generate forecast
            last_sequence = full_series.values[-lookback:]
            forecast = []
            
            for _ in range(self.forecast_span):
                current_seq = last_sequence[-lookback:].reshape(1, -1)
                current_seq_scaled = scaler_X.transform(current_seq)
                pred_scaled = model.predict(current_seq_scaled)[0]
                pred = scaler_y.inverse_transform([[pred_scaled]])[0, 0]
                forecast.append(pred)
                last_sequence = np.append(last_sequence, pred)
            
            return np.array(forecast)
            
        except Exception as e:
            self._log(f"Neural Network prediction failed: {e}", level='WARNING', print_msg=False)
            return self._apply_fallback(full_series)
    
    def fit(self, df):
        """Fit all models and select the best one(s)"""
        # Prepare data
        df_processed = self._prepare_datetime(df)
        df_processed = self._handle_missing_values(df_processed)
        min_data_length = 2 * self.forecast_span
        if len(df_processed) < min_data_length:
            msg = f"Insufficient data length ({len(df_processed)}) for reliable forecasting. Minimum recommended length is {min_data_length}."
            self._log(msg, level='WARNING')
        # Split into train and test
        split_point = int(len(df_processed) * (1 - self.test_size))
        train_data = df_processed[self.value_col][:split_point]
        test_data = df_processed[self.value_col][split_point:]
        
        self._log(f"Data split: Train={len(train_data)}, Test={len(test_data)}", print_msg=False)

        if len(test_data) == 0:
            error_msg = "Test set is empty. Consider reducing test_size."
            self._log(error_msg, level='ERROR')
            raise ValueError(error_msg)
        
        # Fit all models
        all_models = {
            'ARIMA': self._fit_arima,
            'SARIMA': self._fit_sarima,
            'Croston': self._fit_croston,
            'Holt': self._fit_holt,
            'HoltWinters': self._fit_holt_winters,
            'ETS': self._fit_ets,
            'AutoARIMA': self._fit_auto_arima,
            'TBATS': self._fit_tbats,
            'BATS': self._fit_bats,
            'Theta': self._fit_theta,
            'Naive': self._fit_naive,
            'SeasonalNaive': self._fit_seasonal_naive,
            'Prophet': self._fit_prophet,
            'LSTM': self._fit_lstm,
            'NeuralNetwork': self._fit_neural_network
        }
        
        # Filter models to fit based on self.model_list (case-sensitive matching)
        models_to_fit = {name: func for name, func in all_models.items() if name in self.model_list}


        def fit_model(name, fit_func):
            msg = f"Starting fit for {name}..."
            self._log(msg, print_msg=False)
            model, error, predictions = fit_func(train_data, test_data)
            return name, model, error, predictions

        if self.parallel_processing:
            self._log("Running model fitting in parallel...", print_msg=False)
            # Use ThreadPoolExecutor or ProcessPoolExecutor depending on whether fits are CPU bound
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(fit_model, name, func) for name, func in models_to_fit.items()]
                for future in concurrent.futures.as_completed(futures):
                    name, model, error, predictions = future.result()
                    self.model_results[name] = {
                        'model': model,
                        'error': error,
                        'test_predictions': predictions
                    }
        else:
            # Sequential processing
            self._log("Running model fitting sequentially...", print_msg=False)
            for name, fit_func in models_to_fit.items():
                name, model, error, predictions = fit_model(name, fit_func)
                self.model_results[name] = {
                    'model': model,
                    'error': error,
                    'test_predictions': predictions
                }

        # Sort models by error (ascending)
        sorted_models = sorted(
            [(name, result['error']) for name, result in self.model_results.items()],
            key=lambda x: x[1]
        )
        
        # Remove models that failed to fit
        valid_models = [(name, error) for name, error in sorted_models if error != np.inf]
        
        if not valid_models:
            error_msg = "No models could be fitted successfully."
            self._log(error_msg, level='ERROR')
            raise ValueError(error_msg)
        
        # Select best model(s)
        if self.top_models is None:
            self.best_model = valid_models[0][0]
            msg = f"Best model: {self.best_model} (error: {valid_models[0][1]:.4f})"
            self._log(msg)
        else:
            self.best_models = [name for name, _ in valid_models[:self.top_models]]
            self._log(f"\nTop {len(self.best_models)} models selected for ensemble:")
            for i, (name, error) in enumerate(valid_models[:self.top_models]):
                self._log(f"  {i+1}. {name} (error: {error:.4f})")
        
        # Print all model errors
        self._log(f"\nAll model errors ({self.error_metric.upper()}):")
        for name, error in sorted_models:
            status = "✓" if error != np.inf else "✗"
            self._log(f"  {status} {name}: {error:.4f}")
        
        # Store full dataset for final training
        self.full_data = df_processed
        
        return self
    
    def _generate_future_dates(self, last_date, periods):
        """Generate future dates based on datetime_type"""
        future_dates = []
        
        # Convert Period to timestamp if necessary
        if hasattr(last_date, 'to_timestamp'):
            base_date = last_date.to_timestamp()
        else:
            base_date = last_date
        
        if self.datetime_type == 'M':
            for i in range(1, periods + 1):
                future_date = base_date + relativedelta(months=i)
                # Convert back to Period for consistency
                future_dates.append(pd.Period(future_date, freq='M'))
        elif self.datetime_type == 'Y':
            for i in range(1, periods + 1):
                future_date = base_date + relativedelta(years=i)
                future_dates.append(pd.Period(future_date, freq='Y'))
        else:  # Daily
            for i in range(1, periods + 1):
                future_date = base_date + relativedelta(days=i)
                future_dates.append(pd.Period(future_date, freq='D'))
        
        return future_dates
    
    def predict(self):
        """Generate final forecast using only the ensemble (or best model if ensemble not available)."""
        if not hasattr(self, 'full_data'):
            error_msg = "Model must be fitted first using fit() method."
            self._log(error_msg, level='ERROR')
            raise ValueError(error_msg)
        
        full_series = self.full_data[self.value_col]
        last_date = self.full_data[self.datetime_col].iloc[-1]
        max_historical_value = full_series.max()

        msg = f"Generating {self.forecast_span} period forecast..."
        self._log(msg)

        future_dates = self._generate_future_dates(last_date, self.forecast_span)

        # If ensemble is not defined, fall back to best model
        if self.top_models is None:
            forecast = self._predict_single_model(self.best_model, full_series)
            if self.forecast_capping:
                if np.any(forecast > max_historical_value):
                    self._log(f"Forecast exceeds max historical value {max_historical_value}. Capping applied.", level='WARNING')
                forecast = np.clip(forecast, 0, max_historical_value)
            model_name = f'Final_{self.best_model}_Forecast'
        else:
            # Ensemble forecast
            forecasts = []
            weights = self.ensemble_weights or [1 / len(self.best_models)] * len(self.best_models)
            weights = np.array(weights[:len(self.best_models)])
            weights = weights / weights.sum()

            msg = f"Ensemble weights: {dict(zip(self.best_models, weights))}"
            self._log(msg)
            self._log(f"Best models: {self.best_models}")

            for model_name in self.best_models:
                model_forecast = self._predict_single_model(model_name, full_series)
                forecasts.append(model_forecast)

            forecast = np.average(forecasts, axis=0, weights=weights)
            if self.forecast_capping:
                if np.any(forecast > max_historical_value):
                    self._log(f"Ensemble forecast exceeds max historical value {max_historical_value}. Capping applied.", level='WARNING')
                forecast = np.clip(forecast, 0, max_historical_value)
            model_name = f"Final_Ensemble_Forecast_({len(self.best_models)}_models)"

        # Apply optimization if defined
        if self.optimization is not None:
            forecast = self._apply_optimization(forecast, full_series)
            model_name += f"_Optimized({self.optimization})"

        forecast_df = pd.DataFrame({
            self.datetime_col: future_dates,
            f'{self.value_col}_Forecast': forecast,
            'Model': model_name
        })

        self.final_forecast = forecast_df
        self._log(f"Forecast completed using: {model_name}")

        return forecast_df

    def predict_all(self):
        """Generate forecasts for all models including ensemble."""
        if not hasattr(self, 'full_data'):
            error_msg = "Model must be fitted first using fit() method."
            self._log(error_msg, level='ERROR')
            raise ValueError(error_msg)

        full_series = self.full_data[self.value_col]
        last_date = self.full_data[self.datetime_col].iloc[-1]
        max_historical_value = full_series.max()
        future_dates = self._generate_future_dates(last_date, self.forecast_span)
        self._log(f"Generating {self.forecast_span} period forecasts for all models (including ensemble)...")
        all_forecasts = []

        # Individual model forecasts
        for model_name in self.model_list:
            forecast = self._predict_single_model(model_name, full_series)
            
            # Apply optimization if enabled (BEFORE capping)
            if self.optimization and str(self.optimization).lower() != 'none':
                forecast = self._apply_optimization(forecast, full_series)
                display_name = f"{model_name}_Optimized_{self.optimization}"
            else:
                print('else in optimization')
                display_name = model_name

            # Apply capping AFTER optimization
            if self.forecast_capping:
                if np.any(forecast > max_historical_value) or np.any(forecast < 0):
                    self._log(f"{model_name} forecast capped", level='WARNING', print_msg=False)
                forecast = np.clip(forecast, 0, max_historical_value)

            model_df = pd.DataFrame({
                self.datetime_col: future_dates,
                f'{self.value_col}_Forecast': forecast,
                'Model': display_name
            })
            all_forecasts.append(model_df)

        # Final forecast (best model or ensemble)
        if self.top_models is not None:
            # # Single best model
            # forecast = self._predict_single_model(self.best_model, full_series)
            
            # if self.optimization and str(self.optimization).lower() != 'none':
            #     forecast = self._apply_optimization(forecast, full_series)
            #     model_name = f'Final_{self.best_model}_Optimized_{self.optimization}'
            # else:
            #     model_name = f'Final_{self.best_model}'

            # if self.forecast_capping:
            #     if np.any(forecast > max_historical_value) or np.any(forecast < 0):
            #         self._log(f"Best model forecast capped", level='WARNING', print_msg=False)
            #     forecast = np.clip(forecast, 0, max_historical_value)
            # Ensemble forecast
            forecasts = []
            weights = self.ensemble_weights or [1 / len(self.best_models)] * len(self.best_models)
            weights = np.array(weights[:len(self.best_models)])
            weights = weights / weights.sum()

            self._log(f"Ensemble weights: {dict(zip(self.best_models, weights))}")

            for bm in self.best_models:
                forecasts.append(self._predict_single_model(bm, full_series))

            forecast = np.average(forecasts, axis=0, weights=weights)

            if self.optimization and str(self.optimization).lower() != 'none':
                forecast = self._apply_optimization(forecast, full_series)
                model_name = f"Final_Ensemble_{len(self.best_models)}models_Optimized_{self.optimization}"
            else:
                model_name = f"Final_Ensemble_{len(self.best_models)}models"

            if self.forecast_capping:
                if np.any(forecast > max_historical_value) or np.any(forecast < 0):
                    self._log("Ensemble forecast capped", level='WARNING', print_msg=False)
                forecast = np.clip(forecast, 0, max_historical_value)

        # Add final forecast
        final_df = pd.DataFrame({
            self.datetime_col: future_dates,
            f'{self.value_col}_Forecast': forecast,
            'Model': model_name
        })
        all_forecasts.append(final_df)

        forecast_df = pd.concat(all_forecasts, ignore_index=True)
        self.final_forecast = forecast_df
        self._log("Forecasts completed for all models (including ensemble).")
        return forecast_df
    
    def _apply_fallback(self, full_series):
        """Apply fallback strategy when all models fail"""
        try:
            self._log(f"Applying fallback strategy: {self.fallback_strategy}", level='WARNING')
            
            if self.fallback_strategy == 'zero':
                return np.zeros(self.forecast_span)
            
            if self.fallback_strategy == 'last_value':
                return np.full(self.forecast_span, full_series.iloc[-1])
            
            # Parse strategy (e.g., '6_mean' -> periods=6, method='mean')
            parts = self.fallback_strategy.split('_')
            periods = int(parts[0])
            method = parts[1]
            
            # Get recent data (respects actual datetime type)
            recent_data = full_series.tail(min(periods, len(full_series)))
            
            if method == 'mean':
                value = recent_data.mean()
            elif method == 'median':
                value = recent_data.median()
            
            # Log with appropriate time unit
            time_unit = {'M': 'months', 'Y': 'years', 'D': 'days'}[self.datetime_type]
            self._log(f"Fallback: {value:.2f} (last {len(recent_data)} {time_unit}, {method})", 
                    print_msg=False)
            
            return np.full(self.forecast_span, value)
            
        except Exception as e:
            self._log(f"Fallback strategy failed: {e}. Using zeros.", level='ERROR')
            return np.zeros(self.forecast_span)
    
    def _predict_single_model(self, model_name, full_series):
        """Generate prediction for a single model using full dataset"""
        try:
            if model_name == 'ARIMA':
                return self._predict_arima(full_series)
            elif model_name == 'SARIMA':
                return self._predict_sarima(full_series)
            elif model_name == 'Croston':
                return self._predict_croston(full_series)
            elif model_name == 'Holt':
                return self._predict_holt(full_series)
            elif model_name == 'HoltWinters':
                return self._predict_holt_winters(full_series)
            elif model_name == 'ETS':
                return self._predict_ets(full_series)
            elif model_name == 'AutoARIMA':
                return self._predict_auto_arima(full_series)
            elif model_name == 'TBATS':
                return self._predict_tbats(full_series)
            elif model_name == 'BATS':
                return self._predict_bats(full_series)
            elif model_name == 'Theta':
                return self._predict_theta(full_series)
            elif model_name == 'Naive':
                return self._predict_naive(full_series)
            elif model_name == 'SeasonalNaive':
                return self._predict_seasonal_naive(full_series)
            elif model_name == 'Prophet':
                return self._predict_prophet(full_series)
            elif model_name == 'LSTM':
                return self._predict_lstm(full_series)
            elif model_name == 'NeuralNetwork':
                return self._predict_neural_network(full_series)
        except Exception as e:
            self._log(f"Prediction with {model_name} failed: {e}", level='ERROR')
            return self._apply_fallback(full_series)  # Use fallback instead of zeros
    
    def _predict_arima(self, full_series):
        """Predict using ARIMA on full dataset"""
        best_aic = np.inf
        best_model = None
        
        orders = [(p, d, q) for p in range(3) for d in range(2) for q in range(3)]
        
        for order in orders:
            try:
                model = ARIMA(full_series, order=order)
                fitted_model = model.fit()
                if fitted_model.aic < best_aic:
                    best_aic = fitted_model.aic
                    best_model = fitted_model
            except:
                continue
        
        if best_model is None:
            return self._apply_fallback(full_series)
        
        return best_model.forecast(steps=self.forecast_span)
    
    def _predict_sarima(self, full_series):
        """Predict using SARIMA on full dataset"""
        if self.datetime_type == 'M':
            seasonal_period = 12
        elif self.datetime_type == 'Y':
            seasonal_period = 1
        else:
            seasonal_period = 7
        
        if seasonal_period == 1 or len(full_series) < 2 * seasonal_period:
            return self._predict_arima(full_series)
        
        best_aic = np.inf
        best_model = None
        
        orders = [(p, d, q) for p in range(2) for d in range(2) for q in range(2)]
        seasonal_orders = [(P, D, Q, seasonal_period) for P in range(2) for D in range(2) for Q in range(2)]
        
        for order in orders[:6]:
            for seasonal_order in seasonal_orders[:4]:
                try:
                    model = SARIMAX(full_series, order=order, seasonal_order=seasonal_order)
                    fitted_model = model.fit(disp=False)
                    if fitted_model.aic < best_aic:
                        best_aic = fitted_model.aic
                        best_model = fitted_model
                except:
                    continue
        
        if best_model is None:
            self._log("SARIMA prediction failed", level='WARNING', print_msg=False)
            return self._apply_fallback(full_series)
        
        return best_model.forecast(steps=self.forecast_span)
    
    def _predict_croston(self, full_series):
        """Predict using Croston's method on full dataset"""
        alpha = 0.3
        
        non_zero_indices = np.where(full_series > 0)[0]
        
        if len(non_zero_indices) < 2:
            self._log("Croston prediction failed - insufficient data", level='WARNING', print_msg=False)
            return self._apply_fallback(full_series)
        
        z = full_series.iloc[non_zero_indices[0]]
        x = non_zero_indices[0] + 1
        
        for i in range(1, len(non_zero_indices)):
            current_demand = full_series.iloc[non_zero_indices[i]]
            current_interval = non_zero_indices[i] - non_zero_indices[i-1]
            
            z = alpha * current_demand + (1 - alpha) * z
            x = alpha * current_interval + (1 - alpha) * x
        
        forecast_value = z / x if x > 0 else 0
        return np.full(self.forecast_span, forecast_value)
    
    def _predict_holt(self, full_series):
        """Predict using Holt's method on full dataset"""
        try:
            model = ExponentialSmoothing(full_series, trend='add')
            fitted_model = model.fit()
            return fitted_model.forecast(steps=self.forecast_span)
        except Exception as e:
            self._log(f"Holt prediction failed: {e}", level='WARNING', print_msg=False)
            return self._apply_fallback(full_series)
    
    def _predict_holt_winters(self, full_series):
        """Predict using Holt-Winters on full dataset"""
        if self.datetime_type == 'M':
            seasonal_periods = 12
        elif self.datetime_type == 'Y':
            seasonal_periods = 1
        else:
            seasonal_periods = 7
        
        if seasonal_periods == 1 or len(full_series) < 2 * seasonal_periods:
            return self._predict_holt(full_series)
        
        try:
            model = ExponentialSmoothing(
                full_series, 
                trend='add', 
                seasonal='add', 
                seasonal_periods=seasonal_periods
            )
            fitted_model = model.fit()
            return fitted_model.forecast(steps=self.forecast_span)
        except Exception as e:
            self._log(f"Holt-Winters prediction failed: {e}", level='WARNING', print_msg=False)
            return self._apply_fallback(full_series)
    
    def _apply_optimization(self, forecast, full_series):
        """Apply optimization using recent historical data"""
        try:
            recent_data = full_series.tail(min(self.optimization_length, len(full_series)))
            self._log(f"Applying {self.optimization} optimization using recent {self.optimization_length} periods")
            self._log(f"Recent data values: {recent_data.values}", print_msg=False)

            if self.optimization == 'mean':
                optimization_value = recent_data.mean()
            elif self.optimization == 'median':
                optimization_value = recent_data.median()
            elif self.optimization == 'mode':
                mode_result = recent_data.mode()
                if len(mode_result) > 0:
                    optimization_value = mode_result.iloc[0]
                else:
                    self._log("No clear mode found, using mean instead")
                    optimization_value = recent_data.mean()
            # Check for negative or invalid optimization value
            if optimization_value < 0 or np.isnan(optimization_value) or np.isinf(optimization_value):
                self._log(f"Invalid optimization value ({optimization_value}), skipping optimization", 
                        level='WARNING', print_msg=False)
                return forecast
            # Correct weights calculation
            forecast_weight = float(self.optimization_ratio.split(':')[0]) / 100
            optimization_weight = float(self.optimization_ratio.split(':')[1]) / 100

            optimized_forecast = (forecast_weight * forecast + optimization_weight * optimization_value)

            self._log(f"Optimization details:", print_msg=False)
            self._log(f"  Recent {self.optimization_length} periods {self.optimization}: {optimization_value:.2f}", print_msg=False)
            self._log(f"  Optimization ratio: {self.optimization_ratio}", print_msg=False)
            self._log(f"  Forecast weight: {forecast_weight:.2f}", print_msg=False)
            self._log(f"  Optimization weight: {optimization_weight:.2f}", print_msg=False)
            self._log(f"  Sample original forecast: {forecast[0]:.2f}", print_msg=False)
            self._log(f"  Sample optimized forecast: {optimized_forecast[0]:.2f}", print_msg=False)
          
            # Ensure non-negative forecasts
            optimized_forecast = np.maximum(optimized_forecast, 0)
            
            # Log sample values safely
            try:
                self._log(f"  Sample original forecast: {float(forecast[0]):.2f}", print_msg=False)
                self._log(f"  Sample optimized forecast: {float(optimized_forecast[0]):.2f}", print_msg=False)
                change = float(optimized_forecast[0]) - float(forecast[0])
                self._log(f"  Optimization change: {change:+.2f}", print_msg=False)
            except (IndexError, ValueError, TypeError) as e:
                self._log(f"  Could not log sample values: {e}", print_msg=False)
            return optimized_forecast

        except Exception as e:
            self._log(f"Optimization failed ({e}), using original forecast", level='WARNING')
            return forecast

    def get_model_summary(self):
        """Get summary of all model performances"""
        if not hasattr(self, 'model_results'):
            error_msg = "Model must be fitted first using fit() method."
            self._log(error_msg, level='ERROR')
            raise ValueError(error_msg)
        
        summary = []
        for name, result in self.model_results.items():
            summary.append({
                'Model': name,
                f'{self.error_metric.upper()}': result['error'],
                'Status': 'Success' if result['error'] != np.inf else 'Failed'
            })
        
        summary_df = pd.DataFrame(summary)
        summary_df = summary_df.sort_values(f'{self.error_metric.upper()}')
        
        return summary_df
    
    def save_logs(self, filepath=None, return_dataframe=False):
        """
        Save or return the logs from the forecasting session.
        
        Parameters:
        -----------
        filepath : str, optional
            Path to save the logs as CSV file. If None, logs are not saved to file.
        return_dataframe : bool, default False
            If True, returns logs as a pandas DataFrame
        
        Returns:
        --------
        logs_df : pd.DataFrame or list
            If return_dataframe=True, returns DataFrame, otherwise returns list of log dictionaries
        
        Examples:
        ---------
        # Get logs as DataFrame
        logs_df = model.save_logs(return_dataframe=True)
        
        # Save logs to file
        model.save_logs('forecast_logs.csv')
        
        # Get logs as list and save to file
        logs = model.save_logs('forecast_logs.csv')
        """
        if not self.logs:
            self._log("No logs to save", level='WARNING')
            return [] if not return_dataframe else pd.DataFrame()
        
        # Add session end log
        self._log("=" * 60, print_msg=False)
        self._log(f"Session ended. Total log entries: {len(self.logs)}", level='SESSION', print_msg=False)
        self._log("=" * 60, print_msg=False)
        
        # Convert to DataFrame
        logs_df = pd.DataFrame(self.logs)
        
        # Save to file if filepath provided
        if filepath:
            try:
                logs_df.to_csv(filepath, index=False)
                print(f"Logs saved successfully to: {filepath}")
            except Exception as e:
                self._log(f"Failed to save logs to {filepath}: {str(e)}", level='ERROR')
        
        # Return based on preference
        if return_dataframe:
            return logs_df
        else:
            return self.logs
    
    def get_logs_summary(self):
        """
        Get a summary of logs by level.
        
        Returns:
        --------
        summary : dict
            Dictionary containing count of logs by level
        """
        if not self.logs:
            return {}
        
        logs_df = pd.DataFrame(self.logs)
        summary = logs_df['level'].value_counts().to_dict()
        
        print("\n" + "=" * 50)
        print("LOG SUMMARY")
        print("=" * 50)
        for level, count in sorted(summary.items()):
            print(f"{level:12s}: {count:4d} entries")
        print("=" * 50)
        print(f"{'TOTAL':12s}: {len(self.logs):4d} entries")
        print("=" * 50 + "\n")
        
        return summary
    
    def clear_logs(self):
        """Clear all logs from current session"""
        self.logs = []
        self._log("Logs cleared", level='INFO', print_msg=False)
    
    def print_logs(self, level=None, last_n=None):
        """
        Print logs to console with optional filtering.
        
        Parameters:
        -----------
        level : str, optional
            Filter logs by level (e.g., 'ERROR', 'WARNING', 'INFO')
        last_n : int, optional
            Print only the last N log entries
        """
        if not self.logs:
            print("No logs available")
            return
        
        logs_to_print = self.logs
        
        # Filter by level if specified
        if level:
            logs_to_print = [log for log in logs_to_print if log['level'] == level.upper()]
        
        # Limit to last N entries if specified
        if last_n:
            logs_to_print = logs_to_print[-last_n:]
        
        print("\n" + "=" * 80)
        print(f"LOGS ({len(logs_to_print)} entries)")
        if level:
            print(f"Filtered by level: {level.upper()}")
        if last_n:
            print(f"Showing last {last_n} entries")
        print("=" * 80)
        
        for log in logs_to_print:
            print(f"[{log['timestamp']}] [{log['level']:8s}] {log['message']}")
        
        print("=" * 80 + "\n")
    