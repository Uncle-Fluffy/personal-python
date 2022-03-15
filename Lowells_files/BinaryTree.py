# This class defines a binary tree node
# A binary tree node has
#   data:   data associtated with this node
#   left:   Left  child node (None implies no left  child)
#   right:  Right child node (None implies no right child)
#   parent: Parent node      (None implies no parent or not used)
class BinaryTreeNode:
  def __init__(self, data, left = None, right = None, parent = None):
    self.data   = data
    self.left   = left
    self.right  = right
    self.parent = parent

  # data property getter
  @property
  def data(self):
    return self.__data

  # data property setter
  @data.setter
  def data(self, data):
    self.__data = data

  # left property getter
  @property
  def left(self):
    return self.__left

  # left property setter
  @left.setter
  def left(self, left):
    self.__left = left

  # right property getter
  @property
  def right(self):
    return self.__right

  # right property setter
  @right.setter
  def right(self, right):
    self.__right = right

  # parent property getter
  @property
  def parent(self):
    return self.__parent

  # parent property setter
  @parent.setter
  def parent(self, parent):
    self.__parent = parent

# Create a node recursively creating left and right nodes as needed
# data:   Data        for node
# left:   Left   item for node (tuple of data, left, right or None for no left   item)
# right:  Right  item for node (tuple of data, left, right or None for no right  item)
# parent: Parent item for node (type BinaryTreeNode        or None for no parent item)
# Returns Node with given information
def MakeBinaryTreeNode(data, left, right, parent = None):
  # Get node for left  subtree (parent filled in later)
  left  = None if left ==  None else MakeBinaryTreeNode(left[0],  left[1],  left[2])
  # Get node for right subtree (parent filled in later)
  right = None if right == None else MakeBinaryTreeNode(right[0], right[1], right[2])
  # Create current node
  node  = BinaryTreeNode(data, left, right, parent)
  # Fill in parent node info for left and right subtrees (if they exist)
  if left:  left.parent  = node
  if right: right.parent = node
  # Return newly created node
  return node

# Create a binary tree
# given: Tree node structure
#        series of embedded tuples of (node value, node left item, node right item)
# Returns Tree with given nodes
# Note: As tree is built this way parent is automatically handled
def MakeBinaryTree(given):
  # Get info for root node
  data  = given[0]
  left  = given[1]
  right = given[2]
  # Generate root node
  tree  = MakeBinaryTreeNode(data, left, right, None)
  # Return root node
  return tree

# Performs an in-order traversal of a tree
# tree: Tree to be traversed
# fcn:  Function to call with tree data during traversal
# returns nothing
def TraverseTreeInOrder(tree, fcn):
  if tree == None: return
  left  = tree.left
  right = tree.right
  data  = tree.data
  TraverseTreeInOrder(left, fcn)
  fcn(data)
  TraverseTreeInOrder(right, fcn)

# Performs a pre-order traversal of a tree
# tree: Tree to be traversed
# fcn:  Function to call with tree data during traversal
# returns nothing
def TraverseTreePreOrder(tree, fcn):
  if tree == None: return
  left  = tree.left
  right = tree.right
  data  = tree.data
  fcn(data)
  TraverseTreePreOrder(left, fcn)
  TraverseTreePreOrder(right, fcn)

# Performs a post-order traversal of a tree
# tree: Tree to be traversed
# fcn:  Function to call with tree data during traversal
# returns nothing
def TraverseTreePostOrder(tree, fcn):
  if tree == None: return
  left  = tree.left
  right = tree.right
  data  = tree.data
  TraverseTreePostOrder(left, fcn)
  TraverseTreePostOrder(right, fcn)
  fcn(data)

# Performs a level-order traversal of a tree
# tree: Tree to be traversed
# fcn:  Function to call with tree data during traversal
# returns nothing
def TraverseTreeLevelOrder(tree, fcn):
  # Process a given level of a tree
  # tree:    Tree to process
  # fcn:     Function to call
  # level:   Desired level
  # current: Current level
  # returns True if level found, False otherwise
  # Note: Calls fcn for all items at same level
  #       No call is made if level does not exist
  def ProcessTreeLevel(tree, fcn, level, current = 0):
    # Is this the right level?
    if level == current:
      fcn(tree.data)
      return True   # Level does exist
    # Nope, go to next level
    left  = False if not tree.left  else ProcessTreeLevel(tree.left,  fcn, level, current + 1) 
    right = False if not tree.right else ProcessTreeLevel(tree.right, fcn, level, current + 1)
    # Return wheter or not level exists
    return left or right

  # Seat belt!
  if tree == None: return
  level = 0
  # Loop through different levels
  while True:
    # Get the sum for this level
    result = ProcessTreeLevel(tree, fcn, level)
    # Bail if level does not exist
    if not result: break
    # Next level
    level += 1

if __name__ == "__main__":
  # Make a binary tree
  #      2
  #     / \
  #    1   4
  #       / \
  #      3   5
  tree = MakeBinaryTree((2, (1, None, None), (4, (3, None, None), (5, None, None))))
  print('tree in-order traversal')
  TraverseTreeInOrder(tree, print)
  print('tree pre-order traversal')
  TraverseTreePreOrder(tree, print)
  print('tree post-order traversal')
  TraverseTreePostOrder(tree, print)
  print('tree level-order traversal')
  TraverseTreeLevelOrder(tree, print)
