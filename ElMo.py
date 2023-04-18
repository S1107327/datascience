# import necessary libraries
import tensorflow_hub as hub
import tensorflow.compat.v1 as tf
import pandas as pd
import numpy as np

tf.disable_eager_execution()
dataset = pd.read_csv("example_dataset.csv")
# Load pre trained ELMo model
elmo = hub.Module("https://tfhub.dev/google/elmo/3", trainable=True)
embedded = elmo(dataset['no_dots'], signature="default", as_dict=True)
init = tf.global_variables_initializer()
sess = tf.Session()
sess.run(init)
embeddings = sess.run(embedded['default'])
print(embeddings)
print((len(embeddings[0])))