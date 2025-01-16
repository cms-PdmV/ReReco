"""
Module that contains Sequence class
"""
import weakref
from core.model.model_base import ModelBase


class Sequence(ModelBase):
    """
    Sequence is a dictionary that has all user editable attributes
    for cmsDriver command
    """

    _ModelBase__schema = {
        # What conditions to use. This has to be specified
        'conditions': '',
        # Hash of configuration file uploaded to ReqMgr2
        'config_id': '',
        # Specify the file where the code to modify the process object is stored
        # If inline_custom is set to 1, then inline the customisation file
        'customise': '',
        # What data tier to use
        'datatier': [],
        # Specify which era to use (e.g. "run2")
        'era': '',
        # What event content to write out
        'eventcontent': [],
        # Freeform attributes appended at the end
        'extra': '',
        # GPU parameters
        'gpu': {
            'requires': 'forbidden',
            'gpu_memory': '',
            'cuda_capabilities': [],
            'cuda_runtime': '',
            'gpu_name': '',
            'cuda_driver_version': '',
            'cuda_runtime_version': ''
        },
        # Hash of harvesting configuration file uploaded to ReqMgr2
        'harvesting_config_id': '',
        # How many threads should CMSSW use
        'nThreads': 1,
        # Scenario overriding standard settings: 'pp', 'cosmics', 'nocoll', 'HeavyIons'
        'scenario': 'pp',
        # The desired step. The possible values are:
        # RAW2DIGI, L1Reco, RECO, EI, PAT, NANO, ALCA[:@...], DQM[:@...], SKIM[:@...],
        # HARVESTING:@...
        'step': []}

    lambda_checks = {
        'conditions': lambda c: ModelBase.matches_regex(c, '[a-zA-Z0-9_]{0,50}'),
        'config_id': lambda cid: ModelBase.matches_regex(cid, '[a-f0-9]{0,50}'),
        '__datatier': lambda s: s in {'ALCARECO', 'AOD', 'DQMIO', 'MINIAOD',
                                      'NANOAOD', 'RECO', 'USER', 'FEVTDEBUGHLT', 'RAW'},
        'era': lambda e: ModelBase.matches_regex(e, '[a-zA-Z0-9_\\,]{0,50}'),
        '__eventcontent': lambda s: s in {'ALCARECO', 'AOD', 'DQM', 'MINIAOD',
                                          'NANOAOD', 'NANOEDMAOD', 'RECO', 'FEVT',
                                          'FEVTDEBUG', 'FEVTDEBUGHLT', 'RAW'},
        '_gpu': {
            'requires': lambda r: r in ('forbidden', 'optional', 'required'),
            'cuda_capabilities': lambda l: isinstance(l, list),
            'gpu_memory': lambda m: m == '' or int(m) > 0,
        },
        'harvesting_config_id': lambda cid: ModelBase.matches_regex(cid, '[a-f0-9]{0,50}'),
        'nThreads': lambda n: 0 < n < 64,
        'scenario': lambda s: s in {'pp', 'cosmics', 'nocoll', 'HeavyIons'},
        '__step': lambda s: (s.split(':')[0] in {'ALCA', 'DQM', 'EI', 'FILTER', 'HARVESTING',
                                                 'L1Reco', 'NANO', 'PAT', 'RAW2DIGI', 'RECO',
                                                 'SKIM', 'L1REPACK', 'HLT'})
    }

    def __init__(self, json_input=None, parent=None, check_attributes=True):
        self.parent = None
        if json_input:
            if json_input.get('gpu', {}).get('requires') not in ('optional', 'required'):
                json_input['gpu'] = self.schema().get('gpu')
                json_input['gpu']['requires'] = 'forbidden'

        ModelBase.__init__(self, json_input, check_attributes)
        if parent:
            self.parent = weakref.ref(parent)

        self.check_attribute('eventcontent', self.get('eventcontent'))
        self.check_attribute('datatier', self.get('datatier'))

    def get_prepid(self):
        if not self.parent:
            return 'Sequence'

        parent = self.parent()
        index = self.get_index_in_parent()
        return f'Sequence_{parent}_{index}'

    def check_attribute(self, attribute_name, attribute_value):
        if not self.initialized or attribute_name not in ('eventcontent', 'datatier'):
            return super().check_attribute(attribute_name, attribute_value)

        has_harvesting_step = bool([s for s in self.get('step') if s.startswith('HARVESTING:@')])
        if not self.get('step') or has_harvesting_step:
            return super().check_attribute(attribute_name, attribute_value)

        # If sequence does not have HARVESTING step, eventcontent and datatier cannot be empty
        if not self.get('eventcontent'):
            raise AssertionError('No eventcontent is allowed only with HARVESTING step')

        if not self.get('datatier'):
            raise AssertionError('No datatier is allowed only with HARVESTING step')

        return super().check_attribute(attribute_name, attribute_value)

    def needs_harvesting(self):
        """
        Return if this sequence produces input file for harvesting
        and harvesting step is needed
        """
        if self.parent and not self.parent().get('enable_harvesting'):
            # Parent request has harvesting disabled
            return False

        for step in self.get('step'):
            if step == 'DQM' or step.startswith('DQM:'):
                return True

        return False

    def get_index_in_parent(self):
        """
        Return sequence's index in parent's list of sequences
        """
        for index, sequence in enumerate(self.parent().get('sequences')):
            if self == sequence:
                return index

        raise AssertionError(f'Sequence is not a child of {self.parent().get_prepid()}')

    def get_name(self):
        """
        Return a sequence name which is based on parent
        prepid and sequence number
        Last sequence always has the same name as parent prepid
        Other sequences have suffix with their index, e.g

        PrepID_0
        PrepID_1
        PrepID

        If there is only one sequence, it will be the last one
        and have the same name as parent prepid
        """
        index = self.get_index_in_parent()
        parent_prepid = self.parent().get_prepid()
        if index != len(self.parent().get('sequences')) - 1:
            sequence_name = f'{parent_prepid}_{index}'
        else:
            sequence_name = f'{parent_prepid}'

        return sequence_name

    def get_config_file_names(self):
        """
        Return dictionary of 'config' and 'harvest' config file names
        """
        parent_prepid = self.parent().get_prepid()
        index = self.get_index_in_parent()
        config_file_names = {'config': f'{parent_prepid}_{index}_cfg'}
        if self.needs_harvesting():
            config_file_names['harvest'] = f'{parent_prepid}_{index}_harvest_cfg'

        return config_file_names

    def __build_cmsdriver(self, cmsdriver_type, arguments):
        """
        Build a cmsDriver command from given arguments
        Add comment in front of the command
        """
        self.logger.info('Generating %s cmsDriver', cmsdriver_type)
        # Actual command
        command = f'# Command for {cmsdriver_type}:\ncmsDriver.py {cmsdriver_type}'
        # Comment in front of the command for better readability
        comment = f'# Arguments for {cmsdriver_type}:\n'
        for key in sorted(arguments.keys()):
            if not arguments[key]:
                continue

            if key in 'extra':
                continue

            if isinstance(arguments[key], bool):
                arguments[key] = ''

            if isinstance(arguments[key], list):
                arguments[key] = ','.join([str(x) for x in arguments[key]])

            command += f' --{key} {arguments[key]}'.rstrip()
            comment += f'# --{key} {arguments[key]}'.rstrip() + '\n'

        if arguments.get('extra'):
            extra_value = arguments['extra']
            command += f' {extra_value}'
            comment += f'# <extra> {extra_value}\n'

        # Exit the script with error of cmsDriver.py
        command += ' || exit $?'

        return comment + '\n' + command

    def get_cmsdriver(self, overwrite_input=None):
        """
        Return a cmsDriver command for this sequence
        Config file is named like this
        PrepID_0_cfg.py
        """
        sequence_name = self.get_name()
        arguments_dict = dict(self.get_json())
        # Delete sequence metadata
        arguments_dict.pop('config_id', None)
        arguments_dict.pop('gpu', None)
        arguments_dict.pop('harvesting_config_id', None)

        # Fetch list of files for specific runs
        das_query = ''
        # Handle input/output file names
        if overwrite_input:
            arguments_dict['filein'] = overwrite_input
        else:
            index = self.get_index_in_parent()
            arguments_dict['number'] = 10
            if index == 0:
                input_dataset = self.parent().get('input')['dataset']
                all_runs = self.parent().get('runs')
                if not input_dataset:
                    input_request = self.parent().get('input')['request']
                    arguments_dict['filein'] = f'"file:{input_request}.root"'
                elif all_runs:
                    das_file = f'{sequence_name}_files.txt'
                    das_query += '# Query DAS to get list of files for specified runs\n'
                    # Chunkify to 25 runs, otherwise script line gets very long
                    for runs in self.chunkify(all_runs, 25):
                        runs = ','.join([str(r) for r in runs])
                        das_query += 'dasgoclient --limit 0 '
                        das_query += f'--query "file dataset={input_dataset} run in [{runs}]" '
                        das_query += f'>> {das_file}\n'

                    das_query += '\n'
                    arguments_dict['filein'] = f'"filelist:{das_file}"'
                else:
                    arguments_dict['filein'] = f'"dbs:{input_dataset}"'
            else:
                previous_sequence = self.parent().get('sequences')[index - 1]
                input_file = f'{previous_sequence.get_name()}.root'
                arguments_dict['filein'] = f'"file:{input_file}"'

        # Update ALCA and SKIM steps to ALCA:@Dataset and SKIM:@Dataset
        # if dataset name is in "auto" dictionary in CMSSW
        dynamic_steps = self.update_dynamic_steps(arguments_dict['step'])
        # Build argument dictionary
        config_names = self.get_config_file_names()
        arguments_dict['fileout'] = f'"file:{sequence_name}.root"'
        arguments_dict['python_filename'] = f'"{config_names["config"]}.py"'
        arguments_dict['no_exec'] = True
        cms_driver_command = self.__build_cmsdriver('RECO', arguments_dict)
        return dynamic_steps + das_query + cms_driver_command

    def update_dynamic_steps(self, steps):
        """
        Update ALCA and SKIP steps to be variables and return code that resolves them
        """
        dynamic_steps = ''
        for step_index, step in enumerate(steps):
            if step not in ('ALCA', 'SKIM'):
                continue

            dataset = self.parent().get_dataset()
            steps[step_index] = f'${step}_STEP'
            # Build a small python program to get value from CMSSW on the go
            step_var = f'{step}_STEP=$($PYTHON_INT -c "'
            if step == 'ALCA':
                step_var += 'from Configuration.AlCa.autoAlca import AlCaRecoMatrix as ds;'
            elif step == 'SKIM':
                step_var += 'from Configuration.Skimming.autoSkim import autoSkim as ds;'

            step_var += f'print(\'{step}:@{dataset}\' if \'{dataset}\' in ds.keys() else \'\')")'
            dynamic_steps += f'{step_var}\n'

        if dynamic_steps:
            dynamic_steps = f'# Steps based on dataset name\n{dynamic_steps}\n'

        return dynamic_steps

    def get_harvesting_cmsdriver(self):
        """
        Return a harvesting cmsDriver for this sequence
        Config file is named like this
        PrepID_0_harvest_cfg.py
        """
        if not self.needs_harvesting():
            return ''

        arguments_dict = dict(self.get_json())
        # Delete sequence metadata
        for attr in ('config_id', 'gpu', 'harvesting_config_id', 'customise',
                     'datatier', 'eventcontent', 'nThreads', 'extra'):
            arguments_dict.pop(attr, None)

        # Get correct configuration of DQM step, e.g.
        # DQM:@rerecoCommon should be changed to HARVESTING:@rerecoCommon
        step = 'HARVESTING:dqmHarvesting'
        for one_step in self.get('step'):
            if one_step.startswith('DQM:'):
                step = one_step.replace('DQM:', 'HARVESTING:', 1)
                break

        # Build argument dictionary
        sequence_name = self.get_name()
        config_names = self.get_config_file_names()
        arguments_dict['data'] = True
        arguments_dict['no_exec'] = True
        arguments_dict['filetype'] = 'DQM'
        arguments_dict['step'] = step
        arguments_dict['era'] = arguments_dict['era'].split(',')[0]
        arguments_dict['filein'] = f'"file:{sequence_name}_inDQM.root"'
        arguments_dict['python_filename'] = f'"{config_names["harvest"]}.py"'
        arguments_dict['number'] = -1
        harvesting_command = self.__build_cmsdriver('HARVESTING', arguments_dict)
        return harvesting_command

    @staticmethod
    def chunkify(items, chunk_size):
        """
        Yield fixed size chunks of given list
        """
        start = 0
        chunk_size = max(chunk_size, 1)
        while start < len(items):
            yield items[start: start + chunk_size]
            start += chunk_size

    def get_output_module(self):
        """
        Return a output module name
        """
        eventcontent = [e for e in self.get('eventcontent') if not e.startswith('DQM')]
        if not eventcontent:
            return ''

        return f'{eventcontent[0]}output'

    def get_gpu_requires(self):
        """
        Return whether GPU is required, optional of forbidden
        """
        return self.get('gpu')['requires']

    def get_gpu_dict(self):
        """
        Return a dictionary with GPU parameters for ReqMgr2
        """
        gpu_info = self.get('gpu')
        keys = {'cuda_capabilities': 'CUDACapabilities',
                'cuda_runtime': 'CUDARuntime',
                'gpu_name': 'GPUName',
                'cuda_driver_version': 'CUDADriverVersion',
                'cuda_runtime_version': 'CUDARuntimeVersion'}
        params = {key: gpu_info[attr] for attr, key in keys.items() if gpu_info.get(attr)}
        if gpu_info.get('gpu_memory'):
            params['GPUMemoryMB'] = int(gpu_info['gpu_memory'])

        return params
