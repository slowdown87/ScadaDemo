"""
LSTM Model for Remaining Useful Life Prediction
基于LSTM的剩余寿命预测模型
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import json
import os

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from .data_window import DataWindow

logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    """训练配置"""
    input_size: int = 6
    hidden_size: int = 64
    num_layers: int = 2
    output_size: int = 1
    dropout: float = 0.2
    learning_rate: float = 0.001
    epochs: int = 100
    batch_size: int = 32
    sequence_length: int = 30
    train_split: float = 0.8


@dataclass
class TrainingResult:
    """训练结果"""
    train_loss_history: List[float]
    val_loss_history: List[float]
    final_train_loss: float
    final_val_loss: float
    best_epoch: int
    training_time_seconds: float


class LSTMModel(nn.Module):
    """LSTM预测模型"""

    def __init__(
        self,
        input_size: int = 6,
        hidden_size: int = 64,
        num_layers: int = 2,
        output_size: int = 1,
        dropout: float = 0.2
    ):
        """
        初始化LSTM模型

        Args:
            input_size: 输入特征数量
            hidden_size: 隐藏层大小
            num_layers: LSTM层数
            output_size: 输出大小
            dropout: Dropout比率
        """
        super(LSTMModel, self).__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = output_size

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )

        self.fc = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, output_size)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向传播

        Args:
            x: 输入张量 (batch_size, sequence_length, input_size)

        Returns:
            输出张量 (batch_size, output_size)
        """
        lstm_out, _ = self.lstm(x)

        last_output = lstm_out[:, -1, :]

        output = self.fc(last_output)

        return output


class LSTMTrainer:
    """LSTM模型训练器"""

    def __init__(
        self,
        model: LSTMModel,
        config: Optional[TrainingConfig] = None
    ):
        """
        初始化训练器

        Args:
            model: LSTM模型
            config: 训练配置
        """
        self.model = model
        self.config = config or TrainingConfig()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=self.config.learning_rate
        )
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.5,
            patience=10,
            verbose=True
        )

        self.train_loss_history: List[float] = []
        self.val_loss_history: List[float] = []

    def prepare_data(
        self,
        data: np.ndarray,
        labels: np.ndarray
    ) -> Tuple[DataLoader, DataLoader]:
        """
        准备训练数据

        Args:
            data: 特征数据 (n_samples, sequence_length, input_size)
            labels: 标签数据 (n_samples,)

        Returns:
            (训练数据加载器, 验证数据加载器)
        """
        data_tensor = torch.FloatTensor(data)
        labels_tensor = torch.FloatTensor(labels).unsqueeze(1)

        n_samples = len(data)
        n_train = int(n_samples * self.config.train_split)

        train_dataset = TensorDataset(
            data_tensor[:n_train],
            labels_tensor[:n_train]
        )
        val_dataset = TensorDataset(
            data_tensor[n_train:],
            labels_tensor[n_train:]
        )

        train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.batch_size,
            shuffle=False
        )

        return train_loader, val_loader

    def train_epoch(self, train_loader: DataLoader) -> float:
        """训练一个epoch"""
        self.model.train()
        total_loss = 0.0
        n_batches = 0

        for batch_data, batch_labels in train_loader:
            batch_data = batch_data.to(self.device)
            batch_labels = batch_labels.to(self.device)

            self.optimizer.zero_grad()
            outputs = self.model(batch_data)
            loss = self.criterion(outputs, batch_labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()

            total_loss += loss.item()
            n_batches += 1

        return total_loss / n_batches if n_batches > 0 else 0.0

    def validate(self, val_loader: DataLoader) -> float:
        """验证模型"""
        self.model.eval()
        total_loss = 0.0
        n_batches = 0

        with torch.no_grad():
            for batch_data, batch_labels in val_loader:
                batch_data = batch_data.to(self.device)
                batch_labels = batch_labels.to(self.device)

                outputs = self.model(batch_data)
                loss = self.criterion(outputs, batch_labels)

                total_loss += loss.item()
                n_batches += 1

        return total_loss / n_batches if n_batches > 0 else 0.0

    def train(
        self,
        data: np.ndarray,
        labels: np.ndarray
    ) -> TrainingResult:
        """
        训练模型

        Args:
            data: 特征数据
            labels: 标签数据

        Returns:
            训练结果
        """
        import time
        start_time = time.time()

        train_loader, val_loader = self.prepare_data(data, labels)

        best_val_loss = float('inf')
        best_epoch = 0
        patience_counter = 0
        max_patience = 20

        logger.info(f"开始训练，共 {self.config.epochs} epochs")

        for epoch in range(self.config.epochs):
            train_loss = self.train_epoch(train_loader)
            val_loss = self.validate(val_loader)

            self.train_loss_history.append(train_loss)
            self.val_loss_history.append(val_loss)

            self.scheduler.step(val_loss)

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_epoch = epoch
                patience_counter = 0
                self.save_checkpoint(f"best_model_epoch_{epoch}.pt")
            else:
                patience_counter += 1

            if (epoch + 1) % 10 == 0:
                logger.info(
                    f"Epoch {epoch+1}/{self.config.epochs} - "
                    f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}"
                )

            if patience_counter >= max_patience:
                logger.info(f"早停: 验证损失连续 {max_patience} 个epoch未改善")
                break

        training_time = time.time() - start_time

        logger.info(f"训练完成，耗时 {training_time:.2f} 秒")

        return TrainingResult(
            train_loss_history=self.train_loss_history,
            val_loss_history=self.val_loss_history,
            final_train_loss=self.train_loss_history[-1],
            final_val_loss=self.val_loss_history[-1],
            best_epoch=best_epoch,
            training_time_seconds=training_time
        )

    def predict(self, data: np.ndarray) -> np.ndarray:
        """
        预测

        Args:
            data: 输入数据 (n_samples, sequence_length, input_size)

        Returns:
            预测结果 (n_samples,)
        """
        self.model.eval()
        data_tensor = torch.FloatTensor(data).to(self.device)

        with torch.no_grad():
            predictions = self.model(data_tensor)

        return predictions.cpu().numpy().flatten()

    def save_checkpoint(self, path: str):
        """保存模型检查点"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'config': self.config,
            'train_loss_history': self.train_loss_history,
            'val_loss_history': self.val_loss_history,
        }, path)

    def load_checkpoint(self, path: str):
        """加载模型检查点"""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.train_loss_history = checkpoint.get('train_loss_history', [])
        self.val_loss_history = checkpoint.get('val_loss_history', [])

    def save_model(self, path: str):
        """保存完整模型"""
        torch.save({
            'model': self.model,
            'config': self.config,
        }, path)

    @classmethod
    def load_model(cls, path: str) -> 'LSTMTrainer':
        """加载模型"""
        checkpoint = torch.load(path, map_location='cpu')
        model = checkpoint['model']
        config = checkpoint['config']
        trainer = cls(model, config)
        return trainer


class LSTMInference:
    """LSTM模型推理"""

    def __init__(self, model_path: str):
        """
        初始化推理器

        Args:
            model_path: 模型路径
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        checkpoint = torch.load(model_path, map_location=self.device)
        self.model = checkpoint['model']
        self.model.eval()

    def predict(self, sequence: np.ndarray) -> float:
        """
        预测单个序列

        Args:
            sequence: 输入序列 (sequence_length, input_size)

        Returns:
            预测值
        """
        data_tensor = torch.FloatTensor(sequence).unsqueeze(0).to(self.device)

        with torch.no_grad():
            prediction = self.model(data_tensor)

        return float(prediction.cpu().numpy()[0][0])

    def predict_batch(self, sequences: np.ndarray) -> np.ndarray:
        """
        批量预测

        Args:
            sequences: 输入序列 (n_samples, sequence_length, input_size)

        Returns:
            预测结果 (n_samples,)
        """
        data_tensor = torch.FloatTensor(sequences).to(self.device)

        with torch.no_grad():
            predictions = self.model(data_tensor)

        return predictions.cpu().numpy().flatten()
