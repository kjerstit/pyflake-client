"""test_role_schema_grant"""
import queue
import uuid

from pyflake_client.client import PyflakeClient
from pyflake_client.models.assets.role import Role as AssetsRole
from pyflake_client.models.assets.database import Database as AssetsDatabase
from pyflake_client.models.assets.schema import Schema as AssetsSchema
from pyflake_client.models.assets.grant import Grant as GrantAsset
from pyflake_client.models.assets.grants.role_schema_grant import RoleSchemaGrant
from pyflake_client.models.describables.grants.role_grant import RoleGrant as RoleGrantDescribable
from pyflake_client.models.entities.grants.role_grant import RoleGrants as RoleGrantsEntity


def test_grant_role_schema_privilege(
        flake: PyflakeClient,
        assets_queue: queue.LifoQueue,
        db_asset_fixture: AssetsDatabase
    ):
    """test_grant_role_schema_privilege"""
    ### Arrange ###
    schema = AssetsSchema(database=db_asset_fixture, schema_name="IGT_SCHEMA", comment=f"pyflake_client_TEST_{uuid.uuid4()}", owner=AssetsRole("SYSADMIN"))
    role = AssetsRole("IGT_CREATE_ROLE", AssetsRole("USERADMIN"), f"pyflake_client_TEST_{uuid.uuid4()}")
    privilege = GrantAsset(RoleSchemaGrant(role.name, db_asset_fixture.db_name, schema.schema_name), ["USAGE"])

    try:
        flake.register_asset(db_asset_fixture, assets_queue)
        flake.register_asset(schema, assets_queue)
        flake.register_asset(role, assets_queue)
        flake.register_asset(privilege, assets_queue)

        ### Act ###
        granted: RoleGrantsEntity = flake.describe(RoleGrantDescribable(role.name), RoleGrantsEntity)

        ### Assert ###
        assert granted.role_name == role.name
        assert len(granted.grants) == 1
        priv = next((r for r in granted.grants if r.privilege == "USAGE"), None)
        assert priv is not None
        assert priv.granted_on == "SCHEMA"
        assert priv.granted_by == "SYSADMIN"

    finally:
        ### Cleanup ###
        flake.delete_assets(assets_queue)


def test_grant_role_schema_privileges(
        flake: PyflakeClient,
        assets_queue: queue.LifoQueue,
        db_asset_fixture: AssetsDatabase
):
    """test_grant_role_schema_privileges"""
    ### Arrange ###
    schema = AssetsSchema(database=db_asset_fixture, schema_name="IGT_SCHEMA", comment=f"pyflake_client_TEST_{uuid.uuid4()}", owner=AssetsRole("SYSADMIN"))
    role = AssetsRole("IGT_CREATE_ROLE", AssetsRole("USERADMIN"), f"pyflake_client_TEST_{uuid.uuid4()}")
    privilege = GrantAsset(RoleSchemaGrant(role.name, db_asset_fixture.db_name, schema.schema_name), ["USAGE", "MONITOR"])

    try:
        flake.register_asset(db_asset_fixture, assets_queue)
        flake.register_asset(schema, assets_queue)
        flake.register_asset(role, assets_queue)
        flake.register_asset(privilege, assets_queue)

        ### Act ###
        granted: RoleGrantsEntity = flake.describe(RoleGrantDescribable(role.name), RoleGrantsEntity)

        ### Assert ###
        assert granted.role_name == role.name
        assert len(granted.grants) == 2

        priv_usage = next((r for r in granted.grants if r.privilege == "USAGE"), None)
        assert priv_usage is not None
        assert priv_usage.granted_on == "SCHEMA"
        assert priv_usage.granted_by == "SYSADMIN"

        priv_mon = next((r for r in granted.grants if r.privilege == "MONITOR"), None)
        assert priv_mon is not None
        assert priv_mon.granted_on == "SCHEMA"
        assert priv_mon.granted_by == "SYSADMIN"
    finally:
        ### Cleanup ###
        flake.delete_assets(assets_queue)
