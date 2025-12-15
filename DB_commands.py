import os
from db_functions import *
from db_functions import create_page
from typing import BinaryIO, Union
from BPlusTree import BPlusTree
from colorama import Fore


class DBMS:
    def __init__(self):
        self.db_file: Union[BinaryIO, None] = None
        self.page_count = 0
        self.current_table_page = {}
        self.table_tree = {}
        self.schema_slot_indexes = {}

    def create_database(self, name: str) -> None:
        folder = "vina_databases"
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, f"{name}.vndb")
        if os.path.exists(filepath):
            print(Fore.RED + f"Error DataBase {name} already exist You can not create two databases with the same name")
        else:
            self.db_file = open(filepath, "w+b")
            self.db_file.truncate(PAGE_SIZE * 100)
            schema_page = create_page(0)
            self.db_file.write(schema_page)
            self.page_count += 1  # incrementing page count by one so that pages of ordinary tables are inserted from
            # page with index 1 upward

    def create_table(self, name: str):
        if not self.db_file:
            print(Fore.RED + "You must create a ViNa database first of all")
            return
        key: str = input(Fore.BLUE + "Provide table attributes with their data types and constraints\n "
                         "--attr1 type1 pk --attr2 type2 ...\n")
        list_of_attributes = [attr for attr in key.split("--") if attr.strip()]
        self.db_file.seek(0)  # setting page cursor to the first page
        schema_page = bytearray(self.db_file.read(PAGE_SIZE))
        (slot_id, schema_page) = insert_row(schema_page, ", ".join(list_of_attributes).encode("utf-8"))
        if slot_id != -1:
            self.db_file.write(schema_page)  # writing the modified page into file
            self.schema_slot_indexes[name] = slot_id  # this will be used to store count of table info in schema page
            # size schema does not use B+Tree
        else:
            pass
        new_page = create_page(self.page_count)  # creating a new page for the new table
        self.db_file.seek(self.page_count * PAGE_SIZE)
        self.db_file.write(new_page)
        self.current_table_page[name] = self.page_count  # setting the cursor for this table on this particular page
        primary_key = [colon for colon in list_of_attributes if "pk" in colon][0]
        pk_name = [val.strip() for val in primary_key.split(" ") if val.strip()][0]
        self.table_tree[name] = {pk_name: BPlusTree()}  # adding the table B+Tree indexer to the global variable
        self.page_count += 1

    def insert_into_table(self, name: str):
        pass

    def collect_commands(self, command: str):

        if len(command.split(" ")) == 2:
            [instruction, name] = command.split(" ")
            if instruction == "create_db":
                self.create_database(name)
            if instruction == "create_table":
                if len(command) < 18:
                    print("Table name must be at least 4 characters long")
                    return 0
                self.create_table(name)
            if instruction == "insert_into":
                self.insert_into_table(name)
        else:
            print(Fore.RED + "VinaSQL command must have 2 sections; instruction, name")
