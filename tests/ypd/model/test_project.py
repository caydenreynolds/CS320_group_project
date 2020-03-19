import os
import tempfile
from unittest import TestCase
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ypd.model import Base, project


class TestProject(TestCase):
    
    @classmethod
    def setUpClass(self):
        self.engine = create_engine('sqlite:///')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def setUp(self):
        self.session = self.Session(bind=self.engine)
        project.Session = self.Session

    def tearDown(self):
        self.session.query(project.Provided).delete()
        self.session.commit()
        self.session.close()

    @patch.object(project, 'Session')
    def test_project_post_unit(self, mock_session):
        mock_session.return_value = mock_session
        p = project.Provided()
        p.post('foo', 'bar', 0)
        mock_session.assert_called_once()
        mock_session.add.assert_called_once_with(p)
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_project_post_integration(self):
        p = project.Provided()
        p.post('foo', 'bar', 0)

        results = self.session.query(project.Provided).all()
        self.assertEqual(len(results), 1)

        self.assertEqual(results[0].id, p.id)
        self.assertEqual(results[0].title, 'foo')
        self.assertEqual(results[0].description, 'bar')
        self.assertEqual(results[0].date, p.date)
        self.assertEqual(results[0].archived, False)
        self.assertEqual(results[0].needsReview, False)
        
    def test_selected_project_lookup(self):                                     # tests to see that get method works
        s = project.Provided()
        s.post('cookie', 'biscuit', 0)
        
        s = project.Provided.get(1)
        self.assertIsNotNone(s)
        self.assertTrue(s.title == 'cookie' and s.description == 'biscuit')
