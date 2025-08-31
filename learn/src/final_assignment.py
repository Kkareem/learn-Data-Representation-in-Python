# Assignment 4 Visualization
# Research Question:
# “How does the share of renewable energy in total energy consumption influence CO₂ emissions per capita across different countries and regions?”

import pandas as pd
import matplotlib.pyplot as plt

# Example dataset (selected countries with renewable share % and CO2 emissions per capita)
# In practice, you would replace this with actual CSV/Excel datasets (World Bank + IRENA)
data = {
    "Country": ["Norway", "Sweden", "Germany", "France", "USA",
                "China", "India", "Brazil", "Saudi Arabia", "South Africa"],
    "Renewable_Share": [67, 54, 20, 18, 12, 15, 22, 45, 1, 6],
    "CO2_per_capita": [6, 4, 8, 5, 15, 8, 2, 2.5, 18, 7]
}

# Create DataFrame
df = pd.DataFrame(data)

# Create scatter plot
plt.figure(figsize=(10,6))
plt.scatter(df["Renewable_Share"], df["CO2_per_capita"], color="green", alpha=0.7)

# Annotate countries for clarity
for i, row in df.iterrows():
    plt.text(row["Renewable_Share"]+0.5, row["CO2_per_capita"]+0.2,
             row["Country"], fontsize=9)

# Titles and labels
plt.title("CO₂ Emissions vs Renewable Energy Share (Selected Countries)", fontsize=14)
plt.xlabel("Renewable Energy Share (%)", fontsize=12)
plt.ylabel("CO₂ Emissions per Capita (metric tons)", fontsize=12)

# Grid for readability
plt.grid(True, linestyle="--", alpha=0.6)

# Save figure
plt.savefig("renewable_vs_co2.png")
plt.show()
