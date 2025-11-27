import sys

sys.path.append("../../gen-py")
sys.path.append("..")

from typing import Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

from game.ttypes import (
    ItemRequest,
    ItemResponse,
    ItemRequestData,
    ItemResponseData,
    CreateItemRequestData,
    CreateItemResponseData,
    LoadItemRequestData,
    LoadItemResponseData,
    SaveItemRequestData,
    SaveItemResponseData,
    DestroyItemRequestData,
    DestroyItemResponseData,
    ListItemRequestData,
    ListItemResponseData,
    AutocompleteItemRequestData,
    AutocompleteItemResponseData,
    LoadItemWithBlueprintTreeRequestData,
    LoadItemWithBlueprintTreeResponseData,
    ItemAutocompleteResult,
    BlueprintTreeNode,
    Item,
    GameResult,
    StatusType,
    GameError,
    ServiceMetadata,
    MethodDescription,
    EnumDefinition,
    FieldEnumMapping,
)
from game.ItemService import Iface as ItemServiceIface
from models.item_model import ItemModel
from common import is_ok
from services.base_service import BaseServiceHandler


class ItemServiceHandler(BaseServiceHandler, ItemServiceIface):
    """
    Implementation of the ItemService thrift interface.
    Handles item CRUD operations using the ItemModel layer.
    """

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
    ):
        BaseServiceHandler.__init__(self, ItemServiceHandler)
        self.item_model = ItemModel(host, user, password, database)
        self.database = database

    def create(self, request: ItemRequest) -> ItemResponse:
        """Create a new item."""
        logger.info("=== CREATE item request ===")
        try:
            if not request.data.create_item:
                logger.error("Request data missing create_item field")
                return ItemResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain create_item",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            create_data = request.data.create_item
            logger.info(
                f"Creating item with internal_name={create_data.item.internal_name}"
            )

            results = self.item_model.create(create_data.item)

            if is_ok(results):
                logger.info(f"SUCCESS: Created item with id={create_data.item.id}")
                response_data = ItemResponseData(
                    create_item=CreateItemResponseData(
                        item=create_data.item,
                    ),
                )
                return ItemResponse(
                    results=results,
                    response_data=response_data,
                )
            else:
                logger.warning(
                    f"FAILURE: Could not create item - {results[0].message if results else 'unknown error'}"
                )
                return ItemResponse(
                    results=results,
                    response_data=None,
                )

        except Exception as e:
            logger.error(f"EXCEPTION in create: {type(e).__name__}: {str(e)}")
            return ItemResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to create item: {str(e)}",
                        error_code=GameError.DB_INSERT_FAILED,
                    ),
                ],
                response_data=None,
            )

    def load(self, request: ItemRequest) -> ItemResponse:
        """Load an item by ID."""
        logger.info("=== LOAD item request ===")
        try:
            if not request.data.load_item:
                logger.error("Request data missing load_item field")
                return ItemResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain load_item",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            load_data = request.data.load_item
            item_id = load_data.item_id
            logger.info(f"Loading item_id={item_id}")

            result, item = self.item_model.load(item_id)

            if item:
                logger.info(f"SUCCESS: Loaded item_id={item_id}")
                response_data = ItemResponseData(
                    load_item=LoadItemResponseData(
                        item=item,
                    ),
                )
                return ItemResponse(
                    results=[result],
                    response_data=response_data,
                )
            else:
                logger.warning(f"FAILURE: Item_id={item_id} not found in database")
                return ItemResponse(
                    results=[result],
                    response_data=None,
                )

        except Exception as e:
            logger.error(f"EXCEPTION in load: {type(e).__name__}: {str(e)}")
            return ItemResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to load item: {str(e)}",
                        error_code=GameError.DB_QUERY_FAILED,
                    ),
                ],
                response_data=None,
            )

    def save(self, request: ItemRequest) -> ItemResponse:
        """Save (create or update) an item."""
        logger.info("=== SAVE item request ===")
        try:
            if not request.data.save_item:
                logger.error("Request data missing save_item field")
                return ItemResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain save_item",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            save_data = request.data.save_item
            item_id = save_data.item.id if save_data.item.id else "NEW"
            logger.info(f"Saving item_id={item_id}")

            results = self.item_model.save(save_data.item)

            if is_ok(results):
                logger.info(f"SUCCESS: Saved item_id={save_data.item.id}")
                response_data = ItemResponseData(
                    save_item=SaveItemResponseData(
                        item=save_data.item,
                    ),
                )
                return ItemResponse(
                    results=results,
                    response_data=response_data,
                )
            else:
                logger.warning(
                    f"FAILURE: Could not save item - {results[0].message if results else 'unknown error'}"
                )
                return ItemResponse(
                    results=results,
                    response_data=None,
                )

        except Exception as e:
            logger.error(f"EXCEPTION in save: {type(e).__name__}: {str(e)}")
            return ItemResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to save item: {str(e)}",
                        error_code=GameError.DB_INSERT_FAILED,
                    ),
                ],
                response_data=None,
            )

    def destroy(self, request: ItemRequest) -> ItemResponse:
        """Destroy (delete) an item by ID."""
        logger.info("=== DESTROY item request ===")
        try:
            if not request.data.destroy_item:
                logger.error("Request data missing destroy_item field")
                return ItemResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain destroy_item",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            destroy_data = request.data.destroy_item
            item_id = destroy_data.item_id
            logger.info(f"Destroying item_id={item_id}")

            results = self.item_model.destroy(item_id)

            if is_ok(results):
                logger.info(f"SUCCESS: Destroyed item_id={item_id}")
                response_data = ItemResponseData(
                    destroy_item=DestroyItemResponseData(
                        item_id=item_id,
                    ),
                )
                return ItemResponse(
                    results=results,
                    response_data=response_data,
                )
            else:
                logger.warning(
                    f"FAILURE: Could not destroy item - {results[0].message if results else 'unknown error'}"
                )
                return ItemResponse(
                    results=results,
                    response_data=None,
                )

        except Exception as e:
            logger.error(f"EXCEPTION in destroy: {type(e).__name__}: {str(e)}")
            return ItemResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to destroy item: {str(e)}",
                        error_code=GameError.DB_DELETE_FAILED,
                    ),
                ],
                response_data=None,
            )

    def list_records(self, request: ItemRequest) -> ItemResponse:
        """List items with pagination and optional search."""
        logger.info("=== LIST item records request ===")
        try:
            if not request.data.list_item:
                logger.error("Request data missing list_item field")
                return ItemResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain list_item",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            list_data = request.data.list_item
            page = max(0, list_data.page)
            results_per_page = list_data.results_per_page
            search_string = (
                list_data.search_string if hasattr(list_data, "search_string") else None
            )

            logger.info(
                f"Listing items: page={page}, results_per_page={results_per_page}, search_string={search_string}"
            )

            result, items, total_count = self.item_model.search(
                page,
                results_per_page,
                search_string=search_string,
            )

            if items is not None:
                logger.info(
                    f"SUCCESS: Listed {len(items)} items (total: {total_count})"
                )
                response_data = ItemResponseData(
                    list_item=ListItemResponseData(
                        items=items,
                        total_count=total_count,
                    ),
                )
                return ItemResponse(
                    results=[result],
                    response_data=response_data,
                )
            else:
                logger.warning(f"FAILURE: Could not list items - {result.message}")
                return ItemResponse(
                    results=[result],
                    response_data=None,
                )

        except Exception as e:
            logger.error(f"EXCEPTION in list_records: {type(e).__name__}: {str(e)}")
            return ItemResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to list items: {str(e)}",
                        error_code=GameError.DB_QUERY_FAILED,
                    ),
                ],
                response_data=None,
            )

    def autocomplete(self, request: ItemRequest) -> ItemResponse:
        """Autocomplete search for items (lightweight results)."""
        logger.info("=== AUTOCOMPLETE item request ===")
        try:
            if not request.data.autocomplete_item:
                logger.error("Request data missing autocomplete_item field")
                return ItemResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain autocomplete_item",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            autocomplete_data = request.data.autocomplete_item
            search_string = autocomplete_data.search_string
            max_results = (
                autocomplete_data.max_results
                if hasattr(autocomplete_data, "max_results")
                else 10
            )

            logger.info(
                f"Autocomplete search: search_string={search_string}, max_results={max_results}"
            )

            # Use custom SQL query for lightweight autocomplete
            self.item_model.connect()
            cursor = self.item_model.connection.cursor(dictionary=True)

            # Search by internal_name with LIKE
            query = f"""
                SELECT id, internal_name
                FROM {self.database}.items
                WHERE internal_name LIKE %s
                ORDER BY internal_name
                LIMIT %s
            """

            search_pattern = f"%{search_string}%"
            cursor.execute(
                query,
                (
                    search_pattern,
                    max_results,
                ),
            )
            rows = cursor.fetchall()
            cursor.close()

            results = [
                ItemAutocompleteResult(
                    id=row["id"],
                    internal_name=row["internal_name"],
                )
                for row in rows
            ]

            logger.info(f"SUCCESS: Found {len(results)} autocomplete results")

            response_data = ItemResponseData(
                autocomplete_item=AutocompleteItemResponseData(
                    results=results,
                ),
            )

            return ItemResponse(
                results=[
                    GameResult(
                        status=StatusType.SUCCESS,
                        message=f"Found {len(results)} items",
                    ),
                ],
                response_data=response_data,
            )

        except Exception as e:
            logger.error(f"EXCEPTION in autocomplete: {type(e).__name__}: {str(e)}")
            return ItemResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to autocomplete items: {str(e)}",
                        error_code=GameError.DB_QUERY_FAILED,
                    ),
                ],
                response_data=None,
            )

    def load_with_blueprint_tree(self, request: ItemRequest) -> ItemResponse:
        """Load an item with its complete blueprint tree (recursive)."""
        logger.info("=== LOAD WITH BLUEPRINT TREE item request ===")
        try:
            if not request.data.load_with_blueprint_tree:
                logger.error("Request data missing load_with_blueprint_tree field")
                return ItemResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain load_with_blueprint_tree",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            tree_data = request.data.load_with_blueprint_tree
            item_id = tree_data.item_id
            max_depth = tree_data.max_depth if hasattr(tree_data, "max_depth") else 10

            logger.info(
                f"Loading blueprint tree for item_id={item_id}, max_depth={max_depth}"
            )

            # Load the root item
            result, item = self.item_model.load(item_id)

            if not item:
                logger.warning(f"FAILURE: Item_id={item_id} not found")
                return ItemResponse(
                    results=[result],
                    response_data=None,
                )

            # Build the blueprint tree recursively
            visited_items = set()
            tree = self._build_blueprint_tree_node(
                item,
                visited_items,
                current_depth=0,
                max_depth=max_depth,
            )

            logger.info(
                f"SUCCESS: Built blueprint tree for item_id={item_id}, total_bake_time={tree.total_bake_time_ms}ms"
            )

            response_data = ItemResponseData(
                load_with_blueprint_tree=LoadItemWithBlueprintTreeResponseData(
                    tree=tree,
                ),
            )

            return ItemResponse(
                results=[
                    GameResult(
                        status=StatusType.SUCCESS,
                        message=f"Loaded blueprint tree for item {item.internal_name}",
                    ),
                ],
                response_data=response_data,
            )

        except Exception as e:
            logger.error(
                f"EXCEPTION in load_with_blueprint_tree: {type(e).__name__}: {str(e)}"
            )
            import traceback

            traceback.print_exc()
            return ItemResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to load blueprint tree: {str(e)}",
                        error_code=GameError.DB_QUERY_FAILED,
                    ),
                ],
                response_data=None,
            )

    def _build_blueprint_tree_node(
        self,
        item: Item,
        visited_items: set,
        current_depth: int,
        max_depth: int,
    ) -> BlueprintTreeNode:
        """
        Recursively build a blueprint tree node.

        Args:
            item: The current item to process
            visited_items: Set of item IDs we've already visited (for cycle detection)
            current_depth: Current recursion depth
            max_depth: Maximum recursion depth

        Returns:
            BlueprintTreeNode with the item, blueprint, and recursive components
        """
        logger.debug(
            f"Building tree node for item_id={item.id}, internal_name={item.internal_name}, depth={current_depth}"
        )

        # Initialize the tree node
        component_nodes = []
        component_ratios = []
        total_bake_time = 0
        max_depth_reached = False
        cycle_detected = False

        # Add this item's bake time if it has a blueprint
        if item.blueprint:
            total_bake_time = item.blueprint.bake_time_ms
            logger.debug(
                f"Item has blueprint with bake_time={item.blueprint.bake_time_ms}ms"
            )

            # Check if we can recurse deeper
            if current_depth >= max_depth:
                logger.debug(f"Max depth {max_depth} reached at item_id={item.id}")
                max_depth_reached = True
            elif item.blueprint.components:
                # Process each component
                for component_item_id, component in item.blueprint.components.items():
                    logger.debug(
                        f"Processing component: item_id={component_item_id}, ratio={component.ratio}"
                    )

                    # Check for cycles
                    if component_item_id in visited_items:
                        logger.debug(
                            f"Cycle detected: item_id={component_item_id} already visited"
                        )
                        cycle_detected = True
                        continue

                    # Load the component item
                    result, component_item = self.item_model.load(component_item_id)

                    if component_item:
                        # Add to visited set
                        new_visited = visited_items.copy()
                        new_visited.add(item.id)

                        # Recursively build the component's tree
                        component_node = self._build_blueprint_tree_node(
                            component_item,
                            new_visited,
                            current_depth + 1,
                            max_depth,
                        )

                        # Add to lists
                        component_nodes.append(component_node)
                        component_ratios.append(component.ratio)

                        # Add component's total bake time to our total
                        total_bake_time += component_node.total_bake_time_ms
                    else:
                        logger.warning(
                            f"Could not load component item_id={component_item_id}"
                        )

        logger.debug(
            f"Node for item_id={item.id}: total_bake_time={total_bake_time}ms, {len(component_nodes)} components"
        )

        return BlueprintTreeNode(
            item=item,
            blueprint=item.blueprint,
            component_nodes=component_nodes,
            component_ratios=component_ratios,
            total_bake_time_ms=total_bake_time,
            max_depth_reached=max_depth_reached,
            cycle_detected=cycle_detected,
        )
