// Grid layouts for @rjsf forms.
//
// The POA&M edit form describes its layout with nested 'ui:row' / 'ui:col' objects,
// where each column gives Bootstrap 3 widths ({ sm: 3, md: 3, children: [...] }) and
// a row may be marked as a 'ui:group'. This used to be rendered by a custom
// LayoutGridField that subclassed react-jsonschema-form v1 internals. @rjsf v6 has
// a built-in LayoutGridField; `toLayoutGrid` converts the layout description into
// its format (Bootstrap 3 column classes go in `className`).

const COLUMN_SIZES = ['xs', 'sm', 'md', 'lg'];

export function toLayoutGrid(layout) {
  if (typeof layout === 'string') {
    return layout;
  }
  if (layout['ui:row']) {
    const className = layout['ui:group'] !== undefined ? 'row rjsf-layout-grid-group' : 'row';
    return { 'ui:row': { className, children: layout['ui:row'].map(toLayoutGrid) } };
  }
  if (layout['ui:col']) {
    const { children = [], className, ...sizes } = layout['ui:col'];
    const classes = COLUMN_SIZES
      .filter((size) => sizes[size] !== undefined)
      .map((size) => `col-${size}-${sizes[size]}`);
    if (className) classes.push(className);
    return { 'ui:col': { className: classes.join(' '), children: children.map(toLayoutGrid) } };
  }
  return layout;
}
