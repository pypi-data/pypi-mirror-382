import os
import shutil
import re
import pprint

from kabaret import flow


class FileItem(flow.Object):

    file_path             = flow.SessionParam()
    file_name             = flow.SessionParam()
    file_match_name       = flow.SessionParam()
    file_extension        = flow.SessionParam()
    file_status           = flow.SessionParam()

    with flow.group("Entities"):
        film_name         = flow.SessionParam()
        sequence_name     = flow.SessionParam()
        shot_name         = flow.SessionParam()
        asset_lib_name    = flow.SessionParam()
        asset_type_name   = flow.SessionParam()
        asset_family_name = flow.SessionParam()
        asset_name        = flow.SessionParam()
        task_name         = flow.SessionParam()

    file_version          = flow.SessionParam()
    file_target_oid       = flow.SessionParam()
    file_target_format    = flow.SessionParam()
    file_comment          = flow.SessionParam()
    entities_to_create    = flow.SessionParam()

    _action               = flow.Parent(3)

    def check_revision(self):
        try:
            task = self.root().get_object(self.file_target_oid.get())
        except flow.exceptions.MappedNameError:
            return self.file_version.set('v001')
        
        f = None
        rev = None
        name = None
        ext = None

        if self.file_extension.get():
            name, ext = os.path.splitext(self.file_match_name.get())

            if task.files.has_file(name, ext[1:]):
                f = task.files[re.sub('[\s.-]', '_', self.file_match_name.get())]
                rev = f.get_head_revision()
        else:
            name = self.file_match_name.get()

            if task.files.has_folder(self.file_match_name.get()):
                f = task.files[re.sub('[\s.-]', '_', self.file_match_name.get())]
                rev = f.get_head_revision()

        if f is None or rev is None:
            return self.file_version.set('v001')
        
        ver = int(rev.name().strip('v'))
        ver = f'v{(ver + 1):03}'
        return self.file_version.set(ver)


class FilesMap(flow.Map):

    @classmethod
    def mapped_type(cls):
        return FileItem

    def columns(self):
        return ["Name", "Target OID", "Revision"]

    def _fill_row_cells(self, row, item):
        row["Name"]       = item.file_name.get()
        row["Target OID"] = item.file_target_oid.get()
        row["Revision"]   = item.file_version.get()


class ImportFilesSettings(flow.Object):

    files_map              = flow.Child(FilesMap)
    upload_revision        = flow.BoolParam(False)

    with flow.group("Regex"):
        file_regex         = flow.Param('({name}).*?({ext})$').ui(label='File')
        folder_regex       = flow.Param('{name}').ui(label='Folder')
        film_regex         = flow.Param('{name}').ui(label='Film')
        sequence_regex     = flow.Param('(sq).*?([1-9]\d*)').ui(label='Sequence')
        shot_regex         = flow.Param('(sh).*?([1-9]\d*)').ui(label='Shot')
        asset_lib_regex    = flow.Param('{name}').ui(label='Asset lib')
        asset_type_regex   = flow.Param('^{name}').ui(label='Asset type')
        asset_family_regex = flow.Param('(?<={asset_type}_){name}').ui(label='Asset family')
        asset_regex        = flow.Param('(?<={asset_prev_entity}_).*(?=_{match_file})').ui(label='Asset')
    
    use_main_film          = flow.BoolParam(True)
    lowercase_for_task     = flow.BoolParam(False).ui(label='Use lowercase for task')


class ImportFilesAction(flow.Action):

    ICON = ('icons.gui', 'file')

    # Attributes for From Task Mode
    paths = flow.SessionParam([]).ui(hidden=True)
    source_task = flow.SessionParam('').ui(hidden=True)

    settings = flow.Child(ImportFilesSettings)

    def __init__(self, parent, name):
        super(ImportFilesAction, self).__init__(parent, name)
        self.kitsu = self.root().project().admin.kitsu
        self.task_mgr = self.root().project().get_task_manager()
        self.session = self.root().session()

        if self.get_project_type() == 'tvshow':
            self.settings.use_main_film.set(False)

    def allow_context(self, context):
        return context

    def get_project_type(self):
        return self.kitsu.project_type.get()

    def resolve_paths(self, paths):
        for path in paths:
            # Find matching file
            file_name = os.path.basename(path)
            match_file, task_names = self.resolve_file(file_name)

            # If the action was started from a task,
            # there is no need to resolve entities
            target_oid = None
            match_dict = None
            if self.source_task.get():
                target_oid = self.source_task.get()
            else:
                match_dict = self.resolve_entities(file_name, match_file)

            # Create item
            index = len(self.settings.files_map.mapped_items())
            item = self.settings.files_map.add(f'file{index+1}')

            # Set values
            item.file_path.set(path)
            item.file_name.set(file_name)
            item.file_match_name.set(match_file)
            item.file_extension.set(os.path.splitext(file_name)[1] if os.path.isfile(path) else None)

            item.film_name.set(
                match_dict['film'] if match_dict
                else self.get_entity_from_oid(target_oid, 'films')
            )
            item.sequence_name.set(
                match_dict['sequence'] if match_dict
                else self.get_entity_from_oid(target_oid, 'sequences')
            )
            item.shot_name.set(
                match_dict['shot'] if match_dict
                else self.get_entity_from_oid(target_oid, 'shots')
            )
            item.asset_lib_name.set(
                match_dict.get('asset_lib', None) if match_dict
                else self.get_entity_from_oid(target_oid, 'asset_libs')
            )
            item.asset_type_name.set(
                match_dict['asset_type'] if match_dict
                else self.get_entity_from_oid(target_oid, 'asset_types')
            )
            item.asset_family_name.set(
                match_dict['asset_family'] if match_dict
                else self.get_entity_from_oid(target_oid, 'asset_families')
            )
            item.asset_name.set(
                match_dict['asset'] if match_dict
                else self.get_entity_from_oid(target_oid, 'assets')
            )
            item.task_name.set(
                self.get_entity_from_oid(target_oid, 'tasks') if target_oid
                else task_names
            )
            item.file_target_oid.set(target_oid if target_oid else self.set_target_oid(item))

            # Define status
            
            # Valid if we know the matching file,
            # have all shot or asset data,
            # and one target task possible

            status = True
            shot_attr = [
                item.film_name.get(),
                item.sequence_name.get(),
                item.shot_name.get()
            ]
            asset_attr = [
                item.asset_type_name.get(),
                item.asset_name.get()
            ]
            if self.get_project_type() == 'tvshow':
                asset_attr.append(item.asset_lib_name.get())
            
            if (
                match_file is None

                or any([
                    all(value is not None for value in shot_attr),
                    all(value is not None for value in asset_attr)
                ]) is False

                or (
                    type(item.task_name.get()) is list
                    and len(item.task_name.get()) > 1
                )
            ):
                status = False

            item.file_status.set(status)

    def resolve_file(self, file_name):
        self.session.log_info(f'[Import Files] Resolving {file_name}')

        match_file = None
        possible_tasks = None
        for dft_file, task_names in self.task_mgr.default_files.get().items():
            name, ext = os.path.splitext(dft_file)

            # Use correct regex based on type
            regexp = self.settings.file_regex.get().format(
                name=name,
                ext=ext
            ) if ext else self.settings.folder_regex.get().format(name=name)

            match = re.search(regexp, file_name)
            if match:
                self.session.log_info(f'[Import Files] Find matching file ({dft_file})')
                match_file = dft_file
                # Switch to string if there is only one task
                if len(task_names) == 1:
                    possible_tasks = task_names[0]
                    self.session.log_info(f'[Import Files] Find matching task ({possible_tasks})')
                else:
                    possible_tasks = task_names
                break

        return match_file, possible_tasks

    def resolve_entities(self, file_name, match_file):
        pattern_dict = dict(
            film=self.settings.film_regex.get(),
            sequence=self.settings.sequence_regex.get(),
            shot=self.settings.shot_regex.get(),
            asset_type=self.settings.asset_type_regex.get(),
            asset_family=self.settings.asset_family_regex.get(),
            asset=self.settings.asset_regex.get()
        )

        match_dict = dict(
            film=None,
            sequence=None,
            shot=None,
            asset_type=None,
            asset_family=None,
            asset=None
        )

        base_entities = ['film', 'asset_type']
        entity_names = ['sequence', 'shot', 'asset_family', 'asset']

        if self.get_project_type() == 'tvshow':
            pattern_dict.update(dict(asset_lib=self.settings.asset_lib_regex.get()))
            match_dict.update(dict(asset_lib=None))
            base_entities = ['asset_lib' if name == 'asset_type' else name for name in base_entities]
            entity_names = ['asset_type' if name == 'asset_family' else name for name in entity_names]

        for key, pattern in pattern_dict.items():
            # For base entity (film and asset type)
            if key in base_entities:
                if key == 'film':
                    map_items = self.root().project().films.mapped_items()
                elif key == 'asset_lib':
                    map_items = self.root().project().asset_libs.mapped_items()
                else:
                    map_items = self.root().project().asset_types.mapped_items()

                for item in reversed(map_items):
                    regexp = pattern.format(name=item.name())

                    match = re.search(regexp, file_name)
                    if match:
                        self.session.log_info(f'[Import Files] Find matching {key} ({match.group(0)})')
                        match_dict[key] = match.group(0)
                        break

                # Set main film if parameter enabled
                if (
                    key == 'film'
                    and match_dict[key] is None
                    and self.settings.use_main_film.get()
                ):
                    match_dict[key] = self.root().project().films.mapped_items()[0].name()

            # For sequence, shot and asset
            if key in ('sequence', 'shot', 'asset_family', 'asset'):
                regexp = pattern

                # Exception for asset_family and asset
                if key == 'asset_family':
                    if match_dict['asset_type'] is not None:
                        asset_type = self.root().project().asset_types[match_dict['asset_type']]

                        if len(asset_type.asset_families.mapped_items()) > 1:
                            map_items = asset_type.asset_families.mapped_items()

                            for item in reversed(map_items):
                                regexp = pattern.format(
                                    asset_type=match_dict['asset_type'],
                                    name=item.name()
                                )

                                match = re.search(regexp, file_name)
                                if match:
                                    self.session.log_info(f'[Import Files] Find matching {key} ({match.group(0)})')
                                    match_dict[key] = match.group(0)
                                    break
                            
                            if match_dict[key]:
                                continue
                        else:
                            continue
                    else:
                        continue
                elif key == 'asset':
                    if match_dict['asset_family'] is not None or match_dict['asset_type'] is not None:
                        regexp = pattern.format(
                            asset_prev_entity=match_dict['asset_family'] or match_dict['asset_type'],
                            match_file=match_file
                        )
                    else:
                        # Use asset collection to find
                        asset_collection = self.root().project().get_entity_manager().get_asset_collection().collection_name()
                        asset_collection = self.root().project().get_entity_store().get_collection(asset_collection)

                        regexp = f'.+(?=_{match_file})' # Split matching file
                        
                        match = re.search(regexp, file_name)
                        if match:
                            asset_name = match.group(0)

                            query_filter = {
                                'name': {'$regex': f'^{self.get_project_oid()}.*{asset_name}',
                                '$options': 'i'}
                            }
                            cursor = asset_collection.find(query_filter)
                            name_and_doc = [(i["name"], i) for i in cursor]

                            if name_and_doc:
                                if len(name_and_doc) == 1:
                                    oid = name_and_doc[0][0]

                                    match_dict['asset_type'] = re.search('(?<=asset_types\/)[^\/]*', oid).group(0)
                                    self.session.log_info(f'[Import Files] Find matching asset_type ({match_dict["asset_type"]})')

                                    # Check for Asset Family
                                    regexp = '(?<=asset_families\/)[^\/]*'
                                    match = re.search(regexp, oid)

                                    if match:
                                        match_dict['asset_family'] = match.group(0)
                                        self.session.log_info(f'[Import Files] Find matching asset_family ({match_dict["asset_family"]})')
                                    
                                match_dict['asset'] = asset_name
                                self.session.log_info(f'[Import Files] Find matching asset ({match_dict["asset"]})')
                                
                                continue

                        continue

                match = re.search(regexp, file_name)
                if match:
                    self.session.log_info(f'[Import Files] Find matching {key} ({match.group(0)})')
                    match_dict[key] = match.group(0)

        return match_dict

    def get_project_oid(self):
        return self.root().project().oid()
    
    def get_entity_from_oid(self, target_oid, entity_type):
        match = re.search(f'(?<={entity_type}\/)[^\/]*', target_oid)
        return match.group(0) if match else None

    def set_target_oid(self, item):
        film_flow = ['film', 'sequence', 'shot', 'task']
        if self.get_project_type() == 'tvshow':
            asset_flow = ['asset_lib', 'asset_type', 'asset', 'task']
        else:
            asset_flow = ['asset_type', 'asset_family', 'asset', 'task']

        target_oid = self.get_project_oid()

        # Use the correct flow
        flow_to_use = asset_flow if item.asset_type_name.get() else film_flow

        for entity in flow_to_use:
            # Stop resolve if unknown value
            if getattr(item, entity+"_name").get() is None:
                if entity == 'asset_family':
                    continue
                else:
                    break

            # Try to get task if entity exists
            if entity == 'task' and type(getattr(item, entity+"_name").get()) is list:
                try:
                    o = self.root().get_object(target_oid)
                    tasks = [
                        task.name()
                        for task in o.tasks.mapped_items()
                        if task.name() in item.task_name.get()
                    ]
                    
                    if len(tasks) == 1:
                        item.task_name.set(tasks[0])
                        self.session.log_info(f'[Import Files] Find matching task ({tasks[0]})')
                    else:
                        break
                except flow.exceptions.MappedNameError:
                    break

            map_name = entity
            if entity != 'asset_family':
                map_name += 's'
            else:
                map_name = 'asset_families'
            
            target_oid += f'/{map_name}/{getattr(item, entity+"_name").get()}'
        
        return target_oid

    def get_map_oid(self, target_oid, entity_type):
        match = re.search(f'.+(?<=\/{entity_type})', target_oid)
        return match.group(0) if match else None

    def set_path_format(self, item, task_name, file_name):
        dft_file = None

        dft_task = self.check_default_task(task_name)
        
        file_object_name = file_name.replace('.', '_')

        if dft_task and dft_task.files.has_mapped_name(file_object_name):
            dft_file = dft_task.files[file_object_name]
        

        entity = dft_file if dft_file else dft_task if dft_task else None
        path_format = entity.path_format.get() if entity else None
        
        item.file_target_format.set(path_format)

    def check_default_task(self, task_name):
        dft_task = None
        if self.task_mgr.default_tasks.has_mapped_name(task_name):
            dft_task = self.task_mgr.default_tasks[task_name]
        
        return dft_task

    def import_files(self, items):
        for item in items:
            self.session.log_info(f'[Import Files] Import started for {item.file_name.get()}')

            if item.entities_to_create.get():
                self.create_entities(item)

            task_entity = self.root().get_object(item.file_target_oid.get())

            file_entity = None
            if item.file_extension.get():
                if task_entity.files.has_file(
                    os.path.splitext(item.file_match_name.get())[0], item.file_extension.get()[1:]
                ):
                    file_entity = task_entity.files[re.sub('[\s.-]', '_', item.file_match_name.get())]
            else:
                if task_entity.files.has_folder(
                    item.file_match_name.get()
                ):
                    file_entity = task_entity.files[re.sub('[\s.-]', '_', item.file_match_name.get())]

            if file_entity is None:
                if item.file_extension.get():
                    file_entity = task_entity.files.add_file(
                        os.path.splitext(item.file_match_name.get())[0],
                        item.file_extension.get()[1:],
                        tracked=True,
                        default_path_format=item.file_target_format.get()
                    )
                    self.session.log_info(f'[Import Files] File created')
                else:
                    file_entity = task_entity.files.add_folder(
                        item.file_match_name.get(),
                        tracked=True,
                        default_path_format=item.file_target_format.get()
                    )
                    self.session.log_info(f'[Import Files] Folder created')

            revision = self.create_revision(file_entity)
            revision_path = revision.get_path()
            revision_name = revision.name()

            if item.file_comment.get() != '':
                revision.comment.set(item.file_comment.get())

            if item.file_extension.get():
                shutil.copy2(item.file_path.get(), revision_path)
            else:
                shutil.copytree(item.file_path.get(), revision_path)

            self.session.log_info(f'[Import Files] Revision created')

            if self.settings.upload_revision.get():
                self.upload_revision(revision)

            self.settings.files_map.remove(item.name())

        self.session.log_info(f'[Import Files] All files has been imported!')

    def create_entities(self, item):
        for entity_type, data in item.entities_to_create.get().items():
            if entity_type == ('films' or 'asset_types'):
                if entity_type == 'films':
                    map_object = self.root().project().films
                else:
                    map_object = self.root().project().asset_types
            else:
                map_oid = self.get_map_oid(item.file_target_oid.get(), entity_type)
                map_object = self.root().get_object(map_oid)

            if entity_type == 'tasks':
                base_type = 'shot' if 'shots' in map_oid else 'asset'

                # Check if default task
                if self.check_default_task(data['name']) is None:
                    self.task_mgr.default_tasks.add_default_task(
                        data['name'],
                        data['display_name'],
                        base_type,
                        0
                    )
            
            if not map_object.has_mapped_name(data['name']):
                new_entity = map_object.add(data['name'])
                new_entity.display_name.set(data['display_name'])
                if entity_type == 'tasks':
                    new_entity.enabled.set(True)
                
                map_object.touch()


    def create_revision(self, f):
        r = f.add_revision()
        revision_path = r.get_path()
        f.last_revision_oid.set(r.oid())
        os.makedirs(os.path.dirname(revision_path), exist_ok=True)

        return r

    def upload_revision(self, revision):
        current_site = self.root().project().get_current_site()
        job = current_site.get_queue().submit_job(
            job_type='Upload',
            init_status='WAITING',
            emitter_oid=revision.oid(),
            user=self.root().project().get_user_name(),
            studio=current_site.name(),
        )

        self.root().project().get_sync_manager().process(job)

    def _fill_ui(self, ui):
        ui['custom_page'] = 'libreflow.baseflow.ui.importfiles.ImportFilesWidget'
