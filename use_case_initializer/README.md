This application is a module of the INCISIVE infrastructure. It is in charge of decoupling the INCISIVE logic from the AI Engines. 

Perfoms the following actions depending on the use case:
- training from scratch:
    - fill input directory with the dataset downloaded from the INCISIVE infrastructure
    - create output model directory
- training from a pretrained model:
    - fill input directory with the dataset downloaded from the INCISIVE infrastructure
    - fill input directory with the pretrained model downloaded from the INCISIVE infrastructure
    - create output model directory
- evaluting a pretrained model;
    - fill input directory with the dataset downloaded from the INCISIVE infrastructure
    - fill input directory with the pretrained model downloaded from the INCISIVE infrastructure
    - create output results directory
