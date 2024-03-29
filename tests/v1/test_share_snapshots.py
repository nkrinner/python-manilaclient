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
from manilaclient.v1 import share_snapshots

from tests import utils
from tests.v1 import fakes


extensions = [
    extension.Extension('share_snapshots', share_snapshots),
]
cs = fakes.FakeClient(extensions=extensions)


class ShareSnapshotsTest(utils.TestCase):

    def test_create_share_snapshot(self):
        cs.share_snapshots.create(1234)
        cs.assert_called('POST', '/snapshots')

    def test_delete_share_snapshot(self):
        snapshot = cs.share_snapshots.get(1234)
        cs.share_snapshots.delete(snapshot)
        cs.assert_called('DELETE', '/snapshots/1234')

    def test_force_delete_share_snapshot(self):
        snapshot = cs.share_snapshots.get(1234)
        cs.share_snapshots.force_delete(snapshot)
        cs.assert_called('POST', '/snapshots/1234/action',
                         {'os-force_delete': None})

    def test_list_share_snapshots(self):
        cs.share_snapshots.list()
        cs.assert_called('GET', '/snapshots/detail')
