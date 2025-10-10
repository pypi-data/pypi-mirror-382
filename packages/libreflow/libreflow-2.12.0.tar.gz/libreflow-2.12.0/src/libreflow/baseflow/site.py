import os
import sys
import gazu
import time
import timeago
from datetime import datetime, timedelta
import subprocess
import platform
from minio import Minio
from ..scripts.minio_progress import Progress
import zipfile
import fnmatch
import re
import traceback
import tempfile
import uuid
from pathlib import Path

from kabaret import flow
from kabaret.flow_contextual_dict import ContextualView, get_contextual_dict
from kabaret.subprocess_manager.flow import RunAction
from kabaret.flow_entities.entities import EntityCollection, Entity, Property, PropertyValue

from ..utils.os import zip_folder, unzip_archive
from ..utils.kabaret.flow_entities.entities import CustomEntity, CustomEntityCollection, PropertyChoiceValue

from .dependency import get_dependencies
from .maputils import ItemMap, CreateGenericAction, ClearMapAction, RemoveGenericAction, SimpleCreateAction
from .runners import Runner, PythonRunner
from .users import PresetSessionValue


class SiteTypeChoiceValue(PropertyChoiceValue):

    CHOICES = ['Studio', 'User']


class SiteTypeSessionChoiceValue(flow.values.SessionValue):

    CHOICES = ['Studio', 'User']

    def choices(self):
        return self.__class__.CHOICES


class ExchangeSiteChoiceValue(flow.values.ChoiceValue):

    def choices(self):
        return self.root().project().get_exchange_sites().mapped_names()


class StaticSiteSyncStatusChoices(flow.values.ChoiceValue):
    CHOICES = ['NotAvailable', 'Requested', 'Available']


class StaticSiteSyncTransferStateChoices(flow.values.ChoiceValue):
    CHOICES = ['NC', 'UP_REQUESTED', 'DL_REQUESTED', 'UP_IN_PROGRESS', 'DL_IN_PROGRESS']


class LoadType(PropertyValue):

    DEFAULT_EDITOR = 'choice'
    CHOICES = ['Upload', 'Download']

    def choices(self):
        return self.CHOICES


class JobStatus(PropertyValue):

    DEFAULT_EDITOR = 'choice'
    CHOICES = ['WFA', 'WAITING', 'PROCESSING', 'PROCESSED', 'ERROR', 'PAUSE', 'DONE']

    def choices(self):
        return self.CHOICES


class ResetJob(flow.Action):
    """Reset one job.

    Return an error if the file doesn't exist on the exchange server

    """
    # ICON = ('icons.libreflow', 'reset')

    _job = flow.Parent()
    _jobs = flow.Parent(2)

    def needs_dialog(self):
        """Indicate whether this action requires a dialog to be displayed.
        
        Returns:
            bool: True if job type equal upload, revision status equal Available and revision is valid.
            
        """
        rev = self._job.get_related_object()
        return self._job.type.get() == 'Upload' \
            and rev is not None \
            and rev.get_sync_status(exchange=True) == 'Available'

    def allow_context(self, context):
        """Check whether the given context is valid for running the action.
        
        Args:
            context: Context object, usually representing the current project/task.
        
        Returns:
            bool: True if context valid and job status equal ERROR, otherwhise False.
            
        """
        return context and self._job.status.get() == 'ERROR'

    def get_buttons(self):
        """Return the buttons displayed in the dialog.
        
        Returns:
            list[str]: list of button labels, typically ['Confirm', 'Cancel'].
            
        """
        self.message.set((
            '<h3>Revision already on the exchange server</h3>'
            'Reset upload job anyway ?'
        ))
        return ['Confirm', 'Cancel']

    def _is_file_exchange_server(self, revision):
        """Check if a file exist in the exchange server.

        Args:
            revision (Revision): revision of the file

        Returns:
            bool: True if file exist otherwise False.

        """
        exchange = self.root().project().get_exchange_site()
        bucket_name = exchange.bucket_name.get()
        minio_client = exchange.sync_manager._ensure_client()
        path = Path(revision.get_path(relative=True)).as_posix()

        if path.is_dir():
            path = path + ".zip"

        # Check if object exists
        try:
            minio_client.stat_object(bucket_name, path)
        except Exception as error_msg:
            self.root().session().log_error(error_msg)
            self.root().session().log_info('DO NOT EXIST')
            revision.set_sync_status('NotAvailable', exchange=True)
            return False

        return True

    def run(self, button):
        """Execute the render action.

        Args:
            button (str): The label of the button pressed by the user (e.g., 'Confirm' or 'Cancel').

        Returns:
            Any: the result of the parent run method if executed, or None if canceled.

        """
        if button == "Cancel":
            return None

        self._job.status.set("WAITING")
        self._job.log.set("?")
        rev = self._job.get_related_object()
        if rev is None:
            return self.get_result()

        self._is_file_exchange_server(rev)

        return None


class ResetJobs(flow.Action):

    ICON = ('icons.libreflow', 'reset')

    _jobs = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        if button == 'Cancel':
            return
        
        for j in self._jobs.jobs(status=['ERROR']):
            j.status.set('WAITING')
        
        self._jobs.touch()


class ShowRevisionInHistory(flow.Action):

    ICON = ("icons.gui", "ui-layout")

    _job = flow.Parent()

    def allow_context(self,context):
        return context

    def needs_dialog(self):
        return False

    def run(self, button):
        history_oid = self._job.emitter_oid.get() + '/../..'
        history_oid = self.root().session().cmds.Flow.resolve_path(history_oid)

        return self.get_result(goto=history_oid)


class Job(Entity):

    type                = Property(property_value_type=LoadType)
    status              = Property(property_value_type=JobStatus)
    priority            = Property().ui(editor='int')
    emitter_oid         = Property()
    path                = Property()
    date                = Property().ui(editor='datetime')
    date_end            = Property().ui(editor='datetime')
    is_archived         = Property().ui(editor='bool')
    requested_by_user   = Property()
    requested_by_studio = Property()
    log                 = Property().ui(editor='textarea')
    file_size           = Property()

    reset = flow.Child(ResetJob)
    show = flow.Child(ShowRevisionInHistory).ui(label='Show in history')
    _map = flow.Parent()

    def __repr__(self):
        if self._map._document_cache is None:
            self._map.mapped_names()
        name = self.name()
        job_repr = "%s(type=%s, status=%s, priority=%s, emitter=%s, date=%s, date_end=%s, is_archived=%s, requested_by_user=%s, requested_by_studio=%s)" % (
                self.__class__.__name__,
                self._map._document_cache[name]['type'],
                self._map._document_cache[name]['status'],
                self._map._document_cache[name]['priority'],
                self._map._document_cache[name]['emitter_oid'],
                self._map._document_cache[name]['date'],
                self._map._document_cache[name]['date_end'],
                self._map._document_cache[name]['is_archived'],
                self._map._document_cache[name]['requested_by_user'],
                self._map._document_cache[name]['requested_by_studio']
            )

        return job_repr
    
    def get_local_path(self):
        '''
        Returns the local path of the associated object.
        
        Note that the result depends on the current site
        since it includes the root folder of the latter.
        '''
        return os.path.join(
            self.root().project().get_root(),
            self.path.get()
        )
    
    def get_server_path(self):
        '''
        Returns the path of the associated object on the server.
        '''
        path = self.path.get()

        if os.path.splitext(path)[1] == '':
            path += '/' + os.path.basename(path) + '.zip'
        
        return path
    
    def get_related_object(self):
        try:
            o = self.root().get_object(
                self.emitter_oid.get()
            )
        except (ValueError, \
            flow.exceptions.MissingRelationError, \
            flow.exceptions.MappedNameError):
            o = None
        
        return o
    
    def check_valid_state(self):
        '''
        Returns a boolean meaning whether this job is ready
        to be processed or not.
        
        The method may update the job's properties to indicate
        why this job cannot yet be processed. It assumes that
        `emitter_oid` references a valid revision object.
        '''
        if self.status.get() != 'WAITING':
            return False
        
        o = self.get_related_object()
        if o is None:
            log_msg = "Revision does not exist"
            self.status.set('ERROR')
            self.log.set(log_msg)
            self.root().session().log_warning(log_msg)
            return False

        if self.type.get() == 'Download' and o.get_sync_status(exchange=True) != 'Available':
            log_msg = f"Revision {o.oid()} not yet available on exchange server"
            self.log.set(log_msg)
            self.root().session().log_debug(log_msg)
            return False
        
        return True
    
    def on_submitted(self):
        '''
        Method which may be called right after this job
        has been submitted to a queue.

        Its default behaviour is to compute the relative path
        of the job's requested revision (`emitter_oid`).
        If the oid does not refer to an existing revision
        object, the methods puts the job in error state.
        '''
        revision = self.get_related_object()
        
        if revision is None:
            self.status.set('ERROR')
            self.log.set('Object does not exist')
            return
        
        try:
            ready_for_sync = revision.ready_for_sync.get()
            path = revision.get_path(relative=True).replace('\\', '/')
        except AttributeError:
            self.status.set('ERROR')
            self.log.set('Object is not a revision')
            return
        else:
            if not ready_for_sync:
                self.status.set('ERROR')
                self.log.set('Revision is not ready to be synced')
                return
        
        if revision.file_size.get() is not None :
            self.file_size.set(revision.file_size.get())
        
        self.path.set(path)
    
    def on_processed(self):
        '''
        Method which may be called right after this job
        has been processed.

        Its default behaviour is to update the related
        revision statutes. The method assumes that
        `emitter_oid` references a valid revision object.
        '''
        self.status.set('PROCESSED')
        self.date_end.set(time.time())

        self.root().project().get_current_site().set_sync_date()
        revision = self.root().get_object(
            self.emitter_oid.get()
        )
        revision.set_sync_status(
            'Available',
            exchange=(self.type.get() == 'Upload')
        )
        revision.touch()
        revision._revisions.touch()

class RemoveOutdatedJobs(flow.Action):

    _map = flow.Parent()

    def allow_context(self,context):
        return context

    def needs_dialog(self):
        self.message.set(f'Removing outdated jobs...')
        return True
    
    def get_buttons(self):

        count=0

        for job in self._map.mapped_items():

            if job.status.get() == 'WAITING' or job.status.get() == 'ERROR':

                self.root().session().log_info(f'[RemoveOutdatedJobs] Checking entity: {job.emitter_oid.get()}')

                if self.root().session().cmds.Flow.exists(job.emitter_oid.get()):
                
                    rev = self.root().get_object(job.emitter_oid.get())
                    file = self.root().get_object(re.search('.+(?=\/history)', job.emitter_oid.get()).group(0))
                    latest_rev = file.get_head_revision()

                    if (rev.get_sync_status(site_name=job.requested_by_studio.get()) == 'NotAvailable' 
                        or rev.get_sync_status(site_name=job.requested_by_studio.get()) == 'Requested'):

                        latest_rev.sync_statutes.touch()
                        if latest_rev.get_sync_status() == 'Available':

                            # if job.status.get() == 'ERROR' and 'empty revision' not in rev.comment.get() :
                            #     continue

                            self.root().session().log_info(f'[RemoveOutdatedJobs] Removing Job')
                            count+=1
                            self._map.delete_entities([job.name()])
                    
                    # elif file.file_type.get() == 'Outputs' and '_CYCLE' in job.emitter_oid.get():
                    #     self.root().session().log_info(f'[RemoveOutdatedJobs] Removing Job')
                    #     count+=1
                    #     self._map.delete_entities([job.name()])

                else : 
                    self.root().session().log_info(f'[RemoveOutdatedJobs] Removing Job')
                    count+=1
                    self._map.delete_entities([job.name()])

        self.message.set(f'Removed {count} jobs')
        return ['OK']

    def run(self,button):
        if button == 'OK':
            return

class ClearQueueJobStatus(flow.values.ChoiceValue):

    CHOICES = JobStatus.CHOICES + ["All"]


class ClearQueueLoadType(flow.values.ChoiceValue):

    CHOICES = LoadType.CHOICES + ["All"]


class ClearQueueAction(flow.Action):

    _site = flow.Parent(3)
    status = flow.Param("PROCESSED", ClearQueueJobStatus)
    type = flow.Param("All", ClearQueueLoadType)
    emitted_before = flow.SessionParam((datetime.now() - timedelta(days=1)).timestamp()).ui(
        editor='datetime'
    )

    def get_buttons(self):
        self.message.set(
            "<h2>Clear %s jobs</h2>" % self._site.name()
        )
        return ["Clear", "Cancel"]
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        queue = self._site.get_queue()
        status = self.status.get()
        type = self.type.get()

        if status == "All" and type == "All":
            queue.clear()
        else:
            for job in queue.jobs(status=[self.status.get()]):
                if job.date.get() < self.emitted_before.get():
                    queue.delete_entities([job.name()])
                    self.root().session().log_info(f'[Clear Queue] Deleted {job.oid()}')

        queue.touch()

class JobQueue(EntityCollection):

    reset_jobs = flow.Child(ResetJobs).ui(label='Reset erroneous jobs')
    remove_outdated_jobs = flow.Child(RemoveOutdatedJobs)
    clear_queue = flow.Child(ClearQueueAction)

    _queue = flow.Parent()
    _site = flow.Parent(2)

    @classmethod
    def mapped_type(cls):
        return Job
    
    def summary(self):
        # Jobs count
        all_jobs_count = f'{self._site.count_jobs()} Jobs in queue'
        processed_count = f'<font color="#61f791">{self._site.count_jobs(status="PROCESSED")} PROCESSED</font>'
        waiting_count = f'<font color="#EFDD5B">{self._site.count_jobs(status="WAITING")} WAITING</font>'
        error_count = f'<font color="#ff5842">{self._site.count_jobs(status="ERROR")} ERROR</font>'

        message = f'{all_jobs_count} / {processed_count} - {waiting_count} - {error_count}'

        # Latest sync dates
        if self._queue.last_auto_sync.get():
            date = datetime.fromtimestamp(self._queue.last_auto_sync.get())
            full_date = date.strftime('%Y-%m-%d %H:%M:%S')
            nice_date = timeago.format(full_date, datetime.now())

            message += f'<br>Last auto sync: {full_date} ({nice_date})</br>'

        if self._queue.last_manual_sync.get():
            date = datetime.fromtimestamp(self._queue.last_manual_sync.get())
            full_date = date.strftime('%Y-%m-%d %H:%M:%S')
            nice_date = timeago.format(full_date, datetime.now())

            message += f'<br>Last manual sync: {full_date} ({nice_date})</br>'

        return message

    def get_next_waiting_job(self):
        for job in reversed(self.mapped_items()):
            if job.status.get() == "WAITING":
                return job
        
        return None

    def list_users(self):
        coll = self.get_entity_store().get_collection(self.collection_name())
        cursor = coll.distinct('requested_by_user')
        return list(cursor)

    def jobs(self, to_dict=False, type=None, status=None, user=None):
        if type is None and status is None and to_dict is False:
            return self.mapped_items()

        job_filter = {}
        coll = self.get_entity_store().get_collection(self.collection_name())
        if type is not None:
            job_filter["type"] = {"$in": type}
        if status is not None:
            job_filter["status"] = {"$in": status}
        if user is not None:
            job_filter["requested_by_user"] = {"$in": user}
        cursor = coll.find(job_filter)
        if to_dict:
            return list(cursor)

        jobs = [self.get_mapped(d["name"]) for d in cursor]
        return jobs

    def count(self, type=None, status=None):
        job_filter = {}

        if type is not None:
            job_filter['type'] = type
        if status is not None:
            job_filter['status'] = status
        
        c = self.get_entity_store().get_collection(self.collection_name())

        return c.count_documents(job_filter)
    
    def submit_job(self,
            emitter_oid,
            user,
            studio,
            date_end=-1,
            job_type='Download',
            init_status='WAITING',
            priority=50
        ):
        
        name = '%s_%s_%s_%i' % (
            emitter_oid[1:].replace('/', '_'),
            studio,
            job_type,
            time.time()
        )
        c = self.get_entity_store().get_collection(
            self.collection_name())
        c.insert_one({
            "name": name,
            "type": job_type,
            "status": init_status,
            "priority": priority,
            "emitter_oid": emitter_oid,
            "date": time.time(),
            "date_end": date_end,
            "requested_by_user": user,
            "requested_by_studio": studio,
            "is_archived": False,
            "log": '?',
        })
        self._document_cache = None
        job = self.get_mapped(name)
        self.root().session().log_info("Submitted job %s" % job)
        self.touch()
        return job
    
    def columns(self):
        return [
            "Type",
            "Status",
            "Revision",
            "Emitted on",
            "By",
            "Site",
        ]
    
    def _fill_row_cells(self, row, item):
        self.mapped_names()
        item_data = self._document_cache[item.name()]

        row['Type']       = item_data['type']
        row['Status']     = item_data['status']
        row['Revision']   = item_data['emitter_oid']
        row['By']         = item_data['requested_by_user']
        row['Site']       = item_data['requested_by_studio']
        row['Emitted on'] = datetime.fromtimestamp(
            float(item_data['date'])
        ).ctime()


class ProcessJobs(flow.Action):

    def needs_dialog(self):
        return False

    def process(self, job):
        raise NotImplementedError(
            "Must be implemented to process the given job"
        )
    
    def _get_jobs(self):
        current_site = self.root().project().get_current_site()
        return current_site.get_jobs()
    
    def run(self, button):
        for job in self._get_jobs():
            self.root().session().log_info("Processing job %s" % job)
            self.process(job)
        # Refresh project's sync section UI
        self.root().project().synchronization.touch()


class MinioFileUploader(PythonRunner):
    
    def argv(self):
        args = ["%s/../scripts/minio_file_uploader.py" % (
            os.path.dirname(__file__)
        )]
        args += self.extra_argv
        return args


class MinioFileDownloader(PythonRunner):
    
    def argv(self):
        args = ["%s/../scripts/minio_file_downloader.py" % (
            os.path.dirname(__file__)
        )]
        args += self.extra_argv
        return args


class MinioUploadFile(flow.Object):

    def upload(self, local_path, server_path):
        self.root().session().log_info(
            "Uploading file %s -> %s" % (
                local_path,
                server_path
            )
        )
        exchange_site = self.root().project().get_exchange_site()
        minioClient = Minio(
            exchange_site.server_url.get(),
            access_key=exchange_site.server_login.get(),
            secret_key=exchange_site.server_password.get(),
            secure=True
        )

        minioClient.fput_object(
            exchange_site.bucket_name.get(),
            server_path,
            local_path,
            progress=Progress()
        )


class MinioDownloadFile(flow.Object):

    def download(self, server_path, local_path):
        self.root().session().log_info(
            "Downloading file %s -> %s" % (
                server_path,
                local_path
            )
        )
        exchange_site = self.root().project().get_exchange_site()
        minioClient = Minio(
            exchange_site.server_url.get(),
            access_key=exchange_site.server_login.get(),
            secret_key=exchange_site.server_password.get(),
            secure=True
        )
        
        tmp_path = self.root().project().get_temp_folder()

        if tmp_path is not None:
            tmp_name = os.path.splitext(os.path.basename(local_path))[0]
            tmp_path = os.path.join(tmp_path, tmp_name)

        minioClient.fget_object(
            exchange_site.bucket_name.get(),
            server_path,
            local_path,
            tmp_file_path=tmp_path,
            progress=Progress()
        )


class SyncManager(flow.Object):

    _exchange = flow.Parent()

    def __init__(self, parent, name):
        super(SyncManager, self).__init__(parent, name)
        self._client = None

    def upload(self, server_path, local_path, job_entity):
        zipped_folder = self._is_zipped_folder(
            server_path, local_path
        )
        if zipped_folder:
            # Folder to be zipped before upload
            src_path = self._get_temp_zip(server_path)
            zip_folder(local_path, src_path)
        else:
            # File/folder uploaded as is
            src_path = local_path

        self.root().session().log_info(
            f'Upload file {local_path} -> {server_path}'
        )
        self._ensure_client().fput_object(
            self._exchange.bucket_name.get(),
            server_path,
            src_path,
            progress=Progress(job_entity)
        )

        if zipped_folder:
            os.remove(src_path)

    def download(self, server_path, local_path, job_entity):
        zipped_folder = self._is_zipped_folder(
            server_path, local_path
        )
        if zipped_folder:
            dst_path = self._get_temp_zip(server_path)
        else:
            dst_path = local_path
        
        self.root().session().log_info(
            f'Download file {server_path} -> {local_path}'
        )
        self._ensure_client().fget_object(
            self._exchange.bucket_name.get(),
            server_path,
            dst_path,
            progress=Progress(job_entity)
        )

        if zipped_folder:
            unzip_archive(dst_path, local_path)
            os.remove(dst_path)
    
    def check_connection(self):
        try:
            self._ensure_client().list_buckets()
        except Exception as err:
            return str(err)
        else:
            return None

    def _ensure_client(self):
        if self._client is None:
            self._client = Minio(
                self._exchange.server_url.get(),
                access_key=self._exchange.server_login.get(),
                secret_key=self._exchange.server_password.get(),
                secure=self._exchange.enable_tls.get()
            )
        
        return self._client
    
    def _get_temp_zip(self, server_path):
        return os.path.join(
            self.root().project().get_temp_folder(),
            (
                pathlib.PurePath(server_path).stem
                + f'-{str(uuid.uuid4())}.zip'
            )
        )
    
    def _is_zipped_folder(self, server_path, local_path):
        return (
            os.path.splitext(local_path)[1] == ''
            and os.path.splitext(server_path)[1] == '.zip'
        )


class Synchronize(ProcessJobs):

    def _get_jobs(self):
        return self.root().project().get_current_site().get_jobs(
            status=['WAITING']
        )

    def process(self, job):
        if not job.check_valid_state():
            return
        job.on_submitted()
        try:
            job.status.set('PROCESSING')
            sync_manager = self.root().project().get_exchange_site().sync_manager
        
            if job.type.get() == 'Upload':
                sync_manager.upload(
                    job.get_server_path(),
                    job.get_local_path(),
                    job
                )
            else:
                sync_manager.download(
                    job.get_server_path(),
                    job.get_local_path(),
                    job
                )
        except Exception as e:
            job.status.set('ERROR')
            job.log.set(traceback.format_exc())


class ActiveSiteChoiceValue(flow.values.SessionValue):
    
    DEFAULT_EDITOR = 'choice'
    
    _choices = flow.SessionParam(None).ui(editor='set')

    def choices(self):
        if self._choices.get() is None:
            working_sites = self.root().project().get_working_sites()
            names = working_sites.get_site_names(use_custom_order=True, active_only=True)
            self._choices.set(names)
        
        return self._choices.get()


class ActiveSiteAutoSelectChoiceValue(ActiveSiteChoiceValue):
    
    def choices(self):
        choices = super(ActiveSiteAutoSelectChoiceValue, self).choices()
        choices = ['Auto select'] + choices.copy()
        
        return choices


class ActiveSiteRevisionAvailableChoiceValue(flow.values.ChoiceValue):
    
    DEFAULT_EDITOR = 'choice'
    
    _choices = flow.SessionParam(None).ui(editor='set')
    _revision = flow.Parent(2)
    
    exclude_choice = flow.SessionParam(None).ui(hidden=False)

    def choices(self):
        if self._choices.get() is None:
            working_sites = self.root().project().get_working_sites()
            choices = working_sites.get_site_names(use_custom_order=True, active_only=True)
            exclude_choice = self.exclude_choice.get()
            
            if exclude_choice is not None:
                try:
                    choices.remove(exclude_choice)
                except ValueError:
                    pass
            
            choices_available = []
            
            for site_name in choices:
                if self._revision.get_sync_status(site_name) == 'Available':
                    choices_available.append(site_name)
            
            self._choices.set(choices_available)
        
        return self._choices.get()


class SiteSelection(flow.Object):
    
    source_site = flow.Param(None, ActiveSiteAutoSelectChoiceValue).watched()
    target_site = flow.Param(None, ActiveSiteChoiceValue).watched()

    _action = flow.Parent()
    _revision = flow.Parent(2)
    
    def child_value_changed(self, child_value):
        if child_value in (self.source_site, self.target_site):
            self.touch()
    
    def summary(self):
        if (self.source_site.get() == self.target_site.get()) or (
            self.source_site.get() == "Auto select"
            and self.target_site.get() == self._revision.site.get()
        ):
            return '⚠️ Source and target sites can\'t be the same !'
        else:
            return ''


class RequestAs(flow.Action):

    _revision = flow.Parent()
    sites = flow.Child(SiteSelection).ui(expanded=True)
    priority = flow.IntParam(50)
    forced_upload = flow.SessionParam(False).ui(
        editor='bool',
        tooltip=('Ask the source site to upload the revision regardless'
                ' of its status on the exchange site.'))
    
    def get_buttons(self):
        self.sites.source_site.set(self.sites.source_site.choices()[0])
        target_site_choices = self.sites.target_site.choices()
        
        if not target_site_choices:
            msg = self.message.get()
            if msg is None:
                msg = ''
            
            msg += (
                '<h3><font color="#D5000D">Making requests is not possible since '
                'there is no other site defined for this project.</font></h3>'
            )
            self.message.set(msg)
            
            return ['Cancel']
        
        self.sites.target_site.set(target_site_choices[0])

        return ["Request", "Cancel"]
    
    def get_source_site_name(self):
        return self.sites.source_site.get()
    
    def get_target_site_name(self):
        return self.sites.target_site.get()
    
    def allow_context(self, context):
        return (
            context
            and not self._revision.is_working_copy()
            and self.root().project().get_current_site().request_files_from_anywhere.get()
        )

    def find_existing_job(self, job_queue, job_type, job_status, revision_oid):
        coll = job_queue.get_entity_store().get_collection(
            job_queue.collection_name())
        result = coll.find({'emitter_oid': revision_oid,
                            'type': job_type,
                            'status': job_status})
        return len(list(result)) != 0

    def run(self, button):
        if button == "Cancel":
            return
        
        source_site_name = self.get_source_site_name()
        target_site_name = self.get_target_site_name()
        if source_site_name == target_site_name:
            return self.get_result(close=False)

        # Get requesting and requested sites
        sites = self.root().project().get_working_sites()
        target_site = sites[target_site_name]
        job_exists = self.find_existing_job(target_site.get_queue(), \
            'Download', 'WAITING', self._revision.oid())
        if not job_exists:
            # Add a download job for the requesting site
            target_site.get_queue().submit_job(
                job_type="Download",
                init_status="WAITING",
                emitter_oid=self._revision.oid(),
                user=self.root().project().get_user_name(),
                studio=target_site_name,
                priority=self.priority.get(),
            )
        else:
            self.root().session().log_warning(
                "Revision already requested for download in target site")
        self._revision.set_sync_status("Requested", site_name=target_site_name)
        self._revision.touch()
        
        # Check if the version is not available on the exchange server
        revision_status = self._revision.get_sync_status(exchange=True)

        if revision_status == "Available" and not self.forced_upload.get():
            self.root().session().log_warning(
                "Revision already on the exchange server"
            )
            self.root().project().synchronization.touch()
            return self.get_result()
        
        # If enabled, automatically select source site
        if self.sites.source_site.get() == "Auto select":
            source_site_name = self._revision.site.get()
        
        source_site = sites[source_site_name]
        job_exists = self.find_existing_job(source_site.get_queue(), \
            'Upload', 'WAITING', self._revision.oid())
        if job_exists:
            self.root().session().log_warning(
                "Revision already requested for upload in source site")
            self.root().project().synchronization.touch()
            return self.get_result()

        # Add an upload job for the requested site
        source_site.get_queue().submit_job(
            job_type="Upload",
            init_status="WAITING",
            emitter_oid=self._revision.oid(),
            user=self.root().project().get_user_name(),
            studio=target_site_name,
            priority=self.priority.get(),
        )

        # Refresh project's sync section UI
        self.root().project().synchronization.touch()


class Request(RequestAs):

    ICON = ('icons.libreflow', 'request')

    source_site = flow.Param(None, ActiveSiteRevisionAvailableChoiceValue)
    priority = flow.IntParam(50)
    forced_upload = flow.SessionParam(False).ui(
        editor='bool',
        tooltip=('Ask the source site to upload the revision regardless'
                ' of its status on the exchange site.'))
    sites = flow.Child(SiteSelection).ui(hidden=True)

    _revision = flow.Parent()

    def get_buttons(self):
        self.source_site.exclude_choice.set(self.root().project().get_current_site().name())
        source_site_choices = self.source_site.choices()
        
        if not source_site_choices:
            msg = self.message.get()
            if msg is None:
                msg = ''
            
            msg += (
                '<h3><font color="#D5000D">Making requests is not possible since '
                'the revision isn\'t available on any site.</font></h3>'
            )
            self.message.set(msg)
            
            return ['Cancel']
        
        self.source_site.set(source_site_choices[0])

        return ['Request', 'Cancel']

    def needs_dialog(self):
        source_site_choices = self.source_site.choices()
        if len(source_site_choices) == 1:
            return False

        return True
    
    def get_source_site_name(self):
        return self.source_site.get()
    
    def get_target_site_name(self):
        return self.root().project().get_current_site().name()
    
    def allow_context(self, context):
        return (
            context
            and not self._revision.is_working_copy()
            and self._revision.get_sync_status() != "Available"
            and self._revision.get_sync_status(exchange=True) != "Available"
        )


class ResetJobStatuses(flow.Action):
    _site = flow.Parent()
    status = flow.Param("WAITING", JobStatus)

    def run(self, button):
        for job in self._site.get_jobs():
            job.status.set(self.status.get())
        
        self._site.get_queue().touch()


class CreateSite(flow.Action):

    ICON = ("icons.gui", "plus-sign-in-a-black-circle")

    _site_map = flow.Parent()
    site_name = flow.SessionParam("").ui(label="Name")

    def get_buttons(self):
        self.message.set("<h2>Create a site</h2>")
        return ["Create", "Cancel"]
    
    def run(self, button):
        if button == "Cancel":
            return
        
        site_name = self.site_name.get()

        if not site_name or self._site_map.has_mapped_name(site_name):
            if not site_name:
                msg = "Site name must not be empty."
            else:
                msg = f"Site {site_name} already exists."

            self.message.set((
                "<h2>Create a site</h2>"
                f"<font color=#D5000D>{msg}</font>"
            ))
            
            return self.get_result(close=False)

        site = self._site_map.add(site_name)
        self._site_map.touch()

        return self.get_result(next_action=site.configuration.oid())


class ConfigureSite(flow.Action):

    _site_map = flow.Parent(2)
    _site = flow.Parent()
    short_name = flow.SessionParam("").ui(label="Short name")
    description = flow.SessionParam("")

    def get_buttons(self):
        self.message.set(
            "<h2>Site <font color=#fff>%s</font></h2>" % self._site.name()
        )
        self._fill_action_fields()

        return ["Configure", "Cancel"]

    def _configure_site(self, site):
        '''
        This can be used by subclass to configure a mapped site.

        Default is to set site's short name and description.
        '''
        self._site.short_name.set(self.short_name.get())
        self._site.description.set(self.description.get())
    
    def _fill_action_fields(self):
        '''
        This can be used by subclass to fill action's parameters when
        dialog is displayed (e.g. to automatically show site parameters).

        Default is to fill site's short name and description.
        '''
        self.short_name.set(self._site.short_name.get())
        self.description.set(self._site.description.get())
    
    def allow_context(self, context):
        # Hide in map item submenus
        return False
    
    def run(self, button):
        if button == "Cancel":
            return
        
        self._configure_site(self._site)
        self._site.configured.touch()
        self._site_map.touch()


class ComputedBoolValue(flow.values.ComputedValue):

    DEFAULT_EDITOR = 'bool'


class Site(CustomEntity):

    short_name    = Property()
    code          = Property()
    description   = Property()
    configured    = flow.Computed().ui(editor='bool') # What a site needs to be considered configured
    configuration = flow.Child(ConfigureSite)

    is_active     = Property().ui(editor='bool')

    def compute_child_value(self, child_value):
        if child_value is self.configured:
            self.configured.set(True)
    
    def get_code(self):
        return self.code.get() or self.name()


class SiteMap(CustomEntityCollection):

    create_site = flow.Child(CreateSite)

    @classmethod
    def mapped_type(cls):
        return Site

    def mapped_names(self, page_num=0, page_size=None):
        names = super(SiteMap, self).mapped_names(page_num, page_size)
        if "default" not in names:
            names.insert(0, "default")
        return names
    
    def columns(self):
        return ["Site"]
    
    def get_site_names(self, use_custom_order=False, active_only=False, short_names=False):
        sites_data = self.root().project().admin.multisites.sites_data.get()
        
        if use_custom_order:
            current_site = self.root().project().get_current_site()
            names = current_site.ordered_site_names.get()
        else:
            names = self.mapped_names()

        site_names = []

        for name in names:
            data = sites_data[name]

            if active_only and not data['is_active']:
                continue
            
            if short_names:
                site_names.append(data['short_name'])
            else:
                site_names.append(name)
        
        return site_names
    
    def _get_mapped_item_type(self, mapped_name):
        if mapped_name == "default":
            return self.mapped_type()

        return super(SiteMap, self)._get_mapped_item_type(mapped_name)
    
    def _fill_row_cells(self, row, item):
        row["Site"] = item.name()
        if not item.configured.get():
            row["Site"] += " ⚠️"


class ConfigureWorkingSite(ConfigureSite):

    site_type = flow.SessionParam("Studio", SiteTypeSessionChoiceValue)

    root_windows_folder = flow.SessionParam("")
    root_linux_folder = flow.SessionParam("")
    root_darwin_folder = flow.SessionParam("")
    
    sync_dl_max_connections = flow.SessionParam(1)
    sync_up_max_connections = flow.SessionParam(1)
    
    def _fill_action_fields(self):
        super(ConfigureWorkingSite, self)._fill_action_fields()
        self.site_type.set(self._site.site_type.get())
        self.root_windows_folder.set(self._site.root_windows_folder.get())
        self.root_linux_folder.set(self._site.root_linux_folder.get())
        self.root_darwin_folder.set(self._site.root_darwin_folder.get())
        self.sync_dl_max_connections.set(self._site.sync_dl_max_connections.get())
        self.sync_up_max_connections.set(self._site.sync_up_max_connections.get())

    def _configure_site(self, site):
        super(ConfigureWorkingSite, self)._configure_site(site)
        site.site_type.set(self.site_type.get())
        site.root_windows_folder.set(self.root_windows_folder.get())
        site.root_linux_folder.set(self.root_linux_folder.get())
        site.root_darwin_folder.set(self.root_darwin_folder.get())
        site.sync_dl_max_connections.set(self.sync_dl_max_connections.get())
        site.sync_up_max_connections.set(self.sync_up_max_connections.get())


class Queue(flow.Object):

    job_list = flow.Child(JobQueue).ui(
        label="Jobs",
        expanded=True,
        default_height=600,
        show_filter=True)

    last_auto_sync = flow.Param().ui(editor='datetime', editable=False, hidden=True)
    last_manual_sync = flow.Param().ui(editor='datetime', editable=False, hidden=True)

    job_types_filter  = flow.SessionParam(None, PresetSessionValue)
    job_status_filter = flow.SessionParam(None, PresetSessionValue)

    def check_default_values(self):
        self.job_types_filter.apply_preset()
        self.job_status_filter.apply_preset()

    def update_presets(self):
        self.job_types_filter.update_preset()
        self.job_status_filter.update_preset()

    def _fill_ui(self,ui):
        ui['custom_page'] = 'libreflow.baseflow.ui.job_queue.JobQueueWidget'


class GotoQueue(flow.Action):

    _site = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        return self.get_result(goto=self._site.queue.oid())


class GotoCurrentSiteQueue(flow.Action):
    
    ICON = ('icons.flow', 'jobs')
    
    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return context and context.endswith('.inline')
    
    def run(self, button):
        current_site = self.root().project().get_current_site()
        return self.get_result(goto=current_site.queue.oid())


class RemoveEnvironmentVariableAction(flow.Action):

    ICON = ('icons.gui', 'remove-symbol')

    _variable = flow.Parent().ui(hidden=True)
    _collection = flow.Parent(2).ui(hidden=True)

    def get_buttons(self):
        return ['Confirm', 'Cancel']

    def run(self, button):
        if button == 'Cancel':
            return

        collection = self._collection
        self._collection.remove(self._variable.name())
        collection.touch()


class EnvironmentVariable(flow.Object):

    site = flow.Parent(2)
    
    variable = flow.Param("")
    value_windows = flow.Param('')
    value_linux   = flow.Param('')
    value_darwin  = flow.Param('')
    value = flow.Computed(cached=True)

    remove_variable = flow.Child(RemoveEnvironmentVariableAction).ui(hidden=True)

    def compute_child_value(self, child_value):
        if child_value is self.value:
            value = None
            # Get the operative system
            _os = platform.system()
            if _os == "Linux":
                value = self.value_linux.get()
            elif _os == "Windows":
                value = self.value_windows.get()
            elif _os == "Darwin":
                value = self.value_darwin.get()
            else:
                self.root().session().log_error('Unrecognized operative system')
                value = None

            self.value.set(value)


class AddEnvironmentVariableAction(flow.Action):

    _vars_collection = flow.Parent().ui(hidden=True)
    variable = flow.SessionParam("")
    value_windows = flow.SessionParam('').ui(editor='path')
    value_linux   = flow.SessionParam('').ui(editor='path')
    value_darwin  = flow.SessionParam('').ui(editor='path')

    def get_buttons(self):
        return ['Create', 'Cancel']
    
    def revert_params_to_defaults(self):
        self.variable.revert_to_default()
        self.value_windows.revert_to_default()
        self.value_linux.revert_to_default()
        self.value_darwin.revert_to_default()

    def run(self, button):
        var_name = self.variable.get().replace(' ', '_').upper()
        value_windows = self.value_windows.get()
        value_linux = self.value_linux.get()
        value_darwin = self.value_darwin.get()

        if button == 'Cancel':
            self.revert_params_to_defaults()
            return

        elif (len(var_name) == 0) or (len(value_windows) == 0 and len(value_linux) == 0 and len(value_darwin) == 0) or (self._vars_collection.has_mapped_name(var_name)):
            self.revert_params_to_defaults()
            return

        else:
            new_var = self._vars_collection.add(var_name)
            
            new_var.variable.set(var_name)
            new_var.value_windows.set(value_windows)
            new_var.value_linux.set(value_linux)
            new_var.value_darwin.set(value_darwin)
            self.revert_params_to_defaults()
            self._vars_collection.touch()


class SiteEnvironment(flow.Map):
    
    add_environment_variable = flow.Child(AddEnvironmentVariableAction).ui(dialog_size=(600, 310))

    @classmethod
    def mapped_type(cls):
        return EnvironmentVariable


    def columns(self):
        return ['Variable', 'Value']

    def _fill_row_cells(self, row, item):
        row['Variable'] = item.variable.get()
        row['Value'] = item.value.get()

from .users import PresetValue

class SiteJobsPoolNames(PresetValue):

    DEFAULT_EDITOR = 'choice'
    
    def choices(self):
        site = self.root().project().get_current_site()
        return ['default'] + (site.pool_names.get() or [])


class WorkingSite(Site):
    
    _site_map = flow.Parent()
    
    site_type                    = Property(SiteTypeChoiceValue)
    request_files_from_anywhere  = Property().ui(
        editor='bool',
        tooltip=(
            "Allow the site to request files for any other site. "
            "Temporary option as long as synchronisation is manual."
        )
    )

    is_kitsu_admin               = Property().ui(editor='bool')
    auto_upload_kitsu_playblasts = Property().ui(editor='bool')

    root_folder         = flow.Computed(cached=True).ui(editor='path')
    root_windows_folder = Property().ui(editor='path')
    root_linux_folder   = Property().ui(editor='path')
    root_darwin_folder  = Property().ui(editor='path')
    
    ordered_site_names  = flow.Computed(cached=True)
    custom_site_order   = Property().watched().ui(
        label='Custom order',
        tooltip='Manage order in which sites are listed in the interface')
    
    sync_dl_max_connections = Property().ui(editor='int')
    sync_up_max_connections = Property().ui(editor='int')
    pool_names = Property()

    queue = flow.Child(Queue).ui(hidden=True)
    configuration = flow.Child(ConfigureWorkingSite)
    goto_queue = flow.Child(GotoQueue).ui(
        label="Show job queue"
    )
    
    site_environment = flow.Child(SiteEnvironment)

    with flow.group('AfterEffects settings'):
        ae_render_settings_templates = Property().ui(
            editor='mapping',
            label='Render settings templates')
        ae_output_module_templates   = Property().ui(
            editor='mapping',
            label='Output module templates')
        ae_output_module_audio       = Property().ui(
            label='Audio output module template')
        ae_comp_name_patterns        = Property().ui(
            label='Composition name patterns')

    def compute_child_value(self, child_value):
        if child_value is self.root_folder:
            root_dir = None
            # Get the operative system
            _os = platform.system()
            if _os == "Linux":
                root_dir = self.root_linux_folder.get()
            elif _os == "Windows":
                root_dir = self.root_windows_folder.get()
            elif _os == "Darwin":
                root_dir = self.root_darwin_folder.get()
            else:
                self.root().session().log_error("[Working Site] Unrecognized operative system ?")
            
            # if not root_dir or not os.path.exists(root_dir):
            #     self.root().session().log_warning("[Working Site] ROOT_DIR path DOES NOT EXISTS")

            child_value.set(root_dir)

        elif child_value is self.configured:
            self.configured.set(bool(self.root_folder.get()))
        elif child_value is self.ordered_site_names:
            self.ordered_site_names.set(self._compute_ordered_site_names())
    
    def child_value_changed(self, child_value):
        if child_value is self.custom_site_order:
            self.ordered_site_names.touch()
    
    def _compute_ordered_site_names(self):
        names_as_string = self.custom_site_order.get()
        names = names_as_string.replace(' ','').split(',')
        
        if names and names[0] == '':
            names = []
        
        unordered_names = self._site_map.mapped_names()

        for n in names:
            unordered_names.remove(n)
        
        return names + unordered_names
    
    def get_queue(self):
        return self.queue.job_list
    
    def get_jobs(self, type=None, status=None):
        return self.get_queue().jobs(type=type, status=status)
    
    def count_jobs(self, type=None, status=None):
        return self.get_queue().count(type=type, status=status)

    def set_sync_date(self):
        date = time.time()
        
        module_name = os.path.basename(sys.modules['__main__'].__file__)
        if 'sync' in module_name:
            self.queue.last_auto_sync.set(date)
        else:
            self.queue.last_manual_sync.set(date)


class ClearSiteQueues(flow.Action):

    ICON = ('icons.libreflow', 'clean')

    _sites = flow.Parent()
    emitted_since = flow.Param(0.0)

    def get_buttons(self):
        return ['Clear', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        for s in self._sites.mapped_items():
            # for j in s.get_jobs(status='PROCESSED'):
            c = s.queue.job_list.get_entity_store().get_collection(
                s.queue.job_list.collection_name()
            )
            c.delete_many({
                'date': {'$lt': time.time() - self.emitted_since.get()},
                'status': 'PROCESSED'
            })
            self.root().session().log_info(f'[Clear Site Queues] Clean {s.name()} job queue')

        self.root().project().synchronization.touch()
        self.root().session().log_info(f'[Clear Site Queues] Cleaning complete')


class WorkingSites(SiteMap):

    ICON = ('icons.gui', 'home')

    clear_site_queues = flow.Child(ClearSiteQueues)

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(WorkingSite)

    def columns(self):
        return ["Site", "Last manual sync", "Last auto sync"]

    def _configure_child(self, child):
        if child.name() == "default":
            child.short_name.set("dft")
            child.description.set("Default working site")
            child.site_type.set("Studio")
        else:
            super(WorkingSites, self)._configure_child(child)

    def _fill_row_style(self, style, item, row):
        super(WorkingSites, self)._fill_row_style(style, item, row)

        if item.site_type.get() == "User":
            style['icon'] = ('icons.gui', 'user')
        else:
            style['icon'] = ('icons.gui', 'home')

    def _fill_row_cells(self, row, item):
        super(WorkingSites, self)._fill_row_cells(row, item)

        if item.queue.last_manual_sync.get() is None:
            row["Last manual sync"] = ''
        else:
            row["Last manual sync"] = timeago.format(
                datetime.fromtimestamp(item.queue.last_manual_sync.get()), datetime.now()
            )

        if item.queue.last_auto_sync.get() is None:
            row["Last auto sync"] = ''
        else:
            row["Last auto sync"] = timeago.format(
                datetime.fromtimestamp(item.queue.last_auto_sync.get()), datetime.now()
            )


class ConfigureExchangeSite(ConfigureSite):

    server_url = flow.SessionParam("http://")
    server_login = flow.SessionParam("")
    server_password = flow.SessionParam("").ui(editor='password')
    bucket_name = flow.SessionParam('')

    def _fill_action_fields(self):
        super(ConfigureExchangeSite, self)._fill_action_fields()
        self.server_url.set(self._site.server_url.get())
        self.server_login.set(self._site.server_login.get())
        self.server_password.set(self._site.server_password.get())
        self.bucket_name.set(self._site.bucket_name.get())

    def _configure_site(self, site):
        super(ConfigureExchangeSite, self)._configure_site(site)
        site.server_url.set(self.server_url.get())
        site.server_login.set(self.server_login.get())
        site.server_password.set(self.server_password.get())
        site.bucket_name.set(self.bucket_name.get())


class TestConnectionAction(flow.Action):

    _exchange = flow.Parent()

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('Clik the button to test the connection.')
        return ['Test']

    def run(self, button):
        ret = self._exchange.sync_manager.check_connection()

        if ret is not None:
            self.message.set(
                '<font color=red>Connection error:</font><br>'
                f'<pre>{ret}</pre>'
            )
        else:
            self.message.set(
                'Connection looks <b>OK</b>'
            )
        return self.get_result(close=False)


class ExchangeSite(Site):

    ICON = ('icons.libreflow', 'exchange')

    server_url      = Property()
    server_login    = Property()
    server_password = Property().ui(editor='password')
    bucket_name     = Property()
    enable_tls      = Property().ui(editor='bool')

    sync_manager = flow.Child(SyncManager).ui(hidden=True)

    configuration = flow.Child(ConfigureExchangeSite)
    test_connection = flow.Child(TestConnectionAction)

    def compute_child_value(self, child_value):
        if child_value is self.configured:
            self.configured.set(
                (
                    self.server_url.get()
                    and self.server_login.get()
                    and self.server_password.get()
                    and self.bucket_name.get()
                )
            )


class ExchangeSites(SiteMap):
    
    ICON = ('icons.libreflow', 'exchange')

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(ExchangeSite)

    def mapped_names(self, page_num=0, page_size=None):
        names = super(SiteMap, self).mapped_names(page_num, page_size)
        if "default_exchange" not in names:
            names.insert(0, "default_exchange")
        return names

    def _configure_child(self, child):
        if child.name() == "default_exchange":
            child.short_name.set("dftx")
            child.description.set("Default exchange site")
        else:
            super(ExchangeSites, self)._configure_child(child)

    def _get_mapped_item_type(self, mapped_name):
        if mapped_name == "default_exchange":
            return self.mapped_type()

        return super(SiteMap, self)._get_mapped_item_type(mapped_name)


class SyncSiteStatus(flow.Object):
    status = flow.Param("NotAvailable", StaticSiteSyncStatusChoices)


class SyncMap(flow.DynamicMap):
    version = flow.Parent()

    @classmethod
    def mapped_type(cls):
        return SyncSiteStatus

    def mapped_names(self, page_num=0, page_size=None):
        sites_data = self.root().project().admin.multisites.sites_data.get()
        return sites_data.keys()

    def columns(self):
        return ['Name', 'Status']

    def _fill_row_cells(self, row, item):
        row['Status'] = item.status.get()
        name = item.name()

        if name == self.version.site.get():
            name += " (S)"
        
        row['Name'] = name


class UploadRevision(flow.Action):

    ICON = ('icons.libreflow', 'upload')
    
    _revision = flow.Parent()
    _revisions = flow.Parent(2)
    
    def needs_dialog(self):
        return self._revision.get_sync_status(exchange=True) == 'Available'
    
    def allow_context(self, context):
        return (
            context
            and not self._revision.is_working_copy()
            and self._revision.get_sync_status() == 'Available'
        )
    
    def get_buttons(self):  
        self.message.set((
            '<h3>Revision already on the exchange server</h3>'
            'Upload and overwrite it on the server anyway ?'
        ))
        return ['Confirm', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return

        current_site = self.root().project().get_current_site()
        # Add an upload job for the current site
        job = current_site.get_queue().submit_job(
            job_type='Upload',
            init_status='WAITING',
            emitter_oid=self._revision.oid(),
            user=self.root().project().get_user_name(),
            studio=current_site.name(),
        )
        sync_manager = self.root().project().get_sync_manager()
        sync_manager.process(job)
        
        self._revisions.touch()


class DownloadRevision(flow.Action):

    ICON = ('icons.libreflow', 'download')
    
    _revision = flow.Parent()
    _revisions = flow.Parent(2)

    def needs_dialog(self):
        return self._revision.get_sync_status() == 'Available'
    
    def get_buttons(self):  
        self.message.set((
            '<h3>Revision already available</h3>'
            'Download and overwrite it locally anyway ?'
        ))
        return ['Confirm', 'Cancel']
    
    def allow_context(self, context):
        return (
            context
            and not self._revision.is_working_copy()
            and self._revision.get_sync_status(exchange=True) == 'Available'
        )
    
    def run(self, button):
        if button == 'Cancel':
            return

        current_site = self.root().project().get_current_site()
        # Add an upload job for the current site
        job = current_site.get_queue().submit_job(
            job_type='Download',
            init_status='WAITING',
            emitter_oid=self._revision.oid(),
            user=self.root().project().get_user_name(),
            studio=current_site.name(),
        )
        self._revision.set_sync_status('Requested', current_site.name())
        sync_manager = self.root().project().get_sync_manager()
        sync_manager.process(job)
        
        self._revisions.touch()
