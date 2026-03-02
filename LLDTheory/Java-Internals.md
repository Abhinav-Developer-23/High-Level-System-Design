# Java Internals — Tricky Outputs & HashMap Working

---

## Part 1: Java Tricky Outputs

Understanding Java's execution model, type system, and memory semantics is critical for interviews. Each example below tests a specific language subtlety.

---

### 1.1 String Pool and Interning

Java maintains a **String Pool** (in the heap, part of metaspace references) where string literals are stored. When you use a literal, Java first checks if it already exists in the pool.

```java
String s1 = "Hello";
String s2 = "Hello";
String s3 = new String("Hello");
String s4 = new String("Hello").intern();

System.out.println(s1 == s2);      // true  — same pool reference
System.out.println(s1 == s3);      // false — s3 is a new heap object
System.out.println(s1 == s4);      // true  — intern() returns pool reference
System.out.println(s1.equals(s3)); // true  — content is the same
```

**How it works in memory:**

```
String Pool (Heap):
  ┌───────────┐
  │  "Hello"  │ ← s1, s2, s4 all point here
  └───────────┘

Heap (non-pool):
  ┌───────────┐
  │  "Hello"  │ ← s3 points here (separate object)
  └───────────┘
```

**How many String objects are created by `String s = new String("Hello")`?**
- **Two** (if "Hello" doesn't already exist in the pool):
  1. One in the String Pool (the literal `"Hello"`).
  2. One on the heap (the `new String(...)` object).
- **One** (if "Hello" already exists in the pool):
  1. Only the heap object is created.

---

### 1.2 Why Strings are Immutable in Java

**Immutable** means once a `String` object is created, its **content can never be changed**. Any operation that looks like it modifies a String actually creates a **new String object**.

**Proof — Strings don't change, new objects are created:**

```java
String s = "Hello";
System.out.println(System.identityHashCode(s)); // e.g. 12345 (memory address)

s = s.concat(" World");
System.out.println(System.identityHashCode(s)); // e.g. 67890 (DIFFERENT address!)

// The original "Hello" object still exists in the String Pool — untouched.
// s now points to a completely NEW object "Hello World".
```

```
Before concat():
  s ──→ "Hello"        (String Pool)

After concat():
  s ──→ "Hello World"  (NEW object on heap)
         "Hello"        (still exists in pool — unchanged, unreferenced by s)
```

**Another example:**

```java
String str = "Java";
String str2 = str;       // Both point to same "Java" in pool

str = str.toUpperCase(); // Creates NEW string "JAVA"

System.out.println(str);  // "JAVA" — new object
System.out.println(str2); // "Java" — original is UNCHANGED
```

**Internally, String's char array is `private final`:**

```java
// Simplified String class (Java source)
public final class String {       // final — cannot be subclassed
    private final byte[] value;   // final — reference can't change after construction
    private int hash;             // Cached hashCode

    // No methods exist that modify value[] after construction!
}
```

### Why is String Made Immutable?

| Reason | Explanation |
|---|---|
| **String Pool optimization** | Multiple references can safely share the same pool object. If Strings were mutable, changing one reference would corrupt all others pointing to the same pool entry. |
| **Security** | Strings are used for class loading, network connections, file paths, DB URLs. If mutable, an attacker could change `"admin"` to `"root"` after a security check. |
| **HashCode caching** | `hashCode()` is computed once and cached. Since the content never changes, the hash is always valid. This makes Strings extremely fast as `HashMap` keys. |
| **Thread safety** | Immutable objects are inherently thread-safe — no synchronization needed. Multiple threads can share the same String safely. |
| **Class loading** | JVM uses Strings to load classes (`Class.forName("com.example.MyClass")`). Mutable strings would break class loading security. |

**String Pool relies on immutability:**

```java
String a = "Hello";
String b = "Hello";
// Both point to the SAME object in pool — safe ONLY because String is immutable

// If String were mutable:
a.setValue("Goodbye");  // (hypothetical)
System.out.println(b);  // Would print "Goodbye"! ← DISASTER
```

**HashMap key safety:**

```java
String key = "userId";
map.put(key, 42);

// If String were mutable:
key.setValue("orderId");  // (hypothetical) hashCode changes!
map.get(key);             // Can't find it — hash is different now, wrong bucket!
// Same problem as MutableKey in HashMap section
```

### StringBuilder vs StringBuffer (When You Need Mutable Strings)

If you need to modify strings frequently (e.g., building a string in a loop), use `StringBuilder` or `StringBuffer` — they are **mutable**.

```java
// ❌ BAD — creates many intermediate String objects
String result = "";
for (int i = 0; i < 10000; i++) {
    result += i;  // Each += creates a NEW String object!
}
// Creates ~10,000 temporary String objects → slow, wasteful

// ✅ GOOD — uses a single mutable buffer
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 10000; i++) {
    sb.append(i);  // Modifies internal char array in place
}
String result = sb.toString();
```

| Feature | String | StringBuilder | StringBuffer |
|---|---|---|---|
| Mutability | ❌ Immutable | ✅ Mutable | ✅ Mutable |
| Thread-safe | ✅ (immutable) | ❌ (not synchronized) | ✅ (synchronized methods) |
| Performance | Slow for repeated operations | Fastest | Slower (due to synchronization) |
| Use when | Final/constant strings | Single-threaded string building | Multi-threaded string building |

---

### 1.3 String Concatenation Traps

```java
String a = "Hello";
String b = "World";
String c = "HelloWorld";
String d = a + b;             // Computed at RUNTIME → new heap object
String e = "Hello" + "World"; // Computed at COMPILE TIME → pool reference

System.out.println(c == d);   // false — d is a runtime concatenation (heap)
System.out.println(c == e);   // true  — e is a compile-time constant (pool)
```

**Why?** The Java compiler folds constant expressions (`"Hello" + "World"`) into `"HelloWorld"` at compile time. But when variables are involved (`a + b`), it uses `StringBuilder` at runtime, producing a new heap object.

```java
final String x = "Hello";
final String y = "World";
String z = x + y;  // x and y are compile-time constants (final)

System.out.println(c == z);  // true — compiler folds final variables!
```

---

### 1.3 Integer Caching (`IntegerCache`)

Java caches `Integer` objects for values **-128 to 127**. `Integer.valueOf(int)` returns cached objects for this range.

```java
Integer a = 127;
Integer b = 127;
System.out.println(a == b);      // true  — cached (same object)

Integer c = 128;
Integer d = 128;
System.out.println(c == d);      // false — NOT cached (different objects)

Integer e = Integer.valueOf(127);
Integer f = Integer.valueOf(127);
System.out.println(e == f);      // true  — same cache

System.out.println(a.equals(b)); // true  — always use equals() for wrapper types
System.out.println(c.equals(d)); // true
```

**Under the hood:**
```java
// Integer.valueOf() implementation (simplified)
public static Integer valueOf(int i) {
    if (i >= -128 && i <= 127) {
        return IntegerCache.cache[i + 128];  // Returns cached instance
    }
    return new Integer(i);  // Creates new object
}
```

---

### 1.4 Autoboxing and Unboxing Traps

```java
Integer a = 1;
Integer b = 2;
Integer c = 3;
Integer d = 3;
Integer e = 321;
Integer f = 321;
Long    g = 3L;

System.out.println(c == d);          // true  — cached
System.out.println(e == f);          // false — not cached
System.out.println(c == (a + b));    // true  — a+b triggers unboxing, result compared by value
System.out.println(c.equals(a + b)); // true
System.out.println(g == (a + b));    // true  — a+b = 3, widened to long, then compared
System.out.println(g.equals(a + b)); // false — Long.equals(Integer) → different types!
```

**Key takeaway:** `equals()` on wrapper types checks both **value and type**. `Long(3).equals(Integer(3))` is `false`.

---

### 1.5 Method Overloading Resolution

Java resolves overloaded methods at **compile time** using the **most specific** matching rule.

```java
class Overload {
    void print(int a)     { System.out.println("int: " + a); }
    void print(long a)    { System.out.println("long: " + a); }
    void print(Integer a) { System.out.println("Integer: " + a); }
    void print(Object a)  { System.out.println("Object: " + a); }
}

Overload o = new Overload();
o.print(5);          // int: 5         — exact match
o.print(5L);         // long: 5        — exact match
o.print((short) 5);  // int: 5         — widening (short → int)
```

**Resolution priority:**
1. Exact match
2. Widening primitive (`short → int → long → float → double`)
3. Autoboxing (`int → Integer`)
4. Varargs (`int...`)

```java
class Test {
    void m(int a, long b)  { System.out.println("int, long"); }
    void m(long a, int b)  { System.out.println("long, int"); }
}

Test t = new Test();
// t.m(5, 5);  // ❌ COMPILATION ERROR — ambiguous! Both methods match via widening.
```

---

### 1.6 Static vs Instance Binding

```java
class Parent {
    static void greet() {
        System.out.println("Parent static greet");
    }

    void hello() {
        System.out.println("Parent hello");
    }
}

class Child extends Parent {
    static void greet() {
        System.out.println("Child static greet");
    }

    @Override
    void hello() {
        System.out.println("Child hello");
    }
}

Parent p = new Child();
p.greet();   // "Parent static greet"  — static methods are NOT overridden! (static binding)
p.hello();   // "Child hello"          — instance methods ARE overridden (dynamic binding)
```

**Key:** Static methods are **hidden**, not overridden. The reference type decides which static method runs. For instance methods, the **actual object type** decides.

---

### 1.7 Exception Handling Order

```java
public class ExceptionOrder {
    public static int getValue() {
        try {
            System.out.println("try");
            return 1;
        } catch (Exception e) {
            System.out.println("catch");
            return 2;
        } finally {
            System.out.println("finally");
            // return 3;  ← If uncommented, this OVERRIDES the try/catch return!
        }
    }

    public static void main(String[] args) {
        System.out.println("Value: " + getValue());
    }
}

// Output:
// try
// finally
// Value: 1
```

**Critical Rule:** The `finally` block **always** executes (except `System.exit()`). If `finally` has a `return`, it **overrides** the return value from `try` or `catch`.

```java
// ⚠️ Dangerous — finally overrides try's return
static int dangerous() {
    try {
        return 1;
    } finally {
        return 2;  // This WINS
    }
}
System.out.println(dangerous()); // 2
```

---

### 1.8 Constructor and Initialization Order

```java
class Base {
    static { System.out.println("1. Base static block"); }
    { System.out.println("4. Base instance block"); }

    Base() {
        System.out.println("5. Base constructor");
    }
}

class Derived extends Base {
    static { System.out.println("2. Derived static block"); }
    { System.out.println("6. Derived instance block"); }

    Derived() {
        System.out.println("7. Derived constructor");
    }
}

public class Main {
    public static void main(String[] args) {
        System.out.println("3. Main starts");
        new Derived();
    }
}

// Output:
// 1. Base static block         ← static blocks run ONCE when class is loaded
// 2. Derived static block      ← child static block after parent
// 3. Main starts
// 4. Base instance block       ← instance blocks run BEFORE constructor
// 5. Base constructor          ← parent constructor first
// 6. Derived instance block
// 7. Derived constructor
```

**Order:**
1. Parent static blocks/fields (once, when class is loaded)
2. Child static blocks/fields (once)
3. Parent instance blocks → Parent constructor
4. Child instance blocks → Child constructor

---

### 1.9 Covariant Return Types

```java
class Animal {
    Animal create() {
        System.out.println("Creating Animal");
        return new Animal();
    }
}

class Dog extends Animal {
    @Override
    Dog create() {  // Covariant return — Dog is a subtype of Animal ✅
        System.out.println("Creating Dog");
        return new Dog();
    }
}

Animal a = new Dog();
Animal result = a.create();  // "Creating Dog" — runtime polymorphism
```

---

### 1.10 Pass-by-Value (Always!)

Java is **always pass-by-value**. For objects, the **reference (address) is passed by value** — you can modify the object's state, but you cannot change what the reference points to.

```java
class Person {
    String name;
    Person(String name) { this.name = name; }
}

static void changeName(Person p) {
    p.name = "Bob";  // ✅ Modifies the actual object
}

static void reassign(Person p) {
    p = new Person("Charlie");  // ❌ Only changes the local copy of the reference
}

Person person = new Person("Alice");

changeName(person);
System.out.println(person.name);  // "Bob" — object was modified

reassign(person);
System.out.println(person.name);  // "Bob" — reassignment had no effect outside
```

```
Before changeName():
  person ──→ [name: "Alice"]

After changeName():
  person ──→ [name: "Bob"]     ← same object, field changed

Inside reassign():
  p (local copy) ──→ [name: "Charlie"]  ← local reference changed
  person ──→ [name: "Bob"]              ← original reference unchanged
```

---

### 1.11 try-with-resources and AutoCloseable

```java
class MyResource implements AutoCloseable {
    String name;

    MyResource(String name) {
        this.name = name;
        System.out.println(name + " opened");
    }

    @Override
    public void close() {
        System.out.println(name + " closed");
    }
}

// Resources are closed in REVERSE order of declaration
try (MyResource r1 = new MyResource("R1");
     MyResource r2 = new MyResource("R2")) {
    System.out.println("Using resources");
}

// Output:
// R1 opened
// R2 opened
// Using resources
// R2 closed     ← LIFO order (last opened, first closed)
// R1 closed
```

---

### 1.12 Variable Shadowing

```java
class Outer {
    int x = 10;

    class Inner {
        int x = 20;

        void print() {
            int x = 30;
            System.out.println(x);           // 30 — local variable
            System.out.println(this.x);      // 20 — Inner's field
            System.out.println(Outer.this.x); // 10 — Outer's field
        }
    }
}

new Outer().new Inner().print();
// Output: 30, 20, 10
```

---

### 1.13 Array Covariance (Dangerous!)

```java
Object[] arr = new String[3];  // ✅ Compiles — arrays are covariant
arr[0] = "Hello";              // ✅ Works
arr[1] = 123;                  // ❌ ArrayStoreException at RUNTIME!
```

**Why?** Java arrays are **covariant** (a `String[]` can be assigned to an `Object[]`), but this breaks type safety at runtime. Generics fix this:

```java
// List<Object> list = new ArrayList<String>();  // ❌ COMPILE ERROR — generics are invariant!
```

---

### 1.14 Ternary Operator Type Promotion

```java
Object result = true ? new Integer(1) : new Double(2.0);
System.out.println(result);           // 1.0  (not 1!)
System.out.println(result.getClass()); // class java.lang.Double
```

**Why?** The ternary operator promotes both branches to a common type. `int` and `double` → `double`. So `1` becomes `1.0`, then auto-boxed to `Double`.

---

### 1.15 `==` vs `equals()` Summary

| Expression | Result | Why |
|---|---|---|
| `new String("a") == new String("a")` | `false` | Different heap objects |
| `"a" == "a"` | `true` | Same string pool reference |
| `new String("a").equals(new String("a"))` | `true` | Same content |
| `new Integer(5) == new Integer(5)` | `false` | Different objects (bypasses cache) |
| `Integer.valueOf(5) == Integer.valueOf(5)` | `true` | Cached (-128 to 127) |
| `Integer.valueOf(200) == Integer.valueOf(200)` | `false` | Not cached |
| `null == null` | `true` | Both are null |
| `null.equals(null)` | `NullPointerException` | Can't call method on null |

---

---

## Part 2: HashMap Internal Working

---

### 2.1 What is HashMap?

`HashMap<K, V>` is a **hash table-based** implementation of the `Map` interface. It stores **key-value pairs** and provides **O(1) average-case** time for `put()`, `get()`, and `remove()`.

**Key properties:**
- **Not synchronized** (not thread-safe). Use `ConcurrentHashMap` for thread safety.
- **Allows one `null` key** and multiple `null` values.
- **Does not guarantee order** of entries. Use `LinkedHashMap` for insertion order.
- **Keys must correctly implement `hashCode()` and `equals()`.**

---

### 2.2 Internal Data Structure

Since **Java 8**, HashMap uses an array of **Nodes** (linked list) that can transform into **TreeNodes** (red-black tree) when a bucket gets too long.

```
HashMap internal structure (Java 8+):
                                                          
  ┌──────────────────────────────────────────────────────┐
  │  table[] — Node array (initial capacity: 16)         │
  ├────────┬────────┬────────┬────────┬────────┬─────────┤
  │ [0]    │ [1]    │ [2]    │ [3]    │ [4]    │ ...     │
  │  │     │ null   │  │     │ null   │  │     │         │
  └──┼─────┴────────┴──┼─────┴────────┴──┼─────┴─────────┘
     ▼                  ▼                  ▼
  ┌──────┐          ┌──────┐          ┌──────┐
  │Node  │          │Node  │          │Node  │
  │K1,V1 │          │K3,V3 │          │K5,V5 │
  │next──│──►null   │next──│──►┌──────┐│next──│──►null
  └──────┘          └──────┘   │Node  │└──────┘
                               │K4,V4 │
                               │next──│──►┌──────┐
                               └──────┘   │Node  │  ← If chain length > 8
                                          │K6,V6 │     and table size ≥ 64,
                                          │next──│──►  this converts to a
                                          └──────┘     Red-Black Tree
```

**Node class (simplified):**

```java
static class Node<K, V> implements Map.Entry<K, V> {
    final int hash;    // Hash of the key
    final K key;
    V value;
    Node<K, V> next;   // For chaining (linked list)
}
```

---

### 2.3 Critical Constants

```java
static final int DEFAULT_INITIAL_CAPACITY = 16;        // Default table size
static final int MAXIMUM_CAPACITY = 1 << 30;           // Max table size (1 billion)
static final float DEFAULT_LOAD_FACTOR = 0.75f;        // When to resize
static final int TREEIFY_THRESHOLD = 8;                 // List → Tree when chain ≥ 8
static final int UNTREEIFY_THRESHOLD = 6;               // Tree → List when chain ≤ 6
static final int MIN_TREEIFY_CAPACITY = 64;             // Min table size for treeification
```

---

### 2.4 How `put(key, value)` Works — Step by Step

```java
HashMap<String, Integer> map = new HashMap<>();
map.put("Alice", 100);
```

**Step 1: Compute Hash**

```java
// HashMap's internal hash function
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
// XOR with upper 16 bits spreads the hash for better distribution
```

**Why XOR with upper bits?**
- `hashCode()` returns a 32-bit int, but the table index only uses the **lower N bits** (where N = log₂(capacity)).
- XOR mixes the higher bits into the lower bits, reducing collisions when `hashCode()` produces values that differ only in upper bits.

```
Example: hashCode() = 0x12345678
  h           = 0001 0010 0011 0100  0101 0110 0111 1000
  h >>> 16    = 0000 0000 0000 0000  0001 0010 0011 0100
  h ^ h>>>16  = 0001 0010 0011 0100  0100 0100 0100 1100
                                     ↑↑↑↑ ↑↑↑↑ ↑↑↑↑ ↑↑↑↑ — lower bits now include info from upper bits
```

**Step 2: Compute Bucket Index**

```java
int index = (n - 1) & hash;  // n = table length (always power of 2)
// Equivalent to: hash % n, but faster (bitwise AND)
```

**Why power of 2?**
- `(n - 1) & hash` works only when `n` is a power of 2.
- Example: `n = 16`, `n - 1 = 15 = 0b00001111`. AND with hash keeps only last 4 bits → index 0–15.

**Step 3: Insert into Bucket**

```
If bucket is empty:
    → Create a new Node and place it there.

If bucket is not empty (collision):
    → Walk the linked list:
        → If a node with the SAME key exists (equals() check):
            → Replace the value (update).
        → If no match found:
            → Append new node at the end of the chain (Java 8 uses tail insertion).
            → If chain length ≥ TREEIFY_THRESHOLD (8) AND table size ≥ 64:
                → Convert the chain to a Red-Black Tree.
```

**Step 4: Check if Resize is Needed**

```java
if (++size > threshold)  // threshold = capacity * loadFactor
    resize();            // Double the table size
```

---

### 2.5 How `get(key)` Works

```java
Integer value = map.get("Alice");
```

1. Compute `hash("Alice")`.
2. Compute `index = (n - 1) & hash`.
3. Go to `table[index]`.
4. If the first node matches (same hash **and** `equals()` returns `true`) → return value.
5. If not, walk the chain (linked list or tree) until found or end of chain.
6. If not found → return `null`.

```java
// Simplified get() implementation
public V get(Object key) {
    int hash = hash(key);
    int index = (table.length - 1) & hash;
    Node<K,V> node = table[index];

    while (node != null) {
        if (node.hash == hash && (node.key == key || key.equals(node.key))) {
            return node.value;   // Found!
        }
        node = node.next;       // Walk the chain
    }
    return null;                // Not found
}
```

> **Important:** HashMap first compares `hash` (fast int comparison), then calls `equals()` only if hashes match. This is why both `hashCode()` and `equals()` must be consistently implemented.

---

### 2.6 Resizing (Rehashing)

When the number of entries exceeds `capacity * loadFactor`, the table size is **doubled** and all entries are rehashed.

```
Before resize: capacity = 16, loadFactor = 0.75, threshold = 12
After 13th entry → resize!
New capacity = 32, new threshold = 24

Rehash: each entry's new index = (32 - 1) & hash
```

**Java 8 optimization:** During resize, each entry either stays in the **same bucket** or moves to `old_index + old_capacity`. This is because:

```
Old capacity = 16: index = hash & 0b01111  (only lowest 4 bits)
New capacity = 32: index = hash & 0b11111  (lowest 5 bits)

The only difference is the 5th bit.
If bit 5 is 0 → same bucket.
If bit 5 is 1 → bucket moves to old_index + 16.
```

This avoids recalculating `hashCode()` for every entry.

---

### 2.7 Treeification (Java 8+)

When a bucket's linked list exceeds **8 nodes** and the table capacity is **≥ 64**, the list is converted to a **Red-Black Tree**. This changes worst-case lookup from **O(n)** to **O(log n)**.

```
Linked List (O(n) worst case):
  [K1] → [K2] → [K3] → [K4] → [K5] → [K6] → [K7] → [K8] → [K9]
                                                                 ↓
                                                        TREEIFY (≥ 8 nodes)
                                                                 ↓
Red-Black Tree (O(log n) worst case):
                    [K5]
                   /    \
                [K3]    [K7]
               /    \   /    \
            [K1]  [K4] [K6]  [K9]
           /                  /
        [K2]              [K8]
```

When the tree shrinks below **6 nodes** (after removals), it is converted back to a linked list (`UNTREEIFY_THRESHOLD = 6`).

---

### 2.8 Why Capacity is Always Power of 2

1. **Fast index calculation**: `(n - 1) & hash` instead of `hash % n` (modulo is slower).
2. **Efficient resizing**: Entries either stay or move by exactly `old_capacity` positions.
3. **Better bit distribution**: Power-of-2 masking works cleanly with the hash perturbation.

If you specify a non-power-of-2 capacity:
```java
HashMap<String, Integer> map = new HashMap<>(10);
// Internally rounds up to 16 (next power of 2)
```

```java
// tableSizeFor — rounds up to nearest power of 2
static final int tableSizeFor(int cap) {
    int n = cap - 1;
    n |= n >>> 1;
    n |= n >>> 2;
    n |= n >>> 4;
    n |= n >>> 8;
    n |= n >>> 16;
    return (n < 0) ? 1 : (n >= MAXIMUM_CAPACITY) ? MAXIMUM_CAPACITY : n + 1;
}
```

---

### 2.9 Handling `null` Keys

HashMap allows **exactly one `null` key**, which always maps to **bucket index 0**.

```java
HashMap<String, Integer> map = new HashMap<>();
map.put(null, 42);
System.out.println(map.get(null));  // 42

// Internally:
// hash(null) returns 0
// index = (n-1) & 0 = 0 → always bucket 0
```

---

### 2.10 HashMap vs HashTable vs ConcurrentHashMap

| Feature | HashMap | Hashtable | ConcurrentHashMap |
|---|---|---|---|
| Thread-safe | ❌ | ✅ (synchronized) | ✅ (segment/bucket locking) |
| Null keys | ✅ (one) | ❌ | ❌ |
| Null values | ✅ | ❌ | ❌ |
| Performance | Best (single-thread) | Worst (global lock) | Good (fine-grained locks) |
| Iterator | Fail-fast | Fail-fast | Weakly consistent |
| Introduced | Java 1.2 | Java 1.0 | Java 1.5 |

---

### 2.11 HashMap vs LinkedHashMap vs TreeMap

| Feature | HashMap | LinkedHashMap | TreeMap |
|---|---|---|---|
| Order | No order | Insertion order | Sorted (natural/comparator) |
| Implementation | Hash table | Hash table + doubly linked list | Red-Black Tree |
| `get()` / `put()` | O(1) | O(1) | O(log n) |
| `null` key | ✅ | ✅ | ❌ (if using natural ordering) |
| Use case | General purpose | LRU cache, ordered iteration | Sorted data, range queries |

---

### 2.12 Common Interview Code Snippets

**What happens when two keys have the same hashCode?**

```java
class BadKey {
    String value;

    BadKey(String value) { this.value = value; }

    @Override
    public int hashCode() {
        return 1;  // All keys go to the SAME bucket!
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof BadKey)) return false;
        return value.equals(((BadKey) o).value);
    }
}

HashMap<BadKey, String> map = new HashMap<>();
map.put(new BadKey("A"), "Value-A");
map.put(new BadKey("B"), "Value-B");
map.put(new BadKey("C"), "Value-C");

// All 3 entries are in the SAME bucket (bucket 1)
// Chain: [A→Value-A] → [B→Value-B] → [C→Value-C]
// get() is O(n) instead of O(1) — because all entries are in one chain

System.out.println(map.get(new BadKey("B"))); // "Value-B" — found by walking chain + equals()
```

**Mutable key problem:**

```java
class MutableKey {
    int id;

    MutableKey(int id) { this.id = id; }

    @Override
    public int hashCode() { return id; }

    @Override
    public boolean equals(Object o) {
        return o instanceof MutableKey && ((MutableKey) o).id == this.id;
    }
}

HashMap<MutableKey, String> map = new HashMap<>();
MutableKey key = new MutableKey(1);
map.put(key, "Hello");

System.out.println(map.get(key));  // "Hello" ✅

key.id = 2;  // MUTATE the key 💀

System.out.println(map.get(key));  // null ❌ — hash changed, lookup goes to wrong bucket!
System.out.println(map.size());    // 1 — entry still exists, but unreachable!

// The entry is LOST — it's in bucket for hashCode=1, but we're searching bucket for hashCode=2
// This is why HashMap keys should be IMMUTABLE (String, Integer, etc.)
```

---

### 2.13 ConcurrentHashMap Internal Working (Brief)

```
Java 7: Segment-based locking
  ┌────────┬────────┬────────┬────────┐
  │ Seg 0  │ Seg 1  │ Seg 2  │ Seg 3  │  ← Each segment has its own lock
  │ [0][1] │ [2][3] │ [4][5] │ [6][7] │
  └────────┴────────┴────────┴────────┘

Java 8+: Per-bucket locking (CAS + synchronized on node)
  ┌────┬────┬────┬────┬────┬────┬────┬────┐
  │ [0]│ [1]│ [2]│ [3]│ [4]│ [5]│ [6]│ [7]│  ← Lock only the specific bucket
  └────┴────┴────┴────┴────┴────┴────┴────┘
```

**Java 8+ ConcurrentHashMap:**
- Uses **CAS (Compare-And-Swap)** for inserting into empty buckets (lock-free).
- Uses **synchronized on the first node** of the bucket for insertions into non-empty buckets.
- **No global lock** — multiple threads can read and write to different buckets simultaneously.
- Also uses treeification (like HashMap) for long chains.

---

### 2.14 Complete Flow Diagram: `map.put("Alice", 100)`

```
                          map.put("Alice", 100)
                                  │
                                  ▼
                   ┌──────────────────────────┐
                   │ Step 1: hash("Alice")     │
                   │ h = "Alice".hashCode()    │
                   │   = 63476538              │
                   │ hash = h ^ (h >>> 16)     │
                   │   = 63476538 ^ 968        │
                   │   = 63477370              │
                   └──────────┬───────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │ Step 2: Find bucket       │
                   │ index = (16-1) & hash     │
                   │ index = 15 & 63477370     │
                   │ index = 10                │
                   └──────────┬───────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │ Step 3: Check table[10]   │
                   ├──────────────────────────┤
                   │ If null:                  │
                   │   → Create new Node       │
                   │   → table[10] = Node      │
                   ├──────────────────────────┤
                   │ If not null:              │
                   │   → Walk chain            │
                   │   → If key.equals()?      │
                   │     → Replace value       │
                   │   → Else append to end    │
                   └──────────┬───────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │ Step 4: Check chain       │
                   │ If chain ≥ 8 nodes AND    │
                   │ table.length ≥ 64:        │
                   │   → Treeify (Red-Black)   │
                   └──────────┬───────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │ Step 5: Check size        │
                   │ if (++size > threshold)   │
                   │   → resize() (double)     │
                   │   → rehash all entries    │
                   └──────────────────────────┘
```

---

### 2.15 Performance Summary

| Operation | Average | Worst (degenerate) | Worst (treeified) |
|---|---|---|---|
| `put()` | O(1) | O(n) | O(log n) |
| `get()` | O(1) | O(n) | O(log n) |
| `remove()` | O(1) | O(n) | O(log n) |
| `containsKey()` | O(1) | O(n) | O(log n) |
| `containsValue()` | O(n) | O(n) | O(n) |
| `resize()` | O(n) | O(n) | O(n) |

**Best practices:**
1. Always override both `hashCode()` and `equals()` for custom keys.
2. Use **immutable keys** (String, Integer).
3. Set initial capacity to avoid unnecessary resizing: `new HashMap<>(expectedSize * 4 / 3 + 1)`.
4. Use `ConcurrentHashMap` for multi-threaded use — never synchronize manually on `HashMap`.

---
