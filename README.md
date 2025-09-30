# Introducing Modern Physics Concepts for Enhanced Coherent Error Detection in Quantum Computing

This repository contains supplementary materials, code, and data for the research paper "Introducing Modern Physics Concepts for Enhanced Coherent Error Detection in Quantum Computing". The work presents a novel, resource-efficient protocol for detecting coherent errors in quantum circuits by leveraging the imaginary component of pseudo-entropy.

---

## Project Structure

- **pseudo_entropy.ipynb**: Jupyter notebook containing core code for simulating pseudo-entropy calculation and generating main results, building on hardware-data outputs.  
- **hardware-data.ipynb**: Jupyter notebook interfacing with IBM Qiskit simulators, generating hardware datasets for noise model calibration used by pseudo_entropy.ipynb.  
- **requirements.txt**: Python dependencies for running notebooks.  
- **results/**: Generated figures (including sensitivity maps, phase diagrams) and Excel tables from simulations and analysis.  
- **hardware/**: Raw/generated hardware data CSVs from Qiskit backend simulations, including qubit properties and optimized groups derived from hardware-data.ipynb.  
- **data/**: Intermediate and final processed data in Python pickle format facilitating efficient notebook reruns.  
- **documents/**: LaTeX source files for full thesis text and supplementary materials.

---

## Setup and Installation

1. **System Requirements:**  
   * macOS 15.5  
   * Apple M2 chip  
   * Python 3.13.5  

2. **Clone the repository:**  
   ```
   git clone https://github.com/your-repo-name/pseudo-entropy-quantum-error-detection.git
   cd pseudo-entropy-quantum-error-detection
   ```

3. **Install Git LFS and pull data:**  
   ```
   git lfs install
   git lfs pull
   ```

4. **Virtual environment:**  
   ```
   python -m venv venv
   source venv/bin/activate # Windows: venv\Scripts\activate
   ```

5. **Install Python dependencies:**  
   ```
   pip install -r requirements.txt
   ```

6. **Run notebooks:**  
   Launch Jupyter Lab or Notebook:  
   ```
   jupyter lab
   # or
   jupyter notebook
   ```  
   Run `hardware-data.ipynb` first to generate hardware models, then `pseudo_entropy.ipynb` for all analyses and figures.

---

## Thesis Documents List

| File Path                      | Description                                                                       |
|-------------------------------|-----------------------------------------------------------------------------------|
| `documents/master_document.tex` | Primary LaTeX master file controlling build sequence, fonts, languages, numbering |
| `documents/english_title_page.tex` | Official English thesis title page                                                |
| `documents/english_acknowledgements.tex` | English acknowledgments section                                         |
| `documents/english_abstract.tex` | English abstract summarizing thesis                              |
| `documents/main.tex`            | Main thesis body: introduction, methods, results, discussion                      |
| `documents/references.bib`      | Bibliography database for citations                                             |
| `documents/supplementary_content.tex` | Appendix content: supplementary data, proofs, extended results           |
| `documents/hebrew_abstract.tex`  | Hebrew language abstract                                                         |
| `documents/hebrew_acknowledgements.tex` | Hebrew acknowledgments                                                       |
| `documents/hebrew_title_page.tex` | Hebrew thesis title page                                                         |

---

## Supplementary Figures, Data, and Code Guide

This repository provides all figures, data tables and code supporting the article “Enhanced Coherent Error Detection in Quantum Computing.”  
All captions include succinct scientific interpretations and explicitly note critical transitions at $ \beta = \pm\pi/2 $.

### 1. Pseudo-Entropy Derivative and Sensitivity Maps

| Figure (Path)                                                | Description                                                                                                     | Critical Feature                                                  |
|-------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| **results/first_derivative_wrt_beta_ds_dbeta.png**          | First derivative $ d\check{S}/d\beta $ showing sensitivity of pseudo-entropy to interaction strength $\beta$.  | Marked peaks at $ \beta = \pm \pi/2 $ indicate quantum transitions.   |
| **results/first_derivative_wrt_delta_ds_ddelta.png**        | First derivative $ d\check{S}/d\delta $ showing sensitivity to coherent phase error $\delta$.              | Maxima identify phase-sensitive regions crucial for error detection.    |
| **results/half_second_derivative_wrt_beta2_half_d2s_dbeta2.png**  | Half the second derivative $ \frac{1}{2} d^2\check{S}/d\beta^2 $ indicating curvature in $\beta$.           | Critical boundaries emphasized through pronounced curvature.         |
| **results/half_second_derivative_wrt_delta2_half_d2s_ddelta2.png** | Half the second derivative $ \frac{1}{2} d^2\check{S}/d\delta^2 $ showing curvature in phase direction.     | Useful for detecting phase transition regions within error regime.     |
| **results/mixed_second_derivative_d2s_dbeta_ddelta.png**    | Mixed derivative $ d^2\check{S}/d\beta d\delta $ identifying joint parameter sensitivity.                      | Highlights regions of cross-parameter interplay influencing errors.      |

**Additional Variable Sensitivity Details:**

| Figure (Path)                   | Content                       | Notes                                  |
|--------------------------------|------------------------------|---------------------------------------|
| **results/sensitivity_d2S_dbeta2.png**       | Curvature $ d^2\check{S}/d\beta^2 $    | Sensitivity in $\beta$ alone         |
| **results/sensitivity_d2S_dbeta_delta.png** | Cross sensitivity $ d^2\check{S}/d\beta d\delta $ | Joint $\beta$, $\delta$ effects |
| **results/sensitivity_d2S_ddelta2.png**     | Curvature $ d^2\check{S}/d\delta^2 $    | Sensitivity in $\delta$ alone        |
| **results/sensitivity_dS_dbeta.png**        | First derivative $ d\check{S}/d\beta $       | Matches full sensitivity overview     |
| **results/sensitivity_dS_ddelta.png**       | First derivative $ d\check{S}/d\delta $       | Phase-error directional sensitivity   |

***

### 2. Phase Diagrams, Model Comparisons, and Segment Analysis

- **Phase Diagrams:** Located as `results/classical_vs_quantum_regions_thresh_X.png` and `results/continuous_classical_regions_thresh_X.png`. Delineate classical-like vs quantum-like phases, critical boundary annotated at $ \beta = \pm\pi/2 $.
- **Model vs Simulation Consistency:** Figures such as `results/theory_vs_simulation_cartesian.png` and `results/theory_vs_simulation_polar.png` overlay analytical predictions and simulation results, validating the model’s accuracy.
- **Segment Analysis:** `results/segments.xlsx` contains data on detection rates and segment boundaries cross-validated with figures and text.

***

### 3. Quantum Circuit Visualizations and Sources

| File | Description | Notes |
|-|-|-|
| `results/initial_state_circuit.png` | Diagram for initial state preparation in the pseudo-entropy protocol | Generated from `results/initial_state_circuit.tex` |
| `results/initial_state_circuit.tex` | LaTeX source for circuit drawing | Editable code source |
| `results/concatenated_circuit.png` | Full concatenated circuit visualizing repeated blocks | Generated from LaTeX source |
| `results/concatenated_circuit.tex` | Source code for above | Editable multiple block circuit definition |
| `results/measurement_circuit.png` | Measurement step quantum circuit diagram | Generated from `results/measurement_circuit.tex` |
| `results/measurement_circuit.tex` | LaTeX source for measurement circuit | Editable readout operation representation |

***

### 4. Data Tables and Files

| File Path | Description | Purpose |
|-|-|-|
| `additional-info/comparative_methods.xlsx` | Detailed benchmarking data for error detection methods | Section supporting protocol resource and sensitivity claims |
| `additional-info/numerical_instability_parameters.xlsx` | Parameters causing numerical instability in pseudo-entropy | Defines operational protocol boundaries |
| `additional-info/Modern_Physics_Coherent_Error_Detection_Presentation.pptx` | Summary slides of research findings | Outreach and presentation support |
| `results/segments.xlsx` | Segment boundaries and detection rates for thresholds | Validates region and threshold claims |
| `results/fit_results.xlsx` | Parameter estimation data for fitted models | Supports statistical comparison in thesis tables |
| `results/statistics_results.xlsx` | Statistical descriptors of pseudo-entropy distribution | Supplemental quantitative insights |
| `results/sensitivity_results.xlsx` | Sensitivity metrics underlying derivative maps | Core numerical data for robustness analysis |
| `hardware/hardware.csv` | Simulated qubit properties and error rates from IBM backends | Basis for noise modeling and calibration |
| `hardware/optimal_qubit_groups.csv` | Optimized qubit grouping configurations | Backend-specific qubit quality optimization |

***

### 5. Reproducibility and Codebase Summary

- **pseudo_entropy.ipynb:** The full simulation and analysis notebook generating all numerical results and figures.  
- **hardware-data.ipynb:** Interfaces with IBM Qiskit simulators, extracting hardware noise and calibration models to feed into the main analysis.  

***
### 6. Quick Reference: Figure and Data Themes

-   **All sensitivity/gradient maps:** β = ±π/2 is the critical transition, always noted.
-   **Phase diagrams / threshold regions:** Explicitly show sub- and super-threshold behavior, with transitions matching theoretical predictions.
-   **Circuit diagrams:** All protocol steps are visualized with both image and editable LaTeX source.
-   **Data tables:** Complete numerical support for all claims depicted.


## Git Large File Storage (LFS)

Large data and images are stored using Git LFS to ensure efficient cloning and version management without bloating repository size.

