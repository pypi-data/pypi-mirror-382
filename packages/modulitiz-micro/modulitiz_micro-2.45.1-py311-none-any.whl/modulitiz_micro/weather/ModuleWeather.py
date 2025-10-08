from modulitiz_micro.weather.AbstractModuleWeather import AbstractModuleWeather
from modulitiz_nano.ModuloDate import ModuloDate
from modulitiz_nano.ModuloListe import ModuloListe


class ModuleWeather(AbstractModuleWeather):
	"""
	Utility for current weather and forecasts.
	"""
	OPTIONS="lang=it&units=metric"
	KEY="appid=e28cd365c35c12e3ed8f2d84e04398c9"
	
	__BASE_URL="https://api.openweathermap.org"
	URL_CURRENT=__BASE_URL+f"/data/2.5/weather?{OPTIONS}&{KEY}&q="
	URL_FORECAST=__BASE_URL+f"/data/2.5/forecast?{OPTIONS}&{KEY}&q="
	
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
	
	def getCurrent(self,city:str,codState:str)-> dict:
		return self._makeGenericRequest(self.URL_CURRENT,city,codState)
	
	def getForecastRainUntilTomorrow(self,city:str,codState:str)-> list|None:
		"""
		Chiede le previsioni fino al giorno dopo e mostra solo i risultati che dicono che pioverà.
		"""
		now=ModuloDate.now()
		tomorrow=ModuloDate.setEndOfDay(ModuloDate.plusMinusDays(now,1))
		hoursDiff=ModuloDate.hoursDiff(tomorrow, now)
		elements=self.__getForecasts(city, codState,True,None,hoursDiff)
		if elements is None:
			return None
		# filter elements
		results=[]
		for elem in elements:
			if ModuloListe.collectionSafeGet(elem,'rain') is not None:
				results.append(elem)
		return results
	
	def __getForecasts(self,city:str,codState:str,includeFirstForecast:bool,stepHours: int|None,maxHours:int)-> list|None:
		results=self._makeForecastRequest(self.URL_FORECAST,city,codState)
		maxLista=len(results)
		# calculate indexes
		if maxHours is not None:
			maxInd=int(maxHours/3)+1
			if maxInd>=maxLista:
				maxInd=maxLista-1
		else:
			maxInd=maxLista-1
		if stepHours is None:
			step=1
		else:
			step=int(stepHours/3)
		inds=list(range(4,maxInd,step))
		if includeFirstForecast:
			inds.insert(0,1)
		# process json
		output=[]
		for ind in inds:
			elem=results[ind]
			output.append(elem)
		return output
