import os
from quixstreams import Application
from datetime import timedelta

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="transformation-v1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

# ROBUSTLY select columns
filter_cols = ((sdf.contains("location-altitude")) & (sdf.contains("location-longitude")) & (sdf.contains("location-latitude")))
sdf = sdf[filter_cols]
sdf = sdf[["location-altitude", "location-longitude", "location-latitude"]]
sdf.print(metadata=True)

# WINDOW
sdf = (
    sdf.apply(lambda value: value["location-altitude"])
    .sliding_window(duration_ms=timedelta(seconds=10))
    .mean()
    .current()
    # Unwrap the aggregated result to match the expected output format
    .apply(lambda result: result["value"])
)

sdf.print()
sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run()


