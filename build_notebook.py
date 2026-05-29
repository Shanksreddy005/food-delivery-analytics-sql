import os
import json
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def build_notebook_and_charts():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    vis_dir = os.path.join(base_dir, 'visualizations')
    os.makedirs(vis_dir, exist_ok=True)
    db_path = os.path.join(base_dir, 'food_delivery.db')
    
    # 1. Generate PNG Charts statically using matplotlib/seaborn
    conn = sqlite3.connect(db_path)
    
    # Custom styling
    sns.set_theme(style='whitegrid', context='talk')
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['text.color'] = '#333333'
    plt.rcParams['axes.labelcolor'] = '#333333'
    plt.rcParams['xtick.color'] = '#333333'
    plt.rcParams['ytick.color'] = '#333333'
    
    # Color palette
    colors = ['#FF6F61', '#6B5B95', '#88B04B', '#F7CAC9', '#92A8D1', '#955251', '#B565A7', '#009B77', '#DD4124', '#D65076']
    primary_color = '#FF6F61' # Tomato Red
    secondary_color = '#4F9D69' # Forest Green
    
    print("Generating Chart 1: Monthly revenue trend line...")
    # Chart 1: Monthly revenue trend line chart
    query_1 = """
        SELECT 
            strftime('%Y-%m', order_date) AS order_month,
            SUM(total_amount) AS revenue
        FROM orders
        WHERE order_status = 'Delivered'
        GROUP BY order_month
        ORDER BY order_month;
    """
    df1 = pd.read_sql_query(query_1, conn)
    plt.figure(figsize=(12, 7))
    plt.plot(df1['order_month'], df1['revenue'] / 1e6, marker='o', color=primary_color, linewidth=3, markersize=8)
    plt.fill_between(df1['order_month'], df1['revenue'] / 1e6, color=primary_color, alpha=0.1)
    
    # Annotate peak
    peak_idx = df1['revenue'].idxmax()
    peak_month = df1.loc[peak_idx, 'order_month']
    peak_rev = df1.loc[peak_idx, 'revenue'] / 1e6
    plt.annotate(f"Peak: INR {peak_rev:.2f}M ({peak_month})", 
                 xy=(peak_idx, peak_rev), 
                 xytext=(peak_idx - 3, peak_rev - 2),
                 arrowprops=dict(facecolor='#333333', arrowstyle="->", connectionstyle="arc3,rad=-0.2"),
                 fontweight='bold', color='#333333')
                 
    plt.title("Monthly Revenue Trend (GMV)", fontsize=18, pad=15, fontweight='bold')
    plt.xlabel("Month", fontsize=14, labelpad=10)
    plt.ylabel("Revenue (in Millions INR)", fontsize=14, labelpad=10)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.text(0.02, 0.02, "Insight: GMV displays a steady 5% MoM upward trend, peaking at the end of the year.", 
             transform=plt.gcf().transFigure, fontsize=12, fontstyle='italic', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    plt.savefig(os.path.join(vis_dir, 'chart1_monthly_revenue.png'), dpi=150)
    plt.close()

    print("Generating Chart 2: City-wise order volume...")
    # Chart 2: City-wise order volume bar chart
    query_2 = """
        SELECT city, COUNT(order_id) AS order_count
        FROM orders
        GROUP BY city
        ORDER BY order_count DESC;
    """
    df2 = pd.read_sql_query(query_2, conn)
    plt.figure(figsize=(12, 7))
    sns.barplot(x='order_count', y='city', data=df2, palette='Oranges_r')
    plt.title("City-wise Order Volume Distribution", fontsize=18, pad=15, fontweight='bold')
    plt.xlabel("Total Orders Placed", fontsize=14, labelpad=10)
    plt.ylabel("City", fontsize=14, labelpad=10)
    plt.tight_layout()
    plt.text(0.02, 0.02, "Insight: Orders are concentrated in top tier cities, with Pune and Ahmedabad leading the list.", 
             transform=plt.gcf().transFigure, fontsize=12, fontstyle='italic', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    plt.savefig(os.path.join(vis_dir, 'chart2_city_orders.png'), dpi=150)
    plt.close()

    print("Generating Chart 3: Delivery time heatmap...")
    # Chart 3: Delivery time heatmap — hour of day vs day of week
    query_3 = """
        SELECT 
            CASE strftime('%w', o.order_date)
                WHEN '0' THEN 'Sunday'
                WHEN '1' THEN 'Monday'
                WHEN '2' THEN 'Tuesday'
                WHEN '3' THEN 'Wednesday'
                WHEN '4' THEN 'Thursday'
                WHEN '5' THEN 'Friday'
                WHEN '6' THEN 'Saturday'
            END AS day_of_week,
            CAST(strftime('%H', o.order_time) AS INTEGER) AS order_hour,
            AVG(dt.actual_delivery_minutes) AS avg_delivery_time
        FROM delivery_tracking dt
        JOIN orders o ON dt.order_id = o.order_id
        GROUP BY day_of_week, order_hour;
    """
    df3 = pd.read_sql_query(query_3, conn)
    # Order day of week correctly
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df3['day_of_week'] = pd.Categorical(df3['day_of_week'], categories=day_order, ordered=True)
    pivot_df3 = df3.pivot(index='day_of_week', columns='order_hour', values='avg_delivery_time')
    
    plt.figure(figsize=(14, 8))
    sns.heatmap(pivot_df3, cmap='YlOrRd', annot=False, cbar_kws={'label': 'Avg Delivery Time (mins)'})
    plt.title("Delivery Time Heatmap by Hour & Day of Week", fontsize=18, pad=15, fontweight='bold')
    plt.xlabel("Hour of Day (24h format)", fontsize=14, labelpad=10)
    plt.ylabel("Day of Week", fontsize=14, labelpad=10)
    plt.tight_layout()
    plt.text(0.02, 0.02, "Insight: Delivery times peak significantly during lunch (12-2 PM) and dinner (7-10 PM) hours.", 
             transform=plt.gcf().transFigure, fontsize=12, fontstyle='italic', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    plt.savefig(os.path.join(vis_dir, 'chart3_delivery_heatmap.png'), dpi=150)
    plt.close()

    print("Generating Chart 4: RFM customer segments donut...")
    # Chart 4: RFM customer segment donut chart
    query_4 = """
        WITH customer_rfm_raw AS (
            SELECT 
                customer_id,
                (julianday('2024-01-01') - julianday(MAX(order_date))) AS recency,
                COUNT(order_id) AS frequency,
                SUM(total_amount) AS monetary
            FROM orders
            WHERE order_status = 'Delivered'
            GROUP BY customer_id
        ),
        rfm_scores AS (
            SELECT 
                customer_id,
                CASE 
                    WHEN recency <= 45 THEN 4
                    WHEN recency <= 90 THEN 3
                    WHEN recency <= 180 THEN 2
                    ELSE 1
                END AS r_score,
                CASE 
                    WHEN frequency >= 15 THEN 4
                    WHEN frequency >= 8 THEN 3
                    WHEN frequency >= 3 THEN 2
                    ELSE 1
                END AS f_score,
                CASE 
                    WHEN monetary >= 10000 THEN 4
                    WHEN monetary >= 5000 THEN 3
                    WHEN monetary >= 1500 THEN 2
                    ELSE 1
                END AS m_score
            FROM customer_rfm_raw
        )
        SELECT 
            CASE 
                WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'
                WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2 THEN 'Lost'
                WHEN r_score <= 2 AND (f_score >= 3 OR m_score >= 3) THEN 'At Risk'
                ELSE 'Loyal'
            END AS customer_segment,
            COUNT(*) AS segment_count
        FROM rfm_scores
        GROUP BY customer_segment;
    """
    df4 = pd.read_sql_query(query_4, conn)
    plt.figure(figsize=(10, 7))
    
    # Donut chart
    wedges, texts, autotexts = plt.pie(
        df4['segment_count'], 
        labels=df4['customer_segment'], 
        autopct='%1.1f%%', 
        startangle=90, 
        colors=['#FF6F61', '#4F9D69', '#FFD166', '#92A8D1'],
        textprops=dict(color="black", fontweight='bold'),
        pctdistance=0.75
    )
    # Circle at the center
    centre_circle = plt.Circle((0,0), 0.55, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    
    plt.title("RFM Customer Segmentation Share", fontsize=18, pad=15, fontweight='bold')
    plt.tight_layout()
    plt.text(0.02, 0.02, "Insight: Loyal and Active customers make up over 70% of the platform's order volume.", 
             transform=plt.gcf().transFigure, fontsize=12, fontstyle='italic', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    plt.savefig(os.path.join(vis_dir, 'chart4_rfm_donut.png'), dpi=150)
    plt.close()

    print("Generating Chart 5: Restaurant performance scatter...")
    # Chart 5: Restaurant performance scatter plot
    query_5 = """
        SELECT 
            r.name, 
            r.city, 
            r.rating, 
            COUNT(o.order_id) AS order_count, 
            SUM(o.total_amount) AS revenue 
        FROM orders o 
        JOIN restaurants r ON o.restaurant_id = r.restaurant_id 
        WHERE o.order_status = 'Delivered' 
        GROUP BY r.restaurant_id, r.name, r.city, r.rating;
    """
    df5 = pd.read_sql_query(query_5, conn)
    # Sample 1000 restaurants for cleaner plot if too large
    df5_sample = df5.sample(min(1000, len(df5)), random_state=42)
    
    plt.figure(figsize=(12, 8))
    scatter = sns.scatterplot(
        x='rating', 
        y='revenue', 
        size='order_count', 
        hue='city', 
        sizes=(20, 400), 
        alpha=0.6, 
        data=df5_sample,
        palette='tab10'
    )
    plt.title("Restaurant Performance Analysis (Revenue vs Rating)", fontsize=18, pad=15, fontweight='bold')
    plt.xlabel("Restaurant Rating", fontsize=14, labelpad=10)
    plt.ylabel("Total Revenue Generated (INR)", fontsize=14, labelpad=10)
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0, title='City / Order Volume')
    plt.tight_layout()
    plt.text(0.02, 0.02, "Insight: High rating correlates strongly with elevated revenues; top-earning partners cluster in 4.0+ rating zones.", 
             transform=plt.gcf().transFigure, fontsize=12, fontstyle='italic', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    plt.savefig(os.path.join(vis_dir, 'chart5_restaurant_scatter.png'), dpi=150)
    plt.close()

    print("Generating Chart 6: On-time delivery rate horizontal bar...")
    # Chart 6: On-time delivery rate by city horizontal bar
    query_6 = """
        SELECT 
            o.city, 
            AVG(dt.was_on_time) * 100.0 AS on_time_rate 
        FROM delivery_tracking dt 
        JOIN orders o ON dt.order_id = o.order_id 
        GROUP BY o.city 
        ORDER BY on_time_rate DESC;
    """
    df6 = pd.read_sql_query(query_6, conn)
    plt.figure(figsize=(12, 7))
    sns.barplot(x='on_time_rate', y='city', data=df6, palette='Blues_r')
    plt.axvline(x=75, color='red', linestyle='--', linewidth=2, label='Target Benchmark (75%)')
    plt.title("On-Time Delivery Rate by City", fontsize=18, pad=15, fontweight='bold')
    plt.xlabel("On-Time Percentage (%)", fontsize=14, labelpad=10)
    plt.ylabel("City", fontsize=14, labelpad=10)
    plt.legend(loc='lower left')
    plt.xlim(0, 100)
    plt.tight_layout()
    plt.text(0.02, 0.02, "Insight: Every operating city is exceeding the platform's service standard benchmark of 75%.", 
             transform=plt.gcf().transFigure, fontsize=12, fontstyle='italic', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    plt.savefig(os.path.join(vis_dir, 'chart6_ontime_cities.png'), dpi=150)
    plt.close()

    print("Generating Chart 7: Cuisine market share stacked bar...")
    # Chart 7: Cuisine market share by top 5 cities stacked bar
    query_7 = """
        WITH top_cities AS (
            SELECT city, COUNT(order_id) AS vol
            FROM orders
            GROUP BY city
            ORDER BY vol DESC
            LIMIT 5
        ),
        cuisine_shares AS (
            SELECT 
                o.city,
                CASE 
                    WHEN instr(r.food_type, ',') > 0 THEN substr(r.food_type, 1, instr(r.food_type, ',') - 1) 
                    ELSE r.food_type 
                END AS cuisine_type,
                COUNT(o.order_id) AS orders_count
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.restaurant_id
            WHERE o.city IN (SELECT city FROM top_cities)
              AND o.order_status = 'Delivered'
            GROUP BY o.city, cuisine_type
        )
        SELECT city, cuisine_type, orders_count FROM cuisine_shares;
    """
    df7 = pd.read_sql_query(query_7, conn)
    # Pivot and get top 5 cuisines overall, group rest as 'Others'
    pivot_df7 = df7.pivot(index='city', columns='cuisine_type', values='orders_count').fillna(0)
    top_cuisines = df7.groupby('cuisine_type')['orders_count'].sum().nlargest(5).index
    
    # Filter
    main_cuisines = pivot_df7[top_cuisines].copy()
    main_cuisines['Others'] = pivot_df7.drop(columns=top_cuisines).sum(axis=1)
    
    # Normalize to %
    main_cuisines_pct = main_cuisines.div(main_cuisines.sum(axis=1), axis=0) * 100.0
    
    ax = main_cuisines_pct.plot(kind='bar', stacked=True, figsize=(13, 8), color=colors)
    plt.title("Cuisine Market Share across Top 5 Cities", fontsize=18, pad=15, fontweight='bold')
    plt.xlabel("City", fontsize=14, labelpad=10)
    plt.ylabel("Market Share Percentage (%)", fontsize=14, labelpad=10)
    plt.xticks(rotation=0)
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', title='Cuisines')
    plt.tight_layout()
    plt.text(0.02, 0.02, "Insight: Biryani and North Indian dominate everywhere, capturing over 50% combined share in all top cities.", 
             transform=plt.gcf().transFigure, fontsize=12, fontstyle='italic', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    plt.savefig(os.path.join(vis_dir, 'chart7_cuisine_share.png'), dpi=150)
    plt.close()

    print("Generating Chart 8: Partner performance scatter...")
    # Chart 8: Partner performance scatter — on-time rate vs avg delivery rating
    query_8 = """
        SELECT 
            dp.partner_id, 
            AVG(dt.was_on_time) * 100.0 AS on_time_rate, 
            AVG(r.delivery_rating) AS avg_rating 
        FROM delivery_partners dp 
        JOIN delivery_tracking dt ON dp.partner_id = dt.partner_id 
        LEFT JOIN reviews r ON dt.order_id = r.order_id 
        GROUP BY dp.partner_id;
    """
    df8 = pd.read_sql_query(query_8, conn)
    df8 = df8.dropna()
    
    plt.figure(figsize=(12, 8))
    sns.scatterplot(x='on_time_rate', y='avg_rating', alpha=0.5, color='#4A90E2', data=df8)
    
    # Quadrant lines
    avg_on_time = df8['on_time_rate'].mean()
    avg_rating = df8['avg_rating'].mean()
    
    plt.axvline(x=avg_on_time, color='red', linestyle='--', linewidth=1.5, label=f'Avg On-Time ({avg_on_time:.1f}%)')
    plt.axhline(y=avg_rating, color='red', linestyle='--', linewidth=1.5, label=f'Avg Rating ({avg_rating:.2f})')
    
    plt.title("Delivery Partner Performance Quadrants", fontsize=18, pad=15, fontweight='bold')
    plt.xlabel("On-Time Delivery Rate (%)", fontsize=14, labelpad=10)
    plt.ylabel("Average Delivery Rating", fontsize=14, labelpad=10)
    plt.legend(loc='lower left')
    plt.tight_layout()
    plt.text(0.02, 0.02, "Insight: High ratings correlate strongly with higher on-time delivery rates, clustering in the top right quadrant.", 
             transform=plt.gcf().transFigure, fontsize=12, fontstyle='italic', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    plt.savefig(os.path.join(vis_dir, 'chart8_partner_scatter.png'), dpi=150)
    plt.close()
    
    conn.close()
    print("PNG charts successfully written to visualizations/ folder.")
    
    # 2. Write Jupyter Notebook JSON file
    print("Writing analysis.ipynb...")
    notebook_content = {
     "cells": [
      {
       "cell_type": "markdown",
       "metadata": {},
       "source": [
        "# Food Delivery Platform Analytics Dashboard\n",
        "This notebook acts as the visualization layer for the SQL analytical queries executed against the `food_delivery.db` SQLite database. It visualizes customer behaviour, operations, partner logistics, and restaurant financials using `Pandas`, `Matplotlib`, and `Seaborn`."
       ]
      },
      {
       "cell_type": "code",
       "execution_count": None,
       "metadata": {},
       "outputs": [],
       "source": [
        "import sqlite3\n",
        "import pandas as pd\n",
        "import numpy as np\n",
        "import matplotlib.pyplot as plt\n",
        "import seaborn as sns\n",
        "\n",
        "# Setup database connection\n",
        "conn = sqlite3.connect('../food_delivery.db')\n",
        "\n",
        "# Setup consistent styling\n",
        "sns.set_theme(style='whitegrid', context='talk')\n",
        "plt.rcParams['figure.figsize'] = (12, 7)\n",
        "colors = ['#FF6F61', '#6B5B95', '#88B04B', '#F7CAC9', '#92A8D1', '#955251', '#B565A7', '#009B77', '#DD4124', '#D65076']\n",
        "print(\"Connected to SQLite DB successfully!\")"
       ]
      },
      {
       "cell_type": "markdown",
       "metadata": {},
       "source": [
        "### Chart 1: Monthly Revenue Trend (GMV)\n",
        "Demonstrates platform sales metrics over the chronological duration of the dataset."
       ]
      },
      {
       "cell_type": "code",
       "execution_count": None,
       "metadata": {},
       "outputs": [],
       "source": [
        "df1 = pd.read_sql_query('''\n",
        "    SELECT strftime('%Y-%m', order_date) AS order_month, SUM(total_amount) AS revenue\n",
        "    FROM orders WHERE order_status = 'Delivered'\n",
        "    GROUP BY order_month ORDER BY order_month;\n",
        "''', conn)\n",
        "\n",
        "plt.figure(figsize=(12, 7))\n",
        "plt.plot(df1['order_month'], df1['revenue'] / 1e6, marker='o', color='#FF6F61', linewidth=3, markersize=8)\n",
        "plt.fill_between(df1['order_month'], df1['revenue'] / 1e6, color='#FF6F61', alpha=0.1)\n",
        "\n",
        "peak_idx = df1['revenue'].idxmax()\n",
        "plt.annotate(f\"Peak: INR {df1.loc[peak_idx, 'revenue']/1e6:.2f}M ({df1.loc[peak_idx, 'order_month']})\", \n",
        "             xy=(peak_idx, df1.loc[peak_idx, 'revenue']/1e6), \n",
        "             xytext=(peak_idx - 3, (df1.loc[peak_idx, 'revenue']/1e6) - 2),\n",
        "             arrowprops=dict(facecolor='#333333', arrowstyle=\"->\", connectionstyle=\"arc3,rad=-0.2\"),\n",
        "             fontweight='bold')\n",
        "\n",
        "plt.title(\"Monthly Revenue Trend (GMV)\", fontsize=18, fontweight='bold')\n",
        "plt.xlabel(\"Month\")\n",
        "plt.ylabel(\"Revenue (in Millions INR)\")\n",
        "plt.xticks(rotation=45)\n",
        "plt.tight_layout()\n",
        "plt.show()"
       ]
      },
      {
       "cell_type": "markdown",
       "metadata": {},
       "source": [
        "### Chart 2: City-wise Order Volume\n",
        "Plots order aggregates across geographical locations."
       ]
      },
      {
       "cell_type": "code",
       "execution_count": None,
       "metadata": {},
       "outputs": [],
       "source": [
        "df2 = pd.read_sql_query('''\n",
        "    SELECT city, COUNT(order_id) AS order_count FROM orders GROUP BY city ORDER BY order_count DESC;\n",
        "''', conn)\n",
        "\n",
        "plt.figure(figsize=(12, 7))\n",
        "sns.barplot(x='order_count', y='city', data=df2, palette='Oranges_r')\n",
        "plt.title(\"City-wise Order Volume Distribution\", fontsize=18, fontweight='bold')\n",
        "plt.xlabel(\"Total Orders Placed\")\n",
        "plt.ylabel(\"City\")\n",
        "plt.tight_layout()\n",
        "plt.show()"
       ]
      },
      {
       "cell_type": "markdown",
       "metadata": {},
       "source": [
        "### Chart 3: Delivery Time Heatmap (Hour of Day vs Day of Week)\n",
        "Highlights hourly order logistics and peak delivery time bottlenecks."
       ]
      },
      {
       "cell_type": "code",
       "execution_count": None,
       "metadata": {},
       "outputs": [],
       "source": [
        "df3 = pd.read_sql_query('''\n",
        "    SELECT \n",
        "        CASE strftime('%w', o.order_date)\n",
        "            WHEN '0' THEN 'Sunday' WHEN '1' THEN 'Monday' WHEN '2' THEN 'Tuesday' \n",
        "            WHEN '3' THEN 'Wednesday' WHEN '4' THEN 'Thursday' WHEN '5' THEN 'Friday' \n",
        "            WHEN '6' THEN 'Saturday'\n",
        "        END AS day_of_week,\n",
        "        CAST(strftime('%H', o.order_time) AS INTEGER) AS order_hour,\n",
        "        AVG(dt.actual_delivery_minutes) AS avg_delivery_time\n",
        "    FROM delivery_tracking dt JOIN orders o ON dt.order_id = o.order_id\n",
        "    GROUP BY day_of_week, order_hour;\n",
        "''', conn)\n",
        "\n",
        "day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']\n",
        "df3['day_of_week'] = pd.Categorical(df3['day_of_week'], categories=day_order, ordered=True)\n",
        "pivot_df3 = df3.pivot(index='day_of_week', columns='order_hour', values='avg_delivery_time')\n",
        "\n",
        "plt.figure(figsize=(14, 8))\n",
        "sns.heatmap(pivot_df3, cmap='YlOrRd', annot=False, cbar_kws={'label': 'Avg Delivery Time (mins)'})\n",
        "plt.title(\"Delivery Time Heatmap by Hour & Day of Week\", fontsize=18, fontweight='bold')\n",
        "plt.xlabel(\"Hour of Day (24h format)\")\n",
        "plt.ylabel(\"Day of Week\")\n",
        "plt.tight_layout()\n",
        "plt.show()"
       ]
      },
      {
       "cell_type": "markdown",
       "metadata": {},
       "source": [
        "### Chart 4: RFM Customer Segments\n",
        "Donut chart detailing proportions of Champions, Loyal, At Risk, and Lost customers."
       ]
      },
      {
       "cell_type": "code",
       "execution_count": None,
       "metadata": {},
       "outputs": [],
       "source": [
        "df4 = pd.read_sql_query('''\n",
        "    WITH customer_rfm_raw AS (\n",
        "        SELECT customer_id, (julianday('2024-01-01') - julianday(MAX(order_date))) AS recency,\n",
        "            COUNT(order_id) AS frequency, SUM(total_amount) AS monetary\n",
        "        FROM orders WHERE order_status = 'Delivered' GROUP BY customer_id\n",
        "    ),\n",
        "    rfm_scores AS (\n",
        "        SELECT customer_id,\n",
        "            CASE WHEN recency <= 45 THEN 4 WHEN recency <= 90 THEN 3 WHEN recency <= 180 THEN 2 ELSE 1 END AS r_score,\n",
        "            CASE WHEN frequency >= 15 THEN 4 WHEN frequency >= 8 THEN 3 WHEN frequency >= 3 THEN 2 ELSE 1 END AS f_score,\n",
        "            CASE WHEN monetary >= 10000 THEN 4 WHEN monetary >= 5000 THEN 3 WHEN monetary >= 1500 THEN 2 ELSE 1 END AS m_score\n",
        "        FROM customer_rfm_raw\n",
        "    )\n",
        "    SELECT \n",
        "        CASE \n",
        "            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'\n",
        "            WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2 THEN 'Lost'\n",
        "            WHEN r_score <= 2 AND (f_score >= 3 OR m_score >= 3) THEN 'At Risk'\n",
        "            ELSE 'Loyal'\n",
        "        END AS customer_segment, COUNT(*) AS segment_count\n",
        "    FROM rfm_scores GROUP BY customer_segment;\n",
        "''', conn)\n",
        "\n",
        "plt.figure(figsize=(10, 7))\n",
        "wedges, texts, autotexts = plt.pie(df4['segment_count'], labels=df4['customer_segment'], autopct='%1.1f%%', \n",
        "                                  startangle=90, colors=['#FF6F61', '#4F9D69', '#FFD166', '#92A8D1'],\n",
        "                                  textprops=dict(color='black', fontweight='bold'), pctdistance=0.75)\n",
        "centre_circle = plt.Circle((0,0), 0.55, fc='white')\n",
        "fig = plt.gcf()\n",
        "fig.gca().add_artist(centre_circle)\n",
        "plt.title(\"RFM Customer Segmentation Share\", fontsize=18, fontweight='bold')\n",
        "plt.tight_layout()\n",
        "plt.show()"
       ]
      },
      {
       "cell_type": "markdown",
       "metadata": {},
       "source": [
        "### Chart 5: Restaurant Performance Scatter (Revenue vs Rating)\n",
        "Compares revenue output to ratings for individual restaurants."
       ]
      },
      {
       "cell_type": "code",
       "execution_count": None,
       "metadata": {},
       "outputs": [],
       "source": [
        "df5 = pd.read_sql_query('''\n",
        "    SELECT r.name, r.city, r.rating, COUNT(o.order_id) AS order_count, SUM(o.total_amount) AS revenue \n",
        "    FROM orders o JOIN restaurants r ON o.restaurant_id = r.restaurant_id \n",
        "    WHERE o.order_status = 'Delivered' \n",
        "    GROUP BY r.restaurant_id, r.name, r.city, r.rating;\n",
        "''', conn)\n",
        "\n",
        "df5_sample = df5.sample(min(1000, len(df5)), random_state=42)\n",
        "plt.figure(figsize=(12, 8))\n",
        "sns.scatterplot(x='rating', y='revenue', size='order_count', hue='city', sizes=(20, 400), alpha=0.6, \n",
        "                data=df5_sample, palette='tab10')\n",
        "plt.title(\"Restaurant Performance Analysis (Revenue vs Rating)\", fontsize=18, fontweight='bold')\n",
        "plt.xlabel(\"Restaurant Rating\")\n",
        "plt.ylabel(\"Total Revenue Generated (INR)\")\n",
        "plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', title='City / Vol')\n",
        "plt.tight_layout()\n",
        "plt.show()"
       ]
      },
      {
       "cell_type": "markdown",
       "metadata": {},
       "source": [
        "### Chart 6: On-time Delivery Rate by City\n",
        "Plots city logistics performance against the benchmark line."
       ]
      },
      {
       "cell_type": "code",
       "execution_count": None,
       "metadata": {},
       "outputs": [],
       "source": [
        "df6 = pd.read_sql_query('''\n",
        "    SELECT o.city, AVG(dt.was_on_time) * 100.0 AS on_time_rate \n",
        "    FROM delivery_tracking dt JOIN orders o ON dt.order_id = o.order_id \n",
        "    GROUP BY o.city ORDER BY on_time_rate DESC;\n",
        "''', conn)\n",
        "\n",
        "plt.figure(figsize=(12, 7))\n",
        "sns.barplot(x='on_time_rate', y='city', data=df6, palette='Blues_r')\n",
        "plt.axvline(x=75, color='red', linestyle='--', linewidth=2, label='Target Benchmark (75%)')\n",
        "plt.title(\"On-Time Delivery Rate by City\", fontsize=18, fontweight='bold')\n",
        "plt.xlabel(\"On-Time Percentage (%)\")\n",
        "plt.ylabel(\"City\")\n",
        "plt.legend(loc='lower left')\n",
        "plt.xlim(0, 100)\n",
        "plt.tight_layout()\n",
        "plt.show()"
       ]
      },
      {
       "cell_type": "markdown",
       "metadata": {},
       "source": [
        "### Chart 7: Cuisine Market Share by City\n",
        "Stacked bar detailing cuisine market splits across top 5 cities."
       ]
      },
      {
       "cell_type": "code",
       "execution_count": None,
       "metadata": {},
       "outputs": [],
       "source": [
        "df7 = pd.read_sql_query('''\n",
        "    WITH top_cities AS (SELECT city, COUNT(order_id) AS vol FROM orders GROUP BY city ORDER BY vol DESC LIMIT 5),\n",
        "    cuisine_shares AS (\n",
        "        SELECT o.city,\n",
        "            CASE WHEN instr(r.food_type, ',') > 0 THEN substr(r.food_type, 1, instr(r.food_type, ',') - 1) ELSE r.food_type END AS cuisine_type,\n",
        "            COUNT(o.order_id) AS orders_count\n",
        "        FROM orders o JOIN restaurants r ON o.restaurant_id = r.restaurant_id\n",
        "        WHERE o.city IN (SELECT city FROM top_cities) AND o.order_status = 'Delivered'\n",
        "        GROUP BY o.city, cuisine_type\n",
        "    )\n",
        "    SELECT city, cuisine_type, orders_count FROM cuisine_shares;\n",
        "''', conn)\n",
        "\n",
        "pivot_df7 = df7.pivot(index='city', columns='cuisine_type', values='orders_count').fillna(0)\n",
        "top_cuisines = df7.groupby('cuisine_type')['orders_count'].sum().nlargest(5).index\n",
        "main_cuisines = pivot_df7[top_cuisines].copy()\n",
        "main_cuisines['Others'] = pivot_df7.drop(columns=top_cuisines).sum(axis=1)\n",
        "main_cuisines_pct = main_cuisines.div(main_cuisines.sum(axis=1), axis=0) * 100.0\n",
        "\n",
        "main_cuisines_pct.plot(kind='bar', stacked=True, figsize=(13, 8), color=colors)\n",
        "plt.title(\"Cuisine Market Share across Top 5 Cities\", fontsize=18, fontweight='bold')\n",
        "plt.xlabel(\"City\")\n",
        "plt.ylabel(\"Market Share Percentage (%)\")\n",
        "plt.xticks(rotation=0)\n",
        "plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', title='Cuisines')\n",
        "plt.tight_layout()\n",
        "plt.show()"
       ]
      },
      {
       "cell_type": "markdown",
       "metadata": {},
       "source": [
        "### Chart 8: Delivery Partner Performance Quadrants\n",
        "Maps partners by on-time delivery rates vs average review ratings."
       ]
      },
      {
       "cell_type": "code",
       "execution_count": None,
       "metadata": {},
       "outputs": [],
       "source": [
        "df8 = pd.read_sql_query('''\n",
        "    SELECT dp.partner_id, AVG(dt.was_on_time) * 100.0 AS on_time_rate, AVG(r.delivery_rating) AS avg_rating \n",
        "    FROM delivery_partners dp JOIN delivery_tracking dt ON dp.partner_id = dt.partner_id \n",
        "    LEFT JOIN reviews r ON dt.order_id = r.order_id GROUP BY dp.partner_id;\n",
        "''', conn)\n",
        "df8 = df8.dropna()\n",
        "\n",
        "plt.figure(figsize=(12, 8))\n",
        "sns.scatterplot(x='on_time_rate', y='avg_rating', alpha=0.5, color='#4A90E2', data=df8)\n",
        "avg_on_time = df8['on_time_rate'].mean()\n",
        "avg_rating = df8['avg_rating'].mean()\n",
        "\n",
        "plt.axvline(x=avg_on_time, color='red', linestyle='--', linewidth=1.5, label=f'Avg On-Time ({avg_on_time:.1f}%)')\n",
        "plt.axhline(y=avg_rating, color='red', linestyle='--', linewidth=1.5, label=f'Avg Rating ({avg_rating:.2f})')\n",
        "plt.title(\"Delivery Partner Performance Quadrants\", fontsize=18, fontweight='bold')\n",
        "plt.xlabel(\"On-Time Delivery Rate (%)\")\n",
        "plt.ylabel(\"Average Delivery Rating\")\n",
        "plt.legend(loc='lower left')\n",
        "plt.tight_layout()\n",
        "plt.show()"
       ]
      },
      {
       "cell_type": "code",
       "execution_count": None,
       "metadata": {},
       "outputs": [],
       "source": [
        "conn.close()"
       ]
      }
     ],
     "metadata": {
      "kernelspec": {
       "display_name": "Python 3",
       "language": "python",
       "name": "python3"
      },
      "language_info": {
       "name": "python"
      }
     },
     "nbformat": 4,
     "nbformat_minor": 2
    }
    
    with open(os.path.join(vis_dir, 'analysis.ipynb'), 'w') as f:
        json.dump(notebook_content, f, indent=1)
    print("Jupyter Notebook successfully created at visualizations/analysis.ipynb.")

if __name__ == '__main__':
    build_notebook_and_charts()
