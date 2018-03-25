import jwt
import datetime
import requests
import os
import json

def create_jwt(project_id, private_key_file, algorithm, file):
    
    token = {
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'aud': project_id
    }
	
    with open(private_key_file, 'r') as f: private_key = f.read()


    print('Creating JWT using {} from private key file {}\n'.format(algorithm, private_key_file))

    return jwt.encode(token, private_key, algorithm=algorithm)

def create_send_payload(token, file):
    
    file = open(file,"r")
    line = file.readline().split(" ")
    file.close()

    node = line[0]
    measurement = float(line[1])
    measurement = float("{0:.2f}".format(measurement))

    device_id = 'SOP_'+node
    url = 'https://cloudiotdevice.googleapis.com/v1/projects/broadcastapp-1119/locations/us-central1/registries/smart-city-registry/devices/'+device_id+':publishEvent'

    print('Creating payload using device {} and data: {}\n'.format(device_id, measurement))

    headers = {
        "Content-Type": "application/json",
	"Authorization": "Bearer " + token,
	"cache-control": "no-cache"
    }
    payload = "distance measurement: { measurement}"

    binary = payload.encode('base64')

    postData = {
	'binary_data' : binary
    }

    response = requests.post(url, headers=headers, data=json.dumps(postData))
    response.raise_for_status()
    print(response.status_code)
    return response.json()


project_id = 'broadcastapp-1119'
file = os.path.abspath('/home/pi/Desktop/Gateway/payload.txt')
algorithm = 'RS256'
private_key_file = '/home/pi/Desktop/Gateway/rsa_private.pem'

jwt_token = create_jwt(project_id, private_key_file, algorithm, file)
print(jwt_token+'\n')

response = create_send_payload(jwt_token, file)

print(response)
print("======================================================================================================\n")
