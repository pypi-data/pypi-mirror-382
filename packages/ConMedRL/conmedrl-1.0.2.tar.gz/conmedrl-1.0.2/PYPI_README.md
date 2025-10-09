# ConMED-RL: An OCRL-Based Toolkit for Medical Decision Support

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/conmedrl.svg)](https://badge.fury.io/py/conmedrl)

**ConMED-RL** is an **Offline Constrained Reinforcement Learning (OCRL)** toolkit designed for critical care decision support. The toolkit provides state-of-the-art algorithms for medical decision-making tasks, with a focus on ICU discharge and extubation decisions.

This toolkit is based on research published in *IISE Transactions on Healthcare Systems Engineering* and is actively developed by researchers at TUM School of Computation, Information and Technology.

## 🚀 Quick Start

### Installation

Install ConMED-RL using pip:

```bash
pip install conmedrl
```

### Basic Usage

```python
from ConMedRL import FQE, FQI, TrainDataLoader, ValTestDataLoader

# Load your clinical data
train_loader = TrainDataLoader(
    state_df=state_data,
    outcome_df=outcome_data,
    train_ids=train_patient_ids
)

# Initialize and train FQI agent
from ConMedRL import RLTraining

trainer = RLTraining(
    state_dim=state_dim,
    action_dim=action_dim,
    train_loader=train_loader
)

# Train the model
trainer.fqi_agent_train(epochs=100)

# Evaluate using FQE
fqe_results = trainer.fqe_agent_evaluate(test_loader)
```

## 📦 Core Components

### Offline Reinforcement Learning Algorithms

- **Fitted Q-Evaluation (FQE)**: Policy evaluation for offline data
- **Fitted Q-Iteration (FQI)**: Policy optimization with constraint handling
- **Replay Buffer**: Efficient data management for training
- **Custom RL Configurator**: Flexible configuration for different clinical scenarios

### Data Processing

- **TrainDataLoader**: Handles training data preparation and batch generation
- **ValTestDataLoader**: Manages validation and testing data processing
- Support for custom done conditions and constraint cost functions

## 🏥 Key Features

- **Offline Learning**: Train models on historical clinical data without online interaction
- **Constraint Handling**: Built-in support for clinical safety constraints
- **Flexible Architecture**: Easy integration with existing clinical datasets
- **Medical Focus**: Specifically designed for ICU decision-making scenarios
- **Research-Backed**: Based on peer-reviewed methodologies

## 📊 Use Cases

ConMED-RL has been successfully applied to:

- **ICU Discharge Decision-Making**: Optimizing timing and safety of patient discharge
- **Mechanical Ventilation Weaning**: Supporting extubation decisions with constraint satisfaction
- **Multi-Constraint Clinical Decisions**: Balancing multiple clinical objectives and safety requirements

## 🔧 Advanced Configuration

### Custom Reward and Constraint Functions

```python
from ConMedRL import RLConfig_custom

config = RLConfig_custom(
    state_dim=50,
    action_dim=2,
    hidden_layers=[128, 128],
    learning_rate=0.001,
    gamma=0.99
)

# Use custom configuration in training
trainer = RLTraining(config=config, train_loader=train_loader)
```

### Data Preprocessing

ConMED-RL expects data in MDP format:
- **State Table**: Physiological measurements and clinical variables
- **Outcome Table**: Actions, rewards, and terminal indicators

See the [full documentation](https://github.com/smt970913/ConMED-RL) for data preprocessing examples.

## 📖 Documentation and Examples

For comprehensive guides, tutorials, and examples:

- **GitHub Repository**: [https://github.com/smt970913/ConMED-RL](https://github.com/smt970913/ConMED-RL)
- **Library Usage Guide**: See `LIBRARY_USAGE.md` in the repository
- **Example Notebooks**: Interactive Jupyter notebooks for MIMIC-IV datasets
- **Web Application Demo**: Clinical decision support interface

## 🔬 Research and Citation

This toolkit is based on research published in academic journals. If you use ConMED-RL in your research, please cite:

```bibtex
@article{sun2025conmedrl,
  title={ConMED-RL: An Offline Constrained Reinforcement Learning Framework for ICU Discharge Decision-Making},
  author={Sun, Maotong and Xie, Jingui},
  journal={IISE Transactions on Healthcare Systems Engineering},
  year={2025}
}
```

## 🛠️ Requirements

- Python 3.8 or higher
- PyTorch
- NumPy
- Pandas
- scikit-learn

All dependencies are automatically installed with the package.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/smt970913/ConMED-RL/blob/main/LICENSE) file for details.

## 👥 Authors and Contact

- **Maotong Sun** - maotong.sun@tum.de
- **Jingui Xie** - jingui.xie@tum.de

Technical University of Munich (TUM)  
School of Computation, Information and Technology

## 🤝 Contributing

We welcome contributions! For major changes, please open an issue first to discuss what you would like to change.

For development setup and contributing guidelines, visit the [GitHub repository](https://github.com/smt970913/ConMED-RL).

## 🔗 Links

- **PyPI**: [https://pypi.org/project/conmedrl/](https://pypi.org/project/conmedrl/)
- **GitHub**: [https://github.com/smt970913/ConMED-RL](https://github.com/smt970913/ConMED-RL)
- **Issues**: [https://github.com/smt970913/ConMED-RL/issues](https://github.com/smt970913/ConMED-RL/issues)
- **Documentation**: [https://github.com/smt970913/ConMED-RL#readme](https://github.com/smt970913/ConMED-RL#readme)

## ⚠️ Disclaimer

This toolkit is intended for research purposes. Clinical deployment requires appropriate validation, regulatory approval, and should only be used by qualified healthcare professionals in accordance with institutional guidelines and applicable regulations.

---

**Keywords**: reinforcement learning, constrained reinforcement learning, offline reinforcement learning, clinical decision support, healthcare, ICU, critical care, machine learning, artificial intelligence
