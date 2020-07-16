import conf, json, time, math, statistics
from boltiot import Bolt

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
    High_bound = history_data[frame_size-1]+Zn
    Low_bound = history_data[frame_size-1]-Zn
    return [High_bound,Low_bound]

mybolt = Bolt(conf.bolt_api_key, conf.device_id)

history_data=[]

while 1:
    response = mybolt.analogRead('A0')
    data = json.loads(response)
    if data['success'] != 1:
        print("There is an error:"+data['value'])
        time.sleep(10)
        continue

    sensor_value=0
    try:
        sensor_value = int(data['value'])
    except Exception as e:
        print("There was an error while parsing the response: ",e)
        continue
    temperature = sensor_value/10.24
    print ("The temperature right now is ", temperature, "degree celsius")
    bound = compute_bounds(history_data,conf.frame_size,conf.multi_factor)

    if not bound:
        required_data_count=conf.frame_size-len(history_data)
        print("Not enough data to compute Z-score. Need ",required_data_count," more data points")
        history_data.append(int(data['value']))
        time.sleep(30)
        continue

    try:
        if sensor_value > bound[0] :
            print ("The temperature has risen suddenly.")
            response = mybolt.digitalWrite("1",'HIGH')
            time.sleep(5)
            response = mybolt.digitalWrite("1",'LOW')
            print(response)
        if sensor_value < bound[1]:
            print ("The temperature has decreased suddenly.")
            response = mybolt.digitalWrite("3",'HIGH')
            time.sleep(5)
            response = mybolt.digitalWrite("3",'LOW')
            print(response)
            
        history_data.append(sensor_value)
    except Exception as e:
        print ("Error",e)
    time.sleep(30)
