from enum import Enum, auto

class Node(Enum):
    """Nodes in the Stat-Ease 360 GUI."""

    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)

    def __str__(self):
        return '%s' % self.name

    notes = auto()
    design = auto()
    analysis = auto()
    pre_experiment = auto()
    effects = auto()
    fit_summary = auto()
    anova = auto()
    diagnostics = auto()
    classification = auto()
    model_graphs = auto()
    constraints = auto()
    evaluation_results = auto()
    evaluation_graphs = auto()
    optimization_criteria = auto()
    optimization_ramps = auto()
    optimization_results = auto()
    optimization_graphs = auto()
    optimization_predict = auto()
    graphical_optimization = auto()
    numerical_optimization = auto()
    graphical_optimization_criteria = auto()
    graphical_optimization_graphs = auto()
    transform = auto()
    design_status = auto()
    response = auto()
    evaluation = auto()
    optimization = auto()
    point_prediction = auto()
    model_selection = auto()
    evaluation_model_selection = auto()
    graph_columns = auto()
    confirmation = auto()
    post_analysis = auto()
    coef_table = auto()
    group_effects = auto()
    sub_effects = auto()
    anova_reml = auto()
    anova_ml = auto()
    anova_ems = auto()
