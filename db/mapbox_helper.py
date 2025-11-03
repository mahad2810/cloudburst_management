"""
Mapbox Integration Module
Advanced map visualizations using Mapbox and PyDeck
"""

import pydeck as pdk
import pandas as pd
import streamlit as st
from typing import Optional, List, Dict, Any


class MapboxVisualizer:
    """Creates advanced map visualizations using Mapbox and PyDeck"""
    
    def __init__(self, mapbox_token: str, style: str = "mapbox://styles/mapbox/dark-v11"):
        """
        Initialize Mapbox visualizer
        
        Args:
            mapbox_token: Mapbox API token
            style: Mapbox style URL
        """
        self.mapbox_token = mapbox_token
        self.style = style
    
    def create_rainfall_heatmap(
        self,
        df: pd.DataFrame,
        lat_col: str = 'latitude',
        lon_col: str = 'longitude',
        intensity_col: str = 'rainfall_mm',
        center: List[float] = [20.5937, 78.9629],
        zoom: int = 5
    ) -> pdk.Deck:
        """
        Create rainfall intensity heatmap
        
        Args:
            df: DataFrame with location and rainfall data
            lat_col: Latitude column name
            lon_col: Longitude column name
            intensity_col: Rainfall intensity column name
            center: Map center [lat, lon]
            zoom: Initial zoom level
            
        Returns:
            PyDeck visualization
        """
        if df.empty or lat_col not in df.columns or lon_col not in df.columns:
            return None
        
        # Normalize intensity for better visualization
        max_intensity = df[intensity_col].max()
        df['normalized_intensity'] = (df[intensity_col] / max_intensity * 100).fillna(0)
        
        # Create heatmap layer
        heatmap_layer = pdk.Layer(
            "HeatmapLayer",
            data=df,
            get_position=[lon_col, lat_col],
            get_weight='normalized_intensity',
            radiusPixels=60,
            intensity=1,
            threshold=0.05,
            pickable=False
        )
        
        # Create view state
        view_state = pdk.ViewState(
            latitude=center[0],
            longitude=center[1],
            zoom=zoom,
            pitch=0,
            bearing=0
        )
        
        # Create deck
        deck = pdk.Deck(
            layers=[heatmap_layer],
            initial_view_state=view_state,
            map_style=self.style,
            mapbox_key=self.mapbox_token,
            tooltip={
                "text": f"{intensity_col}: {{" + intensity_col + "}} mm"
            }
        )
        
        return deck
    
    def create_marker_map(
        self,
        df: pd.DataFrame,
        lat_col: str = 'latitude',
        lon_col: str = 'longitude',
        color_col: Optional[str] = None,
        size_col: Optional[str] = None,
        tooltip_cols: Optional[List[str]] = None,
        center: List[float] = [20.5937, 78.9629],
        zoom: int = 5
    ) -> pdk.Deck:
        """
        Create map with markers
        
        Args:
            df: DataFrame with location data
            lat_col: Latitude column name
            lon_col: Longitude column name
            color_col: Column for color coding
            size_col: Column for size scaling
            tooltip_cols: Columns to show in tooltip
            center: Map center [lat, lon]
            zoom: Initial zoom level
            
        Returns:
            PyDeck visualization
        """
        if df.empty or lat_col not in df.columns or lon_col not in df.columns:
            return None
        
        # Prepare color mapping
        if color_col and color_col in df.columns:
            color_map = self._get_color_map(df[color_col].unique())
            df['color'] = df[color_col].map(color_map)
        else:
            df['color'] = [[79, 195, 247, 200]] * len(df)  # Default blue
        
        # Prepare size
        if size_col and size_col in df.columns:
            max_size = df[size_col].max()
            df['radius'] = (df[size_col] / max_size * 100000).fillna(50000)
        else:
            df['radius'] = 50000
        
        # Create scatterplot layer
        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position=[lon_col, lat_col],
            get_color='color',
            get_radius='radius',
            pickable=True,
            opacity=0.8,
            stroked=True,
            filled=True,
            radius_scale=1,
            radius_min_pixels=5,
            radius_max_pixels=30,
            line_width_min_pixels=1,
            get_line_color=[255, 255, 255]
        )
        
        # Create view state
        view_state = pdk.ViewState(
            latitude=center[0],
            longitude=center[1],
            zoom=zoom,
            pitch=0,
            bearing=0
        )
        
        # Prepare tooltip
        tooltip_text = ""
        if tooltip_cols:
            tooltip_text = "<br>".join([f"<b>{col}:</b> {{" + col + "}}" for col in tooltip_cols if col in df.columns])
        else:
            tooltip_text = "<b>Location:</b> {" + lat_col + "}, {" + lon_col + "}"
        
        # Create deck
        deck = pdk.Deck(
            layers=[scatter_layer],
            initial_view_state=view_state,
            map_style=self.style,
            mapbox_key=self.mapbox_token,
            tooltip={"html": tooltip_text, "style": {"color": "white"}}
        )
        
        return deck
    
    def create_hexagon_map(
        self,
        df: pd.DataFrame,
        lat_col: str = 'latitude',
        lon_col: str = 'longitude',
        value_col: Optional[str] = None,
        center: List[float] = [20.5937, 78.9629],
        zoom: int = 5,
        radius: int = 50000
    ) -> pdk.Deck:
        """
        Create hexagon aggregation map
        
        Args:
            df: DataFrame with location data
            lat_col: Latitude column name
            lon_col: Longitude column name
            value_col: Column to aggregate
            center: Map center [lat, lon]
            zoom: Initial zoom level
            radius: Hexagon radius in meters
            
        Returns:
            PyDeck visualization
        """
        if df.empty or lat_col not in df.columns or lon_col not in df.columns:
            return None
        
        # Prepare data
        if value_col and value_col in df.columns:
            df['value'] = df[value_col]
        else:
            df['value'] = 1
        
        # Create hexagon layer
        hexagon_layer = pdk.Layer(
            "HexagonLayer",
            data=df,
            get_position=[lon_col, lat_col],
            auto_highlight=True,
            elevation_scale=50,
            pickable=True,
            elevation_range=[0, 3000],
            extruded=True,
            coverage=1,
            radius=radius,
            get_elevation='value'
        )
        
        # Create view state
        view_state = pdk.ViewState(
            latitude=center[0],
            longitude=center[1],
            zoom=zoom,
            pitch=45,
            bearing=0
        )
        
        # Create deck
        deck = pdk.Deck(
            layers=[hexagon_layer],
            initial_view_state=view_state,
            map_style=self.style,
            mapbox_key=self.mapbox_token,
            tooltip={"text": "Value: {elevationValue}"}
        )
        
        return deck
    
    def create_arc_map(
        self,
        df: pd.DataFrame,
        source_lat_col: str = 'source_lat',
        source_lon_col: str = 'source_lon',
        target_lat_col: str = 'target_lat',
        target_lon_col: str = 'target_lon',
        width_col: Optional[str] = None,
        center: List[float] = [20.5937, 78.9629],
        zoom: int = 5
    ) -> pdk.Deck:
        """
        Create arc map for showing flows/connections
        
        Args:
            df: DataFrame with source and target coordinates
            source_lat_col: Source latitude column
            source_lon_col: Source longitude column
            target_lat_col: Target latitude column
            target_lon_col: Target longitude column
            width_col: Column for arc width
            center: Map center [lat, lon]
            zoom: Initial zoom level
            
        Returns:
            PyDeck visualization
        """
        if df.empty:
            return None
        
        required_cols = [source_lat_col, source_lon_col, target_lat_col, target_lon_col]
        if not all(col in df.columns for col in required_cols):
            return None
        
        # Prepare width
        if width_col and width_col in df.columns:
            max_width = df[width_col].max()
            df['arc_width'] = (df[width_col] / max_width * 10).fillna(1)
        else:
            df['arc_width'] = 5
        
        # Create arc layer
        arc_layer = pdk.Layer(
            "ArcLayer",
            data=df,
            get_source_position=[source_lon_col, source_lat_col],
            get_target_position=[target_lon_col, target_lat_col],
            get_source_color=[79, 195, 247, 180],
            get_target_color=[255, 87, 34, 180],
            get_width='arc_width',
            pickable=True
        )
        
        # Create view state
        view_state = pdk.ViewState(
            latitude=center[0],
            longitude=center[1],
            zoom=zoom,
            pitch=30,
            bearing=0
        )
        
        # Create deck
        deck = pdk.Deck(
            layers=[arc_layer],
            initial_view_state=view_state,
            map_style=self.style,
            mapbox_key=self.mapbox_token
        )
        
        return deck
    
    def _get_color_map(self, unique_values) -> Dict[Any, List[int]]:
        """Generate color mapping for categorical values"""
        colors = [
            [255, 23, 68, 200],    # Red
            [255, 111, 0, 200],    # Orange
            [253, 216, 53, 200],   # Yellow
            [76, 175, 80, 200],    # Green
            [79, 195, 247, 200],   # Blue
            [156, 39, 176, 200],   # Purple
            [233, 30, 99, 200],    # Pink
            [0, 188, 212, 200]     # Cyan
        ]
        
        color_map = {}
        for i, value in enumerate(unique_values):
            color_map[value] = colors[i % len(colors)]
        
        return color_map


# Cached instance
@st.cache_resource
def get_mapbox_visualizer(mapbox_token: str, style: str = "mapbox://styles/mapbox/dark-v11") -> Optional[MapboxVisualizer]:
    """
    Get or create Mapbox visualizer instance
    
    Args:
        mapbox_token: Mapbox API token
        style: Map style URL
        
    Returns:
        MapboxVisualizer instance or None
    """
    if not mapbox_token:
        return None
    
    try:
        return MapboxVisualizer(mapbox_token, style)
    except Exception as e:
        st.error(f"Failed to initialize Mapbox: {e}")
        return None
