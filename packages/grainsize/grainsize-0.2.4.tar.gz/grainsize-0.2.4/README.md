# grainsize

## Sedimentological Data Analysis Made Easy

The `grainsize` Python package provides a suite of tools for processing, analyzing, and visualizing grain size distributions, elemental data, and micropaleontological proxies (foraminifera and bryozoans) from sediment cores.

---

## Features

- **Grain Size Analysis:**
  - Clean and normalize grain size distributions.
  - Calculate statistical parameters (mean, median, mode, std, skewness, kurtosis).
  - Create grain size categories (clay, silt, sand, gravel).
  - Visualize statistics and fine fraction (<63 µm).

- **XRF Data Analysis:**
  - Import and clean XRF elemental data.
  - Convert percentages to ppm.
  - Plot elemental abundances and elemental ratios.

- **Cluster Analysis:**
  - Perform Bray-Curtis dissimilarity analysis.
  - Create dendrograms for stratigraphic clustering.

- **Foraminifera Data Analysis:**
  - Calculate normalized abundance per 1cc.
  - Plot planktic and benthic foraminifera abundance with color scaling.

- **Bryozoans Data Analysis:**
  - Compare abundance categories across cores.
  - Perform statistical tests (Chi-square, Mann-Whitney U).
  - Visualize depth distribution of bryozoan types.

- **Integrated Core Analysis:**
  - Plot combined grain size and XRF results side-by-side for stratigraphic interpretation.

---

## Installation

Manually clone the repository and install dependencies listed in requirements

---

## Quickstart Example

```python
from grainsize import GrainSize, XRF, Forams, Bryozoans, Stratigraphy, BCD

# Grain Size Example
gs = GrainSize(fname="grainsize_data.xlsx")
gs.clean_data()
stats = gs.create_stats_df()
stats.plot_stats(core_name="Core A")

# XRF Example
xrf = XRF(fname="xrf_data.xlsx")
xrf_clean = xrf.clean_data()
xrf_clean.plot_elements(core_name="Core A")

# Bray-Curtis Clustering
bcd = BCD.from_grain_size(gs)
bcd.plot_dendrogram(core_name="Core A")

# Foraminifera Example
forams = Forams(fname="forams.csv")
forams.plot_forams(core_name="Core A")

# Bryozoans Example
bryo = Bryozoans(fname="bryozoans.xlsx")
bryo.plot_corr_matrix(core_name="Core A")
```

---

## Main Classes and Functionalities

### GrainSize

- `clean_data()` → Clean raw MasterSizer data.
- `normalize_gs()` → Normalize grain size percentages.
- `create_stats_df()` → Calculate median, mode, mean, std, skewness, kurtosis.
- `create_categories()` → Create clay, silt, sand, gravel summaries.
- `plot_stats()` → Plot statistics.
- `compare_gs()` → Compare multiple cores.

### XRF

- `clean_data()` → Clean depth intervals.
- `to_ppm()` → Convert % values to ppm.
- `plot_elements()` → Plot elemental concentrations.
- `plot_ratios()` → Plot elemental ratios.
- `compare_ratios()` → Compare elemental ratios across cores.

### Forams

- Automatically calculates normalized abundance, p/b ratios, and percentages.
- `plot_forams()` → Plot total abundance colored by planktic %.
- `compare_forams_plot()` → Compare cores.
- `plot_benthic()` → Plot benthic abundance.

### Bryozoans

- `calc_chi2()` → Chi-square test for presence/absence.
- `calc_mann_whitney()` → Mann-Whitney U test.
- `calc_corr()` + `plot_corr_matrix()` → Correlation analysis.
- `plot_large_bryo()` → Compare large bryozoans categories.
- `plot_depth_bars()` → Bryozoan types vs. depth.

### BCD (Bray-Curtis Dissimilarity)

- `compute_BCD()` → Compute Bray-Curtis distances.
- `plot_dendrogram()` → Create a stratigraphic dendrogram.
- `merge_interp()` → Merge and interpolate two cores.

---

## Requirements

- Python 3.8+
- pandas
- numpy
- matplotlib
- seaborn
- scipy

---

## License

MIT License

---

## Acknowledgements

Developed to assist sedimentological and micropaleontological research workflows, with a special focus on making complex laboratory datasets ready for visualization and statistical analysis.

---

## Author

**Jarden Aaltonen**
Feel free to report issues or suggest improvements!
