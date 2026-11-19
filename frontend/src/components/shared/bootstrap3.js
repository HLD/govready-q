// Bootstrap 3 components for the React widgets.
//
// The Django pages that host these widgets load Bootstrap 3 CSS. The widgets used
// to render that markup with react-bootstrap 0.33, which is unmaintained and does
// not work with React 19 (it relies on ReactDOM.findDOMNode). This module provides
// the subset of that API the widgets use, rendering the same Bootstrap 3 class
// names so the widgets keep their look.
import React, { createContext, useContext, useEffect } from 'react';
import { createPortal } from 'react-dom';
import clsx from 'clsx';
import MuiTooltip from '@mui/material/Tooltip';

const sizes = ['xs', 'sm', 'md', 'lg'];

// Layout ------------------------------------------------------------------

export const Grid = ({ fluid, componentClass: Component = 'div', className, ...rest }) => (
  <Component className={clsx(fluid ? 'container-fluid' : 'container', className)} {...rest} />
);

export const Row = ({ componentClass: Component = 'div', className, ...rest }) => (
  <Component className={clsx('row', className)} {...rest} />
);

export const Col = ({ componentClass: Component = 'div', className, ...props }) => {
  const classes = [];
  const rest = {};
  Object.entries(props).forEach(([key, value]) => {
    const match = key.match(/^(xs|sm|md|lg)(Offset|Push|Pull)?$/);
    if (match && sizes.includes(match[1])) {
      if (value === undefined || value === null) return;
      const suffix = match[2] ? `-${match[2].toLowerCase()}` : '';
      classes.push(`col-${match[1]}${suffix}-${value}`);
    } else if (/^(xs|sm|md|lg)Hidden$/.test(key)) {
      if (value) classes.push(`hidden-${key.slice(0, 2)}`);
    } else {
      rest[key] = value;
    }
  });
  return <Component className={clsx(classes, className)} {...rest} />;
};

// Buttons and icons -------------------------------------------------------

export const Button = ({
  bsStyle = 'default', bsSize, block, active, variant, // `variant` was never a react-bootstrap 0.33 prop; ignore it.
  componentClass, href, type = 'button', className, ...rest
}) => {
  const classes = clsx('btn', `btn-${bsStyle}`, {
    'btn-lg': bsSize === 'large' || bsSize === 'lg',
    'btn-sm': bsSize === 'small' || bsSize === 'sm',
    'btn-xs': bsSize === 'xsmall' || bsSize === 'xs',
    'btn-block': block,
    active,
  }, className);
  if (href) {
    return <a href={href} role="button" className={classes} {...rest} />;
  }
  const Component = componentClass || 'button';
  return <Component type={Component === 'button' ? type : undefined} className={classes} {...rest} />;
};

export const Glyphicon = ({ glyph, className, ...rest }) => (
  <span className={clsx('glyphicon', `glyphicon-${glyph}`, className)} {...rest} />
);

// Forms -------------------------------------------------------------------

const FormGroupContext = createContext({});

export const Form = ({ horizontal, inline, className, componentClass: Component = 'form', ...rest }) => (
  <Component className={clsx({ 'form-horizontal': horizontal, 'form-inline': inline }, className)} {...rest} />
);

const FeedbackIcons = { success: 'ok', warning: 'warning-sign', error: 'remove' };

const Feedback = ({ className, children, ...rest }) => {
  const { validationState } = useContext(FormGroupContext);
  if (children) {
    return <span className={clsx('form-control-feedback', className)} {...rest}>{children}</span>;
  }
  const glyph = FeedbackIcons[validationState];
  if (!glyph) return null;
  return <Glyphicon glyph={glyph} className={clsx('form-control-feedback', className)} {...rest} />;
};

const containsFeedback = (children) => React.Children.toArray(children).some((child) =>
  React.isValidElement(child) && (child.type === Feedback || containsFeedback(child.props.children)));

export const FormGroup = ({ controlId, validationState, bsSize, className, children, ...rest }) => (
  <FormGroupContext.Provider value={{ controlId, validationState }}>
    <div
      className={clsx('form-group', {
        [`has-${validationState}`]: validationState,
        'has-feedback': containsFeedback(children),
        'form-group-lg': bsSize === 'large' || bsSize === 'lg',
        'form-group-sm': bsSize === 'small' || bsSize === 'sm',
      }, className)}
      {...rest}
    >
      {children}
    </div>
  </FormGroupContext.Provider>
);

export const ControlLabel = ({ htmlFor, srOnly, className, ...rest }) => {
  const { controlId } = useContext(FormGroupContext);
  return <label htmlFor={htmlFor || controlId} className={clsx('control-label', { 'sr-only': srOnly }, className)} {...rest} />;
};

export const FormControl = ({ componentClass: Component = 'input', type, id, bsSize, className, ...rest }) => {
  const { controlId } = useContext(FormGroupContext);
  return (
    <Component
      type={Component === 'input' ? type : undefined}
      id={id || controlId}
      className={clsx({ 'form-control': type !== 'file' }, {
        'input-lg': bsSize === 'large' || bsSize === 'lg',
        'input-sm': bsSize === 'small' || bsSize === 'sm',
      }, className)}
      {...rest}
    />
  );
};
FormControl.Feedback = Feedback;

export const Checkbox = ({ inline, disabled, title, className, style, children, inputRef, ...rest }) => {
  const input = <input type="checkbox" disabled={disabled} ref={inputRef} {...rest} />;
  if (inline) {
    return (
      <label className={clsx('checkbox-inline', { disabled }, className)} style={style} title={title}>
        {input}{children}
      </label>
    );
  }
  return (
    <div className={clsx('checkbox', { disabled }, className)} style={style}>
      <label title={title}>{input}{children}</label>
    </div>
  );
};

// Lists and tables --------------------------------------------------------

export const ListGroup = ({ className, ...rest }) => <ul className={clsx('list-group', className)} {...rest} />;

export const ListGroupItem = ({ bsStyle, active, disabled, header, className, children, ...rest }) => (
  <li className={clsx('list-group-item', { [`list-group-item-${bsStyle}`]: bsStyle, active, disabled }, className)} {...rest}>
    {header ? <h4 className="list-group-item-heading">{header}</h4> : null}
    {header ? <p className="list-group-item-text">{children}</p> : children}
  </li>
);

export const Table = ({ striped, bordered, condensed, hover, responsive, className, ...rest }) => {
  const table = (
    <table
      className={clsx('table', {
        'table-striped': striped,
        'table-bordered': bordered,
        'table-condensed': condensed,
        'table-hover': hover,
      }, className)}
      {...rest}
    />
  );
  return responsive ? <div className="table-responsive">{table}</div> : table;
};

// Tooltips and popovers ---------------------------------------------------
//
// <Tooltip> and <Popover> describe the overlay content; <OverlayTrigger> shows it
// with an MUI tooltip on hover/focus.

export const Tooltip = ({ children }) => <>{children}</>;

export const Popover = ({ title, children }) => (
  <>
    {title ? <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>{title}</div> : null}
    {children}
  </>
);

export const OverlayTrigger = ({ overlay, placement = 'right', children }) => (
  <MuiTooltip title={overlay || ''} placement={placement} arrow>
    <span style={{ display: 'inline-block' }}>{children}</span>
  </MuiTooltip>
);

// Modal -------------------------------------------------------------------

const ModalContext = createContext({});

const ModalHeader = ({ closeButton, closeLabel = 'Close', className, children, ...rest }) => {
  const { onHide } = useContext(ModalContext);
  return (
    <div className={clsx('modal-header', className)} {...rest}>
      {closeButton ? (
        <button type="button" className="close" aria-label={closeLabel} onClick={onHide}>
          <span aria-hidden="true">&times;</span>
        </button>
      ) : null}
      {children}
    </div>
  );
};

const ModalTitle = ({ componentClass: Component = 'h4', className, ...rest }) => (
  <Component className={clsx('modal-title', className)} {...rest} />
);

const ModalBody = ({ className, ...rest }) => <div className={clsx('modal-body', className)} {...rest} />;

const ModalFooter = ({ className, ...rest }) => <div className={clsx('modal-footer', className)} {...rest} />;

export const Modal = ({
  show, onHide, dialogClassName, bsSize, className, children, backdrop = true, keyboard = true,
  // Focus-management props accepted for compatibility; this modal does not trap focus.
  autoFocus, enforceFocus, restoreFocus,
  ...rest
}) => {
  useEffect(() => {
    if (!show) return undefined;
    document.body.classList.add('modal-open');
    const onKeyDown = (event) => {
      if (keyboard && event.key === 'Escape' && onHide) onHide();
    };
    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.body.classList.remove('modal-open');
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [show, keyboard, onHide]);

  if (!show) return null;

  const onBackdropClick = (event) => {
    if (backdrop === true && event.target === event.currentTarget && onHide) onHide();
  };

  return createPortal(
    <ModalContext.Provider value={{ onHide }}>
      <div
        role="dialog"
        tabIndex={-1}
        className={clsx('modal', 'fade', 'in', className)}
        style={{ display: 'block' }}
        onClick={onBackdropClick}
        {...rest}
      >
        <div className={clsx('modal-dialog', {
          'modal-lg': bsSize === 'large' || bsSize === 'lg',
          'modal-sm': bsSize === 'small' || bsSize === 'sm',
        }, dialogClassName)}>
          <div className="modal-content" role="document">{children}</div>
        </div>
      </div>
      {backdrop ? <div className="modal-backdrop fade in" /> : null}
    </ModalContext.Provider>,
    document.body
  );
};
Modal.Header = ModalHeader;
Modal.Title = ModalTitle;
Modal.Body = ModalBody;
Modal.Footer = ModalFooter;
