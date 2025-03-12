import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import os

# Path to the .xlsx file
file_path = 'sugarbeetstats.xlsx'

# Read the file
df = pd.read_excel(file_path)

# Display the statistics for the different categories
years = ['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023']
area_stats = df.iloc[0]
yield_stats = df.iloc[1]
volume_stats = df.iloc[2]
value_stats = df.iloc[3]
sugar_stats = df.iloc[4]
price_stats = df.iloc[5]

# Function that converts the statistics to lists
def convert_to_list(stats):
    stats_list = []
    for value in stats:
        stats_list.append(value)
    stats_list.pop(0)
    return stats_list

# Convert the statistics to lists
area_list = convert_to_list(area_stats)
yield_list = convert_to_list(yield_stats)
volume_list = convert_to_list(volume_stats)
value_list = convert_to_list(value_stats)
sugar_list = convert_to_list(sugar_stats)
price_list = convert_to_list(price_stats)
value_per_area_list = [value_list[i] / area_list[i] for i in range(len(area_list))]


# Function that shows a line chart for the statistics
# Function that shows a line chart for the statistics
def line_chart(title, x_label, y_label, data, color):
    plt.figure()
    plt.plot(years, data, marker='o', color=color)
    plt.grid(True)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    # Save figure instead of showing
    filename = title.replace(' ', '_').lower() + '.png'
    plt.savefig(os.path.join('figures', filename), dpi=300, bbox_inches='tight')
    plt.close()

# Color dictionary for the graphs
colors = {
    'Area': 'blue',
    'Yield': 'green',
    'Volume': 'red',
    'Value': 'purple',
    'Sugar': 'orange',
    'Price': 'brown'
}

# Show the line charts
line_chart('Volume of Harvested production', 'Year', 'Volume (thousand tonnes)', volume_list, colors['Volume'])
line_chart('Value of Production', 'Year', 'Value (£ million)', value_list, colors['Value'])
line_chart('Average Market Price', 'Year', 'Price (£ per adjusted tonne)', price_list, colors['Price'])
line_chart('Yield per hectare', 'Year', 'Yield (tonnes per hectare)', yield_list, colors['Yield'])
line_chart('Area Harvested', 'Year', 'Area (hectares)', area_list, colors['Area'])


# Combine all lists into a DataFrame
data = {
    'Area': area_list,
    'Yield': yield_list,
    'Volume': volume_list,
    'Value': value_list,
    'Sugar': sugar_list,
    'Price': price_list
}
df_stats = pd.DataFrame(data, index=years)

# Calculate the correlation matrix
corr = df_stats.corr()

# Generate a heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Correlation Heatmap of Sugar Beet Statistics')
plt.savefig(os.path.join('figures', 'correlation_heatmap.png'), dpi=300, bbox_inches='tight')
plt.close()

# Create a scatter plot to show correlation between yield and market price
def scatter_correlation_plot(x_data, y_data, x_label, y_label, title, color):
    plt.figure(figsize=(10, 6))
    plt.scatter(x_data, y_data, color=color, alpha=0.8, s=100)
    
    # Calculate correlation coefficient
    correlation = np.corrcoef(x_data, y_data)[0, 1]
    
    # Add correlation text
    plt.annotate(f'Correlation: {correlation:.2f}', 
                 xy=(0.05, 0.95), xycoords='axes fraction',
                 fontsize=12, ha='left', va='top',
                 bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.7))
    
    # Add regression line
    z = np.polyfit(x_data, y_data, 1)
    p = np.poly1d(z)
    plt.plot(x_data, p(x_data), "r-", alpha=0.7, linewidth=2)
    
    # Add year labels to each point
    for i, year in enumerate(years):
        plt.annotate(year, (x_data[i], y_data[i]), 
                    textcoords="offset points", 
                    xytext=(0,10), 
                    ha='center')
    
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.tight_layout()
    # Save figure instead of showing
    filename = title.replace(' ', '_').lower() + '.png'
    plt.savefig(os.path.join('figures', filename), dpi=300, bbox_inches='tight')
    plt.close()

# Create scatter plot for yield vs value
scatter_correlation_plot(
    yield_list, 
    value_list, 
    'Yield (tonnes per hectare)', 
    'Value (£ million)',
    'Correlation between Yield and Value of Production',
    colors['Yield']
)

# Create scatter plot for yield vs value per area
scatter_correlation_plot(
    yield_list,
    value_per_area_list,
    'Yield (tonnes per hectare)',
    'Value per Area (£ million per hectare)',
    'Correlation between Yield and Value per Area',
    colors['Yield']
)

# Create a comparison of yield before and after the ban
pre_ban_years = years[0:5]  # 2014-2018
post_ban_years = years[5:7]  # 2019-2020

# Calculate average yields for each period
pre_ban_yield = np.mean([yield_list[years.index(year)] for year in pre_ban_years])
post_ban_yield = np.mean([yield_list[years.index(year)] for year in post_ban_years])

# Create bar chart to visualize difference
plt.figure(figsize=(8, 6))
bars = plt.bar([0, 1], [pre_ban_yield, post_ban_yield], width=0.3, color=[colors['Yield'], 'darkgreen'])
plt.xticks([0, 1], ['2014-2018\n(Pre-Ban)', '2019-2020\n(Post-Ban)'])
plt.ylabel('Average Yield (tonnes per hectare)')
plt.title('Comparison of Sugar Beet Yield Before and After Ban')

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
            f'{height:.2f}', ha='center', va='bottom')

# Calculate percent change
percent_change = ((post_ban_yield - pre_ban_yield) / pre_ban_yield) * 100
change_text = f"Change: {percent_change:.1f}%"
plt.annotate(change_text, 
             xy=(0.99, 0.98),  # Position in top right
             xycoords='axes fraction',  # Use axes fraction coordinates
             ha='right',  # Right-align text
             va='top',  # Align to top
             bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7))

# Add individual year data points
plt.scatter([0]*len(pre_ban_years) + [1]*len(post_ban_years),
           [yield_list[years.index(year)] for year in pre_ban_years] + 
           [yield_list[years.index(year)] for year in post_ban_years],
           color='black', zorder=3)

plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join('figures', 'pre_post_ban_yield_comparison.png'), dpi=300, bbox_inches='tight')
plt.close()

pre_ban_years = years[0:5]  # 2014-2018
post_ban_years = years[5:]  # 2019-2023

# Calculate averages for each period
pre_ban_volume = np.mean([volume_list[years.index(year)] for year in pre_ban_years])
post_ban_volume = np.mean([volume_list[years.index(year)] for year in post_ban_years])
pre_ban_value = np.mean([value_list[years.index(year)] for year in pre_ban_years])
post_ban_value = np.mean([value_list[years.index(year)] for year in post_ban_years])

# Create the bar chart
plt.figure(figsize=(12, 7))

# Set up positions for bars
x = np.array([0, 1])
width = 0.35

# Create bars
plt.bar(x - width/2, [pre_ban_volume, pre_ban_value], width, label='2014-2018 (Pre-Ban)', 
        color=['lightcoral', 'lightblue'])
plt.bar(x + width/2, [post_ban_volume, post_ban_value], width, label='2019-2023 (Post-Ban)', 
        color=['darkred', 'darkblue'])

# Add labels, title and legend
plt.ylabel('Average Value')
plt.title('Comparison of Sugar Beet Production Before and After Ban')
plt.xticks(x, ['Volume (thousand tonnes)', 'Value (£ million)'])
plt.legend()

# Add value labels on top of bars
for i, v in enumerate([pre_ban_volume, pre_ban_value]):
    plt.text(i - width/2, v + 0.1, f'{v:.1f}', ha='center', va='bottom')
    
for i, v in enumerate([post_ban_volume, post_ban_value]):
    plt.text(i + width/2, v + 0.1, f'{v:.1f}', ha='center', va='bottom')

# For the bar chart
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join('figures', 'pre_post_ban_comparison.png'), dpi=300, bbox_inches='tight')
plt.close()

# Create stacked area chart to show area and yield interaction over time
plt.figure(figsize=(12, 7))

# Normalize data for better visualization (convert to percentages of max value)
max_area = max(area_list)
max_yield = max(yield_list)
normalized_area = [(a/max_area)*100 for a in area_list]
normalized_yield = [(y/max_yield)*100 for y in yield_list]

# Create the stacked area chart
plt.stackplot(years, 
              [normalized_area, normalized_yield],
              labels=['Harvested Area', 'Yield per Hectare'],
              colors=[colors['Area'], colors['Yield']],
              alpha=0.7)

# Add a line for production volume (which is essentially area × yield)
plt.plot(years, [v/max(volume_list)*100 for v in volume_list], 
         'k-', linewidth=2.5, label='Production Volume')

# Add labels and title
plt.xlabel('Year')
plt.ylabel('Percentage of Maximum Value')
plt.title('Interaction Between Harvested Area and Yield Over Time')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(loc='upper left')

# Add annotations for key points
for i, year in enumerate(years):
    if i % 2 == 0:  # Annotate every other year to avoid crowding
        plt.annotate(f"{area_list[i]:.0f} ha, {yield_list[i]:.1f} t/ha", 
                    (years[i], normalized_area[i] + normalized_yield[i] + 5),
                    textcoords="offset points",
                    xytext=(0,5), 
                    ha='center',
                    fontsize=8)

plt.tight_layout()
plt.savefig(os.path.join('figures', 'area_yield_interaction.png'), dpi=300, bbox_inches='tight')
plt.close()

# Create a scatter plot to show how volume changes with area
plt.figure(figsize=(10, 8))

# Create scatter plot with points colored by yield
scatter = plt.scatter(area_list, volume_list, 
                     c=yield_list, 
                     cmap='viridis', 
                     s=100, 
                     alpha=0.8)

# Add regression line
z = np.polyfit(area_list, volume_list, 1)
p = np.poly1d(z)
plt.plot(area_list, p(area_list), "r-", alpha=0.7, linewidth=2)

# Add correlation coefficient
correlation = np.corrcoef(area_list, volume_list)[0, 1]
plt.annotate(f'Correlation: {correlation:.2f}', 
             xy=(0.05, 0.95), 
             xycoords='axes fraction',
             fontsize=12, 
             ha='left', 
             va='top',
             bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.7))

# Add year labels to points
for i, year in enumerate(years):
    plt.annotate(year, 
                (area_list[i], volume_list[i]),
                textcoords="offset points", 
                xytext=(0,10), 
                ha='center')

# Add colorbar to show yield values
cbar = plt.colorbar(scatter)
cbar.set_label('Yield (tonnes per hectare)')

# Add labels and title
plt.xlabel('Area Harvested (hectares)')
plt.ylabel('Volume of Production (thousand tonnes)')
plt.title('Relationship Between Harvested Area and Production Volume')
plt.grid(True, linestyle='--', alpha=0.7)

# Save and show the figure
plt.tight_layout()
plt.savefig(os.path.join('figures', 'area_vs_volume_relationship.png'), dpi=300, bbox_inches='tight')
plt.show()
plt.close()
