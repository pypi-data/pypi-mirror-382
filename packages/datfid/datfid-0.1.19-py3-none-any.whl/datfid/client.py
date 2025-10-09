import requests
import pandas as pd
from typing import Dict, Any, Optional, Union
import json
from types import SimpleNamespace
import tempfile
import os
import gc
import psutil
import logging

# for nice output
class FitResult(SimpleNamespace):
    _ROW4  = ["Estimate", "Standard Error", "T statistic", "P value"]
    _PERF5 = ["R2 within", "R2 between", "R2 overall", "MSE", "MAE"]
    
    @property
    def id(self):
        import pandas as pd
        if hasattr(self, "df") and isinstance(self.df, pd.DataFrame) and "ID" in self.df.columns:
            return pd.DataFrame(self.df["ID"].astype(str).unique())
        return pd.DataFrame([])
    
    @property
    def ID(self):
        import pandas as pd
        if hasattr(self, "df") and isinstance(self.df, pd.DataFrame) and "ID" in self.df.columns:
            return pd.DataFrame(self.df["ID"].astype(str).unique())
        return pd.DataFrame([])
    
    @property
    def Id(self):
        import pandas as pd
        if hasattr(self, "df") and isinstance(self.df, pd.DataFrame) and "ID" in self.df.columns:
            return pd.DataFrame(self.df["ID"].astype(str).unique())
        return pd.DataFrame([])

    @staticmethod
    def _df4(rows_list):
        if not isinstance(rows_list, list):
            return rows_list
        return pd.DataFrame(rows_list, index=FitResult._ROW4[:len(rows_list)])

    @staticmethod
    def _df_perf(rows_list):
        if not isinstance(rows_list, list):
            return rows_list
        return pd.DataFrame(rows_list, index=FitResult._PERF5[:len(rows_list)])

    def __init__(self, **kwargs):
        # Convert list→DataFrame for table-like fields
        if "alpha" in kwargs:
            kwargs["alpha"] = self._df4(kwargs["alpha"])
        if "beta" in kwargs:
            kwargs["beta"] = self._df4(kwargs["beta"])
        if "Performance" in kwargs:
            kwargs["Performance"] = self._df_perf(kwargs["Performance"])
        if "df" in kwargs and isinstance(kwargs["df"], list):
            kwargs["df"] = pd.DataFrame(kwargs["df"])
        super().__init__(**kwargs)

class FitResultDict(dict):
    @property
    def id(self):
        return pd.DataFrame({"ID": list(self.keys())})
    
    @property
    def ID(self):
        return pd.DataFrame({"ID": list(self.keys())})
    
    @property
    def Id(self):
        return pd.DataFrame({"ID": list(self.keys())})


class DATFIDClient:
    def __init__(self, token: str):
        self.api_url = "https://datfid-org-datfid-sdk.hf.space/"
        self.headers = {"Authorization": f"Bearer {token}"}
        self.logger = logging.getLogger(__name__)

    def _cleanup_memory(self):
        """Clean up memory after operations"""
        gc.collect()
        if hasattr(psutil, 'Process'):
            process = psutil.Process()
            try:
                process.memory_info().rss  # Force memory info update
            except:
                pass

    def ping(self):
        try:
            response = requests.get(self.api_url, headers=self.headers).json()
            self._cleanup_memory()
            return response
        except Exception as e:
            self.logger.error(f"Ping failed: {str(e)}")
            raise

    def secure_ping(self):
        try:
            response = requests.get(f"{self.api_url}secure-ping/", headers=self.headers).json()
            self._cleanup_memory()
            return response
        except Exception as e:
            self.logger.error(f"Secure ping failed: {str(e)}")
            raise

    def fit_model(
        self,
        df: pd.DataFrame,
        id_col: str,
        time_col: str,
        y: str,
        lag_y: Optional[Union[int, str, list[int]]] = None,
        lagged_features: Optional[Dict[str, int]] = None,
        current_features: Optional[list] = None,
        filter_by_significance: bool = False,
        meanvar_test: bool = False
    ) -> FitResult:
        """
        Fit a model using the DATFID API.
        
        Args:
            df: DataFrame containing the data
            id_col: Name of the ID column
            time_col: Name of the time column
            y: Name of the target variable
            lagged_features: Dictionary of features and their lag values
            current_features: List of current features to use
            filter_by_significance: Whether to filter features by significance
            meanvar_test: Whether to perform mean-variance test
            
        Returns:
            SimpleNamespace containing the model fit results
        """

        df = df.copy()
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)

        data = {
            "df": df.to_dict(orient="records"),
            "id_col": id_col,
            "time_col": time_col,
            "y": y,
            "lag_y": lag_y,
            "lagged_features": lagged_features or {},
            "current_features": current_features or [],
            "filter_by_significance": filter_by_significance,
            "meanvar_test": meanvar_test
        }
        
        response = requests.post(
            f"{self.api_url}modelfit/",
            json=data,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Model fit failed: {response.text}")
            
        result_dict = response.json()
        return FitResult(**result_dict)
    
    def forecast_model(
        self,
        df_forecast: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Generate forecasts using the fitted model.
        
        Args:
            df_forecast: DataFrame containing the forecast data
            
        Returns:
            DataFrame containing the forecast results
        """

        try:
            df_forecast = df_forecast.copy()
            for col in df_forecast.columns:
                if pd.api.types.is_datetime64_any_dtype(df_forecast[col]):
                    df_forecast[col] = df_forecast[col].astype(str)

            # Convert DataFrame to list of records
            data = df_forecast.to_dict(orient="records")
            
            response = requests.post(
                f"{self.api_url}modelforecast/",
                json=data,
                headers=self.headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Forecast generation failed: {response.text}")
            
            result = pd.DataFrame(response.json())
            
            # Clean up memory after operation
            del df_forecast
            del data
            self._cleanup_memory()
            
            return result
        except Exception as e:
            self.logger.error(f"Forecast generation failed: {str(e)}")
            raise

    def fit_model_ind(
        self,
        df: pd.DataFrame,
        id_col: str,
        time_col: str,
        y: str,
        lag_y: Optional[Union[int, str, list[int]]] = None,
        lagged_features: Optional[Dict[str, int]] = None,
        current_features: Optional[list] = None,
        filter_by_significance: bool = False,
        meanvar_test: bool = False
    ) -> FitResultDict:
        """
        Fit a model individual by individual using the DATFID API.
        
        Args:
            df: DataFrame containing the data
            id_col: Name of the ID column
            time_col: Name of the time column
            y: Name of the target variable
            lagged_features: Dictionary of features and their lag values
            current_features: List of current features to use
            filter_by_significance: Whether to filter features by significance
            meanvar_test: Whether to perform mean-variance test
            
        Returns:
            SimpleNamespace containing the model fit results
        """

        df = df.copy()
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)

        data = {
            "df": df.to_dict(orient="records"),
            "id_col": id_col,
            "time_col": time_col,
            "y": y,
            "lag_y": lag_y,
            "lagged_features": lagged_features or {},
            "current_features": current_features or [],
            "filter_by_significance": filter_by_significance,
            "meanvar_test": meanvar_test
        }
        
        response = requests.post(
            f"{self.api_url}modelfit_ind/",
            json=data,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Model fit failed: {response.text}")
            
        raw = response.json() 
        # Wrap each per-id result into a SimpleNamespace for dot access:
        result_per_id = FitResultDict({str(k): FitResult(**v) for k, v in raw.items()})
        return result_per_id  # FitResultDict[str, SimpleNamespace]

    def forecast_model_ind(
        self,
        df_forecast: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Generate forecasts using the fitted individual by individual model.
        
        Args:
            df_forecast: DataFrame containing the forecast data
            
        Returns:
            DataFrame containing the forecast results
        """

        try:
            df_forecast = df_forecast.copy()
            for col in df_forecast.columns:
                if pd.api.types.is_datetime64_any_dtype(df_forecast[col]):
                    df_forecast[col] = df_forecast[col].astype(str)

            # Convert DataFrame to list of records
            data = df_forecast.to_dict(orient="records")
            
            response = requests.post(
                f"{self.api_url}modelforecast_ind/",
                json=data,
                headers=self.headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Forecast generation failed: {response.text}")
            
            result = pd.DataFrame(response.json())
            
            # Clean up memory after operation
            del df_forecast
            del data
            self._cleanup_memory()
            
            return result
        except Exception as e:
            self.logger.error(f"Forecast generation failed: {str(e)}")
            raise