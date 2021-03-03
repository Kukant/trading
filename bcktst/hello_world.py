
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

from bcktst import strategies, indicators

# Create a Stratey
from backtrader.feeds import GenericCSVData



class BaseStrategy(bt.Strategy):
    params = dict(
        fast_ma=10,
        slow_ma=20,
    )

    def __init__(self):
        # omitting a data implies self.datas[0] (aka self.data and self.data0)
        self.fast_ma = bt.ind.SMA(period=self.p.fast_ma)
        self.slow_ma = bt.ind.SMA(period=self.p.slow_ma)
        self.ssl = indicators.SSLChannel()
        # our entry point
        self.crossup = bt.ind.CrossUp(self.fast_ma, self.slow_ma)


class TestStrategy(BaseStrategy):
    params = dict(
        trail=0.02,
    )

    def notify_order(self, order):
        if not order.status == order.Completed:
            return  # discard any other notification

        if not self.position:  # we left the market
            print('SELL@price: {:.2f}'.format(order.executed.price))
            return

        # We have entered the market
        print('BUY @price: {:.2f}'.format(order.executed.price))

        self.sell(exectype=bt.Order.StopTrail, trailpercent=self.p.trail)

    def should_buy(self) -> bool:
        """
        Buy only if current price is under fast average, but is bigger than the last one.
        :return:
        """
        blah = self.fast_ma
        num = 4
        return all([blah[-(i + 1)] < blah[-i] for i in range(num)])

    def next(self):
        if not self.position and (self.ssl.lines.ssld[0] <= self.ssl.lines.sslu[0]) and self.data[0] < self.fast_ma[0]:
            # not in the market and signal triggered
            self.buy()

        elif self.position and (self.ssl.lines.ssld[0] > self.ssl.lines.sslu[0]):
            self.sell()


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(strategies.TakeProfitS)

    # Create a Data Feed
    data = GenericCSVData(
        dataname='../data/BTCUSDT_5m_2021-02-09-2021-02-14.csv',

        # similar start/end prices
        #fromdate=datetime.datetime(2017, 8, 8),
        #todate=datetime.datetime(2017, 8, 14),
        fromdate=datetime.datetime(2021, 2, 9),
        todate=datetime.datetime(2021, 2, 14),
        timeframe=bt.TimeFrame.Minutes,

        nullvalue=0.0,

        dtformat=('%Y-%m-%d %H:%M:%S'),
        # 2017-06-01,06:00:00

        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1,
    )


    start_cash = 50000
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(start_cash)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    start_value = cerebro.broker.getvalue()

    # Run over everything
    cerebro.run()

    # Print out the final result
    profit = cerebro.broker.getvalue() - start_value
    print('Final Portfolio Value: %.2f, profit: %.2f, ' % (cerebro.broker.getvalue(), profit))
    print('Buy in the beggining, sell in the end profit: {:.2f}'.format(
        start_cash * (
                data.open.array[-1] / data.open.array[0]
        ) - start_cash
    ))
    # Plot the result
    cerebro.plot(style='candlestick')