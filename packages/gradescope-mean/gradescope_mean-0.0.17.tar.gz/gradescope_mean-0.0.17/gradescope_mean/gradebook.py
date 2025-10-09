from math import ceil
from warnings import warn

import numpy as np
import pandas as pd

from .assign_list import AssignmentList, AssignmentNotFoundError, normalize
from .get_mean_drop_low import get_mean_drop_low
from .perc_to_letter import perc_to_letter


class Gradebook:
    """ a grade for every student-assignment pair & manipulations

    Attributes:
        df_perc (pd.DataFrame): index is email of student and each col is assignment
            values are percentage student earned (nan for waived).
        df_meta (pd.DataFrame): index is email, columns are metadata (first
            name, last name, section, id)
        df_lateday (pd.DataFarme): index are email, cols are assignment and
            values are days each assignment is late
        ass_list (AssignmentList): a list of assignments
        points (np.array): points per assignment (same order as ass_list)
    """
    META_DATA_COLS = 4

    def __init__(self, f_scope):
        df_scope = pd.read_csv(str(f_scope), index_col='Email')

        # groom input data
        df_scope.columns = map(normalize, df_scope.columns)
        for idx in range(self.META_DATA_COLS):
            if df_scope.columns[idx] == 'sid':
                # student ids are ints, lets not cast to str
                continue
            df_scope.iloc[:, idx] = df_scope.iloc[:, idx].astype(str).map(
                str.lower)
        df_scope.index.map(str.lower)
        df_scope.index.name = df_scope.index.name.lower()
        df_scope.fillna(0, inplace=True)

        # store meta data
        self.df_meta = df_scope.iloc[:, :self.META_DATA_COLS]

        # compute percent per assignment & points
        self.ass_list = AssignmentList(df_scope.columns)
        self.df_perc = pd.DataFrame()
        self.points = np.empty(len(self.ass_list))
        for idx, ass in enumerate(self.ass_list):
            # points per assignment
            ass_max_pt = ass + self.ass_list.MAX_PTS
            assert len(df_scope[ass_max_pt].unique()) == 1, \
                f'multiple max pts: {ass}'
            self.points[idx] = df_scope[ass_max_pt].values[0]

            # percentage per assignment
            self.df_perc[ass] = df_scope[ass] / df_scope[ass_max_pt]

        # compute days late
        def get_days_late(s_hour_min_sec):
            # grace period of 1 hour built in (we ignore min / sec)
            return ceil(float(s_hour_min_sec.split(':')[0]) / 24)

        self.df_lateday = pd.DataFrame()
        for ass in self.ass_list:
            ass_late = ass + self.ass_list.LATE
            self.df_lateday[ass] = df_scope[ass_late].map(get_days_late)

    def waive(self, waive_dict):
        """ waives assignment (per student) by marking percentages as nan

        Args:
            waive_dict (dict): keys are emails, values are lists of assignments
        """

        for email, ass_list in waive_dict.items():
            for ass in ass_list:
                try:
                    _ass = self.ass_list.match(ass)
                    self.df_perc.loc[email, _ass] = np.nan
                    self.df_lateday.loc[email, _ass] = np.nan
                except AssignmentNotFoundError:
                    msg = f'waive-fail: not found "{ass}" for {email}'
                    warn(msg)

    def substitute(self, sub_dict):
        """ substitutes some assignment percentages (if sub is higher)

        This method is useful when there are multiple versions of a quiz, each
        with their own gradescope assignment.  It allows you to consolidate
        them into a single assignment (be sure to exclude the substituted
        assignments so they don't count)

        Args:
            sub_dict (dict): keys are target assignment, values are list of
                all assignments which could be substituted
        """
        # we keep all the new, substituted grades in a dict before substituting
        # (were we to substitute, the order of substitutions could cause issue)
        new_col_dict = dict()
        for ass_to, ass_from_list in sub_dict.items():
            if ass_to not in ass_from_list:
                # ensure ass_to is in the list of potential substitutes
                ass_from_list = ass_from_list + [ass_to]

            # get max percentage across all assignments, substitute it
            new_col_dict[ass_to] = self.df_perc.loc[:, ass_from_list].max(
                axis=1)

        # substitute
        for ass_to, s in new_col_dict.items():
            self.df_perc[ass_to] = s

    def prune_email(self, email_list, ignore_suffix=True):
        """ discards rows not in email_list, warns if emails in list not a row

        Args:
            email_list (list): list of strings
        """
        if ignore_suffix:
            def discard_suffix(email_list):
                prefix_list = [email.split('@')[0] for email in email_list]
                prefix_set = set(prefix_list)
                assert len(prefix_list) == len(set(prefix_list)), \
                    'non-unique email (before @) found, disable ignore_suffix'

                prefix_email_dict = dict(zip(prefix_list, email_list))

                return prefix_set, prefix_email_dict

            email_target, _ = discard_suffix(email_list)
            email_scope, prefix_email_dict = discard_suffix(self.df_meta.index)
        else:
            email_scope = set(self.df_meta.index)
            email_target = set(email_list)

        # warn if any emails not found
        email_target_missing = email_target - email_scope
        if email_target_missing:
            s = '\n'.join(email_target_missing)
            warn(f'email not found in scope:\n{s}')

            email_scope_extra = email_scope - email_target
            if email_scope_extra:
                s = '\n'.join(email_scope_extra)
                warn(f'maybe its one of these?\n{s}')

        # discard rows not in email_list
        email_list_found = list(email_scope.intersection(email_target))
        if ignore_suffix:
            email_list_found = [prefix_email_dict[prefix]
                                for prefix in email_list_found]
        self.df_perc = self.df_perc.loc[email_list_found, :]
        self.df_meta = self.df_meta.loc[email_list_found, :]
        self.df_lateday = self.df_lateday.loc[email_list_found, :]

    def remove_thresh(self, min_complete_thresh):
        """ removes assignments which not enough students have submitted

        Args:
            min_complete_thresh (float): below this completion threshold
                an assignment will be excluded (msg printed to user).  0 and
                nan both count as not completed
        """
        # find percent missing per assignment per ass, rm if above thresh
        s_complete_perc = 1 - (self.df_perc.fillna(0) == 0).mean(axis=0)
        for ass, comp_perc in s_complete_perc.sort_values().items():
            if comp_perc < min_complete_thresh:
                msg = f'removed: {comp_perc * 100:.0f}% complete {ass}'
                self.remove(ass, skip_match=True)
            else:
                msg = f'   kept: {comp_perc * 100:.0f}% complete {ass}'
            print(msg)

    def remove(self, ass, multi=False, skip_match=False):
        """ deletes an assignment

        Args:
            ass (s): an assignments to remove from gradebook
            multi (bool): if True, allows for multiple assignments to be
                removed
            skip_match (bool): when True, assignment name is assumed exact and
                no matching is done.  (defaults False)
        """
        if multi:
            # remove all assignments which match given string
            for _ass in tuple(self.ass_list.match_iter(ass)):
                self.remove(_ass, multi=False, skip_match=True)
            return

        # normalize assignment name
        if not skip_match:
            ass = self.ass_list.match(ass)
        ass_idx = self.ass_list.index(ass)

        # remove
        del self.df_perc[ass]
        del self.df_lateday[ass]
        self.ass_list.pop(ass_idx)
        self.points = np.delete(self.points, ass_idx)

    def get_late_penalty(self, cat, penalty_per_day, excuse_day=0,
                         excuse_day_offset=None, waive_dict=None):
        """ computes modifier to category mean to incorporate late penalty

        Let late_day be the total number of days late (across all hws of one
        student).  then the penalty applied is:

            -penalty_per_day * max(late_day - excuse_day, 0)

        to an average assignment score.  For example, when penalty_per_day=.15
        then every unexcused late day effectively negates %15 of a single hw.
        (since all hws needn't have same weight, penalty applied to average hw)

        Args:
            cat (str): category of assignment to apply penalty to
            penalty_per_day (float): percentage of hw penalty per unexcused day
                late.  positive values will lower grades.
            excuse_day (int): number of excused late days each student has (can
                be used on any assignment).  excuse_day_adjust allows this
                default to be modified per student
            excuse_day_offset (dict): keys are student emails, values are
                added to excuse_day value to be used for corresponding student
            waive_dict (dict): keys are student emails, values are lists
                of assignments whose late days are to be waived

        Returns:
            s_unexcuse_late_day (pd.Series): number of unexcused late days
                remaining (negative if late penalty applied)
            s_penalty (pd.Series): index is email.  values are adjustments
        """
        if penalty_per_day < 0:
            raise AttributeError(
                'penalty_per_day should be positive to lower credit when late')

        if waive_dict is None:
            waive_dict = dict()

        # get late days across category
        ass_cat_list = list(self.ass_list.match_iter(s_assign=cat))
        df_late = self.df_lateday.loc[:, ass_cat_list].copy()

        # waive late days per email / assignment
        for email, ass_list in waive_dict.items():
            for ass in ass_list:
                ass = self.ass_list.match(ass)
                if ass in df_late.columns:
                    df_late.loc[email, ass] = np.nan

        # get number of excuse days per student
        s_late_day = df_late.sum(axis=1, skipna=True)
        s_excuse_day = pd.Series(index=s_late_day.index, data=excuse_day)
        if excuse_day_offset is not None:
            for email, offset in excuse_day_offset.items():
                if email in s_excuse_day:
                    s_excuse_day[email] += offset
                else:
                    warn(f'email not found, excuse_day_offset ({offset}) not '
                         f'applied: {email}')

        # get unexcused late days per student
        s_unexcuse_late_day = s_late_day - s_excuse_day

        # get penalty
        s_penalty = - penalty_per_day * s_unexcuse_late_day / len(ass_cat_list)
        s_penalty = s_penalty.apply(lambda x: min(x, 0))

        return s_unexcuse_late_day, s_penalty

    def average_full(self, *args, **kwargs):
        """ like average, but adds metadata & percentage columns to output
        """
        df_grade = self.average(*args, **kwargs)

        return pd.concat((self.df_meta, df_grade, self.df_perc), axis=1)

    def average(self, cat_weight_dict=None, cat_drop_dict=None,
                cat_late_dict=None, grade_thresh=None, late_waive_dict=None):
        """ final grades, weighted by points (default) or category weights

        Args:
            cat_weight_dict (dict): keys are strings which define categories
                values are unnormalized (positive) weights assigned to each
                category.  (e.g. if HW / exam each worth 50% of grade then
                cat_weight_dict {'hw': 50, 'exam': 50}.  Assignment names must
                each contain exactly one category such that categories
                partition all assignments.  (Default: no categories given, each
                assignment weighted by points given on gradescope)
            cat_drop_dict (dict): keys are categories (matching some key
                in cat_weight_dict). values are ints, the number of lowest
                 percentage assignments to drop in each category.  any category
                 without an entry in cat_drop_dict will not have any lowest
                 assignments dropped.  (default: no lowest assignments dropped)
            cat_late_dict (dict): keys are assignment categories.  values are
                dictionaries unpacked as arguments into
                Gradebook.get_late_penalty()

        Returns:
            df_grade (pd.DataFrame): final grade
        """
        if cat_weight_dict is None or cat_weight_dict == dict():
            # all assignments contain ''
            cat_weight_dict = {'': 1}

        if cat_late_dict is None:
            cat_late_dict = dict()

        if cat_drop_dict is None:
            cat_drop_dict = dict()
        else:
            assert set(cat_drop_dict.keys()).issubset(cat_weight_dict.keys())

        # ensure that categories partition assignments (warn if they don't)
        cat_bool_dict = {cat: np.array([cat in ass for ass in self.ass_list])
                         for cat in cat_weight_dict.keys()}
        cat_bool_sum = sum(cat_bool_dict.values())
        if not (cat_bool_sum == 1).all():
            # assignment not included in any category
            ass_not_include = np.array(self.ass_list)[cat_bool_sum < 1]
            if ass_not_include.size:
                s = ', '.join(sorted(ass_not_include))
                warn(f'assignment not in any category: {s}')

            # assignment included in more than 1 category
            ass_over_include = np.array(self.ass_list)[cat_bool_sum > 1]
            if ass_over_include.size:
                s = ', '.join(sorted(ass_over_include))
                warn(f'assignment in multiple categories: {s}')

        # extract percentages as array (a bit quicker)
        perc_all = self.df_perc.values

        df_grade = pd.DataFrame({'mean': 0}, index=self.df_perc.index)

        weight_total = pd.Series(0, index=self.df_perc.index)
        for cat, cat_bool in cat_bool_dict.items():
            perc_cat = perc_all[:, cat_bool]
            _points = self.points[cat_bool]

            # drop lowest n assignments
            drop_n = cat_drop_dict.get(cat, 0)

            s_mean = f'mean_{cat}'
            for idx, email in enumerate(self.df_perc.index):
                # compute mean per student-category
                _perc = perc_cat[idx, :]

                # average across all assignments
                df_grade.loc[email, s_mean] = get_mean_drop_low(perc=_perc,
                                                                weight=_points,
                                                                drop_n=drop_n)

            if cat in cat_late_dict:
                s_unexcused_late, s_penalty = self.get_late_penalty(
                    cat=cat,
                    waive_dict=late_waive_dict,
                    **cat_late_dict[cat])

                df_grade[s_mean] += s_penalty

                # ensure penalty doesn't drop mean below 0
                df_grade[s_mean] = df_grade[s_mean].map(lambda x: max(x, 0))

                # add late days remaining to output
                df_grade[f'late days remain ({cat})'] = \
                    - s_unexcused_late

            # add category's contribution to overall mean
            cat_missing = df_grade[s_mean].isna()
            for email in cat_missing.index[cat_missing]:
                print(
                    f'{email} has no assignments in category: {cat} (ignored in final mean)')
            weight_total += cat_weight_dict[cat] * ~cat_missing

            cat_mean = df_grade[s_mean].copy()
            cat_mean.fillna(0, inplace=True)
            df_grade['mean'] += cat_mean * cat_weight_dict[cat]

        df_grade['mean'] *= 1 / weight_total

        # compute letter grade
        def _perc_to_letter(perc):
            return perc_to_letter(perc, grade_thresh=grade_thresh)

        df_grade['letter'] = df_grade['mean'].map(_perc_to_letter)

        if 'mean_' in df_grade.columns:
            # delete dummy category (equivalent to default behavior)
            del df_grade['mean_']

        return df_grade
