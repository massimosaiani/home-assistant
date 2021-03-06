"""Test ZHA API."""
from unittest.mock import Mock
import pytest
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.components.switch import DOMAIN
from homeassistant.components.zha.api import (
    async_load_api, WS_ENTITIES_BY_IEEE, WS_ENTITY_CLUSTERS, ATTR_IEEE, TYPE,
    ID, NAME, WS_ENTITY_CLUSTER_ATTRIBUTES, WS_ENTITY_CLUSTER_COMMANDS
)
from homeassistant.components.zha.core.const import (
    ATTR_CLUSTER_ID, ATTR_CLUSTER_TYPE, IN
)
from .common import async_init_zigpy_device


@pytest.fixture
async def zha_client(hass, config_entry, zha_gateway, hass_ws_client):
    """Test zha switch platform."""
    from zigpy.zcl.clusters.general import OnOff

    # load the ZHA API
    async_load_api(hass, Mock(), zha_gateway)

    # create zigpy device
    await async_init_zigpy_device(
        hass, [OnOff.cluster_id], [], None, zha_gateway)

    # load up switch domain
    await hass.config_entries.async_forward_entry_setup(
        config_entry, DOMAIN)
    await hass.async_block_till_done()

    return await hass_ws_client(hass)


async def test_entities_by_ieee(hass, config_entry, zha_gateway, zha_client):
    """Test getting entity refs by ieee address."""
    await zha_client.send_json({
        ID: 5,
        TYPE: WS_ENTITIES_BY_IEEE,
    })

    msg = await zha_client.receive_json()

    assert '00:0d:6f:00:0a:90:69:e7' in msg['result']
    assert len(msg['result']['00:0d:6f:00:0a:90:69:e7']) == 2


async def test_entity_clusters(hass, config_entry, zha_gateway, zha_client):
    """Test getting entity cluster info."""
    await zha_client.send_json({
        ID: 5,
        TYPE: WS_ENTITY_CLUSTERS,
        ATTR_ENTITY_ID: 'switch.fakemanufacturer_fakemodel_0a9069e7_1_6',
        ATTR_IEEE: '00:0d:6f:00:0a:90:69:e7'
    })

    msg = await zha_client.receive_json()

    assert len(msg['result']) == 1

    cluster_info = msg['result'][0]

    assert cluster_info[TYPE] == IN
    assert cluster_info[ID] == 6
    assert cluster_info[NAME] == 'OnOff'


async def test_entity_cluster_attributes(
        hass, config_entry, zha_gateway, zha_client):
    """Test getting entity cluster attributes."""
    await zha_client.send_json({
        ID: 5,
        TYPE: WS_ENTITY_CLUSTER_ATTRIBUTES,
        ATTR_ENTITY_ID: 'switch.fakemanufacturer_fakemodel_0a9069e7_1_6',
        ATTR_IEEE: '00:0d:6f:00:0a:90:69:e7',
        ATTR_CLUSTER_ID: 6,
        ATTR_CLUSTER_TYPE: IN
    })

    msg = await zha_client.receive_json()

    attributes = msg['result']
    assert len(attributes) == 4

    for attribute in attributes:
        assert attribute[ID] is not None
        assert attribute[NAME] is not None


async def test_entity_cluster_commands(
        hass, config_entry, zha_gateway, zha_client):
    """Test getting entity cluster commands."""
    await zha_client.send_json({
        ID: 5,
        TYPE: WS_ENTITY_CLUSTER_COMMANDS,
        ATTR_ENTITY_ID: 'switch.fakemanufacturer_fakemodel_0a9069e7_1_6',
        ATTR_IEEE: '00:0d:6f:00:0a:90:69:e7',
        ATTR_CLUSTER_ID: 6,
        ATTR_CLUSTER_TYPE: IN
    })

    msg = await zha_client.receive_json()

    commands = msg['result']
    assert len(commands) == 6

    for command in commands:
        assert command[ID] is not None
        assert command[NAME] is not None
        assert command[TYPE] is not None
