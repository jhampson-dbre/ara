#  Copyright (c) 2017 Red Hat, Inc.
#
#  This file is part of ARA: Ansible Run Analysis.
#
#  ARA is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ARA is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ARA.  If not, see <http://www.gnu.org/licenses/>.

import os
import pytest
import six

from distutils.version import LooseVersion
from flask_frozen import MissingURLGeneratorWarning
from glob import glob
from lxml import etree
from oslo_serialization import jsonutils
from subunit._to_disk import to_disk

import ara.shell
import ara.cli.record
import ara.cli.generate
import ara.cli.host
import ara.cli.play
import ara.cli.playbook
import ara.cli.result
import ara.cli.task

from ara.api.files import FileApi
from ara.api.hosts import HostApi
from ara.api.plays import PlayApi
from ara.api.playbooks import PlaybookApi
from ara.api.records import RecordApi
from ara.api.results import ResultApi
from ara.api.tasks import TaskApi

from ara.tests.unit.fakes import FakeRun
from ara.tests.unit.common import TestAra


class TestCLIRecord(TestAra):
    """ Tests for the ARA CLI record commands """
    def setUp(self):
        super(TestCLIRecord, self).setUp()

    def tearDown(self):
        super(TestCLIRecord, self).tearDown()

    def test_record_list(self):
        ctx = FakeRun()

        cmd = ara.cli.record.RecordList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['-a'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['records'][0]['id'])

    def test_record_list_for_playbook(self):
        ctx = FakeRun()

        cmd = ara.cli.record.RecordList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '--playbook',
            six.text_type(ctx.playbook['id'])
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['records'][0]['id'])

    def test_record_list_for_non_existing_playbook(self):
        cmd = ara.cli.record.RecordList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_record_show_by_id(self):
        ctx = FakeRun()

        cmd = ara.cli.record.RecordShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            six.text_type(ctx.playbook['records'][0]['id'])
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx.playbook['records'][0]['id'])

    def test_record_show_by_key(self):
        ctx = FakeRun()

        # Get record
        record = RecordApi().get(id=ctx.playbook['records'][0]['id'])
        record = jsonutils.loads(record.data)

        cmd = ara.cli.record.RecordShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '-b',
            six.text_type(ctx.playbook['id']),
            record['key']
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], record['id'])

    def test_record_show_for_non_existing_data(self):
        cmd = ara.cli.record.RecordShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLIHost(TestAra):
    """ Tests for the ARA CLI host commands """
    def setUp(self):
        super(TestCLIHost, self).setUp()

    def tearDown(self):
        super(TestCLIHost, self).tearDown()

    def test_host_list(self):
        ctx = FakeRun()

        cmd = ara.cli.host.HostList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['-a'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['hosts'][0]['id'])

    def test_host_list_for_playbook(self):
        ctx = FakeRun()

        cmd = ara.cli.host.HostList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '--playbook',
            six.text_type(ctx.playbook['id'])
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['hosts'][0]['id'])

    def test_host_list_for_non_existing_playbook(self):
        cmd = ara.cli.host.HostList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_host_show_by_id(self):
        ctx = FakeRun()

        cmd = ara.cli.host.HostShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            six.text_type(ctx.playbook['hosts'][0]['id'])
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx.playbook['hosts'][0]['id'])

    def test_host_show_by_name(self):
        ctx = FakeRun()

        # Get host
        host = HostApi().get(id=ctx.playbook['hosts'][0]['id'])
        host = jsonutils.loads(host.data)

        cmd = ara.cli.host.HostShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '-b',
            six.text_type(ctx.playbook['id']),
            host['name']
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], host['id'])

    def test_host_show_for_non_existing_host(self):
        cmd = ara.cli.host.HostShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLIPlay(TestAra):
    """ Tests for the ARA CLI play commands """
    def setUp(self):
        super(TestCLIPlay, self).setUp()

    def tearDown(self):
        super(TestCLIPlay, self).tearDown()

    def test_play_list_all(self):
        ctx = FakeRun()

        cmd = ara.cli.play.PlayList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--all'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.play['id'])

    def test_play_list_playbook(self):
        ctx = FakeRun()

        cmd = ara.cli.play.PlayList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '--playbook',
            six.text_type(ctx.playbook['id'])
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.play['id'])

    def test_play_list_non_existing_playbook(self):
        cmd = ara.cli.play.PlayList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_play_show(self):
        ctx = FakeRun()

        cmd = ara.cli.play.PlayShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([six.text_type(ctx.play['id'])])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx.play['id'])

    def test_play_show_non_existing(self):
        cmd = ara.cli.play.PlayShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLIPlaybook(TestAra):
    """ Tests for the ARA CLI playbook commands """
    def setUp(self):
        super(TestCLIPlaybook, self).setUp()

    def tearDown(self):
        super(TestCLIPlaybook, self).tearDown()

    def test_playbook_list(self):
        ctx = FakeRun()

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['id'])

    def test_playbook_list_complete(self):
        ctx = FakeRun()

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--complete'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['id'])

    def test_playbook_list_complete_with_no_complete(self):
        FakeRun(completed=False)

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--complete'])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_playbook_list_incomplete(self):
        ctx = FakeRun(completed=False)

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--incomplete'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['id'])

    def test_playbook_list_incomplete_with_no_incomplete(self):
        FakeRun()

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--incomplete'])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_playbook_show(self):
        ctx = FakeRun()

        cmd = ara.cli.playbook.PlaybookShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([six.text_type(ctx.playbook['id'])])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx.playbook['id'])

    def test_playbook_show_non_existing(self):
        cmd = ara.cli.playbook.PlaybookShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)

    def test_playbook_delete(self):
        # Run two playbook runs
        ctx = FakeRun()
        FakeRun()

        # Assert that we have two playbooks and that we have valid data for
        # the first playbook
        playbooks = PlaybookApi().get()
        playbooks = jsonutils.loads(playbooks.data)
        self.assertTrue(len(playbooks) == 2)

        # Validate that we have real data for this playbook
        files = FileApi().get(playbook_id=ctx.playbook['id'])
        self.assertNotEqual(len(jsonutils.loads(files.data)), 0)

        hosts = HostApi().get(playbook_id=ctx.playbook['id'])
        self.assertNotEqual(len(jsonutils.loads(hosts.data)), 0)

        plays = PlayApi().get(playbook_id=ctx.playbook['id'])
        self.assertNotEqual(len(jsonutils.loads(plays.data)), 0)

        tasks = TaskApi().get(playbook_id=ctx.playbook['id'])
        self.assertNotEqual(len(jsonutils.loads(tasks.data)), 0)

        results = ResultApi().get(playbook_id=ctx.playbook['id'])
        self.assertNotEqual(len(jsonutils.loads(results.data)), 0)

        # Delete the playbook
        cmd = ara.cli.playbook.PlaybookDelete(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([six.text_type(ctx.playbook['id'])])
        cmd.take_action(args)

        # Assert that we only have one playbook left and that records have been
        # deleted
        playbooks = PlaybookApi().get()
        playbooks = jsonutils.loads(playbooks.data)
        self.assertTrue(len(playbooks) == 1)

        # Assert that we have no data for the first playbook
        playbook = PlaybookApi().get(id=ctx.playbook['id'])
        self.assertEqual(playbook.status_code, 404)

        # Validate that we nog longer have any data for this playbook
        files = FileApi().get(playbook_id=ctx.playbook['id'])
        self.assertEqual(files.status_code, 404)

        hosts = HostApi().get(playbook_id=ctx.playbook['id'])
        self.assertEqual(hosts.status_code, 404)

        plays = PlayApi().get(playbook_id=ctx.playbook['id'])
        self.assertEqual(plays.status_code, 404)

        tasks = TaskApi().get(playbook_id=ctx.playbook['id'])
        self.assertEqual(tasks.status_code, 404)

        results = ResultApi().get(playbook_id=ctx.playbook['id'])
        self.assertEqual(results.status_code, 404)


class TestCLIResult(TestAra):
    """ Tests for the ARA CLI result commands """
    def setUp(self):
        super(TestCLIResult, self).setUp()

    def tearDown(self):
        super(TestCLIResult, self).tearDown()

    def test_result_list_all(self):
        ctx = FakeRun()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--all'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['results'][0]['id'])

    def test_result_list_playbook(self):
        ctx = FakeRun()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '--playbook',
            six.text_type(ctx.playbook['id'])
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['results'][0]['id'])

    def test_result_list_non_existing_playbook(self):
        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_result_list_play(self):
        ctx = FakeRun()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--play', six.text_type(ctx.play['id'])])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['results'][0]['id'])

    def test_result_list_non_existing_play(self):
        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--play', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_result_list_task(self):
        ctx = FakeRun()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--task', six.text_type(ctx.t_ok['id'])])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['results'][0]['id'])

    def test_result_list_non_existing_task(self):
        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--task', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_result_show(self):
        ctx = FakeRun()

        cmd = ara.cli.result.ResultShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            six.text_type(ctx.playbook['results'][0]['id'])
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx.playbook['results'][0]['id'])

    def test_result_show_non_existing(self):
        cmd = ara.cli.result.ResultShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)

    def test_result_show_long(self):
        ctx = FakeRun()

        # Get result
        result = ResultApi().get(id=ctx.playbook['results'][0]['id'])
        result = jsonutils.loads(result.data)

        cmd = ara.cli.result.ResultShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            six.text_type(ctx.playbook['results'][0]['id']), '--long'
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx.playbook['results'][0]['id'])
        self.assertEqual(res[1][-1], jsonutils.dumps(result['result'],
                                                     indent=4))

    def test_result_show_long_non_existing(self):
        cmd = ara.cli.result.ResultShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0, '--long'])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLITask(TestAra):
    """ Tests for the ARA CLI task commands """
    def setUp(self):
        super(TestCLITask, self).setUp()

    def tearDown(self):
        super(TestCLITask, self).tearDown()

    def test_task_list_all(self):
        ctx = FakeRun()

        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--all'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.t_ok['id'])

    def test_task_list_play(self):
        ctx = FakeRun()

        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--play', six.text_type(ctx.play['id'])])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.t_ok['id'])

    def test_task_list_non_existing_play(self):
        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--play', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_task_list_playbook(self):
        ctx = FakeRun()

        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '--playbook',
            six.text_type(ctx.playbook['id'])
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.t_ok['id'])

    def test_task_list_non_existing_playbook(self):
        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_task_show(self):
        ctx = FakeRun()

        cmd = ara.cli.task.TaskShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([six.text_type(ctx.t_ok['id'])])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx.t_ok['id'])

    def test_task_show_non_existing(self):
        cmd = ara.cli.task.TaskShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLIGenerate(TestAra):
    """ Tests for the ARA CLI generate commands """
    def setUp(self):
        super(TestCLIGenerate, self).setUp()

    def tearDown(self):
        super(TestCLIGenerate, self).tearDown()

    def test_generate_empty_html(self):
        """ Ensures the application is still rendered gracefully """
        self.app.config['ARA_IGNORE_EMPTY_GENERATION'] = False
        shell = ara.shell.AraCli()
        shell.prepare_to_run_command(ara.cli.generate.GenerateHtml)
        cmd = ara.cli.generate.GenerateHtml(shell, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([self.tmpdir])

        with pytest.warns(MissingURLGeneratorWarning) as warnings:
            cmd.take_action(args)

        # pytest 3.0 through 3.1 are backwards incompatible here
        if LooseVersion(pytest.__version__) >= LooseVersion('3.1.0'):
            cat = [item._category_name for item in warnings]
            self.assertTrue(any('MissingURLGeneratorWarning' in c
                                for c in cat))
        else:
            self.assertTrue(any(MissingURLGeneratorWarning == w.category
                                for w in warnings))

        paths = [
            os.path.join(self.tmpdir, 'index.html'),
            os.path.join(self.tmpdir, 'static'),
        ]

        for path in paths:
            self.assertTrue(os.path.exists(path))

    def test_generate_empty_html_with_ignore_empty_generation(self):
        """ Ensures the application is still rendered gracefully """
        self.app.config['ARA_IGNORE_EMPTY_GENERATION'] = True

        shell = ara.shell.AraCli()
        shell.prepare_to_run_command(ara.cli.generate.GenerateHtml)
        cmd = ara.cli.generate.GenerateHtml(shell, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([self.tmpdir])
        cmd.take_action(args)

        paths = [
            os.path.join(self.tmpdir, 'index.html'),
            os.path.join(self.tmpdir, 'static'),
        ]

        for path in paths:
            self.assertTrue(os.path.exists(path))

    def test_generate_html_no_destination(self):
        """ Ensures generating without a destination fails """
        FakeRun()

        cmd = ara.cli.generate.GenerateHtml(None, None)
        parser = cmd.get_parser('test')

        with self.assertRaises(SystemExit):
            args = parser.parse_args([])
            cmd.take_action(args)

    def test_generate_html(self):
        """ Roughly ensures the expected files are generated properly """
        ctx = FakeRun()

        shell = ara.shell.AraCli()
        shell.prepare_to_run_command(ara.cli.generate.GenerateHtml)
        cmd = ara.cli.generate.GenerateHtml(shell, None)
        parser = cmd.get_parser('test')

        args = parser.parse_args([self.tmpdir])
        cmd.take_action(args)

        file_id = ctx.playbook['files'][0]['id']
        host_id = ctx.playbook['hosts'][0]['id']
        result_id = ctx.playbook['results'][0]['id']
        paths = [
            os.path.join(self.tmpdir, 'index.html'),
            os.path.join(self.tmpdir, 'static'),
            os.path.join(self.tmpdir, 'file/index.html'),
            os.path.join(self.tmpdir, 'file/{0}'.format(file_id)),
            os.path.join(self.tmpdir, 'host/index.html'),
            os.path.join(self.tmpdir, 'host/{0}'.format(host_id)),
            os.path.join(self.tmpdir, 'reports/index.html'),
            os.path.join(self.tmpdir, 'result/index.html'),
            os.path.join(self.tmpdir, 'result/{0}'.format(result_id))
        ]

        for path in paths:
            self.assertTrue(os.path.exists(path))

    def test_generate_html_for_playbook(self):
        """ Roughly ensures the expected files are generated properly """
        # Record two separate playbooks
        ctx = FakeRun()
        ctx_two = FakeRun()

        shell = ara.shell.AraCli()
        shell.prepare_to_run_command(ara.cli.generate.GenerateHtml)
        cmd = ara.cli.generate.GenerateHtml(shell, None)
        parser = cmd.get_parser('test')

        args = parser.parse_args([
            self.tmpdir,
            '--playbook',
            six.text_type(ctx.playbook['id'])
        ])
        cmd.take_action(args)

        file_id = ctx.playbook['files'][0]['id']
        host_id = ctx.playbook['hosts'][0]['id']
        result_id = ctx.playbook['results'][0]['id']
        paths = [
            os.path.join(self.tmpdir, 'index.html'),
            os.path.join(self.tmpdir, 'static'),
            os.path.join(self.tmpdir, 'file/index.html'),
            os.path.join(self.tmpdir, 'file/{0}'.format(file_id)),
            os.path.join(self.tmpdir, 'host/index.html'),
            os.path.join(self.tmpdir, 'host/{0}'.format(host_id)),
            os.path.join(self.tmpdir, 'reports/index.html'),
            os.path.join(self.tmpdir, 'result/index.html'),
            os.path.join(self.tmpdir, 'result/{0}'.format(result_id))
        ]

        for path in paths:
            self.assertTrue(os.path.exists(path))

        # Retrieve the other playbook and validate that we haven't generated
        # files for it
        path = os.path.join(self.tmpdir,
                            'playbook/{0}'.format(ctx_two.playbook['id']))
        self.assertFalse(os.path.exists(path))

    def test_generate_junit(self):
        """ Roughly ensures the expected xml is generated properly """
        ctx = FakeRun()
        cmd = ara.cli.generate.GenerateJunit(None, None)
        parser = cmd.get_parser('test')

        junit_file = '{0}/junit.xml'.format(self.tmpdir)
        args = parser.parse_args([junit_file])
        cmd.take_action(args)

        self.assertTrue(os.path.exists(junit_file))

        tree = etree.parse(junit_file)
        self.assertEqual(tree.getroot().tag, "testsuites")
        self.assertEqual(tree.getroot()[0].tag, "testsuite")
        self.assertEqual(tree.getroot()[0][0].tag, "testcase")
        self.assertEqual(int(tree.getroot().get('tests')),
                         len(ctx.playbook['results']))
        self.assertEqual(int(tree.getroot().get('failures')),
                         2)

    def test_generate_junit_for_playbook(self):
        """ Roughly ensures the expected xml is generated properly """
        # Record two separate playbooks
        ctx = FakeRun()
        FakeRun()
        cmd = ara.cli.generate.GenerateJunit(None, None)
        parser = cmd.get_parser('test')

        junit_file = "{0}/junit-playbook.xml".format(self.tmpdir)
        args = parser.parse_args([
            junit_file,
            '--playbook',
            six.text_type(ctx.playbook['id'])
        ])
        cmd.take_action(args)

        self.assertTrue(os.path.exists(junit_file))

        tree = etree.parse(junit_file)
        self.assertEqual(tree.getroot().tag, "testsuites")
        self.assertEqual(tree.getroot()[0].tag, "testsuite")
        self.assertEqual(tree.getroot()[0][0].tag, "testcase")
        self.assertEqual(int(tree.getroot().get('tests')),
                         len(ctx.playbook['results']))

    def test_generate_subunit(self):
        """ Roughly ensures the expected subunit is generated properly """
        ctx = FakeRun()
        cmd = ara.cli.generate.GenerateSubunit(None, None)
        parser = cmd.get_parser('test')

        subunit_file = os.path.join(self.tmpdir, 'test.subunit')
        subunit_dir = os.path.join(self.tmpdir, 'subunit_dir')
        args = parser.parse_args([subunit_file])
        cmd.take_action(args)

        self.assertTrue(os.path.exists(subunit_file))
        # Dump the subunit binary stream to some files we can read and assert
        with open(subunit_file, 'r') as f:
            to_disk(['-d', subunit_dir], stdin=f)

        # Get *.json files, load them and test them
        data = []
        testfiles = glob("%s/%s" % (subunit_dir, '*/*.json'))
        for testfile in testfiles:
            with open(testfile, 'rb') as f:
                data.append(jsonutils.load(f))

        keys = ['status', 'tags', 'stop', 'start', 'details', 'id']
        for result in data:
            # Test that we have the expected keys, no more, no less
            for key in keys:
                self.assertTrue(key in result.keys())
            for key in result.keys():
                self.assertTrue(key in keys)

        # Get non-json files, load them and test them
        data = []
        testfiles = [fn for fn in glob("%s/%s" % (subunit_dir, '*/*'))
                     if not os.path.basename(fn).endswith('json')]
        for testfile in testfiles:
            with open(testfile, 'rb') as f:
                data.append(jsonutils.load(f))

        keys = ['host', 'playbook_id', 'playbook_path', 'play_name',
                'task_action', 'task_action_lineno', 'task_id', 'task_name',
                'task_path']
        for result in data:
            # Test that we have the expected keys, no more, no less
            for key in keys:
                self.assertTrue(key in result.keys())
            for key in result.keys():
                self.assertTrue(key in keys)

            # Test that we have matching data for playbook records
            self.assertEqual(ctx.playbook['id'], result['playbook_id'])
            self.assertEqual(ctx.playbook['path'], result['playbook_path'])

            # Test that we have matching data for task records
            task = TaskApi().get(id=result['task_id'])
            task = jsonutils.loads(task.data)
            self.assertEqual(task['id'], result['task_id'])
            self.assertEqual(task['action'], result['task_action'])
            self.assertEqual(task['lineno'], result['task_action_lineno'])
            self.assertEqual(task['name'], result['task_name'])
