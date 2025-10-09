from typing import Tuple, List, Union, Callable, Optional

import torch
import torch.nn as nn
import torch.distributed as dist

import onescience.distributed.comm as comm
from onescience.distributed.dualpipeutils import WeightGradStore, run_backward, scatter, gather


    
class DualPipeV(nn.Module):
    def __init__(
        self,
        modules: Tuple[nn.Module, nn.Module],
        batch_dim: int = 0,
        process_group: Optional[dist.ProcessGroup] = None,
        rank_mapping: Optional[List[int]] = None,
    ) -> None:
        super().__init__()

        assert next(modules[0].parameters()).device == torch.device(torch.cuda.current_device())
        self.module = nn.ModuleList(modules)
        self.overlapped_forward_backward = type(modules[0]) == type(modules[1]) and hasattr(type(modules[0]), "overlapped_forward_backward")
        self.batch_dim = batch_dim
        self.group = process_group or dist.distributed_c10d._get_default_group()
        self.num_ranks = self.group.size()

        # rank_mapping: Map rank in process_group to actual pp rank.
        # rank_inverse_mapping: Map actual pp rank to rank in process_group.
        if rank_mapping is None:
            rank_mapping = list(range(self.num_ranks))
        rank_inverse_mapping = [None] * (self.num_ranks + 1)
        for i in range(self.num_ranks):
            rank_inverse_mapping[rank_mapping[i]] = i

        self.rank = rank_mapping[self.group.rank()]
        self.prev_rank = rank_inverse_mapping[self.rank - 1]
        self.next_rank = rank_inverse_mapping[self.rank + 1]

        self.is_first_rank = self.rank == 0
        self.is_last_rank = self.rank == self.num_ranks - 1

    def log(self, name, phase):
        return
        # print(f"{MARKS[name]} [Rank {self.rank}] {name} start, phase={phase}")
    
    def _reset_states(self) -> None:
        WeightGradStore.clear()

        self.input_chunks: Tuple[List[List[torch.Tensor]], List[List[torch.Tensor]]] = ([], [])
        self.output_chunks: Tuple[List[List[torch.Tensor]], List[List[torch.Tensor]]] = ([], [])
        self.input_grad_chunks: Tuple[List[List[torch.Tensor]], List[List[torch.Tensor]]] = ([], [])
        self.output_grad_chunks: Tuple[List[List[torch.Tensor]], List[List[torch.Tensor]]] = ([], [])
        self.labels: List[List[torch.Tensor]] = None
        self.loss_chunks: List[torch.Tensor] = []
        self.criterion: Callable = None

        self.current_f_chunk_id: List[int] = [0, 0]
        self.current_b_chunk_id: List[int] = [0, 0]
        self.current_send_f_chunk_id: List[int] = [0, 0]
        self.current_send_b_chunk_id: List[int] = [0, 0]
        self.current_recv_f_chunk_id: List[int] = [0, 0]
        self.current_recv_b_chunk_id: List[int] = [0, 0]
        self.comm_ops: List[dist.P2POp] = []
        self.to_free: List[torch.Tensor] = []

    def _forward_compute_chunk(self, phase: int) -> None:
        self.log("_forward_compute_chunk", phase)
        chunk_id = self.current_f_chunk_id[phase]
        self.current_f_chunk_id[phase] += 1
        inputs = self.input_chunks[phase][chunk_id]
        if self.forward_only:
            self.input_chunks[phase][chunk_id] = None

        is_last_stage = (self.is_first_rank and phase == 1)

        outputs = self.module[phase](*inputs)
        outputs = [outputs] if isinstance(outputs, torch.Tensor) else outputs
        if is_last_stage and self.criterion is not None:
            labels = self.labels[chunk_id]
            loss = self.criterion(*outputs, *labels)
            self.loss_chunks.append(loss)

        if self.is_last_rank and phase == 0:
            self.input_chunks[1].append([output.detach().requires_grad_() for output in outputs])
        if (not is_last_stage) or self.return_outputs:
            self.output_chunks[phase].append(outputs)

    def _backward_compute_chunk(self, phase: int, enable_zb: bool = False) -> None:
        self.log("_backward_compute_chunk", phase)
        if self.forward_only:
            return
        chunk_id = self.current_b_chunk_id[phase]
        self.current_b_chunk_id[phase] += 1

        is_last_stage = (self.is_first_rank and phase == 1)

        WeightGradStore.enabled = enable_zb
        if is_last_stage:
            loss = self.loss_chunks[chunk_id]
            loss.backward()
            loss.detach_()
        else:
            outputs = self.output_chunks[phase][chunk_id]
            if not self.return_outputs:
                self.output_chunks[phase][chunk_id] = None
            output_grads = self.output_grad_chunks[phase][chunk_id]
            self.output_grad_chunks[phase][chunk_id] = None
            non_empty = [(t, g) for t, g in zip(outputs, output_grads) if g is not None]
            outputs, output_grads = list(zip(*non_empty))
            if len(outputs) > 0:
                run_backward(outputs, output_grads)
        WeightGradStore.enabled = False
        if enable_zb:
            WeightGradStore.flush()

        inputs = self.input_chunks[phase][chunk_id]
        self.input_chunks[phase][chunk_id] = None
        input_grads = [t.grad for t in inputs]
        if self.is_last_rank and phase == 1:
            self.output_grad_chunks[0].append(input_grads)
        else:
            self.input_grad_chunks[phase].append(input_grads)

    def _forward_backward_compute_chunk(self, phase0: int, phase1: int) -> None:
        
        if self.forward_only:
            self.log("_forward_backward_compute_chunk", phase0)
            self._forward_compute_chunk(phase0)
            return
        if not self.overlapped_forward_backward:
            self._forward_compute_chunk(phase0)
            self.log("_forward_backward_compute_chunk", phase0)
            self._backward_compute_chunk(phase1)
            self.log("_forward_backward_compute_chunk", phase1)
            return

        # pre-forward
        chunk_id0 = self.current_f_chunk_id[phase0]
        self.current_f_chunk_id[phase0] += 1
        module0 = self.module[phase0]
        inputs0 = self.input_chunks[phase0][chunk_id0]
        is_last_stage0 = (self.is_first_rank and phase0 == 1)

        if is_last_stage0 and self.criterion is not None:
            labels0 = self.labels[chunk_id0]
            criterion0 = self.criterion
        else:
            labels0 = []
            criterion0 = None

        # pre-backward
        chunk_id1 = self.current_b_chunk_id[phase1]
        self.current_b_chunk_id[phase1] += 1
        module1 = self.module[phase1]
        is_last_stage1 = (self.is_first_rank and phase1 == 1)

        if is_last_stage1:
            loss1 = self.loss_chunks[chunk_id1]
            outputs1 = []
            output_grads1 = []
        else:
            loss1 = None
            outputs1 = self.output_chunks[phase1][chunk_id1]
            if not self.return_outputs:
                self.output_chunks[phase1][chunk_id1] = None
            output_grads1 = self.output_grad_chunks[phase1][chunk_id1]
            self.output_grad_chunks[phase1][chunk_id1] = None
            non_empty = [(t, g) for t, g in zip(outputs1, output_grads1) if g is not None]
            outputs1, output_grads1 = list(zip(*non_empty))

        # forward & backward
        outputs0, loss0 = type(module0).overlapped_forward_backward(
            module0, inputs0, criterion0, labels0,
            module1, loss1, outputs1, output_grads1,
        )

        # post-forward
        if self.is_last_rank and phase0 == 0:
            self.input_chunks[1].append([output.detach().requires_grad_() for output in outputs0])
        if (not is_last_stage0) or self.return_outputs:
            self.output_chunks[phase0].append(outputs0)
        if is_last_stage0 and self.criterion is not None:
            self.loss_chunks.append(loss0)

        # post-backward
        inputs = self.input_chunks[phase1][chunk_id1]
        self.input_chunks[phase1][chunk_id1] = None
        input_grads1 = [t.grad for t in inputs]
        if self.is_last_rank and phase1 == 1:
            self.output_grad_chunks[0].append(input_grads1)
        else:
            self.input_grad_chunks[phase1].append(input_grads1)

    def _forward_chunk(self, phase: int, recv: bool = True, send: bool = True) -> None:
        self.log("_forward_chunk", phase)
        if recv:
            self._recv_forward(phase)
        self._commit_and_wait_comm()

        self._forward_compute_chunk(phase)

        if send:
            self._send_forward(phase)

    def _backward_chunk(self, phase: int, enable_zb: bool = False, recv: bool = True, send: bool = True) -> None:
        self.log("_backward_chunk", phase)
        if recv:
            self._recv_backward(phase)
        self._commit_and_wait_comm()

        self._backward_compute_chunk(phase, enable_zb)

        if send:
            self._send_backward(phase)

    def _forward_backward_chunk(self, phase0: int, phase1: int, recv0: bool = True) -> None:
        self.log("_forward_backward_chunk", 2)
        if recv0:
            self._recv_forward(phase0)
        self._recv_backward(phase1)
        self._commit_and_wait_comm()

        self._forward_backward_compute_chunk(phase0, phase1)

        self._send_forward(phase0)
        self._send_backward(phase1)

    def _weight_chunk(self) -> None:
        self.log("_weight_chunk", 2)
        if self.forward_only:
            return

        self._commit_and_wait_comm()

        # Assume FIFO
        WeightGradStore.pop()

    def _free_tensors(self) -> None:
        self.log("_free_tensors", 2)
        for tensor in self.to_free:
            assert tensor._base is None, f"pipeline stage should not return view tensors {dist.get_rank(), tensor.shape}"
            tensor.data = torch.Tensor()
        self.to_free = []

    def _recv_forward(self, phase: int) -> None:
        self.log("_recv_forward", phase)
        if (self.is_first_rank and phase == 0) or (self.is_last_rank and phase == 1):
            return

        self.current_recv_f_chunk_id[phase] += 1
        tensors = comm.append_irecv(self.comm_ops, self.prev_rank if phase == 0 else self.next_rank, self.group)
        self.input_chunks[phase].append(tensors)

    def _send_forward(self, phase: int) -> None:
        self.log("_send_forward", phase)
        if (self.is_first_rank and phase == 1) or (self.is_last_rank and phase == 0):
            return

        chunk_id = self.current_send_f_chunk_id[phase]
        self.current_send_f_chunk_id[phase] += 1
        tensors = self.output_chunks[phase][chunk_id]

        comm.append_isend(self.comm_ops, tensors, self.next_rank if phase == 0 else self.prev_rank, self.group)

        if not self.return_outputs:
            self.to_free.extend(tensors)

    def _recv_backward(self, phase: int) -> None:
        self.log("_recv_backward", phase)
        if self.forward_only:
            return

        if (self.is_first_rank and phase == 1) or (self.is_last_rank and phase == 0):
            return

        self.current_recv_b_chunk_id[phase] += 1
        tensors = comm.append_irecv(self.comm_ops, self.next_rank if phase == 0 else self.prev_rank, self.group)
        self.output_grad_chunks[phase].append(tensors)

    def _send_backward(self, phase: int) -> None:
        self.log("_send_backward", phase)
        if self.forward_only:
            return

        if (self.is_first_rank and phase == 0) or (self.is_last_rank and phase == 1):
            return

        chunk_id = self.current_send_b_chunk_id[phase]
        self.current_send_b_chunk_id[phase] += 1
        tensors = self.input_grad_chunks[phase][chunk_id]
        self.input_grad_chunks[phase][chunk_id] = None

        comm.append_isend(self.comm_ops, tensors, self.prev_rank if phase == 0 else self.next_rank, self.group)

    def _commit_and_wait_comm(self) -> None:
        if not self.comm_ops:
            return
        reqs = dist.batch_isend_irecv(self.comm_ops)
        for req in reqs:
            req.wait()
        self.comm_ops = []
        self._free_tensors()

    def step(
        self,
        *inputs: Optional[torch.Tensor],
        num_chunks: int = 0,
        criterion: Optional[Callable] = None,
        labels: List[Optional[torch.Tensor]] = [],
        return_outputs: bool = False,
    ) -> Tuple[Optional[torch.Tensor], Optional[Union[torch.Tensor, Tuple[torch.Tensor]]]]:
        """
        Execute a training or inference step.

        Arguments:
            *inputs: Module inputs. Required only on the first rank.
            num_chunks: The number of micro-batches.
            criterion: Loss function, invoked as ``criterion(*outputs, *labels)``. Required only on the first rank.
            labels: Labels of the loss function. Required only on the first rank.
            return_outputs: Whether to return outputs on the first rank. Default: ``False``.

        Returns: (loss, outputs)
            loss: Loss for the batch. Returned only on the first rank.
            outputs: Module outputs. Returned only if ``return_outputs=True`` and on the first rank.

        """
        assert comm.TENSOR_SHAPES is not None and comm.TENSOR_DTYPE is not None, \
            "You need to call set_p2p_tensor_shapes and set_p2p_tensor_dtype before executing a step."
        self.forward_only = not torch.is_grad_enabled()
        self.return_outputs = return_outputs

        rank = self.rank
        num_ranks = self.num_ranks
        assert num_chunks > 0 and num_chunks >= num_ranks * 2, f"{num_chunks=}, {num_ranks=}"

        if not self.forward_only and self.is_first_rank:
            assert criterion is not None

        self._reset_states()

        if self.is_first_rank:
            self.input_chunks = (scatter(inputs, num_chunks, self.batch_dim), [])
            self.labels = scatter(labels, num_chunks, self.batch_dim)
            self.criterion = criterion

        # Step 1: nF0
        step_1 = (num_ranks - rank - 1) * 2
        for i in range(step_1):
            self._forward_chunk(0)

        # Step 2: nF0F1
        step_2 = rank + 1
        self._recv_forward(0)
        for i in range(step_2):
            self._forward_chunk(0, recv=False, send=False)
            self._recv_forward(0)
            self._forward_chunk(1, send=(not self.is_last_rank) or (i < step_2 - 1))
            self._send_forward(0)

        # Step 3: nB1W1F1 (Use zero bubble)
        step_3 = num_ranks - rank - 1
        for i in range(step_3):
            self._backward_chunk(1, enable_zb=True)
            self._recv_forward(1)
            self._weight_chunk()
            self._forward_chunk(1, recv=False)

        # Step 4 (Main step): nF0B1F1B0
        step_4 = num_chunks - num_ranks * 2 + rank + 1
        for i in range(step_4):
            if i == 0:
                if self.is_last_rank:
                    # NOTE: We don't overlap these two chunks to further reduce bubble size.
                    self._forward_chunk(0, recv=False, send=False)
                    self._send_forward(1)
                    self._backward_chunk(1, send=False)
                    self._send_forward(0)
                    self._send_backward(1)
                else:
                    self._forward_backward_chunk(0, 1, recv0=False)
            else:
                self._forward_backward_chunk(0, 1)
            self._forward_backward_chunk(1, 0)

        # Step 5: nB1F1B0
        step_5 = num_ranks - rank - 1
        for i in range(step_5):
            self._backward_chunk(1)
            self._forward_backward_chunk(1, 0)

        # Step 6: nB1B0 (The second half of the chunks use zero bubble)
        step_6 = rank + 1
        enable_zb = False
        for i in range(step_6):
            if i == step_6 // 2 and rank % 2 == 1:
                enable_zb = True
            self._backward_chunk(1, enable_zb=enable_zb)
            if i == step_6 // 2 and rank % 2 == 0:
                enable_zb = True
            self._backward_chunk(0, enable_zb=enable_zb)

        # Step 7: nWB0 (Use zero bubble)
        step_7 = num_ranks - rank - 1
        for i in range(step_7):
            self._weight_chunk()
            self._backward_chunk(0, enable_zb=True)

        # Step 8: nW
        step_8 = rank + 1
        for i in range(step_8):
            self._weight_chunk()
        assert WeightGradStore.funcs_queue.empty()

        self._commit_and_wait_comm()

        loss, outputs = None, None
        if self.is_first_rank:
            if criterion is not None:
                loss = torch.stack(self.loss_chunks)
            if return_outputs:
                outputs = gather(self.output_chunks[1], self.batch_dim)
                if len(outputs) == 1:
                    outputs = outputs[0]

        self._reset_states()

        return loss, outputs

   