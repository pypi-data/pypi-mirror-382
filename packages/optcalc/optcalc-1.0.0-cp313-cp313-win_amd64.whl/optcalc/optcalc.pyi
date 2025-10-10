"""Stubs för optcalc – Black–Scholes C-extension"""


def getCallArr() -> list[float]:
    ''' vektor med köpoptionspriser'''
    ...

def getPutArr() -> list[float]:
    ''' vektor med säljoptionspriser'''
    ...

def set_params(asset: float, strike: float, maturity: int, volatility: float, interest: float) -> None:

    '''parametrar till Black & choles'''
    ...

def genOptionSer() -> None:
    ''' genererar optionspriser över alla löptider fram till lösen'''
    ...

def getInfo() -> None:
    ''' genererar optionspriser över alla löptider fram till lösen'''
    ...


