import subprocess
import os
from BPlusTree import BPlusTree


def create_database(name: str) -> None:
    folder = "csv_databases"
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"{name}.csv")
    if os.path.exists(filepath):
        print(f"Error DataBase {name} already exist You can not create two databases with the same name")
    else:
        with open(filepath, "w") as file:
            file.close()


def create_table(name: str, attributes: dict, key: list):
    pass


Tree = BPlusTree()
Tree.root_node.move_to_leaf((2, 0), "insert")
Tree.root_node.move_to_leaf((3, 0), "insert")
Tree.root_node.move_to_leaf((4, 0), "insert")
Tree.root_node.move_to_leaf((5, 0), "insert")
Tree.root_node.move_to_leaf((6, 0), "insert")
