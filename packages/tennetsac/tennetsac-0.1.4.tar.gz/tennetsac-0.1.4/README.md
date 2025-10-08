# TeNNet-SAC

TeNNet-SAC (Thermodynamics-Embedded Neural Network for Segment Activity Coefficients) is a machine learning framework designed to predict molecular activity coefficients in multicomponent systems using only molecular SMILES strings, composition, and temperature as input. 

This project provides:

1. **σ-profile prediction model**, including surface area and molecular volume estimation  
2. **Activity coefficient prediction** with two versions:  
   - **Base model**: trained on synthetic data generated from the COSMO-SAC model  
   - **Fine-tuned model**: further optimized using high-quality experimental data  

## Features

- Predicts activity coefficients beyond binary systems
- Requires only SMILES strings, mole fractions, and temperature
- Hard-constraint architecture ensures thermodynamic consistency  
- Modular design: supports use of σ-profiles from QC calculations  
- Robust and generalizable via two-stage training: synthetic COSMO-SAC pretraining followed by experimental fine-tuning, preserving physical consistency

## Citation

Yue Yang, Shiang-Tai Lin. *Physics-Embedded Machine Learning Model for Phase Equilibrium Prediction in Multicomponent Systems*. *Journal of Chemical Information and Modeling*, 2025. [DOI: 10.1021/acs.jcim.5c01804](https://doi.org/10.1021/acs.jcim.5c01804)

## References

This project builds upon the following foundational models. If you use this project in your research, we encourage you to cite them as well:

- **ChemBERTa-2**  
Ahmad, W.; Simon, E.; Chithrananda, S.; Grand, G.; Ramsundar, B. Chemberta-2: Towards chemical foundation models. arXiv preprint arXiv:2209.01712 2022.
[https://arxiv.org/abs/2209.01712](https://arxiv.org/abs/2209.01712)

- **SMI-TED**  
Soares, E.; Shirasuna, V.; Brazil, E. V.; Cerqueira, R.; Zubarev, D.; Schmidt, K. A large encoder-decoder family of foundation models for chemical language. arXiv preprint arXiv:2407.20267 2024.
[https://arxiv.org/abs/2407.20267](https://arxiv.org/abs/2407.20267)

### External Code Acknowledgment

The folder `smi_ted_light/` is adapted from the [SMI-TED](https://github.com/IBM/materials/tree/main/models/smi_ted) repository by Soares et al., with only minimal modifications. The core implementation remains unchanged. Full credit goes to the original authors.

## License

MIT License. See [LICENSE](LICENSE) for details.

---

Maintained by **Yue Yang** ([@yueyue2299](https://github.com/yueyue2299)).

COMET, Department of Chemical Engineering, National Taiwan University  
