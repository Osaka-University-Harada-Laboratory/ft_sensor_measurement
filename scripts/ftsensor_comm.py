#!/usr/bin python
# -*- coding: utf-8 -*-

import socket
import time
import struct
import numpy

FT_RAW_MAX = 10000.0
FXYZ_MAX   = 50.0
TXYZ_MAX   = 1.0
COEFF_GC   = 9.81

class FTsensor:
  def __init__(self, ip, port=10001, buffer_size=4096):
    self.ip = ip
    self.port = port
    self.buffer_size = buffer_size

    self.tcp_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.tcp_cli.connect((self.ip, self.port))


  def get_model_num(self):
    # display command of model name
    cmd = bytearray([0x10, 0x02, 0x04, 0xff, 0x2a, 0x00, 0x10, 0x03, 0xd2])
    self.tcp_cli.send(cmd)
    
    response = self.tcp_cli.recv(self.buffer_size)
    #print(response)
    model_num = bytearray(14)
    
    i = 0
    
    for d in response:
      if i >= 6 and i < 19:
        model_num[i - 6] = d
      i = i + 1

    model_num = model_num.decode()
    print(model_num)

    if 'SFS055YA500R6' in model_num:
      return 0
    else:
      return 1

  # ----- 6軸値の取得 ---- #
  def get_latest_data(self):

    # hand-shake mode command
    cmd = bytearray([0x10, 0x02, 0x04, 0xff, 0x30, 0x00, 0x10, 0x03, 0xc8])
    self.tcp_cli.send(cmd)

    response = self.tcp_cli.recv(self.buffer_size)

    # for byte in response:
    #     print(hex(byte), end=", ")
    # print(" $$ length: {}".format(len(response)))
    # print(response)
    if len(response) != 25:
      return None
    
    fx = bytes(response[6:7+1])
    fy = bytes(response[8:9+1])
    fz = bytes(response[10:11+1])
    mx = bytes(response[12:13+1])
    my = bytes(response[14:15+1])
    mz = bytes(response[16:17+1])

    status = response[20]

    fx = struct.unpack("<h", fx)
    fy = struct.unpack("<h", fy)
    fz = struct.unpack("<h", fz)
    mx = struct.unpack("<h", mx)
    my = struct.unpack("<h", my)
    mz = struct.unpack("<h", mz)

    ft_val = numpy.array([fx, fy, fz, mx, my, mz])
    f_val = ft_val[:3] / FT_RAW_MAX * FXYZ_MAX
    t_val = ft_val[-3:] / FT_RAW_MAX * TXYZ_MAX
    return numpy.concatenate([f_val, t_val])

