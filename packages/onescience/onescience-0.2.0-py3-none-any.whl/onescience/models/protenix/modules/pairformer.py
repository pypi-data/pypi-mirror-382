# pylint: disable=C0114
from functools import partial
from typing import Any, Optional

import torch
import torch.nn as nn

from onescience.models.protenix.modules.primitives import LinearNoBias, Transition
from onescience.models.protenix.modules.transformer import AttentionPairBias
from onescience.models.protenix.utils import pad_at_dim, sample_msa_feature_dict_random_without_replacement
from onescience.models.openfold.dropout import DropoutRowwise
from onescience.models.openfold.outer_product_mean import (
    OuterProductMean,  # Alg 9 in AF3
)
from onescience.models.openfold.primitives import LayerNorm
from onescience.models.openfold.triangular_attention import TriangleAttention
from onescience.models.openfold.triangular_multiplicative_update import (
    TriangleMultiplicationIncoming,  # Alg 13 in AF3
)
from onescience.models.openfold.triangular_multiplicative_update import (
    TriangleMultiplicationOutgoing,  # Alg 12 in AF3
)
from onescience.utils.openfold.checkpointing import checkpoint_blocks, get_checkpoint_fn


class PairformerBlock(nn.Module):
    """Implements Algorithm 17 [Line2-Line8] in AF3
    c_hidden_mul is set as openfold
    Ref to:
    https://github.com/aqlaboratory/openfold/blob/feb45a521e11af1db241a33d58fb175e207f8ce0/openfold/model/evoformer.py#L123
    """

    def __init__(
        self,
        n_heads: int = 16,
        c_z: int = 128,
        c_s: int = 384,
        c_hidden_mul: int = 128,
        c_hidden_pair_att: int = 32,
        no_heads_pair: int = 4,
        dropout: float = 0.25,
    ) -> None:
        """
        Args:
            n_heads (int, optional): number of head [for AttentionPairBias]. Defaults to 16.
            c_z (int, optional): hidden dim [for pair embedding]. Defaults to 128.
            c_s (int, optional):  hidden dim [for single embedding]. Defaults to 384.
            c_hidden_mul (int, optional): hidden dim [for TriangleMultiplicationOutgoing].
                Defaults to 128.
            c_hidden_pair_att (int, optional): hidden dim [for TriangleAttention]. Defaults to 32.
            no_heads_pair (int, optional): number of head [for TriangleAttention]. Defaults to 4.
            dropout (float, optional): dropout ratio [for TriangleUpdate]. Defaults to 0.25.
        """
        super(PairformerBlock, self).__init__()
        self.n_heads = n_heads
        self.tri_mul_out = TriangleMultiplicationOutgoing(
            c_z=c_z, c_hidden=c_hidden_mul
        )
        self.tri_mul_in = TriangleMultiplicationIncoming(c_z=c_z, c_hidden=c_hidden_mul)
        self.tri_att_start = TriangleAttention(
            c_in=c_z,
            c_hidden=c_hidden_pair_att,
            no_heads=no_heads_pair,
        )
        self.tri_att_end = TriangleAttention(
            c_in=c_z,
            c_hidden=c_hidden_pair_att,
            no_heads=no_heads_pair,
        )
        self.dropout_row = DropoutRowwise(dropout)
        self.pair_transition = Transition(c_in=c_z, n=4)
        self.c_s = c_s
        if self.c_s > 0:
            self.attention_pair_bias = AttentionPairBias(
                has_s=False, create_offset_ln_z=True, n_heads=n_heads, c_a=c_s, c_z=c_z
            )
            self.single_transition = Transition(c_in=c_s, n=4)

    def forward(
        self,
        s: Optional[torch.Tensor],
        z: torch.Tensor,
        pair_mask: torch.Tensor,
        use_memory_efficient_kernel: bool = False,
        use_deepspeed_evo_attention: bool = False,
        use_lma: bool = False,
        inplace_safe: bool = False,
        chunk_size: Optional[int] = None,
    ) -> tuple[Optional[torch.Tensor], torch.Tensor]:
        """
        Forward pass of the PairformerBlock.

        Args:
            s (Optional[torch.Tensor]): single feature
                [..., N_token, c_s]
            z (torch.Tensor): pair embedding
                [..., N_token, N_token, c_z]
            pair_mask (torch.Tensor): pair mask
                [..., N_token, N_token]
            use_memory_efficient_kernel (bool): Whether to use memory-efficient kernel. Defaults to False.
            use_deepspeed_evo_attention (bool): Whether to use DeepSpeed evolutionary attention. Defaults to False.
            use_lma (bool): Whether to use low-memory attention. Defaults to False.
            inplace_safe (bool): Whether it is safe to use inplace operations. Defaults to False.
            chunk_size (Optional[int]): Chunk size for memory-efficient operations. Defaults to None.

        Returns:
            tuple[Optional[torch.Tensor], torch.Tensor]: the update of s[Optional] and z
                [..., N_token, c_s] | None
                [..., N_token, N_token, c_z]
        """
        if inplace_safe:
            z = self.tri_mul_out(
                z, mask=pair_mask, inplace_safe=inplace_safe, _add_with_inplace=True
            )
            z = self.tri_mul_in(
                z, mask=pair_mask, inplace_safe=inplace_safe, _add_with_inplace=True
            )
            z += self.tri_att_start(
                z,
                mask=pair_mask,
                use_memory_efficient_kernel=use_memory_efficient_kernel,
                use_deepspeed_evo_attention=use_deepspeed_evo_attention,
                use_lma=use_lma,
                inplace_safe=inplace_safe,
                chunk_size=chunk_size,
            )
            z = z.transpose(-2, -3).contiguous()
            z += self.tri_att_end(
                z,
                mask=pair_mask.transpose(-1, -2) if pair_mask is not None else None,
                use_memory_efficient_kernel=use_memory_efficient_kernel,
                use_deepspeed_evo_attention=use_deepspeed_evo_attention,
                use_lma=use_lma,
                inplace_safe=inplace_safe,
                chunk_size=chunk_size,
            )
            z = z.transpose(-2, -3).contiguous()
            z += self.pair_transition(z)
        else:
            tmu_update = self.tri_mul_out(
                z, mask=pair_mask, inplace_safe=inplace_safe, _add_with_inplace=False
            )
            z = z + self.dropout_row(tmu_update)
            del tmu_update
            tmu_update = self.tri_mul_in(
                z, mask=pair_mask, inplace_safe=inplace_safe, _add_with_inplace=False
            )
            z = z + self.dropout_row(tmu_update)
            del tmu_update
            z = z + self.dropout_row(
                self.tri_att_start(
                    z,
                    mask=pair_mask,
                    use_memory_efficient_kernel=use_memory_efficient_kernel,
                    use_deepspeed_evo_attention=use_deepspeed_evo_attention,
                    use_lma=use_lma,
                    inplace_safe=inplace_safe,
                    chunk_size=chunk_size,
                )
            )
            z = z.transpose(-2, -3)
            z = z + self.dropout_row(
                self.tri_att_end(
                    z,
                    mask=pair_mask.transpose(-1, -2) if pair_mask is not None else None,
                    use_memory_efficient_kernel=use_memory_efficient_kernel,
                    use_deepspeed_evo_attention=use_deepspeed_evo_attention,
                    use_lma=use_lma,
                    inplace_safe=inplace_safe,
                    chunk_size=chunk_size,
                )
            )
            z = z.transpose(-2, -3)

            z = z + self.pair_transition(z)
        if self.c_s > 0:
            s = s + self.attention_pair_bias(
                a=s,
                s=None,
                z=z,
            )
            s = s + self.single_transition(s)
        return s, z


class PairformerStack(nn.Module):
    """
    Implements Algorithm 17 [PairformerStack] in AF3
    """

    def __init__(
        self,
        n_blocks: int = 48,
        n_heads: int = 16,
        c_z: int = 128,
        c_s: int = 384,
        dropout: float = 0.25,
        blocks_per_ckpt: Optional[int] = None,
    ) -> None:
        """
        Args:
            n_blocks (int, optional): number of blocks [for PairformerStack]. Defaults to 48.
            n_heads (int, optional): number of head [for AttentionPairBias]. Defaults to 16.
            c_z (int, optional): hidden dim [for pair embedding]. Defaults to 128.
            c_s (int, optional):  hidden dim [for single embedding]. Defaults to 384.
            dropout (float, optional): dropout ratio. Defaults to 0.25.
            blocks_per_ckpt: number of Pairformer blocks in each activation checkpoint
                Size of each chunk. A higher value corresponds to fewer
                checkpoints, and trades memory for speed. If None, no checkpointing
                is performed.
        """
        super(PairformerStack, self).__init__()
        self.n_blocks = n_blocks
        self.n_heads = n_heads
        self.blocks_per_ckpt = blocks_per_ckpt
        self.blocks = nn.ModuleList()

        for _ in range(n_blocks):
            block = PairformerBlock(n_heads=n_heads, c_z=c_z, c_s=c_s, dropout=dropout)
            self.blocks.append(block)

    def _prep_blocks(
        self,
        pair_mask: Optional[torch.Tensor],
        use_memory_efficient_kernel: bool = False,
        use_deepspeed_evo_attention: bool = False,
        use_lma: bool = False,
        inplace_safe: bool = False,
        chunk_size: Optional[int] = None,
        clear_cache_between_blocks: bool = False,
    ):
        blocks = [
            partial(
                b,
                pair_mask=pair_mask,
                use_memory_efficient_kernel=use_memory_efficient_kernel,
                use_deepspeed_evo_attention=use_deepspeed_evo_attention,
                use_lma=use_lma,
                inplace_safe=inplace_safe,
                chunk_size=chunk_size,
            )
            for b in self.blocks
        ]

        def clear_cache(b, *args, **kwargs):
            torch.cuda.empty_cache()
            return b(*args, **kwargs)

        if clear_cache_between_blocks:
            blocks = [partial(clear_cache, b) for b in blocks]
        return blocks

    def forward(
        self,
        s: torch.Tensor,
        z: torch.Tensor,
        pair_mask: torch.Tensor,
        use_memory_efficient_kernel: bool = False,
        use_deepspeed_evo_attention: bool = False,
        use_lma: bool = False,
        inplace_safe: bool = False,
        chunk_size: Optional[int] = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            s (Optional[torch.Tensor]): single feature
                [..., N_token, c_s]
            z (torch.Tensor): pair embedding
                [..., N_token, N_token, c_z]
            pair_mask (torch.Tensor): pair mask
                [..., N_token, N_token]
            use_memory_efficient_kernel (bool): Whether to use memory-efficient kernel. Defaults to False.
            use_deepspeed_evo_attention (bool): Whether to use DeepSpeed evolutionary attention. Defaults to False.
            use_lma (bool): Whether to use low-memory attention. Defaults to False.
            inplace_safe (bool): Whether it is safe to use inplace operations. Defaults to False.
            chunk_size (Optional[int]): Chunk size for memory-efficient operations. Defaults to None.

        Returns:
            tuple[torch.Tensor, torch.Tensor]: the update of s and z
                [..., N_token, c_s]
                [..., N_token, N_token, c_z]
        """
        if z.shape[-2] > 2000 and (not self.training):
            clear_cache_between_blocks = True
        else:
            clear_cache_between_blocks = False
        blocks = self._prep_blocks(
            pair_mask=pair_mask,
            use_memory_efficient_kernel=use_memory_efficient_kernel,
            use_deepspeed_evo_attention=use_deepspeed_evo_attention,
            use_lma=use_lma,
            inplace_safe=inplace_safe,
            chunk_size=chunk_size,
            clear_cache_between_blocks=clear_cache_between_blocks,
        )

        blocks_per_ckpt = self.blocks_per_ckpt
        if not torch.is_grad_enabled():
            blocks_per_ckpt = None
        s, z = checkpoint_blocks(
            blocks,
            args=(s, z),
            blocks_per_ckpt=blocks_per_ckpt,
        )
        return s, z


class MSAPairWeightedAveraging(nn.Module):
    """
    Implements Algorithm 10 [MSAPairWeightedAveraging] in AF3
    """

    def __init__(self, c_m: int = 64, c: int = 32, c_z: int = 128, n_heads=8) -> None:
        """

        Args:
            c_m (int, optional): hidden dim [for msa embedding]. Defaults to 64.
            c (int, optional): hidden [for MSAPairWeightedAveraging] dim. Defaults to 32.
            c_z (int, optional): hidden dim [for pair embedding]. Defaults to 128.
            n_heads (int, optional): number of heads [for MSAPairWeightedAveraging]. Defaults to 8.
        """
        super(MSAPairWeightedAveraging, self).__init__()
        self.c_m = c_m
        self.c = c
        self.n_heads = n_heads
        self.c_z = c_z
        # Input projections
        self.layernorm_m = LayerNorm(self.c_m)
        self.linear_no_bias_mv = LinearNoBias(
            in_features=self.c_m, out_features=self.c * self.n_heads
        )
        self.layernorm_z = LayerNorm(self.c_z)
        self.linear_no_bias_z = LinearNoBias(
            in_features=self.c_z, out_features=self.n_heads
        )
        self.linear_no_bias_mg = LinearNoBias(
            in_features=self.c_m, out_features=self.c * self.n_heads, initializer="zeros",
        )
        # Weighted average with gating
        self.softmax_w = nn.Softmax(dim=-2)
        # Output projection
        self.linear_no_bias_out = LinearNoBias(
            in_features=self.c * self.n_heads, out_features=self.c_m, initializer="zeros",
        )

    def forward(self, m: torch.Tensor, z: torch.Tensor) -> torch.Tensor:
        """
        Args:
            m (torch.Tensor): msa embedding
                [...,n_msa_sampled, n_token, c_m]
            z (torch.Tensor): pair embedding
                [...,n_token, n_token, c_z]
        Returns:
            torch.Tensor: updated msa embedding
                [...,n_msa_sampled, n_token, c_m]
        """
        # Input projections
        m = self.layernorm_m(m)  # [...,n_msa_sampled, n_token, c_m]
        v = self.linear_no_bias_mv(m)  # [...,n_msa_sampled, n_token, n_heads * c]
        v = v.reshape(
            *v.shape[:-1], self.n_heads, self.c
        )  # [...,n_msa_sampled, n_token, n_heads, c]
        b = self.linear_no_bias_z(
            self.layernorm_z(z)
        )  # [...,n_token, n_token, n_heads]
        g = torch.sigmoid(
            self.linear_no_bias_mg(m)
        )  # [...,n_msa_sampled, n_token, n_heads * c]
        g = g.reshape(
            *g.shape[:-1], self.n_heads, self.c
        )  # [...,n_msa_sampled, n_token, n_heads, c]
        w = self.softmax_w(b)  # [...,n_token, n_token, n_heads]
        wv = torch.einsum(
            "...ijh,...mjhc->...mihc", w, v
        )  # [...,n_msa_sampled,n_token,n_heads,c]
        o = g * wv
        o = o.reshape(
            *o.shape[:-2], self.n_heads * self.c
        )  # [...,n_msa_sampled, n_token, n_heads * c]
        m = self.linear_no_bias_out(o)  # [...,n_msa_sampled, n_token, c_m]
        if (not self.training) and m.shape[-3] > 5120:
            del v, b, g, w, wv, o
            torch.cuda.empty_cache()
        return m


class MSAStack(nn.Module):
    """
    Implements MSAStack Line7-Line8 in Algorithm 8
    """

    def __init__(
        self,
        c_m: int = 64,
        c: int = 8,
        dropout: float = 0.15,
        msa_chunk_size: Optional[int] = 2048,
        msa_max_size: Optional[int] = 16384,
    ) -> None:
        """
        Args:
            c_m (int, optional): hidden dim [for msa embedding]. Defaults to 64.
            c (int, optional): hidden [for MSAStack] dim. Defaults to 8.
            dropout (float, optional): dropout ratio. Defaults to 0.15.
        """
        super(MSAStack, self).__init__()
        self.c = c
        self.msa_pair_weighted_averaging = MSAPairWeightedAveraging(c=self.c)
        self.dropout_row = DropoutRowwise(dropout)
        self.transition_m = Transition(c_in=c_m, n=4)
        self.msa_chunk_size = msa_chunk_size
        self.msa_max_size = msa_max_size

    def forward(self, m: torch.Tensor, z: torch.Tensor) -> torch.Tensor:
        """
        Args:
            m (torch.Tensor): msa embedding
                [...,n_msa_sampled, n_token, c_m]
            z (torch.Tensor): pair embedding
                [...,n_token, n_token, c_z]

        Returns:
            torch.Tensor: updated msa embedding
                [...,n_msa_sampled, n_token, c_m]
        """
        chunk_size = self.msa_chunk_size
        if self.training:
            # Padded m to avoid static graph change in DDP training, which will raise
            # RuntimeError: Your training graph has changed in this iteration,
            # e.g., one parameter is unused in first iteration, but then got used in the second iteration.
            # this is not compatible with static_graph set to True
            m_new = pad_at_dim(
                m, dim=-3, pad_length=(0, self.msa_max_size - m.shape[-3]), value=0
            )
            assert (m_new[: m.shape[-3], :, :] == m).all()
            msa_pair_weighted = self.chunk_forward(
                self.msa_pair_weighted_averaging, m_new, z, chunk_size
            )
            m = m + self.dropout_row(msa_pair_weighted[: m.shape[-3], :, :])
            m_new = pad_at_dim(
                m, dim=-3, pad_length=(0, self.msa_max_size - m.shape[-3]), value=0
            )
            m_transition = self.chunk_forward(
                self.transition_m, m_new, None, chunk_size
            )
            m = m + m_transition[: m.shape[-3], :, :]
            if (not self.training) and (z.shape[-2] > 2000 or m.shape[-3] > 5120):
                del msa_pair_weighted, m_transition
                torch.cuda.empty_cache()
        else:
            m = self.inference_forward(m, z, chunk_size)
        return m

    def chunk_forward(
        self,
        module: nn.Module,
        m: torch.Tensor,
        z: torch.Tensor,
        chunk_size: int = 2048,
    ) -> torch.Tensor:
        """
        Args:
            m (torch.Tensor): msa embedding
                [..., n_msa_sampled, n_token, c_m]
            z (torch.Tensor): pair embedding
                [..., n_token, n_token, c_z]
            chunk_size (int): size of each chunk for gradient checkpointing

        Returns:
            torch.Tensor: updated msa embedding
                [..., n_msa_sampled, n_token, c_m]
        """

        def fixed_length_chunk(m, chunk_length, dim=0):
            dim_size = m.size(dim)
            chunk_num = (dim_size + chunk_length - 1) // chunk_length
            chunks = []

            for i in range(chunk_num):
                start = i * chunk_length
                end = min(start + chunk_length, dim_size)
                chunk = m.narrow(dim, start, end - start)
                chunks.append(chunk)

            return chunks

        checkpoint_fn = get_checkpoint_fn()
        # Split the tensor `m` into chunks along the first dimension
        # m_chunks = torch.chunk(m, chunk_size, dim=0)
        m_chunks = fixed_length_chunk(m, chunk_size, dim=0)

        # Process each chunk with gradient checkpointing
        if z is not None:
            processed_chunks = [checkpoint_fn(module, chunk, z) for chunk in m_chunks]
        else:
            processed_chunks = [checkpoint_fn(module, chunk) for chunk in m_chunks]
        if (not self.training) and m.shape[-3] > 5120:
            del m_chunks
            torch.cuda.empty_cache()
        # Concatenate the processed chunks back together
        m = torch.cat(processed_chunks, dim=0)
        if (not self.training) and m.shape[-3] > 5120:
            del processed_chunks
            torch.cuda.empty_cache()
        return m

    def inference_forward(
        self, m: torch.Tensor, z: torch.Tensor, chunk_size: int = 2048
    ) -> torch.Tensor:
        """Inplace slice forward for saving memory
        Args:
            m (torch.Tensor): msa embedding
                [..., n_msa_sampled, n_token, c_m]
            z (torch.Tensor): pair embedding
                [..., n_token, n_token, c_z]
            chunk_num (int): size of each chunk for gradient checkpointing

        Returns:
            torch.Tensor: updated msa embedding
                [..., n_msa_sampled, n_token, c_m]
        """
        num_msa = m.shape[-3]
        no_chunks = num_msa // chunk_size + (num_msa % chunk_size != 0)
        for i in range(no_chunks):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, num_msa)
            # Use inplace to save memory
            m[start:end, :, :] += self.msa_pair_weighted_averaging(
                m[start:end, :, :], z
            )
            m[start:end, :, :] += self.transition_m(m[start:end, :, :])
        return m


class MSABlock(nn.Module):
    """
    Base MSA Block, Line6-Line13 in Algorithm 8
    """

    def __init__(
        self,
        c_m: int = 64,
        c_z: int = 128,
        c_hidden: int = 32,
        is_last_block: bool = False,
        msa_dropout: float = 0.15,
        pair_dropout: float = 0.25,
        msa_chunk_size: Optional[int] = 2048,
        msa_max_size: Optional[int] = 16384,
    ) -> None:
        """
        Args:
            c_m (int, optional): hidden dim [for msa embedding]. Defaults to 64.
            c_z (int, optional): hidden dim [for pair embedding]. Defaults to 128.
            c_hidden (int, optional): hidden dim [for MSABlock]. Defaults to 32.
            is_last_block (int): if this is the last block of MSAModule. Defaults to False.
            msa_dropout (float, optional): dropout ratio for msa block. Defaults to 0.15.
            pair_dropout (float, optional): dropout ratio for pair stack. Defaults to 0.25.
        """
        super(MSABlock, self).__init__()
        self.c_m = c_m
        self.c_z = c_z
        self.c_hidden = c_hidden
        self.is_last_block = is_last_block
        # Communication
        self.outer_product_mean_msa = OuterProductMean(
            c_m=self.c_m, c_z=self.c_z, c_hidden=self.c_hidden
        )
        if not self.is_last_block:
            # MSA stack
            self.msa_stack = MSAStack(
                c_m=self.c_m,
                dropout=msa_dropout,
                msa_chunk_size=msa_chunk_size,
                msa_max_size=msa_max_size,
            )
        # Pair stack
        self.pair_stack = PairformerBlock(c_z=c_z, c_s=0, dropout=pair_dropout)

    def forward(
        self,
        m: torch.Tensor,
        z: torch.Tensor,
        pair_mask,
        use_memory_efficient_kernel: bool = False,
        use_deepspeed_evo_attention: bool = False,
        use_lma: bool = False,
        inplace_safe: bool = False,
        chunk_size: Optional[int] = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            m (torch.Tensor): msa embedding
                [...,n_msa_sampled, n_token, c_m]
            z (torch.Tensor): pair embedding
                [...,n_token, n_token, c_z]
            pair_mask (torch.Tensor): pair mask
                [..., N_token, N_token]
            use_memory_efficient_kernel (bool): Whether to use memory-efficient kernel. Defaults to False.
            use_deepspeed_evo_attention (bool): Whether to use DeepSpeed evolutionary attention. Defaults to False.
            use_lma (bool): Whether to use low-memory attention. Defaults to False.
            inplace_safe (bool): Whether it is safe to use inplace operations. Defaults to False.
            chunk_size (Optional[int]): Chunk size for memory-efficient operations. Defaults to None.

        Returns:
            tuple[torch.Tensor, torch.Tensor]: updated m z of MSABlock
                [...,n_msa_sampled, n_token, c_m]
                [...,n_token, n_token, c_z]
        """
        # Communication
        if (not self.training) and z.shape[-2] > 2000:
            torch.cuda.empty_cache()
        z = z + self.outer_product_mean_msa(
            m, inplace_safe=inplace_safe, chunk_size=chunk_size
        )
        if (not self.training) and z.shape[-2] > 2000:
            torch.cuda.empty_cache()
        if not self.is_last_block:
            # MSA stack
            m = self.msa_stack(m, z)
        # Pair stack
        _, z = self.pair_stack(
            s=None,
            z=z,
            pair_mask=pair_mask,
            use_memory_efficient_kernel=use_memory_efficient_kernel,
            use_deepspeed_evo_attention=use_deepspeed_evo_attention,
            use_lma=use_lma,
            inplace_safe=inplace_safe,
            chunk_size=chunk_size,
        )
        if (not self.training) and (z.shape[-2] > 2000 or m.shape[-3] > 5120):
            torch.cuda.empty_cache()
        if not self.is_last_block:
            return m, z
        else:
            return None, z  # to ensure that `m` will not be used.


class MSAModule(nn.Module):
    """
    Implements Algorithm 8 [MSAModule] in AF3
    """

    def __init__(
        self,
        n_blocks: int = 4,
        c_m: int = 64,
        c_z: int = 128,
        c_s_inputs: int = 449,
        msa_dropout: float = 0.15,
        pair_dropout: float = 0.25,
        blocks_per_ckpt: Optional[int] = 1,
        msa_chunk_size: Optional[int] = 2048,
        msa_max_size: Optional[int] = 16384,
        msa_configs: dict = None,
    ) -> None:
        """Main Entry of MSAModule

        Args:
            n_blocks (int, optional): number of blocks [for MSAModule]. Defaults to 4.
            c_m (int, optional): hidden dim [for msa embedding]. Defaults to 64.
            c_z (int, optional): hidden dim [for pair embedding]. Defaults to 128.
            c_s_inputs (int, optional):
                hidden dim for single embedding from InputFeatureEmbedder. Defaults to 449.
            msa_dropout (float, optional): dropout ratio for msa block. Defaults to 0.15.
            pair_dropout (float, optional): dropout ratio for pair stack. Defaults to 0.25.
            blocks_per_ckpt: number of MSAModule blocks in each activation checkpoint
                Size of each chunk. A higher value corresponds to fewer
                checkpoints, and trades memory for speed. If None, no checkpointing
                is performed.
            msa_configs (dict, optional): a dictionary containing keys:
                "enable": whether using msa embedding.
        ]"""
        super(MSAModule, self).__init__()
        self.n_blocks = n_blocks
        self.c_m = c_m
        self.c_s_inputs = c_s_inputs
        self.blocks_per_ckpt = blocks_per_ckpt
        self.msa_chunk_size = msa_chunk_size
        self.msa_max_size = msa_max_size
        self.input_feature = {
            "msa": 32,
            "has_deletion": 1,
            "deletion_value": 1,
        }

        self.msa_configs = {
            "enable": msa_configs.get("enable", False),
            "strategy": msa_configs.get("strategy", "random"),
        }
        if "sample_cutoff" in msa_configs:
            self.msa_configs["train_cutoff"] = msa_configs["sample_cutoff"].get(
                "train", 512
            )
            self.msa_configs["test_cutoff"] = msa_configs["sample_cutoff"].get(
                "test", 16384
            )
            # the default msa_max_size is 16384 if not specified
            self.msa_max_size = self.msa_configs["train_cutoff"]
        if "min_size" in msa_configs:
            self.msa_configs["train_lowerb"] = msa_configs["min_size"].get("train", 1)
            self.msa_configs["test_lowerb"] = msa_configs["min_size"].get("test", 1)

        self.linear_no_bias_m = LinearNoBias(
            in_features=32 + 1 + 1, out_features=self.c_m
        )

        self.linear_no_bias_s = LinearNoBias(
            in_features=self.c_s_inputs, out_features=self.c_m
        )
        self.blocks = nn.ModuleList()

        for i in range(n_blocks):
            block = MSABlock(
                c_m=self.c_m,
                c_z=c_z,
                is_last_block=(i + 1 == n_blocks),
                msa_dropout=msa_dropout,
                pair_dropout=pair_dropout,
                msa_chunk_size=self.msa_chunk_size,
                msa_max_size=self.msa_max_size,
            )
            self.blocks.append(block)

    def _prep_blocks(
        self,
        pair_mask: Optional[torch.Tensor],
        use_memory_efficient_kernel: bool = False,
        use_deepspeed_evo_attention: bool = False,
        use_lma: bool = False,
        inplace_safe: bool = False,
        chunk_size: Optional[int] = None,
        clear_cache_between_blocks: bool = False,
    ):
        blocks = [
            partial(
                b,
                pair_mask=pair_mask,
                use_memory_efficient_kernel=use_memory_efficient_kernel,
                use_deepspeed_evo_attention=use_deepspeed_evo_attention,
                use_lma=use_lma,
                inplace_safe=inplace_safe,
                chunk_size=chunk_size,
            )
            for b in self.blocks
        ]

        def clear_cache(b, *args, **kwargs):
            torch.cuda.empty_cache()
            return b(*args, **kwargs)

        if clear_cache_between_blocks:
            blocks = [partial(clear_cache, b) for b in blocks]
        return blocks

    def one_hot_fp32(
        self, tensor: torch.Tensor, num_classes: int, dtype=torch.float32
    ) -> torch.Tensor:
        """like F.one_hot, but output dtype is float32.

        Args:
            tensor (torch.Tensor): the input tensor
            num_classes (int): num_classes
            dtype (torch.float32, optional): the output dtype. Defaults to torch.float32.

        Returns:
            torch.Tensor: the one-hot encoded tensor with shape
                [..., n_msa_sampled, N_token, num_classes]
        """
        shape = tensor.shape
        one_hot_tensor = torch.zeros(
            *shape, num_classes, dtype=dtype, device=tensor.device
        )
        one_hot_tensor.scatter_(len(shape), tensor.unsqueeze(-1), 1)
        return one_hot_tensor

    def forward(
        self,
        input_feature_dict: dict[str, Any],
        z: torch.Tensor,
        s_inputs: torch.Tensor,
        pair_mask: torch.Tensor,
        use_memory_efficient_kernel: bool = False,
        use_deepspeed_evo_attention: bool = False,
        use_lma: bool = False,
        inplace_safe: bool = False,
        chunk_size: Optional[int] = None,
    ) -> torch.Tensor:
        """
        Args:
            input_feature_dict (dict[str, Any]):
                input meta feature dict
            z (torch.Tensor): pair embedding
                [..., N_token, N_token, c_z]
            s_inputs (torch.Tensor): single embedding from InputFeatureEmbedder
                [..., N_token, c_s_inputs]
            pair_mask (torch.Tensor): pair mask
                [..., N_token, N_token]
            use_memory_efficient_kernel (bool): Whether to use memory-efficient kernel. Defaults to False.
            use_deepspeed_evo_attention (bool): Whether to use DeepSpeed evolutionary attention. Defaults to False.
            use_lma (bool): Whether to use low-memory attention. Defaults to False.
            inplace_safe (bool): Whether it is safe to use inplace operations. Defaults to False.
            chunk_size (Optional[int]): Chunk size for memory-efficient operations. Defaults to None.

        Returns:
            torch.Tensor: the updated z
                [..., N_token, N_token, c_z]
        """
        # If n_blocks < 1, return z
        if self.n_blocks < 1:
            return z

        if "msa" not in input_feature_dict:
            return z
        # Check msa shape!
        # IndexError: Dimension out of range (expected to be in range of [-1, 0], but got -2)
        if input_feature_dict["msa"].dim() < 2:
            return z
        msa_feat = sample_msa_feature_dict_random_without_replacement(
            feat_dict=input_feature_dict,
            dim_dict={feat_name: -2 for feat_name in self.input_feature},
            cutoff=(
                self.msa_configs["train_cutoff"]
                if self.training
                else self.msa_configs["test_cutoff"]
            ),
            lower_bound=(
                self.msa_configs["train_lowerb"]
                if self.training
                else self.msa_configs["test_lowerb"]
            ),
            strategy=self.msa_configs["strategy"],
        )
        # pylint: disable=E1102
        if not self.training and z.shape[-2] > 2000:
            # msa_feat["msa"] is torch.int64, we convert it
            # to torch.float32 for saving half of the CUDA memory
            msa_feat["msa"] = self.one_hot_fp32(
                msa_feat["msa"],
                num_classes=self.input_feature["msa"],
            )
        else:
            msa_feat["msa"] = torch.nn.functional.one_hot(
                msa_feat["msa"],
                num_classes=self.input_feature["msa"],
            )

        target_shape = msa_feat["msa"].shape[:-1]
        msa_sample = torch.cat(
            [
                msa_feat[name].reshape(*target_shape, d)
                for name, d in self.input_feature.items()
            ],
            dim=-1,
        )  # [..., N_msa_sample, N_token, 32 + 1 + 1]
        # Msa_feat is very large, if N_MSA=16384 and N_token=4000,
        # msa_feat["msa"] consumes about 16G CUDA memory, so we
        # need to clear cache to avoid OOM
        if not self.training:
            del msa_feat
            torch.cuda.empty_cache()
        # Line2
        msa_sample = self.linear_no_bias_m(msa_sample)

        # Auto broadcast [...,n_msa_sampled, n_token, c_m]
        msa_sample = msa_sample + self.linear_no_bias_s(s_inputs)
        if z.shape[-2] > 2000 and (not self.training):
            clear_cache_between_blocks = True
        else:
            clear_cache_between_blocks = False
        blocks = self._prep_blocks(
            pair_mask=pair_mask,
            use_memory_efficient_kernel=use_memory_efficient_kernel,
            use_deepspeed_evo_attention=use_deepspeed_evo_attention,
            use_lma=use_lma,
            inplace_safe=inplace_safe,
            chunk_size=chunk_size,
            clear_cache_between_blocks=clear_cache_between_blocks,
        )
        blocks_per_ckpt = self.blocks_per_ckpt
        if not torch.is_grad_enabled():
            blocks_per_ckpt = None
        msa_sample, z = checkpoint_blocks(
            blocks,
            args=(msa_sample, z),
            blocks_per_ckpt=blocks_per_ckpt,
        )
        if z.shape[-2] > 2000:
            torch.cuda.empty_cache()
        return z


class TemplateEmbedder(nn.Module):
    """
    Implements Algorithm 16 in AF3
    """

    def __init__(
        self,
        n_blocks: int = 2,
        c: int = 64,
        c_z: int = 128,
        dropout: float = 0.25,
        blocks_per_ckpt: Optional[int] = None,
    ) -> None:
        """
        Args:
            n_blocks (int, optional): number of blocks for TemplateEmbedder. Defaults to 2.
            c (int, optional): hidden dim of TemplateEmbedder. Defaults to 64.
            c_z (int, optional): hidden dim [for pair embedding]. Defaults to 128.
            dropout (float, optional): dropout ratio for PairformerStack. Defaults to 0.25.
                Note this value is missed in Algorithm 16, so we use default ratio for Pairformer
            blocks_per_ckpt: number of TemplateEmbedder/Pairformer blocks in each activation
                checkpoint Size of each chunk. A higher value corresponds to fewer
                checkpoints, and trades memory for speed. If None, no checkpointing
                is performed.
        """
        super(TemplateEmbedder, self).__init__()
        self.n_blocks = n_blocks
        self.c = c
        self.c_z = c_z
        self.input_feature1 = {
            "template_distogram": 39,
            "b_template_backbone_frame_mask": 1,
            "template_unit_vector": 3,
            "b_template_pseudo_beta_mask": 1,
        }
        self.input_feature2 = {
            "template_restype_i": 32,
            "template_restype_j": 32,
        }
        self.distogram = {"max_bin": 50.75, "min_bin": 3.25, "no_bins": 39}
        self.inf = 100000.0

        self.linear_no_bias_z = LinearNoBias(in_features=self.c_z, out_features=self.c)
        self.layernorm_z = LayerNorm(self.c_z)
        self.linear_no_bias_a = LinearNoBias(
            in_features=sum(self.input_feature1.values())
            + sum(self.input_feature2.values()),
            out_features=self.c,
        )
        self.pairformer_stack = PairformerStack(
            c_s=0,
            c_z=c,
            n_blocks=self.n_blocks,
            dropout=dropout,
            blocks_per_ckpt=blocks_per_ckpt,
        )
        self.layernorm_v = LayerNorm(self.c)
        self.linear_no_bias_u = LinearNoBias(in_features=self.c, out_features=self.c_z)

    def forward(
        self,
        input_feature_dict: dict[str, Any],
        z: torch.Tensor,  # pylint: disable=W0613
        pair_mask: torch.Tensor = None,  # pylint: disable=W0613
        use_memory_efficient_kernel: bool = False,  # pylint: disable=W0613
        use_deepspeed_evo_attention: bool = False,  # pylint: disable=W0613
        use_lma: bool = False,  # pylint: disable=W0613
        inplace_safe: bool = False,  # pylint: disable=W0613
        chunk_size: Optional[int] = None,  # pylint: disable=W0613
    ) -> torch.Tensor:
        """
        Args:
            input_feature_dict (dict[str, Any]): input feature dict
            z (torch.Tensor): pair embedding
                [..., N_token, N_token, c_z]
            pair_mask (torch.Tensor, optional): pair masking. Default to None.
                [..., N_token, N_token]

        Returns:
            torch.Tensor: the template feature
                [..., N_token, N_token, c_z]
        """
        # In this version, we do not use TemplateEmbedder by setting n_blocks=0
        if "template_restype" not in input_feature_dict or self.n_blocks < 1:
            return 0
        return 0
