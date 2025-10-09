import math
import os
import warnings
from typing import Optional

import cv2
import numba
import numba.cuda
import numpy as np
import torch
import triton
import triton.language as tl
from matplotlib import pyplot as plt
from torch import Tensor

from hip_attn.utils.rope import adjust_rope
from hip_attn.v1_2.attention_decode_bsa import decode_block_sparse_attention
from hip_attn.v1_2.attention_extend_bsa import block_sparse_attention
from hip_attn.v1_2.attention_extend_bsa_tilelang import block_sparse_attention_tilelang
from hip_attn.v1_2.attention_metadata import (
    EnsembleScoreStage,
    EvalScoreStage,
    HiPAttentionArgs,
    HiPAttentionCacheAccessStatistics,
    HiPAttentionOutputMetadata,
    HiPAttentionStageInputCache,
    HiPAttentionState,
    NopStage,
    ScanStage,
    safe_stride,
)
from hip_attn.v1_2.compute_scores_landmark import compute_scores_landmark
from hip_attn.v1_2.compute_v_cos import compute_v_cos
from hip_attn.v1_2.eval_stage import calculate_chunk_score
from hip_attn.v1_2.landmark_sample import landmark_sample
from hip_attn.v1_2.scan_stage import chunk_controllable_sampling_mask
from hip_attn.v1_2.stage_prologue import stage_prologue

try:
    import torch.distributed as dist
    from sglang.srt.distributed import (
        get_tensor_model_parallel_rank,
        get_tensor_model_parallel_world_size,
        model_parallel_is_initialized,
        split_tensor_along_last_dim,
        tensor_model_parallel_all_gather,
        tensor_model_parallel_all_reduce,
    )

    SGLANG_DIST_ACTIVATED = True
except ImportError as ex:
    SGLANG_DIST_ACTIVATED = False


def get_local_rank() -> int:
    if SGLANG_DIST_ACTIVATED:
        if not model_parallel_is_initialized():
            return 0
        return get_tensor_model_parallel_rank()
    else:
        return 0


def get_world_size() -> int:
    if SGLANG_DIST_ACTIVATED:
        if not model_parallel_is_initialized():
            return 1
        return get_tensor_model_parallel_world_size()
    else:
        return 1


DEFAULT_VALUE_HIP_HEAD_REDUCE = "1"

_NUM_STREAMING_MULTIPROCESSOR = None


def num_streaming_multiprocessor():
    global _NUM_STREAMING_MULTIPROCESSOR
    if _NUM_STREAMING_MULTIPROCESSOR is None:
        _NUM_STREAMING_MULTIPROCESSOR = (
            numba.cuda.get_current_device().MULTIPROCESSOR_COUNT
        )
    return _NUM_STREAMING_MULTIPROCESSOR


def get_block_sparse_backend(
    q: torch.Tensor,
    disable_flashdecode: HiPAttentionArgs,
) -> type(block_sparse_attention):
    # return block_sparse_attention_tilelang

    block_sparse_attention_backend = block_sparse_attention

    # Use flashdecode
    # print(q.shape, int(os.getenv("HIP_FLASHDECODE_THRESH", "32")), (not os.environ.get("HIP_DISABLE_FLASHDECODE", "0") == "1"), (not args.disable_flashdecode))
    if (
        (q.shape[1] < int(os.getenv("HIP_FLASHDECODE_THRESH", "32")))
        and (not os.environ.get("HIP_DISABLE_FLASHDECODE", "0") == "1")
        and (not disable_flashdecode)
    ):
        block_sparse_attention_backend = decode_block_sparse_attention

    return block_sparse_attention_backend


@numba.njit(parallel=True)
def render_plot(out_indices_cpu, debug, DEBUG_HEAD, BLOCK_SIZE_Q):
    for i in numba.prange(out_indices_cpu.shape[1]):
        for j in range(out_indices_cpu.shape[-1]):
            # if j >= out_indices_cpu.shape[-1]: continue
            t = out_indices_cpu[0, i, DEBUG_HEAD, j] // BLOCK_SIZE_Q
            debug[i, t : t + 1] = 1


@numba.njit(parallel=True)
def render_plot_dynamic(
    out_indices_cpu,
    debug,
    DEBUG_HEAD,
    BLOCK_SIZE_Q,
    stage_k,
    chunk_size,
    causal_mask=False,
    sliding_window_size=0,
):
    for i in numba.prange(out_indices_cpu.shape[1]):
        for j in range(math.ceil(stage_k / chunk_size)):
            if j >= out_indices_cpu.shape[-1]:
                continue
            t = out_indices_cpu[0, i, DEBUG_HEAD, j] // BLOCK_SIZE_Q
            if causal_mask and ((t + sliding_window_size // BLOCK_SIZE_Q) >= i):
                continue
            tt = t + math.ceil(chunk_size / BLOCK_SIZE_Q)
            if causal_mask:
                tt = min(tt, i + 1)
            debug[i, t:tt] = 1


@numba.njit(parallel=True)
def render_plot_sampled(
    out_indices_cpu,
    debug,
    DEBUG_HEAD,
    BLOCK_CHUNK,
    chunk_count,
    TDST,
    sink_token_size,
):
    for i in numba.prange(out_indices_cpu.shape[1]):
        t_chunk_size = math.ceil(TDST / chunk_count * BLOCK_CHUNK)
        # print(i, t_chunk_size)
        for j in range(max(0, out_indices_cpu.shape[-1])):
            if j >= out_indices_cpu.shape[-1]:
                continue
            t = (
                out_indices_cpu[0, i, DEBUG_HEAD, j] - sink_token_size
            ) // BLOCK_CHUNK + sink_token_size // BLOCK_CHUNK
            t = t // t_chunk_size * t_chunk_size
            debug[i, t : t + t_chunk_size] = 1


@numba.njit(parallel=True)
def render_plot_ks(indices, ks, debug, DEBUG_HEAD, BLOCK_SIZE_Q):
    for i in numba.prange(indices.shape[1]):
        k = ks[DEBUG_HEAD, i]
        for j in range(indices.shape[-1]):
            if j >= k:
                continue
            t = indices[DEBUG_HEAD, i, j] // BLOCK_SIZE_Q
            debug[i, t : t + 1] = 1


DEBUG = os.getenv("HIP_DEBUG", "0") == "1"
DEBUG_LOGALL = os.getenv("HIP_DEBUG_LOGALL", "0") == "1"
__logall_index = 0
DEBUG_RENDER = os.getenv("HIP_DEBUG_RENDER", "1") == "1"


from .utils import capture


@capture
def dual_stage_quadratic_hip_attention(
    q: Tensor,
    k: Optional[Tensor],
    v: Optional[Tensor],
    args: HiPAttentionArgs,
    cached_metadata: Optional[HiPAttentionOutputMetadata] = None,
):
    global __logall_index
    global DEBUG
    DEBUG_HEAD = -1

    # HIP_LANDMARK_BASED_SCAN_STAGE = (
    #     os.getenv("HIP_LANDMARK_BASED_SCAN_STAGE", "1") == "1"
    # )

    require_state = args.using_landmark or any(
        [s.using_landmark if isinstance(s, ScanStage) else False for s in args.stages]
    )

    if require_state and (not args.is_decode):
        # if q.shape[1] > 1: print('using cached state')
        if (cached_metadata is not None) and (cached_metadata.state is not None):
            state = cached_metadata.state
        else:
            state = HiPAttentionState.from_args(q, args, k)
    else:
        state = None

    flatten_paged_cache = False
    if q.shape[1] == 1:
        pass
    # elif HIP_DEBUG_LANDMARK_BASED_SCAN_STAGE:
    #     # FIXME: just for dev
    #     if k is None:
    #         flatten_paged_cache = True
    #         seq_len = args.position_ids.amax().item() + 1
    #         k = args.gather_k_from_paged_cache(
    #             chunk_size=args.stages[0].stage_chunk_size,
    #             disable_gqa=True,
    #             gqa_q=q,
    #         )
    #         k = k[:, :seq_len]
    #         # v = args.gather_v_from_paged_cache(
    #         #     chunk_size=args.stages[0].stage_chunk_size,
    #         #     disable_gqa=True,
    #         #     gqa_q=q,
    #         # )
    #         # v = v[:, :seq_len]

    if args.q_mask is None:
        q_bsa = q
    else:
        q_bsa = q
        q = args.q_mask
    if args.k_mask is None:
        k_mask = k
    else:
        k_mask = args.k_mask

    k_mask_original = k_mask

    BSZ, TDST, HEAD, HID = q.shape
    if k is not None:
        BSZ, TSRC, HEAD_KV, HID = k.shape
        if v is not None:
            assert v.shape[0] == k.shape[0]
            assert v.shape[1] == k.shape[1]
            assert v.shape[2] == k.shape[2]
        MAX_TSRC = TSRC
    else:
        # MAX_TSRC = args.k_cache.shape[0] * args.k_cache.shape[1]
        # MAX_TSRC = int(os.getenv('EXTEND_LEN', '128')) * 1024
        MAX_TSRC = args.extend_context_length
        if args.k_cache is not None:
            HEAD_KV = args.k_cache.shape[-2]
        else:
            HEAD_KV = args.offload_cache.k_uvm.bank_cpu.shape[-2]
        TSRC = MAX_TSRC

    assert len(args.stages) > 0
    STAGE_STRIDE = args.stages[0].stage_stride
    BLOCK_SIZE_Q = args.stages[0].stage_block_size_q
    BDST = triton.cdiv(TDST, BLOCK_SIZE_Q)
    BDST_SCAN = triton.cdiv(BDST, STAGE_STRIDE)
    BLOCK_CHUNK = int(os.getenv("SCAN_BLOCK_CHUNK", "64"))
    chunk_size = args.stages[0].stage_chunk_size
    chunk_count = triton.cdiv(
        max(0, MAX_TSRC - args.sink_token_size - args.sliding_window_size), chunk_size
    )

    args = args.clone()
    args.mask_k = args.stages[0].stage_chunk_size
    original_sliding_window_size = args.sliding_window_size
    # args.sliding_window_size = max(0, args.sliding_window_size - args.mask_k)

    if args.rope_range is None:
        args.rope_range = (0, HID)

    if args.rope_is_neox_style is None:
        # warnings.warn(
        #     "Deprecated: Please specify `rope_is_neox_style`. Defaulting to True."
        # )
        args.rope_is_neox_style = True

    if args.rope_range[0] == 0 and args.rope_range[1] == HID:
        HID_BLOCK = triton.next_power_of_2(HID)
    else:
        assert triton.next_power_of_2(args.rope_range[0]) == args.rope_range[0]
        assert args.rope_range[1] == HID
        HID_BLOCK = args.rope_range[0]

    if torch.cuda.is_current_stream_capturing() or args.position_ids is not None:
        assert args.position_ids is not None
        position_ids = args.position_ids
    else:
        position_ids = (torch.arange(0, TDST, device=q.device) + (TSRC - TDST))[
            None, :
        ].expand(BSZ, TDST)
        args = args.clone()
        args.position_ids = position_ids
    assert position_ids.shape == (BSZ, TDST), position_ids.shape

    if args.using_paged_cache:
        MAX_PAGE = args.paged_cache_page_count
    else:
        MAX_PAGE = MAX_TSRC

    if args.require_cache_statistics:
        mask_access_counter = torch.zeros(
            (BSZ, HEAD_KV, MAX_PAGE), dtype=torch.int32, device=q.device
        )
        mask_cache_miss_counter = torch.zeros(
            (BSZ, HEAD_KV, MAX_PAGE), dtype=torch.int32, device=q.device
        )
        sa_access_counter = torch.zeros(
            (BSZ, HEAD_KV, MAX_PAGE), dtype=torch.int32, device=q.device
        )
        sa_cache_miss_counter = torch.zeros(
            (BSZ, HEAD_KV, MAX_PAGE), dtype=torch.int32, device=q.device
        )
    else:
        sa_cache_miss_counter = sa_access_counter = mask_cache_miss_counter = (
            mask_access_counter
        ) = None

    stage_caches = (
        []
        if (cached_metadata is None) or (cached_metadata.stage_caches is None)
        else cached_metadata.stage_caches
    )
    if not args.require_stage_caches:
        stage_caches = None

    if (cached_metadata is None) or (cached_metadata.indices is None):
        # loop carrying variables: indices_left, indices_right, out_scores
        if (
            (cached_metadata is None)
            or (cached_metadata.stage_caches is None)
            or (stage_caches is None)
        ):
            indices_left = torch.zeros(
                (BSZ, BDST_SCAN, HEAD, chunk_count), device=q.device, dtype=torch.int64
            )

            indices_left[:, :, :, :] = (
                torch.floor(
                    torch.arange(0, chunk_count, device=q.device, dtype=torch.float64)
                    * chunk_size
                    + args.sink_token_size
                ).to(indices_left.dtype)
            )[None, None, None, :]
            indices_right = indices_left + chunk_size
            indices_right.clamp_max_(MAX_TSRC - args.sliding_window_size)

            out_scores = torch.full(
                (BSZ, BDST_SCAN, HEAD, triton.next_power_of_2(chunk_count)),
                device=q.device,
                dtype=torch.float32,
                fill_value=-32000.0,
            )
        else:
            assert cached_metadata is not None
            assert cached_metadata.stage_caches is not None
            assert len(stage_caches) <= len(args.stages)

            last_stage_cache = stage_caches[-1]

            indices_left = last_stage_cache.indices_left.clone()
            indices_right = last_stage_cache.indices_right.clone()
            out_scores = last_stage_cache.out_scores.clone()

        landmark_scores = None

        for i_stage, stage_info in enumerate(args.stages):
            # if stage_chunk_size > chunk_size: continue
            # if stage_k > TSRC: continue

            stage_block_stride_q = stage_info.stage_block_stride_q
            stage_chunk_size = stage_info.stage_chunk_size
            stage_k = stage_info.stage_k

            if i_stage < (len(stage_caches if stage_caches is not None else []) - 1):
                # print('stage cached pass', i_stage)
                continue
            elif i_stage == (len(stage_caches if stage_caches is not None else []) - 1):
                # print('last cached stage', i_stage)
                pass
            elif i_stage > 0:
                (
                    indices_left,
                    indices_right,
                    out_scores,
                    BLOCK_SIZE_Q,
                    BDST,
                    STAGE_STRIDE,
                ) = stage_prologue(
                    q,
                    indices_left,
                    indices_right,
                    out_scores,
                    stage_k,
                    stage_chunk_size,
                    chunk_size,
                    stage_info,
                    args,
                    TDST,
                    BDST,
                    STAGE_STRIDE,
                    BLOCK_SIZE_Q,
                )
            else:
                assert stage_info.stage_k is None, "first stage always quadratic"
                assert isinstance(
                    stage_info, ScanStage
                ), f"frist stage always scan {stage_info}"
                STAGE_STRIDE = stage_info.stage_stride

            if (stage_caches is not None) and (i_stage >= len(stage_caches)):
                if i_stage == 0:
                    # NOTE: do not cache first stage input, because it is meaning less.
                    stage_caches.append(
                        HiPAttentionStageInputCache(
                            indices_left=None,
                            indices_right=None,
                            out_scores=None,
                        )
                    )
                else:
                    stage_caches.append(
                        HiPAttentionStageInputCache(
                            indices_left=indices_left.clone(),
                            indices_right=indices_right.clone(),
                            out_scores=out_scores.clone(),
                        )
                    )

            chunk_size = stage_chunk_size
            chunk_count = indices_left.shape[-1]
            BLOCK_CHUNK = max(16, triton.next_power_of_2(min(chunk_count, BLOCK_CHUNK)))

            pre_device = torch.cuda.current_device()
            torch.cuda.set_device(q.device)

            if isinstance(stage_info, ScanStage):
                extend_backend = (
                    args.scan_extend_backend
                    if stage_info.stage_extend_backend is None
                    else stage_info.stage_extend_backend
                )

                # if args.offload_cache is not None:
                #     print('before masking')
                #     args.offload_cache.mask_k_cache._verify_cache()

                # B T H D
                # if k_mask_original is not None:
                #     B, T, H, D = k.shape
                #     wind_size = args.stages[i_stage + 1].stage_chunk_size // 2 - 1 if (i_stage + 1) < len(args.stages) else 0
                #     if wind_size > 0:
                #         k_max = torch.nn.functional.max_pool1d(k_mask_original.permute(0, 2, 3, 1).reshape(-1, 1, T), kernel_size=wind_size*2 + 1, padding=wind_size, stride=1)
                #         k_min = -torch.nn.functional.max_pool1d((-k_mask_original).permute(0, 2, 3, 1).reshape(-1, 1, T), kernel_size=wind_size*2 + 1, padding=wind_size, stride=1)
                #         k_mask = ((k_min + k_max) / 2).view(B, H, D, T).permute(0, 3, 1, 2).contiguous()
                #         del k_max, k_min
                #     else:
                #         k_mask = k_mask_original

                debug_exclude_landmark = []
                if "HIP_DEBUG_EXCLUDE_LANDMARK" in os.environ:
                    debug_exclude_landmark = list(
                        map(
                            lambda x: int(x),
                            os.environ["HIP_DEBUG_EXCLUDE_LANDMARK"].split(","),
                        )
                    )

                assert q.shape[1] <= BDST * BLOCK_SIZE_Q
                if (
                    (args.using_landmark or stage_info.using_landmark)
                    and (not args.is_decode)
                    and (BDST > 1)
                    and (args.position_ids.shape[0] == 1)
                    and (args.layer_id not in debug_exclude_landmark)
                ):
                    assert not torch.cuda.is_current_stream_capturing()

                    if triton.next_power_of_2(q.shape[-1]) > q.shape[-1]:
                        NOPE_HID = triton.next_power_of_2(q.shape[-1]) // 2
                    else:
                        NOPE_HID = q.shape[-1]

                    # chunked sampling
                    if landmark_scores is None:
                        landmark_scores = landmark_sample(
                            q[..., :NOPE_HID],
                            k[..., :NOPE_HID] if k is not None else k,
                            state,
                            args,
                            BSZ,
                            HEAD,
                            HEAD_KV,
                            BDST,
                            DEBUG,
                            __logall_index,
                        )

                    _TSRC = TSRC
                    if k is not None:
                        _TSRC = k.shape[1]

                    landmarks = landmark_scores.view(
                        BSZ,
                        HEAD,
                        landmark_scores.shape[-1] // stage_info.stage_chunk_size,
                        stage_info.stage_chunk_size,
                    )
                    num_landmarks = args.landmark_stage_k[i_stage]
                    _, landmarks = torch.topk(landmarks, k=num_landmarks, sorted=False)
                    landmarks = landmarks.permute(0, 2, 1, 3)[
                        :, : _TSRC // stage_info.stage_chunk_size
                    ].contiguous()
                    assert landmarks.shape == (
                        BSZ,
                        _TSRC // stage_info.stage_chunk_size,
                        HEAD,
                        num_landmarks,
                    ), f"{landmarks.shape} == ({BSZ}, {_TSRC // stage_info.stage_chunk_size}, {HEAD}, {num_landmarks}), {k.shape if k is not None else None}"

                    assert indices_left.shape == (
                        BSZ,
                        BDST,
                        HEAD,
                        indices_left.shape[-1],
                    ), f"{indices_left.shape} == ({BSZ},{BDST},{HEAD},{indices_left.shape[-1]},)"

                    # k_temp = args.gather_k_from_paged_cache(
                    #     chunk_size=1,
                    #     disable_gqa=False,
                    #     gqa_q=q,
                    # )
                    scores = compute_scores_landmark(
                        q=q[..., :NOPE_HID],
                        # k=k_temp,
                        # k_cache=None,
                        k=k[..., :NOPE_HID] if k is not None else k,
                        k_cache=(
                            args.get_k_cache()[..., :NOPE_HID]
                            if args.get_k_cache() is not None
                            else None
                        ),
                        block_table=args.block_table,
                        position_ids=args.position_ids,
                        indices_left=indices_left,
                        landmarks=landmarks,
                        cos=args.rope_cos,
                        sin=args.rope_sin,
                        BLOCK_SIZE_Q=stage_info.stage_block_size_q,
                        BLOCK_STRIDE_Q=stage_info.stage_block_stride_q,
                        CHUNK_SIZE=stage_info.stage_chunk_size,
                        SLIDING_WINDOW_SIZE=args.sliding_window_size,
                    )
                    assert (
                        args.sink_token_size % stage_info.stage_chunk_size
                    ) == 0, f"{args.sink_token_size} % {stage_info.stage_chunk_size}"
                    # scores = scores[:, :, :, args.sink_token_size // stage_info.stage_chunk_size:]

                    out_scores[:, :, :, : scores.shape[-1]] = scores
                    out_scores[:, :, :, scores.shape[-1] :].fill_(float("-inf"))
                    # indices_left = (indices_left + indices_right) // 2
                    # indices_right = indices_left.clone()

                    # print('landmark based sampling', args.layer_id)
                elif (
                    os.getenv("HIP_DEBUG_TOPKMEAN", "0") == "1"
                    and (i_stage == 0)
                    and (BDST > 1)
                    and ((q.shape[1] % BLOCK_SIZE_Q) == 0)
                    and (args.position_ids.shape[0] == 1)
                ):
                    debug_topk_window = int(os.getenv("HIP_DEBUG_TOPK_WINDOW", "8"))
                    k_dense = args.gather_k_from_paged_cache(
                        chunk_size=chunk_size, disable_gqa=True, gqa_q=q
                    )
                    scores = torch.matmul(
                        q.permute(0, 2, 1, 3), k_dense.permute(0, 2, 3, 1)
                    )[:, args.sink_token_size : -args.sliding_window_size, :, :]
                    mask = (
                        args.position_ids[0][:, None]
                        >= (
                            args.sink_token_size
                            + torch.arange(
                                0, k_dense.shape[1], dtype=q.dtype, device=q.device
                            )
                        )[None, :]
                    )[None, None, :, :]
                    scores = torch.where(mask, scores, -32000.0)
                    scores = scores.view(
                        scores.shape[0],
                        scores.shape[1],
                        scores.shape[2] // BLOCK_SIZE_Q,
                        BLOCK_SIZE_Q,
                        scores.shape[3] // chunk_size,
                        chunk_size,
                    )
                    scores = torch.amax(scores, dim=3)
                    topk_scores, _ = torch.topk(scores, dim=-1, k=debug_topk_window)
                    scores = topk_scores.mean(dim=-1)
                    scores = scores.permute(0, 2, 1, 3)
                    out_scores[:, :, :, : scores.shape[-1]] = scores
                elif (
                    os.getenv("HIP_DEBUG_SOFTMAXMEAN", "0") == "1"
                    and (i_stage == 0)
                    and (BDST > 1)
                    and ((q.shape[1] % BLOCK_SIZE_Q) == 0)
                    and (args.position_ids.shape[0] == 1)
                ):

                    def rotate_half(vec):
                        # assert len(vec.shape) == 1
                        out = torch.zeros_like(vec)
                        x1 = vec[..., : vec.shape[-1] // 2]
                        x2 = vec[..., vec.shape[-1] // 2 :]
                        out[..., : vec.shape[-1] // 2] = -x2
                        out[..., vec.shape[-1] // 2 :] = x1
                        return out

                    def apply_rope(vec, cos, sin):
                        vec_rope = (vec * cos) + (rotate_half(vec) * sin)
                        return vec_rope

                    k_dense = args.gather_k_from_paged_cache(
                        chunk_size=chunk_size, disable_gqa=True, gqa_q=q
                    )[:, args.sink_token_size : -args.sliding_window_size, :, :]
                    k_dense = apply_rope(
                        k_dense,
                        args.rope_cos[None, 0 : 0 + 1, None, :],
                        args.rope_sin[None, 0 : 0 + 1, None, :],
                    )
                    q_dense = apply_rope(
                        q,
                        args.rope_cos[None, 1024 : 1024 + 1, None, :],
                        args.rope_sin[None, 1024 : 1024 + 1, None, :],
                    )
                    scores = torch.matmul(
                        q_dense.permute(0, 2, 1, 3), k_dense.permute(0, 2, 3, 1)
                    )
                    mask = (
                        args.position_ids[0][:, None]
                        >= (
                            args.sink_token_size
                            + torch.arange(
                                0,
                                k_dense.shape[1],
                                dtype=q_dense.dtype,
                                device=q_dense.device,
                            )
                        )[None, :]
                    )[None, None, :, :]
                    scores = torch.where(mask, scores, -32000.0).float()
                    scores = scores.softmax(dim=-1)
                    scores = torch.where(mask, scores, -32000.0)
                    scores = scores.view(
                        scores.shape[0],
                        scores.shape[1],
                        scores.shape[2] // BLOCK_SIZE_Q,
                        BLOCK_SIZE_Q,
                        scores.shape[3] // chunk_size,
                        chunk_size,
                    )
                    scores = (
                        scores.permute(0, 1, 2, 4, 3, 5)
                        .contiguous()
                        .view(
                            scores.shape[0],
                            scores.shape[1],
                            scores.shape[2],
                            scores.shape[4],
                            -1,
                        )
                    )
                    mask = scores > -30000.0
                    scores = (scores * mask).sum(dim=-1) / (
                        mask.float().sum(dim=-1) + 1e-12
                    )
                    scores.masked_fill_(mask.float().sum(dim=-1) == 0, -32000.0)
                    scores = scores.permute(0, 2, 1, 3)
                    # print(scores[0,:,0,:])
                    out_scores[:, :, :, : scores.shape[-1]] = scores
                elif (
                    os.getenv("HIP_DEBUG_FLATTENMEAN", "0") == "1"
                    and (i_stage == 0)
                    and (BDST > 1)
                    and ((q.shape[1] % BLOCK_SIZE_Q) == 0)
                    and (args.position_ids.shape[0] == 1)
                ):

                    def rotate_half(vec):
                        # assert len(vec.shape) == 1
                        out = torch.zeros_like(vec)
                        x1 = vec[..., : vec.shape[-1] // 2]
                        x2 = vec[..., vec.shape[-1] // 2 :]
                        out[..., : vec.shape[-1] // 2] = -x2
                        out[..., vec.shape[-1] // 2 :] = x1
                        return out

                    def apply_rope(vec, cos, sin):
                        vec_rope = (vec * cos) + (rotate_half(vec) * sin)
                        return vec_rope

                    k_dense = args.gather_k_from_paged_cache(
                        chunk_size=chunk_size, disable_gqa=True, gqa_q=q
                    )[:, args.sink_token_size : -args.sliding_window_size, :, :]
                    k_dense = apply_rope(
                        k_dense,
                        args.rope_cos[None, 0 : 0 + 1, None, :],
                        args.rope_sin[None, 0 : 0 + 1, None, :],
                    )
                    q_dense = apply_rope(
                        q,
                        args.rope_cos[None, 1024 : 1024 + 1, None, :],
                        args.rope_sin[None, 1024 : 1024 + 1, None, :],
                    )
                    scores = torch.matmul(
                        q_dense.permute(0, 2, 1, 3), k_dense.permute(0, 2, 3, 1)
                    )
                    mask = (
                        args.position_ids[0][:, None]
                        >= (
                            args.sink_token_size
                            + torch.arange(
                                0,
                                k_dense.shape[1],
                                dtype=q_dense.dtype,
                                device=q_dense.device,
                            )
                        )[None, :]
                    )[None, None, :, :]
                    scores = torch.where(mask, scores, -32000.0)
                    scores = scores.view(
                        scores.shape[0],
                        scores.shape[1],
                        scores.shape[2] // BLOCK_SIZE_Q,
                        BLOCK_SIZE_Q,
                        scores.shape[3] // chunk_size,
                        chunk_size,
                    )
                    scores = (
                        scores.permute(0, 1, 2, 4, 3, 5)
                        .contiguous()
                        .view(
                            scores.shape[0],
                            scores.shape[1],
                            scores.shape[2],
                            scores.shape[4],
                            -1,
                        )
                    )
                    mask = scores > -30000.0
                    scores = (scores * mask).sum(dim=-1) / (
                        mask.float().sum(dim=-1) + 1e-12
                    )
                    scores.masked_fill_(mask.float().sum(dim=-1) == 0, -32000.0)
                    scores = scores.permute(0, 2, 1, 3)
                    # print(scores[0,:,0,:])
                    out_scores[:, :, :, : scores.shape[-1]] = scores
                elif (
                    os.getenv("HIP_DEBUG_FLATTENTOPKMEAN", "0") == "1"
                    and (i_stage == 0)
                    and (BDST > 1)
                    and ((q.shape[1] % BLOCK_SIZE_Q) == 0)
                    and (args.position_ids.shape[0] == 1)
                ):

                    def rotate_half(vec):
                        # assert len(vec.shape) == 1
                        out = torch.zeros_like(vec)
                        x1 = vec[..., : vec.shape[-1] // 2]
                        x2 = vec[..., vec.shape[-1] // 2 :]
                        out[..., : vec.shape[-1] // 2] = -x2
                        out[..., vec.shape[-1] // 2 :] = x1
                        return out

                    def apply_rope(vec, cos, sin):
                        vec_rope = (vec * cos) + (rotate_half(vec) * sin)
                        return vec_rope

                    debug_topk_window = int(os.getenv("HIP_DEBUG_TOPK_WINDOW", "8"))
                    k_dense = args.gather_k_from_paged_cache(
                        chunk_size=chunk_size, disable_gqa=True, gqa_q=q
                    )[:, args.sink_token_size : -args.sliding_window_size, :, :]
                    k_dense = apply_rope(
                        k_dense,
                        args.rope_cos[None, 0 : 0 + 1, None, :],
                        args.rope_sin[None, 0 : 0 + 1, None, :],
                    )
                    q_dense = apply_rope(
                        q,
                        args.rope_cos[None, 1024 : 1024 + 1, None, :],
                        args.rope_sin[None, 1024 : 1024 + 1, None, :],
                    )
                    scores = torch.matmul(
                        q_dense.permute(0, 2, 1, 3), k_dense.permute(0, 2, 3, 1)
                    )
                    mask = (
                        args.position_ids[0][:, None]
                        >= (
                            args.sink_token_size
                            + torch.arange(
                                0,
                                k_dense.shape[1],
                                dtype=q_dense.dtype,
                                device=q_dense.device,
                            )
                        )[None, :]
                    )[None, None, :, :]
                    scores = torch.where(mask, scores, -32000.0)
                    scores = scores.view(
                        scores.shape[0],
                        scores.shape[1],
                        scores.shape[2] // BLOCK_SIZE_Q,
                        BLOCK_SIZE_Q,
                        scores.shape[3] // chunk_size,
                        chunk_size,
                    )
                    scores = (
                        scores.permute(0, 1, 2, 4, 3, 5)
                        .contiguous()
                        .view(
                            scores.shape[0],
                            scores.shape[1],
                            scores.shape[2],
                            scores.shape[4],
                            -1,
                        )
                    )
                    topk_scores, _ = torch.topk(scores, dim=-1, k=debug_topk_window)
                    topk_scores_mask = topk_scores > -30000.0
                    scores = (topk_scores * topk_scores_mask).sum(dim=-1) / (
                        topk_scores_mask.float().sum(dim=-1) + 1e-12
                    )
                    scores = torch.where(
                        topk_scores_mask.int().sum(dim=-1) != 0, scores, -32000.0
                    )
                    scores = scores.permute(0, 2, 1, 3)
                    out_scores[:, :, :, : scores.shape[-1]] = scores
                else:
                    chunk_controllable_sampling_mask(
                        args,
                        chunk_count,
                        BLOCK_CHUNK,
                        TDST,
                        BLOCK_SIZE_Q,
                        STAGE_STRIDE,
                        HEAD,
                        BSZ,
                        q,
                        k_mask,
                        position_ids,
                        indices_left,
                        indices_right,
                        out_scores,
                        mask_access_counter,
                        mask_cache_miss_counter,
                        MAX_TSRC,
                        HID,
                        HID_BLOCK,
                        stage_block_stride_q,
                        HEAD_KV,
                        extend_backend,
                    )

                # TODO: OPTIMIZE THIS. Add head unified version of HiP.
                HEAD_REDUCE_MODE = os.getenv(
                    "HIP_HEAD_REDUCE", DEFAULT_VALUE_HIP_HEAD_REDUCE
                )
                if (
                    # always reduce the head.
                    (HEAD_REDUCE_MODE == "1")
                    or
                    # reduce only when decode. this is for handling flash-decode kernel.
                    (HEAD_REDUCE_MODE == "2" and BDST == 1)
                    or
                    # reduce only within tp. this will be incorrect in tp size
                    (HEAD_REDUCE_MODE == "3")
                ):
                    ori_shape = out_scores.shape
                    # out_scores = out_scores.softmax(dim=2) # NOTE: not good idea
                    # out_scores, _ = torch.max(out_scores, keepdim=True, dim=2)

                    if (
                        SGLANG_DIST_ACTIVATED
                        and get_world_size() > 1
                        and HEAD_REDUCE_MODE in ["1", "2"]
                    ):
                        warnings.warn(
                            f"TP all gather is used for head reduce, this may degrade throughput. (MODE={HEAD_REDUCE_MODE})"
                        )

                        out_scores_tp = out_scores
                        out_scores = (
                            tensor_model_parallel_all_gather(
                                out_scores_tp.permute(0, 1, 3, 2).contiguous()
                            )
                            .permute(0, 1, 3, 2)
                            .contiguous()
                        )

                    out_scores = torch.amax(out_scores, keepdim=True, dim=2)
                    out_scores = torch.broadcast_to(out_scores, ori_shape).contiguous()
                else:
                    args.disable_flashdecode = True

                if args.offload_cache is not None:
                    # print('after masking')
                    args.offload_cache.mask_k_cache.verify_cache()
            elif isinstance(stage_info, EvalScoreStage):
                raise Exception()  # TODO: handle new args
                extend_backend = (
                    args.scan_extend_backend
                    if stage_info.stage_extend_backend is None
                    else stage_info.stage_extend_backend
                )

                grid = (
                    BSZ
                    * triton.cdiv(BDST, stage_info.stage_stride)
                    * HEAD,  # SCAN_STRIDE = 1
                )
                calculate_chunk_score[grid](
                    q_mask,
                    *q_mask.stride(),
                    k_mask,
                    *safe_stride(k_mask, 4),
                    position_ids,
                    *position_ids.stride(),
                    args.rope_cos,
                    *safe_stride(args.rope_cos, 2),
                    args.rope_sin,
                    *safe_stride(args.rope_sin, 2),
                    *args.args_paged_kv_cache(),
                    *args.args_offload_cache(True),
                    indices_left,
                    *indices_left.stride(),
                    indices_right,
                    *indices_right.stride(),
                    out_scores,
                    *out_scores.stride(),
                    # model_context_length if (not scan_extend_backend == 'streaming') else 0,
                    args.model_context_length,
                    args.sliding_window_size,
                    args.sink_token_size,
                    chunk_size,
                    TDST,
                    BDST,
                    triton.cdiv(BDST, stage_info.stage_stride),  # SCAN STRIDE == 1
                    HEAD,
                    chunk_count,
                    HEAD // HEAD_KV,
                    USING_EXTEND=args.using_extend,
                    NEED_APPLY_ROPE=args.need_apply_rope,
                    EXTEND_BACKEND=extend_backend,
                    BLOCK_HID=BLOCK_HID,
                    BLOCK_SIZE_Q=BLOCK_SIZE_Q,
                    BLOCK_STRIDE_Q=stage_block_stride_q,
                    BLOCK_SIZE_K=args.stage_early_terminate,
                    BLOCK_STRIDE_K=args.block_stride_k,
                    SCAN_STRIDE=stage_info.stage_stride,
                    BLOCK_CHUNK=stage_info.block_chunk,
                )
            elif isinstance(stage_info, EnsembleScoreStage):
                raise Exception()
            elif isinstance(stage_info, NopStage):
                pass
            else:
                raise Exception()

            torch.cuda.set_device(pre_device)

            if stage_info.require_post_sort:
                apply_v_dot = os.getenv("APPLY_V_DOT", "0") == "1"
                # apply_v_dot = apply_v_dot and (i_stage == (len(stages) - 1))
                apply_v_dot = apply_v_dot and (i_stage != 0)
                if apply_v_dot:
                    v_scores = torch.zeros_like(out_scores, dtype=torch.float32)
                    V_BLOCK_SIZE_K = 8
                    V_BLOCK_STRIDE_Q = 1
                    V_BLOCK_STRIDE_K = 1
                    V_GROUP_K = 64 // V_BLOCK_SIZE_K
                    # V_GROUP_K = indices_left.shape[3]
                    grid = (
                        v_scores.shape[0]
                        * v_scores.shape[1]
                        * v_scores.shape[2]
                        * triton.cdiv(indices_left.shape[3], V_GROUP_K),
                    )
                    compute_v_cos[grid](
                        v,
                        *safe_stride(v, 4),
                        indices_left,
                        *indices_left.stride(),
                        position_ids,
                        *position_ids.stride(),
                        v_scores,
                        *v_scores.stride(),
                        *args.args_paged_kv_cache(),
                        *args.args_offload_cache(is_masking=True),
                        sa_access_counter,
                        *safe_stride(sa_access_counter, 3),
                        sa_cache_miss_counter,
                        *safe_stride(sa_cache_miss_counter, 3),
                        TDST,
                        MAX_TSRC,
                        HEAD,
                        indices_left.shape[3],
                        HEAD_GROUP=HEAD // HEAD_KV,
                        GROUP_K=V_GROUP_K,
                        BLOCK_SIZE_Q=BLOCK_SIZE_Q,
                        BLOCK_SIZE_K=V_BLOCK_SIZE_K,
                        BLOCK_STRIDE_Q=V_BLOCK_STRIDE_Q,
                        BLOCK_STRIDE_K=V_BLOCK_STRIDE_K,
                        BLOCK_HID=q.shape[-1],
                    )

                    if out_scores.dtype != torch.float32:
                        out_scores = out_scores.to(torch.float32)
                    out_scores = (
                        out_scores - out_scores.min(dim=-1, keepdim=True).values
                    )

                    # print(indices_left[0, -1, DEBUG_HEAD, :])
                    # print(out_scores[0, -1, DEBUG_HEAD, :])
                    # print(v_scores[0, -1, DEBUG_HEAD, :])

                    if DEBUG and DEBUG_RENDER:
                        img = v_scores[0, :, DEBUG_HEAD, :].cpu().float().numpy()
                        plt.clf()
                        plt.imshow(img)
                        plt.colorbar()
                        plt.savefig("dummy_v_scores.png")

                    # out_scores = torch.where(
                    #     torch.isnan(v_scores),
                    #     out_scores,
                    #     out_scores * v_scores
                    # )

                    # out_scores = out_scores * v_scores

                    out_scores = out_scores + v_scores

                if i_stage < (len(args.stages) - 1):
                    # print(indices_left.shape, (stages[i_stage + 1].stage_k // stages[i_stage + 1].stage_chunk_size))
                    next_stage_k = (
                        args.stages[i_stage + 1].stage_k
                        // args.stages[i_stage].stage_chunk_size
                    )
                else:
                    next_stage_k = (
                        args.second_stage_k // args.stages[i_stage].stage_chunk_size
                    )
                next_stage_k = min(next_stage_k, indices_left.shape[-1])
                _, t_indices = out_scores[..., : indices_left.shape[-1]].topk(
                    k=next_stage_k,
                    dim=-1,
                    sorted=False,
                    largest=True,
                )
                # else:
                #     _, t_indices = out_scores[..., : indices_left.shape[-1]].sort(
                #         dim=-1, descending=True, stable=False
                #     )
                indices_left = indices_left.gather(dim=-1, index=t_indices)
                indices_right = indices_right.gather(dim=-1, index=t_indices)

            if (
                DEBUG
                and DEBUG_RENDER
                and not torch.cuda.is_current_stream_capturing()
                and get_local_rank() == 0
            ):
                if (i_stage + 1) < len(args.stages):
                    next_stage_k = args.stages[i_stage + 1].stage_k
                else:
                    next_stage_k = args.second_stage_k
                out_indices_cpu = (
                    indices_left.repeat_interleave(STAGE_STRIDE, 1)[:, -BDST:]
                    .contiguous()
                    .cpu()
                    .numpy()
                )
                debug = np.zeros(
                    (triton.cdiv(TDST, BLOCK_SIZE_Q), triton.cdiv(TSRC, BLOCK_SIZE_Q))
                )
                render_plot_dynamic(
                    out_indices_cpu,
                    debug,
                    DEBUG_HEAD,
                    BLOCK_SIZE_Q,
                    next_stage_k,
                    chunk_size,
                    causal_mask=True,
                    sliding_window_size=args.sliding_window_size,
                )
                if DEBUG_LOGALL and (BDST > 1):
                    __logall_index += 1
                    os.makedirs("./cache/mask_log", exist_ok=True)
                    # cv2.imwrite(
                    #     f"./cache/mask_log/{__logall_index:04d}_dummy_sampled_stage_{i_stage}.png",
                    #     debug * 255,
                    # )
                else:
                    cv2.imwrite(f"dummy_sampled_stage_{i_stage}.png", debug * 255)
                # print(f'saved dummy_sampled_stage_{i_stage}.png')

        if STAGE_STRIDE > 1:
            indices_left = indices_left.repeat_interleave(STAGE_STRIDE, 1)[
                :, -BDST:
            ].contiguous()
            indices_right = indices_right.repeat_interleave(STAGE_STRIDE, 1)[
                :, -BDST:
            ].contiguous()
            out_scores = out_scores.repeat_interleave(STAGE_STRIDE, 1)[
                :, -BDST:
            ].contiguous()

        assert (args.second_stage_k % chunk_size) == 0
        # if DEBUG:
        #     print('indices_left', indices_left[0, -1])
        #     print('out_scores', out_scores[0, -1], args.second_stage_k, indices_left.shape, chunk_size)
        indices = (
            indices_left[..., : args.second_stage_k // chunk_size]
            // chunk_size
            * chunk_size
        )

        # NOTE: union head masks
        if os.getenv("HIP_DEBUG_UNION_HEAD", "0") == "1":
            assert os.getenv("HIP_HEAD_REDUCE", DEFAULT_VALUE_HIP_HEAD_REDUCE) == "0"
            # args.disable_flashdecode = True
            # B BDST H CHUNK
            indices = indices.flatten(-2, -1).unsqueeze(-2).repeat(1, 1, HEAD, 1)

        # NOTE: sampled indices might be delayed
        if os.getenv("HIP_DEBUG_ADD_DELAY_WINDOW", "0") == "1":
            delayed_indices = [
                indices,
            ]
            delay_window = 64
            for i_delay in range(0, delay_window, chunk_size):
                delayed_indices.append(indices - i_delay - chunk_size)
            # print(indices.shape)
            indices = torch.cat(delayed_indices, dim=-1)
            # print(indices.shape)

        # NOTE: performing SnapKV
        if (os.getenv("HIP_DEBUG_SNAP_KV", "0") == "1") and (BDST > 1):
            is_paged = False
            if k_mask_original is None:
                is_paged = True
                k_mask = args.gather_k_from_paged_cache(chunk_size=chunk_size)
            else:
                k_mask = k_mask_original
            scores = torch.matmul(
                q.permute(0, 2, 1, 3)[:, :, -128:, :],
                k_mask.permute(0, 2, 3, 1).repeat(1, HEAD // HEAD_KV, 1, 1),
            )
            # if is_paged:
            tsrcs = torch.arange(0, scores.shape[-1], device=q.device)
            tsrc_mask = tsrcs[None, :] > args.position_ids[:, -1, None]
            scores = scores.masked_fill_(tsrc_mask[:, None, None, :], float("-inf"))
            scores = scores.amax(dim=-2)  # B H TSRC
            snap_window = 127
            scores = torch.nn.functional.max_pool1d(
                scores, kernel_size=snap_window * 2 + 1, stride=1, padding=snap_window
            )
            scores = scores.view(scores.shape[0], scores.shape[1], -1, chunk_size)
            scores = scores.amax(dim=-1)
            # print(scores.shape)
            _, snap_indices = scores.topk(
                k=min(scores.shape[-1], 131072 // chunk_size), dim=-1
            )
            snap_indices = snap_indices * chunk_size
            snap_indices = snap_indices.unsqueeze(1).expand(
                snap_indices.shape[0],
                indices.shape[1],
                snap_indices.shape[1],
                snap_indices.shape[2],
            )
            indices = torch.concat([indices, snap_indices], dim=-1)
            if is_paged:
                k_mask = None

        # NOTE: add sliding window indices
        if args.sliding_window_indices is not None:
            sw_indices = (args.sliding_window_indices // chunk_size) * chunk_size
            assert position_ids.shape == (BSZ, TDST), position_ids.shape
            assert sw_indices.shape[0] == HEAD, sw_indices.shape
            args.disable_flashdecode = True
            warnings.warn("Flash Decode is disabled due to experimental feature")
            sw_indices = (
                position_ids[:, ::BLOCK_SIZE_Q, None, None]
                + sw_indices[None, None, :, :]
            )
            sw_indices = (sw_indices // chunk_size) * chunk_size
            sw_indices.clamp_min_(0)
            indices = torch.concat([indices, sw_indices], dim=-1)

        # NOTE: adding important Ks
        if (os.getenv("HIP_DEBUG_IMPORTANT_K", "0") == "1") and (BDST > 1):
            k_seq = args.gather_k_from_paged_cache(chunk_size=chunk_size)
            k_bos = k_seq[:, :1, :, :].contiguous().permute(0, 2, 1, 3)
            k_seq = k_seq.permute(0, 2, 1, 3)
            k_seq = k_seq / k_seq.square().sum(dim=-1, keepdim=True).sqrt()
            k_bos = k_bos / k_bos.square().sum(dim=-1, keepdim=True).sqrt()
            scores = torch.matmul(k_bos, k_seq.permute(0, 1, 3, 2)).squeeze(2)  # B H T
            tsrcs = torch.arange(0, scores.shape[-1], device=q.device)
            tsrc_mask = (
                tsrcs[None, :] + original_sliding_window_size
            ) > args.position_ids[:, -1, None]
            scores.masked_fill_(tsrc_mask[:, None, :], float("-inf"))
            scores[:, :, : args.sink_token_size].fill_(float("-inf"))
            scores = scores.view(scores.shape[0], scores.shape[1], -1, chunk_size)
            # scores = scores.amax(dim=1, keepdim=True)
            scores = scores.amax(dim=-1)
            _, important_indices = torch.topk(scores, k=8192 // chunk_size, dim=-1)
            important_indices = (
                important_indices.repeat_interleave(
                    HEAD // important_indices.shape[1], 1
                )
                * chunk_size
            )
            important_indices = important_indices.unsqueeze(1).expand(
                important_indices.shape[0],
                indices.shape[1],
                important_indices.shape[1],
                important_indices.shape[2],
            )
            indices = torch.concat([indices, important_indices], dim=-1)

        if (
            DEBUG
            and DEBUG_RENDER
            and not torch.cuda.is_current_stream_capturing()
            and (BDST > 10)
            and get_local_rank() == 0
        ):
            out_indices_cpu = indices.cpu().numpy()
            debug = np.zeros(
                (triton.cdiv(TDST, BLOCK_SIZE_Q), triton.cdiv(TSRC, BLOCK_SIZE_Q))
            )
            render_plot(out_indices_cpu, debug, DEBUG_HEAD, BLOCK_SIZE_Q)
            debug = debug * 255
            debug = debug.astype(np.uint8)
            debug = np.repeat(debug[:, :, None], 3, axis=2)
            cv2.putText(
                debug,
                f"Layer: {args.layer_id}",
                (320, 256),
                cv2.FONT_HERSHEY_PLAIN,
                2,
                (0, 255, 0),
                2,
            )
            tdst_start = position_ids[0, 0].item() // BLOCK_SIZE_Q
            debug = cv2.line(
                debug,
                (
                    tdst_start,
                    0,
                ),
                (tdst_start + debug.shape[0], debug.shape[0]),
                thickness=1,
                color=(0, 255, 0),
            )

            if DEBUG_LOGALL and (BDST > 1):
                os.makedirs("./cache/mask_log", exist_ok=True)
                __logall_index += 1
                img_path = (
                    f"./cache/mask_log/{__logall_index:04d}_dummy_sampled_final.png"
                )
                print(img_path)
                cv2.imwrite(img_path, debug)
            else:
                cv2.imwrite("dummy_sampled_final.png", debug)
            # print('saved dummy_sampled_final.png')

        args = args.clone()
        args.block_size_q = args.stages[-1].stage_block_size_q
        block_sparse_block_size_q = min(
            args.block_sparse_block_size_q, args.block_size_q
        )
        args.sliding_window_size += args.mask_k
        args.block_size_k = chunk_size
        args.mask_k = args.second_stage_k
        args.using_extend = args.using_extend and True

        # NOTE: convert format and taking unique in indices
        indices = indices.permute(0, 2, 1, 3).flatten(0, 1)

        require_expand_future = False
        expand_future_window = 16
        if require_expand_future and (BDST == 1):
            dups = []
            for i in range(0, expand_future_window, args.block_size_k):
                dups.append(indices + i)
            indices = torch.cat(dups, dim=-1)

        require_post_unique = True  # BDST > 1
        if require_post_unique or require_expand_future:
            indices, t_sort_1 = indices.sort(dim=-1)
            indices = indices // args.block_size_k * args.block_size_k

            unique_mask = torch.roll(indices, shifts=1, dims=-1) != indices
            indices = torch.where(unique_mask, indices, torch.iinfo(indices.dtype).max)
            indices, t_sort_2 = indices.sort(dim=-1)

        active_mask = indices < (
            position_ids[:, :: args.block_size_q, None].repeat_interleave(HEAD, 0)
            + args.block_size_q
        )
        ks = active_mask.int().sum(-1)
        ks_count = ks.unsqueeze(-1)
        ks_start_end = torch.zeros(
            (ks.shape[0], ks.shape[1], 2), dtype=torch.int32, device=q.device
        )
        ks_start_end[:, :, -1] = ks

        # print(args.layer_id, round(ks.float().mean().item() * args.block_size_k))

        if (args.low_percent > 0) and (args.low_k_ratio < 1):
            scores = (
                out_scores[..., : args.second_stage_k // chunk_size]
                .permute(0, 2, 1, 3)
                .flatten(0, 1)
            )
            scores = scores.gather(dim=-1, index=t_sort_1)
            scores = scores.gather(dim=-1, index=t_sort_2)
            scores = torch.where(active_mask, scores, -32000.0)

            masked_scores = torch.where(scores > -16000.0, scores, 0)
            # masked_scores = torch.softmax(scores, dim=-1)
            scores_std, scores_mean = torch.std_mean(masked_scores, dim=-1)

            # TODO: TEST SENSITIVITY

            if dim_to_lower == "head":
                dim_to_lower = 0
                values_to_sort = (scores_std).mean(dim=1)
            elif dim_to_lower == "seq":
                dim_to_lower = 1
                values_to_sort = scores_std
            else:
                raise Exception()

            _, lowk = values_to_sort.topk(
                k=int(scores_mean.shape[dim_to_lower] * args.low_percent),
                dim=dim_to_lower,
                largest=False,
                sorted=False,
            )
            # print(lowk[:, -1])
            if lowk.ndim == 2:
                lowk = lowk[:, :, None].expand(-1, -1, scores.shape[-1])
            if lowk.ndim == 1:
                lowk = lowk[:, None, None].expand(
                    -1, scores.shape[-2], scores.shape[-1]
                )
            _, t_sort_score = torch.topk(
                scores.gather(dim=dim_to_lower, index=lowk),
                dim=-1,
                k=int(scores.shape[-1] * (1 - args.low_k_ratio)),
                largest=False,
            )
            # print(t_sort_score.shape)
            N, BDST = scores_mean.shape
            indices.scatter_(
                dim=dim_to_lower,
                index=lowk,
                src=indices.gather(dim=dim_to_lower, index=lowk).scatter(
                    dim=-1, index=t_sort_score, value=987654321
                ),
            )
            indices, t_sort_2 = indices.sort(dim=-1)
            active_mask = indices < (
                position_ids[:, :: args.block_size_q, None].repeat_interleave(HEAD, 0)
                + args.block_size_q
            )
            # print(indices[1, -1, :])
            # print(active_mask[1, -1, :])
            ks = active_mask.int().sum(-1)
            ks_count = ks.unsqueeze(-1)
            ks_start_end = torch.zeros(
                (ks.shape[0], ks.shape[1], 2), dtype=torch.int32, device=q.device
            )
            ks_start_end[:, :, -1] = ks

            if (
                DEBUG
                and DEBUG_RENDER
                and not torch.cuda.is_current_stream_capturing()
                and (BDST > 10)
            ):
                indices_cpu = indices.cpu().numpy()
                ks_cpu = ks.cpu().numpy()
                debug = np.zeros(
                    (triton.cdiv(TDST, BLOCK_SIZE_Q), triton.cdiv(TSRC, BLOCK_SIZE_Q))
                )
                render_plot_ks(indices_cpu, ks_cpu, debug, DEBUG_HEAD, BLOCK_SIZE_Q)
                cv2.imwrite("dummy_sampled_final_lowk.png", debug * 255)
                print("saved dummy_sampled_final_lowk.png", DEBUG_HEAD)

                # print(ks[:, -1])

                plt.clf()
                plt.plot(scores_std[:3, :].float().cpu().numpy().T)
                # plt.ylim(0, 0.01)
                plt.savefig("dummy_stat_std.png")
                plt.clf()
                plt.plot(scores_mean[:3, :].float().cpu().numpy().T)
                plt.savefig("dummy_stat_mean.png")
                plt.clf()
                plt.plot(ks[DEBUG_HEAD, :].float().cpu().numpy())
                plt.savefig("dummy_stat_ks.png")

        if (
            DEBUG
            and DEBUG_RENDER
            and not torch.cuda.is_current_stream_capturing()
            and (BDST > 10)
            and get_local_rank() == 0
        ):
            try:
                input(f"[{args.layer_id}] >")
            except EOFError:
                print()

        # NOTE: break-down to fit BSA block size
        if (block_sparse_block_size_q is not None) and (
            triton.cdiv(TDST, block_sparse_block_size_q)
            != triton.cdiv(TDST, args.block_size_q)
        ):
            assert (BLOCK_SIZE_Q % block_sparse_block_size_q) == 0
            indices = indices.repeat_interleave(
                BLOCK_SIZE_Q // block_sparse_block_size_q, 1
            )
            ks = ks.repeat_interleave(BLOCK_SIZE_Q // block_sparse_block_size_q, 1)
            ks_count = ks_count.repeat_interleave(
                BLOCK_SIZE_Q // block_sparse_block_size_q, 1
            )
            ks_start_end = ks_start_end.repeat_interleave(
                BLOCK_SIZE_Q // block_sparse_block_size_q, 1
            )
            args.block_size_q = block_sparse_block_size_q

        if args.mask_only:
            return None, None
    else:
        args = args.clone()
        args.sliding_window_size += args.mask_k
        args.block_size_k = args.stages[-1].stage_chunk_size
        args.mask_k = args.second_stage_k
        args.using_extend = args.using_extend and True

        assert cached_metadata is not None
        require_cache_clone = False
        if require_cache_clone:
            indices = cached_metadata.indices.clone()
            ks = cached_metadata.ks.clone()
            ks_count = cached_metadata.ks_count.clone()
            ks_start_end = cached_metadata.ks_start_end.clone()
        else:
            indices = cached_metadata.indices
            ks = cached_metadata.ks
            ks_count = cached_metadata.ks_count
            ks_start_end = cached_metadata.ks_start_end

    args.block_size_q = min(args.block_size_q, triton.next_power_of_2(TDST))

    if args.sliding_window_size == 777:
        args.sliding_window_size = (
            args.model_context_length
            - args.sink_token_size
            - args.second_stage_k
            - args.block_size_q
        )
    elif args.sliding_window_size > 0:
        args.sliding_window_size += args.block_size_q

    if flatten_paged_cache:
        k = None
        v = None

    block_sparse_attention_backend = get_block_sparse_backend(
        q_bsa, args.disable_flashdecode
    )
    # from hip_attn.v1_2.attention_extend_bsa_tilelang import block_sparse_attention as tilelang_bsa
    # block_sparse_attention_backend = tilelang_bsa

    if args.bsa_sliding_window_size > 0:
        args = args.clone()
        args.sliding_window_size = args.bsa_sliding_window_size

    context = block_sparse_attention_backend(
        q=q_bsa,
        k=k,
        v=v,
        seq_lens=position_ids[:, -q_bsa.shape[1] :] + 1,
        indices=indices,
        ks=ks,
        ks_count=ks_count,
        ks_start_end=ks_start_end,
        args=args,
        access_counter=sa_access_counter,
        cache_miss_counter=sa_cache_miss_counter,
        EXTEND_BACKEND=args.sa_extend_backend,  # streaming works way much better in Gemma2, than dynamic_extend
        model_context_length=args.model_context_length,
        extend_context_length=args.extend_context_length,
        offload_update_cache=(cached_metadata is None) and args.online_update_cache,
        return_running_statistics=args.bsa_return_running_statistics,
        k_descale=args.k_descale,
        v_descale=args.v_descale,
        # offload_update_cache=args.online_update_cache,
        # offload_update_cache=False,
    )
    if args.offload_cache is not None:
        args.offload_cache.sa_kv_cache.verify_cache()

    # if DEBUG:
    #     print('context', context[0, :, DEBUG_HEAD, :], context.shape)
    #     print('indices', indices[0 + DEBUG_HEAD, -1], indices.shape)
    #     print('ks', ks[0 + DEBUG_HEAD, -1], ks.shape)

    metadata = HiPAttentionOutputMetadata(
        indices=indices,
        ks=ks,
        ks_count=ks_count,
        ks_start_end=ks_start_end,
        mask_cache_statistics=(
            HiPAttentionCacheAccessStatistics(
                access_counter=mask_access_counter,
                cache_miss_counter=mask_cache_miss_counter,
            )
            if (cached_metadata is None) or (cached_metadata.indices is None)
            else None
        ),
        sa_cache_statistics=HiPAttentionCacheAccessStatistics(
            access_counter=sa_access_counter,
            cache_miss_counter=sa_cache_miss_counter,
        ),
        stage_caches=stage_caches,
        state=state,
    )

    # if BDST > 1:
    #     print(id(metadata), type(state))

    return context, metadata
