import os
from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="transformation-v1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

"""
filter_cols = ((sdf.contains("location-altitude")) & (sdf.contains("location-longitude")) & (sdf.contains("location-latitude")))
sdf = sdf[filter_cols]
sdf = sdf[["location-altitude", "location-longitude", "location-latitude"]]

cols = ["location-altitude", "location-longitude", "location-latitude"]
def check_if_cols_exist(values):
    return all([col in values for col in cols])
"""

if sdf.update(check_if_cols_exist):
    sdf = sdf[["location-altitude", "location-longitude", "location-latitude"]]
else:
    for col in cols:
        sdf[col] = None
    sdf = sdf[["location-altitude", "location-longitude", "location-latitude"]]


sdf.print(metadata=True)
sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run()


