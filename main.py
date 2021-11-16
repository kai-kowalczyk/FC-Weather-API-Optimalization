import sys
import requests
import json
from pathlib import Path

class WeatherForecast:

    BASE_URL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline'

    def __init__(self, api_key):
        self.api_key = api_key
        self.location = 'Warsaw'
        self.logs = 'weather_logs.json'
        self.date = None
        self.precip = None
        self.rain_chance = None
        self.info = None
        self.known_weather_data = self.get_data_from_file()

    def check_if_file_exists(self):
        file_ex = Path(self.logs).exists()
        return file_ex
    
    def get_data_from_file(self):
        if self.check_if_file_exists() == True:
            with open(self.logs) as weather_data:
                    data = json.load(weather_data)
                    return data
        else:
            print("Brak zapisanych w pliku danych pogodowych.")

    def check_if_data_known(self):
        if self.check_if_file_exists() == True:
            if self.date in self.known_weather_data.keys():
                print(self.known_weather_data[self.date])
                return True
            else:
                return False
        else:
            return False

    def get_info(self):
        if self.check_if_data_known() == False:
            self.url_parameters = '&include=current&elements=precip,datetime,precipprob&unitGroup=metric'
            request_url = f'{self.BASE_URL}/{self.location}/{self.date}?key={self.api_key}{self.url_parameters}'
            r = requests.get(request_url)
            self.info = r.json()   
        else:
            quit()
        self.get_precip_info()

    def get_precip_info(self):
        self.precip = float(self.info['days'][0]['precip'])
        return self.get_rain_chance(self.precip)

    def get_rain_chance(self, precip):
        if precip == 0.0:
            self.rain_chance = 'Nie będzie padać.'
        elif precip > 0.0:
            self.rain_chance = 'Będzie padać.'
        else:
            self.rain_chance = 'Nie wiem.'
        self.save_data_to_file()

    def save_data_to_file(self):
        self.known_weather_data[self.date] = self.rain_chance
        with open(self.logs) as weather_data:
            data = json.load(weather_data)
        
        new_data = {self.date: self.rain_chance}
        data.update(new_data)

        with open(self.logs, 'w') as weather_data:
            json.dump(data, weather_data)


    def __iter__(self):
        for date in self.known_weather_data.keys():
            yield date

    def __getitem__(self, key):
        if key not in self.known_weather_data:
            self.get_info()
            return self.known_weather_data[key]
        else:
            return self.known_weather_data[key]

    def items(self):
        for date, precip_info in self.known_weather_data.items():
            yield (date, precip_info)



wf = WeatherForecast(api_key=sys.argv[1])

if len(sys.argv) == 2:
    mode = input('Podaj komendę. "daty": by dowiedziec się dla jakich dat zapisane są juz dane pogodowe. "dane": by wypisać wszystkie zapisane pary data-pogoda.\n')
    if mode == 'daty':
        for date in wf:
            print(date)
    elif mode == 'dane':
        for data in wf.items():
            print(data)
    else:
        print('Wprowadzono błędną komendę.')
        quit()
elif len(sys.argv) == 3:
    wf.date = sys.argv[2]
    print(wf[sys.argv[2]])
