import sys
import os
import base64
import hmac
import hashlib
import time
import requests
import json
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv(), override=True)

# ACRCloud config
host = os.environ.get('ACRCLOUD_HOST')
access_key = os.environ.get('ACRCLOUD_ACCESS_KEY')
access_secret = os.environ.get('ACRCLOUD_SECRET_KEY')

# Signature hash
http_method = "POST"
http_uri = "/v1/identify"
data_type = "audio"
signature_version = "1"
timestamp = time.time()

string_to_sign = "{0}\n{1}\n{2}\n{3}\n{4}\n{5}".format(
    http_method,
    http_uri,
    access_key,
    data_type,
    signature_version,
    str(timestamp)
)

hmac_res = hmac.new(
    access_secret.encode('ascii'),
    string_to_sign.encode('ascii'),
    digestmod=hashlib.sha1
).digest()

sign = base64.b64encode(hmac_res).decode('ascii')

''' Recognize '''
def recognize(clip_url):
    # FB request audio in bytes
    clip_request = requests.get(clip_url)
    sample = clip_request.content
    sample_bytes = len(sample)

    # ACR request
    multipart_form_data = {
        'access_key': access_key,
        'sample_bytes': str(sample_bytes),
        'sample': sample,
        'signature': sign,
        'timestamp': str(timestamp),
        'data_type': data_type,
        "signature_version": signature_version
    }

    acr_request = requests.post(host, files=multipart_form_data)
    return json.loads(acr_request.text)
