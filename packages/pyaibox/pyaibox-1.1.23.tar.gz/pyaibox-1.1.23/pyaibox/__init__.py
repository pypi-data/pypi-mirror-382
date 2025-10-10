from __future__ import division, print_function, absolute_import
from .version import __version__


from .utils.const import *
from .utils.colors import rgb2gray, gray2rgb, ind2rgb, DISTINCT_COLORS_HEX, DISTINCT_COLORS_RGB, DISTINCT_COLORS_CMYK, DISTINCT_COLORS_RGB_NORM, BASE_COLORS, TABLEAU_COLORS, CSS4_COLORS
from .utils.colormaps import cmaps, viridis, parula
from .utils.convert import str2hash, file2hash, dict2str, str2bool, str2list, str2tuple, str2num, str2sec, int2bstr, bstr2int, gridnum, linfov, obs2pos, pos2obs, pos2spec, obs2spec
from .utils.ios import loadyaml, saveyaml, loadjson, loadmat, savemat, loadh5, saveh5, mvkeyh5, loadbin, savebin
from .utils.image import imread, imsave, histeq, imresize
from .utils.file import data_path, pkg_path, copyfile, copyfiles, listxfile, pathjoin, fileparts, writetxt, readtxt, readnum, readcsv, readsec
from .utils.plot_show import cplot, plots, Plots, plot, imshow, mesh, mshow
from .utils.docstr import rmcache, gpyi, dltccmt


from .base import baseops, arrayops, mathops, randomfunc
from .base.baseops import sub2ind, ind2sub, dimpos, dimpermute, dimreduce, dimmerge, rmcdim, upkeys, dreplace, dmka, strfind
from .base.arrayops import sl, cut, cat, arraycomb
from .base.mathops import mag2db, db2mag, fnab, ebeo, nextpow2, prevpow2, ematmul, matmul, r2c, c2r, conj, real, imag, angle, abs, pow, mean, var, std, cov, dot, log
from .base.randomfunc import setseed, randgrid, randperm, randperm2d
from .base.geometry import rad2deg, deg2rad, pol2car, car2pol, sph2car, car2sph
from .base.typevalue import peakvalue, dtypes


from .summary.loss_log import LossLog

from .evaluation.classification import categorical2onehot, onehot2categorical, accuracy, confusion, kappa, plot_confusion
from .evaluation.contrast import contrast
from .evaluation.entropy import entropy
from .evaluation.norm import fnorm, pnorm
from .evaluation.error import mse, sse, mae, sae, nmse, nsse, nmae, nsae
from .evaluation.snrs import snr, psnr
from .evaluation.detection_voc import bbox_iou, calc_detection_voc_ap, calc_detection_voc_prec_rec, eval_detection_voc

from .compression.huffman_coding import HuffmanNode, HuffmanCompressor, TextHuffmanCompressor, FileHuffmanCompressor, AdvancedHuffmanCompressor, get_file_size, calculate_compression_ratio

from .dsp.ffts import padfft, freq, fftfreq, fftshift, ifftshift, fft, ifft, fftx, ffty, ifftx, iffty
from .dsp.convolution import conv1, cutfftconv1, fftconv1
from .dsp.correlation import corr1, cutfftcorr1, fftcorr1, acorr, xcorr, accc
from .dsp.normalsignals import rect, chirp
from .dsp.interpolation1d import sinc, sinc_table, sinc_interp, interp
from .dsp.interpolation2d import interp2d
from .dsp.function_base import unwrap, unwrap2

from .misc.transform import standardization, scale, quantization, ct2rt, rt2ct, db20
from .misc.mapping_operation import mapping
from .misc.sampling import slidegrid, dnsampling, sample_tensor, shuffle_tensor, split_tensor, tensor2patch, patch2tensor, read_samples
from .misc.bounding_box import plot_bbox, fmt_bbox
from .misc.draw_shapes import draw_rectangle
from .misc.noising import awgns, awgns2, imnoise, awgn, wgn


from .datasets.mnist import read_mnist
from .datasets.mstar import mstar_header, mstar_raw

from .nn.activations import linear, sigmoid, tanh, softplus, softsign, elu, relu, relu6, selu, crelu, leaky_relu
from .ml.reduction_pca import pca
from .ml.dataset_visualization import visds 
 
