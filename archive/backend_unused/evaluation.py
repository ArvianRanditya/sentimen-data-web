import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# ============================================================
# HITUNG AKURASI
# ============================================================

def calculate_accuracy(y_true, y_pred):
    return accuracy_score(y_true, y_pred)


# ============================================================
# CLASSIFICATION REPORT → DATAFRAME
# ============================================================

def get_classification_report(y_true, y_pred):
    report = classification_report(y_true, y_pred, output_dict=True)
    return pd.DataFrame(report).transpose()


# ============================================================
# CONFUSION MATRIX (HEATMAP)
# ============================================================

def plot_confusion_matrix(y_true, y_pred):

    cm = confusion_matrix(y_true, y_pred)

    fig, ax = plt.subplots()
    cax = ax.matshow(cm)

    # tambahkan angka di dalam kotak
    for (i, j), val in enumerate(cm.flatten()):
        ax.text(j, i, val, ha='center', va='center')

    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion Matrix")

    fig.colorbar(cax)

    return fig