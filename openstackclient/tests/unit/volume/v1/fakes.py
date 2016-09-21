#   Copyright 2013 Nebula Inc.
#
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

import copy
import mock
import random
import uuid

from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes
from openstackclient.tests.unit import utils


volume_id = 'vvvvvvvv-vvvv-vvvv-vvvvvvvv'
volume_name = 'nigel'
volume_description = 'Nigel Tufnel'
volume_status = 'available'
volume_size = 120
volume_type = 'to-eleven'
volume_zone = 'stonehenge'
volume_metadata = {
    'Alpha': 'a',
    'Beta': 'b',
    'Gamma': 'g',
}
volume_metadata_str = "Alpha='a', Beta='b', Gamma='g'"

VOLUME = {
    'id': volume_id,
    'display_name': volume_name,
    'display_description': volume_description,
    'size': volume_size,
    'status': volume_status,
    'attach_status': 'detached',
    'availability_zone': volume_zone,
    'volume_type': volume_type,
    'metadata': volume_metadata,
}

extension_name = 'SchedulerHints'
extension_namespace = 'http://docs.openstack.org/'\
    'block-service/ext/scheduler-hints/api/v2'
extension_description = 'Pass arbitrary key/value'\
    'pairs to the scheduler.'
extension_updated = '2014-02-07T12:00:0-00:00'
extension_alias = 'OS-SCH-HNT'
extension_links = '[{"href":'\
    '"https://github.com/openstack/block-api", "type":'\
    ' "text/html", "rel": "describedby"}]'

EXTENSION = {
    'name': extension_name,
    'namespace': extension_namespace,
    'description': extension_description,
    'updated': extension_updated,
    'alias': extension_alias,
    'links': extension_links,
}

# NOTE(dtroyer): duplicating here the minimum image info needed to test
#                volume create --image until circular references can be
#                avoided by refactoring the test fakes.

image_id = 'im1'
image_name = 'graven'


IMAGE = {
    'id': image_id,
    'name': image_name,
}

type_id = "5520dc9e-6f9b-4378-a719-729911c0f407"
type_name = "fake-lvmdriver-1"

TYPE = {
    'id': type_id,
    'name': type_name
}

qos_id = '6f2be1de-997b-4230-b76c-a3633b59e8fb'
qos_consumer = 'front-end'
qos_default_consumer = 'both'
qos_name = "fake-qos-specs"
qos_specs = {
    'foo': 'bar',
    'iops': '9001'
}
qos_association = {
    'association_type': 'volume_type',
    'name': type_name,
    'id': type_id
}

QOS = {
    'id': qos_id,
    'consumer': qos_consumer,
    'name': qos_name
}

QOS_DEFAULT_CONSUMER = {
    'id': qos_id,
    'consumer': qos_default_consumer,
    'name': qos_name
}

QOS_WITH_SPECS = {
    'id': qos_id,
    'consumer': qos_consumer,
    'name': qos_name,
    'specs': qos_specs
}

QOS_WITH_ASSOCIATIONS = {
    'id': qos_id,
    'consumer': qos_consumer,
    'name': qos_name,
    'specs': qos_specs,
    'associations': [qos_association]
}


class FakeTransfer(object):
    """Fake one or more Transfer."""

    @staticmethod
    def create_one_transfer(attrs=None):
        """Create a fake transfer.

        :param Dictionary attrs:
            A dictionary with all attributes of Transfer Request
        :return:
            A FakeResource object with volume_id, name, id.
        """
        # Set default attribute
        transfer_info = {
            'auth_key': 'key-' + uuid.uuid4().hex,
            'created_at': 'time-' + uuid.uuid4().hex,
            'volume_id': 'volume-id-' + uuid.uuid4().hex,
            'name': 'fake_transfer_name',
            'id': 'id-' + uuid.uuid4().hex,
            'links': 'links-' + uuid.uuid4().hex,
        }

        # Overwrite default attributes if there are some attributes set
        attrs = attrs or {}

        transfer_info.update(attrs)

        transfer = fakes.FakeResource(
            None,
            transfer_info,
            loaded=True)

        return transfer

    @staticmethod
    def create_transfers(attrs=None, count=2):
        """Create multiple fake transfers.

        :param Dictionary attrs:
            A dictionary with all attributes of transfer
        :param Integer count:
            The number of transfers to be faked
        :return:
            A list of FakeResource objects
        """
        transfers = []
        for n in range(0, count):
            transfers.append(FakeTransfer.create_one_transfer(attrs))

        return transfers

    @staticmethod
    def get_transfers(transfers=None, count=2):
        """Get an iterable MagicMock object with a list of faked transfers.

        If transfers list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List transfers:
            A list of FakeResource objects faking transfers
        :param Integer count:
            The number of transfers to be faked
        :return
            An iterable Mock object with side_effect set to a list of faked
            transfers
        """
        if transfers is None:
            transfers = FakeTransfer.create_transfers(count)

        return mock.Mock(side_effect=transfers)


class FakeService(object):
    """Fake one or more Services."""

    @staticmethod
    def create_one_service(attrs=None):
        """Create a fake service.

        :param Dictionary attrs:
            A dictionary with all attributes of service
        :return:
            A FakeResource object with host, status, etc.
        """
        # Set default attribute
        service_info = {
            'host': 'host_test',
            'binary': 'cinder_test',
            'status': 'enabled',
            'disabled_reason': 'LongHoliday-GoldenWeek',
            'zone': 'fake_zone',
            'updated_at': 'fake_date',
            'state': 'fake_state',
        }

        # Overwrite default attributes if there are some attributes set
        attrs = attrs or {}

        service_info.update(attrs)

        service = fakes.FakeResource(
            None,
            service_info,
            loaded=True)

        return service

    @staticmethod
    def create_services(attrs=None, count=2):
        """Create multiple fake services.

        :param Dictionary attrs:
            A dictionary with all attributes of service
        :param Integer count:
            The number of services to be faked
        :return:
            A list of FakeResource objects
        """
        services = []
        for n in range(0, count):
            services.append(FakeService.create_one_service(attrs))

        return services

    @staticmethod
    def get_services(services=None, count=2):
        """Get an iterable MagicMock object with a list of faked services.

        If services list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List services:
            A list of FakeResource objects faking services
        :param Integer count:
            The number of services to be faked
        :return
            An iterable Mock object with side_effect set to a list of faked
            services
        """
        if services is None:
            services = FakeService.create_services(count)

        return mock.Mock(side_effect=services)


class FakeQos(object):
    """Fake one or more Qos specification."""

    @staticmethod
    def create_one_qos(attrs=None):
        """Create a fake Qos specification.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object with id, name, consumer, etc.
        """
        attrs = attrs or {}

        # Set default attributes.
        qos_info = {
            "id": 'qos-id-' + uuid.uuid4().hex,
            "name": 'qos-name-' + uuid.uuid4().hex,
            "consumer": 'front-end',
            "specs": {"foo": "bar", "iops": "9001"},
        }

        # Overwrite default attributes.
        qos_info.update(attrs)

        qos = fakes.FakeResource(
            info=copy.deepcopy(qos_info),
            loaded=True)
        return qos

    @staticmethod
    def create_qoses(attrs=None, count=2):
        """Create multiple fake Qos specifications.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of Qos specifications to fake
        :return:
            A list of FakeResource objects faking the Qos specifications
        """
        qoses = []
        for i in range(0, count):
            qos = FakeQos.create_one_qos(attrs)
            qoses.append(qos)

        return qoses

    @staticmethod
    def get_qoses(qoses=None, count=2):
        """Get an iterable MagicMock object with a list of faked qoses.

        If qoses list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List volumes:
            A list of FakeResource objects faking qoses
        :param Integer count:
            The number of qoses to be faked
        :return
            An iterable Mock object with side_effect set to a list of faked
            qoses
        """
        if qoses is None:
            qoses = FakeQos.create_qoses(count)

        return mock.Mock(side_effect=qoses)


class FakeVolume(object):
    """Fake one or more volumes."""

    @staticmethod
    def create_one_volume(attrs=None):
        """Create a fake volume.

        :param Dictionary attrs:
            A dictionary with all attributes of volume
        :return:
            A FakeResource object with id, name, status, etc.
        """
        attrs = attrs or {}

        # Set default attribute
        volume_info = {
            'id': 'volume-id' + uuid.uuid4().hex,
            'display_name': 'volume-name' + uuid.uuid4().hex,
            'display_description': 'description' + uuid.uuid4().hex,
            'status': 'available',
            'size': 10,
            'volume_type':
                random.choice(['fake_lvmdriver-1', 'fake_lvmdriver-2']),
            'bootable': 'true',
            'metadata': {
                'key' + uuid.uuid4().hex: 'val' + uuid.uuid4().hex,
                'key' + uuid.uuid4().hex: 'val' + uuid.uuid4().hex,
                'key' + uuid.uuid4().hex: 'val' + uuid.uuid4().hex},
            'snapshot_id': 'snapshot-id-' + uuid.uuid4().hex,
            'availability_zone': 'zone' + uuid.uuid4().hex,
            'attachments': [{
                'device': '/dev/' + uuid.uuid4().hex,
                'server_id': uuid.uuid4().hex,
            }, ],
            'created_at': 'time-' + uuid.uuid4().hex,
        }

        # Overwrite default attributes if there are some attributes set
        volume_info.update(attrs)

        volume = fakes.FakeResource(
            None,
            volume_info,
            loaded=True)
        return volume

    @staticmethod
    def create_volumes(attrs=None, count=2):
        """Create multiple fake volumes.

        :param Dictionary attrs:
            A dictionary with all attributes of volume
        :param Integer count:
            The number of volumes to be faked
        :return:
            A list of FakeResource objects
        """
        volumes = []
        for n in range(0, count):
            volumes.append(FakeVolume.create_one_volume(attrs))

        return volumes

    @staticmethod
    def get_volumes(volumes=None, count=2):
        """Get an iterable MagicMock object with a list of faked volumes.

        If volumes list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List volumes:
            A list of FakeResource objects faking volumes
        :param Integer count:
            The number of volumes to be faked
        :return
            An iterable Mock object with side_effect set to a list of faked
            volumes
        """
        if volumes is None:
            volumes = FakeVolume.create_volumes(count)

        return mock.Mock(side_effect=volumes)


class FakeImagev1Client(object):

    def __init__(self, **kwargs):
        self.images = mock.Mock()


class FakeVolumev1Client(object):

    def __init__(self, **kwargs):
        self.volumes = mock.Mock()
        self.volumes.resource_class = fakes.FakeResource(None, {})
        self.services = mock.Mock()
        self.services.resource_class = fakes.FakeResource(None, {})
        self.extensions = mock.Mock()
        self.extensions.resource_class = fakes.FakeResource(None, {})
        self.qos_specs = mock.Mock()
        self.qos_specs.resource_class = fakes.FakeResource(None, {})
        self.volume_types = mock.Mock()
        self.volume_types.resource_class = fakes.FakeResource(None, {})
        self.transfers = mock.Mock()
        self.transfers.resource_class = fakes.FakeResource(None, {})
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']


class TestVolumev1(utils.TestCommand):

    def setUp(self):
        super(TestVolumev1, self).setUp()

        self.app.client_manager.volume = FakeVolumev1Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        self.app.client_manager.identity = identity_fakes.FakeIdentityv2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        self.app.client_manager.image = FakeImagev1Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )


class FakeType(object):
    """Fake one or more type."""

    @staticmethod
    def create_one_type(attrs=None, methods=None):
        """Create a fake type.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :return:
            A FakeResource object with id, name, description, etc.
        """
        attrs = attrs or {}
        methods = methods or {}

        # Set default attributes.
        type_info = {
            "id": 'type-id-' + uuid.uuid4().hex,
            "name": 'type-name-' + uuid.uuid4().hex,
            "description": 'type-description-' + uuid.uuid4().hex,
            "extra_specs": {"foo": "bar"},
            "is_public": True,
        }

        # Overwrite default attributes.
        type_info.update(attrs)

        volume_type = fakes.FakeResource(
            info=copy.deepcopy(type_info),
            methods=methods,
            loaded=True)
        return volume_type

    @staticmethod
    def create_types(attrs=None, count=2):
        """Create multiple fake types.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of types to fake
        :return:
            A list of FakeResource objects faking the types
        """
        volume_types = []
        for i in range(0, count):
            volume_type = FakeType.create_one_type(attrs)
            volume_types.append(volume_type)

        return volume_types

    @staticmethod
    def get_types(types=None, count=2):
        """Get an iterable MagicMock object with a list of faked types.

        If types list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List types:
            A list of FakeResource objects faking types
        :param Integer count:
            The number of types to be faked
        :return
            An iterable Mock object with side_effect set to a list of faked
            types
        """
        if types is None:
            types = FakeType.create_types(count)

        return mock.Mock(side_effect=types)
