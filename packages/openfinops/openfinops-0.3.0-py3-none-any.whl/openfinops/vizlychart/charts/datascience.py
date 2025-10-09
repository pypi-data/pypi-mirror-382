"""
Advanced Data Science Chart Types
=================================

This module provides specialized charts for data science, statistics,
time series analysis, and advanced financial analytics.
"""

# Copyright (c) 2025 Infinidatum
# Author: Duraimurugan Rajamanickam
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



from __future__ import annotations

import warnings
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime, timedelta
import numpy as np

from .base import BaseChart
from ..exceptions import VizlyError

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    warnings.warn("Pandas not available. Some data science features will be limited.")

try:
    import scipy.stats as stats
    from scipy.signal import find_peaks, savgol_filter
    from scipy.interpolate import interp1d
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    warnings.warn("SciPy not available. Some statistical features will be limited.")

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle, Circle
    from matplotlib.collections import LineCollection
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class TimeSeriesChart(BaseChart):
    """Advanced time series visualization with decomposition and forecasting."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ts_data = None
        self._trend = None
        self._seasonal = None
        self._residual = None

    def plot_timeseries(
        self,
        dates: Union[List[datetime], pd.DatetimeIndex, np.ndarray],
        values: np.ndarray,
        *,
        title: str = "Time Series",
        trend_line: bool = True,
        moving_average: Optional[int] = None,
        confidence_bands: bool = False,
        confidence_level: float = 0.95,
        seasonal_decompose: bool = False,
        detect_anomalies: bool = False,
        anomaly_threshold: float = 2.0,
        **kwargs
    ) -> None:
        """
        Plot time series with advanced analysis features.

        Parameters:
            dates: Time index
            values: Time series values
            title: Chart title
            trend_line: Show polynomial trend line
            moving_average: Window size for moving average
            confidence_bands: Show confidence intervals
            confidence_level: Confidence level for bands
            seasonal_decompose: Perform seasonal decomposition
            detect_anomalies: Highlight anomalous points
            anomaly_threshold: Standard deviations for anomaly detection
        """
        if not HAS_PANDAS:
            raise VizlyError("Pandas required for time series analysis")

        # Convert to pandas if needed
        if not isinstance(dates, pd.DatetimeIndex):
            dates = pd.to_datetime(dates)

        ts = pd.Series(values, index=dates)
        self._ts_data = ts

        # Main time series plot
        self.axes.plot(dates, values, label='Time Series', **kwargs)

        # Add trend line
        if trend_line:
            z = np.polyfit(range(len(values)), values, 2)
            trend = np.polyval(z, range(len(values)))
            self._trend = trend
            self.axes.plot(dates, trend, '--', color='red', alpha=0.7, label='Trend')

        # Add moving average
        if moving_average:
            ma = ts.rolling(window=moving_average, center=True).mean()
            self.axes.plot(dates, ma, color='orange', alpha=0.8,
                          label=f'{moving_average}-period MA')

        # Add confidence bands
        if confidence_bands:
            if moving_average:
                ma = ts.rolling(window=moving_average, center=True).mean()
                std = ts.rolling(window=moving_average, center=True).std()
            else:
                ma = pd.Series(values, index=dates)
                std = ma.rolling(window=min(30, len(values)//4), center=True).std()

            # Calculate confidence interval
            z_score = stats.norm.ppf((1 + confidence_level) / 2)
            upper = ma + z_score * std
            lower = ma - z_score * std

            self.axes.fill_between(dates, lower, upper, alpha=0.2, color='blue',
                                 label=f'{confidence_level*100}% Confidence')

        # Detect and highlight anomalies
        if detect_anomalies:
            # Use z-score method
            z_scores = np.abs(stats.zscore(values))
            anomalies = z_scores > anomaly_threshold

            if np.any(anomalies):
                self.axes.scatter(dates[anomalies], values[anomalies],
                                color='red', s=50, marker='o',
                                label='Anomalies', zorder=5)

        # Seasonal decomposition subplot
        if seasonal_decompose and HAS_SCIPY:
            self._create_decomposition_subplot(ts)

        self.axes.set_title(title)
        self.axes.set_xlabel('Date')
        self.axes.set_ylabel('Value')
        self.axes.legend()
        self.axes.grid(True, alpha=0.3)

        # Format x-axis for dates
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.axes.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
        plt.setp(self.axes.xaxis.get_majorticklabels(), rotation=45)

    def _create_decomposition_subplot(self, ts: pd.Series) -> None:
        """Create seasonal decomposition subplot."""
        try:
            from statsmodels.tsa.seasonal import seasonal_decompose
            decomposition = seasonal_decompose(ts, model='additive', period=min(12, len(ts)//3))

            # Clear figure and create subplots
            self.figure.figure.clear()
            fig = self.figure.figure

            # Create 4 subplots for decomposition
            ax1 = fig.add_subplot(4, 1, 1)
            ax2 = fig.add_subplot(4, 1, 2)
            ax3 = fig.add_subplot(4, 1, 3)
            ax4 = fig.add_subplot(4, 1, 4)

            # Plot components
            ax1.plot(ts.index, ts.values, label='Original')
            ax1.set_title('Original Time Series')
            ax1.legend()

            ax2.plot(ts.index, decomposition.trend, label='Trend', color='red')
            ax2.set_title('Trend Component')
            ax2.legend()

            ax3.plot(ts.index, decomposition.seasonal, label='Seasonal', color='green')
            ax3.set_title('Seasonal Component')
            ax3.legend()

            ax4.plot(ts.index, decomposition.resid, label='Residual', color='orange')
            ax4.set_title('Residual Component')
            ax4.legend()

            # Format all subplots
            for ax in [ax1, ax2, ax3, ax4]:
                ax.grid(True, alpha=0.3)
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

            plt.tight_layout()
            self.bind_axes(ax1)  # Bind to original series plot

        except ImportError:
            warnings.warn("statsmodels not available for seasonal decomposition")


class DistributionChart(BaseChart):
    """Statistical distribution analysis and comparison charts."""

    def plot_distribution(
        self,
        data: np.ndarray,
        *,
        distribution_type: str = 'histogram',
        bins: Union[int, str] = 'auto',
        kde: bool = True,
        rug: bool = False,
        fit_distribution: Optional[str] = None,
        confidence_interval: bool = False,
        **kwargs
    ) -> None:
        """
        Plot data distribution with statistical analysis.

        Parameters:
            data: Input data array
            distribution_type: 'histogram', 'density', 'box', 'violin'
            bins: Number of bins or binning strategy
            kde: Show kernel density estimation
            rug: Show rug plot at bottom
            fit_distribution: Fit theoretical distribution ('normal', 'lognormal', 'exponential')
            confidence_interval: Show confidence intervals for KDE
        """
        if not HAS_SCIPY:
            warnings.warn("SciPy not available. Limited distribution features.")

        data = np.asarray(data)
        data_clean = data[~np.isnan(data)]  # Remove NaN values

        if distribution_type == 'histogram':
            # Create histogram
            n, bins_edges, patches = self.axes.hist(data_clean, bins=bins,
                                                   alpha=0.7, density=kde, **kwargs)

            # Add KDE if requested
            if kde and HAS_SCIPY:
                x_range = np.linspace(data_clean.min(), data_clean.max(), 300)
                kde_values = stats.gaussian_kde(data_clean)(x_range)
                self.axes.plot(x_range, kde_values, color='red', linewidth=2,
                             label='KDE')

                # Add confidence interval for KDE
                if confidence_interval:
                    # Bootstrap confidence intervals
                    n_bootstrap = 100
                    kde_bootstrap = []

                    for _ in range(n_bootstrap):
                        sample = np.random.choice(data_clean, size=len(data_clean), replace=True)
                        kde_boot = stats.gaussian_kde(sample)(x_range)
                        kde_bootstrap.append(kde_boot)

                    kde_bootstrap = np.array(kde_bootstrap)
                    lower = np.percentile(kde_bootstrap, 2.5, axis=0)
                    upper = np.percentile(kde_bootstrap, 97.5, axis=0)

                    self.axes.fill_between(x_range, lower, upper, alpha=0.2,
                                         color='red', label='95% CI')

        elif distribution_type == 'box':
            # Box plot
            box_plot = self.axes.boxplot(data_clean, vert=True, patch_artist=True)
            box_plot['boxes'][0].set_facecolor('lightblue')
            box_plot['boxes'][0].set_alpha(0.7)

        # Add rug plot
        if rug:
            y_min = self.axes.get_ylim()[0]
            self.axes.plot(data_clean, [y_min] * len(data_clean), '|',
                         color='black', alpha=0.5, markersize=1)

        # Fit theoretical distribution
        if fit_distribution and HAS_SCIPY:
            self._fit_theoretical_distribution(data_clean, fit_distribution)

        # Add statistical information
        self._add_distribution_stats(data_clean)

        self.axes.set_xlabel('Value')
        self.axes.set_ylabel('Density' if kde else 'Frequency')
        self.axes.set_title('Distribution Analysis')
        self.axes.legend()
        self.axes.grid(True, alpha=0.3)

    def _fit_theoretical_distribution(self, data: np.ndarray, dist_name: str) -> None:
        """Fit and overlay theoretical distribution."""
        x_range = np.linspace(data.min(), data.max(), 300)

        if dist_name == 'normal':
            mu, sigma = stats.norm.fit(data)
            theoretical = stats.norm.pdf(x_range, mu, sigma)
            label = f'Normal(μ={mu:.2f}, σ={sigma:.2f})'

        elif dist_name == 'lognormal':
            s, loc, scale = stats.lognorm.fit(data, floc=0)
            theoretical = stats.lognorm.pdf(x_range, s, loc, scale)
            label = f'Log-Normal(s={s:.2f})'

        elif dist_name == 'exponential':
            loc, scale = stats.expon.fit(data)
            theoretical = stats.expon.pdf(x_range, loc, scale)
            label = f'Exponential(λ={1/scale:.2f})'

        else:
            return

        self.axes.plot(x_range, theoretical, '--', color='green', linewidth=2,
                     label=label)

    def _add_distribution_stats(self, data: np.ndarray) -> None:
        """Add statistical summary as text box."""
        stats_text = f"""Statistics:
Mean: {np.mean(data):.3f}
Median: {np.median(data):.3f}
Std: {np.std(data):.3f}
Skewness: {stats.skew(data):.3f}
Kurtosis: {stats.kurtosis(data):.3f}"""

        # Add text box
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        self.axes.text(0.02, 0.98, stats_text, transform=self.axes.transAxes,
                      fontsize=9, verticalalignment='top', bbox=props)


class CorrelationChart(BaseChart):
    """Correlation and portfolio analysis visualization."""

    def plot_correlation_matrix(
        self,
        data: Union[np.ndarray, pd.DataFrame],
        labels: Optional[List[str]] = None,
        *,
        method: str = 'pearson',
        cluster: bool = False,
        significance: bool = True,
        **kwargs
    ) -> None:
        """
        Plot correlation matrix with advanced features.

        Parameters:
            data: Data matrix or DataFrame
            labels: Variable names
            method: Correlation method ('pearson', 'spearman', 'kendall')
            cluster: Apply hierarchical clustering to reorder variables
            significance: Show significance levels
        """
        if HAS_PANDAS and isinstance(data, pd.DataFrame):
            corr_matrix = data.corr(method=method)
            if labels is None:
                labels = data.columns.tolist()
        else:
            if not HAS_SCIPY:
                raise VizlyError("SciPy required for correlation analysis")

            data = np.asarray(data)
            if method == 'pearson':
                corr_matrix = np.corrcoef(data.T)
            else:
                # Use scipy for other methods
                n_vars = data.shape[1]
                corr_matrix = np.zeros((n_vars, n_vars))
                for i in range(n_vars):
                    for j in range(n_vars):
                        if method == 'spearman':
                            corr, _ = stats.spearmanr(data[:, i], data[:, j])
                        elif method == 'kendall':
                            corr, _ = stats.kendalltau(data[:, i], data[:, j])
                        corr_matrix[i, j] = corr

        # Apply clustering if requested
        if cluster and HAS_SCIPY:
            from scipy.cluster.hierarchy import linkage, dendrogram, leaves_list
            from scipy.spatial.distance import squareform

            # Convert correlation to distance
            distance_matrix = 1 - np.abs(corr_matrix)
            condensed_distances = squareform(distance_matrix)
            linkage_matrix = linkage(condensed_distances, method='ward')

            # Get leaf order
            leaf_order = leaves_list(linkage_matrix)

            # Reorder correlation matrix
            if HAS_PANDAS and hasattr(corr_matrix, 'iloc'):
                corr_matrix = corr_matrix.iloc[leaf_order, leaf_order]
            else:
                corr_matrix = corr_matrix[np.ix_(leaf_order, leaf_order)]
            if labels:
                labels = [labels[i] for i in leaf_order]

        # Create heatmap
        im = self.axes.imshow(corr_matrix, cmap='RdBu_r', aspect='auto',
                             vmin=-1, vmax=1, **kwargs)

        # Add colorbar
        cbar = self.figure.figure.colorbar(im, ax=self.axes)
        cbar.set_label('Correlation Coefficient')

        # Add correlation values as text
        for i in range(corr_matrix.shape[0]):
            for j in range(corr_matrix.shape[1]):
                if HAS_PANDAS and hasattr(corr_matrix, 'iloc'):
                    value = corr_matrix.iloc[i, j]
                else:
                    value = corr_matrix[i, j]

                # Choose text color based on value
                text_color = 'white' if abs(value) > 0.5 else 'black'

                # Add significance markers if requested
                if significance:
                    if abs(value) > 0.8:
                        marker = '***'
                    elif abs(value) > 0.6:
                        marker = '**'
                    elif abs(value) > 0.3:
                        marker = '*'
                    else:
                        marker = ''

                    text = f'{value:.2f}{marker}'
                else:
                    text = f'{value:.2f}'

                self.axes.text(j, i, text, ha='center', va='center',
                             color=text_color, fontsize=8)

        # Set labels
        if labels:
            self.axes.set_xticks(range(len(labels)))
            self.axes.set_yticks(range(len(labels)))
            self.axes.set_xticklabels(labels, rotation=45, ha='right')
            self.axes.set_yticklabels(labels)

        self.axes.set_title(f'{method.capitalize()} Correlation Matrix')

    def plot_scatter_matrix(
        self,
        data: Union[np.ndarray, pd.DataFrame],
        labels: Optional[List[str]] = None,
        *,
        diagonal: str = 'hist',
        alpha: float = 0.6,
        **kwargs
    ) -> None:
        """
        Create scatter plot matrix for multivariate data exploration.

        Parameters:
            data: Data matrix or DataFrame
            labels: Variable names
            diagonal: What to plot on diagonal ('hist', 'kde', 'none')
            alpha: Point transparency
        """
        if HAS_PANDAS and isinstance(data, pd.DataFrame):
            data_array = data.values
            if labels is None:
                labels = data.columns.tolist()
        else:
            data_array = np.asarray(data)

        n_vars = data_array.shape[1]

        # Clear figure and create subplot grid
        self.figure.figure.clear()
        fig = self.figure.figure

        for i in range(n_vars):
            for j in range(n_vars):
                ax = fig.add_subplot(n_vars, n_vars, i * n_vars + j + 1)

                if i == j:
                    # Diagonal: histogram or KDE
                    if diagonal == 'hist':
                        ax.hist(data_array[:, i], bins=20, alpha=0.7)
                    elif diagonal == 'kde' and HAS_SCIPY:
                        x_range = np.linspace(data_array[:, i].min(),
                                            data_array[:, i].max(), 100)
                        kde = stats.gaussian_kde(data_array[:, i])
                        ax.plot(x_range, kde(x_range))
                else:
                    # Off-diagonal: scatter plot
                    ax.scatter(data_array[:, j], data_array[:, i],
                             alpha=alpha, s=10, **kwargs)

                # Set labels only on edges
                if i == n_vars - 1 and labels:
                    ax.set_xlabel(labels[j])
                if j == 0 and labels:
                    ax.set_ylabel(labels[i])

                # Remove tick labels for internal plots
                if i < n_vars - 1:
                    ax.set_xticklabels([])
                if j > 0:
                    ax.set_yticklabels([])

                ax.grid(True, alpha=0.3)

        plt.tight_layout()
        self.bind_axes(fig.axes[0])  # Bind to first subplot


class FinancialIndicatorChart(BaseChart):
    """Advanced financial technical indicators and analysis."""

    def plot_bollinger_bands(
        self,
        dates: Union[List[datetime], pd.DatetimeIndex],
        prices: np.ndarray,
        window: int = 20,
        num_std: float = 2.0,
        **kwargs
    ) -> None:
        """
        Plot Bollinger Bands indicator.

        Parameters:
            dates: Time index
            prices: Price data (typically closing prices)
            window: Moving average window
            num_std: Number of standard deviations for bands
        """
        if not HAS_PANDAS:
            raise VizlyError("Pandas required for financial indicators")

        # Convert to pandas Series
        if not isinstance(dates, pd.DatetimeIndex):
            dates = pd.to_datetime(dates)

        price_series = pd.Series(prices, index=dates)

        # Calculate Bollinger Bands
        ma = price_series.rolling(window=window).mean()
        std = price_series.rolling(window=window).std()
        upper_band = ma + (num_std * std)
        lower_band = ma - (num_std * std)

        # Plot components
        self.axes.plot(dates, prices, label='Price', color='blue', **kwargs)
        self.axes.plot(dates, ma, label=f'{window}-period MA', color='orange',
                      linestyle='--')
        self.axes.plot(dates, upper_band, label=f'Upper Band (+{num_std}σ)',
                      color='red', alpha=0.7)
        self.axes.plot(dates, lower_band, label=f'Lower Band (-{num_std}σ)',
                      color='red', alpha=0.7)

        # Fill between bands
        self.axes.fill_between(dates, lower_band, upper_band, alpha=0.1,
                             color='gray', label='Bollinger Bands')

        # Identify potential buy/sell signals
        # Buy signal: price touches lower band
        # Sell signal: price touches upper band
        buy_signals = prices <= lower_band
        sell_signals = prices >= upper_band

        if np.any(buy_signals):
            self.axes.scatter(dates[buy_signals], prices[buy_signals],
                            marker='^', color='green', s=50,
                            label='Buy Signal', zorder=5)

        if np.any(sell_signals):
            self.axes.scatter(dates[sell_signals], prices[sell_signals],
                            marker='v', color='red', s=50,
                            label='Sell Signal', zorder=5)

        self.axes.set_title('Bollinger Bands Analysis')
        self.axes.set_xlabel('Date')
        self.axes.set_ylabel('Price')
        self.axes.legend()
        self.axes.grid(True, alpha=0.3)

        # Format dates
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(self.axes.xaxis.get_majorticklabels(), rotation=45)

    def plot_rsi(
        self,
        dates: Union[List[datetime], pd.DatetimeIndex],
        prices: np.ndarray,
        window: int = 14,
        overbought: float = 70,
        oversold: float = 30,
        **kwargs
    ) -> None:
        """
        Plot Relative Strength Index (RSI).

        Parameters:
            dates: Time index
            prices: Price data
            window: RSI calculation window
            overbought: Overbought threshold
            oversold: Oversold threshold
        """
        if not HAS_PANDAS:
            raise VizlyError("Pandas required for RSI calculation")

        # Convert to pandas Series
        if not isinstance(dates, pd.DatetimeIndex):
            dates = pd.to_datetime(dates)

        price_series = pd.Series(prices, index=dates)

        # Calculate RSI
        delta = price_series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # Plot RSI
        self.axes.plot(dates, rsi, label='RSI', color='purple', **kwargs)

        # Add threshold lines
        self.axes.axhline(y=overbought, color='red', linestyle='--', alpha=0.7,
                         label=f'Overbought ({overbought})')
        self.axes.axhline(y=oversold, color='green', linestyle='--', alpha=0.7,
                         label=f'Oversold ({oversold})')
        self.axes.axhline(y=50, color='gray', linestyle=':', alpha=0.5,
                         label='Neutral (50)')

        # Fill overbought/oversold regions
        self.axes.fill_between(dates, overbought, 100, alpha=0.1, color='red')
        self.axes.fill_between(dates, 0, oversold, alpha=0.1, color='green')

        # Identify signals
        overbought_signals = rsi >= overbought
        oversold_signals = rsi <= oversold

        if np.any(overbought_signals):
            signal_dates = dates[overbought_signals]
            signal_values = rsi[overbought_signals]
            self.axes.scatter(signal_dates, signal_values, marker='v',
                            color='red', s=30, label='Sell Signal', zorder=5)

        if np.any(oversold_signals):
            signal_dates = dates[oversold_signals]
            signal_values = rsi[oversold_signals]
            self.axes.scatter(signal_dates, signal_values, marker='^',
                            color='green', s=30, label='Buy Signal', zorder=5)

        self.axes.set_title(f'RSI ({window} periods)')
        self.axes.set_xlabel('Date')
        self.axes.set_ylabel('RSI')
        self.axes.set_ylim(0, 100)
        self.axes.legend()
        self.axes.grid(True, alpha=0.3)

        # Format dates
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(self.axes.xaxis.get_majorticklabels(), rotation=45)

    def plot_macd(
        self,
        dates: Union[List[datetime], pd.DatetimeIndex],
        prices: np.ndarray,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        **kwargs
    ) -> None:
        """
        Plot MACD (Moving Average Convergence Divergence) indicator.

        Parameters:
            dates: Time index
            prices: Price data
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line EMA period
        """
        if not HAS_PANDAS:
            raise VizlyError("Pandas required for MACD calculation")

        # Convert to pandas Series
        if not isinstance(dates, pd.DatetimeIndex):
            dates = pd.to_datetime(dates)

        price_series = pd.Series(prices, index=dates)

        # Calculate EMAs
        ema_fast = price_series.ewm(span=fast_period).mean()
        ema_slow = price_series.ewm(span=slow_period).mean()

        # Calculate MACD line and signal line
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period).mean()
        histogram = macd_line - signal_line

        # Clear figure and create subplots
        self.figure.figure.clear()
        fig = self.figure.figure

        # Price subplot
        ax1 = fig.add_subplot(2, 1, 1)
        ax1.plot(dates, prices, label='Price', color='blue')
        ax1.plot(dates, ema_fast, label=f'EMA{fast_period}', color='orange', alpha=0.7)
        ax1.plot(dates, ema_slow, label=f'EMA{slow_period}', color='red', alpha=0.7)
        ax1.set_title('Price with EMAs')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # MACD subplot
        ax2 = fig.add_subplot(2, 1, 2)
        ax2.plot(dates, macd_line, label='MACD', color='blue', linewidth=2)
        ax2.plot(dates, signal_line, label='Signal', color='red', linewidth=2)

        # MACD histogram
        colors = ['green' if h >= 0 else 'red' for h in histogram]
        ax2.bar(dates, histogram, label='Histogram', alpha=0.6, color=colors)

        # Zero line
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)

        # Identify crossover signals
        crossover = np.where(np.diff(np.sign(macd_line - signal_line)))[0]
        for cross in crossover:
            if cross < len(dates) - 1:
                if macd_line.iloc[cross + 1] > signal_line.iloc[cross + 1]:
                    # Bullish crossover
                    ax2.scatter(dates[cross + 1], macd_line.iloc[cross + 1],
                              marker='^', color='green', s=50, zorder=5)
                else:
                    # Bearish crossover
                    ax2.scatter(dates[cross + 1], macd_line.iloc[cross + 1],
                              marker='v', color='red', s=50, zorder=5)

        ax2.set_title('MACD Indicator')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('MACD')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Format dates
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()
        self.bind_axes(ax1)

    def plot_volume_profile(
        self,
        dates: Union[List[datetime], pd.DatetimeIndex],
        prices: np.ndarray,
        volumes: np.ndarray,
        price_bins: int = 50,
        **kwargs
    ) -> None:
        """
        Plot Volume Profile showing volume traded at each price level.

        Parameters:
            dates: Time index
            prices: Price data
            volumes: Volume data
            price_bins: Number of price bins for profile
        """
        if not HAS_PANDAS:
            raise VizlyError("Pandas required for volume profile")

        # Create price bins
        price_min, price_max = np.min(prices), np.max(prices)
        price_levels = np.linspace(price_min, price_max, price_bins)
        volume_profile = np.zeros(price_bins - 1)

        # Calculate volume at each price level
        for i in range(len(prices) - 1):
            price_idx = np.digitize(prices[i], price_levels) - 1
            if 0 <= price_idx < len(volume_profile):
                volume_profile[price_idx] += volumes[i]

        # Clear figure and create side-by-side subplots
        self.figure.figure.clear()
        fig = self.figure.figure

        # Price chart on left
        ax1 = fig.add_subplot(1, 2, 1)
        ax1.plot(dates, prices, label='Price', color='blue')
        ax1.set_title('Price Chart')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Volume profile on right
        ax2 = fig.add_subplot(1, 2, 2, sharey=ax1)
        price_centers = (price_levels[:-1] + price_levels[1:]) / 2
        ax2.barh(price_centers, volume_profile, height=(price_max - price_min) / price_bins,
                alpha=0.7, color='orange')

        # Highlight Point of Control (POC) - highest volume level
        poc_idx = np.argmax(volume_profile)
        poc_price = price_centers[poc_idx]
        ax2.axhline(y=poc_price, color='red', linestyle='--', linewidth=2,
                   label=f'POC: ${poc_price:.2f}')

        # Value Area (70% of volume)
        sorted_indices = np.argsort(volume_profile)[::-1]
        cumulative_volume = 0
        total_volume = np.sum(volume_profile)
        value_area_indices = []

        for idx in sorted_indices:
            cumulative_volume += volume_profile[idx]
            value_area_indices.append(idx)
            if cumulative_volume >= 0.7 * total_volume:
                break

        value_area_low = np.min(price_centers[value_area_indices])
        value_area_high = np.max(price_centers[value_area_indices])

        ax2.axhspan(value_area_low, value_area_high, alpha=0.2, color='blue',
                   label=f'Value Area: ${value_area_low:.2f}-${value_area_high:.2f}')

        ax2.set_title('Volume Profile')
        ax2.set_xlabel('Volume')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Format dates on price chart
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()
        self.bind_axes(ax1)

    def plot_candlestick_with_indicators(
        self,
        dates: Union[List[datetime], pd.DatetimeIndex],
        open_prices: np.ndarray,
        high_prices: np.ndarray,
        low_prices: np.ndarray,
        close_prices: np.ndarray,
        volumes: Optional[np.ndarray] = None,
        show_bollinger: bool = True,
        show_rsi: bool = True,
        **kwargs
    ) -> None:
        """
        Plot comprehensive candlestick chart with multiple technical indicators.

        Parameters:
            dates: Time index
            open_prices: Opening prices
            high_prices: High prices
            low_prices: Low prices
            close_prices: Closing prices
            volumes: Volume data (optional)
            show_bollinger: Show Bollinger Bands
            show_rsi: Show RSI indicator
        """
        if not HAS_PANDAS:
            raise VizlyError("Pandas required for candlestick charts")

        # Convert to pandas
        if not isinstance(dates, pd.DatetimeIndex):
            dates = pd.to_datetime(dates)

        # Clear figure and create subplots
        self.figure.figure.clear()
        fig = self.figure.figure

        # Determine subplot layout
        n_subplots = 1
        if volumes is not None:
            n_subplots += 1
        if show_rsi:
            n_subplots += 1

        # Main candlestick chart
        ax1 = fig.add_subplot(n_subplots, 1, 1)

        # Create candlestick data
        for i, date in enumerate(dates):
            color = 'green' if close_prices[i] >= open_prices[i] else 'red'
            alpha = 0.8

            # Draw candlestick body
            body_height = abs(close_prices[i] - open_prices[i])
            body_bottom = min(open_prices[i], close_prices[i])

            ax1.add_patch(Rectangle((date, body_bottom), timedelta(days=0.6),
                                  body_height, facecolor=color, alpha=alpha))

            # Draw wicks
            ax1.plot([date, date], [low_prices[i], high_prices[i]],
                    color='black', linewidth=1)

        # Add Bollinger Bands if requested
        if show_bollinger:
            close_series = pd.Series(close_prices, index=dates)
            ma = close_series.rolling(window=20).mean()
            std = close_series.rolling(window=20).std()
            upper_band = ma + (2 * std)
            lower_band = ma - (2 * std)

            ax1.plot(dates, ma, label='20-MA', color='orange', linestyle='--')
            ax1.plot(dates, upper_band, label='Upper BB', color='red', alpha=0.7)
            ax1.plot(dates, lower_band, label='Lower BB', color='red', alpha=0.7)
            ax1.fill_between(dates, lower_band, upper_band, alpha=0.1, color='gray')

        ax1.set_title('Candlestick Chart with Technical Indicators')
        ax1.set_ylabel('Price')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        subplot_idx = 2

        # Volume subplot
        if volumes is not None:
            ax_vol = fig.add_subplot(n_subplots, 1, subplot_idx, sharex=ax1)
            colors = ['green' if close_prices[i] >= open_prices[i] else 'red'
                     for i in range(len(dates))]
            ax_vol.bar(dates, volumes, color=colors, alpha=0.7)
            ax_vol.set_title('Volume')
            ax_vol.set_ylabel('Volume')
            ax_vol.grid(True, alpha=0.3)
            subplot_idx += 1

        # RSI subplot
        if show_rsi:
            ax_rsi = fig.add_subplot(n_subplots, 1, subplot_idx, sharex=ax1)

            # Calculate RSI
            close_series = pd.Series(close_prices, index=dates)
            delta = close_series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            ax_rsi.plot(dates, rsi, label='RSI', color='purple')
            ax_rsi.axhline(y=70, color='red', linestyle='--', alpha=0.7)
            ax_rsi.axhline(y=30, color='green', linestyle='--', alpha=0.7)
            ax_rsi.axhline(y=50, color='gray', linestyle=':', alpha=0.5)
            ax_rsi.fill_between(dates, 70, 100, alpha=0.1, color='red')
            ax_rsi.fill_between(dates, 0, 30, alpha=0.1, color='green')

            ax_rsi.set_title('RSI (14)')
            ax_rsi.set_ylabel('RSI')
            ax_rsi.set_ylim(0, 100)
            ax_rsi.grid(True, alpha=0.3)

        # Format dates
        for ax in fig.axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()
        self.bind_axes(ax1)


class RegressionChart(BaseChart):
    """Regression analysis visualization."""

    def plot(self, x: np.ndarray, y: np.ndarray, show_confidence: bool = True) -> None:
        """Plot data with regression line and confidence intervals."""
        # Simple linear regression
        coeffs = np.polyfit(x, y, 1)
        regression_line = np.polyval(coeffs, x)

        # Plot data points
        self.axes.scatter(x, y, alpha=0.6, label='Data Points')

        # Plot regression line
        self.axes.plot(x, regression_line, 'r-', linewidth=2, label=f'y = {coeffs[0]:.2f}x + {coeffs[1]:.2f}')

        if show_confidence:
            # Simple confidence interval estimation
            residuals = y - regression_line
            std_error = np.std(residuals)
            confidence = 1.96 * std_error  # 95% confidence interval

            self.axes.fill_between(x, regression_line - confidence, regression_line + confidence,
                                 alpha=0.2, color='red', label='95% Confidence Interval')

        self.axes.set_xlabel('X')
        self.axes.set_ylabel('Y')
        self.axes.set_title('Regression Analysis')
        self.axes.legend()
        self.axes.grid(True, alpha=0.3)


# Export all classes for easy importing
__all__ = [
    'TimeSeriesChart',
    'DistributionChart',
    'CorrelationChart',
    'FinancialIndicatorChart',
    'RegressionChart'
]