# Name: Stefan Law
# Course: CS261 - Data Structures
# Assignment: 6 - hash_map_sc
# Due Date: 6/6/24
# Description: Python implementation of hash map utilizing separate
# chaining, along with related helper functions. Built on top of an
# underlying Dynamic Array. Portfolio project for CS261 - Data Structures


from a6_include import (DynamicArray, LinkedList,
                        hash_function_1, hash_function_2)


class HashMap:
    def __init__(self,
                 capacity: int = 11,
                 function: callable = hash_function_1) -> None:
        """
        Initialize new HashMap that uses
        separate chaining for collision resolution
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        self._buckets = DynamicArray()

        # capacity must be a prime number
        self._capacity = self._next_prime(capacity)
        for _ in range(self._capacity):
            self._buckets.append(LinkedList())

        self._hash_function = function
        self._size = 0

    def __str__(self) -> str:
        """
        Override string method to provide more readable output
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        out = ''
        for i in range(self._buckets.length()):
            out += str(i) + ': ' + str(self._buckets[i]) + '\n'
        return out

    def _next_prime(self, capacity: int) -> int:
        """
        Increment from given number and the find the closest prime number
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity % 2 == 0:
            capacity += 1

        while not self._is_prime(capacity):
            capacity += 2

        return capacity

    @staticmethod
    def _is_prime(capacity: int) -> bool:
        """
        Determine if given integer is a prime number and return boolean
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity == 2 or capacity == 3:
            return True

        if capacity == 1 or capacity % 2 == 0:
            return False

        factor = 3
        while factor ** 2 <= capacity:
            if capacity % factor == 0:
                return False
            factor += 2

        return True

    def get_size(self) -> int:
        """
        Return size of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._size

    def get_capacity(self) -> int:
        """
        Return capacity of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._capacity

    # ------------------------------------------------------------------ #

    def put(self, key: str, value: object) -> None:
        """
        A key:value pair are passed as parameters to this function and placed
        in the HashMap based on the key's hash value. If the key already exists
        in the hash map, the associated value is updated. If the current load
        factor of the table is >= 1.0, the table is resized to double its current
        capacity. O(1) average runtime complexity.

        :param: key (string to be hashed)
        :param: value (object of any type to be stored in association with key

        :return: None
        """
        # if current load factor >/= 1.0, table must be resized to
        # double its current capacity
        if self.table_load() >= 1.0:
            self.resize_table(2 * self._capacity)

        # Get key hash and associated LinkedList
        hash = self._hash_function(key)
        index = hash % self._capacity
        list_at_hash = self._buckets[index]

        # If key already in table, update associated value
        if list_at_hash.contains(key):
            # Iterate through LinkedList and find node containing key
            list_at_hash.contains(key).value = value
            return

        # Otherwise, add a new key:value pair, and update size
        list_at_hash.insert(key, value)
        self._size += 1

    def resize_table(self, new_capacity: int) -> None:
        """
        Changes capacity of HashMap to new_capacity parameter. In the process of resizing,
        all key:value pairs are rehashed based on the new capacity. If the passed
        capacity is < 1, the function immediately returns. If the new_capacity is
        not a prime number, it is rounded up to the next prime number.

        :param: new_capacity (integer)
        :return: None
        """
        # Check that new capacity is not less than 1; if so,
        # return
        if new_capacity < 1:
            return

        # Dump keys/values for rehashing
        map_dump = self.get_keys_and_values()

        # If capacity is not a prime number, round up to the next prime number
        if not self._is_prime(new_capacity):
            new_capacity = self._next_prime(new_capacity)

        # Increase capacity x2 until larger than size
        while new_capacity < self._size:
            new_capacity = self._next_prime(new_capacity * 2)

        # Add additional buckets if needed
        if new_capacity > self.get_capacity():
            new_buckets = new_capacity - self.get_capacity()
            for _ in range(new_buckets):
                self._buckets.append(LinkedList())

        # Remove excess buckets if needed
        elif new_capacity < self.get_capacity():
            while new_capacity < self.get_capacity():
                self._buckets.pop()
                self._capacity -= 1

        # Update capacity
        self._capacity = new_capacity

        # Re-hash and transfer all items in current HashMap
        self.clear()
        while map_dump.length() != 0:
            key, value = map_dump.pop()
            self.put(key, value)

    def table_load(self) -> float:
        """
        Calculates and returns the current load factor (# of elements/capacity).
        O(1) runtime complexity.
        :param: None

        :return: load_factor (float)
        """

        load_factor = self._size / self._capacity

        return load_factor

    def empty_buckets(self) -> int:
        """
        Calculates and returns the current number of empty buckets in the
        HashMap table.

        :param: None
        :return: empty (int)
        """
        # Determine the difference of the capacity of the HashMap and
        # the current filled subarray
        empty = 0
        index = 0
        while index != self.get_capacity():
            if self._buckets[index].length() == 0:
                empty += 1

            index += 1

        return empty

    def get(self, key: str):
        """
        Iterates through list indicated by key's hash, looking for matching key that is passed to
        this function as a parameter. If a match is found, the associated value
        is returned, otherwise the function will return None. O(1) average runtime
        complexity.

        :param: key (string, key to be matched in HashMap)
        :returns: associated value(object of any type) if matching key is found, otherwise None
        """
        # Determine hash
        hash = self._hash_function(key)
        index = hash % self._capacity

        # Iterate thru list at index to look for key and return value associated with key
        item = self._buckets[index].contains(key)
        if item:
            return item.value
        # No matches were found
        return None

    def contains_key(self, key: str) -> bool:
        """
        Iterates through the list indicated by the key's hash, looking for the key passed to this function
        as a parameter. If the key is found, the function returns True; otherwise,
        returns False.

        :param: key (string)
        :return: Boolean (True if key is found, otherwise False)
        """
        # Determine hash
        hash = self._hash_function(key)
        index = hash % self._capacity

        # Iterate thru list at index to look for key and return True if found
        item = self._buckets[index].contains(key)
        if item:
            return True
        # No matches were found
        return False

    def remove(self, key: str) -> None:
        """
        Iterate through list indicated by key's hash. If a match is found,
        the node is removed and the size is adjusted. O(1) runtime complexity.

        :param: self (string)
        :return: None
        """
        # Determine hash
        hash = self._hash_function(key)
        index = hash % self._capacity

        # look for key and remove if found
        if self._buckets[index].contains(key):
            self._buckets[index].remove(key)
            self._size -= 1

    def get_keys_and_values(self) -> DynamicArray:
        """
        Returns a DynamicArray containing tuples of all
        stored key/value pairs in the HashMap.

        :param: None
        :return: output_array (DynamicArray)
        """
        # Create output array
        output_array = DynamicArray()

        # iterate through linked lists in HashMap
        index = 0
        while index != self._buckets.length():
            linked_list = self._buckets[index]
            # iterate through linked list and insert key:value pair into output array as a tuple
            for item in linked_list:
                output_array.append((item.key, item.value))
            index += 1

        return output_array

    def clear(self) -> None:
        """
        Removes all stored key/value pairs in the HashMap and updates size
        without altering the underlying capacity.
        :param: None
        :return: None
        """
        # Iterate through each bucket/list
        index = 0
        while index != self.get_capacity():
            # Empty each list
            self._buckets[index] = LinkedList()
            index += 1

        # Reset size
        self._size = 0


def find_mode(da: DynamicArray) -> tuple[DynamicArray, int]:
    """
    Receives an unsorted DynamicArray and determines the mode and associated
    value(s), returning a tuple containing an array of the value(s)
    and the mode. The array is first placed into a HashMap, with the values
    of the array being stored as keys and their frequency being stored as values.
    The key/value pairs of the map are then dumped using get_keys_and_values(),
    and the resulting array is iterated over to determine the mode and associated
    key(s), which are then placed in an output array and returned along with the mode.
    O(N) runtime complexity.

    :param: da (DynamicArray)
    :returns: tuple (DynamicArray, int)
    """
    map = HashMap(11, hash_function_2)
    output_arr = None
    freq = 0

    index = 0
    # Iterate through input array and create a HashMap for each potential key,
    # and store a frequency count in the key's associated value
    while index != da.length():
        key = da[index]
        if map.contains_key(key):
            map.put(key, map.get(key) + 1)
        else:
            map.put(key, 1)
        index += 1
    # Iterate through map, testing each key to see if it's value is equal to
    # or higher than current frequency. If higher, we need to clear the output
    # array, update the frequency, and append the key to the output array. If
    # equal, then we need to append the key to the output array.
    map_dump = map.get_keys_and_values()
    index = 0
    while index < map_dump.length():
        item = map_dump[index]
        if item[1] > freq:
            output_arr = DynamicArray()
            freq = item[1]
            output_arr.append(item[0])
        elif item[1] == freq:
            output_arr.append(item[0])
        index += 1

    return output_arr, freq


# ------------------- BASIC TESTING ---------------------------------------- #

if __name__ == "__main__":

    print("\nPDF - put example 1")
    print("-------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('str' + str(i), i * 100)
        if i % 25 == 24:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - put example 2")
    print("-------------------")
    m = HashMap(41, hash_function_2)
    for i in range(50):
        m.put('str' + str(i // 3), i * 100)
        if i % 10 == 9:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - resize example 1")
    print("----------------------")
    m = HashMap(20, hash_function_1)
    m.put('key1', 10)
    print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))
    m.resize_table(30)
    print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))

    print("\nPDF - resize example 2")
    print("----------------------")
    m = HashMap(75, hash_function_2)
    keys = [i for i in range(1, 1000, 13)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())

    for capacity in range(111, 1000, 117):
        m.resize_table(capacity)

        m.put('some key', 'some value')
        result = m.contains_key('some key')
        m.remove('some key')

        for key in keys:
            # all inserted keys must be present
            result &= m.contains_key(str(key))
            # NOT inserted keys must be absent
            result &= not m.contains_key(str(key + 1))
        print(capacity, result, m.get_size(), m.get_capacity(), round(m.table_load(), 2))

    print("\nPDF - table_load example 1")
    print("--------------------------")
    m = HashMap(101, hash_function_1)
    print(round(m.table_load(), 2))
    m.put('key1', 10)
    print(round(m.table_load(), 2))
    m.put('key2', 20)
    print(round(m.table_load(), 2))
    m.put('key1', 30)
    print(round(m.table_load(), 2))

    print("\nPDF - table_load example 2")
    print("--------------------------")
    m = HashMap(53, hash_function_1)
    for i in range(50):
        m.put('key' + str(i), i * 100)
        if i % 10 == 0:
            print(round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - empty_buckets example 1")
    print("-----------------------------")
    m = HashMap(101, hash_function_1)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key1', 10)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key2', 20)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key1', 30)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key4', 40)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())

    print("\nPDF - empty_buckets example 2")
    print("-----------------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('key' + str(i), i * 100)
        if i % 30 == 0:
            print(m.empty_buckets(), m.get_size(), m.get_capacity())

    print("\nPDF - get example 1")
    print("-------------------")
    m = HashMap(31, hash_function_1)
    print(m.get('key'))
    m.put('key1', 10)
    print(m.get('key1'))

    print("\nPDF - get example 2")
    print("-------------------")
    m = HashMap(151, hash_function_2)
    for i in range(200, 300, 7):
        m.put(str(i), i * 10)
    print(m.get_size(), m.get_capacity())
    for i in range(200, 300, 21):
        print(i, m.get(str(i)), m.get(str(i)) == i * 10)
        print(i + 1, m.get(str(i + 1)), m.get(str(i + 1)) == (i + 1) * 10)

    print("\nPDF - contains_key example 1")
    print("----------------------------")
    m = HashMap(53, hash_function_1)
    print(m.contains_key('key1'))
    m.put('key1', 10)
    m.put('key2', 20)
    m.put('key3', 30)
    print(m.contains_key('key1'))
    print(m.contains_key('key4'))
    print(m.contains_key('key2'))
    print(m.contains_key('key3'))
    m.remove('key3')
    print(m.contains_key('key3'))

    print("\nPDF - contains_key example 2")
    print("----------------------------")
    m = HashMap(79, hash_function_2)
    keys = [i for i in range(1, 1000, 20)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())
    result = True
    for key in keys:
        # all inserted keys must be present
        result &= m.contains_key(str(key))
        # NOT inserted keys must be absent
        result &= not m.contains_key(str(key + 1))
    print(result)

    print("\nPDF - remove example 1")
    print("----------------------")
    m = HashMap(53, hash_function_1)
    print(m.get('key1'))
    m.put('key1', 10)
    print(m.get('key1'))
    m.remove('key1')
    print(m.get('key1'))
    m.remove('key4')

    print("\nPDF - get_keys_and_values example 1")
    print("------------------------")
    m = HashMap(11, hash_function_2)
    for i in range(1, 6):
        m.put(str(i), str(i * 10))
    print(m.get_keys_and_values())

    m.put('20', '200')
    m.remove('1')
    m.resize_table(2)
    print(m.get_keys_and_values())

    print("\nPDF - clear example 1")
    print("---------------------")
    m = HashMap(101, hash_function_1)
    print(m.get_size(), m.get_capacity())
    m.put('key1', 10)
    m.put('key2', 20)
    m.put('key1', 30)
    print(m.get_size(), m.get_capacity())
    m.clear()
    print(m.get_size(), m.get_capacity())

    print("\nPDF - clear example 2")
    print("---------------------")
    m = HashMap(53, hash_function_1)
    print(m.get_size(), m.get_capacity())
    m.put('key1', 10)
    print(m.get_size(), m.get_capacity())
    m.put('key2', 20)
    print(m.get_size(), m.get_capacity())
    m.resize_table(100)
    print(m.get_size(), m.get_capacity())
    m.clear()
    print(m.get_size(), m.get_capacity())

    print("\nGradescope - put test")
    print("-----------------------------")
    m = HashMap(11, hash_function_2)
    m.put('key61', 452)
    m.put('key514', 93)
    m.put('key293', -528)
    m.put('key207', 174)
    m.put('key632', -502)
    m.put('key840', 932)
    m.put('key895', 478)
    m.put('key496', 356)
    m.put('key651', -456)
    m.put('key107', -58)
    m.put('key635', 661)
    print(m.get_capacity(), m.get_size())
    m.put('key945', -975)
    print(m.get_capacity(), m.get_size())

    print("\nGradescope - failed resize test")
    print("-----------------------------")
    m = HashMap(59, hash_function_1)
    m.put('key101', -360)
    m.put('key210', 151)
    m.put('key413', -506)
    m.put('key125', 385)
    m.put('key136', -824)
    m.put('key519', -991)
    m.put('key816', -434)
    m.put('key728', 330)
    m.put('key459', 701)
    m.put('key199', -455)
    m.put('key884', -489)
    m.put('key67', -145)
    m.put('key76', 867)
    print(m.get_size(), m.get_capacity())
    m.resize_table(2)
    print(m.get_size(), m.get_capacity())

    print("\nGradescope - failed empty buckets test")
    print("-----------------------------")
    m = HashMap(23, hash_function_1)
    m.put('key300', 352)
    m.put('key670', -30)
    m.put('key79', 132)
    m.put('key643', -202)
    m.put('key562', -478)
    m.put('key426', 299)
    m.put('key818', 384)
    m.put('key70', 729)
    m.put('key567', -334)
    m.put('key107', 616)
    m.put('key374', -822)
    m.put('key446', 302)
    m.put('key362', 30)
    print(m.get_capacity(), m.get_size())

    print("\nPDF - find_mode example 1")
    print("-----------------------------")
    da = DynamicArray(["apple", "apple", "grape", "melon", "peach"])
    mode, frequency = find_mode(da)
    print(f"Input: {da}\nMode : {mode}, Frequency: {frequency}")

    print("\nPDF - find_mode example 2")
    print("-----------------------------")
    test_cases = (
        ["Arch", "Manjaro", "Manjaro", "Mint", "Mint", "Mint", "Ubuntu", "Ubuntu", "Ubuntu"],
        ["one", "two", "three", "four", "five"],
        ["2", "4", "2", "6", "8", "4", "1", "3", "4", "5", "7", "3", "3", "2"]
    )

    for case in test_cases:
        da = DynamicArray(case)
        mode, frequency = find_mode(da)
        print(f"Input: {da}\nMode : {mode}, Frequency: {frequency}\n")
