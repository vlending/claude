### Design Principles (STRICT)
1. **NO raw HTML elements** - Use MUI components only (Surface replaces div)
2. **200 lines max per file** - Aggressively split components
3. **DRY everything** - Reusable components and hooks
4. **Atomic Design** - Atoms → Molecules → Organisms → Templates
5. **Type-safe** - Full TypeScript, no `any` types
6. **SSR First** - Use Next.js SSR/ISR for performance
7. **Component Composition** - Build complex from simple
8. **Client Components Minimized** - Always prefer SSR, use "use client" sparingly
9. **NO FALLBACKS OR WORKAROUNDS** - Never use setTimeout, fallback patterns, or workarounds
10. **NO COMPROMISES** - Fix root causes, not symptoms. No shortcuts or band-aid solutions
