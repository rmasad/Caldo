class BST:
  def __init__(self, value):
    self.value = value
    self.left = None
    self.right = None

  def add_left(self, value, higher = None):
    if not self.left:
      self.left = BST(value)
    else:
      self.left.add(value, higher)

  def add_right(self, value, higher = None):
    if not self.right:
      self.right = BST(value)
    else:
      self.right.add(value, higher)

  def add(self, value, higher):
    if higher(self.value, value):
      self.add_left(value, higher)
    else:
      self.add_right(value, higher)

  def preOrder(self):
    preOrderResult = []

    if self.left: preOrderResult += self.left.preOrder()
    preOrderResult.append(self.value)
    if self.right: preOrderResult += self.right.preOrder()

    return preOrderResult

  def postOrder(self):
    postOrderResult = []

    if self.right: postOrderResult += self.right.postOrder()
    postOrderResult.append(self.value)
    if self.left: postOrderResult += self.left.postOrder()

    return postOrderResult

def list_to_tree(values, higher):
  Tree = BST(values.pop())
  while values:
    Tree.add(values.pop(), higher)
  return Tree
