# import uuid
import hashlib
from kabaret import flow
from kabaret.flow.exceptions import MissingChildError, MissingRelationError, RefSourceError, RefSourceTypeError
from kabaret.flow_entities.entities import Entity, Property

from ..kabaret.flow_entities.entities import EntityView


# class UnlinkEntityRef(flow.Action):

#     _ref = flow.Parent()
#     _map = flow.Parent(2)

#     def get_buttons(self):
#         return ['Confirm', 'Cancel']
    
#     def run(self, button):
#         if button == 'Cancel':
#             return
        
#         _map = self._map
#         _map.remove(self._ref.name())
#         _map.touch()


class EntityRef(Entity):
    '''
    The EntityRef provides the same features as those of a Ref,
    except it is a Mongo entity.
    '''

    ICON = 'ref'
    DEFAULT_EDITOR = 'ref'

    SOURCE_TYPE = None  # class_or_type_or_tuple

    source_oid = Property()

    # unlink = flow.Child(UnlinkEntityRef)

    @staticmethod
    def resolve_refs(object):
        max = 10
        nb = 0
        while isinstance(object, EntityRef):
            object = object.get()
            nb += 1
            if nb > max:
                raise RuntimeError('Maximum recursion exceeded')
        return object

    def __init__(self, parent, name):
        super(EntityRef, self).__init__(parent, name)
        self.source_object = None
        self._allow_cross_project = False
    
    def set_allow_cross_project(self, b):
        self._allow_cross_project = b

    def get(self):
        source_oid = self.get_source_oid()
        if self.source_object is None or self.source_object.oid() != source_oid:
            if source_oid is None:
                return None
            try:
                self.source_object = self._mng.get_object(source_oid)
            except (MissingChildError, MissingRelationError):
                raise RefSourceError(self.oid(), source_oid)

        return self.source_object

    def get_source_oid(self):
        return self.source_oid.get()
    
    def get_goto_oid(self):
        return self.get_source_oid()

    def can_set(self, source_object):
        try:
            self._assert_source_compatible(source_object)
        except ValueError:
            return False

        source_object = self.resolve_refs(source_object)

        try:
            self._validate_source_object(source_object)
        except RefSourceTypeError:
            return False
        else:
            return True

    def _assert_source_compatible(self, object):
        if not self._allow_cross_project and object.root() is not self.root():
            raise ValueError('Cannot connect to another flow!')

    def _validate_source_object(self, source_object):
        if source_object is not None:
            if self.SOURCE_TYPE is not None and not isinstance(source_object, self.SOURCE_TYPE):
                if 0:
                    # was too geeky :/
                    raise RefSourceTypeError(
                        'Ref %s cannot point to %r (should be a %r, but is a %s)' % (
                            self.oid(), source_object.oid(), self.SOURCE_TYPE, source_object.__class__
                        )
                    )
                else:
                    raise RefSourceTypeError(
                        'This is not a %s' % (self.SOURCE_TYPE.__name__,))
        return source_object

    def set(self, new_source_object):

        if new_source_object is not None:
            self._assert_source_compatible(new_source_object)
            new_source_object = self.resolve_refs(new_source_object)
            new_source_object = self._validate_source_object(new_source_object)
            new_oid = new_source_object.oid()
        else:
            new_oid = None

        old_source_oid = self.get_source_oid()
        if old_source_oid == new_oid:
            return

        self.source_oid.set(new_oid)
        if old_source_oid is not None:
            try:
                old_source_object = self._mng.get_object(old_source_oid)
            except (MissingChildError, MissingRelationError):
                pass
            else:
                old_source_object._mng.remove_ref(self)

        self.source_object = new_source_object
        if self.source_object is not None:
            self.source_object._mng.add_ref(self)


class EntityRefMap(EntityView):

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(EntityRef)
    
    def add_ref(self, source_oid):
        o = self.root().get_object(source_oid)
        name = self._get_mapped_name(source_oid)
        ref = self.add(name)
        ref.set(o)
        return ref
    
    def has_ref(self, source_oid):
        name = self._get_mapped_name(source_oid)
        return self.has_mapped_name(name)
    
    def remove_ref(self, source_oid):
        name = self._get_mapped_name(source_oid)
        ref = self.get_mapped(name)
        ref.set(None)
        self.remove(name)
    
    def can_handle(self, source_oid):
        try:
            o = self.root().get_object(source_oid)
        except (flow.MissingChildError, flow.MissingRelationError):
            return False
        else:
            return isinstance(o, self.mapped_type().SOURCE_TYPE)
    
    def _get_mapped_name(self, source_oid):
        return 'ref'+hashlib.sha1(source_oid.encode('UTF-8')).hexdigest()
