import numpy as np
import pyaibox as pb

x = [1, 2, 3, 4, 5, 6]
y = np.fft.fftshift(x)
print(y)
y = pb.fftshift(x)
print(y)

x = [1, 2, 3, 4, 5, 6, 7]
y = np.fft.fftshift(x)
print(y)
y = pb.fftshift(x)
print(y)


x = [1, 2, 3, 4, 5, 6]
y = np.fft.ifftshift(x)
print(y)
y = pb.ifftshift(x)
print(y)

x = [1, 2, 3, 4, 5, 6, 7]
y = np.fft.ifftshift(x)
print(y)
y = pb.ifftshift(x)
print(y)


# shift all axes

axis = (0, 1)
# axis = 0
axis = 1

x = [[1, 2, 3, 4, 5, 6], [0, 2, 3, 4, 5, 6]]
y = np.fft.fftshift(x, axis)
print(y)
y = pb.fftshift(x, axis=axis)
print(y)


x = [[1, 2, 3, 4, 5, 6, 7], [0, 2, 3, 4, 5, 6, 7]]
y = np.fft.fftshift(x, axis)
print(y)
y = pb.fftshift(x, axis=axis)
print(y)


x = [[1, 2, 3, 4, 5, 6], [0, 2, 3, 4, 5, 6]]
y = np.fft.ifftshift(x, axis)
print(y)
y = pb.ifftshift(x, axis=axis)
print(y)


x = [[1, 2, 3, 4, 5, 6, 7], [0, 2, 3, 4, 5, 6, 7]]
y = np.fft.ifftshift(x, axis)
print(y)
y = pb.ifftshift(x, axis=axis)
print(y)
