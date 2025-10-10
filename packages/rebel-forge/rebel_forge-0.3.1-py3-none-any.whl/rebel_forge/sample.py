"""Sample remote-training script for rebel-forge users."""
from __future__ import annotations

import socket
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

try:
    from .remote import ensure_remote
except ImportError:
    from rebel_forge.remote import ensure_remote


def _build_dataset(num_samples: int = 2048) -> TensorDataset:
    generator = torch.Generator().manual_seed(109)
    features = torch.randn(num_samples, 4, generator=generator)
    targets = torch.stack(
        [
            torch.sin(features[:, 0]) + 0.2 * features[:, 1],
            torch.cos(features[:, 2]) - 0.1 * features[:, 3],
        ],
        dim=1,
    )
    return TensorDataset(features, targets)


def _train(device: torch.device) -> None:
    dataset = _build_dataset()
    loader = DataLoader(dataset, batch_size=64, shuffle=True)

    model = nn.Sequential(
        nn.Linear(4, 128),
        nn.ReLU(),
        nn.Linear(128, 2),
    ).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=5e-3)
    loss_fn = nn.MSELoss()

    for epoch in range(5):
        running = 0.0
        for batch_x, batch_y in loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad(set_to_none=True)
            preds = model(batch_x)
            loss = loss_fn(preds, batch_y)
            loss.backward()
            optimizer.step()
            running += loss.item()
        print(f"[remote] epoch {epoch + 1} loss {running / len(loader):.5f}")

    output_dir = Path("runs/forge-demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), output_dir / "model.pt")
    print(f"[remote] saved checkpoint to {output_dir.resolve()}")


def main() -> None:
    already_remote = ensure_remote()
    if not already_remote:
        return

    if not torch.cuda.is_available():
        raise RuntimeError("Nebius CUDA device required; refusing to run on CPU.")

    device = torch.device("cuda")
    print(f"[remote] running on {socket.gethostname()} with {device}")
    _train(device)


if __name__ == "__main__":
    main()
