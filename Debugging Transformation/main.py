import os
import copy
from quixstreams import Application, State
from datetime import timedelta
from scipy.spatial import ConvexHull
import numpy as np


# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="transformation-v1.1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

# ROBUSTLY select columns
filter_cols = ((sdf.contains("location-altitude")) & (sdf.contains("location-longitude")) & (sdf.contains("location-latitude")))
sdf = sdf[filter_cols]
sdf = sdf[["location-altitude", "location-longitude", "location-latitude"]]


# Smooth coordinates
def coordinates_smoother(window: dict):
    values = window["value"]
    new_row = values[-1]
    #print(map(lambda row: row["location-longitude"], values))
    #new_row["median-location-longitude"] = np.median(map(lambda row: row["location-longitude"], values))
    #new_row["median-location-latitude"] = np.median(map(lambda row: row["location-latitude"], values))
    new_row["median-location-longitude"] = float(np.median(list(map(lambda row: row["location-longitude"], values))))
    new_row["median-location-latitude"] = float(np.median(list(map(lambda row: row["location-latitude"], values))))
    #new_row["mean-location-longitude"] = sum(map(lambda row: row["location-longitude"], values)) / len(values)
    #new_row["mean-location-latitude"] = sum(map(lambda row: row["location-latitude"], values)) / len(values)
    return new_row


# Calculate hull points
def calculate_hull_points(value:dict, state:State):
    # Get latest point coordinates
    #latest_point = np.array([value["mean-location-longitude"], value["mean-location-latitude"]])  
    latest_point = np.array([value["median-location-longitude"], value["median-location-latitude"]])  

    # Update state
    current_points = state.get("position_points")
    new_points = latest_point if current_points is None else np.vstack((np.array(current_points), latest_point))
    
    # Calculate Convex Hull
    if len(new_points) > 3:
        try:
            hull = ConvexHull(new_points)
            new_points = new_points[hull.vertices]
            value["HullArea"] = hull.area  # Create area col
            value["HullPoints"] = new_points.tolist()
        except:
            print("Hasn't worked")

    # Update state with Hull
    state.set('position_points', new_points.tolist())



sdf = sdf.sliding_window(10*10**3).collect().final().apply(coordinates_smoother)
sdf = sdf.update(calculate_hull_points, stateful=True)
sdf.print()
sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run()


