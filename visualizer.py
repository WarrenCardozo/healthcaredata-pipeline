# visualizer.py

import matplotlib.pyplot as plt
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_visualizations(df, output_dir='plots'):
    """Generate Tasks 7-8 charts"""
    os.makedirs(output_dir, exist_ok=True)
    plots = []
    
    # Histogram: Age
    if 'Age' in df.columns:
        plt.figure(figsize=(10, 6))
        plt.hist(df['Age'], bins=15, edgecolor='black', color='skyblue')
        plt.title('Age Distribution', fontsize=14, fontweight='bold')
        plt.xlabel('Age', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        age_plot = f'{output_dir}/age_histogram.png'
        plt.savefig(age_plot, dpi=150, bbox_inches='tight')
        plt.close()
        plots.append(age_plot)
    
    # Bar chart: Delivery type
    if 'DeliveryType' in df.columns:
        plt.figure(figsize=(10, 6))
        delivery_counts = df['DeliveryType'].value_counts()
        colors = ['skyblue', 'lightcoral', 'lightgreen', 'lightyellow'][:len(delivery_counts)]
        delivery_counts.plot(kind='bar', color=colors)
        plt.title('Delivery Type Distribution', fontsize=14, fontweight='bold')
        plt.xlabel('Delivery Type', fontsize=12)
        plt.ylabel('Count', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        delivery_plot = f'{output_dir}/delivery_bar.png'
        plt.savefig(delivery_plot, dpi=150, bbox_inches='tight')
        plt.close()
        plots.append(delivery_plot)
    
    # Pie chart: Complications
    if 'Complications' in df.columns:
        plt.figure(figsize=(10, 6))
        comp_counts = df['Complications'].value_counts()
        comp_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, 
                        colors=['lightcoral', 'lightgreen'])
        plt.title('Complications Distribution', fontsize=14, fontweight='bold')
        plt.ylabel('')
        comp_plot = f'{output_dir}/complications_pie.png'
        plt.savefig(comp_plot, dpi=150, bbox_inches='tight')
        plt.close()
        plots.append(comp_plot)
    
    # Additional: LOS distribution if available
    if 'LOS' in df.columns:
        plt.figure(figsize=(10, 6))
        plt.hist(df['LOS'], bins=15, edgecolor='black', color='lightgreen')
        plt.title('Length of Stay Distribution', fontsize=14, fontweight='bold')
        plt.xlabel('Length of Stay (days)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        los_plot = f'{output_dir}/los_histogram.png'
        plt.savefig(los_plot, dpi=150, bbox_inches='tight')
        plt.close()
        plots.append(los_plot)
    
    logging.info(f"✓ Saved {len(plots)} visualizations to {output_dir}/")
    return plots
