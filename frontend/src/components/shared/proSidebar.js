// Sidebar components with the same markup and class names as react-pro-sidebar 0.7.
//
// react-pro-sidebar 0.7 does not support React 19, and 1.x renders different markup.
// The project sidebar only uses a flat menu, and templates (summary-base.html,
// task-base.html) style the 0.7 class names directly, so the 0.7 markup is rendered
// here and its stylesheet is vendored in pro-sidebar-0.7.css.
import React from 'react';
import clsx from 'clsx';
// The stylesheet (pro-sidebar-0.7.css) is imported at the top of index.css so the project's overrides follow it.

export const ProSidebar = ({ className, width, collapsed, rtl, toggled, breakPoint, style = {}, children, ...rest }) => {
  const widthStyle = width ? { width, minWidth: width } : {};
  return (
    <div className={clsx('pro-sidebar', className, breakPoint, { collapsed, rtl, toggled })} style={{ ...widthStyle, ...style }} {...rest}>
      <div className="pro-sidebar-inner">
        <div className="pro-sidebar-layout">{children}</div>
      </div>
    </div>
  );
};

export const SidebarHeader = ({ className, ...rest }) => (
  <div className={clsx('pro-sidebar-header', className)} {...rest} />
);

export const Menu = ({ className, iconShape, subMenuBullets = false, innerSubMenuArrows = true, children, ...rest }) => (
  <nav
    className={clsx('pro-menu', className, {
      [`shaped ${iconShape}`]: ['square', 'round', 'circle'].includes(iconShape),
      'submenu-bullets': subMenuBullets,
      'inner-submenu-arrows': innerSubMenuArrows,
    })}
    {...rest}
  >
    <ul>{children}</ul>
  </nav>
);

export const MenuItem = ({ className, icon, active, prefix, suffix, children, ...rest }) => (
  <li className={clsx('pro-menu-item', className, { active })} {...rest}>
    <div className="pro-inner-item" tabIndex={0} role="button">
      {icon ? (
        <span className="pro-icon-wrapper">
          <span className="pro-icon">{icon}</span>
        </span>
      ) : null}
      {prefix ? <span className="prefix-wrapper">{prefix}</span> : null}
      <span className="pro-item-content">{children}</span>
      {suffix ? <span className="suffix-wrapper">{suffix}</span> : null}
    </div>
  </li>
);
