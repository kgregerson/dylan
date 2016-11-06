from dylan.payoff import VanillaPayoff, call_payoff, put_payoff
from dylan.engine import BinomialPricingEngine, EuropeanBinomialPricer
from dylan.marketdata import MarketData
from dylan.option import Option

def main():
    spot = 41.0
    strike = 40.0
    rate = 0.08
    volatility = 0.30
    expiry = 1.0
    steps = 3
    dividend = 0.0

    the_call = VanillaPayoff(expiry, strike, call_payoff)
    the_bopm = BinomialPricingEngine(steps, EuropeanBinomialPricer)
    the_data = MarketData(rate, spot, volatility, dividend)

    the_option = Option(the_call, the_bopm, the_data)
    fmt = "The call option price is {0:0.3f}"
    print(fmt.format(the_option.price()))


if __name__ == "__main__":
    main()
