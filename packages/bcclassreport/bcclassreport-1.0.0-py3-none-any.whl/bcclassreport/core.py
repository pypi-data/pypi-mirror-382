
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import warnings
import importlib
import sys
from typing import Union, Optional, Tuple, Any


plt.rcdefaults()
plt.close('all')

if 'matplotlib.backends' in sys.modules:
    importlib.reload(sys.modules['matplotlib.backends'])

warnings.filterwarnings('ignore')

__version__ = "1.0.0"
__author__ = "Open Source Contributors"
__license__ = "MIT"

class BinaryClassificationReport:
   
    
    def __init__(self, y_true: Union[list, np.ndarray], y_pred: Union[list, np.ndarray], 
                 label_0: Optional[str] = None, label_1: Optional[str] = None) -> None:
       
        plt.close('all')
        
        self.y_true = np.array(y_true)
        self.y_pred = np.array(y_pred)
        
        self._convert_to_binary()
        self._set_labels(label_0, label_1)
        self._calculate_metrics()
    
    def _convert_to_binary(self) -> None:
       
        unique_vals = np.unique(np.concatenate([self.y_true, self.y_pred]))
        
        if len(unique_vals) != 2:
            raise ValueError(f"Binary classification required. Found {len(unique_vals)} unique classes: {unique_vals}")
        
        sorted_vals = sorted(unique_vals)
        self._label_mapping = {sorted_vals[0]: 0, sorted_vals[1]: 1}
        self._reverse_mapping = {0: sorted_vals[0], 1: sorted_vals[1]}
        
        self.y_true_binary = np.array([self._label_mapping[y] for y in self.y_true])
        self.y_pred_binary = np.array([self._label_mapping[y] for y in self.y_pred])
    
    def _set_labels(self, label_0: Optional[str], label_1: Optional[str]) -> None:
        """Set human-readable labels for the classes."""
        if label_0 and label_1:
            self.label_0 = str(label_0)
            self.label_1 = str(label_1)
        else:
            original_0 = self._reverse_mapping[0]
            original_1 = self._reverse_mapping[1]
            
            self.label_0 = str(original_0)
            self.label_1 = str(original_1)
    
    def _calculate_metrics(self) -> None:
       
        self.cm = confusion_matrix(self.y_true_binary, self.y_pred_binary)
        
        if self.cm.shape != (2, 2):
            raise ValueError("Invalid confusion matrix shape. Binary classification required.")
        
   
        self.tn = self.cm[0, 0]
        self.fp = self.cm[0, 1]
        self.fn = self.cm[1, 0]
        self.tp = self.cm[1, 1]
        self.total = self.tp + self.tn + self.fp + self.fn
        
      
        self.accuracy = (self.tp + self.tn) / self.total if self.total > 0 else 0.0
        self.precision = self.tp / (self.tp + self.fp) if (self.tp + self.fp) > 0 else 0.0
        self.recall = self.tp / (self.tp + self.fn) if (self.tp + self.fn) > 0 else 0.0
        self.f1_score = (2 * self.precision * self.recall / (self.precision + self.recall) 
                        if (self.precision + self.recall) > 0 else 0.0)
        self.specificity = self.tn / (self.tn + self.fp) if (self.tn + self.fp) > 0 else 0.0
        self.type_1_error = self.fp / (self.tn + self.fp) if (self.tn + self.fp) > 0 else 0.0
        self.type_2_error = self.fn / (self.tp + self.fn) if (self.tp + self.fn) > 0 else 0.0
        
       
        self.total_positive_predictions = self.tp + self.fp
        self.total_negative_predictions = self.tn + self.fn
        self.total_actual_positives = self.tp + self.fn
        self.total_actual_negatives = self.tn + self.fp
        self.total_correct_predictions = self.tp + self.tn
    
    def clear_cache(self) -> None:
        
        plt.close('all')
        plt.rcdefaults()
        plt.ioff()
        
        if hasattr(plt, '_pylab_helpers'):
            plt._pylab_helpers.Gcf.destroy_all()
        
        import gc
        gc.collect()
        
        if 'matplotlib.backends' in sys.modules:
            importlib.reload(sys.modules['matplotlib.backends'])
    
    def print_results(self) -> None:
        
        print("BINARY CLASSIFICATION RESULTS")
        print("=" * 60)
        
        print(f"Total Predictions ({self.total}): You tested your model on {self.total} cases total.")
        print()
        
        print(f"TP ({self.tp}): Your model correctly predicted {self.tp} cases as class '{self.label_1}' when they were actually class '{self.label_1}'.")
        print()
        
        print(f"FN ({self.fn}): Your model wrongly predicted {self.fn} cases as class '{self.label_0}' when they were actually class '{self.label_1}'.")
        print()
        
        print(f"FP ({self.fp}): Your model wrongly predicted {self.fp} cases as class '{self.label_1}' when they were actually class '{self.label_0}'.")
        print()
        
        print(f"TN ({self.tn}): Your model correctly predicted {self.tn} cases as class '{self.label_0}' when they were actually class '{self.label_0}'.")
        print()
        
        print(f"Accuracy ({self.accuracy:.2%}): Out of {self.total} total predictions, your model got {self.total_correct_predictions} predictions completely right. Formula: (TP+TN)/Total")
        print()
        
        print(f"Precision ({self.precision:.2%}): Your model predicted {self.total_positive_predictions} instances as class '{self.label_1}', and {self.tp} of these predictions were correct. Formula: TP/(TP+FP)")
        print()
        
        print(f"Recall ({self.recall:.2%}): Out of {self.total_actual_positives} actual class '{self.label_1}' instances, your model correctly predicted {self.tp} as class '{self.label_1}'. Formula: TP/(TP+FN)")
        print()
        
        print(f"F1-Score ({self.f1_score:.2%}): This is the harmonic mean of Precision and Recall, balancing both metrics. It shows how well your model performs at both making accurate predictions for class '{self.label_1}' and finding actual class '{self.label_1}' instances. Formula: 2×Precision×Recall/(Precision+Recall)")
        print()
        
        print(f"Specificity ({self.specificity:.2%}): Out of {self.total_actual_negatives} actual class '{self.label_0}' instances, your model correctly predicted {self.tn} as class '{self.label_0}'. Formula: TN/(TN+FP)")
        print()
        
        print(f"Type I Error ({self.type_1_error:.2%}): Out of {self.total_actual_negatives} actual class '{self.label_0}' instances, your model incorrectly predicted {self.fp} as class '{self.label_1}'. Formula: FP/(TN+FP)")
        print()
        
        print(f"Type II Error ({self.type_2_error:.2%}): Out of {self.total_actual_positives} actual class '{self.label_1}' instances, your model incorrectly predicted {self.fn} as class '{self.label_0}'. Formula: FN/(TP+FN)")
    
    def visualize(self, save_path: Optional[str] = None, show_plot: bool = True) -> None:
        
        self.clear_cache()
        
        figsize = (26, 8)
        display_dpi = 100
        
        fig = plt.figure(figsize=figsize, facecolor='white', dpi=display_dpi)
        
        from matplotlib.gridspec import GridSpec
        gs = GridSpec(1, 35, figure=fig, wspace=0.5, hspace=0)
        
        # Panel 1: Confusion Matrix [[TP, FN], [FP, TN]]
        ax1 = fig.add_subplot(gs[0, 0:4])
        
        matrix_data = np.array([[self.tp, self.fn], [self.fp, self.tn]])
        ax1.imshow(matrix_data, cmap='Blues', alpha=0.8, aspect='equal')
        
        max_val = max(self.tp, self.fp, self.fn, self.tn) if max(self.tp, self.fp, self.fn, self.tn) > 0 else 1
        
        ax1.text(0, 0, f'{self.tp}', ha='center', va='center', fontsize=8, fontweight='bold', 
                color='white' if self.tp > max_val*0.5 else 'black')
        ax1.text(1, 0, f'{self.fn}', ha='center', va='center', fontsize=8, fontweight='bold', 
                color='white' if self.fn > max_val*0.5 else 'black')
        ax1.text(0, 1, f'{self.fp}', ha='center', va='center', fontsize=8, fontweight='bold', 
                color='white' if self.fp > max_val*0.5 else 'black')
        ax1.text(1, 1, f'{self.tn}', ha='center', va='center', fontsize=8, fontweight='bold', 
                color='white' if self.tn > max_val*0.5 else 'black')
        
        ax1.set_xticks([0, 1])
        ax1.set_xticklabels([self.label_1, self.label_0], fontsize=7)
        ax1.set_yticks([0, 1])
        ax1.set_yticklabels([self.label_1, self.label_0], fontsize=7)
        ax1.set_xlabel('Predicted', fontsize=9, fontweight='bold')
        ax1.set_ylabel('Actual', fontsize=9, fontweight='bold')
        ax1.set_title('Confusion Matrix', fontsize=10, pad=12)
        
        # Panel 2: Performance Breakdown Bar Chart
        ax2 = fig.add_subplot(gs[0, 10:16])
        
        performance_labels = ['TP', 'FN', 'FP', 'TN']
        performance_values = [self.tp, self.fn, self.fp, self.tn]
        performance_colors = ['#2E7D32', '#FF6F00', '#D32F2F', '#1976D2']
        
        bars = ax2.bar(range(len(performance_labels)), performance_values, 
                      color=performance_colors, alpha=0.85, width=0.6)
        
        ax2.set_xticks(range(len(performance_labels)))
        ax2.set_xticklabels(performance_labels, fontsize=7, rotation=45, ha='right')
        ax2.set_title('Performance Breakdown', fontsize=10, pad=8)
        ax2.tick_params(axis='y', labelsize=7)
        ax2.set_ylabel('Count', fontsize=8)
        
        max_val = max(performance_values) if performance_values else 1
        for bar, value in zip(bars, performance_values):
            if value >= 0:
                label_y = bar.get_height() + max_val*0.01
                ax2.text(bar.get_x() + bar.get_width()/2, label_y,
                        str(value), ha='center', va='bottom', fontsize=7)
        
        if max_val > 0:
            ax2.set_ylim(0, max_val * 1.15)
        
        ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
        ax2.set_axisbelow(True)
        
        # Panel 3: Performance Metrics Explained
        ax3 = fig.add_subplot(gs[0, 19:41])
        ax3.axis('off')
        
        detailed_text = f"""PERFORMANCE METRICS EXPLAINED:

Total Predictions ({self.total}): You tested your model on {self.total} cases total.

TP ({self.tp}): Your model correctly predicted {self.tp} cases as class '{self.label_1}' 
when they were actually class '{self.label_1}'.

FN ({self.fn}): Your model wrongly predicted {self.fn} cases as class '{self.label_0}' 
when they were actually class '{self.label_1}'.

FP ({self.fp}): Your model wrongly predicted {self.fp} cases as class '{self.label_1}' 
when they were actually class '{self.label_0}'.

TN ({self.tn}): Your model correctly predicted {self.tn} cases as class '{self.label_0}' 
when they were actually class '{self.label_0}'.

Accuracy ({self.accuracy:.2%}): Out of {self.total} total predictions, your model got 
{self.total_correct_predictions} predictions completely right. Formula: (TP+TN)/Total

Precision ({self.precision:.2%}): Your model predicted {self.total_positive_predictions} 
instances as class '{self.label_1}', and {self.tp} of these predictions were correct. 
Formula: TP/(TP+FP)

Recall ({self.recall:.2%}): Out of {self.total_actual_positives} actual class '{self.label_1}' 
instances, your model correctly predicted {self.tp} as class '{self.label_1}'. 
Formula: TP/(TP+FN)

Specificity ({self.specificity:.2%}): Out of {self.total_actual_negatives} actual 
class '{self.label_0}' instances, your model correctly predicted {self.tn} as 
class '{self.label_0}'. Formula: TN/(TN+FP)

Type I Error ({self.type_1_error:.2%}): Out of {self.total_actual_negatives} actual 
class '{self.label_0}' instances, your model incorrectly predicted {self.fp} as 
class '{self.label_1}'. Formula: FP/(TN+FP)

Type II Error ({self.type_2_error:.2%}): Out of {self.total_actual_positives} actual 
class '{self.label_1}' instances, your model incorrectly predicted {self.fn} as 
class '{self.label_0}'. Formula: FN/(TP+FN)

F1-Score ({self.f1_score:.2%}): This is the harmonic mean of Precision and Recall, balancing 
both metrics. It shows how well your model performs at both making accurate predictions for 
class '{self.label_1}' and finding actual class '{self.label_1}' instances. 
Formula: 2×Precision×Recall/(Precision+Recall)"""
        
        ax3.text(0.02, 1.10, detailed_text, transform=ax3.transAxes, 
                fontsize=7, verticalalignment='top', 
                bbox=dict(boxstyle="round,pad=0.2", facecolor="#f8f9fa", 
                         edgecolor="#dee2e6", alpha=0.98))
        
        fig.suptitle(f'Binary Classification Report: {self.label_0} vs {self.label_1}\n' + '─' * 60, 
            fontsize=14, fontweight='bold')
        
        plt.subplots_adjust(top=0.80, bottom=0.20, left=0.06, right=0.98)
        
        pos1 = ax1.get_position()
        ax1.set_position([pos1.x0 + 0.04, pos1.y0, pos1.width, pos1.height])
        
        pos2 = ax2.get_position()
        ax2.set_position([pos2.x0, pos2.y0 - 0.04, pos2.width, pos2.height])
        
        if save_path:
            target_width_px = 1920
            target_height_px = 920
            save_dpi = 150
            fig_width_inches = target_width_px / save_dpi
            fig_height_inches = target_height_px / save_dpi

            original_size = fig.get_size_inches()
            fig.set_size_inches(fig_width_inches, fig_height_inches)
            fig.savefig(save_path, dpi=save_dpi, facecolor='white', edgecolor='none')
            fig.set_size_inches(original_size)

            print(f"Visualization saved: {save_path} at {target_width_px}x{target_height_px} pixels")
        
        if show_plot:
            plt.show()
        else:
            plt.close(fig)
        
        self.clear_cache()
    
    def get_metrics(self) -> dict:

        return {
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'specificity': self.specificity,
            'f1_score': self.f1_score,
            'type_1_error': self.type_1_error,
            'type_2_error': self.type_2_error,
            'true_positives': self.tp,
            'false_negatives': self.fn,
            'false_positives': self.fp,
            'true_negatives': self.tn,
            'total_samples': self.total,
            'total_positive_predictions': self.total_positive_predictions,
            'total_negative_predictions': self.total_negative_predictions,
            'total_actual_positives': self.total_actual_positives,
            'total_actual_negatives': self.total_actual_negatives,
            'total_correct_predictions': self.total_correct_predictions
        }


def binary_classification_report(y_true: Union[list, np.ndarray], y_pred: Union[list, np.ndarray], 
                                 label_0: Optional[str] = None, label_1: Optional[str] = None,
                                 save_path: Optional[str] = None,
                                 show_visual: bool = True, 
                                 show_console: bool = False) -> BinaryClassificationReport:

    report = BinaryClassificationReport(y_true, y_pred, label_0, label_1)
    
    if show_console:
        report.print_results()
    
    if show_visual:
        if show_console:
            print()
        report.visualize(save_path=save_path)
    
    return report


def _clear_module_cache():
  
    current_module = sys.modules.get(__name__)
    if current_module and hasattr(current_module, '__dict__'):
        plt.close('all')
        plt.rcdefaults()

_clear_module_cache()