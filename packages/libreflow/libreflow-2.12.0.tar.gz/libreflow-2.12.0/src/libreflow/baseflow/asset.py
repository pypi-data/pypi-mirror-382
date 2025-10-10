from kabaret import flow
from kabaret.flow_entities.entities import Entity, Property
from kabaret.flow_contextual_dict import ContextualView
from libreflow.baseflow import Project

from .maputils import SimpleCreateAction
from ..utils.kabaret.flow_entities.entities import EntityView


class Asset(Entity):
    """
    Defines a asset.

    Instances provide the `asset` key in their contextual
    dictionary (`settings` context).
    """

    ICON = ('icons.flow', 'asset')

    code = Property().ui(hidden=True)
    display_name = Property().ui(hidden=True)

    settings = flow.Child(ContextualView).ui(hidden=True)

    @classmethod
    def get_source_display(cls, oid):
        split = oid.split('/')
        indices = list(range(len(split) - 1, 2, -2))
        return ' – '.join([split[i] for i in reversed(indices)])
    
    def get_code(self):
        return self.code.get() or self.name()

    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(
                asset=self.name(),
                asset_code=self.get_code(),
                asset_display_name=self.display_name.get()
            )


class AssetCollection(EntityView):
    """
    Defines a collection of assets.
    """

    ICON = ('icons.flow', 'asset')

    add_asset = flow.Child(SimpleCreateAction)
    
    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(Asset)
    
    def collection_name(self):
        mgr = self.root().project().get_entity_manager()
        return mgr.get_asset_collection().collection_name()
    
    def _fill_row_cells(self, row, item):
        row['Name'] = item.display_name.get() or item.name()


class AssetFamily(Entity):
    """
    Defines a asset family containing a list of assets.

    Instances provide the `asset_family` key in their contextual
    dictionary (`settings` context).
    """

    ICON = ('icons.flow', 'asset_family')

    code = Property().ui(hidden=True)
    display_name = Property().ui(hidden=True)

    assets = flow.Child(AssetCollection).injectable().ui(
        expanded=True, show_filter=True
    )

    settings = flow.Child(ContextualView).ui(hidden=True)

    @classmethod
    def get_source_display(cls, oid):
        split = oid.split('/')
        indices = list(range(len(split) - 1, 2, -2))
        return ' – '.join([split[i] for i in reversed(indices)])

    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(
                asset_family=self.name(),
                asset_family_code=self.code.get(),
                asset_family_display_name=self.code.get()
            )


class AssetFamilyCollection(EntityView):
    """
    Defines a collection of asset families.
    """

    ICON = ('icons.flow', 'asset_family')

    add_asset_family = flow.Child(SimpleCreateAction)
    
    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(AssetFamily)
    
    def collection_name(self):
        mgr = self.root().project().get_entity_manager()
        return mgr.get_asset_family_collection().collection_name()
    
    def _fill_row_cells(self, row, item):
        row['Name'] = item.display_name.get() or item.name()


class AssetType(Entity):
    """
    Defines a asset type containing a list of asset families.

    Instances provide the `asset_type` key in their contextual
    dictionary (`settings` context).
    """

    ICON = ('icons.flow', 'asset_family')

    code = Property().ui(hidden=True)
    display_name = Property().ui(hidden=True)

    asset_families = flow.Child(AssetFamilyCollection).ui(show_filter=True).injectable()

    settings = flow.Child(ContextualView).ui(hidden=True)

    @classmethod
    def get_source_display(cls, oid):
        split = oid.split('/')
        indices = list(range(len(split) - 1, 2, -2))
        return ' – '.join([split[i] for i in reversed(indices)])

    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(
                asset_type=self.name(),
                asset_type_code=self.code.get(),
                asset_type_display_name=self.display_name.get(),
            )


class AssetTypeCollection(EntityView):
    """
    Defines a collection of asset types.
    """

    ICON = ('icons.flow', 'bank')

    add_asset_type = flow.Child(SimpleCreateAction)

    _parent = flow.Parent(1)
    
    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(AssetType)
    
    def collection_name(self):
        mgr = self.root().project().get_entity_manager()
        return mgr.get_asset_type_collection().collection_name()
    
    def _fill_row_cells(self, row, item):
        row['Name'] = item.display_name.get() or item.name()

    def _fill_ui(self, ui):
        kitsu_config = self.root().project().kitsu_config()

        if (
            kitsu_config.project_type.get() == 'tvshow'
            and isinstance(self._parent, Project)
        ):
            ui['hidden'] = True
        else:
            ui['hidden'] = False


class AssetLibrary(Entity):
    """
    Defines an asset library containing a list of asset types.

    Instances provide the `asset_lib` and `asset_lib_code` keys
    in their contextual dictionary (`settings` context).
    """

    ICON = ('icons.flow', 'bank')

    code = Property().ui(hidden=True)
    display_name = Property().ui(hidden=True)

    asset_types = flow.Child(AssetTypeCollection).ui(expanded=True).injectable()

    @classmethod
    def get_source_display(cls, oid):
        split = oid.split('/')
        indices = list(range(len(split) - 1, 2, -2))
        return ' – '.join([split[i] for i in reversed(indices)])

    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(
                asset_lib=self.name(),
                asset_lib_code=self.code.get(),
                asset_lib_display_name=self.display_name.get()
            )


class AssetLibraryCollection(EntityView):
    """
    Defines a collection of asset libraries.
    """

    ICON = ('icons.flow', 'bank')

    add_asset_lib = flow.Child(SimpleCreateAction).ui(label='Add asset library')
    
    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(AssetLibrary)
    
    def collection_name(self):
        mgr = self.root().project().get_entity_manager()
        return mgr.get_asset_library_collection().collection_name()

    def _fill_row_cells(self, row, item):
        row['Name'] = item.display_name.get() or item.name()

    def _fill_ui(self, ui):
        # For the moment, this collection is used when the project is a tvshow on Kitsu.
        kitsu_config = self.root().project().kitsu_config()
        ui['hidden'] = True if kitsu_config.project_type.get() != 'tvshow' else False
