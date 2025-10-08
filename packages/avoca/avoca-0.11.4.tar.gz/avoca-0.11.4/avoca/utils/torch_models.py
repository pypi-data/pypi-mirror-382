from __future__ import annotations

import torch
import torch.nn as nn


# Define the model
class MultipleRegressionModel(nn.Module):
    linears: nn.ModuleList

    def __init__(self, number_of_regression: int):
        super().__init__()
        self.linears = nn.ModuleList(
            [nn.Linear(1, 1, bias=False) for _ in range(number_of_regression)]
        )
        # Intialize the weights to positive values
        for i, linear in enumerate(self.linears):
            linear.weight.data.fill_(float(i))

    def forward(self, x):
        x, y = x[:, 0], x[:, 1]
        # The data will pass throught the two linear layers and then we need to take the minimim of the error
        # from the two linear layers
        errors = [torch.abs(linear(x.view(-1, 1)) - y) for linear in self.linears]
        y_pred = torch.min(
            # Concatenate all the errors to get only the model with the minimum error
            torch.cat(errors, dim=1),
            dim=1,
        ).values

        return y_pred
