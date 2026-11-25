import os
import re
import json
import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

# Configure visualization aesthetics
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 14,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.titlesize": 16,
    "font.family": "sans-serif"
})

class DataAnalyzer:
    """
    Cleans raw scraped dataset, produces descriptive statistics, and
    generates visual reports/charts.
    """
    
    def __init__(self, raw_data_path: str, output_dir: str = "exports"):
        self.raw_data_path = raw_data_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.df = None

    def load_and_clean(self) -> pd.DataFrame:
        """
        Loads dataset from raw JSON and performs data cleaning.
        """
        logger.info(f"Loading raw data from {self.raw_data_path}...")
        with open(self.raw_data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.df = pd.DataFrame(data)
        logger.info(f"Initial raw shape: {self.df.shape}")
        
        if self.df.empty:
            logger.warning("Empty dataset loaded.")
            return self.df
            
        # Clean Prices (Remove £, convert to float)
        def clean_price(val):
            if pd.isna(val) or not isinstance(val, str):
                return 0.0
            match = re.search(r"[\d\.]+", val)
            return float(match.group()) if match else 0.0

        self.df["price_excl_tax"] = self.df["price_excl_tax"].apply(clean_price)
        self.df["price_incl_tax"] = self.df["price_incl_tax"].apply(clean_price)
        self.df["tax"] = self.df["tax"].apply(clean_price)
        
        # Clean Stock Availability (e.g. "In stock (19 available)" -> 19)
        def clean_stock(val):
            if pd.isna(val) or not isinstance(val, str):
                return 0
            match = re.search(r"\((\d+) available\)", val)
            return int(match.group(1)) if match else (1 if "In stock" in val else 0)

        self.df["stock_level"] = self.df["availability"].apply(clean_stock)
        
        # Ensure ratings are numeric
        self.df["rating"] = pd.to_numeric(self.df["rating"], errors="coerce").fillna(0).astype(int)
        
        # Clean up column ordering
        self.df = self.df[[
            "title", "category", "rating", "price_excl_tax", 
            "price_incl_tax", "tax", "stock_level", "upc", 
            "description", "url", "image_url"
        ]]
        
        cleaned_csv_path = os.path.join(self.output_dir, "cleaned_books.csv")
        self.df.to_csv(cleaned_csv_path, index=False, encoding="utf-8")
        logger.info(f"Cleaned dataset saved to {cleaned_csv_path}")
        return self.df

    def generate_report(self) -> str:
        """
        Computes key statistics and generates a detailed text summary report.
        """
        if self.df is None or self.df.empty:
            raise ValueError("Dataframe is empty or not loaded.")

        total_books = len(self.df)
        avg_price = self.df["price_excl_tax"].mean()
        max_price = self.df["price_excl_tax"].max()
        min_price = self.df["price_excl_tax"].min()
        median_price = self.df["price_excl_tax"].median()
        total_stock = self.df["stock_level"].sum()
        
        avg_rating = self.df["rating"].mean()
        
        # Category breakdowns
        cat_counts = self.df["category"].value_counts()
        avg_price_by_cat = self.df.groupby("category")["price_excl_tax"].mean()
        
        # Top expensive and cheapest books
        top_expensive = self.df.sort_values(by="price_excl_tax", ascending=False).head(5)
        top_cheapest = self.df.sort_values(by="price_excl_tax", ascending=True).head(5)
        
        report = []
        report.append("=" * 60)
        report.append("             DATA ANALYSIS SUMMARY REPORT")
        report.append("=" * 60)
        report.append(f"Total Books Scraped: {total_books}")
        report.append(f"Average Book Rating: {avg_rating:.2f} / 5.0")
        report.append(f"Total Stock Available: {total_stock} items")
        report.append("-" * 60)
        report.append("Price Statistics (Excl. Tax):")
        report.append(f"  - Average Price: £{avg_price:.2f}")
        report.append(f"  - Median Price:  £{median_price:.2f}")
        report.append(f"  - Maximum Price: £{max_price:.2f}")
        report.append(f"  - Minimum Price: £{min_price:.2f}")
        report.append("-" * 60)
        
        report.append("Top 5 Most Expensive Books:")
        for idx, row in top_expensive.iterrows():
            report.append(f"  - £{row['price_excl_tax']:.2f} | {row['title']} (Category: {row['category']})")
        report.append("-" * 60)
        
        report.append("Top 5 Cheapest Books:")
        for idx, row in top_cheapest.iterrows():
            report.append(f"  - £{row['price_excl_tax']:.2f} | {row['title']} (Category: {row['category']})")
        report.append("-" * 60)
        
        report.append("Books Count by Category (Top 10):")
        for cat, count in cat_counts.head(10).items():
            avg_p = avg_price_by_cat[cat]
            report.append(f"  - {cat:<25} : {count} books (Avg Price: £{avg_p:.2f})")
        report.append("=" * 60)
        
        report_content = "\n".join(report)
        
        report_path = os.path.join(self.output_dir, "analytical_report.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
            
        logger.info(f"Analytical text report saved to {report_path}")
        return report_content

    def generate_visuals(self):
        """
        Creates and saves analytical visualizations as high-resolution PNGs.
        """
        if self.df is None or self.df.empty:
            raise ValueError("Dataframe is empty or not loaded.")
            
        # 1. Rating Distribution Chart
        plt.figure(figsize=(8, 5))
        rating_counts = self.df["rating"].value_counts().sort_index()
        colors = sns.color_palette("crest", len(rating_counts))
        bars = plt.bar(rating_counts.index, rating_counts.values, color=colors, edgecolor="black", width=0.6)
        
        # Add labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                     f'{int(height)}',
                     ha='center', va='bottom', fontsize=10)
                     
        plt.title("Distribution of Book Ratings")
        plt.xlabel("Star Rating")
        plt.ylabel("Number of Books")
        plt.xticks(range(1, 6))
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "rating_distribution.png"), dpi=150)
        plt.close()

        # 2. Price Distribution Histogram
        plt.figure(figsize=(9, 5))
        sns.histplot(self.df["price_excl_tax"], kde=True, color="#4F46E5", bins=20)
        plt.title("Distribution of Book Prices")
        plt.xlabel("Price (in £)")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "price_distribution.png"), dpi=150)
        plt.close()

        # 3. Average Price by Category (Top 15)
        top_cats = self.df["category"].value_counts().head(15).index
        sub_df = self.df[self.df["category"].isin(top_cats)]
        
        plt.figure(figsize=(10, 6))
        cat_order = sub_df.groupby("category")["price_excl_tax"].mean().sort_values(ascending=False).index
        sns.barplot(
            data=sub_df, 
            y="category", 
            x="price_excl_tax", 
            order=cat_order, 
            errorbar=None, 
            palette="viridis",
            hue="category",
            legend=False
        )
        plt.title("Average Price by Book Category (Top 15 Categories)")
        plt.xlabel("Average Price (in £)")
        plt.ylabel("Category")
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "average_price_by_category.png"), dpi=150)
        plt.close()

        logger.info("Visualizations successfully generated and saved to exports directory.")
