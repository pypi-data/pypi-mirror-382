import os
import re
import json
import time
import pprint
from kabaret import flow
from .users import PresetSessionValue


class TaskItem(flow.Object):

    _action            = flow.Parent(3)

    task_id            = flow.SessionParam()
    task_type          = flow.SessionParam()
    task_status        = flow.SessionParam()
    task_status_color  = flow.SessionParam()
    task_comments      = flow.SessionParam()
    task_oid           = flow.SessionParam()
    entity_id          = flow.SessionParam()
    entity_type        = flow.SessionParam() # Asset or Shot
    entity_type_name   = flow.SessionParam() # Asset Type or Sequence name
    entity_name        = flow.SessionParam() # Asset or Shot name
    episode_name       = flow.SessionParam()
    entity_description = flow.SessionParam().ui(editor='textarea')
    shot_frames        = flow.SessionParam()
    dft_task_name      = flow.SessionParam()
    primary_files      = flow.SessionParam(list)
    is_bookmarked      = flow.SessionParam().ui(editor='bool')


class MyTasksMap(flow.DynamicMap):

    _settings = flow.Parent()
    _action = flow.Parent(2)

    def __init__(self, parent, name):
        super(MyTasksMap, self).__init__(parent, name)
        self._document_cache = None
        self._document_cache_2 = None
        self._document_cache_key = None

    @classmethod
    def mapped_type(cls):
        return TaskItem

    def columns(self):
        return ['Task', 'Status', 'Type', 'Type Name', 'Name']

    def mapped_names(self, page_num=0, page_size=None):
        cache_key = (page_num, page_size)
        
        # Update if no cache or time elapsed
        if (
            self._document_cache is None
            or self._document_cache_key != cache_key
        ):
            self._mng.children.clear()
            self._document_cache = {}

            self.root().session().log_info('[MyTasks] Fetching Kitsu tasks')
            self.get_kitsu_tasks()
            self.root().session().log_info('[MyTasks] Fetching Libreflow bookmarks')
            self.get_bookmarks()

            # Sorting tasks
            self.root().session().log_info('[MyTasks] Sorting list')
            if self._settings.task_sorted.get() == 'Entity name':
                self._document_cache = dict(sorted(
                    self._document_cache.items(),
                    key=lambda data: (data[1]['entity_type_name'], data[1]['entity_name'])
                ))
            elif self._settings.task_sorted.get() == 'Status':
                self._document_cache = dict(sorted(
                    self._document_cache.items(),
                    key=lambda data: (data[1]['task_status'], data[1]['entity_type_name'], data[1]['entity_name'])
                ))
            elif self._settings.task_sorted.get() == 'Latest update':
                self._document_cache = dict(sorted(
                    self._document_cache.items(),
                    key=lambda data: data[1]['updated_date'],
                    reverse=True
                ))

            self._document_cache_key = cache_key
            self.root().session().log_info('[MyTasks] Data updated')

        return self._document_cache.keys()

    def get_cache_key(self):
        return self._document_cache_key

    def compare(self):
        items = self.mapped_items()

        # Fetch data in a second dict
        self._document_cache_2 = {}
        self.get_kitsu_tasks(compare=True)
        self.get_bookmarks(compare=True)

        # Sorting tasks
        if self._settings.task_sorted.get() == 'Entity name':
            self._document_cache_2 = dict(sorted(
                self._document_cache_2.items(),
                key=lambda data: (data[1]['entity_type_name'], data[1]['entity_name'])
            ))
        elif self._settings.task_sorted.get() == 'Status':
            self._document_cache_2 = dict(sorted(
                self._document_cache_2.items(),
                key=lambda data: (data[1]['task_status'], data[1]['entity_type_name'], data[1]['entity_name'])
            ))
        elif self._settings.task_sorted.get() == 'Latest update':
            self._document_cache_2 = dict(sorted(
                self._document_cache_2.items(),
                key=lambda data: data[1]['updated_date'],
                reverse=True
            ))

        equal = True
        # If tasks count has changed
        if len(self._document_cache) != len(self._document_cache_2):
            equal = False

        # Update task if it already exists in the current list
        for key, value in self._document_cache_2.items():
            exists = False
            for item in items:
                if value['task_oid'] == item.task_oid.get():
                    exists = True
                    self._document_cache[item.name()] = self._document_cache_2[key]
                    self._configure_child(item)
                    break
            
            if not exists:
                equal = False

        return equal

    def get_kitsu_tasks(self, compare=None):
        kitsu_tasks = self._action.kitsu.gazu_api.get_assign_tasks()
        kitsu_project_type = self._action.kitsu.project_type.get()
        if 'DONE' in self._settings.task_statues_filter.get():
            kitsu_tasks += self._action.kitsu.gazu_api.get_done_tasks()
        
        for i, task_data in enumerate(kitsu_tasks):
            data = {}
            
            # Ignore it if status is not in filter
            if task_data['task_status_short_name'].upper() not in self._settings.task_statues_filter.get():
                continue

            # Ignore asset entities for FDT
            if (
                task_data['entity_type_name'] in self._settings.hidden_asset_types.get() or
                task_data['task_type_name'] in self._settings.hidden_tasks.get()
            ):
                continue

            # Set base values
            data.update(dict(
                task_id=task_data['id'],
                task_type=task_data['task_type_name'],
                task_status=task_data['task_status_short_name'],
                entity_id=task_data['entity_id'],
                entity_name=task_data['entity_name'],
                entity_description=task_data['entity_description'],
                shot_frames=None,
                is_bookmarked=False,
                updated_date=task_data['updated_at']
            ))

            # Add episode name if project is a tvshow
            if kitsu_project_type == 'tvshow':
                data.update(dict(
                    episode_name=task_data['episode_name']
                ))

            if compare is None:
                self.root().session().log_info(f"[MyTasks]   - Fetching {data['entity_name']}")

            # Get task status color
            task_status_data = self._action.kitsu.gazu_api.get_task_status(short_name=task_data['task_status_short_name'])
            data.update(dict(
                task_status_color=task_status_data["color"]
            ))

            # Get task comments
            data.update(dict(
                task_comments=self._action.kitsu.gazu_api.get_all_comments_for_task(task_data['id'])
            ))

            # Set specific values based on entity type
            if task_data['task_type_for_entity'] == "Shot":
                shot_data = self._action.kitsu.gazu_api.get_shot_data(
                    task_data['entity_name'], task_data['sequence_name'],
                    task_data['episode_name'] if kitsu_project_type == 'tvshow' else None
                )
                data.update(dict(
                    entity_type=task_data['entity_type_name'],
                    entity_type_name=task_data['sequence_name'],
                    shot_frames=shot_data['nb_frames']
                ))
            elif task_data['task_type_for_entity'] == "Asset":
                # Add additional data if project is a tvshow
                if kitsu_project_type == 'tvshow':
                    asset_data = self._action.kitsu.gazu_api.get_asset_data(task_data['entity_name'])
                    if asset_data['source_id']:
                        episode_data = gazu.shot.get_episode(asset_data['source_id'])
                        episode_name = episode_data['name']
                    else:
                        # Get main pack syntax from asset libs
                        asset_libs_names = self.root().project().asset_libs.mapped_names()
                        match = [name for name in asset_libs_names if re.match('main_pack', name, re.IGNORECASE)]
                        episode_name = match[0] if match else 'main_pack'
                    
                    data.update(dict(
                        episode_name=episode_name
                    ))

                data.update(dict(
                    entity_type=task_data['task_type_for_entity'],
                    entity_type_name=task_data['entity_type_name']
                ))
                if 'category' in task_data['entity_data']:
                    data.update(dict(
                        category=task_data['entity_data']['category']
                    ))

            # Set task name, oid and primary files
            data['dft_task_name'] = self.find_default_task(data['task_type'], compare)
            data['task_oid'], data['primary_files'] = self.set_task_oid(data, compare)

            if compare:
                i = len(self._document_cache_2) + 1
                self._document_cache_2['task'+str(i)] = data
            else:
                i = len(self._document_cache) + 1
                self._document_cache['task'+str(i)] = data

    def get_bookmarks(self, compare=None):
        document_cache = self._document_cache if not compare else self._document_cache_2

        bookmarks = self.root().project().get_user().bookmarks.mapped_items()
        kitsu_project_type = self._action.kitsu.project_type.get()

        for b in bookmarks:
            # Regex for get all values and kitsu entity
            oid = b.goto_oid.get()
            task_name = re.search('(?<=tasks\/)[^\/]*', oid).group(0)

            if '/films' in oid:
                sequence_name = re.search('(?<=sequences\/)[^\/]*', oid).group(0)
                shot_name = re.search('(?<=shots\/)[^\/]*', oid).group(0)
                
                episode_name = None
                if kitsu_project_type == 'tvshow':
                    episode_name = re.search('(?<=films\/)[^\/]*', oid).group(0)

                if compare is None:
                    self.root().session().log_info(
                        f'[MyTasks]   - Fetching {episode_name if episode_name else ""} {sequence_name} {shot_name}'
                    )
                    self.root().session().log_info(
                        f'[MyTasks]      - Searching for corresponding Kitsu entity'
                    )
                
                item = self._action.kitsu.gazu_api.get_shot_data(shot_name, sequence_name, episode_name)
            elif '/asset_libs' in oid:
                episode_name = re.search('(?<=asset_libs\/)[^\/]*', oid).group(0)
                asset_type_name = re.search('(?<=asset_types\/)[^\/]*', oid).group(0)
                asset_name = re.search('(?<=assets\/)[^\/]*', oid).group(0)
                if compare is None:
                    self.root().session().log_info(f'[MyTasks]   - Fetching {episode_name} {asset_type_name} {asset_name}')
                    self.root().session().log_info(f'[MyTasks]      - Searching for corresponding Kitsu entity')
                item = self._action.kitsu.gazu_api.get_asset_data(asset_name)
            elif '/asset_types' in oid:
                asset_name = re.search('(?<=assets\/)[^\/]*', oid).group(0)
                if compare is None:
                    self.root().session().log_info(f'[MyTasks]   - Fetching {asset_name}')
                    self.root().session().log_info(f'[MyTasks]      - Searching for corresponding Kitsu entity')
                item = self._action.kitsu.gazu_api.get_asset_data(asset_name)
            
            # Set base values
            data = dict(
                task_id=None, 
                task_type=None,
                task_status=None,
                task_status_color=None,
                task_comments=None,
                task_oid=oid,
                entity_id=None,
                entity_type=None,
                entity_type_name='',
                entity_name='',
                entity_description=None,
                shot_frames=None,
                dft_task_name=task_name,
                primary_files=None,
                is_bookmarked=True,
                updated_date=None
            )

            if kitsu_project_type == 'tvshow':
                data.update(dict(episode_name=episode_name))

            # Libreflow entity has not been found on Kitsu
            if item is None:
                if compare is None:
                    self.root().session().log_info(f'[MyTasks]          - Entity not found')
                
                i = len(document_cache) + 1
                document_cache['task'+str(i)] = data
                continue
            
            # Get kitsu task data
            if compare is None:
                self.root().session().log_info(f'[MyTasks]      - Searching for corresponding Kitsu task')
            kitsu_tasks = self._action.task_mgr.default_tasks[task_name].kitsu_tasks.get()

            # Use task object name if empty
            if kitsu_tasks is None:
                kitsu_task_name = task_name
            # Use single entry in kitsu tasks list
            elif len(kitsu_tasks) == 1:
                kitsu_task_name = kitsu_tasks[0]
            # Try to find the closest one in kitsu tasks list
            else:
                kitsu_task_name = next(
                    (name for name in kitsu_tasks if task_name.lower() in name.lower()), task_name
                )
            
            task_data = self._action.kitsu.gazu_api.get_task(item, kitsu_task_name)

            # If not found, we add the bookmark as it is
            if task_data is None:
                if compare is None:
                    self.root().session().log_info(f'[MyTasks]          - Task not found')
                if '/films' in oid:
                    data.update(dict(
                        entity_type='Shot',
                        entity_type_name=sequence_name,
                        entity_name=shot_name,
                        shot_frames=item['nb_frames']
                    ))
                elif '/asset_libs' in oid or '/asset_types' in oid:
                    data.update(dict(
                        entity_type='Asset',
                        entity_type_name=None,
                        entity_name=asset_name,
                    ))
            
            else:
                # Check if bookmark (task) was not already added during kitsu tasks part
                key_exist = next((key for key, data in document_cache.items() if data['task_id'] == task_data['id']), None)
                if key_exist:
                    if compare is None:
                        self.root().session().log_info(f'[MyTasks]          - Task already fetched')
                    document_cache[key_exist]['task_oid'] = oid
                    document_cache[key_exist]['dft_task_name'] = task_name
                    document_cache[key_exist]['is_bookmarked'] = True
                    continue
                
                if compare is None:
                    self.root().session().log_info(f'[MyTasks]          - Task found')

                # Update base values
                data.update(dict(
                    task_id=task_data['id'], 
                    task_type=task_data['task_type']['name'],
                    task_status=task_data['task_status']['short_name'],
                    entity_id=task_data['entity_id'],
                    entity_name=task_data['entity']['name'],
                    entity_description=task_data['entity']['description'],
                    updated_date=task_data['updated_at'],
                ))

                # Get task status color
                task_status_data = self._action.kitsu.gazu_api.get_task_status(short_name=task_data['task_status']['short_name'])
                data.update(dict(
                    task_status_color=task_status_data["color"]
                ))

                # Get task comments
                data.update(dict(
                    task_comments=self._action.kitsu.gazu_api.get_all_comments_for_task(task_data['id'])
                ))

                # Set specific values based on entity type
                if task_data['task_type']['for_entity'] == "Shot":
                    data.update(dict(
                        entity_type=task_data['entity_type']['name'],
                        entity_type_name=task_data['sequence']['name'],
                        shot_frames=item['nb_frames']
                    ))
                elif task_data['task_type']['for_entity'] == "Asset":
                    # Add additional data if project is a tvshow
                    if kitsu_project_type == 'tvshow':
                        if item['source_id']:
                            episode_data = gazu.shot.get_episode(item['source_id'])
                            episode_name = episode_data['name']
                        else:
                            # Get main pack syntax from asset libs
                            asset_libs_names = self.root().project().asset_libs.mapped_names()
                            match = [name for name in asset_libs_names if re.match('main_pack', name, re.IGNORECASE)]
                            episode_name = match[0] if match else 'main_pack'
                        
                        data.update(dict(episode_name=episode_name))

                    data.update(dict(
                        category=task_data['entity']['data']['category'],
                        entity_type=task_data['task_type']['for_entity'],
                        entity_type_name=task_data['entity_type']['name'],
                    ))

                # Set primary files
                data['primary_files'] = self.root().session().cmds.Flow.call(
                    oid, 'get_primary_files', {}, {}
                )

            i = len(document_cache) + 1
            document_cache['task'+str(i)] = data

    def find_default_task(self, task_type, compare_mode):
        dft_tasks = self._action.task_mgr.default_tasks.mapped_items()
        if compare_mode is None:
            self.root().session().log_info('[MyTasks]       - Searching for corresponding task')
        task_name = next((
            task.name() 
            for task in dft_tasks
            if task_type in task.kitsu_tasks.get()
            or task_type.lower() == task.name()
            ), None
        )
        if compare_mode is None:
            if task_name:
                self.root().session().log_info('[MyTasks]           - Task found')
            else:
                self.root().session().log_info('[MyTasks]           - Task not found')

        return task_name if task_name else None

    def set_task_oid(self, data, compare_mode):
        if compare_mode is None:
            self.root().session().log_info('[MyTasks]       - Searching for corresponding entity')
        
        kitsu_project_type = self._action.kitsu.project_type.get()
        
        # Set current project in the oid
        resolved_oid = self.root().project().oid()
        primary_files = None

        # Set values based on entity type
        if data['entity_type'] == 'Shot':
            # Use episode name for film entity if project is a tvshow
            if kitsu_project_type == 'tvshow':
                resolved_oid += '/films/{episode_name}'.format(
                    episode_name=data['episode_name'],
                )
            # Use project name
            else:
                project_name = self.root().project().name()
                resolved_oid += '/films/{project_name}'.format(
                    project_name=project_name,
                )
            resolved_oid += '/sequences/{sequence_name}/shots/{shot_name}'.format(
                sequence_name=data['entity_type_name'],
                shot_name=data['entity_name']
            )
        elif data['entity_type'] == 'Asset':
            if kitsu_project_type == 'tvshow':
                resolved_oid += '/asset_libs/{episode_name}/asset_types/{asset_type_name}/assets/{asset_name}'.format(
                    episode_name=data['episode_name'],
                    asset_type_name=data['entity_type_name'],
                    asset_name=data['entity_name']
                )
            else:
                resolved_oid += f'/asset_types/{data["entity_type_name"]}'

                # Set asset family level if category
                if 'category' in data:
                    resolved_oid += f'/asset_families/{data["category"]}'

                resolved_oid += f'/assets/{data["entity_name"]}'

        if data['dft_task_name'] is not None:
            resolved_oid += f"/tasks/{data['dft_task_name']}"
            if self.root().session().cmds.Flow.exists(resolved_oid):
                if compare_mode is None:
                    self.root().session().log_info('[MyTasks]           - Entity found')
                primary_files = self.root().session().cmds.Flow.call(
                    resolved_oid, 'get_primary_files', {}, {}
                )
            else:
                if compare_mode is None:
                    self.root().session().log_info('[MyTasks]           - Entity not found')
            
        return resolved_oid, primary_files

    def touch(self):
        self._document_cache = None
        super(MyTasksMap, self).touch()

    def _configure_child(self, child):
        child.task_id.set(self._document_cache[child.name()]['task_id'])
        child.task_type.set(self._document_cache[child.name()]['task_type'])
        child.task_status.set(self._document_cache[child.name()]['task_status'])
        child.task_status_color.set(self._document_cache[child.name()]['task_status_color'])
        child.task_comments.set(self._document_cache[child.name()]['task_comments'])
        child.task_oid.set(self._document_cache[child.name()]['task_oid'])
        child.entity_id.set(self._document_cache[child.name()]['entity_id'])
        child.entity_type.set(self._document_cache[child.name()]['entity_type'])
        child.entity_type_name.set(self._document_cache[child.name()]['entity_type_name'])
        child.entity_name.set(self._document_cache[child.name()]['entity_name'])
        child.entity_description.set(self._document_cache[child.name()]['entity_description'])
        child.shot_frames.set(self._document_cache[child.name()]['shot_frames'])
        child.dft_task_name.set(self._document_cache[child.name()]['dft_task_name'])
        child.primary_files.set(self._document_cache[child.name()]['primary_files'])
        child.is_bookmarked.set(self._document_cache[child.name()]['is_bookmarked'])
        if self._action.kitsu.project_type.get() == 'tvshow':
            child.episode_name.set(self._document_cache[child.name()]['episode_name'])

    def _fill_row_cells(self, row, item):
        row["Task"] = item.task_type.get()
        row["Status"] = item.task_status.get()
        row["Type"] = item.entity_type.get()
        row["Type Name"] = item.entity_type_name.get()
        row["Name"] = item.entity_name.get()


class MyTasksSettings(flow.Object):

    tasks               = flow.Child(MyTasksMap)
    task_statues_filter = flow.SessionParam([], PresetSessionValue)
    task_sorted         = flow.SessionParam(None, PresetSessionValue)
    tasks_expanded      = flow.SessionParam({}, PresetSessionValue)
    auto_expand         = flow.BoolParam(False)
    url_suffix          = flow.Param('my-tasks')
    hidden_asset_types  = flow.Param(['x'])
    hidden_tasks        = flow.Param(['FDT'])

    def check_default_values(self):
        self.task_statues_filter.apply_preset()
        self.task_sorted.apply_preset()
        self.tasks_expanded.apply_preset()

    def update_presets(self):
        self.task_statues_filter.update_preset()
        self.task_sorted.update_preset()
        self.tasks_expanded.update_preset()


class MyTasks(flow.Object):

    _settings = flow.Child(MyTasksSettings)

    def __init__(self, parent, name):
        super(MyTasks, self).__init__(parent, name)
        self.kitsu = self.root().project().admin.kitsu
        self.task_mgr = self.root().project().get_task_manager()
        self._settings.check_default_values()

    def get_tasks(self, force_update=False):
        if force_update:
            self._settings.tasks.touch()
        return self._settings.tasks.mapped_items()

    def compare(self):
        return self._settings.tasks.compare()

    def get_task_statutes(self, short_name):
        return self.kitsu.gazu_api.get_task_statutes(short_name)

    def get_task_status(self, short_name):
        return self.kitsu.gazu_api.get_task_status(short_name=short_name)

    def get_task_comments(self, task_id):
        return self.kitsu.gazu_api.get_all_comments_for_task(task_id)

    def get_server_url(self):
        url = self.kitsu.server_url.get()
        if url.endswith('/'):
            url = url[:-1]
        return url
    
    def get_url_suffix(self):
        return self._settings.url_suffix.get()
    
    def get_project_id(self):
        return self.kitsu.project_id.get()

    def get_project_oid(self):
        return self.root().project().oid()

    def get_project_fps(self):
        return self.kitsu.gazu_api.get_project_fps()

    def is_uploadable(self, file_name):
        return self.kitsu.is_uploadable(file_name)

    def set_task_status(self, task_id, task_status_name, comment, files):
        return self.kitsu.gazu_api.set_task_status(task_id, task_status_name, comment, files)

    def upload_preview(self, entity_id, task_name, task_status_name, file_path, comment):
        return self.kitsu.gazu_api.upload_preview(entity_id, task_name, task_status_name, file_path, comment)

    def toggle_bookmark(self, oid):
        bookmarks = self.root().project().get_user().bookmarks

        if bookmarks.has_bookmark(oid):
            self.root().session().log_debug("Remove %s to bookmarks" % oid)
            bookmarks.remove_bookmark(oid)
            return False
        else:
            self.root().session().log_debug("Add %s to bookmarks" % oid)
            bookmarks.add_bookmark(oid)
            return True

    def _fill_ui(self, ui):
        ui["custom_page"] = "libreflow.baseflow.ui.mytasks.mytasks.MyTasksPageWidget"
