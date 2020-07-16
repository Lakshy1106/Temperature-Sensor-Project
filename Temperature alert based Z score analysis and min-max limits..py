import conf, json, time, math, statistics
from boltiot import Bolt

#--------------------------------------------------------------------------------------------------------------------

def compute_bounds(history_data,frame_size,factor):
    if len(history_data)<frame_size :
        return None

    if len(history_data)>frame_size :
        del history_data[0:len(history_data)-frame_size]

    Mn=statistics.mean(history_data)
    Variance=0

    for data in history_data :
        Variance += math.pow((data-Mn),2)

    Zn = factor * math.sqrt(Variance / frame_size)
    High_bound =history_data[frame_size-1]+Zn
    Low_bound =history_data[frame_size-1]-Zn
    return [High_bound,Low_bound]

def send_email():
    print("Making request to Mailgun to send an email")
    response = mailer.send_email("Alert", "The Current temperature value is out of desired range" +str(temperature))
    print("Response received from Mailgun is:" + response.text)

def sudden_change_email():
    print("Making request to Mailgun to send an email")
    response = mailer.send_email("Alert", "The temperature has changed suddenly" +str(temperature))
    print("Response received from Mailgun is:" + response.text)

#------------------------------------------------------------------------------------------------------------------------
mybolt = Bolt(conf.bolt_api_key, conf.device_id)
mailer = Email(conf.mailgun_key,conf.sandbox_url, conf.sender_email, conf.receiver_email)
minimum=71
maximum=153
history_data =[]
#-------------------------------------------------------------------------------------------------------------------------

while 1:
    response1 = mybolt.analogRead('A0')
    temp =json.loads(response1)
    response2 = mybolt.digitalRead('3')
    light = json.loads(response2)

    print ("The temperature right now is "+temp['value'])

    try:
        temp_value = int(temp['value'])
    except Exception as e:
        print(e)
        continue

    bound = compute_bounds(history_data,conf.frame_size,conf.multi_factor)
    
    if not temp_bound:
        required_data_count=conf.frame_size-len(history_data)
        print("Not enough data to compute Z-score. Need ",required_data_count," more data points")
        history_data.append(temp_value)
        continue
        
    if temp_value >bound[0] or temp_value < bound[1] :
        sudden_change_email()
    if temp_value< minimum or temp_value>maximum:
        send_email()

    history_data.append(temp_value)
    time.sleep(10)
