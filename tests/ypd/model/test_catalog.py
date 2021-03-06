from unittest import TestCase
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ypd.model import Base, catalog, project, session_manager
from ypd.model.user import User

class TestProject(TestCase):
    
    @classmethod
    def setUpClass(self):
        self.engine = create_engine('sqlite:///')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        session_manager.Session = self.Session

    def setUp(self):
        self.session = self.Session()
        self.fake_project_list = ['these', "don't", 'need', 'to', 'be', 'real', 'projects']
        self.fake_catalog = catalog.Catalog()
        self.fake_catalog.projects = self.fake_project_list
        self.user = User(id=1, can_post_provided=True, can_post_solicited=True)

        project.Provided().post('foo', 'bar', self.user)
        project.Provided().post('nobody expects', 'the spanish inquisition', self.user)
        project.Provided().post('sperm whale', 'bowl of petunias', self.user)

    def tearDown(self):
        self.session.query(project.Provided).delete()
        self.session.query(project.Solicited).delete()
        self.session.commit()
        self.session.close()

    def test_apply_no_projects(self):
        self.session.query(project.Provided).delete()
        clg = catalog.Catalog('', True)
        clg.apply()
        self.assertEqual(clg.projects, [])

    def test_apply_many_projects(self):
        clg = catalog.Catalog('', True)
        clg.apply()

        self.assertEqual(len(clg.projects), 3)

        projects = []
        for proj in clg.projects:
            projects.append((proj.title, proj.description))

        self.assertTrue(('foo', 'bar') in projects)
        self.assertTrue(('nobody expects', 'the spanish inquisition') in projects)
        self.assertTrue(('sperm whale', 'bowl of petunias') in projects)

    def test_apply_chooses_correct_table(self):
        project.Provided().post('foo', 'bar', self.user)
        project.Solicited().post('your', 'mom', self.user)
        clg = catalog.Catalog('', False)
        clg.apply()

        self.assertEqual(len(clg.projects), 1)
        self.assertEqual(clg.projects[0].title, 'your')
        self.assertEqual(clg.projects[0].description, 'mom')

    def test_search_by_title_provided(self):
        search_term = 'foo'
        clg = catalog.Catalog(search_term, True)
        clg.apply()

        self.assertEqual(len(clg.projects), 1)
        self.assertEqual(clg.projects[0].title, 'foo')

    def test_contains(self):
        self.assertTrue('need' in self.fake_catalog)
        self.assertTrue('projects' in self.fake_catalog)

        self.assertFalse('foo' in self.fake_catalog)
        self.assertFalse('bar' in self.fake_catalog)

    def test_len(self):
        self.assertEqual(len(self.fake_catalog), 7)

    def test_getattr(self):
        self.assertEqual('need', self.fake_catalog[2])
        self.assertTrue('projects', self.fake_catalog[6])

        with self.assertRaises(IndexError):
            self.fake_catalog[12]

        i = 0
        for fake_project in self.fake_catalog:
            self.assertEqual(fake_project, self.fake_project_list[i])
            i += 1
            
    def test_append(self):
        p0 = self.session.query(project.Provided).filter_by(title='foo').one()
        p1 = self.session.query(project.Provided).filter_by(title='nobody expects').one()

        clg = catalog.Catalog('foo', True)
        clg.apply()
        clg.append(p1)
        self.assertEqual(len(clg), 2)
        self.assertEqual(clg[0].id, p0.id)
        self.assertEqual(clg[1].id, p1.id)

        with self.assertRaises(ValueError):
            clg.append(4)

    def test_extend(self):
        p0 = self.session.query(project.Provided).filter_by(title='foo').one()
        p1 = self.session.query(project.Provided).filter_by(title='nobody expects').one()
        p2 = self.session.query(project.Provided).filter_by(title='sperm whale').one()

        clg = catalog.Catalog('foo', True)
        clg.apply()
        clg.extend([p1, p2])
        self.assertEqual(len(clg), 3)
        self.assertEqual(clg[0].id, p0.id)
        self.assertEqual(clg[1].id, p1.id)
        self.assertEqual(clg[2].id, p2.id)

        with self.assertRaises(ValueError):
            clg.extend([p0, 4, p1])