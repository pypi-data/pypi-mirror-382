# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

from pyiron_base import TableJob

from pyiron_atomistics.table.funct import (
    get_average_waves,
    get_convergence_check,
    get_e_band,
    get_e_conv_level,
    get_ekin_error,
    get_elements,
    get_encut,
    get_energy_free,
    get_energy_free_per_atom,
    get_energy_int,
    get_energy_int_per_atom,
    get_energy_pot,
    get_energy_pot_per_atom,
    get_energy_tot,
    get_energy_tot_per_atom,
    get_equilibrium_parameters,
    get_f_states,
    get_forces,
    get_incar,
    get_ismear,
    get_job_name,
    get_magnetic_structure,
    get_majority_crystal_structure,
    get_majority_species,
    get_n_equ_kpts,
    get_n_kpts,
    get_number_of_final_electronic_steps,
    get_number_of_ionic_steps,
    get_number_of_species,
    get_plane_waves,
    get_sigma,
    get_structure,
    get_total_number_of_atoms,
    get_volume,
    get_volume_per_atom,
)

__author__ = "Uday Gajera, Jan Janssen, Joerg Neugebauer"
__copyright__ = (
    "Copyright 2021, Max-Planck-Institut für Eisenforschung GmbH - "
    "Computational Materials Design (CM) Department"
)
__version__ = "0.0.1"
__maintainer__ = "Jan Janssen"
__email__ = "janssen@mpie.de"
__status__ = "development"
__date__ = "Sep 1, 2018"


TableJob._system_function_lst += [
    get_incar,
    get_sigma,
    get_total_number_of_atoms,
    get_elements,
    get_convergence_check,
    get_number_of_species,
    get_number_of_ionic_steps,
    get_ismear,
    get_encut,
    get_n_kpts,
    get_n_equ_kpts,
    get_number_of_final_electronic_steps,
    get_majority_species,
    get_job_name,
    get_energy_tot,
    get_energy_pot,
    get_energy_free,
    get_energy_int,
    get_energy_tot_per_atom,
    get_energy_pot_per_atom,
    get_energy_free_per_atom,
    get_energy_int_per_atom,
    get_e_conv_level,
    get_f_states,
    get_e_band,
    get_majority_crystal_structure,
    get_equilibrium_parameters,
    get_structure,
    get_forces,
    get_magnetic_structure,
    get_average_waves,
    get_plane_waves,
    get_ekin_error,
    get_volume,
    get_volume_per_atom,
]
