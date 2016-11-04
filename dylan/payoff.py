import abc
from numpy import maximum

class Payoff(object, metaclass=abc.ABCMeta):
    """
    An abstract base class for option payoffs
    """

    @property 
    @abc.abstractmethod
    def expiry(self):
        pass

    @expiry.setter
    @abc.abstractmethod
    def expiry(self):
        pass

    @abc.abstractmethod
    def payoff(self):
        pass


class VanillaPayoff(Payoff):
    """
     

    Args:
        expiry (float):    the option's expiration date.
        strike (int):      the option's strike price.
        payoff (function): the option's payoff function 
    """

    def __init__(self, expiry, strike, payoff):
        self.__expiry = expiry
        self.__strike = strike
        self.__payoff = payoff

    @property
    def expiry(self):
        return self.__expiry

    @expiry.setter
    def expiry(self, new_expiry):
        self.__expiry = new_expiry

    @property
    def strike(self):
        return self__strike

    @strike.setter
    def strike(self, new_strike):
        self.__strike = new_strike

    def payoff(self, spot):
        return self.__payoff(self, spot)

def call_payoff(option, spot):
    return maximum(spot - option.strike, 0.0)

def put_payoff(option, spot):
    return maximum(option.strike - spot, 0.0)


