import os
import random
import time
from typing import Any, Callable, List, MutableMapping, Optional, Tuple, Union
import torch
import fms.utils.spyre.paged  # noqa


def adjust_inputs_to_batch(input_ids: torch.Tensor, **extra_kwargs):
    """
    Adjusts the inputs to a batch. Batch size 1 cannot be handled since we want a symbolic shape for the batch
    and pytorch automatically sets size 1 dimensions as static

    Note: This is fixed in pytorch 2.7
    """
    input_ids = input_ids[0].repeat(2, 1)
    # ensure we pass along other kwargs
    kwargs = {**extra_kwargs}
    mask = extra_kwargs.get("mask", None)
    if mask is not None:
        kwargs["mask"] = torch.stack((mask[0], mask[0]))
    position_ids = extra_kwargs.get("position_ids", None)
    if position_ids is not None:
        kwargs["position_ids"] = position_ids[0].repeat(2, 1)
    return input_ids, kwargs


# FIXME: We should use default generate, but that will require a larger re-work of generate
def generate(
    model: Union[Callable, torch.nn.Module],
    input_ids: torch.Tensor,
    max_new_tokens: int = 256,
    temperature: float = 1.0,
    top_k: int = 10,
    do_sample: bool = True,
    num_beams: int = 1,
    use_cache: bool = False,
    eos_token_id: Optional[int] = None,
    timing: str = "",
    post_iteration_hook: Optional[
        Callable[
            [int, torch.Tensor, torch.Tensor, MutableMapping[str, Any]],
            Tuple[torch.Tensor, MutableMapping[str, Any]],
        ]
    ] = None,
    extra_kwargs: Optional[MutableMapping[str, Any]] = None,
):
    """
    A trivial generate function that can be used for validation/testing in
    cases where HF is not available.
    We could add implementations for other types of generation, but this is
    enough for making sure a model is working.
    Does not implement beam search, but this can be added.

    Args:
        model: A function or nn.Module that takes a batch of input_ids and
            returns logits
        input_ids: a rectangular tensor of input_ids (batch x seq)
        max_new_tokens: max tokens to generate
        temperature: temperature of softmax when sampling
        top_k: only search among top k tokens
        do_sample: multinomial sampling. False for greedy.
        num_beams: TODO: support beam search
        use_cache: requires that the model accept use_cache and
            past_key_value_states args in forward method.
        contiguous_cache: ensures the cache is contiguous in device memory
        eos_token_id: the optional token id representing the end of sequence
        timing: whether to measure timings: "per-token" for each token generation time,
            "e2e" for full generation loop. Both options make `generate` return a tuple
            with the following information:
            - "per-token": Array with `max_new_tokens` time measurements (in s)
            - "e2e": Array with a single e2e generation loop time measurement (in s)
        post_iteration_hook: a function that will get called after each iteration.
            It must have the following signature: f(int token_position, Tensor logits, Tensor next_val, Dict kwargs) ->
            Tuple[Tensor next_val, Dict kwargs]. If it is defined, will replace next_val
            and kwargs based on the contents of the function.
        extra_kwargs: an optional mapping of additional kwargs to pass to the model.
            For example: if extra_kwargs contains position_ids and mask keys, these
            model parameters will be updated as-appropriate for each token generated.
    """
    random.seed(0)
    if num_beams != 1:
        raise NotImplementedError("generate() does yet not support beam search")

    kwargs: MutableMapping[str, Any] = dict()
    if extra_kwargs is not None:
        kwargs.update(extra_kwargs)

    # if we didn't specify last_n_tokens and only_last_token is set to True, set last_n_tokens to 1, otherwise use default
    # we do this since the output shape of only_last_token is different and therefore would change the logic in generate
    if "last_n_tokens" not in kwargs and kwargs.get("only_last_token", False):
        kwargs["last_n_tokens"] = 1

    is_fp8 = "fp8" in kwargs["attn_name"]
    if isinstance(input_ids, torch.Tensor):
        if len(input_ids.shape) == 1:
            input_ids = input_ids.unsqueeze(0)

        is_batch = input_ids.shape[0] > 1
        # our model requires batch dimension when running with fp8
        # this is fixed in torch >= 2.8
        if is_fp8 and not is_batch:
            input_ids, kwargs = adjust_inputs_to_batch(input_ids, **kwargs)
    else:
        raise TypeError("input_ids must be one of Tensor or List")

    if not hasattr(model, "config"):
        raise ValueError("model must have a config")

    eos_found = torch.zeros(
        input_ids.shape[0], dtype=torch.bool, device=input_ids.device
    )

    result = input_ids
    next_input = input_ids
    # this includes empty pages and max_new_tokens
    max_possible_context_length = input_ids.size(1) + max_new_tokens

    BLOCK_SIZE = 64

    # these variables are guaranteed to be set in another location (inference.py, test_decoders.py, etc.)
    # if we set these variables here, we run the risk of warming up and generating with different sizes
    _MAX_BATCH = int(os.environ["VLLM_DT_MAX_BATCH_SIZE"])
    _MAX_CONTEXT_LENGTH = int(os.environ["VLLM_DT_MAX_CONTEXT_LEN"])
    # if the user provides a hint to the number of blocks to use, use it directly
    NUM_BLOCKS = kwargs.get(
        "_kvcache_num_blocks_hint", (_MAX_BATCH * _MAX_CONTEXT_LENGTH) // BLOCK_SIZE
    )

    if hasattr(model, "head"):
        model_dtype = model.head.weight.dtype
    elif hasattr(model, "shared"):
        # TODO: Rework the llama model (should be able to use head instead of shared)
        model_dtype = model.shared.head.weight.dtype
    else:
        model_dtype = torch.float32

    nheads = model.config.nheads
    if hasattr(model.config, "kvheads"):
        kvheads = model.config.kvheads
    elif hasattr(model.config, "multiquery_attn"):
        kvheads = 1 if model.config.multiquery_attn else model.config.nheads
    else:
        kvheads = nheads

    if hasattr(model, "distributed_strategy"):
        tensor_parallel_size = (
            model.distributed_strategy.group.size()
            if hasattr(model.distributed_strategy, "group")
            else 1
        )
    else:
        raise ValueError("model must have a distributed_strategy")

    kvheads = kvheads // tensor_parallel_size if kvheads > 1 else kvheads
    head_size = model.config.emb_dim // nheads
    if "fp8" in kwargs["attn_name"]:
        from fms_mo.aiu_addons.fp8.fp8_utils import ScaledTensor

        kwargs["past_key_value_states"] = [
            (
                ScaledTensor(
                    torch.zeros(
                        NUM_BLOCKS,
                        BLOCK_SIZE,
                        kvheads,
                        head_size,
                        dtype=torch.float8_e4m3fn,
                    ),
                    torch.tensor([1.0] * input_ids.shape[0], dtype=torch.float32),
                    False,
                ),
                ScaledTensor(
                    torch.zeros(
                        NUM_BLOCKS,
                        BLOCK_SIZE,
                        kvheads,
                        head_size,
                        dtype=torch.float8_e4m3fn,
                    ),
                    torch.tensor([1.0] * input_ids.shape[0], dtype=torch.float32),
                    False,
                ),
            )
            for _ in range(model.config.nlayers)
        ]
    else:
        kwargs["past_key_value_states"] = [
            (
                torch.zeros(
                    NUM_BLOCKS, BLOCK_SIZE, kvheads, head_size, dtype=model_dtype
                ),
                torch.zeros(
                    NUM_BLOCKS, BLOCK_SIZE, kvheads, head_size, dtype=model_dtype
                ),
            )
            for _ in range(model.config.nlayers)
        ]
    kwargs["block_table"] = None
    block_numbers = [i for i in range(NUM_BLOCKS)]
    # this will ensure we don't have contiguous blocks
    random.shuffle(block_numbers)

    # this is the true number of left pads when computing paged attention using a paged kv-cache
    # it may include whole empty pages
    left_padded_prompt_mask = (kwargs["position_ids"] == 0).sum(dim=1) - 1

    # this is the context length for each sequence without pads
    context_lengths_without_pads = (kwargs["position_ids"] != 0).sum(dim=1) + 1

    # this is the context length for each sequence with no empty pages (padded to multiple of 64)
    context_lengths = BLOCK_SIZE * (
        (context_lengths_without_pads + BLOCK_SIZE - 1) // BLOCK_SIZE
    )

    # left_padded_prompt_mask - empty_slots + context_lengths
    current_tkv_mask = torch.fill(context_lengths, input_ids.shape[1])

    slot_mapping = []
    block_table = []
    # each sequence has the possibility of a different tkv, so loop over that
    for seq_tkv in context_lengths:
        block_table_i = [block_numbers.pop(0) for _ in range(seq_tkv // BLOCK_SIZE)]
        # pad block_table_i for the real padded length
        block_table_i = [block_table_i[0]] * (
            (input_ids.shape[1] - seq_tkv) // BLOCK_SIZE
        ) + block_table_i
        slot_mapping_i = []
        for pos_i in range(input_ids.shape[1] - seq_tkv, input_ids.shape[1]):
            # we may have already popped a block, so index to the proper block
            block_number = block_table_i[pos_i // BLOCK_SIZE]

            block_offset = pos_i % BLOCK_SIZE
            slot = block_number * BLOCK_SIZE + block_offset
            slot_mapping_i.append(slot)
        slot_mapping.append(slot_mapping_i)
        block_table.append(block_table_i)
    kwargs["current_tkv_mask"] = None
    kwargs["left_padded_prompt_mask"] = None
    kwargs["use_cache"] = use_cache
    last_n_tokens = kwargs.get("last_n_tokens", 0)

    prompt_length = input_ids.shape[1]

    if timing != "":
        times: List[float] = []
        start_time = time.time()

    for i in range(max_new_tokens):
        input_ids = next_input[:, -max_possible_context_length:]

        # prefill
        if i == 0:
            kwargs["mask"] = kwargs["mask"].unsqueeze(1)

            outputs_list = []
            current_kv_cache = kwargs["past_key_value_states"]

            if "fp8" in kwargs["attn_name"]:
                current_kv_scales = [
                    (t1._scale, t2._scale) for t1, t2 in kwargs["past_key_value_states"]
                ]
            for seq_i, current_tkv in enumerate(context_lengths):
                # remove extra pads from the input_ids, slot_mapping, position_ids, mask to account for empty pages
                # each input should be padded to its smallest multiple of BLOCK_SIZE (64)
                # we need to clone these tensors to ensure the pointer offset is 0
                input_ids_i = input_ids[seq_i][-current_tkv:].unsqueeze(0).clone()
                slot_mapping_i = (
                    torch.tensor(slot_mapping[seq_i][-current_tkv:], dtype=torch.int64)
                    .unsqueeze(0)
                    .clone()
                )
                position_ids_i = (
                    kwargs["position_ids"][seq_i][-current_tkv:].unsqueeze(0).clone()
                )

                # This view will result in a discontiguous tensor (creates a new graph during compile)
                # For this reason, we must explicitly make contiguous
                mask_i = (
                    kwargs["mask"][seq_i][:, -current_tkv:, -current_tkv:]
                    .unsqueeze(0)
                    .contiguous()
                )

                # batch dynamic
                torch._dynamo.mark_static(input_ids_i, 0)
                torch._dynamo.mark_static(slot_mapping_i, 0)
                torch._dynamo.mark_static(position_ids_i, 0)
                torch._dynamo.mark_static(mask_i, 0)

                # seq dynamic
                torch._dynamo.mark_dynamic(input_ids_i, 1)
                torch._dynamo.mark_dynamic(slot_mapping_i, 1)
                torch._dynamo.mark_dynamic(position_ids_i, 1)
                torch._dynamo.mark_dynamic(mask_i, 2)
                torch._dynamo.mark_dynamic(mask_i, 3)

                # FP8 per-sentence scale handling
                if "fp8" in kwargs["attn_name"]:
                    for layer_idx, (t1, t2) in enumerate(current_kv_cache):
                        t1._scale = current_kv_scales[layer_idx][0][seq_i].reshape(-1)
                        t2._scale = current_kv_scales[layer_idx][1][seq_i].reshape(-1)

                last_n_tokens = kwargs.get("last_n_tokens", 0)
                output, current_kv_cache = model(
                    input_ids_i,
                    slot_mapping=slot_mapping_i,
                    position_ids=position_ids_i,
                    mask=mask_i,
                    past_key_value_states=current_kv_cache,
                    use_cache=kwargs["use_cache"],
                    last_n_tokens=last_n_tokens,
                    attn_name=kwargs["attn_name"],
                )

                # only last token must be handled here to properly stack the tensors
                output = output[:, -1, :]

                # TODO: Figure out how to do this cleanly
                if "fp8" in kwargs["attn_name"]:
                    for layer_idx, (t1, t2) in enumerate(current_kv_cache):
                        current_kv_scales[layer_idx][0][seq_i] = t1._scale
                        current_kv_scales[layer_idx][1][seq_i] = t2._scale

                    if seq_i != input_ids.size(0) - 1:
                        for layer_cache in current_kv_cache:
                            layer_cache[0]._scaled = False
                            layer_cache[1]._scaled = False
                    else:
                        for layer_idx, (t1, t2) in enumerate(current_kv_cache):
                            t1._scale = current_kv_scales[layer_idx][0]
                            t2._scale = current_kv_scales[layer_idx][1]

                outputs_list.append(output[0].squeeze(0))

            output = (torch.stack(outputs_list), current_kv_cache)
        # decode
        else:
            # prepare any padding keyword arguments
            # iteration 0 is the prefill step (cache has not been filled yet), so no need to extend the mask/position_ids

            # mask is no longer used here
            kwargs["mask"] = None
            kwargs["position_ids"] = kwargs["position_ids"][:, -1:] + 1
            kwargs["position_ids"] = kwargs["position_ids"].clone(
                memory_format=torch.contiguous_format
            )
            kwargs["last_n_tokens"] = 1

            # we no longer have a global pos_i, each sequence has its own pos_i
            slot_mapping = []
            for seq_i, pos_i in enumerate(current_tkv_mask):
                if pos_i % BLOCK_SIZE == 0:
                    block_number = block_numbers.pop(0)
                    block_table[seq_i].append(block_number)

                block_offset = pos_i % BLOCK_SIZE
                slot = block_table[seq_i][-1] * BLOCK_SIZE + block_offset
                slot_mapping.append([slot])

            kwargs["block_table"] = torch.tensor(
                [
                    (
                        [b_seq[0]]
                        * (
                            max(2 if is_fp8 else 1, max([len(b) for b in block_table]))
                            - len(b_seq)
                        )
                    )
                    + b_seq
                    for b_seq in block_table
                ],
                dtype=torch.int64,
            )
            kwargs["left_padded_prompt_mask"] = left_padded_prompt_mask
            current_tkv_mask = current_tkv_mask + 1
            kwargs["current_tkv_mask"] = current_tkv_mask
            kwargs["slot_mapping"] = torch.tensor(slot_mapping, dtype=torch.int64)

            # batch
            input_ids = input_ids.clone(memory_format=torch.contiguous_format)
            torch._dynamo.mark_dynamic(input_ids, 0)
            torch._dynamo.mark_dynamic(kwargs["block_table"], 0)
            torch._dynamo.mark_dynamic(kwargs["slot_mapping"], 0)
            torch._dynamo.mark_dynamic(kwargs["position_ids"], 0)
            torch._dynamo.mark_dynamic(kwargs["current_tkv_mask"], 0)
            torch._dynamo.mark_dynamic(kwargs["left_padded_prompt_mask"], 0)
            if "fp8" in kwargs["attn_name"]:
                for k_cache, v_cache in kwargs["past_key_value_states"]:
                    torch._dynamo.mark_dynamic(k_cache._scale, 0)
                    torch._dynamo.mark_dynamic(v_cache._scale, 0)

            # seq
            torch._dynamo.mark_static(input_ids, 1)  # always 1
            torch._dynamo.mark_dynamic(kwargs["block_table"], 1)
            torch._dynamo.mark_static(kwargs["slot_mapping"], 1)  # always 1
            torch._dynamo.mark_static(kwargs["position_ids"], 1)  # always 1

            logits, past_key_value_states = model(input_ids, **kwargs)

            # typically this is done outside of prefill/decode logic, but since this logic already exists as part of the
            # conditional for prefill (since prefill does this within a loop for each batch size 1 prefill), we also provide
            # this same logic as part of the decode conditional
            logits = logits[:, -1, :]

            output = (logits, past_key_value_states)

        if use_cache:
            logits, past_key_value_states = output
            # TODO: this should go away when reduce-overhead issues are fixed, or
            # maybe could be moved into model code to be more portable.
            kwargs["past_key_value_states"] = past_key_value_states
        else:
            logits = output

        if do_sample:
            # get logits from last value in sequence nad scale
            logits = logits / temperature
            if top_k:
                v, _ = torch.topk(logits, top_k)
                logits[logits < v[:, [-1]]] = -float("inf")

            probs = F.softmax(logits, dim=-1)  # noqa: F821
            next_val = torch.multinomial(probs, num_samples=1)
        else:
            next_val = torch.argmax(logits, dim=-1).unsqueeze(0).t()

        if post_iteration_hook is not None:
            _logits = logits
            _next_val = next_val
            # since we cannot handle batch size 1 for fp8 and mimic with batch size 2, we need to only pass in the first logits/next_val
            if is_fp8 and not is_batch:
                _logits = logits[0].unsqueeze(0)
                _next_val = _next_val[0].unsqueeze(0)
            _next_val, kwargs = post_iteration_hook(
                i + prompt_length, _logits, _next_val, kwargs
            )
            # we need to normalize back to batch size 2
            if is_fp8 and not is_batch:
                # we need to do an in-place copy here for the same reason we do in-place copy for injecting tokens
                next_val.copy_(torch.cat((_next_val, _next_val), dim=0))
            else:
                next_val = _next_val

        result = torch.cat((result, next_val), dim=-1)

        # avoid continuing to generate if all have reached EOS
        if eos_token_id is not None:
            eos_found = torch.logical_or(eos_found, next_val == eos_token_id)
            if torch.sum(eos_found) == input_ids.shape[0]:
                break

        if use_cache:
            next_input = next_val
        else:
            next_input = result

        if timing == "per-token":
            if input_ids.device.type == "cuda":
                torch.cuda.synchronize()
            current_token_time = time.time() - start_time
            times.append(current_token_time)
            start_time = time.time()

    if timing == "e2e":
        if input_ids.device.type == "cuda":
            torch.cuda.synchronize()
        e2e_time = time.time() - start_time
        times.append(e2e_time)

    if not is_batch:
        result = result[0]

    if timing != "":
        return result, times
    return result


# this value is default to 2080 to be consistent with vllm for granite 3.3 8b instruct
KVCACHE_NUM_BLOCKS_HINT = int(
    os.environ.get("AFTU_PAGED_KVCACHE_NUM_BLOCKS_HINT", 2080)
)

VLLM_DT_MAX_BATCH_TKV_LIMIT = int(os.environ.get("VLLM_DT_MAX_BATCH_TKV_LIMIT", 131072))


class ProgramCriteria:
    def __init__(
        self, program_id, max_batch, max_tkv, batch_granularity, tkv_granularity
    ):
        self.program_id = program_id
        self.max_batch = max_batch
        self.max_tkv = max_tkv
        self.batch_granularity = batch_granularity
        self.tkv_granularity = tkv_granularity

    def is_possible(self, batch_size, tkv):
        return (
            (batch_size * tkv <= VLLM_DT_MAX_BATCH_TKV_LIMIT)
            and (batch_size <= self.max_batch)
            and (tkv <= self.max_tkv)
        )

    def calculate_padding(self, batch_size, tkv):
        min_batch_req = (
            ((batch_size - 1) // self.batch_granularity) + 1
        ) * self.batch_granularity
        min_tkv_req = (((tkv - 1) // self.tkv_granularity) + 1) * self.tkv_granularity
        return (min_batch_req * min_tkv_req) - (batch_size * tkv)

    def __str__(self):
        return f"ProgramCriteria(program_id={self.program_id})"

    def __eq__(self, other):
        if not isinstance(other, ProgramCriteria):
            return NotImplemented
        return (
            self.program_id == other.program_id
            and self.max_batch == other.max_batch
            and self.max_tkv == other.max_tkv
            and self.batch_granularity == other.batch_granularity
            and self.tkv_granularity == other.tkv_granularity
        )

    def __hash__(self):
        return hash(self.program_id)  # Hash based on immutable attributes


def get_programs_prompts(
    program_criteria_list,
    multiple,
    max_batch_size,
    max_tkv,
    program_cycles,
    prioritize_large_batch_sizes=True,
):
    program_map = {}

    for batch_size in range(1, max_batch_size + 1):
        for prompt_len in range(multiple, max_tkv - program_cycles, multiple):
            possible_program_switches = ((program_cycles - 1) // multiple) + 1
            resolved_programs = [None] * possible_program_switches
            for program_criteria in program_criteria_list:
                for program_index in range(possible_program_switches):
                    context_length = prompt_len + (multiple * program_index) + 1

                    if program_criteria.is_possible(batch_size, context_length):
                        padding = program_criteria.calculate_padding(
                            batch_size, context_length
                        )
                        if (
                            resolved_programs[program_index] is None
                            or padding < resolved_programs[program_index][1]
                            or (
                                padding == resolved_programs[program_index][1]
                                and program_criteria.batch_granularity
                                > resolved_programs[program_index][0].batch_granularity
                            )
                        ):
                            resolved_programs[program_index] = (
                                program_criteria,
                                padding,
                            )

            if all(p is not None for p in resolved_programs):
                key = tuple(p[0] for p in resolved_programs)
                if key in program_map:
                    program_map[key].append((batch_size, prompt_len))
                else:
                    program_map[key] = [(batch_size, prompt_len)]

    # give higher priority to larger batches
    for _, v in program_map.items():
        v.sort(key=lambda t: t[0], reverse=prioritize_large_batch_sizes)

    return program_map
