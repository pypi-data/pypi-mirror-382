# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

from __future__ import print_function

import posixpath
from collections import defaultdict

import numpy as np
import pint
from pyiron_base import GenericJob, GenericParameters, Logstatus

from pyiron_atomistics.atomistics.job.interactive import GenericInteractive
from pyiron_atomistics.testing.executable import ExampleExecutable

"""
Example Job class for testing the pyiron classes
"""

__author__ = "Joerg Neugebauer, Jan Janssen"
__copyright__ = (
    "Copyright 2021, Max-Planck-Institut für Eisenforschung GmbH - "
    "Computational Materials Design (CM) Department"
)
__version__ = "1.0"
__maintainer__ = "Jan Janssen"
__email__ = "janssen@mpie.de"
__status__ = "production"
__date__ = "Sep 1, 2017"


class ExampleJob(GenericJob):
    """
    ExampleJob generating a list of random numbers to simulate energy fluctuations.

    Args:
        project (ProjectHDFio): ProjectHDFio instance which points to the HDF5 file the job is stored in
        job_name (str): name of the job, which has to be unique within the project

    Attributes:

        .. attribute:: job_name

            name of the job, which has to be unique within the project

        .. attribute:: status

            execution status of the job, can be one of the following [initialized, appended, created, submitted, running,
                                                                      aborted, collect, suspended, refresh, busy, finished]

        .. attribute:: job_id

            unique id to identify the job in the pyiron database

        .. attribute:: parent_id

            job id of the predecessor job - the job which was executed before the current one in the current job series

        .. attribute:: master_id

            job id of the master job - a meta job which groups a series of jobs, which are executed either in parallel or in
            serial.

        .. attribute:: child_ids

            list of child job ids - only meta jobs have child jobs - jobs which list the meta job as their master

        .. attribute:: project

            Project instance the jobs is located in

        .. attribute:: project_hdf5

            ProjectHDFio instance which points to the HDF5 file the job is stored in

        .. attribute:: job_info_str

            short string to describe the job by it is job_name and job ID - mainly used for logging

        .. attribute:: working_directory

            working directory of the job is executed in - outside the HDF5 file

        .. attribute:: path

            path to the job as a combination of absolute file system path and path within the HDF5 file.

        .. attribute:: version

            Version of the hamiltonian, which is also the version of the executable unless a custom executable is used.

        .. attribute:: executable

            Executable used to run the job - usually the path to an external executable.

        .. attribute:: library_activated

            For job types which offer a Python library pyiron can use the python library instead of an external executable.

        .. attribute:: server

            Server object to handle the execution environment for the job.

        .. attribute:: queue_id

            the ID returned from the queuing system - it is most likely not the same as the job ID.

        .. attribute:: logger

            logger object to monitor the external execution and internal pyiron warnings.

        .. attribute:: restart_file_list

            list of files which are used to restart the calculation from these files.

        .. attribute:: job_type

            Job type object with all the available job types: ['ExampleJob', 'ParallelMaster', 'ScriptJob',
                                                               'ListMaster']
    """

    def __init__(self, project, job_name):
        super(ExampleJob, self).__init__(project, job_name)
        self.__version__ = "0.3"

        self.input = ExampleInput()
        self.executable = "python -m pyiron_atomistics.testing.executable"
        self.interactive_cache = {"alat": [], "count": [], "energy": []}

    def set_input_to_read_only(self):
        """
        This function enforces read-only mode for the input classes, but it has to be implement in the individual
        classes.
        """
        self.input.read_only = True

    # define routines that create all necessary input files
    def write_input(self):
        """
        Call routines that generate the codespecifc input files
        """
        self.input.write_file(file_name="input.inp", cwd=self.working_directory)

    # define routines that collect all output files
    def collect_output(self):
        """
        Parse the output files of the example job and store the results in the HDF5 File.
        """
        self.collect_output_log()
        self.collect_warnings()
        self.collect_logfiles()

    def collect_output_log(self, file_name="output.log"):
        """
        general purpose routine to extract output from logfile

        Args:
            file_name (str): output.log - optional
        """
        tag_dict = {
            "alat": {"arg": "0", "rows": 0},
            "count": {"arg": "0", "rows": 0},
            "energy": {"arg": "0", "rows": 0},
        }
        lf = Logstatus()
        file_name = posixpath.join(self.working_directory, file_name)
        lf.extract_file(file_name=file_name, tag_dict=tag_dict)
        with self.project_hdf5.open("output/generic") as h5:
            lf.to_hdf(h5)
            h5["energy_tot"] = np.array(h5["energy"])
            h5["volume"] = np.array(h5["alat"])

    def collect_warnings(self):
        """
        Collect the warnings if any were written to the info.log file and store them in the HDF5 file
        """
        warnings_lst = []
        with open(posixpath.join(self.working_directory, "info.log"), "r") as f:
            lines = f.readlines()
        for line in lines:
            if "WARNING" in line:
                warnings_lst.append(line.split("WARNING"))
                warnings_lst[-1][-1] = warnings_lst[-1][-1].rstrip()
        if len(warnings_lst) > 0:
            warnings_dict = {
                "Module": [warnings_lst[i][0] for i in range(len(warnings_lst))],
                "Message": [warnings_lst[i][1] for i in range(len(warnings_lst))],
            }
            print("module: ", warnings_lst[:][:])
            with self.project_hdf5.open("output"):
                self._hdf5["WARNINGS"] = warnings_dict

    def collect_logfiles(self):
        """
        Collect the errors from the info.log file and store them in the HDF5 file
        """
        errors_lst = []
        with open(posixpath.join(self.working_directory, "info.log"), "r") as f:
            lines = f.readlines()
        for line in lines:
            if "ERROR" in line:
                errors_lst.append(line)
        if len(errors_lst) > 0:
            with self.project_hdf5.open("output") as hdf_output:
                hdf_output["ERRORS"] = errors_lst

    def to_hdf(self, hdf=None, group_name=None):
        """
        Store the ExampleJob object in the HDF5 File

        Args:
            hdf (ProjectHDFio): HDF5 group object - optional
            group_name (str): HDF5 subgroup name - optional
        """
        super(ExampleJob, self).to_hdf(hdf=hdf, group_name=group_name)
        with self.project_hdf5.open("input") as hdf5_input:
            self.input.to_hdf(hdf5_input)

    def from_hdf(self, hdf=None, group_name=None):
        """
        Restore the ExampleJob object in the HDF5 File

        Args:
            hdf (ProjectHDFio): HDF5 group object - optional
            group_name (str): HDF5 subgroup name - optional
        """
        super(ExampleJob, self).from_hdf(hdf=hdf, group_name=group_name)
        with self.project_hdf5.open("input") as hdf5_input:
            self.input.from_hdf(hdf5_input)

    def run_if_interactive(self):
        """
        Run the job as Python library and store the result in the HDF5 File.

        Returns:
            int: job ID
        """
        self._interactive_library = True
        self.status.running = True
        alat, count, energy = ExampleExecutable().run_lib(self.input)
        self.interactive_cache["alat"].append(alat)
        self.interactive_cache["count"].append(count)
        self.interactive_cache["energy"].append(energy)

    def interactive_close(self):
        self._interactive_library = False
        self.to_hdf()
        with self.project_hdf5.open("output") as h5:
            for k in self.interactive_cache.keys():
                h5["generic/" + k] = np.array(self.interactive_cache[k])
        self.project.db.item_update(self._runtime(), self._job_id)
        self.status.finished = True


class ExampleInput(GenericParameters):
    """
    Input class for the ExampleJob based on the GenericParameters class.

    Args:
        input_file_name (str): Name of the input file - optional
    """

    def __init__(self, input_file_name=None):
        super(ExampleInput, self).__init__(
            input_file_name=input_file_name, table_name="input_inp", comment_char="#"
        )

    def load_default(self):
        """
        Loading the default settings for the input file.
        """
        input_str = """\
alat    3.2     # lattice constant (would be in a more realistic example in the structure file)
alpha   0.1     # noise amplitude
a_0     3       # equilibrium lattice constant
a_1     0
a_2     1.0     # 2nd order in energy (corresponds to bulk modulus)
a_3     0.0     # 3rd order
a_4     0.0     # 4th order
count   10      # number of calls (dummy)
epsilon 0.2     # energy prefactor of lennard jones
sigma   2.4     # distance unit of lennard jones
cutoff  4.0     # cutoff length (relative to sigma)
write_restart True
read_restart False
"""
        self.load_string(input_str)


class AtomisticExampleJob(ExampleJob, GenericInteractive):
    """
    ExampleJob generating a list of random numbers to simulate energy fluctuations.

    Args:
        project (ProjectHDFio): ProjectHDFio instance which points to the HDF5 file the job is stored in
        job_name (str): name of the job, which has to be unique within the project

    Attributes:

        .. attribute:: job_name

            name of the job, which has to be unique within the project

        .. attribute:: status

            execution status of the job, can be one of the following [initialized, appended, created, submitted, running,
                                                                      aborted, collect, suspended, refresh, busy, finished]

        .. attribute:: job_id

            unique id to identify the job in the pyiron database

        .. attribute:: parent_id

            job id of the predecessor job - the job which was executed before the current one in the current job series

        .. attribute:: master_id

            job id of the master job - a meta job which groups a series of jobs, which are executed either in parallel or in
            serial.

        .. attribute:: child_ids

            list of child job ids - only meta jobs have child jobs - jobs which list the meta job as their master

        .. attribute:: project

            Project instance the jobs is located in

        .. attribute:: project_hdf5

            ProjectHDFio instance which points to the HDF5 file the job is stored in

        .. attribute:: job_info_str

            short string to describe the job by it is job_name and job ID - mainly used for logging

        .. attribute:: working_directory

            working directory of the job is executed in - outside the HDF5 file

        .. attribute:: path

            path to the job as a combination of absolute file system path and path within the HDF5 file.

        .. attribute:: version

            Version of the hamiltonian, which is also the version of the executable unless a custom executable is used.

        .. attribute:: executable

            Executable used to run the job - usually the path to an external executable.

        .. attribute:: library_activated

            For job types which offer a Python library pyiron can use the python library instead of an external executable.

        .. attribute:: server

            Server object to handle the execution environment for the job.

        .. attribute:: queue_id

            the ID returned from the queuing system - it is most likely not the same as the job ID.

        .. attribute:: logger

            logger object to monitor the external execution and internal pyiron warnings.

        .. attribute:: restart_file_list

            list of files which are used to restart the calculation from these files.

        .. attribute:: job_type

            Job type object with all the available job types: ['ExampleJob', 'ParallelMaster', 'ScriptJob',
                                                               'ListMaster']
    """

    def __init__(self, project, job_name):
        super(AtomisticExampleJob, self).__init__(project, job_name)
        self.__version__ = "0.3"

        self.input = ExampleInput()
        self.executable = "python -m pyiron_atomistics.testing.executable"
        self.interactive_cache = defaultdict(list)
        self._velocity = None
        self._neigh = None
        self._unit = pint.UnitRegistry()

    @property
    def neigh(self):
        if self._neigh is None:
            self._neigh = self.structure.get_neighbors(
                num_neighbors=None,
                cutoff_radius=self.input["cutoff"] * self.input["sigma"],
            )
        return self._neigh

    @property
    def structure(self):
        """

        Returns:

        """
        return self._structure

    def _get_structure(self, frame=-1, wrap_atoms=True):
        try:
            return super()._get_structure(frame=frame, wrap_atoms=wrap_atoms)
        except IndexError:
            return self.structure

    def _number_of_structures(self):
        return max(1, super()._number_of_structures())

    @structure.setter
    def structure(self, structure):
        """

        Args:
            structure:

        Returns:

        """
        self._structure = structure
        if structure is not None:
            self.input["alat"] = self._structure.cell[0, 0]
            # print("set alat: {}".format(self.input["alat"]))

    def set_input_to_read_only(self):
        """
        This function enforces read-only mode for the input classes, but it has to be implement in the individual
        classes.
        """
        super(AtomisticExampleJob, self).set_input_to_read_only()
        self.input.read_only = True

    def to_hdf(self, hdf=None, group_name=None):
        """
        Store the ExampleJob object in the HDF5 File

        Args:
            hdf (ProjectHDFio): HDF5 group object - optional
            group_name (str): HDF5 subgroup name - optional
        """
        super(AtomisticExampleJob, self).to_hdf(hdf=hdf, group_name=group_name)
        self._structure_to_hdf()

    def from_hdf(self, hdf=None, group_name=None):
        """
        Restore the ExampleJob object in the HDF5 File

        Args:
            hdf (ProjectHDFio): HDF5 group object - optional
            group_name (str): HDF5 subgroup name - optional
        """
        super(AtomisticExampleJob, self).from_hdf(hdf=hdf, group_name=group_name)
        self._structure_from_hdf()

    def interactive_cells_getter(self):
        return self._structure.cell.copy()

    @property
    def _s_r(self):
        return self.input["sigma"] / self.neigh.flattened.distances

    def interactive_energy_pot_getter(self):
        return self.input["epsilon"] * (np.sum(self._s_r**12) - np.sum(self._s_r**6))

    def interactive_energy_tot_getter(self):
        return (
            self.interactive_energy_pot_getter() + self.interadtive_energy_kin_getter()
        )

    def interadtive_energy_kin_getter(self):
        v = np.einsum("ni,n->", self._velocity**2, self.structure.get_masses()) / 2
        return (
            (v * self._unit.angstrom**2 / self._unit.second**2 / 1e-30 * self._unit.amu)
            .to("eV")
            .magnitude
        )

    def interactive_forces_getter(self):
        all_values = self.input["epsilon"] * np.einsum(
            "ni,n,n->ni",
            self.neigh.flattened.vecs,
            1 / self.neigh.flattened.distances**2,
            12 * self._s_r**12 - 6 * self._s_r**6,
        )
        forces = np.zeros_like(self.structure.positions)
        np.add.at(forces, self.neigh.flattened.atom_numbers, all_values)
        return forces

    def interactive_positions_getter(self):
        return self._structure.positions

    def interactive_pressures_getter(self):
        pot_part = (
            self.input["epsilon"]
            * np.einsum(
                "ni,nj,n,n->ij",
                self.neigh.flattened.vecs,
                self.neigh.flattened.vecs,
                1 / self.neigh.flattened.distances**2,
                12 * self._s_r**12 - 6 * self._s_r**6,
            )
            * self._unit.electron_volt
        )
        kin_part = (
            np.einsum(
                "ni,nj,n->ij",
                self._velocity,
                self._velocity,
                self.structure.get_masses(),
            )
            * self._unit.angstrom**2
            / self._unit.second**2
            / 1e-30
            * self._unit.amu
        )
        return (
            (pot_part + kin_part) / self.structure.get_volume() / self._unit.angstrom**3
        ).to(self._unit.pascal).magnitude / 1e9

    def interactive_stress_getter(self):
        return np.random.random((len(self._structure), 3, 3))

    def interactive_steps_getter(self):
        return len(self.interactive_cache["steps"])

    def interactive_temperatures_getter(self):
        value = self.interadtive_energy_kin_getter() / len(self.structure)
        return (
            (value / self._unit.boltzmann_constant * self._unit.electron_volt)
            .to("kelvin")
            .magnitude
        )

    def interactive_indices_getter(self):
        return self._structure.indices

    def interactive_computation_time_getter(self):
        return np.random.random()

    def interactive_unwrapped_positions_getter(self):
        return self._structure.positions

    def interactive_volume_getter(self):
        return self._structure.get_volume()

    def interactive_initialize_interface(self):
        self._interactive_library = True

    def run_if_interactive(self):
        """
        Run the job as Python library and store the result in the HDF5 File.

        Returns:
            int: job ID
        """
        self._neigh = None
        if self._generic_input["calc_mode"] == "md":
            self._velocity = np.random.randn(len(self._structure), 3) / 1000
        elif self._velocity is None:
            self._velocity = np.zeros((len(self._structure), 3))
        GenericInteractive.run_if_interactive(self)
        self.interactive_collect()
