#!/usr/bin/env python3

import argparse
from datetime import datetime

import pandas as pd

import gradescope_mean

parser = argparse.ArgumentParser(description='preps csv for canvas upload ('
                                             'https://github.com/matthigger/gradescope_mean/blob/main/doc/upload_canvas.md)')
parser.add_argument('grade_full', type=str,
                    help='output csv of gradescope_mean CLI')
parser.add_argument('canvas', type=str,
                    help='csv of grades downloaded from canvas ')
parser.add_argument('--scale100', dest='scale100', action='store_true',
                    help='canvas has 2 decimal places of precision and they '
                         'round the final decimal place which is ambiguous '
                         'for students.  passing this flag will scale output by'
                         '100 (grades are between 0-100) which mitigates this')


def main(args=None):
    if args is None:
        args = parser.parse_args()

    df_grade_full = pd.read_csv(args.grade_full)

    df_canvas_out = gradescope_mean.canvas_merge(f_canvas=args.canvas,
                                                 df_grade=df_grade_full,
                                                 rm_gradescope_meta=True,
                                                 scale100=args.scale100)

    # output csv
    timestamp = datetime.now().strftime('%b%d_%H%M')
    f_canvas_out = args.canvas.replace('.csv', f'{timestamp}.csv')
    df_canvas_out.to_csv(f_canvas_out, index=False)


if __name__ == '__main__':
    main()
