# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

import structuretoolkit as stk
from pyiron_base import state

__author__ = "Osamu Waseda"
__copyright__ = (
    "Copyright 2021, Max-Planck-Institut für Eisenforschung GmbH - "
    "Computational Materials Design (CM) Department"
)
__version__ = "1.0"
__maintainer__ = "Osamu Waseda"
__email__ = "waseda@mpie.de"
__status__ = "development"
__date__ = "Sep 1, 2018"


def analyse_phonopy_equivalent_atoms(atoms, symprec=1e-5, angle_tolerance=-1.0):
    """
    Args: (read phonopy.structure.spglib for more details)
        symprec:
            float: Symmetry search tolerance in the unit of length.
        angle_tolerance:
            float: Symmetry search tolerance in the unit of angle deg.
                If the value is negative, an internally optimized routine
                is used to judge symmetry.

    """
    state.publications.add(publication())
    return stk.analyse.get_equivalent_atoms(
        structure=atoms, symprec=symprec, angle_tolerance=angle_tolerance
    )


def publication():
    return {
        "phonopy": {
            "phonopy": {
                "journal": "Scr. Mater.",
                "year": "2015",
                "title": "First principles phonon calculations in materials science",
                "author": ["Togo, A", "Tanaka, I"],
                "pages": "1--5",
                "volume": "108",
                "month": "Nov",
            }
        }
    }
