# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)[^1].

<!---
Types of changes

- Added for new features.
- Changed for changes in existing functionality.
- Deprecated for soon-to-be removed features.
- Removed for now removed features.
- Fixed for any bug fixes.
- Security in case of vulnerabilities.

-->

## [Unreleased]

## [2.12.0] - 2025-10-09

### Added

* Enable contextual dict editing on following flow objects: `Film`, `Sequence`, `Shot`, `AssetType`, `AssetFamily`, `Asset`, `Task`, `TrackedFile` and User Tasks interface.
* Support Kabaret new `select_changed` event for any item selection.

### Fixed

* Clear `Action.allow_context() with context=None` warning message for some actions on the home page.
* Highlighted palette color is now handled on the homepage.
* Focus tracking now supports all view types.

## [2.11.0] - 2025-10-06

### Added

* Custom Homepage implementation
* Search View: auto show more action

### Fixed

* Sync session: change job status type to an array for the mongo query.
* Reset Job: check existence of file for the minio query.

## [2.10.4] - 2025-09-03

### Added

* The date on which a sync job is processed is now stored.

### Changed

* The model used for the job queue view on a working site has been rewritten to load much faster and be more stable.
  * You can now filter by job type, as well as by multiple job statuses and users.
    * Job type and status selections are stored as user presets. This means that you can change the default behaviour yourself.
* Ensure that QMenu widgets are independent of the OS style.

### Removed

* The progression of a sync job is no longer tracked.
  * This is the main cause of instability when using the job queue view on a working site.

### Fixed

* User Tasks: list was empty if a task does not have a libreflow entity

## [2.10.3.2] - 2025-08-05

### Fixed

* Fixed FileData constructor arguments and updated related calls to match old argument structure in MyTasks

## [2.10.3.1] - 2025-08-01

### Fixed

* removed EVERY match case statements to keep compatibilty with older python versions

## [2.10.3] - 2025-08-01

### Fixed

*  removed any match case statements to keep compatibilty with older python versions

## [2.10.2] - 2025-08-01

### Changed

* Added focus view highlight to dark theme
* Highlight color slightly darker in dark theme

### Fixed

* Search view loads faster
* Fixed navigation bar focus issues with search view
* Fixed pixelated font in dark theme

## [2.10.1] - 2025-07-31

### Fixed

* Site status view
  * All columns have icons indicating the type of site.
  * Task view cannot load when other sites are not studio based.

## [2.10.0] - 2025-07-30

### BREAKING CHANGES

* Pyside2 can no longer be used, version 6 is now the minimum requirement.

### Added

* Add resolution percentage parameter for Blender in the render playblast action.
* Access Kabaret styles with a theme selection menu from the FlowView menu.
  * A new dark purple style has been added, but it needs a name, which will be determined in a future update.
* Most command-line arguments are no longer required and can be set using an environment variable instead.
  * Priority is still given to arguments.
  * `--layout-savepath`: `KABARET_LAYOUT_SAVEPATH`
  * `--site`: `LIBREFLOW_SITE`
  * `--index-uri` (for indexing session): `LIBREFLOW_SEARCH_INDEX_URI`
* Search engine:
  * An entry now stores the object type.
  * Allow certain object types to be excluded from a query.
  * A new, dedicated view for large search entities.
    * Accessible from the navigation bar — simply type a search and press enter.

### Changed

* Site sync statutes in the file history view have been reworked to be more readable:
  * The sites are ordered by default as follows: the current site, then the exchange and studio sites.
  * The new `Display More/Less` button allows you to make all sites visible again.
  * Use the settings button to choose which sites are displayed by default and to arrange them in any order.
  * Sync status from the current site is now displayed differently to make it more distinct from the other sites.
  * Two icons are now used in the header to indicate whether the site is remote or studio-based.
    * This is only effective for the current site. A patch for all columns will be released as soon as possible.
* Restore the automatic source site selection for revision requests.
  * This is now the default behaviour for any request actions.
  * Request action will no longer display a dialog if only one site has the revision.
* Search engine: the maximum depth has been increased to allow file indexing.
* The title bar of a FlowView is now highlighted when the view is in focus.
  * This behaviour will be more useful in future updates.
  * This only applies to the default style. A patch for the others will be released as soon as possible.

### Fixed

* Closed FlowViews no longer remain in the views list.

## [2.9.15] - 2025-07-17

### Added

* When creating a default file from the working file of a previous task, the action will try to download the file from the exchange server if it is not available locally

* Wait runner can now be passed a list of runner IDs instead of a single one

### Changed

* Highly requested change of colors of the scroll bars for better clarity

## [2.9.14] - 2025-07-11

### Fixed

* Improved login and fixed any issues

### Added

* Kritarunner added to runners list, to handle scripting.

## [2.9.13.2] - 2025-07-09

### Fixed

* Fixed login with full email adress

## [2.9.13] - 2025-06-12

### Added

* FileJob class has new practical functions for operating and logging jobs.
  * For example, check whether a runner is still running or print their information.
* A job map has been added to a Task entity.

## [2.9.12] - 2025-06-12

### Changed

* The Submit Job button in Render Playblast actions is now hidden if no pool has been configured on the working site.

### Fixed

* When rendering a Blender playblast on an asset, the frame count defined on Kitsu is no longer checked, since this entity type does not have the parameter.
* Libreflow module path has been extended to allow submodules to be imported in a virtual environment (venv).

## [2.9.11] - 2025-05-19

### Fixed

* Handling empty regex on login

## [2.9.10] - 2025-05-03

### Added

* An icon for publish photoshop actions
* An error exception now occurs when the Kitsu project is unreachable
  * This happens when the user is not assigned to the project
* A Kitsu function to get the duration of a shot.

### Fixed

* User: Logging in to Kitsu with an email address does not save the address correctly
* User: Registered user was not used if logging in to Kitsu with an email address

## [2.9.9] - 2025-04-03

### Added

* Mark Image Sequence: An error occurs if FFMpeg or ImageMagick is not found in the PATH

### Changed

* Mark Image Sequence
  * Now uses name of matching default file
    * Fallback to `{file_base_name}_movie.mov` if no default file is found
  * Migrating of PATH command usage for ImageMagick to `magick`
    * The old `convert` command for earlier versions is still supported
    * This change only affects any runner, except Blender at the moment

### Fixed

* Compute value of target kitsu task type on `DefaultTaskFile`
* Sometimes, the TVPaint interface doesn't appear at all. Making the process unusable
* Mark Image Sequence: Revision name is now parsed correctly

## [2.9.8] - 2025-03-14

### Added

* Photoshop added to runners list, to handle scripting.

### Changed

* No longer necessary to create a user by hand.
  * If authentication with Kitsu works, the user will now be automatically created in the map.
  * Initial authentication now supports login from email
    * Next time the user logs in, all he has to do is enter his username (the first part of the e-mail).

### Fixed

* Updating of Kitsu task type files

## [2.9.7.1] - 2025-02-20

### Fixed

* Handle `.grg` files in releases.

## [2.9.7] - 2025-02-20

### Changed

* A script written in George is now run when a TVPaint file is opened to force the `save audio & video dependencies` options on the project.

## [2.9.6] - 2025-01-29

### Added

* User environment
  * An action for remove a variable
  * A warning message to inform to the user, how variables work.

### Fixed

* User Tasks: use episode name for film entity in task oid if kitsu project is a TV Show.
* User environment: action to edit a variable did not work.

### Removed

* FileSystemMap no longer uses an aggregate on the mongo query to fetch files.

## [2.9.5.2] - 2024-12-17

### Fixed

* Error raising when a job is removed while its pool is undefined.

## [2.9.5.1] - 2024-12-05

### Fixed

* Import Files Action: existing revision check for files.

## [2.9.5] - 2024-11-26

### Fixed

* Import Files Action
  * OID path of the action is no longer overwritten.
  * Fetching files in Target Wizard should be much faster.
  * Fixed folder import.
* Mark Image Sequence is no longer dependent on After Effect working files.

## [2.9.4] - 2024-11-26

### Added

* TVPaint file template.

## [2.9.3] - 2024-11-21

### Fixed

* Updated the `RenderBlenderPlayblast` action with the current parameters used by the Blender addon.

## [2.9.2] - 2024-11-14

### Changed

* Task Type Files in Kitsu Bindings have been improved:
  * Patterns are now regexes, allowing more flexibility.
  * The full OID of a file is used instead of the file name. So you can specify for example, that all files in a particular task go to a kitsu task type.
  * You can now use regex for the kitsu task type.
  * The parameter has been converted to a map for easier management.

## [2.9.1.1] - 2024-11-14

### Fixed

* Import Files Action: don't use asset lib name parameter if kitsu project is not a TV Show.

## [2.9.1] - 2024-11-12

### Fixed

* Create Kitsu Users action: ignore Kitsu users with no desktop (LDAP) login.

## [2.9.0.2] - 2024-11-12

### Fixed

* User Tasks was broken because it tried to use an episode name even though the kitsu project was not a TV Show.

## [2.9.0.1] - 2024-11-07

### Fixed

* Kitsu project type is only updated when host is valid.

## [2.9.0] - 2024-11-07

### Added

* A param that specified the project type on Kitsu.
* When the kitsu project type is a TV Show, various changes are made to the flow.
  * Asset Types base level is hidden in order to use the Asset Library.
  * Additional Kitsu data are handled on Upload To Kitsu, Import Files actions and User Tasks interface.

### Fixed

* Upload to Kitsu action is accessible only if there is a published revision.

## [2.8.6] - 2024-10-25

### Added

* Runner handlers for Blender and MarkSequenceRunner.
  * FFMpeg and ImageMagick are possibly not installed.
  * Blender operator not recognized.
  * Image Sequence not found on MarkSequenceRunner.

### Fixed

* Base template file for TVPaint
* Blender playblast: use a 0 shot duration when the Kitsu host is invalid. It currently happens when the action is called from the `libreflow.jobs_node` session.
* Several bugs in the JobQueue and minio progress script that can cause freezes and crashes.
* Remove outdated jobs action now gets the emitter's site sync status instead of the current site.
* Mark Sequence action can now use the default task path format, if there is no default file.

## [2.8.5] - 2024-10-17

### Fixed

* Revision Sync status will now be updated when the Job is actually processed instead of during the processing

## [2.8.4] - 2024-10-17

### Added

* TVPaint added to runners list.
* Search Index Session can now be started with a periodic mode.

### Changed

* Clean Sync Jobs Session can now be run once.
  * To be used by the libreflow periodic docker.

### Fixed

* Clear Site Queues Action: Clearing job queues has been improved.

## [2.8.3] - 2024-10-10

### Added

* A command line session for indexing all project entities to be searched.
  * This session runs once.
* JobQueue
  * Filtering by status and user
  * Progress Bar and estimated left time indicator
  * Search Bar
* Small Ui and log changes to RemoveOutdatedJobs and Clear Queue Actions

### Changed

* Indexing entities to search engine has been dramatically improved.
  * Restricted to entities (objects) only. Actions and values will now be ignored.
  * Start indexing from films and asset types maps.
  * Limit flow depth level to tasks.

## [2.8.2] - 2024-10-04

### Fixed

* Fixed empty sync dates handling
* Moved file size property to revision

## [2.8.1] - 2024-10-03

### Added

* Brand new custom UI for the Job Queue on the working sites
  * List refresh has been optimized for bigger queues
  * User can filter by job status
  * Sorted by date by default, starting from the most recent jobs.
  * Job queue now displays file size (non-retroactively)
  * Double click on a job to open its object, right click to open its revision history

## [2.8.0] - 2024-09-24

### BREAKING CHANGES

* Force `kabaret.subprocess_manager` minimum version to `1.2.0` to support runner handlers.
  * It's for capturing specific messages in a runner's log.
  * A new map in the project settings shows the base runner handlers and allows the user to override or create new handlers.
  * Extra or overridden handlers are passed through the `extra_handlers` function in `GenericRunAction`.

### Added

* A working site has new parameters for storing the date of the last automatic and manual sync job.
  * These dates are visible on the Working sites map and the JobQueue.

### Fixed

* User tasks: Background thread for updating task data is now correctly stopped when the user manually updates the task list.
* RenderBlenderPlayblast: Correct type for pass the frame count to playblast blender operator.

## [2.7.6] - 2024-09-19

### Fixed

* Make sure that a Blender outdated working copy shows a warning message in its viewport on opening.

## [2.7.5] - 2024-09-18

### Added

* A warning message is displayed in Blender outdated working copies when they are opened from their file's history.

### Changed

* Existing default files with a defined base file can now be recreated manually in the Create Default Files action.
  * A confirmation message is displayed to warn the user.

## [2.7.4] - 2024-09-05

### Added

* User tasks: "FDT" button has been renamed to "Timesheet" with custom URL from environement variable (`LF_MYTASKS_FDT_URL` and `LF_MYTASKS_FDT_LABEL`)
* User tasks: New parameters for hidden specific asset types and tasks
* User tasks: If the corresponding libreflow entity of a kitsu task can't be found, a warning is now shown to the user
* User tasks: New log messages printed to the console for better error handling
* Progress bar now displayed in console for syncronization jobs

### Changed

* Render After Effects Playblast action now asks if you want to keep existing images when using a specific frame range
* Removes outdated jobs action now handles ERROR status

### Fixed

* User tasks: Check for asset family (Kitsu category) was performed incorrectly

## [2.7.3] - 2024-08-30

### Fixed

* Re-set the correct status to check for the working copy outdated warning on blender.

## [2.7.2] - 2024-08-29

### Added

* Working site job queue now has a jobs counter.

### Changed

* Clear working site job queue action has been moved to the job queue.

### Fixed

* Jobs with non-existent objects are now removed in the remove outdated jobs action.

## [2.7.1] - 2024-08-29

### Fixed

* Upload To Kitsu action was broken if a source file is not defined.

## [2.7.0] - 2024-08-29

### Added

* An Action in job queue that removes outdated jobs when a more recent revision has been uploaded.
* A toogleable option to autoplay a blender playblast after being rendered
* An icon for when the revision is uploaded on Kitsu
* An icon for when the file's latest revision is uploaded on Kitsu
* Libreflow will prevent opening an already opened working copy
* Path and image Kabaret editors integrated in Project thumbnail param and Site environement params
* A check if the playblast frame number is the same as defined on Kitsu before rendering in Blender and uploading to Kitsu
* Frame range parameter in Render AE Playblast

### Changed

* When a working copy of a `.blend` file is outdated, the Blender read-only script is now used to display a warning to the user, but doesn't disable saving.
* Simplified Kitsu Task status names in Upload To Kitsu action
* Increased Job Queue default height

## [2.6.4] - 2024-07-22

### Added

* USDA and USDZ file format support.

## [2.6.3] - 2024-07-05

### Added

* XPIX file format support.

## [2.6.2] - 2024-06-25

### Fixed

* The synchronization session tries to process all waiting jobs, instead of the first waiting job only. This prevents the session from getting stuck if this job cannot be processed (unavailable revision on the current site/exchange server).

## [2.6.1] - 2024-06-21

### Fixed

* Non-GUI sessions now have the new session arguments for redis cluster replica.

### Removed

* Unused `DebugGUISession` class (from `libreflow.session`).
* Register the `kabaret.script_view` view type on session, as this is now done automatically in version 1.2.0 of the plugin.

## [2.6.0] - 2024-06-20

### BREAKING CHANGES

* Force kabaret minimum version to `2.4.0rc1` to support replica of a redis cluster.

## [2.5.3] - 2024-06-19

### Changed

* `Revision.get_path()` does not raise an exception anymore when the revision's `path` property is undefined. Instead, the `path` is computed using the path format of the revision's parent file. The method eventually raises an exception if this path format is undefined.

## [2.5.2] - 2024-06-13

### Fixed

* The awaited jobs of a `LinkedJob` are linked by their OIDs instead of their `job_id`, which allows to link jobs before their submission to a pool queue.

### Removed

* Dependency to SentrySDK in jobs worker session (not in Libreflow's default dependencies).

## [2.5.1] - 2024-06-07

### Fixed

* Import Files action was broken due to a bug in harmonising log messages.

## [2.5.0] - 2024-06-06

### BREAKING CHANGES

* Force kabaret.subprocess_manager minimum version to `1.1.0`.
  * All our changes were applied to the original addon.
* Force kabaret minimum version to `2.3.0rc6` to support main window resizing.

### Added

* Declare a Connection parameter to specify which Import Files action to use.
  * In case you need to use a `kabaret.flow_extensions` version.
* A button in the *FlowView* option menu to show the `SubprocessView` from `kabaret.subprocess_manager`.

### Changed

* Clean and harmonise log messages with the session logger for a better readability.
* Define a default dialog size in few actions for a better user experience.

### Fixed

* Remove ICCP chunk on `.png` files of resources to clear a libpng error.
* Clear `Action.allow_context() with context=None` warning message for some actions on files and tasks.
* Non-GUI sessions (such as the synchronisation session) are no longer affected by Kabaret Layout Manager session arguments.

## [2.4.6] - 2024-05-24

### Changed

* Import Files action:
  * Handle asset families when they are used on an asset type.
  * Use asset collection of entity manager for finding asset data if the imported file has the following format `{asset}_{file_base_name}`.

### Fixed

* The synchronisation session `libreflow.sync` now stops if the root directory of the current site is invalid.
* Import Files action:
  * Default task check for retrieving the path format works again.
  * Make the creation of an entity case insensitive in task target wizard.
  * If an entity already exists, it won't make an error and break the import process.

## [2.4.5] - 2024-05-23

### Changed

* *RequestAs* action: Faster search of an existing upload request of the revision (using pymongo `Collection.find()`).
* Faster job filtering with `JobQueue.jobs()` (using pymongo `Collection.find()`).
* Faster job submission:
  - job creation directly uses pymongo API (`Collection.insert_one()`)
  - local and server paths of a job are ignored. They are computed only when the job is processed instead.

### Fixed

* *RequestAs* action: this is not possible anymore to confirm a request if the selected source and target sites are the same.
* *RequestAs* action: skip the download request towards the target site if a request already exists.

## [2.4.4] - 2024-05-23

### Changed

* User tasks: handle asset famillies

## [2.4.3] - 2024-05-16

### Changed

* Activate the filter (search bar) on the assets and asset families map.

## [2.4.2] - 2024-05-03

### Added

* mrViewer added in runners list for playback movies.

## [2.4.1] - 2024-04-27

### Fixed

* Synchronization session to comply with the new Kabaret session arguments for layout management.

## [2.4.0] - 2024-04-26

### BREAKING CHANGES

* Force Kabaret minimum version to `2.3.0rc5` to handle new Kabaret's layout manager on the GUI session.

## [2.3.2] - 2024-04-26

### Added

* Kitsu (Gazu) wrapper has a new method `get_project_type()` for retrieve project type (Short, TV Show etc.)
* MXF and PRPROJ file formats support.
* Premiere Pro added in runners list.
* A parameter in default files to specify the target Kitsu task type. Only used for Kitsu uploadable files.

### Changed

* Users list now sorted alphabetically (by user ID) by default.
* Default Tasks in Task Manager are now sorted by task position number.
* Improved log messages for Create Task Default Files and Kitsu Tasks actions.

### Fixed

* Kitsu episodes is now handled in `get_entity_data()` of Kitsu (Gazu) wrapper.
  * Caused problems when trying to retrieve kitsu entity of a shot when project is a TV Show.
* File and revision paths are now normalised to avoid opening issues with differents slashes.
* Task Template now has a function to get path format and fixes the action for creating files in a task template.
* Import Files action: typo on `Resolving files` popup.
* User tasks: the display of a file entry's action menu when the file is right-clicked and its secondary action button is clicked.
* User tasks: dragging a file out of the UI.
* User tasks: focus detection for keyboard shortcuts when using multiple views in the window
* View title is updated again when current oid is changed. Fixed confusion when multiple views were docked.
* View width is no longer expanded if the current oid is on a custom UI page and there are multiple views.
* Fixed *Create default files* task action when a file is incremented from its base file.
* Lock a synchronization job starting to be processed by setting its status to `PROCESSING` (avoids multiples processing of the same job from different sessions).
* Synchronization session: rectified deprecated OIDs and automatic relaunch when an error occurs.

## [2.3.1] - 2024-03-14

### Added

* New parameters `width` and `height` in the project settings. These are available in the project default contextual dict.
* New task icons to display in a shot or asset task list.
  * If a color is defined in a task, the new icon will match it, maintaining its brightness and saturation.
* A Blender script to open a published revision of a Blender file in a kind of read-only mode.
  * The script disables the main functions for saving the file and displaying a warning in the interface.
  * The Save As function and the unsaved changes warning that appears when you close the software are still active.
  * This feature is enabled by default, but can be disabled in the project settings.
* User tasks: Tasks can be resized vertically by dragging between them.
* The subdirectories of the working copy are now removed when changes are published and keep editing option is disabled.
* Base file mode is now handled on create working copy action.
  * Alert the user if the source revision has not been created on file.
* New icon for Publish and render blender playblast action.

### Changed

* Task List UI
  - Matching the new color scheme of LFS style class.
  - Slight adjustments to the button shape of a task.
* Use path format from default task is used first on PathFormatValue
  * Used for create task default files actions
* Color of file actions error messages has been adapted to LFS style class color scheme.
* Value of the *Upload after publish* is not stored anymore in the action value store. It only depends on the *auto upload* project setting.
* Logging level of the session worker (INFO).

### Fixed

* Create Kitsu Tasks action: switch to case insensitive for check task templates names.
* The `TaskManager.get_task_files()` method now returns enabled only files when corresponding attribute is used.
* Create default files:
  * `NoneType` error when a default file was created from a base file which has no revision or whose latest revision wasn't available.
  * A default file is now not create by default, when it already exists and use base file mode is enabled.
    * The user can still manually choose to create the revision from base file. This is to avoid issues when action is used in a batch way.
* User Tasks: 
  * Libreflow bookmarks no longer break the interface
  * No longer resizes window when update warning appears
  * Scrollbar of comments widget is no longer reset when task list is updated
* Remove unused parameters on Publish and render blender playblast action to make it work again.
* Task Ui: The visibility of file main actions is now set at view init.

### Removed

* Task assignation methods for fixes the update of the contextual view on a task.
* Deprecated features related to dependencies of a Blender file:
  - *include dependencies* option in the actions for requesting revisions
  - saving of the dependencies when publishing a Blender file

## [2.3.0] - 2024-10-01

### Added

* A parameter to the `MarkImageSequence` action to specify the suffix in the name of the generated movie (default: `_movie`).
* A set of icons for classic tasks.
* The entity manager can now define a global collection to be used for file references with the `EntityManager.get_file_ref_collection()` method.
* New contextual parameters for the project and the main entities, accessible in the contextual dict of entities using the following keywords:

| Entity property               | Keyword                     |
|:------------------------------|:----------------------------|
| Project name                  | `project_name`              |
| Project code                  | `project_code`              |
| Film code                     | `film_code`                 |
| Film display name             | `film_display_name`         |
| Sequence code                 | `sequence_code`             |
| Sequence display name         | `sequence_display_name`     |
| Shot code                     | `shot_code`                 |
| Shot display name             | `shot_display_name`         |
| Asset display name            | `asset_display_name`        |
| Asset family code             | `asset_family_code`         |
| Asset family display name     | `asset_family_display_name` |
| Asset type code               | `asset_type_code`           |
| Asset type display name       | `asset_type_display_name`   |
| Task prefix                   | `task_prefix`               |
| File extension                | `file_extension`            |
| Revision is a working copy    | `revisioin_working_copy`    |

* The new `file` contextual key has replaced the `file_mapped_name` key (defined in 2.1.0).
* A `code` property in the `TaskTemplate` entity. It is used by default for default tasks.
* A `prefix` property to the `Task` entity.
* A list of statutes in the project Kitsu settings to configure the statutes available in the `UploadPlayblastToKitsu` action's dialog.
* The `Task` class now provides a `position` property which holds the task position among the list of tasks in the UI.
* A default task now provides an `entity_filter` parameter used to filter entities by oid in which the default task can be created.
* A new method `get_default_tasks()` in the `TaskManager` class returns a filtered list of default tasks (see docstring for more details about filters).
* New parameters have been added to the `CreateDefaultTasksAction` action to:
  - hide *optional* tasks
  - hide *filtered* tasks, i.e. tasks for which the entity oid does not match the `entity_filter`
* The `Task` class provides a new instance method `get_files()` returning a filtered list of files - optionally including linked files - existing in a task (see docstring for more details about filtering parameters). It comes with another new method `has_file_ref()` which allows to check if a task has a reference to a given file. This can be useful to filter files and references from the first method output.
* If the `optional_publish_comment` option in the project settings is enabled, the user must enter a non-empty comment to publish changes made in a file.
* A new `file_user_status` property in the `TrackedFile` class which represents the state of the file from the point of view of the current user:

| User status                                                                                                | Value       | UI Color |
|:-----------------------------------------------------------------------------------------------------------|:------------|:--|
| The user has no working copy.                                                                               | `None`      | ⚪ |
| The user has a working copy which is newer than the latest revision and no other users have working copies. | `"latest"`  | 🟢 |
| The working copy of the user is older than the latest publication.                                          | `"old"`     | 🔴 |
| Other users have working copies.                                                                            | `"warning"` | 🟠 |

* The UI of a file entry in the task UI have been updated to indicate if the file is **primary** (name in bold) and if it is *empty* (name in italic). The entry's text/background color also reflects the file's user status (see table above).
* A new key `frame_rate` in the project's contextual settings.
* Actions `CreateFileAction` and `CreateFolderAction` now allow to select the target category (*Inputs*, *Works* or *Outputs*) of the item to create.
* The `LaunchSessionWorker` action provides two new methods `launcher_exec_func_args()` and `launcher_exec_func_kwargs()` to set arguments passed by the worker to the executed method.
* The `TrackedFile.has_working_copy()` method now checks the working copy synchronisation status using the parameter `sync_status`.
* Option `auto_open` in the default file settings allows to automatically open the last revision of a file/folder when double-clicked in the task UI. When the file/folder has no published revision, the default behavior is used.

#### Automatic indexing of search entries

When enabled, this feature allows to index OIDs of flow touched objects according to a list of filters. Each filter is composed of:
- an oid pattern, used to filter touched objects
- a boolean option which determine if the touched object must be indexed
- a list of target oid patterns, which state which target objects relative to the touched object must be indexed

These filters can be managed in the search settings in the *FlowView* option menu. Automatic indexing is disabled by default, and can be enabled from the session (see `Search` actor constructor).

### Fixed

* Play sequence: `NoneType` error when a file to be added in the sequence is empty.
* Render Image Sequence: The source revision comment is now defined in the folder revision.
* The time to access to file presets in a default task (`DefaultTaskFiles`) has been reduced by replacing preset parameters with computed values. This avoids broadcasting a 'touch' event whenever a parameter of a preset is set, which was useless since preset data is stored in the session.
* User tasks: Dialog for editing a task status works again if no revision was found for primary files.
* An error raising after confirming the creation of a working copy from a revision in the file history, which prevented the dialog from closing and the revision list from being updated.
* Bug occuring when saving the name and version of a default application while these had not been edited in the dialog. The values displayed by default when the dialog shows up now reflect correctly the actual values.
* The display of disabled tasks in the UI of an entity (asset/shot).
* Calling `ManagedTaskCollection.mapped_names()` (e.g., to display the task list UI) does not raise a `KeyError` exception anymore when a task has no corresponding default task in the task manager. Instead, it uses the task's `position` property value, or a `0` position if the latter is undefined.
* The type of a file is not modified anymore whenever a reference to it is moved by drag-and-drop to another file category.
* `IndexError` preventing from moving a file entry after any file placed before in the same list was moved.
* The list of references of an object wasn't updated when an `EntityRef` was added/removed to a `EntityRefMap` (using `add_ref()`/`remove_ref()` methods).
* The cache of the task UI was not updated correctly when a file link was created. When a file link just created was dragged-and-dropped in another list, a new link was created in the target list instead of updating the type of the moved link.
* Simultaneous rendering of multiple revisions of an AfterEffects file.
* The `OpenTrackedFileAction` action shows its dialog if the working copy is not available on the current site.
* Ensure that the marking process for AE playblast rendering waits for the marking to finish to get grayed out in the process view.

#### Runner configuration checking

The actions `GenericRunAction` and `LaunchSessionWorker` now provide a method `runner_configured()` to check if a runner is properly configured. Both actions check if the runner type must be registered in the project's factory. In addition, a runner run by the `GenericRunAction` action is considered configured if:
  - a default application is defined for the extension of the target file (in the project `admin` section by default)
  - the runner executable path is defined (either in the session, site or system environment)

The following action classes have been updated to prompt an error message whenever the corresponding runner still needs to be configured:
- `OpenRevision`
- `OpenTrackedFileAction`
- `RenderBlenderPlayblast`
- `SelectAEPlayblastRenderMode`
- `RevealInExplorer`
- `RevealRevisionInExplorer`
- `RevealFileInExplorer`
- `OpenTrackedFolderRevision`

### Changed

* The `CustomEntityCollection`'s `get_property()` and `get_properties()` methods now check for the properties in the collection cache, which significantly reduces the time needed to display the properties of a large number of entities in the UI.
* File references are now stored in a `GlobalEntityCollection` (project scope), which reduces the time to access a large number of references, e.g. for display in the task UI.
* The Gazu wrapper has been updated to manage sequences and shots belonging to episodes.
* `KitsuAPIWrapper.get_assets_data()` takes a new argument `episode_name` to filter assets by episode.
* The search engine is now case-insensitive.
* Only admin users have access to the `Admin` project relation.
* The map of default applications is not static anymore: file formats can be added/removed. Only extensions defined in this map will be available through the `CreateFileAction` dialog. A list of default file extensions is still provided when adding a new default application.
* The responsiveness to window resizing of action thumbnails of a task file entry has been improved: thumbnails display/hide so that the file name is always visible.
* A result in the completion list of the OID bar is automatically validated when it is clicked.
* The `MarkImageSequence` action now outputs a movie at the frame rate specified by the `frame_rate` contextual setting. If not defined, the frame rate used is 24.0 FPS.
* The `SelectAEPlayblastRenderMode` now allows to select the output module template used by AfterEffects to render a playblast. An error message is also displayed in the dialog with details in the terminal if at least one rendering template in the the current site settings is undefined.
* Messages of the `OpenTrackedFileAction` dialog.

#### User Tasks 

* The user interface has been redesigned for greater clarity and to match the new colour scheme.
* A file list now has the same UI as in the task UI, including the working copy status
* Tasks data is now cached for a faster UI loading
* File list and comments widgets are now loaded in background to improve UI loading speed
* New background thread for updating task data every 30 seconds
* Scrolling of filter drop-down combobox is now correctly reset

### Removed

* The unused `MarkSequenceAfterRender` action.

## [2.2.7] - 2023-03-22

### Added

* A new flow view registerable in the GUI session. Its navigation bar allows a direct edition of the current oid and does not display map names.
* KitsuAPIWrapper provides a `upload_asset_preview()` method to upload a preview to an asset task in Kitsu.
* Project Wizard:
  - Action dialog of an item can now be opened by a mouse double click
  - If no project has been created in libreflow, home page links directly to the wizard
  - For new projects, films entities are now created by default
  - A widget to import a project thumbnail
* Is primary file option has been added to edit task default file action.
* User tasks:
  - Added popup menus in navigation buttons
  - Added a separation line between presets and task status in the filter combobox
  - If a libreflow or kitsu task was not found, a warning is now displayed
* Task default files: a default file can be created/incremented from a base file (which can be configured in the default file preset in the task manager). The creation action now lets the user:
  - choose between creating a file from scratch or from its base file
  - edit its base file when the default file already exists

### Changed

* The layout of the flow view header: view options are now available in the view title bar.
* The `TaskManager.get_task_files()` method now returns a dictionnary in which data is mapped with the default file flow name to simplify the look-up.
* Blender playblast: the name of the sequence is marked as is on the frames.
* The label of a Blender playblast rendering job contains the Blender file oid.
* Project Wizard:
  - Non editable files and auto-upload parameters have been reworked.
  - The task manager page has been updated with recent changes.
* User tasks:
  - Buttons to edit a task status and redirect to a task have been reversed.
  - File upload in edit task status action has been completely reworked.
  - Sorting by status has been improved.
  - Added small modifications to the user interface to adapt to the new style class.

### Fixed

* Create an After Effects playblast with the path format of its corresponding default file when defined in the task manager. The project default path format is used otherwise.
* A non-default file can again be defined as a primary file
* User tasks:
  - Better detection if names of libreflow and kitsu tasks are the same
  - If the kitsu task was not found for a libreflow bookmark, feature was not working
* The value of the `file_type` param of the `AddDefaultTaskFileEdit` action dialog was not reflecting its actual value, which was leading to default files with a `None` file type, as well as the task files created from them.
* When a file is created with the `CreateTaskDefaultFiles` action, its `file_type` and `is_primary_file` properties are set according to the corresponding file preset in the task manager.

## [2.2.6] - 2023-02-13

### Added

* A new flow view registerable in the GUI session. Its navigation bar allows a direct edition of the current oid and does not display map names.
* New data which can be used in a file path format, using the following keywords and formats:

| Object data            | Keyword           | Data type / format   |
|:-----------------------|:------------------|:---------------------|
| Current user name      | `user`            | `str`                |
| Current user code      | `user_code`       | `str`                |
| Current site name      | `site`            | `str`                |
| Current site code      | `site_code`       | `str`                |
| Revision number        | `revision_number` | `int`                |
| Revision creation date | `revision_date`   | `str` / `%y%m%d`     |
| Asset code             | `asset_code`      | `str`                |
| Task code              | `task_code`       | `str`                |

* Each file link in a task file list displays the label of its origin task.
* A new style class.

### Changed

* User and site data is stored in MongoDB collections.

### Removed

* Actions to request revisions at the project, sequence and shot scopes.
* Action to check synchronisation errors.

### Fixed

* Update of a default task file preset: the map cache was not updated.
* Creation of the default files of a task: created files did not match the selection due to a cache timeout.

## [2.2.5] - 2023-01-23

### Added

* File priority actions can be managed in the file presets of the project's default tasks. If priority actions are not defined for a given file, they are retrieved from the corresponding default task's file preset.
* A revision can be double-clicked in the history. The action run is specified in `Revision.activate_oid()`, which is the open action by default.

### Fixed

* Prevent an error raising when a task is touched while its UI has not been built yet.
* Fix an error raising at the display of the tasks of an entity when the color of at least one of them is undefined (neither in the task manager nor in the task itself).

## [2.2.4] - 2023-01-11

### Added

* An action to reveal a revision in the explorer.
* An action to remove a file of a default task.
* An action to set a file as a task's primary file.

#### Project Wizard

* A new interface lists all the essential parameters that must be configured for the project.
  - Accessible from a right click on the home page in the navigation bar

#### Import Files

* An action to import files into shots and assets

#### Task Manager

* An action to create default tasks from Kitsu ones
* A path format can be specified for a task template, which is inherited by default by its files (unless they explicitly override it). A path format can be also specified for a default task, in which case the path format of a file is evaluated to the value of the first path format defined in the following order: default task file > default task > task template file > task template.

#### Task UI

* A new button to add the task in the bookmarks.
* Can open the new Import Files action by drag and drop files

#### User Tasks

* A dialog to edit task status
* Handle libreflow bookmarks

### Changed

* Task UI: Button icon that displays disabled tasks is now dynamic according to its activation status.
* Revealing a tracked file in the explorer opens the grand-parent folder of the revisions by default.
* The action to open a revision is available only when the revision is marked as available on the current site. A warning dialog still appears if the revision doesn't exists.
* The action to create a working copy from a revision is available only when this revision is marked as available on the current site.
* User tasks:
  - Better readability of task comments
  - Shot duration is now displayed by total frames number and timestamp

### Fixed

* Task UI: The last site in file statues list was not displayed.
* Set the position of a default task when using the creation action.
* User tasks: Gets Kitsu tasks only from the current project

## [2.2.3] - 2022-11-29

### Added

* A task provides a list of files which are to be edited by the user, called **primary files**. If no such file is defined for a given task, the primary files defined for the corresponding default task are returned.

#### User tasks

* A new interface lists the project tasks corresponding to the Kitsu tasks to which the user is assigned.
  - For each task, the view presents its primary files (whose options can be found by right-clicking) and its Kitsu history.
  - Pressing `Shift` key allows to display the description and duration of the task's shot.
  - A task in Libreflow can be bound to multiple Kitsu tasks in the corresponding default task settings.

### Changed

* When a Blender playblast is created, if it belongs to the default files of the current task, its path format is set to that defined in the default file settings. Otherwise, the playblast is created with the same path format as the source Blender file.

### Fixed

* Blender playblast rendering is possible for files which don't belong to shots. The sequence number and shot name are replaced by placeholders.

## [2.2.2.3] - 2022-11-29

### Fixed

* Update Gazu required version (0.8.33) to properly check if the host is valid.

## [2.2.2.2] - 2022-11-28

### Changed

* Make After Effects file template compatible with the 2023 version.

## [2.2.2.1] - 2022-11-28

### Fixed

* Kitsu host check is done using the original Gazu method (`gazu.client.host_is_valid()`).

## [2.2.2] - 2022-11-21

#### Task

* File map actions are accessible in the task UI as buttons under the file list widget.

## [2.2.1] - 2022-11-08

### Added

#### Task UI improvements

* Add new icons to be displayed in the task list of a shot.
* Links to other files can be created by drag-and-dropping a file onto one of the file list of the task. The user can interact with links the same way as with regular files.
* File lists are updated whenever a file belonging to the task is touched. Similarly, the selected file history is updated whenever a revision belonging to this file is touched.
* A revision now holds a status parameter. Default statutes are `working_copy` and `init` for working copies and publications respectively. Custom statutes can be defined in the `revision_statutes` parameter in the project settings.
* A revision now keeps track of the source revision it is created from. On this basis, a graph in the history view allows to visualise the parentage of the revisions and their statutes.

### Fixed

* Fixed the update of the revision data of the selected file in the task UI, making the application crash when switching to the history display mode.

---

## [2.2.0] - 2022-10-14

### Added

* Define new methods for Gazu wrapper:
  - `get_shots_data(sequence)` : Retrieve all shots data of a sequence
  - `get_sequences_data()` : Retrieve all sequences data of the Kitsu project
  - `get_assets_data(asset_type)` : Retrieve all assets data of a asset type
  - `get_asset_type_data(name)` : Retrieve all data of a asset type
  - `get_asset_types_data()` : Retrieve all asset types data of the Kitsu project
  - `get_users()` : Retrieve all users name associated on the Kitsu project
* An choice value for choosing output module for After Effects playblast rendering.
* RenderImageSequence: Can now handle a custom output file name and path.

#### Task UI

Tasks are ordered in the GUI according the position configured in the default tasks of the project.

When reaching a task in the flow, the user is now provided with three lists of files: the input, working and output files of the task. When a file is selected, its revision history appears in the bottom of the page. General information of each revision is displayed by default. One can access to the revision synchronisation statutes of all the project's sites by pressing the `shift` key.

### Changed

* Users list is now injectable.
* File lock is now disabled by default.
* `TrackedFile.get_revision()` method now return `None` if the searched revision doesn't exist, rather than raising an exception.

### Fixed

* Properly set Blender playblast revisions created at rendering (i.e. according to the playblast path format).
* Name the render folder and movie resulting from AfterEffect playblast rendering with the name of the rendered AfterEffects scene.

## [2.1.6.3] - 2022-08-19

### Fixed

* Make action to create a working copy from a file injectable.

## [2.1.6.2] - 2022-08-17

### Fixed

* Make action to create a working copy from a revision injectable.

## [2.1.6.1] - 2022-08-11

### Fixed

* Revisions are sorted by name in a natural way.

## [2.1.6] - 2022-08-11

### Added

* A new `utils.flow.values` module to gather custom value types.
* A `MultiOSValue` whose value is computed from that of an environment variable if defined, or that of a parameter corresponding to the OS currently running (among Linux, Windows and Darwin).
* Support for .psb files.

## [2.1.5] - 2022-07-28

### Added

* A property and operators to the manage task class to assign users.
* Tasks to which the current user is not assigned are grayed out, unless assignation is disabled for the associated default task.
* A managed task can now contain subtasks:
  - subtasks are defined in the default tasks
  - a managed task provides an option to assign one of the project users to one or more of its subtasks.
  - the managed task has a parameter which specify the current subtask
* A list of tasks in the Kitsu settings now allows to associate a subtask with a task defined in the Kitsu project.

### Changed

* The oid of the last revision is automatically updated when adding a revision with the `TrackedFile.add_revision()` method.
* File advanced options are no longer listed in a `Advanced` submenu.

### Fixed

* The status color of the last revision displayed in the file list, when the revision name begins with a `t`.

## [2.1.4] - 2022-07-26

### Added

* New classes defining the following elements of an asset library:asset types, asset families and assets.

## [2.1.3.1] - 2022-07-22

### Fixed

* Upload of playblasts to Kitsu.

## [2.1.3] - 2022-07-21

### Changed

#### Authentication

* Multiple users can use the same Kitsu account.
* A user now logs in with a login defined in its profile. The password is that of the Kitsu account being used by the user.

### Added

* A map of users in the Kitsu settings allowing to redefine the Kitsu account used by each user of the project.

## [2.1.2] - 2022-07-21

### Fixed

* The opening of applications when entering a project from the home page using the search engine. The fix currently assumes that all the required runner types are registered in the `touch()` method of the project.
* AE playblasts: ensure that the render folder revision is created before submitting (and is thus available to) the marking job.
* Ensure the playblast's last revision oid is updated when the rendering has finished.
* The extra environment of a runner isn't updated with the content of the contextual dictionary anymore, in order to prevent an environment update error raising when the contextual dictionary contains numerical values.

### Added

* Tasks are ordered in the GUI according the position configured in the default tasks of the project.
* Modifying the display name of the default tasks now update the names of the corresponding tasks displayed in the task list.
* A task stores 3 icon paths/references, one for each of its size (small, medium and large).
* A `PriorityFiles` map which manages a list of files to be prioritised for batch actions.
* An action for open a full sequence in Shotgun RV.
  - At every use, the parameter values are reset to those stored in the project's **action value store**.
  - It retrieves shots according to this priority order. Compositing preview (`compositing/compositing_movie.mov` by default) first or if it's not exist, the latest revision of the animatic (`misc/animatic.mp4` by default).
  - If no file has been found in a shot, it is possible to replace it with a filler screen (`Black`, `Magenta`, `SMPTE Bars`).

### Changed

* The action to create default tasks in a task collection has been updated to allow to choose the tasks to create among the default ones defined in the task manager. Non-optional tasks are preselected. Tasks which already exist appear greyed out and can't be selected.
* A user can now create a working copy from that of another user, provided that the *Create working copies* option in his/her preferences is enabled.

## [2.1.1] - 2022-06-01

### Added

* A new type of task (`libreflow.baseflow.task.ManagedTask`), providing features (e.g., the creation of a list of default files) which use the task manager.
* A new type of task collection (`libreflow.baseflow.task.ManagedTaskCollection`). This collection uses, for each of its task, the icon and color defined by its associated default task in the task manager. It also provides an action to create a default task among those defined in the task manager.
* Actions to add and edit a default file of a task.

### Fixed

* Make the terminal automatically close when RV is closed.

## [2.1.0] - 2022-05-17

### Added

* An `EntityManager` object which manages the collections of common entities (films, sequences, shots, departments, files, revisions, synchronisation statutes).
* Revision maps provide the `file_base_name` and `file_mapped_name` entries in their contextual dictionary, which are respectively the real name of the parent file on the file system without its extension, and its mapped name in the flow.
* As for other entities, the `Task` and `TaskCollection` classes have been defined to allow to manage tasks, in a single Mongo collection for the entire project.
* A `task_manager` module to manage the creation of tasks based on default tasks.

### Changed

* Redefine films, sequences and shots as Mongo entities.
* Films, sequences, shots, files, revisions and synchronisation statutes are retrieved by default from the global entity collections provided by the project's entity manager, assuming the project provides the latter in the `get_entity_manager()` method.
* If no default path format is provided to the `FileSystemMap` `add_file()` and `add_folder()` methods, the file/folder is created with the path format in the contextual dictionary by default, if defined.

### Removed

* Unused `kitsu_name()` and `kitsu_id()` method of the project class.

## [2.0.13] - 2022-05-13

### Added

* Use Sentry to monitor jobs flow worker events. The Sentry SDK is initialised before starting a `JobsWorkerSession`, assuming the project Data Source Name (DSN) is provided in the `SENTRY_DSN` environment variable. When the job executed by the worker encounters an error, an exception is raised after the status of the job is updated, ensuring that the error is reported to Sentry.

### Fixed

* Make the `Reveal In Explorer` option reveal the latest available revision.
* Gazu wrapper's `get_shots()` method: tasks undefined in Kitsu are skipped in the filtering.
* An exception is raised whenever the `get_path()` method of a revision is called while its relative path is undefined (i.e., the value of its `path` property is an empty string or `None`).

## [2.0.12] - 2022-04-26

### Fixed

* Get around the error raised by Gazu upon the upload of some video files.

### Added

* Mark Sequence:
  - mark current and total time codes if provided in the marking template, as `tc` and `total_tc` respectively
  - update the text font
  - remove gray bands

### Changed

* Gazu wrapper: allow to specify multiple statutes for a given task in the `get_shot()` method filter.

## [2.0.11] - 2022-04-21

### Added

* One can specify the `--force-delete` argument to the jobs cleanup session to force job deletion.
* Gazu wrapper: add a method to upload a preview on a shot task, given the names of the shot and the sequence it belongs to.

### Changed

* Gazu wrapper: allow to get a list of shots filtered by their current statutes on given tasks

## [2.0.10] - 2022-03-30

### Added

* Render AfterEffects playblast/Publish and Render Playblast: allow to choose the render resolution.
  - Whenever the option dialog opens, the parameter value is reset to the value stored in the project's **action value store**.
* A module `action_values` which defines classes to be used by actions to manage a set of default values (typically that of their parameters), which can be overriden at the project and site scopes.

### Changed

* Utility functions related to context values are located in the `libreflow.utils.flow.context_values` module.

### Fixed

* Make sure that the last revision oid of each file created during playblast rendering is updated, so that it can show up in the file map.

## [2.0.9] - 2022-03-21

### Added

* A WAV file template
* Operators in Kitsu API wrapper to update the status of a shot's task

## [2.0.8] - 2022-03-15

### Added

* A new module allowing to browse through project entries. It provides for that purpose:
1. an `Actor` and commands to index and search through projects on the current cluster
2. `SearchFlowView`s (inherited from Kabaret's base flow views) which embed a search bar at their top.  
In order make this type of view available in the GUI, one must register the `SearchFlowViewPlugin` plugin type in the session plugins.

## [2.0.7] - 2022-03-13

### Added

* AfterEffects templates used for rendering (render settings, movie and audio output modules) can be configured in the settings of the current site.
* An option to export a temporary audio track of an AfterEffects scene, which may be used by image sequence marking option to generate a playblast. This option assumes a template named `audio_only` is available in the output module templates of the AfterEffects session used for rendering.

### Fixed

* File maps appearing empty when touched from other sessions, because properties of some entities are not yet set: these maps now update their cache whenever an accessed file property is not found in it.
* Render AfterEffects playblasts:
  - Ensure that paths to the revisions created during rendering and marking are generated using the path formats of the files they belong to.
  - Generate the playblast with the scene audio track, if it exists.

## [2.0.6] - 2022-03-13

### Added

* Tracked file class provides the `add_revision` method to add a revision a generic way.
* Working site type is now injectable
* WAV file format

## [2.0.5] - 2022-02-22

### Added

* File lock can be enabled/disabled in the project settings (with option `Enable File Lock`).
* Indicate the sync status of the last revision displayed in the file list with colors.

## [2.0.4] - 2022-02-16

### Fixed

* The matching between the selected and the displayed values of a param with a preset, which could differ if the preset couldn't be applied: in this case, the param is reverted to its default value.
* Playblast rendering at sequence level

## [2.0.3] - 2022-02-09

### Added

* An option in playblast rendering actions to scale the render resolution given a percentage.

## [2.0.2] - 2022-02-03

### Changed

* Hide dependency request option on working copies.
* A warning dialog shows up when one is about to download a revision already available locally.

### Added

* Icons for revision options

### Fixed

* File upload to Kitsu
* Force stored revision paths to contain slashes (`/`) only to ensure they are correctly interpreted by Unix systems when revisions are synced.
* Waiting download jobs which reference revisions unavailable on the exchange server are not processed.
* When submitted, a synchronisation job stored the local path of the referenced revision, rooted at the current site's root directory. This ineluctably raised a conflict when the job was processed from another site with a different root path.  
  Instead, only the revision relative path is stored, and its local path is computed on the fly, when the job is processed.

## [2.0.1] - 2022-02-02

### Added

* Added a path format property to file objects, used by default to generate revision paths.
* A system allowing to configure and create default files.

### Fixed

* Ensure local paths are valid on Windows, Linux and MacOS systems.
* Fix tracked file `is_empty` method when used to check if the file is empty on the current site.

## [2.0.0] - 2022-01-28

### IMPORTANT NOTE

This 2.x version of Libreflow embed many changes, including way more speed for map components, using a MongoDB service. Thus, it requires the setup of a MongoDB for Libreflow to work.

### Changed

* Use `kabaret.flow_entities` extension to manage file system objects (files, revisions, synchronisation statutes) and site synchronisation queues in a Mongo database.
* Encapsulate file transfert operations in a single object hold by the exchange site.
* Revision paths are stored in the database.
* Revision paths can be generated and updated based on the content of the revision's contextual settings.
* Hide file publish option on locked files and when the current user has no working copy on them.

### Added

* Add an action to test the connection to the file exchange server.

### Fixed

* Warn the user when an unavailable revision is double-clicked.
* Hide revision request option if the revision is already available on the exchange server.
* Hide revision upload option if the revision isn't available.
* Hide user's bookmarks if not registered in the project's users.
* Hide Kitsu options if the project's Kitsu settings aren't configured.

## [1.6.30] - 2021-12-16

### Added

* A preset system for each user which pre-fills option parameters (available for *Upload to Kitsu*, publication and playblast rendering options)

## [1.6.29] - 2021-12-03

### Fixed

* Temporary forced gazu dependency version, as latest version is making trouble to connect

## [1.6.28] - 2021-11-30

### Fixed

* Publish from history: fix window display error
* Publish from history: ensure that the revision is uploaded (when *Upload After Publish* enabled) and Blender dependencies are saved.

## [1.6.27] - 2021-11-25

### Changed

* Add -autoRetime 0 option to RV launcher, so that sequences with different frame rates are kept in sync.

### Added

* Playblast: add options to reduce texture sizes and set target texture size
* Publish: hide *Upload After Publish* option for files matching one of the patterns provided in the project settings

## [1.6.26] - 2021-11-15

### Changed

* Improve synchronization job management: show requested revisions in the history, reset erroneous jobs

### Added

* A site option to automatically upload playblasts to the exchange server while they are being uploaded to Kitsu.

### Fixed

* Don't store parameters of user environment variable creation dialog in the DB, to avoid access conflicts between sessions.

## [1.6.25] - 2021-11-08

### Fixed

* Add a missed synchronization icon, preventing the project root page to display entirely.

## [1.6.24] - 2021-11-08

### Changed

* Do not copy in current folder anymore when publishing.

### Fixed

* Correct the warning message that appears when opening a file edited by other users.
* So far, site environment variables could only be redefined for a single OS. These variables have now one value for each OS (Linux, Darwin or Windows), active depending on the OS being used.
* Fix crash when trying to create a tracked folder's empty working copy folder while it already exists.
* Create a user's profile upon the first login
* Users can log in using their Kitsu desktop login or email

## [1.6.23] - 2021-10-14

### Added

* The possibility to select the columns to display in the job list, by right-clicking on the list header.
* Application versions can be overriden in a department's contextual environment. This can be achieved creating a variable that follows the naming convention `<RUNNER_NAME>_VERSION` in the environment map of a department (option `Show Environment`).  
  **NB:** In order for overrides to be effective, one must have defined the executable paths corresponding to the runner overriden versions, either in the system, site or user environment. For instance, setting Blender version used in a given department to `2.93` requires the `BLENDER_2_93_EXEC_PATH` variable to be set up. Otherwise, the application will launch in its default version.

## [1.6.22] - 2021-09-30

### Added

* A launchable session which deletes jobs emitted before a given date, daily at a given time. Additionally, the cleaning process can stop on some days of the week specified by the user.
* Allow users to add sequences to their bookmarks.

### Fixed

* The job view now reacts to job creation and deletion events. This allows two optimisations:
  - Items are added/removed as jobs are created/deleted, without a complete refresh of the list
  - The job list is built once, the first time the view is shown
* First step toward chaining jobs: When generating the playblast of an AfterEffects scene, ensure the generated image sequence is marked only when the job in charge of the rendering has terminated.

## [1.6.21] - 2021-09-20

### Fixed

* Speed up the display time of the waiting job count on the synchronization section, updating a counter at site level as files are requested and synchronized.
* Allow to upload playblasts to Kitsu in tasks of different types.

## [1.6.20] - 2021-09-13

### Added

* A parameter to set the MinIO server bucket name, which can be set in the current exchange site.
* `Upload after publish` option is now enabled by default for all files matching one of the patterns provided in the projet settings.

### Fixed

* Site names are cached in the order defined in the current site, improving the time for histories to display.
* Prevent users from synchronizing files if the exchange server is not configured.

## [1.6.19] - 2021-09-09

### Fixed

* Download MinIO's intermediate files in a folder at the project's root path, named `.tmp`, to ensure that the drive of intermediate files is the same as that of the final downloaded files.
  - Fixes 1.6.18 synchronisation error occuring at download when the project root drive and the OS temporary folder drive differ.

## [1.6.18] - 2021-09-07

### Fixed

* Minimise the risk of exceeding the maximum path length on Windows when using MinIO API to download a file from the exchange server, using a custom intermediate temporary file.

## [1.6.17] - 2021-09-01

### Added

* A new session to periodically clear synchronisation jobs.
* An option to compare the playblasts of two tasks of a shot in Shotgun RV. Available tasks: layout, blocking, animation, compositing

### Changed

* Remove unused options (locking, open with...) on files.
* Rework the _Publish and playblast_ option for Blender files, and define it for AfterEffects files. Make this option accessible right under the _Publish_ option.

### Fixed

* Ensure that image sequence rendering and playblast generation for AfterEffects scenes are **processed the same way: locally or on a jobs node session**. In the latter case, ensure that both steps are **handled in the same pool**.
* Add `fileseq` to the project's dependencies, needed to render AfterEffects playblasts.
* Prevent the user from publishing in a non-editable file, and from creating a working copy when the file is double-clicked.

## [1.6.16] - 2021-08-24

### Added

* An option to upload all playblasts of a sequence to the right tasks in Kitsu.
  - If a task type is provided in the Kitsu data of a task (in the dependency template), it is used in priority for all files belonging to this task.
* An option to request revisions towards multiple sites, with an automatic source site selection option.

### Changed

* Do not pack AfterEffects playblast images after they have been rendered (cf. 1.6.12 folder packing update).
* Mark playblast images with the name of the original AfterEffects scene (or the containing folder's, if it doesn't exist) instead of the resulting playblast name.

### Fixed

* One can validate credentials pressing the Enter key.

## [1.6.15] - 2021-08-17

### Fixed

* Handle synchronization errors, now reported in the log of jobs.

## [1.6.14] - 2021-08-11

### Fixed

* Options to request a single revision and its dependencies.

## [1.6.13] - 2021-08-03

### Added

* Each site can define a custom list of site names to change their display order in file histories and request option windows (these now include `Request` and `Request as` options available on a single revision).
* OBJ file format
* The possibility to define shot elements that are not requestable, which can be achieved adding a `requestable` entry in the data of the element in the shot dependency template.

### Changed

* Request actions have been revised.

## [1.6.12] - 2021-07-20

### Changed

* The content of a tracked folder revision is packed/unpacked only when it needs to be uploaded to/downloaded from the exchange server.

## [1.6.11] - 2021-07-19

### Added

* A set of job and action classes to render playblasts of After Effects scenes. The procedure is made in two steps:
  - The image sequence rendering. This step can be achieved in a subprocess or using a job.
  - The marking of images to generate the playblast. When using the `Render Image Sequence`, this step is handled in a job by default. This step is also available as a standalone option on any tracked folder which contains at least one image; in this case, the generate of the playblast can be achieved in a subprocess or using a job.

### Changed

* By default, a file's history displays only the synchronisation statutes of sites considered as active on the project.
* Display synchronisation statutes and site short names by default in a file's history.

* Sequence playblast rendering action has been update in order to render playblasts of After Effects scenes existing (depending on the defined shot dependencies).

### Fixed

* Ensure that the source site and creator of sequence marking jobs are the same as those of the image rendering jobs.

## [1.6.10] - 2021-07-07

### Fixed

* Sequence playblast rendering action dialog:
  - Make the first available head revision be the default selected revision
  - Make unavailable revisions unselectable
* Ensure runner types are registered when the project root is touched. This fixes the case where a runner is not found when launching an application, because the project root has not been accessed at least once.
* Systematically remove the content of the `current` revision folder when a revision is made current. This prevents the packaging of files already present in the `current` folder, making the archive grow each time a revision is made current.

## [1.6.9] - 2021-07-01

### Fixed

* Make runner id accessible to the submitted job when rendering a playblast.

## [1.6.8] - 2021-07-01

### Fixed

* The setting of the environment variable holding a runner executable path has been moved, so that every RunAction which aims at opening a file properly updates the current environment before launching its corresponding runner.

## [1.6.7] - 2021-06-28

### Added

* An action to render playblasts of Blender scenes of a whole sequence.  
**Note:** This early version needs the different tasks of a shot (e.g., layout, animation, etc.) to be explicitly defined in a dependency template named `shot`.

### Changed

* An application executable path is searched in the different environments just before launching the application, in the following order of priority: System environment > user environment > site environment.

### Fixed

* Added status icons with lowercase names to prevent resource lookup error on Linux.

## [1.6.6] - 2021-06-23

### Fixed

* When a user logs in, the Libreflow ID (computed from the Kitsu ID) is changed to lowercase before the map of users is looked up. This prevents multiple users from having the same IDs with different character cases, and thus ensures the same behaviour in Windows and Linux when the user creates and access working copies.

## [1.6.5] - 2021-06-09

### Fixed

* All files in a tracked folder working copy are properly zipped when a publication is made.
* Make the revision upload after publication work again.
* Make *Keep editing* option work again when publishing a working copy from a file history.

### Added

* Brute-force integration of the `kabaret.jobs` module implementation (with subtle corrections) to manage jobs.
* Based on `kabaret.jobs`, the possibility for studios to handle playblast renderings as jobs.
  - Jobs can be submitted in one of the pools of the current site.
  - The feature can be used choosing the `Submit job` option when rendering a playblast.
* Adaptations of `kabaret.jobs`:
  - Make view's job filter case-sensitive, and include pool name in filtering attributes
  - Provide a job with a label and definable owner and creator
  - Define a JOBS_DEFAULT_FILTER environment variable, usable by the JobsView as a default filter. If not explicitly provided at session startup, the variable defaults to the current site name.

## [1.6.4] - 2021-05-27

### Added

* Allow Kitsu admin sites to upload playblasts toward any Kitsu task type available for the project.

### Changed

* Users are warned whenever one or more users have a working copy on a file, but are not prevented anymore from publishing in that case.
* Reference revision name in the dialog to create a working copy is set to the file's last publication name by default (if it exists).

## [1.6.3] - 2021-05-21

### Fixed

* Copy of runner command to clipboard is handled by native Qt application clipboard object, instead of TKinter features (not integrated to Python main package on all LInux distributions).
* A new action to request elements related to a shot (assets, scenes, misc), including their dependencies.

## [1.6.2] - 2021-05-20

### Added

* Runner implementation provides additional information, such as the command used, the time of the last run, etc.
* A panel in the `SubprocessView` displays information about the currently selected runner.
* A new option in the `SubprocessView` menu allows to hide completed runner instances.

### Fixed

* A runner instance is now identified by a Universal Unique Identifier, which eases its deletion in the subprocess manager.

## [1.6.1] - 2021-05-11

### Added

* A new flow utility function `get_context_value` can be used to recursively find and concatenate the values of all flow params of a given name declared in the parents of an object, including itself. To improve the flexibility of the context value parameterisation, the function makes use of the contextual dict when param values are specified between braces.

## [1.6.0] - 2021-05-11

### Added

* A new `kabaret.subprocess_manager` utility module has been created to redefine and extend the core classes of the original Kabaret extension.
  - Core classes have been extended to keep track of runner instances.
  - A bunch of commands has been added to manage the underlying processes of these instances (launch, terminate, kill).
  - A new view, which inherits from the original `SubprocessView`, lists all the runners instanciated from the current session, and allow to display the output of the subprocess launched by the selected runner in the list. For now, the list has to be manually refreshed.
* A shortcut to the current site's job queue is available in the *Synchronization* section of the project's root page.

### Changed

* The base runner class has been adapted as required by the first version of the `SubprocessView`. Notable changes are:
  - The redirection of both *stdout* and *stderr* of the subprocess to the same file.
  - Additional data and operators to manage the subprocess, usable by the actor commands.

### Fixed

* The SubprocessManager does not add a runner's data in the list of runner infos if it has not run at least once. This is a temporary check which prevents from accessing unavailable data about a subprocess, because currently not provided by some runner types (e.g. `DefaultEditor`).

## [1.5.12] - 2021-05-07

### Fixed

* Exchange sites have been removed from the `RequestAs` action's lists of requesting and requested sites.
* The revision published in a target file is automatically made current. Consequently, the last comment in the file list updates to the published revision's comment.
* Revision upload after publishing into another file has been fixed.

### Added

* A new action allows to upload a published revision on the exchange server.

## [1.5.11] - 2021-05-04

### Changed

* Playblast upload dialog messages have been reworked.

### Fixed

* An additional test checks if the current's user data retrieved with Kitsu API provides the user's role. If not, the user is considered as not having the required rights to upload the target playblast while not assigned to the corresponding task.

## [1.5.10] - 2021-04-30

### Fixed

* The revision drop-down menu display isn't raising an error anymore when the file reference is not set.

### Added

* The option to use simplified rigs has been made available on the action dialog to publish and render a playblast.
* JSX file format is available.

## [1.5.9] - 2021-04-22

### Fixed

* Kitsu entity data is retrieved only when the preview uploading action shows up or run (not in the constructor). This fixes an issue occuring whenever the action object was instantiated, since it tried to get data from flow object not yet instantiated.

## [1.5.8] - 2021-04-22

### Fixed

* Checking if a user is assigned to a Kitsu task is done exclusively by the preview uploading action. This means the internal function used to upload a preview assumes the user has sufficient rights.

## [1.5.7] - 2021-04-22

### Changed

* Kitsu supervisors and studio managers can upload previews regardless of their task assignment.

## [1.5.6] - 2021-04-22

### Changed

* Two choice values have been redefined to select a file's revision:
  - One list all available revisions of the file
  - The other list all available published revisions
* Revision type (working copy or publication) is no longer checked from the revision creator's name but a name pattern (currently, `v\d\d\d`).

## [1.5.5] - 2021-04-21

### Added

* A new action allows to upload files with eligible names as Kitsu previews. For now, uploadable files are defined in the project's Kitsu configuration.

### Changed

* Change time format in log files, to make it human readable

## [1.5.4] - 2021-04-20

### Fixed

* Single files are checked to see if they match a folder in the flow, before checking if they match a file. It prevents folders containing a single file from being considered files.

## [1.5.3] - 2021-04-20

### Added

* Two new features of the Blender playblast are used by the playblast action:
  - to enable the use of low-definition rigs in the Blender scene, available as a checkbox
  - to print on the sequence the name of the selected revision
* A new action `GetDependencies` allows to summarise dependency information of a given object and request all those which can be requested.
  - As of now, real dependencies are collected from the Blender Asset Tracer tracing result. The feature is thus truly practical for Blender files, and dependencies related to files of any other format remain theoretical.

### Changed

* Open file action displays by default last revision, or user's working copy if it does not exist.
* A revision is systematically made current when published.

### Fixed

* Project root path is added to the environment when opening a revision from a file history.
* File relation to department has been temporarily removed, allowing to define files elsewhere than in a department.
* Users can publish in files which are not related to a department in the flow.

## [1.5.2] - 2021-04-16

### Added

* Login page shows up when accessing bookmarks if user is not connected to Kitsu.

## [1.5.1] - 2021-04-02

### Fixed

* Publishing into another file creates the necessary intermediate directories when the target file has not been created on the current site.

## [1.5.0] - 2021-04-01

### Added

* JSON file format has been made available.
* libreflow.utils.b3d has been created with a wrapper for python-expressions to handle specific launch cases on windows.

### Fixed

* The python expression wrapper is applied to playblasts so they work when Blender is called through a .bat file.

## [1.4.3] - 2021-03-30

* Force Kabaret version to 2.2.0rc2

## [1.4.2] - 2021-03-26

### Changed

* Allow the creation of working copies only on authorised files.

### Fixed

* A workaround has been added to make GUI display on latest MacOS version ([Kabaret issue #96](https://gitlab.com/kabaretstudio/kabaret/-/issues/96)).
* Requested and requesting sites are properly taken into account when requesting revisions.

### Added

* An additional parameter on revisions indicates if they are ready for synchronisation. A typical use case motivating this change is to prevent files not entirely created and initialised to be synchronised.
* An action now allows to request (for both source and target sites) elements of a given sequence.
  - Requestable elements: sets, characters, props, sound files, storyboards and layout scenes
* An action allows to resize all PNG images in a tracked folder revision into another tracked folder. Resulting tracked folder has the same name of source folder suffixed with *_half*.
* Revision oid pattern has been updated:
  - to include multiple subpatterns separated by `;`
  - so that each subpattern can include multiple substrings in the form `{substring0, substring1, ...}`
* A new action now allows to remove jobs emitted for a site before a given date, and of given type and status.

## [1.4.1] - 2021-03-22

### Fixed

* Redefinition of TrackedFolder `open` and `history` related types have been removed, as it mistakenly redefined the same relations in the TrackedFile class.
* Force the indices of `open` and `history` in TrackedFolder relation list to be the same as for TrackedFile in order to bypass submenu display issue.

## [1.4.0] - 2021-03-22

### Changed

* The way the names of new users are computed has been updated to take into account mail IDs.
* User class is now injectable

### Added

* A warning message appears in home page when the computed name of a new user is already registered in the project's user list.
* Revisions now hold a dict of dependencies stored at publication. This feature applies exclusively for Blender files using pil library `blender-asset-tracer` (aka BAT) which is now mandatory.


### Fixed

* Submenus show up again when right clicking on tracked folders.

## [1.3.4] - 2021-03-18

### Changed

* Publish action has been made injectable.
* Some improvements on advanced action dialogs have been made (message content, reset of file reference).

## [1.3.3] - 2021-03-16

### Added

* Action for requesting file revisions now displays a list of found oids given a wildcard-based oid pattern (** not supported).
* Using *[last]* keyword in the pattern allows to get the latest published revision of a file. For instance, according to how the base flow is currently designed, `/project/sequences/*/shots/*/departments/*/files/*/history/revisions/[last]` allows to retrieve the latest publications of all files of the project named `project`.

## [1.3.2] - 2021-03-15

### Fixed

* Action for requesting file revisions does not stop anymore when it falls onto a revision already available on requesting site, or not available on requested site.
* Current user is stored when profile has not already been registered.

### Changed

* Actions on tracked files have been refined and reorganised.

## Added

* Two new actions on tracked files allow respectively:
  - to publish changes made in a file into another file
  - to create a working copy on a file from a selected revision of another file
* Users can now publish their changes made to a file from their working copy in the revision history.

## [1.3.1] - 2021-03-10

### Changed

* project settings are now injectable

## [1.3.0] - 2021-03-10

### Added

* File maps now display tracked element latest revisions and their availability. These can be requested directly from the file map.

### Changed

* Site definitions have been updated to distinguish working and exchange sites. 
* Exchange server configuration is held by the project's exchange site.
* A working site's job queue can be accessed by right-clicking on its entry in the site map.
* Default exchange site has been renamed as *default_site*, to be distinguished from default working site.

### Fixed

* Job emission date is stored as a floating point timestamp (not a formatted date string anymore) to be easily processed.
* Corrections on file list UI for untracked items.
* Publication option is not available anymore when rendering a playblast on a Blender file if the user hasn't a working copy on this file. This fixes an error which causes the resulting publication to be empty.

## [1.2.8] - 2021-03-10

### Fixed

* Logout from project has been fixed.

## [1.2.7] - 2021-03-09

### Fixed

* Subprocess environments are updated with the current site's root path. In particular, this makes root path, required in scene builder, accessible in Blender environment whenever a Blender scene is opened from Libreflow.

### Added

* Subprocess extra environments also include the current user name and contextual settings.

## [1.2.6] - 2021-03-05

### Fixed

* Added FBX file format in PyPI package data to make FBX template available.

## [1.2.5] - 2021-03-01

* Omitted in 1.2.4: *script* folder made as a valid Python package.

## [1.2.4] - 2021-03-01

### Added

* An action to batch revisions request as another site (currently not publicly available).

### Changed

* A new Blender template file.

### Fixed

* *script* folder made as a valid Python package.
* Project object is systematically touched when accessed from a home page widget to ensure user environment update.

## [1.2.3] - 2021-02-15

### Added

MP4, Illustrator and FBX file formats support

### Changed

* Actions to render a Blender file playblast is available in the base flow. Moreover, rendering a revision playblast generate a revision of the same index in a .mov tracked file.  
* Map clearing action relations have been removed to prevent unfortunate deletions.  
* Folder hierarchy in which user settings are stored has been changed to *<user_folder>/.libreflow/<project_name>/<user_name>/<user_settings>.*. This allows:  
  - a single user to be part of multiple projects
  - multiple users to authenticate on a project on the same workstation.
* Revisions display the time elapsed since their publication

## [1.2.2] - 2021-02-09

### Fixed

- Change *Request* action allowing context condition

## [1.2.1] - 2021-02-09

### Changed

- User name is now computed from Kitsu ID at first connection
- Files and folders of any type can be revealed in file explorer

## [1.2.0] - 2021-02-08

### Changed

- Bookmarks have been changed from a local json file to a dedicated map on the project's flow. #12
- File extensions and icons are now constants
- Revisions and TrackedFiles are now injectable
- A site can now request file revisions for other sites, if authorized (*request_files_from_anywhere* BoolParam).

### Added

- The project thumbnail flow can now be saved within the project admin/project settings area. So the thumbnail is available from anywhere no matter the site or OS. The old system is still present. #13

### Deprecated
- The old system for the thumbnail will soon be removed.

### Fixed
- At publish of a trackedFolder on python 3.7 an error appears because of a 3.8 update of stdlib shutil. Made a dirty fix for that.

## [1.1.7] - 2021-02-04

### Added

Users can log out from the project, sending them back to the login page.

### Fixed

User Kitsu id and the one used in the flow are distinguished, in order to ensure users are identified with a unique flow id which matches the pattern of a valid Python attribute, as required by Kabaret features. This currently implies users working on the project to be registered in this map.

## [1.1.6] - 2021-02-01

### Fixed

File data formats have been added in *setup.py* to make template files available within PyPI package.
Unforgivable hard-coded paths of several scripts have been changed for relative ones.

## [1.1.5] - 2021-01-29

### Fixed

Fix revision playblast rendering: Get playblast folder path from *Computed* department path.

## [1.1.4] - 2021-01-29

### Fixed

Fix revision upload: *Revision.get_relative_path()* gets parent file Computed path, instead of wrongly accessing *get_contextual_dict*.

## [1.1.3] - 2021-01-29

### Fixed

Until now, the computation of *File* and *Revision* paths implied implying a costly non-linear look-up of contextual edits, and long wait for maps to display. There is now only one contextual settings look-up to compute a *Department* path, from which department's file paths are computed and cached.

## [1.1.2] - 2021-01-21

### Fixed

User environment map items are now *SessionValue*s to make environment variable values stored at session's scope.

## [1.1.1] - 2021-01-20

### Fixed

MinIO and timeago added in setuptools requirements.

## [1.1.0] - 2021-01-20

*Multisite v1 release*

### Added 

- A ComputedParam named `root_dir` is now available in admin and it's cached as requiered by issue #4. A function `get_root()` at the Project level use it and is able to provide the root folder of the project according to the operative system. Call it from anywhere in the flow with `self.root().project().get_root()`.
- `CHANGELOG.md`, `LICENCE` and `AUTORS` files have been added to the repo
- **Multi-site** file synchronization features (related to issue #5):
  - Add and configure project's sites (type - studio, user or exchange -, per-OS root directories, exchange server properties)
  - Request tracked file's revisions unavailable on current site for download, based on a job submission feature
  - A `SynchronizeFile` action allow users to process files they requested, and files other sites requested from theirs. This currently uses a MinIO client.
  - Retrieve the current site and exchange site in the flow with `self.root().project().[get_current_site()|get_exchange_site()]`
  - UI improvement: revision history maps can toggle site sync statuses
- Runners redirect their logs in a file placed in the user folder (bce8aadf)
- A new `DefaultRunner` is available to let the OS choose the default application for a given file path.
- Previews and renders of AfterEffects file revisions can be launched at revision and episode level, given AfterEffectsRender render settings and output module templates
- Playblasts of blender file revisions can be made with an action (*preview* folder created in department's files if not already added)
- Md5 hash is computed for publishes for later features (cc0478e8)

### Changed

- According to the new `get_root()` function added and requiered by issue #4, the default contextual dict doens't provide a `ROOT_DIR` value anymore. Calls to that value have been changed, and you must define `ROOT_DIR_WINDOWS`, `ROOT_DIR_LINUX` and/or `ROOT_DIR_MAC` in the admin panel.
- Cosmetic changes to get some maps expanded or not (832605d8).
- There is no need to manually specify the user folder anymore: project's `get_user_folder()` method now returns the path to a `.libreflow` in the user's home directory.
- For sake of readability, file maps showcase the time elapsed since file last modification, instead of date (59d364a8).

## [1.0.3] - 2020-12-24

### Fixed

issue #7 libreflow icons are missing from the distributed package (and also the example packages where not accessible)

## [1.0.2-1.0.1] - 2020-12-23

Initial public commit and pypi setup. This version is an early version of libreflow. It includes a baseflow and examples flows overriding the baseflow. We have been working on departments, files, file version history, and stuff like that.

### Fixed

issue #6 : Pip Package is now ready for use


[^1]: Except we started libreflow MAJOR version number at 1, as we consider our in-house previous flow being version 0.