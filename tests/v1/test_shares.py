# Copyright 2010 Jacob Kaplan-Moss

# Copyright 2011 OpenStack LLC.
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

from manilaclient import extension
from manilaclient.v1 import shares

from tests import utils
from tests.v1 import fakes


extensions = [
    extension.Extension('shares', shares),
]
cs = fakes.FakeClient(extensions=extensions)


class SharesTest(utils.TestCase):

    def test_create_nfs_share(self):
        cs.shares.create('nfs', 1)
        cs.assert_called('POST', '/shares')

    def test_create_cifs_share(self):
        cs.shares.create('cifs', 2)
        cs.assert_called('POST', '/shares')

    def test_delete_share(self):
        share = cs.shares.get('1234')
        cs.shares.delete(share)
        cs.assert_called('DELETE', '/shares/1234')

    def test_force_delete_share(self):
        share = cs.shares.get('1234')
        cs.shares.force_delete(share)
        cs.assert_called('POST', '/shares/1234/action',
                         {'os-force_delete': None})

    def test_list_shares(self):
        cs.shares.list()
        cs.assert_called('GET', '/shares/detail')

    def test_allow_access_to_share(self):
        share = cs.shares.get(1234)
        ip = '192.168.0.1'
        cs.shares.allow(share, 'ip', ip)
        cs.assert_called('POST', '/shares/1234/action')

    def test_get_metadata(self):
        cs.shares.get_metadata(1234)
        cs.assert_called('GET', '/shares/1234/metadata')

    def test_set_metadata(self):
        cs.shares.set_metadata(1234, {'k1': 'v2'})
        cs.assert_called('POST', '/shares/1234/metadata',
                         {'metadata': {'k1': 'v2'}})

    def test_delete_metadata(self):
        keys = ['key1']
        cs.shares.delete_metadata(1234, keys)
        cs.assert_called('DELETE', '/shares/1234/metadata/key1')

    def test_metadata_update_all(self):
        cs.shares.update_all_metadata(1234, {'k1': 'v1'})
        cs.assert_called('PUT', '/shares/1234/metadata',
                         {'metadata': {'k1': 'v1'}})
