#!/usr/bin/env python
#-*- coding: utf-8 -*-
# @file      : demo_docstring.py
# @author    : Zhi Liu
# @email     : zhiliu.mind@gmail.com
# @homepage  : http://iridescent.ink
# @date      : Sun May 01 2023
# @version   : 0.0
# @license   : The GNU General Public License (GPL) v3.0
# @note      : 
# 
# The GNU General Public License (GPL) v3.0
# Copyright (C) 2013- Zhi Liu
#
# This file is part of pyaibox.
#
# pyaibox is free software: you can redistribute it and/or modify it under the 
# terms of the GNU General Public License as published by the Free Software Foundation, 
# either version 3 of the License, or (at your option) any later version.
#
# pyaibox is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with pyaibox. 
# If not, see <https://www.gnu.org/licenses/>. 
#

import pyaibox as pb


pkgdir = '/mnt/e/ws/github/antsfamily/torchcs/torchcsc/torchcs/'
# pkgdir = '/mnt/e/ws/github/antsfamily/torchtsa/torchtsac/torchtsa/'
pkgdir = '/mnt/e/ws/github/antsfamily/torchbox/torchboxc/torchbox/'
# pkgdir = '/mnt/e/ws/github/antsfamily/torchsar/torchsarc/torchsar/'
pkgdir = '/mnt/e/ws/github/antsfamily/pyaibox/pyaiboxc/pyaibox/'
pkgdir = '/mnt/e/ws/github/antsfamily/dpgbox/dpgboxc/dpgbox/'
# pkgdir = '/mnt/e/ws/github/antsfamily/torchsar/torchsar_deploy/torchsar/'

pb.dltccmt(pkgdir)
pb.rmcache(pkgdir, exts='.py')




