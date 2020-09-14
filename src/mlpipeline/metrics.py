"""
Metrics module to evaluate and assess/gauge nlp ml model performance.
"""
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, auc, roc_curve, roc_auc_score, average_precision_score
from sklearn.preprocessing import LabelBinarizer
import itertools
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle


class BasicMetrics:
    """Basic class responsible to set basic Metrics attr."""
    def __init__(self, exp_name, classes, test_Y, predictions, output_path):
        self.exp_name = exp_name
        self.classes = classes
        self.test_Y = test_Y
        self.prediction_labels = predictions
        self.prediction_probabilities = predictions
        self.output_path = output_path
        self.file_extension = 'csv'

    @property
    def test_Y(self):
        return self._test_Y

    @test_Y.setter
    def test_Y(self, value):
        if not isinstance(value, pd.Series) and not \
                isinstance(value, pd.DataFrame):
            raise ValueError(f"test_Y must be a `pd.Series` or `pd.DataFrame`"
                             f" object found {type(value)} instead.")

        if isinstance(value, pd.DataFrame):
            value = value.iloc[:, 0]

        self._test_Y = value

    def validate_results(self, data):
        if not isinstance(data, np.ndarray):
            raise ValueError("Results from predictions must be of type `np.ndarray`.")

        if not data.dtype == np.float \
                and not data.dtype == np.object:
            raise ValueError("Predictions must be a `np.ndarray` dtype float or str object.")

        return True

    @property
    def prediction_labels(self):
        return self._prediction_labels

    @prediction_labels.setter
    def prediction_labels(self, data):
        """sets the prediction labels attributes"""
        if self.validate_results(data) and data.shape[1] > 1 and data.dtype == np.float:
            pred_class_nums = np.argmax(data, axis=1)
            class_names = list(enumerate(self.classes))
            prediction_class_names = list(map(lambda x: class_names[x][1], pred_class_nums))

        else:
            prediction_class_names = data

        self._prediction_labels = prediction_class_names

    @property
    def prediction_probabilities(self):
        return self._prediction_probabilities

    @prediction_probabilities.setter
    def prediction_probabilities(self, data):
        if self.validate_results(data) and data.shape[1] > 1 and data.dtype == np.float:
            self._prediction_probabilities = data
        else:
            self._prediction_probabilities = None


class Metrics(BasicMetrics):
    """
    Metrics class to get main sklearn classification ml metrics.
    """
    def __init__(self, exp_name, classes, test_Y, predictions, output_path='../data/results/'):
        super().__init__(exp_name, classes, test_Y, predictions, output_path=output_path)
        self._fpr = dict()
        self._tpr = dict()
        self._roc_auc = dict()

    @property
    def summary_report(self):
        return NotImplemented

    @property
    def accuracy_score(self):
        return accuracy_score(self.test_Y, self.prediction_labels)

    # I believe precision score does not work for multiclass classification
    @property
    def average_precision_score(self):
        return average_precision_score(self.test_Y, self.prediction_labels)

    @property
    def classification_report(self):
        return classification_report(self.test_Y, self.prediction_labels, output_dict=True)

    @property
    def confusion_matrix(self):
        return confusion_matrix(self.test_Y, self.prediction_labels)

    @property
    def f1_score(self):
        """
        By default pipeline uses average='weighted'.
        """
        return f1_score(self.test_Y, self.prediction_labels, average='weighted')

    @property
    def roc_auc_score(self):
        """
        By default pipeline uses average='macro'.
        """
        return roc_auc_score(self.test_Y, self.prediction_labels)

    def plot_confusion_matrix(self, figsize=(8, 8),
                              labels=None,
                              title='Confusion Matrix of the Classifier\n',
                              xlabel='Predicted', ylabel='True'):
        """
        Returns a confusin matrix figure.
        """
        if labels is None:
            labels = ['positive', 'neutral', 'negative']

        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)

        cm = self.confusion_matrix
        cax = ax.matshow(cm)

        plt.title(title)
        fig.colorbar(cax)

        ax.set_xticklabels([''] + labels)
        ax.set_yticklabels([''] + labels)

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        thresh = cm.max() / 2

        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            plt.text(j, i, format(cm[i, j], 'd'), horizontalalignment='center',
                     color='white' if cm[i, j] < thresh else 'black', fontsize=26)

        return fig

    # Left this here for now. If not needed we can delete it immediately.
    def dump_results_csv(self):
        data = pd.DataFrame({'test_Y': self.test_Y, 'Y_hat': self.prediction_labels})
        data.to_csv(self.output_path + self.exp_name + self.file_extension)

    @staticmethod
    def _get_binary_labels(labels):
        """
        Transforms class `str` labels into numerical 0,1.
        """
        lb = LabelBinarizer()
        return lb.fit_transform(labels)

    def _calculate_micro_rates(self):
        """
        Calculates micro rates for roc plots purposes.
        """
        if self.prediction_probabilities is None:
            raise Exception("Could not find probabilities for model results")

        binary_y_test = Metrics._get_binary_labels(self.test_Y)

        for i in range(len(self.classes)):
            self._fpr[i], self._tpr[i], _ = roc_curve(binary_y_test[:, i], self.prediction_probabilities[:, i])
            self._roc_auc[i] = auc(self._fpr[i], self._tpr[i])

        self._fpr["micro"], self._tpr["micro"], _ = roc_curve(binary_y_test.ravel(), self.prediction_probabilities.ravel())
        self._roc_auc["micro"] = auc(self._fpr["micro"], self._tpr["micro"])

    def plot_single_roc_curve(self, color='darkorange', label='ROC curve (area = %0.2f)',
                       xlabel='False Positive Rate', ylabel='True Positive Rate',
                       title='Receiver operating characteristic', legend_loc="lower right",
                       lw=2, figsize=(20, 10)):
        """
        Returns one plot with one single trace showing overall model performance.
        """
        if not self._fpr.get('micro') and not self._tpr.get('micro'):
            self._calculate_micro_rates()

        fig = plt.figure(figsize=figsize)
        plt.plot(self._fpr[2], self._tpr[2], color=color,
                 lw=lw, label=label % self._roc_auc[2])
        plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend(loc=legend_loc)
        return fig

    def _calculate_macro_rates(self):
        """
        Calculates macro rates for multi label roc curves plots.
        """
        # Elia: TO have a look
        # Ensure micro rates have been calculated
        # if not all([self._tpr.get(i) for i in range(len(self.classes))]):
        #     self.calculate_micro_rates()

        all_fpr = np.unique(np.concatenate([self._fpr[i] for i in range(len(self.classes))]))
        mean_tpr = np.zeros_like(all_fpr)

        for i in range(len(self.classes)):
            mean_tpr += np.interp(all_fpr, self._fpr[i], self._tpr[i])
            mean_tpr /= len(self.classes)

        self._fpr["macro"] = all_fpr
        self._tpr["macro"] = mean_tpr
        self._roc_auc["macro"] = auc(self._fpr["macro"], self._tpr["macro"])

    def plot_multi_label_roc_curves(self, color_micro_avg='deeppink', color_macro_avg='navy',
                         color_classes=('aqua', 'darkorange', 'cornflowerblue'),
                         xlabel='False Positive Rate', ylabel='True Positive Rate',
                         title='Receiver operating characteristic to multi-class',
                         legend_loc="lower right", lw=2, figsize=(20, 10)):
        """
        Plots multiple lines/traces one for each class found in the classification problem.
        Plot single roc curve first and after multilabel roc curves
        """
        # Elia: TO have a look
        #  Ensure before plotting multiple traces, that micro rates have been calculated.
        self._calculate_macro_rates()
        d = list(enumerate(self.classes))

        fig = plt.figure(figsize=figsize)
        plt.plot(self._fpr["micro"], self._tpr["micro"],
                 label='micro-average ROC curve (area = {0:0.2f})'
                       ''.format(self._roc_auc["micro"]),
                 color=color_micro_avg, linestyle=':', linewidth=4)

        plt.plot(self._fpr["macro"], self._tpr["macro"],
                 label='macro-average ROC curve (area = {0:0.2f})'
                       ''.format(self._roc_auc["macro"]),
                 color=color_macro_avg, linestyle=':', linewidth=4)

        colors = cycle(color_classes)
        for i, color in zip(range(len(self.classes)), colors):
            plt.plot(self._fpr[i], self._tpr[i], color=color, lw=lw,
                     label='ROC curve of class {0} (area = {1:0.2f})'
                           ''.format(d[i][1], self._roc_auc[i]))

        plt.plot([0, 1], [0, 1], 'k--', lw=lw)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend(loc=legend_loc)
        return fig
