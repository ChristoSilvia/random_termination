

class LabeledHeap(object):
	"""
Maintains a heap data structure based around a python array,
	which exposes the standard heap features:

	* `push(element)`: an element can be placed onto the heap.
	* `pop()`: the smallest element currently on the heap
		will be removed from the heap and returned.

The comparison function is by default a normal python comparison,
	but can be user-defined by specifying the `is_less_than`
	named argument at instantiation time.
Both operations take asymptotically log(n) time, where n is the
	number of elements on the heap.

The heap also exposes the additional features:

	* `item_index_dict`: a dictionary which relates the elements
		of the heap to their array indices within the heap's internal
		python array.
	* `reheap_from_decrease_at_index(index)`: if the elements or 
		comparison function change and cause the heap element at
		`index` to decrease, then this function will resort the 
		heap based on the new value.
	* `reheap_from_increase_at_index(index)`: if the elements or 
		comparison function change and cause the heap element at
		`index` to increase, then this function will resort the 
		heap based on the new value.

A heap is a binary tree-type data structure which is implemented
	implicitly with an array.  The array forms a tree by having
	the index i be the parents of the index 2*i + 1 and 2*i + 2.
	The tree is a heap because parents are always smaller than
	children:

	for all i:
		heap[i] < heap[2*i + 1]
		heap[i] < heap[2*i + 2]

When the value of an element on the heap decreses, then it 
	suffices to compare it with its parent, and then swap the two 
	if the element's new value is less than that of its parent.
	Next, from the element's new place on the heap, it compares
	and maybe swaps its value with that of its new parent, and so 
	on, until the element is on the top of the heap, or the 
	element is greater than one of its parents.

When the value of an element on the heap increases, restoring
	the heap invariant is slightly more complicated.  The element
	is compared with its smaller child, and if it is greater
	than its smaller child, then the two elements are swapped.
	This process is repeated at the new site of the increased
	element, until the originally increased element is smaller 
	than its smallest child.

To pop an element out of the heap, the elemet at index 0 is 
	returned.  To restore the heap invariant, the element which
	was at the end of the heap array, python index -1, is placed
	at its position, and then the `reheap_from_increase_at_index`
	subroutine is called on index 0, restoring the heap invariant.
	This takes log(n) time, where n is the number of elements
	in the heap.

To push an element onto the heap, it is placed at the end of the
	heap's array, and then the `reheap_from_increase_at_index`
	routine is run on it, pulling it up towards the top of the heap
	and restoring the heap invariant.
"""
	def __init__(self, 
		initial_elements,
		is_less_than = lambda a,b: a<b):
		
		self.is_less_than = is_less_than

		self.heap = []
		self.item_index_dict = {}

		for item in initial_elements:
			self.push(item)
	
	def _reheap_up(self, index_of_increase, item):
		out_of_order_element_index = index_of_increase
		# record the index of the last index with children
		last_non_leaf_index = (len(self.heap) - 2)//2		

		while out_of_order_element_index <= last_non_leaf_index:
			# find the indices of the current children
			left_child_index = 2*out_of_order_element_index + 1
			right_child_index = 2*out_of_order_element_index + 2

			# find the index of the smaller child
			if right_child_index < len(self.heap) and self.is_less_than(self.heap[right_child_index], self.heap[left_child_index]):
				child_index = right_child_index
			else:
				child_index = left_child_index

			# if the smallest child is less than the parent
			if self.is_less_than(self.heap[child_index], self.heap[out_of_order_element_index]):
				# swap the parent and the child
				child = self.heap[child_index]
				self.heap[child_index] = self.heap[out_of_order_element_index]
				self.heap[out_of_order_element_index] = child

				# record the child's new position in the array
				self.item_index_dict[child] = out_of_order_element_index

				# update the out of order element index
				out_of_order_element_index = child_index
			else:
				break

		self.item_index_dict[item] = out_of_order_element_index
	
	def reheap_from_increase_at_index(self, index_of_increase):
		""" Restore the heap invariant from an increase at 
			index_of_increase """
		self._reheap_up(index_of_increase, self.heap[index_of_increase])

	def reheap_from_increase_at_item(self, item):
		self._reheap_up(self.item_index_dict[item], item)

	def _reheap_down(self, index_of_decrease, item):
		# set the initial out of order index and parent index
		out_of_order_element_index = index_of_decrease
		parent_index = (index_of_decrease - 1) // 2

		while out_of_order_element_index > 0:
			# check if the parent is still less than the child
			if self.is_less_than(self.heap[out_of_order_element_index], 
				self.heap[parent_index]):
				# swap the parent and child's positions on the heap
				parent = self.heap[parent_index]
				self.heap[parent_index] = self.heap[out_of_order_element_index]
				self.heap[out_of_order_element_index] = parent

				# update the parent's new index in the item_index_dict
				self.item_index_dict[parent] = out_of_order_element_index

				# reset the indices
				out_of_order_element_index = parent_index
				parent_index = (out_of_order_element_index-1) // 2
			else:
				break

		# record the new position of the out of order element
		self.item_index_dict[self.heap[out_of_order_element_index]] = out_of_order_element_index

	def reheap_from_decrease_at_index(self, index_of_decrease):
		""" Restory the heap invariant from an increase at
			index_of_decrease"""
		self._reheap_down(index_of_decrease, self.heap[index_of_decrease])

	def reheap_from_decrease_at_item(self, item):
		self._reheap_down(self.item_index_dict[item], item)

	def push(self, item):
		self.heap.append(item)
		last_element_index = len(self.heap)-1
		self.item_index_dict[item] = last_element_index
		self._reheap_down(last_element_index, item)

	def pop(self):
		return_item = self.heap[0]
		self.item_index_dict.pop(return_item, None)
		if len(self.heap) == 1:
			self.heap = []
		else:
			last_item = self.heap.pop()
			self.heap[0] = last_item
			self.item_index_dict[last_item] = 0
			self.reheap_from_increase_at_index(0)
		return return_item

	def verify(self):
		last_index_with_children = (len(self.heap) - 2) // 2
		for i in xrange(last_index_with_children+1):
			assert not self.is_less_than(self.heap[2*i+1], self.heap[i])
			if 2*i+2 < len(self.heap):
				assert not self.is_less_than(self.heap[2*i+2], self.heap[i])

	def verify_dict(self):
		assert set(self.item_index_dict.values()) == set(range(len(self.heap))), (str(self.heap) + "\n" + str(self.item_index_dict) + "\n" + str(sorted(self.item_index_dict.values())))

	def __str__(self):
		return str(self.heap)	

	def __repr__(self):
		return str(self.heap)

	def __nonzero__(self):
		return bool(self.heap)
