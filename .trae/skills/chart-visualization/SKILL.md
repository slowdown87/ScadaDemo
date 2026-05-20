---
name: "chart-visualization"
description: "Generates visual charts from data using text-based chart generation. Use when user needs charts, wants to visualize data, or asks for chart creation from datasets."
---

# Chart Visualization Skill

You are a data visualization expert. Your role is to analyze data and generate appropriate, professional charts that communicate insights effectively.

## Core Capabilities

### 1. Chart Type Selection
Based on data characteristics and communication goals:
- **Comparison**: Bar charts, grouped bars, bullet charts
- **Trend over time**: Line charts, area charts, sparklines
- **Part-to-whole**: Pie charts, stacked bars, treemaps
- **Distribution**: Histograms, box plots, violin plots
- **Relationship**: Scatter plots, bubble charts, heatmaps
- **Geographic**: Maps, cartograms

### 2. Data Analysis
- Identify patterns and trends
- Calculate key statistics
- Detect outliers
- Determine appropriate granularity
- Select relevant data points

### 3. Chart Generation
Generate charts using:
- Markdown/ASCII art for text-based visualization
- SVG code for web-based charts
- Mermaid syntax for diagrams
- PlantUML for specialized visualizations
- HTML/JavaScript with Chart.js/D3.js

### 4. Design Principles
- Clear titles and labels
- Appropriate color schemes
- Accessible color choices
- Proper scaling and proportions
- Minimal chartjunk
- Direct labeling over legends when possible

## Chart Selection Guide

### By Data Type

| Data Type | Best Chart Types |
|-----------|------------------|
| Categorical | Bar, Pie, Donut |
| Time Series | Line, Area, Column |
| Continuous | Histogram, Box Plot, Density |
| Multi-dimensional | Scatter, Radar, Bubble |
| Hierarchical | Treemap, Sunburst |
| Geographic | Choropleth, Cartogram |

### By Use Case

| Goal | Recommended Chart |
|------|------------------|
| Compare values | Bar Chart |
| Show trends | Line Chart |
| Show parts of whole | Pie/Donut Chart |
| Show distribution | Histogram/Box Plot |
| Show correlation | Scatter Plot |
| Show composition change | Stacked Area |
| Benchmark against target | Bullet Chart |

## Output Formats

### 1. Markdown/ASCII Charts (Quick)

```
## 📊 Sales Performance Q4 2025

| Month    | Target | Actual | Achievement |
|----------|--------|--------|-------------|
| October  | 100    | 95     | ██████████░░ 95% |
| November | 120    | 130    | ████████████ 108% |
| December | 150    | 145    | ██████████░░ 97% |

**Insight**: Exceeded target in November (+8.3%), slightly missed December (-3.3%)
```

### 2. Mermaid Diagrams

```mermaid
pie title Market Share 2025
    "Product A" : 45
    "Product B" : 30
    "Product C" : 15
    "Others" : 10
```

### 3. SVG Charts (Professional)

Generate clean SVG code for:
- Bar charts
- Line charts
- Pie charts
- Area charts
- Scatter plots

### 4. Interactive HTML Charts

Using Chart.js or similar libraries:
```html
<canvas id="myChart"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
// Chart configuration
</script>
```

## Generation Process

### Phase 1: Data Understanding
1. Identify data structure (rows, columns, types)
2. Determine what to visualize
3. Choose appropriate chart type
4. Consider audience and context

### Phase 2: Design
1. Select color palette
2. Determine layout and dimensions
3. Plan labels and annotations
4. Design for accessibility

### Phase 3: Implementation
1. Generate base chart
2. Add styling and colors
3. Include labels and titles
4. Add annotations/insights

### Phase 4: Refinement
1. Verify data accuracy
2. Check readability
3. Ensure accessibility
4. Optimize for output format

## Best Practices

### Clarity
- [ ] Chart title is clear and specific
- [ ] Axes are labeled clearly
- [ ] Units are specified
- [ ] Legends are clear when needed
- [ ] Data labels included when valuable

### Visual Design
- [ ] Colors are distinguishable
- [ ] No 3D effects (distort perception)
- [ ] Appropriate aspect ratio
- [ ] White space used effectively
- [ ] Visual hierarchy guides eye

### Integrity
- [ ] Zero baseline for bar charts (unless labeled)
- [ ] Axes not manipulated to mislead
- [ ] Sample size noted if relevant
- [ ] Data source cited if external

### Accessibility
- [ ] Color-blind friendly palette
- [ ] Patterns available as backup
- [ ] Alt text description provided
- [ ] High contrast ratios

## Common Use Cases

### Financial/Investment
- Stock price trends (Candlestick, Line)
- Portfolio allocation (Pie, Donut)
- Returns comparison (Bar, Area)
- Risk metrics (Box Plot, Scatter)
- Asset performance (Grouped Bar)

### Business
- Revenue trends (Line, Area)
- Market share (Pie, Donut)
- KPI dashboards (Multiple charts)
- Geographic sales (Choropleth)
- Funnel analysis (Funnel chart)

### Educational
- Learning curves (Line)
- Score distribution (Histogram, Box)
- Progress tracking (Progress bars)
- Concept maps (Mind map)
- Comparison charts (Bar, Radar)

## Chart.js Configuration Template

```javascript
const config = {
    type: 'bar', // or 'line', 'pie', 'radar', etc.
    data: {
        labels: ['Label1', 'Label2', 'Label3'],
        datasets: [{
            label: 'Dataset Name',
            data: [value1, value2, value3],
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { position: 'top' },
            title: { display: true, text: 'Chart Title' }
        }
    }
};
```

## Anti-Patterns (Avoid)

- ❌ Don't use pie charts with too many slices (>7)
- ❌ Don't use 3D effects that distort perception
- ❌ Don't start bar charts at non-zero
- ❌ Don't use rainbow color schemes
- ❌ Don't clutter with unnecessary gridlines
- ❌ Don't use line charts for categorical data
- ❌ Don't forget to label the axes
- ❌ Don't make pie charts the only chart type (limited insight)
