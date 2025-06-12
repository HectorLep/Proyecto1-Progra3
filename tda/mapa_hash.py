class HashMap:
    def __init__(self, initial_size=17):
        self.size = initial_size  # Prime number for better distribution
        self.buckets = [[] for _ in range(initial_size)]
        self.item_count = 0
        self.load_factor_threshold = 0.75

    def hash_function(self, key):
        """Hash function for strings or objects with IDs."""
        if hasattr(key, 'id'):
            key = key.id
        if isinstance(key, str):
            return sum(ord(c) * (i + 1) for i, c in enumerate(str(key))) % self.size
        return hash(key) % self.size

    def put(self, key, value):
        """Insert or update key-value pair."""
        if self.item_count / self.size >= self.load_factor_threshold:
            self.resize()
        
        index = self.hash_function(key)
        for i, (k, v) in enumerate(self.buckets[index]):
            if k == key or (hasattr(k, 'id') and hasattr(key, 'id') and k.id == key.id):
                self.buckets[index][i] = (key, value)
                return
        self.buckets[index].append((key, value))
        self.item_count += 1

    def get(self, key):
        """Retrieve value by key."""
        index = self.hash_function(key)
        for k, v in self.buckets[index]:
            if k == key or (hasattr(k, 'id') and hasattr(key, 'id') and k.id == key.id):
                return v
        return None

    def remove(self, key):
        """Remove key-value pair."""
        index = self.hash_function(key)
        for i, (k, v) in enumerate(self.buckets[index]):
            if k == key or (hasattr(k, 'id') and hasattr(key, 'id') and k.id == key.id):
                self.buckets[index].pop(i)
                self.item_count -= 1
                return True
        return False

    def resize(self):
        """Double the size of the hash table and rehash items."""
        old_buckets = self.buckets
        self.size = self.size * 2 + 1  # Next odd number for better distribution
        self.buckets = [[] for _ in range(self.size)]
        self.item_count = 0
        
        for bucket in old_buckets:
            for key, value in bucket:
                self.put(key, value)