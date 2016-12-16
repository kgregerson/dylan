import abc
import numpy as np
from scipy.stats import binom, norm


class PricingEngine(object, metaclass=abc.ABCMeta):
    """
    An option pricing engine interface.

    """

    @abc.abstractmethod
    def calculate(self):
        """
        A method to implement an option pricing model.

        The pricing method may be either an analytic model (i.e. Black-Scholes or Heston) or
        a numerical method such as lattice methods or Monte Carlo simulation methods.

        """

        pass


class BinomialPricingEngine(PricingEngine):
    """
    A concrete PricingEngine class that implements the Binomial model.

    Args:
        

    Attributes:


    """

    def __init__(self, steps, pricer):
        self.__steps = steps
        self.__pricer = pricer

    @property
    def steps(self):
        return self.__steps

    @steps.setter
    def steps(self, new_steps):
        self.__steps = new_steps

    def calculate(self, option, data):
        return self.__pricer(self, option, data)


def EuropeanBinomialPricer(pricing_engine, option, data):
    """
    The binomial option pricing model for a plain vanilla European option.

    Args:
        pricing_engine (PricingEngine): a pricing method via the PricingEngine interface
        option (Payoff):                an option payoff via the Payoff interface
        data (MarketData):              a market data variable via the MarketData interface

    """

    expiry = option.expiry
    strike = option.strike
    (spot, rate, volatility, dividend) = data.get_data()
    steps = pricing_engine.steps
    nodes = steps + 1
    dt = expiry / steps 
    u = np.exp((rate * dt) + volatility * np.sqrt(dt)) 
    d = np.exp((rate * dt) - volatility * np.sqrt(dt))
    pu = (np.exp(rate * dt) - d) / (u - d)
    pd = 1 - pu
    disc = np.exp(-rate * expiry)
    spotT = 0.0
    payoffT = 0.0
    
    for i in range(nodes):
        spotT = spot * (u ** (steps - i)) * (d ** (i))
        payoffT += option.payoff(spotT)  * binom.pmf(steps - i, steps, pu)  
    price = disc * payoffT 
     
    return price 
    
class ControlVariateEngine(PricingEngine):
    def __init__(self, replications, time_steps, alpha, Vbar, xi, pricer):
        self.__replications = replications
        self.__time_steps = time_steps
        self.__pricer = pricer
        self.__alpha = alpha
        self.__Vbar = Vbar
        self.__xi = xi
        
    @property
    def replications(self):
        return self.__replications
    
    @replications.setter
    def replications(self, new_replications):
        self.__replications = new_replications
        
    @property
    def time_steps(self):
        return self.__time_steps
    
    @time_steps.setter
    def time_steps(self, new_time_steps):
        self.__time_steps = new_time_steps
    
    @property
    def alpha(self):
        return self.__alpha
    
    @alpha.setter
    def alpha(self, new_alpha):
        self.__alpha = new_alpha
    
    @property
    def Vbar(self):
        return self.__Vbar
    
    @Vbar.setter
    def Vbar(self, new_Vbar):
        self.__Vbar = new_Vbar
        
    @property
    def xi(self):
        return self.__xi
    
    @xi.setter
    def xi(self, new_xi):
        self.__xi = new_xi
    
    def calculate(self, option, data):
        return self.__pricer(self, option, data)


class MonteCarloPricingEngine(PricingEngine):
    """
    Doc string
    """

    def __init__(self, reps, steps, pricer):
        self.__reps = reps
        self.__steps = steps
        self.__pricer = pricer

    @property
    def reps(self):
        return self.__reps

    @reps.setter
    def reps(self, new_reps):
        self.__reps = new_reps

    @property
    def steps(self):
        return self.__steps

    @steps.setter
    def steps(self, new_steps):
        self.__steps = new_steps

    def calculate(self, option, data):
        return self.__pricer(self, option, data)


def NaiveMonteCarloPricer(pricing_engine, option, data):
    """
    Doc string
    """

    expiry = option.expiry
    strike = option.strike
    (spot, rate, volatility, dividend) = data.get_data()
    reps = pricing_engine.reps
    steps = pricing_engine.steps
    disc = np.exp(-rate * expiry)
    dt = expiry / steps

    nudt = (rate - dividend - 0.5 * volatility * volatility) * dt
    sigsdt = volatility * np.sqrt(dt)
    z = np.random.normal(size=reps)

    spotT = spot * np.exp(nudt + sigsdt * z)
    callT = option.payoff(spotT)

    return callT.mean() * disc


def BlackScholesDelta(St, t, K, T, sig, r, div):
    tau = T - t
    d1 = (np.log(St/K) + (r - div + 0.5 * sig * sig) * tau) / (sig * np.sqrt(tau))
    delta = np.exp(-div * tau) * norm.cdf(d1)
    return delta
    
def BlackScholesGamma(St, t, K, T, sig, r, div):
    tau = T - t
    d1 = (np.log(St/K) + (r - div + 0.5 * sig * sig) * tau) / (sig * np.sqrt(tau))
    gamma = np.exp(-div * tau ) * (norm.pdf(d1) / St * sig * np.sqrt(tau))
    return gamma
    
def BlackScholesVega(St, t, K, T, sig, r, div):
    tau = T - t
    d2 = (np.log(St / K) + (r - div - sig * sig * 0.5) * tau)/( sig * np.sqrt(tau))
    vega = K * np.exp(-r * tau) * norm.pdf(d2) * np.sqrt(tau)
    return vega
    
def ControlVariateMonteCarloPricer(pricing_engine, option, data):
    expiry = option.expiry
    strike = option.strike
    alpha = pricing_engine.alpha
    xi = pricing_engine.xi
    Vbar = pricing_engine.Vbar
    (spot, rate, volatility, dividend) = data.get_data()
    dt = expiry / pricing_engine.time_steps
    #nudt = (rate - dividend - 0.5 * volatility * volatility) * dt
    xisdt = xi * np.sqrt(dt)
    erddt = np.exp((rate - dividend) * dt)
    egam1 = np.exp(2*(rate-dividend)*dt)
    egam2 = -2*erddt+1
    eveg1 = np.exp(-alpha*dt)
    eveg2 = Vbar - Vbar *eveg1
    
    beta1 = -1
    beta2 = 1
    beta3 = 1
    
    payoff = np.zeros((pricing_engine.replications, ))
    price = 0.0

    for j in range(pricing_engine.replications):
        
        cv1 = 0
        cv2 = 0
        cv3 = 0
        
        s = np.zeros(pricing_engine.time_steps)
        v = np.zeros(pricing_engine.time_steps)
        s[0] = spot
        v[0] = Vbar
        z1 = np.random.normal(size=int(pricing_engine.time_steps))
        z2 = np.random.normal(size=int(pricing_engine.time_steps))
        
        for i in range(int(pricing_engine.time_steps)):
            t = (i-1) * dt
            delta = BlackScholesDelta(s[i], t, strike, expiry, volatility, rate, dividend)
            gamma = BlackScholesGamma(s[i], t, strike, expiry, volatility, rate, dividend)
            vega = BlackScholesVega(s[i], t, strike, expiry, volatility, rate, dividend)
            
            ##### Evolve Variance #####
            v[i] = v[i-1] + alpha * dt + (Vbar - v[i-1]) + xisdt * z1[i]
            if v[i] < 0.0: 
                v[i] = 0.0
        
            #####Evolve Asset Price #####
            s[i] = s[i-1] * np.exp((rate - 0.5 * v[i-1]) * dt + np.sqrt(v[i-1]) * np.sqrt(dt) * z2[i])
            
            ##### Accumulate Control Variates #####
            cv1 = cv1 + delta * (s[i] - s[i-1] * erddt)
            cv2 = cv2 + gamma * ((s[i] - s[i-1]) * (s[i] - s[i-1]) - s[i-1] * s[i-1] * (egam1 * np.exp(v[i-1]*dt) + egam2))
            cv3 = cv3 + vega * ((v[i]- v[i-1])-(v[i] * v[i] * eveg1 + eveg2 - v[i-1]))

        print(strike)
        strike = option.strike
        payoff[j] = option.payoff(strike, s)
        #payoff[j] = option.payoff(strike, s) + beta1 * cv1 + beta2 * cv3 + beta3 * cv3

    price = np.exp(-rate * expiry) * payoff.mean()
    #stderr = payoff.std() / np.sqrt(engine.replications)
    return price