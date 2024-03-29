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

from manilaclient import base


class QuotaSet(base.Resource):

    @property
    def id(self):
        """Needed by base.Resource to self-refresh and be indexed"""
        return self.tenant_id

    def update(self, *args, **kwargs):
        self.manager.update(self.tenant_id, *args, **kwargs)


class QuotaSetManager(base.ManagerWithFind):
    resource_class = QuotaSet

    def get(self, tenant_id, user_id=None):
        if hasattr(tenant_id, 'tenant_id'):
            tenant_id = tenant_id.tenant_id
        if user_id:
            url = "/os-quota-sets/%s?user_id=%s" % (tenant_id, user_id)
        else:
            url = "/os-quota-sets/%s" % tenant_id
        return self._get(url, "quota_set")

    def update(self, tenant_id, shares=None, snapshots=None, gigabytes=None,
               share_networks=None, force=None, user_id=None):

        body = {
            'quota_set': {
                'tenant_id': tenant_id,
                'shares': shares,
                'snapshots': snapshots,
                'gigabytes': gigabytes,
                'share_networks': share_networks,
                'force': force,
            },
        }

        for key in body['quota_set'].keys():
            if body['quota_set'][key] is None:
                body['quota_set'].pop(key)
        if user_id:
            url = '/os-quota-sets/%s?user_id=%s' % (tenant_id, user_id)
        else:
            url = '/os-quota-sets/%s' % tenant_id

        return self._update(url, body, 'quota_set')

    def defaults(self, tenant_id):
        return self._get('/os-quota-sets/%s/defaults' % tenant_id,
                         'quota_set')

    def delete(self, tenant_id, user_id=None):
        if user_id:
            url = '/os-quota-sets/%s?user_id=%s' % (tenant_id, user_id)
        else:
            url = '/os-quota-sets/%s' % tenant_id
        self._delete(url)
