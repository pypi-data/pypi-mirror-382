import pathlib
import shutil
from datetime import datetime

from ruamel.yaml import YAML

from .assign_list import normalize
from .gradebook import Gradebook

F_CONFIG_DEFAULT = (pathlib.Path(__file__).parent / 'config.yaml').resolve()
yaml = YAML(typ='safe')


class Config:
    def __init__(self, cat_weight_dict=None, cat_drop_dict=None,
                 remove_list=tuple(), sub_dict=None, waive_dict=None,
                 email_list=None, cat_late_dict=None,
                 exclude_complete_thresh=0, grade_thresh=None,
                 late_waive_dict=None):
        if cat_late_dict is None:
            self.cat_weight_dict = dict()
        else:
            self.cat_weight_dict = cat_weight_dict

        if cat_drop_dict is None:
            self.cat_drop_dict = dict()
        else:
            self.cat_drop_dict = cat_drop_dict

        if remove_list is None:
            self.remove_list = list()
        else:
            self.remove_list = remove_list

        if sub_dict is None:
            self.sub_dict = dict()
        else:
            self.sub_dict = sub_dict

        if waive_dict is None:
            self.waive_dict = dict()
        else:
            self.waive_dict = waive_dict

        if email_list is None:
            self.email_list = list()
        else:
            self.email_list = email_list

        if cat_late_dict is None:
            self.cat_late_dict = dict()
        else:
            self.cat_late_dict = cat_late_dict

        if late_waive_dict is None:
            self.late_waive_dict = dict()
        else:
            self.late_waive_dict = late_waive_dict

        self.exclude_complete_thresh = exclude_complete_thresh
        self.grade_thresh = grade_thresh

        self._normalize()

    def _normalize(self):
        """ normalizes category names, throws meaningful errors if invalid """
        # normalize assignment names
        self.cat_weight_dict = {normalize(c): w
                                for c, w in self.cat_weight_dict.items()}

        self.cat_drop_dict = {normalize(c): d
                              for c, d in self.cat_drop_dict.items()}

        self.remove_list = [normalize(a) for a in self.remove_list]

        self.sub_dict = {normalize(s0): list(map(normalize, s1_list))
                         for s0, s1_list in self.sub_dict.items()}

        self.waive_dict = {email: [normalize(a) for a in a_list.split(',')]
                           for email, a_list in self.waive_dict.items()}

        self.cat_late_dict = {normalize(c): l
                              for c, l in self.cat_late_dict.items()}
        self.late_waive_dict = {email: [normalize(a) for a in a_list.split(
            ',')]
                                for email, a_list in
                                self.late_waive_dict.items()}

    def __call__(self, f_scope):
        """ runs a typical processing pipeline given config and f_scop

        Args:
            f_scope (str): raw gradescope csv

        Returns:
            gradebook (Gradebook): processed gradebook
            df_grade_full (pd.DataFrame): full data frame
        """
        gradebook = Gradebook(f_scope=f_scope)

        if self.email_list:
            gradebook.prune_email(email_list=self.email_list)

        if self.sub_dict:
            gradebook.substitute(sub_dict=self.sub_dict)

        for ass in self.remove_list:
            gradebook.remove(ass, multi=True)

        gradebook.remove_thresh(
            min_complete_thresh=self.exclude_complete_thresh)

        if self.waive_dict:
            gradebook.waive(waive_dict=self.waive_dict)

        df_grade_full = gradebook.average_full(
            cat_weight_dict=self.cat_weight_dict,
            cat_drop_dict=self.cat_drop_dict,
            cat_late_dict=self.cat_late_dict,
            grade_thresh=self.grade_thresh,
            late_waive_dict=self.late_waive_dict)

        return gradebook, df_grade_full

    @classmethod
    def from_file(cls, f_config):
        """ loads config from yaml file

        Args:
            f_config (str): yaml file

        Returns:
            config (Config): configuration
        """
        # load yaml
        d = yaml.load(pathlib.Path(f_config))

        cat_weight_dict = d['category']['weight']
        cat_drop_n = d['category']['drop_low']
        cat_late_dict = d['category']['late_penalty']
        exclude_list = d['assignments']['exclude']
        sub_dict = d['assignments']['substitute']
        waive_dict = d['waive']
        email_list = d['email_list']
        exclude_complete_thresh = d['assignments']['exclude_complete_thresh']

        if 'grade_thresh' in d.keys():
            grade_thresh = d['grade_thresh']
        else:
            grade_thresh = None

        return cls(cat_weight_dict, cat_drop_n, exclude_list, sub_dict,
                   waive_dict, email_list, cat_late_dict,
                   exclude_complete_thresh, grade_thresh=grade_thresh)

    @classmethod
    def cli_copy_config(cls, folder):
        """ copies default config file to folder, uses existing local if user wants
        """
        # default config location
        f_config = pathlib.Path(folder) / F_CONFIG_DEFAULT.name

        if f_config.exists():
            # if config already exists, ask if it should be used
            print(f'local config exists: {f_config.resolve()}')
            while True:
                s = input('use [e]xisting config or create [n]ew config?')
                if s == 'e':
                    # use existing config
                    return cls.from_file(f_config)
                elif s == 'n':
                    # create new config
                    s_now = datetime.now().strftime('_%Y_%b_%d@%H:%M:%S')
                    f_config = str(f_config).replace('.yaml', f'{s_now}.yaml')
                    f_config = pathlib.Path(f_config)
                    break
                print('invalid input')

        # copy config
        shutil.copy(F_CONFIG_DEFAULT, f_config)
        print(f'using new copy of default config file.  see '
              f'https://github.com/matthigger/gradescope_mean/blob/main/doc'
              f'/config.md for details:\n {f_config}')

        return cls.from_file(f_config)
