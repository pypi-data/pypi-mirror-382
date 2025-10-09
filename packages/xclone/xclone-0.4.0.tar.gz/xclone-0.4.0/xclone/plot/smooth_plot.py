"""Base functions for XClone smoothing plotting
"""

# Author: Rongting Huang
# Date: 2022/07/26
# update: 2022/07/26


from ._data import reorder_data_by_cellanno
from ._base_xanndata import Xheatmap, XXheatmap

import gc

## Visualization part in smoothing performance
def raw_ratio_visualization(Xdata, cell_anno_key = "cell_type",
                            Xlayer = "RDR_smooth", vmin=-0.7, vmax=0.7,
                            colorbar_name = "RDR raw ratio (log)", 
                            **kwargs):
    """
    """
    re_Xdata = reorder_data_by_cellanno(Xdata, cell_anno_key = cell_anno_key)
    Xheatmap(re_Xdata, Xlayer = Xlayer, cell_anno_key = cell_anno_key, 
            vmin=vmin, vmax=vmax,
            colorbar_name = colorbar_name, **kwargs)
    
    del re_Xdata
    gc.collect()

def smooth_visualization(Xdata, cell_anno_key = "cell_type", 
                         Xlayer = "RDR_smooth", vmin=-0.7, vmax=0.7,
                         colorbar_name = "RDR smooth", 
                         **kwargs):
    """
    RENAME TO `RDR_smooth_visualization`.
    """
    re_Xdata = reorder_data_by_cellanno(Xdata, cell_anno_key = cell_anno_key)
    Xheatmap(re_Xdata, Xlayer = Xlayer, cell_anno_key = cell_anno_key, 
            vmin=vmin, vmax=vmax,
            colorbar_ticks = [vmin, 0, vmax], 
            colorbar_label = ["copy loss",  "copy neutral",  "copy gain"], 
            colorbar_name = colorbar_name, **kwargs)
    del re_Xdata
    gc.collect()

def RDR_smooth_visualization(Xdata, cell_anno_key = "cell_type", 
                             Xlayer = "RDR_smooth", vmin=-0.7, vmax=0.7, 
                             colorbar_name = "RDR smooth (log)", reorder = True, **kwargs):
    """
    """
    # add an option for reorder the adata or not.[next step for improvement]
    if reorder:
        re_Xdata = reorder_data_by_cellanno(Xdata, cell_anno_key = cell_anno_key)
        Xheatmap(re_Xdata, Xlayer = Xlayer, cell_anno_key = cell_anno_key, 
                vmin=vmin, vmax=vmax,
                colorbar_name = colorbar_name, **kwargs)
        del re_Xdata
        gc.collect()
    else:
         Xheatmap(Xdata, Xlayer = Xlayer, cell_anno_key = cell_anno_key, 
                vmin=vmin, vmax=vmax,
                colorbar_name = colorbar_name, **kwargs)

        


def smooth_visualization2(Xdata, cell_anno_key = ["cell_type", "Clone"],
                          clusters_display_name = ["Celltype", "Clone"],
                          Xlayer = "RDR_smooth",vmin=-0.7, vmax=0.7, 
                          colorbar_name = "RDR smooth (log)", **kwargs):
    """
    can setting colorbar;
    XXheatmap
    """
    re_Xdata = reorder_data_by_cellanno(Xdata, cell_anno_key =cell_anno_key)
    XXheatmap(re_Xdata, Xlayer = Xlayer, cell_anno_key = cell_anno_key, 
              clusters_display_name = clusters_display_name,
              vmin=vmin, vmax=vmax, 
              colorbar_name = colorbar_name, **kwargs)
    del re_Xdata
    gc.collect()

def RDR_smooth_complex_visualization(Xdata, cell_anno_key = ["cell_type", "Clone"],
                          clusters_display_name = ["Celltype", "Clone"],
                          Xlayer = "RDR_smooth", vmin=-0.7, vmax=0.7, 
                          colorbar_name = "RDR smooth (log)", **kwargs):
    """
    update from `smooth_visualization3`
    default: change color_bar

    """
    re_Xdata = reorder_data_by_cellanno(Xdata, cell_anno_key =cell_anno_key)
    XXheatmap(re_Xdata, Xlayer = Xlayer, cell_anno_key = cell_anno_key, 
              clusters_display_name = clusters_display_name,
              vmin=vmin, vmax=vmax, colorbar_ticks = [vmin, 0, vmax], 
              colorbar_name = colorbar_name,
              colorbar_label = ["copy loss",  "copy neutral",  "copy gain"],
              **kwargs)
    del re_Xdata
    gc.collect()


def BAF_smooth_visualization(Xdata, cell_anno_key = "cell_type", 
                             Xlayer = "phased_KNN_smoothed", 
                             colorbar_name = "BAF smooth",
                             **kwargs):
    """
    """
    re_Xdata = reorder_data_by_cellanno(Xdata, cell_anno_key = cell_anno_key)
    Xheatmap(re_Xdata, Xlayer = Xlayer, 
             cell_anno_key = cell_anno_key, center = 0.5, cmap="vlag", 
             colorbar_name = colorbar_name, **kwargs)
    del re_Xdata
    gc.collect()

def BAF_smooth_complex_visualization(Xdata,
                                     cell_anno_key = ["cluster", "cell_type"],
                                     clusters_display_name = ["Clone", "Celltype"],
                                     Xlayer = "phased_KNN_smoothed", 
                                     colorbar_name = "BAF smooth",
                                     **kwargs):
    """
    """
    re_Xdata = reorder_data_by_cellanno(Xdata, cell_anno_key = cell_anno_key)
    XXheatmap(re_Xdata, Xlayer = Xlayer, 
             cell_anno_key = cell_anno_key, 
             clusters_display_name = clusters_display_name,
             center = 0.5, cmap="vlag", 
             colorbar_name = colorbar_name, **kwargs)
    del re_Xdata
    gc.collect()