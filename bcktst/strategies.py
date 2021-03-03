import backtrader as bt

from bcktst import indicators


class TakeProfitS(bt.Strategy):
    params = (
        ("period1", 2),
        ("devfactor", 2),
        ("rsip", 8),
        ("buy_price_adjust", 0.0),
        ("buy_limit_adjust", 0.02),
        ("buy_stop_adjust", 0.02),
    )

    def log(self, txt, dt=None):
        """ Logging function fot this strategy"""
        dt = dt or self.data.datetime[0]
        if isinstance(dt, float):
            dt = bt.num2date(dt)
        print("%s, %s" % (dt.date(), txt))

    def print_signal(self):

        self.log(
            "o {:5.2f}\th {:5.2f}\tl {:5.2f}\tc {:5.2f}\tv {:5.0f}".format(
                self.datas[0].open[0],
                self.datas[0].high[0],
                self.datas[0].low[0],
                self.datas[0].close[0],
                self.datas[0].volume[0],
            )
        )

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status in [order.Canceled, order.Margin]:
            if order.isbuy():
                self.log("BUY FAILED, Cancelled or Margin")

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    "BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )

            self.bar_executed = len(self)

        # Cleans up the order list.
        if not order.alive() and order in self.o_li:
            self.o_li.remove(order)

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log("OPERATION PROFIT, GROSS %.2f, NET %.2f" % (trade.pnl, trade.pnlcomm))

    def __init__(self):
        self.o_li = list()

        self.ssl = indicators.SSLChannel()


    def next(self):

        self.print_signal()

        if self.position.size == 0 and len(self.o_li) == 0:
            if self.ssl.lines.ssld[0] <= self.ssl.lines.sslu[0]:
                price = self.data.close[0] * (1.0 - self.p.buy_price_adjust)
                price_limit = price * (1.0 + self.p.buy_limit_adjust)
                price_stop = price * (1.0 - self.p.buy_stop_adjust)

                self.long_buy_order = self.buy_bracket(
                    data=self.datas[0],
                    size=1,
                    exectype=bt.Order.Limit,
                    plimit=price,
                    stopprice=price_stop,
                    stopexec=bt.Order.Stop,
                    limitprice=price_limit,
                    limitexec=bt.Order.Limit,
                )

                # Store orders in a list
                self.o_li = [o for o in self.long_buy_order]

                self.log(
                    "LONG BUY limit Targets: Buy {:8.2f}, Limit {:8.2f}, Stop {:8.2f}".format(
                        price, price_limit, price_stop
                    )
                )


        # if self.position.size > 0:
        #     if self.rsi > 70:
        #         print("Sell shares at {}".format(self.data.close[0]))
        #         self.close()
        #         self.o_li = list()