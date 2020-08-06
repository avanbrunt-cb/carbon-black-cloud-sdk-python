# *******************************************************
# Copyright (c) VMware, Inc. 2020. All Rights Reserved.
# SPDX-License-Identifier: MIT
# *******************************************************
# *
# * DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
# * WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
# * EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
# * WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
# * NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.

"""Tests for the BaseAPI object."""

import pytest
from cbc_sdk.connection import BaseAPI
from cbc_sdk.credentials import Credentials
from cbc_sdk.credential_providers import EnvironCredentialProvider
from cbc_sdk.errors import CredentialError
from tests.unit.fixtures.mock_credentials import MockCredentialProvider


def test_BaseAPI_init_raw_params():
    """Test initializing the credentials from raw parameters to the BaseAPI."""
    sut = BaseAPI(integration_name='test1', url='https://example.com', token='ABCDEFGHIJKLM', org_key='A1B2C3D4')
    assert sut.credentials.url == 'https://example.com'
    assert sut.credentials.token == 'ABCDEFGHIJKLM'
    assert sut.credentials.org_key == 'A1B2C3D4'
    assert sut.credential_profile_name is None
    assert sut.credential_provider is None
    assert sut.session.server == 'https://example.com'
    assert sut.session.token == 'ABCDEFGHIJKLM'
    assert 'test1' in sut.session.token_header['User-Agent']


def test_BaseAPI_init_default_provider(monkeypatch):
    """Test initializing the credentials from the default provider."""
    monkeypatch.setenv('CBAPI_URL', 'https://example.com')
    monkeypatch.setenv('CBAPI_TOKEN', 'ABCDEFGHIJKLM')
    monkeypatch.setenv('CBAPI_ORG_KEY', 'A1B2C3D4')
    sut = BaseAPI(integration_name='test2', credential_file=None, profile='anything')
    assert sut.credentials.url == 'https://example.com'
    assert sut.credentials.token == 'ABCDEFGHIJKLM'
    assert sut.credentials.org_key == 'A1B2C3D4'
    assert sut.credential_profile_name == 'anything'
    assert isinstance(sut.credential_provider, EnvironCredentialProvider)
    assert sut.session.server == 'https://example.com'
    assert sut.session.token == 'ABCDEFGHIJKLM'
    assert 'test2' in sut.session.token_header['User-Agent']


def test_BaseAPI_init_external_provider():
    """Test initializing the credentials from an externally-supplied provider."""
    creds = Credentials({'url': 'https://example.com', 'token': 'ABCDEFGHIJKLM', 'org_key': 'A1B2C3D4'})
    mock_provider = MockCredentialProvider({'my_section': creds})
    sut = BaseAPI(integration_name='test3', credential_provider=mock_provider, profile='my_section')
    assert sut.credentials is creds
    assert sut.credentials.url == 'https://example.com'
    assert sut.credentials.token == 'ABCDEFGHIJKLM'
    assert sut.credentials.org_key == 'A1B2C3D4'
    assert sut.credential_profile_name == 'my_section'
    assert sut.credential_provider is mock_provider
    assert sut.session.server == 'https://example.com'
    assert sut.session.token == 'ABCDEFGHIJKLM'
    assert 'test3' in sut.session.token_header['User-Agent']


def test_BaseAPI_init_provider_raises_error():
    """Test initializing the credentials when the provider raises an error."""
    creds = Credentials({'url': 'https://example.com', 'token': 'ABCDEFGHIJKLM', 'org_key': 'A1B2C3D4'})
    mock_provider = MockCredentialProvider({'my_section': creds})
    with pytest.raises(CredentialError):
        BaseAPI(integration_name='test4', credential_provider=mock_provider, profile='notexist')
