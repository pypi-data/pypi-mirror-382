from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import final
import numpy as np
import pandas as pd
from .datasource import DataSource
from .enums import CommissionType


class OrderSide(Enum):
    BUY = 1
    SELL = -1

class OrderType(Enum):
    MARKET = 0
    LIMIT = 1

class OrderStatus(Enum):
    ACTIVE = 0 ## Will go here if there is a stop loss or take profit
    COMPLETE = 1 ## Will go to this state if there are no more actions that can be done with the order
    PENDING = 2 ## Will be here when created, waiting for either the right price, or for time step

@dataclass
class Order:
    side: OrderSide
    quantity: np.float64
    type: OrderType
    price: np.float64 | None
    stop_loss: np.float64 | None
    take_profit: np.float64 | None
    status: OrderStatus
    timestamp: datetime


def same_sign(num1, num2):
    if (num1 > 0 and num2 > 0):
        return True
    elif (num1 < 0 and num2 < 0):
        return True
    return False

class Broker:
    def __init__(self, source: DataSource):
        self.position: np.float64 = np.float64(0)
        self.position_avg_price: np.float64 = np.float64(0)
        self.cash: np.float64 = np.float64(10_000)
        self.commision: np.float64 = np.float64(0.002)
        self.commision_type: CommissionType = CommissionType.PERCENTAGE
        self.lot_size: int = 1
        self.margin_call: float = 0.5 ## 50% of the cash value
        self.share_decimals = 1
        self.orders: list[Order] = []
        self.complete_orders = []
        self._i = 0
        self.source = source
        self.PnLRecord = np.full(len(self.source.data['Close']), self.cash, dtype=np.float64)

    @final
    def buy(self, quantity: float = 1, limit: np.float64 | None = None, amount: np.float64 | None = None, stop_loss: np.float64 | None = None, take_profit: np.float64 | None = None):
        ## Default to full account buy
        if (quantity > 1 or quantity <= 0):
            raise ValueError("Quantity must be between 0 and 1")
        if (limit and limit < 0):
            raise ValueError("Cannot have a negative limit price")
        if (amount and amount < 0):
            raise ValueError("Cannot have a negative amount!")
        if (limit):
            type = OrderType.LIMIT
        else:
            type = OrderType.MARKET
        current_price = self.source.Close[-1]
        total_shares = round((self.cash * quantity) / current_price, self.share_decimals)
        if (amount):
            total_shares = amount
        order = Order(
            side=OrderSide.BUY, 
            quantity=total_shares, 
            type=type,
            price=limit,
            stop_loss=stop_loss,
            take_profit=take_profit,
            status=OrderStatus.PENDING,
            timestamp=self.source.Index[self._i]
            )
        ## Transmit the order
        self.orders.append(order)
            

    @final
    def sell(self, quantity: float = 1, limit = None, amount: np.float64 | None = None, stop_loss: np.float64 | None = None, take_profit: np.float64 | None = None):
        ## Default to full account size sell
        if (quantity > 1 or quantity <= 0):
            raise ValueError("Quantity must be between 0 and 1")
        if (limit and limit < 0):
            raise ValueError("Cannot have a negative limit price")
        if (amount and amount < 0):
            raise ValueError("Cannot have a negative amount!")
        if (limit):
            type = OrderType.LIMIT
        else:
            type = OrderType.MARKET
        current_price = self.source.Close[-1]
        total_shares = round((self.cash * quantity) / current_price, self.share_decimals)
        if (amount):
            total_shares = amount
        order = Order(
            side=OrderSide.SELL, 
            quantity=total_shares, 
            type=type,
            price=limit,
            stop_loss=stop_loss,
            take_profit=take_profit,
            status=OrderStatus.PENDING,
            timestamp=self.source.Index[self._i]
            )
        ## Transmit the order
        self.orders.append(order)
    
    @final
    def close(self):
        ## Close active and complete positions
        if (self.position > 0):
            order = Order(
                side=OrderSide.SELL, 
                quantity=self.position, 
                type=OrderType.MARKET,
                price=None,
                stop_loss=None,
                take_profit=None,
                status=OrderStatus.PENDING,
                timestamp=self.source.Index[self._i]
                )
            self.orders.append(order)
        elif (self.position < 0):
            order = Order(
                side=OrderSide.BUY, 
                quantity=-self.position, 
                type=OrderType.MARKET,
                price=None,
                stop_loss=None,
                take_profit=None,
                status=OrderStatus.PENDING,
                timestamp=self.source.Index[self._i]
                )
            self.orders.append(order)

    def _debit(self, amount: np.float64): ## Give money to the market (buy shares)
        if (self.cash - amount < 0):
            ## Order fail
            raise ValueError("Tried to purchase more than account balance")
        self.cash -= amount

    def _credit(self, amount: np.float64): ## Take money from the market (sell shares)
        self.cash += amount
    

    def _calc_commission(self, quantity: np.float64, price: np.float64):
        if self.commision_type == CommissionType.CASH:
            debit = quantity * self.commision / self.lot_size
        else:
            debit = quantity * price * self.commision
        return debit

    def _apply_commission(self, quantity: np.float64, price: np.float64):
        debit = self._calc_commission(quantity, price)
        self._debit(debit)

    def _iterate(self, current_index: int):
        self._i = current_index
        to_delete = []
        ## Do one loop to see if you can execute any orders
        for order in self.orders:
            ## Check for new orders
            match order.status:
                case OrderStatus.PENDING:
                    if (order.type == OrderType.LIMIT):
                        if (order.side == OrderSide.BUY):
                            if (not order.price == None and self.source.COpen <= order.price):
                                ## We can buy it
                                old_pos = self.position
                                new_pos = old_pos + order.quantity
                                if (old_pos == 0):
                                    self.position_avg_price = order.price
                                elif same_sign(old_pos, new_pos):
                                    if (abs(new_pos) > abs(old_pos)):
                                        self.position_avg_price = (old_pos * self.position_avg_price + order.quantity * order.price) / new_pos
                                else:
                                    self.position_avg_price = order.price
                                self._debit(order.price * order.quantity)
                                self._apply_commission(order.quantity, order.price)
                                self.position = new_pos
                        else:
                            if (not order.price == None and self.source.COpen >= order.price):
                                ## We can sell it
                                old_pos = self.position
                                new_pos = old_pos - order.quantity
                                if (old_pos == 0):
                                    self.position_avg_price = order.price
                                elif same_sign(old_pos, new_pos):
                                    if (abs(new_pos) > abs(old_pos)):
                                        self.position_avg_price = (old_pos * self.position_avg_price + order.quantity * order.price) / new_pos
                                else:
                                    self.position_avg_price = order.price
                                self._credit(order.price * order.quantity)
                                self._apply_commission(order.quantity, order.price)
                                self.position = new_pos
                        if (order.stop_loss or order.take_profit):
                            order.status = OrderStatus.ACTIVE ## Will need to be checked on for each update
                        else:
                            order.status = OrderStatus.COMPLETE ## We are done with it
                            to_delete.append(order)
                    else:
                        try:
                            if (order.side == OrderSide.BUY):
                                old_pos = self.position
                                new_pos = old_pos + order.quantity
                                price = self.source.COpen
                                if (old_pos == 0):
                                    self.position_avg_price = price
                                elif same_sign(old_pos, new_pos):
                                    if (abs(new_pos) > abs(old_pos)):
                                        self.position_avg_price = (old_pos * self.position_avg_price + order.quantity * price) / new_pos
                                else:
                                    self.position_avg_price = price
                                self._debit(self.source.COpen * order.quantity)
                                self._apply_commission(order.quantity, self.source.COpen)
                                self.position = new_pos
                            else:
                                old_pos = self.position
                                new_pos = old_pos - order.quantity
                                price = self.source.COpen
                                if (old_pos == 0):
                                    self.position_avg_price = price
                                elif same_sign(old_pos, new_pos):
                                    if (abs(new_pos) > abs(old_pos)):
                                        self.position_avg_price = (old_pos * self.position_avg_price + order.quantity * price) / new_pos
                                else:
                                    self.position_avg_price = price
                                self._credit(self.source.COpen * order.quantity)
                                self._apply_commission(order.quantity, self.source.COpen)
                                self.position = new_pos
                            if (order.stop_loss or order.take_profit):
                                order.status = OrderStatus.ACTIVE
                            else:
                                order.status = OrderStatus.COMPLETE
                                self.complete_orders.append(order)
                                to_delete.append(order)
                        except:
                            pass
                case OrderStatus.ACTIVE:
                    if (
                        order.side == OrderSide.BUY 
                        and (
                            (order.take_profit and self.source.COpen >= order.take_profit)
                            or (order.stop_loss and self.source.COpen <= order.stop_loss)
                            )):
                            close_order = Order(
                                side=OrderSide.SELL, 
                                quantity=order.quantity, 
                                type=OrderType.MARKET, 
                                price= None, 
                                stop_loss= None, 
                                take_profit= None, 
                                status=OrderStatus.PENDING,
                                timestamp=self.source.Index[self._i]
                                )
                            self.orders.append(close_order)
                            order.status = OrderStatus.COMPLETE
                            self.complete_orders.append(order)
                            to_delete.append(order)
                    elif(order.side == OrderSide.SELL
                         and (
                             (order.take_profit and self.source.COpen <= order.take_profit) 
                             or (order.stop_loss and self.source.COpen >= order.stop_loss)
                             )):
                            close_order = Order(
                                side=OrderSide.BUY,
                                quantity=order.quantity,
                                type=OrderType.MARKET,
                                price=None,
                                stop_loss=None,
                                take_profit=None,
                                status=OrderStatus.PENDING,
                                timestamp=self.source.Index[self._i]
                            )
                            self.orders.append(close_order)
                            order.status = OrderStatus.COMPLETE
                            self.complete_orders.append(order)
                            to_delete.append(order)
        for item in to_delete:
            self.orders.remove(item)
        unrealized = self.position * self.source.CClose
        equity = self.cash + unrealized
        margin_call = self.margin_call * abs(self.position) * self.source.CClose
        if equity < margin_call and self.position < 0:
            self.close() ## Close all positions immediately, margin call
        self.PnLRecord[len(self.source.Close)] = equity