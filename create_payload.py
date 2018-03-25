#!/usr/bin/env python

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Python sample for connecting to Google Cloud IoT Core via HTTP, using JWT.
This example connects to Google Cloud IoT Core via HTTP, using a JWT for device
authentication. After connecting, by default the device publishes 100 messages
to the server at a rate of one per second, and then exits.
Before you run the sample, you must register your device as described in the
README in the parent folder.
"""

# [START iot_http_includes]
import base64
import datetime
import json
import time
import os

import jwt
import requests
# [END iot_http_includes]

# [START iot_http_jwt]
def create_jwt(project_id, private_key_file, algorithm):
    token = {
            # The time the token was issued.
            'iat': datetime.datetime.utcnow(),
            # Token expiration time.
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            # The audience field should always be set to the GCP project id.
            'aud': project_id
    }

    # Read the private key file.
    with open(private_key_file, 'r') as f:
        private_key = f.read()

    print('Creating JWT using {} from private key file {}'.format(
            algorithm, private_key_file))

    return jwt.encode(token, private_key, algorithm=algorithm).decode('ascii')
# [END iot_http_jwt]


# [START iot_http_publish]
def publish_message(
        message, base_url, project_id, cloud_region, registry_id,
        device_id, jwt_token):
    headers = {
            'authorization': 'Bearer {}'.format(jwt_token),
            'content-type': 'application/json',
            'cache-control': 'no-cache'
    }

    url_suffix = 'publishEvent'

    publish_url = (
        '{}/projects/{}/locations/{}/registries/{}/devices/{}:{}').format(
            base_url, project_id, cloud_region, registry_id, device_id,
            url_suffix)

    print('Publish url: {}'.format(publish_url))
    print(json.dumps(message))
    body = None
    msg_bytes = base64.urlsafe_b64encode(json.dumps(message))
    body = {'binary_data': msg_bytes.decode('ascii')}

    resp = requests.post(
            publish_url, data=json.dumps(body), headers=headers)

    if (resp.status_code != 200):
        print('Response came back {}'.format(resp.status_code))

    return resp
# [END iot_http_publish]


# [START iot_http_run]
def main():

    project_id = 'broadcastapp-1119'
    file = os.path.abspath('/home/pi/Desktop/RTFL_Gateway/payload.txt')
    algorithm = 'RS256'
    private_key_file = '/home/pi/Desktop/RTFL_Gateway/rsa_private.pem'

    jwt_token = create_jwt(
            project_id, private_key_file, algorithm)

    file = open(file,"r")
    line = file.readline().split(" ")
    file.close()

    node = line[0]
    measurement = float(line[1])
    measurement = float("{0:.2f}".format(measurement))

    device_id = 'SOP_'+node
    registry_id = 'smart-city-registry'
    cloud_region = 'us-central1'
    base_url = 'https://cloudiotdevice.googleapis.com/v1'

    print('Creating payload using device {} and data: {}\n'.format(device_id, measurement))
    payload = 'node: {} measurement: {} cm'.format(node, measurement)
    
    messageToSend = {
        "filled": 30, # int
        "position": [25.7701224,-80.36776989999998], # float array: lat, lng 
        "battery": 100, #int
        "lastseen": "" # you dont need this
    }
    print('Publishing message \'{}\''.format(payload))

    resp = publish_message(
        messageToSend, base_url, project_id, cloud_region, registry_id, device_id, jwt_token)

    print('HTTP response: ', resp)
    print('Finished.')
    print('=========================================================================================================\n')
# [END iot_http_run]

#Running the program
main()
