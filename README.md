# PROJ-H402 Robot Skill Wizard

## Description

This is the repositery for the code of the Robot Skill Wizard project. 

## Dependencies and Setup

The required libraries, included in `requirement.txt`, are the following :

- [PyQt 5](https://pypi.org/project/PyQt5/) Graphical Interface : `pip install PyQt5`
- [Lark](https://pypi.org/project/lark/) Parser : `pip install lark`

They can also all be installed simply with the following command :
```commandline
pip install -r requirements.txt 
```

## Usage

The application is launched from the src.main module, using the following command :
```commandline
python -m src.main
```

This should open a blank window, prompting the user to either create a mission (CTRL + N) or open an existing one (CTRL + O).
Alternatively, those actions are available in the top-left *file* menu.

Once a mission is open, the user can navigate the different elements in the right side panel. The selected element is 
displayed in the main center panel. The user can select skills, behaviors, or one of the editor that can be found in the
settings tab in the top right. This allows to customize the mission arena or the objective functions. Those editors can also
be accessed via the *edit* menu in top left. 

A mission can then be saved to a file (CTRL + S). Additionaly, it is possible to generate the ARGoS file (CTRL + G) 
and the C++ files (CTRL + H), again also accessible from the *file* menu.