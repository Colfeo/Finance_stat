import pandas as pd
df = pd.DataFrame.from_dict(
    {'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]}
)

df.to_excel('filename.xlsx')