def plot_bbox(bboxes, labels=None, scores=None, edgecolors=None, linewidths=1, fontdict=None, textpos='TopCenter', offset=None, ax=None):
    r"""Plots bounding boxes with scores and labels


    Parameters
    ----------
    bboxes : list or numpy array
        The bounding boxes, in ``LeftTopRightBottom`` mode, which means (xmin, ymin, xmax, ymax)
    labels : list or None, optional
        The labels, can be a list of class id or class name. If None, won't show labels.
    scores : list or None, optional
        The scores, can be a list of float numbers. If None, won't show labels.
    edgecolors : None, optional
        The edgecolors for bounding boxes.
    linewidths : int, optional
        The linewidths for bounding boxes.
    fontdict : None, optional
        The fontdict for labels and scores.
    textpos : str, optional
        The position for text (labels and scores).
    offset : None, optional
        The offset for text (labels and scores).
    ax : None, optional
        The ``ax`` handle, If None, auto generated.

    Returns
    -------
    ax
        The ``ax`` handle

    see :func:`fmt_bbox`

    Example
    -------

    Plot bounding boxes with scores and labels on an image.

    .. image:: ./_static/demo_plot_bboxes.png
       :scale: 100 %
       :align: center

    The results shown in the above figure can be obtained by the following codes.

    ::

        import pyaibox as pl
        import matplotlib.pyplot as plt

        bboxes = [[100, 100, 200, 200], [300, 300, 400, 500]]
        labels = ['dog', 'cat']
        scores = [0.987, None]
        edgecolors = [list(pb.DISTINCT_COLORS_RGB_NORM.values())[0], None]
        edgecolors = list(pb.DISTINCT_COLORS_RGB_NORM.values())[0:2]
        linewidths = [2, 4]

        fontdict = {'family': 'Times New Roman',
                    'style': 'italic',
                    'weight': 'normal',
                    'color': 'darkred',
                    'size': 12,
                    }

        x = pb.imread('../../data/images/LenaRGB512.tif')
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.imshow(x)

        pb.plot_bbox(bboxes, labels=labels, scores=scores, edgecolors=edgecolors, linewidths=linewidths, fontdict=fontdict, textpos='TopLeft', ax=ax)
        plt.axis('off')
        plt.savefig('./bbbox.png', bbox_inches='tight', pad_inches=0)
        plt.show()

    """

# def fmt_bbox(bboxes, dtype='LTRB2CHW'):
#     r"""Formats bounding boxes

#     .. warning:: The height and width are computed by :math:`y_{\rm max} - y_{\rm min}` and :math:`x_{\rm max} - x_{\rm min}`.


#     Parameters
#     ----------
#     bboxes : list or numpy array
#         The bounding boxes to be converted, all bboxes have the same mode.
#     dtype : str, optional
#         - ``'LTRB2TLBR'``: LeftTopRightBottom (xmin, ymin, xmax, ymax) --> TopLeftBottomRight (ymin, xmin, ymax, xmax)
#         - ``'TLBR2LTRB'``: TopLeftBottomRight (ymin, xmin, ymax, xmax) --> LeftTopRightBottom (xmin, ymin, xmax, ymax)
#         - ``'CWH2CHW'``: CenterWidthHeight (x, y, w, h) --> CenterHeightWidth (y, x, h, w)
#         - ``'CHW2CWH'``: CenterHeightWidth (y, x, h, w) --> CenterWidthHeight (x, y, w, h)
#         - ``'LTRB2CWH'``: LeftTopRightBottom (xmin, ymin, xmax, ymax) --> CenterWidthHeight (x, y, w, h)
#         - ``'LTRB2CHW'``: LeftTopRightBottom (xmin, ymin, xmax, ymax) --> CenterHeightWidth (y, x, h, w)
#         - ``'TLBR2CWH'``: TopLeftBottomRight (ymin, xmin, ymax, xmax) --> CenterWidthHeight (x, y, w, h)
#         - ``'TLBR2CHW'``: TopLeftBottomRight (ymin, xmin, ymax, xmax) --> CenterHeightWidth (y, x, h, w)
#         - ``'CWH2LTRB'``: CenterWidthHeight (x, y, w, h) --> LeftTopRightBottom (xmin, ymin, xmax, ymax)
#         - ``'CWH2TLBR'``: CenterWidthHeight (x, y, w, h) --> TopLeftBottomRight (ymin, xmin, ymax, xmax)
#         - ``'CHW2LTRB'``: CenterHeightWidth (y, x, h, w) --> LeftTopRightBottom (xmin, ymin, xmax, ymax)
#         - ``'CHW2TLBR'``: CenterHeightWidth (y, x, h, w) --> TopLeftBottomRight (ymin, xmin, ymax, xmax)
#         - ``'LRTB2LTRB'``: LeftRightTopBottom (xmin, xmax, ymin, ymax) --> LeftTopRightBottom (xmin, ymin, xmax, ymax)
#         - ``'LRTB2TLBR'``: LeftRightTopBottom (xmin, xmax, ymin, ymax) --> TopLeftBottomRight (ymin, xmin, ymax, xmax)
#         - ``'LTRB2LRTB'``: LeftTopRightBottom (xmin, ymin, xmax, ymax) --> LeftRightTopBottom (xmin, xmax, ymin, ymax)
#         - ``'LRTB2CWH'``: LeftRightTopBottom (xmin, xmax, ymin, ymax) --> CenterWidthHeight (x, y, w, h)
#         - ``'LRTB2CHW'``: LeftRightTopBottom (xmin, xmax, ymin, ymax) --> CenterHeightWidth (y, x, h, w)
#         - ``'CWH2LRTB'``: CenterWidthHeight (x, y, w, h) --> LeftRightTopBottom (xmin, xmax, ymin, ymax)
#         - ``'CHW2LRTB'``: CenterHeightWidth (y, x, h, w) --> LeftRightTopBottom (xmin, xmax, ymin, ymax)

#     Returns
#     -------
#     list or numpy array
#         The formated bounding boxes.

#     see :func:`plot_bbox`

#     """

def fmt_bbox(bboxes, dtype='LTRB2CHW'):
    r"""Formats bounding boxes

    .. warning:: The height and width are computed by :math:`y_{\rm max} - y_{\rm min}` and :math:`x_{\rm max} - x_{\rm min}`.


    Parameters
    ----------
    bboxes : list or numpy array
        The bounding boxes to be converted, all bboxes have the same mode.
    dtype : str, optional
        - ``'LTRB2TLBR'``: LeftTopRightBottom (xmin, ymin, xmax, ymax) --> TopLeftBottomRight (ymin, xmin, ymax, xmax)
        - ``'TLBR2LTRB'``: TopLeftBottomRight (ymin, xmin, ymax, xmax) --> LeftTopRightBottom (xmin, ymin, xmax, ymax)
        - ``'CWH2CHW'``: CenterWidthHeight (x, y, w, h) --> CenterHeightWidth (y, x, h, w)
        - ``'CHW2CWH'``: CenterHeightWidth (y, x, h, w) --> CenterWidthHeight (x, y, w, h)
        - ``'LTRB2CWH'``: LeftTopRightBottom (xmin, ymin, xmax, ymax) --> CenterWidthHeight (x, y, w, h)
        - ``'LTRB2CHW'``: LeftTopRightBottom (xmin, ymin, xmax, ymax) --> CenterHeightWidth (y, x, h, w)
        - ``'TLBR2CWH'``: TopLeftBottomRight (ymin, xmin, ymax, xmax) --> CenterWidthHeight (x, y, w, h)
        - ``'TLBR2CHW'``: TopLeftBottomRight (ymin, xmin, ymax, xmax) --> CenterHeightWidth (y, x, h, w)
        - ``'CWH2LTRB'``: CenterWidthHeight (x, y, w, h) --> LeftTopRightBottom (xmin, ymin, xmax, ymax)
        - ``'CWH2TLBR'``: CenterWidthHeight (x, y, w, h) --> TopLeftBottomRight (ymin, xmin, ymax, xmax)
        - ``'CHW2LTRB'``: CenterHeightWidth (y, x, h, w) --> LeftTopRightBottom (xmin, ymin, xmax, ymax)
        - ``'CHW2TLBR'``: CenterHeightWidth (y, x, h, w) --> TopLeftBottomRight (ymin, xmin, ymax, xmax)
        - ``'LRTB2LTRB'``: LeftRightTopBottom (xmin, xmax, ymin, ymax) --> LeftTopRightBottom (xmin, ymin, xmax, ymax)
        - ``'LRTB2TLBR'``: LeftRightTopBottom (xmin, xmax, ymin, ymax) --> TopLeftBottomRight (ymin, xmin, ymax, xmax)
        - ``'LTRB2LRTB'``: LeftTopRightBottom (xmin, ymin, xmax, ymax) --> LeftRightTopBottom (xmin, xmax, ymin, ymax)
        - ``'LRTB2CWH'``: LeftRightTopBottom (xmin, xmax, ymin, ymax) --> CenterWidthHeight (x, y, w, h)
        - ``'LRTB2CHW'``: LeftRightTopBottom (xmin, xmax, ymin, ymax) --> CenterHeightWidth (y, x, h, w)
        - ``'CWH2LRTB'``: CenterWidthHeight (x, y, w, h) --> LeftRightTopBottom (xmin, xmax, ymin, ymax)
        - ``'CHW2LRTB'``: CenterHeightWidth (y, x, h, w) --> LeftRightTopBottom (xmin, xmax, ymin, ymax)

    Returns
    -------
    list or numpy array
        The formated bounding boxes.

    see :func:`plot_bbox`

    """


