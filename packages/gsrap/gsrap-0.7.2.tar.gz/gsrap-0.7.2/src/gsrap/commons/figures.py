from io import BytesIO

import numpy as np
import pandas as pnd

from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, cut_tree, dendrogram, leaves_list

import matplotlib.pyplot as plt
from matplotlib.patches import Patch



def figure_df_C_F1(df_coverage):

    bin_matrix = df_coverage[[i for i in df_coverage.columns if i not in ['map_ids', 'modeled']]]
    strains = bin_matrix.columns
    bin_matrix = bin_matrix.T  # features in column

    # pdist() / linkage() will loose the accession information. So here we save a dict: 
    index_to_strain = {i: strain for i, strain in enumerate(bin_matrix.index)}

    # Calculate the linkage matrix using Ward clustering and Jaccard dissimilarity
    distances = pdist(bin_matrix, 'jaccard')
    linkage_matrix = linkage(distances, method='ward')


    # PART 0: create the frame
    fig, axs = plt.subplots(
        nrows=2, ncols=2, 
        figsize=(15, 10), 
        gridspec_kw={  # suplots width proportions. 
            'width_ratios': [0.5, 1.0],
            'height_ratios': [0.015, 0.985]
        }
    ) 

    # PART 1: dendrogram
    dn = dendrogram(
        linkage_matrix, ax=axs[1,0],
        orientation='left',
        color_threshold=0, above_threshold_color='black',
    )


    ### PART 2: heatmap
    ord_leaves = leaves_list(linkage_matrix)
    ord_leaves = np.flip(ord_leaves)  # because leaves are returned in the inverse sense.
    ord_leaves = [index_to_strain[i] for i in ord_leaves]  # convert index as number to index as accession
    bin_matrix = bin_matrix.loc[ord_leaves, :]  # reordered dataframe.
    axs[1,1].matshow(
        bin_matrix,  
        cmap='viridis',
        aspect='auto', # non-squared pixels to fit the axis
    )


    ### PART 3: coverage bar
    axs[0,1].matshow(
        df_coverage[['modeled']].T,  
        cmap='cool_r',
        aspect='auto', # non-squared pixels to fit the axis
    )


    ### PART 4: legends
    legend_feat = [
        Patch(facecolor=plt.colormaps.get_cmap('viridis')(0.0), edgecolor='black', label='Absent'),
        Patch(facecolor=plt.colormaps.get_cmap('viridis')(1.0), edgecolor='black', label='Probably present'),
    ]
    legend_cov = [
        Patch(facecolor=plt.colormaps.get_cmap('cool_r')(0.0), edgecolor='black', label='Not modeled'),
        Patch(facecolor=plt.colormaps.get_cmap('cool_r')(1.0), edgecolor='black', label='Modeled'),
    ]
    l1 = axs[1,0].legend(handles=legend_cov, title='Universe coverage', loc='upper left')
    l2 = axs[1,0].legend(handles=legend_feat, title='KEGG reaction in strain', loc='lower left')
    axs[1,0].add_artist(l1)  # keep both legends visible


    ### PART 5: aesthetics
    plt.subplots_adjust(wspace=0, hspace=0)  # adjust the space between subplots: 
    axs[0,0].axis('off')  # remove frame and axis
    axs[1,0].axis('off')  # remove frame and axis

    axs[0,1].yaxis.set_visible(False)  # remove ticks, tick labels, axis label

    axs[1,1].xaxis.set_ticks([])       # remove ticks
    axs[1,1].set_xticklabels([])       # remove tick labels
    axs[1,1].xaxis.set_label_position("bottom")
    axs[1,1].set_xlabel("KEGG reactions")

    axs[1,1].yaxis.set_ticks([])       # remove ticks
    axs[1,1].set_yticklabels([])       # remove tick labels
    axs[1,1].yaxis.set_label_position("right")
    axs[1,1].set_ylabel(f"{len(strains)} strains", rotation=270, labelpad=13)  # labelpad is in points (1 point = 1/72 inch)


    ### PART 6: save fig
    buf = BytesIO()
    fig.savefig(buf, dpi=300, bbox_inches='tight')  # labelpad is in inches (1 point = 1/72 inch)
    plt.close(fig)
    buf.seek(0)  # rewind the buffer to the beginning
    
    
    return buf
