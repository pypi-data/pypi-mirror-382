import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_hist(df_grade_full, cat_weight_dict):
    """ plots a histogram of grades

    example:
    https://github.com/matthigger/gradescope_mean/blob/main/doc/hist.png

    Args:
        df_grade_full (pd.DataFrame):
        cat_weight_dict (dict): keys are categories, values are weights

    Returns:
        fig (plotly):
    """

    # always plot mean grade histogram
    feat_list = ['mean']
    if cat_weight_dict is not None:
        # plot histogram per category (if specified)
        feat_list += [f'mean_{feat}' for feat in cat_weight_dict.keys()]

    # make histogram subplots
    fig = make_subplots(cols=len(feat_list), rows=1, subplot_titles=feat_list)
    for col_idx, feat in enumerate(feat_list):
        trace = go.Histogram(y=df_grade_full[feat], name='feat',
                             ybins=dict(start=.5, end=1, size=.025),
                             opacity=0.75)
        fig.append_trace(trace, col=col_idx + 1, row=1)

        mean = df_grade_full[feat].mean()
        fig.add_hline(y=mean, annotation_text=f'mean: {mean:.3f}',
                      col=col_idx + 1, row=1)
    fig.update_layout(showlegend=False)

    return fig


def plot_pca(df_grade_full, cat_weight_dict, point_dict):
    """ plots scatter of students on 1st 2 PCA directions

    (helps identify trends between assignments and spot outliers, likely hw
    and exam scores are correlated, but maybe some sub-group have abnormally
    high hw

    Args:
        df_grade_full (pd.DataFrame):
        cat_weight_dict (dict): keys are categories, values are weights
        point_dict (dict): keys are assignments (str), values are max points
            per assignment

    Returns:
        fig (plotly):
    """
    if cat_weight_dict is not None:
        print('warning: category weight not accounted for, each assignment '
              'given equal weight')

    # kludge: assignments are all columns after 'letter'
    idx_letter = list(df_grade_full.columns).index('letter')
    df = df_grade_full.iloc[:, idx_letter + 1:].copy()

    # compute scale per category
    weight_total = sum(cat_weight_dict.values())
    cat_scale_dict = {cat: weight / weight_total
                      for cat, weight in cat_weight_dict.items()}

    # compute scale per assignment
    ass_list = df_grade_full.columns[idx_letter + 1:]
    cat_bool_dict = {cat: np.array([cat in ass for ass in ass_list])
                     for cat in cat_weight_dict.keys()}
    assert (sum(cat_bool_dict.values()) == 1).all(), \
        'mapping from assignments to categories broken'
    perc = np.ones(len(ass_list))
    points = np.array([point_dict[ass] for ass in ass_list])
    for idx, ass in enumerate(ass_list):
        # lookup category
        for cat in cat_weight_dict.keys():
            if cat in ass:
                break

        # compute scale for this assignment
        perc[idx] = point_dict[ass] / sum(points[cat_bool_dict[cat]]) * \
            cat_scale_dict[cat]

    # center and impute
    df -= df.mean()
    df = df.fillna(0)

    # scale & pca projection
    x = df.values
    x = x @ np.diag(perc ** .5 / x.std(axis=0))
    assert np.allclose(x.std(axis=0), perc ** .5)
    c = np.cov(x.T)
    evals, evecs = np.linalg.eig(c)

    # ensure pca vectors largely point "positive" (top right is for strong
    # students in resulting graph).  we flip direction if most of the weight
    # in a component is negative
    weight_tug_war = np.diag(perc) @ ((evecs > 0) * 2 - 1)
    flip = weight_tug_war.sum(axis=0) > 0
    evecs = evecs @ np.diag(flip * 2 - 1)

    # prep p
    df = df_grade_full.copy()
    df['pca0'] = x @ evecs[:, 0]
    df['pca1'] = x @ evecs[:, 1]
    fig = px.scatter(df,
                     x='pca0',
                     y='pca1',
                     hover_data=df.columns)

    return fig
