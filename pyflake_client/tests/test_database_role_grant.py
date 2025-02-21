# -*- coding: utf-8 -*-
import queue

from pyflake_client.client import PyflakeClient
from pyflake_client.models.assets.database import Database as DatabaseAsset
from pyflake_client.models.assets.database_role import DatabaseRole as DatabaseRoleAsset
from pyflake_client.models.assets.grant_action import GrantAction
from pyflake_client.models.assets.grants.database_grant import DatabaseGrant
from pyflake_client.models.assets.grants.schema_grant import SchemaGrant
from pyflake_client.models.assets.role import Role as RoleAsset
from pyflake_client.models.assets.schema import Schema as SchemaAsset
from pyflake_client.models.describables.database_role import (
    DatabaseRole as DatabaseRoleDescribable,
)
from pyflake_client.models.describables.role_grant import (
    RoleGrant as RoleGrantDescribable,
)
from pyflake_client.models.entities.role_grant import RoleGrant as RoleGrantEntity
from pyflake_client.models.enums.privilege import Privilege

# TODO: test_describe_grant_for_non_existing_database_role


def test_describe_grant_for_non_existing_database_role(
    flake: PyflakeClient, assets_queue: queue.LifoQueue, rand_str: str, comment: str
):
    ### Arrange ###
    sys_admin = RoleAsset("SYSADMIN")
    database = DatabaseAsset(
        f"PYFLAKE_CLIENT_TEST_DB_{rand_str}", comment, owner=sys_admin
    )
    try:
        flake.register_asset_async(database, assets_queue).wait()
        ### Act ###
        grants = flake.describe_async(
            describable=RoleGrantDescribable(
                principal=DatabaseRoleDescribable(
                    name="NON_EXISTING_DATABASE_ROLE", db_name=database.db_name
                )
            )
        ).deserialize_many(RoleGrantEntity)

        ### Assert ###

        assert grants == []
    finally:
        ### Cleanup ###
        flake.delete_assets(assets_queue)


def test_database_role_database_grant(
    flake: PyflakeClient, assets_queue: queue.LifoQueue, rand_str: str, comment: str
):
    ### Arrange ###
    user_admin = RoleAsset("USERADMIN")
    sys_admin = RoleAsset("SYSADMIN")
    database = DatabaseAsset(
        f"PYFLAKE_CLIENT_TEST_DB_{rand_str}", comment, owner=sys_admin
    )
    db_role = DatabaseRoleAsset(
        "PYFLAKE_CLIENT_TEST_DB_ROLE", database.db_name, comment, user_admin
    )
    grant = GrantAction(
        db_role,
        DatabaseGrant(database_name=database.db_name),
        [Privilege.CREATE_DATABASE_ROLE, Privilege.CREATE_SCHEMA],
    )

    try:
        flake.register_asset_async(database, assets_queue).wait()
        flake.register_asset_async(db_role, assets_queue).wait()
        flake.register_asset_async(grant, assets_queue).wait()

        ### Act ###
        grants = flake.describe_async(
            describable=RoleGrantDescribable(
                principal=DatabaseRoleDescribable(
                    name=db_role.name, db_name=database.db_name
                )
            )
        ).deserialize_many(RoleGrantEntity)

        ### Assert ###
        assert grants is not None
        assert len(grants) == 3

        usg = next(
            (
                r
                for r in grants
                if r.privilege == Privilege.USAGE and r.granted_on == "DATABASE"
            ),
            None,
        )
        assert usg is not None
        assert (
            usg.granted_by == ""
        )  # Implisit usage grant on databases for database roles
        assert usg.grantee_identifier == db_role.name
        assert usg.grantee_type == "DATABASE_ROLE"
        assert usg.granted_identifier == database.db_name

        cdr = next(
            (
                r
                for r in grants
                if r.privilege == Privilege.CREATE_DATABASE_ROLE
                and r.granted_on == "DATABASE"
            ),
            None,
        )
        assert cdr is not None
        assert cdr.granted_on == "DATABASE"
        assert cdr.granted_by == "SYSADMIN"
        assert cdr.grantee_identifier == db_role.name
        assert cdr.grantee_type == "DATABASE_ROLE"
        assert cdr.granted_identifier == database.db_name

        cs = next(
            (
                r
                for r in grants
                if r.privilege == Privilege.CREATE_SCHEMA and r.granted_on == "DATABASE"
            ),
            None,
        )
        assert cs is not None
        assert cs.granted_on == "DATABASE"
        assert cs.granted_by == "SYSADMIN"
        assert cs.grantee_identifier == db_role.name
        assert cs.grantee_type == "DATABASE_ROLE"
        assert cs.granted_identifier == database.db_name
    finally:
        ### Cleanup ###
        flake.delete_assets(assets_queue)


def test_database_role_schema_grant(
    flake: PyflakeClient, assets_queue: queue.LifoQueue, rand_str: str, comment: str
):
    ### Arrange ###
    user_admin = RoleAsset("USERADMIN")
    sys_admin = RoleAsset("SYSADMIN")
    database = DatabaseAsset(
        f"PYFLAKE_CLIENT_TEST_DB_{rand_str}", comment, owner=sys_admin
    )
    schema = SchemaAsset(database.db_name, "TEST_SCHEMA", comment, sys_admin)
    db_role = DatabaseRoleAsset(
        "PYFLAKE_CLIENT_TEST_DB_ROLE", database.db_name, comment, user_admin
    )
    grant = GrantAction(
        db_role,
        SchemaGrant(database_name=database.db_name, schema_name=schema.schema_name),
        [
            Privilege.USAGE,
            Privilege.CREATE_TABLE,
            Privilege.CREATE_MODEL,
            Privilege.CREATE_SF_ML_ANOMALY_DETECTION,
            Privilege.CREATE_CORTEX_SEARCH_SERVICE,
        ],
    )

    try:
        flake.register_asset_async(database, assets_queue).wait()
        w1 = flake.register_asset_async(schema, assets_queue)
        w2 = flake.register_asset_async(db_role, assets_queue)
        flake.wait_all([w1, w2])
        flake.register_asset_async(grant, assets_queue).wait()

        ### Act ###
        grants = flake.describe_async(
            describable=RoleGrantDescribable(
                principal=DatabaseRoleDescribable(
                    name=db_role.name, db_name=database.db_name
                )
            )
        ).deserialize_many(RoleGrantEntity)

        ### Assert ###
        assert grants is not None
        assert len(grants) == 6

        usg = next(
            (
                r
                for r in grants
                if r.privilege == Privilege.USAGE and r.granted_on == "DATABASE"
            ),
            None,
        )
        assert usg is not None
        assert (
            usg.granted_by == ""
        )  # Implisit usage grant on databases for database roles
        assert usg.grantee_identifier == db_role.name
        assert usg.grantee_type == "DATABASE_ROLE"
        assert usg.granted_identifier == database.db_name

        susg = next(
            (
                r
                for r in grants
                if r.privilege == Privilege.USAGE and r.granted_on == "SCHEMA"
            ),
            None,
        )
        assert susg is not None
        assert susg.granted_by == "SYSADMIN"
        assert susg.grantee_identifier == db_role.name
        assert susg.grantee_type == "DATABASE_ROLE"
        assert susg.granted_identifier == f"{database.db_name}.{schema.schema_name}"

        ct = next(
            (
                r
                for r in grants
                if r.privilege == Privilege.CREATE_TABLE and r.granted_on == "SCHEMA"
            ),
            None,
        )
        assert ct is not None
        assert ct.granted_by == "SYSADMIN"
        assert ct.grantee_identifier == db_role.name
        assert ct.grantee_type == "DATABASE_ROLE"
        assert ct.granted_identifier == f"{database.db_name}.{schema.schema_name}"

        cm = next(
            (
                r
                for r in grants
                if r.privilege == Privilege.CREATE_MODEL and r.granted_on == "SCHEMA"
            ),
            None,
        )
        assert cm is not None
        assert cm.granted_by == "SYSADMIN"
        assert cm.grantee_identifier == db_role.name
        assert cm.grantee_type == "DATABASE_ROLE"
        assert cm.granted_identifier == f"{database.db_name}.{schema.schema_name}"

        mlad = next(
            (
                r
                for r in grants
                if r.privilege == Privilege.CREATE_SF_ML_ANOMALY_DETECTION
                and r.granted_on == "SCHEMA"
            ),
            None,
        )
        assert mlad is not None
        assert mlad.granted_by == "SYSADMIN"
        assert mlad.grantee_identifier == db_role.name
        assert mlad.grantee_type == "DATABASE_ROLE"
        assert mlad.granted_identifier == f"{database.db_name}.{schema.schema_name}"

        cortex = next(
            (
                r
                for r in grants
                if r.privilege == Privilege.CREATE_CORTEX_SEARCH_SERVICE
                and r.granted_on == "SCHEMA"
            ),
            None,
        )
        assert cortex is not None
        assert cortex.granted_by == "SYSADMIN"
        assert cortex.grantee_identifier == db_role.name
        assert cortex.grantee_type == "DATABASE_ROLE"
        assert cortex.granted_identifier == f"{database.db_name}.{schema.schema_name}"
    finally:
        ### Cleanup ###
        flake.delete_assets(assets_queue)
