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

sdf1 = sdf[["location-altitude"]]
#sdf1.print(metadata=True)

sdf2 = sdf[["location-longitude"]]
#sdf2.print(metadata=True)

sdf3 = sdf[["location-latitude"]]
#sdf3.print(metadata=True)


# WINDOW
sdf1 = (
    sdf1.apply(lambda value: value["location-altitude"])
    .sliding_window(duration_ms=timedelta(seconds=10))
    .mean()
    .current()
    .apply(lambda result: result["value"]) # Unwrap the aggregated result to match the expected output format
)
print("sdf1")
sdf1.print()

sdf["new_col"] = 2
#sdf["avg_location-altitude"] = 
sdf1.update(lambda value: print(value))

"""
sdf2 = (
    sdf2.apply(lambda value: value["location-longitude"])
    .sliding_window(duration_ms=timedelta(seconds=10))
    .mean()
    .current()
    .apply(lambda result: result["value"]) # Unwrap the aggregated result to match the expected output format
)
print("sdf2")
sdf2.print()

sdf3 = (
    sdf3.apply(lambda value: value["location-latitude"])
    .sliding_window(duration_ms=timedelta(seconds=10))
    .mean()
    .current()
    .apply(lambda result: result["value"]) # Unwrap the aggregated result to match the expected output format
)
print("sdf3")
sdf3.print()
"""
#sdf.print()
sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run()


