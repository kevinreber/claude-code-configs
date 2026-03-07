# React Skill

Idiomatic React patterns, hooks best practices, and performance guidance for modern React development.

## Activation

Use this skill when working on React projects — building components, managing state, debugging renders, or reviewing React code.

---

## Core Rules

1. **Functional components only** — no class components
2. **Hooks at the top level** — never inside conditions, loops, or nested functions
3. **Single responsibility** — one component does one thing well
4. **Lift state only as high as needed** — don't over-share state

---

## Hooks

### useState

```tsx
// Use separate state for unrelated values
const [name, setName] = useState('');
const [age, setAge] = useState(0);

// Use an object for related values that change together
const [form, setForm] = useState({ name: '', email: '' });
const updateForm = (field: keyof typeof form, value: string) =>
  setForm(prev => ({ ...prev, [field]: value }));
```

### useEffect

```tsx
// Always include all dependencies
useEffect(() => {
  const subscription = subscribe(userId);
  return () => subscription.unsubscribe(); // cleanup
}, [userId]); // re-runs when userId changes

// Fetch data — handle cleanup to prevent state updates on unmounted component
useEffect(() => {
  let cancelled = false;
  fetchUser(id).then(user => {
    if (!cancelled) setUser(user);
  });
  return () => { cancelled = true; };
}, [id]);

// Empty deps = run once on mount
useEffect(() => {
  init();
}, []);
```

### useMemo / useCallback

```tsx
// useMemo: expensive computation
const sortedUsers = useMemo(
  () => [...users].sort((a, b) => a.name.localeCompare(b.name)),
  [users] // only re-sort when users changes
);

// useCallback: stable function reference (for child component props, event handlers in deps)
const handleClick = useCallback((id: string) => {
  setSelectedId(id);
}, []); // stable — no deps change it

// Don't over-memoize — only when profiling shows a real perf issue
```

### Custom hooks

```tsx
// Extract reusable stateful logic into custom hooks
function useLocalStorage<T>(key: string, initial: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      return JSON.parse(localStorage.getItem(key) ?? '') ?? initial;
    } catch {
      return initial;
    }
  });

  const setStored = useCallback((v: T) => {
    setValue(v);
    localStorage.setItem(key, JSON.stringify(v));
  }, [key]);

  return [value, setStored] as const;
}
```

---

## Component Patterns

### Props typing

```tsx
interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
  className?: string; // always accept className for flexibility
  children?: React.ReactNode;
}

function Button({ label, onClick, variant = 'primary', disabled, className }: ButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn('btn', `btn-${variant}`, className)}
    >
      {label}
    </button>
  );
}
```

### Compound components

```tsx
// Related components grouped under a namespace
function Card({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn('card', className)}>{children}</div>;
}

Card.Header = function CardHeader({ title }: { title: string }) {
  return <div className="card-header">{title}</div>;
};

Card.Body = function CardBody({ children }: { children: React.ReactNode }) {
  return <div className="card-body">{children}</div>;
};

// Usage:
<Card>
  <Card.Header title="My Card" />
  <Card.Body>Content here</Card.Body>
</Card>
```

### Render lists correctly

```tsx
// Always use stable, unique keys — NOT array index for dynamic lists
{users.map(user => (
  <UserRow key={user.id} user={user} />
))}

// Index is OK only for static, never-reordered lists
{TABS.map((tab, i) => <Tab key={i} {...tab} />)}
```

---

## State Management

### Local → Context → External library

1. **Local state** (`useState`) — for component-specific state
2. **Lifted state** — pass up to nearest common ancestor
3. **Context** (`useContext`) — for cross-cutting concerns (theme, auth, locale)
4. **External** (Zustand, Jotai, Redux) — for complex global state

### Context pattern

```tsx
const ThemeContext = createContext<Theme | null>(null);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light');
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
}
```

---

## Performance

```tsx
// React.memo — skip re-render if props haven't changed
const ExpensiveList = React.memo(function ExpensiveList({ items }: { items: Item[] }) {
  return <ul>{items.map(i => <li key={i.id}>{i.name}</li>)}</ul>;
});

// Lazy load heavy components
const HeavyChart = React.lazy(() => import('./HeavyChart'));

function Dashboard() {
  return (
    <Suspense fallback={<Spinner />}>
      <HeavyChart />
    </Suspense>
  );
}
```

**Profile before optimizing** — React DevTools Profiler identifies actual bottlenecks.

---

## Common Mistakes

```tsx
// BAD: object/array created on every render defeats memoization
<Component options={{ key: 'value' }} />   // new object each render
<Component items={[1, 2, 3]} />            // new array each render

// GOOD: define outside component or memoize
const OPTIONS = { key: 'value' };
const ITEMS = [1, 2, 3];
<Component options={OPTIONS} items={ITEMS} />

// BAD: mutating state directly
state.items.push(newItem); // doesn't trigger re-render
setState(state);

// GOOD: always return new references
setState(prev => ({ ...prev, items: [...prev.items, newItem] }));

// BAD: useEffect with missing deps
useEffect(() => {
  fetchData(userId); // userId used but not in deps
}, []);             // stale closure bug

// GOOD:
useEffect(() => {
  fetchData(userId);
}, [userId]);
```
