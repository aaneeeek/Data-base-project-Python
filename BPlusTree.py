import math
import matplotlib.pyplot as plt


class BPlusTreeNode:
    def __init__(self, keys: list[tuple], level: int, order: int, tree: "BPlusTree", pos=0, left_sibling=None,
                 right_sibling=None, parent=None, is_leaf_node=False):
        # assert order - 1 >= len(keys) >= order/2 - 1, "The number of keys does not satisfy B+Tree criteria"
        self.keys = keys  # [(index1, value1), (index2, value2),...]
        self.level = level
        self.order = order
        self.children: list[BPlusTreeNode] = []
        self.parent: BPlusTreeNode = parent
        self.left_sibling: BPlusTreeNode = left_sibling
        self.right_sibling: BPlusTreeNode = right_sibling
        self.is_leaf_node = is_leaf_node
        self.pos = pos
        self.tree = tree

    def __str__(self):
        children = [child.keys for child in self.children]
        return f"{self.keys} =>[ {children} ]"

    def sort_children(self):
        if self.is_leaf_node:
            pass
        else:
            assert len(self.children) == len(self.keys) + 1, ("Constraint between keys length and children length is "
                                                              "not satisfied")
            print(f"sorting node children {self.keys}")
            for index, child in enumerate(self.children):
                for i in range(len(self.keys)):
                    if i == 0 and child.keys[-1][0] < self.keys[i][0]:
                        intermediary: BPlusTreeNode = self.children[0]
                        self.children[0] = child
                        self.children[index] = intermediary
                        break
                    elif i == len(self.keys) - 1 and child.keys[0][0] >= self.keys[i][0]:
                        intermediary: BPlusTreeNode = self.children[-1]
                        self.children[-1] = child
                        self.children[index] = intermediary
                        break
                    elif i < len(self.keys) - 1 and child.keys[0][0] >= self.keys[i][0] and child.keys[-1][0] < self.keys[i+1][0]:
                        intermediary: BPlusTreeNode = self.children[i+1]
                        self.children[i+1] = child
                        self.children[index] = intermediary
                        break
                child.pos = index
            print("sorting complete")

    def move_to_leaf(self, key: tuple, action: str):
        if not self.is_leaf_node:
            for i, k in enumerate(self.keys):
                if i == 0 and key[0] < k[0]:
                    self.children[0].move_to_leaf(key, action)
                    break
                elif i == len(self.keys) - 1 and key[0] >= k[0]:
                    self.children[-1].move_to_leaf(key, action)
                    break
                elif i < len(self.keys) - 1 and k[0] <= key[0] < self.keys[i + 1][0]:
                    print(self)
                    print(self.keys)
                    self.children[i + 1].move_to_leaf(key, action)
                    break
        else:
            if action == "insert":
                self.leaf_insert_key(key)
            if action == "search":
                found = False
                for k in self.keys:
                    if k[0] == key[0]:
                        print(f"found index {key[0]}, its value is {k[1]}")
                        found = True
                        break
                if not found:
                    print(f"##################{key[0]}Error Not Found#####################")

    def parent_insert_key(self, key: tuple, new_child: "BPlusTreeNode", modified_child: "BPlusTreeNode"):
        assert not self.is_leaf_node, "The node must be a parent node"
        assert len(self.keys) <= self.order - 1
        if self.parent and len(self.keys) + 1 <= self.order - 1:
            print(f"Inserting key inside free space {key}")
            self.keys.append(key)
            self.keys.sort()
            self.children[modified_child.pos] = modified_child
            self.children.insert(modified_child.pos+1, new_child)
            self.children[modified_child.pos+1].parent = self
            self.sort_children()
        else:
            print(f"splitting node due to insufficient space inorder to insert key {key}")
            # create a new list of keys that contains **self.keys and the new key
            print(f"This is the parent node to be split {self}")
            new_keys = self.keys + [key]
            new_keys.sort()
            index = math.floor(len(new_keys)/2)
            keys_to_the_right_node = new_keys[index:]
            keys_to_the_left_node = new_keys[:index-1]
            # create a new list of children that contains **self.children and the new child
            new_children = self.children
            new_children[modified_child.pos] = modified_child
            assert len(new_children) == len(new_keys), (f"New children and key list must respect B+tree constraint "
                                                        f"len_children = {len(new_children)} len_key = {len(new_keys)}")
            new_children.insert(modified_child.pos+1, new_child)
            # create new parent as a sibling to the right
            new_parent_sibling = BPlusTreeNode(keys_to_the_right_node, level=self.level, order=self.order,
                                               tree=self.tree, left_sibling=self, parent=None)
            self.keys = keys_to_the_left_node
            self.children = new_children[:len(self.keys)+1]
            new_parent_sibling.children = new_children[len(self.keys)+1:]
            assert len(self.children) == len(self.keys) + 1, (f"Ensuring balance between key and children "
                                                              f"there are {len(self.children)} children and "
                                                              f"{len(self.keys)} keys")
            assert len(new_parent_sibling.children) == len(new_parent_sibling.keys) + 1, (f"Ensuring balance between "
                                                                                          f"key and children there are "
                                                                                          f"{len(new_parent_sibling.children)} "
                                                                                          f"children and "
                                                                                          f"{len(new_parent_sibling.keys)} keys")
            assert len(self.children) + len(new_parent_sibling.children) == len(new_children), ("number of children"
                                                                                                " does not match")
            if modified_child.pos < len(self.keys):  # if new child is found in the left node
                # then set its parent to the current object
                self.children[modified_child.pos+1].parent = self
            else:
                # if not, set its parent to the newly created parent sibling object
                new_parent_sibling.children[modified_child.pos - len(self.keys)].parent = new_parent_sibling
            print(f"this is self{self}")
            print(f"this is new sibling {new_parent_sibling}")
            if self.parent:
                print("Node has been split but parent is full, splitting parent to create allowance for all children")
                self.parent.parent_insert_key(new_keys[index-1], new_parent_sibling, self)
            else:
                print("No parent to this node, ...creating a parent")
                print(self)
                self.create_new_parent(self, new_parent_sibling, new_keys[index-1])

    def create_new_parent(self, left_child: "BPlusTreeNode", right_child: "BPlusTreeNode", key: tuple):
        new_parent = BPlusTreeNode([key], self.level+1, self.order, self.tree)
        new_parent.children = [left_child, right_child]
        new_parent.children[0].parent = new_parent
        new_parent.children[1].parent = new_parent
        self.tree.root_node = new_parent
        self.tree.height = self.level+1
        print("New Root created")

    def leaf_insert_key(self, key: tuple):
        assert key not in self.keys, "Cannot add two keys with the same index on the same node"
        if len(self.keys) + 1 <= self.order - 1 and self.is_leaf_node:
            print(f"Adding extra key {key} to node")
            self.keys.append(key)
            self.keys.sort()
        elif len(self.keys) + 1 > self.order - 1 and self.is_leaf_node and self.parent:
            print("Cannot add key, node is full. splitting current node to to two")
            if len(self.parent.keys) + 1 <= self.order - 1:
                self.split_leaf_node(key)
            else:
                self.split_parent_node(key)
        elif len(self.keys) + 1 > self.order - 1 and self.is_leaf_node and not self.parent:
            print("This leaf node is orphan creating a sibling and a parent for it")
            new_keys = self.keys + [key]
            new_keys.sort()
            index = new_keys.index(key)
            self.keys = new_keys[:index]
            new_parent = BPlusTreeNode([key], self.level+1, self.order, self.tree)
            new_sibling = BPlusTreeNode(new_keys[index:], self.level, self.order, self.tree, left_sibling=self,
                                        is_leaf_node=True, parent=new_parent)
            self.parent = new_parent
            self.right_sibling = new_sibling
            self.parent.children = [self, new_sibling]
            self.tree.root_node = self.parent
            self.tree.height = self.level+1

    def split_leaf_node(self, key: tuple):
        assert self.is_leaf_node, "This method can only be used on leaf nodes"
        print("Starting leaf node split")
        keys: list[tuple] = self.keys + [key]
        keys.sort()
        index = keys.index(key)
        self.keys = keys[:index]
        new_keys = keys[index:]
        #  create new node sibling with the same parent
        new_sibling: BPlusTreeNode = BPlusTreeNode(new_keys, self.level, self.order, self.tree, left_sibling=self,
                                                   right_sibling=self.right_sibling, parent=self.parent,
                                                   is_leaf_node=True)
        self.right_sibling = new_sibling  # including new node as the new right sibling of the current node
        self.parent.children.append(new_sibling)  # add new node to list of parent sibling
        self.parent.keys.append((new_keys[0][0], 0))  # add new key to parent list of keys
        self.parent.keys.sort()
        self.parent.sort_children()

    def split_parent_node(self, key: tuple):
        # we will first start by splitting current node and then pass in result to the already full parent node for
        # insertion so that the splitting will be done automatically
        # the current node must be a leaf node
        assert self.is_leaf_node, "This method is only for leaf Nodes"
        print("---")
        keys: list[tuple] = self.keys + [key]
        keys.sort()
        index = keys.index(key)
        self.keys = keys[:index]
        new_keys = keys[index:]
        #  create new node sibling with the no parent
        new_sibling: BPlusTreeNode = BPlusTreeNode(new_keys, self.level, self.order, self.tree, left_sibling=self,
                                                   right_sibling=self.right_sibling, parent=None, is_leaf_node=True)
        self.parent.parent_insert_key(key, new_sibling, self)


class BPlusTree:
    def __init__(self):
        self.root_node = BPlusTreeNode([(1, 1, 1)], 1, 5, self, is_leaf_node=True)
        self.height = 1



