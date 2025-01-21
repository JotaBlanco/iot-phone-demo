import os
from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="transformation-v1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)
cols = ["location-altitude", "location-longitude", "location-latitude"]

def check_if_cols_exist(value):
    return all([col in value for col in cols])

if sdf.update(check_if_cols_exist):
    sdf = sdf[cols]
else:
    for col in cols:
        sdf[col] = None

sdf.print(metadata=True)
sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run()