import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='3'
import re
import sys
import json

import tensorflow_hub as hub
import numpy as np
import tensorflow as tf
from tensorflow import keras
import tensorflow_text

import redis
import time

def sent(predictedSentiment):
    if np.argmax(predictedSentiment) == 0:
        return "Negative Sentiment"
    else:
        return "Positive Sentiment"
        

def main():

    use = hub.load("/src/universalEncoder")

    model = keras.models.load_model('my_model.h5')

    r = redis.Redis(host='sentiment-analysis-broker', port=6379)
    p = r.pubsub()

    p.subscribe('sentiment-request')

    print("loaded models")
    while True:
        message = p.get_message()
        if message:
            print(message)
            if message["type"] == "message":
                json_data = json.loads(bytes(message['data']).decode())
                emb_input = use([str(json_data['post'])])
                review_emb_input = tf.reshape(emb_input, [-1]).numpy()
                predictedSentiment = model.predict(emb_input)
                res_dict = {'clientId':str(json_data['clientId']), 'sentiment': sent(predictedSentiment)}
                r.publish('sentiment-reply', json.dumps(res_dict))
        time.sleep(0.001)


if __name__ == "__main__":
    main()
