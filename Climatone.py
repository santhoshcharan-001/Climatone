import requests
from time import sleep

url = """https://api.telegram.org/[YOUR_TELEGRAM_BOT_API_KEY]/"""
weather_api = "[YOUR_WEATHER_API_KEY]"

def get_chat_id(update):
    chat_id = update['message']['chat']['id']
    return chat_id

def get_weather_using_loc(loc):
    latitude = loc[0]
    longitude = loc[1]
    base_url = "https://api.openweathermap.org/data/2.5/weather?units=metric&lat={0}&lon={1}&appid={2}".format(latitude,longitude,weather_api) 
    response = requests.get(base_url)
    result = response.json()
    return result

def get_weather_city(city):
    base_url = "https://api.openweathermap.org/data/2.5/weather?units=metric&q={0}&appid={1}".format(city,weather_api)
    response = requests.get(base_url)
    result = response.json()
    return result

def send_location_msg(location,chat_id):
    send_message(chat_id,"Weather : " + location["weather"][0]["main"])
    send_message(chat_id,"City : " + location["name"])
    send_message(chat_id,"description : " + location["weather"][0]["description"])
    d = location["main"]
    for i in d.keys():
        if(i in ["temp" , "temp_min" , "temp_max" , "feels_like"]):
            send_message(chat_id,i + " : " + str(d[i]) + " °C")
        elif(i in ["humidity"]):
            send_message(chat_id,i + " : " + str(d[i]) + " %")
        elif(i in ["pressure" , "sea_level" , "grnd_level"]):
            send_message(chat_id,i + " : " + str(d[i]) + " hPa")
        else:
            send_message(chat_id,i + " : " + str(d[i]))
        

def get_message_loc(update):
    latitude = update["message"]["location"]["latitude"]
    longitude = update["message"]["location"]["longitude"]
    loc = (latitude,longitude)
    return get_weather_using_loc(loc)

def get_message_text(update):
    message_text = update['message']['text']
    return message_text

def last_update(req):
    response = requests.get(req + "getUpdates")
    response = response.json()
    result = response['result']
    total_updates = len(result) - 1
    return result[total_updates]

def send_message(chat_id,message_text):
    params = {'chat_id' : chat_id , 'text' : message_text}
    response = requests.post(url + 'sendMessage' , data=params)
    return response

def main():
    update_id = last_update(url)['update_id']
    while True:
        print("Sending Requests...")
        update = last_update(url)
        if(update_id == update['update_id']):
            try:
                location = get_message_loc(update)
                send_location_msg(location,get_chat_id(update))
            except:
                try:
                    msg = get_message_text(update).lower()
                    if(msg == "/start"):
                        send_message(get_chat_id(update) , "Hello " + update["message"]["from"]["first_name"])
                        send_message(get_chat_id(update) , "This bot can give you the complete weather details of any city.")
                        send_message(get_chat_id(update) , "Just send your location or type /help for more commands.")
                    elif(msg == "/help"):
                        send_message(get_chat_id(update) , "Type /city cityname ,replace cityname with cityname you want to get the details")
                    
                    elif(msg.startswith("/city")):
                        try:
                            location = get_weather_city(" ".join(msg.split(" ")[1:]))
                            send_location_msg(location,get_chat_id(update))
                        except:
                            send_message(get_chat_id(update) , "City not found")
                    else:
                        send_message(get_chat_id(update) , "No command found")  
                except:
                    send_message(get_chat_id(update) , "Only Text and location formats are Supported")
            update_id += 1

main()
