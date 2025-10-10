from . import datacollector_ECB
from . import datacollector_ICE
from . import datacollector_Boliga
from . import datacollector_Business_insider
from . import datacollector_Entsoe
from . import datacollector_energidataservice
# from . import datacollector_trading_economics
from . import datacollector_Barchart


class ECB(datacollector_ECB.ECB):
    pass

class ICE(datacollector_ICE.ICE):
    pass

class Entsoe(datacollector_Entsoe.Entsoe):
    pass

class Boliga(datacollector_Boliga.Boliga):
    pass

class Business_insider(datacollector_Business_insider.Business_insider):
    pass

class Energidataservice(datacollector_energidataservice.Energidataservice):
    pass

# class Trading_economics(datacollector_trading_economics.Trading_economics):
#     pass

class Barchart(datacollector_Barchart.Barchart):
    pass

