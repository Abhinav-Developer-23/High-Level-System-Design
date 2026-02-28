# LLD Theory — Question Bank

## Beginner Level

### OOP Fundamentals

1. What is Object-Oriented Programming and how does it differ from procedural programming?

<details><summary>Answer</summary>Object-Oriented Programming (OOP) organizes software around **objects** — instances of classes that bundle data (fields) and behavior (methods). Unlike procedural programming which follows a top-down, step-by-step approach with shared global data, OOP encapsulates data inside objects, uses access modifiers for security, and promotes reusability through inheritance. In procedural: `calculateSalary(employee)`. In OOP: `employee.calculateSalary()`.</details>

2. What is the difference between a class and an object?

<details><summary>Answer</summary>A **class** is a blueprint/template that defines structure and behavior — no memory is allocated until instantiated. An **object** is an instance of a class with actual data occupying memory. A class is declared once (`class Car {}`), but multiple objects can be created (`Car c1 = new Car(); Car c2 = new Car();`). When `new` is called: memory is allocated on the heap, fields get default values, the constructor runs, and a reference is returned.</details>

3. What are the four access modifiers in Java and their visibility scopes?

<details><summary>Answer</summary>**`private`**: accessible only within the same class. **Default (package-private)**: accessible within the same package. **`protected`**: accessible within the same package AND subclasses in different packages. **`public`**: accessible everywhere. Interface methods are implicitly `public abstract`, interface fields are `public static final`, and enum constructors are implicitly `private`.</details>

4. What is a constructor in Java and what are its rules?

<details><summary>Answer</summary>A constructor is a special method called automatically when an object is created via `new`. Rules: (1) same name as the class, (2) no return type (not even `void`), (3) cannot be `abstract`, `static`, `final`, or `synchronized`. If you don't define any constructor, Java provides a default no-arg constructor. But if you define **any** constructor, Java does NOT provide the default one — you must explicitly define a no-arg constructor if needed.</details>

5. What is the difference between shallow copy and deep copy?

<details><summary>Answer</summary>**Shallow copy** copies the reference — both original and copy point to the **same** nested object. Modifying the nested object through one affects the other. **Deep copy** creates a completely new copy of all nested objects. They are fully independent. For example, if a `Car` has an `Engine` reference: shallow copy shares the same `Engine` object, while deep copy creates a new `Engine` object with the same values.</details>

6. What happens when there are no more references to an object in Java?

<details><summary>Answer</summary>The object becomes eligible for **Garbage Collection (GC)**. Java has no destructors — the GC automatically reclaims memory. An object becomes eligible when: (1) its reference is set to `null`, (2) its reference is reassigned to another object, (3) it was created inside a method that has returned, or (4) it was an anonymous object. The `finalize()` method (deprecated since Java 9) was unreliable — modern Java uses `try-with-resources` + `AutoCloseable` for deterministic cleanup.</details>

7. What is encapsulation and how do you achieve it in Java?

<details><summary>Answer</summary>Encapsulation bundles data and methods together while restricting direct access to data. Achieve it by: (1) declaring fields as `private`, (2) providing `public` getters/setters, (3) adding validation in setters to enforce invariants. For example, a `BankAccount` with `private double balance` and no setter — balance changes only through validated `deposit()` and `withdraw()` methods. Benefits: data protection, flexibility to change internals, reusability, and testability.</details>

8. What is abstraction and how does it differ from encapsulation?

<details><summary>Answer</summary>Abstraction shows only essential features while hiding implementation details. **Encapsulation** is the *mechanism* (HOW to hide — `private` + getters/setters), while **abstraction** is the *concept* (WHAT to hide — implementation complexity). Encapsulation hides **data** at implementation level; abstraction hides **complexity** at design level using abstract classes and interfaces. Example: an ATM — you press "Withdraw" without knowing the internal verification and cash dispensing process.</details>

9. What is the difference between an abstract class and an interface in Java?

<details><summary>Answer</summary>**Abstract class**: can have constructors, instance fields, any access modifiers, represents IS-A (strong) relationship, allows 0–100% abstraction. **Interface**: no constructors, only `public static final` fields, supports multiple inheritance, has `default` methods (Java 8+) and `private` methods (Java 9+), represents CAN-DO relationship. Rule of thumb: share **code** among related classes → abstract class. Define a **contract** for unrelated classes → interface.</details>

10. What are the types of inheritance supported in Java?

<details><summary>Answer</summary>Java supports: (1) **Single** — A → B, (2) **Multilevel** — A → B → C, (3) **Hierarchical** — A → B, A → C. Java does **NOT** support **Multiple** inheritance via classes (A,B → C) due to the Diamond Problem — if both parents override the same method, it's ambiguous which one the child inherits. Java's solution: use **interfaces** for multiple inheritance, where conflicts must be resolved explicitly using `InterfaceName.super.method()`.</details>

11. What is the difference between method overloading and method overriding?

<details><summary>Answer</summary>**Overloading** (compile-time polymorphism): same method name, different parameter signatures, resolved at compile time, no inheritance required. **Overriding** (runtime polymorphism): subclass provides its own implementation with the identical method signature, resolved at runtime based on actual object type, requires inheritance. Key differences: overriding cannot have a more restrictive access modifier, return type must be same or covariant, and `static`/`private`/`final` methods cannot be overridden.</details>

12. What does the `static` keyword mean in Java?

<details><summary>Answer</summary>`static` means belonging to the **class**, not any instance. Static variables are shared across all instances. Static methods can be called without creating an object and cannot access instance members. Static blocks run once when the class is loaded. A static method cannot use `this` because there's no instance context. Common use: utility methods (`Math.max()`), constants (`static final`), factory methods, and counters shared across instances.</details>

13. What does the `final` keyword mean for variables, methods, and classes?

<details><summary>Answer</summary>**Final variable**: constant — cannot be reassigned after initialization (but for objects, the object's state CAN still be modified). **Final method**: cannot be overridden by subclasses. **Final class**: cannot be extended (e.g., `String`, `Integer`). A "blank final" variable is declared `final` but assigned in the constructor. Note: `final List<String> list` means the reference can't change, but you can still `list.add("item")`.</details>

14. What is the `Object` class in Java and why is it important?

<details><summary>Answer</summary>Every class in Java implicitly extends `java.lang.Object`. It provides default implementations of key methods: `equals()` (reference equality by default), `hashCode()` (based on memory address by default), `toString()`, `clone()`, `finalize()`, `getClass()`, `wait()`, `notify()`, `notifyAll()`. Classes must override `equals()` and `hashCode()` for correct behavior in collections like `HashMap` and `HashSet`.</details>

### Java Internals

15. How does the String Pool work in Java?

<details><summary>Answer</summary>Java maintains a **String Pool** in heap memory where string literals are stored. When you use a literal like `"Hello"`, Java checks if it already exists in the pool and reuses it. `String s1 = "Hello"; String s2 = "Hello";` → `s1 == s2` is `true` (same pool reference). `new String("Hello")` always creates a new heap object, so `==` with a pool string is `false`. The `intern()` method returns the pool reference. `new String("Hello")` creates 1 or 2 objects: one in the pool (if not already there) and one on the heap.</details>

16. Why are Strings immutable in Java?

<details><summary>Answer</summary>(1) **String Pool safety** — multiple references can share the same pool object safely. (2) **Security** — Strings used for class loading, file paths, DB URLs can't be tampered with after security checks. (3) **HashCode caching** — computed once and cached, making Strings efficient as HashMap keys. (4) **Thread safety** — immutable objects are inherently thread-safe. (5) **Class loading** — JVM uses Strings for `Class.forName()`. Any "modification" like `concat()` creates a new String object entirely.</details>

17. What is Integer caching in Java?

<details><summary>Answer</summary>Java caches `Integer` objects for values **-128 to 127**. `Integer.valueOf(int)` returns cached objects for this range. So `Integer a = 127; Integer b = 127; a == b` is `true` (same cached object). But `Integer c = 128; Integer d = 128; c == d` is `false` (different objects, not cached). Always use `.equals()` for wrapper type comparisons. This also applies to `Byte`, `Short`, `Long`, and `Character` (0-127).</details>

18. What is the difference between `==` and `equals()` in Java?

<details><summary>Answer</summary>`==` compares **references** (memory addresses) for objects and **values** for primitives. `equals()` compares **content/value** (when properly overridden). Key examples: `new String("a") == new String("a")` → `false` (different objects). `"a" == "a"` → `true` (same pool ref). `new String("a").equals(new String("a"))` → `true` (same content). For wrapper types, `equals()` also checks **type**: `Long(3).equals(Integer(3))` is `false` because types differ.</details>

### SOLID Principles

19. What is the Single Responsibility Principle?

<details><summary>Answer</summary>"A class should have one, and only one, reason to change." A class should encapsulate one responsibility. Violation: an `Employee` class that handles business logic (`calculatePay()`), persistence (`saveToDatabase()`), AND reporting (`generateReport()`). Fix: split into `Employee` (business logic), `EmployeeRepository` (persistence), and `EmployeeReportGenerator` (reporting). Now each class changes for exactly one reason.</details>

20. What is the Open/Closed Principle?

<details><summary>Answer</summary>"Software entities should be open for extension, but closed for modification." Add new behavior without modifying existing code, achieved through abstraction and polymorphism. Violation: a `DiscountCalculator` with an `if-else` chain for customer types — every new type requires modification. Fix: define a `DiscountStrategy` interface, implement it per type (`RegularDiscount`, `PremiumDiscount`). Adding `StudentDiscount` requires only a new class, no changes to existing code.</details>

21. What is the Liskov Substitution Principle?

<details><summary>Answer</summary>"Subtypes must be substitutable for their base types without breaking the application." The classic violation is the Rectangle-Square problem: `Square extends Rectangle` breaks because `setWidth()` on a Square also changes height, violating Rectangle's contract. Fix: don't force Square to extend Rectangle — use a `Shape` interface that both implement independently. LSP rules: preconditions can't be strengthened, postconditions can't be weakened, parent invariants must be preserved.</details>

22. What is the Interface Segregation Principle?

<details><summary>Answer</summary>"No client should be forced to depend on methods it does not use." Instead of one fat interface, create smaller focused ones. Violation: a `Worker` interface with `work()`, `eat()`, `writeCode()`, `manageTeam()` — a `Developer` must implement `manageTeam()` (throwing `UnsupportedOperationException`). Fix: split into `Workable`, `Codeable`, `Manageable` etc. `Developer` implements only what it needs; `Robot` implements only `Workable` and `Codeable`.</details>

23. What is the Dependency Inversion Principle?

<details><summary>Answer</summary>"High-level modules should not depend on low-level modules. Both should depend on abstractions." Violation: `UserService` directly creates `new MySQLDatabase()` — switching to PostgreSQL requires modifying `UserService`. Fix: define a `Database` interface, have `MySQLDatabase` and `PostgreSQLDatabase` implement it, and inject the dependency via constructor. DIP is achieved through **Dependency Injection** — constructor injection (preferred), setter injection, or method injection.</details>

## Intermediate Level

24. Explain constructor chaining with `this()` and `super()`.

<details><summary>Answer</summary>`this()` calls another constructor in the **same class** — enables constructor overloading where simpler constructors delegate to the main one. `super()` calls the **parent class** constructor — must be the first statement. Rules: `this()` and `super()` cannot both be used in the same constructor. If neither is explicitly called, Java inserts `super()` (no-arg) implicitly. If the parent has no no-arg constructor, you must explicitly call `super(args)` or it's a compilation error.</details>

25. How does Java resolve overloaded methods at compile time?

<details><summary>Answer</summary>Java uses the "most specific" matching rule with this priority: (1) **Exact match**, (2) **Widening** (`short → int → long → float → double`), (3) **Autoboxing** (`int → Integer`), (4) **Varargs** (`int...`). If two methods are equally specific, it's a compilation error (ambiguous). Example: `void m(int, long)` and `void m(long, int)` — calling `m(5, 5)` is ambiguous because both match via widening.</details>

26. What is the difference between static binding and dynamic binding?

<details><summary>Answer</summary>**Static binding** (early): resolved at compile time, based on **reference type**. Applies to `static`, `final`, `private` methods and constructors. Faster (no runtime lookup). **Dynamic binding** (late): resolved at runtime, based on **actual object type**. Applies to overridden instance methods. Uses vtable lookup. Example: `Animal a = new Dog(); a.staticMethod()` calls Animal's version (static binding), while `a.instanceMethod()` calls Dog's version (dynamic binding).</details>

27. Explain the `equals()` and `hashCode()` contract.

<details><summary>Answer</summary>The contract: (1) if `a.equals(b)` is true, then `a.hashCode() == b.hashCode()` **must** be true. (2) The converse is NOT required (hash collisions exist). (3) `equals()` must be reflexive, symmetric, transitive, and return false for null. Without proper overrides, HashMap/HashSet break — equal objects get different hashCodes, land in different buckets, and lookups fail. Common mistakes: overriding `equals()` but not `hashCode()`, using mutable fields, or using wrong parameter type (`equals(Employee)` instead of `equals(Object)`).</details>

28. What is the initialization and execution order in Java class loading?

<details><summary>Answer</summary>Order: (1) **Parent static blocks/fields** (once, when class is loaded), (2) **Child static blocks/fields** (once), (3) **Parent instance blocks** → Parent constructor, (4) **Child instance blocks** → Child constructor. So for `new Derived()`: Base static block → Derived static block → Base instance block → Base constructor → Derived instance block → Derived constructor. Static blocks run only once per class loading.</details>

29. How does HashMap work internally in Java 8+?

<details><summary>Answer</summary>HashMap uses an array of `Node` objects (linked lists) that can transform into Red-Black Trees. **put()**: (1) compute `hash = key.hashCode() ^ (hashCode >>> 16)` — XOR spreads upper bits into lower bits, (2) compute `index = (capacity - 1) & hash`, (3) if bucket empty → new Node; if collision → walk chain, replace if key matches (`equals()`), else append. If chain ≥ 8 nodes AND table ≥ 64 → treeify. (4) If `size > capacity * loadFactor (0.75)` → resize (double). **get()**: compute hash → bucket → walk chain comparing hash first, then `equals()`.</details>

30. Why must HashMap capacity always be a power of 2?

<details><summary>Answer</summary>(1) **Fast index calculation**: `(n-1) & hash` is equivalent to `hash % n` but faster (bitwise AND vs modulo). This only works when n is a power of 2. (2) **Efficient resizing**: during resize, each entry either stays in the same bucket or moves to `old_index + old_capacity` — determined by a single bit check, avoiding `hashCode()` recalculation. (3) **Better bit distribution**: power-of-2 masking works cleanly with the hash perturbation. If you specify a non-power-of-2 capacity, HashMap rounds up internally using `tableSizeFor()`.</details>

31. What is the difference between HashMap, LinkedHashMap, and TreeMap?

<details><summary>Answer</summary>**HashMap**: no ordering, O(1) get/put, allows one null key, general purpose. **LinkedHashMap**: maintains **insertion order** via a doubly linked list, O(1) get/put, useful for LRU caches. **TreeMap**: maintains **sorted order** (natural or comparator), uses Red-Black Tree, O(log n) get/put, no null keys with natural ordering, useful for range queries and sorted data.</details>

32. What is the difference between HashMap, Hashtable, and ConcurrentHashMap?

<details><summary>Answer</summary>**HashMap**: not thread-safe, allows null keys/values, best single-thread performance. **Hashtable**: thread-safe via global `synchronized` lock (worst performance), no nulls, legacy (Java 1.0). **ConcurrentHashMap**: thread-safe via fine-grained per-bucket locking (Java 8+ uses CAS + synchronized on first node), no nulls, good concurrent performance, weakly consistent iterator. Always use ConcurrentHashMap over Hashtable for thread-safe maps.</details>

33. What happens when you use a mutable object as a HashMap key?

<details><summary>Answer</summary>If the key's fields used in `hashCode()` are mutated after insertion, the entry becomes **unreachable**. The entry still exists in the original bucket (based on old hash), but lookups use the new hash and search the wrong bucket. `map.get(key)` returns `null` even though `map.size()` shows the entry exists. This is why HashMap keys should be **immutable** — use `String`, `Integer`, or ensure key objects never change. This is also why String immutability is critical for its use as HashMap keys.</details>

34. What is the difference between `Serializable` and `Cloneable` marker interfaces?

<details><summary>Answer</summary>Both are marker interfaces (no methods). **`Serializable`**: tells JVM the object can be converted to a byte stream for saving to files, sending over network, or caching. Uses `serialVersionUID` for version control and `transient` to exclude fields. **`Cloneable`**: tells JVM that `clone()` can be called. Without it, `clone()` throws `CloneNotSupportedException`. `clone()` does a shallow copy by default — deep copy requires manually cloning nested objects. Modern Java prefers copy constructors over `clone()`.</details>

35. What are Java Records (Java 14+) and when should you use them?

<details><summary>Answer</summary>Records are immutable data carriers. `record Point(int x, int y) {}` auto-generates: `private final` fields, canonical constructor, accessor methods (`x()`, `y()`), `equals()`, `hashCode()`, and `toString()`. Records can have custom compact constructors (for validation), static fields/methods, instance methods, and can implement interfaces. They **cannot**: extend classes, declare additional instance fields, have setters, or be abstract. Use for DTOs, value objects, API responses. Use regular classes when you need mutability, inheritance, or complex logic.</details>

36. What is coupling vs cohesion and what should you aim for?

<details><summary>Answer</summary>**Coupling** = dependency between classes. **Tight coupling**: classes directly depend on each other's internals (bad). **Loose coupling**: classes interact through abstractions/interfaces (good). **Cohesion** = focus of a class. **Low cohesion**: class does many unrelated things (bad). **High cohesion**: class has a single, focused responsibility (good). Aim for **low coupling + high cohesion**. Example: `OrderService` hardcoded to `EmailService` = tight coupling. Using a `NotificationService` interface = loose coupling.</details>

37. Explain upcasting and downcasting in Java.

<details><summary>Answer</summary>**Upcasting** (widening): child → parent reference. Implicit and always safe. `Animal a = new Dog();` — `a.speak()` calls Dog's method via runtime polymorphism. **Downcasting** (narrowing): parent → child reference. Explicit and risky. `Dog d = (Dog) animal;` — works only if the actual object IS a Dog, otherwise throws `ClassCastException`. Always check with `instanceof` first. Java 16+ supports pattern matching: `if (animal instanceof Dog d) { d.breed; }`.</details>

## Advanced Level

38. Why does Java not support multiple inheritance through classes, and how do default methods in interfaces handle the diamond problem?

<details><summary>Answer</summary>Multiple class inheritance creates the Diamond Problem: if both parents override the same method, which does the child inherit? Java avoids this by disallowing multiple class inheritance. With interfaces, if two interfaces have the same `default` method, the implementing class **must** explicitly override and resolve the conflict using `InterfaceName.super.method()`. This makes the resolution explicit and unambiguous, unlike C++ where it can be implicit and error-prone.</details>

39. How does HashMap handle treeification and what triggers it?

<details><summary>Answer</summary>When a bucket's linked list exceeds **8 nodes** (`TREEIFY_THRESHOLD`) AND the table capacity is **≥ 64** (`MIN_TREEIFY_CAPACITY`), the list converts to a **Red-Black Tree**, changing worst-case lookup from O(n) to O(log n). If table capacity < 64, HashMap resizes instead of treeifying. When the tree shrinks below **6 nodes** (`UNTREEIFY_THRESHOLD`) after removals, it converts back to a linked list. The gap between 8 and 6 prevents oscillation between list and tree forms.</details>

40. Why does HashMap XOR the hashCode with its upper 16 bits?

<details><summary>Answer</summary>The bucket index uses only the **lower N bits** of the hash (where N = log₂(capacity)). For a table of size 16, only the lowest 4 bits determine the bucket. If many keys' hashCodes differ only in upper bits, they'd all collide. XORing with `h >>> 16` mixes upper bits into lower bits: `hash = h ^ (h >>> 16)`. This spreads the hash across buckets even when hashCodes have poor lower-bit distribution, reducing collisions without the cost of a full hash recalculation.</details>

41. Why is composition preferred over inheritance? Give a concrete example.

<details><summary>Answer</summary>Inheritance creates tight coupling (fragile base class problem) and breaks encapsulation. Classic example: `InstrumentedHashSet extends HashSet` overrides `add()` and `addAll()` to count additions. But `HashSet.addAll()` internally calls `add()`, causing double-counting. With **composition**: `InstrumentedSet` HAS-A `Set` field and delegates calls — no double-counting because it doesn't depend on `HashSet`'s internal implementation. Composition provides flexibility (can wrap any `Set` implementation) without fragile coupling.</details>

42. Explain the difference between fail-fast and weakly consistent iterators.

<details><summary>Answer</summary>**Fail-fast** (HashMap, ArrayList): if the collection is structurally modified during iteration (except through the iterator's own methods), it throws `ConcurrentModificationException`. This is a best-effort detection. **Weakly consistent** (ConcurrentHashMap): the iterator may or may not reflect modifications made after iterator creation. It never throws `ConcurrentModificationException` and guarantees traversal of elements as they existed at construction time, plus may reflect subsequent changes.</details>

43. What is the `try-with-resources` statement and how does resource closing order work?

<details><summary>Answer</summary>`try-with-resources` (Java 7+) automatically closes resources implementing `AutoCloseable`. Resources are closed in **reverse order** of declaration (LIFO). If both the try block and `close()` throw exceptions, the try block's exception is primary and the close exception is added as a **suppressed exception** (accessible via `getSuppressed()`). This is superior to `finally` blocks because: (1) deterministic closing, (2) no resource leaks from forgotten closes, (3) cleaner exception handling.</details>

## Scenario-Based Questions

44. In an interview, someone writes `String a = "Hello"; String b = "Hello"; String c = a + ""; System.out.println(a == b); System.out.println(a == c);`. What outputs and why?

<details><summary>Answer</summary>`a == b` prints `true` — both are string literals pointing to the same String Pool reference. `a == c` prints `false` — `a + ""` involves a variable (`a`), so it's a runtime concatenation using StringBuilder, producing a new heap object. However, if `a` were declared `final String a = "Hello"`, then `a + ""` would be a compile-time constant and `a == c` would be `true`. The compiler only folds expressions where all operands are compile-time constants.</details>

45. You're designing an e-commerce system. How would you apply all five SOLID principles?

<details><summary>Answer</summary>**SRP**: `OrderService` only orchestrates; tax calculation, payment, persistence, and notification are separate classes. **OCP**: new payment methods are added by implementing `PaymentProcessor` interface — no modification to `OrderService`. **LSP**: any `PaymentProcessor` implementation (Stripe, Razorpay) is fully substitutable. **ISP**: interfaces are small and focused — `PaymentProcessor` doesn't force `save()` or `notify()`. **DIP**: `OrderService` depends on abstractions (`PaymentProcessor`, `OrderRepository`, `NotificationService`), all injected via constructor — not on `StripePaymentProcessor` or `MySQLOrderRepository` directly.</details>

46. An `Employee` class is used as a HashMap key but lookups keep returning null. What's wrong?

<details><summary>Answer</summary>Most likely, `equals()` and/or `hashCode()` are not overridden. Default `hashCode()` is memory-address-based, so `new Employee(1, "Alice")` used for put and a different `new Employee(1, "Alice")` for get produce different hashCodes → different buckets → lookup fails. Fix: override both `equals()` (compare `id` and `name`) and `hashCode()` (use `Objects.hash(id, name)`) using the same fields. Also ensure the key is immutable — if fields change after insertion, the entry becomes unreachable.</details>

47. Your team has a `Bird` class with a `fly()` method. Now you need to add `Ostrich` which can't fly. How do you design this?

<details><summary>Answer</summary>Making `Ostrich extends Bird` and throwing `UnsupportedOperationException` in `fly()` violates **LSP** — code expecting any `Bird` to fly will break. Fix: restructure using **ISP**. Create a `Bird` interface with `eat()`, then a `FlyingBird` interface extending `Bird` with `fly()`. `Sparrow implements FlyingBird` (has `eat()` + `fly()`). `Ostrich implements Bird` (has only `eat()`). Now code that needs flying birds uses `FlyingBird` type, and Ostrich is never forced into an incompatible contract.</details>

## Interview-Focused Questions

48. What is the output of this code and why? `Parent p = new Child(); p.greet();` where `Parent` has `static void greet()` printing "Parent" and `Child` has `static void greet()` printing "Child".

<details><summary>Answer</summary>Output: "Parent". Static methods are **hidden**, not overridden — they use **static binding** (decided by reference type, not actual object type). Since `p` is declared as `Parent`, `Parent.greet()` is called. For instance methods, the actual object type decides (dynamic binding). This is a critical interview distinction: static → reference type decides, instance → object type decides.</details>

49. Explain what a functional interface is and give built-in examples.

<details><summary>Answer</summary>A functional interface has **exactly one abstract method** and can be used with lambda expressions. Annotated with `@FunctionalInterface` (optional but recommended). Built-in examples: `Predicate<T>` → `boolean test(T)`, `Function<T,R>` → `R apply(T)`, `Consumer<T>` → `void accept(T)`, `Supplier<T>` → `T get()`, `Runnable` → `void run()`, `Comparator<T>` → `int compare(T,T)`. Functional interfaces can have multiple `default` and `static` methods — only the abstract method count matters.</details>

50. Why is Java NOT a purely object-oriented language?

<details><summary>Answer</summary>A purely OOP language treats everything as an object. Java fails because: (1) **Primitive types** (`int`, `char`, `boolean`) are NOT objects. (2) **Static methods/fields** belong to the class, not objects. (3) **Wrapper classes** (`Integer`, `Double`) exist as workarounds. (4) **`null`** is not an object. (5) **Operators** (`+`, `-`) are not method calls. In contrast, Ruby/Smalltalk are purely OOP — even `5.even?` works because `5` is an object of class `Integer`.</details>

51. Walk through the complete lifecycle of `map.put("Alice", 100)` in a HashMap with default capacity.

<details><summary>Answer</summary>(1) Compute hash: `h = "Alice".hashCode()` → XOR with `h >>> 16` to get perturbated hash. (2) Find bucket: `index = (16 - 1) & hash` (bitwise AND with 15, keeping last 4 bits). (3) Check `table[index]`: if null → create new Node. If not null → walk chain: compare hash first (fast int comparison), then `equals()`. If key matches → replace value. If no match → append at tail (Java 8 uses tail insertion, not head). (4) Check chain length: if ≥ 8 and table ≥ 64 → treeify. (5) Check size: if `++size > 16 * 0.75 = 12` → resize to 32, rehash all entries.</details>

52. What is the ternary operator type promotion trap that interviewers love to ask?

<details><summary>Answer</summary>`Object result = true ? new Integer(1) : new Double(2.0);` prints `1.0`, not `1`. The ternary operator promotes both branches to a **common type**. `int` and `double` → `double` (numeric promotion). So `Integer(1)` is unboxed to `int 1`, promoted to `double 1.0`, then autoboxed to `Double`. The result is `1.0` of type `Double`. This catches many developers off guard because the "true" branch still gets type-promoted due to the other branch's type.</details>

53. Explain how `ConcurrentHashMap` differs internally from `HashMap` in Java 8+.

<details><summary>Answer</summary>Java 8+ ConcurrentHashMap uses **CAS (Compare-And-Swap)** for inserting into empty buckets (lock-free) and **`synchronized` on the first node** of non-empty buckets. There is **no global lock** — multiple threads can read and write to different buckets simultaneously. It also supports treeification like HashMap. Key differences: no null keys/values allowed, weakly consistent iterators (no `ConcurrentModificationException`), and atomic compound operations like `computeIfAbsent()`. Much better than Hashtable's global lock approach.</details>

54. How would you explain the Dependency Inversion Principle using a real-world Spring Boot example?

<details><summary>Answer</summary>In Spring Boot, DIP is built-in via IoC (Inversion of Control). Instead of `UserService` creating `new MySQLRepository()`, you: (1) define an interface `UserRepository`, (2) implement `MySQLUserRepository implements UserRepository`, (3) inject via constructor: `UserService(UserRepository repo)`. Spring's container manages the wiring. To switch to PostgreSQL, you only create `PostgreSQLUserRepository` and change a config — `UserService` is untouched. The high-level module (`UserService`) depends on an abstraction (`UserRepository`), not the concrete database implementation.</details>

55. What are sealed classes (Java 17+) and what problem do they solve?

<details><summary>Answer</summary>Sealed classes restrict which classes can extend them using the `permits` clause: `sealed class Shape permits Circle, Rectangle {}`. Subclasses must be `final` (no further extension), `sealed` (controlled extension), or `non-sealed` (open extension). This solves the problem of uncontrolled inheritance hierarchies — you know exactly which subtypes exist, enabling exhaustive pattern matching in `switch` expressions. It's especially useful for domain modeling where you want a closed set of variants (like algebraic data types).</details>

## OOP Relationships — Association, Aggregation, Composition, Dependency & Realization

56. What is Association in OOP and what are its types?

<details><summary>Answer</summary>**Association** is the most general relationship between two classes — it means one class "knows about" or "uses" another. It represents a **HAS-A** or **USES-A** relationship. Association can be: (1) **Unidirectional** — only one class knows about the other (e.g., `Customer` knows `Order`, but `Order` doesn't know `Customer`). (2) **Bidirectional** — both classes know about each other (e.g., `Doctor` knows `Patient` and vice versa). Association has **multiplicity**: one-to-one (1 person has 1 passport), one-to-many (1 department has many employees), many-to-many (students and courses). Association is the parent concept — **Aggregation** and **Composition** are specialized forms of association.

```java
// Unidirectional association — Customer knows Order
class Customer {
    List<Order> orders;  // Customer → Order
}

// Bidirectional association — Doctor ↔ Patient
class Doctor {
    List<Patient> patients;
}
class Patient {
    Doctor doctor;
}
```</details>

57. What is Aggregation and how does it differ from a plain Association?

<details><summary>Answer</summary>**Aggregation** is a specialized form of association representing a **"HAS-A" (whole-part)** relationship where the part can exist **independently** of the whole. If the whole is destroyed, the parts **survive**. It is a **weak ownership** relationship. UML notation: an empty diamond (◇) on the whole side.

```java
// Aggregation: Department HAS Professors
// Professors exist independently — they can belong to another department
class Department {
    String name;
    List<Professor> professors;  // Aggregation — professors are NOT created/destroyed by Department

    Department(String name, List<Professor> professors) {
        this.professors = professors;  // Passed in from outside
    }
}

class Professor {
    String name;
    Professor(String name) { this.name = name; }
}

// Professors exist before and after Department
Professor p1 = new Professor("Alice");
Professor p2 = new Professor("Bob");
Department dept = new Department("CS", List.of(p1, p2));
// If dept is destroyed, p1 and p2 still exist
```

**Key indicator**: the part is passed INTO the whole from outside (not created inside). The whole does NOT control the part's lifecycle.</details>

58. What is Composition and how does it differ from Aggregation?

<details><summary>Answer</summary>**Composition** is a specialized form of association representing a **"HAS-A" (whole-part)** relationship where the part **cannot exist independently** of the whole. If the whole is destroyed, the parts are **also destroyed**. It is a **strong ownership** relationship. UML notation: a filled diamond (◆) on the whole side.

```java
// Composition: House HAS Rooms
// Rooms cannot exist without a House — they are created and destroyed WITH it
class House {
    private final List<Room> rooms;

    House() {
        // Rooms are created INSIDE House — House controls their lifecycle
        this.rooms = new ArrayList<>();
        rooms.add(new Room("Living Room"));
        rooms.add(new Room("Kitchen"));
        rooms.add(new Room("Bedroom"));
    }
    // When House is garbage collected, all Rooms are too
}

class Room {
    String name;
    Room(String name) { this.name = name; }
}
```

| Feature | Aggregation | Composition |
|---|---|---|
| Ownership | Weak (shared) | Strong (exclusive) |
| Lifecycle | Part survives if whole dies | Part dies with the whole |
| UML | Empty diamond ◇ | Filled diamond ◆ |
| Part created by | Outside, passed in | Inside, by the whole |
| Example | Department → Professors | House → Rooms |
| Example | Team → Players | Human → Heart |
| Example | Library → Books | Car → Engine (in most designs) |</details>

59. What is Dependency in OOP and how is it different from Association?

<details><summary>Answer</summary>**Dependency** is the **weakest** relationship between classes — it means one class **temporarily uses** another, typically as a method parameter, local variable, or return type. The dependent class does NOT hold a reference as a field — the relationship exists only during a method call. UML notation: a dashed arrow (- - - →).

```java
// Dependency: OrderService USES PaymentGateway temporarily (only in method scope)
class OrderService {
    // NOT a field — no long-term relationship
    void processOrder(Order order, PaymentGateway gateway) {
        gateway.charge(order.getTotal());  // Uses gateway temporarily
    }
}

// Association: OrderService HAS a PaymentGateway (long-term relationship)
class OrderService {
    private PaymentGateway gateway;  // Stored as field — long-term
    void processOrder(Order order) {
        gateway.charge(order.getTotal());
    }
}
```

| Feature | Dependency | Association |
|---|---|---|
| Strength | Weakest | Stronger |
| Duration | Temporary (method scope) | Long-term (field) |
| How used | Parameter, local variable, return type | Instance field |
| UML | Dashed arrow (- - →) | Solid arrow (→) |
| Change impact | Changes in used class MAY affect dependent | Changes in associated class WILL affect |</details>

60. What is Realization in OOP?

<details><summary>Answer</summary>**Realization** is the relationship between an **interface** and a class that **implements** it. The class realizes (fulfills) the contract defined by the interface. UML notation: a dashed arrow with a hollow triangle (- - - ▷). Realization is similar to generalization (inheritance) but for interfaces instead of classes.

```java
// Realization: PaymentProcessor REALIZES (implements) PaymentGateway interface
interface PaymentGateway {
    void charge(double amount);
    void refund(double amount);
}

class StripeProcessor implements PaymentGateway {  // Realization
    @Override
    public void charge(double amount) {
        System.out.println("Stripe: Charged $" + amount);
    }

    @Override
    public void refund(double amount) {
        System.out.println("Stripe: Refunded $" + amount);
    }
}

class RazorpayProcessor implements PaymentGateway {  // Realization
    @Override
    public void charge(double amount) {
        System.out.println("Razorpay: Charged ₹" + amount);
    }

    @Override
    public void refund(double amount) {
        System.out.println("Razorpay: Refunded ₹" + amount);
    }
}
```

| Relationship | Keyword | UML | Example |
|---|---|---|---|
| **Generalization** (Inheritance) | `extends` | Solid line + hollow triangle (—▷) | `Dog extends Animal` |
| **Realization** (Implementation) | `implements` | Dashed line + hollow triangle (- -▷) | `StripeProcessor implements PaymentGateway` |</details>

61. Compare all six OOP relationships: Association, Aggregation, Composition, Dependency, Generalization, and Realization.

<details><summary>Answer</summary>

| Relationship | Type | Strength | Lifecycle Coupling | UML Notation | Java Keyword | Example |
|---|---|---|---|---|---|---|
| **Dependency** | Uses temporarily | Weakest | None | Dashed arrow (- - →) | Method parameter | `void print(Printer p)` |
| **Association** | Knows about / Uses | Weak | Independent | Solid arrow (→) | Field reference | `class Student { Course course; }` |
| **Aggregation** | HAS-A (shared) | Medium | Part survives | Empty diamond (◇→) | Field (passed in) | `Department has Professors` |
| **Composition** | HAS-A (owned) | Strong | Part dies with whole | Filled diamond (◆→) | Field (created inside) | `House has Rooms` |
| **Generalization** | IS-A | Strongest | Child depends on parent | Solid line + hollow triangle (—▷) | `extends` | `Dog extends Animal` |
| **Realization** | Implements contract | Strong | Class must fulfill interface | Dashed line + hollow triangle (- -▷) | `implements` | `ArrayList implements List` |

**How to identify which relationship to use:**
- Does class A temporarily use class B in a method? → **Dependency**
- Does class A hold a reference to class B, but B can exist independently? → **Association** or **Aggregation**
- Does class A create and own class B (B dies with A)? → **Composition**
- Is class A a specialized type of class B? → **Generalization** (`extends`)
- Does class A fulfill a contract defined by interface B? → **Realization** (`implements`)</details>

62. What are the different types of Cohesion and Coupling? Explain with examples.

<details><summary>Answer</summary>

### Types of Cohesion (from worst to best):

| Type | Description | Example |
|---|---|---|
| **Coincidental** (worst) | Unrelated functions grouped randomly | A `Utils` class with `sendEmail()`, `formatDate()`, `calculateTax()` |
| **Logical** | Related by category but not by functionality | A `DataProcessor` that handles CSV, JSON, and XML based on a flag |
| **Temporal** | Grouped because they run at the same time | An `init()` method that opens DB connection, reads config, AND starts logging |
| **Procedural** | Grouped because they follow a sequence | A method that validates input, THEN saves to DB, THEN sends email — all in one |
| **Communicational** | Operate on the same data | A `StudentReport` class that calculates GPA AND prints transcript — both use student data |
| **Sequential** | Output of one feeds into the next | A method that reads raw data → parses it → validates it (pipeline) |
| **Functional** (best) | Every element contributes to ONE well-defined task | A `PasswordHasher` class that only hashes passwords |

### Types of Coupling (from worst to best):

| Type | Description | Example |
|---|---|---|
| **Content** (worst) | One class modifies another's internal data directly | Class A directly accesses `classB.privateField` via reflection |
| **Common** | Classes share global/static data | Two classes both read/write to a `static GlobalState.config` |
| **Control** | One class passes a flag to control another's behavior | `process(data, isAdmin)` — the caller controls internal logic via flag |
| **Stamp** | Passing a whole object when only part of it is needed | `printName(Employee emp)` when only `emp.name` is needed |
| **Data** (best) | Classes communicate only through simple parameters | `calculateTax(double amount, double rate)` — only needed data is passed |

```java
// ❌ Content coupling — directly accessing internals
class A {
    void hack(B b) {
        b.secret = 42;  // Reaching into B's internals
    }
}

// ❌ Control coupling — flag controls behavior
class Processor {
    void process(String data, boolean isUpperCase) {
        if (isUpperCase) { /* ... */ } else { /* ... */ }
    }
}

// ✅ Data coupling — only needed values passed
class TaxCalculator {
    double calculate(double amount, double rate) {
        return amount * rate;
    }
}

// ✅ Functional cohesion — single focused responsibility
class PasswordHasher {
    String hash(String password) { /* only hashing logic */ }
    boolean verify(String password, String hash) { /* only verification */ }
}
```

**Goal: High (Functional) Cohesion + Low (Data) Coupling** — each class does one thing well, and classes interact through minimal, well-defined interfaces.</details>

## Enums

63. What is an enum in Java and what problem does it solve?

<details><summary>Answer</summary>An **enum** (enumeration) is a special data type that defines a **fixed set of named constants**. It is type-safe — the compiler ensures only valid values from the defined set can be used. Enums solve the problem of "magic values": without enums, you'd represent states as strings (`"SHIPPED"`) or integers (`2`), both of which are error-prone. A string typo like `"Shiped"` compiles fine but silently fails at runtime. An int like `if (status == 2)` is meaningless without context. Enums eliminate this entire class of bugs by making invalid values a **compile-time error** rather than a runtime surprise.</details>

64. What are the advantages of using enums over plain string or integer constants?

<details><summary>Answer</summary>(1) **Type safety** — only valid enum values compile; `OrderStatus.SHIPED` is a compile error, `"Shiped"` is not. (2) **No magic values** — `OrderStatus.SHIPPED` is far more descriptive than `3` or `"SHIPPED"`. (3) **Compiler checks** — switch statements on enums warn if a case is missing. (4) **IDE support** — auto-completion and refactoring tools work with enums, not raw strings. (5) **Can carry data and behavior** — enums can have fields, constructors, and methods (unlike plain `static final` constants). (6) **Safe comparison** — enums are singletons, so `==` is always safe; with Strings, `==` vs `equals()` causes bugs. (7) **`values()` / `valueOf()`** — built-in iteration and conversion support.</details>

65. When should you use an enum vs a String constant vs an integer constant?

<details><summary>Answer</summary>**Use enum when**: the set of values is **fixed and known at compile time** (order statuses, user roles, directions, coin types). You need compiler validation, IDE support, or want to attach behavior to each constant. **Use String when**: values are **dynamic** — loaded from config, database, or API at runtime; or for free-text fields like names and descriptions. **Use integer constants when**: interfacing with external systems or protocols that use integer codes (e.g., HTTP status codes in a low-level library). In general, if you find yourself writing `static final String STATUS_SHIPPED = "SHIPPED"`, that's a signal to use an enum instead.</details>

66. How do you add fields, constructors, and methods to a Java enum? Give an example.

<details><summary>Answer</summary>Enum constants can carry additional data by defining fields and a constructor. The constructor is implicitly `private`.

```java
public enum PaymentMethod {
    CREDIT_CARD("Credit Card", 2.5),
    DEBIT_CARD("Debit Card", 1.0),
    UPI("UPI", 0.0),
    NET_BANKING("Net Banking", 1.5);

    private final String displayName;
    private final double feePercent;

    PaymentMethod(String displayName, double feePercent) {
        this.displayName = displayName;
        this.feePercent = feePercent;
    }

    public String getDisplayName() { return displayName; }
    public double getFeePercent()  { return feePercent; }
}

// Usage:
double fee = PaymentMethod.CREDIT_CARD.getFeePercent(); // 2.5
```

The data lives right next to the constant — no separate lookup table needed, no risk of data and name going out of sync.</details>

67. What built-in methods does every Java enum provide?

<details><summary>Answer</summary>Every enum automatically inherits from `java.lang.Enum` and gets: (1) **`name()`** — returns the constant's name as a String (`"SHIPPED"`). (2) **`ordinal()`** — returns the 0-based position in declaration order. (3) **`toString()`** — same as `name()` by default, can be overridden. (4) **`values()`** — static method returning an array of all constants in declaration order. (5) **`valueOf(String)`** — static method converting a String to the matching enum constant (case-sensitive; throws `IllegalArgumentException` if not found). (6) **`compareTo()`** — compares by ordinal. (7) Enums can be used in `switch` statements and are implicitly `final` and `Serializable`.</details>

68. Why is using `==` safe for enum comparison but not for Strings?

<details><summary>Answer</summary>Each enum constant is a **singleton** — only one object exists per constant in the JVM. So `==` (reference equality) always works correctly: `status == OrderStatus.SHIPPED` is safe and even preferred over `.equals()`. With Strings, `==` checks reference (memory address), not value — `new String("SHIPPED") == "SHIPPED"` is `false` because they are different objects. `equals()` must be used for String content comparison. Enums avoid this trap entirely: you can never accidentally have two `OrderStatus.SHIPPED` objects with different references.</details>

69. How does an enum-based order status design control valid state transitions? Walk through the order processing example.

<details><summary>Answer</summary>The `OrderStatus` enum (`PLACED → CONFIRMED → SHIPPED → DELIVERED | CANCELLED`) works with the `Order` class to enforce business rules:

```java
public boolean advanceStatus() {
    switch (status) {
        case PLACED:    status = OrderStatus.CONFIRMED; return true;
        case CONFIRMED: status = OrderStatus.SHIPPED;   return true;
        case SHIPPED:   status = OrderStatus.DELIVERED; return true;
        default:        return false; // DELIVERED or CANCELLED — no advance
    }
}

public boolean cancel() {
    if (status == OrderStatus.PLACED || status == OrderStatus.CONFIRMED) {
        status = OrderStatus.CANCELLED;
        return true;
    }
    return false; // Cannot cancel after shipping
}
```

**Why this works well**: (1) Invalid transitions are impossible — you can't jump from `PLACED` to `DELIVERED`. (2) Cancellation rules are enforced by enum comparison — no string matching risks. (3) The `switch` on an enum gives a compiler warning if you add a new status and forget to handle it. (4) Adding a `RETURNED` status only requires adding it to the enum and updating the switch — the compiler will flag any missed case handlers.</details>

70. How does adding a new enum constant affect existing code, and what does the compiler help you catch?

<details><summary>Answer</summary>Adding a new enum constant (e.g., `RETURNED` to `OrderStatus`) is **additive and safe** — existing code compiles. However, the compiler (and IDEs) will warn you about **non-exhaustive switch statements**: if your `switch` on an enum doesn't cover the new value and has no `default`, it's a missing case warning. With **switch expressions** (Java 14+), exhaustiveness is enforced — a missing case is a **compilation error**:

```java
// Java 14+ switch expression — compiler ENFORCES all cases are handled
String label = switch (status) {
    case PLACED    -> "Awaiting confirmation";
    case CONFIRMED -> "Confirmed";
    case SHIPPED   -> "On the way";
    case DELIVERED -> "Delivered";
    case CANCELLED -> "Cancelled";
    // case RETURNED -> ... // ← Compile error if RETURNED is added and not handled here
};
```

This is one of the most powerful aspects of enums: **the compiler acts as a safeguard**, reminding you to update all the places in the code that need to handle the new value.</details>

## Interfaces

71. What is an interface in Java and what is the core idea behind it?

<details><summary>Answer</summary>An interface is a **contract** — a list of methods that any implementing class must provide. It defines the **"what"** (the behavior), while the implementing class defines the **"how"** (the implementation). Think of a remote control: it exposes `play()`, `pause()`, `volumeUp()`, `powerOff()` — it doesn't care whether the device is a TV, soundbar, or projector. Each device implements the contract differently, but the remote works with all of them. In Java: `interface PaymentGateway { void initiatePayment(double amount); }` — any class implementing this is guaranteed to provide `initiatePayment()`, regardless of whether it talks to Stripe, Razorpay, or PayPal.</details>

72. What are the key properties/benefits of using interfaces in software design?

<details><summary>Answer</summary>(1) **Defines behavior without dictating implementation** — implementers are free to provide their own logic while honoring the contract. (2) **Enables polymorphism** — different classes can implement the same interface and be used interchangeably. (3) **Promotes decoupling** — code depending on interfaces is insulated from changes in concrete classes, making it easier to extend (add new implementations), test (mock interfaces in unit tests), and maintain (fewer ripple effects from changes). Example: `CheckoutService` depends on `PaymentGateway` interface — it works with Stripe, Razorpay, or any future provider without modification.</details>

73. What does "programming to the interface" mean and why is it important?

<details><summary>Answer</summary>"Programming to the interface" means declaring variables and parameters using the **interface type** rather than the concrete class type. Instead of `StripePayment gateway = new StripePayment()`, you write `PaymentGateway gateway = new StripePayment()`. The calling code (`CheckoutService`) only knows about `PaymentGateway` — it has zero knowledge of Stripe or Razorpay internals. This single decision: (1) allows swapping implementations without changing the caller, (2) enables dependency injection, (3) makes unit testing easy (inject a mock), (4) future-proofs the design — a new provider just needs to implement the interface.</details>

74. What is dependency injection and how does it relate to interfaces?

<details><summary>Answer</summary>**Dependency injection (DI)** means a class receives its dependencies from the outside rather than creating them internally. It works because the dependency is typed as an **interface**, not a concrete class. Example: `CheckoutService(PaymentGateway gateway)` — the constructor accepts any implementation. At runtime, you choose which concrete class to inject: `new CheckoutService(new StripePayment())` or `new CheckoutService(new RazorpayPayment())`. You can also inject a mock in tests. Without interfaces, DI breaks — if the parameter was `StripePayment`, you can only ever inject Stripe. DI + interfaces together are the foundation of frameworks like Spring (IoC container).</details>

75. How does the `NotificationService` interface example demonstrate the Open/Closed Principle?

<details><summary>Answer</summary>The `NotificationService` interface (`send(String recipient, String message)`) with `EmailNotifier`, `SlackNotifier`, and `WebhookNotifier` implementations demonstrates OCP: `AlertService` is **closed for modification** (never changes) and **open for extension** (new channels just implement the interface). Adding `PagerDutyNotifier`? Create one new class implementing `NotificationService`. `AlertService` works with it immediately — zero changes. Without the interface, adding a new channel would require modifying `AlertService`'s conditional logic. The interface makes the system infinitely extensible without touching existing code.</details>

76. What is the difference between an interface and an abstract class? When do you use each?

<details><summary>Answer</summary>**Interface**: no constructors, only `public static final` fields, supports multiple inheritance, no shared state, represents a **capability/contract** (CAN-DO). **Abstract class**: can have constructors, instance fields, any access modifier, allows partial implementation, represents a **type hierarchy** (IS-A). **Use interface when**: defining a contract for unrelated classes (e.g., `Serializable`, `Comparable`, `PaymentGateway` — a bank and a crypto wallet both process payments but share nothing). **Use abstract class when**: sharing common code among closely related classes (e.g., `Logger` abstract class with shared `formatMessage()` used by `ConsoleLogger` and `FileLogger`). Key rule: share **behavior** → abstract class; define **contract** → interface.</details>

77. Can a class implement multiple interfaces? Give a practical example of when this is useful.

<details><summary>Answer</summary>Yes — Java allows implementing multiple interfaces, which is how it achieves multiple inheritance of type. Example: `class OrderService implements Exportable, Auditable, Notifiable`. `Exportable` provides `export()`, `Auditable` provides `logAction()`, `Notifiable` provides `notify()`. `OrderService` can fulfill all three contracts independently. This is useful when a class naturally needs to be plug-compatible with multiple systems — e.g., a `PaymentProcessor` that is both `Loggable` (for audit trails) and `Retryable` (for failure handling). If two interfaces have the same `default` method, the class must override and resolve explicitly using `InterfaceName.super.method()`.</details>

## Encapsulation

78. What is encapsulation and what does "data hiding + controlled access" mean?

<details><summary>Answer</summary>**Encapsulation** is the practice of grouping data (fields) and behavior (methods) into a single unit (class) and restricting direct external access to internal data. **Data hiding** means fields are `private` — external code can't read or write them directly. **Controlled access** means external code interacts only through `public` methods that enforce business rules. Bank analogy: you can't walk into the vault and change numbers. You use the ATM (`deposit()`, `withdraw()`, `getBalance()`). The bank can change how it stores data internally without affecting how you use the ATM. That separation is encapsulation.</details>

79. How do access modifiers implement encapsulation in Java?

<details><summary>Answer</summary>Access modifiers control which code can see a class's members: **`private`** (only within the same class) is the primary tool for data hiding — fields are almost always `private`. **`protected`** (same package + subclasses) is useful when child classes need parent data. **`public`** (everywhere) is used for the controlled interface — the methods callers are allowed to use. **General rule**: make everything `private` by default, then selectively expose what needs to be public. Example: `BankAccount` — `private double balance` (hidden), `public void deposit(double amount)` (controlled interface with validation).</details>

80. What is the role of getters and setters in encapsulation? When should you add validation in a setter?

<details><summary>Answer</summary>**Getters** provide read-only access to private fields. **Setters** provide controlled write access, often with validation logic. Add validation in a setter whenever the field has constraints: `setPrice(double price)` should throw `IllegalArgumentException` if `price < 0` — this ensures the `Product` object is **always in a valid state**. Without a setter with validation, calling code could set `product.price = -50` if the field were public. The constructor should **call the setter** (not assign directly) so validation runs at creation time too. Not every field needs a setter — if a field should never change after construction (like `accountHolder`), omit the setter entirely.</details>

81. Why is encapsulation important for maintainability and security?

<details><summary>Answer</summary>**Maintainability**: internal implementation can change without affecting external code. If `BankAccount` switches from storing balance as `double` to `BigDecimal` for precision, only the class internals change — callers using `getBalance()` and `deposit()` are unaffected. **Security**: sensitive data is protected from direct tampering. `PaymentProcessor` immediately masks the raw card number in the constructor — even if someone inspects the object via debugging or reflection, they only see `****-****-****-5678`. The raw number is never stored. **Invariants**: encapsulation guarantees class invariants — `balance` can never go negative because both `withdraw()` and `deposit()` validate before modifying. Direct field access could bypass all checks.</details>

82. Explain the `PaymentProcessor` card masking example and what it demonstrates about encapsulation.

<details><summary>Answer</summary>The `PaymentProcessor` constructor takes a full 16-digit card number but immediately calls `maskCardNumber()` — a `private` method — and stores only `"****-****-****-5678"`. The original number is **never stored**. This demonstrates: (1) **Private methods hide implementation details** — callers don't know masking exists or how it works. (2) **Encapsulation applied to security** — sensitive data enters, gets transformed, and the original is discarded. (3) **Minimal external interface** — callers just do `new PaymentProcessor("1234...", 250.0)` and `processPayment()`. (4) **Change isolation** — changing the masking format (first 4 vs last 4) means editing one private method; zero callers are affected.</details>

83. What's the difference between encapsulation enforcing invariants vs just hiding fields?

<details><summary>Answer</summary>Merely making fields `private` with trivial getters/setters is **"accidental encapsulation"** — it hides the field but doesn't protect the invariant. True encapsulation means the methods enforce business rules: `BankAccount.withdraw()` checks `amount > 0` AND `amount <= balance` before modifying `balance`. This guarantees the account is **always in a valid state** — balance can never go negative, you can never withdraw zero. A "getter/setter bean" with `setBalance(double b) { this.balance = b; }` exposes no more protection than a public field. Real encapsulation = controlled access with meaningful validation, not just syntactic hiding.</details>

## Abstraction

84. What is abstraction in OOP and how does it differ from encapsulation?

<details><summary>Answer</summary>**Abstraction** hides **complexity** — it shows only essential, high-level functionality and suppresses irrelevant details. **Encapsulation** hides **data** — it protects internal state via access modifiers. Car analogy: the accelerator pedal is abstraction (you press it without knowing fuel injection mechanics). The sealed engine housing is encapsulation (pistons and valves are protected from tampering). In code: `DatabaseClient` exposes `connect()` and `query()` (abstraction — caller sees only essentials), while `private void openSocket()` and `private void authenticate()` are protected (encapsulation). Abstraction is **design-level** (what the user sees), encapsulation is **implementation-level** (how internals are protected).</details>

85. What are the three mechanisms to achieve abstraction in Java?

<details><summary>Answer</summary>(1) **Abstract classes** — define a blueprint with abstract methods (must be implemented by subclass) and concrete methods (shared behavior). Example: `abstract class Logger` with abstract `log()` and concrete `formatMessage()`. (2) **Interfaces** — purely define a contract (what), no shared behavior. Example: `interface Exportable { String export(); }` — `CSVExporter` and `JSONExporter` share the capability, not the implementation. (3) **Clean public APIs** — regular classes with well-designed `public` methods and `private` helpers. Example: `DatabaseClient` exposes `connect()` and `query()` while hiding `openSocket()`, `authenticate()`, `executeWithRetry()`. All three achieve the same goal: callers see the essential surface, not the complexity behind it.</details>

86. What is the advantage of an abstract class over an interface when you need shared behavior?

<details><summary>Answer</summary>Abstract classes let you **write shared code once** and have all subclasses inherit it. Example: `abstract Logger` has `formatMessage()` that prepends timestamp and log level — every subclass (`ConsoleLogger`, `FileLogger`) inherits this without reimplementing it. With an interface, there's no field for `level` and no shared `formatMessage()` — every implementer would have to duplicate the formatting logic. The division of labor: abstract class handles **what every logger has in common** (formatting), concrete subclasses handle **what's different** (where the message goes). Interfaces only define the contract; abstract classes can define the contract AND provide reusable implementations.</details>

87. How does the logging system example show the four benefits of abstraction?

<details><summary>Answer</summary>(1) **Swap implementations without changing callers**: `Application` holds a `Logger` reference — switching from `ConsoleLogger` to `FileLogger` is one line change at the injection point. Application code unchanged. (2) **Reduce complexity for consumers**: the application calls `logger.log("Server started")` — it never sees file handles, HTTP connections, or buffering. (3) **Extend without modifying**: adding `DatabaseLogger extends Logger` requires zero changes to `Application`, `ConsoleLogger`, or `FileLogger`. (4) **Share common logic once**: `formatMessage()` in the abstract `Logger` is written once; all subclasses inherit consistent formatting. Without abstraction, that formatting would be duplicated in every conditional branch.</details>

88. When should you use an interface vs an abstract class for abstraction?

<details><summary>Answer</summary>**Use abstract class**: classes are **closely related**, share common state or behavior, and form an IS-A hierarchy. Example: `Logger` → `ConsoleLogger`/`FileLogger` — all loggers share `level` field and `formatMessage()`. **Use interface**: classes are **unrelated** but share a capability. Example: `Exportable` implemented by `CSVExporter`, `JSONExporter`, `XMLExporter` — these have nothing structurally in common, just share the ability to export. Rule: **"Is this a type hierarchy with shared code?"** → abstract class. **"Is this a capability contract across unrelated classes?"** → interface. In practice, many designs use both: an abstract class can implement an interface, giving consumers an interface dependency while subclasses inherit shared implementation.</details>

89. Walk through the `MediaPlayer` abstract class example and explain the design decisions.

<details><summary>Answer</summary>`abstract class MediaPlayer` has: `play()`, `pause()`, `stop()` declared abstract (each player type implements differently), and `displayStatus()`, `logAction()` concrete (shared by all players). **Design decisions**: (1) Abstract methods force `AudioPlayer`, `VideoPlayer`, `StreamingPlayer` to implement channel-specific logic — forgetting one is a compile error. (2) Concrete `logAction()` and `displayStatus()` are written once — every player uses the same format without code duplication. (3) `PlayerController` depends only on `MediaPlayer` — it imports nothing from `AudioPlayer` or `StreamingPlayer`. Adding `PodcastPlayer`? Zero changes to `PlayerController`. (4) Each player's complexity stays internal — `StreamingPlayer` manages buffer size internally; the controller just calls `play()`.</details>

## Inheritance

90. What is inheritance and what does the "is-a" relationship mean?

<details><summary>Answer</summary>**Inheritance** allows a subclass (child) to inherit fields and methods from a superclass (parent), enabling code reuse and specialization. The **"is-a"** relationship is the validity test: `ElectricCar` IS-A `Vehicle` ✅, `Admin` IS-A `User` ✅, `EmailNotification` IS-A `Notification` ✅. If the "is-a" test fails, inheritance is wrong — a `Car` HAS-AN `Engine` (composition, not inheritance). When a subclass inherits from a parent: it gets all non-private fields/methods, can override inherited methods with its own implementation, and can add new fields and methods specific to its type.</details>

91. What are the four main benefits of inheritance?

<details><summary>Answer</summary>(1) **Code reusability (DRY)** — common logic written once in the parent, shared across all subclasses. `Vehicle.startEngine()` is written once; both `ElectricCar` and `GasCar` inherit it. (2) **Logical hierarchy** — creates intuitive IS-A structure mirroring real-world relationships. (3) **Ease of maintenance** — fix a bug in the parent and all subclasses automatically get the fix. Change `Notification.formatHeader()` format once; all three notification types inherit the updated format. (4) **Polymorphism** — inheritance is a prerequisite for runtime polymorphism: a `Notification` reference can point to any subclass, and `send()` dispatches to the correct implementation at runtime.</details>

92. What are the types of inheritance and which does Java support?

<details><summary>Answer</summary>**Single**: one child extends one parent (`ElectricCar extends Vehicle`) — most common, supported everywhere. **Multilevel**: chain (`Vehicle → Car → ElectricCar`) — supported in Java, but keep chains shallow (2-3 levels max). **Hierarchical**: multiple children extend the same parent (`ElectricCar`, `GasCar`, `HybridCar` all extend `Vehicle`) — supported, very natural. **Multiple**: one child extends multiple parents — Java does **NOT** support this for classes due to the **Diamond Problem** (ambiguous method resolution). Java's solution: implement multiple **interfaces** (not classes). Python resolves diamond ambiguity with C3 linearization (MRO); C++ with virtual inheritance. Java simply prevents the problem at the language level.</details>

93. What is the Diamond Problem and how does Java avoid it?

<details><summary>Answer</summary>The Diamond Problem occurs in multiple inheritance: class `C extends A, B`. Both `A` and `B` override `method()`. When `C.method()` is called, which parent's version runs? This is ambiguous. Java avoids it by **not allowing a class to extend more than one class**. You can only `extends` one class. For multiple type relationships, use `implements` with interfaces. If two interfaces have the same `default` method, the implementing class **must** explicitly override it and can call a specific parent's default via `InterfaceName.super.method()` — making the resolution explicit. This is safe because interfaces carry no state that could conflict.</details>

94. When should you use inheritance vs composition?

<details><summary>Answer</summary>**Use inheritance when**: there's a genuine IS-A relationship, the parent defines shared behavior children should inherit, child doesn't violate parent's expected behavior (LSP), and the hierarchy is shallow (≤ 3 levels). **Use composition when**: the relationship is HAS-A or USES-A (a `Car` HAS-AN `Engine`), you need runtime flexibility to swap behaviors (inject a `FileLogger` or `ConsoleLogger`), you want to combine behaviors from multiple sources dynamically, or you want to avoid tight coupling from deep inheritance chains. **Rule**: "when in doubt, start with composition." Refactoring from composition to inheritance is straightforward; untangling a deep inheritance tree back into composition is much harder. The Gang of Four explicitly advises: *"Favor composition over inheritance."*</details>

95. Explain the `super` keyword — when and why is it used in inheritance?

<details><summary>Answer</summary>`super` refers to the **parent class**. Used in two contexts: (1) **Constructor chaining**: `super(make, model, year)` in `ElectricCar`'s constructor calls the `Vehicle` constructor — must be the **first statement**. Without it, Java inserts an implicit `super()` (no-arg) call, which fails if the parent has no no-arg constructor. (2) **Calling parent method**: inside an overridden method, `super.send()` calls the parent's version before adding child-specific behavior. Example: `EmailNotification.send()` can call `super.send()` to print the header, then add its own subject line. This avoids duplicating the base display logic in every subclass.</details>

96. Walk through the `Notification` inheritance example and explain why the design works.

<details><summary>Answer</summary>`Notification` (parent) holds `recipient`, `message`, `timestamp` and provides `formatHeader()` — written once, inherited by all. `EmailNotification`, `SMSNotification`, `PushNotification` each `@Override send()` with channel-specific logic. **Why it works**: (1) `formatHeader()` is written once — consistent timestamp/recipient format across all channels. Change it once, all three update. (2) Each child encapsulates its own complexity — `SMSNotification` handles 160-char limit internally, `PushNotification` manages device tokens/priority. None leaks into the parent. (3) Polymorphism: a `Notification` reference can point to any subclass, enabling `for (Notification n : notifications) { n.send(); }` that dispatches to the correct channel at runtime. (4) Adding `SlackNotification extends Notification` requires only one new class — no existing code changes.</details>

97. What is the fragile base class problem and how does it affect inheritance?

<details><summary>Answer</summary>The **fragile base class problem** occurs when a change to a parent class breaks subclasses that depend on its internal behavior. Classic example: `InstrumentedHashSet extends HashSet` overrides `add()` and `addAll()` to count insertions. But `HashSet.addAll()` internally calls `add()` — so `addAll(["a","b","c"])` increments `addCount` by 6, not 3 (double-counting). The subclass broke because it relied on an internal implementation detail of the parent. **Why this is dangerous**: parent class authors don't know all subclasses depending on their internals; internal implementation changes are valid but break subclasses silently. **Solution**: prefer composition — `InstrumentedSet` HAS-A `Set` field and delegates calls, isolating itself from the parent's internal behavior entirely.</details>

## Polymorphism

98. What is polymorphism and what are its two types in Java?

<details><summary>Answer</summary>**Polymorphism** (Greek: "many forms") allows the same method name or interface to exhibit different behaviors depending on the object invoking it. **Compile-time polymorphism (method overloading)**: multiple methods with the same name but different parameter lists in the same class — resolved by the compiler based on argument types. **Runtime polymorphism (method overriding / dynamic dispatch)**: a child class overrides a parent method and the JVM decides which version to call at runtime based on the actual object type, not the declared reference type. Runtime polymorphism is the more powerful and important form — it enables loose coupling and extensibility.</details>

99. How does compile-time polymorphism (method overloading) work? What does the compiler use to decide which method to call?

<details><summary>Answer</summary>The compiler resolves overloaded methods based on the **number, types, and order of arguments** at the call site — before the program runs. Priority order: (1) exact match, (2) widening (`int → long → double`), (3) autoboxing (`int → Integer`), (4) varargs. Example: `calc.add(2, 3)` → `add(int, int)`. `calc.add(2.5, 3.5)` → `add(double, double)`. `calc.add(1, 2, 3)` → `add(int, int, int)`. Important: return type alone does NOT distinguish overloaded methods — `int add(int, int)` and `double add(int, int)` is a compile error. A static method cannot be overridden, so static overloading is always compile-time.</details>

100. Explain runtime polymorphism (dynamic dispatch) with an example. What does the JVM actually do?

<details><summary>Answer</summary>Runtime polymorphism occurs when a child overrides a parent method and the JVM resolves the call **at runtime** based on the actual object type. Example: `List<Notification> list = List.of(new EmailNotification(...), new SMSNotification(...)); for (Notification n : list) { n.send(); }` — every element is stored as a `Notification` reference, but `send()` dispatches to `EmailNotification.send()` or `SMSNotification.send()` based on the actual object. The JVM uses a **virtual method table (vtable)** — a per-class lookup table of overridden methods. Instance method calls index into the vtable at runtime. Static/private/final methods bypass vtable (static binding). This is why `Base b = new Child(); b.instanceMethod()` calls Child's version.</details>

101. What are the four concrete benefits of polymorphism in software design?

<details><summary>Answer</summary>(1) **Loose coupling** — code interacts with abstractions (interfaces, base classes), not specific implementations. (2) **Flexibility** — introduce new behaviors without modifying existing code, supporting OCP: adding `PushNotification` doesn't change the loop that calls `n.send()`. (3) **Scalability** — systems grow by adding new types without impacting existing logic. (4) **Extensibility** — plug in new implementations without touching core business logic. Real example: A notification dispatch loop works for Email, SMS, Push, and any future channel — just because all implement `send()`, without a single `if-else` or `instanceof`.</details>

102. When should you use an interface vs an abstract class to enable polymorphism?

<details><summary>Answer</summary>Both enable polymorphism — calling `send()` on a base reference dispatches to the correct override whether `Notification` is an abstract class or interface. The choice depends on **relationship type**: **Abstract class** → related classes sharing state and behavior ("is-a" family). Use when all sending types share `recipient`, `message`, `formatHeader()` logic. **Interface** → unrelated classes sharing a capability ("can-do"). Use when `Email`, `Invoice`, and `Report` are structurally different but all need `send()`. **In practice, combine both**: an abstract `Notification` class provides shared fields and formatting, while a `Sendable` interface marks anything that can be sent (notifications, alerts, reports). Abstract class inheritance is single; interface implementation is multiple.</details>

103. What is the difference between method hiding (static) and method overriding (instance)?

<details><summary>Answer</summary>**Method overriding** (instance methods): resolved at **runtime** based on actual object type (dynamic dispatch via vtable). `Animal a = new Dog(); a.speak()` calls Dog's `speak()`. **Method hiding** (static methods): resolved at **compile time** based on **reference type**. `Animal a = new Dog(); a.staticMethod()` calls Animal's version — because static methods belong to the class, not the object. Static methods are NOT polymorphic. Common interview trap: `Parent p = new Child(); p.greet()` where both have `static void greet()` → prints "Parent" (reference type decides). The `@Override` annotation on a static method is a compile error — static methods can be hidden but never overridden.</details>

## Dependency Inversion Principle (DIP)

104. What does the Dependency Inversion Principle state and what does "inversion" mean?

<details><summary>Answer</summary>DIP has two rules (Robert C. Martin): (1) **High-level modules should not depend on low-level modules — both should depend on abstractions**. (2) **Abstractions should not depend on details — details (concrete implementations) should depend on abstractions**. The **"inversion"** refers to the direction of dependency. Before DIP: `EmailService` depends directly on `GmailClient` (high → low). After DIP: `EmailService` depends on `EmailClient` interface, and `GmailClientImpl` also depends on `EmailClient` — both depend on the abstraction. The control flow still goes from EmailService to the implementation, but the **source code dependency is inverted**: the high-level module now defines the contract, and low-level modules fulfill it.</details>

105. Explain the tightly coupled `EmailService` problem and why switching providers is painful without DIP.

<details><summary>Answer</summary>The problem: `EmailService` hardcodes `private GmailClient gmailClient = new GmailClient()` and calls `gmailClient.sendGmail(...)`. To switch to Outlook, you must: rewrite `EmailService`, replace every method call, change the constructor, and if you need multiple providers (Gmail + Outlook + SES), `EmailService` becomes a giant `if-else` chain. Every provider change touches business logic. Without DIP, `EmailService` (a high-level business logic module) is directly coupled to `GmailClient` (a low-level implementation detail). Any change to Gmail's API forces changes in the business logic class — the exact coupling that makes codebases fragile and expensive to maintain.</details>

106. Walk through the DIP refactoring steps for the `EmailService` example.

<details><summary>Answer</summary>(1) **Define the abstraction**: `interface EmailClient { void sendEmail(String to, String subject, String body); }` — the contract both sides depend on. (2) **Implement concrete classes**: `GmailClientImpl implements EmailClient`, `OutlookClientImpl implements EmailClient` — each knows only its own provider details. (3) **Update high-level module**: `EmailService` takes `EmailClient` in its constructor — it depends only on the interface, knows nothing about Gmail or Outlook. (4) **Wire at composition root** (e.g., `main()`): `new EmailService(new GmailClientImpl())` or `new EmailService(new OutlookClientImpl())`. Switching providers = zero changes to `EmailService`, just a different object at the injection point. Adding AWS SES = one new class implementing `EmailClient`, ready immediately.</details>

107. What is the difference between Dependency Inversion (DIP), Dependency Injection (DI), and Inversion of Control (IoC)?

<details><summary>Answer</summary>**DIP** (principle): "Depend on abstractions, not concrete implementations." Defines the rule. **DI** (technique): a class receives its dependencies from the outside (constructor, setter, or method) instead of creating them. DI is the most common way to achieve DIP. But you can use DI without DIP (e.g., injecting a concrete class, not an interface). **IoC** (broader concept): the flow of control is inverted — instead of your code calling a framework, the framework calls your code (e.g., Spring controlling object lifecycle). DIP is one specific way to achieve IoC. Think of it as: IoC is the big idea → DI is a pattern implementing it → DIP is the principle guiding what to inject.</details>

108. What are the five benefits of following DIP?

<details><summary>Answer</summary>(1) **Decoupling** — business logic is independent of implementation details (switch Gmail to Outlook without touching `EmailService`). (2) **Flexibility & extensibility** — add Amazon SES by creating one new class; no existing code changes. (3) **Testability** — inject a mock `EmailClient` in tests without hitting real SMTP servers. (4) **Maintainability** — changes in `GmailClientImpl` stay isolated; as long as `EmailClient` interface is unchanged, `EmailService` is unaffected. (5) **Parallel development** — once the interface is defined, one team builds `EmailService` while another builds provider implementations independently.</details>

109. What are the four common DIP pitfalls to avoid?

<details><summary>Answer</summary>(1) **Over-abstraction** — creating interfaces for everything, even stable internal utilities. Only abstract when there are multiple implementations, external dependencies, or testing needs. (2) **Leaky abstractions** — adding provider-specific methods to the interface (e.g., `configureGmailSpecificSetting()` in `EmailClient`) defeats the purpose. (3) **Interfaces owned by low-level modules** — if `GmailClient` defines `IGmailClient` and `EmailService` depends on it, `EmailService` is still tied to Gmail. The interface should be owned by the high-level module or a neutral shared module. (4) **No actual injection** — depending on the interface but still doing `this.emailClient = new GmailClient()` inside the class. The dependency must come from the outside.</details>

110. Where should interface abstractions live in a project, and who "owns" them?

<details><summary>Answer</summary>The **high-level module** (the client/consumer) should define and own the interface — it declares what it needs. Example: `EmailClient` interface lives in the same package/module as `EmailService`, not inside `GmailClient`'s package. In large codebases, interfaces may live in a shared `contracts`, `api`, or `ports` module (common in hexagonal/ports-and-adapters architecture). The key rule: **the high-level module should not depend on anything in the low-level module's territory**. If `EmailService` had to import from `com.gmail.client.IGmailClient`, it's still coupled to Gmail's namespace and structure — which defeats the inversion.</details>

## Interface Segregation Principle (ISP)

111. What does the Interface Segregation Principle state and what problem does it solve?

<details><summary>Answer</summary>ISP states: **"Clients should not be forced to depend on methods they do not use."** It solves the **fat interface** problem — when a single interface combines multiple responsibilities, classes implementing it must provide empty no-ops or throw `UnsupportedOperationException` for methods they don't support. Example: `AudioOnlyPlayer implements MediaPlayer` where `MediaPlayer` has both audio and video methods — `AudioOnlyPlayer` is forced to implement `playVideo()`, `displaySubtitles()` etc., throwing exceptions for each. This is interface pollution: the class carries the weight of unrelated functionality it never uses.</details>

112. What are the three problems with a "fat" interface like the original `MediaPlayer`?

<details><summary>Answer</summary>(1) **Interface pollution** — `AudioOnlyPlayer` must implement 7 methods when it only needs 3. Any new method added to `MediaPlayer` (e.g., `enablePictureInPicture()`) forces updates in all implementations, including unrelated ones. (2) **Fragile code** — one interface change ripples across all implementing classes. The more methods an interface has, the more likely a change breaks unrelated classes. (3) **LSP violation** — a client expecting any `MediaPlayer` to support video will get `UnsupportedOperationException` from `AudioOnlyPlayer`. Subtypes that throw exceptions for inherited methods violate LSP. The interface becomes an unreliable contract.</details>

113. Walk through the ISP refactoring of the `MediaPlayer` example.

<details><summary>Answer</summary>**Before**: one fat `MediaPlayer` interface with 7 methods (3 audio + 4 video). **After ISP**: (1) Split into `AudioPlayerControls` (`playAudio()`, `stopAudio()`, `adjustAudioVolume()`) and `VideoPlayerControls` (`playVideo()`, `stopVideo()`, `adjustVideoBrightness()`, `displaySubtitles()`). (2) `ModernAudioPlayer implements AudioPlayerControls` — only 3 methods, no video stubs. (3) `SilentVideoPlayer implements VideoPlayerControls` — only 4 methods, no audio stubs. (4) `ComprehensiveMediaPlayer implements AudioPlayerControls, VideoPlayerControls` — opts into both. Each class implements **only the interfaces it can fully honor** — no empty methods, no exceptions, no wasted code. The interfaces are small, focused, and composable.</details>

114. What are the five benefits of applying ISP?

<details><summary>Answer</summary>(1) **Increased cohesion, reduced coupling** — `AudioOnlyPlayer` only knows about audio methods; unrelated dependencies are eliminated. (2) **Improved flexibility & reusability** — small, role-specific interfaces are composable: `ComprehensiveMediaPlayer` opts into both audio and video by implementing two small interfaces. (3) **Better readability** — implemented interfaces clearly communicate a class's capabilities; no guessing which methods actually do something vs. throw exceptions. (4) **Enhanced testability** — mocking `AudioPlayerControls` only requires 3 methods instead of 7; tests are focused and minimal. (5) **Avoids LSP violations** — classes never implement methods they don't support, so `UnsupportedOperationException` surprises are eliminated.</details>

115. What is "interface-itis" (over-segregation) and how do you avoid it?

<details><summary>Answer</summary>**Interface-itis** is creating a separate interface for every single method: `Playable`, `Stoppable`, `AdjustableVolume` — making navigation through the codebase as painful as a single fat interface. **How to avoid it**: group methods by **logical roles or capabilities** that naturally belong together. `playAudio()`, `stopAudio()`, and `adjustAudioVolume()` represent one cohesive role — controlling audio playback — so they belong in one interface. **Rule of thumb**: design interfaces from the **client's perspective** — ask "what is the minimal set of methods this caller actually needs?" not "how many individual methods can I extract?" An interface should represent a single, well-defined role, not an arbitrary split of methods.</details>

116. How does ISP relate to LSP, and why do fat interfaces often lead to LSP violations?

<details><summary>Answer</summary>ISP and LSP are complementary: **ISP ensures interfaces are minimal and relevant; LSP ensures implementations honor those contracts completely**. Fat interfaces (ISP violation) directly cause LSP violations: when `AudioOnlyPlayer` is forced to implement video methods, it throws `UnsupportedOperationException`. A client expecting any `MediaPlayer` to support video gets a crash — the subtype broke the base type's contract (LSP violation). The chain: fat interface → forced implementation of irrelevant methods → empty stubs or exceptions → unreliable substitution → LSP broken. Applying ISP prevents this chain: if `AudioOnlyPlayer` only implements `AudioPlayerControls`, it can never be passed to code expecting `VideoPlayerControls`. The type system enforces correctness at compile time.</details>

## Liskov Substitution Principle (LSP)

117. What does the Liskov Substitution Principle state, and what is its core promise?

<details><summary>Answer</summary>LSP (Barbara Liskov, 1987): **"If S is a subtype of T, then objects of type T may be replaced with objects of type S without altering any of the desirable properties of the program."** In plain terms: you should be able to use any subclass anywhere the parent class is expected, and the program must still behave correctly — no crashes, no exceptions, no unexpected behavior. The core promise is **reliable substitution**: client code doesn't need to know the exact subtype it's dealing with. If a method accepts `Document`, it must work correctly with any `Document` subclass. LSP is what makes runtime polymorphism trustworthy.</details>

118. Explain the `ReadOnlyDocument` LSP violation — what went wrong and why?

<details><summary>Answer</summary>`Document` has a `save()` method, implying all documents are saveable. `ReadOnlyDocument extends Document` and overrides `save()` to throw `UnsupportedOperationException`. `DocumentProcessor.processAndSave(Document doc)` assumes any `Document` can be saved — a reasonable assumption given the contract. When a `ReadOnlyDocument` is passed, it crashes at runtime with `UnsupportedOperationException`. **What went wrong**: the base class (`Document`) established a contract that all documents are saveable. `ReadOnlyDocument` broke that contract by overriding a method to throw an exception. **The tell-tale sign**: if you find yourself overriding a method just to throw an exception or do nothing, the subclass is likely not a valid subtype — it's an LSP violation.</details>

119. How was the document system refactored to comply with LSP?

<details><summary>Answer</summary>(1) **Define behavior interfaces**: `interface Document { void open(); String getData(); }` (read-only capability) and `interface Editable extends Document { void save(String newData); }` (adds write capability). (2) `EditableDocument implements Editable` — honors both reading and writing. (3) `ReadOnlyDocument implements Document` — only implements `open()` and `getData()`. It never promises `save()`, so it can never break that contract. (4) `DocumentProcessor` has `process(Document doc)` for read-only use, and `processAndSave(Editable doc, ...)` for editable use. **Key result**: passing a `ReadOnlyDocument` to `processAndSave()` is a **compile-time error** — the type system prevents violations before the program even runs, instead of runtime crashes.</details>

120. What are the five common LSP pitfalls to avoid?

<details><summary>Answer</summary>(1) **The "is-a" linguistic trap** — a penguin is a bird biologically, but if `Bird.fly()` exists and `Penguin` throws an exception, LSP is violated. Subtyping must be based on **behavior**, not taxonomy. (2) **Overriding methods to throw exceptions** — `throw new UnsupportedOperationException()` in an override is almost always an LSP violation. (3) **Precondition violations** — subclass requires more than base class promised (base accepts any positive number; subclass requires > 100). (4) **Postcondition violations** — subclass delivers less than base class guaranteed (base guarantees non-null; subclass returns null). (5) **`instanceof` checks in client code** — `if (doc instanceof ReadOnlyDocument)` signals broken polymorphism. Client code should never need to know the exact subtype.</details>

121. What five benefits does LSP provide when followed correctly?

<details><summary>Answer</summary>(1) **Reliability & predictability** — any subtype can be substituted without surprising behavior; code behaves consistently regardless of which concrete type is used. (2) **Reduced bugs** — no `instanceof` checks or special-case logic scattered in client code. (3) **Maintainability & extensibility** — well-behaved hierarchies let you add new subtypes without fear of breaking existing code. (4) **True polymorphism** — generic algorithms operating on a base type work correctly with all current and future subtypes — the foundation of scalable OOP design. (5) **Testability** — tests written for the base class interface pass for all subtypes (Liskov test suites). If LSP holds, base-class tests are automatically valid for every subclass.</details>

## Single Responsibility Principle (SRP)

122. What does the Single Responsibility Principle state, and what is a "reason to change"?

<details><summary>Answer</summary>SRP (Robert C. Martin): **"A class should have one, and only one, reason to change."** A **reason to change** is not a method or a function — it is a distinct business logic or technical concern that might require the class to be modified. Ask: "How many different forces could cause this class to change in the future?" If the answer is more than one, the class likely breaks SRP. Example: a `UserService` that hashes passwords, saves to DB, generates tokens, and sends emails has **four** reasons to change. Each responsibility is a separate reason: password algorithm change, DB schema change, token format change, email provider change — all unrelated forces that should not be coupled in one class.</details>

123. What is a "God Class" and why is it a problem?

<details><summary>Answer</summary>A **God Class** is a class that tries to do everything — it accumulates multiple unrelated responsibilities. Example: `UserService` that validates/hashes passwords, saves to database, generates auth tokens, and sends welcome emails. Problems: (1) **Hard to read** — you must scroll through hundreds of lines to find one method. (2) **Fragile** — a change to email logic can accidentally break password hashing. (3) **Impossible to test in isolation** — testing password hashing requires a database connection and email server. (4) **No reuse** — you can't use the auth token generator without pulling in the entire registration flow. (5) **Team conflicts** — multiple developers changing the same class for unrelated reasons constantly create merge conflicts.</details>

124. Walk through the SRP refactoring of `UserService` — what classes are extracted and why?

<details><summary>Answer</summary>The `UserService` god class is split into five focused classes: (1) **`User`** — pure data class representing a user (username, email, password). Reason to change: domain model evolves. (2) **`PasswordHasher`** — validates and hashes passwords. Reason to change: hashing algorithm changes (bcrypt → argon2). (3) **`UserRepository`** — saves user to database. Reason to change: database technology changes (JDBC → JPA, SQL → NoSQL). (4) **`AuthTokenService`** — generates JWT tokens. Reason to change: token format changes (JWT → opaque tokens). (5) **`EmailService`** — sends welcome email. Reason to change: email provider changes (SMTP → SendGrid). Each class now has exactly one reason to change, and changes in one class don't ripple into unrelated others.</details>

125. What are the five benefits of following SRP?

<details><summary>Answer</summary>(1) **Easier to read** — each class has a clear, single purpose; no scrolling through unrelated methods. (2) **Easier to test** — `PasswordHasher` tests don't need a database or email server; dependencies are minimal. (3) **Less brittle** — changing the email provider doesn't risk breaking password hashing. (4) **Easier to reuse** — `AuthTokenService` can serve a web app and a mobile API independently. (5) **Scales better** — teams can own different classes (database team owns `UserRepository`, platform team owns `AuthTokenService`) without merge conflicts. These benefits compound: a SRP-compliant codebase is dramatically easier to extend 6 months later than one full of God Classes.</details>

126. What are the four common SRP pitfalls to avoid?

<details><summary>Answer</summary>(1) **Over-splitting** — creating `PasswordValidator`, `SaltGenerator`, `BcryptEncoder`, `HashAggregator` when a single `PasswordHasher` suffices. Focus on cohesion: group logic that changes together. (2) **Confusing methods with responsibilities** — `EmailService` with `sendWelcomeEmail()` and `sendPasswordResetEmail()` is fine; both serve the same responsibility (sending emails). Don't split just because there are multiple methods. (3) **Ignoring SRP in small/utility classes** — `ReportUtils` with `generateCSV()`, `sendReportEmail()`, `archiveReport()` seems small but will grow. Apply SRP early. (4) **Misunderstanding "reason to change"** — it's not about who requests the change but what kind of change it is. Password hashing and DB persistence are two different concerns even if one product manager requests both.</details>

127. Does SRP apply beyond classes? Give examples at different levels.

<details><summary>Answer</summary>Yes — SRP is a mindset applicable at every level: **Method** — a method should do one thing. `validateAndSave()` breaks SRP; split into `validate()` and `save()`. **Class** — one reason to change (covered above). **Module** — a module should encapsulate one area of functionality (e.g., a `payments` module shouldn't contain user authentication logic). **Service/Microservice** — each service owns a single business domain (Order Service, Payment Service, Notification Service). **System** — large systems are organized around clear bounded contexts. The guiding test at all levels: if you need the word "and" or "or" to describe what something does, it likely has more than one responsibility.</details>

## Realization (Interface Implementation) — Deep Dive

128. What is the difference between realization and inheritance in UML and code?

<details><summary>Answer</summary>**Inheritance (Generalization)** — solid line with hollow triangle (—▷). Models **identity**: "A Dog IS an Animal." The child inherits state (fields) and behavior (methods) from the parent. Use when there's a true taxonomic/IS-A relationship with shared implementation. **Realization** — dashed line with hollow triangle (- -▷). Models **capability**: "A Bird CAN fly, and so can an Airplane." The implementing classes share what they can do, not what they are. No state is inherited — each class provides its own implementation from scratch. A Bird and Airplane have nothing structurally in common except the `Flyable` contract. Key test: if you're sharing code → inheritance. If you're sharing a contract across unrelated things → realization.</details>

129. Why does the `Flyable` example demonstrate realization better than inheritance?

<details><summary>Answer</summary>`Bird`, `Airplane`, and `Drone` share the `Flyable` interface but have **completely unrelated internal structures**: `Bird` has `species` and `wingSpan`; `Airplane` has `model` and `maxAltitude`; `Drone` has `batteryLevel` and `maxRange`. They share zero fields, zero common behavior, and no parent class. Realization is appropriate here because these classes share a **capability** (flight), not an **identity** (type of animal or type of machine). If `Flyable` were a base class, you'd have a nonsensical hierarchy where Airplane extends Bird or some artificial `FlyingThing` class. The interface lets them be completely independent while still being usable through the same contract: `List<Flyable>` works for all three.</details>

130. What are the four key things that make the `Flyable` code pure realization?

<details><summary>Answer</summary>(1) **Interface defines contract, not implementation** — `Flyable` declares `fly()` and `getFlightInfo()` but provides zero code. Each class writes its own version from scratch (unlike inheritance where the child gets parent code for free). (2) **Implementing classes are completely unrelated** — `Bird`, `Airplane`, `Drone` share no parent class, no common fields, no shared behavior. (3) **Calling code depends only on the interface** — `main()` works with `List<Flyable>` without knowing or caring about the actual types in the list. (4) **Adding a new implementer requires zero changes to existing code** — adding `Helicopter implements Flyable` just works; no existing class is modified. This is the Open/Closed Principle in action through realization.</details>

131. When should you use both inheritance AND realization together?

<details><summary>Answer</summary>Many real designs combine both. Example: `Car extends Vehicle` (inheritance — IS-A, shares common vehicle state/behavior like `fuelLevel`, `startEngine()`) while also `implements Drivable, Insurable, Parkable` (realization — CAN-DO capabilities shared across unrelated types). `FileHandler implements Readable, Writable, Closeable` — three focused interfaces each representing a single capability. A method that only needs to read files accepts `Readable`; one that needs to close resources accepts `Closeable`. The caller doesn't know it's dealing with a `FileHandler`. Rule: use inheritance for IS-A family hierarchies with shared implementation; use realization for CAN-DO capabilities that unrelated classes share. When a class has both a family identity and multiple capabilities, use both.</details>

132. What is the advantage of multiple interface implementation (realization) over multiple class inheritance?

<details><summary>Answer</summary>Java allows a class to implement multiple interfaces (multiple realization) but extend only one class (single inheritance). This avoids the **Diamond Problem** while still enabling a class to fulfill multiple contracts. Example: `class FullMediaPlayer implements AudioPlayerControls, VideoPlayerControls` — opts into both capabilities cleanly. With multiple class inheritance (C++), if both parents define the same method, the compiler doesn't know which to use. With interfaces, if two interfaces define the same default method, the compiler requires the class to explicitly override it — making the resolution clear and intentional. Multiple realization gives you **composable capabilities** without the ambiguity of multiple inheritance.</details>

## Dependency (OOP Relationship)

133. What is a Dependency relationship in OOP and what makes it the weakest relationship type?

<details><summary>Answer</summary>**Dependency** is when one class temporarily uses another to fulfill a responsibility, **without retaining a permanent reference to it**. It's the weakest relationship because: (1) **Short-lived** — exists only during method execution, not as a stored field. (2) **No ownership** — the dependent class doesn't manage the lifecycle of the other. (3) **"Uses-a" not "has-a"** — the class uses another to accomplish a task, then lets it go. UML notation: dashed arrow (- - →) from dependent to used class. Chef analogy: a chef picks up a knife to chop vegetables, then puts it down. The chef doesn't own the knife or keep it stored. If `Printer` stored `private Document lastPrinted`, it would become an **association**; storing as a field = persistent structural link.</details>

134. What are the four forms dependency can appear in code? Give examples of each.

<details><summary>Answer</summary>(1) **Method parameter** (most common): `void print(Document doc)` — `Printer` uses `Document` during the method, releases it when done. (2) **Local variable**: `JsonFormatter formatter = new JsonFormatter();` inside `process()` — created, used, and discarded within the method scope; never stored as a field. (3) **Return type**: `public User createUser(String name, String email) { return new User(name, email); }` — `UserFactory` depends on `User` because it creates and returns them, but stores none as a field. (4) **Static method call**: `HashUtils.sha256(input)` in `PasswordService.verify()` — no instance of `HashUtils` is ever stored; dependency is at the class level through a static call. All four forms share the key characteristic: no persistent field reference to the used class.</details>

135. How is a dependency different from an association?

<details><summary>Answer</summary>The key difference is **whether the reference is stored as a field**: **Dependency** — used temporarily in a method (parameter, local variable, return type, static call). No field. Relationship exists only during method execution. Lower coupling. UML: dashed arrow (- - →). Example: `Printer.print(Document doc)` — Document is a parameter. **Association** — stored as an instance field for long-term use. Higher coupling. UML: solid arrow (→). Example: `class OrderService { private PaymentGateway gateway; }` — gateway is a field retained across multiple method calls. **One-line test**: if you remove all fields from a class and the relationship disappears, it was an association. If the relationship was only in method signatures, it was a dependency.</details>

136. What is Dependency Injection (DI) and why is it better than a class creating its own dependencies?

<details><summary>Answer</summary>**Dependency Injection** means a class receives its dependencies from the outside rather than creating them internally. **Without DI**: `NotificationService` does `this.sender = new EmailSender()` in its constructor — tightly coupled to `EmailSender`. Can't switch to SMS, can't mock in tests without modifying the class. **With DI**: `NotificationService(Sender sender)` — takes a `Sender` interface via constructor. In production: `new NotificationService(new EmailSender())`. In tests: `new NotificationService(new MockSender())`. **Three concrete benefits**: (1) **Swappable implementations** — pass `SmsSender`, `PushSender`, or any future `Sender` without touching `NotificationService`. (2) **Easy testing** — inject a mock that records messages instead of sending real emails. (3) **Loose coupling** — `NotificationService` depends on the `Sender` interface, not on any concrete class.</details>

137. What are the three problems with a class that creates its own dependencies (without DI)?

<details><summary>Answer</summary>(1) **Can't switch implementations** — `NotificationService` hardcoding `new EmailSender()` means you must modify the class to switch to SMS. Violates OCP. (2) **Can't test in isolation** — unit tests will actually send real emails (or fail) because there's no way to inject a mock. Tests become slow, flaky, and side-effect-prone. (3) **Violates Open/Closed Principle** — adding a new notification channel requires editing the existing `NotificationService` class rather than simply providing a new implementation of `Sender`. The class is closed for extension and open for modification — the opposite of what OCP requires.</details>

138. Explain the `TicketBookingService` dependency example — what makes it pure dependency with no structural coupling?

<details><summary>Answer</summary>`TicketBookingService` has **zero fields**. Every collaborator — `SeatValidator`, `PaymentProcessor`, `QRCodeGenerator`, `EmailService` — is received as a **method parameter** to `bookTicket()` and released when the method returns. Pure dependency characteristics: (1) No fields = no structural coupling. (2) All dependencies are created externally and passed in. (3) The booking service just coordinates the flow — each class has a single responsibility. (4) **Testing**: pass mock `PaymentProcessor` returning `false` to test payment failure path — zero real services needed. (5) **Swapping**: replace `EmailService` parameter with `SmsService` without changing `TicketBookingService`. If any of these were stored as fields, they'd become associations — a different (stronger) relationship.</details>

139. What is the difference between Dependency Injection (DI) and the Dependency Inversion Principle (DIP)?

<details><summary>Answer</summary>**DIP** (principle): "High-level modules should not depend on low-level modules — both should depend on abstractions." Defines the design rule. **DI** (technique): inject dependencies from the outside instead of creating them internally. DI is the most common way to achieve DIP. **Key distinction**: you can use DI without DIP — e.g., injecting a concrete `EmailSender` class (not an interface) into `NotificationService`. The injection happens, but `NotificationService` is still coupled to the concrete class, so DIP is violated. DIP requires the dependency to be typed as an **interface or abstraction**, not a concrete class. You can also follow DIP without a formal DI mechanism — e.g., a factory method providing the abstraction. Both are needed for maximum flexibility: DI provides the mechanism, DIP provides the principle.</details>

140. How does Dependency Injection relate to Inversion of Control (IoC)?

<details><summary>Answer</summary>**IoC** (broad concept): the "control" of object creation and lifecycle is inverted — instead of your code instantiating dependencies, a framework or container does it for you. **DI** (specific pattern): one way to implement IoC — dependencies are injected rather than created. When Spring initializes your application, it reads annotations (`@Autowired`, `@Bean`), creates all objects, and injects them automatically — you don't call `new` anywhere in your business code. The container (Spring) has control. **Analogy**: IoC = "don't call us, we'll call you." Your code defines what it needs; the framework provides it. DI is one specific manifestation of this — the framework injects dependencies. DIP is the design principle saying what those dependencies should be typed as (abstractions, not concretes).</details>

141. Compare all five OOP relationship types by strength and how to identify them in code.

<details><summary>Answer</summary>

| Relationship | Strength | How to Identify in Code | UML | Example |
|---|---|---|---|---|
| **Dependency** | Weakest | Method parameter, local variable, return type, static call — no field | Dashed arrow (- - →) | `void print(Document d)` |
| **Association** | Weak | Instance field; both objects independent lifecycle | Solid arrow (→) | `class Student { Course course; }` |
| **Aggregation** | Medium | Instance field, passed in from outside; part survives if whole dies | Empty diamond (◇→) | `Department(List<Professor> profs)` |
| **Composition** | Strong | Instance field, created inside; part dies with whole | Filled diamond (◆→) | `House() { rooms.add(new Room()); }` |
| **Generalization** | Strongest | `extends` keyword | Solid + hollow triangle (—▷) | `Dog extends Animal` |
| **Realization** | Strong | `implements` keyword | Dashed + hollow triangle (- -▷) | `Stripe implements PaymentGateway` |

**Quick decision guide**: temporary use in a method → dependency. Long-term field, parts independent → association/aggregation. Long-term field, parts owned → composition. IS-A → generalization. CAN-DO contract → realization.</details>

142. What are the practical benefits of using the Dependency relationship (passing objects as parameters) over storing them as fields?

<details><summary>Answer</summary>(1) **Lower coupling** — the class has no structural dependency on the other; removing the method removes the relationship entirely. (2) **Testability** — every caller decides which implementation to pass; tests can inject mocks directly at the call site without any constructor wiring. (3) **Statelessness** — classes with no fields are inherently thread-safe; multiple threads can call the same method simultaneously without shared mutable state. (4) **Explicit dependencies** — method signatures document all required inputs; nothing is hidden in fields. (5) **Flexibility** — the same class can work with different implementations on different calls: `bookingService.bookTicket(..., new StripeProcessor(), ...)` or `bookingService.bookTicket(..., new PayPalProcessor(), ...)`. The trade-off: passing many parameters is unwieldy (see `TicketBookingService.bookTicket()` with 8 parameters) — this is a signal to consider constructor injection or a request object pattern.</details>

143. Name all the core OOP concepts and give a one-line description of each.

<details><summary>Answer</summary>

**Four Pillars:**
| Concept | One-line Description |
|---|---|
| **Encapsulation** | Bundle data + behavior in a class; hide internal state; expose only controlled public methods |
| **Abstraction** | Hide implementation complexity; show only the essential high-level interface to the caller |
| **Inheritance** | A subclass inherits fields and methods from a parent (IS-A), enabling hierarchy and code reuse |
| **Polymorphism** | Same method name, different behavior — overloading at compile time, overriding at runtime |

**Building Blocks:**
| Concept | One-line Description |
|---|---|
| **Class** | Blueprint/template defining the structure and behavior of objects |
| **Object** | A runtime instance of a class with its own state |
| **Interface** | A contract declaring what methods must exist, with no implementation |
| **Abstract Class** | Partial blueprint — can mix abstract (unimplemented) and concrete (shared) methods |
| **Enum** | A type-safe named constant set; can carry fields and methods |

**OOP Relationships:**
| Concept | One-line Description |
|---|---|
| **Association** | A class holds a reference to another as a field; independent lifecycles |
| **Aggregation** | Weak HAS-A: part is passed in from outside, can outlive the whole (◇) |
| **Composition** | Strong HAS-A: part is created inside and dies with the whole (◆) |
| **Dependency** | Temporary USES-A: one class uses another as a method parameter/local var — no field stored |
| **Generalization** | IS-A: subclass `extends` parent, inheriting state and behavior |
| **Realization** | CAN-DO: class `implements` an interface contract, providing its own implementation |

**Design Principles (SOLID):**
| Concept | One-line Description |
|---|---|
| **SRP** | One class, one reason to change |
| **OCP** | Open for extension, closed for modification |
| **LSP** | Subtypes must be fully substitutable for their base types |
| **ISP** | Clients should not depend on methods they don't use — keep interfaces focused |
| **DIP** | Both high-level and low-level modules should depend on abstractions, not each other |

**Key Mechanisms:**
| Concept | One-line Description |
|---|---|
| **Cohesion** | How closely related a class's responsibilities are (aim for high/functional cohesion) |
| **Coupling** | How much classes depend on each other (aim for low/data coupling) |
| **Dependency Injection** | Receive dependencies from outside rather than creating them internally |
| **Method Overloading** | Same method name, different parameter lists — resolved at compile time |
| **Method Overriding** | Subclass replaces a parent method with its own implementation — resolved at runtime |</details>
