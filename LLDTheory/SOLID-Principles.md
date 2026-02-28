# SOLID Principles — Complete Theory

---

## What is SOLID?

SOLID is a set of five design principles introduced by **Robert C. Martin** (Uncle Bob) that guide writing **maintainable, flexible, and scalable** object-oriented software. Violating these principles leads to code that is rigid, fragile, and hard to extend.

| Letter | Principle | Core Idea |
|---|---|---|
| **S** | Single Responsibility | A class should have only one reason to change |
| **O** | Open/Closed | Open for extension, closed for modification |
| **L** | Liskov Substitution | Subtypes must be substitutable for their base types |
| **I** | Interface Segregation | Many specific interfaces > one fat interface |
| **D** | Dependency Inversion | Depend on abstractions, not concretions |

---

## 1. Single Responsibility Principle (SRP)

> **"A class should have one, and only one, reason to change."**

A class should encapsulate **one responsibility**. If a class has multiple reasons to change (e.g., it handles both business logic **and** data persistence), it violates SRP.

### ❌ Violation

```java
class Employee {
    String name;
    double salary;

    // Responsibility 1: Business logic
    double calculatePay() {
        return salary * 1.2;
    }

    // Responsibility 2: Persistence (saving to database)
    void saveToDatabase() {
        // JDBC code to insert employee
        System.out.println("Saving " + name + " to database...");
    }

    // Responsibility 3: Reporting
    String generateReport() {
        return "Employee Report: " + name + ", Salary: " + salary;
    }
}
```

**Problems:**
- If the database schema changes → you modify `Employee`.
- If the report format changes → you modify `Employee`.
- If the pay calculation logic changes → you modify `Employee`.
- Three different reasons to change = three responsibilities tangled together.

### ✅ Correct Design

```java
// Responsibility 1: Employee data and business logic
class Employee {
    String name;
    double salary;

    Employee(String name, double salary) {
        this.name = name;
        this.salary = salary;
    }

    double calculatePay() {
        return salary * 1.2;
    }
}

// Responsibility 2: Persistence
class EmployeeRepository {
    void save(Employee employee) {
        // JDBC/JPA code to save employee
        System.out.println("Saving " + employee.name + " to database...");
    }

    Employee findById(int id) {
        // Query DB and return Employee
        return new Employee("Alice", 50000);
    }
}

// Responsibility 3: Reporting
class EmployeeReportGenerator {
    String generate(Employee employee) {
        return "Employee Report: " + employee.name + ", Salary: " + employee.salary;
    }
}
```

**Now each class has exactly one reason to change:**
- `Employee` changes only when business rules change.
- `EmployeeRepository` changes only when the storage mechanism changes.
- `EmployeeReportGenerator` changes only when the report format changes.

---

## 2. Open/Closed Principle (OCP)

> **"Software entities should be open for extension, but closed for modification."**

You should be able to add new behavior **without modifying existing code**. This is achieved through **abstraction** and **polymorphism**.

### ❌ Violation

```java
class DiscountCalculator {
    double calculate(String customerType, double amount) {
        if (customerType.equals("REGULAR")) {
            return amount * 0.1;
        } else if (customerType.equals("PREMIUM")) {
            return amount * 0.2;
        } else if (customerType.equals("VIP")) {
            return amount * 0.3;
        }
        // Every new customer type → MODIFY this class!
        return 0;
    }
}
```

**Problem:** Every time a new customer type is introduced (e.g., `STUDENT`, `EMPLOYEE`), you must modify the `DiscountCalculator` class. This risks breaking existing logic on every change.

### ✅ Correct Design

```java
// Abstraction
interface DiscountStrategy {
    double calculate(double amount);
}

// Extensions — each in its own class
class RegularDiscount implements DiscountStrategy {
    @Override
    public double calculate(double amount) {
        return amount * 0.1;
    }
}

class PremiumDiscount implements DiscountStrategy {
    @Override
    public double calculate(double amount) {
        return amount * 0.2;
    }
}

class VIPDiscount implements DiscountStrategy {
    @Override
    public double calculate(double amount) {
        return amount * 0.3;
    }
}

// Adding a new type → just create a new class
class StudentDiscount implements DiscountStrategy {
    @Override
    public double calculate(double amount) {
        return amount * 0.15;
    }
}

// Calculator is CLOSED for modification
class DiscountCalculator {
    private final DiscountStrategy strategy;

    DiscountCalculator(DiscountStrategy strategy) {
        this.strategy = strategy;
    }

    double applyDiscount(double amount) {
        return strategy.calculate(amount);
    }
}

// Usage
DiscountCalculator calc = new DiscountCalculator(new VIPDiscount());
System.out.println(calc.applyDiscount(1000)); // 300.0

// Add StudentDiscount WITHOUT touching DiscountCalculator
DiscountCalculator studentCalc = new DiscountCalculator(new StudentDiscount());
System.out.println(studentCalc.applyDiscount(1000)); // 150.0
```

---

## 3. Liskov Substitution Principle (LSP)

> **"Objects of a superclass should be replaceable with objects of its subclasses without breaking the application."**

If class B is a subclass of class A, then we should be able to use B wherever A is expected, **without unexpected behavior**. Subclasses must honour the **contract** of the parent class.

### ❌ Classic Violation — Rectangle-Square Problem

```java
class Rectangle {
    protected int width;
    protected int height;

    public void setWidth(int width) {
        this.width = width;
    }

    public void setHeight(int height) {
        this.height = height;
    }

    public int getArea() {
        return width * height;
    }
}

class Square extends Rectangle {
    // A square's width must always equal its height
    @Override
    public void setWidth(int width) {
        this.width = width;
        this.height = width;  // Enforce square invariant
    }

    @Override
    public void setHeight(int height) {
        this.width = height;  // Enforce square invariant
        this.height = height;
    }
}

// Test that works for Rectangle but BREAKS for Square
void testArea(Rectangle r) {
    r.setWidth(5);
    r.setHeight(4);
    // Expected: 5 * 4 = 20
    System.out.println("Area: " + r.getArea());
}

testArea(new Rectangle()); // Area: 20  ✅
testArea(new Square());    // Area: 16  ❌ — Square rewrites width when setHeight is called!
```

**Problem:** `Square` changes the expected behavior of `Rectangle`'s setter methods. Substituting a `Square` for a `Rectangle` produces incorrect results.

### ✅ Correct Design

```java
// Don't force Square to extend Rectangle
// Use an interface or separate hierarchy

interface Shape {
    int getArea();
}

class Rectangle implements Shape {
    private final int width;
    private final int height;

    Rectangle(int width, int height) {
        this.width = width;
        this.height = height;
    }

    @Override
    public int getArea() { return width * height; }
}

class Square implements Shape {
    private final int side;

    Square(int side) {
        this.side = side;
    }

    @Override
    public int getArea() { return side * side; }
}

// Both are substitutable as Shape without breaking semantics
void printArea(Shape s) {
    System.out.println("Area: " + s.getArea());
}

printArea(new Rectangle(5, 4)); // Area: 20  ✅
printArea(new Square(5));       // Area: 25  ✅
```

### LSP Guidelines:
1. **Preconditions** cannot be strengthened in the subclass (subclass cannot require "more").
2. **Postconditions** cannot be weakened in the subclass (subclass cannot deliver "less").
3. **Invariants** of the parent class must be preserved.
4. The **History Constraint**: subclass should not allow state transitions that the parent does not.

### Another Violation: Empty/Unsupported Methods

```java
class Bird {
    void fly() {
        System.out.println("Flying...");
    }
}

class Ostrich extends Bird {
    @Override
    void fly() {
        throw new UnsupportedOperationException("Ostriches can't fly!");  // ❌ LSP violation
    }
}
```

**Fix:** Restructure the hierarchy.

```java
interface Bird {
    void eat();
}

interface FlyingBird extends Bird {
    void fly();
}

class Sparrow implements FlyingBird {
    public void eat() { System.out.println("Sparrow eating..."); }
    public void fly() { System.out.println("Sparrow flying..."); }
}

class Ostrich implements Bird {
    public void eat() { System.out.println("Ostrich eating..."); }
    // Ostrich doesn't have fly() — because it's not a FlyingBird
}
```

---

## 4. Interface Segregation Principle (ISP)

> **"No client should be forced to depend on methods it does not use."**

Instead of creating one large "god" interface, break it into smaller, focused interfaces that clients can implement selectively.

### ❌ Violation — Fat Interface

```java
interface Worker {
    void work();
    void eat();
    void sleep();
    void attendMeeting();
    void writeCode();
    void manageTeam();
}

class Developer implements Worker {
    @Override public void work() { System.out.println("Writing code"); }
    @Override public void eat() { System.out.println("Eating lunch"); }
    @Override public void sleep() { System.out.println("Sleeping"); }
    @Override public void attendMeeting() { System.out.println("In meeting"); }
    @Override public void writeCode() { System.out.println("Coding!"); }

    @Override
    public void manageTeam() {
        // Developer doesn't manage a team!
        throw new UnsupportedOperationException();  // ❌ Forced to implement useless method
    }
}

class Manager implements Worker {
    @Override public void work() { System.out.println("Managing"); }
    @Override public void eat() { System.out.println("Eating"); }
    @Override public void sleep() { System.out.println("Sleeping"); }
    @Override public void attendMeeting() { System.out.println("Leading meeting"); }
    @Override public void manageTeam() { System.out.println("Managing team"); }

    @Override
    public void writeCode() {
        // Manager doesn't write code!
        throw new UnsupportedOperationException();  // ❌ Forced to implement useless method
    }
}
```

### ✅ Correct Design — Segregated Interfaces

```java
interface Workable {
    void work();
}

interface Eatable {
    void eat();
}

interface Sleepable {
    void sleep();
}

interface Codeable {
    void writeCode();
}

interface Manageable {
    void manageTeam();
}

interface Meetable {
    void attendMeeting();
}

// Developer: picks only the interfaces it needs
class Developer implements Workable, Eatable, Sleepable, Codeable, Meetable {
    @Override public void work() { System.out.println("Writing code"); }
    @Override public void eat() { System.out.println("Eating lunch"); }
    @Override public void sleep() { System.out.println("Sleeping"); }
    @Override public void writeCode() { System.out.println("Coding!"); }
    @Override public void attendMeeting() { System.out.println("In standup"); }
}

// Manager: picks only the interfaces it needs
class Manager implements Workable, Eatable, Sleepable, Manageable, Meetable {
    @Override public void work() { System.out.println("Managing"); }
    @Override public void eat() { System.out.println("Eating"); }
    @Override public void sleep() { System.out.println("Sleeping"); }
    @Override public void manageTeam() { System.out.println("Managing team"); }
    @Override public void attendMeeting() { System.out.println("Leading meeting"); }
}

// Robot: only works — doesn't eat, sleep, or manage
class Robot implements Workable, Codeable {
    @Override public void work() { System.out.println("Working 24/7"); }
    @Override public void writeCode() { System.out.println("Auto-generating code"); }
}
```

### Real-World Example: `java.util` follows ISP

Java's Collections Framework is a great example:
- `Iterable<T>` — can iterate.
- `Collection<T>` — add, remove, size.
- `List<T>` — ordered, index-based access.
- `Set<T>` — no duplicates.
- `Queue<T>` — FIFO operations.

Each adds specific capability. A `TreeSet` doesn't need to implement `get(index)` because it implements `Set`, not `List`.

---

## 5. Dependency Inversion Principle (DIP)

> **"High-level modules should not depend on low-level modules. Both should depend on abstractions."**
>
> **"Abstractions should not depend on details. Details should depend on abstractions."**

High-level business logic should be decoupled from low-level implementation details (databases, APIs, file systems) through **interfaces/abstractions**.

### ❌ Violation

```java
// Low-level module
class MySQLDatabase {
    void save(String data) {
        System.out.println("Saving to MySQL: " + data);
    }
}

// High-level module — DIRECTLY depends on low-level
class UserService {
    private MySQLDatabase database = new MySQLDatabase();  // ❌ Tightly coupled

    void createUser(String name) {
        // Business logic
        database.save(name);
    }
}
// What if we want to switch to PostgreSQL or MongoDB? → Must MODIFY UserService
```

### ✅ Correct Design

```java
// Abstraction — both high and low level depend on THIS
interface Database {
    void save(String data);
    String findById(int id);
}

// Low-level modules implement the abstraction
class MySQLDatabase implements Database {
    @Override
    public void save(String data) {
        System.out.println("MySQL: INSERT INTO users VALUES ('" + data + "')");
    }

    @Override
    public String findById(int id) {
        return "MySQL user #" + id;
    }
}

class PostgreSQLDatabase implements Database {
    @Override
    public void save(String data) {
        System.out.println("PostgreSQL: INSERT INTO users VALUES ('" + data + "')");
    }

    @Override
    public String findById(int id) {
        return "PostgreSQL user #" + id;
    }
}

class MongoDatabase implements Database {
    @Override
    public void save(String data) {
        System.out.println("MongoDB: db.users.insertOne({name: '" + data + "'})");
    }

    @Override
    public String findById(int id) {
        return "MongoDB user #" + id;
    }
}

// High-level module — depends on ABSTRACTION, not implementation
class UserService {
    private final Database database;  // Depends on interface

    UserService(Database database) {  // Injected via constructor
        this.database = database;
    }

    void createUser(String name) {
        // Business logic
        System.out.println("Creating user: " + name);
        database.save(name);
    }
}

// Switch databases WITHOUT modifying UserService
UserService service1 = new UserService(new MySQLDatabase());
service1.createUser("Alice");
// Output: Creating user: Alice
//         MySQL: INSERT INTO users VALUES ('Alice')

UserService service2 = new UserService(new MongoDatabase());
service2.createUser("Bob");
// Output: Creating user: Bob
//         MongoDB: db.users.insertOne({name: 'Bob'})
```

### DIP in Practice — Dependency Injection

The DIP is achieved through **Dependency Injection (DI)** — providing dependencies from the outside rather than creating them inside. Three forms:

```java
// 1. Constructor Injection (preferred)
class OrderService {
    private final PaymentGateway gateway;

    OrderService(PaymentGateway gateway) {
        this.gateway = gateway;
    }
}

// 2. Setter Injection
class OrderService {
    private PaymentGateway gateway;

    void setPaymentGateway(PaymentGateway gateway) {
        this.gateway = gateway;
    }
}

// 3. Interface / Method Injection
class OrderService {
    void processOrder(Order order, PaymentGateway gateway) {
        gateway.charge(order.getTotal());
    }
}
```

**Spring Framework** is built entirely on DIP — the IoC (Inversion of Control) container manages all dependencies.

---

## 6. SOLID in a Single System — Full Example

Here's a mini e-commerce order system applying **all five principles**:

```java
// ===== INTERFACES (Abstractions — DIP + ISP) =====

interface OrderRepository {
    void save(Order order);
    Order findById(String id);
}

interface PaymentProcessor {
    boolean charge(double amount, String paymentMethod);
}

interface NotificationService {
    void notify(String recipient, String message);
}

interface TaxCalculator {
    double calculateTax(double amount, String region);
}

// ===== DATA =====

class Order {
    String id;
    String customerEmail;
    double amount;
    String region;
    String paymentMethod;

    Order(String id, String customerEmail, double amount, String region, String paymentMethod) {
        this.id = id;
        this.customerEmail = customerEmail;
        this.amount = amount;
        this.region = region;
        this.paymentMethod = paymentMethod;
    }
}

// ===== IMPLEMENTATIONS (Low-level details — depend on abstractions) =====

class InMemoryOrderRepository implements OrderRepository {
    private final Map<String, Order> store = new HashMap<>();

    @Override
    public void save(Order order) {
        store.put(order.id, order);
        System.out.println("Order " + order.id + " saved to memory store.");
    }

    @Override
    public Order findById(String id) {
        return store.get(id);
    }
}

class StripePaymentProcessor implements PaymentProcessor {
    @Override
    public boolean charge(double amount, String paymentMethod) {
        System.out.println("Stripe: Charged $" + amount + " via " + paymentMethod);
        return true;
    }
}

class EmailNotificationService implements NotificationService {
    @Override
    public void notify(String recipient, String message) {
        System.out.println("Email to " + recipient + ": " + message);
    }
}

class RegionalTaxCalculator implements TaxCalculator {
    @Override
    public double calculateTax(double amount, String region) {
        double rate = switch (region) {
            case "US" -> 0.08;
            case "EU" -> 0.20;
            case "IN" -> 0.18;
            default -> 0.10;
        };
        return amount * rate;
    }
}

// ===== HIGH-LEVEL SERVICE (SRP — only orchestrate order placement) =====

class OrderService {
    private final OrderRepository repository;       // DIP
    private final PaymentProcessor paymentProcessor; // DIP
    private final NotificationService notifier;      // DIP
    private final TaxCalculator taxCalculator;       // DIP

    // Constructor Injection
    OrderService(OrderRepository repository,
                 PaymentProcessor paymentProcessor,
                 NotificationService notifier,
                 TaxCalculator taxCalculator) {
        this.repository = repository;
        this.paymentProcessor = paymentProcessor;
        this.notifier = notifier;
        this.taxCalculator = taxCalculator;
    }

    void placeOrder(Order order) {
        // Calculate tax
        double tax = taxCalculator.calculateTax(order.amount, order.region);
        double total = order.amount + tax;

        // Process payment
        boolean paid = paymentProcessor.charge(total, order.paymentMethod);
        if (!paid) {
            throw new RuntimeException("Payment failed for order " + order.id);
        }

        // Save order
        repository.save(order);

        // Send notification
        notifier.notify(order.customerEmail,
            "Order " + order.id + " confirmed! Total: $" + total);
    }
}

// ===== COMPOSING THE SYSTEM =====

public class Main {
    public static void main(String[] args) {
        // Wire up dependencies
        OrderService orderService = new OrderService(
            new InMemoryOrderRepository(),
            new StripePaymentProcessor(),
            new EmailNotificationService(),
            new RegionalTaxCalculator()
        );

        // Place an order
        Order order = new Order("ORD-001", "alice@example.com", 100.0, "IN", "credit_card");
        orderService.placeOrder(order);

        // Output:
        // Stripe: Charged $118.0 via credit_card
        // Order ORD-001 saved to memory store.
        // Email to alice@example.com: Order ORD-001 confirmed! Total: $118.0
    }
}
```

**How each principle is applied:**
- **SRP**: `OrderService` only orchestrates. Tax, payment, persistence, notification are separate.
- **OCP**: To add a new payment method, create `RazorpayProcessor implements PaymentProcessor` — no modification needed.
- **LSP**: Any `PaymentProcessor` implementation is fully substitutable.
- **ISP**: Interfaces are small and focused — `PaymentProcessor` doesn't force `save()` methods.
- **DIP**: `OrderService` depends on abstractions (`PaymentProcessor`, `OrderRepository`), not on `StripePaymentProcessor` or `MySQLOrderRepository`.

---

## 7. Common Violations Cheat Sheet

| Principle | Smell / Violation | Fix |
|---|---|---|
| SRP | "God class" with 20+ methods doing unrelated things | Split into focused classes |
| OCP | Long `if-else` / `switch` chains for types | Strategy pattern, polymorphism |
| LSP | Subclass throws `UnsupportedOperationException` | Redesign hierarchy, use composition |
| ISP | Interface with 10+ methods | Break into smaller interfaces |
| DIP | `new MySQLDatabase()` inside business logic | Inject via constructor, use interface |

---
