import conf, json, time
from boltiot import Bolt,Email

#Setting up device
device = Bolt(conf.api_key, conf.device_id)

minimum = 71.68 
maximum = 153.6

mailer = Email(conf.mailgun_key,conf.sandbox_url, conf.sender_email, conf.receiver_email)

while 1: 
    print ("Reading sensor value")
    response = device.analogRead('A0') 
    data = json.loads(response) 
    print ("Sensor value is: " + str(data['value']))
    try: 
        sensor_value = int(data['value'])
        temperature=(100*sensor_value)/1024 
    except Exception as e: 
        print ("Error occured: details are")
        print (e)
        
    if sensor_value > maximum or sensor_value < minimum:
            print("Making request to Mailgun to send an email")
            response = mailer.send_email("Alert", "The Current temperature value is out of desired range" +str(temperature))
            print("Response received from Mailgun is:" + response.text)
    time.sleep(10)
