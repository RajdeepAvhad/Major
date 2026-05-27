"""Plot 2D PCA and t-SNE visualizations for meal clusters (breakfast by default).

Saves output PNG to scripts/output/breakfast_clusters.png
"""
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


def main():
    BASE_DIR = Path(__file__).resolve().parent.parent

    # Load food data (fallback to food.csv)
    food_path = BASE_DIR / 'static' / 'data' / 'food_master.csv'
    if not food_path.exists():
        food_path = BASE_DIR / 'static' / 'data' / 'food.csv'

    food_data = pd.read_csv(food_path)

    # Nutrient columns used in clustering
    nutrient_cols = [
        'Calories', 'Fats', 'Proteins', 'Iron', 'Calcium',
        'Sodium', 'Potassium', 'Carbohydrates', 'Fibre', 'VitaminD'
    ]

    # Select breakfast foods
    breakfast_foods = food_data[food_data['Breakfast'] == 1].copy()
    breakfast_foods = breakfast_foods.dropna(subset=nutrient_cols)

    X = breakfast_foods[nutrient_cols].values
    names = breakfast_foods['Food_items'].astype(str).values if 'Food_items' in breakfast_foods.columns else None

    if X.shape[0] < 3:
        print("Not enough breakfast samples to plot (need >=3).")
        return

    # Apply Agglomerative Clustering (same as project)
    clustering = AgglomerativeClustering(n_clusters=5, linkage='ward')
    labels = clustering.fit_predict(X)

    # PCA reduction
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X)

    # t-SNE reduction (use a small perplexity relative to sample size)
    perp = min(30, max(5, X.shape[0] // 10))
    tsne = TSNE(n_components=2, random_state=42, init='pca', learning_rate='auto', perplexity=perp)
    X_tsne = tsne.fit_transform(X)

    # Prepare output dir
    out_dir = BASE_DIR / 'scripts' / 'output'
    os.makedirs(out_dir, exist_ok=True)

    out_path = out_dir / 'breakfast_clusters.png'

    # Plot
    plt.figure(figsize=(14, 6))
    palette = sns.color_palette('tab10', n_colors=len(np.unique(labels)))

    ax1 = plt.subplot(1, 2, 1)
    for lbl in np.unique(labels):
        idx = labels == lbl
        ax1.scatter(X_pca[idx, 0], X_pca[idx, 1], s=40, color=palette[int(lbl) % len(palette)], label=f'Cluster {lbl} ({idx.sum()})', alpha=0.8)
    ax1.set_title('PCA (2D) - Breakfast clusters')
    ax1.set_xlabel('PC1')
    ax1.set_ylabel('PC2')
    ax1.legend(loc='best', fontsize='small')

    ax2 = plt.subplot(1, 2, 2)
    for lbl in np.unique(labels):
        idx = labels == lbl
        ax2.scatter(X_tsne[idx, 0], X_tsne[idx, 1], s=40, color=palette[int(lbl) % len(palette)], label=f'Cluster {lbl} ({idx.sum()})', alpha=0.8)
    ax2.set_title('t-SNE (2D) - Breakfast clusters')
    ax2.set_xlabel('Dim1')
    ax2.set_ylabel('Dim2')
    ax2.legend(loc='best', fontsize='small')

    plt.suptitle('Breakfast: AgglomerativeClustering (n_clusters=5) — PCA vs t-SNE')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(out_path, dpi=150)
    plt.close()

    print(f"Saved cluster visualization to: {out_path}")


if __name__ == '__main__':
    main()
