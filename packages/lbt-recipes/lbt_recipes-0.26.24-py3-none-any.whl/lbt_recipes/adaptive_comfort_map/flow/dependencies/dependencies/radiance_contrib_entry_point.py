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


_default_inputs = {   'grid_name': None,
    'group_name': None,
    'octree_file_diff': None,
    'octree_file_spec': None,
    'octree_file_with_suns': None,
    'params_folder': '__params',
    'radiance_parameters': '-ab 2 -ad 5000 -lw 2e-05',
    'ref_sensor_grid': None,
    'result_sql': None,
    'sensor_count': None,
    'sensor_grid': None,
    'simulation_folder': '.',
    'sky_dome': None,
    'sky_matrix': None,
    'sky_matrix_direct': None,
    'sun_modifiers': None,
    'sun_up_hours': None}


class DirectSkyGroup(QueenbeeTask):
    """Calculate daylight coefficient for a grid of sensors from a sky matrix."""

    # DAG Input parameters
    _input_params = luigi.DictParameter()
    _status_lock = _queenbee_status_lock_

    # Task inputs
    @property
    def grid(self):
        return self._input_params['grid_name']

    @property
    def group(self):
        return self._input_params['group_name']

    @property
    def radiance_parameters(self):
        return self._input_params['radiance_parameters']

    @property
    def fixed_radiance_parameters(self):
        return '-aa 0.0 -I -ab 1 -c 1 -faf'

    @property
    def sensor_count(self):
        return self._input_params['sensor_count']

    @property
    def conversion(self):
        return '0.265 0.670 0.065'

    header = luigi.Parameter(default='keep')

    order_by = luigi.Parameter(default='sensor')

    output_format = luigi.Parameter(default='f')

    @property
    def sky_matrix(self):
        value = pathlib.Path(self._input_params['sky_matrix_direct'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def sky_dome(self):
        value = pathlib.Path(self._input_params['sky_dome'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def sensor_grid(self):
        value = pathlib.Path(self._input_params['sensor_grid'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def scene_file(self):
        value = pathlib.Path(self._input_params['octree_file_spec'])
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
        return pathlib.Path(__file__).parent.joinpath('scripts', 'direct_sky_group.py').resolve()

    @property
    def is_script(self):
        return False

    def command(self):
        return 'honeybee-radiance dc scoeff scene.oct grid.pts sky.dome sky.mtx --sensor-count {sensor_count} --output results.ill --rad-params "{radiance_parameters}" --rad-params-locked "{fixed_radiance_parameters}" --conversion "{conversion}" --output-format {output_format} --order-by-{order_by} --{header}-header'.format(radiance_parameters=self.radiance_parameters, sensor_count=self.sensor_count, output_format=self.output_format, conversion=self.conversion, header=self.header, fixed_radiance_parameters=self.fixed_radiance_parameters, order_by=self.order_by)

    def output(self):
        return {
            'result_file': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, 'dynamic/initial/{group}/direct_sky/{grid}.ill'.format(grid=self.grid, group=self.group)).resolve().as_posix()
            )
        }

    @property
    def input_artifacts(self):
        return [
            {'name': 'sky_matrix', 'to': 'sky.mtx', 'from': self.sky_matrix, 'optional': False},
            {'name': 'sky_dome', 'to': 'sky.dome', 'from': self.sky_dome, 'optional': False},
            {'name': 'sensor_grid', 'to': 'grid.pts', 'from': self.sensor_grid, 'optional': False},
            {'name': 'scene_file', 'to': 'scene.oct', 'from': self.scene_file, 'optional': False}]

    @property
    def output_artifacts(self):
        return [
            {
                'name': 'result-file', 'from': 'results.ill',
                'to': pathlib.Path(self.execution_folder, 'dynamic/initial/{group}/direct_sky/{grid}.ill'.format(grid=self.grid, group=self.group)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            }]

    @property
    def input_parameters(self):
        return {
            'grid': self.grid,
            'group': self.group,
            'radiance_parameters': self.radiance_parameters,
            'fixed_radiance_parameters': self.fixed_radiance_parameters,
            'sensor_count': self.sensor_count,
            'conversion': self.conversion,
            'header': self.header,
            'order_by': self.order_by,
            'output_format': self.output_format}

    @property
    def task_image(self):
        return 'docker.io/ladybugtools/honeybee-radiance:1.66.103'

    @property
    def image_workdir(self):
        return '/home/ladybugbot/run'


class DirectSunGroup(QueenbeeTask):
    """Calculate daylight contribution for a grid of sensors from a series of modifiers
    using rcontrib command."""

    # DAG Input parameters
    _input_params = luigi.DictParameter()
    _status_lock = _queenbee_status_lock_

    # Task inputs
    @property
    def grid(self):
        return self._input_params['grid_name']

    @property
    def group(self):
        return self._input_params['group_name']

    @property
    def radiance_parameters(self):
        return self._input_params['radiance_parameters']

    @property
    def fixed_radiance_parameters(self):
        return '-aa 0.0 -I -ab 0 -dc 1.0 -dt 0.0 -dj 0.0 -dr 0'

    @property
    def sensor_count(self):
        return self._input_params['sensor_count']

    @property
    def conversion(self):
        return '0.265 0.670 0.065'

    @property
    def output_format(self):
        return 'f'

    @property
    def header(self):
        return 'keep'

    calculate_values = luigi.Parameter(default='value')

    order_by = luigi.Parameter(default='sensor')

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
        value = pathlib.Path(self._input_params['octree_file_with_suns'])
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
        return pathlib.Path(__file__).parent.joinpath('scripts', 'direct_sun_group.py').resolve()

    @property
    def is_script(self):
        return False

    def command(self):
        return 'honeybee-radiance dc scontrib scene.oct grid.pts suns.mod --{calculate_values} --sensor-count {sensor_count} --rad-params "{radiance_parameters}" --rad-params-locked "{fixed_radiance_parameters}" --conversion "{conversion}" --output-format {output_format} --output results.ill --order-by-{order_by} --{header}-header'.format(radiance_parameters=self.radiance_parameters, calculate_values=self.calculate_values, sensor_count=self.sensor_count, output_format=self.output_format, conversion=self.conversion, header=self.header, fixed_radiance_parameters=self.fixed_radiance_parameters, order_by=self.order_by)

    def output(self):
        return {
            'result_file': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, 'dynamic/initial/{group}/direct_spec/{grid}.ill'.format(grid=self.grid, group=self.group)).resolve().as_posix()
            )
        }

    @property
    def input_artifacts(self):
        return [
            {'name': 'modifiers', 'to': 'suns.mod', 'from': self.modifiers, 'optional': False},
            {'name': 'sensor_grid', 'to': 'grid.pts', 'from': self.sensor_grid, 'optional': False},
            {'name': 'scene_file', 'to': 'scene.oct', 'from': self.scene_file, 'optional': False}]

    @property
    def output_artifacts(self):
        return [
            {
                'name': 'result-file', 'from': 'results.ill',
                'to': pathlib.Path(self.execution_folder, 'dynamic/initial/{group}/direct_spec/{grid}.ill'.format(grid=self.grid, group=self.group)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            }]

    @property
    def input_parameters(self):
        return {
            'grid': self.grid,
            'group': self.group,
            'radiance_parameters': self.radiance_parameters,
            'fixed_radiance_parameters': self.fixed_radiance_parameters,
            'sensor_count': self.sensor_count,
            'conversion': self.conversion,
            'output_format': self.output_format,
            'header': self.header,
            'calculate_values': self.calculate_values,
            'order_by': self.order_by}

    @property
    def task_image(self):
        return 'docker.io/ladybugtools/honeybee-radiance:1.66.103'

    @property
    def image_workdir(self):
        return '/home/ladybugbot/run'


class GroundReflectedSkyDiffGroup(QueenbeeTask):
    """Calculate daylight coefficient for a grid of sensors from a sky matrix."""

    # DAG Input parameters
    _input_params = luigi.DictParameter()
    _status_lock = _queenbee_status_lock_

    # Task inputs
    @property
    def grid(self):
        return self._input_params['grid_name']

    @property
    def group(self):
        return self._input_params['group_name']

    @property
    def radiance_parameters(self):
        return self._input_params['radiance_parameters']

    @property
    def fixed_radiance_parameters(self):
        return '-aa 0.0 -I -c 1'

    @property
    def sensor_count(self):
        return self._input_params['sensor_count']

    @property
    def conversion(self):
        return '0.265 0.670 0.065'

    @property
    def output_format(self):
        return 'f'

    @property
    def header(self):
        return 'keep'

    order_by = luigi.Parameter(default='sensor')

    @property
    def sky_matrix(self):
        value = pathlib.Path(self._input_params['sky_matrix'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def sky_dome(self):
        value = pathlib.Path(self._input_params['sky_dome'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def sensor_grid(self):
        value = pathlib.Path(self._input_params['ref_sensor_grid'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def scene_file(self):
        value = pathlib.Path(self._input_params['octree_file_diff'])
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
        return pathlib.Path(__file__).parent.joinpath('scripts', 'ground_reflected_sky_diff_group.py').resolve()

    @property
    def is_script(self):
        return False

    def command(self):
        return 'honeybee-radiance dc scoeff scene.oct grid.pts sky.dome sky.mtx --sensor-count {sensor_count} --output results.ill --rad-params "{radiance_parameters}" --rad-params-locked "{fixed_radiance_parameters}" --conversion "{conversion}" --output-format {output_format} --order-by-{order_by} --{header}-header'.format(radiance_parameters=self.radiance_parameters, sensor_count=self.sensor_count, output_format=self.output_format, conversion=self.conversion, header=self.header, fixed_radiance_parameters=self.fixed_radiance_parameters, order_by=self.order_by)

    def output(self):
        return {
            'result_file': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, 'dynamic/initial/{group}/reflected_diff/{grid}.ill'.format(grid=self.grid, group=self.group)).resolve().as_posix()
            )
        }

    @property
    def input_artifacts(self):
        return [
            {'name': 'sky_matrix', 'to': 'sky.mtx', 'from': self.sky_matrix, 'optional': False},
            {'name': 'sky_dome', 'to': 'sky.dome', 'from': self.sky_dome, 'optional': False},
            {'name': 'sensor_grid', 'to': 'grid.pts', 'from': self.sensor_grid, 'optional': False},
            {'name': 'scene_file', 'to': 'scene.oct', 'from': self.scene_file, 'optional': False}]

    @property
    def output_artifacts(self):
        return [
            {
                'name': 'result-file', 'from': 'results.ill',
                'to': pathlib.Path(self.execution_folder, 'dynamic/initial/{group}/reflected_diff/{grid}.ill'.format(grid=self.grid, group=self.group)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            }]

    @property
    def input_parameters(self):
        return {
            'grid': self.grid,
            'group': self.group,
            'radiance_parameters': self.radiance_parameters,
            'fixed_radiance_parameters': self.fixed_radiance_parameters,
            'sensor_count': self.sensor_count,
            'conversion': self.conversion,
            'output_format': self.output_format,
            'header': self.header,
            'order_by': self.order_by}

    @property
    def task_image(self):
        return 'docker.io/ladybugtools/honeybee-radiance:1.66.103'

    @property
    def image_workdir(self):
        return '/home/ladybugbot/run'


class GroundReflectedSkySpecGroup(QueenbeeTask):
    """Calculate daylight coefficient for a grid of sensors from a sky matrix."""

    # DAG Input parameters
    _input_params = luigi.DictParameter()
    _status_lock = _queenbee_status_lock_

    # Task inputs
    @property
    def grid(self):
        return self._input_params['grid_name']

    @property
    def group(self):
        return self._input_params['group_name']

    @property
    def radiance_parameters(self):
        return self._input_params['radiance_parameters']

    @property
    def fixed_radiance_parameters(self):
        return '-aa 0.0 -I -c 1'

    @property
    def sensor_count(self):
        return self._input_params['sensor_count']

    @property
    def conversion(self):
        return '0.265 0.670 0.065'

    @property
    def output_format(self):
        return 'f'

    @property
    def header(self):
        return 'keep'

    order_by = luigi.Parameter(default='sensor')

    @property
    def sky_matrix(self):
        value = pathlib.Path(self._input_params['sky_matrix'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def sky_dome(self):
        value = pathlib.Path(self._input_params['sky_dome'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def sensor_grid(self):
        value = pathlib.Path(self._input_params['ref_sensor_grid'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def scene_file(self):
        value = pathlib.Path(self._input_params['octree_file_spec'])
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
        return pathlib.Path(__file__).parent.joinpath('scripts', 'ground_reflected_sky_spec_group.py').resolve()

    @property
    def is_script(self):
        return False

    def command(self):
        return 'honeybee-radiance dc scoeff scene.oct grid.pts sky.dome sky.mtx --sensor-count {sensor_count} --output results.ill --rad-params "{radiance_parameters}" --rad-params-locked "{fixed_radiance_parameters}" --conversion "{conversion}" --output-format {output_format} --order-by-{order_by} --{header}-header'.format(radiance_parameters=self.radiance_parameters, sensor_count=self.sensor_count, output_format=self.output_format, conversion=self.conversion, header=self.header, fixed_radiance_parameters=self.fixed_radiance_parameters, order_by=self.order_by)

    def output(self):
        return {
            'result_file': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, 'dynamic/initial/{group}/reflected_spec/{grid}.ill'.format(grid=self.grid, group=self.group)).resolve().as_posix()
            )
        }

    @property
    def input_artifacts(self):
        return [
            {'name': 'sky_matrix', 'to': 'sky.mtx', 'from': self.sky_matrix, 'optional': False},
            {'name': 'sky_dome', 'to': 'sky.dome', 'from': self.sky_dome, 'optional': False},
            {'name': 'sensor_grid', 'to': 'grid.pts', 'from': self.sensor_grid, 'optional': False},
            {'name': 'scene_file', 'to': 'scene.oct', 'from': self.scene_file, 'optional': False}]

    @property
    def output_artifacts(self):
        return [
            {
                'name': 'result-file', 'from': 'results.ill',
                'to': pathlib.Path(self.execution_folder, 'dynamic/initial/{group}/reflected_spec/{grid}.ill'.format(grid=self.grid, group=self.group)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            }]

    @property
    def input_parameters(self):
        return {
            'grid': self.grid,
            'group': self.group,
            'radiance_parameters': self.radiance_parameters,
            'fixed_radiance_parameters': self.fixed_radiance_parameters,
            'sensor_count': self.sensor_count,
            'conversion': self.conversion,
            'output_format': self.output_format,
            'header': self.header,
            'order_by': self.order_by}

    @property
    def task_image(self):
        return 'docker.io/ladybugtools/honeybee-radiance:1.66.103'

    @property
    def image_workdir(self):
        return '/home/ladybugbot/run'


class TotalSkyDiffGroup(QueenbeeTask):
    """Calculate daylight coefficient for a grid of sensors from a sky matrix."""

    # DAG Input parameters
    _input_params = luigi.DictParameter()
    _status_lock = _queenbee_status_lock_

    # Task inputs
    @property
    def grid(self):
        return self._input_params['grid_name']

    @property
    def group(self):
        return self._input_params['group_name']

    @property
    def radiance_parameters(self):
        return self._input_params['radiance_parameters']

    @property
    def fixed_radiance_parameters(self):
        return '-aa 0.0 -I -c 1'

    @property
    def sensor_count(self):
        return self._input_params['sensor_count']

    @property
    def conversion(self):
        return '0.265 0.670 0.065'

    @property
    def output_format(self):
        return 'f'

    @property
    def header(self):
        return 'keep'

    order_by = luigi.Parameter(default='sensor')

    @property
    def sky_matrix(self):
        value = pathlib.Path(self._input_params['sky_matrix'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def sky_dome(self):
        value = pathlib.Path(self._input_params['sky_dome'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def sensor_grid(self):
        value = pathlib.Path(self._input_params['sensor_grid'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def scene_file(self):
        value = pathlib.Path(self._input_params['octree_file_diff'])
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
        return pathlib.Path(__file__).parent.joinpath('scripts', 'total_sky_diff_group.py').resolve()

    @property
    def is_script(self):
        return False

    def command(self):
        return 'honeybee-radiance dc scoeff scene.oct grid.pts sky.dome sky.mtx --sensor-count {sensor_count} --output results.ill --rad-params "{radiance_parameters}" --rad-params-locked "{fixed_radiance_parameters}" --conversion "{conversion}" --output-format {output_format} --order-by-{order_by} --{header}-header'.format(radiance_parameters=self.radiance_parameters, sensor_count=self.sensor_count, output_format=self.output_format, conversion=self.conversion, header=self.header, fixed_radiance_parameters=self.fixed_radiance_parameters, order_by=self.order_by)

    def output(self):
        return {
            'result_file': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, 'dynamic/initial/{group}/total_diff/{grid}.ill'.format(grid=self.grid, group=self.group)).resolve().as_posix()
            )
        }

    @property
    def input_artifacts(self):
        return [
            {'name': 'sky_matrix', 'to': 'sky.mtx', 'from': self.sky_matrix, 'optional': False},
            {'name': 'sky_dome', 'to': 'sky.dome', 'from': self.sky_dome, 'optional': False},
            {'name': 'sensor_grid', 'to': 'grid.pts', 'from': self.sensor_grid, 'optional': False},
            {'name': 'scene_file', 'to': 'scene.oct', 'from': self.scene_file, 'optional': False}]

    @property
    def output_artifacts(self):
        return [
            {
                'name': 'result-file', 'from': 'results.ill',
                'to': pathlib.Path(self.execution_folder, 'dynamic/initial/{group}/total_diff/{grid}.ill'.format(grid=self.grid, group=self.group)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            }]

    @property
    def input_parameters(self):
        return {
            'grid': self.grid,
            'group': self.group,
            'radiance_parameters': self.radiance_parameters,
            'fixed_radiance_parameters': self.fixed_radiance_parameters,
            'sensor_count': self.sensor_count,
            'conversion': self.conversion,
            'output_format': self.output_format,
            'header': self.header,
            'order_by': self.order_by}

    @property
    def task_image(self):
        return 'docker.io/ladybugtools/honeybee-radiance:1.66.103'

    @property
    def image_workdir(self):
        return '/home/ladybugbot/run'


class TotalSkySpecGroup(QueenbeeTask):
    """Calculate daylight coefficient for a grid of sensors from a sky matrix."""

    # DAG Input parameters
    _input_params = luigi.DictParameter()
    _status_lock = _queenbee_status_lock_

    # Task inputs
    @property
    def grid(self):
        return self._input_params['grid_name']

    @property
    def group(self):
        return self._input_params['group_name']

    @property
    def radiance_parameters(self):
        return self._input_params['radiance_parameters']

    @property
    def fixed_radiance_parameters(self):
        return '-aa 0.0 -I -c 1 -faf'

    @property
    def sensor_count(self):
        return self._input_params['sensor_count']

    @property
    def conversion(self):
        return '0.265 0.670 0.065'

    header = luigi.Parameter(default='keep')

    order_by = luigi.Parameter(default='sensor')

    output_format = luigi.Parameter(default='f')

    @property
    def sky_matrix(self):
        value = pathlib.Path(self._input_params['sky_matrix'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def sky_dome(self):
        value = pathlib.Path(self._input_params['sky_dome'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def sensor_grid(self):
        value = pathlib.Path(self._input_params['sensor_grid'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def scene_file(self):
        value = pathlib.Path(self._input_params['octree_file_spec'])
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
        return pathlib.Path(__file__).parent.joinpath('scripts', 'total_sky_spec_group.py').resolve()

    @property
    def is_script(self):
        return False

    def command(self):
        return 'honeybee-radiance dc scoeff scene.oct grid.pts sky.dome sky.mtx --sensor-count {sensor_count} --output results.ill --rad-params "{radiance_parameters}" --rad-params-locked "{fixed_radiance_parameters}" --conversion "{conversion}" --output-format {output_format} --order-by-{order_by} --{header}-header'.format(radiance_parameters=self.radiance_parameters, sensor_count=self.sensor_count, output_format=self.output_format, conversion=self.conversion, header=self.header, fixed_radiance_parameters=self.fixed_radiance_parameters, order_by=self.order_by)

    def output(self):
        return {
            'result_file': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, 'dynamic/initial/{group}/total_sky/{grid}.ill'.format(grid=self.grid, group=self.group)).resolve().as_posix()
            )
        }

    @property
    def input_artifacts(self):
        return [
            {'name': 'sky_matrix', 'to': 'sky.mtx', 'from': self.sky_matrix, 'optional': False},
            {'name': 'sky_dome', 'to': 'sky.dome', 'from': self.sky_dome, 'optional': False},
            {'name': 'sensor_grid', 'to': 'grid.pts', 'from': self.sensor_grid, 'optional': False},
            {'name': 'scene_file', 'to': 'scene.oct', 'from': self.scene_file, 'optional': False}]

    @property
    def output_artifacts(self):
        return [
            {
                'name': 'result-file', 'from': 'results.ill',
                'to': pathlib.Path(self.execution_folder, 'dynamic/initial/{group}/total_sky/{grid}.ill'.format(grid=self.grid, group=self.group)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            }]

    @property
    def input_parameters(self):
        return {
            'grid': self.grid,
            'group': self.group,
            'radiance_parameters': self.radiance_parameters,
            'fixed_radiance_parameters': self.fixed_radiance_parameters,
            'sensor_count': self.sensor_count,
            'conversion': self.conversion,
            'header': self.header,
            'order_by': self.order_by,
            'output_format': self.output_format}

    @property
    def task_image(self):
        return 'docker.io/ladybugtools/honeybee-radiance:1.66.103'

    @property
    def image_workdir(self):
        return '/home/ladybugbot/run'


class OutputMatrixMathGroup(QueenbeeTask):
    """Subtract direct sky from total sky to get indirect sky."""

    # DAG Input parameters
    _input_params = luigi.DictParameter()
    _status_lock = _queenbee_status_lock_

    # Task inputs
    @property
    def grid(self):
        return self._input_params['grid_name']

    @property
    def group(self):
        return self._input_params['group_name']

    @property
    def output_format(self):
        return 'f'

    @property
    def header(self):
        return 'keep'

    conversion = luigi.Parameter(default=' ')

    @property
    def total_sky_matrix(self):
        value = pathlib.Path(self.input()['TotalSkySpecGroup']['result_file'].path)
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def direct_sky_matrix(self):
        value = pathlib.Path(self.input()['DirectSkyGroup']['result_file'].path)
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
        return pathlib.Path(__file__).parent.joinpath('scripts', 'output_matrix_math_group.py').resolve()

    @property
    def is_script(self):
        return False

    def command(self):
        return 'honeybee-radiance mtxop operate-two sky.ill sky_dir.ill --operator "-" --{header}-header --conversion "{conversion}" --output-mtx final.ill --output-format {output_format}'.format(header=self.header, output_format=self.output_format, conversion=self.conversion)

    def requires(self):
        return {'TotalSkySpecGroup': TotalSkySpecGroup(_input_params=self._input_params), 'DirectSkyGroup': DirectSkyGroup(_input_params=self._input_params)}

    def output(self):
        return {
            'results_file': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, 'dynamic/initial/{group}/indirect_spec/{grid}.ill'.format(grid=self.grid, group=self.group)).resolve().as_posix()
            )
        }

    @property
    def input_artifacts(self):
        return [
            {'name': 'total_sky_matrix', 'to': 'sky.ill', 'from': self.total_sky_matrix, 'optional': False},
            {'name': 'direct_sky_matrix', 'to': 'sky_dir.ill', 'from': self.direct_sky_matrix, 'optional': False}]

    @property
    def output_artifacts(self):
        return [
            {
                'name': 'results-file', 'from': 'final.ill',
                'to': pathlib.Path(self.execution_folder, 'dynamic/initial/{group}/indirect_spec/{grid}.ill'.format(grid=self.grid, group=self.group)).resolve().as_posix(),
                'optional': False,
                'type': 'file'
            }]

    @property
    def input_parameters(self):
        return {
            'grid': self.grid,
            'group': self.group,
            'output_format': self.output_format,
            'header': self.header,
            'conversion': self.conversion}

    @property
    def task_image(self):
        return 'docker.io/ladybugtools/honeybee-radiance:1.66.103'

    @property
    def image_workdir(self):
        return '/home/ladybugbot/run'


class CreateIrradianceContribMap(QueenbeeTask):
    """Get .ill files with maps of irradiance contributions from dynamic windows."""

    # DAG Input parameters
    _input_params = luigi.DictParameter()
    _status_lock = _queenbee_status_lock_

    # Task inputs
    @property
    def aperture_id(self):
        return self._input_params['group_name']

    @property
    def output_format(self):
        return 'binary'

    @property
    def grid(self):
        return self._input_params['grid_name']

    @property
    def result_sql(self):
        value = pathlib.Path(self._input_params['result_sql'])
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def direct_specular(self):
        value = pathlib.Path(self.input()['DirectSunGroup']['result_file'].path)
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def indirect_specular(self):
        value = pathlib.Path(self.input()['OutputMatrixMathGroup']['results_file'].path)
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def ref_specular(self):
        value = pathlib.Path(self.input()['GroundReflectedSkySpecGroup']['result_file'].path)
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def indirect_diffuse(self):
        value = pathlib.Path(self.input()['TotalSkyDiffGroup']['result_file'].path)
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def ref_diffuse(self):
        value = pathlib.Path(self.input()['GroundReflectedSkyDiffGroup']['result_file'].path)
        return value.as_posix() if value.is_absolute() \
            else pathlib.Path(self.initiation_folder, value).resolve().as_posix()

    @property
    def sun_up_hours(self):
        value = pathlib.Path(self._input_params['sun_up_hours'])
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
        return pathlib.Path(__file__).parent.joinpath('scripts', 'create_irradiance_contrib_map.py').resolve()

    @property
    def is_script(self):
        return False

    def command(self):
        return 'ladybug-comfort map irradiance-contrib result.sql direct_spec.ill indirect_spec.ill ref_spec.ill indirect_diff.ill ref_diff.ill sun-up-hours.txt --aperture-id "{aperture_id}" --{output_format} --folder output'.format(output_format=self.output_format, aperture_id=self.aperture_id)

    def requires(self):
        return {'DirectSunGroup': DirectSunGroup(_input_params=self._input_params), 'OutputMatrixMathGroup': OutputMatrixMathGroup(_input_params=self._input_params), 'GroundReflectedSkySpecGroup': GroundReflectedSkySpecGroup(_input_params=self._input_params), 'TotalSkyDiffGroup': TotalSkyDiffGroup(_input_params=self._input_params), 'GroundReflectedSkyDiffGroup': GroundReflectedSkyDiffGroup(_input_params=self._input_params)}

    def output(self):
        return {
            'result_folder': luigi.LocalTarget(
                pathlib.Path(self.execution_folder, 'dynamic/final/{grid}/{aperture_id}'.format(grid=self.grid, aperture_id=self.aperture_id)).resolve().as_posix()
            )
        }

    @property
    def input_artifacts(self):
        return [
            {'name': 'result_sql', 'to': 'result.sql', 'from': self.result_sql, 'optional': False},
            {'name': 'direct_specular', 'to': 'direct_spec.ill', 'from': self.direct_specular, 'optional': False},
            {'name': 'indirect_specular', 'to': 'indirect_spec.ill', 'from': self.indirect_specular, 'optional': False},
            {'name': 'ref_specular', 'to': 'ref_spec.ill', 'from': self.ref_specular, 'optional': False},
            {'name': 'indirect_diffuse', 'to': 'indirect_diff.ill', 'from': self.indirect_diffuse, 'optional': False},
            {'name': 'ref_diffuse', 'to': 'ref_diff.ill', 'from': self.ref_diffuse, 'optional': False},
            {'name': 'sun_up_hours', 'to': 'sun-up-hours.txt', 'from': self.sun_up_hours, 'optional': False}]

    @property
    def output_artifacts(self):
        return [
            {
                'name': 'result-folder', 'from': 'output',
                'to': pathlib.Path(self.execution_folder, 'dynamic/final/{grid}/{aperture_id}'.format(grid=self.grid, aperture_id=self.aperture_id)).resolve().as_posix(),
                'optional': False,
                'type': 'folder'
            }]

    @property
    def input_parameters(self):
        return {
            'aperture_id': self.aperture_id,
            'output_format': self.output_format,
            'grid': self.grid}

    @property
    def task_image(self):
        return 'docker.io/ladybugtools/ladybug-comfort:0.18.42'

    @property
    def image_workdir(self):
        return '/home/ladybugbot/run'


class _RadianceContribEntryPoint_6b5ce744Orchestrator(luigi.WrapperTask):
    """Runs all the tasks in this module."""
    # user input for this module
    _input_params = luigi.DictParameter()

    @property
    def input_values(self):
        params = dict(_default_inputs)
        params.update(dict(self._input_params))
        return params

    def requires(self):
        yield [CreateIrradianceContribMap(_input_params=self.input_values)]
