# Spring Boot

Interview-prep notes on Spring Boot. Written for Spring Boot 3.x / 4.x on Java 17+ (code uses records, constructor injection and `jakarta.*` packages).

## 📚 Table of Contents

**Beans: Defining Them and the Stereotypes**

1. [What is a bean?](#1-what-is-a-bean)
2. [Three ways to define a bean](#2-three-ways-to-define-a-bean)
3. [Way 1: @Component and component scanning](#3-way-1-component-and-component-scanning)
4. [Way 2: @Bean methods in a @Configuration class](#4-way-2-bean-methods-in-a-configuration-class)
5. [@Component vs @Bean](#5-component-vs-bean)
6. [The four stereotype annotations](#6-the-four-stereotype-annotations)
7. [What @Repository adds: exception translation](#7-what-repository-adds-exception-translation)
8. [What @Controller adds, and @RestController](#8-what-controller-adds-and-restcontroller)
9. [Bean names, multiple candidates and scope](#9-bean-names-multiple-candidates-and-scope)
10. [Lazy vs eager bean initialization](#10-lazy-vs-eager-bean-initialization)
11. [Conditional beans and other ways to register](#11-conditional-beans-and-other-ways-to-register)
12. [Bean interview questions](#12-bean-interview-questions)
13. [Bean cheat sheet](#13-bean-cheat-sheet)

**@SpringBootApplication and Startup**

1. [@SpringBootApplication: three annotations in one](#1-springbootapplication-three-annotations-in-one)
2. [What happens when the app starts, step by step](#2-what-happens-when-the-app-starts-step-by-step)
3. [Auto-configuration: how Boot decides what to create](#3-auto-configuration-how-boot-decides-what-to-create)
4. [Running your own code at startup](#4-running-your-own-code-at-startup)
5. [Startup interview questions](#5-startup-interview-questions)
6. [Startup cheat sheet](#6-startup-cheat-sheet)

**The 10 Most Used Annotations**

1. [Where the annotations fit](#1-where-the-annotations-fit)
2. [The top 10, one by one](#2-the-top-10-one-by-one)
3. [Next 10 worth knowing](#3-next-10-worth-knowing)
4. [Annotation cheat sheet](#4-annotation-cheat-sheet)

**Famous Spring Boot Interview Questions**

1. [Core container and dependency injection](#1-core-container-and-dependency-injection)
2. [Common error: calling an annotated method from the same class](#2-common-error-calling-an-annotated-method-from-the-same-class)
3. [Proxies, @Transactional and @Async](#3-proxies-transactional-and-async)
4. [The web layer](#4-the-web-layer)
5. [Filter vs interceptor](#5-filter-vs-interceptor)
6. [Data and JPA](#6-data-and-jpa)
7. [Configuration and production](#7-configuration-and-production)
8. [Quick-fire answers](#8-quick-fire-answers)

---

# Beans: Defining Them and the Stereotypes

## 1. What is a bean?

A **bean** is an object that Spring creates, wires and manages for you. You don't call `new OrderService(...)`. You tell Spring the class exists, and Spring:

1. creates it (once, by default),
2. passes in its dependencies (other beans) through the constructor,
3. keeps it in the **ApplicationContext** (the IoC container),
4. hands it to anyone who asks for that type,
5. calls its shutdown hooks when the app stops.

This is **Inversion of Control (IoC)**: the container, not your code, controls object creation. **Dependency Injection (DI)** is how it does it: a class declares what it needs and the container supplies it.

```java
public class OrderService {
    private final PaymentClient payments;          // a dependency

    public OrderService(PaymentClient payments) {  // Spring passes the PaymentClient bean in
        this.payments = payments;
    }
}
```

> [!NOTE]
> A plain object you create with `new` is **not** a bean. Spring doesn't know about it, so it gets no injection, no `@Transactional`, no `@Async`, nothing.

---

## 2. Three ways to define a bean

| Way | You write | Use it for |
|---|---|---|
| **1. Stereotype annotation** + component scan | `@Component` / `@Service` / `@Repository` / `@Controller` on **your** class | Your own classes (90% of beans) |
| **2. `@Bean` method** in a `@Configuration` class | A method that builds and returns the object | Third-party classes you can't annotate, or objects that need setup code |
| **3. Auto-configuration** | Nothing. Add a starter to the build | `DataSource`, `ObjectMapper`, `RestClient.Builder`, Tomcat… Boot creates them |

All three end up as **bean definitions** (a recipe: class, name, scope, dependencies). At startup the container turns each definition into an object.

![How beans get into the container: your stereotype classes found by component scan, your @Bean methods in a @Configuration class, and Boot's auto-configurations all become bean definitions, which the ApplicationContext turns into singleton objects and wires through constructors](svg/springboot/d001-ways-to-define-beans.svg)

---

## 3. Way 1: @Component and component scanning

Put a stereotype annotation on the class. That's it.

```java
package com.example.shop.order;

@Service
public class OrderService {

    private final OrderRepository orders;
    private final PaymentClient payments;

    // Only one constructor → Spring uses it. No @Autowired needed.
    public OrderService(OrderRepository orders, PaymentClient payments) {
        this.orders = orders;
        this.payments = payments;
    }

    public Order place(CreateOrderRequest req) {
        payments.charge(req.customerId(), req.amount());
        return orders.save(new Order(req.sku(), req.qty()));
    }
}
```

**Component scanning** finds these classes. `@SpringBootApplication` includes `@ComponentScan`, which scans the **package of the main class and every package below it**.

```text
com.example.shop                 ← ShopApplication (@SpringBootApplication) lives here
├── order/OrderService.java      ✓ scanned
├── order/OrderRepository.java   ✓ scanned
└── web/OrderController.java     ✓ scanned
com.example.common/Util.java     ✗ NOT scanned: sibling package, not below
```

> [!WARNING]
> ⚠️ The classic "my bean isn't found" bug (`NoSuchBeanDefinitionException`): the class is outside the main class's package. Move the main class up to the root package, or use `@SpringBootApplication(scanBasePackages = {"com.example.shop", "com.example.common"})`.

---

## 4. Way 2: @Bean methods in a @Configuration class

When you **can't** put `@Component` on a class (it's from a library) or it needs **construction logic**, write a method that builds it and mark it `@Bean`. The method's return value becomes the bean, and the **method name** becomes the bean name.

```java
@Configuration
public class ClientConfig {

    @Bean
    public Clock clock() {                        // bean "clock" of type Clock (a JDK class)
        return Clock.systemUTC();
    }

    @Bean
    public RestClient paymentsClient(RestClient.Builder builder,          // parameters are injected
                                     @Value("${payments.base-url}") String baseUrl) {
        return builder
                .baseUrl(baseUrl)
                .defaultHeader("X-Client", "shop")
                .build();
    }

    @Bean
    public RestClient inventoryClient(RestClient.Builder builder,
                                      @Value("${inventory.base-url}") String baseUrl) {
        return builder.baseUrl(baseUrl).build();  // a second bean of the same type
    }
}
```

Things to notice:

- **Dependencies come in as method parameters.** `RestClient.Builder` is itself a bean (from auto-configuration).
- `@Bean` lets you make **several beans of one type** with different setups (`paymentsClient`, `inventoryClient`). One annotated class can only give you one.
- You can take a `Clock` bean in your services and swap in `Clock.fixed(...)` in tests. That's impossible if code calls `Instant.now()` directly.

> [!TIP]
> A `@Configuration` class is itself a bean (it's meta-annotated with `@Component`), so component scan finds it too.

### Full mode vs lite mode

What if one `@Bean` method **calls** another?

```java
@Configuration                                  // proxyBeanMethods = true (default)
public class AppConfig {

    @Bean
    public DataSource dataSource() { return new HikariDataSource(); }

    @Bean
    public JdbcTemplate jdbcTemplate() {
        return new JdbcTemplate(dataSource());  // looks like it creates a second DataSource…
    }
}
```

- **`@Configuration` (full mode):** Spring subclasses the config class with CGLIB. The call `dataSource()` is intercepted and returns **the existing singleton**. Only one `DataSource`.
- **`@Configuration(proxyBeanMethods = false)` or `@Bean` inside a `@Component` (lite mode):** no proxy. `dataSource()` is a normal Java call and creates a **new, unmanaged** `DataSource`. A bug.

The clean habit that works in both modes: **don't call `@Bean` methods, take the bean as a parameter.**

```java
@Bean
public JdbcTemplate jdbcTemplate(DataSource dataSource) {   // injected, always the singleton
    return new JdbcTemplate(dataSource);
}
```

Boot's own auto-configurations use `proxyBeanMethods = false`, because it starts faster (no CGLIB subclass).

---

## 5. @Component vs @Bean

| | `@Component` (and stereotypes) | `@Bean` |
|---|---|---|
| Goes on | A **class** | A **method** in a `@Configuration` class |
| Who creates the object | Spring calls the constructor | **Your code** in the method body |
| Third-party classes | ✗ Can't annotate library code | ✓ The main reason it exists |
| Several beans of one type | One per class | ✓ One per method |
| Construction logic | Only through the constructor | ✓ Any code: builders, if/else, properties |
| Found by | Component scan | The config class being loaded |
| Default name | Class name, first letter lower-cased: `orderService` | Method name: `paymentsClient` |

Rule of thumb: **your own classes → stereotype annotation. Library classes or anything that needs setup → `@Bean`.**

---

## 6. The four stereotype annotations

`@Service`, `@Repository` and `@Controller` are all **meta-annotated with `@Component`**. Look at the source of `@Service`:

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Component              // ← this is why component scan finds a @Service
public @interface Service { ... }
```

So for **creating the bean**, all four are identical. They differ in **which layer they mark** and in **extra behaviour** that some of them switch on.

![Stereotype family tree: @Component at the top is a generic Spring-managed bean; @Service (business logic, no extra behaviour), @Repository (data access, adds exception translation) and @Controller (web layer, its methods are registered with DispatcherServlet) are meta-annotated with it; @RestController is @Controller plus @ResponseBody](svg/springboot/d002-stereotype-hierarchy.svg)

| Annotation | Layer | Extra behaviour Spring adds | Typical class |
|---|---|---|---|
| `@Component` | Any / generic | None | `SlugGenerator`, `JwtParser`, helpers |
| `@Service` | Business logic | **None today.** A label for readers and for AOP pointcuts | `OrderService` |
| `@Repository` | Data access | **Exception translation**: persistence exceptions → Spring's `DataAccessException` | `JpaOrderRepository` |
| `@Controller` | Web (MVC) | **Request mapping**: its `@GetMapping` etc. methods become HTTP endpoints | `OrderController` |

A layered example, top to bottom:

```java
@RestController                    // web layer: HTTP in, JSON out
@RequestMapping("/orders")
public class OrderController {
    private final OrderService orderService;

    public OrderController(OrderService orderService) { this.orderService = orderService; }

    @PostMapping
    public Order create(@RequestBody CreateOrderRequest req) {
        return orderService.place(req);
    }
}

@Service                           // business layer: rules, transactions, orchestration
public class OrderService {
    private final OrderRepository orders;

    public OrderService(OrderRepository orders) { this.orders = orders; }

    @Transactional
    public Order place(CreateOrderRequest req) {
        if (req.qty() <= 0) throw new IllegalArgumentException("qty must be positive");
        return orders.save(new Order(req.sku(), req.qty()));
    }
}

@Repository                        // data layer: talks to the database
public class OrderRepository {
    private final EntityManager em;

    public OrderRepository(EntityManager em) { this.em = em; }

    public Order save(Order order) {
        em.persist(order);
        return order;
    }
}

@Component                         // generic helper, belongs to no layer
public class OrderNumberGenerator {
    public String next() { return "ORD-" + UUID.randomUUID(); }
}
```

> [!IMPORTANT]
> Interview one-liner: **"All four make the class a bean via component scan. `@Service` is just semantic. `@Repository` adds exception translation. `@Controller` makes the methods web endpoints. `@Component` is the generic parent of all three."**

---

## 7. What @Repository adds: exception translation

Every persistence library throws its own exceptions: JPA throws `jakarta.persistence.NoResultException`, Hibernate throws `org.hibernate.exception.ConstraintViolationException`, the JDBC driver throws `SQLException` with vendor codes. If your service catches those, it is tied to that library.

Spring Boot registers a `PersistenceExceptionTranslationPostProcessor`. It wraps every `@Repository` bean in a **proxy** that catches those exceptions and rethrows them as Spring's **`DataAccessException`** family, which is the same no matter what database technology sits underneath.

```java
@Repository
public class UserRepository {
    private final EntityManager em;

    public UserRepository(EntityManager em) { this.em = em; }

    public User findByEmail(String email) {
        return em.createQuery("select u from User u where u.email = :e", User.class)
                 .setParameter("e", email)
                 .getSingleResult();      // throws NoResultException if nobody matches
    }
}

@Service
public class UserService {
    private final UserRepository users;

    public UserService(UserRepository users) { this.users = users; }

    public Optional<User> find(String email) {
        try {
            return Optional.of(users.findByEmail(email));
        } catch (EmptyResultDataAccessException e) {   // Spring's type, not JPA's
            return Optional.empty();
        }
    }
}
```

![Exception translation, before and after: without @Repository, JPA's NoResultException travels up unchanged and the service must catch a JPA type; with @Repository, a proxy added by PersistenceExceptionTranslationPostProcessor converts it to EmptyResultDataAccessException, a DataAccessException that is the same for JPA, JDBC or Mongo](svg/springboot/d003-repository-exception-translation.svg)

| Database problem | Spring exception |
|---|---|
| No row where exactly one was expected | `EmptyResultDataAccessException` |
| Unique / foreign-key constraint violated | `DataIntegrityViolationException` (`DuplicateKeyException` for duplicates) |
| Optimistic lock (`@Version`) conflict | `OptimisticLockingFailureException` |
| Lock wait timeout / deadlock | `PessimisticLockingFailureException` / `CannotAcquireLockException` |
| Can't reach the database | `DataAccessResourceFailureException` |

> [!NOTE]
> - **Spring Data repository interfaces** (`interface OrderRepository extends JpaRepository<Order, Long>`) get translation automatically. They don't need `@Repository`.
> - `JdbcTemplate` translates `SQLException` itself, even in a plain `@Component`.
> - `DataAccessException` is **unchecked**, so you only catch it where you can actually do something.

---

## 8. What @Controller adds, and @RestController

Spring MVC's `RequestMappingHandlerMapping` looks at every bean, and for each class annotated **`@Controller`** it registers the `@GetMapping` / `@PostMapping` / `@RequestMapping` methods as endpoints. Without `@Controller` the methods are never mapped and every call returns 404.

`@Controller` methods by default return a **view name** (for server-side HTML with Thymeleaf):

```java
@Controller
public class PageController {

    @GetMapping("/home")
    public String home(Model model) {
        model.addAttribute("user", "Asha");
        return "home";                       // → renders templates/home.html
    }

    @GetMapping("/api/ping")
    @ResponseBody                            // write the return value to the body instead
    public String ping() { return "pong"; }
}
```

**`@RestController` = `@Controller` + `@ResponseBody` on every method.** Return values are converted by an `HttpMessageConverter` (Jackson for objects → JSON). This is what you use for REST APIs.

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping("/{id}")
    public UserDto get(@PathVariable long id) {
        return new UserDto(id, "Asha");      // → {"id":1,"name":"Asha"}
    }
}
```

> [!CAUTION]
> Since Spring 6 (Boot 3), a class with only `@Component` + `@RequestMapping` is **not** treated as a controller anymore. The class must carry `@Controller` or `@RestController`.

---

## 9. Bean names, multiple candidates and scope

### Bean names

| Defined by | Default name | Custom name |
|---|---|---|
| `@Service class OrderService` | `orderService` | `@Service("orders")` |
| `@Bean RestClient paymentsClient()` | `paymentsClient` | `@Bean("payments")` |

### Two beans of the same type

With the two `RestClient` beans from section 4, this fails at startup with `NoUniqueBeanDefinitionException`:

```java
public PaymentService(RestClient client) { ... }   // which one? 2 candidates
```

Three ways to pick:

```java
// 1. @Qualifier: name the one you want at the injection point
public PaymentService(@Qualifier("paymentsClient") RestClient client) { ... }

// 2. @Primary: mark a default on the definition side
@Bean @Primary
public RestClient paymentsClient(...) { ... }

// 3. Parameter name matches a bean name (works, but fragile under renaming)
public PaymentService(RestClient paymentsClient) { ... }
```

`@Qualifier` beats `@Primary`. You can also inject **all** of them: `List<RestClient>` or `Map<String, RestClient>` (key = bean name). That's handy for strategy patterns, e.g. all `PaymentGateway` implementations.

### Scope

| Scope | One instance per… | Typical use |
|---|---|---|
| `singleton` (default) | ApplicationContext | Services, repositories, controllers: almost everything |
| `prototype` | Every injection / `getBean()` | Stateful, short-lived helpers |
| `request` | HTTP request | Per-request context (web apps only) |
| `session` | HTTP session | Shopping cart in a server-rendered app |
| `application` | `ServletContext` | Rare |

```java
@Component
@Scope("prototype")          // or @Scope(ConfigurableBeanFactory.SCOPE_PROTOTYPE)
public class ReportBuilder { ... }
```

> [!WARNING]
> ⚠️ A singleton is shared by **every request thread at once**. Keep it **stateless**: no mutable fields holding per-request data. Fields should be `final` dependencies only.

---

## 10. Lazy vs eager bean initialization

**Eager** (the default for singletons): Spring creates **every** singleton bean during startup, inside `refresh()`, before the app takes traffic. **Lazy**: the bean is created only when something **first needs it**.

![Eager vs lazy bean initialization: eagerly, refresh() creates all singletons including pdfReportService before the app is ready, so startup is slower but config errors fail before traffic and the first request is fast; lazily, refresh() skips pdfReportService, the app is ready sooner, and the bean is created on the first request that uses it, which makes that first call slow and means a broken bean only fails in production; @Lazy on an injection point injects a proxy, and a lazy bean is then created on the first method call](svg/springboot/d011-bean-eager-vs-lazy.svg)

| | Eager (default) | Lazy |
|---|---|---|
| Created | At startup, all at once | On first use |
| Startup time | Slower | Faster |
| First request | Fast: everything is ready | Slower: beans get built during the request |
| A misconfigured bean | **Fails at startup**, before any traffic ✓ | Fails later, on the first request that needs it ✗ |
| Memory | Every bean exists, even unused ones | Only beans that were used |

### Making one bean lazy

```java
@Service
@Lazy                                             // don't create at startup
public class PdfReportService {
    public PdfReportService() {
        System.out.println("PdfReportService created");   // heavy: loads fonts and templates
    }

    public byte[] render() { ... }
}

@RestController
public class ReportController {
    private final PdfReportService pdf;

    public ReportController(@Lazy PdfReportService pdf) {   // ← @Lazy here too: inject a proxy
        this.pdf = pdf;
    }

    @GetMapping("/reports/pdf")
    public byte[] pdf() { return pdf.render(); }  // first call creates the real bean
}
```

```text
Started ShopApplication in 1.4 seconds
                                                  ← no "PdfReportService created" yet
GET /reports/pdf
PdfReportService created                          ← built on the first request
```

> [!WARNING]
> ⚠️ `@Lazy` on the class alone is **not enough** if an eager bean injects it normally. `ReportController` is created at startup, it needs a `PdfReportService`, so Spring builds it right then and the `@Lazy` does nothing. Put `@Lazy` on the **injection point** as well: Spring then injects a small proxy, and because the bean itself is lazy, it's created on the first method call. (`@Lazy` on the injection point alone, with a normal eager bean behind it, only delays the lookup; the bean is still built at startup.) `ObjectProvider<PdfReportService>` works too.

### Making everything lazy

```yaml
spring:
  main:
    lazy-initialization: true      # all beans lazy; opt a bean out with @Lazy(false)
```

Good for **local development and tests** (faster restarts). Risky in **production**: a missing property or broken bean is no longer caught at startup, the first requests are slow (bad with autoscaling, see JVM warm-up in the Java notes), and a health check can pass while half the app was never built.

When `@Lazy` makes sense:

- A **heavy bean that's rarely used** (PDF engine, ML model, big in-memory index).
- An **optional integration** that may never be called in some deployments.
- Breaking a **circular dependency** as a stop-gap (`@Lazy` on one constructor parameter). Fix the design afterwards.

`prototype` beans are always created on demand, so lazy/eager only matters for singletons.

---

## 11. Conditional beans and other ways to register

Beans can be switched on and off by profile, property, classpath or the presence of other beans.

```java
@Configuration
public class PaymentConfig {

    @Bean
    @Profile("!prod")                                   // every profile except prod
    public PaymentGateway fakeGateway() { return new FakePaymentGateway(); }

    @Bean
    @Profile("prod")
    public PaymentGateway stripeGateway(StripeProperties props) { return new StripeGateway(props); }

    @Bean
    @ConditionalOnProperty(name = "shop.audit.enabled", havingValue = "true")
    public AuditListener auditListener() { return new AuditListener(); }

    @Bean
    @ConditionalOnMissingBean                           // only if nobody else defined an ObjectMapper
    public ObjectMapper objectMapper() { return new ObjectMapper(); }
}
```

| Annotation | Creates the bean only if… |
|---|---|
| `@Profile("prod")` | That profile is active |
| `@ConditionalOnProperty` | A property has a given value |
| `@ConditionalOnClass` | A class is on the classpath |
| `@ConditionalOnMissingBean` | No other bean of that type exists |
| `@ConditionalOnBean` | Some other bean exists |
| `@ConditionalOnWebApplication` | It's a web app |

Less common ways to get beans in:

- **`@Import(SomeConfig.class)`**: pull in a `@Configuration` class that component scan doesn't reach (e.g. from a library).
- **`@ConfigurationPropertiesScan` / `@EnableConfigurationProperties`**: register `@ConfigurationProperties` classes as beans.
- **Programmatic registration** with `BeanRegistrar` (Spring 7) or `GenericApplicationContext.registerBean(...)`: for frameworks that register beans in a loop. Rare in application code.
- **XML** (`<bean id="..." class="..."/>`): only in old apps. Not used in new Boot code.

---

## 12. Bean interview questions

<details>
<summary><b>Q1. What's the difference between @Component, @Service, @Repository and @Controller?</b></summary>

All four register the class as a bean through component scanning, because the last three are meta-annotated with `@Component`. `@Component` is the generic one. `@Service` marks the business layer and adds no behaviour. `@Repository` marks the data layer and enables **exception translation** into `DataAccessException`. `@Controller` marks the web layer: Spring MVC registers its handler methods as endpoints. `@RestController` is `@Controller` + `@ResponseBody`.
</details>

<details>
<summary><b>Q2. Can I just use @Component everywhere?</b></summary>

For a service, yes: nothing changes except readability. For a repository you lose exception translation (unless it's a Spring Data interface or uses `JdbcTemplate`). For a controller, **no**: since Spring 6 only classes with `@Controller` / `@RestController` are scanned for request mappings, so the endpoints would return 404. Use the specific annotation: it documents the layer and lets you target layers with AOP (e.g. log every `@Service` method).
</details>

<details>
<summary><b>Q3. @Component vs @Bean?</b></summary>

`@Component` goes on a class and Spring calls its constructor. `@Bean` goes on a method in a `@Configuration` class and your code builds the object. Use `@Bean` for third-party classes you can't annotate, for several beans of the same type, or when construction needs logic. The default name is the class name (`orderService`) for `@Component` and the method name for `@Bean`.
</details>

<details>
<summary><b>Q4. My bean isn't found: NoSuchBeanDefinitionException. Why?</b></summary>

Usual causes: the class is outside the main class's package tree, so component scan misses it; it has no stereotype annotation; a `@Profile` / `@Conditional…` excluded it; or you're asking for the concrete class while the bean is a JDK proxy that only implements the interface. Fix the package (or `scanBasePackages`), add the annotation, or check the conditions report (`--debug`).
</details>

<details>
<summary><b>Q5. Two beans implement the same interface. What happens on injection, and how do you fix it?</b></summary>

Startup fails with `NoUniqueBeanDefinitionException`. Use `@Qualifier("name")` at the injection point, `@Primary` on the default bean, or inject `List<Interface>` / `Map<String, Interface>` to get all of them. `@Qualifier` wins over `@Primary`.
</details>

<details>
<summary><b>Q6. What's the default bean scope? Are singleton beans thread-safe?</b></summary>

Singleton: one instance per ApplicationContext, created at startup. Spring does **nothing** to make it thread-safe. It's shared by all request threads, so it's safe only if it's stateless (only `final` dependency fields). Per-request data belongs in local variables or method parameters.
</details>

<details>
<summary><b>Q7. In a @Configuration class, one @Bean method calls another. Do you get two instances?</b></summary>

No, with the default `@Configuration` (`proxyBeanMethods = true`): the class is CGLIB-subclassed and the call returns the existing singleton. Yes, in lite mode (`proxyBeanMethods = false`, or `@Bean` methods in a `@Component`): it's a plain Java call that creates a new unmanaged object. Safest: take the dependency as a method parameter instead of calling the method.
</details>

<details>
<summary><b>Q8. Does a Spring Data JPA repository interface need @Repository?</b></summary>

No. `@EnableJpaRepositories` (switched on by Boot's auto-configuration) finds interfaces extending `Repository`/`JpaRepository`, generates a proxy implementation for each, registers it as a bean and applies exception translation. Adding `@Repository` doesn't hurt, it's just redundant.
</details>

<details>
<summary><b>Q9. @Controller vs @RestController?</b></summary>

`@Controller` methods return a view name rendered by a template engine, unless the method has `@ResponseBody`. `@RestController` puts `@ResponseBody` on every method, so return values are serialized (to JSON by Jackson) into the response body. Use `@RestController` for APIs, `@Controller` for server-rendered pages.
</details>

<details>
<summary><b>Q10. Are beans created lazily or eagerly? When would you use @Lazy?</b></summary>

Singletons are created **eagerly** at startup, so wiring and config errors fail before the app takes traffic, and the first request is fast. `@Lazy` delays creation until first use: useful for heavy, rarely used beans or optional integrations. Put it on the injection point too, otherwise an eager bean that injects it forces creation at startup anyway. `spring.main.lazy-initialization=true` makes everything lazy: nice for dev, risky in production because errors and slowness move to the first requests. Prototype beans are always created on demand.
</details>

---

## 13. Bean cheat sheet

| Topic | Remember |
|---|---|
| Bean | Object created, wired and managed by the Spring container |
| IoC / DI | Container creates objects; dependencies come in through the constructor |
| Ways to define | Stereotype + component scan · `@Bean` method · auto-configuration |
| Component scan | Main class's package **and below** only |
| `@Component` | Generic bean. Parent of the other three |
| `@Service` | Business layer. No extra behaviour |
| `@Repository` | Data layer + exception translation → `DataAccessException` |
| `@Controller` | Web layer. Methods become endpoints. Returns view names |
| `@RestController` | `@Controller` + `@ResponseBody` → JSON |
| `@Bean` | Method in `@Configuration`. Third-party classes, setup logic, several of one type |
| Default names | `orderService` (class) · method name (`@Bean`) |
| Two candidates | `@Qualifier` > `@Primary`, or inject `List<T>` |
| Default scope | Singleton, shared by all threads → keep it stateless |
| Full vs lite | `@Configuration` proxies `@Bean` calls. Better: inject as parameters |
| Constructor injection | One constructor → no `@Autowired` needed |
| Eager vs lazy | Singletons eager at startup (fail fast). `@Lazy` on class **and** injection point, or `spring.main.lazy-initialization` |

---

# @SpringBootApplication and Startup

## 1. @SpringBootApplication: three annotations in one

```java
@SpringBootApplication
public class ShopApplication {
    public static void main(String[] args) {
        SpringApplication.run(ShopApplication.class, args);
    }
}
```

`@SpringBootApplication` is a **combination of 3 Spring annotations**:

| Annotation | What it does |
|---|---|
| `@SpringBootConfiguration` | Marks the class as a `@Configuration`, so it can hold `@Bean` methods. (It's a specialised `@Configuration`, which is a `@Component`.) |
| `@EnableAutoConfiguration` | Turns on auto-configuration: loads the auto-configuration classes that starters ship and keeps the ones whose conditions match |
| `@ComponentScan` | Scans the main class's package and its sub-packages for `@Component` classes |

So this is equivalent:

```java
@SpringBootConfiguration
@EnableAutoConfiguration
@ComponentScan
public class ShopApplication { ... }
```

Its source also carries 4 plain Java meta-annotations (`@Target`, `@Retention`, `@Documented`, `@Inherited`). Those only say "goes on a class, visible at runtime", so the interview answer is **three**.

![Anatomy of @SpringBootApplication: one annotation that equals three — @SpringBootConfiguration (a @Configuration, so the class can hold @Bean methods), @EnableAutoConfiguration (imports auto-configurations via AutoConfigurationImportSelector and keeps those whose conditions match) and @ComponentScan (scans the main package and below) — plus the plain Java meta-annotations @Target, @Retention, @Documented and @Inherited](svg/springboot/d004-springbootapplication-anatomy.svg)

Useful attributes:

```java
@SpringBootApplication(
    scanBasePackages = {"com.example.shop", "com.example.common"},   // widen component scan
    exclude = DataSourceAutoConfiguration.class                      // switch off one auto-config
)
```

---

## 2. What happens when the app starts, step by step

Everything starts from `SpringApplication.run(ShopApplication.class, args)`.

![Spring Boot startup sequence: run() detects the app type and loads listeners, prepares the Environment, prints the banner, creates the ApplicationContext, then refresh() reads config classes into bean definitions, creates the embedded Tomcat, creates all singleton beans and starts the web server; then the started log line, ApplicationRunner and CommandLineRunner beans, and finally ApplicationReadyEvent with readiness ACCEPTING_TRAFFIC; each step publishes an event, and a failure publishes ApplicationFailedEvent](svg/springboot/d005-startup-sequence.svg)

1. **Create `SpringApplication`.** Boot looks at the classpath to decide the **app type**: Spring MVC on the classpath → servlet web app; only WebFlux → reactive; neither → plain (no web server). It loads initializers and listeners registered by the libraries.
2. **Prepare the `Environment`.** All configuration is gathered into one place: command-line arguments, environment variables, system properties, `application.yml` / `application.properties`, and the profile-specific files (`application-prod.yml`). Active profiles are decided here.
3. **Print the banner.**
4. **Create the `ApplicationContext`.** For a servlet app it's a web-server-aware context. Initializers run, and the main class is registered as the first configuration source.
5. **`refresh()`: the big step.** Most of startup time is spent here.
   1. **Read configuration into bean definitions.** `ConfigurationClassPostProcessor` processes the main class: `@ComponentScan` finds your classes, `@Bean` methods are read, `@Import`s are followed, and then **auto-configurations** are loaded and their `@Conditional…` checks are evaluated. The result is a list of bean definitions. No objects yet.
   2. **Register `BeanPostProcessor`s**: the hooks that later handle `@Autowired`, `@PostConstruct`, `@Transactional`, `@Async`…
   3. **Create the embedded web server** (Tomcat by default), not started yet.
   4. **Create every singleton bean**, in dependency order. For each bean: call the constructor (injecting dependencies) → run `@PostConstruct` → wrap it in an AOP proxy if it needs one (`@Transactional`, `@Async`, `@Cacheable`).
   5. **Start the web server.** The port opens ("Tomcat started on port 8080"). `ContextRefreshedEvent` is published.
6. **Log "Started ShopApplication in 2.1 seconds"** and publish `ApplicationStartedEvent`.
7. **Run `ApplicationRunner` and `CommandLineRunner` beans.**
8. **Ready.** `ApplicationReadyEvent` is published and the readiness state becomes `ACCEPTING_TRAFFIC` (what `/actuator/health/readiness` reports to Kubernetes).

If anything fails along the way (a missing bean, a port already in use), Boot publishes `ApplicationFailedEvent`, a **failure analyzer** prints a readable "APPLICATION FAILED TO START" report with the cause and a suggested action, and the app exits.

```text
***************************
APPLICATION FAILED TO START
***************************

Description:
Web server failed to start. Port 8080 was already in use.

Action:
Identify and stop the process that's listening on port 8080 or configure this application to listen on another port.
```

> [!TIP]
> Interview version in one breath: **"`run()` detects the app type, builds the Environment from all property sources, creates the ApplicationContext and refreshes it. Refresh scans components and evaluates auto-configurations into bean definitions, creates the embedded server, instantiates and wires all singletons with their proxies, then starts the server. Finally runners run and the app is marked ready."**

---

## 3. Auto-configuration: how Boot decides what to create

Add `spring-boot-starter-data-jpa` and you get a `DataSource`, a connection pool, an `EntityManagerFactory` and a transaction manager without writing any config. How?

1. A **starter** is just a dependency bundle: it pulls in the libraries (Hibernate, HikariCP, Spring Data JPA) and Boot's auto-configuration module.
2. Each auto-configuration module lists its classes in `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`.
3. `@EnableAutoConfiguration` reads every such file on the classpath. That's well over a hundred candidate classes.
4. Each candidate is a normal configuration class full of `@Bean` methods, guarded by **conditions**. Only those whose conditions pass are applied.
5. Auto-configurations are processed **after** your own configuration, so `@ConditionalOnMissingBean` can see your beans and **back off**.

A simplified auto-configuration:

```java
@AutoConfiguration
@ConditionalOnClass(DataSource.class)                     // JDBC on the classpath?
@EnableConfigurationProperties(DataSourceProperties.class)
public class DataSourceAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean(DataSource.class)           // you didn't define your own?
    public HikariDataSource dataSource(DataSourceProperties props) {
        return props.initializeDataSourceBuilder().type(HikariDataSource.class).build();
    }
}
```

![How one auto-configuration decides, using DataSource: with the JPA starter on the classpath, DataSourceAutoConfiguration checks @ConditionalOnClass (class missing → skipped), then @ConditionalOnMissingBean (you defined your own → Boot backs off and yours wins), then whether a URL or embedded database is available (no → startup fails with "Failed to configure a DataSource"); if all pass it creates a HikariDataSource from spring.datasource properties](svg/springboot/d006-auto-configuration-conditions.svg)

To see every decision, start with `--debug` (prints the **CONDITIONS EVALUATION REPORT**: positive matches, negative matches and why) or call `/actuator/conditions`.

To switch one off:

```yaml
spring:
  autoconfigure:
    # full class name; Boot 4 moved it to org.springframework.boot.jdbc.autoconfigure
    exclude: org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
```

---

## 4. Running your own code at startup

| Hook | Runs | Use it for |
|---|---|---|
| `@PostConstruct` on a bean | Right after **that bean** is created and injected | Validate the bean's own config, build an in-memory index |
| `ApplicationRunner` / `CommandLineRunner` | After the context is fully started, **before** the app is marked ready | Warm caches, run a one-off job, warm-up calls |
| `@EventListener(ApplicationReadyEvent.class)` | After the app is ready and taking traffic | Things that must not delay readiness: register with a service registry, send "I'm up" |

```java
@Component
public class CacheWarmer implements ApplicationRunner {
    private final ProductService products;

    public CacheWarmer(ProductService products) { this.products = products; }

    @Override
    public void run(ApplicationArguments args) {
        products.loadTopSellers();        // readiness waits for this to finish
    }
}

@Component
public class StartupNotifier {
    @EventListener(ApplicationReadyEvent.class)
    public void onReady() {
        System.out.println("Ready to serve traffic");
    }
}
```

`ApplicationRunner` gets parsed arguments (`args.getOptionValues("mode")`); `CommandLineRunner` gets the raw `String... args`. Several runners are ordered with `@Order`.

> [!WARNING]
> ⚠️ Don't rely on `@Transactional` inside `@PostConstruct`. Calling your own transactional method from there is self-invocation (the proxy isn't involved), and the context isn't fully started yet. Do database work and warm-up calls in a runner.

---

## 5. Startup interview questions

<details>
<summary><b>Q1. @SpringBootApplication is a combination of which annotations?</b></summary>

Three: `@SpringBootConfiguration` (the class is a `@Configuration`), `@EnableAutoConfiguration` (turn on auto-configuration) and `@ComponentScan` (scan the main package and below). Its source also has the Java meta-annotations `@Target`, `@Retention`, `@Documented` and `@Inherited`, but those don't add Spring behaviour.
</details>

<details>
<summary><b>Q2. Walk me through what happens when a Spring Boot app starts.</b></summary>

`SpringApplication.run()` detects the app type from the classpath, prepares the Environment (args, env vars, `application.yml`, profiles), prints the banner and creates the ApplicationContext. `refresh()` then turns component scan, `@Bean` methods and matching auto-configurations into bean definitions, creates the embedded server, instantiates all singletons (constructor → injection → `@PostConstruct` → proxies) and starts the server. Then `ApplicationStartedEvent`, the runners, and `ApplicationReadyEvent`.
</details>

<details>
<summary><b>Q3. How does auto-configuration work?</b></summary>

Starters bring auto-configuration classes, listed in `META-INF/spring/…AutoConfiguration.imports`. `@EnableAutoConfiguration` loads all candidates, and each is applied only if its `@Conditional…` annotations match: class on the classpath, property set, **no user bean of that type**. They're processed after user config so your beans win.
</details>

<details>
<summary><b>Q4. How do you override or disable an auto-configured bean?</b></summary>

Override: define your own bean of that type. `@ConditionalOnMissingBean` makes Boot back off. Tweak: most auto-configured beans read properties (`spring.datasource.hikari.maximum-pool-size`), or offer customizer beans (e.g. `RestClientCustomizer`, which adjusts the auto-configured `RestClient.Builder`). Disable completely: `@SpringBootApplication(exclude = …)` or `spring.autoconfigure.exclude`.
</details>

<details>
<summary><b>Q5. How do you find out why an auto-configuration did or didn't apply?</b></summary>

Run with `--debug` (or `debug=true`) to print the Conditions Evaluation Report, or call `/actuator/conditions` on a running app. Each auto-configuration is listed with the conditions that matched or failed.
</details>

<details>
<summary><b>Q6. What is a starter?</b></summary>

A dependency bundle for one feature: `spring-boot-starter-web` brings Spring MVC, Jackson and embedded Tomcat with compatible versions. Combined with auto-configuration, adding the starter is usually all you need. Versions come from Boot's dependency management, so you don't specify them.
</details>

<details>
<summary><b>Q7. CommandLineRunner vs ApplicationRunner vs @PostConstruct vs ApplicationReadyEvent?</b></summary>

`@PostConstruct` runs per bean, right after it's wired, before the rest of the app exists. The runners run once the whole context has started, before readiness, so they suit warm-up and one-off jobs (`ApplicationRunner` gets parsed args, `CommandLineRunner` raw args). An `ApplicationReadyEvent` listener runs after the app is ready, for work that shouldn't delay traffic.
</details>

<details>
<summary><b>Q8. How would you make startup faster?</b></summary>

Remove unused starters (fewer auto-configurations), narrow component scan, use `spring.main.lazy-initialization=true` in dev (moves cost to the first request, so avoid it in prod), use Class Data Sharing (CDS), or compile to a GraalVM native image with Spring AOT for millisecond startup. Measure first with the `/actuator/startup` endpoint (`BufferingApplicationStartup`).
</details>

---

## 6. Startup cheat sheet

| Topic | Remember |
|---|---|
| `@SpringBootApplication` | `@SpringBootConfiguration` + `@EnableAutoConfiguration` + `@ComponentScan` |
| App type | Detected from classpath: servlet / reactive / none |
| Environment | Args, env vars, system props, `application.yml`, profile files |
| `refresh()` | Bean definitions → post-processors → web server created → singletons → server started |
| Bean creation | Constructor → inject → `@PostConstruct` → proxy |
| Auto-config list | `META-INF/spring/…AutoConfiguration.imports` |
| Your bean wins | `@ConditionalOnMissingBean` + auto-config runs after user config |
| Debug conditions | `--debug` or `/actuator/conditions` |
| Disable auto-config | `exclude = …` or `spring.autoconfigure.exclude` |
| Startup hooks | `@PostConstruct` (per bean) → runners (before ready) → `ApplicationReadyEvent` |
| Event order | Starting → EnvironmentPrepared → ContextInitialized → Prepared → (Refreshed) → Started → Ready |
| Failure | `ApplicationFailedEvent` + failure analyzer report |

---

# The 10 Most Used Annotations

## 1. Where the annotations fit

![Where the 10 most used annotations live: an HTTP POST /orders hits the @RestController (with @PostMapping, @RequestBody, @PathVariable, @RequestParam), which calls the @Service (@Transactional), which calls the @Repository and the database, all wired with constructor injection; exceptions go to a @RestControllerAdvice with @ExceptionHandler that returns a JSON error; at startup @SpringBootApplication, @Configuration with @Bean, and @Value / @ConfigurationProperties set things up](svg/springboot/d007-annotation-map.svg)

---

## 2. The top 10, one by one

### 1. @SpringBootApplication

Goes on the main class. = `@SpringBootConfiguration` + `@EnableAutoConfiguration` + `@ComponentScan` (see [the startup part](#1-springbootapplication-three-annotations-in-one)).

```java
@SpringBootApplication
public class ShopApplication {
    public static void main(String[] args) { SpringApplication.run(ShopApplication.class, args); }
}
```

### 2. @RestController

Makes a class a REST controller: its methods handle HTTP requests and their return values are written as JSON.

```java
@RestController
@RequestMapping("/api/orders")          // common URL prefix for every method in the class
public class OrderController { ... }
```

### 3. @GetMapping / @PostMapping / @PutMapping / @PatchMapping / @DeleteMapping

Map an HTTP method + path to a Java method. They're shortcuts for `@RequestMapping(method = …)`.

```java
@GetMapping("/{id}")                    // GET    /api/orders/42
public OrderDto get(@PathVariable long id) { ... }

@PostMapping                            // POST   /api/orders
@ResponseStatus(HttpStatus.CREATED)     // 201 instead of 200
public OrderDto create(@Valid @RequestBody CreateOrderRequest req) { ... }

@DeleteMapping("/{id}")                 // DELETE /api/orders/42
public ResponseEntity<Void> delete(@PathVariable long id) {
    orderService.delete(id);
    return ResponseEntity.noContent().build();   // 204
}
```

### 4. @PathVariable / @RequestParam / @RequestBody

Bind parts of the request to method parameters.

| Annotation | Reads from | Example URL / body | Typical use |
|---|---|---|---|
| `@PathVariable` | The URL path | `/orders/42` → `42` | Identify **one** resource |
| `@RequestParam` | The query string | `/orders?status=PAID&page=2` | Filter, sort, paginate |
| `@RequestBody` | The JSON body | `{"sku":"A1","qty":2}` → a record | Create / update payloads |

```java
@GetMapping
public List<OrderDto> search(@RequestParam(defaultValue = "PAID") String status,
                             @RequestParam(required = false) Integer page) { ... }

public record CreateOrderRequest(@NotBlank String sku, @Positive int qty) { }
```

`@RequestHeader("X-Request-Id")` and `@CookieValue` work the same way for headers and cookies.

### 5. @Service / @Component / @Repository

Register your classes as beans, one annotation per layer. Covered in [the four stereotype annotations](#6-the-four-stereotype-annotations).

### 6. @Autowired

Asks Spring to inject a dependency. **With a single constructor you don't need it at all**; Spring uses the constructor automatically. You'll still see it on fields in older code and in tests.

```java
@Service
public class OrderService {
    private final OrderRepository orders;

    public OrderService(OrderRepository orders) {   // implicit @Autowired
        this.orders = orders;
    }
}

// ❌ Field injection: works, but hides dependencies, can't be final, hard to unit-test
@Autowired
private OrderRepository orders;
```

### 7. @Configuration + @Bean

Define beans with Java code: third-party classes, several instances of one type, objects with setup logic. Covered in [Way 2](#4-way-2-bean-methods-in-a-configuration-class).

```java
@Configuration
public class TimeConfig {
    @Bean
    public Clock clock() { return Clock.systemUTC(); }
}
```

### 8. @Value / @ConfigurationProperties

Read configuration from `application.yml`, environment variables, etc.

```yaml
payments:
  base-url: https://pay.example.com
  timeout: 2s
  retries: 3
```

```java
// @Value: one value, fine for a single setting
@Value("${payments.base-url}")
private String baseUrl;

@Value("${payments.retries:3}")          // ":3" = default if the property is missing
private int retries;

// @ConfigurationProperties: a typed, validated group. Preferred for anything with 2+ settings
@ConfigurationProperties(prefix = "payments")
@Validated
public record PaymentsProperties(@NotBlank String baseUrl, Duration timeout, int retries) { }

@SpringBootApplication
@ConfigurationPropertiesScan            // registers every @ConfigurationProperties class as a bean
public class ShopApplication { ... }
```

`base-url` in YAML binds to `baseUrl` (relaxed binding), and `2s` binds to a `Duration`. The env var `PAYMENTS_BASEURL` overrides it.

### 9. @Transactional

Runs the method in a database transaction: commit if it returns normally, rollback if it throws a `RuntimeException`.

```java
@Service
public class TransferService {

    @Transactional
    public void transfer(long from, long to, BigDecimal amount) {
        accounts.debit(from, amount);
        accounts.credit(to, amount);      // throws → the debit is rolled back too
    }

    @Transactional(readOnly = true)       // hint: no writes, lets Hibernate skip dirty checking
    public BigDecimal balance(long id) { ... }
}
```

It works through a proxy, so it has traps (self-invocation, checked exceptions). See [the common error with self-calls](#2-common-error-calling-an-annotated-method-from-the-same-class) and [the proxy questions](#3-proxies-transactional-and-async).

### 10. @RestControllerAdvice + @ExceptionHandler

One central place that turns exceptions into HTTP error responses, so controllers don't need try/catch.

```java
@RestControllerAdvice
public class ApiExceptionHandler {

    @ExceptionHandler(OrderNotFoundException.class)
    public ProblemDetail notFound(OrderNotFoundException ex) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
    }

    @ExceptionHandler(DataIntegrityViolationException.class)
    public ProblemDetail conflict(DataIntegrityViolationException ex) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.CONFLICT, "Order already exists");
    }
}
```

`ProblemDetail` is the standard error JSON (RFC 9457): `{"type":"about:blank","title":"Not Found","status":404,"detail":"Order 42 not found","instance":"/api/orders/42"}`.

---

## 3. Next 10 worth knowing

| Annotation | Use |
|---|---|
| `@Qualifier` / `@Primary` | Choose between several beans of the same type |
| `@Profile("prod")` | Create a bean only when a profile is active |
| `@ConditionalOnProperty` | Create a bean only when a property is set |
| `@Valid` / `@Validated` | Trigger Bean Validation (`@NotBlank`, `@Email`, `@Positive`…) on a request body or a properties class → 400 on failure |
| `@Async` (+ `@EnableAsync`) | Run the method on another thread; return `void` or `CompletableFuture` |
| `@Scheduled` (+ `@EnableScheduling`) | Run a method on a fixed rate or cron: `@Scheduled(cron = "0 0 * * * *")` |
| `@Cacheable` (+ `@EnableCaching`) | Cache a method's result by its arguments |
| `@EventListener` | React to application events (yours or Spring's) |
| `@SpringBootTest` | Full integration test: starts the whole context |
| `@WebMvcTest` / `@DataJpaTest` + `@MockitoBean` | Slice tests: only the web or JPA layer, with mocked collaborators |

---

## 4. Annotation cheat sheet

| # | Annotation | One-line use |
|---|---|---|
| 1 | `@SpringBootApplication` | Main class: config + auto-config + component scan |
| 2 | `@RestController` | Class handles HTTP, returns JSON |
| 3 | `@GetMapping` / `@PostMapping`… | Map HTTP method + path to a method |
| 4 | `@PathVariable` / `@RequestParam` / `@RequestBody` | Bind path / query string / JSON body |
| 5 | `@Service` / `@Component` / `@Repository` | Register your class as a bean, by layer |
| 6 | `@Autowired` | Inject a dependency (implicit with one constructor) |
| 7 | `@Configuration` + `@Bean` | Define beans in Java code |
| 8 | `@Value` / `@ConfigurationProperties` | Read config: one value / typed group |
| 9 | `@Transactional` | Commit or roll back a method as one DB transaction |
| 10 | `@RestControllerAdvice` + `@ExceptionHandler` | Central exception → HTTP error mapping |

---

# Famous Spring Boot Interview Questions

Classic questions that didn't fit in the parts above, grouped by topic.

## 1. Core container and dependency injection

<details>
<summary><b>Q1. What's the difference between Spring and Spring Boot?</b></summary>

Spring Framework is the core: IoC container, DI, AOP, transactions, Spring MVC. Spring Boot sits on top and removes setup work: **auto-configuration** (beans created from the classpath), **starters** (curated dependency sets with matching versions), an **embedded server** (run with `java -jar`, no external Tomcat), externalized config and **Actuator** for production. Boot isn't a different framework. It's Spring with sensible defaults.
</details>

<details>
<summary><b>Q2. BeanFactory vs ApplicationContext?</b></summary>

`BeanFactory` is the basic container: it creates and wires beans, lazily on first request. `ApplicationContext` extends it and adds eager singleton creation at startup (so config errors fail fast), events, internationalization (`MessageSource`), resource loading, environment/profiles and automatic registration of post-processors. Boot always uses an `ApplicationContext`.
</details>

<details>
<summary><b>Q3. Constructor, setter or field injection: which and why?</b></summary>

**Constructor injection.** Dependencies are explicit and can be `final` (immutable, thread-safe to share), the object can't exist half-wired, unit tests just call `new OrderService(mockRepo)` without Spring, and too many constructor parameters is a visible smell. Setter injection only for truly optional dependencies. Avoid field injection (`@Autowired` on a field): hidden dependencies, not `final`, needs reflection or Spring to test.
</details>

<details>
<summary><b>Q4. Explain the bean lifecycle.</b></summary>

1. **Instantiate**: constructor called, constructor dependencies injected.
2. **Populate**: setter/field injection.
3. **Aware callbacks**: `BeanNameAware`, `ApplicationContextAware`… if implemented.
4. **`BeanPostProcessor.postProcessBeforeInitialization`**: this is where `@PostConstruct` runs.
5. **Init**: `InitializingBean.afterPropertiesSet()`, then a custom `initMethod`.
6. **`BeanPostProcessor.postProcessAfterInitialization`**: AOP proxies (`@Transactional`, `@Async`) are created here, so other beans get the proxy.
7. **In use.**
8. **Shutdown**: `@PreDestroy` → `DisposableBean.destroy()` → custom `destroyMethod`.

Prototype beans get steps 1–7 only. Spring doesn't track them, so no destroy callbacks.
</details>

<details>
<summary><b>Q5. You inject a prototype bean into a singleton. What happens?</b></summary>

You get **one** prototype instance, created when the singleton was created, and reused forever. The singleton is wired only once. To get a fresh instance each time, inject `ObjectProvider<ReportBuilder>` and call `getObject()`, use a `@Lookup` method, or make the prototype a scoped proxy.

```java
@Service
public class ReportService {
    private final ObjectProvider<ReportBuilder> builders;

    public ReportService(ObjectProvider<ReportBuilder> builders) { this.builders = builders; }

    public Report build() {
        ReportBuilder b = builders.getObject();   // new prototype instance every call
        return b.title("Daily").build();
    }
}
```
</details>

<details>
<summary><b>Q6. What is a circular dependency and how does Spring Boot handle it?</b></summary>

A needs B and B needs A. With constructor injection it can never be built: startup fails with `BeanCurrentlyInCreationException` ("The dependencies of some of the beans form a cycle"). Since Boot 2.6, circular references are forbidden by default even for field injection (`spring.main.allow-circular-references=false`). The real fix is design: extract the shared logic into a third bean, or decouple with events. `@Lazy` on one parameter (injects a proxy) is a workaround, not a fix.
</details>

<details>
<summary><b>Q7. What is AOP and where does Spring use it?</b></summary>

Aspect-Oriented Programming adds behaviour around methods without changing them: "cross-cutting concerns". Spring does it with **proxies**: callers get a proxy that runs the extra logic (the advice) and then calls the real method. Spring itself uses this for `@Transactional`, `@Async`, `@Cacheable`, `@PreAuthorize` and `@Retryable`. You can write your own with `@Aspect` + `@Around("@within(org.springframework.stereotype.Service)")`, e.g. to time every service method.
</details>

---

## 2. Common error: calling an annotated method from the same class

The most common Spring bug. You put `@Transactional` (or `@Async`, `@Cacheable`…) on a method, call it from **another method of the same class**, and the annotation does **nothing**. No error, no warning.

### The broken code

```java
@Service
public class OrderService {
    private final OrderRepository orders;
    private final StockClient stock;

    public OrderService(OrderRepository orders, StockClient stock) {
        this.orders = orders;
        this.stock = stock;
    }

    public void placeOrder(Order order) {        // called by the controller, no annotation
        validate(order);
        saveOrder(order);                        // same as this.saveOrder(order)  ❌
    }

    @Transactional
    public void saveOrder(Order order) {
        orders.save(order);
        stock.reserve(order);                    // throws → orders.save(...) is NOT rolled back
    }
}
```

The controller calls `placeOrder()`, which calls `saveOrder()`. You'd expect a transaction around `saveOrder()`. There is none: the order row stays in the database even though reserving stock failed.

### Why: the annotation lives in the proxy, not in your class

Annotations like `@Transactional` don't change your method. At startup Spring creates your `OrderService` object and then wraps it in a **proxy** (a generated subclass). The proxy is what gets injected into the controller. Roughly what Spring generates:

```java
// Simplified: what the CGLIB proxy does
class OrderService$$SpringCGLIB$$0 extends OrderService {
    private final OrderService target;            // your real object

    @Override
    public void saveOrder(Order order) {          // annotated → extra logic around the call
        TransactionStatus tx = txManager.getTransaction(definition);
        try {
            target.saveOrder(order);
            txManager.commit(tx);
        } catch (RuntimeException e) {
            txManager.rollback(tx);
            throw e;
        }
    }

    @Override
    public void placeOrder(Order order) {         // not annotated → just forwards
        target.placeOrder(order);
    }
}
```

Follow the call:

1. The controller calls `placeOrder()` **on the proxy**. It isn't annotated, so the proxy simply forwards it to the real object.
2. Now we're **inside the real object**. There, `this` is the real object, not the proxy.
3. `this.saveOrder()` is a plain Java method call on the real object. It **never goes back through the proxy**, so the transaction code never runs.

The annotation only works when the call **comes in from outside, through the proxy**.

![Why this.method() skips @Transactional: a call from the controller goes through the CGLIB proxy, which begins and commits the transaction around saveOrder(); but when placeOrder() calls this.saveOrder() inside the real object, the call never goes through the proxy, so no transaction is applied; fixes are moving the method to another bean, self-injection, or TransactionTemplate](svg/springboot/d008-proxy-self-invocation.svg)

### Which annotations are affected

Everything that Spring implements with a proxy:

| Annotation | What silently doesn't happen on a self-call |
|---|---|
| `@Transactional` | No transaction: no rollback, each repository call commits on its own |
| `@Async` | Runs **synchronously** on the caller's thread |
| `@Cacheable` / `@CacheEvict` | Cache never read or cleared |
| `@Retryable` | No retries |
| `@PreAuthorize` / `@Secured` | **No security check** (a real security hole) |
| `@Validated` method validation | Arguments not validated |
| Your own `@Aspect` advice | Not applied |

### The same trap in other forms

The annotation is also ignored when:

- the method is **`private`**: the proxy subclass can't override it.
- the method or class is **`final`**: CGLIB can't override it. Kotlin classes are final by default, which is why Spring's Kotlin plugin opens them.
- you created the object with **`new`**: it's not a bean, so there's no proxy at all.
- you call it from the bean's own **constructor or `@PostConstruct`**: that's also a self-call, and the proxy doesn't exist yet.

### How to confirm it

Turn on transaction logging:

```yaml
logging:
  level:
    org.springframework.transaction.interceptor: TRACE
```

A working call logs `Getting transaction for [com.example.shop.OrderService.saveOrder]`. If that line is missing, the proxy was bypassed. Inside the method you can also check `TransactionSynchronizationManager.isActualTransactionActive()`.

### How to fix it

**Fix 1: move the method to another bean.** The clean fix, and usually better design anyway.

```java
@Service
public class OrderService {
    private final OrderWriter writer;

    public OrderService(OrderWriter writer) { this.writer = writer; }

    public void placeOrder(Order order) {
        validate(order);
        writer.saveOrder(order);                 // ✓ goes through OrderWriter's proxy
    }
}

@Service
public class OrderWriter {
    @Transactional
    public void saveOrder(Order order) { ... }
}
```

**Fix 2: put the annotation on the method that's called from outside.** If the whole `placeOrder()` may run in one transaction, annotate it instead. The inner call then just joins it.

```java
@Transactional
public void placeOrder(Order order) {            // ✓ the controller's call goes through the proxy
    validate(order);
    saveOrder(order);                            // runs inside the same transaction
}
```

**Fix 3: use `TransactionTemplate` (programmatic).** No proxy involved, so self-calls don't matter. Good when only part of a method needs a transaction.

```java
@Service
public class OrderService {
    private final TransactionTemplate tx;
    private final OrderRepository orders;
    private final StockClient stock;

    public OrderService(TransactionTemplate tx, OrderRepository orders, StockClient stock) {
        this.tx = tx;
        this.orders = orders;
        this.stock = stock;
    }

    public void placeOrder(Order order) {
        validate(order);                         // outside the transaction
        tx.executeWithoutResult(status -> {      // ✓ transaction for just this block
            orders.save(order);
            stock.reserve(order);
        });
    }
}
```

**Fix 4: inject the bean into itself, lazily.** Call through `self`, which is the proxy. Works, but it's a workaround that confuses readers.

```java
@Service
public class OrderService {
    private final OrderService self;

    public OrderService(@Lazy OrderService self) {   // @Lazy avoids a circular-dependency error
        this.self = self;
    }

    public void placeOrder(Order order) {
        self.saveOrder(order);                   // ✓ through the proxy
    }

    @Transactional
    public void saveOrder(Order order) { ... }
}
```

Rarely used: `AopContext.currentProxy()` with `@EnableAspectJAutoProxy(exposeProxy = true)`, or AspectJ weaving (`@EnableTransactionManagement(mode = AdviceMode.ASPECTJ)`), which changes the bytecode itself so even self-calls are advised.

> [!IMPORTANT]
> Interview answer: **"Spring applies `@Transactional`, `@Async` and `@Cacheable` through a proxy around the bean. A call from another method of the same class uses `this`, the real object, so it skips the proxy and the annotation is ignored. Fix it by moving the method to another bean, annotating the outer method, using `TransactionTemplate`, or calling through a lazily self-injected proxy."**

---

## 3. Proxies, @Transactional and @Async

<details>
<summary><b>Q1. How does @Transactional actually work?</b></summary>

At startup a `BeanPostProcessor` sees `@Transactional` and replaces the bean with a **proxy**. Other beans get the proxy injected. When they call the method, the proxy asks the `PlatformTransactionManager` to begin a transaction (binding a DB connection to the current thread), calls the real method, then commits, or rolls back if it threw. Repositories called inside use the same thread-bound connection, so they're in the same transaction.
</details>

<details>
<summary><b>Q2. Why does @Transactional not work when I call the method from the same class?</b></summary>

**Self-invocation.** The annotation is applied by a proxy around the bean, but `this.saveOrder()` is a plain call on the real object, so it never goes through the proxy. Same for `@Async`, `@Cacheable`, `@Retryable`. Fixes: move the method to another bean, annotate the outer method, use `TransactionTemplate`, or call through a `@Lazy` self-injected proxy. Full walkthrough in [the common-error section](#2-common-error-calling-an-annotated-method-from-the-same-class).
</details>

<details>
<summary><b>Q3. Which exceptions cause a rollback?</b></summary>

By default only **unchecked** ones: `RuntimeException` and `Error`. A **checked** exception (`IOException`, your own `extends Exception`) **commits** the transaction, which surprises people. Change it with `@Transactional(rollbackFor = Exception.class)`, or `noRollbackFor` for the reverse. An exception you catch inside the method doesn't roll back anything, because the proxy never sees it.
</details>

<details>
<summary><b>Q4. Explain transaction propagation: REQUIRED vs REQUIRES_NEW.</b></summary>

Propagation decides what happens when a transactional method is called while a transaction is already running.

| Propagation | Behaviour |
|---|---|
| `REQUIRED` (default) | Join the existing transaction, or start one if none. One rollback undoes everything |
| `REQUIRES_NEW` | Suspend the outer one and run in a **new, independent** transaction (a second DB connection). Commits even if the outer one later rolls back |
| `NESTED` | A savepoint inside the outer transaction: can roll back alone, but commits only with the outer one |
| `SUPPORTS` / `NOT_SUPPORTED` / `MANDATORY` / `NEVER` | Run with a transaction if there is one / without one / fail if none / fail if one exists |

Classic use of `REQUIRES_NEW`: write an audit log entry that must survive even if the business transaction rolls back. It has to be in **another bean**, or self-invocation skips it.
</details>

<details>
<summary><b>Q5. "Transaction silently rolled back because it has been marked as rollback-only". What happened?</b></summary>

An inner `@Transactional` method (propagation `REQUIRED`, so the **same** transaction) threw a `RuntimeException`. The proxy marked the shared transaction rollback-only. The outer method caught the exception and carried on, then tried to commit, and Spring threw `UnexpectedRollbackException`. Fix: don't swallow it, or run the inner call with `REQUIRES_NEW` if it really is independent.
</details>

<details>
<summary><b>Q6. JDK dynamic proxy vs CGLIB proxy?</b></summary>

A JDK proxy implements the bean's **interfaces**, so it can only be injected as the interface type. A CGLIB proxy is a generated **subclass** of the class, so it can be injected as the class; it can't proxy `final` classes or `final`/`private` methods. Spring Boot uses CGLIB by default (`spring.aop.proxy-target-class=true`), which avoids the "bean is of type $Proxy, not OrderService" error.
</details>

<details>
<summary><b>Q7. How does @Async work, and what are its traps?</b></summary>

`@EnableAsync` + `@Async` on a method: the proxy submits the call to a `TaskExecutor` and returns immediately. Return `void` or `CompletableFuture<T>`. Traps: self-invocation runs it synchronously; exceptions from a `void` method are only logged (by the `AsyncUncaughtExceptionHandler`); the transaction and the security context of the caller don't carry over to the new thread. Boot auto-configures the executor (`spring.task.execution.pool.*`), or virtual threads if `spring.threads.virtual.enabled=true`.

```java
@Async
public CompletableFuture<Invoice> generateInvoice(long orderId) {
    return CompletableFuture.completedFuture(pdf.render(orderId));
}
```
</details>

---

## 4. The web layer

![Spring MVC request flow: the client's request passes servlet filters (security, CORS, logging) to the DispatcherServlet, which asks HandlerMapping which method handles it, runs interceptor preHandle, lets the HandlerAdapter bind @RequestBody and @PathVariable and validate @Valid, invokes the @RestController method, converts the returned object to JSON with Jackson, runs postHandle and afterCompletion and sends the response; a thrown exception goes to @RestControllerAdvice which returns error JSON](svg/springboot/d009-dispatcherservlet-flow.svg)

<details>
<summary><b>Q1. What happens when an HTTP request reaches a Spring Boot app?</b></summary>

Tomcat takes a thread from its pool and runs the servlet **filter chain** (Spring Security, CORS, logging). Then the **`DispatcherServlet`**, the front controller, asks the `HandlerMapping` which controller method matches the method and path, runs the interceptors' `preHandle`, and the `HandlerAdapter` binds arguments (`@PathVariable`, `@RequestBody` via Jackson), validates `@Valid`, and calls the method. The return value is serialized by an `HttpMessageConverter`, interceptors' `postHandle` / `afterCompletion` run, and the response goes back. Exceptions go to `@ExceptionHandler`s.
</details>

<details>
<summary><b>Q2. Filter vs HandlerInterceptor?</b></summary>

A filter is Servlet API and runs before the `DispatcherServlet` for every request; it can wrap the request and response (security, CORS, logging). An interceptor is Spring MVC and runs around the controller method, knows which handler runs, and has `preHandle`, `postHandle` and `afterCompletion`. Exceptions from filters don't reach `@ControllerAdvice`. Full comparison with code in [Filter vs interceptor](#5-filter-vs-interceptor).
</details>

<details>
<summary><b>Q3. How do you handle exceptions globally?</b></summary>

A `@RestControllerAdvice` class with `@ExceptionHandler` methods that map exception types to responses, ideally returning `ProblemDetail` (RFC 9457). Validation failures (`MethodArgumentNotValidException`) become 400 automatically; turn on `spring.mvc.problemdetails.enabled=true` to get Spring's built-in errors as `ProblemDetail` too. For a single exception type you can also put `@ResponseStatus(HttpStatus.NOT_FOUND)` on the exception class.
</details>

<details>
<summary><b>Q4. How do you validate a request body?</b></summary>

Add `spring-boot-starter-validation`, put constraints on the DTO, and `@Valid` on the parameter. Invalid input → `MethodArgumentNotValidException` → 400 with the field errors.

```java
public record SignupRequest(@NotBlank String name, @Email String email, @Min(18) int age) { }

@PostMapping("/signup")
public UserDto signup(@Valid @RequestBody SignupRequest req) { ... }
```
</details>

<details>
<summary><b>Q5. How many requests can a Spring Boot app handle at once?</b></summary>

With embedded Tomcat and platform threads: **200** worker threads by default (`server.tomcat.threads.max`), up to 8,192 open connections (`max-connections`) and 100 more waiting in the OS accept queue (`accept-count`). A request that blocks (DB, HTTP call) holds its thread the whole time. With Java 21 and `spring.threads.virtual.enabled=true`, each request gets a cheap virtual thread, so blocking I/O no longer caps you at 200. The real limit then moves to the DB pool (Hikari default: 10 connections) and downstream services.
</details>

<details>
<summary><b>Q6. ResponseEntity vs returning the object directly?</b></summary>

Returning the object gives 200 (or the `@ResponseStatus` you set) with the body as JSON. `ResponseEntity<T>` lets you choose the status, headers and body per call: `ResponseEntity.created(uri).body(dto)`, `ResponseEntity.notFound().build()`. Use it when the status depends on the outcome.
</details>

---

## 5. Filter vs interceptor

Both let you run code **before and after** a request without touching every controller. The difference is **where** they sit:

- A **Filter** belongs to the **Servlet API** (Jakarta EE). Tomcat runs it **outside** Spring MVC, before the request reaches the `DispatcherServlet`.
- A **HandlerInterceptor** belongs to **Spring MVC**. The `DispatcherServlet` runs it **inside**, right around the controller method, once it knows which method will handle the request.

Think of an onion: Tomcat → filters → `DispatcherServlet` → interceptors → your controller method, and the response travels back out through the same layers in reverse.

![Filter vs interceptor: the servlet container runs the filter chain (request ID, CORS, Spring Security), which wraps the DispatcherServlet, which runs the interceptors (preHandle on the way in, postHandle and afterCompletion on the way out) around the @RestController method; @RestControllerAdvice only sees exceptions thrown inside the DispatcherServlet, so an exception thrown in a filter never reaches it; with two filters and two interceptors the order is Filter A, Filter B, DispatcherServlet, preHandle 1, preHandle 2, controller, then postHandle 2, postHandle 1, afterCompletion 2, afterCompletion 1, Filter B, Filter A](svg/springboot/d010-filter-vs-interceptor.svg)

### A filter: request ID and timing for every request

Extend `OncePerRequestFilter`. A plain `Filter` can run twice for one request (on internal forwards and error dispatches); this base class guarantees once.

```java
@Component                                   // registered for ALL URLs automatically
@Order(Ordered.HIGHEST_PRECEDENCE)           // run before the other filters
public class RequestIdFilter extends OncePerRequestFilter {

    private static final Logger log = LoggerFactory.getLogger(RequestIdFilter.class);

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
                                    FilterChain chain) throws ServletException, IOException {
        String id = Optional.ofNullable(request.getHeader("X-Request-Id"))
                            .orElse(UUID.randomUUID().toString());
        MDC.put("requestId", id);                // every log line of this request carries the id
        response.setHeader("X-Request-Id", id);
        long start = System.nanoTime();
        try {
            chain.doFilter(request, response);   // ← the rest of the app runs INSIDE this call
        } finally {
            long ms = (System.nanoTime() - start) / 1_000_000;
            log.info("{} {} → {} in {} ms", request.getMethod(), request.getRequestURI(),
                     response.getStatus(), ms);
            MDC.remove("requestId");             // threads are reused: always clean up
        }
    }
}
```

Code before `chain.doFilter(...)` runs on the way in, code after it on the way out. If you **don't** call `chain.doFilter`, the request stops here and never reaches Spring MVC. That's how a security filter rejects a request.

To apply a filter to some URLs only, register it with a `FilterRegistrationBean` instead of `@Component`:

```java
@Bean
public FilterRegistrationBean<AuditFilter> auditFilter() {
    var registration = new FilterRegistrationBean<>(new AuditFilter());
    registration.addUrlPatterns("/api/*");
    registration.setOrder(10);
    return registration;
}
```

> [!WARNING]
> ⚠️ Don't also put `@Component` on `AuditFilter`. Boot registers every `Filter` bean for all URLs, so it would run twice: once for `/api/*` and once for everything.

### An interceptor: check an API key on annotated endpoints

An interceptor gets the **handler**: the controller method that will run. So it can read that method's annotations, which a filter can't.

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface RequiresApiKey { }

@Component
public class ApiKeyInterceptor implements HandlerInterceptor {

    private static final Logger log = LoggerFactory.getLogger(ApiKeyInterceptor.class);
    private final String apiKey;

    public ApiKeyInterceptor(@Value("${shop.api-key}") String apiKey) { this.apiKey = apiKey; }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response,
                             Object handler) throws IOException {
        if (handler instanceof HandlerMethod method
                && method.hasMethodAnnotation(RequiresApiKey.class)
                && !apiKey.equals(request.getHeader("X-Api-Key"))) {
            response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Missing or wrong API key");
            return false;                        // stop: the controller is NOT called
        }
        return true;                             // carry on to the next interceptor / controller
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response,
                                Object handler, Exception ex) {
        if (handler instanceof HandlerMethod method) {
            log.info("handled by {}.{}()", method.getBeanType().getSimpleName(),
                     method.getMethod().getName());
        }
    }
}
```

Unlike filters, interceptors are **not** picked up automatically. Register them in a `WebMvcConfigurer`, with path patterns:

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    private final ApiKeyInterceptor apiKeyInterceptor;

    public WebConfig(ApiKeyInterceptor apiKeyInterceptor) { this.apiKeyInterceptor = apiKeyInterceptor; }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(apiKeyInterceptor)
                .addPathPatterns("/api/**")
                .excludePathPatterns("/api/health");
    }
}

@RestController
public class ReportController {
    @RequiresApiKey                              // the interceptor checks this one
    @GetMapping("/api/reports")
    public List<Report> reports() { ... }
}
```

The three interceptor methods:

| Method | Runs | Use it for |
|---|---|---|
| `preHandle` | Before the controller. Return `false` to stop the request | Auth checks, rate limits, setting up per-request context |
| `postHandle` | After the controller returns, before a view is rendered. **Skipped if the controller threw** | Adding model attributes for HTML views. Useless for `@RestController`: the JSON body is already written |
| `afterCompletion` | At the very end, **always** (if this interceptor's `preHandle` returned `true`) | Cleanup, timing, logging. Gets the exception if nobody handled it |

### The order they run in

With two filters (A, B) and two interceptors (1, 2):

```text
in:   Filter A → Filter B → DispatcherServlet → preHandle 1 → preHandle 2 → controller
out:  postHandle 2 → postHandle 1 → afterCompletion 2 → afterCompletion 1 → Filter B → Filter A
```

The way out is the **reverse** of the way in. If `preHandle 2` returns `false`, the controller and all `postHandle`s are skipped, but `afterCompletion 1` still runs, because interceptor 1 already said yes.

### What happens with exceptions

This is the difference interviewers like most:

- **Exception in the controller (or a service it calls):** it's thrown inside the `DispatcherServlet`, so your `@RestControllerAdvice` catches it and writes the error JSON. `postHandle` is skipped and `afterCompletion` still runs.
- **Exception in a filter:** it's thrown **outside** the `DispatcherServlet`. `@RestControllerAdvice` **never sees it**. It goes to Tomcat, which forwards to Boot's `/error` page, and the client gets the generic error JSON instead of your format. (Normal filters don't even run again for that `/error` forward. Spring Security does, since it's registered for error dispatches too.) So a filter must handle its own errors: catch them and write the response itself, as Spring Security does with its `AuthenticationEntryPoint` (401) and `AccessDeniedHandler` (403).

### Filter vs interceptor at a glance

| | Filter | HandlerInterceptor |
|---|---|---|
| Part of | Servlet API (`jakarta.servlet`) | Spring MVC (`org.springframework.web.servlet`) |
| Runs | Outside, before the `DispatcherServlet` | Inside the `DispatcherServlet`, around the controller |
| Applies to | **Every** request the container gets: static files, other servlets too | Only requests that reach a Spring MVC handler (static files served by Spring MVC included, unless excluded) |
| Knows the controller method | ✗ Only the raw request | ✓ `HandlerMethod`: class, method, annotations |
| Can wrap / replace request and response | ✓ e.g. `ContentCachingRequestWrapper` to log the body | ✗ Gets them as they are |
| Can stop the request | ✓ Don't call `chain.doFilter` | ✓ Return `false` from `preHandle` |
| Exceptions handled by `@RestControllerAdvice` | ✗ | ✓ |
| Registered by | `@Component` (all URLs) or `FilterRegistrationBean` | `WebMvcConfigurer.addInterceptors` |
| Typical use | Security, CORS, request IDs / MDC, request logging, compression, rate limiting | Checks based on controller annotations, per-endpoint auth or audit, locale / tenant from the handler |

**Rule of thumb:** if it's about **HTTP in general** (every request, raw bytes, security), use a filter. If it needs to know **which controller method** runs, use an interceptor. If it's about **business methods** rather than HTTP (timing every `@Service` call), use an AOP `@Aspect`. To change a response body after the controller, use a `ResponseBodyAdvice`.

> [!IMPORTANT]
> Interview answer: **"A filter is a Servlet component that runs before the `DispatcherServlet` for every request and can wrap the request and response, so it's used for security, CORS and logging. An interceptor is Spring MVC's hook around the controller: it knows the handler method, has `preHandle`, `postHandle` and `afterCompletion`, and only runs for requests that reach Spring MVC. Exceptions from a filter don't reach `@ControllerAdvice`; exceptions from the controller do."**

---

## 6. Data and JPA

### Lazy vs eager fetching

In JPA, "lazy vs eager" is about **associations**: when you load an `Order`, is its `Customer` loaded too?

- **`FetchType.EAGER`**: the association is loaded **together with** the entity, every time.
- **`FetchType.LAZY`**: you get a placeholder (a Hibernate **proxy**, or an unloaded collection). The real data is loaded by an extra query the **first time you touch it**, and only if the persistence context (Hibernate session) is still open. Normally that closes when the `@Transactional` method ends. But Boot's default `spring.jpa.open-in-view=true` keeps it open for the whole web request, so in a controller the access usually works (with an extra query) instead of throwing `LazyInitializationException`.

```java
@Entity
@Table(name = "orders")
public class Order {
    @Id @GeneratedValue
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)        // default for @ManyToOne would be EAGER
    private Customer customer;

    @OneToMany(mappedBy = "order")            // collections are LAZY by default
    private List<OrderItem> items = new ArrayList<>();
}
```

![JPA fetching, eager vs lazy: with EAGER, findById joins the customer every time even if unused, and findAll runs 1 query for orders plus N queries for customers, an N+1 that can't be switched off per query; with LAZY, findById loads only the order, getCustomer() returns a proxy holding just the id, and getName() while the session is open runs one query to load it, but the same call after the session closed throws LazyInitializationException; defaults are EAGER for @ManyToOne and @OneToOne and LAZY for @OneToMany and @ManyToMany](svg/springboot/d012-jpa-fetch-lazy-vs-eager.svg)

| | EAGER | LAZY |
|---|---|---|
| Loaded | Always, with the entity | On first access to the association |
| You get | The real object | A proxy / an unloaded collection |
| Default for | `@ManyToOne`, `@OneToOne` | `@OneToMany`, `@ManyToMany` |
| Problem | Loads data you don't need. List queries trigger **N+1**. Can't be turned off per query | `LazyInitializationException` once the session is closed. N+1 if you loop and touch it |

**Best practice: make every association `LAZY`** (so add `fetch = FetchType.LAZY` to every `@ManyToOne` and `@OneToOne`), then load what each use case needs **in the query**:

```java
public interface OrderRepository extends JpaRepository<Order, Long> {

    @Query("select o from Order o join fetch o.customer where o.id = :id")
    Optional<Order> findWithCustomer(long id);             // order + customer, 1 query

    @EntityGraph(attributePaths = {"customer", "items"})
    List<Order> findByStatus(Status status);               // orders + customers + items, 1 query
}
```

EAGER is a decision baked into the mapping, the same for every query. LAZY + fetch joins lets each query decide. Return **DTOs** from your services, not entities, so Jackson never walks into an unloaded lazy association in the controller.

<details>
<summary><b>Q1. What is the N+1 query problem, and how do you fix it?</b></summary>

You load N orders with 1 query, then touch a lazy association on each (`order.getItems()`), which fires 1 more query **per order**: N+1 queries. Slow, and it grows with the data. Detect it with SQL logging or Hibernate statistics. Fix it by fetching what you need in the same query: `JOIN FETCH` in JPQL, `@EntityGraph(attributePaths = "items")` on the repository method, or `@BatchSize` / `hibernate.default_batch_fetch_size` to load the associations in batches.

```java
@EntityGraph(attributePaths = "items")
List<Order> findByStatus(Status status);   // orders + items in one query
```
</details>

<details>
<summary><b>Q2. What is LazyInitializationException? What is open-in-view?</b></summary>

A lazy association was accessed after the persistence context (session) closed, typically in the controller or during JSON serialization, after the `@Transactional` service method returned. Boot's default `spring.jpa.open-in-view=true` hides this by keeping the session open for the whole web request, at the cost of holding a DB connection longer and running lazy queries from the view (Boot logs a warning about it). Better: set it to `false` and fetch what you need inside the transaction (fetch joins, entity graphs) and return DTOs, not entities.
</details>

<details>
<summary><b>Q3. How does a Spring Data repository work with only an interface?</b></summary>

At startup Spring Data creates a **proxy** for each repository interface. CRUD methods (`save`, `findById`) are delegated to `SimpleJpaRepository`. Derived query methods are parsed from the method name: `findByEmailAndStatus(String email, Status s)` becomes `where email = ? and status = ?`. `@Query` methods run the JPQL/SQL you give. The query parsing happens at startup, so a typo in a method name fails fast.
</details>

<details>
<summary><b>Q4. Optimistic vs pessimistic locking in JPA?</b></summary>

**Optimistic:** add a `@Version` field. Each update checks the version and increments it (`update … where id = ? and version = ?`). If someone else updated first, 0 rows match → `OptimisticLockingFailureException`, and you retry or report a conflict. No DB locks held, great when conflicts are rare. **Pessimistic:** `@Lock(LockModeType.PESSIMISTIC_WRITE)` issues `SELECT … FOR UPDATE`, blocking other writers until commit. Use it when conflicts are frequent and retries are expensive, e.g. a hot inventory row.
</details>

<details>
<summary><b>Q5. Which connection pool does Boot use, and how do you size it?</b></summary>

HikariCP, default `maximum-pool-size` = 10. Bigger isn't better: the database has limited cores, and hundreds of connections thrash it. Start small (a common rule: about cores × 2 for the DB server, shared across all app instances), watch `hikaricp.connections.pending` and acquire time in metrics, and keep transactions short so connections return quickly. `connection-timeout` (30 s default) is how long a request waits for a free connection before failing.
</details>

---

## 7. Configuration and production

<details>
<summary><b>Q1. What are profiles and how do you use them?</b></summary>

Named sets of config and beans for an environment. `application-dev.yml` and `application-prod.yml` hold per-environment values on top of `application.yml`, and `@Profile("prod")` limits beans. Activate with `spring.profiles.active=prod`, the env var `SPRING_PROFILES_ACTIVE=prod`, or `--spring.profiles.active=prod`.
</details>

<details>
<summary><b>Q2. The same property is set in several places. Which wins?</b></summary>

Highest priority first (simplified):

1. Command-line arguments (`--server.port=9090`)
2. Java system properties (`-Dserver.port=9090`)
3. OS environment variables (`SERVER_PORT=9090`)
4. Profile-specific files (`application-prod.yml`), outside the jar before inside
5. `application.yml` / `application.properties`, outside the jar before inside
6. `@PropertySource` and defaults

So an env var in Kubernetes overrides the value baked into the jar, without a rebuild.
</details>

<details>
<summary><b>Q3. @Value vs @ConfigurationProperties?</b></summary>

`@Value("${x}")` injects one value, supports SpEL, but has no grouping, weak validation and the key is a string repeated wherever it's used. `@ConfigurationProperties(prefix = "payments")` binds a whole group into a typed object (a record works well): relaxed binding, `Duration`/`DataSize` conversion, `@Validated` checks at startup, IDE autocompletion. Prefer it for anything beyond one or two values.
</details>

<details>
<summary><b>Q4. What is Spring Boot Actuator?</b></summary>

Production endpoints under `/actuator`: `health` (with `liveness` and `readiness` groups for Kubernetes probes), `metrics` and `prometheus` (Micrometer), `info`, `env`, `loggers` (change log levels at runtime), `threaddump`, `heapdump`, `conditions`, `startup`. Only `health` is exposed over HTTP by default. Expose more with `management.endpoints.web.exposure.include`, and secure them, because `env` and `heapdump` leak secrets.
</details>

<details>
<summary><b>Q5. How does graceful shutdown work?</b></summary>

On `SIGTERM` (e.g. Kubernetes stopping a pod), Boot stops accepting new requests, lets in-flight requests finish for up to `spring.lifecycle.timeout-per-shutdown-phase` (30 s default), then closes the context: `@PreDestroy` hooks run, pools close. Graceful shutdown is the default since Boot 3.4 (`server.shutdown=graceful`). Kubernetes' `terminationGracePeriodSeconds` must be longer than the timeout.
</details>

<details>
<summary><b>Q6. How do you change the port or the embedded server?</b></summary>

Port: `server.port=8081` (`0` = random free port, handy in tests). Server: Tomcat comes with `spring-boot-starter-web`; to use Jetty, exclude `spring-boot-starter-tomcat` and add `spring-boot-starter-jetty`. A reactive (WebFlux) app runs on Netty by default.
</details>

<details>
<summary><b>Q7. You add spring-boot-starter-security. What changes immediately?</b></summary>

Every endpoint now requires authentication. Boot creates a default user `user` with a random password printed in the log, enables form login and HTTP Basic, CSRF protection and security headers. You replace that by defining a `SecurityFilterChain` bean (which paths are open, JWT/OAuth2 resource server, etc.). Security runs as a servlet **filter**, before the `DispatcherServlet`.
</details>

---

## 8. Quick-fire answers

| Question | Short answer |
|---|---|
| Default embedded server? | Tomcat (Netty for WebFlux) |
| Default port? | 8080 |
| Default JSON library? | Jackson |
| Default connection pool? | HikariCP, 10 connections |
| Default log library? | Logback via SLF4J |
| Default Tomcat threads? | 200 |
| Default bean scope? | Singleton |
| Beans created lazily or eagerly? | Eagerly at startup (singletons) |
| Default JPA fetch type? | `@ManyToOne` / `@OneToOne` EAGER · `@OneToMany` / `@ManyToMany` LAZY |
| Default `@Transactional` rollback? | `RuntimeException` and `Error` only |
| Default propagation? | `REQUIRED` |
| Default proxy type in Boot? | CGLIB |
| `@Autowired` needed on a single constructor? | No |
| Is `open-in-view` on by default? | Yes (with a warning). Turn it off |
| Circular references allowed? | No, since Boot 2.6 |
| Graceful shutdown on by default? | Yes, since Boot 3.4 |
| Actuator endpoints exposed by default? | Only `health` |
| Run a method every 5 minutes? | `@Scheduled(fixedRate = 300_000)` + `@EnableScheduling` |
| Virtual threads? | Java 21 + `spring.threads.virtual.enabled=true` |
| Mock a bean in a Boot test? | `@MockitoBean` (`@MockBean` is gone in Boot 4) |
