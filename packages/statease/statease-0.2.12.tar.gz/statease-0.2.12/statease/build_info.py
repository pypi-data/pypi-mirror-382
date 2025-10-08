from .factor import Factor
from .response import Response
from enum import Enum, auto
import json

class DesignProperty(Enum):
    """An enumeration representing the different design properties
used when building a new design.
"""
    center_points = auto()
    replicates = auto()
    block_by_replicate = auto()
    taguchi_subtype = auto()
    ccd_type = auto()
    ccd_fraction = auto()
    ccd_alpha_type = auto()
    ccd_alpha = auto()
    center_per_axial_block = auto()
    center_per_factorial_block = auto()
    ccd_factorial_replicates = auto()
    ccd_axial_replicates = auto()
    ccd_center_point_group_size = auto()
    factorial_full_factors = auto()
    factorial_base_factors = auto()
    factor_generators = auto()
    block_generators = auto()
    group_generators = auto()
    include_axial_check_blends = auto()
    include_constraint_plane_centroids = auto()
    simplex_vertices = auto()
    simplex_augment = auto()
    extra_min_res_iv_runs = auto()
    coord_exchange = auto()
    point_exchange = auto()
    lof_points = auto()
    model_points = auto()
    optimality = auto()
    build_cand_method = auto()
    build_model_point_type = auto()
    failed_attempts = auto()
    successful_attempts = auto()
    force_balance = auto()
    process_order = auto()
    mix_order = auto()
    mixture_order = auto()
    build_time = auto()
    build_seed = auto()
    built_with_wizard = auto()
    use_candidate_type = auto()
    groups = auto()
    subgroups = auto()
    center_point_groups = auto()
    factorial_whole_plot_factors = auto()
    factorial_whole_plot_full_factors = auto()
    variance_ratio = auto()
    run_count = auto()

    def __str__(self):
        return self.name

class BuildInfo:
    """BuildInfo

The BuildInfo class holds information required to build a design in
Stat-Ease 360.

Example Usage:
    >>> se_conn = statease.connect()
    >>> bi = statease.BuildInfo('Response Surface', 'CCD')
    >>> bi.add_factor('time', units='min.', low=40, high=50)
    >>> bi.add_factor('temperature', units='deg C', low=80, high=90)
    >>> bi.add_factor('catalyst', units='%', low=2, high=3)
    >>>
    >>> bi.add_response('Conversion', units='%')
    >>> bi.add_response('Activity', units='')
    >>>
    >>> bi.blocks = ['B1', 'B2']
    >>>
    >>> bi.add_design_property(DesignProperty.center_points, 6)
    >>> bi.add_design_property(DesignProperty.center_per_axial_block, 2)
    >>>
    >>> se_conn.build_design(bi)
"""
    def __init__(self, study_type, design_type, study_subtype=None):
        self.__factors = []
        self.__responses = []
        self.__block_levels = []
        self.__design_properties = {}
        self.__study_type = study_type
        self.__design_type = design_type
        self.__study_subtype = study_subtype

    def __str__(self):
        return json.dumps(self.to_dict())

    @property
    def study_type(self):
        """The study type of the design. This can be any of the following:
        'Factorial'
        'Response Surface'
        'Mixture'
        """
        return self.__study_type

    @study_type.setter
    def study_type(self, study_type):
        self.__study_type = study_type

    @property
    def design_type(self):
        return self.__design_type

    @design_type.setter
    def design_type(self, design_type):
        self.__design_type = design_type

    @property
    def study_subtype(self):
        """The study subtype of the design. This can be any of the following:
        'Randomized'
        'Split-plot'
        'Split-split-plot'
        """
        return self.__study_subtype

    @study_subtype.setter
    def study_subtype(self, study_subtype):
        self.__study_subtype = study_subtype

    @property
    def blocks(self):
        return self.__block_levels

    @blocks.setter
    def blocks(self, block_levels):
        self.__block_levels = block_levels

    @property
    def design_properties(self):
        return self.__design_properties

    def add_design_property(self, property_names, property_value):
        self.__design_properties[str(property_names)] = property_value

    def add_factor(self, name, **kwargs):
        facInfo = Factor(name=name, **kwargs)
        self.__factors.append(facInfo)

    @property
    def factors(self):
        return self.__factors

    def add_response(self, name, **kwargs):
        rsp = Response(name=name, **kwargs)
        self.__responses.append(rsp)

    @property
    def responses(self):
        return self.__responses

    def to_dict(self):
        data = {}
        data['study_type'] = self.__study_type
        data['study_subtype'] = self.__study_subtype
        data['design_type'] = self.__design_type
        data['factors'] = [ factor.to_dict() for factor in self.__factors ]
        data['responses'] = [ response.to_dict() for response in self.__responses ]
        data['block_levels'] = self.__block_levels
        data['design_properties'] = self.__design_properties
        return data
