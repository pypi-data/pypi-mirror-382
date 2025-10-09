import pandas as pd


def canvas_merge(f_canvas, df_grade, del_col_list=None,
                 rm_gradescope_meta=True, scale100=True):
    """ merges canvas and gradescope data

    Args:
        f_canvas (str): canvas csv output
        df_grade (pd.DataFrame): processed grades, consistent with
            gradebook.average() output
        del_col_list (list): list of columns to delete from final output csv
        rm_gradescope_meta (bool): if True, removes the following columns (
            default meta data from pipeline):
            'firstname', 'lastname', 'sid', 'sections', 'sid (banner)'
        scale100 (bool): if True, scales grades by 100 (canvas displays with
            precision 2 and rounds this final value ...)

    Returns:
        df_canvas_out (pd.DataFrame): canvas consistent dataframe of grades
    """

    if del_col_list is None:
        del_col_list = list()

    if rm_gradescope_meta:
        del_col_list += ['firstname', 'lastname', 'sid', 'sections']

    # we discard all canvas grades
    N_COL_CANVAS_META = 5

    # load df_canvas & merge
    df_canvas = pd.read_csv(f_canvas)
    df_canvas = df_canvas.iloc[:, :N_COL_CANVAS_META]

    # merge
    df_canvas.set_index('SIS User ID', inplace=True)
    df_grade.set_index('sid', inplace=True)
    df_canvas_out = df_canvas.merge(df_grade,
                                    left_index=True,
                                    right_index=True,
                                    how='left')

    def print_missing(df, idx_missing, msg, n_cols=3):
        if not idx_missing:
            print('<no students>')
        print(msg)
        for idx in idx_missing:
            print(df.loc[idx, :].iloc[:n_cols].to_dict())

    # find and print canvas students not in gradescope
    idx_missing = set(df_canvas.index) - set(df_grade.index)
    print_missing(df=df_canvas,
                  idx_missing=idx_missing,
                  msg='students in canvas, not in gradescope:')

    idx_missing = set(df_grade.index) - set(df_canvas.index)
    print_missing(df=df_grade,
                  idx_missing=idx_missing,
                  msg='students in gradescope, not in canvas:')

    # strip out any missing data
    df_canvas_out.index.name = 'sid'
    df_canvas_out.reset_index(inplace=True)
    for col in del_col_list:
        del df_canvas_out[col]

    if scale100:
        for col in df_canvas_out.columns[N_COL_CANVAS_META:]:
            if 'late days remain' in col:
                # don't scale late days
                continue
            dtype = df_canvas_out[col].dtype
            if pd.api.types.is_numeric_dtype(dtype):
                df_canvas_out[col] = df_canvas_out[col] * 100

    return df_canvas_out