# MeoX (MeoMaya)

MeoX is a pure-Python, hardware-aware NLP framework with a clean, modular core for text processing. It supports optional multimodal pipelines, local transformers, a REST API, and hardware-aware execution (CPU/CUDA/MPS).

Install with:

```bash
pip install MeoX
```


[![Documentation](https://img.shields.io/badge/Docs-Site-blue?logo=github)](https://kashyapsinh-gohil.github.io/MeoMaya-Info/) 
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1G61wWs2pzCKJ2lyVkrtYVjIq_lBZPFrW?usp=sharing)


https://github.com/user-attachments/assets/df92d1db-3bd6-445e-a502-fb730513847d

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r meomaya/requirements.txt
```

Run API:

```bash
uvicorn meomaya.api.server:app --host 0.0.0.0 --port 8000
```

Run CLI:

```bash
python -m meomaya "Hello from MeoMaya!" --mode text
```

Offline mode:

```bash
export MEOMAYA_STRICT_OFFLINE=1
```

## License

Polyform Noncommercial 1.0.0. For commercial licensing, contact Kagohil000@gmail.com.


