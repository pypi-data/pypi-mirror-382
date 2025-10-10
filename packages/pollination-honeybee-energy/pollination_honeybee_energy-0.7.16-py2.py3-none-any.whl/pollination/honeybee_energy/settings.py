from dataclasses import dataclass
from pollination_dsl.function import Inputs, Outputs, Function, command


@dataclass
class SimParDefault(Function):
    """Get a SimulationParameter JSON with default outputs for energy use only."""

    ddy = Inputs.file(
        description='A DDY file with design days to be included in the '
        'SimulationParameter', path='input.ddy', extensions=['ddy'], optional=True
    )

    reporting_frequency = Inputs.str(
        description='Text for the frequency at which the outputs are reported. '
        '(Default: Hourly). Choose from the following: Annual, Monthly, Daily, '
        'Hourly, Timestep', default='Hourly',
        spec={
            'type': 'string',
            'enum': ['Annual', 'Monthly', 'Daily', 'Hourly', 'Timestep']
        }
    )

    run_period = Inputs.str(
        description='An AnalysisPeriod string or an IDF RunPeriod string to set the '
        'start and end dates of the simulation (eg. "6/21 to 9/21 between 0 and 23 @1").'
        ' If None, the simulation will be annual.', default=''
    )

    north = Inputs.int(
        description='A number from -360 to 360 for the counterclockwise difference '
        'between North and the positive Y-axis in degrees. 90 is west; 270 is east',
        default=0, spec={'type': 'integer', 'maximum': 360, 'minimum': -360}
    )

    filter_des_days = Inputs.str(
        description='A switch for whether the ddy-file should be filtered to only '
        'include 99.6 and 0.4 design days', default='filter-des-days',
        spec={'type': 'string', 'enum': ['filter-des-days', 'all-des-days']}
    )

    efficiency_standard = Inputs.str(
        description='Text to set the efficiency standard, which will '
        'automatically set the efficiencies of all HVAC equipment when provided. '
        'Note that providing a standard here will cause the OpenStudio translation '
        'process to perform an additional sizing calculation with EnergyPlus, '
        'which is needed since the default efficiencies of equipment vary depending on '
        'their size. THIS WILL SIGNIFICANTLY INCREASE TRANSLATION TIME TO OPENSTUDIO. '
        'However, it is often worthwhile when the goal is to match the '
        'HVAC specification with a particular standard.Choose from the following: '
        'DOE_Ref_Pre_1980, DOE_Ref_1980_2004, ASHRAE_2004, ASHRAE_2007, ASHRAE_2010, '
        'ASHRAE_2013, ASHRAE_2016, ASHRAE_2019', default=''
    )

    climate_zone = Inputs.str(
        description='Text indicating the ASHRAE climate zone to be used with the '
        'efficiency_standard. When unspecified, the climate zone will be '
        'inferred from the design days. This input can be a single integer (in which '
        'case it is interpreted as A) or it can include the A, B, or C qualifier '
        '(eg. 3C).', default=''
    )

    building_type = Inputs.str(
        description='Text for the building type to be used in the efficiency_standard. '
        'If the type is not recognized or is None, it will be assumed that '
        'the building is a generic NonResidential.', default=''
    )

    @command
    def create_sim_param(self):
        return 'honeybee-energy settings default-sim-par input.ddy ' \
            '--reporting-frequency {{self.reporting_frequency}} ' \
            '--run-period "{{self.run_period}}" --north {{self.north}} ' \
            '--efficiency-standard "{{self.efficiency_standard}}" ' \
            '--climate-zone "{{self.climate_zone}}" ' \
            '--building-type "{{self.building_type}}" ' \
            '--{{self.filter_des_days}} --output-file sim_par.json'

    sim_par_json = Outputs.file(
        description='SimulationParameter JSON with default outputs for energy use',
        path='sim_par.json'
    )


@dataclass
class SimParLoadBalance(SimParDefault):
    """Get a SimulationParameter JSON with all outputs for constructing load balances."""

    load_type = Inputs.str(
        description='Text to indicate the type of load. Choose from (Total, Sensible, '
        'Latent, All)', default='Total',
        spec={'type': 'string', 'enum': ['Total', 'Sensible', 'Latent', 'All']}
    )

    @command
    def create_sim_param(self):
        return 'honeybee-energy settings load-balance-sim-par input.ddy --load-type ' \
            '{{self.load_type}} --run-period "{{self.run_period}}" --north ' \
            '{{self.north}} --{{self.filter_des_days}} --output-file sim_par.json'


@dataclass
class SimParComfort(SimParDefault):
    """Get a SimulationParameter JSON with all outputs for thermal comfort mapping."""

    @command
    def create_sim_param(self):
        return 'honeybee-energy settings comfort-sim-par input.ddy ' \
            '--run-period "{{self.run_period}}" --north {{self.north}} ' \
            '--{{self.filter_des_days}} --output-file sim_par.json'


@dataclass
class SimParSizing(Function):
    """Get a SimulationParameter JSON with outputs for peak loads and HVAC sizing."""

    ddy = Inputs.file(
        description='A DDY file with design days to be included in the '
        'SimulationParameter', path='input.ddy', extensions=['ddy'], optional=True
    )

    load_type = Inputs.str(
        description='Text to indicate the type of load. Choose from (Total, Sensible, '
        'Latent, All)', default='Total',
        spec={'type': 'string', 'enum': ['Total', 'Sensible', 'Latent', 'All']}
    )

    north = Inputs.int(
        description='A number from -360 to 360 for the counterclockwise difference '
        'between North and the positive Y-axis in degrees. 90 is west; 270 is east',
        default=0, spec={'type': 'integer', 'maximum': 360, 'minimum': -360}
    )

    filter_des_days = Inputs.str(
        description='A switch for whether the ddy-file should be filtered to only '
        'include 99.6 and 0.4 design days', default='filter-des-days',
        spec={'type': 'string', 'enum': ['filter-des-days', 'all-des-days']}
    )

    @command
    def create_sim_param(self):
        return 'honeybee-energy settings sizing-sim-par input.ddy ' \
            '--load-type {{self.load_type}} --north {{self.north}} ' \
            '--{{self.filter_des_days}} --output-file sim_par.json'

    sim_par_json = Outputs.file(
        description='SimulationParameter JSON with outputs for peak loads and '
        'HVAC sizing.', path='sim_par.json'
    )


@dataclass
class BaselineOrientationSimPars(Function):
    """Get SimulationParameters with different north angles for a baseline building sim.
    """

    ddy = Inputs.file(
        description='A DDY file with design days to be included in the '
        'SimulationParameter', path='input.ddy', extensions=['ddy'], optional=True
    )

    reporting_frequency = Inputs.str(
        description='Text for the frequency at which the outputs are reported. '
        '(Default: Hourly). Choose from the following: Annual, Monthly, Daily, '
        'Hourly, Timestep', default='Hourly',
        spec={
            'type': 'string',
            'enum': ['Annual', 'Monthly', 'Daily', 'Hourly', 'Timestep']
        }
    )

    run_period = Inputs.str(
        description='An AnalysisPeriod string or an IDF RunPeriod string to set the '
        'start and end dates of the simulation (eg. "6/21 to 9/21 between 0 and 23 @1").'
        ' If None, the simulation will be annual.', default=''
    )

    north = Inputs.int(
        description='A number from -360 to 360 for the counterclockwise difference '
        'between North and the positive Y-axis in degrees. 90 is west; 270 is east',
        default=0, spec={'type': 'integer', 'maximum': 360, 'minimum': -360}
    )

    filter_des_days = Inputs.str(
        description='A switch for whether the ddy-file should be filtered to only '
        'include 99.6 and 0.4 design days', default='filter-des-days',
        spec={'type': 'string', 'enum': ['filter-des-days', 'all-des-days']}
    )

    efficiency_standard = Inputs.str(
        description='Text to set the efficiency standard, which will '
        'automatically set the efficiencies of all HVAC equipment when provided. '
        'Note that providing a standard here will cause the OpenStudio translation '
        'process to perform an additional sizing calculation with EnergyPlus, '
        'which is needed since the default efficiencies of equipment vary depending on '
        'their size. THIS WILL SIGNIFICANTLY INCREASE TRANSLATION TIME TO OPENSTUDIO. '
        'However, it is often worthwhile when the goal is to match the '
        'HVAC specification with a particular standard.Choose from the following: '
        'DOE_Ref_Pre_1980, DOE_Ref_1980_2004, ASHRAE_2004, ASHRAE_2007, ASHRAE_2010, '
        'ASHRAE_2013, ASHRAE_2016, ASHRAE_2019', default=''
    )

    climate_zone = Inputs.str(
        description='Text indicating the ASHRAE climate zone to be used with the '
        'efficiency_standard. When unspecified, the climate zone will be '
        'inferred from the design days. This input can be a single integer (in which '
        'case it is interpreted as A) or it can include the A, B, or C qualifier '
        '(eg. 3C).', default=''
    )

    building_type = Inputs.str(
        description='Text for the building type to be used in the efficiency_standard. '
        'If the type is not recognized or is None, it will be assumed that '
        'the building is a generic NonResidential.', default=''
    )

    @command
    def baseline_orientation_sim_pars(self):
        return 'honeybee-energy settings orientation-sim-pars input.ddy ' \
            '0 90 180 270 --reporting-frequency {{self.reporting_frequency}} ' \
            '--run-period "{{self.run_period}}" --start-north {{self.north}} ' \
            '--efficiency-standard "{{self.efficiency_standard}}" ' \
            '--climate-zone "{{self.climate_zone}}" ' \
            '--building-type "{{self.building_type}}" ' \
            '--{{self.filter_des_days}} --folder output ' \
            '--log-file output/sim_par_info.json'

    sim_par_list = Outputs.dict(
        description='A JSON array that includes information about generated simulation '
        'parameters.', path='output/sim_par_info.json'
    )

    output_folder = Outputs.folder(
        description='Output folder with the simulation parameters.', path='output'
    )


@dataclass
class DynamicOutputs(Function):
    """Get an IDF file that requests transmittance outputs for dynamic windows."""

    model = Inputs.file(
        description='Honeybee model in JSON format.', path='model.json'
    )

    base_idf = Inputs.file(
        description='An optional base IDF file to which the outputs '
        'for dynamic windows will be appended.',
        path='base.idf', extensions=['idf'], optional=True
    )

    @command
    def create_sim_param(self):
        return 'honeybee-energy settings dynamic-window-outputs model.json ' \
            '--base-idf base.idf --output-file base.idf'

    dynamic_out_idf = Outputs.file(
        description='An IDF string that requests transmittance outputs for dynamic '
        'windows. This should be used within comfort mapping workflows to request '
        'transmittance outputs for dynamic windows. Note that the output is just an '
        'IDF text file that should be incorporated in the energy simulation by '
        'means of additional IDF.', path='base.idf'
    )
