"""Financial and trading chart types."""

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

import logging
from typing import List, Optional, Tuple, Union
import warnings

import numpy as np
import pandas as pd
from datetime import datetime

from .base import BaseChart

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
    from matplotlib.collections import LineCollection
except ImportError:
    warnings.warn("Matplotlib not available for financial charts")

try:
    import talib

    HAS_TALIB = True
except ImportError:
    HAS_TALIB = False


logger = logging.getLogger(__name__)


class CandlestickChart(BaseChart):
    """Candlestick chart for financial data."""

    def plot(
        self,
        dates: Union[List[datetime], pd.DatetimeIndex],
        open_prices: np.ndarray,
        high_prices: np.ndarray,
        low_prices: np.ndarray,
        close_prices: np.ndarray,
        volume: Optional[np.ndarray] = None,
        up_color: str = "green",
        down_color: str = "red",
        wick_color: str = "black",
        volume_color: str = "blue",
        alpha: float = 0.8,
    ) -> None:
        """Plot candlestick chart."""

        if not (
            len(dates)
            == len(open_prices)
            == len(high_prices)
            == len(low_prices)
            == len(close_prices)
        ):
            raise ValueError("All price arrays must have the same length")

        # Convert dates to matplotlib format
        if isinstance(dates, pd.DatetimeIndex):
            dates_mpl = mdates.date2num(dates.to_pydatetime())
        else:
            dates_mpl = mdates.date2num(dates)

        # Determine bar width
        if len(dates_mpl) > 1:
            bar_width = 0.6 * (dates_mpl[1] - dates_mpl[0])
        else:
            bar_width = 0.6

        # Create subplot layout if volume is provided
        if volume is not None:
            # Clear current axes and create subplots
            self.figure.figure.clear()
            price_ax = self.figure.figure.add_subplot(2, 1, 1)
            volume_ax = self.figure.figure.add_subplot(2, 1, 2, sharex=price_ax)
            self.bind_axes(price_ax)
        else:
            price_ax = self.axes
            volume_ax = None

        # Plot candlesticks
        for i, (date, o, h, l, c) in enumerate(
            zip(dates_mpl, open_prices, high_prices, low_prices, close_prices)
        ):
            # Determine color
            color = up_color if c >= o else down_color

            # Draw the wick (high-low line)
            price_ax.plot([date, date], [l, h], color=wick_color, linewidth=1)

            # Draw the body (open-close rectangle)
            body_height = abs(c - o)
            body_bottom = min(o, c)

            rect = Rectangle(
                (date - bar_width / 2, body_bottom),
                bar_width,
                body_height,
                facecolor=color,
                edgecolor=wick_color,
                alpha=alpha,
            )
            price_ax.add_patch(rect)

        # Format x-axis
        price_ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        price_ax.xaxis.set_major_locator(
            mdates.DayLocator(interval=max(1, len(dates) // 10))
        )
        plt.setp(price_ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

        # Set labels
        price_ax.set_ylabel("Price")
        price_ax.grid(True, alpha=0.3)

        # Plot volume if provided
        if volume is not None and volume_ax is not None:
            colors = [
                up_color if c >= o else down_color
                for o, c in zip(open_prices, close_prices)
            ]

            volume_ax.bar(dates_mpl, volume, width=bar_width, color=colors, alpha=0.6)
            volume_ax.set_ylabel("Volume")
            volume_ax.grid(True, alpha=0.3)

        self.figure.figure.tight_layout()

    def add_moving_average(
        self,
        dates: Union[List[datetime], pd.DatetimeIndex],
        prices: np.ndarray,
        period: int,
        color: str = "blue",
        label: Optional[str] = None,
    ) -> None:
        """Add moving average to the chart."""

        if HAS_TALIB:
            ma = talib.SMA(prices, timeperiod=period)
        else:
            # Simple moving average calculation
            ma = np.convolve(prices, np.ones(period) / period, mode="valid")
            # Pad with NaNs to match original length
            ma = np.concatenate([np.full(period - 1, np.nan), ma])

        # Convert dates
        if isinstance(dates, pd.DatetimeIndex):
            dates_mpl = mdates.date2num(dates.to_pydatetime())
        else:
            dates_mpl = mdates.date2num(dates)

        # Plot moving average
        label = label or f"{period}-day MA"
        self.axes.plot(dates_mpl, ma, color=color, linewidth=2, label=label)
        self.axes.legend()

    def add_bollinger_bands(
        self,
        dates: Union[List[datetime], pd.DatetimeIndex],
        prices: np.ndarray,
        period: int = 20,
        num_std: float = 2.0,
        color: str = "gray",
        alpha: float = 0.3,
    ) -> None:
        """Add Bollinger Bands to the chart."""

        if HAS_TALIB:
            upper, middle, lower = talib.BBANDS(
                prices, timeperiod=period, nbdevup=num_std, nbdevdn=num_std
            )
        else:
            # Manual calculation
            rolling_mean = np.convolve(prices, np.ones(period) / period, mode="valid")
            rolling_std = np.array(
                [
                    np.std(prices[i : i + period])
                    for i in range(len(prices) - period + 1)
                ]
            )

            # Pad with NaNs
            rolling_mean = np.concatenate([np.full(period - 1, np.nan), rolling_mean])
            rolling_std = np.concatenate([np.full(period - 1, np.nan), rolling_std])

            upper = rolling_mean + num_std * rolling_std
            lower = rolling_mean - num_std * rolling_std
            middle = rolling_mean

        # Convert dates
        if isinstance(dates, pd.DatetimeIndex):
            dates_mpl = mdates.date2num(dates.to_pydatetime())
        else:
            dates_mpl = mdates.date2num(dates)

        # Plot bands
        self.axes.plot(
            dates_mpl, upper, color=color, linewidth=1, linestyle="--", alpha=0.7
        )
        self.axes.plot(
            dates_mpl, lower, color=color, linewidth=1, linestyle="--", alpha=0.7
        )
        self.axes.plot(dates_mpl, middle, color=color, linewidth=1, alpha=0.7)

        # Fill between bands
        self.axes.fill_between(dates_mpl, upper, lower, color=color, alpha=alpha)


class OHLCChart(BaseChart):
    """OHLC (Open-High-Low-Close) bar chart."""

    def plot(
        self,
        dates: Union[List[datetime], pd.DatetimeIndex],
        open_prices: np.ndarray,
        high_prices: np.ndarray,
        low_prices: np.ndarray,
        close_prices: np.ndarray,
        color: str = "black",
        tick_size: float = 0.3,
    ) -> None:
        """Plot OHLC bars."""

        # Convert dates to matplotlib format
        if isinstance(dates, pd.DatetimeIndex):
            dates_mpl = mdates.date2num(dates.to_pydatetime())
        else:
            dates_mpl = mdates.date2num(dates)

        # Determine bar width
        if len(dates_mpl) > 1:
            bar_width = (dates_mpl[1] - dates_mpl[0]) * tick_size
        else:
            bar_width = tick_size

        # Plot OHLC bars
        for date, o, h, l, c in zip(
            dates_mpl, open_prices, high_prices, low_prices, close_prices
        ):
            # Vertical line (high-low)
            self.axes.plot([date, date], [l, h], color=color, linewidth=1)

            # Left tick (open)
            self.axes.plot([date - bar_width, date], [o, o], color=color, linewidth=1)

            # Right tick (close)
            self.axes.plot([date, date + bar_width], [c, c], color=color, linewidth=1)

        # Format axes
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        self.axes.xaxis.set_major_locator(
            mdates.DayLocator(interval=max(1, len(dates) // 10))
        )
        plt.setp(self.axes.xaxis.get_majorticklabels(), rotation=45, ha="right")

        self.axes.set_ylabel("Price")
        self.axes.grid(True, alpha=0.3)


class VolumeProfileChart(BaseChart):
    """Volume profile chart showing volume distribution by price."""

    def plot(
        self,
        prices: np.ndarray,
        volumes: np.ndarray,
        price_bins: int = 50,
        orientation: str = "horizontal",
        color: str = "blue",
        alpha: float = 0.7,
    ) -> None:
        """Plot volume profile."""

        # Create price bins
        price_range = np.linspace(prices.min(), prices.max(), price_bins + 1)
        volume_profile = np.zeros(price_bins)

        # Accumulate volume in each price bin
        for price, volume in zip(prices, volumes):
            bin_idx = np.digitize(price, price_range) - 1
            if 0 <= bin_idx < price_bins:
                volume_profile[bin_idx] += volume

        # Calculate bin centers
        bin_centers = (price_range[:-1] + price_range[1:]) / 2

        # Plot profile
        if orientation == "horizontal":
            self.axes.barh(
                bin_centers,
                volume_profile,
                height=(price_range[1] - price_range[0]),
                color=color,
                alpha=alpha,
            )
            self.axes.set_xlabel("Volume")
            self.axes.set_ylabel("Price")
        else:
            self.axes.bar(
                bin_centers,
                volume_profile,
                width=(price_range[1] - price_range[0]),
                color=color,
                alpha=alpha,
            )
            self.axes.set_xlabel("Price")
            self.axes.set_ylabel("Volume")

        self.axes.grid(True, alpha=0.3)


class RSIChart(BaseChart):
    """Relative Strength Index (RSI) chart."""

    def plot(
        self,
        dates: Union[List[datetime], pd.DatetimeIndex],
        prices: np.ndarray,
        period: int = 14,
        overbought: float = 70,
        oversold: float = 30,
        color: str = "purple",
    ) -> None:
        """Plot RSI indicator."""

        if HAS_TALIB:
            rsi = talib.RSI(prices, timeperiod=period)
        else:
            # Manual RSI calculation
            rsi = self._calculate_rsi(prices, period)

        # Convert dates
        if isinstance(dates, pd.DatetimeIndex):
            dates_mpl = mdates.date2num(dates.to_pydatetime())
        else:
            dates_mpl = mdates.date2num(dates)

        # Plot RSI
        self.axes.plot(dates_mpl, rsi, color=color, linewidth=2, label="RSI")

        # Add overbought/oversold lines
        self.axes.axhline(
            y=overbought, color="red", linestyle="--", alpha=0.7, label="Overbought"
        )
        self.axes.axhline(
            y=oversold, color="green", linestyle="--", alpha=0.7, label="Oversold"
        )
        self.axes.axhline(y=50, color="gray", linestyle="-", alpha=0.5, label="Midline")

        # Fill overbought/oversold areas
        self.axes.fill_between(dates_mpl, overbought, 100, alpha=0.2, color="red")
        self.axes.fill_between(dates_mpl, 0, oversold, alpha=0.2, color="green")

        # Format axes
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        self.axes.xaxis.set_major_locator(
            mdates.DayLocator(interval=max(1, len(dates) // 10))
        )
        plt.setp(self.axes.xaxis.get_majorticklabels(), rotation=45, ha="right")

        self.axes.set_ylabel("RSI")
        self.axes.set_ylim(0, 100)
        self.axes.legend()
        self.axes.grid(True, alpha=0.3)

    def _calculate_rsi(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate RSI manually."""
        if len(prices) < period + 1:
            return np.full(len(prices), np.nan)

        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gains = np.full(len(prices), np.nan)
        avg_losses = np.full(len(prices), np.nan)

        # Initial averages
        avg_gains[period] = np.mean(gains[:period])
        avg_losses[period] = np.mean(losses[:period])

        # Subsequent averages using smoothing
        for i in range(period + 1, len(prices)):
            avg_gains[i] = (avg_gains[i - 1] * (period - 1) + gains[i - 1]) / period
            avg_losses[i] = (avg_losses[i - 1] * (period - 1) + losses[i - 1]) / period

        # Calculate RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))

        return rsi


class MACDChart(BaseChart):
    """MACD (Moving Average Convergence Divergence) chart."""

    def plot(
        self,
        dates: Union[List[datetime], pd.DatetimeIndex],
        prices: np.ndarray,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> None:
        """Plot MACD indicator."""

        if HAS_TALIB:
            macd, macd_signal, macd_hist = talib.MACD(
                prices,
                fastperiod=fast_period,
                slowperiod=slow_period,
                signalperiod=signal_period,
            )
        else:
            # Manual MACD calculation
            macd, macd_signal, macd_hist = self._calculate_macd(
                prices, fast_period, slow_period, signal_period
            )

        # Convert dates
        if isinstance(dates, pd.DatetimeIndex):
            dates_mpl = mdates.date2num(dates.to_pydatetime())
        else:
            dates_mpl = mdates.date2num(dates)

        # Plot MACD components
        self.axes.plot(dates_mpl, macd, color="blue", linewidth=2, label="MACD")
        self.axes.plot(dates_mpl, macd_signal, color="red", linewidth=2, label="Signal")

        # Plot histogram
        colors = ["green" if h >= 0 else "red" for h in macd_hist]
        self.axes.bar(dates_mpl, macd_hist, color=colors, alpha=0.6, label="Histogram")

        # Add zero line
        self.axes.axhline(y=0, color="gray", linestyle="-", alpha=0.5)

        # Format axes
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        self.axes.xaxis.set_major_locator(
            mdates.DayLocator(interval=max(1, len(dates) // 10))
        )
        plt.setp(self.axes.xaxis.get_majorticklabels(), rotation=45, ha="right")

        self.axes.set_ylabel("MACD")
        self.axes.legend()
        self.axes.grid(True, alpha=0.3)

    def _calculate_macd(
        self, prices: np.ndarray, fast_period: int, slow_period: int, signal_period: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate MACD manually."""
        # Calculate EMAs
        fast_ema = self._calculate_ema(prices, fast_period)
        slow_ema = self._calculate_ema(prices, slow_period)

        # MACD line
        macd = fast_ema - slow_ema

        # Signal line (EMA of MACD)
        macd_signal = self._calculate_ema(macd, signal_period)

        # Histogram
        macd_hist = macd - macd_signal

        return macd, macd_signal, macd_hist

    def _calculate_ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average."""
        ema = np.full(len(prices), np.nan)
        multiplier = 2.0 / (period + 1)

        # First EMA value is SMA
        ema[period - 1] = np.mean(prices[:period])

        # Calculate subsequent EMA values
        for i in range(period, len(prices)):
            ema[i] = (prices[i] * multiplier) + (ema[i - 1] * (1 - multiplier))

        return ema


class PointAndFigureChart(BaseChart):
    """Point and Figure chart for trend analysis."""

    def plot(
        self,
        prices: np.ndarray,
        box_size: Optional[float] = None,
        reversal_amount: int = 3,
        x_color: str = "red",
        o_color: str = "green",
    ) -> None:
        """Plot Point and Figure chart."""

        if box_size is None:
            # Auto-calculate box size (1% of average price)
            box_size = np.mean(prices) * 0.01

        # Generate P&F data
        pf_data = self._calculate_point_figure(prices, box_size, reversal_amount)

        # Plot the chart
        for col_idx, column in enumerate(pf_data):
            for row_idx, symbol in enumerate(column):
                if symbol == "X":
                    self.axes.text(
                        col_idx,
                        row_idx,
                        "X",
                        fontsize=12,
                        ha="center",
                        va="center",
                        color=x_color,
                        weight="bold",
                    )
                elif symbol == "O":
                    self.axes.text(
                        col_idx,
                        row_idx,
                        "O",
                        fontsize=12,
                        ha="center",
                        va="center",
                        color=o_color,
                        weight="bold",
                    )

        # Set up axes
        self.axes.set_xlim(-0.5, len(pf_data) - 0.5)
        self.axes.set_ylim(-0.5, max(len(col) for col in pf_data if col) - 0.5)
        self.axes.set_xlabel("Time Columns")
        self.axes.set_ylabel("Price Boxes")
        self.axes.grid(True, alpha=0.3)

    def _calculate_point_figure(
        self, prices: np.ndarray, box_size: float, reversal_amount: int
    ) -> List[List[str]]:
        """Calculate Point and Figure chart data."""
        columns = []
        current_column = []
        trend = None  # 'up' or 'down'
        current_price = prices[0]

        for price in prices[1:]:
            if trend is None:
                # Determine initial trend
                if price > current_price + box_size:
                    trend = "up"
                    # Add X's from current_price to price
                    start_box = int(current_price / box_size)
                    end_box = int(price / box_size)
                    current_column = ["X"] * (end_box - start_box + 1)
                elif price < current_price - box_size:
                    trend = "down"
                    # Add O's from current_price to price
                    start_box = int(current_price / box_size)
                    end_box = int(price / box_size)
                    current_column = ["O"] * (start_box - end_box + 1)
                current_price = price
                continue

            if trend == "up":
                if price > current_price + box_size:
                    # Continue up trend - add X's
                    boxes_to_add = int((price - current_price) / box_size)
                    current_column.extend(["X"] * boxes_to_add)
                    current_price = price
                elif price < current_price - (box_size * reversal_amount):
                    # Reversal - start new column with O's
                    columns.append(current_column)
                    trend = "down"
                    start_price = current_price - box_size
                    boxes_to_add = int((start_price - price) / box_size) + 1
                    current_column = ["O"] * boxes_to_add
                    current_price = price

            elif trend == "down":
                if price < current_price - box_size:
                    # Continue down trend - add O's
                    boxes_to_add = int((current_price - price) / box_size)
                    current_column.extend(["O"] * boxes_to_add)
                    current_price = price
                elif price > current_price + (box_size * reversal_amount):
                    # Reversal - start new column with X's
                    columns.append(current_column)
                    trend = "up"
                    start_price = current_price + box_size
                    boxes_to_add = int((price - start_price) / box_size) + 1
                    current_column = ["X"] * boxes_to_add
                    current_price = price

        # Add the last column
        if current_column:
            columns.append(current_column)

        return columns
