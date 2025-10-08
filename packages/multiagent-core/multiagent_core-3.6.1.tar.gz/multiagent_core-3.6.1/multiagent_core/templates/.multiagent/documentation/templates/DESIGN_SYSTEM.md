# Design System

## Overview

**Project**: {{PROJECT_NAME}}
**Version**: {{VERSION}}
**Last Updated**: {{CURRENT_DATE}}
**Maintained by**: {{TEAM_NAME}}

This design system provides the foundational design elements, components, and guidelines for building consistent user interfaces across {{PROJECT_NAME}}.

## Design Principles

### 1. {{PRINCIPLE_1_NAME}}
{{PRINCIPLE_1_DESCRIPTION}}

### 2. {{PRINCIPLE_2_NAME}}
{{PRINCIPLE_2_DESCRIPTION}}

### 3. {{PRINCIPLE_3_NAME}}
{{PRINCIPLE_3_DESCRIPTION}}

## Brand Identity

### Brand Values
- {{BRAND_VALUE_1}}
- {{BRAND_VALUE_2}}
- {{BRAND_VALUE_3}}

### Voice & Tone
- **Voice**: {{BRAND_VOICE}}
- **Tone**: {{BRAND_TONE}}

## Color System

### Primary Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Primary | `{{PRIMARY_COLOR}}` | {{PRIMARY_USAGE}} |
| Primary Hover | `{{PRIMARY_HOVER}}` | {{PRIMARY_HOVER_USAGE}} |
| Primary Active | `{{PRIMARY_ACTIVE}}` | {{PRIMARY_ACTIVE_USAGE}} |

### Secondary Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Secondary | `{{SECONDARY_COLOR}}` | {{SECONDARY_USAGE}} |
| Secondary Hover | `{{SECONDARY_HOVER}}` | {{SECONDARY_HOVER_USAGE}} |

### Semantic Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Success | `{{SUCCESS_COLOR}}` | Success states, confirmations |
| Warning | `{{WARNING_COLOR}}` | Warning messages, caution |
| Error | `{{ERROR_COLOR}}` | Error states, destructive actions |
| Info | `{{INFO_COLOR}}` | Informational messages |

### Neutral Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Text Primary | `{{TEXT_PRIMARY}}` | Body text, headings |
| Text Secondary | `{{TEXT_SECONDARY}}` | Supporting text, labels |
| Text Disabled | `{{TEXT_DISABLED}}` | Disabled elements |
| Background | `{{BACKGROUND_COLOR}}` | Page background |
| Surface | `{{SURFACE_COLOR}}` | Card backgrounds, panels |
| Border | `{{BORDER_COLOR}}` | Borders, dividers |

### Color Usage Guidelines

```css
/* Primary Color Usage */
.button-primary {
  background-color: var(--primary-color);
  color: var(--text-on-primary);
}

.button-primary:hover {
  background-color: var(--primary-hover);
}

/* Semantic Color Usage */
.alert-error {
  background-color: var(--error-light);
  border-color: var(--error-color);
  color: var(--error-dark);
}
```

## Typography

### Font Families

- **Primary**: {{PRIMARY_FONT}} - Used for body text, UI elements
- **Heading**: {{HEADING_FONT}} - Used for headings, titles
- **Monospace**: {{MONOSPACE_FONT}} - Used for code, technical content

### Type Scale

| Name | Size | Line Height | Weight | Usage |
|------|------|-------------|--------|-------|
| Display | {{DISPLAY_SIZE}} | {{DISPLAY_LINE_HEIGHT}} | {{DISPLAY_WEIGHT}} | Hero sections, large headings |
| H1 | {{H1_SIZE}} | {{H1_LINE_HEIGHT}} | {{H1_WEIGHT}} | Page titles |
| H2 | {{H2_SIZE}} | {{H2_LINE_HEIGHT}} | {{H2_WEIGHT}} | Section headings |
| H3 | {{H3_SIZE}} | {{H3_LINE_HEIGHT}} | {{H3_WEIGHT}} | Subsection headings |
| H4 | {{H4_SIZE}} | {{H4_LINE_HEIGHT}} | {{H4_WEIGHT}} | Card headings |
| Body Large | {{BODY_LARGE_SIZE}} | {{BODY_LARGE_LINE_HEIGHT}} | {{BODY_LARGE_WEIGHT}} | Large body text |
| Body | {{BODY_SIZE}} | {{BODY_LINE_HEIGHT}} | {{BODY_WEIGHT}} | Default body text |
| Body Small | {{BODY_SMALL_SIZE}} | {{BODY_SMALL_LINE_HEIGHT}} | {{BODY_SMALL_WEIGHT}} | Small text, captions |
| Caption | {{CAPTION_SIZE}} | {{CAPTION_LINE_HEIGHT}} | {{CAPTION_WEIGHT}} | Labels, helper text |

### Typography Usage

```css
/* Headings */
h1 { font: {{H1_WEIGHT}} {{H1_SIZE}}/{{H1_LINE_HEIGHT}} {{HEADING_FONT}}; }
h2 { font: {{H2_WEIGHT}} {{H2_SIZE}}/{{H2_LINE_HEIGHT}} {{HEADING_FONT}}; }

/* Body Text */
body {
  font-family: {{PRIMARY_FONT}};
  font-size: {{BODY_SIZE}};
  line-height: {{BODY_LINE_HEIGHT}};
  color: var(--text-primary);
}

/* Code */
code, pre {
  font-family: {{MONOSPACE_FONT}};
  font-size: {{CODE_SIZE}};
}
```

## Spacing System

### Spacing Scale

Based on {{SPACING_BASE_UNIT}} base unit:

| Token | Value | Usage |
|-------|-------|-------|
| `spacing-xs` | {{SPACING_XS}} | Tight spacing within components |
| `spacing-sm` | {{SPACING_SM}} | Small gaps between related elements |
| `spacing-md` | {{SPACING_MD}} | Default spacing |
| `spacing-lg` | {{SPACING_LG}} | Large gaps between sections |
| `spacing-xl` | {{SPACING_XL}} | Extra large spacing |
| `spacing-2xl` | {{SPACING_2XL}} | Maximum spacing |

### Spacing Usage

```css
/* Component Internal Spacing */
.card {
  padding: var(--spacing-md);
  gap: var(--spacing-sm);
}

/* Layout Spacing */
.section {
  margin-bottom: var(--spacing-xl);
}

/* Grid Spacing */
.grid {
  gap: var(--spacing-md);
}
```

## Layout System

### Grid System

**Breakpoints**:

| Name | Min Width | Container | Columns |
|------|-----------|-----------|---------|
| Mobile | `{{MOBILE_BREAKPOINT}}` | 100% | {{MOBILE_COLUMNS}} |
| Tablet | `{{TABLET_BREAKPOINT}}` | {{TABLET_CONTAINER}} | {{TABLET_COLUMNS}} |
| Desktop | `{{DESKTOP_BREAKPOINT}}` | {{DESKTOP_CONTAINER}} | {{DESKTOP_COLUMNS}} |
| Wide | `{{WIDE_BREAKPOINT}}` | {{WIDE_CONTAINER}} | {{WIDE_COLUMNS}} |

### Container Sizes

```css
.container {
  max-width: {{CONTAINER_MAX_WIDTH}};
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

.container-fluid {
  width: 100%;
  padding: 0 var(--spacing-md);
}
```

## Component Library

### Buttons

#### Primary Button

**Usage**: Main call-to-action, primary actions

```jsx
<Button variant="primary" size="md">
  {{BUTTON_TEXT}}
</Button>
```

**Variants**:
- `primary` - Main actions
- `secondary` - Secondary actions
- `outline` - Less prominent actions
- `ghost` - Subtle actions
- `link` - Text-only actions

**Sizes**: `xs`, `sm`, `md`, `lg`, `xl`

**States**:
- Default
- Hover
- Active
- Focus
- Disabled
- Loading

#### Button Specifications

| Variant | Background | Text Color | Border |
|---------|------------|------------|--------|
| Primary | {{PRIMARY_COLOR}} | {{TEXT_ON_PRIMARY}} | None |
| Secondary | {{SECONDARY_COLOR}} | {{TEXT_ON_SECONDARY}} | None |
| Outline | Transparent | {{PRIMARY_COLOR}} | {{PRIMARY_COLOR}} |
| Ghost | Transparent | {{TEXT_PRIMARY}} | None |

### Form Elements

#### Text Input

**Usage**: Single-line text entry

```jsx
<Input
  type="text"
  label="{{LABEL_TEXT}}"
  placeholder="{{PLACEHOLDER_TEXT}}"
  helperText="{{HELPER_TEXT}}"
/>
```

**States**:
- Default
- Focus
- Error
- Success
- Disabled

#### Input Specifications

| State | Border | Background | Text |
|-------|--------|------------|------|
| Default | {{INPUT_BORDER}} | {{INPUT_BACKGROUND}} | {{TEXT_PRIMARY}} |
| Focus | {{INPUT_BORDER_FOCUS}} | {{INPUT_BACKGROUND}} | {{TEXT_PRIMARY}} |
| Error | {{ERROR_COLOR}} | {{INPUT_BACKGROUND}} | {{TEXT_PRIMARY}} |
| Disabled | {{INPUT_BORDER_DISABLED}} | {{INPUT_BACKGROUND_DISABLED}} | {{TEXT_DISABLED}} |

#### Select

**Usage**: Dropdown selection from list

```jsx
<Select label="{{LABEL_TEXT}}" options={{{OPTIONS_ARRAY}}} />
```

#### Checkbox

**Usage**: Multiple selections, toggles

```jsx
<Checkbox label="{{LABEL_TEXT}}" />
```

#### Radio Button

**Usage**: Single selection from options

```jsx
<Radio name="{{NAME}}" label="{{LABEL_TEXT}}" />
```

### Cards

**Usage**: Container for related information

```jsx
<Card>
  <CardHeader>{{HEADER_CONTENT}}</CardHeader>
  <CardBody>{{BODY_CONTENT}}</CardBody>
  <CardFooter>{{FOOTER_CONTENT}}</CardFooter>
</Card>
```

**Variants**:
- Default
- Elevated
- Outlined
- Interactive

### Modals & Dialogs

**Usage**: Important information, user actions

```jsx
<Modal
  isOpen={isOpen}
  onClose={onClose}
  title="{{MODAL_TITLE}}"
>
  {{MODAL_CONTENT}}
</Modal>
```

**Sizes**: `sm`, `md`, `lg`, `xl`, `full`

### Navigation

#### Navigation Bar

**Usage**: Primary site navigation

```jsx
<Navbar>
  <NavbarBrand>{{BRAND_NAME}}</NavbarBrand>
  <NavbarMenu>
    <NavbarItem href="{{LINK}}">{{LABEL}}</NavbarItem>
  </NavbarMenu>
</Navbar>
```

#### Breadcrumbs

**Usage**: Show navigation hierarchy

```jsx
<Breadcrumbs>
  <BreadcrumbItem href="/">Home</BreadcrumbItem>
  <BreadcrumbItem href="/{{PATH}}">{{LABEL}}</BreadcrumbItem>
</Breadcrumbs>
```

### Alerts & Notifications

**Usage**: System messages, feedback

```jsx
<Alert variant="{{VARIANT}}" title="{{TITLE}}">
  {{MESSAGE_TEXT}}
</Alert>
```

**Variants**: `success`, `warning`, `error`, `info`

### Data Display

#### Table

**Usage**: Tabular data display

```jsx
<Table>
  <TableHeader>
    <TableRow>
      <TableHead>{{COLUMN_NAME}}</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>{{CELL_DATA}}</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

#### Badge

**Usage**: Status indicators, labels

```jsx
<Badge variant="{{VARIANT}}">{{TEXT}}</Badge>
```

**Variants**: `primary`, `secondary`, `success`, `warning`, `error`, `info`

## Icons

### Icon System

**Icon Library**: {{ICON_LIBRARY}}
**Icon Sizes**: {{ICON_SIZES}}

### Icon Usage

```jsx
<Icon name="{{ICON_NAME}}" size="{{SIZE}}" color="{{COLOR}}" />
```

### Common Icons

| Name | Usage |
|------|-------|
| {{ICON_1}} | {{ICON_1_USAGE}} |
| {{ICON_2}} | {{ICON_2_USAGE}} |
| {{ICON_3}} | {{ICON_3_USAGE}} |

## Motion & Animation

### Animation Tokens

| Name | Duration | Easing | Usage |
|------|----------|--------|-------|
| `fast` | {{ANIM_FAST}} | {{EASING_FAST}} | Micro-interactions |
| `normal` | {{ANIM_NORMAL}} | {{EASING_NORMAL}} | Standard transitions |
| `slow` | {{ANIM_SLOW}} | {{EASING_SLOW}} | Complex animations |

### Animation Guidelines

```css
/* Micro-interactions */
.button {
  transition: background-color var(--anim-fast) var(--easing-fast);
}

/* Page transitions */
.page-enter {
  animation: fadeIn var(--anim-normal) var(--easing-normal);
}

/* Complex animations */
.modal-enter {
  animation: slideUp var(--anim-slow) var(--easing-slow);
}
```

## Accessibility

### WCAG Compliance

**Target Level**: {{WCAG_LEVEL}} (A/AA/AAA)

### Color Contrast

All color combinations meet minimum contrast ratios:
- Normal text: {{NORMAL_TEXT_CONTRAST}} (4.5:1 minimum)
- Large text: {{LARGE_TEXT_CONTRAST}} (3:1 minimum)
- UI components: {{UI_CONTRAST}} (3:1 minimum)

### Keyboard Navigation

All interactive elements must be:
- ✅ Keyboard accessible (Tab, Enter, Space, Arrow keys)
- ✅ Have visible focus indicators
- ✅ Follow logical tab order

### Screen Reader Support

- ✅ All images have `alt` text
- ✅ Form inputs have associated labels
- ✅ ARIA attributes used where appropriate
- ✅ Semantic HTML structure

## Responsive Design

### Mobile-First Approach

Design and build for mobile first, enhance for larger screens:

```css
/* Mobile (default) */
.component {
  flex-direction: column;
}

/* Tablet and up */
@media (min-width: {{TABLET_BREAKPOINT}}) {
  .component {
    flex-direction: row;
  }
}

/* Desktop and up */
@media (min-width: {{DESKTOP_BREAKPOINT}}) {
  .component {
    max-width: {{DESKTOP_MAX_WIDTH}};
  }
}
```

### Touch Targets

Minimum touch target size: {{TOUCH_TARGET_SIZE}} (44x44px recommended)

## Dark Mode

### Dark Mode Colors

| Color | Light Mode | Dark Mode |
|-------|------------|-----------|
| Background | {{LIGHT_BACKGROUND}} | {{DARK_BACKGROUND}} |
| Surface | {{LIGHT_SURFACE}} | {{DARK_SURFACE}} |
| Text Primary | {{LIGHT_TEXT}} | {{DARK_TEXT}} |
| Text Secondary | {{LIGHT_TEXT_SECONDARY}} | {{DARK_TEXT_SECONDARY}} |

### Dark Mode Implementation

```css
:root {
  --background: {{LIGHT_BACKGROUND}};
  --text-primary: {{LIGHT_TEXT}};
}

[data-theme="dark"] {
  --background: {{DARK_BACKGROUND}};
  --text-primary: {{DARK_TEXT}};
}
```

## Design Tokens

### Token Format

```json
{
  "color": {
    "primary": {
      "value": "{{PRIMARY_COLOR}}",
      "type": "color"
    }
  },
  "spacing": {
    "md": {
      "value": "{{SPACING_MD}}",
      "type": "spacing"
    }
  }
}
```

### Implementation

**CSS Variables**:
```css
:root {
  --color-primary: {{PRIMARY_COLOR}};
  --spacing-md: {{SPACING_MD}};
  --font-body: {{PRIMARY_FONT}};
}
```

**JavaScript/TypeScript**:
```typescript
export const tokens = {
  color: {
    primary: '{{PRIMARY_COLOR}}',
  },
  spacing: {
    md: '{{SPACING_MD}}',
  },
};
```

## Component Development Guidelines

### Component Checklist

When creating new components:

- [ ] Follows design system colors and typography
- [ ] Implements all required variants and sizes
- [ ] Supports all interactive states (hover, focus, active, disabled)
- [ ] Accessible (WCAG {{WCAG_LEVEL}} compliant)
- [ ] Keyboard navigable
- [ ] Screen reader compatible
- [ ] Responsive across all breakpoints
- [ ] Supports dark mode
- [ ] Has Storybook documentation
- [ ] Has unit tests
- [ ] Has visual regression tests

## Usage Examples

### Complete Form Example

```jsx
<Form onSubmit={handleSubmit}>
  <Input
    label="Email"
    type="email"
    placeholder="you@example.com"
    required
  />
  <Input
    label="Password"
    type="password"
    helperText="Must be at least 8 characters"
    required
  />
  <Checkbox label="Remember me" />
  <Button type="submit" variant="primary">
    Sign In
  </Button>
</Form>
```

### Dashboard Card Example

```jsx
<Card variant="elevated">
  <CardHeader>
    <h3>{{CARD_TITLE}}</h3>
    <Badge variant="success">Active</Badge>
  </CardHeader>
  <CardBody>
    <p>{{CARD_CONTENT}}</p>
  </CardBody>
  <CardFooter>
    <Button variant="outline" size="sm">View Details</Button>
  </CardFooter>
</Card>
```

## Resources

- [Component Library]({{COMPONENT_LIBRARY_URL}})
- [Storybook]({{STORYBOOK_URL}})
- [Figma Design Files]({{FIGMA_URL}})
- [Icon Library]({{ICON_LIBRARY_URL}})
- [Accessibility Guidelines](./ACCESSIBILITY.md)

## Contributing

To contribute to the design system:

1. Review existing components and patterns
2. Propose new components via {{PROPOSAL_PROCESS}}
3. Follow component development guidelines
4. Submit for design review
5. Create PR with implementation and documentation

## Changelog

### Version {{VERSION}} - {{CURRENT_DATE}}

- {{CHANGE_1}}
- {{CHANGE_2}}
- {{CHANGE_3}}

---

*This design system is maintained by {{TEAM_NAME}}. For questions or contributions, contact {{DESIGN_TEAM_EMAIL}}.*
