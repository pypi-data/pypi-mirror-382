"""
This file is auto-generated from adaptive-comfort-map:0.9.2.
It is unlikely that you should be editing this file directly.
Try to edit the original recipe itself and regenerate the code.

Contact the recipe maintainers with additional questions.
    chris: chris@ladybug.tools
    ladybug-tools: info@ladybug.tools

This file is licensed under "PolyForm Shield License 1.0.0".
See https://polyformproject.org/wp-content/uploads/2020/06/PolyForm-Shield-1.0.0.txt for more information.
"""


import luigi
import pathlib
from queenbee_local import QueenbeeTask
from queenbee_local import load_input_param as qb_load_input_param
from . import _queenbee_status_lock_


_default_inputs = {   'air_speed': None,
    'comfort_parameters': '--standard ASHRAE-55',
    'contributions': None,
    'direct_irradiance': None,
    'enclosure_info': None,
    'epw': None,
    'grid_name': None,
    'indirect_irradiance': None,
    'modifiers': None,
    'occ_schedules': None,
    'params_folder': '__params',
    'prevailing': None,
    'ref_irradiance': None,
    'result_sql': None,
    'run_period': '',
    'simulation_folder': '.',
    'solarcal_parameters': '--posture seated --sharp 135 --absorptivity 0.7 '
                           '--emissivity 0.95',
    'sun_up_hours': None,
    'trans_schedules': None,
    'transmittance_contribs': None,
    'view_factors': None}


class CreateAirSpeedJson(QueenbeeTask):
    """Get a JSON of air speeds that can be used as input for the mtx functions."""

    # DAG Input parameters
    _input_params = luigi.DictParameter()
    _status_lock = _queenbee_status_lock_

    # Task inputs
    @property
    def multiply_by(self):
        return '0.5'

    @property
    def run_period(self):
        return self._input_params['run_period']

    @property
    def name(self):
        return self._input_params['grid_name']

    @property
    def epw(self):
        value = pathlib.Path(self._input_params['epw'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def enclosure_info(self):
        value = pathlib.Path(self._input_params['enclosure_info'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def indoor_air_speed(self):
        try:
            pathlib.Path(self._input_params['air_speed'])
        except TypeError:
            # optional artifact
            return None
        value = pathlib.Path(self._input_params['air_speed'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def execution_folder(self):
        return pathlib.Path(self._input_params['simulation_folder']).as_posix()

    @property
    def initiation_folder(self):
        return pathlib.Path(self._input_params['simulation_folder']).as_posix()

    @property
    def params_folder(self):
        return pathlib.Path(self.execution_folder, self._input_params['params_folder']).resolve().as_posix()

    @property
    def __script__(self):
        return pathlib.Path(__file__).parent.joinpath('scripts', 'create_air_speed_json.py').resolve()

    @property
    def is_script(self):
        return False

    def command(self):
        return 'ladybug-comfort epw air-speed-json weather.epw enclosure_info.json --multiply-by {multiply_by} --indoor-air-speed in_speed.txt --outdoor-air-speed out_speed.txt --run-period "{run_period}" --output-file air_speed.json'.format(multiply_by=self.multiply_by, run_period=self.run_period)

    def output(self):
        return {
            'air_speeds': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, 'conditions/air_speed/{name}.json'.format(name=self.name)).resolve().as_posix()
            )
        }

    @property
    def input_artifacts(self):
        return [
            {'name': 'epw', 'to': 'weather.epw', 'from': self.epw, 'optional': False},
            {'name': 'enclosure_info', 'to': 'enclosure_info.json', 'from': self.enclosure_info, 'optional': False},
            {'name': 'indoor_air_speed', 'to': 'in_speed.txt', 'from': self.indoor_air_speed, 'optional': True}]

    @property
    def output_artifacts(self):
        return [
            {
                'name': 'air-speeds', 'from': 'air_speed.json',
                'to': pathlib.Path(self.execution_folder, 'conditions/air_speed/{name}.json'.format(name=self.name)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            }]

    @property
    def input_parameters(self):
        return {
            'multiply_by': self.multiply_by,
            'run_period': self.run_period,
            'name': self.name}

    @property
    def task_image(self):
        return 'docker.io/ladybugtools/ladybug-comfort:0.18.42'

    @property
    def image_workdir(self):
        return '/home/ladybugbot/run'


class CreateAirTemperatureMap(QueenbeeTask):
    """Get CSV files with maps of air temperatures or humidity from EnergyPlus results."""

    # DAG Input parameters
    _input_params = luigi.DictParameter()
    _status_lock = _queenbee_status_lock_

    # Task inputs
    @property
    def run_period(self):
        return self._input_params['run_period']

    @property
    def metric(self):
        return 'air-temperature'

    @property
    def name(self):
        return self._input_params['grid_name']

    @property
    def output_format(self):
        return 'binary'

    @property
    def result_sql(self):
        try:
            pathlib.Path(self._input_params['result_sql'])
        except TypeError:
            # optional artifact
            return None
        value = pathlib.Path(self._input_params['result_sql'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def enclosure_info(self):
        value = pathlib.Path(self._input_params['enclosure_info'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def epw(self):
        value = pathlib.Path(self._input_params['epw'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def execution_folder(self):
        return pathlib.Path(self._input_params['simulation_folder']).as_posix()

    @property
    def initiation_folder(self):
        return pathlib.Path(self._input_params['simulation_folder']).as_posix()

    @property
    def params_folder(self):
        return pathlib.Path(self.execution_folder, self._input_params['params_folder']).resolve().as_posix()

    @property
    def __script__(self):
        return pathlib.Path(__file__).parent.joinpath('scripts', 'create_air_temperature_map.py').resolve()

    @property
    def is_script(self):
        return False

    def command(self):
        return 'ladybug-comfort map air result.sql enclosure_info.json weather.epw --run-period "{run_period}" --{metric} --{output_format} --output-file air.csv'.format(output_format=self.output_format, metric=self.metric, run_period=self.run_period)

    def output(self):
        return {
            'air_map': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, 'conditions/air_temperature/{name}.csv'.format(name=self.name)).resolve().as_posix()
            )
        }

    @property
    def input_artifacts(self):
        return [
            {'name': 'result_sql', 'to': 'result.sql', 'from': self.result_sql, 'optional': True},
            {'name': 'enclosure_info', 'to': 'enclosure_info.json', 'from': self.enclosure_info, 'optional': False},
            {'name': 'epw', 'to': 'weather.epw', 'from': self.epw, 'optional': False}]

    @property
    def output_artifacts(self):
        return [
            {
                'name': 'air-map', 'from': 'air.csv',
                'to': pathlib.Path(self.execution_folder, 'conditions/air_temperature/{name}.csv'.format(name=self.name)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            }]

    @property
    def input_parameters(self):
        return {
            'run_period': self.run_period,
            'metric': self.metric,
            'name': self.name,
            'output_format': self.output_format}

    @property
    def task_image(self):
        return 'docker.io/ladybugtools/ladybug-comfort:0.18.42'

    @property
    def image_workdir(self):
        return '/home/ladybugbot/run'


class CreateLongwaveMrtMap(QueenbeeTask):
    """Get CSV files with maps of longwave MRT from Radiance and EnergyPlus results."""

    # DAG Input parameters
    _input_params = luigi.DictParameter()
    _status_lock = _queenbee_status_lock_

    # Task inputs
    @property
    def run_period(self):
        return self._input_params['run_period']

    @property
    def name(self):
        return self._input_params['grid_name']

    @property
    def output_format(self):
        return 'binary'

    @property
    def result_sql(self):
        try:
            pathlib.Path(self._input_params['result_sql'])
        except TypeError:
            # optional artifact
            return None
        value = pathlib.Path(self._input_params['result_sql'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def view_factors(self):
        value = pathlib.Path(self._input_params['view_factors'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def modifiers(self):
        value = pathlib.Path(self._input_params['modifiers'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def enclosure_info(self):
        value = pathlib.Path(self._input_params['enclosure_info'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def epw(self):
        value = pathlib.Path(self._input_params['epw'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def execution_folder(self):
        return pathlib.Path(self._input_params['simulation_folder']).as_posix()

    @property
    def initiation_folder(self):
        return pathlib.Path(self._input_params['simulation_folder']).as_posix()

    @property
    def params_folder(self):
        return pathlib.Path(self.execution_folder, self._input_params['params_folder']).resolve().as_posix()

    @property
    def __script__(self):
        return pathlib.Path(__file__).parent.joinpath('scripts', 'create_longwave_mrt_map.py').resolve()

    @property
    def is_script(self):
        return False

    def command(self):
        return 'ladybug-comfort map longwave-mrt result.sql view_factors.csv view_factors.mod enclosure_info.json weather.epw --run-period "{run_period}" --{output_format} --output-file longwave.csv'.format(output_format=self.output_format, run_period=self.run_period)

    def output(self):
        return {
            'longwave_mrt_map': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, 'conditions/longwave_mrt/{name}.csv'.format(name=self.name)).resolve().as_posix()
            )
        }

    @property
    def input_artifacts(self):
        return [
            {'name': 'result_sql', 'to': 'result.sql', 'from': self.result_sql, 'optional': True},
            {'name': 'view_factors', 'to': 'view_factors.csv', 'from': self.view_factors, 'optional': False},
            {'name': 'modifiers', 'to': 'view_factors.mod', 'from': self.modifiers, 'optional': False},
            {'name': 'enclosure_info', 'to': 'enclosure_info.json', 'from': self.enclosure_info, 'optional': False},
            {'name': 'epw', 'to': 'weather.epw', 'from': self.epw, 'optional': False}]

    @property
    def output_artifacts(self):
        return [
            {
                'name': 'longwave-mrt-map', 'from': 'longwave.csv',
                'to': pathlib.Path(self.execution_folder, 'conditions/longwave_mrt/{name}.csv'.format(name=self.name)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            }]

    @property
    def input_parameters(self):
        return {
            'run_period': self.run_period,
            'name': self.name,
            'output_format': self.output_format}

    @property
    def task_image(self):
        return 'docker.io/ladybugtools/ladybug-comfort:0.18.42'

    @property
    def image_workdir(self):
        return '/home/ladybugbot/run'


class CreateShortwaveMrtMap(QueenbeeTask):
    """Get CSV files with maps of shortwave MRT Deltas from Radiance results."""

    # DAG Input parameters
    _input_params = luigi.DictParameter()
    _status_lock = _queenbee_status_lock_

    # Task inputs
    @property
    def solarcal_par(self):
        return self._input_params['solarcal_parameters']

    @property
    def run_period(self):
        return self._input_params['run_period']

    @property
    def name(self):
        return self._input_params['grid_name']

    @property
    def output_format(self):
        return 'binary'

    indirect_is_total = luigi.Parameter(default='is-indirect')

    @property
    def epw(self):
        value = pathlib.Path(self._input_params['epw'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def indirect_irradiance(self):
        value = pathlib.Path(self._input_params['indirect_irradiance'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def direct_irradiance(self):
        value = pathlib.Path(self._input_params['direct_irradiance'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def ref_irradiance(self):
        value = pathlib.Path(self._input_params['ref_irradiance'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def sun_up_hours(self):
        value = pathlib.Path(self._input_params['sun_up_hours'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def contributions(self):
        try:
            pathlib.Path(self._input_params['contributions'])
        except TypeError:
            # optional artifact
            return None
        value = pathlib.Path(self._input_params['contributions'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def transmittance_contribs(self):
        try:
            pathlib.Path(self._input_params['transmittance_contribs'])
        except TypeError:
            # optional artifact
            return None
        value = pathlib.Path(self._input_params['transmittance_contribs'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def trans_schedules(self):
        try:
            pathlib.Path(self._input_params['trans_schedules'])
        except TypeError:
            # optional artifact
            return None
        value = pathlib.Path(self._input_params['trans_schedules'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def execution_folder(self):
        return pathlib.Path(self._input_params['simulation_folder']).as_posix()

    @property
    def initiation_folder(self):
        return pathlib.Path(self._input_params['simulation_folder']).as_posix()

    @property
    def params_folder(self):
        return pathlib.Path(self.execution_folder, self._input_params['params_folder']).resolve().as_posix()

    @property
    def __script__(self):
        return pathlib.Path(__file__).parent.joinpath('scripts', 'create_shortwave_mrt_map.py').resolve()

    @property
    def is_script(self):
        return False

    def command(self):
        return 'ladybug-comfort map shortwave-mrt weather.epw indirect.ill direct.ill ref.ill sun-up-hours.txt --contributions dynamic --transmittance-contribs dyn_shade --trans-schedule-json trans_schedules.json --solarcal-par "{solarcal_par}" --run-period "{run_period}" --{indirect_is_total} --{output_format} --output-file shortwave.csv'.format(solarcal_par=self.solarcal_par, output_format=self.output_format, indirect_is_total=self.indirect_is_total, run_period=self.run_period)

    def output(self):
        return {
            'shortwave_mrt_map': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, 'conditions/shortwave_mrt/{name}.csv'.format(name=self.name)).resolve().as_posix()
            )
        }

    @property
    def input_artifacts(self):
        return [
            {'name': 'epw', 'to': 'weather.epw', 'from': self.epw, 'optional': False},
            {'name': 'indirect_irradiance', 'to': 'indirect.ill', 'from': self.indirect_irradiance, 'optional': False},
            {'name': 'direct_irradiance', 'to': 'direct.ill', 'from': self.direct_irradiance, 'optional': False},
            {'name': 'ref_irradiance', 'to': 'ref.ill', 'from': self.ref_irradiance, 'optional': False},
            {'name': 'sun_up_hours', 'to': 'sun-up-hours.txt', 'from': self.sun_up_hours, 'optional': False},
            {'name': 'contributions', 'to': 'dynamic', 'from': self.contributions, 'optional': True},
            {'name': 'transmittance_contribs', 'to': 'dyn_shade', 'from': self.transmittance_contribs, 'optional': True},
            {'name': 'trans_schedules', 'to': 'trans_schedules.json', 'from': self.trans_schedules, 'optional': True}]

    @property
    def output_artifacts(self):
        return [
            {
                'name': 'shortwave-mrt-map', 'from': 'shortwave.csv',
                'to': pathlib.Path(self.execution_folder, 'conditions/shortwave_mrt/{name}.csv'.format(name=self.name)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            }]

    @property
    def input_parameters(self):
        return {
            'solarcal_par': self.solarcal_par,
            'run_period': self.run_period,
            'name': self.name,
            'output_format': self.output_format,
            'indirect_is_total': self.indirect_is_total}

    @property
    def task_image(self):
        return 'docker.io/ladybugtools/ladybug-comfort:0.18.42'

    @property
    def image_workdir(self):
        return '/home/ladybugbot/run'


class ProcessAdaptiveMatrix(QueenbeeTask):
    """Get CSV files with matrices of Adaptive comfort from matrices of Adaptive inputs."""

    # DAG Input parameters
    _input_params = luigi.DictParameter()
    _status_lock = _queenbee_status_lock_

    # Task inputs
    @property
    def comfort_par(self):
        return self._input_params['comfort_parameters']

    @property
    def output_format(self):
        return 'binary'

    @property
    def name(self):
        return self._input_params['grid_name']

    @property
    def air_temperature_mtx(self):
        value = pathlib.Path(self.input()['CreateAirTemperatureMap']['air_map'].path)
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def rad_temperature_mtx(self):
        value = pathlib.Path(self.input()['CreateLongwaveMrtMap']['longwave_mrt_map'].path)
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def rad_delta_mtx(self):
        value = pathlib.Path(self.input()['CreateShortwaveMrtMap']['shortwave_mrt_map'].path)
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def air_speed_json(self):
        value = pathlib.Path(self.input()['CreateAirSpeedJson']['air_speeds'].path)
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def prevailing_temperature(self):
        value = pathlib.Path(self._input_params['prevailing'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def execution_folder(self):
        return pathlib.Path(self._input_params['simulation_folder']).as_posix()

    @property
    def initiation_folder(self):
        return pathlib.Path(self._input_params['simulation_folder']).as_posix()

    @property
    def params_folder(self):
        return pathlib.Path(self.execution_folder, self._input_params['params_folder']).resolve().as_posix()

    @property
    def __script__(self):
        return pathlib.Path(__file__).parent.joinpath('scripts', 'process_adaptive_matrix.py').resolve()

    @property
    def is_script(self):
        return False

    def command(self):
        return 'ladybug-comfort mtx adaptive air_temperature.csv prevailing.csv --rad-temperature-mtx rad_temperature.csv --rad-delta-mtx rad_delta.csv --air-speed-json air_speed.json --comfort-par "{comfort_par}" --{output_format} --folder output'.format(comfort_par=self.comfort_par, output_format=self.output_format)

    def requires(self):
        return {'CreateLongwaveMrtMap': CreateLongwaveMrtMap(_input_params=self._input_params), 'CreateShortwaveMrtMap': CreateShortwaveMrtMap(_input_params=self._input_params), 'CreateAirTemperatureMap': CreateAirTemperatureMap(_input_params=self._input_params), 'CreateAirSpeedJson': CreateAirSpeedJson(_input_params=self._input_params)}

    def output(self):
        return {
            'temperature_map': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, 'results/temperature/{name}.csv'.format(name=self.name)).resolve().as_posix()
            ),
            
            'condition_map': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, 'results/condition/{name}.csv'.format(name=self.name)).resolve().as_posix()
            ),
            
            'deg_from_neutral_map': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, 'results/condition_intensity/{name}.csv'.format(name=self.name)).resolve().as_posix()
            )
        }

    @property
    def input_artifacts(self):
        return [
            {'name': 'air_temperature_mtx', 'to': 'air_temperature.csv', 'from': self.air_temperature_mtx, 'optional': False},
            {'name': 'rad_temperature_mtx', 'to': 'rad_temperature.csv', 'from': self.rad_temperature_mtx, 'optional': False},
            {'name': 'rad_delta_mtx', 'to': 'rad_delta.csv', 'from': self.rad_delta_mtx, 'optional': False},
            {'name': 'air_speed_json', 'to': 'air_speed.json', 'from': self.air_speed_json, 'optional': False},
            {'name': 'prevailing_temperature', 'to': 'prevailing.csv', 'from': self.prevailing_temperature, 'optional': False}]

    @property
    def output_artifacts(self):
        return [
            {
                'name': 'temperature-map', 'from': 'output/temperature.csv',
                'to': pathlib.Path(self.execution_folder, 'results/temperature/{name}.csv'.format(name=self.name)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            },
                
            {
                'name': 'condition-map', 'from': 'output/condition.csv',
                'to': pathlib.Path(self.execution_folder, 'results/condition/{name}.csv'.format(name=self.name)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            },
                
            {
                'name': 'deg-from-neutral-map', 'from': 'output/condition_intensity.csv',
                'to': pathlib.Path(self.execution_folder, 'results/condition_intensity/{name}.csv'.format(name=self.name)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            }]

    @property
    def input_parameters(self):
        return {
            'comfort_par': self.comfort_par,
            'output_format': self.output_format,
            'name': self.name}

    @property
    def task_image(self):
        return 'docker.io/ladybugtools/ladybug-comfort:0.18.42'

    @property
    def image_workdir(self):
        return '/home/ladybugbot/run'


class ComputeTcp(QueenbeeTask):
    """Compute Thermal Comfort Petcent (TCP) from thermal condition CSV map."""

    # DAG Input parameters
    _input_params = luigi.DictParameter()
    _status_lock = _queenbee_status_lock_

    # Task inputs
    @property
    def name(self):
        return self._input_params['grid_name']

    @property
    def condition_csv(self):
        value = pathlib.Path(self.input()['ProcessAdaptiveMatrix']['condition_map'].path)
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def enclosure_info(self):
        value = pathlib.Path(self._input_params['enclosure_info'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def occ_schedule_json(self):
        value = pathlib.Path(self._input_params['occ_schedules'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def execution_folder(self):
        return pathlib.Path(self._input_params['simulation_folder']).as_posix()

    @property
    def initiation_folder(self):
        return pathlib.Path(self._input_params['simulation_folder']).as_posix()

    @property
    def params_folder(self):
        return pathlib.Path(self.execution_folder, self._input_params['params_folder']).resolve().as_posix()

    @property
    def __script__(self):
        return pathlib.Path(__file__).parent.joinpath('scripts', 'compute_tcp.py').resolve()

    @property
    def is_script(self):
        return False

    def command(self):
        return 'ladybug-comfort map tcp condition.csv enclosure_info.json --schedule schedule.txt --occ-schedule-json occ_schedule.json --folder output'

    def requires(self):
        return {'ProcessAdaptiveMatrix': ProcessAdaptiveMatrix(_input_params=self._input_params)}

    def output(self):
        return {
            'tcp': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, 'metrics/TCP/{name}.csv'.format(name=self.name)).resolve().as_posix()
            ),
            
            'hsp': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, 'metrics/HSP/{name}.csv'.format(name=self.name)).resolve().as_posix()
            ),
            
            'csp': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, 'metrics/CSP/{name}.csv'.format(name=self.name)).resolve().as_posix()
            )
        }

    @property
    def input_artifacts(self):
        return [
            {'name': 'condition_csv', 'to': 'condition.csv', 'from': self.condition_csv, 'optional': False},
            {'name': 'enclosure_info', 'to': 'enclosure_info.json', 'from': self.enclosure_info, 'optional': False},
            {'name': 'occ_schedule_json', 'to': 'occ_schedule.json', 'from': self.occ_schedule_json, 'optional': False}]

    @property
    def output_artifacts(self):
        return [
            {
                'name': 'tcp', 'from': 'output/tcp.csv',
                'to': pathlib.Path(self.execution_folder, 'metrics/TCP/{name}.csv'.format(name=self.name)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            },
                
            {
                'name': 'hsp', 'from': 'output/hsp.csv',
                'to': pathlib.Path(self.execution_folder, 'metrics/HSP/{name}.csv'.format(name=self.name)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            },
                
            {
                'name': 'csp', 'from': 'output/csp.csv',
                'to': pathlib.Path(self.execution_folder, 'metrics/CSP/{name}.csv'.format(name=self.name)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            }]

    @property
    def input_parameters(self):
        return {
            'name': self.name}

    @property
    def task_image(self):
        return 'docker.io/ladybugtools/ladybug-comfort:0.18.42'

    @property
    def image_workdir(self):
        return '/home/ladybugbot/run'


class _ComfortMappingEntryPoint_6b5ce744Orchestrator(luigi.WrapperTask):
    """Runs all the tasks in this module."""
    # user input for this module
    _input_params = luigi.DictParameter()

    @property
    def input_values(self):
        params = dict(_default_inputs)
        params.update(dict(self._input_params))
        return params

    def requires(self):
        yield [ComputeTcp(_input_params=self.input_values)]
