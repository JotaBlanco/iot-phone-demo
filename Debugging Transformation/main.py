import os
import copy
from quixstreams import Application, State
from datetime import timedelta
from scipy.spatial import ConvexHull
import numpy as np


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

# 
def calculate_hull_points(value:dict, state:State):
    # Get latest point coordinates
    latest_point = np.array([value["location-longitude"],value["location-latitude"]])
    print(latest_point)
    """

    # Update state
    current_points_array = state.get("position_points")
    if current_points_array is None:
        current_points_array = latest_point
    else:
        current_points_array = np.vstack((current_points_array, latest_point))
    
    # Calculate Convex Hull
    hull = ConvexHull(current_points_array)
    hull_vertices = current_points_array[hull.vertices]

    # Update state with Hull
    state.set('position_points', hull_vertices)

    # Create area col
    value["HullArea"] = hull.area

    """

sdf = sdf.update(calculate_hull_points, stateful=True)
sdf.print()

"""
# WINDOW
# location-altitude
sdf1 = sdf[["location-altitude"]]
sdf1 = (
    sdf1.apply(lambda value: value["location-altitude"])
    .sliding_window(duration_ms=timedelta(seconds=10)).mean().current()
    .apply(lambda result: {"mean_location_altitude": result["value"]})
)
sdf1.print()
print(sdf1.apply(lambda value: value["mean_location_altitude"]))


# location-longitude
sdf2 = sdf[["location-longitude"]]
sdf2 = (
    sdf2.apply(lambda value: value["location-longitude"])
    .sliding_window(duration_ms=timedelta(seconds=10))
    .mean()
    .current()
    .apply(lambda result: result["value"]) # Unwrap the aggregated result to match the expected output format
)
mean_location_longitude = sdf2.update(lambda value: print(value)) 
# location-latitude
sdf3 = sdf[["location-latitude"]]
sdf3 = (
    sdf3.apply(lambda value: value["location-latitude"])
    .sliding_window(duration_ms=timedelta(seconds=10))
    .mean()
    .current()
    .apply(lambda result: result["value"]) # Unwrap the aggregated result to match the expected output format
)
mean_location_latitude = sdf3.update(lambda value: print(value))
"""

sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run()


