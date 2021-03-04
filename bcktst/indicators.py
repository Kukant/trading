import backtrader as bt


class SSLChannel(bt.Indicator):
    lines = ('signal', 'ssld', 'sslu')
    params = (('period', 30),)
    plotinfo = dict(
        plot=True,
        plotname='SSL Channel',
        subplot=False,
        plotlinelabels=True)

    def _plotlabel(self):
        return [self.p.period]

    def __init__(self):
        self.addminperiod(self.p.period)
        self.hma_lo = bt.indicators.SmoothedMovingAverage(self.data.low, period=self.p.period)
        self.hma_hi = bt.indicators.SmoothedMovingAverage(self.data.high, period=self.p.period)

    def next(self):
        hlv = 1 if self.data.close > self.hma_hi[0] else -1
        self.lines.signal[0] = hlv
        if hlv == -1:
            self.lines.ssld[0] = self.hma_hi[0]
            self.lines.sslu[0] = self.hma_lo[0]

        elif hlv == 1:
            self.lines.ssld[0] = self.hma_lo[0]
            self.lines.sslu[0] = self.hma_hi[0]


class EngulfingPattern(bt.Indicator):
    """
    The second candle stick is bigger than the second one by `ration`.
        bullish - The second is green, first red
        bearish - First red, second green
    """
    lines = ('signal',)  # 'bull_engulfing', 'bear_engulfing')
    params = (
        ('ratio', 2.5),
        ('minsize', 100)  # min size of the first candle
    )

    plotinfo = dict(
        subplot=True,
        plotlinelabels=True
    )
    # plotlines = dict(
    #     bull_hammer=dict(marker='^', markersize=8.0, color='blue', fillstyle='full', ls='',),
    #     bear_hammer=dict(marker='v', markersize=8.0, color='orange', fillstyle='full', ls='',),
    #     signal=dict()
    # )

    def next(self):
        first_o = self.data.open[-1]
        first_c = self.data.close[-1]

        second_o = self.data.open[0]
        second_c = self.data.close[0]

        first_size = abs(first_o - first_c)
        second_size = abs(second_o - second_c)

        first_green = first_o < first_c
        second_green = second_o < second_c

        # lets check for the engulfing pattern
        if (
                self.p.minsize < first_size < first_size * self.p.ratio < second_size and
                # have different color
                first_green != second_green
        ):
            self.lines.signal[0] = 1 if second_green else -1
        else:
            self.lines.signal[0] = 0
            print(f"{self.p.minsize} < {first_size} < {second_size} <= {first_size * self.p.ratio}")






class HammerCandles(bt.Indicator):
    '''
    Thor is a pin candle reversal indicator that tries to catch swings and
    ride the retracement down.
    '''
    lines = ('signal', 'bull_hammer', 'bear_hammer')
    params = (
        ('rev_wick_ratio', 0.6), #ratio of the long wick
    )

    plotinfo = dict(
        subplot=False,
        plotlinelabels=True
    )
    plotlines = dict(
        bull_hammer=dict(marker='^', markersize=8.0, color='blue', fillstyle='full', ls='',),
        bear_hammer=dict(marker='v', markersize=8.0, color='orange', fillstyle='full', ls='',),
        signal=dict(_plotskip=True)
    )

    def next(self):
        # then check the ranges
        range = round(self.data.high - self.data.low, 5)

        # Calcualte ratios for green candles or open/close are the same value
        if self.data.open <= self.data.close:
            upper_wick = round(self.data.high - self.data.close, 5)
            lower_wick = round(self.data.open - self.data.low, 5)

            try:
                upper_ratio = round(upper_wick/range,5)
            except ZeroDivisionError:
                upper_ratio = 0

            try:
                lower_ratio = round(lower_wick/range,5)
            except ZeroDivisionError:
                lower_ratio = 0

        # Repeat for a red candle
        else:  # if self.data.open > self.data.close:
            upper_wick = round(self.data.high - self.data.open, 5)
            lower_wick = round(self.data.close - self.data.low, 5)

            try:
                upper_ratio = round(upper_wick/range, 5)
            except ZeroDivisionError:
                upper_ratio = 0

            try:
                lower_ratio = round(lower_wick/range, 5)
            except ZeroDivisionError:
                lower_ratio = 0

        if upper_ratio >= self.p.rev_wick_ratio:
            self.lines.bear_hammer[0] = self.data.high[0]
            self.lines.signal[0] = -1
        elif lower_ratio >= self.p.rev_wick_ratio:
            self.lines.bull_hammer[0] = self.data.low[0]
            self.lines.signal[0] = 1
        else:
            self.lines.signal[0] = 0

