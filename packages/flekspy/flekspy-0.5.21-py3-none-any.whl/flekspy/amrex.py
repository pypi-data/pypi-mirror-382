import numpy as np
from pathlib import Path
import re


class AMReXParticleHeader:
    """
    This class is designed to parse and store the information
    contained in an AMReX particle header file.
    """

    def __init__(self, header_filename):

        self.real_component_names = []
        self.int_component_names = []
        with open(header_filename, "r") as f:
            self.version_string = f.readline().strip()

            particle_real_type = self.version_string.split("_")[-1]
            if particle_real_type == "double":
                self.real_type = np.float64
            elif particle_real_type == "single":
                self.real_type = np.float32
            else:
                raise RuntimeError("Did not recognize particle real type.")
            self.int_type = np.int32

            self.dim = int(f.readline().strip())
            self.num_int_base = 2
            self.num_real_base = self.dim

            if self.dim == 3:
                self.real_component_names = ["x", "y", "z"]
            elif self.dim == 2:
                self.real_component_names = ["x", "y"]

            self.int_component_names = ["particle_id", "particle_cpu"]

            self.num_real_extra = int(f.readline().strip())
            for i in range(self.num_real_extra):
                self.real_component_names.append(f.readline().strip())
            self.num_int_extra = int(f.readline().strip())
            for i in range(self.num_int_extra):
                self.int_component_names.append(f.readline().strip())
            self.num_int = self.num_int_base + self.num_int_extra
            self.num_real = self.num_real_base + self.num_real_extra
            self.is_checkpoint = bool(int(f.readline().strip()))
            self.num_particles = int(f.readline().strip())
            self.max_next_id = int(f.readline().strip())
            self.finest_level = int(f.readline().strip())
            self.num_levels = self.finest_level + 1

            if not self.is_checkpoint:
                self.num_int_base = 0
                self.num_int_extra = 0
                self.num_int = 0

            self.grids_per_level = np.zeros(self.num_levels, dtype="int64")
            for level_num in range(self.num_levels):
                self.grids_per_level[level_num] = int(f.readline().strip())

            self.grids = [[] for _ in range(self.num_levels)]
            for level_num in range(self.num_levels):
                for grid_num in range(self.grids_per_level[level_num]):
                    entry = [int(val) for val in f.readline().strip().split()]
                    self.grids[level_num].append(tuple(entry))

    def __repr__(self):
        """
        Returns a string representation of the header contents.
        """
        level_info = "\n".join(
            [
                f"  Level {level_num}: {self.grids_per_level[level_num]} grids"
                for level_num in range(self.num_levels)
            ]
        )
        return (
            f"Version string: {self.version_string}\n"
            f"Dimensions: {self.dim}\n"
            f"Number of integer components: {self.num_int}\n"
            f"Integer component names: {self.int_component_names}\n"
            f"Number of real components: {self.num_real}\n"
            f"Real component names: {self.real_component_names}\n"
            f"Is checkpoint: {self.is_checkpoint}\n"
            f"Number of particles: {self.num_particles}\n"
            f"Max next ID: {self.max_next_id}\n"
            f"Finest level: {self.finest_level}\n"
            f"Number of levels: {self.num_levels}\n"
            f"{level_info}"
        )

    @property
    def idtype_str(self):
        return f"({self.num_int},)i4"

    @property
    def rdtype_str(self):
        if self.real_type == np.float64:
            return f"({self.num_real},)f8"
        elif self.real_type == np.float32:
            return f"({self.num_real},)f4"
        raise RuntimeError("Unrecognized real type.")


def read_amrex_binary_particle_file(fn, header):
    """
    This function returns the particle data stored in a particular
    plot file. It returns two numpy arrays, the
    first containing the particle integer data, and the second the
    particle real data.
    """
    ptype = "particles"
    base_fn = Path(fn) / ptype

    idtype = header.idtype_str
    fdtype = header.rdtype_str

    idata = np.empty((header.num_particles, header.num_int), dtype=header.int_type)
    rdata = np.empty((header.num_particles, header.num_real), dtype=header.real_type)

    ip = 0
    for lvl, level_grids in enumerate(header.grids):
        for which, count, where in level_grids:
            if count == 0:
                continue
            fn = base_fn / f"Level_{lvl}" / f"DATA_{which:05d}"

            with open(fn, "rb") as f:
                f.seek(where)
                if header.is_checkpoint:
                    ints = np.fromfile(f, dtype=idtype, count=count)
                    idata[ip : ip + count] = ints

                floats = np.fromfile(f, dtype=fdtype, count=count)
                rdata[ip : ip + count] = floats
            ip += count

    return idata, rdata


class AMReXParticleData:
    """
    This class provides an interface to the particle data in a plotfile.
    Data is loaded lazily upon first access to `idata` or `rdata`.
    """

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.ptype = "particles"

        self._idata = None
        self._rdata = None

        self._parse_main_header()
        self.header = AMReXParticleHeader(self.output_dir / self.ptype / "Header")

    def _load_data(self):
        """Loads the particle data from disk if it has not been loaded yet."""
        if self._idata is None:
            self._idata, self._rdata = read_amrex_binary_particle_file(
                self.output_dir, self.header
            )

    @property
    def idata(self):
        """Lazily loads and returns the integer particle data."""
        self._load_data()
        return self._idata

    @property
    def rdata(self):
        """Lazily loads and returns the real particle data."""
        self._load_data()
        return self._rdata

    def _parse_main_header(self):
        header_path = self.output_dir / "Header"
        with open(header_path, 'r') as f:
            f.readline() # version string
            num_fields = int(f.readline())
            # skip field names
            for _ in range(num_fields):
                f.readline()

            self.dim = int(f.readline())
            self.time = float(f.readline())
            f.readline() # prob_refine_ratio

            self.left_edge = [float(v) for v in f.readline().strip().split()]
            self.right_edge = [float(v) for v in f.readline().strip().split()]
            f.readline()
            #TODO check a 3D particle file for correctness!
            dim_line = f.readline().strip()
            matches = re.findall(r'\d+', dim_line)
            coords = [int(num) for num in matches]
            x1, y1, x2, y2, z1, z2 = coords
            dim_x = x2 - x1 + 1
            dim_y = y2 - y1 + 1
            dim_z = z2 - z1 + 1

            self.domain_dimensions = [dim_x, dim_y, dim_z]

    def __repr__(self):
        repr_str = (
            f"AMReXParticleData from {self.output_dir}\n"
            f"Time: {self.time}\n"
            f"Dimensions: {self.dim}\n"
            f"Domain Dimensions: {self.domain_dimensions}\n"
            f"Domain Edges: {self.left_edge} to {self.right_edge}\n"
            f"Integer component names: {self.header.int_component_names}\n"
            f"Real component names: {self.header.real_component_names}"
        )
        if self._idata is not None:
            repr_str += (
                f"\nParticle data shape (int): {self._idata.shape}\n"
                f"Particle data shape (real): {self._rdata.shape}"
            )
        else:
            repr_str += "\nParticle data: Not loaded (access .idata or .rdata to load)"
        return repr_str

    def select_particles_in_region(self, x_range=None, y_range=None, z_range=None):
        """
        Selectively loads real component data for particles that fall within a
        specified rectangular region.

        This method reads particle data chunk-by-chunk and filters it on-the-fly,
        avoiding loading the entire dataset into memory. Integer data is skipped
        for efficiency.

        Args:
            x_range (tuple, optional): A tuple (min, max) for the x-axis boundary.
            y_range (tuple, optional): A tuple (min, max) for the y-axis boundary.
            z_range (tuple, optional): A tuple (min, max) for the z-axis boundary.
                                       For 2D data, this is ignored.

        Returns:
            np.ndarray: A numpy array containing the real data for the
                        selected particles.
        """
        selected_rdata = []

        idtype = self.header.idtype_str
        fdtype = self.header.rdtype_str

        for lvl, level_grids in enumerate(self.header.grids):
            for which, count, where in level_grids:
                if count == 0:
                    continue

                fn = self.output_dir / self.ptype / f"Level_{lvl}" / f"DATA_{which:05d}"
                with open(fn, 'rb') as f:
                    f.seek(where)

                    if self.header.is_checkpoint:
                        # Skip over the integer data instead of reading it
                        bytes_to_skip = count * np.dtype(idtype).itemsize
                        f.seek(bytes_to_skip, 1)

                    floats = np.fromfile(f, dtype=fdtype, count=count)

                    # Create a boolean mask, starting with all True
                    mask = np.ones(count, dtype=bool)

                    if x_range:
                        x_coords = floats[:, 0]
                        mask &= (x_coords >= x_range[0]) & (x_coords <= x_range[1])

                    if y_range:
                        y_coords = floats[:, 1]
                        mask &= (y_coords >= y_range[0]) & (y_coords <= y_range[1])

                    if self.dim == 3 and z_range:
                        z_coords = floats[:, 2]
                        mask &= (z_coords >= z_range[0]) & (z_coords <= z_range[1])

                    # Apply the mask to the data
                    if np.any(mask):
                        selected_rdata.append(floats[mask])

        # Concatenate the lists of arrays into final numpy arrays
        final_rdata = np.concatenate(selected_rdata) if selected_rdata else np.empty((0, self.header.num_real), dtype=self.header.real_type)

        return final_rdata