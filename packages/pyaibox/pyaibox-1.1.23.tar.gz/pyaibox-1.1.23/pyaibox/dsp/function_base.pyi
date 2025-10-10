def unwrap(x, discont=pb.PI, axis=-1):
    r"""Unwrap by changing deltas between values to :math:`2\pi` complement.

    Unwrap radian phase `x` by changing absoluted jumps greater than
    `discont` to their :math:`2\pi` complement along the given axis.

    Parameters
    ----------
    x : ndarray
        The input.
    discont : float, optional
        Maximum discontinuity between values, default is :math:`\pi`.
    axis : int, optional
        Axis along which unwrap will operate, default is the last axis.

    Returns
    -------
    ndarray
        The unwrapped.
    
    Examples
    --------

    ::

        x = np.array([3.14, -3.12, 3.12, 3.13, -3.11])
        y_np = unwrap(x)
        print(y_np, y_np.shape, type(y_np))

        # output

        array([3.1400, 3.1632, 3.1200, 3.1300, 3.1732], dtype=np.float64) torch.Size([5]) <class 'torch.Tensor'>

    """

def unwrap2(x, discont=pb.PI, axis=-1):
    r"""Unwrap by changing deltas between values to :math:`2\pi` complement.

    Unwrap radian phase `x` by changing absoluted jumps greater than
    `discont` to their :math:`2\pi` complement along the given axis. The elements
    are divided into 2 parts (with equal length) along the given axis.
    The first part is unwrapped in inverse order, while the second part
    is unwrapped in normal order.

    Parameters
    ----------
    x : Tensor
        The input.
    discont : float, optional
        Maximum discontinuity between values, default is :math:`\pi`.
    axis : int, optional
        Axis along which unwrap will operate, default is the last axis.

    Returns
    -------
    Tensor
        The unwrapped.

    see :func:`unwrap`

    Examples
    --------

    ::

        x = np.array([3.14, -3.12, 3.12, 3.13, -3.11])
        y = unwrap(x)
        print(y, y.shape, type(y))

        print("------------------------")
        x = np.array([3.14, -3.12, 3.12, 3.13, -3.11])
        x = np.concatenate((x[::-1], x), axis=0)
        print(x)
        y = unwrap2(x)
        print(y, y.shape, type(y))

        # output
        [3.14       3.16318531 3.12       3.13       3.17318531] (5,) <class 'numpy.ndarray'>
        ------------------------
        [3.17318531 3.13       3.12       3.16318531 3.14       3.14
        3.16318531 3.12       3.13       3.17318531] (10,) <class 'numpy.ndarray'>
    
    """


