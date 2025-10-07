"""Figure module."""

import geofig.geometry as gg
import math
import sympy as sp
import xml.etree.ElementTree as et

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from sympy.geometry.entity import GeometryEntity
from typing import Any, Iterable


def _n(x: Any) -> int | float:
    f = round(float(x), 4)
    i = int(f)
    return i if i == f else f


@dataclass
class _Bounds:
    """Bounding box."""

    xmin: gg.Scalar
    ymin: gg.Scalar
    xmax: gg.Scalar
    ymax: gg.Scalar

    def union(self, other: "_Bounds") -> "_Bounds":
        """Return the union of this and another bounding box."""
        return _Bounds(
            sp.Min(self.xmin, other.xmin),
            sp.Min(self.ymin, other.ymin),
            sp.Max(self.xmax, other.xmax),
            sp.Max(self.ymax, other.ymax),
        )


def _kw(kwargs: dict[str, Any]) -> dict[str, Any]:
    return {k.rstrip("_").replace("_", "-"): v for k, v in kwargs.items()}


_CSS_KEY = str | tuple[str, ...]


class CSS:
    """
    Dynamic cascading style sheet.

    When the style sheet is generated (converted to a string), only styles that have been
    selected are included.

    The dynamic style sheet acts like a dictionary, whose keys are can be string for a single
    selector, and tuple of strings for a group selector.
    """

    rules: dict[_CSS_KEY, str]
    selected: set[str]

    def __init__(self, rules: dict[_CSS_KEY, str] | None = None):
        self.rules = {}
        self.selected = set(("*", "svg"))
        if rules:
            self.rules.update(rules)

    def __bool__(self) -> bool:
        return bool(self.rules)

    def __str__(self) -> str:
        result = []
        result.append("")
        for key, value in self.rules.items():
            if isinstance(key, str):
                key = (key,)
            if selectors := ", ".join(s for s in key if s in self.selected):
                result.append(f"{selectors} {{")
                for line in value.split("\n"):
                    line = line.strip()
                    if line:
                        result.append(f"\t{line}")
                result.append("}")
        result.append("")
        return f"{'\n'.join(result)}"

    def __setitem__(self, key: _CSS_KEY, value: str) -> None:
        if key in self.rules:
            raise ValueError(f"{key} rule already defined")
        self.rules[key] = value

    def select(self, element: et.Element) -> None:
        """Select an element and its attributes for styling."""

        def _select(_element: et.Element) -> None:
            self.selected.add(_element.tag)
            keys = _element.keys()
            if id := _element.get("id"):
                self.selected.add(f"#{id}")
            if classes := _element.get("class"):
                for cls in classes.split(" "):
                    self.selected.add(f".{cls}")

        _select(element)
        for subelement in element:
            _select(subelement)

    def update(self, rules: dict[_CSS_KEY, str]) -> None:
        for key, value in rules.items():
            self[key] = value


@dataclass
class Padding:
    """Figure padding."""

    top: int | float
    right: int | float
    bottom: int | float
    left: int | float


@dataclass
class Scale:
    """Figure scale."""

    x: int | float = 1
    y: int | float = 1


class ts:
    """A text span, for inclusion in figure text."""

    def __init__(self, text: str, **kwargs: Any):
        self.text = text
        self.kwargs = kwargs


class Figure:
    """
    A geometric figure, expressed on a Cartesian plane, rendered as an SVG drawing.

    Parameters and attributes:
    • background: attributes for background rectangle
    • css: cascading style sheet included in scalable vector graphic
    • description: a description of the figure
    • scale: the scaling factor to be applied to scalable vector graphic
    • title: the figure title

    If a background is specified, a rectangle with the dimensions of the figure
    and any attributes associated with the background will be added as the first object.
    """

    background: dict[str, Any] | None
    css: CSS | None
    description: str | None
    padding: Padding
    scale: Scale
    title: str | None

    def __init__(
        self,
        *,
        background: dict[str, Any] | None = None,
        css: CSS | None = None,
        description: str | None = None,
        padding: int | float | Padding = 8,
        scale: int | float | Scale = 1,
        title: str | None = None,
    ):
        self.background = background
        self.css = css
        self.description = description
        self.padding = (
            padding
            if isinstance(padding, Padding)
            else Padding(padding, padding, padding, padding)
        )
        self.scale = scale if isinstance(scale, Scale) else Scale(x=scale, y=scale)
        self.title = title

        self._bounds: _Bounds | None = None
        self._ops: list[Callable[[gg.Transformer], et.Element]] = []

    def arc(self, arc: gg.Arc, **kwargs: Any):
        """Add an arc to the figure."""

        def op(transformer: gg.Transformer) -> et.Element:
            _arc = transformer.apply(arc)
            return et.Element(
                "path",
                d=(
                    f"M {_n(_arc.points[0].x)} {_n(_arc.points[0].y)} "
                    f"A "
                    f"{_n(_arc.ellipse.hradius)} "  # rx
                    f"{_n(_arc.ellipse.vradius)} "  # ry
                    f"0 "  # rotation
                    f"{int(bool(_arc.length > sp.pi or _arc.length < -sp.pi))} "  # large_arc
                    f"{int(bool(_arc.length > 0))} "  # sweep
                    f"{_n(_arc.points[1].x)} "  # x
                    f"{_n(_arc.points[1].y)}"  # y
                ),
                **_kw(kwargs),
            )

        self._ops.append(op)
        self.include(arc)

    def circle(self, circle: sp.Circle, **kwargs: Any) -> None:
        """Add a circle to the figure."""

        def op(transformer: gg.Transformer) -> et.Element:
            _circle = transformer.apply(circle)
            if isinstance(_circle, sp.Circle):
                return et.Element(
                    "circle",
                    cx=f"{_n(_circle.center.x)}",
                    cy=f"{_n(_circle.center.y)}",
                    r=f"{_n(_circle.radius)}",
                    **_kw(kwargs),
                )
            elif isinstance(_circle, sp.Ellipse):  # transformed to ellipse
                return et.Element(
                    "ellipse",
                    cx=f"{_n(_circle.center.x)}",
                    cy=f"{_n(_circle.center.y)}",
                    rx=f"{_n(_circle.hradius)}",
                    ry=f"{_n(_circle.vradius)}",
                    **_kw(kwargs),
                )
            raise TypeError(f"unsupported type: {type(_circle)}")

        self._ops.append(op)
        self.include(circle)

    def curve(
        self, *args: Any, samples: int = 10, tension: float = 1 / 6, **kwargs: Any
    ) -> None:
        """
        Add a curve to the figure.

        Parameters:
        • args: a single parameterized Curve object, or multiple Point objects
        • samples: number of vertices to sample for parameterized curve
        • tension: Catmull-Rom smoothing factor (0 < tension ≤ 0.5)
        """

        vertices = gg.discretize(args[0], samples) if len(args) == 1 else list(args)
        if len(vertices) < 2:
            return

        def _distinct(points: list[sp.Point], tolerance: float = 1e-6) -> list[sp.Point]:
            out = []
            last = None
            for p in points:
                if last is None or float(p.distance(last)) > tolerance:
                    out.append(p)
                    last = p
            return out

        vertices = _distinct(vertices)
        if len(vertices) < 2:
            return

        def op(transformer: gg.Transformer) -> et.Element:
            _v = [transformer.apply(v) for v in vertices]

            def _closed(points: list[sp.Point], tolerance: float = 1e-6) -> bool:
                if len(points) < 3:
                    return False
                p0, pn = points[0], points[-1]
                d2 = (p0.x - pn.x) ** 2 + (p0.y - pn.y) ** 2
                return float(d2) < tolerance**2

            closed = _closed(_v)
            if closed:
                _v = _v[:-1]
            n = len(_v)
            commands = [f"M {_n(_v[0].x)} {_n(_v[0].y)}"]
            if n == 2:
                commands.append(f"L {_n(_v[1].x)} {_n(_v[1].y)}")
            else:
                t = float(tension)

                def at(k: int) -> sp.Point:
                    if closed:
                        return _v[k % n]
                    if k < 0:
                        return sp.Point(2 * _v[0].x - _v[1].x, 2 * _v[0].y - _v[1].y)
                    if k >= n:
                        return sp.Point(
                            2 * _v[n - 1].x - _v[n - 2].x, 2 * _v[n - 1].y - _v[n - 2].y
                        )
                    return _v[k]

                for i in range(n if closed else n - 1):
                    p0, p1, p2, p3 = at(i - 1), at(i), at(i + 1), at(i + 2)
                    cp1 = sp.Point(p1.x + (p2.x - p0.x) * t, p1.y + (p2.y - p0.y) * t)
                    cp2 = sp.Point(p2.x - (p3.x - p1.x) * t, p2.y - (p3.y - p1.y) * t)

                    if i == 0:
                        commands.append(
                            f"C {_n(cp1.x)} {_n(cp1.y)} {_n(cp2.x)} {_n(cp2.y)} {_n(p2.x)} {_n(p2.y)}"
                        )
                    else:
                        commands.append(f"S {_n(cp2.x)} {_n(cp2.y)} {_n(p2.x)} {_n(p2.y)}")
            if closed:
                commands.append("Z")
            return et.Element("path", d=" ".join(commands), **_kw(kwargs))

        self._ops.append(op)
        for vertex in vertices:
            self.include(vertex)

    def ellipse(self, ellipse: sp.Ellipse, **kwargs: Any) -> None:
        """Add an ellipse to the figure."""

        def op(transformer: gg.Transformer) -> et.Element:
            _ellipse = transformer.apply(ellipse)
            if isinstance(_ellipse, sp.Ellipse):
                return et.Element(
                    "ellipse",
                    cx=f"{_n(_ellipse.center.x)}",
                    cy=f"{_n(_ellipse.center.y)}",
                    rx=f"{_n(_ellipse.hradius)}",
                    ry=f"{_n(_ellipse.vradius)}",
                    **_kw(kwargs),
                )
            elif isinstance(_ellipse, sp.Circle):  # transformed to circle
                return et.Element(
                    "circle",
                    cx=f"{_n(_ellipse.center.x)}",
                    cy=f"{_n(_ellipse.center.y)}",
                    r=f"{_n(_ellipse.radius)}",
                    **_kw(kwargs),
                )
            raise TypeError(f"unsupported type: {type(_ellipse)}")

        self._ops.append(op)
        self.include(ellipse)

    def line(self, *args: sp.Segment | sp.Point, **kwargs: Any) -> None:
        """
        Add a line to figure.

        The line can be expressed as either a single `Segment`, or two `Point`s.
        """

        if len(args) == 1:
            segment = args[0]
            if not isinstance(segment, sp.Segment):
                raise ValueError("single argument must be segment")
        elif len(args) == 2:
            p1, p2 = args[0], args[1]
            if not isinstance(p1, sp.Point) or not isinstance(p2, sp.Point):
                raise ValueError("two arguments must be points")
            segment = sp.Segment(p1, p2)
        else:
            raise ValueError("require single segment or two points")

        def op(transformer: gg.Transformer) -> et.Element:
            _segment = transformer.apply(segment)
            return et.Element(
                "line",
                x1=f"{_n(_segment.p1.x)}",
                y1=f"{_n(_segment.p1.y)}",
                x2=f"{_n(_segment.p2.x)}",
                y2=f"{_n(_segment.p2.y)}",
                **_kw(kwargs),
            )

        self._ops.append(op)
        self.include(segment)

    def path(
        self, *entities: Iterable[gg.Arc | sp.Segment], close: bool = False, **kwargs: Any
    ) -> None:
        """
        Add a connected path to the figure.

        Parameters:
        • entities: sequence of arc or segment objects that define the path
        • close: close the path to the starting point
        """

        def op(transformer: gg.Transformer) -> et.Element:
            _entities = [transformer.apply(entity) for entity in entities]
            commands = []
            last = None
            count = len(_entities)
            for n in range(count):
                entity = _entities[n]
                p1, p2 = entity.points
                if last == p2:
                    p1, p2 = p2, p1
                if last != p1:
                    if n < count - 1:
                        next = _entities[n + 1]
                        if p1 in next.points:
                            p1, p2 = p2, p1
                if last != p1:
                    commands.append(f"M {_n(p1.x)} {_n(p1.y)}")
                if isinstance(entity, sp.Segment):
                    commands.append(f"L {_n(p2.x)} {_n(p2.y)}")
                elif isinstance(entity, gg.Arc):
                    commands.append(
                        f"A "
                        f"{_n(entity.ellipse.hradius)} "  # rx
                        f"{_n(entity.ellipse.vradius)} "  # ry
                        f"0 "  # rotation
                        f"{int(bool(entity.length > sp.pi or entity.length < -sp.pi))} "  # large_arc
                        f"{int((bool(entity.length > 0) ^ (p1 != entity.points[0])))} "  # sweep
                        f"{_n(p2.x)} "  # x
                        f"{_n(p2.y)}"  # y
                    )
                else:
                    raise ValueError(f"unsupported entity: {type(entity)}")
                last = p2
            if close:
                commands.append("Z")
            return et.Element("path", d=" ".join(commands), **_kw(kwargs))

        self._ops.append(op)
        for entity in entities:
            self.include(entity)

    def polygon(self, *args: sp.Polygon | sp.Point, **kwargs: Any) -> None:
        """
        Add a polygon to the figure.

        The polygon can be expressed as either a single `Polygon`, or three or more
        `Point`s.
        """

        if len(args) == 1:
            polygon = args[0]
            if not isinstance(polygon, sp.Polygon):
                raise ValueError("single argument must be polygon")
        elif len(args) >= 3:
            polygon = sp.Polygon(*args)
        else:
            raise ValueError("require single polygon or three or more points")

        def op(transformer: gg.Transformer) -> et.Element:
            _polygon = transformer.apply(polygon)
            return et.Element(
                "polygon",
                points=" ".join(f"{_n(v.x)} {_n(v.y)}" for v in _polygon.vertices),
                **_kw(kwargs),
            )

        self._ops.append(op)
        self.include(polygon)

    def polyline(self, *vertices: sp.Point, **kwargs: Any) -> None:
        """Add a polyline to the figure."""

        def op(transformer: gg.Transformer) -> et.Element:
            _vertices = [transformer.apply(vertex) for vertex in vertices]
            return et.Element(
                "polyline",
                points=" ".join(f"{_n(v.x)} {_n(v.y)}" for v in _vertices),
                **_kw(kwargs),
            )

        self._ops.append(op)
        for vertex in vertices:
            self.include(vertex)

    def text(
        self,
        text: str | Iterable[str | ts],
        point: sp.Point,
        *,
        sx: gg.Scalar = 0,
        sy: gg.Scalar = 0,
        **kwargs: Any,
    ) -> None:
        """
        Add text to the figure.

        Parameters:
        • text: text and/or text spans to be added
        • point: point of text, in Cartesian space
        • sx: shift x-axis offset in SVG pixels
        • sy: shift y-axis offset in SVG pixels

        Example:

        ```
        origin = Point(0, 0)
        fig.text("This is normal text.", origin)
        fig.text(("This is ", ts("italic", class_="italic"), " text."), origin, sy=18)
        ```
        """

        def op(transformer: gg.Transformer) -> et.Element:
            _point = transformer.apply(point)
            _text = (text,) if isinstance(text, str) else text
            element = et.Element(
                "text",
                x=f"{_n(_point.x + sx)}",
                y=f"{_n(_point.y + sy)}",
                **_kw(kwargs),
            )
            for part in _text:
                if isinstance(part, str):
                    if not len(element):
                        element.text = f"{element.text or ''}{part}"
                    else:
                        element[-1].tail = f"{element[-1].tail or ''}{part}"
                else:
                    tspan = et.Element("tspan", **_kw(part.kwargs))
                    tspan.text = part.text
                    element.append(tspan)
            return element

        self._ops.append(op)
        self.include(point)

    def include(self, entity: GeometryEntity) -> None:
        """Include an entity in the figure's bounding box."""
        bounds = _Bounds(*entity.bounds)
        self._bounds = self._bounds.union(bounds) if self._bounds else bounds

    def save(self, path: str | Path) -> None:
        """Save the figure as an SVG file."""
        if not self._ops:
            raise RuntimeError("nothing to save")
        transformer = gg.Transformer()
        transformer.scale(self.scale.x, -self.scale.y)
        transformer.translate(
            -self._bounds.xmin * self.scale.x + self.padding.left,
            self._bounds.ymax * self.scale.y + self.padding.top,
        )
        width = math.ceil(
            _n(
                (self._bounds.xmax - self._bounds.xmin) * self.scale.x
                + self.padding.right
                + self.padding.left
            )
        )
        height = math.ceil(
            _n(
                (self._bounds.ymax - self._bounds.ymin) * self.scale.y
                + self.padding.top
                + self.padding.bottom
            )
        )
        svg = et.Element(
            "svg",
            xmlns="http://www.w3.org/2000/svg",
            version="1.1",
            viewBox=f"0 0 {width} {height}",
        )
        if self.title:
            title = et.Element("title")
            title.text = self.title
            svg.append(title)
        if self.description:
            desc = et.Element("desc")
            desc.text = self.description
            svg.append(desc)
        elements = []
        if self.background is not None:
            elements.append(
                et.Element(
                    "rect",
                    x="0",
                    y="0",
                    width=f"{width}",
                    height=f"{height}",
                    **_kw(self.background),
                )
            )
        for op in self._ops:
            elements.append(op(transformer))
        for element in elements:
            self.css.select(element)
        if self.css:
            defs = et.Element("defs")
            style = et.Element("style", type="text/css")
            style.text = str(self.css)
            defs.append(style)
            svg.append(defs)
        for element in elements:
            svg.append(element)
        et.indent(svg, space="\t")
        with open(path, "w", encoding="utf-8") as file:
            file.write('<?xml version="1.0" encoding="utf-8"?>\n')
            file.write(et.tostring(svg, encoding="unicode", xml_declaration=False))
            file.write("\n")
