import torch
from abc import ABC


class MegatronContainer(ABC):
    def __init__(self, policy, config, model_config):
        super().__init__(policy, config, model_config)
        self.megatron_v2 = self.policy.is_megatron_v2

    def transpose_qkv_alignment(self, x):
        attention_head_size = x.shape[-1] // self.num_attention_heads
        new_x_shape = x.size()[:-1] + (self.num_attention_heads, attention_head_size)
        x_1 = x.view(*new_x_shape)
        (q, k, v) = torch.split(x_1, (x_1.shape[-1] // 3), dim=(x_1.dim() - 1))
        if len(q.shape) > 2:
            return torch.cat((q.reshape(q.shape[0],
                                        -1),
                              k.reshape(q.shape[0],
                                        -1),
                              v.reshape(q.shape[0],
                                        -1)),
                             dim=-1).reshape(x.shape)
        else:
            return torch.cat((q.reshape(-1),
                              k.reshape(-1),
                              v.reshape(-1)),
                             dim=-1).reshape(x.shape)

    def transpose(self):
        super().transpose()
        if self.megatron_v2:
            self.qkvw = torch.nn.parameter.Parameter(
                self.transpose_qkv_alignment(self.qkvw).contiguous())
            self.qkvb = torch.nn.parameter.Parameter(
                self.transpose_qkv_alignment(self.qkvb).contiguous())