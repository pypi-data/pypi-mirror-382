"""XClone analysis.
"""

from .extract import dir_make
from .extract import extract_xclone_matrix

from .evaluation import prob_adata_generate

from .evaluation import extract_Xdata, extract_Xdata1
from .evaluation import Ground_truth_mtx_generate
from .evaluation import load_ground_truth, resort_Ground_truth_mtx
from .evaluation import base_evaluate_map, roc_auc_evaluate, fast_evaluate
from .evaluation import base_evaluate_map1

from .evaluation import get_confusion, get_confuse_mat_df

from .evaluation import change_res_resolution

from ._clustering import XClustering, Cluster_mapping
from ._clustering import XClustering2

from ._spatial import CalculateSampleCNVProb, CalculateSampleBAF, CalculateSampleRDR
from ._spatial import spatial_analysis

from ._quickanalysis import exploreClustering, OnestopBAFClustering

from .benchmark import extract_numbat