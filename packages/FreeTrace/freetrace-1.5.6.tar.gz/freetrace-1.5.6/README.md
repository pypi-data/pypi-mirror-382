
![Static Badge](https://img.shields.io/badge/%3E%3D3.10-1?style=flat&label=Python&color=blue)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13336251.svg)](https://doi.org/10.5281/zenodo.13336251)
![GitHub License](https://img.shields.io/github/license/JunwooParkSaribu/FreeTrace)
## FreeTrace

> [!IMPORTANT]  
> Requirements </br>
> - Windows(10/11) / GNU/Linux(Debian/Ubuntu) / MacOS(Sequoia/Tahoe)</br>
> - C compiler (clang)</br>
> - Python3.10 &#8593;</br>
> - GPU & Cuda12 on GNU/Linux with pre-trained [models](https://github.com/JunwooParkSaribu/FreeTrace/blob/main/FreeTrace/models/README.md) (recommended)</br>


> [!NOTE]  
> - PRE-REQUISITE: pre-installation and compilation, check [tutorial](https://github.com/JunwooParkSaribu/FreeTrace/blob/main/tutorial.ipynb). </br>
> - Check [compatibilities](https://github.com/JunwooParkSaribu/FreeTrace/blob/main/FreeTrace/models/README.md) of Python and Tensorflow to run FreeTrace with source code.</br>
> - Without GPU, FreeTrace is slow if it infers under fractional Brownian motion.</br>
> - Current version is stable with python 3.10 / 3.11 / 3.12</br>


&nbsp;&nbsp;<b>FreeTrace</b> infers individual trajectories from time-series images. To detect the particles and their positions at sub-pixel level, FreeTrace first extends the image sequences by sampling noises at the edges of images. These extensions of images allow detecting the particles at the edges of images since FreeTrace utilises sliding windows to calculate the particle's position at sub-pixel level. Next, FreeTrace estimates the existence of particles at a pixel with a given PSF function for each sliding window and makes a hypothesis map to determine whether a particle exists at a given sliding window or not. FreeTrace then finds local maxima from the constructed hypothesis maps. To find the precise centre-position of particles at sub-pixel level, FreeTrace performs 2D Gaussian regression by transforming it into a linear system. Finally, FreeTrace reconnects the detected particles by constructing a network and infer the most probable trajectories by calculating the reconnection-likelihoods on paths.</br>

<h2>Visualized result of FreeTrace</h2>
<img width="825" src="https://github.com/JunwooParkSaribu/FreeTrace/blob/main/tmps/stars.gif">
<table border="0"> 
        <tr> 
            <td><img src="https://github.com/JunwooParkSaribu/FreeTrace/blob/main/tmps/trjs0.gif" width="230" height="230"></td> 
            <td><img src="https://github.com/JunwooParkSaribu/FreeTrace/blob/main/tmps/trjs1.gif" width="230" height="230"></td>
            <td><img src="https://github.com/JunwooParkSaribu/FreeTrace/blob/main/tmps/trjs2.gif" width="285" height="230"></td>
        </tr>  
</table>

[Brief description of the method] will be available soon.

<h3> Contact person </h3>

<junwoo.park@sorbonne-universite.fr>

<h3> Contributors </h3>

> If you use this software, please cite it as below. </br>
```
@software{FreeTrace,
    author = {Park, Junwoo and Sokolovska, Nataliya and Cabriel, Clément and Izeddin, Ignacio and Miné-Hattab, Judith},
    title = {FreeTrace},
    year = {2024},
    doi = {10.5281/zenodo.13336251},
    publisher = {Zenodo},
}
```
<br>
