import pprint
import gazu
import os
import re
import json
import time
from collections import defaultdict

from kabaret import flow
from kabaret.subprocess_manager.flow import RunAction
from kabaret.flow_entities.entities import Entity, EntityCollection, Property

from ..utils.kabaret.flow_entities.entities import GlobalEntityCollection

from .maputils import ClearMapAction
from .users import PresetChoiceValue


class KitsuAPIWrapper(flow.Object):

    _server_url = flow.Param("")
    _config = flow.Parent()

    def set_host(self, url):
        gazu.client.set_host(url)

    def get_host(self):
        return gazu.client.get_host()

    def set_server_url(self, url):
        self._server_url.set(url)

    def get_server_url(self):
        return self._server_url.get()

    def log_in(self, login, password):
        success = False

        if login is not None:
            try:
                gazu.log_in(login, password)
            except (
                gazu.exception.AuthFailedException,
                gazu.exception.ServerErrorException,
            ):
                return success
            else:
                success = True

        return success
    
    def log_out(self):
        gazu.log_out()

    def get_tokens(self):
        return gazu.client.default_client.tokens

    def set_tokens(self, tokens):
        gazu.client.set_tokens(tokens)

    def host_is_valid(self):
        return gazu.client.host_is_valid()

    def current_user_logged_in(self):
        """
        Checks if the current user is logged in.

        This method assumes Kitsu client's host is valid.
        """
        try:
            gazu.client.get_current_user()
        except gazu.exception.NotAuthenticatedException:
            return False

        return True
    
    def get_task_name(self, project_task_name, project_subtask_name):
        kitsu_task = None

        if self._config.tasks.has_mapped_name(project_task_name):
            subtasks = self._config.tasks[project_task_name].subtasks
            
            if subtasks.has_mapped_name(project_subtask_name):
                kitsu_task = subtasks[project_subtask_name].get()
        
        return kitsu_task
    
    def get_project_id(self):
        import requests
        try:
            data = gazu.project.get_project_by_name(
                self._config.project_name.get()
            )
        except requests.exceptions.ConnectionError:
            return None
        else:
            return data['id']

    def get_project_fps(self):
        import requests
        try:
            data = gazu.project.get_project_by_name(
                self._config.project_name.get()
            )
        except requests.exceptions.ConnectionError:
            return None
        else:
            return data['fps']

    def get_project_type(self):
        import requests
        try:
            data = gazu.project.get_project_by_name(
                self._config.project_name.get()
            )
        except requests.exceptions.ConnectionError:
            return None
        else:
            return data['production_type']

    def get_entity_type_data(self, entity_type_id):
        return gazu.entity.get_entity_type(entity_type_id)
   
    def get_shot_data(self, name, sequence, episode_name=None):
        if isinstance(sequence, str):
            sequence = self.get_sequence_data(sequence, episode_name)

        if not sequence:
            return None
        
        return gazu.shot.get_shot_by_name(
            sequence,
            name
        )

    def get_shot_duration(self, name, sequence, episode_name=None):
        shot_data = self.get_shot_data(name, sequence, episode_name)
        return shot_data["nb_frames"] if shot_data["nb_frames"] is not None else 0

    def get_shots_data(self, sequence, episode_name=None):
        if isinstance(sequence, str):
            sequence = self.get_sequence_data(sequence, episode_name)

        if not sequence:
            return None
        
        return gazu.shot.all_shots_for_sequence(sequence)
    
    def create_shot(self, sequence_name, shot_name, task_status=None):
        '''
        Creates a shot in the Kitsu project with all its tasks with the status `Todo`.
        '''
        sequence = self.get_sequence_data(sequence_name)
        
        if sequence is None:
            sequence = self.create_sequence(sequence_name)
        
        shot = gazu.shot.new_shot(self._config.project_id.get(), sequence, shot_name)

        if task_status:
            task_status = self.get_task_status(short_name=task_status)

        for task_type in gazu.task.all_task_types_for_project(self._config.project_id.get()):
            if task_type['for_entity'] == 'Shot':
                gazu.task.new_task(shot, task_type, task_status=task_status)
    
    def get_shots(self, task_status_filters=None):
        if task_status_filters is not None:
            shots = []
            shot_is_valid = defaultdict(lambda: False)
            target_tasks = defaultdict(list)
            
            for type_name, statutes in task_status_filters.items():
                task_type = gazu.task.get_task_type_by_name(type_name)

                if task_type is None:
                    continue
                
                for status_name in statutes:
                    task_status = gazu.task.get_task_status_by_name(status_name)

                    if task_status is None:
                        continue

                    target_tasks[task_type['id']].append(task_status['id'])
            
            if target_tasks:
                for t in gazu.task.all_tasks_for_project(self.get_project_id()):
                    if t['task_type_id'] not in target_tasks:
                        continue
                    
                    shot_id = t['entity_id']
                    has_valid_status = False

                    # Loop over statutes
                    for status_id in target_tasks[t['task_type_id']]:
                        if status_id == t['task_status_id']:
                            has_valid_status = True
                            break
                    
                    if has_valid_status:
                        shot = gazu.shot.get_shot(shot_id)
                        shots.append((shot['sequence_name'], shot['name']))
        else:
            shots = [
                (gazu.shot.get_sequence_from_shot(s)['name'], s['name'])
                for s in gazu.shot.all_shots_for_project(self.get_project_id())
            ]
        
        return shots
    
    def get_shot_casting(self, shot, sequence=None, episode_name=None):
        if isinstance(shot, str):
            shot = self.get_shot_data(shot, sequence, episode_name)

        if not shot:
            return None

        return gazu.casting.get_shot_casting(shot)
    
    def get_sequence_data(self, name, episode_name=None):
        episode = None
        if episode_name is not None:
            episode = self.get_episode_data(episode_name)
        
        return gazu.shot.get_sequence_by_name(
            self._config.project_id.get(),
            name,
            episode=episode
        )

    def get_sequences_data(self, episode_name=None):
        episode = None
        if episode_name is not None:
            episode = self.get_episode_data(episode_name)
        
        if episode is not None:
            return gazu.shot.all_sequences_for_episode(episode)
        else:
            return gazu.shot.all_sequences_for_project(
                self._config.project_id.get()
            )
    
    def get_sequence_casting(self, sequence, episode_name=None):
        if isinstance(sequence, str):
            sequence = self.get_sequence_data(sequence, episode_name)

        if not sequence:
            return None

        return gazu.casting.get_sequence_casting(sequence)
    
    def get_episode_data(self, name):
        return gazu.shot.get_episode_by_name(
            self._config.project_id.get(),
            name
        )
    
    def get_episodes_data(self):
        return gazu.shot.all_episodes_for_project(
            self._config.project_id.get()
        )
    
    def get_asset_data(self, name):
        return gazu.asset.get_asset_by_name(
            self._config.project_id.get(),
            name
        )

    def get_assets_data(self, asset_type=None, episode_name=None):
        '''
        Returns a list of Kitsu asset data.

        The result may be filtered by asset type and episode. If
        the `episode_name` is "default_episode", returns the assets
        belonging to the Kitsu default episode "Main Pack".
        '''
        if not asset_type:
            assets_data = gazu.asset.all_assets_for_project(self._config.project_id.get())
        else:
            if isinstance(asset_type, str):
                asset_type = self.get_asset_type_data(asset_type)

            if not asset_type:
                return None
            
            assets_data = gazu.asset.all_assets_for_project_and_type(
                self._config.project_id.get(),
                asset_type
            )
        
        if episode_name is not None:
            # FIXME: find a prettier way to handle Kitsu 'Main Pack' default episode
            if episode_name == 'default_episode':
                assets_data = [
                    a for a in assets_data
                    if a['source_id'] is None
                ]
            else:
                assets_data = [
                    a for a in assets_data
                    if a['source_id'] is not None and episode_name == gazu.shot.get_episode(a['source_id']).get('name')
                ]
            
        return assets_data
    
    def get_asset_type(self, asset):
        if isinstance(asset, str):
            asset = self.get_asset_data(asset)

        if not asset:
            return None

        return gazu.asset.get_asset_type(asset["entity_type_id"])

    def get_asset_type_data(self, name):
        return gazu.asset.get_asset_type_by_name(
            name
        )

    def get_asset_types_data(self):
        import requests
        try:
            data = gazu.project.get_project_by_name(
                self._config.project_name.get()
            )
        except requests.exceptions.ConnectionError:
            return None
        else:
            return gazu.asset.all_asset_types_for_project(
                data
            )
    
    def get_task(self, entity, task_type_name):
        task_type = gazu.task.get_task_type_by_name(task_type_name)
        
        # Check if task type is valid
        if task_type is None:
            task_types = gazu.task.all_task_statuses()
            names = [tt['name'] for tt in task_types]
            self.root().session().log_error((
                f"Invalid task type '{task_type_name}'. "
                "Should be one of " + str(names) + "."
            ))
            return None
        
        task = gazu.task.get_task_by_entity(entity, task_type)
        
        if task is None:
            self.root().session().log_error("Invalid Kitsu entity")
            return None
        
        task = gazu.task.get_task(task['id'])
        
        return task
    
    def get_assign_tasks(self):
        return [task for task in gazu.user.all_tasks_to_do() if task['project_name'] == self._config.project_name.get()]

    def get_done_tasks(self):
        return [task for task in gazu.user.all_done_tasks() if task['project_name'] == self._config.project_name.get()]

    def get_all_comments_for_task(self, task_id):
        return gazu.task.all_comments_for_task(task_id)

    def get_shot_task(self, sequence_name, shot_name, task_type_name, episode_name=None):
        task = None
        shot = self.get_shot_data(shot_name, sequence_name, episode_name)

        if shot is not None:
            task = self.get_task(shot, task_type_name)
        
        return task
    
    def get_shot_task_status_name(self, sequence_name, shot_name, task_type_name, episode_name=None):
        task = self.get_shot_task(sequence_name, shot_name, task_type_name, episode_name)
        status = None
        
        if task is not None:
            status = task['task_status']['name']
        
        return status
    
    def get_task_statutes(self, short_name=False):
        task_statuses = gazu.task.all_task_statuses()
        if short_name:
            return [ts['short_name'] for ts in task_statuses]
        return [ts['name'] for ts in task_statuses]
    
    def get_task_current_status(self, entity, task_type_name):
        task = self.get_task(entity, task_type_name)
        
        if task is None:
            return None
        
        return task['task_status']['name']
    
    def get_task_types(self, entity_type=None):
        types = gazu.task.all_task_types()
        if entity_type == 'Shot':
            return [t['name'] for t in types if t['for_entity'] == 'Shot']
        elif entity_type == 'Asset':
            return [t['name'] for t in types if t['for_entity'] == 'Asset']
        return [t['for_entity']+' - '+t['name'] for t in types]

    def get_user(self, project_user_name=None):
        if project_user_name is None:
            project_user_name = self.root().project().get_user_name()

        user = self.root().project().get_user(project_user_name)

        if user is None:
            self.root().session().log_error(
                (f"No user '{project_user_name}' registered in this project")
            )
            return None

        logins = user.login.get()
        kitsu_user = None
        for login in logins:
            if "@" in login:
                kitsu_user = gazu.person.get_person_by_email(login)
            else:
                kitsu_user = gazu.person.get_person_by_desktop_login(login)

            if not kitsu_user:
                continue
            else:
                break

        if kitsu_user is None:
            self.root().session().log_error(
                (f"No Kitsu login found for user '{project_user_name}'")
            )
            return None

        return kitsu_user

    def get_users(self):
        data = gazu.project.get_project(
            self.get_project_id()
        )
        user_names = []
        for user_id in data['team']:
            user_dict = gazu.person.get_person(user_id)
            if user_dict.get('desktop_login', None) is not None:
                user_names.append(user_dict['desktop_login'])
        return sorted(user_names)
    
    def user_is_assigned(self, kitsu_user, kitsu_task):
        kitsu_id = kitsu_user.get('id', None)
        
        if kitsu_id is None:
            self.root().session().log_error("Invalid Kitsu user")
            return None
        
        assignees = kitsu_task.get('assignees', None)
        
        if assignees is None:
            self.root().session().log_error("Invalid Kitsu task")
            return None
        
        return kitsu_id in assignees

    def get_task_status(self, name=None, short_name=None):
        if name:
            return gazu.task.get_task_status_by_name(name)
        if short_name:
            return gazu.task.get_task_status_by_short_name(short_name)

    def set_task_status(self, task_id, task_status_name, comment='', files=None):
        status = gazu.task.get_task_status_by_name(task_status_name)

        if status is not None:
            comment = gazu.task.add_comment(task_id, status, comment=comment)

            if files:
                gazu.task.add_attachment_files_to_comment(task_id, comment, files)
    
    def set_shot_task_status(self, sequence_name, shot_name, task_type_name, task_status_name, comment='', episode_name=None):
        task = self.get_shot_task(sequence_name, shot_name, task_type_name, episode_name)

        if task is not None:
            status = gazu.task.get_task_status_by_name(task_status_name)

            if status is not None:
                gazu.task.add_comment(task, status, comment=comment)
    
    def upload_shot_preview(self, sequence_name, shot_name, task_type_name, task_status_name, file_path, comment="", episode_name=None, user_name=None):
        shot = self.get_shot_data(shot_name, sequence_name, episode_name)
        result = False
        
        if shot is not None:
            result = self.upload_preview(shot, task_type_name, task_status_name, file_path, comment, user_name)
        
        return result
    
    def upload_asset_preview(self, asset_name, task_type_name, task_status_name, file_path, comment="", user_name=None):
        asset = self.get_asset_data(asset_name)
        result = False
        
        if asset is not None:
            result = self.upload_preview(asset, task_type_name, task_status_name, file_path, comment, user_name)
        
        return result

    def upload_preview(self, kitsu_entity, task_type_name, task_status_name, file_path, comment="", user_name=None):
        # Get user
        user = self.get_user(user_name)
        
        # Get task
        task = self.get_task(kitsu_entity, task_type_name)
        
        if task is None or user is None:
            return False
        
        # Add comment with preview
        
        # Check if preview file exists
        if not os.path.exists(file_path):
            self.root().session().log_error(
                f"Preview file '{file_path}' does not exists."
            )
            return False
        
        task_status = gazu.task.get_task_status_by_name(task_status_name)
        
        # Check if status is valid
        if task_status is None:
            task_statuses = gazu.task.all_task_statuses()
            names = [ts['name'] for ts in task_statuses]
            self.root().session().log_error((
                f"Invalid task status '{task_status_name}'."
                "Should be one of " + str(names) + "."
            ))
            return False
        
        comment = gazu.task.add_comment(task, task_status, comment=comment)

        try:
            gazu.task.add_preview(task, comment, file_path)
        except json.decoder.JSONDecodeError:
            self.root().session().log_warning(
                f'Invalid response from Gazu while uploading preview {file_path}'
            )
            pass
        
        return True


class AddKitsuTaskTypeFile(flow.Action):

    oid_patterns = flow.Param('.*mov$')
    task_patterns = flow.Param(['.*'])

    _map = flow.Parent()

    def needs_dialog(self):
        return True

    def allow_context(self, context):
        return context

    def get_buttons(self):
        return ['Create', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        task_type_file = self._map.add(f'task_type_file_{str(int(time.time()))}')
        task_type_file.oid_patterns.set(self.oid_patterns.get())
        task_type_file.task_patterns.set(self.task_patterns.get())
        self._map.touch()


class RemoveKitsuTaskTypeFile(flow.Action):

    ICON = ('icons.gui', 'remove-symbol')

    _task_type_file = flow.Parent()
    _map = flow.Parent(2)

    def needs_dialog(self):
        return False

    def allow_context(self, context):
        return context

    def run(self, button):
        _map = self._map
        _map.remove(self._task_type_file.name())
        _map.touch()


class KitsuTaskTypeFile(flow.Object):

    oid_patterns = flow.Param()
    task_patterns = flow.Param()

    delete = flow.Child(RemoveKitsuTaskTypeFile)


class KitsuTaskTypeFiles(flow.Map):

    add_task_type_file = flow.Child(AddKitsuTaskTypeFile)

    @classmethod
    def mapped_type(cls):
        return KitsuTaskTypeFile

    def columns(self):
        return ["OID Patterns", "Task Types"]

    def _fill_row_cells(self, row, item):
        row["OID Patterns"] = item.oid_patterns.get()
        row["Task Types"] = item.task_patterns.get()


class KitsuBindings(flow.Object):

    asset_types = flow.HashParam()
    asset_families = flow.HashParam()
    task_type_files = flow.Child(KitsuTaskTypeFiles)

    def _kitsu_api(self):
        return self.root().project().kitsu_api()

    def get_asset_oid(self, kitsu_asset_name):
        kitsu_api = self.root().project().kitsu_api()
        kitsu_asset = kitsu_api.get_asset_data(kitsu_asset_name)

        asset_type = kitsu_api.get_asset_type(kitsu_asset['name'])['name']
        asset_type = self.get_asset_type(asset_type)
        asset_family = self.get_asset_family(kitsu_asset['data']['family'])

        return '%s/asset_lib/asset_types/%s/asset_families/%s/assets/%s' % (
            self.root().project().oid(),
            asset_type,
            asset_family,
            kitsu_asset['name']
        )

    def get_asset_data(self, name):
        kitsu_api = self._kitsu_api()
        kitsu_asset = kitsu_api.get_asset_data(name)

        return dict(
            type=kitsu_api.get_asset_type(name)['name'],
            family=kitsu_asset['data']['family']
        )

    def get_shot_casting(self, shot_name, sequence_name):
        kitsu_api = self._kitsu_api()
        kitsu_casting = kitsu_api.get_shot_casting(shot_name, sequence_name)
        
        if kitsu_casting is None:
            return {}
        
        casting = dict()

        for asset in kitsu_casting:
            asset_name = asset['asset_name']
            asset_data = self.get_asset_data(asset_name)
            asset_data['nb_occurrences'] = asset['nb_occurences']
            casting[asset_name] = asset_data

        return casting

    def get_asset_type(self, kitsu_asset_type):
        if not self.asset_types.has_key(kitsu_asset_type):
            return kitsu_asset_type

        return self.asset_types.get_key(kitsu_asset_type)

    def get_asset_family(self, kitsu_asset_family):
        if not self.asset_families.has_key(kitsu_asset_family):
            return kitsu_asset_family

        return self.asset_families.get_key(kitsu_asset_family)
    
    def get_task(self, entity_data, task_type_name):
        entity = self.get_entity(entity_data)
        
        if entity is None:
            self.root().session().log_error("Invalid Kitsu entity")
            return None
        
        return self._kitsu_api().get_task(entity, task_type_name)
    
    def get_task_types(self, oid):
        task_types = []
        kitsu_config = self.root().project().kitsu_config()

        for task_type_file in self.task_type_files.mapped_items():
            oid_pattern = task_type_file.oid_patterns.get()
            task_patterns = task_type_file.task_patterns.get()
            
            if not isinstance(task_patterns, list):
                task_patterns = [task_patterns]
            
            # Match file name
            if re.search(oid_pattern, oid):
                # Fetch every task that matches
                task_types = [
                    t['name']
                    for t in gazu.task.all_task_types_for_project(kitsu_config.project_id.get())
                    for pattern in task_patterns
                    if re.search(pattern, t['name'])
                ]
        
        return task_types
    
    def get_entity_data(self, contextual_settings):
        kitsu_api = self.root().project().kitsu_api()
        entities_data = {
            'shot': ['shot', 'sequence', 'episode'],
            'asset': ['asset'],
        }
        
        # Remove episode key if kitsu project is not a TV Show
        project_type = kitsu_api.get_project_type()
        if project_type != 'tvshow':
            entities_data['shot'].remove('episode')
        
        entity_data = {}
        
        for entity_type, entity_keys in entities_data.items():
            for key in entity_keys:
                entity_data[key] = contextual_settings.get(key, None)
            
            if all(v is not None for v in entity_data.values()):
                entity_data.update(dict(entity_type=entity_type))
                return entity_data
            else:
                entity_data = {}
        
        return None
    
    def get_kitsu_entity(self, entity_data):
        if entity_data is None:
            return None

        entity_type = entity_data['entity_type']
        
        if entity_type == 'shot':
            return self._kitsu_api().get_shot_data(entity_data['shot'], entity_data['sequence'], entity_data.get('episode'))
        elif entity_type == 'asset':
            return self._kitsu_api().get_asset_data(entity_data['asset'])
        else:
            return None

    def set_task_type(self, file_name, task_type):
        existing = [t for t in self.task_type_files.mapped_items() if file_name in t.oid_patterns.get()]
        if len(existing) > 0:
            existing = existing[0].task_patterns.set(task_type)
        else:
            new = self.task_type_files.add(f"task_type_file_{str(int(time.time()))}")
            new.oid_patterns.set(file_name)
            new.task_patterns.set(task_type)
        
        self.task_type_files.touch()
        
        # return self.task_type_files.get()


class ChangeKitsuUserLogin(flow.Action):

    login = flow.SessionParam('')

    _user = flow.Parent()
    _map  = flow.Parent(2)

    def needs_dialog(self):
        self.login.set(self._user.get_login())
        return True
    
    def get_buttons(self):
        return ['Save', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        self._user.set_login(self.login.get())
        self._map.touch()


class EditKitsuSubtask(flow.Action):

    kitsu_task = flow.SessionParam('')

    _subtask = flow.Parent()
    _map  = flow.Parent(2)

    def needs_dialog(self):
        self.kitsu_task.set(self._subtask.get())
        return True
    
    def get_buttons(self):
        return ['Save', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        self._subtask.set(self.kitsu_task.get())
        self._map.touch()


class KitsuSubtask(flow.values.Value):
    
    edit = flow.Child(EditKitsuSubtask)


class KitsuSubtasks(flow.DynamicMap):

    _task = flow.Parent()

    @classmethod
    def mapped_type(cls):
        return KitsuSubtask

    def mapped_names(self, page_num=0, page_size=None):
        tm = self.root().project().get_task_manager()
        return tm.get_subtasks(self._task.name())
    
    def columns(self):
        return ['Name', 'Kitsu task']
    
    def _fill_row_cells(self, row, item):
        row['Name'] = item.name()
        row['Kitsu task'] = item.get()
    
    def _fill_row_style(self, style, item, row):
        style['activate_oid'] = item.edit.oid()


class KitsuTask(flow.Object):
    
    subtasks = flow.Child(KitsuSubtasks).ui(
        expanded=True,
        action_submenus=True,
        items_action_submenus=True,
    )


class KitsuTasks(flow.DynamicMap):

    @classmethod
    def mapped_type(cls):
        return KitsuTask

    def mapped_names(self, page_num=0, page_size=None):
        tm = self.root().project().get_task_manager()
        return tm.default_tasks.mapped_names()


class KitsuTaskAvailableStatutes(flow.values.MultiChoiceValue):

    DEFAULT_EDITOR = 'multichoice'

    def choices(self):
        return self.root().project().kitsu_api().get_task_statutes(short_name=True)


class KitsuTaskStatus(PresetChoiceValue):
    
    DEFAULT_EDITOR = 'choice'
    
    def choices(self):
        status = self.root().project().kitsu_config().task_statutes.get()
        self.names_dict={}
        for s in status:
            self.names_dict[s.upper()] = s
        return self.names_dict.keys()


class UpdateKitsuSettings(flow.Action):

    _kitsu_object = flow.Parent(2)

    def needs_dialog(self):
        return False

    def run(self, button):
        self._kitsu_object.update_kitsu_settings()


class UpdateItemsKitsuSettings(flow.Action):

    _kitsu_map = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        for item in self._kitsu_map.mapped_items():
            item.update_kitsu_settings()

        self._kitsu_map.touch()


class KitsuSetting(flow.values.Value):
    pass


class KitsuSettings(flow.Map):

    clear_settings = flow.Child(ClearMapAction)
    update_settings = flow.Child(UpdateKitsuSettings)

    @classmethod
    def mapped_type(cls):
        return KitsuSetting

    def columns(self):
        return ["Name", "Value"]

    def _fill_row_cells(self, row, item):
        row["Name"] = item.name()
        row["Value"] = item.get()

    def update(self, settings):
        try:
            settings["kitsu_name"] = settings.pop("name")
        except KeyError:
            pass

        for name, value in settings.items():
            try:
                kitsu_setting = self.get_mapped(name)
            except flow.exceptions.MappedNameError:
                kitsu_setting = self.add(name)

            kitsu_setting.set(value)

        self.touch()


class OpenInBrowser(RunAction):

    ICON = ("icons.libreflow", "firefox")

    _url = flow.Parent()

    def runner_name_and_tags(self):
        return "Firefox", ["Browser"]

    def extra_argv(self):
        return [self._url.get()]

    def allow_context(self, context):
        return context and context.endswith(".inline")

    def needs_dialog(self):
        return False


class Url(flow.values.ComputedValue):

    open_in_browser = flow.Child(OpenInBrowser)


class KitsuObject(flow.Object):
    """
    Abstract class representing a Kitsu entity.

    Subclasses must implement the *kitsu_dict* and *compute_child_value* methods.
    """

    kitsu_settings = flow.Child(KitsuSettings).ui(hidden=True)
    kitsu_url = flow.Computed(computed_value_type=Url).ui(hidden=True)
    kitsu_id = flow.Param().ui(editable=False).ui(hidden=True)

    def kitsu_setting_names(self):
        """
        Returns the list of object's settings names, as a subset of the keys
        of the dictionary returned by *kitsu_dict*.

        Returning None will skip name filtering on *kitsu_dict* result
        in *get_kitsu_settings*.
        """
        return None

    def kitsu_dict(self):
        """
        Must be implemented to return a dictionary of parameters related
        to the Kitsu entity.

        It should simply consists in calling the appropriate Gazu
        function given the object's *kitsu_id*.
        """
        raise NotImplementedError()

    def get_kitsu_settings(self):
        settings = self.kitsu_dict()
        names = self.kitsu_setting_names()

        if names is None:
            return settings

        return {name: settings[name] for name in names}

    def update_kitsu_settings(self):
        self.kitsu_settings.update(self.get_kitsu_settings())


class KitsuMap(flow.Map):
    @classmethod
    def mapped_type(cls):
        return KitsuObject


class EntityType(flow.values.ChoiceValue):

    CHOICES = ["Assets", "Shots"]


class SyncFromKitsu(flow.Action):

    ICON = ("icons.libreflow", "sync_arrow")

    entity_type = flow.Param("Assets", EntityType)
    from_index = flow.IntParam(0).ui(label="From")
    to_index = flow.IntParam(10).ui(label="To")

    def get_buttons(self):
        self.message.set("<h3>Synchronize entities from Kitsu</h3>")

        return ["Synchronize", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return

        project = self.root().project()
        project_kitsu_id = project.kitsu_id.get()

        import time

        start_time = time.time()
        i = 0

        if self.entity_type.get() == "Shots":
            kitsu_sequences = gazu.shot.all_sequences_for_project(project_kitsu_id)[
                self.from_index.get() : self.to_index.get()
            ]
            sequences = project.sequences

            # Pull sequences
            for kitsu_sequence in kitsu_sequences:
                try:
                    sequence = sequences.add(kitsu_sequence["name"])
                except flow.exceptions.MappedNameError:
                    # Ignore sequence already mapped
                    continue

                sequence_id = kitsu_sequence["id"]
                sequence.kitsu_id.set(sequence_id)
                sequence.description.set(kitsu_sequence["description"])
                sequence.update_kitsu_settings()

                # Pull shots
                kitsu_shots = gazu.shot.all_shots_for_sequence(sequence_id)
                shots = sequence.shots

                for kitsu_shot in kitsu_shots:
                    try:
                        shot = shots.add(kitsu_shot["name"])
                    except flow.exceptions.MappedNameError:
                        # Ignore shot already mapped
                        continue

                    shot.kitsu_id.set(kitsu_shot["id"])
                    shot.description.set(kitsu_shot["description"])
                    shot.update_kitsu_settings()

                    i += 1

                shots.touch()

            sequences.touch()

            elapsed_time = float(time.time() - start_time)
            self.root().session().log_debug(
                "Elapsed time: {:.4f} min. ({:.4f} min. per shot) ({} shots)".format(
                    elapsed_time / 60.0, elapsed_time / (60.0 * float(i)), i
                )
            )

        elif self.entity_type.get() == "Assets":
            kitsu_assets = gazu.asset.all_assets_for_project(project_kitsu_id)[
                self.from_index.get() : self.to_index.get()
            ]
            assets = project.asset_lib
            i = 0

            for kitsu_asset in kitsu_assets:
                try:
                    asset = assets.add(kitsu_asset["name"])
                except (flow.exceptions.MappedNameError, TypeError) as e:
                    if isinstance(e, flow.exceptions.MappedNameError):
                        # Asset is already mapped
                        i += 1
                        continue

                    try:
                        asset = assets.add("asset{:04d}".format(i))
                    except flow.exceptions.MappedNameError:
                        i += 1
                        continue

                asset.kitsu_id.set(kitsu_asset["id"])
                asset.description.set(kitsu_asset["description"])
                asset.update_kitsu_settings()

                i += 1

            assets.touch()


class KitsuProject(KitsuObject):

    kitsu_name = flow.Param("").watched().ui(hidden=True)
    kitsu_url = flow.Computed().ui(hidden=True)
    kitsu_id = flow.Computed().ui(hidden=True)

    kitsu_api = flow.Child(KitsuAPIWrapper).ui(hidden=True)
    sync_from_kitsu = flow.Child(SyncFromKitsu).injectable().ui(label="Synchronize", hidden=True)

    def kitsu_dict(self):
        project_name = self.kitsu_name.get()
        if not project_name:
            project_name = self.name()

        return gazu.project.get_project_by_name(project_name)

    def child_value_changed(self, child_value):
        if child_value is self.kitsu_name:
            self.kitsu_id.touch()
            self.kitsu_url.touch()

    def compute_child_value(self, child_value):
        if child_value is self.kitsu_id:
            project_dict = self.kitsu_dict()
            child_value.set(project_dict["id"])
        elif child_value is self.kitsu_url:
            child_value.set(
                "%s/productions/%s"
                % (self.kitsu_api.get_server_url(), self.kitsu_id.get())
            )


class KitsuShot(KitsuObject):

    # def kitsu_setting_names(self):
    #     return ['name', 'description', 'nb_frames', 'data']

    def kitsu_dict(self):
        return gazu.shot.get_shot(self.kitsu_id.get())

    def compute_child_value(self, child_value):
        if child_value is self.kitsu_url:
            child_value.set(
                "%s/shots/%s"
                % (self.root().project().kitsu_url.get(), self.kitsu_id.get())
            )


class KitsuSequence(KitsuObject):
    def kitsu_dict(self):
        return gazu.shot.get_sequence(self.kitsu_id.get())

    def compute_child_value(self, child_value):
        if child_value is self.kitsu_url:
            child_value.set(
                "%s/shots?search=%s"
                % (self.root().project().kitsu_url.get(), self.name())
            )


class KitsuAsset(KitsuObject):
    def kitsu_dict(self):
        return gazu.asset.get_asset(self.kitsu_id.get())

    def compute_child_value(self, child_value):
        if child_value is self.kitsu_url:
            child_value.set(
                "%s/assets/%s"
                % (self.root().project().kitsu_url.get(), self.kitsu_id.get())
            )
