# Name: Stefan Law
# Course: CS261 - Data Structures
# Assignment: 6 - hash_map_oa
# Due Date: 6/6/24
# Description: Python implementation of hash map utilizing open addressing
# with quadratic programming, along with related helper functions. Built on
# top of an underlying Dynamic Array. Portfolio project for CS261- Data Structures

from a6_include import (DynamicArray, DynamicArrayException, HashEntry,
                        hash_function_1, hash_function_2)


class HashMap:
    def __init__(self, capacity: int, function) -> None:
        """
        Initialize new HashMap that uses
        quadratic probing for collision resolution
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        self._buckets = DynamicArray()

        # capacity must be a prime number
        self._capacity = self._next_prime(capacity)
        for _ in range(self._capacity):
            self._buckets.append(None)

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
        Increment from given number to find the closest prime number
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
        Add key/value pair to HashMap. If load factor >= 0.5,
        first double the capacity of the HashMap and rehash it.
        Use quadratic probe/addressing to determine placement of
        key/value pair and store it in a HashEntry object. If the
        key already exists in the HashMap, update it's associated
        value.

        :param: key (string)
        :param: value (object of any type)
        :return: None
        """
        # If load factor > 0.5, double capacity using resize
        if self.table_load() >= 0.5:
            self.resize_table(2 * self.get_capacity())

        # Get hash
        hash = self._hash_function(key)
        index = hash % self.get_capacity()

        # Quadratic probe for next empty slot or _TS_ based on hash
        j = 1
        i = index
        while self._buckets[index] and not self._buckets[index].is_tombstone:
            # If key is already in map, update value
            if self._buckets[index].key == key:
                self._buckets[index].value = value
                return
            index = (i + (j ** 2)) % self.get_capacity()
            j += 1

        # Otherwise, add new HashEntry at index
        self._buckets[index] = HashEntry(key, value)

        self._size += 1


    def resize_table(self, new_capacity: int) -> None:
        """
        Resize table to new_capacity. If new_capacity is not
        prime, round to next prime number. Contents of old table
        are rehashed into new table.

        :param: new_capacity(integer)
        :return: None
        """
        # If new_capacity is less than # of elements, then return
        if new_capacity < self._size:
            return

        # If capacity is not prime, round to next prime
        if not self._is_prime(new_capacity):
            new_capacity = self._next_prime(new_capacity)

        # Create new table
        new_array = DynamicArray()
        for _ in range(new_capacity):
            new_array.append(None)

        # Swap old and new array
        old_array = self._buckets
        self._buckets = new_array
        old_capacity = self._capacity
        self._capacity = new_capacity
        self._size = 0

        # Rehash all items that are not tombstoned into new table
        for index in range(old_capacity):
            if old_array[index] and not old_array[index].is_tombstone:
                self.put(old_array[index].key, old_array[index].value)

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
        Calculate number of empty buckets

        :param: none
        :return: int (number of empty buckets)
        """
        return self._capacity - self._size

    def get(self, key: str) -> object:
        """
        Search for key in HashMap using quadratic probing. If the
        key is found return value/object associated with it,
        otherwise return None.

        :param: key (string)
        :return: value(object of any type) if key is found, otherwise None
        """
        # Determine hash
        hash = self._hash_function(key)
        index = hash % self.get_capacity()

        # Probe quadratically until the key is found, or return None
        j = 1
        i = index
        while self._buckets[index]:
            # If key is already in map, return value
            if self._buckets[index].key == key:
                if self._buckets[index].is_tombstone:
                    return None
                return self._buckets[index].value
            index = (i + (j ** 2)) % self.get_capacity()
            j += 1

    def contains_key(self, key: str) -> bool:
        """
        Search for key in HashMap using quadratic probing. If the
        key is found return True, otherwise return False.

        :param: key (string)
        :return: bool
        """
        # Determine hash
        hash = self._hash_function(key)
        index = hash % self.get_capacity()

        # Probe quadratically until the key is found, or return False
        j = 1
        i = index
        while self._buckets[index]:
            # If key is already in map, return value
            if self._buckets[index].key == key:
                if self._buckets[index].is_tombstone:
                    return False
                return True
            index = (i + (j ** 2)) % self.get_capacity()
            j += 1

        return False

    def remove(self, key: str) -> None:
        """
        Remove HashEntry object containing key. If no match is found, nothing happens.
        Otherwise, the item is "removed" by setting "is_tombstone" to True.

        :param: key (string)
        :return: None
        """
        # Determine hash
        hash = self._hash_function(key)
        index = hash % self.get_capacity()

        # Probe quadratically until the key is found, or return False
        j = 1
        i = index
        while self._buckets[index]:
            # If key is in map, tombstone it
            if self._buckets[index].key == key:
                if self._buckets[index].is_tombstone:
                    return
                self._buckets[index].is_tombstone = True
                self._size -= 1
                return
            index = (i + (j ** 2)) % self.get_capacity()
            j += 1

    def get_keys_and_values(self) -> DynamicArray:
        """
        Returns a DynamicArray containing tuples of key/value pairs from
        the HashMap.

        :param: None
        :return: DynamicArray object
        """
        output_arr = DynamicArray()
        index = 0
        while index != self.get_capacity():
            if self._buckets[index] and not self._buckets[index].is_tombstone:
                output_arr.append((self._buckets[index].key, self._buckets[index].value))
            index += 1

        return output_arr

    def clear(self) -> None:
        """
        Clears the HashMap by iterating through the DynamicArray and setting
        contents of each cell to None.

        :param: None
        :return: None
        """
        # Reset size
        self._size = 0

        #Iterate through each bucket
        index = 0
        while index != self.get_capacity():
            # Set each bucket to none
            self._buckets[index] = None
            index += 1

    def __iter__(self):
        """
        Constructs iterator for instance of HashMap class.

        :param: None
        :return: self
        """
        self._index = 0

        return self

    def __next__(self):
        """
        Iterates to next instance of HashEntry inside HashMap.

        :param: none
        :return: value (HashEntry object)
        """

        if self._index == self._capacity:
            raise StopIteration

        while not self._buckets[self._index] or self._buckets[self._index].is_tombstone:
            self._index += 1
            if self._index == self._capacity:
                raise StopIteration

        value = self._buckets[self._index]
        self._index += 1

        return value


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
    keys = [i for i in range(25, 1000, 13)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())

    for capacity in range(111, 1000, 117):
        m.resize_table(capacity)

        if m.table_load() > 0.5:
            print(f"Check that the load factor is acceptable after the call to resize_table().\n"
                  f"Your load factor is {round(m.table_load(), 2)} and should be less than or equal to 0.5")

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
    m = HashMap(11, hash_function_1)
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

    m.resize_table(2)
    print(m.get_keys_and_values())

    m.put('20', '200')
    m.remove('1')
    m.resize_table(12)
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

    print("\nFailed Gradescope put")
    print("---------------------")
    m = HashMap(53, hash_function_1)
    print(m.get_size(), m.get_capacity())
    for i in range(27):
        m.put("str" + str(i), i * 100)
    print(m.get_size(), m.get_capacity())
    m.put("str27", 2700)
    print(m.get_size(), m.get_capacity())

    print("\nPDF - __iter__(), __next__() example 1")
    print("---------------------")
    m = HashMap(10, hash_function_1)
    for i in range(5):
        m.put(str(i), str(i * 10))
    print(m)
    for item in m:
        print('K:', item.key, 'V:', item.value)

    print("\nPDF - __iter__(), __next__() example 2")
    print("---------------------")
    m = HashMap(10, hash_function_2)
    for i in range(5):
        m.put(str(i), str(i * 24))
    m.remove('0')
    m.remove('4')
    print(m)
    for item in m:
        print('K:', item.key, 'V:', item.value)
