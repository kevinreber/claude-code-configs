# Project: [Project Name]

## Overview

[Brief description of what this project does]

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite / Next.js
- **State Management**: React Query / Zustand / Redux Toolkit
- **Styling**: Tailwind CSS / CSS Modules / styled-components
- **Testing**: Vitest / Jest + React Testing Library
- **Routing**: React Router / Next.js App Router

## Project Structure

```
src/
├── app/                  # App entry, providers, layout (Next.js)
├── components/
│   ├── ui/               # Reusable UI components (Button, Input, etc.)
│   └── features/         # Feature-specific components
├── hooks/                # Custom React hooks
├── lib/                  # Utility functions and helpers
├── services/             # API client and service functions
├── stores/               # State management (Zustand/Redux)
├── types/                # TypeScript type definitions
├── styles/               # Global styles
└── __tests__/            # Test files
```

## Development Commands

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Type check
npm run typecheck

# Lint
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview

# Storybook (if configured)
npm run storybook
```

## Coding Conventions

### File Naming
- Components: PascalCase (`UserProfile.tsx`)
- Hooks: camelCase with `use` prefix (`useAuth.ts`)
- Utils: camelCase (`formatDate.ts`)
- Types: PascalCase (`User.types.ts`)

### Component Structure
```typescript
// Imports (external, internal, types, styles)
import { useState } from 'react';
import { Button } from '@/components/ui';
import type { User } from '@/types';
import styles from './Component.module.css';

// Types
interface Props {
  user: User;
  onUpdate: (user: User) => void;
}

// Component
export function UserCard({ user, onUpdate }: Props) {
  // Hooks first
  const [isEditing, setIsEditing] = useState(false);

  // Handlers
  const handleSave = () => {
    // ...
  };

  // Render
  return (
    <div className={styles.card}>
      {/* ... */}
    </div>
  );
}
```

### Hooks
- Extract complex logic into custom hooks
- Prefix with `use`
- Return object for multiple values

### State Management
- Local state for UI-only state
- React Query for server state
- Zustand/Redux for shared client state

## Important Patterns

### Data Fetching (React Query)
```typescript
export function useUser(id: string) {
  return useQuery({
    queryKey: ['user', id],
    queryFn: () => api.getUser(id),
  });
}
```

### Forms
```typescript
// Use react-hook-form for complex forms
const { register, handleSubmit, formState: { errors } } = useForm<FormData>();
```

### Error Boundaries
- Wrap feature areas in error boundaries
- Provide fallback UI

## Environment Variables

Required variables (see `.env.example`):
- `VITE_API_URL` - Backend API URL
- `VITE_PUBLIC_URL` - Public assets URL

Note: Only `VITE_` prefixed vars are exposed to client.

## Sensitive Areas

- API keys should never be in client code
- Auth tokens stored in httpOnly cookies (not localStorage)
- Sanitize user input before rendering

## Performance Considerations

- Use `React.memo` for expensive components
- Use `useMemo`/`useCallback` sparingly (when needed)
- Lazy load routes with `React.lazy`
- Optimize images with next/image or similar
- Avoid unnecessary re-renders

## Accessibility

- Use semantic HTML elements
- Include ARIA labels where needed
- Ensure keyboard navigation works
- Test with screen readers
