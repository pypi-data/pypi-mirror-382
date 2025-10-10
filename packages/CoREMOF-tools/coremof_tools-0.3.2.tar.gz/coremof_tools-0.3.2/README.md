<img src="https://raw.githubusercontent.com/Chung-Research-Group/CoRE-MOF-Tools/main/logo.png" alt="CoRE MOF Tools logo" width="500"/>

[![Static Badge](https://img.shields.io/badge/chemrxiv-2024.nvmnr.v2-brightgreen?style=flat)](https://doi.org/10.26434/chemrxiv-2024-nvmnr-v2)
[![Docs](https://img.shields.io/badge/API-Docs-blue?logo=readthedocs&logoColor=white)](https://coremof-tools.readthedocs.io/en/latest/index.html#)
![GitHub repo size](https://img.shields.io/github/repo-size/sxm13/CoREMOF_tools?logo=github&logoColor=white&label=Repo%20Size)
[![PyPI](https://img.shields.io/pypi/v/CoREMOF-tools?logo=pypi&logoColor=white)](https://pypi.org/project/CoREMOF-tools?logo=pypi&logoColor=white)
[![Requires Python 3.9](https://img.shields.io/badge/Python-3.9-blue.svg?logo=python&logoColor=white)](https://python.org/downloads)
[![GitHub license](https://img.shields.io/github/license/sxm13/CoREMOF_tools)](https://github.com/sxm13/CoREMOF_tools/blob/main/LICENSE)
[![Downloads](https://pepy.tech/badge/CoREMOF_tools)](https://pepy.tech/project/CoREMOF_tools)
[![GitHub issues](https://img.shields.io/github/issues/sxm13/CoREMOF_tools.svg)](https://GitHub.com/sxm13/CoREMOF_tools/issues/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15055758.svg)](https://doi.org/10.5281/zenodo.15055758)
<!-- [![codecov](https://codecov.io/gh/sxm13/CoREMOF_tools/branch/main/graph/badge.svg)](https://codecov.io/gh/sxm13/CoREMOF_tools)
[![Build Status](https://travis-ci.org/sxm13/CoREMOF_tools.svg?branch=master)](https://travis-ci.org/sxm13/CoREMOF_toolst) -->

**Develop by [Guobin Zhao](https://github.com/sxm13)**

#### Installation                                                                                    
This API includes tools developed to collect, curate, and classify Computation-Ready, Experimental MOF database.    
a. You need to install the [CSD software and python API](https://downloads.ccdc.cam.ac.uk/documentation/API/installation_notes.html) before downloading the full CoRE MOF database.                                                            
b. For using CoREMOF.calculation.Zeopp, you need to input `conda install -c conda-forge zeopp-lsmo` to install Zeo++.   
c. For using CoREMOF.get_mofid, you need to install MOFid following the [manual](https://snurr-group.github.io/mofid/compiling/#installation).                    
d. For using CoREMOF.mof_check, you need to install MOFChecker by input `pip install git+https://github.com/sxm13/mofchecker_2.0.git@main`. 

#### Examples                                                                                     
Available at [Github](https://github.com/mtap-research/CoRE-MOF-Tools/tree/main/tests/examples) and [CoRE MOF Website](https://mof-db.pusan.ac.kr/API) to view examples.                         
                            

#### Citation                                          
- [CoRE MOF](https://doi.org/10.1016/j.matt.2025.102140): Zhao G, Brabson L, Chheda S, Huang J, Kim H, Liu K, et al. CoRE MOF DB: a curated experimental metal-organic framework database with machine-learned properties for integrated material-process screening. Matter, 8 (2025), 102140.                        
- [Zeo++](https://www.sciencedirect.com/science/article/pii/S1387181111003738): T.F. Willems, C.H. Rycroft, M. Kazi, J.C. Meza, and M. Haranczyk, Algorithms and tools for high-throughput geometry- based analysis of crystalline porous materials, Microporous and Mesoporous Materials, 149 (2012), 134-141.                            
- [Heat capacity](https://doi.org/10.1038/s41563-022-01374-3): Models from Moosavi, S.M., Novotny, B.A., Ongari, D. et al.A data-science approach to predict the heat capacity of nanoporous materials. Nat. Mater. 21 (2022), 1419-1425.
- [Water stability](https://pubs.acs.org/doi/full/10.1021/jacs.4c05879): Terrones G G, Huang S P, Rivera M P, et al. Metal-organic framework stability in water and harsh environments from data-driven models trained on the diverse WS24 data set. Journal of the American Chemical Society, 146 (2024), 20333-20348.
- [Activation and thermal stability](https://pubs.acs.org/doi/full/10.1021/jacs.1c07217): Nandy A, Duan C, Kulik H J. Using machine learning and data mining to leverage community knowledge for the engineering of stable metal-organic frameworks. Journal of the American Chemical Society, 143 (2021), 17535-17547.
- [MOFid-v1](https://pubs.acs.org/doi/full/10.1021/acs.cgd.9b01050): Bucior B J, Rosen A S, Haranczyk M, et al. Identification schemes for metal-organic frameworks to enable rapid search and cheminformatics analysis. Crystal Growth & Design, 19 (2019), 6682-6697.
- [PACMAN-charge](https://pubs.acs.org/doi/10.1021/acs.jctc.4c00434): Zhao G, Chung Y G. PACMAN: A Robust Partial Atomic Charge Predicter for Nanoporous Materials Based on Crystal Graph Convolution Networks. Journal of Chemical Theory and Computation, 20 (2024), 5368-5380.
- [Revised Autocorrelation](https://pubs.acs.org/doi/10.1021/acs.jpca.7b08750): Jon Paul Janet and Heather J. Kulik. Resolving Transition Metal Chemical Space: Feature Selection for Machine Learning and Structure-Property Relationships. The Journal of Physical Chemistry A. 121 (2017), 8939-8954. 
- [Topology](https://doi.org/10.21468/SciPostChem.1.2.005): Zoubritzky L, Coudert F X. CrystalNets. jl: identification of crystal topologies. SciPost Chemistry, 1 (2022), 005.
- [Chen_Manz](https://doi.org/10.1039/D0RA02498H): Chen T, Manz T.A. Identifying misbonded atoms in the 2019 CoRE metal–organic framework database. RSC Adv, 10 (2025), 26944-26951.
- [MOFChecker](https://doi.org/10.1039/D5DD00109A): JIN X, Jablonka K, Moubarak E, Li Y, Smit B. MOFChecker: An algorithm for Validating and Correcting Metal-Organic Framework (MOF) Structures. Digital Discovery, 4 (2025), 1560-1569.
- [MOSAEC](https://pubs.acs.org/doi/10.1021/jacs.5c04914): White A, Gibaldi M, Burner J, Mayo RA, Woo T. High Structural Error Rates in "Computation-Ready" MOF Databases Discovered by Checking Metal Oxidation States. JACS, 147 (2025), 17579-17583.                                     
- [MOFClassifier](https://pubs.acs.org/doi/10.1021/jacs.5c10126): Zhao G, Zhao P, Chung Y. G. MOFClassifier: A Machine Learning Approach for Validating Computation-Ready Metal-Organic Frameworks. JACS, 147 (2025), 33343-33349.                         