# Copyright 2013 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import fixtures

import mock

from manilaclient import client
from manilaclient import shell
from manilaclient import exceptions
from manilaclient.v1 import shell as shell_v1
from tests import utils
from tests.v1 import fakes


class ShellTest(utils.TestCase):

    FAKE_ENV = {
        'MANILA_USERNAME': 'username',
        'MANILA_PASSWORD': 'password',
        'MANILA_PROJECT_ID': 'project_id',
        'OS_SHARE_API_VERSION': '2',
        'MANILA_URL': 'http://no.where',
    }

    # Patch os.environ to avoid required auth info.
    def setUp(self):
        """Run before each test."""
        super(ShellTest, self).setUp()
        for var in self.FAKE_ENV:
            self.useFixture(fixtures.EnvironmentVariable(var,
                                                         self.FAKE_ENV[var]))

        self.shell = shell.OpenStackManilaShell()

        #HACK(bcwaldon): replace this when we start using stubs
        self.old_get_client_class = client.get_client_class
        client.get_client_class = lambda *_: fakes.FakeClient

    def tearDown(self):
        # For some method like test_image_meta_bad_action we are
        # testing a SystemExit to be thrown and object self.shell has
        # no time to get instantatiated which is OK in this case, so
        # we make sure the method is there before launching it.
        if hasattr(self.shell, 'cs'):
            self.shell.cs.clear_callstack()

        #HACK(bcwaldon): replace this when we start using stubs
        client.get_client_class = self.old_get_client_class
        super(ShellTest, self).tearDown()

    def run_command(self, cmd):
        self.shell.main(cmd.split())

    def assert_called(self, method, url, body=None, **kwargs):
        return self.shell.cs.assert_called(method, url, body, **kwargs)

    def assert_called_anytime(self, method, url, body=None):
        return self.shell.cs.assert_called_anytime(method, url, body)

    def test_list(self):
        self.run_command('list')
        # NOTE(jdg): we default to detail currently
        self.assert_called('GET', '/shares/detail')

    def test_list_filter_status(self):
        self.run_command('list --status=available')
        self.assert_called('GET', '/shares/detail?status=available')

    def test_list_filter_name(self):
        self.run_command('list --name=1234')
        self.assert_called('GET', '/shares/detail?name=1234')

    def test_list_all_tenants(self):
        self.run_command('list --all-tenants=1')
        self.assert_called('GET', '/shares/detail?all_tenants=1')

    def test_show(self):
        self.run_command('show 1234')
        self.assert_called('GET', '/shares/1234')

    def test_delete(self):
        self.run_command('delete 1234')
        self.assert_called('DELETE', '/shares/1234')

    def test_snapshot_list_filter_share_id(self):
        self.run_command('snapshot-list --share-id=1234')
        self.assert_called('GET', '/snapshots/detail?share_id=1234')

    def test_snapshot_list_filter_status_and_share_id(self):
        self.run_command('snapshot-list --status=available --share-id=1234')
        self.assert_called('GET', '/snapshots/detail?'
                           'status=available&share_id=1234')

    def test_rename(self):
        # basic rename with positional agruments
        self.run_command('rename 1234 new-name')
        expected = {'share': {'display_name': 'new-name'}}
        self.assert_called('PUT', '/shares/1234', body=expected)
        # change description only
        self.run_command('rename 1234 --description=new-description')
        expected = {'share': {'display_description': 'new-description'}}
        self.assert_called('PUT', '/shares/1234', body=expected)
        # rename and change description
        self.run_command('rename 1234 new-name '
                         '--description=new-description')
        expected = {'share': {
            'display_name': 'new-name',
            'display_description': 'new-description',
        }}
        self.assert_called('PUT', '/shares/1234', body=expected)
        self.assertRaises(exceptions.CommandError,
                          self.run_command, 'rename 1234')

    def test_rename_snapshot(self):
        # basic rename with positional agruments
        self.run_command('snapshot-rename 1234 new-name')
        expected = {'snapshot': {'display_name': 'new-name'}}
        self.assert_called('PUT', '/snapshots/1234', body=expected)
        # change description only
        self.run_command('snapshot-rename 1234 '
                         '--description=new-description')
        expected = {'snapshot': {'display_description': 'new-description'}}

        self.assert_called('PUT', '/snapshots/1234', body=expected)
        # snapshot-rename and change description
        self.run_command('snapshot-rename 1234 new-name '
                         '--description=new-description')
        expected = {'snapshot': {
            'display_name': 'new-name',
            'display_description': 'new-description',
        }}
        self.assert_called('PUT', '/snapshots/1234', body=expected)
        # noop, the only all will be the lookup
        self.assertRaises(exceptions.CommandError,
                          self.run_command, 'rename 1234')

    def test_set_metadata_set(self):
        self.run_command('metadata 1234 set key1=val1 key2=val2')
        self.assert_called('POST', '/shares/1234/metadata',
                           {'metadata': {'key1': 'val1', 'key2': 'val2'}})

    def test_set_metadata_delete_dict(self):
        self.run_command('metadata 1234 unset key1=val1 key2=val2')
        self.assert_called('DELETE', '/shares/1234/metadata/key1')
        self.assert_called('DELETE', '/shares/1234/metadata/key2', pos=-2)

    def test_set_metadata_delete_keys(self):
        self.run_command('metadata 1234 unset key1 key2')
        self.assert_called('DELETE', '/shares/1234/metadata/key1')
        self.assert_called('DELETE', '/shares/1234/metadata/key2', pos=-2)

    def test_share_metadata_update_all(self):
        self.run_command('metadata-update-all 1234 key1=val1 key2=val2')
        self.assert_called('PUT', '/shares/1234/metadata',
                           {'metadata': {'key1': 'val1', 'key2': 'val2'}})

    def test_extract_metadata(self):
        # mimic the result of argparse's parse_args() method
        class Arguments:
            def __init__(self, metadata=[]):
                self.metadata = metadata

        inputs = [
            ([], {}),
            (["key=value"], {"key": "value"}),
            (["key"], {"key": None}),
            (["k1=v1", "k2=v2"], {"k1": "v1", "k2": "v2"}),
            (["k1=v1", "k2"], {"k1": "v1", "k2": None}),
            (["k1", "k2=v2"], {"k1": None, "k2": "v2"})
        ]

        for input in inputs:
            args = Arguments(metadata=input[0])
            self.assertEqual(shell_v1._extract_metadata(args), input[1])

    def test_reset_state(self):
        self.run_command('reset-state 1234')
        expected = {'os-reset_status': {'status': 'available'}}
        self.assert_called('POST', '/shares/1234/action', body=expected)

    def test_reset_state_with_flag(self):
        self.run_command('reset-state --state error 1234')
        expected = {'os-reset_status': {'status': 'error'}}
        self.assert_called('POST', '/shares/1234/action', body=expected)

    def test_snapshot_reset_state(self):
        self.run_command('snapshot-reset-state 1234')
        expected = {'os-reset_status': {'status': 'available'}}
        self.assert_called('POST', '/snapshots/1234/action', body=expected)

    def test_snapshot_reset_state_with_flag(self):
        self.run_command('snapshot-reset-state --state error 1234')
        expected = {'os-reset_status': {'status': 'error'}}
        self.assert_called('POST', '/snapshots/1234/action', body=expected)

    def test_share_network_security_service_list_by_name(self):
        self.run_command('share-network-security-service-list fake_share_nw')
        self.assert_called('GET', '/security-services?share_network_id=1234')

    def test_share_network_security_service_list_by_name_not_found(self):
        self.assertRaises(exceptions.CommandError, self.run_command,
            'share-network-security-service-list inexistent_share_nw')

    def test_share_network_security_service_list_by_name_multiple(self):
        self.assertRaises(exceptions.CommandError, self.run_command,
            'share-network-security-service-list duplicated_name')

    def test_share_network_security_service_list_by_id(self):
        self.run_command('share-network-security-service-list 1111')
        self.assert_called('GET', '/security-services?share_network_id=1111')

    def test_create_share(self):
        # Use only required fields
        self.run_command("create nfs 1")
        expected = {
            "share": {
                "volume_type": None,
                "name": None,
                "snapshot_id": None,
                "description": None,
                "metadata": {},
                "share_proto": "nfs",
                "share_network_id": None,
                "size": 1,
            }
        }
        self.assert_called("POST", "/shares", body=expected)

    def test_create_with_share_network(self):
        # Except required fields added share network
        sn = "fake-share-network"
        with mock.patch.object(shell_v1, "_find_share_network",
                               mock.Mock(return_value=sn)):
            self.run_command("create nfs 1 --share-network %s" % sn)
            expected = {
                "share": {
                    "volume_type": None,
                    "name": None,
                    "snapshot_id": None,
                    "description": None,
                    "metadata": {},
                    "share_proto": "nfs",
                    "share_network_id": sn,
                    "size": 1,
                }
            }
            self.assert_called("POST", "/shares", body=expected)
            shell_v1._find_share_network.assert_called_once_with(mock.ANY, sn)

    def test_create_with_metadata(self):
        # Except required fields added metadata
        self.run_command("create nfs 1 --metadata key1=value1 key2=value2")
        expected = {
            "share": {
                "volume_type": None,
                "name": None,
                "snapshot_id": None,
                "description": None,
                "metadata": {"key1": "value1", "key2": "value2"},
                "share_proto": "nfs",
                "share_network_id": None,
                "size": 1,
            }
        }
        self.assert_called("POST", "/shares", body=expected)
