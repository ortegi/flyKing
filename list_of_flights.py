import requests
import random
import os 
from dotenv import load_dotenv
import datetime
import tweepy

load_dotenv()

##twepy
bearer_token  = os.getenv('bearer_token')
consumer_key  = os.getenv('consumer_key')
consumer_secret = os.getenv('consumer_secret')
access_token = os.getenv('access_token')
access_token_secret  = os.getenv('access_token_secret')

#tequila
api_key = os.getenv("API_KEY")
base_url_2 = 'https://api.tequila.kiwi.com/'
base_url = os.getenv('base_url')


codigos_FROM = [
    #España
    "MAD", "BCN", "VLC", "SVQ", "AGP", "BIO", "PMI", "LPA", "TFS", "TFN", "ALC",
    #LATAM
     "BOG", "CCS"
]

def search(fly_from, fly_to, date_from, date_to, currency):

  headers = {
        'Content-type': 'application/json',
        'apikey': api_key
  }

  payload = {'fly_from': fly_from, 'fly_to': fly_to, 'date_from': date_from , 'date_to': date_to, 'locale': 'es', 'curr': currency, 'limit': 1}
  response = requests.get(base_url+"search/", headers=headers, params=payload)

  return response


def finalFly(fly_from, fly_to, departure, arrival):

  headers = {
        'Content-type': 'application/json',
        'apikey': api_key
  }

  payload = {'fly_from': fly_from, 'fly_to': fly_to, 'date_from': departure , 'date_to': departure,'return_from': arrival, 'return_to': arrival, 'locale': 'es', 'curr':'EUR'}
  response = requests.get(base_url+"search/", headers=headers, params=payload)
  return response


def toDate(date_str):
  return datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f%z')


def searchFlights(fly_from, fly_to, date_from, date_to, currency, delay):
    
  curr = {
      'EUR': '€',
      'USD': '$'
  }
  
  response = search(fly_from, fly_to, date_from, date_to, currency)
  print(fly_from, fly_to, date_from, date_to, currency)
  for option in response.json()['data'][:10]:
    precio = 0
    v = search(option['flyTo'], fly_from, (toDate(option['local_arrival']) + datetime.timedelta(days=delay)).strftime("%d/%m/%Y"), (toDate(option['local_arrival']) + datetime.timedelta(days=delay+3)).strftime("%d/%m/%Y"), currency)
    v = v.json()['data'][0]
    precio = option['price'] + v['price']
    final = finalFly(fly_from, fly_to, datetime.datetime.strptime(option['local_departure'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime("%d/%m/%Y"), datetime.datetime.strptime(v['local_departure'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime("%d/%m/%Y"),  )
    link = final.json()['data'][0]['deep_link']
    results = {'from': option['cityFrom'], 'to': option['cityTo'], 'price': precio, 'from_date': option['local_departure'], 'to_date': v['local_departure'], 'link': link, 'curr_sign': curr[currency], 'from_code': option['countryFrom']['code'], 'to_code': option['countryTo']['code'] }   
    return results

   


def  getTopDestinations(city_code):
  headers = {
        'Content-type': 'application/json',
        'apikey': api_key
  }
  
  payload = {
        'term': city_code,
        'limit': '20'
  }
  
  try:
      response = requests.get(base_url_2 + 'locations/topdestinations', headers=headers, params=payload)
      list_of_citys = []
      for item in response.json()['locations']:
            list_of_citys.append({'id': item['id'], 'continent': item['continent']['name']})
      
      return list_of_citys
  except:
        print('something went wrong on getTopDestinations')
    


def getDates():
  today = datetime.datetime.today()    
  #calculate next month
  next_month_date= today + datetime.timedelta(days=30)
  next_month = next_month_date.month
  preorigin = datetime.date(next_month_date.year, next_month, 1)
  origin = preorigin.strftime("%d/%m/%Y")
  pre_destiny = preorigin + datetime.timedelta(days=29)
  destiny = pre_destiny.strftime("%d/%m/%Y")
  return origin, destiny
  
  
  
def gettenRandomFlights():
      list_of_flights = []
      origin = codigos_FROM[random.randint(0, len(codigos_FROM)-1)]
      continent_origin = ''
      if origin == 'CCS' or origin =='BOG':
            continent_origin = 'America'
      else:
            continent_origin = 'Europe'
            
      destination = getTopDestinations(origin)
      first_date, second_date = getDates()
      try:
            for city in destination:
                  time_spent = 0
                  if city['continent'].lower() != continent_origin.lower():
                        time_spent = 14
                  else:
                        time_spent = 5
                  print('-')
                  print(origin, city['id'], first_date, second_date, 'EUR', time_spent)
                  results = searchFlights(origin, city['id'], first_date, second_date, 'EUR', time_spent)
                  list_of_flights.append(results)
            return list_of_flights, origin
      except:
            print('something went wrong on getRandomFligths')


def getCheapestFlights():
      da_list, origin = gettenRandomFlights()
      sorted_list = sorted(da_list, key=lambda x: x['price'])
      print(sorted_list)
      cheapest_flights = []
      for i in range(5):
            cheapest_flights.append(sorted_list[i])
      
      return cheapest_flights, origin




def getMonthFullName():
      months_spanish = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
      ]
      today = datetime.datetime.today()
      next_month_date= today + datetime.timedelta(days=30)
      return months_spanish[next_month_date.month - 1]



def getCityName(code):
 headers = {
        'Content-type': 'application/json',
        'apikey': api_key
    }
  
 payload = {
        'term': code,
        'limit': '1'
  }
 response = requests.get(base_url_2 + 'locations/query', headers=headers, params=payload)
 return response.json()['locations'][0]['city']['name']
 


def generateTweetText():
      cheapest_flights, origin = getCheapestFlights()
      print('cheapest-----------------------------')
      print(cheapest_flights)
      city_origin = getCityName(origin)
      month = getMonthFullName()
      twitt_text = """
      Los  4 vuelos 💰 más baratos desde {} en {}\n
      ✈{} {}{} {}\n
      ✈{} {}{} {}\n
      ✈{} {}{} {}\n
      ✈{} {}{} {}\n
      """.format(city_origin, month, cheapest_flights[0]['to'], cheapest_flights[0]['price'], cheapest_flights[0]['curr_sign'], cheapest_flights[0]['link'], cheapest_flights[1]['to'], cheapest_flights[1]['price'], cheapest_flights[1]['curr_sign'], cheapest_flights[1]['link'], cheapest_flights[2]['to'], cheapest_flights[2]['price'], cheapest_flights[2]['curr_sign'], cheapest_flights[2]['link'], cheapest_flights[3]['to'], cheapest_flights[3]['price'], cheapest_flights[3]['curr_sign'], cheapest_flights[3]['link']  )
      return twitt_text




# You can authenticate as your app with just your bearer token
client = tweepy.Client(bearer_token=bearer_token)

# You can provide the consumer key and secret with the access token and access
# token secret to authenticate as a user
client = tweepy.Client(
    consumer_key=consumer_key, consumer_secret=consumer_secret,
    access_token=access_token, access_token_secret=access_token_secret
)


tweet = generateTweetText()
#print(tweet)
client.create_tweet(text=tweet)  

  

  

