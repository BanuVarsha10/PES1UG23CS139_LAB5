"""
Inventory Management System
Performs basic inventory operations: add, remove, save, load, and check stock.
Improved using static code analysis fixes (Pylint, Bandit, Flake8).
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    filename="inventory.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global variable (mutate, don't rebind)
stock_data: Dict[str, int] = {}


def add_item(item: str = "default", qty: int = 0, logs: Optional[List[str]] = None) -> None:
    """Add an item and quantity to the inventory."""
    if logs is None:
        logs = []
    if not isinstance(item, str) or not isinstance(qty, (int, float)):
        logger.warning("Invalid item or quantity type provided: item=%r qty=%r", item, qty)
        return

    stock_data[item] = stock_data.get(item, 0) + qty
    logs.append(f"{datetime.now()}: Added {qty} of {item}")

    # Use lazy % formatting for logging to avoid f-string interpolation cost
    logger.info(
        "%s: Added %s of %s to inventory list successfully",
        datetime.now(),
        qty,
        item,
    )


def remove_item(item: str, qty: int) -> None:
    """Remove a specified quantity of an item from inventory."""
    if not isinstance(item, str):
        logger.warning("remove_item: item must be a string; got %r", item)
        return
    try:
        qty_int = int(qty)
    except (TypeError, ValueError):
        logger.warning("remove_item: qty must be an integer; got %r", qty)
        return

    if item in stock_data:
        try:
            stock_data[item] -= qty_int
            if stock_data[item] <= 0:
                del stock_data[item]
                logger.info("remove_item: %s removed from inventory.", item)
        except KeyError as error:
            logger.error("Error removing %s: %s", item, error)
    else:
        logger.warning("Attempted to remove non-existent item: %s", item)


def get_qty(item: str) -> int:
    """Return the quantity of a specific item."""
    if not isinstance(item, str):
        logger.warning("get_qty: item must be a string; got %r", item)
        return 0
    return int(stock_data.get(item, 0))


def load_data(file: str = "inventory.json") -> None:
    """Load inventory data from a JSON file without rebinding the global dict."""
    path = Path(file)
    if not path.exists():
        logger.info("load_data: file %r not found. Starting with empty inventory.", file)
        # ensure stock_data is empty but keep same dict object
        stock_data.clear()
        return

    try:
        with path.open("r", encoding="utf-8") as file_obj:
            data = json.load(file_obj)
    except (OSError, json.JSONDecodeError) as exc:
        logger.error("load_data: failed to load %r: %s", file, exc)
        stock_data.clear()
        return

    # Update existing dict rather than rebinding (avoids global)
    stock_data.clear()
    if isinstance(data, dict):
        for k, v in data.items():
            try:
                stock_data[str(k)] = int(v)
            except (TypeError, ValueError):
                logger.warning("load_data: invalid quantity for %r -> %r, skipping", k, v)
    else:
        logger.warning("load_data: data in %r is not a dict; starting with empty inventory.", file)


def save_data(file: str = "inventory.json") -> None:
    """Save current inventory data to a JSON file."""
    path = Path(file)
    try:
        with path.open("w", encoding="utf-8") as file_obj:
            json.dump(stock_data, file_obj, indent=4, ensure_ascii=False)
            logger.info("save_data: inventory data saved to %r", file)
    except OSError as error:
        logger.error("save_data: failed to save inventory data to %r: %s", file, error)


def print_data() -> None:
    """Print all items and their quantities."""
    print("\nInventory Report:")
    for item, quantity in stock_data.items():
        print(f"{item} -> {quantity}")
    logger.info("print_data: inventory report printed.")


def check_low_items(threshold: int = 5) -> List[str]:
    """Return items with quantity below the given threshold."""
    try:
        thr = int(threshold)
    except (TypeError, ValueError):
        logger.warning("check_low_items: threshold must be an integer; got %r", threshold)
        thr = 5
    result = [item for item, qty in stock_data.items() if qty < thr]
    logger.info("check_low_items: items below %d checked", thr)
    return result


def main() -> None:
    """Main function to test inventory operations."""
    add_item("apple", 10)
    add_item("banana", 3)
    add_item(123, "ten")  # invalid types logged inside add_item
    remove_item("apple", 3)
    remove_item("orange", 1)
    print("Apple stock:", get_qty("apple"))
    print("Low items:", check_low_items())
    save_data()
    load_data()
    print_data()


if __name__ == "__main__":
    main()
