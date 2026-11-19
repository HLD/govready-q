import { createRoot } from 'react-dom/client';

// React 18+ replacement for ReactDOM.render(element, container). Like ReactDOM.render,
// calling it again for the same container re-renders into the existing root.
const roots = new WeakMap();

export function renderInto(container, element) {
  let root = roots.get(container);
  if (!root) {
    root = createRoot(container);
    roots.set(container, root);
  }
  root.render(element);
}
