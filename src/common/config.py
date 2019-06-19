from .singleton import SingletonType
import configparser

class DefaultConfig(object):

    __metaclass__ = SingletonType

    def __init__(self):
        self._config = None
        self._initialize()

    def _initialize(self):
        self._config = { 
                'mdtest_iops_unit': 'null',
                'mdtest_header': ['task', 'dir_creation', 'dir_stat',
                                  'dir_removal', 'file_creation',
                                  'file_stat', 'file_remove',
                                  'tree_create', 'tree_remove'],

                'ior_header': ['task', 'all_write_max',
                               'all_write_min',
                               'all_write_mean',
                               'all_read_max',
                               'all_read_min',
                               'all_read_mean'],
 
                'fio_iops_unit': 'null',
                'fio_bw_unit': 'MiB',
                'fio_lat_unit': 'usec',
                'fio_header': ['task', 'bs', 'iodepth',
                               'num_jobs', 'iops_avg',
                               'bw_avg', 'lat_avg']
                }

    def set(self, key, value):
        self._config[key] = value

    def get(self, key):
        return self._config[key]

class MoudleConfig(object):

    __metaclass__ = SingletonType

    MODULES = ['MDTest', 'IOR', 'FIO']

    def __init__(self, config_path):
        self._cf = configparser.ConfigParser()
        self._cf.read(config_path)
        self._map = {}
        self._build_map()

    def _build_map(self):
        sections = self._cf.sections()
        for section in sections:
            items = self._cf.items(section)
            items_type = self._cf.get(section, 'type').lower()
            items_dict = {}
            for item in items:
                items_dict[item[0]] = item[1]
            items_dict['name'] = section
            if items_type not in self._map:
                self._map[items_type] = []
            self._map[items_type].append(items_dict)

    def get_config(self, module):
        return self._map[module]

    def get_modules(self):
        return self._map.keys()
