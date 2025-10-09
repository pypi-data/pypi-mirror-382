#!/usr/bin/env python3

import argparse
import pathlib

import pandas as pd

import gradescope_mean

parser = argparse.ArgumentParser(
    description='grade synthesis from gradescope (see doc at: https://github.com/matthigger/gradescope_mean/blob/main/readme.md)')
parser.add_argument('f_scope', type=str,
                    help='gradescope output csv (Assignments > Download Grades > CSV)')
parser.add_argument('--config', dest='f_config', action='store',
                    default=None,
                    help='yaml configuration (see doc at: https://github.com/matthigger/gradescope_mean/blob/main/doc/config.md)')
parser.add_argument('--plot', dest='f_hist', action='store',
                    default=None,
                    help='html of histogram plot per assignment category ('
                         'none generated if no html output file specified)')
parser.add_argument('--pca', dest='f_pca', action='store',
                    default=None,
                    help='html of principal component analysis on student'
                         'scores (none generated if no html output file '
                         'specified)')
parser.add_argument('--late_csv', dest='f_late_csv', action='store',
                    default=None,
                    help='csv of late days applied per assignment')
parser.add_argument('--per_student', dest='per_stud', action='store_true',
                    help='outputs csv per student')


def main(args=None):
    if args is None:
        args = parser.parse_args()

    # load config
    folder = pathlib.Path(args.f_scope).resolve().parent
    if args.f_config is None:
        config = gradescope_mean.Config.cli_copy_config(folder)
    else:
        config = gradescope_mean.Config.from_file(args.f_config)

    # process
    gradebook, df_grade_full = config(f_scope=args.f_scope)

    # output
    df_grade_full.to_csv(str(folder / 'grade_full.csv'))

    # outputs csv per student
    if args.per_stud:
        _folder = folder / 'per_student'
        _folder.mkdir(exist_ok=True)
        for idx, row in df_grade_full.iterrows():
            _df = pd.DataFrame(row)
            last = row['last name']
            first = row['first name']
            _df.to_csv(_folder / f'{last}_{first}.csv')

    # print late days to csv
    if args.f_late_csv is not None:
        f_late = folder / args.f_late_csv
        gradebook.df_lateday.to_csv(f_late.with_suffix('.csv'))

    # plot histogram (per category)
    if args.f_hist:
        fig = gradescope_mean.plot_hist(df_grade_full=df_grade_full,
                                        cat_weight_dict=config.cat_weight_dict)
        f_html = folder / args.f_hist
        fig.write_html(str(f_html), include_plotlyjs='cdn')

    # plot pca scatter
    if args.f_pca:
        point_dict = dict(zip(gradebook.ass_list,
                              gradebook.points))
        fig = gradescope_mean.plot_pca(df_grade_full=df_grade_full,
                                       cat_weight_dict=config.cat_weight_dict,
                                       point_dict=point_dict)
        f_pca = folder / args.f_pca
        fig.write_html(str(f_pca), include_plotlyjs='cdn')


if __name__ == '__main__':
    cmd_line = ['/home/matt/Dropbox/teach/DS4400/admin/grade/scope_oct8.csv',
                '--config',
                '/home/matt/Dropbox/teach/DS4400/admin/grade/config.yaml']
    main(parser.parse_args(cmd_line))

    # main()
