# A minimal version of TIDE
Numpy is the only dependency of this library. 
To achieve this, the coco datasets and plotting features were removed.
The core funcionality is the same as in *dbolya/tide*.


# A General **T**oolbox for **I**dentifying Object **D**etection **E**rrors
```
████████╗██╗██████╗ ███████╗
╚══██╔══╝██║██╔══██╗██╔════╝
   ██║   ██║██║  ██║█████╗  
   ██║   ██║██║  ██║██╔══╝  
   ██║   ██║██████╔╝███████╗
   ╚═╝   ╚═╝╚═════╝ ╚══════╝
```

An easy-to-use, general toolbox to compute and evaluate the effect of object detection and instance segmentation on overall performance. This is the code for our paper: [TIDE: A General Toolbox for Identifying Object Detection Errors](https://dbolya.github.io/tide/paper.pdf) ([ArXiv](https://arxiv.org/abs/2008.08115)) [ECCV2020 Spotlight].

Check out our ECCV 2020 short video for an explanation of what TIDE can do:

[![TIDE Introduction](https://img.youtube.com/vi/McYFYU3PXcU/0.jpg)](https://youtu.be/McYFYU3PXcU)

# Installation

This fork contains a light version which only depends on numpy. 
To achieve this, the coco datasets and most reporting features were removed.
It is available on [PyPi](https://pypi.org/project/tidecv-light/) as well.
Install with pip:
```shell
pip3 install tidecv-light
```

# Usage
TIDE is meant as a drop-in replacement for the [COCO Evaluation toolkit](https://github.com/cocodataset/cocoapi), and getting started is easy:

```python
from tidecv import TIDE, datasets

tide = TIDE()
tide.evaluate(datasets.COCO(), datasets.COCOResult('path/to/your/results/file'), mode=TIDE.BOX) # Use TIDE.MASK for masks
tide.summarize()  # Summarize the results as tables in the console.
```

This prints evaluation summary tables to the console:
```
-- mask_rcnn_bbox --

bbox AP @ 50: 61.80

                         Main Errors
=============================================================
  Type      Cls      Loc     Both     Dupe      Bkg     Miss
-------------------------------------------------------------
   dAP     3.40     6.65     1.18     0.19     3.96     7.53
=============================================================

        Special Error
=============================
  Type   FalsePos   FalseNeg
-----------------------------
   dAP      16.28      15.57
=============================
```


## Jupyter Notebook

Check out the [example notebook](https://github.com/dbolya/tide/blob/master/examples/coco_instance_segmentation.ipynb) for more details.


# Datasets
The currently supported datasets are COCO, LVIS, Pascal, and Cityscapes. More details and documentation on how to write your own database drivers coming soon!

# Citation
If you use TIDE in your project, please cite
```
@inproceedings{tide-eccv2020,
  author    = {Daniel Bolya and Sean Foley and James Hays and Judy Hoffman},
  title     = {TIDE: A General Toolbox for Identifying Object Detection Errors},
  booktitle = {ECCV},
  year      = {2020},
}
```

## Contact
For questions about our paper or code, make an issue in this github or contact [Daniel Bolya](mailto:dbolya@gatech.edu). Note that I may not respond to emails, so github issues are your best bet.
