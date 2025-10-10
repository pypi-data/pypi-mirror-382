from __future__ import annotations
from contextlib import nullcontext

import torch
from torch import nn
import torch.nn.functional as F
from torch.nn import Module, ModuleList
from torch.optim import AdamW
from torch.utils.data import Dataset, DataLoader

from einops import rearrange, repeat
from einops.layers.torch import Reduce, Rearrange

# network related

from x_transformers import Encoder
from tiny_recursive_model.mlp_mixer_1d import MLPMixer1D

# ema - apparently greatly helped with results

from ema_pytorch import EMA

# helpers

def exists(v):
    return v is not None

def default(v, d):
    return v if exists(v) else d

def range_from_one(n):
    return range(1, n + 1)

def is_empty(t):
    return t.numel() == 0

# classes

class TinyRecursiveModel(Module):
    def __init__(
        self,
        *,
        dim,
        num_tokens,
        network: Module,
        num_refinement_blocks = 3,   # T in paper
        num_latent_refinements = 6,  # n in paper - 1 output refinement per N latent refinements
        halt_loss_weight = 1.
    ):
        super().__init__()
        assert num_refinement_blocks > 1

        self.input_embed = nn.Embedding(num_tokens, dim)
        self.output_init_embed = nn.Parameter(torch.randn(dim) * 1e-2)
        self.latent_init_embed = nn.Parameter(torch.randn(dim) * 1e-2)

        self.network = network

        self.num_latent_refinements = num_latent_refinements
        self.num_refinement_blocks = num_refinement_blocks

        # prediction heads

        self.to_pred = nn.Linear(dim, num_tokens, bias = False)

        self.to_halt_pred = nn.Sequential(
            Reduce('b n d -> b d', 'mean'),
            nn.Linear(dim, 1, bias = False),
            nn.Sigmoid(),
            Rearrange('... 1 -> ...')
        )

        self.halt_loss_weight = halt_loss_weight

    def refine_latent_then_output_once(
        self,
        inputs,     # (b n d)
        outputs,    # (b n d)
        latents,    # (b n d)
    ):

        # so it seems for this work, they use only one network
        # the network learns to refine the latents if input is passed in, otherwise it refines the output

        for _ in range(self.num_latent_refinements):

            latents = self.network(outputs + latents + inputs)

        outputs = self.network(outputs + latents)

        return outputs, latents

    def get_initial(self):
        outputs = self.output_init_embed
        latents = self.latent_init_embed

        return outputs, latents

    def deep_refinement(
        self,
        inputs,    # (b n d)
        outputs,   # (b n d)
        latents,   # (b n d)
    ):

        for i in range(self.num_refinement_blocks):

            # only last round of refinement receives gradients

            is_last = i == (self.num_refinement_blocks - 1)
            context = torch.no_grad if not is_last else nullcontext

            with context():
                outputs, latents = self.refine_latent_then_output_once(inputs, outputs, latents)

        return outputs, latents

    def forward(
        self,
        seq,
        outputs,
        latents,
        labels = None
    ):
        inputs = self.input_embed(seq)

        outputs, latents = self.deep_refinement(inputs, outputs, latents)

        pred = self.to_pred(outputs)

        should_halt = self.to_halt_pred(outputs)

        outputs, latents = outputs.detach(), latents.detach()

        return_package = (outputs, latents, pred, should_halt)

        if not exists(labels):
            return return_package

        # calculate loss if labels passed in

        loss = F.cross_entropy(rearrange(pred, 'b n l -> b l n'), labels)

        is_all_correct = (pred.argmax(dim = -1) == labels).all(dim = -1)

        halt_loss = F.binary_cross_entropy(should_halt, is_all_correct.float())

        # total loss and loss breakdown

        total_loss = loss + halt_loss * self.halt_loss_weight
        losses = (loss, halt_loss)

        return (total_loss, losses, *return_package)

# trainer

class Trainer(Module):
    def __init__(
        self,
        model: TinyRecursiveModel | Module,
        dataset: Dataset,
        optim_klass = AdamW,
        learning_rate = 1e-4,
        weight_decay = 1.,
        batch_size = 16,
        epochs = 2,
        halt_prob_thres = 0.5,
        max_recurrent_steps = 12,
        ema_decay_rate = 0.999,
        ema_update_model_with_ema_every = 10000
    ):
        super().__init__()

        self.batch_size = batch_size
        self.epochs = epochs

        self.dataset = dataset
        self.dataloader = dataloader = DataLoader(self.dataset, batch_size = self.batch_size, shuffle = True)

        self.optim = optim_klass(
            model.parameters(),
            lr = learning_rate,
            weight_decay = weight_decay
        )

        self.model = model

        self.ema_model = EMA(
            model,
            beta = ema_decay_rate,
            update_model_with_ema_every = ema_update_model_with_ema_every
        )

        self.halt_prob_thres = halt_prob_thres

        self.max_recurrent_steps = max_recurrent_steps

    def forward(self):

        for epoch in range_from_one(self.epochs):

            for dataset_input, dataset_output in self.dataloader:

                outputs, latents = self.model.get_initial()

                for recurrent_step in range_from_one(self.max_recurrent_steps):

                    loss, (main_loss, halt_loss), outputs, latents, pred, halt = self.model(dataset_input, outputs, latents, labels = dataset_output)

                    print(f'[{epoch} ({recurrent_step} / {self.max_recurrent_steps})] loss: {main_loss.item():.3f} | halt loss: {halt_loss.item():.3f}')

                    loss.backward()

                    self.optim.step()
                    self.optim.zero_grad()

                    self.ema_model.update()

                    # handle halting

                    halt_mask = halt >= self.halt_prob_thres

                    if not halt_mask.any():
                        continue

                    outputs = outputs[~halt_mask]
                    latents = latents[~halt_mask]
                    dataset_input = dataset_input[~halt_mask]
                    dataset_output = dataset_output[~halt_mask]

                    if is_empty(outputs):
                        break
