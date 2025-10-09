from typing import Dict, List, Tuple, Union, Any

from .abstract import Engine, Aggregation
from ..utils import logger, pbar, dict_topk, load_singleton

from pathlib import Path

import torch
import pickle
import os
import time
import mmap



_plaidx_checkpoint_singletons: Dict[str, Tuple['Checkpoint', int]] = {}

def colbert_all_pair_scores(Q: torch.Tensor, D: torch.Tensor, Dm: torch.Tensor = None):
    assert len(Q.shape) == 3
    assert len(D.shape) == 3
    assert D.shape[-1] == Q.shape[-1]
    if Dm is not None:
        assert Dm.shape[1] == D.shape[1]
    dim = Q.shape[-1]

    x = (Q.to(D.dtype).view(-1, dim) @ D.view(-1, dim).T).view(-1, *D.shape[:2])
    if Dm is not None:
        x = torch.mul(x, Dm.squeeze(2).unsqueeze(0))
    return x.max(-1).values.view(*Q.shape[:2], -1).sum(1)


def _load_mapping(fn, containing_passage_id=True):
    if containing_passage_id:
        return [
            "_".join( line.strip().split("\t")[1].split("_")[:-1] )
            for line in pbar(open(fn))
        ] 
    else: 
        return [ 
            line.strip().split("\t")[1]
            for line in pbar(open(fn)) 
        ]

def _cumsum(arr):
    return [ sum(arr[:i+1]) for i in range(len(arr)) ]
    
def _keydict(x):
    return dict(enumerate(x))


class PLAIDX(Engine):

    def __init__(self, name: str = 'PLAID-X', config: Union[str, Path, Dict[str, Any]] = None, **kwargs):
        super().__init__(name, config, **kwargs)

        from colbert.infra import Run, RunConfig, ColBERTConfig
        from colbert import Searcher
        from colbert.search.index_storage import IndexScorer
        from colbert.modeling.checkpoint import Checkpoint
        from colbert.modeling.colbert import ColBERT

        # make sure ninja can load
        IndexScorer.try_load_torch_extensions(False)

        self.colbert_config = ColBERTConfig.load_from_index(self.index_path)
        if 'checkpoint' in self.config:
            self.colbert_config.checkpoint = self.config['checkpoint']
        
        checkpoint = PLAIDX._get_existing_checkpoint_instance(self.colbert_config.checkpoint)

        if checkpoint is not None:
            logger.info("===== Reuse model!")
        else: 
            ColBERT.try_load_torch_extensions(False) # make sure it is loaded
            checkpoint = Checkpoint(self.colbert_config.checkpoint, colbert_config=self.colbert_config)
            if config.get('use_gpu', False):
                checkpoint = checkpoint.half().to(device=f'cuda:{self.config.get("gpu_assignment", 0)}')
                checkpoint.compile()
            PLAIDX._cache_checkpoint_instance(self.colbert_config.checkpoint, checkpoint)

        # use_gpu = int(config.get('use_gpu', False)))

        self.passage_mapper = None
        if 'passage_mapping' in self.config:        
            self.passage_mapper = Aggregation(
                _load_mapping(self.config['passage_mapping'], self.config.get('mapping_containing_passage_id', True))
            )
        
        self.subset_mapper: Dict[str, str] = None
        if 'id_to_subset_mapping' in self.config:
            if self.config['id_to_subset_mapping'].endswith('.pkl'):
                self.subset_mapper = load_singleton(self.config['id_to_subset_mapping'])
            else:
                logger.warning(f"Unable to load subset mapping file {self.config['id_to_subset_mapping']}")

        # Time the actual loading
        start_time = time.time()

        with Run().context(RunConfig(index_root=self.index_path.parent, gpus=0)):
            logger.info(f"Loading PLAID-X index `{self.index_path}` and checkpoint `{self.colbert_config.checkpoint}`")
            self.searcher = Searcher(
                index=self.index_path.name, 
                checkpoint=checkpoint,
                load_collection=False
            )
        
        load_time = time.time() - start_time
        logger.info(f"COLBERT index loaded in {load_time:.2f} seconds")
        
        self.inference_batch_size = int(config.get('inference_batch_size', 32))
    
    def _apply_loading_optimizations(self):
        """Apply optimizations for faster loading."""
        # Set PyTorch threads
        torch.set_num_threads(min(12, os.cpu_count() or 1))
        torch.set_grad_enabled(False)
        
        # Enable MKL optimizations
        if torch.backends.mkl.is_available():
            torch.backends.mkl.enabled = True
        
        # CUDA optimizations
        if torch.cuda.is_available() and self.config.get('use_gpu', False):
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            torch.backends.cudnn.benchmark = True
            
            # Pre-allocate GPU memory
            if self.config.get('preallocate_gpu_memory', True):
                try:
                    torch.cuda.empty_cache()
                    torch.cuda.set_per_process_memory_fraction(0.9)
                except:
                    pass
        
        # Set environment variables for faster loading
        os.environ['OMP_NUM_THREADS'] = '12'
        os.environ['MKL_NUM_THREADS'] = '12'
        os.environ['TOKENIZERS_PARALLELISM'] = 'true'
    
    def __del__(self):
        if hasattr(self, 'searcher'):
            PLAIDX._delete_checkpoint_reference(self.searcher.checkpoint)

    @staticmethod
    def _get_existing_checkpoint_instance(checkpoint_path: str):
        global _plaidx_checkpoint_singletons
        abs_path = Path(checkpoint_path).absolute()
        if abs_path not in _plaidx_checkpoint_singletons:
            return None
        else:
            _plaidx_checkpoint_singletons[abs_path] = (
                _plaidx_checkpoint_singletons[abs_path][0],
                _plaidx_checkpoint_singletons[abs_path][1]+1
            )
            return _plaidx_checkpoint_singletons[abs_path][0]
    
    @staticmethod
    def _cache_checkpoint_instance(checkpoint_path: str, checkpoint: 'Checkpoint'):
        global _plaidx_checkpoint_singletons
        abs_path = Path(checkpoint_path).absolute()
        assert abs_path not in _plaidx_checkpoint_singletons
        _plaidx_checkpoint_singletons[abs_path] = (checkpoint, 1)
    
    @staticmethod
    def _delete_checkpoint_reference(checkpoint: 'Checkpoint'):
        global _plaidx_checkpoint_singletons
        for path in _plaidx_checkpoint_singletons:
            if _plaidx_checkpoint_singletons[path][0] == checkpoint:
                _plaidx_checkpoint_singletons[path] = (
                    _plaidx_checkpoint_singletons[path][0],
                    _plaidx_checkpoint_singletons[path][1]-1
                )
                if _plaidx_checkpoint_singletons[path][1] == 0:
                    del _plaidx_checkpoint_singletons[path]
                return 

    def filter_subset(self, scores: Dict[str, float], only_subset: str = None):
        if only_subset is None or self.subset_mapper is None:
            return scores
        return {
            doc_id: score
            for doc_id, score in scores.items()
            if self.subset_mapper[doc_id] == only_subset
        }

    async def search_batch(self, queries: List[str], limit: Union[int, List[int]] = 20, subsets: List[str] = None, maxp: bool = True) -> List[Dict[str, float]]:
        if isinstance(limit, int):
            limit = [int(limit*1.5)]*len(queries)
        
        if subsets is None:
            subsets = [None]*len(queries)

        Q = self.searcher.encode(queries)
        scores = []
        
        for query_idx, (k, sub) in enumerate(zip(limit, subsets)):
            # TODO: expose these settings into config
            if k <= 10:
                self.searcher.configure(ncells=1, centroid_score_threshold=0.5, ndocs=256)
            elif k <= 100:
                self.searcher.configure(ncells=2, centroid_score_threshold=0.45, ndocs=1024)
            else:
                self.searcher.configure(ncells=2, centroid_score_threshold=0.4, ndocs=2048)
                
            pids, q_scores = self.searcher.ranker.rank(self.searcher.config, Q[query_idx:query_idx+1])
            scores.append(dict(zip(pids, q_scores)))
            # s = dict((pid, score) for pid, _ , score in zip(*self.searcher.dense_search(Q[query_idx:query_idx+1], max(100, k*2))) )

        if not maxp or self.passage_mapper is None:
            return scores
        
        return [
            dict_topk(self.filter_subset(scores, subset), l)
            for subset, l, scores in zip(subsets, limit, map(self.passage_mapper.maxp, scores))
        ]
        
    @torch.inference_mode()
    async def score_batch(
            self, 
            queries: List[str], passages: List[str], 
            candidate_length: List[int]
        ) -> List[List[float]]:

        assert len(candidate_length) == len(queries)
        assert sum(candidate_length) == len(passages)
        offsets = _cumsum([0] + candidate_length)

        Q = self.searcher.checkpoint.queryFromText(queries)
        D, Dm = self.searcher.checkpoint.doc(
            *self.searcher.checkpoint.doc_tokenizer.tensorize(passages), keep_dims='return_mask'
        )

        return [
            colbert_all_pair_scores(Q[[i]], D[bidx:eidx], Dm[bidx:eidx]).cpu().tolist()[0]
            for i, (bidx, eidx) in enumerate(zip(offsets[:-1], offsets[1:]))
        ]