import os
import math
import pandas as pd
import numpy as np
import ndex2
from cellmaps_utils import music_utils
from cellmaps_utils import constants
from cellmaps_generate_hierarchy.exceptions import CellmapsGenerateHierarchyError


class PPINetworkGenerator(object):
    """
    Base class for objects that generate
    Protein to Protein interaction networks
    """

    def __init__(self):
        """
        Constructor
        """
        pass

    def get_next_network(self):
        """
        Gets next protein to protein interaction network

        :return: Network
        :rtype: :py:class:`ndex2.nice_cx_network.NiceCXNetwork`
        """
        raise NotImplementedError('subclasses need to implement')


class CosineSimilarityPPIGenerator(PPINetworkGenerator):
    """
    Takes Embedding file of format:

    .. code-block::

        ID # # # #

    Where ID is gene and #'s is embedding vector
    """
    PPI_CUTOFFS = [0.001, 0.002, 0.003, 0.004, 0.005, 0.006,
                   0.007, 0.008, 0.009, 0.01, 0.02, 0.03,
                   0.04, 0.05, 0.10]

    def __init__(self, embeddingdirs=[],
                 cutoffs=PPI_CUTOFFS):
        """
        Constructor
        """
        super().__init__()
        if embeddingdirs is None or len(embeddingdirs) < 1:
            raise CellmapsGenerateHierarchyError('embeddingdir is None')

        self._embeddingdirs = embeddingdirs
        self._cutoffs = cutoffs

    def _get_ppi_dataframe(self):
        """

        :return:
        """
        sim_mats = []
        index = []

        for fold, embeddingdir in enumerate(self._embeddingdirs):
            embeddingfile = os.path.join(embeddingdir, constants.CO_EMBEDDING_FILE)
            if os.path.exists(os.path.join(embeddingdir, constants.PPI_EMBEDDING_FILE)):
                embeddingfile = os.path.join(embeddingdir, constants.PPI_EMBEDDING_FILE)
            elif os.path.exists(os.path.join(embeddingdir, constants.IMAGE_EMBEDDING_FILE)):
                embeddingfile = os.path.join(embeddingdir, constants.IMAGE_EMBEDDING_FILE)

            z = pd.read_table(embeddingfile, sep='\t', index_col=0)

            # give the same ordering
            if len(index) == 0:
                index = z.index.values
            else:
                try:
                    z = z.loc[index]
                except KeyError:
                    index_set = set(index)
                    fold_set = set(z.index.values)
                    missing_in_current_fold = index_set.difference(fold_set)
                    extra_in_current_fold = fold_set.difference(index_set)
                    error_message = (
                        f"Discrepancy in protein sets across embedding folds detected. "
                        f"Proteins present in fold 1 but absent in fold {fold + 1}: {missing_in_current_fold}. "
                        f"Proteins present in fold {fold + 1} but absent in fold 1: {extra_in_current_fold}."
                    )
                    raise CellmapsGenerateHierarchyError(error_message)

            sim_mat = music_utils.cosine_similarity_scaled(z)
            keep = np.triu(np.ones(sim_mat.shape)).astype(bool)
            sim_mat = sim_mat.where(keep)
            sim_mats.append(sim_mat)

        # take mean across folds
        sim_mat = pd.DataFrame(np.array(sim_mats).mean(axis=0), index=index, columns=index)

        pairs = sim_mat.stack().reset_index().rename(columns={'level_0': constants.PPI_EDGELIST_GENEA_COL,
                                                              'level_1': constants.PPI_EDGELIST_GENEB_COL,
                                                              0: constants.WEIGHTED_PPI_EDGELIST_WEIGHT_COL})

        pairs = pairs[pairs[constants.PPI_EDGELIST_GENEA_COL] != pairs[constants.PPI_EDGELIST_GENEB_COL]]
        return pairs.sort_values(constants.WEIGHTED_PPI_EDGELIST_WEIGHT_COL, ascending=False)

    def get_next_network(self):
        """
        Gets all the edges

        :param cutoff: Fraction of top edges to keep
                       0.01 means 1% 0.5 means 50%
        :type cutoff: float
        :return: Network
        :rtype: :py:class:`ndex2.nice_cx_network.NiceCXNetwork`
        """
        df = self._get_ppi_dataframe()
        for cutoff in self._cutoffs:
            df_cutoff = df.iloc[0:math.ceil(cutoff * len(df))]
            net = ndex2.create_nice_cx_from_pandas(df_cutoff,
                                                   source_field=constants.PPI_EDGELIST_GENEA_COL,
                                                   target_field=constants.PPI_EDGELIST_GENEB_COL,
                                                   edge_attr=[constants.WEIGHTED_PPI_EDGELIST_WEIGHT_COL])
            net.set_name('parent interactome with ' + str(cutoff) + ' cutoff')
            net.set_network_attribute(name='description',
                                      values='Protein to Protein Interaction\n'
                                             'network generated by cellmaps_generate_hierarchy\n'
                                             'tool where top ' +
                                             str(round(cutoff * 100.0)) +
                                             '% of interactions sorted by weight\n')
            net.set_network_attribute(name='cutoff', values=str(cutoff))
            yield net
