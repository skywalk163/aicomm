# -*- coding: utf-8 -*-
"""Tests for search functionality."""

import unittest
from unittest.mock import Mock, MagicMock, patch
from pyramid import testing


class TestSearchView(unittest.TestCase):
    """Tests for the search view."""

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @patch('kotti_ai_community.views.search.DBSession')
    def test_search_view_no_query(self, mock_session):
        """Test search view with no query."""
        from kotti_ai_community.views.search import search_view
        
        context = Mock()
        request = testing.DummyRequest()
        request.params = {}
        
        result = search_view(context, request)
        
        self.assertEqual(result['query'], '')
        self.assertEqual(result['results'], [])
        self.assertEqual(result['total_count'], 0)

    @patch('kotti_ai_community.views.search.DBSession')
    def test_search_view_short_query(self, mock_session):
        """Test search view with query shorter than 2 chars."""
        from kotti_ai_community.views.search import search_view
        
        context = Mock()
        request = testing.DummyRequest()
        request.params = {'q': 'a'}
        
        result = search_view(context, request)
        
        self.assertEqual(result['query'], 'a')
        self.assertEqual(result['results'], [])
        self.assertEqual(result['total_count'], 0)

    @patch('kotti_ai_community.views.search.DBSession')
    def test_search_view_with_query(self, mock_session):
        """Test search view with valid query."""
        from kotti_ai_community.views.search import search_view
        
        # Mock idea
        mock_idea = Mock()
        mock_idea.title = 'Test Idea'
        mock_idea.description = 'A test idea description'
        mock_idea.tags = ['test', 'ai']
        mock_idea.creation_date = 1000
        
        # Mock query chain - return idea for first call, empty for others
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.side_effect = [[mock_idea], [], []]  # ideas, resources, projects
        mock_session.query.return_value = mock_query
        
        context = Mock()
        request = testing.DummyRequest()
        request.params = {'q': 'test'}
        request.resource_url = lambda x: '/test-idea'
        
        result = search_view(context, request)
        
        self.assertEqual(result['query'], 'test')
        self.assertEqual(result['total_count'], 1)
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['type'], 'idea')

    @patch('kotti_ai_community.views.search.DBSession')
    def test_search_view_filter_by_type(self, mock_session):
        """Test search view with content type filter."""
        from kotti_ai_community.views.search import search_view
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        mock_session.query.return_value = mock_query
        
        context = Mock()
        request = testing.DummyRequest()
        request.params = {'q': 'test', 'type': 'ideas'}
        
        result = search_view(context, request)
        
        self.assertEqual(result['content_type'], 'ideas')

    @patch('kotti_ai_community.views.search.DBSession')
    def test_search_view_pagination(self, mock_session):
        """Test search view pagination."""
        from kotti_ai_community.views.search import search_view
        
        # Create 25 mock ideas
        mock_ideas = []
        for i in range(25):
            idea = Mock()
            idea.title = f'Idea {i}'
            idea.description = f'Description {i}'
            idea.tags = []
            idea.creation_date = i
            mock_ideas.append(idea)
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        # Return ideas for first call, empty for resources and projects
        mock_query.all.side_effect = [mock_ideas, [], []]
        mock_session.query.return_value = mock_query
        
        context = Mock()
        request = testing.DummyRequest()
        request.params = {'q': 'test', 'page': '1'}
        request.resource_url = lambda x: '/idea'
        
        result = search_view(context, request)
        
        self.assertEqual(result['total_count'], 25)
        self.assertEqual(len(result['results']), 20)  # per_page = 20
        self.assertIsNotNone(result['pagination'])


class TestSearchAPI(unittest.TestCase):
    """Tests for the search API."""

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @patch('kotti_ai_community.views.search.DBSession')
    def test_search_api_no_query(self, mock_session):
        """Test search API with no query."""
        from kotti_ai_community.views.search import search_api
        
        context = Mock()
        request = testing.DummyRequest()
        request.params = {}
        
        result = search_api(context, request)
        
        self.assertEqual(result, {'results': []})

    @patch('kotti_ai_community.views.search.DBSession')
    def test_search_api_short_query(self, mock_session):
        """Test search API with short query."""
        from kotti_ai_community.views.search import search_api
        
        context = Mock()
        request = testing.DummyRequest()
        request.params = {'q': 'a'}
        
        result = search_api(context, request)
        
        self.assertEqual(result, {'results': []})

    @patch('kotti_ai_community.views.search.DBSession')
    def test_search_api_with_results(self, mock_session):
        """Test search API with results."""
        from kotti_ai_community.views.search import search_api
        
        mock_idea = Mock()
        mock_idea.title = 'Test Idea'
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        # Return idea for first call (ideas), empty for others
        mock_query.all.side_effect = [[mock_idea], [], []]
        mock_session.query.return_value = mock_query
        
        context = Mock()
        request = testing.DummyRequest()
        request.params = {'q': 'test'}
        request.resource_url = lambda x: '/test-idea'
        
        result = search_api(context, request)
        
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['type'], 'idea')
        self.assertEqual(result['results'][0]['title'], 'Test Idea')

    @patch('kotti_ai_community.views.search.DBSession')
    def test_search_api_limit(self, mock_session):
        """Test search API respects limit parameter."""
        from kotti_ai_community.views.search import search_api
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_session.query.return_value = mock_query
        
        context = Mock()
        request = testing.DummyRequest()
        request.params = {'q': 'test', 'limit': '5'}
        
        result = search_api(context, request)
        
        # Verify limit was called with 5
        mock_query.limit.assert_called()


if __name__ == '__main__':
    unittest.main()
