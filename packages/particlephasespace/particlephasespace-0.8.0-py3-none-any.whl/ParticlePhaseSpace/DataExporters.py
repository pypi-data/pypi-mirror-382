import platform
import numpy as np
from numpy.lib import recfunctions
from ParticlePhaseSpace import PhaseSpace
from pathlib import Path
from abc import ABC, abstractmethod
from ParticlePhaseSpace import __phase_space_config__ as ps_cfg
from ParticlePhaseSpace import __particle_config__ as particle_cfg
from ParticlePhaseSpace import ParticlePhaseSpaceUnits
from ParticlePhaseSpace import UnitSet
import warnings

class _DataExportersBase(ABC):
    """
    Abstract base class to be inherited by other DataExporters
    """

    def __init__(self, PhaseSpaceInstance: PhaseSpace, output_location: (str, Path), output_name: str):

        if not isinstance(PhaseSpaceInstance, PhaseSpace):
            raise TypeError(f'PhaseSpaceInstance must be an instance of ParticlePhaseSpace.PhaseSpace,'
                            f'not {type(PhaseSpaceInstance)}')
        self._PS = PhaseSpaceInstance

        self._units = self._PS._units
        self._set_expected_units()
        self._check_and_convert_units()
        self._output_location = Path(output_location)
        self._check_output_location_exists()
        self._output_name = output_name
        self._required_columns = []  # filled in _define_required_columns
        self._define_required_columns()
        self._check_required_columns_allowed()
        self._fill_required_columns()
        self._export_data()

    def _check_output_location_exists(self):
        if not self._output_location.is_dir():
            raise FileNotFoundError(f'output_location should be an existing path;'
                                    f'\n{self._output_location}\n does not exist')

    def _check_required_columns_allowed(self):
        """
        check that the columns that are required for data export are actually allowed
        :return:
        """
        allowed_columns = ps_cfg.required_columns + list(ps_cfg.allowed_columns.keys())
        for col in self._required_columns:
            if not col in allowed_columns:
                raise AttributeError(f'column: "{col}" is required for export, but is not an allowed column name.')

    def _fill_required_columns(self):
        """
        fill in any data required for the export
        :return:
        """
        for col in self._required_columns:
            if col in ps_cfg.required_columns:
                continue
            if not col in self._PS.ps_data.columns:
                try:
                    self._PS.fill.__getattribute__(ps_cfg.allowed_columns[col])()
                except (AttributeError, KeyError):
                    raise AttributeError(f'unable to fill required column {col}')

    def _check_and_convert_units(self):
        if not isinstance(self._units, UnitSet):
            raise TypeError('The units of the PhaseSpace data are invalid')
        if not hasattr(self,'_expected_units'):
            raise AttributeError("_expected_units must be set in the _set_expected_units method")
        if not isinstance(self._expected_units, UnitSet):
            raise TypeError('_expected_units must be an instnace of _UnitSet')

        if not self._units.label == self._expected_units.label:
            # will eventually put conversion method here
            try:
                self._PS.set_units(self._expected_units)
            except AttributeError:
                raise AttributeError(f'unable to convert data to requested units: {self._expected_units.label}')

    @abstractmethod
    def _define_required_columns(self):
        """
        user should fill in the required columns here
        :return:
        """
        pass

    @abstractmethod
    def _export_data(self):
        """
        this is the method which should actually perform the data export
        :return:
        """
        pass

    @abstractmethod
    def _set_expected_units(self):
        pass


class Topas_Exporter(_DataExportersBase):
    """
    output the phase space to `topas ascii or binary format <https://topas.readthedocs.io/en/latest/parameters/source/phasespace.html>`_.
    the default output is ascii, the user can output binary by passing the flag `binary` as a boolean e.g. `binary=True`

    Note:
        - we do not handle any time features
        - every particle in the phase space is flagged as being a new history.
    """

    def __init__(self, PhaseSpaceInstance: PhaseSpace, output_location: (str, Path), output_name: str,
                 binary: bool = False):
        self._binary = binary
        super().__init__(PhaseSpaceInstance, output_location, output_name)


    def _define_required_columns(self):
        self._required_columns = ['x', 'y', 'z', 'Direction Cosine X', 'Direction Cosine Y',
                                  'Direction Cosine Z', 'Ek', 'weight', 'particle id']

    def _export_data(self):
        """
        Convert Phase space into format appropriate for topas.

        You can read more about the required format
        `Here <https://topas.readthedocs.io/en/latest/parameters/scoring/phasespace.html>`_
        """

        if 'windows' in platform.system().lower():
            warnings.warn('to generate a valid file, please use a unix-based system')
        if self._binary:
            warnings.warn('binary exports are platform dependent, please use ascii files for cross-platform compatibility')
        print('generating topas data file')

        self._generate_topas_header_file()
        # make sure output is in correct format
        if not Path(self._output_name).suffix == '.phsp':
            _output_name = str(self._output_name) + '.phsp'
        else:
            _output_name = self._output_name
        WritefilePath = Path(self._output_location) / _output_name

        first_particle_flag = np.ones(self._PS.ps_data['x [mm]'].shape[0])
        third_direction_flag = np.int8(self._PS.ps_data['Direction Cosine Z'] < 0)

        # Nb: topas requires units of cm
        Data = [self._PS.ps_data['x [mm]'].to_numpy() * 0.1, self._PS.ps_data['y [mm]'].to_numpy() * 0.1,
                self._PS.ps_data['z [mm]'].to_numpy() * 0.1,
                self._PS.ps_data['Direction Cosine X'].to_numpy(), self._PS.ps_data['Direction Cosine Y'].to_numpy(),
                self._PS.ps_data['Ek [MeV]'].to_numpy(), self._PS.ps_data['weight'].to_numpy(),
                self._PS.ps_data['particle type [pdg_code]'].to_numpy(),
                third_direction_flag, first_particle_flag]

        # write the data to file
        if self._binary:
            dtype_strings = ['f4', 'f4', 'f4', 'f4', 'f4', 'f4', 'f4', 'i4', 'b1', 'b1']
            Data = [d.astype(dt) for d, dt in zip(Data, dtype_strings)]
            Data = recfunctions.merge_arrays(Data)
            with open(WritefilePath, 'wb') as f:
                Data.tofile(f)
        else:
            Data = np.transpose(Data)
            FormatSpec = ['%11.5f', '%11.5f', '%11.5f', '%11.5f', '%11.5f', '%11.5f', '%11.5f', '%2d', '%2d', '%2d']
            np.savetxt(WritefilePath, Data, fmt=FormatSpec, delimiter='      ')
            print('success')

    def _generate_topas_header_file(self):
        """
        Generate the header file required for a topas phase space source.
        This is only intended to be used from within the class (private method)
        """

        if Path(self._output_name).suffix == '.phsp':
            _output_name = Path(self._output_name).stem
        else:
            _output_name = self._output_name
        _output_name = str(_output_name) + '.header'
        WritefilePath = self._output_location / _output_name

        ParticlesInPhaseSpace = str(len(self._PS.ps_data['x [mm]'] ))
        TopasHeader = []

        format_name = 'Binary' if self._binary else 'ASCII'
        TopasHeader.append('TOPAS {:s} Phase Space\n'.format(format_name))
        TopasHeader.append('Number of Original Histories: ' + ParticlesInPhaseSpace)
        TopasHeader.append('Number of Original Histories that Reached Phase Space: ' + ParticlesInPhaseSpace)
        TopasHeader.append('Number of Scored Particles: ' + ParticlesInPhaseSpace)

        if self._binary:
            TopasHeader.append('Number of Bytes per Particle: 34' + '\n')
            TopasHeader.append('Byte order of each record is as follows:')
            TopasHeader.append('f4: Position X [cm]')
            TopasHeader.append('f4: Position Y [cm]')
            TopasHeader.append('f4: Position Z [cm]')
            TopasHeader.append('f4: Direction Cosine X')
            TopasHeader.append('f4: Direction Cosine Y')
            TopasHeader.append('f4: Energy [MeV]')
            TopasHeader.append('f4: Weight')
            TopasHeader.append('i4: Particle Type (in PDG Format)')
            TopasHeader.append('b1: Flag to tell if Third Direction Cosine is Negative (1 means true)')
            TopasHeader.append('b1: Flag to tell if this is the First Scored Particle from this History (1 means true)\n')
        else:
            TopasHeader.append('')
            TopasHeader.append('Columns of data are as follows:')
            TopasHeader.append(' 1: Position X [cm]')
            TopasHeader.append(' 2: Position Y [cm]')
            TopasHeader.append(' 3: Position Z [cm]')
            TopasHeader.append(' 4: Direction Cosine X')
            TopasHeader.append(' 5: Direction Cosine Y')
            TopasHeader.append(' 6: Energy [MeV]')
            TopasHeader.append(' 7: Weight')
            TopasHeader.append(' 8: Particle Type (in PDG Format)')
            TopasHeader.append(' 9: Flag to tell if Third Direction Cosine is Negative (1 means true)')
            TopasHeader.append('10: Flag to tell if this is the First Scored Particle from this History (1 means true)\n')

        particle_number_string = []
        minimum_Ek_string = []
        maximum_Ek_string = []
        for particle in self._PS._unique_particles:
            if particle_cfg.particle_properties[particle]['name'] == 'electrons':
                electron_PS = self._PS('electrons')
                electron_PS.fill.kinetic_E()
                particle_number_string.append('Number of e-: ' + str(len(electron_PS.ps_data['x [mm]'])) )
                minimum_Ek_string.append('Minimum Kinetic Energy of e-: ' + str(min(electron_PS.ps_data['Ek [MeV]'])) + ' MeV')
                maximum_Ek_string.append('Maximum Kinetic Energy of e-: ' + str(max(electron_PS.ps_data['Ek [MeV]'])) + ' MeV')
            elif particle_cfg.particle_properties[particle]['name'] == 'positrons':
                positron_PS = self._PS('positrons')
                positron_PS.fill.kinetic_E()
                particle_number_string.append('Number of e+: ' + str(len(positron_PS.ps_data['x [mm]'])))
                minimum_Ek_string.append('Minimum Kinetic Energy of e+: ' + str(min(positron_PS.ps_data['Ek [MeV]'])) + ' MeV')
                maximum_Ek_string.append('Maximum Kinetic Energy of e+: ' + str(max(positron_PS.ps_data['Ek [MeV]'])) + ' MeV')
            elif particle_cfg.particle_properties[particle]['name'] == 'gammas':
                gamma_PS = self._PS('gammas')
                gamma_PS.fill.kinetic_E()
                particle_number_string.append('Number of gamma: ' + str(len(gamma_PS.ps_data['x [mm]'])))
                minimum_Ek_string.append('Minimum Kinetic Energy of gamma: ' + str(min(gamma_PS.ps_data['Ek [MeV]'])) + ' MeV')
                maximum_Ek_string.append('Maximum Kinetic Energy of gamma: ' + str(max(gamma_PS.ps_data['Ek [MeV]'])) + ' MeV')
            elif particle_cfg.particle_properties[particle]['name'] == 'neutrons':
                neutrons_PS = self._PS('neutrons')
                neutrons_PS.fill.kinetic_E()
                particle_number_string.append('Number of neutrons: ' + str(len(neutrons_PS.ps_data['x [mm]'])))
                minimum_Ek_string.append(
                    'Minimum Kinetic Energy of neutron: ' + str(min(neutrons_PS.ps_data['Ek [MeV]'])) + ' MeV')
                maximum_Ek_string.append(
                    'Maximum Kinetic Energy of neutron: ' + str(max(neutrons_PS.ps_data['Ek [MeV]'])) + ' MeV')
            elif particle_cfg.particle_properties[particle]['name'] == 'protons':
                protons_PS = self._PS('protons')
                protons_PS.fill.kinetic_E()
                particle_number_string.append('Number of protons: ' + str(len(protons_PS.ps_data['x [mm]'])))
                minimum_Ek_string.append(
                    'Minimum Kinetic Energy of proton: ' + str(min(protons_PS.ps_data['Ek [MeV]'])) + ' MeV')
                maximum_Ek_string.append(
                    'Maximum Kinetic Energy of proton: ' + str(max(protons_PS.ps_data['Ek [MeV]'])) + ' MeV')
            else:
                raise NotImplementedError(f'cannot currently export particle type {particle_cfg.particle_properties[particle]["name"]}.'
                                          f'\nneed to update header writer')
        for line in particle_number_string:
            TopasHeader.append(line)
        TopasHeader.append('')
        for line in minimum_Ek_string:
            TopasHeader.append(line)
        TopasHeader.append('')
        for line in maximum_Ek_string:
            TopasHeader.append(line)

        # open file:
        f = open(WritefilePath, 'w')
        # Write file line by line:
        for Line in TopasHeader:
            f.write(Line)
            f.write('\n')
        f.close()

    def _set_expected_units(self):
        self._expected_units = ParticlePhaseSpaceUnits()('mm_MeV')


class CSV_Exporter(_DataExportersBase):
    '''
    Export data to a csv format, in particular one which can be read by p2sat read text
    # weight          x (um)          y (um)          z (um)          px (MeV/c)      py (MeV/c)      pz (MeV/c)      t (fs)
    '''

    def _define_required_columns(self):
        self._required_columns = ['x', 'y', 'z', 'px', 'py', 'pz', 'time', 'weight']

    def _export_data(self):

        data_string = ['weight', 'x [um]', 'y [um]', 'z [um]', 'px [MeV/c]', 'py [MeV/c]', 'pz [MeV/c]', 'time [fs]']
        self._PS.ps_data[data_string].to_csv(self._output_location / self._output_name, index=False, header=False)

    def _set_expected_units(self):
        self._expected_units = ParticlePhaseSpaceUnits()('p2_sat_UHI')