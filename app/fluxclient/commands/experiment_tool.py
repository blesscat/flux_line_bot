#!/usr/bin/env python3
import argparse
import logging
from re import findall
from time import time
import datetime

import numpy as np

from fluxclient.scanner.scan_settings import ScanSetting
from fluxclient.scanner.tools import read_pcd, write_stl, write_pcd
from fluxclient.scanner.pc_process import PcProcess


def show_pc(name, pc_in):
    return '{} size:{}'.format(name, len(pc_in[0]))


def sub_command(in_file, out_file, command=''):
    _PcProcess = PcProcess(ScanSetting())
    tmp = out_file.rfind('.')
    prefix, suffix = out_file[:tmp], out_file[tmp + 1:]
    print('out_file', prefix, suffix)

    _PcProcess.clouds['in'] = _PcProcess.to_cpp([read_pcd(in_file), []])
    print(show_pc('pc_in', _PcProcess.clouds['in']))
    # for i in findall('[A-Z][+-]?[0-9]+[.]?[0-9]*', command):
    for i in findall('[A-Z][a-z]?[+-]?[0-9]*[.]?[0-9]*', command):
        timestamp = datetime.datetime.fromtimestamp(time()).strftime('%H:%M:%S')
        if i.startswith('N'):
            _PcProcess.delete_noise('in', 'in', float(i[1:]))
            print(timestamp, show_pc('after noise del', _PcProcess.clouds['in']))
        elif i.startswith('P'):
            print(timestamp, 'converting to mesh....', end='')
            _PcProcess.to_mesh('in')
            suffix = 'stl'
            print('done')
        elif i.startswith('A'):
            print('adding at {}...'.format(float(i[2:])))
            _PcProcess.closure('in', 'in', float(i[2:]), i[1] == 'f')
            print('done')
        elif i.startswith('E'):
            print(timestamp, 'export file {}.{}'.format(prefix, suffix))
            tmp = _PcProcess.export('in', suffix)
            with open(prefix + '.' + suffix, 'wb') as f:
                f.write(tmp)
        elif i.startswith('C'):
            print('Clustering')
            if i[1] == 's':  # show the clustering
                thres = float(i[2:])
            else:
                thres = float(i[1:])
            pc = _PcProcess.clouds['in']
            # Euclidean_Cluster
            output = pc[0].Euclidean_Cluster(thres)
            output = sorted(output, key=lambda x: len(x))
            print('finish with {} cluster'.format(len(output)))

            tmp_pc = _PcProcess.to_cpp([[], []])
            if i[1] == 's':
                tmp_index = 0
            else:
                tmp_index = -1
            import random
            r = lambda: random.randint(0, 255)
            for j in output[tmp_index:]:
                c = [r(), r(), r()]
                for k in j:
                    p = _PcProcess.clouds['in'][0][k]
                    if i[1] == 's':
                        tmp_pc[0].push_backPoint(p[0], p[1], p[2], *c)
                    else:
                        tmp_pc[0].push_backPoint(*p)
            _PcProcess.clouds['in'] = tmp_pc


def main():
    parser = argparse.ArgumentParser(description='An experiment tool for scanning improve', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', '--input', help='input filename', required=True)
    parser.add_argument('-o', '--output', help='output filename', default='output.pcd')
    parser.add_argument('-c', '--command', default='', help='ex: N0.3PE\n'
                                                            'N[stddev]: noise del with dev [stddev]\n'
                                                            'P: Possion Meshing\n'
                                                            'A[fc][value]: add [floor] or [ceiling] at z = [value]'
                                                            'E: export file\n'
                                                            'C[s]?[value]: clustring points base on distance'
                        )
    args = parser.parse_args()

    if args.output is None:
        args.output = args.input[:-4] + "_out" + ".pcd"

    sub_command(args.input, args.output, args.command)
