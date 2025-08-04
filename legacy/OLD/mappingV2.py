import pandas as pd
import matplotlib.pyplot as plt

# Load the .txt file
file_path = 'output.txt'
df = pd.read_csv(file_path, sep=' ')

# Rename the columns for easier access
df.columns = ['Day','Time', 'Speed', 'Rpm', 'Engine_Load', 'Barometric_Pressure', 'wt']
df = df.drop(columns=['wt'])

# Create subplots (one for each parameter)
fig, axs = plt.subplots(4, 1, figsize=(10, 10), sharex=True)

# Plot 'Speed' with its own y-axis limits
axs[0].plot(df.index, df['Speed'], label='Speed (km/h or mph)', marker='o')
axs[0].set_ylim(df['Speed'].min() - 5, df['Speed'].max() + 5)
axs[0].set_ylabel('Speed')
axs[0].legend()
axs[0].grid(True)

# Plot 'Rpm' with its own y-axis limits
axs[1].plot(df.index, df['Rpm'], label='Rpm', marker='o', color='orange')
axs[1].set_ylim(df['Rpm'].min() - 5, df['Rpm'].max() + 5)
axs[1].set_ylabel('Rpm')
axs[1].legend()
axs[1].grid(True)

# Plot 'Engine_Load' with its own y-axis limits
axs[2].plot(df.index, df['Engine_Load'], label='Engine Load (%)', marker='o', color='green')
axs[2].set_ylim(df['Engine_Load'].min() - 5, df['Engine_Load'].max() + 5)
axs[2].set_ylabel('Engine Load')
axs[2].legend()
axs[2].grid(True)

# Plot 'Barometric_Pressure' with its own y-axis limits
axs[3].plot(df.index, df['Barometric_Pressure'], label='Barometric Pressure (kPa)', marker='o', color='red')
axs[3].set_ylim(df['Barometric_Pressure'].min() - 5, df['Barometric_Pressure'].max() + 5)
axs[3].set_ylabel('Pressure')
axs[3].legend()
axs[3].grid(True)

# Adding common labels and titles
plt.xlabel('Timestamp')
plt.xticks(rotation=45)
plt.tight_layout()

# Show the plot
plt.show()