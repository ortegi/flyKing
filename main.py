import requests
import datetime
import random
from datetime import timedelta
import flag
import tweepy
import requests
from pyunsplash import PyUnsplash
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from dateutil import relativedelta
from dotenv import load_dotenv
import os

load_dotenv()

#API KEYS 

##tequila
api_key = os.getenv("API_KEY")
base_url = os.getenv('base_url')
##twepy
bearer_token  = os.getenv('bearer_token')
consumer_key  = os.getenv('consumer_key')
consumer_secret = os.getenv('consumer_secret')
access_token = os.getenv('access_token')
access_token_secret  = os.getenv('access_token_secret')
##unsplash
unsplash_key = os.getenv('unsplash_key')

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
  results = ''
  for option in response.json()['data'][:10]:
    precio = 0
    print("Ida:", option['cityFrom'], '-', option['cityTo'], 'Precio:', option['price'], curr[currency], 'Salida:', option['local_departure'])
    v = search(option['flyTo'], fly_from, (toDate(option['local_arrival']) + datetime.timedelta(days=delay)).strftime("%d/%m/%Y"), (toDate(option['local_arrival']) + datetime.timedelta(days=delay+3)).strftime("%d/%m/%Y"), currency)
    v = v.json()['data'][0]
    print("Vuelta:", v['cityFrom'], '-', v['cityTo'], 'Precio:', v['price'], curr[currency] , 'Salida:', v['local_departure'])
    precio = option['price'] + v['price']
    print('--------------------------------------')
    final = finalFly(fly_from, fly_to, datetime.datetime.strptime(option['local_departure'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime("%d/%m/%Y"), datetime.datetime.strptime(v['local_departure'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime("%d/%m/%Y"),  )
    link = final.json()['data'][0]['deep_link']
    print(link)
    print(option)
    print("Total", precio, currency)
    results = {'from': option['cityFrom'], 'to': option['cityTo'], 'price': precio, 'from_date': option['local_departure'], 'to_date': v['local_departure'], 'link': link, 'curr_sign': curr[currency], 'from_code': option['countryFrom']['code'], 'to_code': option['countryTo']['code'] }
    print()
  return results



codigos_FROM = [
    #España
    "MAD", "BCN", "VLC", "SVQ", "AGP", "BIO", "PMI", "LPA", "TFS", "TFN", "ALC",
    #LATAM
     "BOG", "CCS"
]


codigos_TO = [
    "LHR", "LGW", "STN", "MAN",   # Reino Unido
    "CDG", "ORY", "NCE",          # Francia
    "MAD", "BCN", "AGP", "VLC", "SVQ", "BIO", "PMI", "LPA", "TFS", "TFN", "ALC", # España
    "FCO", "MXP", "VCE",           # Italia
    "FRA", "MUC",                 # Alemania
    "AMS", "RTM",                  # Países Bajos
    "ZRH", "GVA",                  # Suiza
    "LIS", "OPO",                  # Portugal
    "ATH",                         # Grecia
    "IST",                         # Turquía
    "VIE",                         # Austria
    "BRU",                         # Bélgica
    "GOT",                         # Suecia
    "CPH",                         # Dinamarca
    "OSL",                         # Noruega
    "DUB",                         # Irlanda
    "HEL",                         # Finlandia
    "PRG",                         # República Checa                  
    "JFK", "LGA",                  # Nueva York
    "LAX",                         # Los Ángeles
    "MIA",                         #MIAMI
    "BOG",
    "CCS"
    
    ]


ciudades_europa = [
    "LHR", "LGW", "STN", "MAN",   
    "CDG", "ORY", "NCE", "MAD", "BCN", "AGP", "VLC", "SVQ", "BIO", "PMI", "LPA", "TFS", "TFN", "ALC",
    "FCO", "MXP", "VCE", "FRA", "MUC","AMS", "RTM", "ZRH", "GVA","LIS", "OPO", "ATH", "IST",                         
    "VIE", "BRU","GOT", "CPH","OSL","DUB","HEL", "PRG","MAD", "BCN", "VLC", "SVQ", "AGP", "BIO", "PMI", "LPA", "TFS", "TFN", "ALC"
]

ciudades_latinoamerica = [
    "CCS", "BOG"
]

ciudades_estados_unidos = [
    "JFK", "LGA",                  # Nueva York
    "LAX",                         # Los Ángeles
    "MIA"
]



def getContinent(code):
  if code in ciudades_europa:
    return 'Europe'
  elif code in ciudades_latinoamerica:
    return 'Latam'
  elif code in ciudades_estados_unidos:
    return 'NorthAmerica'

def getRandomDate():
  today = datetime.datetime.now()
  start_date = today + timedelta(days=40)
  end_date = start_date + timedelta(days=250)
  random_date = start_date + (end_date - start_date) * random.random()
  return random_date



def getCurrency(code):
  if code in ciudades_europa:
    return 'EUR'
  else:
    return 'USD'


#returns the differences between two STR DATES.
def getDiffBetweenDates(first_date, second_date):
  # Parse the dates from strings into datetime objects
  date1 = datetime.datetime.strptime(first_date, "%d/%m/%Y")
  date2 = datetime.datetime.strptime(second_date, "%d/%m/%Y")
  # Calculate the difference between the two dates
  difference = relativedelta.relativedelta(date1, date2)
  # Print the number of days between the two dates
  return abs(difference.days)




def getRandomFlight():
 #Get route - origin and destination from list of AIRPORT CODES. 
 from_random = codigos_FROM[random.randint(0, len(codigos_FROM) - 1)]
 to_random = codigos_TO[random.randint(0, len(codigos_TO) -1)]
 while to_random == from_random:
    to_random = codigos_TO[random.randint(0, len(codigos_TO) -1)]
    
 ##get date
 random_date = getRandomDate()
 date_from = random_date.strftime("%d/%m/%Y")
 date_to_raw = random_date + timedelta(days=2)
 date_to = date_to_raw.strftime("%d/%m/%Y")
 
 continent_from = getContinent(from_random)
 continent_to = getContinent(to_random)
 
 ## get duration of trip
 delay_trip = 0
 
 if continent_from == continent_to:
     delay_trip = 3
 else:
     delay_trip = 13
 

 #get continent of origin and destination --> so if we get different continets, the trip 
 #will be longer in days
 
 """
 if continent_to == continent_from:
   date_to_raw = random_date + timedelta(days=5)
 else:
  date_to_raw = random_date + timedelta(days=14)
  ##
  """

 currency = getCurrency(from_random)     #if origin is on LATAM currency is $

 return searchFlights(from_random, to_random, date_from, date_to, currency, delay_trip)  #CALL THE API
  #print(from_random, to_random, date_from, date_to, currency)


def getImage(city_origin, city_destiny, price, curr_sign, diff):
    
  base_url = 'https://api.unsplash.com/'
  params = {
      'query' : city_destiny,
      'orientation': 'landscape',
      'client_id': unsplash_key
  }
  image = ''
  image_sub = 'https://unsplash.com/photos/iiqpxCg2GD4/download?ixid=M3w0ODczODh8MHwxfGFsbHx8fHx8fHx8fDE2OTIwMjQ4ODl8'
  response = requests.get(base_url + 'search/photos',  params=params)
  json_response = response.json()
  if len(json_response['results']) >= 1:
    image = json_response['results'][0]['links']['download']

  
  response_img = requests.get(image, allow_redirects=True)
  
  if response_img.ok:
    open('./unsplash_temp.png', 'wb').write(response_img.content)
  else:
       response_img = requests.get(image_sub, allow_redirects=True)
       open('./unsplash_temp.png', 'wb').write(response_img.content)

  # Open the desired Image you want to add text on
  i = Image.open('plantilla.jpg')
  i2 = Image.open('./unsplash_temp.png')

  i2.thumbnail((800, 600))

  # To add 2D graphics in an image call draw Method
  back_im = i.copy()
  back_im.paste(i2, (70, 100))
  Im = ImageDraw.Draw(back_im)
  mf = ImageFont.truetype('font.ttf', 70)
  mx = ImageFont.truetype('jack.ttf', 70)
  mz = ImageFont.truetype('jack.ttf', 65)
 
   # Add Text to an image
  Im.text((100, 700), "{} - {} ".format(city_origin, city_destiny), (80, 81, 79), font=mf)
  Im.text((1250,500), "{} {}".format(price, curr_sign), (255,255,255), font=mf)
  Im.text((1000, 220), '{} días'.format(diff), (80, 81, 79), font=mx)
  Im.text((1000, 300), 'en {}!'.format(city_destiny), (80, 81, 79), font=mz)

  # Display edited image on which we have added the text
  i.show()
  # Save the image on which we have added the text
  back_im.save("mm.png")
  
  
def makeTwitterCode():
  flight_data = getRandomFlight()
  #print(flight_data)
  first_date = toDate(flight_data['from_date']).strftime("%d/%m/%Y")
  second_date = toDate(flight_data['to_date']).strftime("%d/%m/%Y")
  diff = getDiffBetweenDates(first_date, second_date)
  from_flag = flag.flag(flight_data['from_code'])
  to_flag = flag.flag(flight_data['to_code'])
  #getimage
  getImage(flight_data['from'],flight_data['to'], flight_data['price'], flight_data['curr_sign'], diff)
  twitt_text = "Vuelo ✈  {} {} - {} {}  \n Del {} al {} \n Por sólo {}{} 💸 \n Resérvalo ahora 😎: {}! \n #{} #{} #vuelos #vuelosbaratos #chollo #flight #cheap #holidays #vacaciones #travel #trip".format(flight_data['from'], from_flag, flight_data['to'], to_flag, first_date, second_date, flight_data['price'], flight_data['curr_sign'], flight_data['link'], flight_data['from'],  flight_data['to'])
  return twitt_text





# You can authenticate as your app with just your bearer token
client = tweepy.Client(bearer_token=bearer_token)

# You can provide the consumer key and secret with the access token and access
# token secret to authenticate as a user
client = tweepy.Client(
    consumer_key=consumer_key, consumer_secret=consumer_secret,
    access_token=access_token, access_token_secret=access_token_secret
)

##this is used by v1 api, lo use asi porque en v2 no encontrabamos como subir la img
auth=tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_token_secret)
api=tweepy.API(auth)

#mezclo las dos versiones, con v1 subo la img, y con v2 twitteo :)

image_path ='mm.png'


tweet = makeTwitterCode()
#print(tweet)
media = api.simple_upload(image_path)
client.create_tweet(text=tweet, media_ids=[media.media_id])  

  
