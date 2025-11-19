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
