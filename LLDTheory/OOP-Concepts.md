# Object-Oriented Programming (OOP) — Complete Theory

---

## 1. What is OOP?

**Object-Oriented Programming** is a programming paradigm that organizes software design around **objects** — instances of classes that bundle **data** (fields/attributes) and **behavior** (methods) together. Instead of writing a sequence of instructions, you model the problem as interacting objects.

### 1.1 OOP and the Real World — Analogy

OOP mirrors how we think about the real world:

| Real World | OOP Concept |
|---|---|
| Blueprint of a car | **Class** (template) |
| Your actual car | **Object** (instance) |
| Car's color, fuel level, speed | **Attributes** (fields) |
| Accelerate, brake, turn | **Methods** (behavior) |
| Car's engine is hidden under the hood | **Encapsulation** (hide internals) |
| You just press the accelerator, don't know how the engine works | **Abstraction** (hide complexity) |
| A sports car IS-A car, inherits all car properties | **Inheritance** |
| Same "start" button works differently in petrol vs diesel car | **Polymorphism** |

**Analogy — Online Food Ordering:**
```
Class: Restaurant
  - Attributes: name, cuisine, rating
  - Methods: acceptOrder(), prepareFood(), deliverOrder()

Class: Customer
  - Attributes: name, address, orderHistory
  - Methods: placeOrder(), makePayment(), rateRestaurant()

Class: DeliveryPerson
  - Attributes: name, currentLocation, vehicle
  - Methods: pickUpOrder(), deliverOrder(), updateLocation()

Objects:
  - Restaurant dominos = new Restaurant("Domino's", "Pizza", 4.5)
  - Customer alice = new Customer("Alice", "MG Road")
  - DeliveryPerson raj = new DeliveryPerson("Raj", "Bike")
```

### 1.2 Procedural vs Object-Oriented Programming

| Feature | Procedural (C) | OOP (Java) |
|---|---|---|
| Approach | Top-down, step-by-step | Model real-world entities as objects |
| Data | Global, shared across functions | Encapsulated inside objects |
| Reusability | Functions | Classes + Inheritance |
| Security | No data hiding | Access modifiers (`private`, `protected`) |
| Example | `calculateSalary(employee)` | `employee.calculateSalary()` |
| Modification | Changing one function can break others | Changes are localized to the class |

---

## 2. Class vs Object

| Class | Object |
|---|---|
| **Blueprint** / template | **Instance** of a class |
| Defines structure and behavior | Has actual data and occupies memory |
| Declared once | Created multiple times |
| No memory allocated until instantiated | Memory allocated on `new` |
| Example: `class Car { }` | Example: `Car myCar = new Car();` |

```java
// Class = Blueprint
class Student {
    String name;
    int rollNo;

    void study() {
        System.out.println(name + " is studying");
    }
}

// Object = Instance
Student s1 = new Student(); // Object 1
Student s2 = new Student(); // Object 2 — different memory, different state

s1.name = "Alice";
s2.name = "Bob";
s1.study(); // Alice is studying
s2.study(); // Bob is studying
```

**What happens during `new Student()`?**
1. Memory is allocated on the **heap** for the object.
2. Instance variables are initialized to **default values** (`null`, `0`, `false`).
3. The **constructor** runs.
4. A **reference** to the object is returned and stored in the variable.

---

## 3. Access Modifiers

Access modifiers control **visibility** of classes, fields, methods, and constructors.

| Modifier | Same Class | Same Package | Subclass (diff pkg) | World |
|---|---|---|---|---|
| `private` | ✅ | ❌ | ❌ | ❌ |
| (default / package-private) | ✅ | ✅ | ❌ | ❌ |
| `protected` | ✅ | ✅ | ✅ | ❌ |
| `public` | ✅ | ✅ | ✅ | ✅ |

```java
package com.example;

public class Account {
    private   double balance;    // Only this class
              String accountId;  // Default — same package only
    protected String owner;      // Same package + subclasses
    public    String bankName;   // Everyone

    private void deductFee() {
        balance -= 10;
    }

    public double getBalance() {
        return balance;  // Controlled access
    }
}
```

```java
package com.other;
import com.example.Account;

class SavingsAccount extends Account {
    void test() {
        System.out.println(bankName);  // ✅ public
        System.out.println(owner);     // ✅ protected (subclass)
        // System.out.println(accountId);  // ❌ default — different package
        // System.out.println(balance);    // ❌ private
        // deductFee();                    // ❌ private
    }
}
```

**Default access modifier for classes, methods, and variables:**
- **Top-level class**: If no modifier → **package-private** (accessible only within the same package).
- **Interface methods**: Implicitly `public abstract` (before Java 9).
- **Interface fields**: Implicitly `public static final`.
- **Enum constructors**: Implicitly `private`.

---

## 4. Member Functions (Methods)

A **member function** (method) is a function defined inside a class that operates on the object's data.

```java
class Circle {
    double radius;

    // Member function — operates on the object's state
    double area() {
        return Math.PI * radius * radius;
    }

    // Member function with parameters
    boolean isLargerThan(Circle other) {
        return this.area() > other.area();
    }
}

Circle c = new Circle();
c.radius = 5;
System.out.println(c.area()); // 78.539...
```

**Note:** In Java, all functions must be inside a class — there are no standalone functions. They are either:
- **Instance methods** — operate on object state, need an object to call.
- **Static methods** — belong to the class, don't need an object.

---

## 5. Constructors — Complete Theory

A **constructor** is a special method that is called **automatically** when an object is created. It initializes the object's state.

**Rules:**
- Same name as the class.
- No return type (not even `void`).
- Called automatically on `new`.
- Cannot be `abstract`, `static`, `final`, or `synchronized`.

### 5.1 Default Constructor

If you **don't define any constructor**, Java provides a **default no-arg constructor** that initializes fields to default values.

```java
class Car {
    String brand;
    int speed;
    // No constructor defined → Java provides default constructor
}

Car c = new Car(); // Default constructor called
// c.brand = null, c.speed = 0 (default values)
```

> **Important:** If you define **any** constructor, Java does **NOT** provide the default one. You must explicitly define a no-arg constructor if needed.

```java
class Car {
    String brand;
    Car(String brand) { this.brand = brand; }
}

// Car c = new Car(); // ❌ COMPILATION ERROR — no default constructor!
Car c = new Car("Toyota"); // ✅
```

### 5.2 Parameterized Constructor

Takes parameters to initialize the object with specific values.

```java
class Employee {
    String name;
    double salary;
    String department;

    // Parameterized constructor
    Employee(String name, double salary, String department) {
        this.name = name;         // 'this' disambiguates field vs parameter
        this.salary = salary;
        this.department = department;
    }
}

Employee emp = new Employee("Alice", 75000, "Engineering");
```

### 5.3 Constructor Overloading

Multiple constructors with **different parameter lists** — the correct one is chosen at compile time based on arguments.

```java
class Product {
    String name;
    double price;
    String category;

    // No-arg constructor
    Product() {
        this("Unknown", 0.0, "General");  // Chain to 3-arg constructor
    }

    // 2-arg constructor
    Product(String name, double price) {
        this(name, price, "General");     // Chain to 3-arg constructor
    }

    // 3-arg constructor (the main one)
    Product(String name, double price, String category) {
        this.name = name;
        this.price = price;
        this.category = category;
    }
}

Product p1 = new Product();                        // "Unknown", 0.0, "General"
Product p2 = new Product("Phone", 999);            // "Phone", 999.0, "General"
Product p3 = new Product("Laptop", 1500, "Electronics"); // "Laptop", 1500.0, "Electronics"
```

> **`this()` rule:** Must be the **first statement** in the constructor. A constructor cannot call both `this()` and `super()`.

### 5.4 Copy Constructor (Java Way)

Java does NOT have a built-in copy constructor like C++. You write it manually.

```java
class Address {
    String city;
    String state;

    Address(String city, String state) {
        this.city = city;
        this.state = state;
    }

    // Manual copy constructor
    Address(Address other) {
        this.city = other.city;
        this.state = other.state;
    }
}

Address a1 = new Address("Mumbai", "Maharashtra");
Address a2 = new Address(a1); // Copy

a2.city = "Pune";
System.out.println(a1.city); // "Mumbai" — a1 is NOT affected
```

### 5.5 Deep Copy vs Shallow Copy

**Shallow Copy:** Copies the reference (pointer) — both original and copy point to the **same** nested object.  
**Deep Copy:** Creates a **completely new copy** of all nested objects.

```java
class Engine {
    String type;
    Engine(String type) { this.type = type; }
}

class Car {
    String brand;
    Engine engine;   // Reference type — needs attention during copy

    Car(String brand, Engine engine) {
        this.brand = brand;
        this.engine = engine;
    }

    // ❌ SHALLOW COPY — engine is shared!
    Car shallowCopy() {
        return new Car(this.brand, this.engine);  // Same engine reference
    }

    // ✅ DEEP COPY — engine is fully duplicated
    Car deepCopy() {
        Engine engineCopy = new Engine(this.engine.type);  // New engine object
        return new Car(this.brand, engineCopy);
    }
}

Car original = new Car("BMW", new Engine("V8"));

// Shallow copy — changing engine affects original
Car shallow = original.shallowCopy();
shallow.engine.type = "V6";
System.out.println(original.engine.type); // "V6" ← AFFECTED! ❌

// Deep copy — changing engine does NOT affect original
Car deep = original.deepCopy();
deep.engine.type = "Electric";
System.out.println(original.engine.type); // "V6" ← NOT affected ✅
```

```
SHALLOW COPY:                          DEEP COPY:
original ──→ [brand:"BMW"]             original ──→ [brand:"BMW"]
              engine ──→ [type:"V8"]                 engine ──→ [type:"V8"]
shallow  ──→ [brand:"BMW"]             deep     ──→ [brand:"BMW"]
              engine ──↗ (SAME object)               engine ──→ [type:"V8"] (NEW object)
```

### 5.6 Copy Constructor vs Assignment (`=`)

```java
Car c1 = new Car("Toyota", new Engine("V4"));

// Assignment (=) — copies the REFERENCE, not the object
Car c2 = c1;          // c2 and c1 point to the SAME object
c2.brand = "Honda";
System.out.println(c1.brand); // "Honda" ← Both changed!

// Copy constructor — creates a NEW object
Car c3 = new Car(c1); // Different object, same values
c3.brand = "Ford";
System.out.println(c1.brand); // "Honda" ← NOT affected
```

### 5.7 Constructor vs Member Function

| Feature | Constructor | Member Function |
|---|---|---|
| Purpose | Initialize object state | Perform actions |
| Name | Same as class name | Any valid name |
| Return type | None (not even void) | Has a return type |
| Called | Automatically on `new` | Manually by programmer |
| Invocation | Only once per object creation | Multiple times |
| Inheritance | NOT inherited | Inherited |
| Can be called with `this()` | Yes (chaining) | Yes (via `this.method()`) |

---

## 6. No Destructors in Java — Garbage Collection

Java does **not have destructors**. Memory management is handled by the **Garbage Collector (GC)**, which automatically reclaims memory for objects that are no longer referenced.

### 6.1 How Garbage Collection Works

```java
void method() {
    Student s = new Student("Alice");  // Object created on heap
    s = null;  // Reference removed — object is now eligible for GC
    // OR
}  // 's' goes out of scope — object eligible for GC
```

**GC Eligibility:**
1. Setting reference to `null`: `s = null;`
2. Reassigning reference: `s = new Student("Bob");` (old object eligible)
3. Object created inside a method → eligible after method returns.
4. Anonymous objects: `new Student("Temp").getName();` (immediately eligible)

### 6.2 `finalize()` Method (Deprecated since Java 9)

`finalize()` was called by the GC **before** destroying an object. It was meant for cleanup (closing files, releasing resources).

```java
class DatabaseConnection {
    @Override
    protected void finalize() throws Throwable {
        System.out.println("Connection being freed by GC");
        // Close connection, release resources
        super.finalize();
    }
}
```

**Why `finalize()` is deprecated:**
- **Not guaranteed to run** — GC may never call it.
- **Unpredictable timing** — you don't know when GC runs.
- **Performance penalty** — objects with `finalize()` take longer to collect.
- **Resurrection risk** — object can make itself reachable again inside `finalize()`.

**Modern alternative — `try-with-resources` + `AutoCloseable`:**

```java
class DatabaseConnection implements AutoCloseable {
    @Override
    public void close() {
        System.out.println("Connection closed deterministically");
    }
}

// Resource is GUARANTEED to be closed
try (DatabaseConnection conn = new DatabaseConnection()) {
    // Use connection
}  // close() is called here — deterministic!
```

### 6.3 Key GC Concepts

| Concept | Description |
|---|---|
| **`System.gc()`** | Requests GC — but JVM can ignore it |
| **Heap** | Where all objects are stored |
| **Young Generation** | New objects; frequent GC (Minor GC) |
| **Old Generation** | Long-lived objects; less frequent GC (Major GC) |
| **Mark-and-Sweep** | GC algorithm — marks reachable objects, sweeps unreachable |
| **Stop-the-World** | GC pauses all threads during collection |
| **G1 GC** | Default GC in modern Java — balances throughput and latency |

---

## 7. The Four Pillars of OOP

### 7.1 Encapsulation

**Encapsulation** = **Data Hiding + Bundling**. It bundles data (fields) and methods that operate on that data into a single class, while restricting direct access to the data.

**How to achieve encapsulation:**
1. Declare fields as `private`.
2. Provide `public` getter/setter methods.
3. Add validation inside setters to enforce invariants.

**Real-world analogy:** A capsule medicine — you don't see the individual chemicals inside, you just take the capsule. The complexity is hidden.

```java
class BankAccount {
    private double balance;  // Data hiding
    private String owner;

    public BankAccount(String owner, double initialBalance) {
        this.owner = owner;
        if (initialBalance < 0) {
            throw new IllegalArgumentException("Balance cannot be negative");
        }
        this.balance = initialBalance;
    }

    // Controlled access via methods — with validation
    public void deposit(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("Deposit must be positive");
        this.balance += amount;
    }

    public void withdraw(double amount) {
        if (amount > balance) throw new IllegalArgumentException("Insufficient funds");
        this.balance -= amount;
    }

    public double getBalance() {
        return balance;  // Read-only access
    }

    // No setter for balance! — enforces invariant (balance changes only through deposit/withdraw)
}

BankAccount acc = new BankAccount("Alice", 1000);
acc.deposit(500);
acc.withdraw(200);
System.out.println(acc.getBalance()); // 1300.0
// acc.balance = -9999;  ← COMPILATION ERROR — data is hidden
```

**Advantages of Encapsulation:**
1. **Data protection** — prevent invalid state.
2. **Flexibility** — change internal implementation without affecting external code.
3. **Reusability** — self-contained units.
4. **Testability** — test behavior through public API.

**Encapsulation = Data Hiding + Abstraction combined.**

---

### 7.2 Abstraction

**Abstraction** = showing only **essential features** and hiding implementation details.

**Encapsulation vs Abstraction:**

| Encapsulation | Abstraction |
|---|---|
| **How** to hide (mechanism) | **What** to hide (concept) |
| Uses `private` + getters/setters | Uses abstract classes / interfaces |
| Hides **data** | Hides **implementation complexity** |
| Example: `private double balance;` | Example: `interface PaymentGateway { void pay(); }` |
| Implementation level | Design level |

**How to achieve abstraction in Java:**
1. **Abstract classes** (0-100% abstraction)
2. **Interfaces** (100% abstraction before Java 8; near-100% after Java 8 default methods)

**Real-world analogy:** ATM machine — you enter your PIN and amount, press "Withdraw". You don't know the internal process (verification, balance check, cash dispensing mechanism).

```java
// Abstraction: User knows WHAT, not HOW
abstract class PaymentProcessor {
    // Template method — defines the workflow
    public final void processPayment(double amount) {
        validate(amount);
        authenticate();
        executeTransaction(amount);
        sendReceipt();
    }

    private void validate(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("Invalid amount");
    }

    protected abstract void authenticate();            // HOW is hidden
    protected abstract void executeTransaction(double amount); // HOW is hidden

    private void sendReceipt() {
        System.out.println("Receipt sent.");
    }
}

class UPIProcessor extends PaymentProcessor {
    @Override
    protected void authenticate() {
        System.out.println("Authenticating via UPI PIN...");
    }

    @Override
    protected void executeTransaction(double amount) {
        System.out.println("Transferring ₹" + amount + " via UPI.");
    }
}

// Caller doesn't know HOW payment is processed — abstraction!
PaymentProcessor p = new UPIProcessor();
p.processPayment(500);
```

### Interface vs Abstract Class (When to Use What)

| Feature | Abstract Class | Interface |
|---|---|---|
| Constructor | ✅ | ❌ |
| Instance fields | ✅ | ❌ (only `public static final`) |
| Multiple inheritance | ❌ | ✅ |
| Access modifiers on methods | Any | `public` only |
| `default` methods | ❌ (use regular methods) | ✅ (Java 8+) |
| `private` methods | ✅ | ✅ (Java 9+) |
| Use case | Shared state + behavior among related classes | Contract / capability for unrelated classes |
| Relationship | IS-A (strong) | CAN-DO / HAS-BEHAVIOR |

**Rule of thumb:**
- Share **code** among related classes → **abstract class**.
- Define a **contract** for unrelated classes → **interface**.

```java
// Abstract class — shared state and code
abstract class Vehicle {
    String brand;
    int year;

    Vehicle(String brand, int year) { this.brand = brand; this.year = year; }

    void startEngine() { System.out.println(brand + " engine started."); }

    abstract double fuelEfficiency(); // Subclass-specific
}

// Interface — contract for a capability
interface Flyable {
    void fly();
    default void land() { System.out.println("Landing..."); }
}

interface Swimmable {
    void swim();
}

class Duck implements Flyable, Swimmable {
    @Override public void fly() { System.out.println("Duck flying!"); }
    @Override public void swim() { System.out.println("Duck swimming!"); }
}
```

**Can you create instances of an abstract class?**
No. `new Vehicle()` → compilation error. However, you can create **anonymous inner classes**:

```java
Vehicle v = new Vehicle("Test", 2024) {
    @Override
    double fuelEfficiency() { return 10.0; }
};
// This creates an anonymous subclass — NOT an instance of the abstract class itself
```

---

### 7.3 Inheritance

**Inheritance** is a mechanism where a child class derives properties and behavior from a parent class. It establishes an **IS-A** relationship and promotes **code reuse**.

**Types of Inheritance:**

```
1. Single:        A → B
2. Multilevel:    A → B → C
3. Hierarchical:  A → B, A → C, A → D
4. Multiple:      A → C, B → C  (NOT supported via classes in Java)
5. Hybrid:        Combination    (NOT supported via classes in Java)
```

```java
// Single Inheritance
class Animal {
    void eat() { System.out.println("Eating"); }
}
class Dog extends Animal {
    void bark() { System.out.println("Barking"); }
}

// Multilevel Inheritance
class Puppy extends Dog {
    void weep() { System.out.println("Weeping"); }
}
// Puppy has: eat() + bark() + weep()

// Hierarchical Inheritance
class Cat extends Animal {
    void meow() { System.out.println("Meowing"); }
}
// Both Dog and Cat inherit from Animal
```

### Why Java Doesn't Support Multiple Inheritance (via Classes)

The **Diamond Problem (Dreaded Diamond):**

```
       Animal
      /      \
  Flyer    Swimmer
      \      /
       Duck
```

If both `Flyer` and `Swimmer` override `Animal.eat()`, which version does `Duck` inherit? This ambiguity is the diamond problem.

**Java's solution:** Use **interfaces** for multiple inheritance.

```java
interface Flyable {
    default void move() { System.out.println("Flying"); }
}

interface Swimmable {
    default void move() { System.out.println("Swimming"); }
}

// Must resolve the conflict explicitly
class Duck implements Flyable, Swimmable {
    @Override
    public void move() {
        Flyable.super.move();    // Explicitly choose which default to call
        Swimmable.super.move();  // Or call both
    }
}

Duck d = new Duck();
d.move();
// Output:
// Flying
// Swimming
```

### What is Inherited from Parent Class?

| Inherited | Not Inherited |
|---|---|
| `public` methods | Constructors |
| `protected` methods | `private` methods |
| `public` fields | `private` fields |
| `protected` fields | Static methods (hidden, not overridden) |
| Default (package-private) — if same package | |

### Sealed Classes (Java 17+)

Java 17 introduced the `sealed` modifier — restricts which classes can extend a class.

```java
sealed class Shape permits Circle, Rectangle, Triangle {
    // Only Circle, Rectangle, and Triangle can extend Shape
}

final class Circle extends Shape { }       // final — cannot be further extended
non-sealed class Rectangle extends Shape { } // Can be extended by anyone
sealed class Triangle extends Shape permits RightTriangle { }

final class RightTriangle extends Triangle { }

// class Hexagon extends Shape { } // ❌ COMPILATION ERROR — not in permits list
```

### Does Overloading Work with Inheritance?

Yes. A subclass can **overload** a parent's method (same name, different parameters).

```java
class Printer {
    void print(String s) {
        System.out.println("String: " + s);
    }
}

class AdvancedPrinter extends Printer {
    // OVERLOADING — same name, different parameter type
    void print(int n) {
        System.out.println("Integer: " + n);
    }

    // OVERRIDING — same name AND same parameter type
    @Override
    void print(String s) {
        System.out.println("Advanced: " + s);
    }
}

AdvancedPrinter ap = new AdvancedPrinter();
ap.print("Hello"); // Advanced: Hello (overridden)
ap.print(42);       // Integer: 42 (overloaded)
```

### Hiding Base Class Methods

In Java, you can't truly "hide" inherited public methods. But:
- **Static methods**: A static method in child with same signature **hides** (not overrides) parent's static method.
- **`final` methods**: Cannot be overridden at all.

```java
class Parent {
    static void display() { System.out.println("Parent static"); }
    final void greet() { System.out.println("Cannot override this"); }
}

class Child extends Parent {
    static void display() { System.out.println("Child static"); } // Hides, not overrides

    // void greet() { }  // ❌ COMPILATION ERROR — cannot override final method
}

Parent p = new Child();
p.display(); // "Parent static" — static binding (reference type decides)
```

### Polymorphism vs Inheritance

| Inheritance | Polymorphism |
|---|---|
| Mechanism for code **reuse** | Mechanism for **multiple forms** of behavior |
| IS-A relationship | Same method, different behavior |
| `class Dog extends Animal` | `Animal a = new Dog(); a.speak();` |
| Creates hierarchy | Uses hierarchy |
| Without polymorphism = just code reuse | Without inheritance = cannot have runtime polymorphism |

### Limitations of Inheritance

1. **Tight coupling** between parent and child — changing parent can break child.
2. **Fragile base class problem** — internal changes in parent affect all children.
3. **No multiple inheritance** via classes (diamond problem).
4. **Breaks encapsulation** — child has access to `protected` internals of parent.

> **Rule:** *"Favor composition over inheritance."* — Gang of Four

### Generalization vs Aggregation vs Composition

| Relationship | Type | Lifecycle | Example |
|---|---|---|---|
| **Generalization** (Inheritance) | IS-A | Child depends on parent's type | Dog IS-A Animal |
| **Aggregation** | HAS-A (weak) | Independent | Department HAS Professors |
| **Composition** | HAS-A (strong) | Dependent | House HAS Rooms |

```java
// Generalization: Dog IS-A Animal
class Dog extends Animal { }

// Aggregation: Department HAS Professors (professors exist independently)
class Department {
    List<Professor> professors; // Professors survive if Department is destroyed
}

// Composition: House HAS Rooms (rooms cannot exist without house)
class House {
    private final List<Room> rooms = new ArrayList<>();
    House() {
        rooms.add(new Room("Living Room"));
        rooms.add(new Room("Kitchen"));
    } // Rooms are created and destroyed WITH the House
}
```

---

### 7.4 Polymorphism

**Polymorphism** (Greek: "many forms") = the same interface/method behaves differently depending on the object.

**Types of Polymorphism:**

```
Polymorphism
├── Compile-Time (Static)
│   └── Method Overloading
└── Runtime (Dynamic)
    └── Method Overriding
```

> **Note:** Java does NOT support operator overloading (except `+` for String concatenation, which is built-in).

#### Compile-Time Polymorphism (Method Overloading)

Same method name, **different parameter signatures**. Resolved at **compile time**.

```java
class MathHelper {
    int add(int a, int b)             { return a + b; }
    double add(double a, double b)    { return a + b; }
    int add(int a, int b, int c)      { return a + b + c; }
    String add(String a, String b)    { return a + b; }
}

MathHelper m = new MathHelper();
System.out.println(m.add(2, 3));           // 5         (int)
System.out.println(m.add(2.5, 3.1));       // 5.6       (double)
System.out.println(m.add(1, 2, 3));        // 6         (3 ints)
System.out.println(m.add("Hello", " World")); // Hello World (String)
```

> **Return type alone does NOT distinguish overloaded methods.** `int add(int, int)` and `double add(int, int)` causes compilation error.

#### Runtime Polymorphism (Method Overriding)

Subclass provides its own implementation. Resolved at **runtime** based on actual object type.

```java
class Shape {
    void draw() { System.out.println("Drawing a shape"); }
    double area() { return 0; }
}

class Circle extends Shape {
    double radius;
    Circle(double r) { this.radius = r; }

    @Override
    void draw() { System.out.println("Drawing circle with radius " + radius); }

    @Override
    double area() { return Math.PI * radius * radius; }
}

class Rectangle extends Shape {
    double w, h;
    Rectangle(double w, double h) { this.w = w; this.h = h; }

    @Override
    void draw() { System.out.println("Drawing rectangle " + w + "x" + h); }

    @Override
    double area() { return w * h; }
}

// Runtime polymorphism — JVM decides which method to call
Shape[] shapes = { new Circle(5), new Rectangle(4, 6) };
for (Shape s : shapes) {
    s.draw();
    System.out.println("Area: " + s.area());
}
// Output:
// Drawing circle with radius 5.0
// Area: 78.53...
// Drawing rectangle 4.0x6.0
// Area: 24.0
```

#### Overloading vs Overriding

| Feature | Overloading | Overriding |
|---|---|---|
| Binding | Compile-time (static) | Runtime (dynamic) |
| Method signature | Must differ | Must be identical |
| Return type | Can differ | Must be same or covariant |
| Inheritance required | No | Yes |
| `@Override` | Not used | Used |
| Access modifier | Any | Cannot be more restrictive |
| `static` methods | Can be overloaded | Cannot be overridden (hidden) |
| `private` methods | Can be overloaded | Cannot be overridden |
| `final` methods | Can be overloaded | Cannot be overridden |

#### Virtual Functions in Java

**In Java, all non-static, non-final, non-private instance methods are virtual by default.** There is no `virtual` keyword like C++. The JVM always does dynamic dispatch on instance method calls.

```java
class Base {
    void show() { System.out.println("Base"); }       // Virtual by default
    private void secret() { System.out.println("Secret"); } // NOT virtual
    final void locked() { System.out.println("Locked"); }   // NOT virtual
    static void util() { System.out.println("Static"); }    // NOT virtual
}

class Child extends Base {
    @Override
    void show() { System.out.println("Child"); }  // Overrides (dynamic dispatch)
    // Cannot override secret() — it's private
    // Cannot override locked() — it's final
    // Cannot override util() — it's static (can only hide)
}

Base b = new Child();
b.show();   // "Child" — dynamic dispatch (virtual)
b.locked(); // "Locked" — static binding (final)
Base.util(); // "Static" — static binding
```

**Abstract methods = pure virtual functions in C++:**

```java
abstract class Shape {
    abstract double area();  // Must be implemented by concrete subclass
}

// Shape s = new Shape(); // ❌ Cannot instantiate abstract class
```

---

## 8. Important Java Keywords

### 8.1 `static`

Belongs to the **class**, not to any instance.

```java
class Counter {
    static int count = 0;         // Shared across ALL instances
    String name;

    Counter(String name) {
        this.name = name;
        count++;
    }

    static int getCount() {       // Can be called without an object
        // System.out.println(name); // ❌ Cannot access instance member from static method
        return count;
    }
}

new Counter("A"); new Counter("B"); new Counter("C");
System.out.println(Counter.getCount()); // 3

// Static block — runs once when class is loaded
class Config {
    static String dbUrl;
    static {
        dbUrl = "jdbc:mysql://localhost:3306/mydb";
        System.out.println("Config loaded"); // Runs once, before any constructor
    }
}
```

### 8.2 `abstract`

Declares a class that **cannot be instantiated** or a method that **must be implemented** by subclasses.

```java
abstract class Animal {
    String name;
    Animal(String name) { this.name = name; }

    abstract void sound();   // No body — subclass MUST implement

    void breathe() {         // Concrete method — inherited as-is
        System.out.println(name + " is breathing");
    }
}

class Dog extends Animal {
    Dog(String name) { super(name); }

    @Override
    void sound() { System.out.println(name + " barks"); }
}

// Animal a = new Animal("Cat"); // ❌ Cannot instantiate abstract class
Animal a = new Dog("Rex");
a.sound();   // Rex barks
a.breathe(); // Rex is breathing
```

### 8.3 `final`

Prevents modification — different meaning for variables, methods, and classes.

```java
// Final variable — constant, cannot be reassigned
final int MAX = 100;
// MAX = 200; // ❌ COMPILATION ERROR

// Final method — cannot be overridden
class Parent {
    final void security() {
        System.out.println("Critical — do not override");
    }
}

// Final class — cannot be extended
final class ImmutableConfig {
    // String, Integer, etc. are final classes in Java
}
// class ExtendedConfig extends ImmutableConfig { }  // ❌ COMPILATION ERROR

// Final reference — reference can't change, but object's state CAN
final List<String> list = new ArrayList<>();
list.add("Hello");  // ✅ Modifying the object is allowed
// list = new ArrayList<>(); // ❌ Changing the reference is NOT allowed
```

**Blank final variable** — declared `final` but assigned in constructor:

```java
class Employee {
    final int id;  // Blank final — must be assigned in every constructor

    Employee(int id) {
        this.id = id;  // Assigned here
    }
}
```

### 8.4 `this`

Refers to the **current object**.

```java
class Student {
    String name;

    // 1. Disambiguate field vs parameter
    Student(String name) {
        this.name = name;
    }

    // 2. Constructor chaining
    Student() {
        this("Unknown"); // Calls parameterized constructor
    }

    // 3. Return current object (method chaining / builder pattern)
    Student setName(String name) {
        this.name = name;
        return this;
    }

    // 4. Pass current object as argument
    void enroll(Course course) {
        course.addStudent(this);
    }
}
```

### 8.5 `super`

Refers to the **parent class**.

```java
class Animal {
    String name;
    Animal(String name) { this.name = name; }
    void speak() { System.out.println(name + " speaks"); }
}

class Dog extends Animal {
    String breed;

    Dog(String name, String breed) {
        super(name);       // 1. Call parent constructor — MUST be first line
        this.breed = breed;
    }

    @Override
    void speak() {
        super.speak();     // 2. Call parent method
        System.out.println(name + " barks (" + breed + ")");
    }
}

Dog d = new Dog("Rex", "Lab");
d.speak();
// Rex speaks
// Rex barks (Lab)
```

### 8.6 `new`

Allocates memory on the **heap** and calls the constructor.

```java
Student s = new Student("Alice");
// 1. Memory allocated on heap for Student object
// 2. Fields initialized to defaults (null, 0, false)
// 3. Constructor runs
// 4. Reference to heap object stored in 's' (on stack)
```

---

## 9. Static and Dynamic Binding

**Binding** = connecting a method call to a method body.

| Feature | Static Binding (Early) | Dynamic Binding (Late) |
|---|---|---|
| When | Compile time | Runtime |
| Which methods | `static`, `final`, `private`, constructors | Overridden instance methods |
| Based on | **Reference type** | **Actual object type** |
| Performance | Faster (no runtime lookup) | Slightly slower (vtable lookup) |

```java
class Animal {
    static void staticMethod() { System.out.println("Animal static"); }
    void instanceMethod() { System.out.println("Animal instance"); }
}

class Dog extends Animal {
    static void staticMethod() { System.out.println("Dog static"); }

    @Override
    void instanceMethod() { System.out.println("Dog instance"); }
}

Animal a = new Dog();
a.staticMethod();    // "Animal static"   ← STATIC binding (reference type = Animal)
a.instanceMethod();  // "Dog instance"    ← DYNAMIC binding (actual type = Dog)
```

---

## 10. Message Passing

In OOP, objects communicate by **sending messages** to each other — i.e., invoking methods on other objects.

```java
class Customer {
    void placeOrder(OrderService service, String item) {
        // Customer sends a message to OrderService
        service.createOrder(this, item);
    }
}

class OrderService {
    void createOrder(Customer customer, String item) {
        // OrderService sends message to PaymentService
        PaymentService ps = new PaymentService();
        ps.processPayment(customer, 500);
        System.out.println("Order created: " + item);
    }
}

class PaymentService {
    void processPayment(Customer customer, double amount) {
        System.out.println("Payment of $" + amount + " processed");
    }
}

// Message flow: Customer → OrderService → PaymentService
new Customer().placeOrder(new OrderService(), "Laptop");
```

A message consists of:
1. **Receiver** — the object receiving the message (`service`).
2. **Method name** — the message itself (`createOrder`).
3. **Arguments** — the data passed along (`this, item`).

---

## 11. Call by Value in Java

**Java is always pass-by-value.** For primitives, the value is copied. For objects, the **reference** (address) is copied — NOT the object itself.

```java
// Primitives — value is copied
static void changeValue(int x) {
    x = 100;  // Changes local copy only
}

int num = 5;
changeValue(num);
System.out.println(num);  // 5 — unchanged

// Objects — reference is copied
static void changeName(Person p) {
    p.name = "Bob";  // Modifies the actual object ✅
}

static void reassign(Person p) {
    p = new Person("Charlie");  // Changes local copy of reference ❌
}

Person person = new Person("Alice");
changeName(person);
System.out.println(person.name);  // "Bob"

reassign(person);
System.out.println(person.name);  // "Bob" — reassignment had no effect
```

---

## 12. Coupling vs Cohesion

### Coupling (dependency between classes)

| Type | Description | Goal |
|---|---|---|
| **Tight** | Classes directly depend on each other's internals | ❌ Avoid |
| **Loose** | Classes interact through abstractions/interfaces | ✅ Prefer |

```java
// ❌ Tight coupling — OrderService hardcoded to EmailService
class OrderService {
    private EmailService emailService = new EmailService();
    void placeOrder(String item) {
        emailService.sendEmail("user@test.com", "Order: " + item);
    }
}

// ✅ Loose coupling — depend on interface
class OrderService {
    private final NotificationService notifier;
    OrderService(NotificationService notifier) { this.notifier = notifier; }
    void placeOrder(String item) {
        notifier.send("user@test.com", "Order: " + item);
    }
}
```

### Cohesion (focus of a class)

| Type | Description | Goal |
|---|---|---|
| **Low** | Class does many unrelated things | ❌ Avoid |
| **High** | Class has a single, focused responsibility | ✅ Prefer |

```java
// ❌ Low cohesion — does everything
class UserManager {
    void createUser() { }
    void sendEmail() { }          // Not user management
    void generateReport() { }     // Not user management
}

// ✅ High cohesion — each class does one thing
class UserService { void createUser() { } void deleteUser() { } }
class EmailService { void sendEmail() { } }
class ReportService { void generateReport() { } }
```

---

## 13. Why Java is Not Purely Object-Oriented

A **purely OOP language** treats everything as an object. Java fails this because:

| Reason | Explanation |
|---|---|
| **Primitive types** | `int`, `char`, `boolean`, `double` etc. are NOT objects |
| **Static methods/fields** | Belong to the class, not objects — breaks OOP purity |
| **Wrapper classes** | Java needs `Integer`, `Double` etc. as workarounds |
| **`null`** | Not an object — it represents "nothing" |
| **Operators** | `+`, `-`, `*` are not method calls on objects |

**Compared to a purely OOP language like Ruby/Smalltalk:**
```ruby
# Ruby — EVERYTHING is an object
5.class      # → Integer
5.even?      # → false
"hi".length  # → 2
true.class   # → TrueClass
```

```java
// Java — primitives are NOT objects
int x = 5;
// x.getClass(); ← COMPILATION ERROR — int is not an object
Integer y = 5; // Autoboxing wraps it into an object
y.getClass();  // ✅ Works — Integer is an object
```

---

## 14. Is Array Primitive or Object in Java?

**Arrays in Java are OBJECTS.** They:
- Are created with `new`.
- Have a `length` field.
- Extend `java.lang.Object`.
- Can be assigned to `Object` reference.
- Have their own class type.

```java
int[] arr = new int[5];

System.out.println(arr instanceof Object); // true
System.out.println(arr.getClass().getName()); // "[I" (array of int)
System.out.println(arr.length); // 5

Object obj = arr; // ✅ — arrays are objects

String[] names = {"Alice", "Bob"};
System.out.println(names.getClass().getSuperclass()); // class java.lang.Object
```

But the **elements** can be primitives: `int[]`, `char[]`, `boolean[]` etc. hold primitive values, not objects.

---

## 15. Exception Handling

### 15.1 Error vs Exception

| Feature | Error | Exception |
|---|---|---|
| Package | `java.lang.Error` | `java.lang.Exception` |
| Recoverability | **Unrecoverable** | **Recoverable** |
| Cause | JVM / system level | Application level |
| Examples | `OutOfMemoryError`, `StackOverflowError` | `NullPointerException`, `IOException` |
| Should you catch? | ❌ No | ✅ Yes |

**Hierarchy:**

```
Throwable
├── Error (unchecked — do NOT catch)
│   ├── OutOfMemoryError
│   ├── StackOverflowError
│   └── VirtualMachineError
└── Exception
    ├── RuntimeException (unchecked — compiler doesn't force handling)
    │   ├── NullPointerException
    │   ├── ArrayIndexOutOfBoundsException
    │   ├── ArithmeticException
    │   ├── ClassCastException
    │   └── IllegalArgumentException
    └── Checked Exceptions (compiler FORCES handling)
        ├── IOException
        ├── SQLException
        ├── FileNotFoundException
        └── ClassNotFoundException
```

### 15.2 Exception Handling Mechanism

```java
try {
    // Code that might throw an exception
    int result = 10 / 0;
} catch (ArithmeticException e) {
    // Handle specific exception
    System.out.println("Cannot divide by zero: " + e.getMessage());
} catch (Exception e) {
    // Handle general exception (catch more specific FIRST)
    System.out.println("Error: " + e.getMessage());
} finally {
    // ALWAYS runs — whether exception occurred or not
    System.out.println("Cleanup code here");
}
```

### 15.3 `finally` Block

```java
// finally ALWAYS runs (except System.exit())
static int getValue() {
    try {
        System.out.println("try");
        return 1;
    } catch (Exception e) {
        System.out.println("catch");
        return 2;
    } finally {
        System.out.println("finally");  // Runs BEFORE the return!
    }
}

System.out.println("Value: " + getValue());
// Output:
// try
// finally
// Value: 1
```

> ⚠️ If `finally` has a `return` statement, it **overrides** the return from `try`/`catch`.

### 15.4 `final` vs `finally` vs `finalize()`

| Keyword | Purpose |
|---|---|
| `final` | Makes variable constant, method non-overridable, class non-extendable |
| `finally` | Block that always executes after try/catch |
| `finalize()` | Method called by GC before object destruction (deprecated) |

### 15.5 Checked vs Unchecked Exceptions

```java
// Checked — compiler FORCES you to handle it
void readFile() throws IOException {  // Must declare or handle
    FileReader fr = new FileReader("file.txt");
}

// Unchecked — compiler does NOT force handling
void divide(int a, int b) {
    int result = a / b;  // ArithmeticException if b=0 — no compiler warning
}
```

### 15.6 Custom Exception

```java
class InsufficientBalanceException extends Exception {
    double amount;

    InsufficientBalanceException(double amount) {
        super("Insufficient balance. Attempted withdrawal: $" + amount);
        this.amount = amount;
    }
}

class Account {
    double balance = 1000;

    void withdraw(double amount) throws InsufficientBalanceException {
        if (amount > balance) {
            throw new InsufficientBalanceException(amount);
        }
        balance -= amount;
    }
}

try {
    new Account().withdraw(5000);
} catch (InsufficientBalanceException e) {
    System.out.println(e.getMessage());
    // Insufficient balance. Attempted withdrawal: $5000.0
}
```

---

## 16. Enum

An `enum` is a special class representing a **fixed set of constants**.

```java
enum OrderStatus {
    PENDING("Order is pending"),
    SHIPPED("Order shipped"),
    DELIVERED("Order delivered"),
    CANCELLED("Order cancelled");

    private final String description;

    OrderStatus(String description) { // Constructor is implicitly PRIVATE
        this.description = description;
    }

    public String getDescription() { return description; }

    public boolean isTerminal() {
        return this == DELIVERED || this == CANCELLED;
    }
}

OrderStatus status = OrderStatus.SHIPPED;
System.out.println(status.getDescription());  // Order shipped
System.out.println(status.isTerminal());      // false
System.out.println(status.ordinal());         // 1 (index)
System.out.println(status.name());            // SHIPPED

// Iterate all values
for (OrderStatus s : OrderStatus.values()) {
    System.out.println(s.name() + " → " + s.getDescription());
}
```

**Why use enums instead of `int` constants:**
- **Type safety** — `setStatus(3)` accepts any int; `setStatus(OrderStatus.SHIPPED)` is safe.
- **Namespace** — constants scoped inside the enum.
- **Methods and fields** — far more powerful than bare constants.

### String Constants vs Enum — When to Use Which

**❌ Using String constants (bad):**

```java
class OrderService {
    void updateStatus(String status) {
        if (status.equals("PENDING")) {
            // ...
        } else if (status.equals("SHIPED")) {  // ← Typo! No compile-time check!
            // ...
        }
    }
}

// Problems:
orderService.updateStatus("PENDING");    // ✅ Works
orderService.updateStatus("pending");    // ❌ Case mismatch — silently fails
orderService.updateStatus("SHIPED");     // ❌ Typo — silently fails
orderService.updateStatus("ANYTHING");   // ❌ No validation — compiles fine
```

**✅ Using Enum (good):**

```java
enum OrderStatus { PENDING, SHIPPED, DELIVERED, CANCELLED }

class OrderService {
    void updateStatus(OrderStatus status) {
        switch (status) {
            case PENDING -> { /* ... */ }
            case SHIPPED -> { /* ... */ }
            // Compiler warns if you miss a case!
        }
    }
}

// orderService.updateStatus(OrderStatus.SHIPED);  // ❌ COMPILATION ERROR — typo caught!
orderService.updateStatus(OrderStatus.SHIPPED);     // ✅ Only valid values allowed
```

**Comparison:**

| Feature | String Constants | Enum |
|---|---|---|
| **Type safety** | ❌ Any string accepted | ✅ Only valid values compile |
| **Typo protection** | ❌ Typos compile silently | ✅ Caught at compile time |
| **IDE autocomplete** | ❌ No suggestions | ✅ Full autocomplete |
| **Refactoring** | ❌ Must find-replace everywhere | ✅ Rename refactors all usages |
| **Switch exhaustiveness** | ❌ No compiler check | ✅ Compiler warns missing cases |
| **Can have methods** | ❌ Just a value | ✅ Methods, fields, logic |
| **Serialization (JSON/DB)** | ✅ Easy — it's already a string | ⚠️ Need `.name()` or `@JsonValue` |
| **Dynamic values** | ✅ Can come from config/DB | ❌ Fixed at compile time |
| **Comparison** | `equals()` needed (NPE risk) | `==` is safe and fast |
| **Performance** | Slower (string comparison) | Faster (identity comparison) |
| **Null safety** | ❌ `status.equals("X")` → NPE if null | ⚠️ Still can be null, but `==` won't NPE |

**When to use String:**
- Values are **dynamic** — loaded from config, database, or API at runtime.
- External input that hasn't been validated yet.
- Free-text fields (names, descriptions).

**When to use Enum:**
- Values are a **fixed, known set** (status codes, directions, days of week).
- You need **compile-time validation** and IDE support.
- You want to attach **behavior** (methods) to each constant.

**Converting between Enum and String:**

```java
enum Color { RED, GREEN, BLUE }

// Enum → String
String s = Color.RED.name();       // "RED"
String s2 = Color.RED.toString();  // "RED" (can be overridden)

// String → Enum
Color c = Color.valueOf("RED");    // Color.RED
// Color.valueOf("red");           // ❌ IllegalArgumentException (case-sensitive!)

// Safe conversion
Color safe = Arrays.stream(Color.values())
    .filter(v -> v.name().equalsIgnoreCase("red"))
    .findFirst()
    .orElse(null);  // Color.RED
```

---

## 17. Marker Interfaces and Functional Interfaces

### Marker Interface

An interface with **no methods** — marks a class as having a certain property.

```java
class MyClass implements Serializable { }  // Tells JVM: "this object can be serialized"
class MyClass implements Cloneable { }     // Tells JVM: "clone() is allowed"
```

### Functional Interface (Java 8+)

An interface with **exactly one abstract method**. Can be used with **lambda expressions**.

```java
@FunctionalInterface
interface Transformer<T, R> {
    R transform(T input);
}

Transformer<String, Integer> length = s -> s.length();
System.out.println(length.transform("Hello")); // 5

// Built-in functional interfaces:
// Predicate<T>  → boolean test(T t)
// Function<T,R> → R apply(T t)
// Consumer<T>   → void accept(T t)
// Supplier<T>   → T get()
```

---

## 18. Local and Nested Classes

### 18.1 Types

```
Classes in Java
├── Top-level class
└── Nested class
    ├── Static nested class          — declared static inside another class
    └── Inner class (non-static)
        ├── Member inner class       — declared at class level
        ├── Local inner class        — declared inside a method
        └── Anonymous inner class    — declared + instantiated in one expression
```

### 18.2 Static Nested Class

```java
class LinkedList {
    static class Node {  // Does NOT need a LinkedList instance
        int data;
        Node next;
    }
}

LinkedList.Node node = new LinkedList.Node(); // No outer instance needed
```

### 18.3 Member Inner Class

```java
class Outer {
    int x = 10;

    class Inner {
        void display() {
            System.out.println("Outer x = " + x);  // Can access outer's members
        }
    }
}

Outer.Inner inner = new Outer().new Inner();  // Needs outer instance
inner.display(); // Outer x = 10
```

### 18.4 Local Inner Class (inside a method)

```java
class Calculator {
    void compute() {
        // Local class — only visible inside this method
        class Adder {
            int add(int a, int b) { return a + b; }
        }
        Adder adder = new Adder();
        System.out.println(adder.add(3, 4)); // 7
    }
}

// Adder is NOT visible outside compute()
```

### 18.5 Anonymous Inner Class

```java
interface Greeting {
    void greet();
}

// Anonymous class — class definition + instantiation in one shot
Greeting g = new Greeting() {
    @Override
    public void greet() {
        System.out.println("Hello from anonymous class!");
    }
};
g.greet();

// Same thing with lambda (if it's a functional interface):
Greeting g2 = () -> System.out.println("Hello from lambda!");
g2.greet();
```

---

## 19. Upcasting and Downcasting

### Upcasting (Widening) — implicit, always safe

```java
Dog dog = new Dog("Rex");
Animal animal = dog;  // Upcasting: Dog → Animal (implicit)
animal.speak();       // Calls Dog's speak() — runtime polymorphism
```

### Downcasting (Narrowing) — explicit, risky

```java
Animal animal = new Dog("Rex");

Dog dog = (Dog) animal;   // ✅ Safe — actual object IS a Dog

Animal cat = new Animal("Whiskers");
// Dog d = (Dog) cat;  // ❌ ClassCastException at runtime!

// Always check with instanceof
if (animal instanceof Dog d) {  // Java 16+ pattern matching
    System.out.println(d.breed);
}
```

---

## 20. Composition vs Inheritance

> **Rule of thumb:** *"Favor composition over inheritance."* — Gang of Four

**Inheritance** = IS-A. Use when there's a genuine type hierarchy.  
**Composition** = HAS-A. Use when a class needs another class's functionality.

```java
// ❌ Problem with inheritance — Fragile base class
class InstrumentedHashSet<E> extends HashSet<E> {
    private int addCount = 0;

    @Override
    public boolean add(E e) { addCount++; return super.add(e); }

    @Override
    public boolean addAll(Collection<? extends E> c) {
        addCount += c.size();
        return super.addAll(c); // BUG: HashSet.addAll() calls add() internally!
    }
    // addAll(asList("a","b","c")) → addCount = 6, not 3!
}

// ✅ Fix with composition
class InstrumentedSet<E> {
    private final Set<E> set;  // HAS-A, not IS-A
    private int addCount = 0;

    InstrumentedSet(Set<E> set) { this.set = set; }

    public boolean add(E e) { addCount++; return set.add(e); }
    public boolean addAll(Collection<? extends E> c) {
        addCount += c.size();
        return set.addAll(c); // No double-counting!
    }
}
```

---

## 21. Ternary Operator

A compact if-else expression: `condition ? valueIfTrue : valueIfFalse`

```java
int age = 20;
String status = (age >= 18) ? "Adult" : "Minor";
System.out.println(status); // Adult

// Nested ternary (avoid — hard to read)
String grade = (marks >= 90) ? "A" : (marks >= 80) ? "B" : (marks >= 70) ? "C" : "F";

// Ternary type promotion trap (interview question!)
Object result = true ? new Integer(1) : new Double(2.0);
System.out.println(result);            // 1.0 (not 1!)
System.out.println(result.getClass()); // java.lang.Double
// Why? Ternary promotes both branches to common type: int + double → double
```

---

## 22. `equals()` and `hashCode()` — Deep Dive

Every class implicitly extends `java.lang.Object`, which provides default implementations of `equals()` and `hashCode()`.

### What Does `Object.equals()` Do by Default?

By default, `equals()` checks **reference equality** — whether two variables point to the **exact same object in memory** (same as `==`).

```java
class Employee {
    int id;
    String name;

    Employee(int id, String name) { this.id = id; this.name = name; }
    // NO equals() or hashCode() overridden
}

Employee e1 = new Employee(1, "Alice");
Employee e2 = new Employee(1, "Alice");  // Same data, DIFFERENT object

System.out.println(e1.equals(e2)); // false ❌ — default equals() compares references
System.out.println(e1 == e2);      // false — different objects on heap
```

### What Does `Object.hashCode()` Do by Default?

By default, `hashCode()` returns a value derived from the **memory address** of the object. Two different objects → two different hash codes (even if they have identical data).

### What Breaks If You Don't Override Them?

**HashMap and HashSet stop working correctly:**

```java
class Employee {
    int id;
    String name;
    Employee(int id, String name) { this.id = id; this.name = name; }
    // NO equals() or hashCode() overridden!
}

// ❌ PROBLEM 1: HashSet treats duplicates as unique
Set<Employee> set = new HashSet<>();
set.add(new Employee(1, "Alice"));
set.add(new Employee(1, "Alice")); // Same data!
System.out.println(set.size()); // 2 ← Should be 1! Duplicates not detected.

// ❌ PROBLEM 2: HashMap can't find keys
Map<Employee, String> map = new HashMap<>();
Employee key = new Employee(1, "Alice");
map.put(key, "Engineering");

// Trying to get with a new object with same data:
Employee lookupKey = new Employee(1, "Alice");
System.out.println(map.get(lookupKey)); // null ← Can't find it!
// Because lookupKey has a DIFFERENT hashCode → goes to a different bucket

// Only works with the EXACT SAME reference:
System.out.println(map.get(key)); // "Engineering" ← Works because same reference
```

**Why?** HashMap lookup: `hashCode()` → bucket → `equals()` → match. If either is wrong, lookup fails.

### The `equals()` and `hashCode()` Contract

| Rule | Description |
|---|---|
| **Consistency** | If `a.equals(b)` is `true`, then `a.hashCode() == b.hashCode()` MUST be `true` |
| **Converse NOT required** | `a.hashCode() == b.hashCode()` does NOT mean `a.equals(b)` (hash collisions exist) |
| **Reflexive** | `a.equals(a)` must be `true` |
| **Symmetric** | If `a.equals(b)` then `b.equals(a)` |
| **Transitive** | If `a.equals(b)` and `b.equals(c)` then `a.equals(c)` |
| **Null check** | `a.equals(null)` must be `false` |

### Correct Implementation:

```java
class Employee {
    int id;
    String name;

    Employee(int id, String name) { this.id = id; this.name = name; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;                    // Same reference → equal
        if (o == null || getClass() != o.getClass()) return false; // Null or diff type
        Employee emp = (Employee) o;
        return id == emp.id && Objects.equals(name, emp.name);  // Compare fields
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, name);  // Must use SAME fields as equals()
    }

    @Override
    public String toString() {
        return "Employee{id=" + id + ", name='" + name + "'}";
    }
}

// Now everything works:
Employee e1 = new Employee(1, "Alice");
Employee e2 = new Employee(1, "Alice");

System.out.println(e1.equals(e2));  // true ✅
System.out.println(e1.hashCode() == e2.hashCode()); // true ✅

Set<Employee> set = new HashSet<>();
set.add(e1);
set.add(e2);
System.out.println(set.size()); // 1 ✅ — duplicate detected!

Map<Employee, String> map = new HashMap<>();
map.put(e1, "Engineering");
System.out.println(map.get(e2)); // "Engineering" ✅ — lookup works!
```

### Common Mistakes

```java
// ❌ Mistake 1: Override equals() but NOT hashCode()
// Equal objects get different hashCodes → land in different buckets → HashMap breaks

// ❌ Mistake 2: Use mutable fields in hashCode()
// If field changes after insertion → object is lost in HashMap (wrong bucket)

// ❌ Mistake 3: Wrong parameter type
public boolean equals(Employee other) { }  // ❌ This is OVERLOADING, not overriding!
public boolean equals(Object other) { }    // ✅ Correct — must take Object
```

---

## 23. Record vs Class (Java 14+)

A **record** is a special kind of class introduced in Java 14 that is designed for **immutable data carriers** — classes whose sole purpose is to hold data.

### The Problem Records Solve

For a simple data class, you have to write a LOT of boilerplate:

```java
// Traditional class — ~40 lines for a simple data container
class Point {
    private final int x;
    private final int y;

    Point(int x, int y) { this.x = x; this.y = y; }            // Constructor
    int x() { return x; }                                        // Getter
    int y() { return y; }                                        // Getter
    @Override public boolean equals(Object o) { /* ... */ }      // equals
    @Override public int hashCode() { return Objects.hash(x, y); } // hashCode
    @Override public String toString() { return "Point[x=" + x + ", y=" + y + "]"; } // toString
}
```

### Record — One Line Does It All

```java
// Record — 1 line replaces everything above!
record Point(int x, int y) { }
```

**This single line automatically generates:**
1. `private final` fields for `x` and `y`
2. A **canonical constructor** `Point(int x, int y)`
3. **Getter methods** `x()` and `y()` (NOT `getX()` / `getY()`)
4. `equals()` — compares all fields
5. `hashCode()` — based on all fields
6. `toString()` — returns `Point[x=5, y=10]`

```java
record Point(int x, int y) { }

Point p1 = new Point(5, 10);
Point p2 = new Point(5, 10);

System.out.println(p1.x());       // 5 (accessor, NOT getX())
System.out.println(p1.y());       // 10
System.out.println(p1);           // Point[x=5, y=10] (auto toString)
System.out.println(p1.equals(p2)); // true (auto equals based on fields)
System.out.println(p1.hashCode() == p2.hashCode()); // true (auto hashCode)
```

### What You CAN Do in Records

```java
record Employee(int id, String name, String department) {

    // Custom (compact) constructor — for validation
    Employee {
        if (id <= 0) throw new IllegalArgumentException("ID must be positive");
        name = name.trim();  // Modify before assignment
    }

    // Static fields and methods
    static int count = 0;
    static int getCount() { return count; }

    // Instance methods
    String displayName() {
        return name + " (" + department + ")";
    }

    // Can implement interfaces
}

Employee emp = new Employee(1, "  Alice  ", "Engineering");
System.out.println(emp.name());         // "Alice" (trimmed by compact constructor)
System.out.println(emp.displayName());  // "Alice (Engineering)"
```

### What You CANNOT Do in Records

```java
// ❌ Cannot extend another class (records implicitly extend java.lang.Record)
// record Employee extends Person { }  // COMPILATION ERROR

// ❌ Cannot declare additional instance fields
// record Point(int x, int y) { int z; }  // COMPILATION ERROR

// ❌ Fields are always final — cannot have setters
// Point p = new Point(5, 10);
// p.x = 20;  // COMPILATION ERROR

// ❌ Cannot be abstract
// abstract record Shape() { }  // COMPILATION ERROR

// ✅ CAN implement interfaces
record Point(int x, int y) implements Serializable { }

// ✅ CAN be generic
record Pair<A, B>(A first, B second) { }
```

### Record vs Class — Comparison

| Feature | Class | Record |
|---|---|---|
| Mutability | Mutable or immutable | Always **immutable** |
| Fields | Any kind | `private final` only (auto-generated) |
| Constructor | Custom | Auto-generated (can customize) |
| `equals()` / `hashCode()` | Must override manually | Auto-generated based on all fields |
| `toString()` | Must override manually | Auto-generated |
| Inheritance | Can extend other classes | Cannot extend (extends `Record`) |
| Can implement interfaces | ✅ | ✅ |
| Additional instance fields | ✅ | ❌ |
| Setters | Possible | ❌ (immutable) |
| Boilerplate | A lot | Almost none |
| Use case | Complex objects with logic | Simple **data carriers** (DTOs, value objects) |

### When to Use Record vs Class

```java
// ✅ USE RECORD — simple data container
record ApiResponse(int statusCode, String body, Map<String, String> headers) { }
record Coordinate(double lat, double lng) { }
record UserDTO(String name, String email, String role) { }

// ❌ DON'T USE RECORD — needs mutability or complex logic
class ShoppingCart {
    private List<Item> items = new ArrayList<>();  // Mutable state
    void addItem(Item item) { items.add(item); }   // Mutating operation
    void removeItem(Item item) { items.remove(item); }
    double getTotal() { /* computation */ }
}

// ❌ DON'T USE RECORD — needs inheritance
class Animal { }
class Dog extends Animal { }  // Records can't extend classes
```

---
