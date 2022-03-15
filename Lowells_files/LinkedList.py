# Class for a singly-linked list
class SinglyLinkedNode:
  # Constructor
  # data: Data for this node
  # next: Next link for this node
  def __init__(self, data, next = None):
    self.data = data
    self.next = next

  # data property getter
  @property
  def data(self):
    return self.__data

  # data property setter
  @data.setter
  def data(self, data):
    self.__data = data

  # next property getter
  @property
  def next(self):
    return self.__next

  # next property setter
  @next.setter
  def next(self, next):
    self.__next = next

# Class for a doubly-linked list
class DoublyLinkedNode(SinglyLinkedNode):
  # Constructor
  # data: Data for this node
  # next: Next link for this node
  # prev: Prevoius link for this node
  def __init__(self, data, next = None, prev = None):
    SinglyLinkedNode.__init__(self, data, next)
    self.prev = prev

  # prev property getter
  @property
  def prev(self):
    return self.__prev

  # data property setter
  @prev.setter
  def prev(self, prev):
    self.__prev = prev

# Create a singly-linked list
# info: list of data to be linked
# returns first link in the linked list
def MakeSinglyLinkedList(info):
  # Seat belt
  if info == None: return None
  assert type(info) is list
  # Initialize for loop
  first = None  # First node not defined yet
  prev  = None  # Previous node indicates top of list
  # Loop through items in the list
  for data in info:
    # Create a node with given data
    node = SinglyLinkedNode(data)
    # Save first node in linked list
    if not first: first = node
    # Set previous node's next link
    if prev: prev.next = node
    # This node will be the previous one on next iteration of loop
    prev = node
  # Return the first node in the linked list
  return first

# Create a doubly-linked list
# info: list of data to be linked
# returns first link in the linked list
def MakeDoublyLinkedList(info):
  # Seat belt
  if info == None: return None
  assert type(info) is list
  # Initialize for loop
  first = None  # First node not defined yet
  prev  = None  # Previous node indicates top of list
  # Loop through items in the list
  for data in info:
    # Create a node with given data
    node = DoublyLinkedNode(data, prev = prev)
    # Save first node in linked list
    if not first: first = node
    # Set previous node's next link
    if prev: prev.next = node
    # This node will be the previous one on next iteration of loop
    prev = node
  # Return the first node in the linked list
  return first

if __name__ == "__main__":
  print('Singly-linked list using next:')
  lst = MakeSinglyLinkedList([1, 2, 3, 4, 5])
  while lst:
    print(lst.data)
    lst = lst.next

  print('Doubly-linked list using next')
  lst = MakeDoublyLinkedList([1, 2, 3, 4, 5])
  while lst:
    last = lst
    print(lst.data)
    lst = lst.next
  print('Doubly-linked list using prev')
  while last:
    print(last.data)
    last = last.prev
