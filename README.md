# CMIP6 replication


## Overview

CMIP6 replication planing related information and tools.
See the [CMIP6 replication planing document](https://docs.google.com/document/d/1JvO9ezLeiRDiL9zB1hDqW7wm5K1lAXn7Q1EYNQB2jJc/edit) for an overview.

## Organization of repo

* **communication**: CMIP6 replication related documents, etc. 
* **selection_files**: synda selection files for ESGF data replication
   * **CORE**: core CMIP6 data collection
   * **CEDA, DKRZ, IPSL, LLNL,NCI**: priority data collection at T1 center
   * **TEST**: data collections for replication testing 
* **util**: various tools supporting e.g. automatic synda selection file generation
   * **MakeSelectionFiles**: tool to generate selection files based on CMIP6_CVs and user input
   * **data**: various lists, e.g. most oftenly used variables in CMIP6 (based on IPCC-WDC access statistics)
* .. 
   
