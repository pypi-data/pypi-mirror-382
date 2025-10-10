import pymongo
import traceback
import re
import json

from bson.objectid import ObjectId

from kabaret import flow
from kabaret.app._actor import Actor, Cmd, Cmds


#------ CMDS


class SearchCmds(Cmds):
    '''
    '''


@SearchCmds.cmd
class Query_Index(Cmd):
    '''
    Returns a list of dicts describing the first `limit` entries
    of the search index matching the given `query_filter`.

    The dict keys are the following:
        id       : unique id of the entry
        goto_oid : id of the flow object corresponding to this entry
        label    : entry label
    '''
    def _decode(self, query_filter=None, limit=10, exclude_types=None):
        self._query_filter = query_filter
        self._limit = limit
        self._exclude_types = exclude_types

    def _execute(self):
        results = self.actor().query_index(
            self._query_filter,
            self._limit,
            self._exclude_types
        )
        return [r.to_dict() for r in results]


@SearchCmds.cmd
class Query_Project_Index(Cmd):
    '''
    Returns a list of dicts describing the first `limit` entries
    of the search index matching the given `query_filter` and
    referencing objects under the project `project_name`.

    The dict keys are similar to that returned by the Query_Index
    command.
    '''
    def _decode(self, project_name, query_filter=None, page=1, limit=10, exclude_types=None, include_types=None):
        self._project_name = project_name
        self._query_filter = query_filter
        self._page = page
        self._limit = limit
        self._exclude_types = exclude_types
        self._include_types = include_types

    def _execute(self):
        results,count = self.actor().query_project_index(
            self._project_name,
            self._query_filter,
            self._page,
            self._limit,
            self._exclude_types,
            self._include_types,
        )
        return [r.to_dict() for r in results], count


@SearchCmds.cmd
class Rebuild_Project_Index(Cmd):
    '''
    Rebuilds the index of search entries for the project
    with the given name using the registered filters.
    '''
    def _decode(self, project_name, start_oid=None, max_depth=None):
        self._project_name = project_name
        self._start_oid = start_oid
        self._max_depth = max_depth

    def _execute(self):
        self.actor().crawl_project(self._project_name, start_oid=self._start_oid, max_depth=self._max_depth)


@SearchCmds.cmd
class List_Project_Names(Cmd):
    '''
    Returns a list containing the names of all projects
    existing on the cluster.
    '''
    def _decode(self):
        pass

    def _execute(self):
        return self.actor().get_project_names()


@SearchCmds.cmd
class List_Indexing_Filters(Cmd):
    '''
    Returns the list of filters for automatic indexing
    as a list of 4D tuples, representing the two parts
    of a filter (cf. actor docstring).
    '''
    def _decode(self):
        pass

    def _execute(self):
        return self.actor().get_filters()


@SearchCmds.cmd
class Add_Indexing_Filter(Cmd):
    '''
    '''
    def _decode(self, pattern, targets, enabled, index_matches):
        self.pattern = pattern
        self.targets = targets
        self.enabled = enabled
        self.index_matches = index_matches

    def _execute(self):
        return self.actor().add_filter(self.pattern, self.targets, self.enabled, self.index_matches)


@SearchCmds.cmd
class Remove_Indexing_Filter(Cmd):
    '''
    '''
    def _decode(self, filter_id):
        self.id = filter_id

    def _execute(self):
        return self.actor().remove_filter(self.id)


@SearchCmds.cmd
class Update_Filter(Cmd):
    '''
    '''
    def _decode(self, filter_id, pattern, enabled, index_matches):
        self.id = filter_id
        self.pattern = pattern
        self.enabled = enabled
        self.index_matches = index_matches

    def _execute(self):
        return self.actor().update_filter(self.id, self.pattern, self.enabled, self.index_matches)


@SearchCmds.cmd
class Update_Filter_Targets(Cmd):
    '''
    '''
    def _decode(self, filter_id, targets):
        self.id = filter_id
        self.targets = targets

    def _execute(self):
        return self.actor().update_filter_targets(self.id, self.targets)


@SearchCmds.cmd
class Dump_Filter_Template(Cmd):
    '''
    Create a JSON template file from the list of existing filters.
    '''
    def _decode(self, file_path):
        self.file_path = file_path

    def _execute(self):
        return self.actor().dump_filter_template(self.file_path)


@SearchCmds.cmd
class Load_Filter_Template(Cmd):
    '''
    Create filters from a JSON template file.
    '''
    def _decode(self, file_path):
        self.file_path = file_path

    def _execute(self):
        return self.actor().load_filter_template(self.file_path)


#------ Actor


class SearchResult:

    def __init__(self, actor, document):
        self._actor = actor
        self._document = None
        
        self.set_document(document)
    
    def set_document(self, doc):
        self._document = doc
        self._document['id'] = self._document.pop('_id')
    
    def id(self):
        return str(self._document['id'])
    
    def goto_oid(self):
        return self._document['goto_oid']
    
    def label(self):
        return self._document['label']
    
    def to_dict(self):
        return self._document


class Search(Actor):
    '''
    The Search actor manages a single search index for all projects
    defined in the cluster.
    
    Search entries are indexed in the `Search:index` collection
    within the <CLUSTER_NAME> Mongo database.
    
    This actor automatically indexes the oids of touched flow objects
    according to a list of filters stored in the `Search:filters`
    collection. A filter has three parts:
      - the filter ID as a 12-byte unique identifier in hexadecimal format (see https://pymongo.readthedocs.io/en/stable/api/bson/objectid.html#bson.objectid.ObjectId)
      - the oid pattern used to filter touched objects
      - a list of oid patterns used to index matching oids relative to the filtered object
    '''

    def __init__(self, session, mongo_uri, auto_indexing=False):
        super(Search, self).__init__(session)
        
        self._mongo_uri = mongo_uri
        self._mongo_client = None
        self._auto_indexing = auto_indexing

        self.touch_unsubscribe = None
    
    def _create_cmds(self):
        return SearchCmds(self)
    
    def on_session_connected(self):
        self.log('Configuring Search Engine')
        cluster = self.session().get_actor('Cluster')
        cluster_name = cluster.get_cluster_name()
        
        self._mongo_client = pymongo.MongoClient(
            self._mongo_uri,
            appname=self.session().session_uid()
        )
        self._coll_index = self._mongo_client[cluster_name]['Search:index']
        self._coll_index.create_index([('goto_oid', 1)], unique=True)
        self._coll_filters = self._mongo_client[cluster_name]['Search:filters']

        self.log('Subcribing to flow_touched messages.')
        self.touch_unsubscribe = self.session().channels_subscribe(
            flow_touched=self._on_touch_message
        )
    
    def die(self):
        if self.touch_unsubscribe is not None:
            self.touch_unsubscribe()
    
    def get_result(self, document):
        return SearchResult(self, document)
    
    # def query_index(self, query_filter=None, limit=10, exclude_types=None):
    #     '''
    #     Returns the `limit` indexed search entries with the highest
    #     similarity score with the given filter, ordered by score.
    #     '''
    #     # TODO filter using a computed score
    #     if query_filter is None:
    #         query_filter = {}
    #     else:
    #         tokens = query_filter.split()
    #         query_filter = {'goto_oid': {'$regex': '.*'.join(tokens), '$options': 'i'}}
    #         if exclude_types:
    #             query_filter['type'] = {'$nin': exclude_types}
        
    #     results = [
    #         self.get_result(doc)
    #         for doc in self._coll_index.find(query_filter, limit=limit)
    #     ]
    #     return results

    def query_index(self, query_filter=None, page=1, limit=10, exclude_types=None, include_types=None):
        '''
        Returns the `limit` indexed search entries with the highest
        similarity score with the given filter, ordered by score.

        '''
        # TODO filter using a computed score
        if query_filter is None:
            query_filter = {}
        else:
            tokens = query_filter.split()
            query_filter = {'goto_oid': {'$regex': '.*'.join(tokens), '$options': 'i'}}
            if exclude_types:
                query_filter['type'] = {'$nin': exclude_types}
            
            if include_types:
                query_filter["type"] = (
                    query_filter["type"] | {"$in": include_types}
                    if "type" in query_filter
                    else {"$in": include_types}
                )

                # if 'type' in query_filter:
                #     query_filter['type'] += {'$in' : include_types}

                # else : 
                #     query_filter['type'] = {'$in' : include_types}
        
        match_stage = {"$match" : query_filter}
        # sort_stage = {"$sort" : {"score" : {"$meta": "textScore"}}} # --> sort by relevance
        # sort_stage = {"$sort" : {'_id' : -1 }} --> sort by date (recent to old)
        page_stage = {
                        "$facet" : {
                            'metadata': [{'$count': 'totalCount'}],
                            'data': [ {'$skip': (page -1)* limit}, {'$limit': limit} ],
                        }
                    }
        
        mongo_results = list(self._coll_index.aggregate([match_stage, page_stage]))[0]

        results = [ self.get_result(doc) for doc in mongo_results['data'] ]
        count = mongo_results['metadata'][0]['totalCount'] if mongo_results['metadata'] else 0
        return results, count
    
    def get_project_names(self):
        return [
            project_name for project_name, _ in self.session().get_actor('Flow').get_projects_info()
        ]
    
    # def query_project_index(self, project_name, query_filter=None, limit=10, exclude_types=None):
    #     if query_filter is not None and re.match(f'^/?{project_name}.*', query_filter) is None:
    #         query_filter = f'^/{project_name} {query_filter}'
        
    #     return self.query_index(query_filter, limit, exclude_types)

    def query_project_index(self, project_name, query_filter=None, page=1, limit=10, exclude_types=None, include_types=None):
        if query_filter is not None and re.match(f'^/?{project_name}.*', query_filter) is None:
            query_filter = f'^/{project_name} {query_filter}'
        
        return self.query_index(query_filter, page, limit, exclude_types, include_types)
    
    def build_project_indexes(self, oid_seed_list=None):
        self._coll_index.delete_many({})
        self.crawl_projects(oid_seed_list)
    
    def crawl_projects(self, oid_seed_list=None):
        '''
        oid_seed_list: list of tuples (oid seed, regex filter)
        '''
        for project_name, _ in self.session().get_actor('Flow').get_projects_info():
            self.crawl_project(project_name, oid_seed_list)
    
    def crawl_project(self, project_name, filters=None, start_oid=None, max_depth=-1):
        '''
        Crawls the project `project_name` and indexes all flow
        objects whose OIDs match the filters in the `filter` list.

        `filters` must be a list of 3D-tuples, each containing:
          - `filter`: an OID pattern used to filter objects
          - `start_oid` (optional): an OID to start the crawling from
          - `max_depth` (optional): a crawling depth limit (optional)
        
        If `filters` is `None`, the entire project tree is browsed
        according to the registered filters.
        '''
        if filters is None:
            filters = [{'filter': f[1]} for f in self.get_filters(index_matches_only=True)]

        for oid in self.glob_project(project_name, filters, start_oid=start_oid, max_depth=max_depth):
            try:
                self._create_entry(oid)
            except pymongo.errors.DuplicateKeyError:
                self._update_entry(oid)
                self.session().log_debug(f'[SEARCH] Exists : {oid}')
            else:
                self.session().log_info(f'[SEARCH] Added : {oid}')
    
    def glob_project(self, project_name, oid_filters, start_oid=None, max_depth=-1):
        '''
        Returns a list of OIDs of objects existing in the project `project_name`
        and matching the filter `oid_filter`.
        
        `oid_filter` must be a regular expression.
        
        If `start_oid` is not `None`, it defines the OID to start the browsing
        from, and the matching is performed against the relative OIDs; otherwise
        the function starts browsing from the project root, and the matching is
        performed against the full OIDs.

        The browsing is performed until the depth from the start OID reaches
        `max_depth`; if `max_depth` is negative, the function browses the entire
        project tree.
        '''
        if start_oid is None:
            start_oid = '/'+project_name
        elif not start_oid.startswith('/'+project_name):
            # Object identified by from_oid doesn't belong to the project
            return []
        else:
            start_oid = re.sub('/*$', '', start_oid)
        
        return self._glob(start_oid, oid_filters, 0, max_depth)
    
    def add_filter(self, pattern, targets=None, enabled=True, index_matches=False):
        '''
        Adds a filter for automatic indexing of touched flow object oids.

        TODO: Clarify targets data structure
        '''
        f = self._coll_filters.insert_one({
            'filter': pattern,
            'targets': targets,
            'enabled': enabled,
            'index_matches': index_matches
        })
        return f.inserted_id
    
    def update_filter(self, filter_id, pattern, enabled, index_matches):
        '''
        Set the pattern of the filter with the provided ID.

        TODO: Clarify targets data structure
        '''
        self._coll_filters.update_one(
            {'_id': ObjectId(filter_id)},
            {
                '$set': {
                    'filter': pattern,
                    'enabled': enabled,
                    'index_matches': index_matches
                }
            }
        )
    
    def update_filter_targets(self, filter_id, targets):
        '''
        Set the targets of the filter with the provided ID.

        TODO: Clarify targets data structure
        '''
        self._coll_filters.update_one({'_id': ObjectId(filter_id)}, {'$set': {'targets': targets}})
    
    def remove_filter(self, filter_id):
        self._coll_filters.delete_one({'_id': ObjectId(filter_id)})
    
    def index_targets(self, oid):
        '''
        For each filter the OID `oid` matches, searches and
        indexes the relative objects whose OIDs match the
        target patterns of enabled filters (see actor docstring).
        '''
        for f in self._coll_filters.find({'enabled': True}):
            if re.fullmatch(f['filter'], oid) is not None:
                if f['index_matches']:
                    if not self._has_entry(oid):
                        self._create_entry(oid)
                        self.session().log_info(f'[SEARCH] Added : {oid}')
                    else:
                        self.session().log_debug(f'[SEARCH] Exists : {oid}')

                filters = [
                    { 'filter': target[0], 'start_oid': oid, 'max_depth': int(target[1]) }
                    for target in f['targets']
                ]

                self.crawl_project(oid.split('/')[1], filters)
    
    def get_filters(self, index_matches_only=False):
        _filter = {'enabled': True, 'index_matches': True} if index_matches_only else {}

        return [
            (str(f['_id']), f['filter'], f['targets'], f['enabled'], f['index_matches'])
            for f in self._coll_filters.find(_filter)
        ]
    
    def dump_filter_template(self, file_path):
        filters = [
            { 'filter': f[1], 'targets': f[2], 'enabled': f[3], 'index_matches': f[4] }
            for f in self.get_filters()
        ]

        with open(file_path, 'w') as f:
            json.dump(filters, f, indent=4)
    
    def load_filter_template(self, file_path):
        with open(file_path, 'r') as f:
            try:
                json_filters = json.load(f)
            except json.JSONDecodeError:
                self.session().log_error(' Invalid filter template file {} (it must be a valid JSON file)')
            else:
                self._coll_filters.delete_many({})

                for f in json_filters:
                    targets = [
                        (t[0], int(t[1]))
                        for t in f['targets']
                    ]
                    self.add_filter(f['filter'], targets, f['enabled'], f['index_matches'])
    
    def _on_touch_message(self, message):
        oid = message['data']
        if self._auto_indexing:
            self.index_targets(oid)
            
    def _glob(self, oid, oid_filters, depth, max_depth=-1):
        matches = []

        for f in oid_filters:
            if re.fullmatch(f['filter'], oid) is not None:
                matches.append(oid)
        
        if depth == max_depth:
            return matches

        for child_oid in self._ls(oid):
            matches += self._glob(child_oid, oid_filters, depth + 1, max_depth)
        
        return matches

    def _get_relation_infos(self, parent, relation):
        if relation.related_type is not None:
            if issubclass(relation.related_type, flow.Action):
                return None
            if issubclass(relation.related_type, flow.values.Value):
                return None

        if relation.relation_type_name() == 'Relative':
            # Replace Related with their source
            # when possible:
            related = getattr(parent, relation.name)
            if related is None:
                relative_oid = relation.get_relative_oid(parent)
                if relative_oid is None:
                    return None # hide the relation
                return (
                    # Use the target oid so that GUI can display it:
                    os.path.join(
                        parent.oid(), relative_oid
                    )
                )
        else:
            related = getattr(parent, relation.name)

        return (
            related.oid()
        )

    def _get_mapped_names(self, o):
        if not isinstance(o, flow.MAP_TYPES):
            return []
        return o.mapped_names()
    
    def _ls(self, oid):
        '''
        Returns a list of OIDs of all children of the object
        with the provided OID, excluding parent relations.

        If an exception occurs during the listing, an empty
        list is returned and the exception is reported in stdout.
        '''
        child_oids = []

        try:
            o = self.session().get_actor('Flow').get_object(oid)

            related_info = [
                self._get_relation_infos(o, relation)
                for relation in o._mng.relations()
            ]
            related_info = [i for i in related_info if i is not None]
            mapped_names = self._get_mapped_names(o)

            from_relations = (related_info, mapped_names)
        except Exception as e:
            self.session().log_error(f'Search :: error while calling LS command on object {oid}')
            print(traceback.format_exc())
        else:
            child_oids = [
                child_oid for child_oid in from_relations[0]
                if child_oid.startswith(oid)
            ]
            child_oids += [oid+'/'+mapped_name for mapped_name in from_relations[1]]
        
        return child_oids
    
    def _create_entry(self, oid):
        self._coll_index.insert_one({
            'goto_oid': oid,
            'label': self.session().cmds.Flow.get_source_display(oid),
            'type': type(self.session().get_actor('Flow').get_object(oid)).__name__
        })
    
    def _update_entry(self, oid):
        self._coll_index.update_one(
            {'goto_oid': oid},
            {
                '$set': {
                    'label': self.session().cmds.Flow.get_source_display(oid),
                    'type': type(self.session().get_actor('Flow').get_object(oid)).__name__
                }
            }
        )
    
    def _has_entry(self, oid):
        ret = self._coll_index.find_one({
            'goto_oid': oid
        })
        # print([r for r in ret])
        # print(ret)
        return ret is not None
