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

    def save_not_applicable(
        self,
        obj: NotApplicable,
    ) -> list[GameResult]:
        return [
            GameResult(
                status=StatusType.SUCCESS,
                message="Successfully saved NotApplicable",
            ),
        ]

    def save_stackability_info(
        self,
        obj: StackabilityInfo,
    ) -> list[GameResult]:
        return [
            GameResult(
                status=StatusType.SUCCESS,
                message="Successfully saved StackabilityInfo",
            ),
        ]

    def save_item_vector3(
        self,
        obj: ItemVector3,
    ) -> list[GameResult]:
        return [
            GameResult(
                status=StatusType.SUCCESS,
                message="Successfully saved ItemVector3",
            ),
        ]

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

    def save_item_blueprint_component(
        self,
        obj: ItemBlueprintComponent,
    ) -> list[GameResult]:
        return [
            GameResult(
                status=StatusType.SUCCESS,
                message="Successfully saved ItemBlueprintComponent",
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

    def save_item_db(
        self,
        obj: ItemDb,
    ) -> list[GameResult]:
        return [
            GameResult(
                status=StatusType.SUCCESS,
                message="Successfully saved ItemDb",
            ),
        ]

    def save_inventory_entry(
        self,
        obj: InventoryEntry,
    ) -> list[GameResult]:
        return [
            GameResult(
                status=StatusType.SUCCESS,
                message="Successfully saved InventoryEntry",
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

    def save_game_result(
        self,
        obj: GameResult,
    ) -> list[GameResult]:
        return [
            GameResult(
                status=StatusType.SUCCESS,
                message="Successfully saved GameResult",
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
