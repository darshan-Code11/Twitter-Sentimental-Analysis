import pandas as pd
import numpy as np

new_data = [
    {"id": 999901, "label": 0, "tweet": "I love this product! It is amazing!"},
    {"id": 999902, "label": 1, "tweet": "This is terrible. Worst experience ever."},
    {"id": 999903, "label": 0, "tweet": "The meeting is scheduled for 3 PM today."},
    {"id": 999904, "label": 1, "tweet": "Oh great, another Monday."},
    {"id": 999905, "label": 0, "tweet": "So happy today!!"},
    {"id": 999906, "label": 0, "tweet": "The food was good but service was terrible."},
    {"id": 999907, "label": 1, "tweet": "I HATE THIS SO MUCH"}
]

df = pd.read_csv('twitter.csv')
new_df = pd.DataFrame(new_data)
updated_df = pd.concat([df, new_df], ignore_index=True)
updated_df.to_csv('twitter.csv', index=False)
print(f"Added {len(new_data)} new examples to twitter.csv")
