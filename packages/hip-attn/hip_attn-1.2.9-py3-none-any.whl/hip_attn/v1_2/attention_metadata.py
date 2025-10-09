import copy
import os
import warnings
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Dict, List, Literal, Optional

import torch
from torch import Tensor

if TYPE_CHECKING:
    from hip_attn.v1_2.uvm_gpu_cache import HiPOffloadCache


HIP_DEBUG_ALLOW_GATHER_KV_CACHE = (
    os.getenv("HIP_DEBUG_ALLOW_GATHER_KV_CACHE", "0") == "1"
)


def safe_stride(x: Optional[Tensor], ndim: int):
    if x is None:
        return tuple(
            [
                0,
            ]
            * ndim
        )
    else:
        stride = x.stride()
        assert len(stride) == ndim
        return stride


@dataclass
class Stage:
    stage_block_size_q: int
    stage_block_stride_q: int
    stage_chunk_size: int
    stage_k: Optional[int]
    stage_stride: int

    require_realign_index: bool = False
    require_reset_score: bool = False
    require_post_sort: bool = False


@dataclass
class NopStage(Stage):
    require_realign_index: bool = True
    require_reset_score: bool = False
    require_post_sort: bool = True


@dataclass
class EvalScoreStage(Stage):
    block_chunk: int = 64
    stage_extend_backend: Optional[str] = None
    require_reset_score: bool = True
    require_post_sort: bool = True


@dataclass
class ScanStage(Stage):
    stage_extend_backend: Optional[str] = None
    using_landmark: Optional[bool] = None
    require_realign_index: bool = True
    require_reset_score: bool = True
    require_post_sort: bool = True


@dataclass
class EnsembleScoreStage(Stage):
    reduce_method: str = "sum"
    require_reset_score: bool = True
    require_post_sort: bool = True


StatKeys = Literal[
    "unique_access_count",
    "access_count",
    "cache_miss_count",
    "cache_hit_ratio",
]


@dataclass
class HiPAttentionCacheAccessStatistics:
    # [BSZ, HEAD_KV, MAX_TSRC]
    access_counter: Tensor
    # [BSZ, HEAD_KV, MAX_TSRC]
    cache_miss_counter: Tensor

    def compute_statistics(self) -> Dict[
        StatKeys,
        Tensor,
    ]:
        # FIXME: heejun
        if (os.getenv("HIP_DISABLE_COMPUTE_STATISTICS", "1") == "0") and (
            self.access_counter is not None
        ):
            unique_access_count = self.access_counter.clamp(0, 1).sum()
            access_counts = self.access_counter.sum()
            cache_miss_counts = self.cache_miss_counter.sum()
            cache_hit_ratio = 1 - (cache_miss_counts / access_counts)
        else:
            unique_access_count = None
            access_counts = None
            cache_miss_counts = None
            cache_hit_ratio = None

        return {
            "unique_access_count": unique_access_count,
            "access_count": access_counts,
            "cache_miss_count": cache_miss_counts,
            "cache_hit_ratio": cache_hit_ratio,
        }


@dataclass
class HiPAttentionStageInputCache:
    indices_left: Tensor
    indices_right: Tensor
    out_scores: Tensor


@dataclass
class HiPAttentionState:
    # [MAX_NUM_TOKENS, HEAD]
    landmark_scores: torch.Tensor
    # [NUM_STAGES, MAX_NUM_TOKENS // CHUNK_SIZE, K]
    landmark_indices: List[torch.Tensor]

    @classmethod
    def from_args(
        cls, q: torch.Tensor, args: "HiPAttentionArgs", k: Optional[torch.Tensor] = None
    ):
        if k is None:
            assert args.using_paged_cache

        if args.get_k_cache() is not None:
            k_cache = args.get_k_cache()
            num_tokens = k_cache.shape[0] * k_cache.shape[1]
        else:
            num_tokens = k.shape[1]

        num_tokens = max(args.extend_context_length, num_tokens)
        num_tokens = max(int(os.getenv("HIP_DEBUG_MAX_TOKENS", "0")), num_tokens)

        # padding for SGlang
        num_tokens += 1024

        num_heads = q.shape[2]
        landmark_scores = torch.zeros(
            (num_tokens, num_heads), dtype=torch.float32, device=q.device
        )

        return HiPAttentionState(
            landmark_scores=landmark_scores,
            landmark_indices=None,
        )


@dataclass
class HiPAttentionOutputMetadata:
    indices: Optional[Tensor]
    ks: Optional[Tensor]
    ks_count: Optional[Tensor]
    ks_start_end: Optional[Tensor]

    # memory access statistics
    mask_cache_statistics: Optional[HiPAttentionCacheAccessStatistics]
    sa_cache_statistics: Optional[HiPAttentionCacheAccessStatistics]

    # stage caches
    stage_caches: Optional[List[HiPAttentionStageInputCache]]

    state: Optional[HiPAttentionState] = None


@dataclass
class HiPAttentionArgs:
    position_ids: Optional[Tensor] = None

    sink_token_size: int = 256
    sliding_window_size: int = 512
    block_size_k: int = 64  # for optimization this will be BLOCK_CHUNK

    block_size_q: int = 64  # no effect, set automatically
    mask_k: int = 512  # no effect, set automatically

    second_stage_k: int = 2048
    stages: List[Stage] = field(
        default_factory=lambda: [
            ScanStage(
                stage_block_size_q=64,
                stage_block_stride_q=4,
                stage_chunk_size=256,
                stage_k=None,
                stage_stride=1,
            ),
            ScanStage(
                stage_block_size_q=64,
                stage_block_stride_q=4,
                stage_chunk_size=32,
                stage_k=32768,
                stage_stride=1,
            ),
            ScanStage(
                stage_block_size_q=64,
                stage_block_stride_q=1,
                stage_chunk_size=8,
                stage_k=8192,
                stage_stride=1,
            ),
        ]
    )
    model_context_length: int = 131072
    extend_context_length: int = 512 * 1024

    using_landmark: bool = field(
        default_factory=lambda: os.getenv("HIP_DEBUG_LANDMARK_BASED_SCAN_STAGE", "1")
        == "1"
    )
    landmark_stage_k: List[int] = field(default_factory=lambda: [1, 1, 1])

    # kernel args,
    mask_only: bool = False
    block_sparse_block_size_q: Optional[int] = 64
    v_hidden_dim: Optional[int] = None

    scan_early_terminate: int = 1
    stage_early_terminate: int = 1
    scan_extend_backend: str = "relative"
    sa_extend_backend: str = "streaming"
    low_percent: float = 0.0
    low_k_ratio: float = 1.0
    dim_to_lower: Literal["head", "seq"] = "head"
    q_mask: Optional[Tensor] = None
    k_mask: Optional[Tensor] = None
    idx_pca_hid_q: Optional[Tensor] = None
    idx_pca_hid_k: Optional[Tensor] = None

    is_causal: bool = True

    using_extend: bool = False
    need_apply_rope: bool = False
    rope_cos: Optional[Tensor] = None
    rope_sin: Optional[Tensor] = None
    rope_range: Optional[tuple[int, int]] = None
    rope_is_neox_style: Optional[bool] = None

    offload_cache: "Optional[HiPOffloadCache]" = None
    k_cache: Optional[Tensor] = None
    v_cache: Optional[Tensor] = None
    cache_seq_lens: Optional[Tensor] = None
    block_table: Optional[Tensor] = None

    # to support gemma2
    logit_softcap: Optional[float] = None

    online_update_cache: bool = False

    require_cache_statistics: bool = True
    require_stage_caches: bool = True

    disable_flashdecode: bool = False

    sliding_window_indices: Optional[torch.Tensor] = None

    using_chunked_sliding_window: bool = False

    # NOTE: use only for debugging purpose
    layer_id: int = 31

    query_for_landmark: Optional[Tensor] = None
    position_ids_for_landmark: Optional[Tensor] = None

    is_decode: bool = False

    bsa_return_running_statistics: bool = False
    bsa_sliding_window_size: int = -1

    k_descale: Optional[Tensor] = None
    v_descale: Optional[Tensor] = None

    self_extend_scale: int = 12
    self_extend_window: int = 4096

    softmax_sink: Optional[Tensor] = None

    def __post_init__(self):
        if self.rope_cos is not None and self.rope_cos.ndim == 3:
            self.rope_cos = self.rope_cos.view(-1, self.rope_cos.shape[-1])
            self.rope_sin = self.rope_sin.view(-1, self.rope_sin.shape[-1])
        # if self.q_quant is not None:
        #     assert self.q_quant.ndim == 4
        #     assert self.k_quant.ndim == 4
        if self.using_extend:
            assert self.model_context_length is not None
            assert self.extend_context_length is not None
        self.update_flags()

    def update_flags(self):
        if self.logit_softcap == 0:
            self.logit_softcap = None
        self.using_paged_cache = (self.k_cache is not None) or (
            self.offload_cache is not None
        )
        if self.using_paged_cache:
            if self.k_cache is not None:
                self.paged_cache_page_count = self.k_cache.shape[0]
                self.paged_cache_page_size = self.k_cache.shape[1]
            else:
                self.paged_cache_page_count = self.offload_cache.get_page_count()
                self.paged_cache_page_size = 1
            assert self.paged_cache_page_size in (1, 2, 4, 8, 16, 32)
        if self.logit_softcap == 0:
            self.logit_softcap = None

    def clone(self):
        self.update_flags()
        return copy.copy(self)

    def json(self, convert_tensor_to_meta=True):
        from dataclasses import fields

        json = {}
        for field in fields(self):
            json[field.name] = getattr(self, field.name)

        if convert_tensor_to_meta:
            for k, v in json.items():
                if isinstance(v, Tensor):
                    v = f"{v.dtype}{list(v.shape)}@{v.device}.{v.data_ptr():02X}"
                json[k] = v

        return json

    def args_extend(self):
        return (
            self.using_extend,
            self.need_apply_rope,
            *self.args_rope_cos(),
            *self.args_rope_sin(),
            self.rope_range[0],
            self.rope_range[1],
            self.rope_is_neox_style,
        )

    def args_rope_cos(self):
        return (
            self.rope_cos,
            *safe_stride(self.rope_cos, 2),
        )

    def args_rope_sin(self):
        return (
            self.rope_sin,
            *safe_stride(self.rope_sin, 2),
        )

    def args_paged_kv_cache(self, disable_cache: bool = False):
        using_page = self.using_paged_cache

        if disable_cache:
            return (
                False,
                1,
                None,
                0,
                0,
                0,
                0,
                None,
                0,
                0,
                0,
                0,
                None,
                0,
                0,
                None,
                0,
            )

        if self.offload_cache is None:
            if using_page:
                assert self.v_cache is not None
                assert self.k_cache.ndim == self.v_cache.ndim
                assert self.k_cache.ndim == 4
                assert self.block_table is not None
                assert self.block_table.ndim == 2
                assert self.cache_seq_lens is not None
                assert self.cache_seq_lens.ndim == 1
                page_size = self.k_cache.shape[1]
            else:
                page_size = 0

            return (
                using_page,
                page_size,
                self.k_cache,
                *safe_stride(self.k_cache, 4),
                self.v_cache,
                *safe_stride(self.v_cache, 4),
                self.block_table,
                *safe_stride(self.block_table, 2),
                self.cache_seq_lens,
                *safe_stride(self.cache_seq_lens, 1),
            )
        else:
            assert using_page

            k_cache = self.offload_cache.k_uvm.bank_gpu.unsqueeze(1)
            v_cache = self.offload_cache.v_uvm.bank_gpu.unsqueeze(1)

            return (
                True,
                1,
                k_cache,
                *safe_stride(k_cache, 4),
                v_cache,
                *safe_stride(v_cache, 4),
                self.block_table,
                *safe_stride(self.block_table, 2),
                self.cache_seq_lens,
                *safe_stride(self.cache_seq_lens, 1),
            )

    def args_offload_cache(self, is_masking, disable_cache: bool = False):
        if self.offload_cache and (not disable_cache):
            gpu_cache = (
                self.offload_cache.mask_k_cache
                if is_masking
                else self.offload_cache.sa_kv_cache
            )
            is_packed = gpu_cache.kv_packed
            uvm_metadata = self.offload_cache.k_uvm.metadata
            return (
                True,
                is_packed,
                gpu_cache.bank.shape[0],
                uvm_metadata,
                *safe_stride(uvm_metadata, 2),
                gpu_cache.global_metadata,
                *safe_stride(gpu_cache.global_metadata, 2),
                gpu_cache.bank,
                *safe_stride(gpu_cache.bank, 2),
                gpu_cache.metadata,
                *safe_stride(gpu_cache.metadata, 2),
                gpu_cache.table,
                *safe_stride(gpu_cache.table, 3),
            )
        else:
            return (
                False,
                False,
                0,
                None,
                0,
                0,
                None,
                0,
                0,
                None,
                0,
                0,
                None,
                0,
                0,
                None,
                0,
                0,
                0,
            )

    def get_k_cache(self):
        if self.k_cache is not None:
            k_cache = self.k_cache
        elif self.offload_cache is not None:
            k_cache = self.offload_cache.k_uvm.bank_gpu.unsqueeze(1)
        else:
            k_cache = None

        # k_cache: [MAX_TOKENS, 1, HEAD, HID]
        return k_cache

    def get_v_cache(self):
        if self.v_cache is not None:
            v_cache = self.v_cache
        elif self.offload_cache is not None:
            v_cache = self.offload_cache.v_uvm.bank_gpu.unsqueeze(1)
        else:
            v_cache = None

        # v_cache: [MAX_TOKENS, 1, HEAD, HID]
        return v_cache

    def gather_extend_k_from_paged_cache(
        self,
        disable_gqa=False,
        gqa_q: torch.Tensor = None,
        position_ids: torch.Tensor = None,
    ):
        k_cache = self.get_k_cache()
        # self.block_table[BLOCK_TABLE_BSZ, MODEL_SEQ_LEN]
        assert self.block_table is not None
        if position_ids is None:
            position_ids = self.position_ids
        assert position_ids is not None
        assert (
            position_ids.shape[0] == self.block_table.shape[0]
        ), f"{position_ids.shape} == {self.block_table.shape}"
        # k_cache: [T, HEAD, HID]
        k = k_cache[:, 0, :, :][self.block_table.gather(dim=1, index=position_ids)]
        if gqa_q is not None:
            B, T, H, D = gqa_q.shape
            assert k.shape == (B, T, k.shape[2], D), f"{gqa_q.shape} {k.shape}"
        if disable_gqa:
            k = k.repeat_interleave(gqa_q.shape[2] // k.shape[2], dim=2)
        return k

    def gather_k_from_paged_cache(
        self,
        chunk_size: int = 1,
        disable_gqa=False,
        gqa_q: torch.Tensor = None,
        seq_len: int = None,
    ):
        if not HIP_DEBUG_ALLOW_GATHER_KV_CACHE:
            raise Exception(
                "Please set HIP_DEBUG_ALLOW_GATHER_KV_CACHE=1 for allow this behavior"
            )
        else:
            # warnings.warn("For developers: gathering paged cache will occure overhead.")
            pass

        k_cache = self.get_k_cache()
        assert self.block_table is not None

        if seq_len is None:
            seq_len = self.block_table.shape[1]

        is_fp8 = k_cache.dtype in (torch.float8_e5m2, torch.float8_e4m3fn)
        index_dtype = torch.uint8 if is_fp8 else k_cache.dtype

        k = k_cache.view(index_dtype)[:, 0, :, :][
            self.block_table[
                :,
                : seq_len - (seq_len % chunk_size),
            ]
        ].view(k_cache.dtype)
        if disable_gqa:
            k = k.repeat_interleave(gqa_q.shape[2] // k.shape[2], dim=2)
        return k

    def gather_v_from_paged_cache(
        self,
        chunk_size: int = 1,
        disable_gqa: bool = False,
        gqa_q: torch.Tensor = None,
        seq_len: int = None,
    ):
        if not HIP_DEBUG_ALLOW_GATHER_KV_CACHE:
            raise Exception(
                "Please set HIP_DEBUG_ALLOW_GATHER_KV_CACHE=1 for allow this behavior"
            )
        else:
            # warnings.warn("For developers: gathering paged cache will occure overhead.")
            pass

        if self.v_cache is not None:
            assert self.v_cache is not None
            v_cache = self.v_cache
        else:
            v_cache = self.offload_cache.v_uvm.bank_gpu.unsqueeze(1)

        assert self.block_table is not None

        if seq_len is None:
            seq_len = self.block_table.shape[1]

        is_fp8 = v_cache.dtype in (torch.float8_e5m2, torch.float8_e4m3fn)
        index_dtype = torch.uint8 if is_fp8 else v_cache.dtype

        v = v_cache.view(index_dtype)[:, 0, :, :][
            self.block_table[
                :,
                : seq_len - (seq_len % chunk_size),
            ]
        ].view(v_cache.dtype)
        if disable_gqa:
            v = v.repeat_interleave(gqa_q.shape[2] // v.shape[2], dim=2)
        return v

    def pretty(self) -> str:
        json = asdict(self)
        for k, v in json.items():
            if isinstance(v, torch.Tensor):
                json[k] = f"{v.dtype}{list(v.shape)}@{str(v.device)}"
        return str(json)
