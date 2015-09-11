#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

"""Object Store v1 API Library"""

import io
import os
import six

try:
    from urllib.parse import urlparse  # noqa
except ImportError:
    from urlparse import urlparse  # noqa

from openstackclient.api import api


class APIv1(api.BaseAPI):
    """Object Store v1 API"""

    def __init__(self, **kwargs):
        super(APIv1, self).__init__(**kwargs)

    def container_create(
        self,
        container=None,
    ):
        """Create a container

        :param string container:
            name of container to create
        :returns:
            dict of returned headers
        """

        response = self.create(container, method='PUT')
        data = {
            'account': self._find_account_id(),
            'container': container,
            'x-trans-id': response.headers.get('x-trans-id', None),
        }

        return data

    def container_delete(
        self,
        container=None,
    ):
        """Delete a container

        :param string container:
            name of container to delete
        """

        if container:
            self.delete(container)

    def container_list(
        self,
        all_data=False,
        limit=None,
        marker=None,
        end_marker=None,
        prefix=None,
        **params
    ):
        """Get containers in an account

        :param boolean all_data:
            if True, return a full listing, else returns a max of
            10000 listings
        :param integer limit:
            query return count limit
        :param string marker:
            query marker
        :param string end_marker:
            query end_marker
        :param string prefix:
            query prefix
        :returns:
            list of container names
        """

        params['format'] = 'json'

        if all_data:
            data = listing = self.container_list(
                limit=limit,
                marker=marker,
                end_marker=end_marker,
                prefix=prefix,
                **params
            )
            while listing:
                marker = listing[-1]['name']
                listing = self.container_list(
                    limit=limit,
                    marker=marker,
                    end_marker=end_marker,
                    prefix=prefix,
                    **params
                )
                if listing:
                    data.extend(listing)
            return data

        if limit:
            params['limit'] = limit
        if marker:
            params['marker'] = marker
        if end_marker:
            params['end_marker'] = end_marker
        if prefix:
            params['prefix'] = prefix

        return self.list('', **params)

    def container_save(
        self,
        container=None,
    ):
        """Save all the content from a container

        :param string container:
            name of container to save
        """

        objects = self.object_list(container=container)
        for object in objects:
            self.object_save(container=container, object=object['name'])

    def container_set(
        self,
        container,
        properties,
    ):
        """Set container properties

        :param string container:
            name of container to modify
        :param dict properties:
            properties to add or update for the container
        """

        headers = self._set_properties(properties, 'X-Container-Meta-%s')
        if headers:
            self.create(container, headers=headers)

    def container_show(
        self,
        container=None,
    ):
        """Get container details

        :param string container:
            name of container to show
        :returns:
            dict of returned headers
        """

        response = self._request('HEAD', container)
        data = {
            'account': self._find_account_id(),
            'container': container,
            'object_count': response.headers.get(
                'x-container-object-count',
                None,
            ),
            'meta-owner': response.headers.get('x-container-meta-owner', None),
            'bytes_used': response.headers.get('x-container-bytes-used', None),
            'read_acl': response.headers.get('x-container-read', None),
            'write_acl': response.headers.get('x-container-write', None),
            'sync_to': response.headers.get('x-container-sync-to', None),
            'sync_key': response.headers.get('x-container-sync-key', None),
        }
        return data

    def container_unset(
        self,
        container,
        properties,
    ):
        """Unset container properties

        :param string container:
            name of container to modify
        :param dict properties:
            properties to remove from the container
        """

        headers = self._unset_properties(properties,
                                         'X-Remove-Container-Meta-%s')
        if headers:
            self.create(container, headers=headers)

    def object_create(
        self,
        container=None,
        object=None,
    ):
        """Create an object inside a container

        :param string container:
            name of container to store object
        :param string object:
            local path to object
        :returns:
            dict of returned headers
        """

        if container is None or object is None:
            # TODO(dtroyer): What exception to raise here?
            return {}

        full_url = "%s/%s" % (container, object)
        with io.open(object, 'rb') as f:
            response = self.create(
                full_url,
                method='PUT',
                data=f,
            )
        data = {
            'account': self._find_account_id(),
            'container': container,
            'object': object,
            'x-trans-id': response.headers.get('X-Trans-Id', None),
            'etag': response.headers.get('Etag', None),
        }

        return data

    def object_delete(
        self,
        container=None,
        object=None,
    ):
        """Delete an object from a container

        :param string container:
            name of container that stores object
        :param string object:
            name of object to delete
        """

        if container is None or object is None:
            return

        self.delete("%s/%s" % (container, object))

    def object_list(
        self,
        container=None,
        all_data=False,
        limit=None,
        marker=None,
        end_marker=None,
        delimiter=None,
        prefix=None,
        **params
    ):
        """List objects in a container

        :param string container:
            container name to get a listing for
        :param boolean all_data:
            if True, return a full listing, else returns a max of
            10000 listings
        :param integer limit:
            query return count limit
        :param string marker:
            query marker
        :param string end_marker:
            query end_marker
        :param string prefix:
            query prefix
        :param string delimiter:
            string to delimit the queries on
        :returns: a tuple of (response headers, a list of objects) The response
            headers will be a dict and all header names will be lowercase.
        """

        if container is None or object is None:
            return None

        params['format'] = 'json'
        if all_data:
            data = listing = self.object_list(
                container=container,
                limit=limit,
                marker=marker,
                end_marker=end_marker,
                prefix=prefix,
                delimiter=delimiter,
                **params
            )
            while listing:
                if delimiter:
                    marker = listing[-1].get('name', listing[-1].get('subdir'))
                else:
                    marker = listing[-1]['name']
                listing = self.object_list(
                    container=container,
                    limit=limit,
                    marker=marker,
                    end_marker=end_marker,
                    prefix=prefix,
                    delimiter=delimiter,
                    **params
                )
                if listing:
                    data.extend(listing)
            return data

        if limit:
            params['limit'] = limit
        if marker:
            params['marker'] = marker
        if end_marker:
            params['end_marker'] = end_marker
        if prefix:
            params['prefix'] = prefix
        if delimiter:
            params['delimiter'] = delimiter

        return self.list(container, **params)

    def object_save(
        self,
        container=None,
        object=None,
        file=None,
    ):
        """Save an object stored in a container

        :param string container:
            name of container that stores object
        :param string object:
            name of object to save
        :param string file:
            local name of object
        """

        if not file:
            file = object

        response = self._request(
            'GET',
            "%s/%s" % (container, object),
            stream=True,
        )
        if response.status_code == 200:
            if not os.path.exists(os.path.dirname(file)):
                if len(os.path.dirname(file)) > 0:
                    os.makedirs(os.path.dirname(file))
            with open(file, 'wb') as f:
                for chunk in response.iter_content():
                    f.write(chunk)

    def object_set(
        self,
        container,
        object,
        properties,
    ):
        """Set object properties

        :param string container:
            container name for object to modify
        :param string object:
            name of object to modify
        :param dict properties:
            properties to add or update for the container
        """

        headers = self._set_properties(properties, 'X-Object-Meta-%s')
        if headers:
            self.create("%s/%s" % (container, object), headers=headers)

    def object_unset(
        self,
        container,
        object,
        properties,
    ):
        """Unset object properties

        :param string container:
            container name for object to modify
        :param string object:
            name of object to modify
        :param dict properties:
            properties to remove from the object
        """

        headers = self._unset_properties(properties, 'X-Remove-Object-Meta-%s')
        if headers:
            self.create("%s/%s" % (container, object), headers=headers)

    def object_show(
        self,
        container=None,
        object=None,
    ):
        """Get object details

        :param string container:
            container name for object to get
        :param string object:
            name of object to get
        :returns:
            dict of object properties
        """

        if container is None or object is None:
            return {}

        response = self._request('HEAD', "%s/%s" % (container, object))
        data = {
            'account': self._find_account_id(),
            'container': container,
            'object': object,
            'content-type': response.headers.get('content-type', None),
            'meta-owner': response.headers.get('x-container-meta-owner', None),
        }
        if 'content-length' in response.headers:
            data['content-length'] = response.headers.get(
                'content-length',
                None,
            )
        if 'last-modified' in response.headers:
            data['last-modified'] = response.headers.get('last-modified', None)
        if 'etag' in response.headers:
            data['etag'] = response.headers.get('etag', None)
        if 'x-object-manifest' in response.headers:
            data['x-object-manifest'] = response.headers.get(
                'x-object-manifest',
                None,
            )
        for key, value in six.iteritems(response.headers):
            if key.startswith('x-object-meta-'):
                data[key[len('x-object-meta-'):].lower()] = value
            elif key not in (
                    'content-type',
                    'content-length',
                    'last-modified',
                    'etag',
                    'date',
                    'x-object-manifest',
                    'x-container-meta-owner',
            ):
                data[key.lower()] = value

        return data

    def account_set(
        self,
        properties,
    ):
        """Set account properties

        :param dict properties:
            properties to add or update for the account
        """

        headers = self._set_properties(properties, 'X-Account-Meta-%s')
        if headers:
            # NOTE(stevemar): The URL (first argument) in this case is already
            # set to the swift account endpoint, because that's how it's
            # registered in the catalog
            self.create("", headers=headers)

    def account_show(self):
        """Show account details"""

        # NOTE(stevemar): Just a HEAD request to the endpoint already in the
        # catalog should be enough.
        response = self._request("HEAD", "")
        data = {}
        for k, v in response.headers.iteritems():
            data[k] = v
        # Map containers, bytes and objects a bit nicer
        data['Containers'] = data.pop('x-account-container-count', None)
        data['Objects'] = data.pop('x-account-object-count', None)
        data['Bytes'] = data.pop('x-account-bytes-used', None)
        # Add in Account info too
        data['Account'] = self._find_account_id()
        return data

    def account_unset(
        self,
        properties,
    ):
        """Unset account properties

        :param dict properties:
            properties to remove from the account
        """

        headers = self._unset_properties(properties,
                                         'X-Remove-Account-Meta-%s')
        if headers:
            self.create("", headers=headers)

    def _find_account_id(self):
        url_parts = urlparse(self.endpoint)
        return url_parts.path.split('/')[-1]

    def _unset_properties(self, properties, header_tag):
        # NOTE(stevemar): As per the API, the headers have to be in the form
        # of "X-Remove-Account-Meta-Book: x". In the case where metadata is
        # removed, we can set the value of the header to anything, so it's
        # set to 'x'. In the case of a Container property we use:
        # "X-Remove-Container-Meta-Book: x", and the same logic applies for
        # Object properties

        headers = {}
        for k in properties:
            header_name = header_tag % k
            headers[header_name] = 'x'
        return headers

    def _set_properties(self, properties, header_tag):
        # NOTE(stevemar): As per the API, the headers have to be in the form
        # of "X-Account-Meta-Book: MobyDick". In the case of a Container
        # property we use: "X-Add-Container-Meta-Book: MobyDick", and the same
        # logic applies for Object properties

        headers = {}
        for k, v in properties.iteritems():
            header_name = header_tag % k
            headers[header_name] = v
        return headers
