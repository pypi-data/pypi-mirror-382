# -*- coding: utf-8 -*-

# Copyright 2014 Spanish National Research Council (CSIC)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Fixtures for cASO tests."""

import datetime
import typing

import pytest

import caso
import caso.record

now = datetime.datetime(2023, 5, 25, 21, 59, 6, 0, tzinfo=datetime.timezone.utc)
cloud_type = caso.user_agent

valid_cloud_records_fields = [
    dict(
        uuid="721cf1db-0e0f-4c24-a5ea-cd75e0f303e8",
        site_name="TEST-Site",
        name="VM Name 1",
        user_id="a4519d7d-f60a-4908-9d63-7d9e17422188",
        group_id="03b6a6c4-cf2b-48b9-82f1-69c52b9f30af",
        fqan="VO 1 FQAN",
        start_time=now - datetime.timedelta(days=5),
        end_time=now,
        compute_service="Fake Cloud Service",
        status="started",
        image_id="b39a8ed9-e15d-4b71-ada2-daf88efbac0a",
        user_dn="User DN",
        benchmark_type=None,
        benchmark_value=None,
        memory=16,
        cpu_count=8,
        disk=250,
        public_ip_count=7,
    ),
    dict(
        uuid="a53738e1-13eb-4047-800c-067d14ce3d22",
        site_name="TEST-Site",
        name="VM Name 2",
        user_id="a4519d7d-f60a-4908-9d63-7d9e17422188",
        group_id="03b6a6c4-cf2b-48b9-82f1-69c52b9f30af",
        fqan="VO 2 FQAN",
        start_time=now - datetime.timedelta(days=6),
        end_time=now,
        compute_service="Fake Cloud Service",
        status="completed",
        image_id="b39a8ed9-e15d-4b71-ada2-daf88efbac0a",
        user_dn="User DN",
        benchmark_type=None,
        benchmark_value=None,
        memory=16,
        cpu_count=8,
        disk=250,
        public_ip_count=7,
    ),
]

valid_cloud_records_dict = [
    {
        "CloudComputeService": "Fake Cloud Service",
        "CpuCount": 8,
        "CpuDuration": 3456000,
        "CloudType": cloud_type,
        "Disk": 250,
        "StartTime": 1684619946,
        "EndTime": 1685051946,
        "FQAN": "VO 1 FQAN",
        "GlobalUserName": "User DN",
        "ImageId": "b39a8ed9-e15d-4b71-ada2-daf88efbac0a",
        "LocalGroupId": "03b6a6c4-cf2b-48b9-82f1-69c52b9f30af",
        "LocalUserId": "a4519d7d-f60a-4908-9d63-7d9e17422188",
        "MachineName": "VM Name 1",
        "Memory": 16,
        "PublicIPCount": 7,
        "SiteName": "TEST-Site",
        "Status": "started",
        "VMUUID": "721cf1db-0e0f-4c24-a5ea-cd75e0f303e8",
        "WallDuration": 432000,
    },
    {
        "CloudComputeService": "Fake Cloud Service",
        "CpuCount": 8,
        "CpuDuration": 3456000,
        "CloudType": cloud_type,
        "Disk": 250,
        "StartTime": 1684533546,
        "EndTime": 1685051946,
        "FQAN": "VO 2 FQAN",
        "GlobalUserName": "User DN",
        "ImageId": "b39a8ed9-e15d-4b71-ada2-daf88efbac0a",
        "LocalGroupId": "03b6a6c4-cf2b-48b9-82f1-69c52b9f30af",
        "LocalUserId": "a4519d7d-f60a-4908-9d63-7d9e17422188",
        "MachineName": "VM Name 2",
        "Memory": 16,
        "PublicIPCount": 7,
        "SiteName": "TEST-Site",
        "Status": "completed",
        "VMUUID": "a53738e1-13eb-4047-800c-067d14ce3d22",
        "WallDuration": 432000,
    },
]


valid_ip_records_fields = [
    dict(
        uuid="e3c5aeef-37b8-4332-ad9f-9d068f156dc2",
        measure_time=now,
        site_name="TEST-Site",
        user_id="a4519d7d-f60a-4908-9d63-7d9e17422188",
        group_id="03b6a6c4-cf2b-48b9-82f1-69c52b9f30af",
        user_dn="User 1 DN",
        fqan="VO 1 FQAN",
        ip_version=4,
        public_ip_count=10,
        compute_service="Fake Cloud Service",
        cloud_type=cloud_type,
    ),
    dict(
        uuid="5c50720e-a653-4d70-9b0e-d4388687fcbc",
        measure_time=now,
        site_name="TEST-Site",
        user_id="3391a44e-3728-478d-abde-b86c25356571",
        group_id="2dae43c4-1889-4e63-b172-d4e99381e30a",
        user_dn="User 2 DN",
        fqan="VO 2 FQAN",
        ip_version=6,
        public_ip_count=20,
        compute_service="Fake Cloud Service",
        cloud_type=cloud_type,
    ),
]

valid_ip_records_dict = [
    {
        "CloudComputeService": "Fake Cloud Service",
        "FQAN": "VO 1 FQAN",
        "GlobalUserName": "User 1 DN",
        "IPCount": 10,
        "IPVersion": 4,
        "LocalGroup": "03b6a6c4-cf2b-48b9-82f1-69c52b9f30af",
        "LocalUser": "a4519d7d-f60a-4908-9d63-7d9e17422188",
        "MeasurementTime": 1685051946,
        "SiteName": "TEST-Site",
        "uuid": "e3c5aeef-37b8-4332-ad9f-9d068f156dc2",
        "CloudType": cloud_type,
    },
    {
        "CloudComputeService": "Fake Cloud Service",
        "FQAN": "VO 1 FQAN",
        "GlobalUserName": "User 2 DN",
        "IPCount": 20,
        "IPVersion": 4,
        "LocalGroup": "2dae43c4-1889-4e63-b172-d4e99381e30a",
        "LocalUser": "3391a44e-3728-478d-abde-b86c25356571",
        "MeasurementTime": 1685051946,
        "SiteName": "TEST-Site",
        "uuid": "5c50720e-a653-4d70-9b0e-d4388687fcbc",
        "CloudType": cloud_type,
    },
]

valid_accelerator_records_fields = [
    dict(
        measurement_month=6,
        measurement_year=2022,
        uuid="99cf5d02-a573-46a1-b90d-0f7327126876",
        fqan="VO 1 FQAN",
        compute_service="Fake Cloud Service",
        site_name="TEST-Site",
        count=3,
        available_duration=5000,
        accelerator_type="GPU",
        user_dn="d4e547e6f298fe34389@foobar.eu",
        model="Foobar A200",
    ),
    dict(
        measurement_month=2,
        measurement_year=2022,
        uuid="99cf5d02-a573-46a1-b90d-0f7327126876",
        fqan="VO 1 FQAN",
        compute_service="Fake Cloud Service",
        site_name="TEST-Site",
        count=30,
        available_duration=5000,
        accelerator_type="GPU",
        user_dn="d4e547e6f298fe34389@foobar.eu",
        model="Foobar A300",
    ),
]

valid_accelerator_records_dict = [
    {
        "AccUUID": "99cf5d02-a573-46a1-b90d-0f7327126876",
        "AssociatedRecordType": "cloud",
        "AvailableDuration": 5000,
        "ActiveDuration": 5000,
        "Count": 3,
        "FQAN": "VO 1 FQAN",
        "GlobalUserName": "d4e547e6f298fe34389@foobar.eu",
        "MeasurementMonth": 6,
        "MeasurementYear": 2022,
        "Model": "Foobar A200",
        "SiteName": "TEST-Site",
        "Type": "GPU",
        "CloudType": cloud_type,
        "CloudComputeService": "Fake Cloud Service",
    },
    {
        "AccUUID": "99cf5d02-a573-46a1-b90d-0f7327126876",
        "AssociatedRecordType": "cloud",
        "AvailableDuration": 5000,
        "ActiveDuration": 5000,
        "Count": 30,
        "FQAN": "VO 1 FQAN",
        "GlobalUserName": "d4e547e6f298fe34389@foobar.eu",
        "MeasurementMonth": 2,
        "MeasurementYear": 2022,
        "Model": "Foobar A300",
        "SiteName": "TEST-Site",
        "Type": "GPU",
        "CloudType": cloud_type,
        "CloudComputeService": "Fake Cloud Service",
    },
]

valid_storage_records_fields = [
    dict(
        uuid="99cf5d02-a573-46a1-b90d-0f7327126876",
        site_name="TEST-Site",
        name="Test Volume 1",
        user_id="63296dcd-b652-4039-b274-aaa70f9d57e5",
        group_id="313c6f62-e05f-4ec7-b0f2-256612db18f5",
        fqan="VO 1 FQAN",
        compute_service="Fake Cloud Service",
        status="in-use",
        active_duration=400,
        measure_time=now,
        start_time=now - datetime.timedelta(days=5),
        capacity=322122547200,
        user_dn="d4e547e6f298fe34389@foobar.eu",
        volume_creation=now - datetime.timedelta(days=5),
    ),
    dict(
        uuid="99cf5d02-a573-46a1-b90d-0f7327126876",
        site_name="TEST-Site",
        name="Test Volume 1",
        user_id="63296dcd-b652-4039-b274-aaa70f9d57e5",
        group_id="313c6f62-e05f-4ec7-b0f2-256612db18f5",
        fqan="VO 2 FQAN",
        compute_service="Fake Cloud Service",
        status="in-use",
        active_duration=400,
        measure_time=now,
        start_time=now - datetime.timedelta(days=6),
        capacity=122122547200,
        user_dn="d4e547e6f298fe34389@foobar.eu",
        volume_creation=now - datetime.timedelta(days=6),
    ),
]

valid_storage_records_dict = [
    {
        "SiteName": "TEST-Site",
        "CloudType": cloud_type,
        "CloudComputeService": "Fake Cloud Service",
        "VolumeUUID": "99cf5d02-a573-46a1-b90d-0f7327126876",
        "RecordName": "Test Volume 1",
        "LocalUser": "63296dcd-b652-4039-b274-aaa70f9d57e5",
        "GlobalUserName": "d4e547e6f298fe34389@foobar.eu",
        "LocalGroup": "313c6f62-e05f-4ec7-b0f2-256612db18f5",
        "FQAN": "VO 1 FQAN",
        "ActiveDuration": 400,
        "CreateTime": 1685051946,
        "StartTime": 1684619946,
        "Type": "Block Storage (cinder)",
        "Status": "in-use",
        "Capacity": 322122547200,
        "VolumeCreationTime": 1684619946,
    },
    {
        "SiteName": "TEST-Site",
        "CloudType": cloud_type,
        "CloudComputeService": "Fake Cloud Service",
        "VolumeUUID": "99cf5d02-a573-46a1-b90d-0f7327126876",
        "RecordName": "Test Volume 2",
        "LocalUser": "63296dcd-b652-4039-b274-aaa70f9d57e5",
        "GlobalUserName": "d4e547e6f298fe34389@foobar.eu",
        "LocalGroup": "313c6f62-e05f-4ec7-b0f2-256612db18f5",
        "FQAN": "VO 2 FQAN",
        "ActiveDuration": 400,
        "CreateTime": 1685051946,
        "StartTime": 1684533546,
        "Type": "Block Storage (cinder)",
        "Status": "in-use",
        "Capacity": 122122547200,
        "VolumeCreationTime": 1684533546,
    },
]

# Cloud Record fixtures


@pytest.fixture()
def cloud_record() -> caso.record.CloudRecord:
    """Get a fixture for the CloudRecord."""
    record = caso.record.CloudRecord(**valid_cloud_records_fields[0])
    return record


@pytest.fixture()
def another_cloud_record() -> caso.record.CloudRecord:
    """Get another fixture for the CloudRecord."""
    record = caso.record.CloudRecord(**valid_cloud_records_fields[1])
    return record


@pytest.fixture()
def valid_cloud_record() -> dict:
    """Get a fixture for a valid record."""
    return valid_cloud_records_dict[0]


@pytest.fixture()
def valid_cloud_records() -> typing.List[dict]:
    """Get a fixture for valid records as a dict."""
    return valid_cloud_records_dict


@pytest.fixture()
def another_valid_cloud_record() -> dict:
    """Get another fixture for a valid record as a dict."""
    return valid_cloud_records_dict[0]


@pytest.fixture()
def cloud_record_list(
    cloud_record, another_cloud_record
) -> typing.List[caso.record.CloudRecord]:
    """Get a fixture for a list of valid records."""
    return [cloud_record, another_cloud_record]


# IP record fixtures


@pytest.fixture()
def ip_record() -> caso.record.IPRecord:
    """Get a fixture for an IP record."""
    record = caso.record.IPRecord(**valid_ip_records_fields[0])
    return record


@pytest.fixture()
def another_ip_record() -> caso.record.IPRecord:
    """Get another fixture for an IP record."""
    record = caso.record.IPRecord(**valid_ip_records_fields[1])
    return record


@pytest.fixture()
def valid_ip_record() -> dict:
    """Get a fixture for a valid IP record as a dict."""
    return valid_ip_records_dict[0]


@pytest.fixture()
def valid_ip_records() -> typing.List[dict]:
    """Get a fixture for all IP records as a dict."""
    return valid_ip_records_dict


@pytest.fixture()
def another_valid_ip_record() -> dict:
    """Get another fixture for an IP record as a dict."""
    return valid_ip_records_dict[1]


@pytest.fixture()
def ip_record_list(ip_record, another_ip_record) -> typing.List[caso.record.IPRecord]:
    """Get a fixture for a list of IP records."""
    return [ip_record, another_ip_record]


# Accelerator records


@pytest.fixture()
def accelerator_record() -> caso.record.AcceleratorRecord:
    """Get a fixture for the AcceleratorRecord."""
    record = caso.record.AcceleratorRecord(**valid_accelerator_records_fields[0])
    return record


@pytest.fixture()
def another_accelerator_record() -> caso.record.AcceleratorRecord:
    """Get another fixture for the AcceleratorRecord."""
    record = caso.record.AcceleratorRecord(**valid_accelerator_records_fields[1])
    return record


@pytest.fixture()
def valid_accelerator_record() -> dict:
    """Get a fixture for a valid record."""
    return valid_accelerator_records_dict[0]


@pytest.fixture()
def valid_accelerator_records() -> typing.List[dict]:
    """Get a fixture for valid records as a dict."""
    return valid_accelerator_records_dict


@pytest.fixture()
def accelerator_record_list(
    accelerator_record, another_accelerator_record
) -> typing.List[caso.record.AcceleratorRecord]:
    """Get a fixture for a list of Accelerator records."""
    return [accelerator_record, another_accelerator_record]


# Storage records


@pytest.fixture()
def storage_record() -> caso.record.StorageRecord:
    """Get a fixture for the StorageRecord."""
    record = caso.record.StorageRecord(**valid_storage_records_fields[0])
    return record


@pytest.fixture()
def another_storage_record() -> caso.record.StorageRecord:
    """Get another fixture for the StorageRecord."""
    record = caso.record.StorageRecord(**valid_storage_records_fields[1])
    return record


@pytest.fixture()
def valid_storage_record() -> dict:
    """Get a fixture for a valid record."""
    return valid_storage_records_dict[0]


@pytest.fixture()
def valid_storage_records() -> typing.List[dict]:
    """Get a fixture for valid records as a dict."""
    return valid_storage_records_dict


@pytest.fixture()
def storage_record_list(
    storage_record, another_storage_record
) -> typing.List[caso.record.StorageRecord]:
    """Get a fixture for a list of Storage records."""
    return [storage_record, another_storage_record]


# SSM entries


@pytest.fixture
def expected_entries_cloud() -> typing.List[str]:
    """Get a fixture for all cloud entries."""
    ssm_entries = [
        "CloudComputeService: Fake Cloud Service\n"
        f"CloudType: {cloud_type}\n"
        "CpuCount: 8\n"
        "CpuDuration: 3456000\n"
        "Disk: 250\n"
        "EndTime: 1685051946\n"
        "FQAN: VO 1 FQAN\n"
        "GlobalUserName: User DN\n"
        "ImageId: b39a8ed9-e15d-4b71-ada2-daf88efbac0a\n"
        "LocalGroupId: 03b6a6c4-cf2b-48b9-82f1-69c52b9f30af\n"
        "LocalUserId: a4519d7d-f60a-4908-9d63-7d9e17422188\n"
        "MachineName: VM Name 1\n"
        "Memory: 16\n"
        "PublicIPCount: 7\n"
        "SiteName: TEST-Site\n"
        "StartTime: 1684619946\n"
        "Status: started\n"
        "VMUUID: 721cf1db-0e0f-4c24-a5ea-cd75e0f303e8\n"
        "WallDuration: 432000",
        "CloudComputeService: Fake Cloud Service\n"
        f"CloudType: {cloud_type}\n"
        "CpuCount: 8\n"
        "CpuDuration: 4147200\n"
        "Disk: 250\n"
        "EndTime: 1685051946\n"
        "FQAN: VO 2 FQAN\n"
        "GlobalUserName: User DN\n"
        "ImageId: b39a8ed9-e15d-4b71-ada2-daf88efbac0a\n"
        "LocalGroupId: 03b6a6c4-cf2b-48b9-82f1-69c52b9f30af\n"
        "LocalUserId: a4519d7d-f60a-4908-9d63-7d9e17422188\n"
        "MachineName: VM Name 2\n"
        "Memory: 16\n"
        "PublicIPCount: 7\n"
        "SiteName: TEST-Site\n"
        "StartTime: 1684533546\n"
        "Status: completed\n"
        "VMUUID: a53738e1-13eb-4047-800c-067d14ce3d22\n"
        "WallDuration: 518400",
    ]

    return ssm_entries


@pytest.fixture
def expected_message_cloud() -> str:
    """Get a fixture for a complete Cloud message."""
    message = (
        "APEL-cloud-message: v0.4\n"
        "CloudComputeService: Fake Cloud Service\n"
        f"CloudType: {cloud_type}\nCpuCount: 8\nCpuDuration: 3456000\n"
        "Disk: 250\nEndTime: 1685051946\nFQAN: VO 1 FQAN\nGlobalUserName: User DN\n"
        "ImageId: b39a8ed9-e15d-4b71-ada2-daf88efbac0a\n"
        "LocalGroupId: 03b6a6c4-cf2b-48b9-82f1-69c52b9f30af\n"
        "LocalUserId: a4519d7d-f60a-4908-9d63-7d9e17422188\nMachineName: VM Name 1\n"
        "Memory: 16\nPublicIPCount: 7\nSiteName: TEST-Site\nStartTime: 1684619946\n"
        "Status: started\nVMUUID: 721cf1db-0e0f-4c24-a5ea-cd75e0f303e8\n"
        "WallDuration: 432000\n"
        "%%"
        "\nCloudComputeService: Fake Cloud Service\n"
        f"CloudType: {cloud_type}\nCpuCount: 8\nCpuDuration: 4147200\n"
        "Disk: 250\nEndTime: 1685051946\nFQAN: VO 2 FQAN\nGlobalUserName: User DN\n"
        "ImageId: b39a8ed9-e15d-4b71-ada2-daf88efbac0a\n"
        "LocalGroupId: 03b6a6c4-cf2b-48b9-82f1-69c52b9f30af\n"
        "LocalUserId: a4519d7d-f60a-4908-9d63-7d9e17422188\nMachineName: VM Name 2\n"
        "Memory: 16\nPublicIPCount: 7\nSiteName: TEST-Site\nStartTime: 1684533546\n"
        "Status: completed\nVMUUID: a53738e1-13eb-4047-800c-067d14ce3d22\n"
        "WallDuration: 518400\n"
    )
    return message.encode("utf-8")


@pytest.fixture
def expected_entries_ip() -> typing.List[str]:
    """Get a fixture for all IP entries."""
    ssm_entries = [
        '{"SiteName":"TEST-Site",'
        f'"CloudType":"{cloud_type}",'
        '"CloudComputeService":"Fake Cloud Service",'
        '"uuid":"e3c5aeef-37b8-4332-ad9f-9d068f156dc2",'
        '"LocalUser":"a4519d7d-f60a-4908-9d63-7d9e17422188",'
        '"GlobalUserName":"User 1 DN",'
        '"LocalGroup":"03b6a6c4-cf2b-48b9-82f1-69c52b9f30af",'
        '"FQAN":"VO 1 FQAN",'
        '"IPVersion":4,'
        '"IPCount":10,'
        '"MeasurementTime":1685051946}',
        '{"SiteName":"TEST-Site",'
        f'"CloudType":"{cloud_type}",'
        '"CloudComputeService":"Fake Cloud Service",'
        '"uuid":"5c50720e-a653-4d70-9b0e-d4388687fcbc",'
        '"LocalUser":"3391a44e-3728-478d-abde-b86c25356571",'
        '"GlobalUserName":"User 2 DN",'
        '"LocalGroup":"2dae43c4-1889-4e63-b172-d4e99381e30a",'
        '"FQAN":"VO 2 FQAN",'
        '"IPVersion":6,'
        '"IPCount":20,'
        '"MeasurementTime":1685051946}',
    ]
    return ssm_entries


@pytest.fixture
def expected_message_ip() -> str:
    """Get a fixture for a complete IP message."""
    message = (
        '{"Type": "APEL Public IP message", "Version": "0.2", "UsageRecords": ['
        '{"SiteName": "TEST-Site", '
        f'"CloudType": "{cloud_type}", '
        '"CloudComputeService": "Fake Cloud Service", '
        '"uuid": "e3c5aeef-37b8-4332-ad9f-9d068f156dc2", '
        '"LocalUser": "a4519d7d-f60a-4908-9d63-7d9e17422188", '
        '"GlobalUserName": "User 1 DN", '
        '"LocalGroup": "03b6a6c4-cf2b-48b9-82f1-69c52b9f30af", '
        '"FQAN": "VO 1 FQAN", '
        '"IPVersion": 4, '
        '"IPCount": 10, '
        '"MeasurementTime": 1685051946}, '
        '{"SiteName": "TEST-Site", '
        f'"CloudType": "{cloud_type}", '
        '"CloudComputeService": "Fake Cloud Service", '
        '"uuid": "5c50720e-a653-4d70-9b0e-d4388687fcbc", '
        '"LocalUser": "3391a44e-3728-478d-abde-b86c25356571", '
        '"GlobalUserName": "User 2 DN", '
        '"LocalGroup": "2dae43c4-1889-4e63-b172-d4e99381e30a", '
        '"FQAN": "VO 2 FQAN", '
        '"IPVersion": 6, '
        '"IPCount": 20, '
        '"MeasurementTime": 1685051946}'
        "]}"
    )
    return message


@pytest.fixture
def expected_entries_accelerator() -> typing.List[str]:
    """Get a fixture for all accelerator entries."""
    ssm_entries = [
        '{"SiteName":"TEST-Site",'
        f'"CloudType":"{cloud_type}",'
        '"CloudComputeService":"Fake Cloud Service",'
        '"AccUUID":"99cf5d02-a573-46a1-b90d-0f7327126876",'
        '"GlobalUserName":"d4e547e6f298fe34389@foobar.eu",'
        '"FQAN":"VO 1 FQAN",'
        '"Count":3,'
        '"AvailableDuration":5000,'
        '"MeasurementMonth":6,'
        '"MeasurementYear":2022,'
        '"AssociatedRecordType":"cloud",'
        '"Type":"GPU",'
        '"Model":"Foobar A200",'
        '"ActiveDuration":5000}',
        '{"SiteName":"TEST-Site",'
        f'"CloudType":"{cloud_type}",'
        '"CloudComputeService":"Fake Cloud Service",'
        '"AccUUID":"99cf5d02-a573-46a1-b90d-0f7327126876",'
        '"GlobalUserName":"d4e547e6f298fe34389@foobar.eu",'
        '"FQAN":"VO 1 FQAN",'
        '"Count":30,'
        '"AvailableDuration":5000,'
        '"MeasurementMonth":2,'
        '"MeasurementYear":2022,'
        '"AssociatedRecordType":"cloud",'
        '"Type":"GPU",'
        '"Model":"Foobar A300",'
        '"ActiveDuration":5000}',
    ]

    return ssm_entries


@pytest.fixture
def expected_message_accelerator() -> str:
    """Get a fixture for a complete Accelerator message."""
    message = (
        '{"Type": "APEL-accelerator-message", "Version": "0.1", "UsageRecords": ['
        '{"SiteName": "TEST-Site", '
        f'"CloudType": "{cloud_type}", '
        '"CloudComputeService": "Fake Cloud Service", '
        '"AccUUID": "99cf5d02-a573-46a1-b90d-0f7327126876", '
        '"GlobalUserName": "d4e547e6f298fe34389@foobar.eu", '
        '"FQAN": "VO 1 FQAN", '
        '"Count": 3, '
        '"AvailableDuration": 5000, '
        '"MeasurementMonth": 6, '
        '"MeasurementYear": 2022, '
        '"AssociatedRecordType": "cloud", '
        '"Type": "GPU", '
        '"Model": "Foobar A200", '
        '"ActiveDuration": 5000}, '
        '{"SiteName": "TEST-Site", '
        f'"CloudType": "{cloud_type}", '
        '"CloudComputeService": "Fake Cloud Service", '
        '"AccUUID": "99cf5d02-a573-46a1-b90d-0f7327126876", '
        '"GlobalUserName": "d4e547e6f298fe34389@foobar.eu", '
        '"FQAN": "VO 1 FQAN", '
        '"Count": 30, '
        '"AvailableDuration": 5000, '
        '"MeasurementMonth": 2, '
        '"MeasurementYear": 2022, '
        '"AssociatedRecordType": "cloud", '
        '"Type": "GPU", '
        '"Model": "Foobar A300", '
        '"ActiveDuration": 5000}'
        "]}"
    )
    return message


@pytest.fixture
def expected_entries_storage() -> typing.List[str]:
    """Get a fixture for all Storage entries."""
    ssm_entries = [
        '<sr:StorageUsageRecord xmlns:sr="http://eu-emi.eu/namespaces/2011/02/storagerecord">'  # noqa
        '<sr:RecordIdentity sr:createTime="2023-05-25T21:59:06+00:00" sr:recordId="99cf5d02-a573-46a1-b90d-0f7327126876" />'  # noqa
        "<sr:StorageSystem>Fake Cloud Service</sr:StorageSystem>"
        "<sr:Site>TEST-Site</sr:Site>"
        "<sr:SubjectIdentity>"
        "<sr:LocalUser>63296dcd-b652-4039-b274-aaa70f9d57e5</sr:LocalUser>"
        "<sr:LocalGroup>313c6f62-e05f-4ec7-b0f2-256612db18f5</sr:LocalGroup>"
        "<sr:UserIdentity>d4e547e6f298fe34389@foobar.eu</sr:UserIdentity>"
        "<sr:Group>VO 1 FQAN</sr:Group>"
        "</sr:SubjectIdentity>"
        "<sr:StartTime>2023-05-20T21:59:06+00:00</sr:StartTime>"
        "<sr:EndTime>2023-05-25T21:59:06+00:00</sr:EndTime>"
        "<sr:ResourceCapacityUsed>345876451382054092800</sr:ResourceCapacityUsed>"
        "</sr:StorageUsageRecord>",
        '<sr:StorageUsageRecord xmlns:sr="http://eu-emi.eu/namespaces/2011/02/storagerecord">'  # noqa
        '<sr:RecordIdentity sr:createTime="2023-05-25T21:59:06+00:00" sr:recordId="99cf5d02-a573-46a1-b90d-0f7327126876" />'  # noqa
        "<sr:StorageSystem>Fake Cloud Service</sr:StorageSystem>"
        "<sr:Site>TEST-Site</sr:Site>"
        "<sr:SubjectIdentity>"
        "<sr:LocalUser>63296dcd-b652-4039-b274-aaa70f9d57e5</sr:LocalUser>"
        "<sr:LocalGroup>313c6f62-e05f-4ec7-b0f2-256612db18f5</sr:LocalGroup>"
        "<sr:UserIdentity>d4e547e6f298fe34389@foobar.eu</sr:UserIdentity>"
        "<sr:Group>VO 2 FQAN</sr:Group>"
        "</sr:SubjectIdentity>"
        "<sr:StartTime>2023-05-19T21:59:06+00:00</sr:StartTime>"
        "<sr:EndTime>2023-05-25T21:59:06+00:00</sr:EndTime>"
        "<sr:ResourceCapacityUsed>131128086582054092800</sr:ResourceCapacityUsed>"
        "</sr:StorageUsageRecord>",
    ]
    return ssm_entries


@pytest.fixture
def expected_message_storage() -> str:
    """Get a fixture for a complete Storage message."""
    message = (
        '<sr:StorageUsageRecords xmlns:sr="http://eu-emi.eu/namespaces/2011/02/storagerecord">'  # noqa
        "<sr:StorageUsageRecord>"
        '<sr:RecordIdentity sr:createTime="2023-05-25T21:59:06+00:00" sr:recordId="99cf5d02-a573-46a1-b90d-0f7327126876" />'  # noqa
        "<sr:StorageSystem>Fake Cloud Service</sr:StorageSystem>"
        "<sr:Site>TEST-Site</sr:Site>"
        "<sr:SubjectIdentity>"
        "<sr:LocalUser>63296dcd-b652-4039-b274-aaa70f9d57e5</sr:LocalUser>"
        "<sr:LocalGroup>313c6f62-e05f-4ec7-b0f2-256612db18f5</sr:LocalGroup>"
        "<sr:UserIdentity>d4e547e6f298fe34389@foobar.eu</sr:UserIdentity>"
        "<sr:Group>VO 1 FQAN</sr:Group>"
        "</sr:SubjectIdentity>"
        "<sr:StartTime>2023-05-20T21:59:06+00:00</sr:StartTime>"
        "<sr:EndTime>2023-05-25T21:59:06+00:00</sr:EndTime>"
        "<sr:ResourceCapacityUsed>345876451382054092800</sr:ResourceCapacityUsed>"
        "</sr:StorageUsageRecord>"
        "<sr:StorageUsageRecord>"
        '<sr:RecordIdentity sr:createTime="2023-05-25T21:59:06+00:00" sr:recordId="99cf5d02-a573-46a1-b90d-0f7327126876" />'  # noqa
        "<sr:StorageSystem>Fake Cloud Service</sr:StorageSystem>"
        "<sr:Site>TEST-Site</sr:Site>"
        "<sr:SubjectIdentity>"
        "<sr:LocalUser>63296dcd-b652-4039-b274-aaa70f9d57e5</sr:LocalUser>"
        "<sr:LocalGroup>313c6f62-e05f-4ec7-b0f2-256612db18f5</sr:LocalGroup>"
        "<sr:UserIdentity>d4e547e6f298fe34389@foobar.eu</sr:UserIdentity>"
        "<sr:Group>VO 2 FQAN</sr:Group>"
        "</sr:SubjectIdentity>"
        "<sr:StartTime>2023-05-19T21:59:06+00:00</sr:StartTime>"
        "<sr:EndTime>2023-05-25T21:59:06+00:00</sr:EndTime>"
        "<sr:ResourceCapacityUsed>131128086582054092800</sr:ResourceCapacityUsed>"
        "</sr:StorageUsageRecord>"
        "</sr:StorageUsageRecords>"
    )
    return message
