import time

from kabaret import flow
from kabaret.flow_entities.entities import Entity, EntityCollection, PropertyValue


class PropertyChoiceValue(PropertyValue):
    '''
    This class defines a PropertyValue providing the same features
    as the base ChoiceValue.
    '''

    DEFAULT_EDITOR = 'choice'

    STRICT_CHOICES = True
    CHOICES = []

    def choices(self):
        return self.__class__.CHOICES

    def set(self, value):
        if self.STRICT_CHOICES and value not in self.choices():
            # we still touch ourself, so we sure GUI refresh with the unchanged value:
            self.touch()
            raise ValueError('Invalid value %r. Should be one of %r' %
                             (value, self.choices()))
        super(PropertyChoiceValue, self).set(value)


class CustomEntity(Entity):

    def get_properties(self, *property_names):
        return self._collection.get_properties(self.name(), *property_names)


class CustomEntityCollection(EntityCollection):
    '''
    A collection provided with operators to add and remove single elements.
    '''

    def columns(self):
        return ['Name']
    
    def add(self, name, object_type=None):
        '''
        Adds an object to the map.
        If provided, object_type must be a subclass of the map's mapped_type
        (returned by the classmethod mapped_type())
        '''
        mapped_type = flow.injection.resolve(
            self.mapped_type(), self
        )

        # Check file type
        if object_type is None:
            object_type = mapped_type
        elif not issubclass(object_type, mapped_type):
            raise TypeError(
                'Cannot add %r of type %r to Map %r: not a subclass of %r' % (
                    name, object_type, self.oid(), mapped_type
                )
            )

        # Check file name
        if '.' in name:
            raise TypeError(
                'Invalid object name %r (it must be a valid attribute name).' % (name,))
        try:
            exec(name + '=None') in {}
        except:
            raise TypeError(
                'Invalid object name %r (it must be a valid attribute name).' % (name,))
        if name in dir(self):
            raise ValueError(
                'Cannot add an item "%r", this name is already defined in the class "%s" (%s).' %
                (
                    name, self.__class__.__name__, self._mng.oid()
                )
            )
        
        if self.has_mapped_name(name):
            raise ValueError(
                'An item %r is already mapped in %r.' %
                (
                    name, self._mng.oid()
                )
            )

        object_qualified_type_name = self._mng.get_qualified_type_name(object_type)

        # Add entry to project's Mongo store
        self.get_entity_store().get_collection(self.collection_name()).insert_one({
            'name': self._get_mapped_item_name(name),
            'mapped_type': object_qualified_type_name
        })
        self._document_cache = None # Reset cache

        return self.get_mapped(name)

    def remove(self, name):
        '''
        Removes an Entity from the map.
        '''
        try:
            self._mng.destroy_child(name)
        except flow.MissingChildError:
            # was not yet instantiated, nothing to destroy
            pass

        self.get_entity_store().get_collection(self.collection_name()).delete_one(
            {'name': self._get_mapped_item_name(name)}
        )
        self._document_cache = None # Reset cache
    
    def clear(self):
        '''
        Clears all Entities belonging to this map.
        '''
        for name in self.mapped_names():
            try:
                self._mng.destroy_child(name)
            except flow.MissingChildError:
                # was not yet instantiated, nothing to destroy
                pass
        
        self.get_entity_store().get_collection(self.collection_name()).delete_many(
            self.query_filter()
        )
        self._document_cache = None # Reset cache
    
    def set_property(self, entity_name, property_name, value):
        self.get_entity_store().get_collection(self.collection_name()).update_one(
            {"name": self._get_mapped_item_name(entity_name)},
            {"$set": {property_name: value}},
            upsert=True
        )

    def get_property(self, entity_name, property_name):
        self.root().session().log_debug(f'===========> {self._get_mapped_item_name(entity_name)} {property_name}')
        name = self._get_mapped_item_name(entity_name)
        
        if (
            self._document_cache is None
            or self._document_cache_birth < time.time() - self._document_cache_ttl
            or entity_name not in self._document_cache
        ):
            value = (
                self.get_entity_store()
                .get_collection(self.collection_name())
                .find_one(
                    {"name": name},
                    {property_name: 1},
                )
             )
        else:
            value = self._document_cache[name]
        
        try:
            return value[property_name]
        except (KeyError, TypeError):
            return getattr(self._get_mapped_item_type(entity_name), property_name).get_default_value()
    
    def get_properties(self, entity_name, *property_names):
        '''
        Returns the values of the given properties as a dict.

        This method assumes that all the requested properties exist in this entity.
        '''
        name = self._get_mapped_item_name(entity_name)

        if (
            self._document_cache is None
            or self._document_cache_birth < time.time() - self._document_cache_ttl
            or entity_name not in self._document_cache
        ):
            doc = (
                self.get_entity_store()
                .get_collection(self.collection_name())
                .find_one(
                    {"name": name},
                    {
                        property_name: True
                        for property_name in property_names
                    },
                )
            )
        else:
            doc = self._document_cache[name]
        values = {}

        for property_name in property_names:
            try:
                values[property_name] = doc[property_name]
            except (KeyError, TypeError):
                values[property_name] = getattr(self.mapped_type(), property_name).get_default_value()

        return values
    
    def _fill_row_cells(self, row, item):
        row['Name'] = item.name()

    def _get_mapped_item_type(self, mapped_name):
        self.mapped_names()
        
        name = self._get_mapped_item_name(mapped_name)
        object_qualified_type_name = self._document_cache[name].get('mapped_type', None)
        
        if object_qualified_type_name is None:
            return self.mapped_type()
        
        try:
            object_type = self._mng.qualified_type_name_to_type(
                object_qualified_type_name
            )
        except ImportError:
            object_type = self.mapped_type()
            self.root().session().log_debug(
                'WARNING: unable to access type %r. Downgrading to map default type %r' % (
                    object_qualified_type_name, object_type
                )
            )
        
        return object_type
    
    def _get_mapped_item_name(self, name):
        '''
        Returns the actual mapped name used to map the item identified
        by `name` in the flow.

        A typical use is mapping an entity in a collection with a name
        which differs from its name in the flow.
        Default is to return its original flow name.
        '''
        return name


class GlobalEntityCollection(EntityCollection):
    '''
    An entity collection which stores entities at the scope of an entire project.

    Entities of this collection are mapped by their oids.
    '''
    
    def columns(self):
        return ['Oid', 'Type']
    
    def _fill_row_cells(self, row, item):
        self.mapped_names()

        oid = item.oid()
        row['Oid'] = oid
        row['Type'] = self._document_cache[oid].get(
            'mapped_type',
            self._mng.get_qualified_type_name(self.mapped_type())
        )
    
    def get_mapped(self, name):
        return self.root().get_object(name)


class EntityView(CustomEntityCollection):
    '''
    A collection acting as a view on a subset of a GlobalEntityCollection.

    User may return the global collection name in the `collection_name()` method.
    '''

    def mapped_names(self, page_num=0, page_size=None):
        oids = super(EntityView, self).mapped_names(page_num, page_size)
        return [oid.rsplit('/', maxsplit=1)[-1] for oid in oids]
    
    def query_filter(self):
        return {'name': {'$regex': f'^{self.oid()}/[^/]*'}}
    
    def _get_mapped_item_name(self, name):
        return self.oid() + '/' + name
