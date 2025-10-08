# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

import copy
import numbers
import os
import posixpath
import warnings
from functools import wraps
from typing import Callable, Tuple, Union

import numpy as np
from ase.io import write as ase_write
from pyiron_base import (
    GenericJob as GenericJobCore,
)
from pyiron_base import (
    GenericMaster,
    GenericParameters,
)
from pyiron_snippets.deprecate import deprecate
from pyiron_snippets.logger import logger

from pyiron_atomistics.atomistics.structure.atoms import Atoms
from pyiron_atomistics.atomistics.structure.has_structure import HasStructure
from pyiron_atomistics.atomistics.structure.neighbors import NeighborsTrajectory

try:
    from pyiron_base import ProjectGUI
except (ImportError, TypeError, AttributeError):
    pass

__author__ = "Jan Janssen"
__copyright__ = (
    "Copyright 2021, Max-Planck-Institut für Eisenforschung GmbH - "
    "Computational Materials Design (CM) Department"
)
__version__ = "1.0"
__maintainer__ = "Jan Janssen"
__email__ = "janssen@mpie.de"
__status__ = "production"
__date__ = "Sep 1, 2017"


class AtomisticGenericJob(GenericJobCore, HasStructure):
    """
    Atomistic Generic Job class extends the Generic Job class with all the functionality to run jobs containing
    atomistic structures. From this class all specific atomistic Hamiltonians are derived. Therefore it should contain
    the properties/routines common to all atomistic jobs. The functions in this module should be as generic as possible.

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
        super(AtomisticGenericJob, self).__init__(project, job_name)
        self.__version__ = "0.1"
        self._structure = None
        self._generic_input = GenericInput()
        self.output = GenericOutput(job=self)
        self.map_functions = MapFunctions()

    @property
    def structure(self):
        """

        Returns:

        """
        return self._structure

    @structure.setter
    def structure(self, basis):
        """

        Args:
            basis:

        Returns:

        """
        self._generic_input["structure"] = "atoms"
        self._structure = basis

    def set_input_to_read_only(self):
        """
        This function enforces read-only mode for the input classes, but it has to be implement in the individual
        classes.
        """
        self._generic_input.read_only = True

    def create_pipeline(self, step_lst, delete_existing_job=False):
        """
        Create a job pipeline

        Args:
            step_lst (list): List of functions which create calculations

        Returns:
            FlexibleMaster:
        """
        return self.project.create_pipeline(
            job=self, step_lst=step_lst, delete_existing_job=delete_existing_job
        )

    def _after_generic_copy_to(self, original, new_database_entry, reloaded):
        if self._structure is None:
            self._structure = copy.copy(original._structure)

    def calc_minimize(
        self,
        ionic_energy_tolerance=0,
        ionic_force_tolerance=1e-4,
        e_tol=None,
        f_tol=None,
        max_iter=1000,
        pressure=None,
        n_print=1,
    ):
        """

        Args:
            ionic_energy_tolerance (float): Maximum energy difference between 2 steps
            ionic_force_tolerance (float): Maximum force magnitude that each of atoms is allowed to have
            e_tol (float): same as ionic_energy_tolerance (deprecated)
            f_tol (float): same as ionic_force_tolerance (deprecated)
            max_iter (int): Maximum number of force evluations
            pressure (float/list): Targetpressure values
            n_print (int): Print period

        Returns:

        """
        if e_tol is not None:
            warnings.warn(
                "e_tol is deprecated as of vers. 0.3.0. It is not guaranteed to be in service in vers. 0.4.0"
            )
        if f_tol is not None:
            warnings.warn(
                "f_tol is deprecated as of vers. 0.3.0. It is not guaranteed to be in service in vers. 0.4.0"
            )
        self._generic_input["calc_mode"] = "minimize"
        if max_iter is not None:
            self._generic_input["max_iter"] = int(max_iter)
        else:
            self._generic_input["max_iter"] = max_iter
        if isinstance(pressure, list):
            self._generic_input["pressure"] = [
                float(p) if p is not None else p for p in pressure
            ]
        elif pressure is not None:
            self._generic_input["pressure"] = float(pressure)
        else:
            self._generic_input["pressure"] = pressure
        self._generic_input.remove_keys(
            ["temperature", "n_ionic_steps", "n_print", "velocity"]
        )

    def calc_static(self):
        """

        Returns:

        """
        self._generic_input["calc_mode"] = "static"
        self._generic_input.remove_keys(
            [
                "max_iter",
                "pressure",
                "temperature",
                "n_ionic_steps",
                "n_print",
                "velocity",
            ]
        )

    def calc_md(
        self,
        temperature=None,
        pressure=None,
        n_ionic_steps=1000,
        time_step=None,
        n_print=100,
        temperature_damping_timescale=100.0,
        pressure_damping_timescale=None,
        seed=None,
        tloop=None,
        initial_temperature=True,
        langevin=False,
    ):
        self._generic_input["calc_mode"] = "md"
        if isinstance(temperature, list):
            self._generic_input["temperature"] = [float(t) for t in temperature]
        elif temperature is not None:
            self._generic_input["temperature"] = float(temperature)
        else:
            self._generic_input["temperature"] = temperature
        self._generic_input["n_ionic_steps"] = int(n_ionic_steps)
        self._generic_input["n_print"] = int(n_print)
        self._generic_input["temperature_damping_timescale"] = float(
            temperature_damping_timescale
        )
        if isinstance(pressure, list):
            self._generic_input["pressure"] = [
                float(p) if p is not None else p for p in pressure
            ]
        elif pressure is not None:
            self._generic_input["pressure"] = float(pressure)
        if pressure_damping_timescale is not None:
            self._generic_input["pressure_damping_timescale"] = float(
                pressure_damping_timescale
            )
        if time_step is not None:
            self._generic_input["time_step"] = int(time_step)
        self._generic_input.remove_keys(["max_iter"])

    def from_dict(self, obj_dict):
        super().from_dict(obj_dict=obj_dict)
        self._generic_input.from_dict(obj_dict=obj_dict["input"]["generic"])

    def to_dict(self):
        job_dict = super(AtomisticGenericJob, self).to_dict()
        job_dict.update(
            {"input/generic/" + k: v for k, v in self._generic_input.to_dict().items()}
        )
        return job_dict

    def store_structure(self):
        """
        Create :class:`~.StructureContainer` job with the initial structure of
        the job and sets that jobs :attr:`~.parent_id` from this job.

        Returns:
            :class:`~.StructureContainer`: job containing initial structure of
            this job
        """
        if self.structure is not None:
            structure_container = self.create_job(
                job_type=self.project.job_type.StructureContainer,
                job_name=self.job_name + "_structure",
            )
            structure_container.structure = self.structure
            self.parent_id = structure_container.job_id
            return structure_container
        else:
            ValueError("There is no structure attached to the current Job.")

    @deprecate(
        "Call animate_structures() instead.  Arguments stride/center_of_mass/atom_indices/snapshot_indices/repeat "
        "can be emulated by calling trajectory() first."
    )
    def animate_structure(
        self,
        spacefill: bool = True,
        show_cell: bool = True,
        stride: int = 1,
        center_of_mass: bool = False,
        particle_size: float = 0.5,
        camera: str = "orthographic",
        atom_indices: Union[list, np.ndarray] = None,
        snapshot_indices: Union[list, np.ndarray] = None,
        repeat: Union[int, Tuple[int, int, int]] = None,
    ):
        """
        Animates the job if a trajectory is present

        Args:
            spacefill (bool): If True, then atoms are visualized in spacefill stype
            show_cell (bool): True if the cell boundaries of the structure is to be shown
            stride (int): show animation every stride [::stride]
                          use value >1 to make animation faster
                           default=1
            particle_size (float): Scaling factor for the spheres representing the atoms.
                                    (The radius is determined by the atomic number)
            center_of_mass (bool): False (default) if the specified positions are w.r.t. the origin
            camera (str):
                camera perspective, choose from "orthographic" or "perspective"
            atom_indices (list/numpy.ndarray): The atom indices for which the trajectory should be generated
            snapshot_indices (list/numpy.ndarray): The snapshots for which the trajectory should be generated
            repeat (int/3-tuple of int): Repeat the structures by this before animating

        Returns:
            animation: nglview IPython widget

        """

        if self.number_of_structures <= 1:
            raise ValueError("job must have more than one structure to animate!")

        traj = self.trajectory(
            stride=stride,
            center_of_mass=center_of_mass,
            atom_indices=atom_indices,
            snapshot_indices=snapshot_indices,
        )
        if repeat is not None:
            traj = traj.transform_structures(lambda s: s.repeat(repeat))

        if self.structure.cell is None:
            show_cell = False

        animation = traj.animate_structures(
            spacefill, show_cell, center_of_mass, particle_size, camera
        )
        return animation

    def view_structure(self, snapshot=-1, spacefill=True, show_cell=True):
        """

        Args:
            snapshot (int): Snapshot of the trajectory one wants
            spacefill (bool):
            show_cell (bool):

        Returns:
            view: nglview IPython widget

        """
        import nglview

        atoms = self.get_structure(snapshot)
        picture = nglview.show_ase(atoms)
        if spacefill:
            picture.add_spacefill(radius_type="vdw", scale=0.5)
            picture.remove_ball_and_stick()
        else:
            picture.add_ball_and_stick()
        if show_cell:
            if atoms.cell is not None:
                picture.add_unitcell()
        return picture

    def validate_ready_to_run(self):
        """

        Returns:

        """
        if not self.structure and self._generic_input["structure"] == "atoms":
            raise ValueError(
                "This job does not contain a valid structure: {}".format(self.job_name)
            )

    def db_entry(self):
        """
        Generate the initial database entry

        Returns:
            (dict): db_dict
        """
        db_dict = super(AtomisticGenericJob, self).db_entry()
        if self.structure:
            if isinstance(self.structure, Atoms):
                parent_structure = self.structure.get_parent_basis()
            else:
                parent_structure = self.structure.copy()
            db_dict["ChemicalFormula"] = parent_structure.get_chemical_formula()
        return db_dict

    def restart(self, job_name=None, job_type=None):
        """
        Restart a new job created from an existing calculation.
        Args:
            project (pyiron_atomistics.project.Project instance): Project instance at which the new job should be created
            job_name (str): Job name
            job_type (str): Job type

        Returns:
            new_ham: New job
        """
        new_ham = super(AtomisticGenericJob, self).restart(
            job_name=job_name, job_type=job_type
        )
        if isinstance(new_ham, GenericMaster) and not isinstance(self, GenericMaster):
            new_child = self.restart(job_name=None, job_type=None)
            new_ham.append(new_child)
        if self.number_of_structures > 0:
            new_ham.structure = self.get_structure(frame=-1)
        else:
            new_ham.structure = self.structure.copy()
        new_ham._generic_input["structure"] = "atoms"
        return new_ham

    @deprecate("use job.files instead!")
    def get_workdir_file(self, filename: str) -> None:
        """
        Checks if a given file exists within the job's working directory and returns the absolute path to it.

        ToDo: Move this to pyiron_base since this is more generic.

        Args:
            filename (str): The name of the file

        Returns:
            str: The name absolute path of the file in the working directory

        Raises:
            FileNotFoundError: Raised if the given file does not exist.
        """
        appended_path = posixpath.join(self.working_directory, filename)
        if not os.path.isfile(appended_path):
            raise FileNotFoundError(
                f"File {filename} not found in working directory: {self.working_directory}"
            )
        return appended_path

    # Required functions
    def continue_with_restart_files(self, job_type=None, job_name=None):
        """

        Args:
            job_type:
            job_name:

        Returns:

        """
        if job_name is None:
            job_name = "{}_continue".format(self.job_name)
        new_ham = self.restart(job_type=job_type, job_name=job_name)
        if self.status.initialized:
            self._job_id = self.save()
        new_ham.parent_id = self.job_id
        new_ham._generic_input["structure"] = "continue_final"
        return new_ham

    def continue_with_final_structure(self, job_type=None, job_name=None):
        """

        Args:
            job_type:
            job_name:

        Returns:

        """
        if job_name is None:
            job_name = "{}_continue".format(self.job_name)
        if job_type is None:
            job_type = self.__name__
        new_ham = self.create_job(job_type, job_name)
        if self.status.initialized:
            self._job_id = self.save()
        new_ham.parent_id = self.job_id
        if self.status.finished:
            new_ham.structure = self.get_structure(iteration_step=-1)
            new_ham._generic_input["structure"] = "atoms"
        else:
            new_ham._generic_input["structure"] = "continue_final"
        return new_ham

    def trajectory(
        self,
        stride=1,
        center_of_mass=False,
        atom_indices=None,
        snapshot_indices=None,
        overwrite_positions=None,
        overwrite_cells=None,
    ):
        """
        Returns a `Trajectory` instance containing the necessary information to describe the evolution of the atomic
        structure during the atomistic simulation.

        Args:
            stride (int): The trajectories are generated with every 'stride' steps
            center_of_mass (bool): False (default) if the specified positions are w.r.t. the origin
            atom_indices (list/ndarray): The atom indices for which the trajectory should be generated
            snapshot_indices (list/ndarray): The snapshots for which the trajectory should be generated
            overwrite_positions (list/ndarray): List of positions that are meant to overwrite the existing
                                                      trajectory. Useful to wrap coordinates for example
            overwrite_cells(list/ndarray): List of cells that are meant to overwrite the existing
                                                 trajectory. Only used when `overwrite_positions` is defined. This must
                                                 have the same length of `overwrite_positions`

        Returns:
            pyiron_atomistics.atomistics.job.atomistic.Trajectory: Trajectory instance

        """
        cells = self.output.cells
        if len(self.output.indices) != 0:
            indices = self.output.indices
        else:
            indices = [self.structure.indices] * len(
                cells
            )  # Use the same indices throughout
        if overwrite_positions is not None:
            positions = np.array(overwrite_positions).copy()
            if overwrite_cells is not None:
                if overwrite_cells.shape == (len(positions), 3, 3):
                    cells = np.array(overwrite_cells).copy()
                else:
                    raise ValueError(
                        "overwrite_cells must be compatible with the positions!"
                    )
        else:
            positions = self.output.positions.copy()
        conditions = list()
        if isinstance(cells, (list, np.ndarray)):
            if len(cells) == 0:
                conditions.append(True)
            else:
                conditions.append(cells[0] is None)
        conditions.append(cells is None)
        if any(conditions):
            max_pos = np.max(np.max(positions, axis=0), axis=0)
            max_pos[np.abs(max_pos) < 1e-2] = 10
            cell = np.eye(3) * max_pos
            cells = np.array([cell] * len(positions))

        if len(positions) != len(cells):
            raise ValueError("The positions must have the same length as the cells!")
        if snapshot_indices is not None:
            positions = positions[snapshot_indices]
            cells = cells[snapshot_indices]
            indices = indices[snapshot_indices]
        if atom_indices is None:
            return Trajectory(
                positions[::stride],
                self.structure.get_parent_basis(),
                center_of_mass=center_of_mass,
                cells=cells[::stride],
                indices=indices[::stride],
            )
        else:
            sub_struct = self.structure.get_parent_basis()[atom_indices]
            if len(sub_struct.species) < len(self.structure.species):
                # Then `sub_struct` has had its indices remapped so they run from 0 to the number of species - 1
                # But the `indices` array is unaware of this and needs to be remapped to this new space
                original_symbols = np.array(
                    [el.Abbreviation for el in self.structure.species]
                )
                sub_symbols = np.array([el.Abbreviation for el in sub_struct.species])

                map_ = np.array(
                    [
                        np.argwhere(original_symbols == symbol)[0, 0]
                        for symbol in sub_symbols
                    ],
                    dtype=int,
                )

                remapped_indices = np.array(indices)
                for i_sub, i_original in enumerate(map_):
                    np.place(remapped_indices, indices == i_original, i_sub)
            else:
                remapped_indices = indices

            return Trajectory(
                positions[::stride, atom_indices, :],
                sub_struct,
                center_of_mass=center_of_mass,
                cells=cells[::stride],
                indices=np.asarray(remapped_indices)[::stride, atom_indices],
            )

    def write_traj(
        self,
        filename,
        file_format=None,
        parallel=True,
        append=False,
        stride=1,
        center_of_mass=False,
        atom_indices=None,
        snapshot_indices=None,
        overwrite_positions=None,
        overwrite_cells=None,
        **kwargs,
    ):
        """
        Writes the trajectory in a given file file_format based on the `ase.io.write`_ function.

        Args:
            filename (str): Filename of the output
            file_format (str): The specific file_format of the output
            parallel (bool): ase parameter
            append (bool): ase parameter
            stride (int): Writes trajectory every `stride` steps
            center_of_mass (bool): True if the positions are centered on the COM
            atom_indices (list/numpy.ndarray): The atom indices for which the trajectory should be generated
            snapshot_indices (list/numpy.ndarray): The snapshots for which the trajectory should be generated
            overwrite_positions (list/numpy.ndarray): List of positions that are meant to overwrite the existing
                                                      trajectory. Useful to wrap coordinates for example
            overwrite_cells(list/numpy.ndarray): List of cells that are meant to overwrite the existing
                                                 trajectory. Only used when `overwrite_positions` is defined. This must
                                                 have the same length of `overwrite_positions`
            **kwargs: Additional ase arguments

        .. _ase.io.write: https://wiki.fysik.dtu.dk/ase/_modules/ase/io/formats.html#write
        """
        traj = self.trajectory(
            stride=stride,
            center_of_mass=center_of_mass,
            atom_indices=atom_indices,
            snapshot_indices=snapshot_indices,
            overwrite_positions=overwrite_positions,
            overwrite_cells=overwrite_cells,
        )
        # Using thr ASE output writer
        ase_write(
            filename=filename,
            images=traj,
            format=file_format,
            parallel=parallel,
            append=append,
            **kwargs,
        )

    def get_neighbors_snapshots(
        self, snapshot_indices=None, num_neighbors=12, **kwargs
    ):
        """
        Get the neighbors only for the required snapshots from the trajectory

        Args:
            snapshot_indices (list/numpy.ndarray): Snapshots for which the the neighbors need to be computed
                                                   (eg. [1, 5, 10,..., 100]
            num_neighbors (int): The cutoff for the number of neighbors
            **kwargs (dict): Additional arguments to be passed to the `get_neighbors()` routine
                             (eg. cutoff_radius, norm_order , etc.)

        Returns:
            pyiron_atomistics.atomistics.structure.neighbors.NeighborsTrajectory: `NeighborsTraj` instances
                                                                             containing the neighbor information.
        """
        return self.trajectory().get_neighbors_snapshots(
            snapshot_indices=snapshot_indices, num_neighbors=num_neighbors, **kwargs
        )

    def get_neighbors(self, start=0, stop=-1, stride=1, num_neighbors=12, **kwargs):
        """
        Get the neighbors for a given section of the trajectory

        Args:
            start (int): Start point of the slice of the trajectory to be sampled
            stop (int): End point of of the slice of the trajectory to be sampled
            stride (int): Samples the snapshots evert `stride` steps
            num_neighbors (int): The cutoff for the number of neighbors
            **kwargs (dict): Additional arguments to be passed to the `get_neighbors()` routine
                             (eg. cutoff_radius, norm_order , etc.)

        Returns:
            pyiron_atomistics.atomistics.structure.neighbors.NeighborsTrajectory: `NeighborsTraj` instances
                                                                             containing the neighbor information.
        """
        return self.trajectory().get_neighbors(
            start=start, stop=stop, stride=stride, num_neighbors=num_neighbors, **kwargs
        )

    # Compatibility functions
    @deprecate("Use get_structure()")
    def get_final_structure(self):
        """
        Get the final structure calculated from the job.

        Returns:
            :class:`.Atoms`
        """
        return self.get_structure(iteration_step=-1)

    def _get_structure(self, frame=-1, wrap_atoms=True):
        if self.structure is None:
            raise AssertionError("Structure not set")
        if self.output.cells is not None:
            try:
                cell = self.output.cells[frame]
            except IndexError:
                if wrap_atoms:
                    raise IndexError("cell at step ", frame, " not found") from None
                cell = None
        if self.output.indices is not None:
            try:
                indices = self.output.indices[frame]
            except IndexError:
                indices = None
        if indices is not None and len(indices) != len(self.structure):
            snapshot = Atoms(
                species=self.structure.species,
                indices=indices,
                positions=np.zeros(indices.shape + (3,)),
                cell=cell,
                pbc=self.structure.pbc,
            )
        else:
            snapshot = self.structure.copy()
            if cell is not None:
                snapshot.cell = cell
            if indices is not None:
                snapshot.set_array("indices", indices)
        if self.output.positions is not None:
            if wrap_atoms:
                snapshot.positions = self.output.positions[frame]
                snapshot.center_coordinates_in_unit_cell()
            elif len(self.output.unwrapped_positions) > max([frame, 0]):
                snapshot.positions = self.output.unwrapped_positions[frame]
            else:
                snapshot.positions += self.output.total_displacements[frame]
        return snapshot

    def _number_of_structures(self):
        return self.output.positions.shape[0]

    def map(self, function, parameter_lst):
        """
        Create :class:`.MapMaster` with the current job as reference job.

        The job name is created as 'map_{self.name}'

        Args:
            function (callable): passed as `modify_function` to the map master
            parameter_list (list): passed as `parameter_list` to the map master

        Returns:
            :class:`.MapMaster`: newly created master job
        """
        master = self.create_job(
            job_type=self.project.job_type.MapMaster, job_name="map_" + self.job_name
        )
        master.modify_function = function
        master.parameter_list = parameter_lst
        return master

    def gui(self):
        """

        Returns:

        """
        ProjectGUI(self)

    def _structure_to_dict(self):
        if self.structure is not None and self._generic_input["structure"] == "atoms":
            return {"structure/" + k: v for k, v in self.structure.to_dict().items()}
        else:
            return None

    def _structure_from_dict(self, obj_dict):
        if (
            "structure" in obj_dict["input"].keys()
            and self._generic_input["structure"] == "atoms"
        ):
            self.structure = Atoms().from_dict(obj_dict=obj_dict["input"]["structure"])

    def _structure_to_hdf(self):
        data_dict = self._structure_to_dict()
        if data_dict is not None:
            with self.project_hdf5.open("input") as hdf5_input:
                hdf5_input.write_dict_to_hdf(data_dict)

    def _structure_from_hdf(self):
        if (
            "structure" in self.project_hdf5["input"].list_groups()
            and self._generic_input["structure"] == "atoms"
        ):
            with self.project_hdf5.open("input/structure") as hdf5_input:
                self.structure = Atoms().from_dict(
                    obj_dict=hdf5_input.read_dict_from_hdf(recursive=True)
                )

    def _write_chemical_formular_to_database(self):
        if self.structure:
            parent_structure = self.structure.get_parent_basis()
            self.project.db.item_update(
                {"ChemicalFormula": parent_structure.get_chemical_formula()},
                self._job_id,
            )

    def _before_successor_calc(self, ham):
        if ham._generic_input["structure"] == "continue_final":
            ham.structure = self.get_structure(iteration_step=-1)
            ham.to_hdf()


def set_structure(job, parameter):
    job.structure = parameter
    return job


class MapFunctions(object):
    def __init__(self):
        self.set_structure = set_structure


class Trajectory(HasStructure):
    """
    A trajectory instance compatible with the ase.io class
    """

    def __init__(
        self, positions, structure, center_of_mass=False, cells=None, indices=None
    ):
        """

        Args:
            positions (ndarray): The array of the trajectory in cartesian coordinates
            structure (pyiron.atomistics.structure.atoms.Atoms): The initial structure instance from which the species
                                                                 info is derived
            center_of_mass (bool): False (default) if the specified positions are w.r.t. the origin
            cells (None/ndarray): Optional argument of the cell shape at every time step (Nx3x3 array) when the volume
                                  varies
            indices (None/ndarray): Indices for the species in the structure
        """

        if center_of_mass:
            pos = np.copy(positions)
            pos[:, :, 0] = (pos[:, :, 0].T - np.mean(pos[:, :, 0], axis=1)).T
            pos[:, :, 1] = (pos[:, :, 1].T - np.mean(pos[:, :, 1], axis=1)).T
            pos[:, :, 2] = (pos[:, :, 2].T - np.mean(pos[:, :, 2], axis=1)).T
            self._positions = pos
        else:
            self._positions = positions
        self._structure = structure
        self._cells = cells
        self._indices = indices
        # If the indices don't exist, we construct the indices based on the indices of the initial structure
        if self._indices is None:
            self._indices = np.broadcast_to(
                self._structure.indices,
                (len(self._positions), len(self._structure.indices)),
            )

    def __getitem__(self, item):
        if isinstance(item, numbers.Integral):
            new_structure = self._structure.copy()
            if self._cells is not None:
                new_structure.cell = self._cells[item]
            if self._indices is not None:
                new_structure.set_array("indices", self._indices[item])
            new_structure.positions = self._positions[item]
            # This step is necessary for using ase.io.write for trajectories
            new_structure.arrays["positions"] = new_structure.positions
            # new_structure.arrays['cells'] = new_structure.cell
            return new_structure
        elif isinstance(item, (list, np.ndarray, slice)):
            snapshots = np.arange(len(self), dtype=int)[item]
            if self._cells is not None:
                return Trajectory(
                    positions=self._positions[snapshots],
                    cells=self._cells[snapshots],
                    structure=self[snapshots[0]],
                    indices=self._indices[snapshots],
                )
            else:
                return Trajectory(
                    positions=self._positions[snapshots],
                    cells=self._cells,
                    structure=self[snapshots[0]],
                    indices=self._indices[snapshots],
                )

    def _get_structure(self, frame=-1, wrap_atoms=True):
        return self[frame]

    def __len__(self):
        return len(self._positions)

    _number_of_structures = __len__

    def get_neighbors_snapshots(
        self, snapshot_indices=None, num_neighbors=12, **kwargs
    ):
        """
        Get the neighbors only for the required snapshots from the trajectory

        Args:
            snapshot_indices (list/numpy.ndarray): Snapshots for which the the neighbors need to be computed
                                                   (eg. [1, 5, 10,..., 100]
            num_neighbors (int): The cutoff for the number of neighbors
            **kwargs (dict): Additional arguments to be passed to the `get_neighbors()` routine
                             (eg. cutoff_radius, norm_order , etc.)

        Returns:
            pyiron_atomistics.atomistics.structure.neighbors.NeighborsTrajectory: `NeighborsTraj` instances
                                                                             containing the neighbor information.
        """
        if snapshot_indices is None:
            snapshot_indices = np.arange(len(self), dtype=int)

        n_obj = NeighborsTrajectory(
            has_structure=self[snapshot_indices], num_neighbors=num_neighbors, **kwargs
        )
        n_obj.compute_neighbors()
        return n_obj

    def get_neighbors(self, start=0, stop=-1, stride=1, num_neighbors=12, **kwargs):
        """
        Get the neighbors for a given section of the trajectory

        Args:
            start (int): Start point of the slice of the trajectory to be sampled
            stop (int): End point of of the slice of the trajectory to be sampled
            stride (int): Samples the snapshots evert `stride` steps
            num_neighbors (int): The cutoff for the number of neighbors
            **kwargs (dict): Additional arguments to be passed to the `get_neighbors()` routine
                             (eg. cutoff_radius, norm_order , etc.)

        Returns:
            pyiron_atomistics.atomistics.structure.neighbors.NeighborsTrajectory: `NeighborsTraj` instances
                                                                             containing the neighbor information.
        """
        snapshot_indices = np.arange(len(self))[start:stop:stride]
        return self.get_neighbors_snapshots(
            snapshot_indices=snapshot_indices, num_neighbors=num_neighbors, **kwargs
        )


class GenericInput(GenericParameters):
    def __init__(self, input_file_name=None, table_name="generic"):
        super(GenericInput, self).__init__(
            input_file_name=input_file_name,
            table_name=table_name,
            comment_char="#",
            separator_char="=",
        )

    def load_default(self):
        """
        Loads the default file content
        """
        file_content = """\
calc_mode=static # static, minimize, md
structure=atoms # atoms, continue_final
"""
        self.load_string(file_content)


def _suppress_notfound(meth):
    @wraps(meth)
    def f(*args, **kwargs):
        try:
            return meth(*args, **kwargs)
        except (ValueError, KeyError):
            logger.warning(f"Could not access {meth.__name__}, returning None!")
            return None

    return f


class GenericOutput(object):
    def __init__(self, job):
        self._job = job

    @property
    @_suppress_notfound
    def cells(self):
        return self._job.content["output/generic/cells"]

    @property
    @_suppress_notfound
    def energy_pot(self):
        return self._job.content["output/generic/energy_pot"]

    @property
    @_suppress_notfound
    def energy_tot(self):
        return self._job.content["output/generic/energy_tot"]

    @property
    @_suppress_notfound
    def forces(self):
        return self._job.content["output/generic/forces"]

    @property
    def force_max(self):
        """
        maximum force magnitude of each step which is used for
        convergence criterion of structure optimizations
        """
        return np.linalg.norm(self.forces, axis=-1).max(axis=-1)

    @property
    @_suppress_notfound
    def positions(self):
        return self._job.content["output/generic/positions"]

    @property
    @_suppress_notfound
    def pressures(self):
        return self._job.content["output/generic/pressures"]

    @property
    @_suppress_notfound
    def steps(self):
        return self._job.content["output/generic/steps"]

    @property
    @_suppress_notfound
    def temperature(self):
        return self._job.content["output/generic/temperature"]

    @property
    @_suppress_notfound
    def computation_time(self):
        return self._job.content["output/generic/computation_time"]

    @property
    def unwrapped_positions(self):
        try:
            unwrapped_positions = self._job.content[
                "output/generic/unwrapped_positions"
            ]
            return unwrapped_positions
        except KeyError:
            return self._job.structure.positions + self.total_displacements

    @property
    @_suppress_notfound
    def volume(self):
        return self._job.content["output/generic/volume"]

    @property
    @_suppress_notfound
    def indices(self):
        return self._job.content["output/generic/indices"]

    @property
    def displacements(self):
        """
        Output for 3-d displacements between successive snapshots, with minimum image convention.
        For the total displacements from the initial configuration, use total_displacements
        This algorithm collapses if (if `unwrapped_positions` is not available in output):
            - the ID's are not consistent (i.e. you can also not change the number of atoms)
            - there are atoms which move by more than half a box length in any direction within
                two snapshots (due to periodic boundary conditions)
        """
        try:
            unwrapped_positions = self._job.content[
                "output/generic/unwrapped_positions"
            ]
            return np.diff(
                np.append([self._job.structure.positions], unwrapped_positions, axis=0),
                axis=0,
            )
        except KeyError:
            return self.get_displacements(
                self._job.structure, self.positions, self.cells
            )

    @staticmethod
    def get_displacements(structure, positions, cells):
        """
        Output for 3-d displacements between successive snapshots, with minimum image convention.
        For the total displacements from the initial configuration, use total_displacements
        This algorithm collapses if:
        - the ID's are not consistent (i.e. you can also not change the number of atoms)
        - there are atoms which move by more than half a box length in any direction within two snapshots (due to
        periodic boundary conditions)

        Args:
            structure (pyiron.atomistics.structure.atoms.Atoms): The initial structure
            positions (numpy.ndarray/list): List of positions in cartesian coordinates (N_steps x N_atoms x 3)
            cells (numpy.ndarray/list): List of cells (N_steps x 3 x 3)

        Returns:
            numpy.ndarray: Displacements (N_steps x N_atoms x 3)

        """
        # Check if the cell changes in any snapshot
        c = cells.reshape(-1, 9)
        if np.max(c.max(axis=0) - c.min(axis=0)) > 1e-5:
            warnings.warn(
                "You are computing displacements in a simulation with periodic boundary conditions \n"
                "and a varying cell shape."
            )
        displacement = np.einsum("nki,nij->nkj", positions, np.linalg.inv(cells))
        displacement[1:] -= displacement[:-1]
        displacement[0] -= structure.get_scaled_positions()
        displacement[:, :, structure.pbc] -= np.rint(displacement)[:, :, structure.pbc]
        displacement = np.einsum("nki,nij->nkj", displacement, cells)
        return displacement

    @property
    def total_displacements(self):
        """
        Output for 3-d total displacements from the initial configuration, with minimum image convention.
        For the displacements for the successive snapshots, use displacements
        This algorithm collapses if (if `unwrapped_positions` is not available in the output):
            - the ID's are not consistent (i.e. you can also not change the number of atoms)
            - there are atoms which move by more than half a box length in any direction within
                two snapshots (due to periodic boundary conditions)
        """
        try:
            unwrapped_positions = self._job.content[
                "output/generic/unwrapped_positions"
            ]
            return unwrapped_positions - self._job.structure.positions
        except KeyError:
            return np.cumsum(self.displacements, axis=0)

    def __dir__(self):
        try:
            hdf5_path = self._job.content["output/generic"]
            return hdf5_path.list_nodes()
        except KeyError:
            return []
