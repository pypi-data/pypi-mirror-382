from collections import deque
import json


class TreeNode:
    def __init__(self, name, value, node_type, selected_models=None, left=None, right=None):
        # if node_type not in ["root", "imp", "automl", "hbd", "rsp", "clf"]:
        #     raise ValueError("Node type {} not supported in TreeNode".format(node_type))
        self.node_name = name
        self.node_type = node_type
        self.left = left
        self.right = right
        self.max_leaf_value = value  # Initialize max_leaf_value with node value
        self.max_value_pipe = []
        self.index = {}
        self.available_models = selected_models if selected_models else []

class BinaryTree:
    def __init__(self):
        self.root = TreeNode("root", -1, "root")

    def insert(self, name, value, node_type, parent_type, selected_models=None):
        node = TreeNode(name, value, node_type, selected_models)

        self._search_insert(parent_type, node, self.root)

    def _search_insert(self, parent_type, child, parent):
        if parent is None:
            return
        if parent.node_type != parent_type:
            self._search_insert(parent_type, child, parent.left)
            self._search_insert(parent_type, child, parent.right)
        else:
            self._insert(parent, child)

    def _insert(self, parent: TreeNode, child: TreeNode):
        if parent.left is None:
            parent.left = child
        elif parent.right is None:
            if parent.left.max_leaf_value >= child.max_leaf_value:
                parent.right = child
            else:
                parent.right = parent.left
                parent.left = child
        else:
            self.print_tree()
            raise ValueError("Tree node is full, no more insert")

    def _search_recursive(self, node, node_type, max_value=None, node_name=None):
        """ Search for node_type in BinaryTree
            if max_value is not None, replace the max_leaf_value for all the element of the path

        Return
        ----------
        The path found
        """
        if node is None:
            return None

        if node.node_type == node_type:
            if max_value is not None:
                node.max_leaf_value = max_value
                node.node_name = node_name
            return [node.node_name]

        for child in [node.left, node.right]:
            if child:
                path = self._search_recursive(child, node_type, max_value, node_name)
                if path:
                    if max_value is not None:
                        node.max_leaf_value = max(node.left.max_leaf_value if node.left else -1,
                                                  node.right.max_leaf_value if node.right else -1)
                        self._ensure_order(node)
                    return [node.node_name] + path
        return None

    @staticmethod
    def _ensure_order(node):
        """Ensure that left child always has the largest max_leaf_value."""
        if node.left and node.right and node.left.max_leaf_value < node.right.max_leaf_value:
            node.left, node.right = node.right, node.left

    def replace(self, node_type, max_value, node_name):
        """ Replace the max_leaf_value for all the element of the path """
        # node = self._search(node_type, max_value)
        node = self._search_recursive(self.root, node_type, max_value, node_name=node_name)
        if node is None:
            return None
        self.root.max_leaf_value = max_value

    def _search_node(self, node: TreeNode, target_type) -> TreeNode:
        """Search for a given node type downward from a node in a tree"""
        if node is None:
            return False
        if node.node_type == target_type:
            return node
        else:
            left = self._search_node(node.left, target_type)
            if left:
                return left

            right = self._search_node(node.right, target_type)
            if right:
                return right


    def update_pipe(self, pipe, value):
        """ check if sub-branch of the  BinaryTree need to be updated or not

        Return
        ----------
        Ture : if it updated the BinaryTree
        False : if it didn't update the BinaryTree
        """
        if len(pipe) == 1:
            target_node = self._search_node(self.root, "automl")
            if target_node.max_leaf_value < value:
                self.replace("automl", value, pipe[0])
                return True
            else:
                return False

        elif len(pipe) == 2:
            target_node = self._search_node(self.root, "hbd")
            if target_node.max_leaf_value < value:
                self.replace("imp", value, pipe[0])
                self.replace("hbd", value, pipe[1])
                return True
            else:
                return False

        elif len(pipe) == 3:
            target_node = self._search_node(self.root, "clf")
            if target_node.max_leaf_value < value:
                self.replace("imp", value, pipe[0])
                self.replace("rsp", value, pipe[1])
                self.replace("clf", value, pipe[2])
                return True
            else:
                return False

    def best_pipe(self):
        node = self.root.left
        pipe = []
        while node is not None:
            pipe.append(node.node_name)
            node = node.left

        return pipe

    def sub_best_pipe(self, node_type="automl"):
        """ Search for the best pipe built with node_type """
        node = self._search_node(self.root, target_type=node_type)
        pipe = []
        while node is not None:
            pipe.append(node.node_name)
            node = node.left
        return pipe

    def build_pipe(self, node_type):
        """Build the pipeline with the last element of the pipeline as node_type"""
        if node_type not in ["clf", "hbd", "automl"]:
            raise ValueError(
                "Please select the last element of the pipeline as the node_type, {} is not".format(node_type))
        else:
            result = self._search_recursive(self.root, node_type=node_type)
            return result[1:]

    def print_tree(self):
        print("----------------")
        self._print_tree_recursive(self.root, 0)
        print("----------------")

    def _print_tree_recursive(self, node, level):
        if node is not None:
            self._print_tree_recursive(node.right, level + 1)
            print("     " * level + str(node.node_name) + " " + str(node.node_type) + " (" + str(node.max_leaf_value) + ")" + str(node.available_models))
            self._print_tree_recursive(node.left, level + 1)

    def serialize(self):
        """Serialize the tree to a JSON string"""
        def serialize_node(node):
            if node is None:
                return None
            return {
                'name': node.node_name,
                'value': node.max_leaf_value,
                'type': node.node_type,
                'selected_models': node.available_models,
                'left': serialize_node(node.left),
                'right': serialize_node(node.right)
            }

        return json.dumps(serialize_node(self.root), indent=4)

    def save_to_file(self, filename):
        """Save the serialized tree to a JSON file."""
        serialized_tree = self.serialize()
        with open(filename, 'w') as file:
            file.write(serialized_tree)

    @classmethod
    def load_from_file(cls, filename):
        """Load a tree from a JSON file and deserialize it."""
        with open(filename, 'r') as file:
            serialized_tree = file.read()
        return cls.deserialize(serialized_tree)

    @classmethod
    def deserialize(cls, data):
        """Deserialize the JSON string to reconstruct the tree."""
        def deserialize_node(node_data):
            if node_data is None:
                return None
            node = TreeNode(node_data['name'], node_data['value'], node_data['type'], node_data['selected_models'])
            node.left = deserialize_node(node_data['left'])
            node.right = deserialize_node(node_data['right'])
            return node

        data = json.loads(data)
        root = deserialize_node(data)
        tree = cls()
        tree.root = root
        return tree


if __name__ == "__main__":
    tree = BinaryTree()
    tree.insert("mean", 0, "imp", "root", selected_models=['lr', 'mean'])
    tree.insert("autosklearn", 0, "automl", "root")
    tree.insert("s2sl", 0, "rsp", "imp")
    tree.insert("autosmote", 0, "hbd", "imp")
    tree.insert("svm", 0, "clf", "rsp")
    tree.print_tree()
    tree.save_to_file("test.json")

    load_tree = BinaryTree.load_from_file("test.json")
    load_tree.print_tree()

