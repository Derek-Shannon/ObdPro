import matplotlib.pyplot as plt
import pandas as pd

# Sample data
# data = {
#     'Timestamp': ['2024-09-16 21:32:09', '2024-09-16 21:32:10', '2024-09-16 21:32:11', 
#                   '2024-09-16 21:32:12', '2024-09-16 21:32:13', '2024-09-16 21:32:14'],
#     'Speed': [50, 55, 60, 65, 70, 75],
#     'Rpm': [2000, 2100, 2200, 2300, 2400, 2500],
#     'Engine_Load': [30, 35, 40, 45, 50, 55],
#     'Barometric_Pressure': [101.3, 101.2, 101.1, 101.0, 100.9, 100.8]
# }
f = open("output.txt", "r")
titles = f.readline()
titleList = str.split(titles," ")
titleList.pop()
while True:
    line = f.readline()
    if line is "":
        break
    lineList = str.split(line, " ")
    print(line)
print(titleList)
f.close()

# Load the .txt file
file_path = 'output.txt'
df = pd.read_csv(file_path, sep=' ')

# Rename the columns for easier access
df.columns = ['Day','Time', 'Speed', 'Rpm', 'Engine_Load', 'Barometric_Pressure', 'wt']
df = df.drop(columns=['wt'])

# Set the Timestamp column as the index (optional, useful for time-series data)
df.set_index('Time', inplace=True)

# Print the DataFrame to verify the content
print(df)

# Plot the data
plt.figure(figsize=(10,6))
plt.plot(df.index, df['Speed'], label='Speed (km/h or mph)', marker='o')
plt.plot(df.index, df['Rpm']/100, label='Rpm', marker='o')
plt.plot(df.index, df['Engine_Load'], label='Engine Load (%)', marker='o')
plt.plot(df.index, df['Barometric_Pressure'], label='Barometric Pressure (kPa)', marker='o')

# Ensure that we only consider numeric columns for min and max
numeric_df = df.select_dtypes(include='number')

# Now, set the y-axis limits based on numeric data
plt.ylim(numeric_df.min().min() - 5, numeric_df.max().max() + 5)

# Adding titles and labels
plt.title('Vehicle Parameters over Time')
plt.xlabel('Time')
plt.ylabel('Values')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# Show the plot
plt.show()