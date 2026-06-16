# ⚡ SINTONIA — Máquinas Elétricas

**S**istemas **I**nterativos para **T**eoria e **O**timização no **N**ível de **I**nterpretação e **A**prendizagem

Recurso Educacional Digital (RED) de acesso livre para o estudo de **Máquinas Elétricas e Conversão Eletromecânica de Energia**.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sintonia-maquinas.streamlit.app)

---

## 📦 Módulos

| # | Módulo | Status |
|---|--------|--------|
| 01 | 🔋 Introdução à Conversão Eletromecânica de Energia | 🚧 Em construção |
| 02 | 🔄 Transformadores | 🚧 Em construção |
| 03 | ⚙️ Máquinas Elétricas de Corrente Contínua | 🚧 Em construção |
| 04 | 🌀 Máquinas CA Polifásicas — Indução | 🚧 Em construção |
| 05 | 🔁 Máquinas CA Polifásicas — Síncrona | 🚧 Em construção |
| 06 | 🔌 Máquinas de Pequeno Porte | 🚧 Em construção |
| 07 | 🔬 Máquinas Especiais | 🚧 Em construção |

## 🚀 Execução local

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 🏛️ Informações

- **Autor:** Marcus V A Fernandes
- **Instituição:** IFRN — Campus Natal-Central (CNAT) · Diretoria de Indústria
- **Contato:** marcus.fernandes@ifrn.edu.br
- **Versão:** 1.0 · 2026
- **Licença:** Acesso livre para fins educacionais

## 📁 Estrutura do projeto

```
SINTONIA-ME/
├── streamlit_app.py                # Entrypoint principal — navegação e home
├── requirements.txt
├── README.md
└── modulos/
    ├── __init__.py
    ├── intro_conversao.py          # Módulo 1 — Conversão Eletromecânica
    ├── transformadores.py          # Módulo 2 — Transformadores
    ├── maquinas_cc.py              # Módulo 3 — Máquinas CC
    ├── maquinas_inducao.py         # Módulo 4 — Máquinas de Indução
    ├── maquinas_sincrona.py        # Módulo 5 — Máquinas Síncronas
    ├── maquinas_pequeno_porte.py   # Módulo 6 — Máquinas de Pequeno Porte
    └── maquinas_especiais.py       # Módulo 7 — Máquinas Especiais
```
