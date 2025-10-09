from dataclasses import dataclass
from pollination_dsl.function import Inputs, Outputs, Function, command


@dataclass
class ModelToBaseline(Function):
    """Convert a Model to be conformant with ASHRAE 90.1 appendix G.

    This includes running all functions to adjust the geometry, constructions,
    lighting, HVAC, SHW, and remove any clearly-defined energy conservation
    measures like daylight controls. Note that all schedules are essentially
    unchanged, meaning that additional post-processing of setpoints may be
    necessary to account for energy conservation strategies like expanded
    comfort ranges, ceiling fans, and personal thermal comfort devices. It may
    also be necessary to adjust electric equipment loads in cases where such
    equipment qualifies as an energy conservation strategy or hot water loads in
    cases where low-flow fixtures are implemented.

    Note that not all versions of ASHRAE 90.1 use this exact definition of a
    baseline model but version 2016 and onward conform to it. It is essentially
    an adjusted version of the 90.1-2004 methods.
    """

    model = Inputs.file(
        description='Honeybee model.', path='model.hbjson',
        extensions=['hbjson', 'json', 'hbpkl', 'pkl']
    )

    climate_zone = Inputs.str(
        description='Text indicating the ASHRAE climate zone. This can be a single '
        'integer (in which case it is interpreted as A) or it can include the '
        'A, B, or C qualifier (eg. 3C).',
        spec={
            'type': 'string',
            'enum': [
                '0', '1', '2', '3', '4', '5', '6', '7', '8',
                '0A', '1A', '2A', '3A', '4A', '5A', '6A',
                '0B', '1B', '2B', '3B', '4B', '5B', '6B',
                '3C', '4C', '5C'
            ]
        }
    )

    building_type = Inputs.str(
        description='Text for the building type that the Model represents. This is used '
        'to determine the baseline window-to-wall ratio and HVAC system. If the type is '
        'not recognized or is "Unknown", it will be assumed that the building is generic'
        ' NonResidential. The following have specified systems per the standard: '
        'Residential, NonResidential, MidriseApartment, HighriseApartment, LargeOffice, '
        'MediumOffice, SmallOffice, Retail, StripMall, PrimarySchool, SecondarySchool, '
        'SmallHotel, LargeHotel, Hospital, Outpatient, Warehouse, SuperMarket, '
        'FullServiceRestaurant, QuickServiceRestaurant, Laboratory',
        default='NonResidential'
    )

    floor_area = Inputs.float(
        description='A number for the floor area of the building that the model '
        'is a part of in m2. Setting this value is useful when the input model '
        'represents a portion of the full building so it is necessary to explicitly '
        'specify the full floor area to ensure the correct baseline HVAC system is '
        'selected. If unspecified or 0, the model floor area will be used.', default=0
    )

    story_count = Inputs.int(
        description='An integer for the number of stories of the building that the '
        'model is a part of. Setting this value is useful when the input model '
        'represents a portion of the full building so it is necessary to explicitly '
        'specify the total story count to ensure the correct baseline HVAC system is '
        'selected. If unspecified or 0, the model stories will be used.', default=0,
        spec={'type': 'integer', 'minimum': 0}
    )

    lighting_method = Inputs.str(
        description='A switch to note whether the building-type should be used to '
        'assign the baseline lighting power density, which will use the same value '
        'for all Rooms in the model, or a space-by-space method should be used. '
        'To use the space-by-space method, the model should either be built '
        'with the programs that ship with Ladybug Tools in honeybee-energy-standards '
        'or the baseline_watts_per_area should be correctly '
        'assigned for all Rooms.', default='space',
        spec={'type': 'string', 'enum': ['space', 'building']}
    )

    @command
    def create_baseline(self):
        return 'honeybee-energy baseline create model.hbjson {{self.climate_zone}} ' \
            '--building-type "{{self.building_type}}" ' \
            '--story-count {{self.story_count}} --floor-area {{self.floor_area}} ' \
            '--lighting-by-{{self.lighting_method}} ' \
            '--output-file baseline_model.hbjson'

    baseline_model = Outputs.file(
        description='Model JSON with its properties edited to conform to ASHRAE '
        '90.1 appendix G.', path='baseline_model.hbjson'
    )


@dataclass
class AppendixGSummary(Function):
    """Get a JSON with a summary of ASHRAE-90.1 Appendix G performance.

    This includes Appendix G performance for versions 2016, 2019, and 2022.
    """

    proposed_result = Inputs.file(
        description=' The path of the SQL result file that has been generated from '
        'an energy simulation of a proposed building.',
        path='proposed_result.sql', extensions=['sql', 'db', 'sqlite']
    )

    baseline_result_folder = Inputs.folder(
        description='The path of a directory with several SQL result files generated '
        'from an energy simulation of a baseline building (eg. for several simulations '
        'of different orientations). The baseline performance will be computed as '
        'the average across all SQL files in the directory.', path='baseline_results'
    )

    climate_zone = Inputs.str(
        description='Text indicating the ASHRAE climate zone. This can be a single '
        'integer (in which case it is interpreted as A) or it can include the '
        'A, B, or C qualifier (eg. 3C).',
        spec={
            'type': 'string',
            'enum': [
                '0', '1', '2', '3', '4', '5', '6', '7', '8',
                '0A', '1A', '2A', '3A', '4A', '5A', '6A',
                '0B', '1B', '2B', '3B', '4B', '5B', '6B',
                '3C', '4C', '5C'
            ]
        }
    )

    building_type = Inputs.str(
        description='Text for the building type that the Model represents. This is used '
        'to determine the baseline window-to-wall ratio and HVAC system. If the type is '
        'not recognized or is "Unknown", it will be assumed that the building is generic'
        ' NonResidential. The following have specified systems per the standard: '
        'Residential, NonResidential, MidriseApartment, HighriseApartment, LargeOffice, '
        'MediumOffice, SmallOffice, Retail, StripMall, PrimarySchool, SecondarySchool, '
        'SmallHotel, LargeHotel, Hospital, Outpatient, Warehouse, SuperMarket, '
        'FullServiceRestaurant, QuickServiceRestaurant, Laboratory',
        default='NonResidential'
    )

    energy_costs = Inputs.str(
        description='A string of energy cost parameters to customize the cost '
        'assumptions used to calculate the Performance Cost Index (PCI). Note that '
        'not all of the energy sources need to be specified for this input to be valid. '
        'For example, if the input model contains no district heating or cooling, '
        'something like the following would be acceptable: --electricity-cost 0.24 '
        '--natural-gas-cost 0.08',
        default='--electricity-cost 0.15 --natural-gas-cost 0.06 '
        '--district-cooling-cost 0.04 --district-heating-cost 0.08'
    )

    @command
    def compute_appendix_g_summary(self):
        return 'honeybee-energy baseline appendix-g-summary proposed_result.sql ' \
            'baseline_results {{self.climate_zone}} ' \
            '--building-type "{{self.building_type}}" ' \
            '{{inputs.energy_costs}} --output-file output.json'

    summary_json = Outputs.file(
        description='A JSON object with the following keys - proposed_eui, '
        'proposed_energy, proposed_cost, baseline_eui, baseline_energy, baseline_cost, '
        'pci_t_2016, pci_t_2019, pci_t_2022, pci, pci_improvement_2016, '
        'pci_improvement_2019, pci_improvement_2022. All energy and energy intensity '
        'values are in kWh or kWh/m2. All PCI values are fractional and all '
        '"improvement" values are in percent (from 0 to 100).', path='output.json'
    )


@dataclass
class LeedV4Summary(Function):
    """Get a JSON with a summary of LEED V4 (and 4.1) performance.

    This includes ASHRAE 90.1-2016 Appendix G performance for both cost and
    carbon (GHG) emissions as well as the estimated number of LEED "Optimize
    Energy Performance" points.
    """

    proposed_result = Inputs.file(
        description=' The path of the SQL result file that has been generated from '
        'an energy simulation of a proposed building.',
        path='proposed_result.sql', extensions=['sql', 'db', 'sqlite']
    )

    baseline_result_folder = Inputs.folder(
        description='The path of a directory with several SQL result files generated '
        'from an energy simulation of a baseline building (eg. for several simulations '
        'of different orientations). The baseline performance will be computed as '
        'the average across all SQL files in the directory.', path='baseline_results'
    )

    climate_zone = Inputs.str(
        description='Text indicating the ASHRAE climate zone. This can be a single '
        'integer (in which case it is interpreted as A) or it can include the '
        'A, B, or C qualifier (eg. 3C).',
        spec={
            'type': 'string',
            'enum': [
                '0', '1', '2', '3', '4', '5', '6', '7', '8',
                '0A', '1A', '2A', '3A', '4A', '5A', '6A',
                '0B', '1B', '2B', '3B', '4B', '5B', '6B',
                '3C', '4C', '5C'
            ]
        }
    )

    building_type = Inputs.str(
        description='Text for the building type that the Model represents. This is used '
        'to determine the baseline window-to-wall ratio and HVAC system. If the type is '
        'not recognized or is "Unknown", it will be assumed that the building is generic'
        ' NonResidential. The following have specified systems per the standard: '
        'Residential, NonResidential, MidriseApartment, HighriseApartment, LargeOffice, '
        'MediumOffice, SmallOffice, Retail, StripMall, PrimarySchool, SecondarySchool, '
        'SmallHotel, LargeHotel, Hospital, Outpatient, Warehouse, SuperMarket, '
        'FullServiceRestaurant, QuickServiceRestaurant, Laboratory',
        default='NonResidential'
    )

    energy_costs = Inputs.str(
        description='A string of energy cost parameters to customize the cost '
        'assumptions used to calculate the Performance Cost Index (PCI). Note that '
        'not all of the energy sources need to be specified for this input to be valid. '
        'For example, if the input model contains no district heating or cooling, '
        'something like the following would be acceptable: --electricity-cost 0.24 '
        '--natural-gas-cost 0.08',
        default='--electricity-cost 0.15 --natural-gas-cost 0.06 '
        '--district-cooling-cost 0.04 --district-heating-cost 0.08'
    )

    electricity_emissions = Inputs.float(
        description='A number for the electric grid carbon emissions'
        'in kg CO2 per MWh. For locations in the USA, this can be obtained '
        'from he honeybee_energy.result.emissions future_electricity_emissions '
        'method. For locations outside of the USA where specific data is unavailable, '
        'the following rules of thumb may be used as a guide. (Default: 400).\n'
        '800 kg/MWh - for an inefficient coal or oil-dominated grid\n'
        '400 kg/MWh - for the US (energy mixed) grid around 2020\n'
        '100-200 kg/MWh - for grids with majority renewable/nuclear composition\n'
        '0-100 kg/MWh - for grids with renewables and storage', default=400
    )

    @command
    def compute_leed_v4_summary(self):
        return 'honeybee-energy baseline leed-v4-summary proposed_result.sql ' \
            'baseline_results {{self.climate_zone}} ' \
            '--building-type "{{self.building_type}}" {{inputs.energy_costs}} ' \
            '--electricity-emissions {{self.electricity_emissions}} ' \
            '--output-file output.json'

    summary_json = Outputs.file(
        description='A JSON object with the following keys - proposed_eui, '
        'proposed_cost, proposed_carbon, baseline_eui, baseline_cost, baseline_carbon, '
        'pci_target, pci, pci_improvement, carbon_target, pci_carbon '
        'carbon_improvement, leed_points. All energy and energy intensity '
        'values are in kWh or kWh/m2. All carbon emission values are in kg CO2. '
        'All PCI values are fractional and all "improvement" values are in percent '
        '(from 0 to 100). LEED points are reported from 0 to (16, 18, 20) '
        'depending on the input building_type.', path='output.json'
    )
