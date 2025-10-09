# -*- coding: utf-8 -*-

# Copyright 2015 Spanish National Research Council (CSIC)
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

"""Module defining all the options to be managed by oslo."""

import itertools

import caso.extract.base
import caso.extract.manager
import caso.extract.openstack.nova
import caso.keystone_client
import caso.manager
import caso.messenger.logstash
import caso.messenger.ssm


def list_opts():
    """Get the list of all configured options."""
    return [
        (
            "DEFAULT",
            itertools.chain(
                caso.manager.opts,
                caso.manager.cli_opts,
                caso.extract.base.opts,
                caso.extract.manager.cli_opts,
            ),
        ),
        ("accelerator", caso.extract.openstack.nova.accelerator_opts),
        ("benchmark", caso.extract.openstack.nova.benchmark_opts),
        ("keystone_auth", caso.keystone_client.opts),
        ("logstash", caso.messenger.logstash.opts),
        ("ssm", caso.messenger.ssm.opts),
    ]
