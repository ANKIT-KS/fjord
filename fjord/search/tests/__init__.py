import time

from django.conf import settings

import factory
from elasticsearch.exceptions import NotFoundError

from fjord.base.tests import BaseTestCase
from fjord.search.index import get_index, get_es
from fjord.search.models import Record


class ElasticTestCase(BaseTestCase):
    """Base class for Elastic Search tests, providing some conveniences"""
    @classmethod
    def setUpClass(cls):
        super(ElasticTestCase, cls).setUpClass()

        cls._old_es_index_prefix = settings.ES_INDEX_PREFIX
        settings.ES_INDEX_PREFIX = settings.ES_INDEX_PREFIX + 'test'

    @classmethod
    def tearDownClass(cls):
        super(ElasticTestCase, cls).tearDownClass()

        # Restore old setting.
        settings.ES_INDEX_PREFIX = cls._old_es_index_prefix

    def setUp(self):
        super(ElasticTestCase, self).setUp()
        self.setup_indexes()

    def tearDown(self):
        super(ElasticTestCase, self).tearDown()
        self.teardown_indexes()

    def refresh(self, timesleep=0):
        index = get_index()

        # Any time we're doing a refresh, we're making sure that the
        # index is ready to be queried.  Given that, it's almost
        # always the case that we want to run all the generated tasks,
        # then refresh.
        # TODO: uncomment this when we have live indexing.
        # generate_tasks()

        get_es().indices.refresh(index)
        if timesleep > 0:
            time.sleep(timesleep)

    def setup_indexes(self, empty=False, wait=True):
        """(Re-)create ES indexes."""
        from fjord.search.index import es_reindex_cmd

        if empty:
            # Removes the index and creates a new one with nothing in
            # it (by abusing the percent argument).
            es_reindex_cmd(percent=0)
        else:
            # Removes the index, creates a new one, and indexes
            # existing data into it.
            es_reindex_cmd()

        self.refresh()
        if wait:
            get_es().cluster.health(wait_for_status='yellow')

    def teardown_indexes(self):
        es = get_es()
        try:
            es.indices.delete(get_index())
        except NotFoundError:
            # If we get this error, it means the index didn't exist
            # so there's nothing to delete.
            pass


class RecordFactory(factory.DjangoModelFactory):
    class Meta:
        model = Record

    batch_id = 'ou812'
    name = 'Frank'
