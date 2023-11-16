import copy

import numpy as np
from matplotlib import pyplot as plt

from hpcflow.sdk.core.parameters import ParameterValue
from hpcflow.sdk.core.utils import get_in_container, set_in_container
from matflow.param_classes.orientations import Orientations


class SingleCrystalParameters(ParameterValue):
    _typ = "single_crystal_parameters"

    def __init__(self, phases, perturbations=None):
        self._base = phases
        self._perturbations = perturbations
        self._phases = None  # assigned (perturbations applied) on first access

    def __getitem__(self, name):
        """Dict-like retrieval of the parameters for a given phase, with perturbations
        applied."""
        return self.phases[name]

    def to_dict(self):
        out = {k.lstrip("_"): v for k, v in super().to_dict().items() if k != "_phases"}
        out["phases"] = out.pop("base")
        return out

    def as_base(self):
        """Return a copy where `base` includes the perturbations."""
        return self.__class__(phases=self.phases)

    @property
    def base(self):
        return self._base

    @property
    def phases(self):
        if not self._phases:
            phases = copy.deepcopy(self._base)

            perturbations = self._perturbations
            if not isinstance(perturbations, list):
                perturbations = [perturbations]

            for pert_i in perturbations:
                if not pert_i:
                    continue
                scale = pert_i["multiplicative"]
                new_val = get_in_container(phases, pert_i["path"]) * scale
                set_in_container(phases, pert_i["path"], new_val)
            self._phases = phases
        return self._phases

    @property
    def perturbations(self):
        return self._perturbations
