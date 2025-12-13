import math


class BPlusTreeNode:
    def __init__(self, keys: list[tuple], level: int, order: int, pos=0, left_sibling=None,
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

    def sort_children(self):
        if self.is_leaf_node:
            pass
        else:
            assert len(self.children) == len(self.keys) + 1, ("Constraint between keys length and children length is "
                                                              "not satisfied")
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

    def move_to_leaf(self, key: tuple, action: str):
        if not self.is_leaf_node:
            for i, k in enumerate(self.keys):
                if i == 0 and key[0] < k[0]:
                    self.children[0].move_to_leaf(key, action)
                elif i == len(self.keys) - 1 and key[0] >= k[0]:
                    self.children[-1].move_to_leaf(key, action)
                elif i < len(self.keys) - 1 and k[0] <= key[0] < self.keys[i + 1]:
                    self.children[i + 1].move_to_leaf(key, action)
        else:
            # for k in self.keys:
            #     if k[0] == key[0]:
            #         print("found")
            #         break
            if action == "insert":
                self.leaf_insert_key(key)

    def parent_insert_key(self, key: tuple, new_child: "BPlusTreeNode", modified_child: "BPlusTreeNode"):
        assert not self.is_leaf_node, "The node must be a parent node"
        if len(self.parent.keys) + 1 <= self.order - 1:
            self.keys.append(key)
            self.keys.sort()
            self.children[modified_child.pos] = modified_child
            self.children.insert(modified_child.pos+1, new_child)
            self.children[modified_child.pos+1].parent = self
            self.sort_children()
        else:
            # create a new list of keys that contains **self.keys and the new key
            new_keys = self.keys + [key]
            new_keys.sort()
            index = math.floor(len(new_keys)/2)
            keys_to_the_right_node = new_keys[index:]
            keys_to_the_left_node = new_keys[index-1:]
            # create a new list of children that contains **self.children and the new child
            new_children = self.children
            new_children[modified_child.pos] = modified_child
            new_children.insert(modified_child.pos+1, new_child)
            # create new parent as a sibling to the right
            new_parent_sibling = BPlusTreeNode(keys_to_the_right_node, level=self.level-1, order=self.order,
                                               left_sibling=self, parent=None)
            self.keys = keys_to_the_left_node
            self.children = new_children[:len(self.keys)+1]
            new_parent_sibling.children = new_children[len(self.keys)+1:]
            assert len(self.children) + len(new_parent_sibling.children) == len(new_children), ("number of children"
                                                                                                " does not match")
            if modified_child.pos < len(self.keys):  # if new child is found in the left node
                # then set its parent to the current object
                self.children[modified_child.pos+1].parent = self
            else:
                # if not, set its parent to the newly created parent sibling object
                new_parent_sibling.children[modified_child.pos - len(self.keys)].parent = new_parent_sibling
            if self.parent:
                self.parent.parent_insert_key(key, new_parent_sibling, self)
            else:
                self.create_new_parent(self, new_parent_sibling, keys_to_the_right_node[0])

    def create_new_parent(self, left_child: "BPlusTreeNode", right_child: "BPlusTreeNode", key: tuple):
        new_parent = BPlusTreeNode([key], self.level, self.order)
        new_parent.children = [left_child, right_child]
        new_parent.children[0].parent = new_parent
        new_parent.children[1].parent = new_parent

    def leaf_insert_key(self, key: tuple):
        assert self.is_leaf_node, "Insertion must start at the leaf node"
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
            pass

    def split_leaf_node(self, key: tuple):
        assert self.is_leaf_node, "This method can only be used on leaf nodes"
        keys: list[tuple] = self.keys + [key]
        keys.sort()
        index = keys.index(key)
        self.keys = keys[:index]
        new_keys = keys[index:]
        #  create new node sibling with the same parent
        new_sibling: BPlusTreeNode = BPlusTreeNode(new_keys, self.level, self.order, left_sibling=self,
                                                   right_sibling=self.right_sibling, parent=self.parent)
        self.right_sibling = new_sibling  # including new node as the new right sibling of the current node
        self.parent.children.append(new_sibling)  # add new node to list of parent sibling
        self.parent.keys.append(tuple(new_keys[0][0]))  # add new key to parent list of keys
        self.parent.keys.sort()
        self.parent.sort_children()

    def split_parent_node(self, key: tuple):
        # we will first start by splitting current node and then pass in result to the already full parent node for
        # insertion so that the splitting will be done automatically
        # the current node must be a leaf node
        assert self.is_leaf_node, "This method is only for leaf Nodes"
        keys: list[tuple] = self.keys + [key]
        keys.sort()
        index = keys.index(key)
        self.keys = keys[:index]
        new_keys = keys[index:]
        #  create new node sibling with the no parent
        new_sibling: BPlusTreeNode = BPlusTreeNode(new_keys, self.level, self.order, left_sibling=self,
                                                   right_sibling=self.right_sibling, parent=None, is_leaf_node=True)
        self.parent.parent_insert_key(key, new_sibling, self)


class BPlusTree:
    def __init__(self):
        self.root_node = BPlusTreeNode([(1, 1)], 1, 3, is_leaf_node=True)



