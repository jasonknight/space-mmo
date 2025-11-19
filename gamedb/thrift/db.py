import mysql.connector
from typing import Optional
import sys
sys.path.append('gen-py')

from game.ttypes import (
    GameResult,
    StatusType,
    NotApplicable,
    StackabilityInfo,
    ItemVector3,
    Attribute,
    Item,
    ItemBlueprintComponent,
    ItemBlueprint,
    ItemDb,
    InventoryEntry,
    Inventory,
    Mobile,
)


class DB:
    def __init__(self, host: str, user: str, password: str):
        self.host = host
        self.user = user
        self.password = password
        self.connection: Optional[
            mysql.connector.connection.MySQLConnection
        ] = None

    def connect(self):
        if not self.connection or not self.connection.is_connected():
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
            )

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def create_attribute_table(
        self,
        database: str,
    ) -> str:
        return f"""CREATE TABLE IF NOT EXISTS {database}.attributes (
                id BIGINT PRIMARY KEY,
                internal_name VARCHAR(255) NOT NULL,
                visible BOOLEAN NOT NULL,
                attribute_type VARCHAR(50) NOT NULL
            );"""

    def create_attribute_value_table(
        self,
        database: str,
    ) -> str:
        return f"""CREATE TABLE IF NOT EXISTS {database}.attribute_values (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                attribute_id BIGINT NOT NULL,
                bool_value BOOLEAN,
                double_value DOUBLE,
                vector3_x DOUBLE,
                vector3_y DOUBLE,
                vector3_z DOUBLE,
                asset_id BIGINT,
                FOREIGN KEY (attribute_id) REFERENCES {database}.attributes(id)
            );"""

    def create_owner_table(
        self,
        database: str,
    ) -> str:
        return f"""CREATE TABLE IF NOT EXISTS {database}.owners (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                attribute_id BIGINT NOT NULL,
                mobile_id BIGINT,
                item_id BIGINT,
                asset_id BIGINT,
                FOREIGN KEY (attribute_id) REFERENCES {database}.attributes(id)
            );"""

    def create_item_table(
        self,
        database: str,
    ) -> str:
        return f"""CREATE TABLE IF NOT EXISTS {database}.items (
                id BIGINT PRIMARY KEY,
                internal_name VARCHAR(255) NOT NULL,
                max_stack_size BIGINT,
                item_type VARCHAR(50) NOT NULL,
                blueprint_id BIGINT
            );"""

    def create_item_attribute_table(
        self,
        database: str,
    ) -> str:
        return f"""CREATE TABLE IF NOT EXISTS {database}.item_attributes (
                id BIGINT PRIMARY KEY,
                item_id BIGINT NOT NULL,
                internal_name VARCHAR(255) NOT NULL,
                visible BOOLEAN NOT NULL,
                attribute_type VARCHAR(50) NOT NULL,
                FOREIGN KEY (item_id) REFERENCES {database}.items(id)
            );"""

    def create_item_attribute_value_table(
        self,
        database: str,
    ) -> str:
        return f"""CREATE TABLE IF NOT EXISTS {database}.item_attribute_values (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                item_attribute_id BIGINT NOT NULL,
                bool_value BOOLEAN,
                double_value DOUBLE,
                vector3_x DOUBLE,
                vector3_y DOUBLE,
                vector3_z DOUBLE,
                asset_id BIGINT,
                FOREIGN KEY (item_attribute_id) REFERENCES {database}.item_attributes(id)
            );"""

    def create_item_attribute_owner_table(
        self,
        database: str,
    ) -> str:
        return f"""CREATE TABLE IF NOT EXISTS {database}.item_attribute_owners (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                item_attribute_id BIGINT NOT NULL,
                mobile_id BIGINT,
                item_id BIGINT,
                asset_id BIGINT,
                FOREIGN KEY (item_attribute_id) REFERENCES {database}.item_attributes(id)
            );"""

    def create_item_blueprint_table(
        self,
        database: str,
    ) -> str:
        return f"""CREATE TABLE IF NOT EXISTS {database}.item_blueprints (
                id BIGINT PRIMARY KEY,
                bake_time_ms BIGINT NOT NULL
            );"""

    def create_item_blueprint_component_table(
        self,
        database: str,
    ) -> str:
        return f"""CREATE TABLE IF NOT EXISTS {database}.item_blueprint_components (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                item_blueprint_id BIGINT NOT NULL,
                component_item_id BIGINT NOT NULL,
                ratio DOUBLE NOT NULL,
                FOREIGN KEY (item_blueprint_id) REFERENCES {database}.item_blueprints(id)
            );"""

    def create_inventory_table(
        self,
        database: str,
    ) -> str:
        return f"""CREATE TABLE IF NOT EXISTS {database}.inventorys (
                id BIGINT PRIMARY KEY,
                max_entries BIGINT NOT NULL,
                max_volume DOUBLE NOT NULL,
                last_calculated_volume DOUBLE DEFAULT 0.0
            );"""

    def create_inventory_entry_table(
        self,
        database: str,
    ) -> str:
        return f"""CREATE TABLE IF NOT EXISTS {database}.inventory_entrys (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                inventory_id BIGINT NOT NULL,
                item_id BIGINT NOT NULL,
                quantity DOUBLE NOT NULL,
                is_max_stacked BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (inventory_id) REFERENCES {database}.inventorys(id)
            );"""

    def create_mobile_table(
        self,
        database: str,
    ) -> str:
        return f"""CREATE TABLE IF NOT EXISTS {database}.mobiles (
                id BIGINT PRIMARY KEY,
                mobile_type VARCHAR(50) NOT NULL
            );"""

    def create_mobile_attribute_table(
        self,
        database: str,
    ) -> str:
        return f"""CREATE TABLE IF NOT EXISTS {database}.mobile_attributes (
                id BIGINT PRIMARY KEY,
                mobile_id BIGINT NOT NULL,
                internal_name VARCHAR(255) NOT NULL,
                visible BOOLEAN NOT NULL,
                attribute_type VARCHAR(50) NOT NULL,
                FOREIGN KEY (mobile_id) REFERENCES {database}.mobiles(id)
            );"""

    def create_mobile_attribute_value_table(
        self,
        database: str,
    ) -> str:
        return f"""CREATE TABLE IF NOT EXISTS {database}.mobile_attribute_values (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                mobile_attribute_id BIGINT NOT NULL,
                bool_value BOOLEAN,
                double_value DOUBLE,
                vector3_x DOUBLE,
                vector3_y DOUBLE,
                vector3_z DOUBLE,
                asset_id BIGINT,
                FOREIGN KEY (mobile_attribute_id) REFERENCES {database}.mobile_attributes(id)
            );"""

    def create_mobile_attribute_owner_table(
        self,
        database: str,
    ) -> str:
        return f"""CREATE TABLE IF NOT EXISTS {database}.mobile_attribute_owners (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                mobile_attribute_id BIGINT NOT NULL,
                mobile_id BIGINT,
                item_id BIGINT,
                asset_id BIGINT,
                FOREIGN KEY (mobile_attribute_id) REFERENCES {database}.mobile_attributes(id)
            );"""

    def save_attribute(
        self,
        obj: Attribute,
    ) -> list[GameResult]:
        return [
            GameResult(
                status=StatusType.SUCCESS,
                message="Successfully saved Attribute",
            ),
        ]

    def save_item(
        self,
        obj: Item,
    ) -> list[GameResult]:
        return [
            GameResult(
                status=StatusType.SUCCESS,
                message="Successfully saved Item",
            ),
        ]


    def save_item_blueprint(
        self,
        obj: ItemBlueprint,
    ) -> list[GameResult]:
        return [
            GameResult(
                status=StatusType.SUCCESS,
                message="Successfully saved ItemBlueprint",
            ),
        ]


    def save_inventory(
        self,
        obj: Inventory,
    ) -> list[GameResult]:
        return [
            GameResult(
                status=StatusType.SUCCESS,
                message="Successfully saved Inventory",
            ),
        ]

    def save_mobile(
        self,
        obj: Mobile,
    ) -> list[GameResult]:
        return [
            GameResult(
                status=StatusType.SUCCESS,
                message="Successfully saved Mobile",
            ),
        ]
