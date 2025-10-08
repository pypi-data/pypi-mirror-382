"""
This file is auto-generated from direct-sun-hours:0.5.18.
It is unlikely that you should be editing this file directly.
Try to edit the original recipe itself and regenerate the code.

Contact the recipe maintainers with additional questions.
    mostapha: mostapha@ladybug.tools
    ladybug-tools: info@ladybug.tools

This file is licensed under "PolyForm Shield License 1.0.0".
See https://polyformproject.org/wp-content/uploads/2020/06/PolyForm-Shield-1.0.0.txt for more information.
"""


import luigi
import pathlib
from queenbee_local import QueenbeeTask
from queenbee_local import load_input_param as qb_load_input_param
from . import _queenbee_status_lock_


_default_inputs = {   'bsdfs': None,
    'grid_name': None,
    'octree_file': None,
    'params_folder': '__params',
    'sensor_count': None,
    'sensor_grid': None,
    'simulation_folder': '.',
    'sun_modifiers': None,
    'timestep': 1}


class DirectIrradianceCalculation(QueenbeeTask):
    """Calculate daylight contribution for a grid of sensors from a series of modifiers
    using rcontrib command."""

    # DAG Input parameters
    _input_params = luigi.DictParameter()
    _status_lock = _queenbee_status_lock_

    # Task inputs
    @property
    def fixed_radiance_parameters(self):
        return '-aa 0.0 -I -faa -ab 0 -dc 1.0 -dt 0.0 -dj 0.0 -dr 0'

    @property
    def conversion(self):
        return '0.265 0.670 0.065'

    @property
    def sensor_count(self):
        return self._input_params['sensor_count']

    @property
    def grid_name(self):
        return self._input_params['grid_name']

    calculate_values = luigi.Parameter(default='value')

    header = luigi.Parameter(default='keep')

    order_by = luigi.Parameter(default='sensor')

    output_format = luigi.Parameter(default='a')

    radiance_parameters = luigi.Parameter(default='')

    @property
    def modifiers(self):
        value = pathlib.Path(self._input_params['sun_modifiers'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def sensor_grid(self):
        value = pathlib.Path(self._input_params['sensor_grid'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def scene_file(self):
        value = pathlib.Path(self._input_params['octree_file'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def bsdf_folder(self):
        try:
            pathlib.Path(self._input_params['bsdfs'])
        except TypeError:
            # optional artifact
            return None
        value = pathlib.Path(self._input_params['bsdfs'])
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
        return pathlib.Path(__file__).parent.joinpath('scripts', 'direct_irradiance_calculation.py').resolve()

    @property
    def is_script(self):
        return False

    def command(self):
        return 'honeybee-radiance dc scontrib scene.oct grid.pts suns.mod --{calculate_values} --sensor-count {sensor_count} --rad-params "{radiance_parameters}" --rad-params-locked "{fixed_radiance_parameters}" --conversion "{conversion}" --output-format {output_format} --output results.ill --order-by-{order_by} --{header}-header'.format(calculate_values=self.calculate_values, order_by=self.order_by, conversion=self.conversion, sensor_count=self.sensor_count, output_format=self.output_format, radiance_parameters=self.radiance_parameters, header=self.header, fixed_radiance_parameters=self.fixed_radiance_parameters)

    def output(self):
        return {
            'result_file': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, '{grid_name}.ill'.format(grid_name=self.grid_name)).resolve().as_posix()
            )
        }

    @property
    def input_artifacts(self):
        return [
            {'name': 'modifiers', 'to': 'suns.mod', 'from': self.modifiers, 'optional': False},
            {'name': 'sensor_grid', 'to': 'grid.pts', 'from': self.sensor_grid, 'optional': False},
            {'name': 'scene_file', 'to': 'scene.oct', 'from': self.scene_file, 'optional': False},
            {'name': 'bsdf_folder', 'to': 'model/bsdf', 'from': self.bsdf_folder, 'optional': True}]

    @property
    def output_artifacts(self):
        return [
            {
                'name': 'result-file', 'from': 'results.ill',
                'to': pathlib.Path(self.execution_folder, '{grid_name}.ill'.format(grid_name=self.grid_name)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            }]

    @property
    def input_parameters(self):
        return {
            'fixed_radiance_parameters': self.fixed_radiance_parameters,
            'conversion': self.conversion,
            'sensor_count': self.sensor_count,
            'grid_name': self.grid_name,
            'calculate_values': self.calculate_values,
            'header': self.header,
            'order_by': self.order_by,
            'output_format': self.output_format,
            'radiance_parameters': self.radiance_parameters}

    @property
    def task_image(self):
        return 'docker.io/ladybugtools/honeybee-radiance:1.65.32'

    @property
    def image_workdir(self):
        return '/home/ladybugbot/run'


class ConvertToSunHours(QueenbeeTask):
    """Convert a Radiance matrix to a new matrix with 0-1 values."""

    # DAG Input parameters
    _input_params = luigi.DictParameter()
    _status_lock = _queenbee_status_lock_

    # Task inputs
    @property
    def grid_name(self):
        return self._input_params['grid_name']

    @property
    def minimum(self):
        return '0'

    @property
    def include_min(self):
        return 'exclude'

    include_max = luigi.Parameter(default='include')

    maximum = luigi.Parameter(default='1e+100')

    reverse = luigi.Parameter(default='comply')

    @property
    def input_mtx(self):
        value = pathlib.Path(self.input()['DirectIrradianceCalculation']['result_file'].path)
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
        return pathlib.Path(__file__).parent.joinpath('scripts', 'convert_to_sun_hours.py').resolve()

    @property
    def is_script(self):
        return False

    def command(self):
        return 'honeybee-radiance post-process convert-to-binary input.mtx --output binary.mtx --maximum {maximum} --minimum {minimum} --{reverse} --{include_min}-min --{include_max}-max'.format(reverse=self.reverse, include_max=self.include_max, include_min=self.include_min, minimum=self.minimum, maximum=self.maximum)

    def requires(self):
        return {'DirectIrradianceCalculation': DirectIrradianceCalculation(_input_params=self._input_params)}

    def output(self):
        return {
            'output_mtx': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, '{grid_name}_sun_hours.ill'.format(grid_name=self.grid_name)).resolve().as_posix()
            )
        }

    @property
    def input_artifacts(self):
        return [
            {'name': 'input_mtx', 'to': 'input.mtx', 'from': self.input_mtx, 'optional': False}]

    @property
    def output_artifacts(self):
        return [
            {
                'name': 'output-mtx', 'from': 'binary.mtx',
                'to': pathlib.Path(self.execution_folder, '{grid_name}_sun_hours.ill'.format(grid_name=self.grid_name)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            }]

    @property
    def input_parameters(self):
        return {
            'grid_name': self.grid_name,
            'minimum': self.minimum,
            'include_min': self.include_min,
            'include_max': self.include_max,
            'maximum': self.maximum,
            'reverse': self.reverse}

    @property
    def task_image(self):
        return 'docker.io/ladybugtools/honeybee-radiance:1.65.32'

    @property
    def image_workdir(self):
        return '/home/ladybugbot/run'


class CalculateCumulativeHours(QueenbeeTask):
    """Postprocess a Radiance matrix and add all the numbers in each row.

    This function is useful for translating Radiance results to outputs like radiation
    to total radiation. Input matrix must be in ASCII format. The header in the input
    file will be ignored."""

    # DAG Input parameters
    _input_params = luigi.DictParameter()
    _status_lock = _queenbee_status_lock_

    # Task inputs
    @property
    def grid_name(self):
        return self._input_params['grid_name']

    @property
    def divisor(self):
        return self._input_params['timestep']

    @property
    def input_mtx(self):
        value = pathlib.Path(self.input()['ConvertToSunHours']['output_mtx'].path)
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
        return pathlib.Path(__file__).parent.joinpath('scripts', 'calculate_cumulative_hours.py').resolve()

    @property
    def is_script(self):
        return False

    def command(self):
        return 'honeybee-radiance post-process sum-row input.mtx --divisor {divisor} --output sum.mtx'.format(divisor=self.divisor)

    def requires(self):
        return {'ConvertToSunHours': ConvertToSunHours(_input_params=self._input_params)}

    def output(self):
        return {
            'output_mtx': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, '../cumulative/{grid_name}.res'.format(grid_name=self.grid_name)).resolve().as_posix()
            )
        }

    @property
    def input_artifacts(self):
        return [
            {'name': 'input_mtx', 'to': 'input.mtx', 'from': self.input_mtx, 'optional': False}]

    @property
    def output_artifacts(self):
        return [
            {
                'name': 'output-mtx', 'from': 'sum.mtx',
                'to': pathlib.Path(self.execution_folder, '../cumulative/{grid_name}.res'.format(grid_name=self.grid_name)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            }]

    @property
    def input_parameters(self):
        return {
            'grid_name': self.grid_name,
            'divisor': self.divisor}

    @property
    def task_image(self):
        return 'docker.io/ladybugtools/honeybee-radiance:1.65.32'

    @property
    def image_workdir(self):
        return '/home/ladybugbot/run'


class CopySunHours(QueenbeeTask):
    """Copy a file or folder to a destination."""

    # DAG Input parameters
    _input_params = luigi.DictParameter()
    _status_lock = _queenbee_status_lock_

    # Task inputs
    @property
    def grid_name(self):
        return self._input_params['grid_name']

    @property
    def src(self):
        value = pathlib.Path(self.input()['ConvertToSunHours']['output_mtx'].path)
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
        return pathlib.Path(__file__).parent.joinpath('scripts', 'copy_sun_hours.py').resolve()

    @property
    def is_script(self):
        return False

    def command(self):
        return 'echo copying input path...'

    def requires(self):
        return {'ConvertToSunHours': ConvertToSunHours(_input_params=self._input_params)}

    def output(self):
        return {
            'dst': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, '../direct_sun_hours/{grid_name}.ill'.format(grid_name=self.grid_name)).resolve().as_posix()
            )
        }

    @property
    def input_artifacts(self):
        return [
            {'name': 'src', 'to': 'input_path', 'from': self.src, 'optional': False}]

    @property
    def output_artifacts(self):
        return [
            {
                'name': 'dst', 'from': 'input_path',
                'to': pathlib.Path(self.execution_folder, '../direct_sun_hours/{grid_name}.ill'.format(grid_name=self.grid_name)).resolve().as_posix(),
                'optional': False,
                'type': 'folder'
            }]

    @property
    def input_parameters(self):
        return {
            'grid_name': self.grid_name}

    @property
    def task_image(self):
        return 'docker.io/python:3.7-slim'

    @property
    def image_workdir(self):
        return '/home/ladybugbot/run'


class _DirectSunHoursCalculation_6aed763bOrchestrator(luigi.WrapperTask):
    """Runs all the tasks in this module."""
    # user input for this module
    _input_params = luigi.DictParameter()

    @property
    def input_values(self):
        params = dict(_default_inputs)
        params.update(dict(self._input_params))
        return params

    def requires(self):
        yield [CalculateCumulativeHours(_input_params=self.input_values), CopySunHours(_input_params=self.input_values)]
