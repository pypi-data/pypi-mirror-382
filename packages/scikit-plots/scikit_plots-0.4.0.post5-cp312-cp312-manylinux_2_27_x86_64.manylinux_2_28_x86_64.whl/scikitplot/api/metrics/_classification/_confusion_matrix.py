"""
The :mod:`~scikitplot.metrics` module includes plots for machine learning
evaluation metrics e.g. confusion matrix, silhouette scores, etc.

The Scikit-plots Functional API

This package/module is designed to be compatible with both Python 2 and Python 3.
The imports below ensure consistent behavior across different Python versions by
enforcing Python 3-like behavior in Python 2.
"""

# Authors: The scikit-plots developers
# SPDX-License-Identifier: BSD-3-Clause

# pylint: disable=import-error
# pylint: disable=broad-exception-caught

# code that needs to be compatible with both Python 2 and Python 3
from __future__ import (
    absolute_import,  # Ensures that all imports are absolute by default, avoiding ambiguity.
    division,  # Changes the division operator `/` to always perform true division.
    print_function,  # Treats `print` as a function, consistent with Python 3 syntax.
    unicode_literals,  # Makes all string literals Unicode by default, similar to Python 3.
)

# import json
import itertools

# import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
)
from sklearn.utils.multiclass import unique_labels

from ..._utils._helpers import (
    validate_labels,
)
from ..._utils.validation import (
    validate_plotting_kwargs_decorator,
)
from ....utils.utils_plot_mpl import save_plot_decorator
from ...._docstrings import _docstring

## Define __all__ to specify the public interface of the module,
# not required default all above func
__all__ = [
    "plot_confusion_matrix",
    "plot_classifier_eval",
]


@validate_plotting_kwargs_decorator
@save_plot_decorator
@_docstring.interpd
def plot_confusion_matrix(
    y_true,
    y_pred,
    *,
    labels=None,
    true_labels=None,
    pred_labels=None,
    normalize=False,
    hide_zeros=False,
    hide_counts=False,
    title=None,
    title_fontsize="large",
    text_fontsize="medium",
    x_tick_rotation=0,
    cmap="Blues",
    show_colorbar=True,
    **kwargs,
):
    """
    Generates a confusion matrix plot from predictions and true labels.

    The confusion matrix is a summary of prediction results that shows the counts of true
    and false positives and negatives for each class. This function also provides options for
    normalizing, hiding zero values, and customizing the plot appearance.

    Parameters
    ----------
    y_true : array-like, shape (n_samples,)
        Ground truth (correct) target values.

    y_pred : array-like, shape (n_samples,)
        Estimated targets as returned by a classifier.

    labels : array-like, shape (n_classes), optional
        List of labels to index the matrix. This may be used to reorder or select a subset
        of labels. If None, labels appearing at least once in `y_true` or `y_pred` are used
        in sorted order. (new in v0.2.5)

    true_labels : array-like, optional
        The true labels to display. If None, all labels are used.

    pred_labels : array-like, optional
        The predicted labels to display. If None, all labels are used.

    normalize : bool, optional, default=False
        If True, normalizes the confusion matrix before plotting.

    hide_zeros : bool, optional, default=False
        If True, cells containing a value of zero are not plotted.

    hide_counts : bool, optional, default=False
        If True, counts are not overlaid on the plot.

    title : string, optional
        Title of the generated plot. Defaults to "Confusion Matrix" if `normalize` is True.
        Otherwise, defaults to "Normalized Confusion Matrix".

    title_fontsize : string or int, optional, default="large"
        Font size for the plot title. Use "small", "medium", "large", or integer values.

    text_fontsize : string or int, optional, default="medium"
        Font size for text in the plot. Use "small", "medium", "large", or integer values.

    x_tick_rotation : int, optional, default=0
        Rotates x-axis tick labels by the specified angle. Useful when labels overlap.

    cmap : None, str or matplotlib.colors.Colormap, optional, default=None
        Colormap used for plotting.
        Options include 'viridis', 'PiYG', 'plasma', 'inferno', 'nipy_spectral', etc.
        See Matplotlib Colormap documentation for available choices.

        - https://matplotlib.org/stable/users/explain/colors/index.html
        - plt.colormaps()
        - plt.get_cmap()  # None == 'viridis'

    show_colorbar : bool, optional, default=True
        If False, the colorbar is not displayed.

        .. versionadded:: 0.3.9

    **kwargs: dict
        Generic keyword arguments.

    Other Parameters
    ----------------
    %(_validate_plotting_kwargs_doc)s

    %(_save_plot_decorator_kwargs_doc)s

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes on which the plot was drawn.

    Notes
    -----
    Ensure that `y_true` and `y_pred` have the same shape and contain valid class labels.
    The `normalize` parameter applies only to the confusion matrix plot. Adjust `cmap` and
    `x_tick_rotation` to customize the appearance of the plot. The `show_colorbar` parameter
    controls whether a colorbar is displayed.

    Examples
    --------

    .. plot::
       :context: close-figs
       :align: center
       :alt: Confusion Matrix

        >>> from sklearn.datasets import load_digits as data_10_classes
        >>> from sklearn.model_selection import train_test_split
        >>> from sklearn.naive_bayes import GaussianNB
        >>> import scikitplot as skplt
        >>> X, y = data_10_classes(return_X_y=True, as_frame=False)
        >>> X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.5, random_state=0)
        >>> model = GaussianNB()
        >>> model.fit(X_train, y_train)
        >>> y_val_pred = model.predict(X_val)
        >>> skplt.metrics.plot_confusion_matrix(
        >>>     y_val, y_val_pred,
        >>> );
    """
    ##################################################################
    ## Preprocessing
    ##################################################################
    # Proceed with your preprocess logic here
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    cm = confusion_matrix(y_true, y_pred, labels=labels)
    if labels is None:
        classes = unique_labels(y_true, y_pred)
    else:
        classes = np.asarray(labels)

    if normalize:
        cm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
        cm = np.around(cm, decimals=2)
        cm[np.isnan(cm)] = 0.0

    if true_labels is None:
        true_classes = classes
    else:
        validate_labels(classes, true_labels, "true_labels")

        true_label_indexes = np.isin(classes, true_labels)

        true_classes = classes[true_label_indexes]
        cm = cm[true_label_indexes]

    if pred_labels is None:
        pred_classes = classes
    else:
        validate_labels(classes, pred_labels, "pred_labels")

        pred_label_indexes = np.isin(classes, pred_labels)

        pred_classes = classes[pred_label_indexes]
        cm = cm[:, pred_label_indexes]

    ##################################################################
    ## Plotting
    ##################################################################
    # fig, ax = validate_plotting_kwargs(
    #     ax=ax, fig=fig, figsize=figsize, subplot_position=111
    # )
    # Set title, labels, and formatting
    _fig, ax = kwargs.get("fig"), kwargs.get("ax")
    image = ax.imshow(cm, interpolation="nearest", cmap=plt.get_cmap(cmap))
    if show_colorbar is True:
        plt.colorbar(mappable=image)

    thresh = cm.max() / 2.0

    if not hide_counts:
        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            if not (hide_zeros and cm[i, j] == 0):
                ax.text(
                    j,
                    i,
                    cm[i, j],
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontsize=text_fontsize,
                    color="white" if cm[i, j] > thresh else "black",
                )
    if title:
        ax.set_title(title, fontsize=title_fontsize)
    elif normalize:
        ax.set_title("Normalized Confusion Matrix", fontsize=title_fontsize)
    else:
        ax.set_title("Confusion Matrix", fontsize=title_fontsize)
    ax.set_xlabel("Predicted label", fontsize=text_fontsize)
    ax.set_ylabel("True label", fontsize=text_fontsize)

    x_tick_marks = np.arange(len(pred_classes))
    y_tick_marks = np.arange(len(true_classes))
    ax.set_xticks(x_tick_marks)
    ax.set_xticklabels(pred_classes, fontsize=text_fontsize, rotation=x_tick_rotation)
    ax.set_yticks(y_tick_marks)
    ax.set_yticklabels(true_classes, fontsize=text_fontsize)

    ax.grid(False)
    return ax


@validate_plotting_kwargs_decorator
@save_plot_decorator
@_docstring.interpd
def plot_classifier_eval(
    ## default params
    y_true,
    y_pred,
    *,
    labels=None,
    normalize=None,
    digits=3,
    ## plotting params
    title="train",
    title_fontsize="large",
    text_fontsize="medium",
    cmap=None,
    # heatmap
    x_tick_rotation=0,
    # add docstr
    figsize=(8, 3),
    nrows=1,
    ncols=2,
    index=2,
    ## additional params
    **kwargs,
):
    """
    Generates various evaluation plots for a classifier, including confusion matrix,
    precision-recall curve, and ROC curve.

    This function provides a comprehensive view of a classifier's performance through
    multiple plots, helping in the assessment of its effectiveness
    and areas for improvement.

    Parameters
    ----------
    y_true : array-like, shape (n_samples,)
        Ground truth (correct) target values.

    y_pred : array-like, shape (n_samples,)
        Predicted target values from the classifier.

    labels : list of string, optional
        List of labels for the classes.
        If None, labels are automatically generated based on the class indices.

    normalize : {'true', 'pred', 'all', None}, optional
        Normalizes the confusion matrix according to the specified mode. Defaults to None.

        - 'true': Normalizes by true (actual) values.
        - 'pred': Normalizes by predicted values.
        - 'all': Normalizes by total values.
        - None: No normalization.

    digits : int, optional, default=3
        Number of digits for formatting floating point values in the plots.

    title : string, optional, default='train'
        Title of the generated plot.

    title_fontsize : string or int, optional, default="large"
        Font size for the plot title.
        Use e.g. "small", "medium", "large" or integer values.

    text_fontsize : string or int, optional, default="medium"
        Font size for the text in the plot.
        Use e.g. "small", "medium", "large" or integer values.

    cmap : None, str or matplotlib.colors.Colormap, optional, default=None
        Colormap used for plotting.
        Options include 'viridis', 'PiYG', 'plasma', 'inferno', 'nipy_spectral', etc.
        See Matplotlib Colormap documentation for available choices.

        - https://matplotlib.org/stable/users/explain/colors/index.html
        - plt.colormaps()
        - plt.get_cmap()  # None == 'viridis'

    x_tick_rotation : int, optional, default=0
        Rotates x-axis tick labels by the specified angle.

        .. versionadded:: 0.3.9

    **kwargs: dict
        Generic keyword arguments.

    Other Parameters
    ----------------
    %(_validate_plotting_kwargs_doc)s

    %(_save_plot_decorator_kwargs_doc)s

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure on which the plot was drawn.

    Notes
    -----
    The function generates and displays multiple evaluation plots. Ensure that `y_true` and `y_pred`
    have the same shape and contain valid class labels. The `normalize` parameter is applicable
    to the confusion matrix plot. Adjust `cmap` and `x_tick_rotation` to customize the appearance
    of the plots.


    .. dropdown:: References

      * `"scikit-learn classification_report"
        <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html#>`_.

      * `"scikit-learn confusion_matrix"
        <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html#>`_.

    Examples
    --------

    .. plot::
       :context: close-figs
       :align: center
       :alt: Confusion Matrix

        >>> from sklearn.datasets import load_digits as data_10_classes
        >>> from sklearn.model_selection import train_test_split
        >>> from sklearn.naive_bayes import GaussianNB
        >>> import scikitplot as skplt
        >>> X, y = data_10_classes(return_X_y=True, as_frame=False)
        >>> X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.5, random_state=0)
        >>> model = GaussianNB()
        >>> model.fit(X_train, y_train)
        >>> y_val_pred = model.predict(X_val)
        >>> skplt.metrics.plot_classifier_eval(
        >>>     y_val, y_val_pred,
        >>>     title='val',
        >>> );
    """
    ##################################################################
    ## Preprocessing
    ##################################################################
    # Proceed with your preprocess logic here
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    classes = unique_labels(y_true, y_pred)
    if labels is None:
        labels = classes
    else:
        labels = np.array(labels)
        validate_labels(classes, labels, "labels")

    # Generate the classification report
    report = classification_report(
        y_true,
        y_pred,
        labels=labels,
        digits=digits,
        zero_division=np.nan,
    )
    # Generate the confusion matrix
    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=labels,
        normalize=normalize,
    )
    cm = np.around(cm, decimals=2)

    ##################################################################
    ## Plotting
    ##################################################################
    # Proceed with your plotting logic here
    fig, ax = kwargs.get("fig"), kwargs.get("ax")
    # Plot the classification report on the first subplot
    ax[0].axis("off")
    ax[0].set_title(f"{title.capitalize()} Classification Report\n", fontsize=11)
    ax[0].text(
        0,
        0.5,
        "\n" * 3 + str(report),
        ha="left",
        va="center",
        fontfamily="monospace",
        fontsize=8,
    )

    # Choose a colormap
    cmap_ = plt.get_cmap(cmap)

    # Plot the confusion matrix on the second subplot
    cax = ax[1].matshow(cm, cmap=cmap_, aspect="auto")

    # Remove the edge of the matshow
    ax[1].spines["top"].set_visible(False)
    ax[1].spines["bottom"].set_visible(False)
    ax[1].spines["left"].set_visible(False)
    ax[1].spines["right"].set_visible(False)

    # Also remove the colorbar edge
    cbar = fig.colorbar(mappable=cax, ax=ax[1])
    cbar.outline.set_edgecolor("none")

    # Annotate the matrix with dynamic text color
    threshold = cm.max() / 2.0
    for (i, j), val in np.ndenumerate(cm):
        # val == cm[i, j]
        cmap_method = cmap_.get_over if val > threshold else cmap_.get_under
        # Get the color at the top end of the colormap
        rgba = cmap_method()  # Get the RGB values

        # Calculate the luminance of this color
        luminance = 0.2126 * rgba[0] + 0.7152 * rgba[1] + 0.0722 * rgba[2]

        # If luminance is low (dark color), use white text; otherwise, use black text
        text_color = {True: "w", False: "k"}[(luminance < 0.5)]
        ax[1].text(
            j,
            i,
            f"{val}",
            ha="center",
            va="center",
            fontsize=text_fontsize,
            color=text_color,
        )

    # Set title and axis labels
    ax[1].set_title(f"{title.capitalize()} Confusion Matrix\n", fontsize=title_fontsize)
    ax[1].set_xlabel("Predicted Labels", fontsize=text_fontsize)
    ax[1].set_ylabel("True Labels", fontsize=text_fontsize)
    # Set class labels for x and y axis
    ax[1].set_xticks(np.arange(len(labels)))
    ax[1].set_yticks(np.arange(len(labels)))
    ax[1].set_xticklabels(
        labels,
        fontsize=text_fontsize,
    )
    ax[1].set_yticklabels(labels, fontsize=text_fontsize, rotation=x_tick_rotation)

    # Move x-axis labels to the bottom and y-axis labels to the right
    ax[1].xaxis.set_label_position("bottom")
    ax[1].xaxis.tick_bottom()
    ax[1].yaxis.set_label_position("left")
    ax[1].yaxis.tick_left()

    # Adjust layout with additional space
    plt.tight_layout()
    fig.tight_layout()
    # Show the plot
    # plt.show()
    return fig
