import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

print("Mock Analysis Insights:")
print("- Revenue is trending upwards.")
print("- Widgets are the top-selling category.")

# Create a mock plot
plt.figure(figsize=(8, 6))
plt.plot([1, 2, 3], [10, 20, 30])
plt.title("Mock Sales Trend")
plt.xlabel("Time")
plt.ylabel("Sales")
os.makedirs('data_detective/test_output', exist_ok=True)
plt.savefig('data_detective/test_output/sales_trend.png')
print("Generated plot at data_detective/test_output/sales_trend.png")