# MakingIEGreatAgain

### A Voice Cloning Demo Built Entirely in Python with Flet

MakingIEGreatAgain transforms any text into the speaking style and voice of a political leader. You type a sentence, select a leader (Donald Trump or Nicolas Maduro), and the system rewrites it in their rhetorical style, then synthesizes speech audio that sounds like them. The entire application, both frontend and backend, is written in Python.

This README focuses on **how and why we chose Flet** for the frontend, the specific patterns that made it productive, and how each piece of the UI is constructed.

---

## Table of Contents

1. [Why Flet](#why-flet)
2. [Flet vs React vs Vue vs Streamlit](#flet-vs-react-vs-vue-vs-streamlit)
3. [System Architecture](#system-architecture)
4. [The Four Pages](#the-four-pages)
5. [The Five Reusable Components](#the-five-reusable-components)
6. [Design System](#design-system)
7. [Flet Patterns and Techniques](#flet-patterns-and-techniques)
8. [Routing](#routing)
9. [Frontend to Backend Communication](#frontend-to-backend-communication)
10. [Backend Overview](#backend-overview)
11. [Project Structure](#project-structure)
12. [Setup and Running](#setup-and-running)
13. [Testing](#testing)
14. [Future Enhancements](#future-enhancements)

---

## Why Flet

Flet is a Python framework that compiles to Flutter, giving you Material 3 design, smooth animations, and cross platform support (web, desktop, mobile) from a single Python codebase. We chose it for nine specific reasons:

### 1. Single Language Stack

The entire application is Python. Frontend, backend, API client, configuration, theming, routing, state management, tests. No JavaScript, no HTML, no CSS, no JSX, no TypeScript. For a team of Python developers, this eliminated an entire category of tooling, context switching, and hiring concerns.

### 2. Flutter Under the Hood

Flet compiles to Flutter, which means the rendered UI uses Flutter's Skia engine. The result is a Material 3 design system with proper elevation, shadows, ripple effects, and theming that adheres to Google's design specifications. We get all of this without writing a single line of Dart.

### 3. Rapid Prototyping

We built a full multi page web app with custom theming, interactive state management, async API calls, audio playback, and four distinct pages using five reusable components. The total frontend code is under 1,000 lines of Python across 12 files.

### 4. No Build Step

There is no webpack, no Vite, no npm, no `node_modules`, no bundler configuration, no transpilation. To start the frontend:

```bash
python -m frontend.main
```

The app opens in a browser. That is the entire build and deploy process for development.

### 5. Component Model

Flet's control based architecture maps naturally to composable UI design. Each component is a Python function that accepts typed parameters and returns an `ft.Container`. The function signature IS the component's API contract. No props interfaces, no TypeScript generics, no defaultProps.

### 6. Async Native

Flet's event system natively supports `async def` handlers. When you assign an `async def` function to `on_click`, Flet detects it via `inspect.iscoroutinefunction()` and properly awaits it. We use this for every API call so the UI never freezes while waiting for Claude or fal.ai to respond.

### 7. Mutable Control Updates

Instead of virtual DOM diffing (React) or reactivity tracking (Vue), Flet controls are mutable Python objects. To update the UI, you change `.value` on a control and call `.update()`. This is a simpler mental model: the control IS the element, and mutating it mutates the screen.

### 8. Built In Theming

Material 3 `ColorScheme`, custom fonts via URL, light and dark mode support, spacing utilities. All built into the framework. No Tailwind CSS, no styled components, no CSS modules, no design token libraries.

### 9. Built In Routing

`page.on_route_change` with an `ft.View` stack gives SPA routing without React Router, Vue Router, or any third party routing library. Navigation, route matching, view transitions, and browser back button support are all handled by the framework.

---

## Flet vs React vs Vue vs Streamlit

This table compares what we would have needed for the same application in other frameworks:

| Concern | Flet | React | Vue | Streamlit |
|---|---|---|---|---|
| **Language** | Python only | JavaScript/TypeScript + Python backend | JavaScript/TypeScript + Python backend | Python only |
| **Build tooling** | None | webpack/Vite + npm + node_modules | Vite + npm + node_modules | None |
| **UI update model** | Mutable objects + `.update()` | Virtual DOM diffing | Proxy based reactivity | Full page rerun |
| **State management** | Dataclass + rebuild function | useState/Redux/Zustand/Context | ref/reactive/Pinia | Session state dict |
| **Theming** | Built in Material 3 `ColorScheme` | Tailwind/styled components/CSS modules | Tailwind/Vuetify/CSS modules | Limited (st.set_page_config) |
| **Routing** | Built in `page.on_route_change` | React Router (separate package) | Vue Router (separate package) | Not supported (pages are files) |
| **Async event handlers** | `async def` detected automatically | useEffect + fetch + state updates | Composition API + async setup | Not supported (synchronous model) |
| **Component signature** | Python function with typed params | JSX + Props interface + generics | SFC with defineProps | st.columns/st.container (layout only) |
| **Cross platform** | Web + Desktop + Mobile from one codebase | Web only (need React Native for mobile) | Web only (need separate mobile framework) | Web only |
| **Design system** | Material 3 (Flutter) | Must install and configure | Must install (Vuetify/Quasar) | Material inspired, not customizable |
| **Total frontend files** | 12 Python files, ~1,000 lines | 20+ files (TSX + CSS + config + types) | 15+ files (SFC + config + types) | 1 file (but limited functionality) |

The key insight: **Streamlit is simpler but cannot do what we need** (multi page routing, async state, interactive components with hover effects, custom theming). **React and Vue can do everything but require a second language, a second ecosystem, and significantly more code.** Flet sits in the productive middle: Python's simplicity with Flutter's full UI capabilities.

---

## System Architecture

```
+-------------------+       HTTP/REST      +-------------------+
|                   | ------------------> |                   |
|   Flet Frontend   |                     |  FastAPI Backend   |
|   (port 8550)     | <----------------- |  (port 8000)       |
|                   |    JSON + Audio     |                   |
+-------------------+                     +--------+----------+
                                                   |
                                                   |  External APIs:
                                                   |
                                                   +-------> Claude API (Anthropic)
                                                   |         Text transformation via
                                                   |         leader specific metaprompt
                                                   |
                                                   +-------> fal.ai Qwen3 TTS 1.7B
                                                   |         Two step voice cloning:
                                                   |         speaker embedding + synthesis
                                                   |
                                                   v
                                          +-------------------+
                                          |   Audio Output    |
                                          |   WAV/MP3 files   |
                                          +-------------------+
```

**Data flow in five steps:**

1. The user types text and selects a political leader in the Flet frontend
2. The frontend sends the text to the FastAPI backend via HTTP (`/api/transform`)
3. The backend sends the text plus a leader specific metaprompt to the Claude API, which rewrites it in that leader's rhetorical style and language
4. The rewritten text is sent to the fal.ai Qwen3 TTS cloud API, which synthesizes speech using a pre cloned speaker embedding of the leader's voice
5. The generated audio file (WAV or MP3) is served back to the frontend for playback

---

## The Four Pages

### Home Page (`/`)

**File:** `frontend/pages/home.py`

The main interactive page where users perform voice cloning. It is organized into three zones that appear progressively as the user interacts:

**Zone 1: Leader Selection**
Two `build_leader_card()` components side by side in an `ft.Row`. Each card shows a portrait, the leader's name, and a language label. When selected, the card gets a gold border (3px), a gold glow shadow (12px blur), and full opacity on the portrait. When unselected, the portrait fades to 60% opacity with a subtle gray border.

**Zone 2: Text Input**
Appears only after a leader is selected. Contains the `build_text_input_panel()` component with a multiline `ft.TextField`, a live character counter that updates without rebuilding the page, and a "TRANSFORM TEXT" button with an inline `ft.ProgressRing` spinner during API calls.

**Zone 3: Audio Generation**
Appears only after text is transformed. Contains a "GENERATE AUDIO" button, an `ft.ProgressBar` that animates during the 15 to 30 second TTS generation, and then Play/Download buttons via `build_audio_player()`.

**State management:** A `HomeState` dataclass tracks seven fields: `selected_leader`, `input_text`, `transformed_text`, `is_transforming`, `is_generating`, `audio_url`, and `error_message`. When state changes, the `rebuild()` function clears `content_column.controls`, repopulates it from current state, and calls `content_column.update()`. This is the complete state management system. No Redux, no Zustand, no Context API, no stores.

```python
@dataclass
class HomeState:
    selected_leader: str | None = None
    input_text: str = ""
    transformed_text: str = ""
    is_transforming: bool = False
    is_generating: bool = False
    audio_url: str | None = None
    error_message: str | None = None
    max_input_length: int = field(
        default_factory=lambda: get_settings().max_input_length,
    )
```

### Trump Biography (`/bio/trump`)

**File:** `frontend/pages/bio_trump.py`

A static biography page laid out as a two column row: a 400x500 portrait on the left (using `ft.DecorationImage` with `BoxFit.COVER`) and a scrollable text column on the right with five biography paragraphs and a Key Facts card. The Key Facts card uses `ft.Row` controls with fixed width label containers and value text, inside a `SURFACE_DIM` background container.

### Maduro Biography (`/bio/maduro`)

**File:** `frontend/pages/bio_maduro.py`

Same layout architecture as the Trump page, adapted for Nicolas Maduro with his biographical content and portrait.

### Architecture Page (`/architecture`)

**File:** `frontend/pages/architecture.py`

Explains the system pipeline with five numbered steps. Each step number is rendered inside a gold bordered circle (36x36 `ft.Container` with `border_radius=18` and `ft.border.all(2, ACCENT_GOLD)`). Below the pipeline, a technology stack grid displays each layer (Frontend, Backend, LLM, TTS, Communication) in labeled rows inside a `SURFACE_DIM` card.

---

## The Five Reusable Components

Every component follows the same pattern: a Python function that accepts typed parameters and returns `ft.Container`. No classes, no inheritance, no JSX, no templates. The function signature is the component's contract.

### 1. Navigation Bar

**File:** `frontend/components/nav_bar.py`

```python
def build_nav_bar(page: ft.Page, active_route: str) -> ft.Container
```

A black (`#000000`) header bar, 64px tall, with horizontal padding. Contains:

| Element | Implementation |
|---|---|
| Brand text | `ft.Text` in Playfair Display, 22px bold, gold (#C5A572) |
| Nav buttons | `ft.TextButton` with `content=ft.Text(...)` for each route |
| Active state | Gold text at 100% opacity |
| Inactive state | White text at 70% opacity |
| Layout | `ft.Row` with `SPACE_BETWEEN` alignment |

**Critical Flet detail:** `ft.TextButton` in Flet 0.80.5 uses the `content=` parameter (accepting a control), NOT a `text=` parameter. This is a common gotcha when migrating from older Flet versions.

**Closure based navigation:** Each button needs its own route, but Python closures over loop variables capture the reference, not the value. The solution is a factory function:

```python
def _make_nav_click_handler(route: str):
    async def on_nav_click(e: ft.ControlEvent) -> None:
        await page.push_route(route)
    return on_nav_click
```

Each call to `_make_nav_click_handler("/bio/trump")` creates a new closure with its own captured `route` value.

### 2. Leader Card

**File:** `frontend/components/leader_card.py`

```python
def build_leader_card(
    name: str,
    language_label: str,
    is_selected: bool,
    on_select: Callable[[], None],
) -> ft.Container
```

A 280px wide clickable card. The visual states are:

| Property | Selected | Unselected | Hovered (unselected only) |
|---|---|---|---|
| Border | 3px gold (#C5A572) | 1px gray (#E0D8CC) | 1px light gold (#D4B98A) |
| Shadow blur | 12px gold glow | 4px subtle | 4px subtle |
| Portrait opacity | 1.0 | 0.6 | 0.6 |
| Name color | Gold (#C5A572) | Dark (#1A1A1A) | Dark (#1A1A1A) |

**Portrait rendering:** Uses `ft.Container.image` with `ft.DecorationImage(src=image_file, fit=ft.BoxFit.COVER, alignment=ft.Alignment.TOP_CENTER)`. The image file name is derived from the leader's last name (e.g., `"Trump.jpg"`), loaded from the Flet assets directory.

**Hover interaction:** The `on_hover` handler checks `e.data == "true"` for hover enter and mutates `e.control.border` directly, then calls `e.control.update()`. No state variable, no rebuild. The hover effect only fires when `is_selected` is `False`.

### 3. Text Input Panel

**File:** `frontend/components/text_input_panel.py`

```python
def build_text_input_panel(
    leader_name: str,
    on_text_change: Callable[[str], None],
    on_transform: Callable[[], Any],
    current_text: str,
    transformed_text: str,
    is_transforming: bool,
    max_length: int,
) -> ft.Container
```

A 600px wide panel containing:

| Element | Control | Details |
|---|---|---|
| Title | `subheading_text()` | "What should {leader_name} say?" |
| Text field | `ft.TextField` | Multiline, 3 to 8 lines, hint text, gold focus border |
| Character counter | `caption_text()` | "{count}/{max}" updated via mutable control |
| Transform button | `ft.Button` | Gold background, disabled when empty, inline ProgressRing during transform |
| Result display | `ft.Container` | Quote style with 4px gold left border |

**Live character counter (no rebuild):** This is one of the most important Flet patterns in the project. On every keystroke, the `handle_text_change` handler directly mutates the counter label and button state:

```python
def handle_text_change(e: ft.ControlEvent) -> None:
    value = e.control.value or ""
    on_text_change(value)
    # Update counter in place. No rebuild, no virtual DOM diff.
    counter_label.value = f"{len(value)}/{max_length}"
    counter_label.update()
    transform_button.disabled = len(value.strip()) == 0 or is_transforming
    transform_button.update()
```

In React, this would require `useState` + re render of the component tree. In Flet, it is two attribute assignments and two `.update()` calls.

**Async transform handler:** The `handle_transform` function is `async def`. Flet detects this via `inspect.iscoroutinefunction()` and awaits it. Inside, it delegates to the parent's `on_transform` callback and handles both sync and async return values:

```python
async def handle_transform(_e: ft.ControlEvent) -> None:
    result = on_transform()
    if hasattr(result, "__await__"):
        await result
```

**Quote style result:** The transformed text appears in a container with a gold left border using `ft.border.only(left=ft.BorderSide(4, ACCENT_GOLD))` and `ft.BorderRadius.only(top_right=8, bottom_right=8)`, over a `SURFACE_DIM` background. This creates a visual "blockquote" effect entirely with Flet layout primitives.

### 4. Audio Player

**File:** `frontend/components/audio_player.py`

```python
def build_audio_player(audio_url: str, page: ft.Page) -> ft.Container
```

Two buttons in a centered `ft.Row`:

| Button | Style | Action |
|---|---|---|
| "Play Audio" | Gold `ft.ElevatedButton` with play arrow icon | Opens audio URL via `UrlLauncher().launch_url()` |
| "Download" | Gray `ft.ElevatedButton` with download icon | Opens same URL to trigger browser download |

**`UrlLauncher` service:** This is a Flet Service (imported from `flet.controls.services.url_launcher`) that auto registers with the page context. It works across web, desktop, and mobile without platform specific code. Both handlers are `async def` for consistency with Flet's event system.

### 5. Page Header

**File:** `frontend/components/page_header.py`

```python
def build_page_header(title: str, subtitle: str | None = None) -> ft.Container
```

A centered column with:
1. Title in Playfair Display, 36px bold (via `display_text()`)
2. Optional subtitle in Inter, 20px medium (via `subheading_text()`)
3. Gold accent divider: an 80px wide, 3px tall `ft.Container` with `bgcolor=ACCENT_GOLD` and `border_radius=2`

Padded with `SPACING_XXL` (48px) top and `SPACING_LG` (24px) bottom.

---

## Design System

**File:** `frontend/theme.py`

The entire visual identity is defined in a single Python file with no CSS.

### Color Palette

| Token | Hex | Usage |
|---|---|---|
| `PRIMARY` | `#000000` | Navigation bar background, button text |
| `SURFACE` | `#FFFFFF` | Page backgrounds |
| `ON_SURFACE` | `#1A1A1A` | Body text |
| `ACCENT_GOLD` | `#C5A572` | Brand color, selected states, buttons, dividers |
| `ACCENT_GOLD_LIGHT` | `#D4B98A` | Hover states, progress bar backgrounds |
| `ACCENT_GOLD_DARK` | `#A8894F` | Dark theme accent |
| `ERROR` | `#B00020` | Error message backgrounds |
| `SURFACE_DIM` | `#F5F5F0` | Card backgrounds, quote containers |
| `DIVIDER` | `#E0D8CC` | Borders, separators |
| `ON_PRIMARY` | `#FFFFFF` | Text on dark backgrounds |

### Typography

Two fonts loaded from Google Fonts via raw URL (no npm package, no font file bundling):

```python
FONTS: dict[str, str] = {
    "Playfair Display": "https://raw.githubusercontent.com/.../PlayfairDisplay%5Bwght%5D.ttf",
    "Inter": "https://raw.githubusercontent.com/.../Inter%5Bopsz%2Cwght%5D.ttf",
}
```

Five typography helper functions:

| Function | Font | Size | Weight | Use Case |
|---|---|---|---|---|
| `display_text()` | Playfair Display | 36px | Bold | Page titles |
| `heading_text()` | Playfair Display | 28px | SemiBold (W_600) | Section headings |
| `subheading_text()` | Inter | 20px | Medium (W_500) | Panel titles, subtitles |
| `body_text()` | Inter | 16px | Normal | Paragraphs, descriptions |
| `caption_text()` | Inter | 12px | Normal | Labels, counters, metadata |

Each function returns a configured `ft.Text` control with an optional color override defaulting to `ON_SURFACE`.

### Spacing Scale

| Token | Value | Usage |
|---|---|---|
| `SPACING_XS` | 4px | Tight gaps |
| `SPACING_SM` | 8px | Icon spacing, minor gaps |
| `SPACING_MD` | 16px | Standard padding, inter element gaps |
| `SPACING_LG` | 24px | Section padding, card padding |
| `SPACING_XL` | 32px | Card row spacing |
| `SPACING_XXL` | 48px | Page top padding, major sections |
| `SECTION_GAP` | 64px | Between major page sections |

### Material 3 Theme Configuration

Both light and dark themes are constructed via `ft.Theme(color_scheme=ft.ColorScheme(...))`, mapping our gold accent palette to Material 3 semantic roles:

```python
def build_light_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ACCENT_GOLD,
            on_primary=PRIMARY,
            primary_container=ACCENT_GOLD_LIGHT,
            on_primary_container=PRIMARY,
            secondary=ON_SURFACE,
            on_secondary=ON_PRIMARY,
            surface=SURFACE,
            on_surface=ON_SURFACE,
            surface_dim=SURFACE_DIM,
            error=ERROR,
            outline=DIVIDER,
            shadow=PRIMARY,
        ),
        font_family="Inter",
    )
```

The dark theme variant adjusts surface colors to `#111111` backgrounds with `#F5F5F0` text, while keeping the gold accent consistent.

### Environment Driven Theming

**File:** `frontend/config.py`

Colors are configurable via environment variables. The `FrontendSettings` frozen dataclass reads `COLOR_PRIMARY`, `COLOR_ACCENT_GOLD`, `COLOR_SURFACE`, and `COLOR_ON_SURFACE` from `.env`, with sensible defaults. Change the entire app's visual identity by editing four lines in `.env`.

```python
@dataclass(frozen=True)
class FrontendSettings:
    color_primary: str = field(default_factory=lambda: _env("COLOR_PRIMARY", "#000000"))
    color_accent_gold: str = field(default_factory=lambda: _env("COLOR_ACCENT_GOLD", "#C5A572"))
    color_surface: str = field(default_factory=lambda: _env("COLOR_SURFACE", "#FFFFFF"))
    color_on_surface: str = field(default_factory=lambda: _env("COLOR_ON_SURFACE", "#1A1A1A"))
```

---

## Flet Patterns and Techniques

These are the eight core patterns that made this project work. Each pattern solves a specific problem that would require significantly more complexity in a traditional frontend framework.

### Pattern 1: Functional Component Architecture

Every UI element is a pure Python function returning `ft.Container`. No classes, no inheritance, no decorators, no JSX, no templates. The function signature defines the component's API:

```python
def build_leader_card(
    name: str,
    language_label: str,
    is_selected: bool,
    on_select: Callable[[], None],
) -> ft.Container:
```

Python's type annotations serve as the "Props interface." `Callable[[], None]` is equivalent to React's `() => void` callback prop.

### Pattern 2: State as Dataclass + Rebuild

The home page uses a plain Python `@dataclass` for state. On any state change, the `rebuild()` function clears the content column's controls list, repopulates it from current state, and calls `.update()`:

```python
def rebuild() -> None:
    content_column.controls.clear()
    content_column.controls.extend([header, build_zone_1(), build_zone_2(), build_zone_3()])
    content_column.update()
```

This replaces Redux, Zustand, Pinia, Context API, and every other state management library. It is not the most efficient approach for a large application, but for a demo with a bounded UI, it is drastically simpler.

### Pattern 3: Mutable Control Updates (No Rebuild)

For high frequency events like keystrokes, we do NOT call `rebuild()`. Instead, we directly mutate the specific control that changed:

```python
counter_label.value = f"{len(value)}/{max_length}"
counter_label.update()
```

Two lines. No virtual DOM diffing, no re render cascade, no `shouldComponentUpdate`, no `React.memo`, no `useMemo`. The control IS the DOM element (conceptually), and mutating it updates only that element on screen.

**When to use which:** Use `rebuild()` for state transitions (leader selection, API response received). Use mutable updates for continuous events (typing, hovering).

### Pattern 4: Async Event Handlers with Thread Offloading

API calls to Claude and fal.ai take 2 to 30 seconds. Blocking the Flet event loop would freeze the entire UI. The solution:

```python
async def on_transform() -> None:
    state.is_transforming = True
    rebuild()  # Show spinner immediately

    result = await asyncio.to_thread(
        get_api_client().transform_text,
        state.selected_leader,
        state.input_text,
    )

    state.transformed_text = result.transformed_text
    state.is_transforming = False
    rebuild()  # Show result, hide spinner
```

`asyncio.to_thread()` runs the blocking `httpx` call in a background thread. The `await` yields control back to Flet's event loop, which keeps the ProgressBar animating and the UI responsive. When the thread completes, execution resumes and `rebuild()` shows the result.

**The lambda trap:** Wrapping an async handler in `lambda _e: handler()` breaks Flet's `inspect.iscoroutinefunction()` detection, because the lambda is a sync function that returns a coroutine. Flet will call it without `await`, and the coroutine is silently dropped. Always pass async handlers directly, or use the factory pattern (see Pattern 5).

### Pattern 5: Closure Based Event Handler Factories

Navigation buttons in a loop need per button route capture. Python closures over loop variables capture the variable reference, not the value, so all buttons would navigate to the last route. The fix is a factory function:

```python
def _make_nav_click_handler(route: str):
    async def on_nav_click(e: ft.ControlEvent) -> None:
        await page.push_route(route)
    return on_nav_click
```

Each call creates a new closure with its own `route` binding. The returned function is `async def`, so Flet correctly detects and awaits it.

### Pattern 6: Container as Universal Layout Primitive

`ft.Container` replaces HTML's `<div>` plus CSS entirely. A single Container can handle:

| Capability | Property |
|---|---|
| Background color | `bgcolor` |
| Borders (per side) | `border` via `ft.border.all()` or `ft.border.only()` |
| Border radius | `border_radius` |
| Box shadows | `shadow` via `ft.BoxShadow` |
| Padding and margin | `padding`, `margin` via `ft.Padding`, `ft.Margin` |
| Click events | `on_click` |
| Hover events | `on_hover` |
| Background images | `image` via `ft.DecorationImage` |
| Content alignment | `alignment` via `ft.Alignment` |
| Clipping | `clip_behavior` via `ft.ClipBehavior` |
| Fixed dimensions | `width`, `height` |

One Python object replaces what would be a `<div>` tag plus 10+ CSS properties in a traditional web stack.

### Pattern 7: Environment Driven Theming

The color palette flows from `.env` through three layers:

```
.env  -->  FrontendSettings (frozen dataclass)  -->  theme.py constants  -->  ft.Theme(color_scheme=...)
```

The `FrontendSettings` instance is cached as a module level singleton via `get_settings()`. Theme constants are resolved at import time. To change the entire app's visual identity:

```bash
# .env
COLOR_ACCENT_GOLD=#FF6B35  # Now the app is orange instead of gold
```

### Pattern 8: Service Based URL Launching

The `UrlLauncher` from `flet.controls.services.url_launcher` is a Flet Service that auto registers with the page context. It abstracts platform differences for opening URLs:

```python
from flet.controls.services.url_launcher import UrlLauncher

async def on_play(_e: ft.ControlEvent) -> None:
    await UrlLauncher().launch_url(audio_url)
```

On web, it opens a new browser tab. On desktop, it opens the default browser. On mobile, it opens the in app browser. One line of code, three platforms.

---

## Routing

**File:** `frontend/router.py`

The routing system maps URL strings to page builder modules:

```python
_ROUTE_BUILDERS: dict[str, object] = {
    "/": home,
    "/bio/trump": bio_trump,
    "/bio/maduro": bio_maduro,
    "/architecture": architecture,
}
```

Each module exposes a `build(page: ft.Page) -> list[ft.Control]` function. The router calls `builder_module.build(page)`, wraps the result in an `ft.View` with the shared navigation bar and a scrollable content column, and pushes it onto the page's view stack.

**Route change handler** in `main.py`:

```python
def route_change() -> None:
    page.views.clear()
    page.views.append(build_view(page, page.route))
    page.update()
```

**Browser back button** is handled by `view_pop`:

```python
async def view_pop(e: ft.ViewPopEvent) -> None:
    if e.view is not None:
        page.views.remove(e.view)
        top_view = page.views[-1]
        await page.push_route(top_view.route)
```

Unknown routes fall back to `/` via `resolved_route = route if route in _ROUTE_BUILDERS else "/"`.

---

## Frontend to Backend Communication

**File:** `frontend/api_client.py`

A singleton `APIClient` wraps `httpx.Client` with a 180 second timeout (TTS generation can take 15 to 30 seconds):

```python
class APIClient:
    def __init__(self, base_url: str | None = None) -> None:
        self._client = httpx.Client(base_url=base_url, timeout=180.0)

    def transform_text(self, leader: str, text: str) -> TransformResult: ...
    def generate_tts(self, leader: str, text: str) -> TTSResult: ...
    def get_audio_url(self, audio_path: str) -> str: ...
```

Return types are frozen dataclasses:

```python
@dataclass(frozen=True)
class TransformResult:
    original_text: str
    transformed_text: str
    leader: str
    language: str

@dataclass(frozen=True)
class TTSResult:
    audio_url: str
    duration_seconds: float
    sample_rate: int
```

**Thread offloading:** Because `httpx.Client` is synchronous, all API calls from async Flet handlers go through `asyncio.to_thread()`:

```python
result = await asyncio.to_thread(
    get_api_client().transform_text, state.selected_leader, state.input_text
)
```

This keeps the Flet UI thread free to handle animations and user input while the HTTP request runs in a background thread.

---

## Backend Overview

**File:** `backend/main.py`

FastAPI application with two router modules:

| Endpoint | Method | Module | Purpose |
|---|---|---|---|
| `/api/transform` | POST | `routers/transform.py` | Send text + leader to Claude API, return transformed text |
| `/api/tts` | POST | `routers/tts.py` | Send text + leader to fal.ai Qwen3 TTS, return audio metadata |
| `/api/audio/{filename}` | GET | `routers/tts.py` | Serve generated audio files with correct MIME types |
| `/api/health` | GET | `main.py` | Health check |
| `/api/docs` | GET | Built in | Swagger UI documentation |

**LLM Service** (`backend/services/llm_service.py`): Wraps the Anthropic Python SDK. Sends the user's text as a message with a leader specific system prompt (metaprompt). Trump's metaprompt produces English in his rhetorical style. Maduro's metaprompt produces Spanish in his political oratory style.

**TTS Service** (`backend/services/tts_service.py`): Calls the fal.ai Qwen3 TTS 1.7B cloud API in two steps. First, speaker embeddings are pre generated from 30 second reference audio clips (via `scripts/upload_ref_audio.py`) and stored in `data/fal_voice_config.json`. Then, at synthesis time, the service sends the transformed text plus the speaker embedding URL to fal.ai, which generates the audio. The result is downloaded and saved locally as a WAV or MP3 file.

---

## Project Structure

```
making-ie-great-again/
    backend/
        __init__.py
        config.py                  # Environment config (API keys, paths, model IDs)
        main.py                    # FastAPI app with CORS and router mounts
        models/
            __init__.py
            schemas.py             # Pydantic v2 request/response models
        prompts/
            __init__.py
            trump_metaprompt.py    # Claude system prompt for Trump style
            maduro_metaprompt.py   # Claude system prompt for Maduro style
        routers/
            __init__.py
            transform.py           # POST /api/transform endpoint
            tts.py                 # POST /api/tts + GET /api/audio/{filename}
        services/
            __init__.py
            llm_service.py         # Claude API client (Anthropic SDK)
            tts_service.py         # fal.ai Qwen3 TTS client + audio download
    frontend/
        __init__.py
        config.py                  # FrontendSettings frozen dataclass from .env
        main.py                    # Flet app entry (fonts, themes, routing, launch)
        api_client.py              # Singleton httpx client for backend REST API
        router.py                  # URL to page module mapping + View builder
        theme.py                   # Colors, fonts, spacing, Material 3 themes
        assets/
            Trump.jpg              # Leader portrait (served by Flet asset system)
            Maduro.jpg             # Leader portrait
        components/
            __init__.py
            audio_player.py        # Play/Download buttons with UrlLauncher
            leader_card.py         # Clickable portrait card with selection state
            nav_bar.py             # Black header bar with gold brand + nav buttons
            page_header.py         # Centered title + subtitle + gold divider
            text_input_panel.py    # TextField + counter + transform button + result
        pages/
            __init__.py
            home.py                # Main page: leader select, text input, audio gen
            bio_trump.py           # Trump biography with portrait and key facts
            bio_maduro.py          # Maduro biography with portrait and key facts
            architecture.py        # System pipeline and tech stack explanation
    tests/
        __init__.py
        conftest.py                # Shared test fixtures
        unit/
            __init__.py
            test_config.py         # Config loading tests
            test_llm_service.py    # LLM service unit tests
            test_schemas.py        # Pydantic model validation tests
            test_tts_service.py    # TTS service unit tests (mock mode)
        integration/
            __init__.py
            test_transform_api.py  # Transform endpoint integration tests
            test_tts_api.py        # TTS endpoint integration tests
        e2e/
            __init__.py
            conftest.py            # Playwright browser fixtures
            test_full_flow.py      # Complete user flow E2E test
            test_home_page.py      # Home page interaction tests
            test_leader_selection.py  # Leader card selection tests
            test_navigation.py     # Navigation and routing tests
    scripts/
        run_all.sh                 # Start backend + frontend together
        run_backend.sh             # Start FastAPI with uvicorn
        run_frontend.sh            # Start Flet frontend
        transcribe.py              # Transcribe reference audio for TTS config
        upload_ref_audio.py        # Upload audio to fal CDN + generate embeddings
    data/
        fal_voice_config.json      # Pre generated speaker embeddings + reference text
        trump_30s.wav              # Trump reference audio (30s clip)
        trump_transcript.txt       # Trump reference audio transcript
        maduro_30s.wav             # Maduro reference audio (30s clip)
        maduro_transcript.txt      # Maduro reference audio transcript
    output/                        # Generated audio files (WAV/MP3)
    pyproject.toml                 # Project metadata, dependencies, tool config
    Makefile                       # Development commands (install, lint, test, run)
    CLAUDE.md                      # AI assistant project context
    HANDOFF.md                     # Development state and next steps
```

---

## Setup and Running

### Prerequisites

- Python 3.11 or later
- An Anthropic API key (for Claude text transformation)
- A fal.ai API key (for Qwen3 TTS voice cloning)

### Installation

```bash
# Clone and enter the project directory
cd making-ie-great-again

# Copy environment template and set API keys
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY and FAL_KEY

# Install all dependencies (dev + TTS extras + Playwright browser)
make install
```

### Preparing Voice Embeddings

Before using TTS, you must upload reference audio and generate speaker embeddings:

```bash
FAL_KEY=your-key python scripts/upload_ref_audio.py
```

This uploads the 30 second WAV clips from `data/` to the fal CDN, clones each voice via Qwen3 TTS, and saves the resulting speaker embeddings to `data/fal_voice_config.json`.

### Running the Application

Start the backend and frontend in separate terminals:

```bash
# Terminal 1: FastAPI backend on port 8000
make backend

# Terminal 2: Flet frontend on port 8550
make frontend
```

Or use the combined script:

```bash
scripts/run_all.sh
```

Then open `http://localhost:8550` in your browser.

---

## Testing

| Command | Description | Requirements |
|---|---|---|
| `make test-unit` | Unit tests (mocked dependencies) | None |
| `make test-integration` | API integration tests | Backend running |
| `make test-e2e` | Playwright browser tests | Both servers running |
| `make lint` | Ruff linter + format check | None |
| `make typecheck` | mypy in strict mode | None |
| `make format` | Auto fix formatting and lint issues | None |

Integration and E2E tests skip gracefully when the required servers are not running.

The test suite covers: configuration loading, Pydantic model validation, LLM service transformation, TTS service generation (mock mode), API endpoint responses, full user flow through the browser (leader selection, text input, transformation, audio generation), navigation between pages, and leader card interaction states.

---

## Future Enhancements

- **Inline HTML5 audio player:** Replace browser tab playback once Flet's web audio service matures
- **Real time streaming TTS:** Play audio as it generates, chunk by chunk
- **Additional world leaders:** More voice embeddings and metaprompts
- **Dark mode toggle:** Add a switch to the navigation bar (theme infrastructure already supports light and dark)
- **Drag and drop reference audio:** Upload custom voice clips for ad hoc voice cloning
- **Side by side comparison:** Show original text next to transformed text
- **Audio waveform visualization:** Render waveforms using Flet's Canvas control
- **Mobile responsive layout:** Use `page.width` breakpoints for adaptive layouts
- **WebSocket progress updates:** Real time generation progress instead of indeterminate progress bar
- **Generation history panel:** Save and replay previous transformations

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `flet` | 0.80.5 | Frontend framework (compiles to Flutter) |
| `fastapi` | 0.115+ | Backend REST API |
| `uvicorn` | 0.34+ | ASGI server for FastAPI |
| `httpx` | 0.28+ | HTTP client (frontend to backend + audio download) |
| `anthropic` | 0.52+ | Claude API SDK for text transformation |
| `python-dotenv` | 1.0+ | Environment variable loading from .env |
| `pydantic` | 2.10+ | Request/response data validation |
| `soundfile` | 0.13+ | Audio file reading (duration, sample rate) |
| `numpy` | 2.0+ | Audio array processing |
| `fal-client` | 0.5+ | fal.ai cloud API client for TTS |

Dev dependencies: `pytest`, `pytest-asyncio`, `pytest-playwright`, `playwright`, `ruff`, `mypy`, `coverage`.
