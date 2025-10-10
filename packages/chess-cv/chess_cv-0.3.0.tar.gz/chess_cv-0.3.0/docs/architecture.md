# Architecture

Detailed information about the Chess CV model architectures, training strategies, and performance characteristics for both the pieces and arrows models.

<figure markdown>
  ![Model Architecture](assets/model.svg)
  <figcaption>CNN architecture for chess piece classification</figcaption>
</figure>

## Pieces Model

### Model Architecture

Chess CV uses a lightweight Convolutional Neural Network (CNN) designed for efficient inference while maintaining high accuracy on 32×32 pixel chess square images.

#### Network Design

```
Input: 32×32×3 RGB image

Conv Layer 1:
├── Conv2d(3 → 16 channels, 3×3 kernel)
├── ReLU activation
└── MaxPool2d(2×2) → 16×16×16

Conv Layer 2:
├── Conv2d(16 → 32 channels, 3×3 kernel)
├── ReLU activation
└── MaxPool2d(2×2) → 8×8×32

Conv Layer 3:
├── Conv2d(32 → 64 channels, 3×3 kernel)
├── ReLU activation
└── MaxPool2d(2×2) → 4×4×64

Flatten → 1024 features

Fully Connected 1:
├── Linear(1024 → 128)
├── ReLU activation
└── Dropout(0.5)

Fully Connected 2:
└── Linear(128 → 13) → Output logits

Softmax → 13-class probabilities
```

#### Model Statistics

- **Total Parameters**: 156,077
- **Trainable Parameters**: 156,077
- **Model Size**: ~600 KB (safetensors format)
- **Input Size**: 32×32×3 (RGB)
- **Output Classes**: 13

#### Class Labels

The model classifies chess squares into 13 categories:

**Black Pieces (6):**

- `bB` – Black Bishop
- `bK` – Black King
- `bN` – Black Knight
- `bP` – Black Pawn
- `bQ` – Black Queen
- `bR` – Black Rook

**White Pieces (6):**

- `wB` – White Bishop
- `wK` – White King
- `wN` – White Knight
- `wP` – White Pawn
- `wQ` – White Queen
- `wR` – White Rook

**Empty (1):**

- `xx` – Empty square

### Performance Characteristics

#### Expected Results

With the default configuration:

- **Test Accuracy**: ~99.94%
- **F1 Score (Macro)**: ~99.94%
- **Training Time**: ~90 minutes (varies by hardware)
- **Inference Speed**: 0.05 ms per image (batch size 8192, varying by hardware)

#### Per-Class Performance

Actual accuracy by piece type (Test Dataset):

| Class | Accuracy | Class | Accuracy |
| ----- | -------- | ----- | -------- |
| bB    | 99.90%   | wB    | 99.90%   |
| bK    | 100.00%  | wK    | 99.81%   |
| bN    | 100.00%  | wN    | 100.00%  |
| bP    | 99.91%   | wP    | 99.90%   |
| bQ    | 99.90%   | wQ    | 100.00%  |
| bR    | 100.00%  | wR    | 100.00%  |
| xx    | 99.91%   |       |          |

#### Evaluation on External Datasets

The model has been evaluated on external datasets to assess generalization:

##### OpenBoard

- **Dataset**: [S1M0N38/chess-cv-openboard](https://huggingface.co/datasets/S1M0N38/chess-cv-openboard)
- **Number of samples**: 6,016
- **Overall Accuracy**: 99.30%
- **F1 Score (Macro)**: 98.26%

Per-class performance on OpenBoard:

| Class | Accuracy | Class | Accuracy |
| ----- | -------- | ----- | -------- |
| bB    | 100.00%  | wB    | 100.00%  |
| bK    | 100.00%  | wK    | 100.00%  |
| bN    | 98.91%   | wN    | 97.94%   |
| bP    | 99.81%   | wP    | 99.61%   |
| bQ    | 97.10%   | wQ    | 98.48%   |
| bR    | 99.32%   | wR    | 98.68%   |
| xx    | 99.24%   |       |          |

##### ChessVision

- **Dataset**: [S1M0N38/chess-cv-chessvision](https://huggingface.co/datasets/S1M0N38/chess-cv-chessvision)
- **Number of samples**: 3,186
- **Overall Accuracy**: 86.38%
- **F1 Score (Macro)**: 83.47%

Per-class performance on ChessVision:

| Class | Accuracy | Class | Accuracy |
| ----- | -------- | ----- | -------- |
| bB    | 90.00%   | wB    | 95.04%   |
| bK    | 84.43%   | wK    | 91.82%   |
| bN    | 100.00%  | wN    | 98.18%   |
| bP    | 83.83%   | wP    | 80.09%   |
| bQ    | 95.70%   | wQ    | 89.66%   |
| bR    | 86.56%   | wR    | 85.08%   |
| xx    | 86.50%   |       |          |

!!! note "Multi-Split Dataset"

    The ChessVision dataset contains multiple splits. All splits are concatenated during evaluation to produce a single comprehensive score.

!!! note "Out of Sample Performance"

    The lower performance on OpenBoard (99.30% accuracy, 98.26% F1) and ChessVision (86.38% accuracy, 83.47% F1) compared to the test set (99.94% accuracy, 99.94% F1) indicates some domain gap between the synthetic training data and these external datasets. ChessVision shows significantly lower performance, particularly on specific piece types like black kings (84.43%) and pawns (80-84%).

### Dataset Characteristics

#### Synthetic Data Generation

The training data is synthetically generated:

**Source Materials:**

- 55 board styles (256×256px)
- 64 piece sets (32×32px)
- Multiple visual styles from chess.com and lichess

**Generation Process:**

1. Render each piece onto each board style
2. Extract 32×32 squares at piece locations
3. Extract empty squares from light and dark squares
4. Split combinations across train/val/test sets

**Data Statistics:**

- **Total Combinations**: ~3,520 (55 boards × 64 piece sets)
- **Images per Combination**: 26 (12 pieces × 2 colors + 2 empty)
- **Total Images**: ~91,500
- **Train Set**: ~64,000 (70%)
- **Validation Set**: ~13,500 (15%)
- **Test Set**: ~13,500 (15%)

#### Class Balance

The dataset is perfectly balanced:

- Each class has equal representation
- Each board-piece combination contributes equally
- Train/val/test splits maintain class balance

---

## Arrows Model

### Model Architecture

#### Overview

The arrows model uses the same SimpleCNN architecture as the pieces model, but is trained to classify arrow overlay components instead of chess pieces. This enables detection and reconstruction of arrow annotations commonly used in chess analysis interfaces.

#### Network Design

The network architecture is identical to the pieces model (see [Pieces Model Architecture](#network-design) above), with the only difference being the output layer dimension.

```
[Same architecture as pieces model]

Fully Connected 2:
└── Linear(128 → 49) → Output logits

Softmax → 49-class probabilities
```

#### Model Statistics

- **Total Parameters**: 156,077 (same as pieces model)
- **Trainable Parameters**: 156,077
- **Model Size**: ~645 KB (safetensors format)
- **Input Size**: 32×32×3 (RGB)
- **Output Classes**: 49

#### Class Labels

The model classifies chess squares into 49 categories representing arrow components:

**Arrow Heads (20):**

Directional arrow tips in 8 cardinal/ordinal directions plus intermediate angles:

- `head-N`, `head-NNE`, `head-NE`, `head-ENE`, `head-E`, `head-ESE`, `head-SE`, `head-SSE`
- `head-S`, `head-SSW`, `head-SW`, `head-WSW`, `head-W`, `head-WNW`, `head-NW`, `head-NNW`

**Arrow Tails (12):**

Directional arrow tails in 8 cardinal/ordinal directions plus intermediate angles:

- `tail-N`, `tail-NNE`, `tail-NE`, `tail-ENE`, `tail-E`, `tail-ESE`, `tail-SE`, `tail-SSE`
- `tail-S`, `tail-SSW`, `tail-SW`, `tail-W`

**Middle Segments (8):**

Arrow shaft segments for straight and diagonal lines:

- `middle-N-S`, `middle-E-W`, `middle-NE-SW`, `middle-SE-NW`
- `middle-N-ENE`, `middle-E-SSE`, `middle-S-WSW`, `middle-W-NNW`
- `middle-N-WNW`, `middle-E-NNE`, `middle-S-ESE`, `middle-W-SSW`

**Corners (4):**

Corner pieces for knight-move arrows (L-shaped patterns):

- `corner-N-E`, `corner-E-S`, `corner-S-W`, `corner-W-N`

**Empty (1):**

- `xx` – Empty square (no arrow)

**Naming Convention:** NSEW refers to compass directions (North/South/East/West), indicating arrow orientation on the board from white's perspective.

### Performance Characteristics

#### Expected Results

With the default configuration:

- **Test Accuracy**: ~99.97%
- **F1 Score (Macro)**: ~99.97%
- **Training Time**: ~9 minutes for 20 epochs (varies by hardware)
- **Inference Speed**: ~0.019 ms per image (batch size 512, varies by hardware)

#### Per-Class Performance

The arrows model achieves near-perfect accuracy across all 49 classes on the synthetic test dataset:

**Summary Statistics:**

- **Highest Accuracy**: 100.00% (13 classes including corner-E-S, head-ESE, middle-E-SSE, etc.)
- **Lowest Accuracy**: 99.79% (tail-S)
- **Mean Accuracy**: 99.97%
- **Classes > 99.9%**: 44 out of 49

**Performance by Component Type:**

| Component Type  | Classes | Avg Accuracy | Range         |
| --------------- | ------- | ------------ | ------------- |
| Arrow Heads     | 20      | 99.98%       | 99.96% - 100% |
| Arrow Tails     | 12      | 99.95%       | 99.79% - 100% |
| Middle Segments | 12      | 99.98%       | 99.96% - 100% |
| Corners         | 4       | 99.97%       | 99.85% - 100% |
| Empty Square    | 1       | 99.82%       | -             |

!!! note "No External Dataset Evaluation"

    Unlike the pieces model, the arrows model has only been evaluated on synthetic test data. No external datasets with annotated arrow components are currently available for out-of-distribution testing.

#### Training Configuration

The arrows model uses different hyperparameters than the pieces model, optimized for the 49-class arrow classification task:

- **Epochs**: 20 (vs 200 for pieces - converges much faster)
- **Batch Size**: 128 (vs 64 for pieces - larger batches for more stable training)
- **Learning Rate**: 0.0005 (vs 0.0003 for pieces)
- **Weight Decay**: 0.00005 (vs 0.0003 for pieces - less regularization needed)
- **Optimizer**: AdamW
- **Early Stopping**: Disabled

### Dataset Characteristics

#### Synthetic Data Generation

The arrows training data is synthetically generated using the same board styles as the pieces model:

**Source Materials:**

- 55 board styles (256×256px)
- Arrow overlay images organized by component type
- Multiple visual styles from chess.com and lichess

**Generation Process:**

1. Render arrow components onto board backgrounds
2. Extract 32×32 squares at arrow locations
3. Extract empty squares from light and dark squares
4. Split combinations across train/val/test sets

**Data Statistics:**

- **Total Images**: ~4.5 million
- **Train Set**: ~3,139,633 (70%)
- **Validation Set**: ~672,253 (15%)
- **Test Set**: ~672,594 (15%)

The significantly larger dataset compared to pieces (~4.5M vs ~91K) is due to the combination of 55 boards × 49 arrow component types, with multiple arrow variants per component type.

#### Class Balance

The dataset maintains balanced class distribution:

- Each arrow component class has equal representation
- Each board-arrow combination contributes equally
- Train/val/test splits maintain class balance

#### Limitations

!!! warning "Single Arrow Component Per Square"

    The model is trained on images containing **at most one arrow component per square**. Classification accuracy degrades significantly when multiple arrow parts overlap in a single square, which can occur with densely annotated boards or crossing arrows.

    **Example failure case**: If a square contains both an arrow head and a perpendicular arrow shaft, the model may only detect one component or produce incorrect predictions.
