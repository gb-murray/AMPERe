# AMPERe - Adaptive Melt Pool Edge Recognition

AMPERe is a machine-learning tool for semantically segmenting the key features of LPBF melt pools from x-ray images. It can be used in an OpenMSI stream processer or as an independent processing tool. 

AMPERe utilizes a combination of `scikit image`  open source computer-vision and Meta's Detectron2 implementation of Mask R-CNN to segment images. 

# TO-DO
* Integrate stream processor
* Slim down docker environment
* Migrate model and trainer from Colab
* Update docs for general use, training instructions, implementation
* Organize citations
* Remove deprecated and unused files

# Citations

[1]  Wang, R., Garcia, D., Kamath, R.R. et al. 
    In situ melt pool measurements for laser powder bed fusion using multi sensing and correlation analysis. Sci Rep 12, 13716 (2022). 
    https://doi.org/10.1038/s41598-022-18096-w

[2] Marc-André Nielsen, Johann Flemming Gloy, Dieter Lott, Tao Sun, Martin Müller, Peter Staron,
    Automatic melt pool recognition in X-ray radiography images from laser-molten Al alloy,
    Journal of Materials Research and Technology, Volume 21, 2022, Pages 3502-3513, ISSN 2238-7854,
    https://doi.org/10.1016/j.jmrt.2022.10.121.
    
[3]  Corvellec M. and Becker C. G. (2021, May 17-18)
    "Quantifying solidification of metallic alloys with scikit-image"
    [Conference presentation]. BIDS ImageXD 2021 (Image Analysis Across
    Domains). Virtual participation.
    https://www.youtube.com/watch?v=cB1HTgmWTd8
