"""Well schematic generator for visualization and analysis of wellbore configurations."""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import List, Optional, Dict, Any, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, date
import logging
from abc import ABC, abstractmethod
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================


class FluidType(Enum):
    """Enum for fluid types."""

    BRINE = "brine"
    OIL = "oil"
    MUD = "mud"
    GAS = "gas"
    WATER = "water"
    AIR = "air"
    N2 = "N2"
    CEMENT = "cement"
    EMPTY = "empty"
    OPENHOLE = "openhole"


# Color configurations
ANNULUS_FLUID_COLORS = {
    FluidType.BRINE: '#8bc1f4',
    FluidType.OIL: 'gold',
    FluidType.MUD: 'saddlebrown',
    FluidType.GAS: 'lightgreen',
    FluidType.WATER: 'aqua',
    FluidType.AIR: 'lightgrey',
    FluidType.N2: 'blue',
}

INNER_FLUID_COLORS = {
    FluidType.BRINE: '#87cefa',
    FluidType.OIL: 'gold',
    FluidType.MUD: 'saddlebrown',
    FluidType.GAS: 'lightgreen',
    FluidType.WATER: 'aqua',
    FluidType.AIR: 'lightgrey',
    FluidType.N2: 'blue',
}

CEMENT_COLOR = '#6e6a6a'
OPENHOLE_COLOR = '#e6d3b3'
SECONDARY_BARRIER_COLOR = '#d62728'

# Drawing constants
SHOE_HEIGHT = 25
PACKER_COLOR = '#222222'
EPSILON = 1e-6  # For floating point comparisons

# =============================================================================
# DATA MODELS
# =============================================================================


@dataclass
class Dimensions:
    """Well element dimensions."""

    inner_diameter: Optional[float] = None
    outer_diameter: Optional[float] = None
    openhole_diameter: Optional[float] = None


@dataclass
class DepthInterval:
    """Depth interval with top and bottom."""

    top: float
    bottom: float

    def __post_init__(self):
        """Validate depth interval."""
        if self.top > self.bottom:
            raise ValueError(f"Top depth ({self.top}) cannot be greater than "
                             f"bottom depth ({self.bottom})")

    @property
    def height(self) -> float:
        """Get height of depth interval."""
        return self.bottom - self.top

    def overlaps_with(self, other: 'DepthInterval') -> bool:
        """Check if this interval overlaps with another."""
        return not (self.top >= other.bottom or self.bottom <= other.top)

    def contains_depth(self, depth: float) -> bool:
        """Check if depth is within this interval."""
        return self.top <= depth < self.bottom


@dataclass
class FluidInterval:
    """Fluid interval with type and depth range."""

    fluid_type: Union[FluidType, str]
    depth_interval: DepthInterval

    def __post_init__(self):
        """Convert string fluid type to enum."""
        if isinstance(self.fluid_type, str):
            self.fluid_type = FluidType(self.fluid_type)


@dataclass
class PackerData:
    """Packer configuration data."""

    depth_interval: DepthInterval
    packer_type: str = "generic"
    fluid_above: Optional[Union[FluidType, str]] = None
    fluid_below: Optional[Union[FluidType, str]] = None
    fluid_above_level: Optional[float] = None
    fluid_below_level: Optional[float] = None


@dataclass
class PlugData:
    """Plug configuration data."""

    depth_interval: DepthInterval
    plug_type: str = "generic"
    fluid_below: Optional[Union[FluidType, str]] = None
    cement_above: bool = False
    cement_above_height: Optional[float] = None


@dataclass
class PerforationData:
    """Perforation configuration data."""

    depth_interval: DepthInterval
    phases: int = 1
    density: int = 12  # shots per foot/meter


# =============================================================================
# BASE CLASSES
# =============================================================================


class WellElement(ABC):
    """Base class for all well elements."""

    def __init__(self, name: str, depth_interval: DepthInterval):
        """Initialize well element."""
        self.name = name
        self.depth_interval = depth_interval
        self._patches = []  # Store matplotlib patches for this element

    @property
    def top_depth(self) -> float:
        """Get top depth of the element."""
        return self.depth_interval.top

    @property
    def bottom_depth(self) -> float:
        """Get bottom depth of the element."""
        return self.depth_interval.bottom

    @abstractmethod
    def draw(self, ax: plt.Axes, **kwargs) -> None:
        """Draw the element on the given axes."""
        pass

    def get_info(self) -> Dict[str, Any]:
        """Get information dict for this element."""
        return {
            'name': self.name,
            'type': self.__class__.__name__,
            'top_depth': self.top_depth,
            'bottom_depth': self.bottom_depth,
        }

    def log_info(self) -> None:
        """Log information about this element."""
        info = self.get_info()
        logger.info(f"{info['type']} '{info['name']}': "
                    f"{info['top_depth']:.2f} - {info['bottom_depth']:.2f}")


class GeometryCalculator:
    """Helper class for geometry calculations."""

    @staticmethod
    def get_unit_diameter_at_depth(unit: 'Unit', depth: float,
                                   diameter_type: str = 'outer') -> float:
        """Get unit diameter at specific depth (handles tapered units)."""
        if not hasattr(unit, 'is_tapered') or not unit.is_tapered:
            return getattr(unit.dimensions, f'{diameter_type}_diameter') or 0

        if depth <= unit.transition_depth:
            return getattr(unit.dimensions, f'{diameter_type}_diameter') or 0
        else:
            return getattr(unit, f'bottom_{diameter_type}_diameter') or 0

    @staticmethod
    def get_wall_thickness_at_depth(unit: 'Unit', depth: float) -> float:
        """Get wall thickness at specific depth."""
        outer_d = GeometryCalculator.get_unit_diameter_at_depth(unit, depth, 'outer')
        inner_d = GeometryCalculator.get_unit_diameter_at_depth(unit, depth, 'inner')
        return (outer_d - inner_d) / 2

    @staticmethod
    def units_overlap(unit1: 'Unit', unit2: 'Unit') -> bool:
        """Check if two units overlap in depth."""
        return unit1.depth_interval.overlaps_with(unit2.depth_interval)

    @staticmethod
    def find_split_points(intervals: List[DepthInterval]) -> List[float]:
        """Find all split points from a list of intervals."""
        points = set()
        for interval in intervals:
            points.add(interval.top)
            points.add(interval.bottom)
        return sorted(points)


class DrawingHelper:
    """Helper class for drawing operations."""

    @staticmethod
    def create_rectangle_patch(x: float, y: float, width: float, height: float,
                               facecolor: str = 'black', edgecolor: str = None,
                               linewidth: int = 1, alpha: float = 1.0,
                               hatch: str = None, zorder: int = 1) -> patches.Rectangle:
        """Create a rectangle patch with common parameters."""
        return patches.Rectangle(
            (x, y), width, height,
            facecolor=facecolor,
            edgecolor=edgecolor,
            linewidth=linewidth,
            alpha=alpha,
            hatch=hatch,
            zorder=zorder
        )

    @staticmethod
    def draw_crossing_lines(ax: plt.Axes, left: float, right: float,
                            top: float, bottom: float, color: str = 'white',
                            linewidth: int = 1, zorder: int = 4) -> None:
        """Draw crossing lines (X pattern)."""
        ax.plot([left, right], [top, bottom], color=color, linewidth=linewidth, zorder=zorder)
        ax.plot([left, right], [bottom, top], color=color, linewidth=linewidth, zorder=zorder)

    @staticmethod
    def get_fluid_color(fluid_type: Union[FluidType, str], is_annulus: bool = False) -> str:
        """Get color for fluid type."""
        if isinstance(fluid_type, str):
            fluid_type = FluidType(fluid_type)

        if fluid_type == FluidType.CEMENT:
            return CEMENT_COLOR

        color_map = ANNULUS_FLUID_COLORS if is_annulus else INNER_FLUID_COLORS
        return color_map.get(fluid_type, 'lightblue')

# =============================================================================
# UNIT CLASSES
# =============================================================================


class Unit(WellElement):
    """Base class for all well units (casing, tubing, etc.)."""

    def __init__(self, name: str, depth_interval: DepthInterval, dimensions: Dimensions,
                 annulus_fluids: List[FluidInterval] = None,
                 inner_fluids: List[FluidInterval] = None,
                 packers: List[PackerData] = None,
                 plugs: List[PlugData] = None,
                 perforations: List[PerforationData] = None,
                 draw_shoe: bool = True):
        """Initialize well unit."""
        super().__init__(name, depth_interval)
        self.dimensions = dimensions
        self.annulus_fluids = annulus_fluids or []
        self.inner_fluids = inner_fluids or []
        self.packers = packers or []
        self.plugs = plugs or []
        self.perforations = perforations or []
        self.draw_shoe = draw_shoe

    @property
    def inner_diameter(self) -> Optional[float]:
        """Get inner diameter of the unit."""
        return self.dimensions.inner_diameter

    @property
    def outer_diameter(self) -> Optional[float]:
        """Get outer diameter of the unit."""
        return self.dimensions.outer_diameter

    @property
    def openhole_diameter(self) -> Optional[float]:
        """Get openhole diameter of the unit."""
        return self.dimensions.openhole_diameter

    def add_packer(self, packer: PackerData) -> None:
        """Add a packer to the unit."""
        self.packers.append(packer)

    def add_plug(self, plug: PlugData) -> None:
        """Add a plug to the unit."""
        self.plugs.append(plug)

    def add_perforation(self, perforation: PerforationData) -> None:
        """Add perforations to the unit."""
        self.perforations.append(perforation)

    def draw(self, ax: plt.Axes, is_innermost: bool = False,
             all_units: List['Unit'] = None, **kwargs) -> None:
        """Draw the complete unit with all its components."""
        all_units = all_units or []

        # Draw unit structure
        self._draw_walls(ax)
        self._draw_shoes(ax)

        # Draw internal elements
        self._draw_plugs(ax)

        # Draw fluids and annuli
        self._draw_annulus_fluids(ax, all_units)
        self._draw_open_holes(ax, all_units)
        self._draw_annulus_packers(ax, all_units)

        if is_innermost:
            self._draw_inner_fluids(ax, all_units)

    def _draw_walls(self, ax: plt.Axes) -> None:
        """Draw the unit walls."""
        if not self.inner_diameter or not self.outer_diameter:
            return
        wall_thickness = (self.outer_diameter - self.inner_diameter) / 2
        height = self.depth_interval.height
        # Left wall
        left_wall = DrawingHelper.create_rectangle_patch(
            x=-self.outer_diameter / 2,
            y=self.top_depth,
            width=wall_thickness,
            height=height,
            facecolor='black',
            edgecolor='black',
            zorder=2
        )
        ax.add_patch(left_wall)
        self._patches.append(('wall', left_wall))

        # Right wall
        right_wall = DrawingHelper.create_rectangle_patch(
            x=self.inner_diameter / 2,
            y=self.top_depth,
            width=wall_thickness,
            height=height,
            facecolor='black',
            edgecolor='black',
            zorder=2
        )
        ax.add_patch(right_wall)
        self._patches.append(('wall', right_wall))

    def _draw_shoes(self, ax: plt.Axes) -> None:
        """Draw casing shoes if enabled."""
        if (not self.draw_shoe or not self.inner_diameter or
                not self.outer_diameter):
            return

        openhole_radius = (self.openhole_diameter or self.outer_diameter) / 2

        # Left shoe
        left_shoe_points = [
            [-self.outer_diameter / 2, self.bottom_depth],
            [-openhole_radius, self.bottom_depth],
            [-self.outer_diameter / 2, self.bottom_depth - SHOE_HEIGHT]
        ]
        left_shoe = patches.Polygon(left_shoe_points, closed=True,
                                    facecolor='black', edgecolor='black',
                                    linewidth=1, zorder=5)
        ax.add_patch(left_shoe)
        self._patches.append(('shoe', left_shoe))

        # Right shoe
        right_shoe_points = [
            [self.outer_diameter / 2, self.bottom_depth],
            [openhole_radius, self.bottom_depth],
            [self.outer_diameter / 2, self.bottom_depth - SHOE_HEIGHT]
        ]
        right_shoe = patches.Polygon(right_shoe_points, closed=True,
                                     facecolor='black', edgecolor='black',
                                     linewidth=1, zorder=5)
        ax.add_patch(right_shoe)
        self._patches.append(('shoe', right_shoe))

    def _draw_plugs(self, ax: plt.Axes) -> None:
        """Draw all plugs in the unit."""
        if not self.inner_diameter or not self.plugs:
            return

        for i, plug in enumerate(self.plugs):
            plug_patch = DrawingHelper.create_rectangle_patch(
                x=-self.inner_diameter / 2,
                y=plug.depth_interval.top,
                width=self.inner_diameter,
                height=plug.depth_interval.height,
                facecolor='black',
                edgecolor='black',
                alpha=1.0,
                zorder=3
            )
            ax.add_patch(plug_patch)
            self._patches.append(('plug', plug_patch, i))

            # Draw crossing lines
            DrawingHelper.draw_crossing_lines(ax,
                                              left=-self.inner_diameter / 2,
                                              right=self.inner_diameter / 2,
                                              top=plug.depth_interval.top,
                                              bottom=plug.depth_interval.bottom,
                                              zorder=4)

    def _draw_annulus_fluids(self, ax: plt.Axes, all_units: List['Unit']) -> None:
        """Draw fluids in the annulus."""
        if not self.annulus_fluids or not all_units:
            return

        for fluid in self.annulus_fluids:
            intervals = self._calculate_annulus_intervals(fluid, all_units)
            for interval in intervals:
                self._draw_annulus_fluid_segment(ax, interval, fluid.fluid_type)

    def _calculate_annulus_intervals(self, fluid: FluidInterval,
                                     all_units: List['Unit']) -> List[Dict]:
        """Calculate the depth intervals for annulus fluid drawing."""
        # Get all relevant split points
        split_points = {fluid.depth_interval.top, fluid.depth_interval.bottom}

        # Add unit boundaries that overlap with this fluid
        for unit in all_units:
            if unit is self:
                continue
            temp_unit = Unit('temp', fluid.depth_interval, Dimensions())
            if GeometryCalculator.units_overlap(unit, temp_unit):
                if self._is_unit_outside(unit):
                    split_points.add(unit.top_depth)
                    split_points.add(unit.bottom_depth)

        # Add packer boundaries
        for packer in self.packers:
            split_points.add(packer.depth_interval.top)
            split_points.add(packer.depth_interval.bottom)

        # Filter and sort split points
        valid_points = [p for p in split_points
                        if fluid.depth_interval.top <= p <= fluid.depth_interval.bottom]
        valid_points.sort()

        # Create intervals
        intervals = []
        for i in range(len(valid_points) - 1):
            top, bottom = valid_points[i], valid_points[i + 1]
            if bottom - top > EPSILON:
                interval = self._create_annulus_interval(top, bottom, all_units)
                if interval:
                    intervals.append(interval)

        return intervals

    def _create_annulus_interval(self, top: float,
                                 bottom: float, all_units: List['Unit']) -> Optional[Dict]:
        """Create an annulus interval with proper boundaries."""
        mid_depth = (top + bottom) / 2
        outer_id = self._find_outer_boundary(mid_depth, all_units)
        if not outer_id or outer_id <= self.outer_diameter:
            return None

        return {
            'top': top,
            'bottom': bottom,
            'inner_od': self.outer_diameter,
            'outer_id': outer_id
        }

    def _find_outer_boundary(self, depth: float, all_units: List['Unit']) -> Optional[float]:
        """Find the outer boundary (inner diameter of next unit or openhole)."""
        outer_id = None
        current_unit_od = GeometryCalculator.get_unit_diameter_at_depth(self, depth, 'outer')

        for unit in all_units:
            if unit is self:
                continue

            if unit.depth_interval.contains_depth(depth):
                unit_od_at_depth = GeometryCalculator.get_unit_diameter_at_depth(
                    unit, depth, 'outer')
                unit_id_at_depth = GeometryCalculator.get_unit_diameter_at_depth(
                    unit, depth, 'inner')

                if unit_od_at_depth > current_unit_od:
                    if outer_id is None or (unit_id_at_depth or 0) < outer_id:
                        outer_id = unit_id_at_depth

        return outer_id or self.openhole_diameter

    def _draw_annulus_fluid_segment(self, ax: plt.Axes, interval: Dict,
                                    fluid_type: FluidType) -> None:
        """Draw a single annulus fluid segment."""
        if self._should_skip_fluid_segment(interval):
            return

        actual_fluid_type = self._get_actual_fluid_type(interval, fluid_type)
        color = DrawingHelper.get_fluid_color(actual_fluid_type, is_annulus=True)
        alpha = 0.7 if actual_fluid_type == FluidType.CEMENT else 0.5
        width = (interval['outer_id'] - interval['inner_od']) / 2

        # Left patch
        left_patch = DrawingHelper.create_rectangle_patch(
            x=-interval['outer_id'] / 2,
            y=interval['top'],
            width=width,
            height=interval['bottom'] - interval['top'],
            facecolor=color,
            alpha=alpha,
            zorder=1
        )
        ax.add_patch(left_patch)
        self._patches.append((actual_fluid_type.value, left_patch))

        # Right patch
        right_patch = DrawingHelper.create_rectangle_patch(
            x=interval['inner_od'] / 2,
            y=interval['top'],
            width=width,
            height=interval['bottom'] - interval['top'],
            facecolor=color,
            alpha=alpha,
            zorder=1
        )
        ax.add_patch(right_patch)
        self._patches.append((actual_fluid_type.value, right_patch))

    def _should_skip_fluid_segment(self, interval: Dict) -> bool:
        """Check if fluid segment should be skipped due to packer."""
        for packer in self.packers:
            if packer.depth_interval.contains_depth(interval['top']):
                return True
        return False

    def _get_actual_fluid_type(self, interval: Dict, default_fluid_type: FluidType) -> FluidType:
        """Get the actual fluid type, considering packer overrides."""
        for packer in self.packers:
            if (abs(interval['top'] - packer.depth_interval.bottom) < EPSILON and
                    packer.fluid_below is not None):
                return packer.fluid_below
        return default_fluid_type

    def _draw_open_holes(self, ax: plt.Axes, all_units: List['Unit']) -> None:
        """Draw open hole sections for the outermost unit."""
        if (not all_units or not self.openhole_diameter or
                self is not all_units[0]):
            return

        covered_intervals = self._get_covered_intervals()
        uncovered_intervals = self._find_uncovered_intervals(covered_intervals)

        for top, bottom in uncovered_intervals:
            if bottom - top > EPSILON:
                self._draw_open_hole_segment(ax, top, bottom)

    def _get_covered_intervals(self) -> List[Tuple[float, float]]:
        """Get all intervals covered by annulus fluids."""
        covered = []
        for fluid in self.annulus_fluids:
            covered.append((fluid.depth_interval.top, fluid.depth_interval.bottom))
        return sorted(covered)

    def _find_uncovered_intervals(self, covered_intervals: List[Tuple[float, float]]
                                  ) -> List[Tuple[float, float]]:
        """Find intervals not covered by fluids."""
        intervals = []
        last_depth = self.top_depth

        for top, bottom in covered_intervals:
            if last_depth < top:
                intervals.append((last_depth, top))
            last_depth = max(last_depth, bottom)

        if last_depth < self.bottom_depth:
            intervals.append((last_depth, self.bottom_depth))

        return intervals

    def _draw_open_hole_segment(self, ax: plt.Axes, top: float, bottom: float) -> None:
        """Draw a single open hole segment."""
        width = ((self.openhole_diameter - self.outer_diameter) / 2
                 if self.outer_diameter else self.openhole_diameter / 2)

        # Left open hole
        left_patch = DrawingHelper.create_rectangle_patch(
            x=-self.openhole_diameter / 2,
            y=top,
            width=width,
            height=bottom - top,
            facecolor=OPENHOLE_COLOR,
            alpha=0.5,
            hatch='//',
            zorder=0
        )
        ax.add_patch(left_patch)
        self._patches.append(('openhole', left_patch))

        # Right open hole
        right_patch = DrawingHelper.create_rectangle_patch(
            x=self.outer_diameter / 2 if self.outer_diameter else 0,
            y=top,
            width=width,
            height=bottom - top,
            facecolor=OPENHOLE_COLOR,
            alpha=0.5,
            hatch='//',
            zorder=0
        )
        ax.add_patch(right_patch)
        self._patches.append(('openhole', right_patch))

    def _draw_annulus_packers(self, ax: plt.Axes, all_units: List['Unit']) -> None:
        """Draw packers in the annulus."""
        if not self.packers or not all_units:
            return

        for i, packer in enumerate(self.packers):
            packer_boundaries = self._get_packer_boundaries(packer, all_units)
            if packer_boundaries:
                self._draw_single_annulus_packer(ax, packer, packer_boundaries, i)

    def _get_packer_boundaries(self, packer: PackerData, all_units: List['Unit']) -> Optional[Dict]:
        """Get the boundaries for drawing a packer."""
        outer_id = self._find_outer_boundary(packer.depth_interval.top, all_units)
        if not outer_id or outer_id <= self.outer_diameter:
            return None

        return {
            'inner_od': self.outer_diameter,
            'outer_id': outer_id,
            'width': (outer_id - self.outer_diameter) / 2
        }

    def _draw_single_annulus_packer(self, ax: plt.Axes, packer: PackerData,
                                    boundaries: Dict, index: int) -> None:
        """Draw a single packer in the annulus."""
        # Left packer
        left_packer = DrawingHelper.create_rectangle_patch(
            x=-boundaries['outer_id'] / 2,
            y=packer.depth_interval.top,
            width=boundaries['width'],
            height=packer.depth_interval.height,
            facecolor=PACKER_COLOR,
            edgecolor='black',
            alpha=1.0,
            zorder=6
        )
        ax.add_patch(left_packer)
        self._patches.append(('packer', left_packer, index))

        # Right packer
        right_packer = DrawingHelper.create_rectangle_patch(
            x=boundaries['inner_od'] / 2,
            y=packer.depth_interval.top,
            width=boundaries['width'],
            height=packer.depth_interval.height,
            facecolor=PACKER_COLOR,
            edgecolor='black',
            alpha=1.0,
            zorder=6
        )
        ax.add_patch(right_packer)
        self._patches.append(('packer', right_packer, index))

        # Draw crossing lines
        DrawingHelper.draw_crossing_lines(ax,
                                          left=-boundaries['outer_id'] / 2,
                                          right=(-boundaries['outer_id'] / 2 +
                                                 boundaries['width']),
                                          top=packer.depth_interval.top,
                                          bottom=packer.depth_interval.bottom,
                                          zorder=7)
        DrawingHelper.draw_crossing_lines(ax,
                                          left=boundaries['inner_od'] / 2,
                                          right=(boundaries['inner_od'] / 2 +
                                                 boundaries['width']),
                                          top=packer.depth_interval.top,
                                          bottom=packer.depth_interval.bottom,
                                          zorder=7)

    def _draw_inner_fluids(self, ax: plt.Axes, all_units: List['Unit']) -> None:
        """Draw fluids inside the unit."""
        if not self.inner_diameter or not self.inner_fluids:
            return

        main_fluid = self.inner_fluids[0]
        main_intervals = self._calculate_inner_fluid_intervals(main_fluid, all_units)

        for interval in main_intervals:
            self._draw_inner_fluid_segment(ax, interval, main_fluid.fluid_type)

        self._draw_plug_fluids(ax)

    def _calculate_inner_fluid_intervals(self, main_fluid: FluidInterval,
                                         all_units: List['Unit']) -> List[Dict]:
        """Calculate intervals for main inner fluid, avoiding inner units."""
        main_top = main_fluid.depth_interval.top
        main_bottom = main_fluid.depth_interval.bottom

        blocking_points = set()

        # Add plug boundaries
        for plug in self.plugs:
            if main_top < plug.depth_interval.top < main_bottom:
                blocking_points.add(plug.depth_interval.top)
            if main_top < plug.depth_interval.bottom < main_bottom:
                blocking_points.add(plug.depth_interval.bottom)

        # Add inner unit boundaries
        if all_units:
            for unit in all_units:
                if unit is self:
                    continue
                unit_max_od = max(unit.outer_diameter or 0,
                                  getattr(unit, 'bottom_outer_diameter',
                                          unit.outer_diameter) or 0)
                self_min_id = min(self.inner_diameter or float('inf'),
                                  getattr(self, 'bottom_inner_diameter',
                                          self.inner_diameter) or float('inf'))

                if unit_max_od < self_min_id:
                    if not (unit.top_depth >= main_bottom or unit.bottom_depth <= main_top):
                        if main_top <= unit.top_depth <= main_bottom:
                            blocking_points.add(unit.top_depth)
                        if main_top <= unit.bottom_depth <= main_bottom:
                            blocking_points.add(unit.bottom_depth)

        # Create intervals between blocking points
        split_points = sorted([main_top, main_bottom] + list(blocking_points))
        intervals = []

        for i in range(len(split_points) - 1):
            interval_top = split_points[i]
            interval_bottom = split_points[i + 1]

            if interval_bottom - interval_top < EPSILON:
                continue

            # Check if this interval is blocked
            is_blocked = False
            for plug in self.plugs:
                if plug.depth_interval.contains_depth(interval_top):
                    is_blocked = True
                    break

            if not is_blocked:
                intervals.append({
                    'top': interval_top,
                    'bottom': interval_bottom,
                    'fluid_type': main_fluid.fluid_type
                })

        return intervals

    def _draw_inner_fluid_segment(self, ax: plt.Axes, interval: Dict,
                                  fluid_type: FluidType) -> None:
        """Draw a single inner fluid segment."""
        color = DrawingHelper.get_fluid_color(fluid_type, is_annulus=False)

        patch = DrawingHelper.create_rectangle_patch(
            x=-self.inner_diameter / 2,
            y=interval['top'],
            width=self.inner_diameter,
            height=interval['bottom'] - interval['top'],
            facecolor=color,
            alpha=0.5,
            zorder=3
        )
        ax.add_patch(patch)
        self._patches.append((fluid_type.value, patch))

    def _draw_plug_fluids(self, ax: plt.Axes) -> None:
        """Draw fluids below plugs."""
        for plug in self.plugs:
            if plug.fluid_below:
                # Find the interval below this plug
                below_top = plug.depth_interval.bottom
                below_bottom = self.bottom_depth

                # Check if there's another plug below
                for other_plug in self.plugs:
                    if (other_plug.depth_interval.top > below_top and
                            other_plug.depth_interval.top < below_bottom):
                        below_bottom = other_plug.depth_interval.top

                if below_bottom > below_top:
                    interval = {
                        'top': below_top,
                        'bottom': below_bottom,
                        'fluid_type': plug.fluid_below
                    }
                    self._draw_inner_fluid_segment(ax, interval, plug.fluid_below)

    def _is_unit_outside(self, unit: 'Unit') -> bool:
        """Check if unit is outside the current unit."""
        unit_max_od = max(unit.outer_diameter or 0,
                          getattr(unit, 'bottom_outer_diameter',
                                  unit.outer_diameter) or 0)
        self_max_od = max(self.outer_diameter or 0,
                          getattr(self, 'bottom_outer_diameter',
                                  self.outer_diameter) or 0)
        return unit_max_od > self_max_od

    def get_info(self) -> Dict[str, Any]:
        """Get comprehensive information about this unit."""
        info = super().get_info()
        info.update({
            'inner_diameter': self.inner_diameter,
            'outer_diameter': self.outer_diameter,
            'openhole_diameter': self.openhole_diameter,
            'perforations': len(self.perforations),
            'packers': len(self.packers),
            'plugs': len(self.plugs),
            'annulus_fluids': len(self.annulus_fluids),
            'inner_fluids': len(self.inner_fluids)
        })
        return info


class Casing(Unit):
    """Casing unit with cement and fluid capabilities."""

    def __init__(self, name: str, depth_interval: DepthInterval, dimensions: Dimensions,
                 is_tapered: bool = False,
                 transition_depth: Optional[float] = None,
                 bottom_inner_diameter: Optional[float] = None,
                 bottom_outer_diameter: Optional[float] = None,
                 **kwargs):
        """Initialize casing unit."""
        super().__init__(name, depth_interval, dimensions, **kwargs)
        self.is_tapered = is_tapered
        self.transition_depth = transition_depth
        self.bottom_inner_diameter = bottom_inner_diameter
        self.bottom_outer_diameter = bottom_outer_diameter

        if self.is_tapered:
            self._validate_tapered_parameters()

    def _validate_tapered_parameters(self) -> None:
        """Validate tapered casing parameters."""
        if (self.transition_depth is None or
                self.bottom_inner_diameter is None or
                self.bottom_outer_diameter is None):
            raise ValueError("Tapered casing requires transition_depth, "
                             "bottom_inner_diameter, and bottom_outer_diameter")

        if not (self.top_depth <= self.transition_depth <= self.bottom_depth):
            raise ValueError("Transition depth must be between top and bottom depths")

    def draw(self, ax: plt.Axes, **kwargs) -> None:
        """Draw the complete casing unit, handling tapered configuration."""
        if self.is_tapered:
            self._draw_tapered_casing(ax, **kwargs)
        else:
            super().draw(ax, **kwargs)

    def _draw_tapered_casing(self, ax: plt.Axes, **kwargs) -> None:
        """Draw tapered casing as two separate sections (top and bottom)."""
        all_units = kwargs.get('all_units', [])
        is_innermost = kwargs.get('is_innermost', False)

        # --- Draw casing walls ---
        # Top section
        wall_thickness_top = (self.outer_diameter - self.inner_diameter) / 2
        height_top = self.transition_depth - self.top_depth
        if height_top > 0:
            # Left wall (top)
            left_wall_top = DrawingHelper.create_rectangle_patch(
                x=-self.outer_diameter / 2,
                y=self.top_depth,
                width=wall_thickness_top,
                height=height_top,
                facecolor='black',
                edgecolor='black',
                zorder=2
            )
            ax.add_patch(left_wall_top)
            self._patches.append(('wall', left_wall_top))
            # Right wall (top)
            right_wall_top = DrawingHelper.create_rectangle_patch(
                x=self.inner_diameter / 2,
                y=self.top_depth,
                width=wall_thickness_top,
                height=height_top,
                facecolor='black',
                edgecolor='black',
                zorder=2
            )
            ax.add_patch(right_wall_top)
            self._patches.append(('wall', right_wall_top))
        # Bottom section
        wall_thickness_bottom = (self.bottom_outer_diameter -
                                 self.bottom_inner_diameter) / 2
        height_bottom = self.bottom_depth - self.transition_depth
        if height_bottom > 0:
            # Left wall (bottom)
            left_wall_bottom = DrawingHelper.create_rectangle_patch(
                x=-self.bottom_outer_diameter / 2,
                y=self.transition_depth,
                width=wall_thickness_bottom,
                height=height_bottom,
                facecolor='black',
                edgecolor='black',
                zorder=2
            )
            ax.add_patch(left_wall_bottom)
            self._patches.append(('wall', left_wall_bottom))
            # Right wall (bottom)
            right_wall_bottom = DrawingHelper.create_rectangle_patch(
                x=self.bottom_inner_diameter / 2,
                y=self.transition_depth,
                width=wall_thickness_bottom,
                height=height_bottom,
                facecolor='black',
                edgecolor='black',
                zorder=2
            )
            ax.add_patch(right_wall_bottom)
            self._patches.append(('wall', right_wall_bottom))

        # --- Draw shoes ---
        if self.draw_shoe:
            shoe_height = 25
            openhole_radius = (self.openhole_diameter or
                               self.bottom_outer_diameter) / 2
            # Left shoe
            left_shoe_points = [
                [-self.bottom_outer_diameter / 2, self.bottom_depth],
                [-openhole_radius, self.bottom_depth],
                [-self.bottom_outer_diameter / 2, self.bottom_depth - shoe_height]
            ]
            left_shoe = patches.Polygon(left_shoe_points, closed=True,
                                        facecolor='black', edgecolor='black',
                                        linewidth=1, zorder=5)
            ax.add_patch(left_shoe)
            self._patches.append(('shoe', left_shoe))
            # Right shoe
            right_shoe_points = [
                [self.bottom_outer_diameter / 2, self.bottom_depth],
                [openhole_radius, self.bottom_depth],
                [self.bottom_outer_diameter / 2, self.bottom_depth - shoe_height]
            ]
            right_shoe = patches.Polygon(right_shoe_points, closed=True,
                                         facecolor='black', edgecolor='black',
                                         linewidth=1, zorder=5)
            ax.add_patch(right_shoe)
            self._patches.append(('shoe', right_shoe))

        # --- Draw plugs ---
        if self.plugs:
            for i, plug in enumerate(self.plugs):
                # Determine which section the plug is in and get appropriate diameter
                if plug.depth_interval.top < self.transition_depth:
                    inner_diameter = self.inner_diameter
                else:
                    inner_diameter = self.bottom_inner_diameter
                plug_patch = DrawingHelper.create_rectangle_patch(
                    x=-inner_diameter / 2,
                    y=plug.depth_interval.top,
                    width=inner_diameter,
                    height=plug.depth_interval.height,
                    facecolor='black',
                    edgecolor='black',
                    alpha=1.0,
                    zorder=3
                )
                ax.add_patch(plug_patch)
                self._patches.append(('plug', plug_patch, i))
                # Draw crossing lines
                DrawingHelper.draw_crossing_lines(
                    ax,
                    left=-inner_diameter / 2,
                    right=inner_diameter / 2,
                    top=plug.depth_interval.top,
                    bottom=plug.depth_interval.bottom,
                    zorder=4
                )

        # --- Draw annulus fluids ---
        if self.annulus_fluids and all_units:
            for fluid in self.annulus_fluids:
                # Split at transition depth
                split_points = [fluid.depth_interval.top,
                                fluid.depth_interval.bottom,
                                self.transition_depth]
                split_points = [p for p in split_points
                                if fluid.depth_interval.top <= p <=
                                fluid.depth_interval.bottom]
                split_points = sorted(set(split_points))
                for i in range(len(split_points) - 1):
                    top, bottom = split_points[i], split_points[i + 1]
                    if bottom - top < 1e-6:
                        continue
                    # Section: top or bottom
                    if bottom <= self.transition_depth:
                        inner_od = self.outer_diameter
                    elif top >= self.transition_depth:
                        inner_od = self.bottom_outer_diameter
                    else:
                        inner_od = self.outer_diameter
                    # Find outer boundary
                    outer_id = self._find_outer_boundary(top, all_units)
                    if not outer_id or outer_id <= inner_od:
                        continue
                    # Draw annulus fluid segment
                    color = DrawingHelper.get_fluid_color(fluid.fluid_type,
                                                          is_annulus=True)
                    alpha = 0.7 if fluid.fluid_type == FluidType.CEMENT else 0.5
                    width = (outer_id - inner_od) / 2
                    # Left patch
                    left_patch = DrawingHelper.create_rectangle_patch(
                        x=-outer_id / 2,
                        y=top,
                        width=width,
                        height=bottom - top,
                        facecolor=color,
                        alpha=alpha,
                        zorder=1
                    )
                    ax.add_patch(left_patch)
                    self._patches.append((fluid.fluid_type.value, left_patch))
                    # Right patch
                    right_patch = DrawingHelper.create_rectangle_patch(
                        x=inner_od / 2,
                        y=top,
                        width=width,
                        height=bottom - top,
                        facecolor=color,
                        alpha=alpha,
                        zorder=1
                    )
                    ax.add_patch(right_patch)
                    self._patches.append((fluid.fluid_type.value, right_patch))

        # --- Draw open holes ---
        if all_units and self.openhole_diameter and self is all_units[0]:
            # Find covered intervals
            covered = []
            for fluid in self.annulus_fluids:
                covered.append((fluid.depth_interval.top,
                                fluid.depth_interval.bottom))
            covered = sorted(covered)
            # Find uncovered intervals
            last_depth = self.top_depth
            uncovered = []
            for top, bottom in covered:
                if last_depth < top:
                    uncovered.append((last_depth, top))
                last_depth = max(last_depth, bottom)
            if last_depth < self.bottom_depth:
                uncovered.append((last_depth, self.bottom_depth))
            # Draw open hole for each uncovered interval
            for top, bottom in uncovered:
                if bottom - top < 1e-6:
                    continue
                # Section: top or bottom
                if bottom <= self.transition_depth:
                    outer_diameter = self.outer_diameter
                elif top >= self.transition_depth:
                    outer_diameter = self.bottom_outer_diameter
                else:
                    # Spans transition - split into two segments
                    if top < self.transition_depth:
                        self._draw_tapered_casing(ax, all_units=all_units,
                                                  is_innermost=is_innermost)
                    continue
                width = ((self.openhole_diameter - outer_diameter) / 2
                         if outer_diameter else self.openhole_diameter / 2)
                # Left open hole
                left_patch = DrawingHelper.create_rectangle_patch(
                    x=-self.openhole_diameter / 2,
                    y=top,
                    width=width,
                    height=bottom - top,
                    facecolor=OPENHOLE_COLOR,
                    alpha=0.5,
                    hatch='//',
                    zorder=0
                )
                ax.add_patch(left_patch)
                self._patches.append(('openhole', left_patch))
                # Right open hole
                right_patch = DrawingHelper.create_rectangle_patch(
                    x=outer_diameter / 2 if outer_diameter else 0,
                    y=top,
                    width=width,
                    height=bottom - top,
                    facecolor=OPENHOLE_COLOR,
                    alpha=0.5,
                    hatch='//',
                    zorder=0
                )
                ax.add_patch(right_patch)
                self._patches.append(('openhole', right_patch))

        # --- Draw annulus packers ---
        if self.packers and all_units:
            for i, packer in enumerate(self.packers):
                # Section: top or bottom
                if packer.depth_interval.top < self.transition_depth:
                    inner_od = self.outer_diameter
                else:
                    inner_od = self.bottom_outer_diameter
                outer_id = self._find_outer_boundary(packer.depth_interval.top,
                                                     all_units)
                if not outer_id or outer_id <= inner_od:
                    continue
                boundaries = {
                    'inner_od': inner_od,
                    'outer_id': outer_id,
                    'width': (outer_id - inner_od) / 2
                }
                # Left packer
                left_packer = DrawingHelper.create_rectangle_patch(
                    x=-boundaries['outer_id'] / 2,
                    y=packer.depth_interval.top,
                    width=boundaries['width'],
                    height=packer.depth_interval.height,
                    facecolor=PACKER_COLOR,
                    edgecolor='black',
                    alpha=1.0,
                    zorder=6
                )
                ax.add_patch(left_packer)
                self._patches.append(('packer', left_packer, i))
                # Right packer
                right_packer = DrawingHelper.create_rectangle_patch(
                    x=boundaries['inner_od'] / 2,
                    y=packer.depth_interval.top,
                    width=boundaries['width'],
                    height=packer.depth_interval.height,
                    facecolor=PACKER_COLOR,
                    edgecolor='black',
                    alpha=1.0,
                    zorder=6
                )
                ax.add_patch(right_packer)
                self._patches.append(('packer', right_packer, i))
                # Draw crossing lines
                DrawingHelper.draw_crossing_lines(
                    ax,
                    left=-boundaries['outer_id'] / 2,
                    right=-boundaries['outer_id'] / 2 + boundaries['width'],
                    top=packer.depth_interval.top,
                    bottom=packer.depth_interval.bottom,
                    zorder=7)
                DrawingHelper.draw_crossing_lines(
                    ax,
                    left=boundaries['inner_od'] / 2,
                    right=boundaries['inner_od'] / 2 + boundaries['width'],
                    top=packer.depth_interval.top,
                    bottom=packer.depth_interval.bottom,
                    zorder=7)

        # --- Draw inner fluids ---
        if is_innermost and self.inner_fluids:
            main_fluid = self.inner_fluids[0]
            # Split at transition depth
            split_points = [main_fluid.depth_interval.top,
                            main_fluid.depth_interval.bottom,
                            self.transition_depth]
            split_points = [p for p in split_points
                            if main_fluid.depth_interval.top <= p <=
                            main_fluid.depth_interval.bottom]
            split_points = sorted(set(split_points))
            for i in range(len(split_points) - 1):
                top, bottom = split_points[i], split_points[i + 1]
                if bottom - top < 1e-6:
                    continue
                # Section: top or bottom
                if bottom <= self.transition_depth:
                    inner_diameter = self.inner_diameter
                elif top >= self.transition_depth:
                    inner_diameter = self.bottom_inner_diameter
                else:
                    inner_diameter = self.inner_diameter
                color = DrawingHelper.get_fluid_color(main_fluid.fluid_type,
                                                      is_annulus=False)
                patch = DrawingHelper.create_rectangle_patch(
                    x=-inner_diameter / 2,
                    y=top,
                    width=inner_diameter,
                    height=bottom - top,
                    facecolor=color,
                    alpha=0.5,
                    zorder=3
                )
                ax.add_patch(patch)
                self._patches.append((main_fluid.fluid_type.value, patch))

        # --- Draw transition connection ---
        # Draw lines at transition depth to connect top and bottom sections
        transition_color = 'black'
        transition_zorder = 3
        # Left side transition
        ax.plot([
            -self.outer_diameter / 2,
            -self.bottom_outer_diameter / 2
        ], [
            self.transition_depth,
            self.transition_depth
        ], color=transition_color, linewidth=2, zorder=transition_zorder)
        # Right side transition
        ax.plot([
            self.outer_diameter / 2,
            self.bottom_outer_diameter / 2
        ], [
            self.transition_depth,
            self.transition_depth
        ], color=transition_color, linewidth=2, zorder=transition_zorder)
        # Inner left transition
        ax.plot([
            -self.inner_diameter / 2,
            -self.bottom_inner_diameter / 2
        ], [
            self.transition_depth,
            self.transition_depth
        ], color=transition_color, linewidth=2, zorder=transition_zorder)
        # Inner right transition
        ax.plot([
            self.inner_diameter / 2,
            self.bottom_inner_diameter / 2
        ], [
            self.transition_depth,
            self.transition_depth
        ], color=transition_color, linewidth=2, zorder=transition_zorder)


class Tubing(Unit):
    """Tubing unit with fluid capabilities."""

    pass


class Liner(Unit):
    """Liner unit with packer at top."""

    def __init__(self, name: str, depth_interval: DepthInterval,
                 dimensions: Dimensions,
                 packer_height: float = 20, **kwargs):
        """Initialize liner unit."""
        super().__init__(name, depth_interval, dimensions, **kwargs)

        # Add the liner packer
        packer_interval = DepthInterval(depth_interval.top,
                                        depth_interval.top + packer_height)
        liner_packer = PackerData(packer_interval, packer_type="liner_packer")
        self.packers.append(liner_packer)

# =============================================================================
# OTHER WELL ELEMENTS
# =============================================================================


class Lithology(WellElement):
    """Lithology element for geological formations."""

    def __init__(self, name: str, depth_interval: DepthInterval,
                 color: str, hatch: str = '', caprock: bool = False):
        """Initialize lithology element."""
        super().__init__(name, depth_interval)
        self.color = color
        self.hatch = hatch
        self.caprock = caprock

    def draw(self, ax: plt.Axes, x_offset: float = 0, width: float = 2.0,
             caprock_boundaries: Optional[Dict] = None, **kwargs) -> None:
        """Draw the lithology element."""
        if self.caprock and caprock_boundaries:
            self._draw_caprock(ax, caprock_boundaries)
        else:
            self._draw_standard_lithology(ax, x_offset, width)

    def _draw_caprock(self, ax: plt.Axes, boundaries: Dict) -> None:
        """Draw caprock around wellbore."""
        # Left caprock
        left_patch = DrawingHelper.create_rectangle_patch(
            x=boundaries['left'],
            y=self.top_depth,
            width=boundaries['left_inner'] - boundaries['left'],
            height=self.depth_interval.height,
            facecolor=self.color,
            edgecolor='black',
            hatch=self.hatch,
            alpha=0.7,
            zorder=0
        )
        ax.add_patch(left_patch)
        self._patches.append(('lithology', left_patch))

        # Right caprock
        right_patch = DrawingHelper.create_rectangle_patch(
            x=boundaries['right_inner'],
            y=self.top_depth,
            width=boundaries['right'] - boundaries['right_inner'],
            height=self.depth_interval.height,
            facecolor=self.color,
            edgecolor='black',
            hatch=self.hatch,
            alpha=0.7,
            zorder=0
        )
        ax.add_patch(right_patch)
        self._patches.append(('lithology', right_patch))

    def _draw_standard_lithology(self, ax: plt.Axes, x_offset: float,
                                 width: float) -> None:
        """Draw standard lithology column."""
        litho_patch = DrawingHelper.create_rectangle_patch(
            x=x_offset,
            y=self.top_depth,
            width=width,
            height=self.depth_interval.height,
            facecolor=self.color,
            edgecolor='black',
            hatch=self.hatch,
            alpha=0.7,
            zorder=0
        )
        ax.add_patch(litho_patch)
        self._patches.append(('lithology', litho_patch))


class Perforation(WellElement):
    """Perforation element."""

    def __init__(self, name: str, depth_interval: DepthInterval,
                 phases: int = 1, density: int = 12):
        """Initialize perforation element."""
        super().__init__(name, depth_interval)
        self.phases = phases
        self.density = density

    def draw(self, ax: plt.Axes, outer_diameter: float, **kwargs) -> None:
        """Draw perforation spikes."""
        spike_spacing = 10  # spacing between spikes
        spike_length = max(outer_diameter * 0.6, 0.5)
        spike_width = 5

        y = self.top_depth
        while y < self.bottom_depth:
            # Left spike
            left_spike = patches.Polygon([
                [-outer_diameter / 2, y],
                [-outer_diameter / 2, y + spike_width],
                [-outer_diameter / 2 - spike_length, y + spike_width / 2]
            ], closed=True, facecolor='red', edgecolor='black', zorder=4)
            ax.add_patch(left_spike)
            self._patches.append(('perforation', left_spike))

            # Right spike
            right_spike = patches.Polygon([
                [outer_diameter / 2, y],
                [outer_diameter / 2, y + spike_width],
                [outer_diameter / 2 + spike_length, y + spike_width / 2]
            ], closed=True, facecolor='red', edgecolor='black', zorder=4)
            ax.add_patch(right_spike)
            self._patches.append(('perforation', right_spike))

            y += spike_spacing


class OpenHole(WellElement):
    """Open hole section."""

    def __init__(self, name: str, depth_interval: DepthInterval, diameter: float):
        """Initialize open hole section."""
        super().__init__(name, depth_interval)
        self.diameter = diameter

    def draw(self, ax: plt.Axes, **kwargs) -> None:
        """Draw open hole section."""
        openhole_patch = DrawingHelper.create_rectangle_patch(
            x=-self.diameter / 2,
            y=self.top_depth,
            width=self.diameter,
            height=self.depth_interval.height,
            facecolor=OPENHOLE_COLOR,
            alpha=0.5,
            hatch='//',
            zorder=0
        )
        ax.add_patch(openhole_patch)
        self._patches.append(('openhole', openhole_patch))

# =============================================================================
# PRESSURE BARRIER SYSTEM
# =============================================================================


@dataclass
class PressureElement:
    """Represents a pressure barrier element."""

    id: int
    element_type: str
    unit_name: str
    side: str
    top_depth: float
    bottom_depth: float
    size: str
    is_sealed: bool = False
    fluid_type: Optional[str] = None
    annulus_label: str = ""


class PressureBarrierAnalyzer:
    """Analyzes pressure barriers in the well."""

    def __init__(self, units: List[Unit]):
        """Initialize pressure barrier analyzer."""
        self.units = units
        self._pressure_elements = []
        self._generate_pressure_elements()

    def _generate_pressure_elements(self) -> None:
        """Generate all pressure elements from units."""
        element_id = 0

        # Add structural elements
        for unit in self.units:
            element = PressureElement(
                id=element_id,
                element_type=type(unit).__name__.lower(),
                unit_name=unit.name,
                side='Left',
                top_depth=unit.top_depth,
                bottom_depth=unit.bottom_depth,
                size=f"{unit.outer_diameter:.2f}" if unit.outer_diameter else ""
            )
            self._pressure_elements.append(element)
            element_id += 1

            # Add packers
            for packer in unit.packers:
                packer_element = PressureElement(
                    id=element_id,
                    element_type='packer',
                    unit_name=unit.name,
                    side='Left',
                    top_depth=packer.depth_interval.top,
                    bottom_depth=packer.depth_interval.bottom,
                    size='varies'
                )
                self._pressure_elements.append(packer_element)
                element_id += 1

            # Add plugs
            for plug in unit.plugs:
                plug_element = PressureElement(
                    id=element_id,
                    element_type='plug',
                    unit_name=unit.name,
                    side='Center',
                    top_depth=plug.depth_interval.top,
                    bottom_depth=plug.depth_interval.bottom,
                    size=f"{unit.inner_diameter:.2f}" if unit.inner_diameter else ""
                )
                self._pressure_elements.append(plug_element)
                element_id += 1

            # Add fluids
            for fluid in unit.inner_fluids:
                fluid_element = PressureElement(
                    id=element_id,
                    element_type='fluid',
                    unit_name=f"{unit.name} (inner)",
                    side='Center',
                    top_depth=fluid.depth_interval.top,
                    bottom_depth=fluid.depth_interval.bottom,
                    size=f"{unit.inner_diameter:.2f}" if unit.inner_diameter else "",
                    fluid_type=fluid.fluid_type.value
                )
                self._pressure_elements.append(fluid_element)
                element_id += 1

            for fluid in unit.annulus_fluids:
                fluid_element = PressureElement(
                    id=element_id,
                    element_type='fluid',
                    unit_name=f"{unit.name} (annulus)",
                    side='Left',
                    top_depth=fluid.depth_interval.top,
                    bottom_depth=fluid.depth_interval.bottom,
                    size='varies',
                    fluid_type=fluid.fluid_type.value
                )
                self._pressure_elements.append(fluid_element)
                element_id += 1

    def get_pressure_elements(self) -> List[PressureElement]:
        """Get all pressure elements."""
        return self._pressure_elements

    def update_sealing_state(self, element_id: int, is_sealed: bool) -> None:
        """Update the sealing state of an element."""
        for element in self._pressure_elements:
            if element.id == element_id:
                element.is_sealed = is_sealed
                break

# =============================================================================
# CALIPER MEASUREMENT SYSTEM
# =============================================================================


class CaliperMeasurementGenerator:
    """Generates realistic caliper measurements for units."""

    NOMINAL_START_DATE = datetime(2020, 1, 1)
    JOINT_LENGTH = 39.37  # 12m in feet

    def __init__(self, unit: Unit, selected_date: Optional[datetime] = None):
        """Initialize caliper measurement generator."""
        self.unit = unit
        self.selected_date = selected_date or datetime.now()
        self.measurements = []
        self._generate_measurements()

    def _generate_measurements(self) -> None:
        """Generate caliper measurements for the unit."""
        if isinstance(self.selected_date, date) and not isinstance(self.selected_date, datetime):
            self.selected_date = datetime.combine(self.selected_date, datetime.min.time())

        days_diff = max(0, (self.selected_date - self.NOMINAL_START_DATE).days)
        unit_seed = hash(self.unit.name) % 2**32
        np.random.seed(unit_seed)

        unit_depth_range = self.unit.depth_interval.height
        num_joints = max(1, int(np.ceil(unit_depth_range / self.JOINT_LENGTH)))

        for i in range(num_joints):
            joint_top = self.unit.top_depth + (i * self.JOINT_LENGTH)
            joint_bottom = min(self.unit.top_depth + ((i + 1) * self.JOINT_LENGTH),
                               self.unit.bottom_depth)
            joint_mid = (joint_top + joint_bottom) / 2

            nominal_thickness = GeometryCalculator.get_wall_thickness_at_depth(
                self.unit, joint_mid
            )
            min_thickness = nominal_thickness * 0.5

            # Generate corrosion
            depth_factor = 1 + 0.3 * np.sin(
                np.pi * (joint_mid - self.unit.top_depth) / unit_depth_range
            )
            base_corrosion_rate = np.random.normal(0.000008, 0.000003)
            total_corrosion = abs(base_corrosion_rate) * days_diff * depth_factor
            joint_variation = np.random.normal(0, 0.002)

            remaining_thickness = nominal_thickness - total_corrosion + joint_variation
            remaining_thickness = np.clip(remaining_thickness, min_thickness,
                                          nominal_thickness)

            self.measurements.append({
                'depth': joint_mid,
                'remaining_thickness': remaining_thickness,
                'nominal_thickness': nominal_thickness,
                'min_thickness': min_thickness
            })

    def get_measurements(self) -> List[Dict]:
        """Get all measurements."""
        return self.measurements

# =============================================================================
# MAIN WELL SCHEMATIC CLASS
# =============================================================================


class WellSchematic:
    """Main class for managing and drawing the well schematic."""

    def __init__(self):
        """Initialize well schematic."""
        self.units: List[Unit] = []
        self.lithologies: List[Lithology] = []
        self.perforations: List[Perforation] = []
        self.pressure_analyzer: Optional[PressureBarrierAnalyzer] = None

    def add_unit(self, unit: Unit) -> None:
        """Add a unit to the well."""
        self.units.append(unit)
        self._update_pressure_analyzer()

    def add_lithology(self, lithology: Lithology) -> None:
        """Add lithology to the well."""
        self.lithologies.append(lithology)

    def add_perforation(self, perforation: Perforation) -> None:
        """Add perforation to the well."""
        self.perforations.append(perforation)

    def _update_pressure_analyzer(self) -> None:
        """Update the pressure barrier analyzer."""
        self.pressure_analyzer = PressureBarrierAnalyzer(self.units)

    def get_pressure_elements(self) -> List[PressureElement]:
        """Get all pressure elements."""
        if not self.pressure_analyzer:
            self._update_pressure_analyzer()
        return self.pressure_analyzer.get_pressure_elements()

    def set_sealed_status(self, element_id: int, is_sealed: bool) -> None:
        """Set the sealed status of a pressure element."""
        if not self.pressure_analyzer:
            self._update_pressure_analyzer()
        self.pressure_analyzer.update_sealing_state(element_id, is_sealed)

    def _setup_figure_and_axes(self, show_caliper: bool = True,
                               caliper_data: Optional[list] = None):
        """Set up the figure and axes for the well schematic and caliper plots."""
        # Calculate maximum depth based only on schematic units
        max_depth = max(u.bottom_depth for u in self.units) if self.units else 1000

        # Inform user if caliper data extends beyond schematic depth
        if caliper_data:
            caliper_max_depth = max(point['depth'] for point in caliper_data)
            if caliper_max_depth > max_depth:
                beyond_count = len([p for p in caliper_data
                                    if p['depth'] > max_depth])
                print(f"INFO: {beyond_count} caliper data points extend beyond "
                      f"schematic depth ({caliper_max_depth:.1f}m > {max_depth}m) "
                      f"and will be clipped")

        if show_caliper:
            # Set figure size to 800x900 pixels with caliper plot
            fig = plt.figure(figsize=(7, 9))
            gs = fig.add_gridspec(1, 2, width_ratios=[2, 1], wspace=0)  # No gap
            ax_well = fig.add_subplot(gs[0])
            ax_caliper = fig.add_subplot(gs[1], sharey=ax_well)

            # Add secondary y-axis (TVD) only to the caliper plot (right)
            ax_caliper_tvd = ax_caliper.twinx()
            ax_caliper.set_ylim(0, max_depth * 1.05)
            ax_caliper.invert_yaxis()
            ax_caliper_tvd.set_ylim(0, max_depth * 1.05)
            ax_caliper_tvd.invert_yaxis()
            ax_caliper_tvd.set_ylabel('Depth TVD (m)')
            ax_caliper_tvd.yaxis.set_label_position('right')
            ax_caliper_tvd.yaxis.set_ticks_position('right')

            # Set y-axis for well schematic on the left
            ax_well.set_ylabel("Depth MD (m)")
            return fig, ax_well, ax_caliper, ax_caliper_tvd
        else:
            # Set figure size for well schematic only
            fig = plt.figure(figsize=(6, 9))
            ax_well = fig.add_subplot(111)

            # Set y-axis for well schematic
            ax_well.set_ylim(0, max_depth * 1.05)
            ax_well.invert_yaxis()
            ax_well.set_ylabel("Depth MD (m)")
            return fig, ax_well, None, None

    def draw(self, selected_date: Optional[datetime] = None,
             primary_barriers: List[int] = None,
             secondary_barriers: List[int] = None,
             caliper_unit_index: Optional[int] = None,
             show_legend: bool = True,
             show_caliper: bool = True,
             caliper_data: Optional[list] = None) -> None:
        """Draw the complete well schematic."""
        primary_barriers = primary_barriers or []
        secondary_barriers = secondary_barriers or []
        # Update sealed status for specified pressure barrier elements
        for element_id in primary_barriers + secondary_barriers:
            self.set_sealed_status(element_id, True)
        # Setup figure and axes
        fig, ax_well, ax_caliper, ax_caliper_tvd = self._setup_figure_and_axes(
            show_caliper, caliper_data
        )
        # Sort units by outer diameter (smallest to largest)
        units_sorted = sorted(self.units, key=lambda u: u.outer_diameter or 0)
        # Draw all units
        for unit in units_sorted:
            unit._patches.clear()
            is_innermost = unit == min(units_sorted,
                                       key=lambda u: u.outer_diameter or 0)
            unit.draw(ax_well, is_innermost=is_innermost, all_units=units_sorted)
            self._apply_barrier_coloring(unit, primary_barriers, secondary_barriers)
        # Draw perforations
        for perforation in self.perforations:
            for unit in units_sorted:
                if unit.depth_interval.overlaps_with(perforation.depth_interval):
                    perforation.draw(ax_well, outer_diameter=unit.outer_diameter or 0)
        # Draw lithologies
        self._draw_lithologies(ax_well, units_sorted)
        # Draw annulus labels
        self._draw_annulus_labels(ax_well, units_sorted)
        # Setup well plot
        self._setup_well_plot(ax_well, show_legend=show_legend)
        # Setup caliper plot only if show_caliper is True
        if show_caliper and ax_caliper is not None:
            self._setup_caliper_plot(ax_caliper, caliper_unit_index, selected_date,
                                     show_legend=show_legend, caliper_data=caliper_data)
        self._print_information_tables()

    def _apply_barrier_coloring(self, unit: Unit, primary_barriers: List[int],
                                secondary_barriers: List[int]) -> None:
        """Apply barrier coloring to unit patches."""
        pressure_elements = self.get_pressure_elements()

        for patch_info in unit._patches:
            if len(patch_info) >= 2:
                patch_type, patch = patch_info[0], patch_info[1]

                # Find matching pressure element
                matching_element = self._find_matching_element(
                    unit, patch_type, patch, pressure_elements
                )

                if matching_element:
                    if matching_element.id in primary_barriers:
                        patch.set_facecolor('blue')
                        patch.set_alpha(0.8)
                        patch.set_zorder(20)
                    elif matching_element.id in secondary_barriers:
                        patch.set_facecolor(SECONDARY_BARRIER_COLOR)
                        patch.set_alpha(0.8)
                        patch.set_zorder(20)

    def _find_matching_element(self, unit: Unit, patch_type: str, patch,
                               pressure_elements: List[PressureElement]
                               ) -> Optional[PressureElement]:
        """Find matching pressure element for a patch."""
        for element in pressure_elements:
            # Match unit structural elements (casing, tubing, liner)
            if (element.unit_name == unit.name and
                element.element_type in ['casing', 'tubing', 'liner'] and
                    patch_type == 'wall'):
                return element

            # Match packer elements with 'packer' patches
            elif (element.unit_name == unit.name and
                  element.element_type == 'packer' and
                  patch_type == 'packer'):
                return element

            # Match plug elements with 'plug' patches
            elif (element.unit_name == unit.name and
                  element.element_type == 'plug' and
                  patch_type == 'plug'):
                return element

            # Match fluid elements with their specific fluid type patches
            elif (element.element_type == 'fluid' and
                  element.fluid_type == patch_type and
                  element.unit_name.startswith(unit.name)):
                return element

        return None

    def _draw_lithologies(self, ax: plt.Axes, units_sorted: List[Unit]) -> None:
        """Draw all lithologies."""
        if not self.lithologies:
            return

        max_diameter = max(u.outer_diameter or 0 for u in units_sorted)
        litho_x_offset = max_diameter / 2 * 1.75
        litho_width = 2.0

        for lithology in self.lithologies:
            if lithology.caprock:
                # Calculate caprock boundaries
                caprock_boundaries = self._calculate_caprock_boundaries(lithology, units_sorted)
                lithology.draw(ax, caprock_boundaries=caprock_boundaries)
            else:
                lithology.draw(ax, x_offset=litho_x_offset, width=litho_width)

    def _calculate_caprock_boundaries(self, lithology: Lithology,
                                      units_sorted: List[Unit]) -> Dict:
        """Calculate boundaries for caprock drawing."""
        def get_outermost_at_depth(depth: float) -> float:
            candidates = [u for u in units_sorted
                          if u.depth_interval.contains_depth(depth)]
            if not candidates:
                return 0
            return max(u.openhole_diameter or u.outer_diameter or 0
                       for u in candidates)

        left_inner = get_outermost_at_depth(lithology.top_depth)
        outmost_oh = max(u.openhole_diameter or 0 for u in units_sorted)

        return {
            'left': -outmost_oh / 2,
            'left_inner': -left_inner / 2,
            'right': outmost_oh / 2,
            'right_inner': left_inner / 2
        }

    def _draw_annulus_labels(self, ax: plt.Axes, units_sorted: List[Unit]) -> None:
        """Draw annulus labels in the correct annulus spaces."""
        # Only show annulus labels for units that actually have annulus fluids
        # and position them in the middle of the actual annulus space
        for i, unit in enumerate(units_sorted):
            # Skip liners and units without annulus fluids
            if isinstance(unit, Liner) or not unit.annulus_fluids:
                continue

            # Find the innermost unit that overlaps and creates the main annulus
            inner_unit = None
            max_overlap = 0
            for j in range(i + 1, len(units_sorted)):
                candidate = units_sorted[j]
                # Check if this unit overlaps with our unit
                if unit.depth_interval.overlaps_with(candidate.depth_interval):
                    # Calculate overlap length to find the most significant overlap
                    overlap_top = max(unit.top_depth, candidate.top_depth)
                    overlap_bottom = min(unit.bottom_depth, candidate.bottom_depth)
                    overlap_length = overlap_bottom - overlap_top
                    # Prefer the unit with the longest overlap that starts from surface
                    if (overlap_length > max_overlap or
                            (candidate.top_depth == 0 and unit.top_depth == 0)):
                        max_overlap = overlap_length
                        inner_unit = candidate
            if inner_unit:
                # Calculate position using the provided formula
                outer_radius = (unit.inner_diameter or 0) / 2
                OH = (unit.openhole_diameter or 0) / 2  # Openhole radius
                OD = (unit.outer_diameter or 0) / 2  # Outer diameter radius
                # Position in the space between outer diameter and openhole
                x_pos = -(outer_radius + (OH - OD) / 2)
                # Place label at the very top of the plot (y=0)
                y_pos = 0
                # Use a simple numbering system based on outer diameter size
                # Largest unit gets A, next gets B, etc.
                annulus_letter = chr(65 + i)  # A, B, C, etc.
                ax.text(x_pos, y_pos, annulus_letter,
                        ha='center', va='bottom',
                        bbox=dict(facecolor='white', edgecolor='black',
                                  alpha=0.9, boxstyle='round,pad=0.3'),
                        fontsize=12, fontweight='bold', zorder=15)

    def _setup_well_plot(self, ax: plt.Axes, show_legend: bool = True) -> None:
        """Set up the well schematic plot."""
        if not self.units:
            return

        max_depth = max(u.bottom_depth for u in self.units)
        max_diameter = max(u.outer_diameter or 0 for u in self.units)

        # Set limits
        ax.set_ylim(0, max_depth * 1.05)
        ax.invert_yaxis()

        litho_x_offset = max_diameter / 2 * 1.75
        litho_width = 2.0
        ax.set_xlim(-max_diameter / 2 * 1.3, litho_x_offset + litho_width)

        # Remove x-ticks from the lithology column and higher
        xticks = ax.get_xticks()
        filtered_xticks = [tick for tick in xticks if tick < litho_x_offset]
        ax.set_xticks(filtered_xticks)

        # Labels and grid
        ax.set_title('Well Schematic', pad=20, fontsize=18, fontweight='bold')
        ax.set_xlabel('Radius (inches)')
        ax.set_ylabel('Depth MD (m)')
        ax.grid(True, linestyle='--', alpha=0.3)

        # Setup legends
        if show_legend:
            self._setup_legends(ax)

    def _setup_legends(self, ax: plt.Axes) -> None:
        """Set up legends for the plot."""
        # Main legend elements
        legend_elements = [
            patches.Patch(facecolor='black', edgecolor='black', label='Casing/Tubing'),
        ]
        # Add Open hole entry only if openhole patches are drawn
        if any(isinstance(p, patches.Patch) and p.get_hatch() == '//' for p in ax.patches):
            legend_elements.append(
                patches.Patch(facecolor=OPENHOLE_COLOR, alpha=0.5, hatch='//', label='Open hole')
            )
        # Add fluid colors
        fluids_in_use = set()
        for unit in self.units:
            for fluid in unit.inner_fluids + unit.annulus_fluids:
                fluids_in_use.add(fluid.fluid_type)
        for fluid_type in fluids_in_use:
            color = DrawingHelper.get_fluid_color(fluid_type)
            legend_elements.append(
                patches.Patch(facecolor=color, alpha=0.5,
                              label=fluid_type.value.capitalize())
            )
        # Add lithology legend entries
        for litho in self.lithologies:
            legend_elements.append(
                patches.Patch(facecolor=litho.color, edgecolor='black', hatch=litho.hatch,
                              alpha=0.7, label=litho.name)
            )
        # Place legend below the plot
        ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  ncol=2, fontsize=8, title='Schematic elements', title_fontsize=9, frameon=True)

    def _setup_caliper_plot(self, ax: plt.Axes, caliper_unit_index: Optional[int],
                            selected_date: Optional[datetime],
                            show_legend: bool = True,
                            caliper_data: Optional[list] = None) -> None:
        """Set up the caliper measurement plot."""
        ax.set_title('Caliper Measurements', pad=20, fontsize=16, fontweight='bold')
        ax.set_xlabel('Remaining Thickness (inches)')
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.invert_xaxis()
        ax.yaxis.set_tick_params(labelleft=False)
        if (caliper_unit_index is not None and
                0 <= caliper_unit_index < len(self.units)):
            selected_unit = self.units[caliper_unit_index]
            if caliper_data is not None and len(caliper_data) > 0:
                # Filter caliper data to only include points within depth range
                max_depth = (max(u.bottom_depth for u in self.units)
                             if self.units else 1000)
                filtered_data = [point for point in caliper_data
                                 if point['depth'] <= max_depth]

                if filtered_data:
                    depths = [point['depth'] for point in filtered_data]
                    thicknesses = [point.get('remaining_thickness',
                                             point.get('diameter'))
                                   for point in filtered_data]
                    ax.plot(thicknesses, depths, 'b-o', linewidth=2, markersize=4,
                            label='Remaining Thickness (inches)')

                    # Set proper x-axis limits for custom caliper data
                    if thicknesses:
                        min_thickness = min(thicknesses)
                        max_thickness = max(thicknesses)
                        x_range = max_thickness - min_thickness
                        # Add padding (20% on each side)
                        padding = x_range * 0.2 if x_range > 0 else 0.1
                        ax.set_xlim(max(0, min_thickness - padding),
                                    max_thickness + padding)

                    # Show info about filtered data
                    total_points = len(caliper_data)
                    shown_points = len(filtered_data)
                    if total_points > shown_points:
                        print(f"INFO: Showing {shown_points}/{total_points} "
                              f"caliper points (clipped at {max_depth}m)")
                else:
                    ax.text(0.5, 0.5, 'No caliper data within schematic depth range',
                            transform=ax.transAxes, ha='center', va='center')
            else:
                caliper_gen = CaliperMeasurementGenerator(selected_unit,
                                                          selected_date)
                measurements = caliper_gen.get_measurements()
                if measurements:
                    depths = [m['depth'] for m in measurements]
                    thicknesses = [m['remaining_thickness'] for m in measurements]
                    ax.plot(thicknesses, depths, 'b-o', linewidth=2, markersize=4,
                            label='Remaining Thickness (inches)')
                    nominal_thick = measurements[0]['nominal_thickness']
                    min_thick = measurements[0]['min_thickness']
                    depth_range = [selected_unit.top_depth, selected_unit.bottom_depth]
                    ax.plot([nominal_thick, nominal_thick], depth_range,
                            'g--', linewidth=2, alpha=0.8, label='Nominal Thickness')
                    ax.plot([min_thick, min_thick], depth_range,
                            'r-.', linewidth=2, alpha=0.8, label='Min Required (50%)')
            if show_legend:
                ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                          ncol=2, fontsize=8)
            ax.set_xlim(0, ax.get_xlim()[1] * 1.2)
        else:
            ax.text(0.5, 0.5, 'Select a unit for caliper measurements',
                    transform=ax.transAxes, ha='center', va='center')

    def _print_information_tables(self) -> None:
        """Print information tables to console."""
        pressure_elements = self.get_pressure_elements()

        # Structural Elements Table
        print("\nStructural Elements Table:")
        print("-" * 80)
        print(f"{'Name':<25} {'Type':<10} {'Top':<8} {'Bottom':<8} {'ID':<4}")
        print("-" * 80)

        for element in pressure_elements:
            if element.element_type in ['casing', 'tubing', 'liner', 'packer', 'plug']:
                print(f"{element.unit_name:<25} {element.element_type:<10} "
                      f"{element.top_depth:<8.1f} {element.bottom_depth:<8.1f} "
                      f"{element.id:<4}")
        print("-" * 80)

        # Annulus Fluids Table
        print("\nAnnulus Fluids Table:")
        print("-" * 90)
        print(f"{'Unit':<25} {'Annulus':<15} {'Fluid Type':<12} "
              f"{'Top':<8} {'Bottom':<8} {'Height':<8} {'ID':<4}")
        print("-" * 90)

        # Collect all annulus fluids with their pressure element IDs
        annulus_data = []
        for unit in self.units:
            if unit.annulus_fluids:
                for fluid in unit.annulus_fluids:
                    # Find the corresponding pressure element ID
                    element_id = None
                    for element in pressure_elements:
                        if (element.element_type == 'fluid' and
                                element.unit_name.startswith(unit.name) and
                                element.unit_name.endswith('(annulus)') and
                                element.fluid_type == fluid.fluid_type.value):
                            element_id = element.id
                            break

                    # Determine annulus letter (A, B, C, etc.)
                    # Sort all units by outer diameter (largest to smallest)
                    units_sorted = sorted(self.units,
                                          key=lambda u: u.outer_diameter or 0, reverse=True)
                    annulus_letter = "N/A"

                    # Find which annulus this unit creates
                    for i, sorted_unit in enumerate(units_sorted):
                        if sorted_unit == unit and i < len(units_sorted) - 1:
                            annulus_letter = chr(65 + i)  # A, B, C, etc.
                            break

                    annulus_data.append({
                        'unit_name': unit.name,
                        'annulus_letter': annulus_letter,
                        'fluid_type': fluid.fluid_type.value,
                        'top_depth': fluid.depth_interval.top,
                        'bottom_depth': fluid.depth_interval.bottom,
                        'height': fluid.depth_interval.height,
                        'element_id': element_id or 'N/A'
                    })

        # Sort by unit name and depth
        annulus_data.sort(key=lambda x: (x['unit_name'], x['top_depth']))

        for data in annulus_data:
            print(f"{data['unit_name']:<25} {data['annulus_letter']:<15} "
                  f"{data['fluid_type']:<12} {data['top_depth']:<8.1f} "
                  f"{data['bottom_depth']:<8.1f} {data['height']:<8.1f} {data['element_id']:<4}")

        if not annulus_data:
            print("No annulus fluids defined")

        print("-" * 90)

        # Pressure Barrier Elements Table
        print("\nPressure Barrier Elements Table:")
        print("-" * 100)
        print(f"{'ID':<4} {'Type':<10} {'Unit':<25} {'Side':<8} {'Top':<8} "
              f"{'Bottom':<8} {'Sealed':<8} {'Fluid':<10}")
        print("-" * 100)

        for element in sorted(pressure_elements, key=lambda x: x.id):
            fluid_type = element.fluid_type or ''
            print(f"{element.id:<4} {element.element_type:<10} "
                  f"{element.unit_name:<25} {element.side:<8} "
                  f"{element.top_depth:<8.1f} {element.bottom_depth:<8.1f} "
                  f"{int(element.is_sealed):<8} {fluid_type:<10}")
        print("-" * 100)

    def get_all_annuluses(self) -> List[Dict[str, Any]]:
        """
        Get all annuluses in the well with their properties.

        Returns:
            List of dictionaries containing annulus information:
            - annulus_id: Letter identifier (A, B, C, etc.)
            - outer_unit: Name of the outer unit forming the annulus
            - inner_unit: Name of the inner unit (if any)
            - fluids: List of fluid intervals in this annulus
            - depth_range: Overall depth range of the annulus
        """
        if not self.units:
            return []

        annuluses = []

        # Sort units by outer diameter (largest to smallest)
        units_sorted = sorted(self.units, key=lambda u: u.outer_diameter or 0, reverse=True)

        # For each unit that has annulus fluids, determine its annulus properties
        for i, unit in enumerate(units_sorted):
            # Skip units without annulus fluids
            if not unit.annulus_fluids:
                continue

            # Find the inner unit that creates this annulus
            inner_unit = None
            max_overlap = 0

            for j in range(i + 1, len(units_sorted)):
                candidate = units_sorted[j]
                # Check if this unit overlaps with our unit
                if unit.depth_interval.overlaps_with(candidate.depth_interval):
                    # Calculate overlap length to find the most significant overlap
                    overlap_top = max(unit.top_depth, candidate.top_depth)
                    overlap_bottom = min(unit.bottom_depth, candidate.bottom_depth)
                    overlap_length = overlap_bottom - overlap_top

                    # Prefer the unit with the longest overlap that starts from surface
                    if (overlap_length > max_overlap or
                            (candidate.top_depth == 0 and unit.top_depth == 0)):
                        max_overlap = overlap_length
                        inner_unit = candidate

            # Create annulus information
            annulus_info = {
                'annulus_id': chr(65 + i),  # A, B, C, etc.
                'outer_unit': unit.name,
                'inner_unit': inner_unit.name if inner_unit else None,
                'outer_diameter': unit.outer_diameter,
                'inner_diameter': inner_unit.outer_diameter if inner_unit else None,
                'openhole_diameter': unit.openhole_diameter,
                'depth_range': {
                    'top': unit.top_depth,
                    'bottom': unit.bottom_depth
                },
                'fluids': []
            }

            # Add fluid information
            for fluid in unit.annulus_fluids:
                fluid_info = {
                    'fluid_type': fluid.fluid_type.value,
                    'top_depth': fluid.depth_interval.top,
                    'bottom_depth': fluid.depth_interval.bottom,
                    'height': fluid.depth_interval.height
                }
                annulus_info['fluids'].append(fluid_info)

            # Calculate overall annulus dimensions
            if inner_unit:
                annulus_info['annulus_width'] = (
                    (unit.inner_diameter - inner_unit.outer_diameter) / 2
                )
            else:
                annulus_info['annulus_width'] = (
                    (unit.openhole_diameter - unit.outer_diameter) / 2
                    if unit.openhole_diameter else None
                )

            annuluses.append(annulus_info)

        return annuluses
# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def _convert_fluid_lists(kwargs: Dict) -> Dict:
    """Convert fluid dictionaries to FluidInterval objects."""
    # Convert annulus fluids
    if 'annulus_fluids' in kwargs:
        annulus_fluids = []
        for fluid_dict in kwargs['annulus_fluids']:
            fluid_interval = DepthInterval(fluid_dict['top_depth'], fluid_dict['bottom_depth'])
            fluid = FluidInterval(fluid_dict['fluid_type'], fluid_interval)
            annulus_fluids.append(fluid)
        kwargs['annulus_fluids'] = annulus_fluids

    # Convert inner fluids
    if 'inner_fluids' in kwargs:
        inner_fluids = []
        for fluid_dict in kwargs['inner_fluids']:
            fluid_interval = DepthInterval(fluid_dict['top_depth'], fluid_dict['bottom_depth'])
            fluid = FluidInterval(fluid_dict['fluid_type'], fluid_interval)
            inner_fluids.append(fluid)
        kwargs['inner_fluids'] = inner_fluids

    return kwargs


def create_casing(name: str, top_depth: float, bottom_depth: float,
                  inner_diameter: float, outer_diameter: float,
                  openhole_diameter: Optional[float] = None,
                  is_tapered: bool = False,
                  transition_depth: Optional[float] = None,
                  bottom_inner_diameter: Optional[float] = None,
                  bottom_outer_diameter: Optional[float] = None,
                  **kwargs) -> Casing:
    """Create a casing unit."""
    depth_interval = DepthInterval(top_depth, bottom_depth)
    dimensions = Dimensions(inner_diameter, outer_diameter, openhole_diameter)
    kwargs = _convert_fluid_lists(kwargs)
    return Casing(name, depth_interval, dimensions, is_tapered,
                  transition_depth, bottom_inner_diameter,
                  bottom_outer_diameter, **kwargs)


def create_tubing(name: str, top_depth: float, bottom_depth: float,
                  inner_diameter: float, outer_diameter: float,
                  **kwargs) -> Tubing:
    """Create a tubing unit."""
    depth_interval = DepthInterval(top_depth, bottom_depth)
    dimensions = Dimensions(inner_diameter, outer_diameter)
    kwargs = _convert_fluid_lists(kwargs)
    return Tubing(name, depth_interval, dimensions, **kwargs)


def create_liner(name: str, top_depth: float, bottom_depth: float,
                 inner_diameter: float, outer_diameter: float,
                 openhole_diameter: Optional[float] = None,
                 **kwargs) -> Liner:
    """Create a liner unit."""
    depth_interval = DepthInterval(top_depth, bottom_depth)
    dimensions = Dimensions(inner_diameter, outer_diameter, openhole_diameter)
    kwargs = _convert_fluid_lists(kwargs)
    return Liner(name, depth_interval, dimensions, **kwargs)

# =============================================================================
# JSON INPUT BUILDER
# =============================================================================


def build_well_from_json(data):
    """Build a WellSchematic object from a JSON-like dict input."""
    well = WellSchematic()
    # Add units
    for unit in data.get("units", []):
        unit_type = unit["type"].lower()
        if unit_type == "casing":
            well.add_unit(create_casing(
                name=unit["name"],
                top_depth=unit["top_depth"],
                bottom_depth=unit["bottom_depth"],
                inner_diameter=unit["inner_diameter"],
                outer_diameter=unit["outer_diameter"],
                openhole_diameter=unit.get("openhole_diameter"),
                is_tapered=unit.get("is_tapered", False),
                transition_depth=unit.get("transition_depth"),
                bottom_inner_diameter=unit.get("bottom_inner_diameter"),
                bottom_outer_diameter=unit.get("bottom_outer_diameter"),
                annulus_fluids=unit.get("annulus_fluids", []),
                inner_fluids=unit.get("inner_fluids", [])
            ))
        elif unit_type == "liner":
            well.add_unit(create_liner(
                name=unit["name"],
                top_depth=unit["top_depth"],
                bottom_depth=unit["bottom_depth"],
                inner_diameter=unit["inner_diameter"],
                outer_diameter=unit["outer_diameter"],
                openhole_diameter=unit.get("openhole_diameter"),
                annulus_fluids=unit.get("annulus_fluids", []),
                inner_fluids=unit.get("inner_fluids", [])
            ))
        elif unit_type == "tubing":
            well.add_unit(create_tubing(
                name=unit["name"],
                top_depth=unit["top_depth"],
                bottom_depth=unit["bottom_depth"],
                inner_diameter=unit["inner_diameter"],
                outer_diameter=unit["outer_diameter"],
                annulus_fluids=unit.get("annulus_fluids", []),
                inner_fluids=unit.get("inner_fluids", [])
            ))
    # Add lithologies
    for lith in data.get("lithologies", []):
        well.add_lithology(Lithology(
            name=lith["name"],
            depth_interval=DepthInterval(lith["top_depth"], lith["bottom_depth"]),
            color=lith["color"],
            hatch=lith.get("hatch", "")
        ))
    return well
