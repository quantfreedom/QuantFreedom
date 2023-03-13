How to install in cmd line
I am using vscode so just create a new terminal and then do the following

Create a new virtual environement by typing this into your command line
```
python -m venv venv
```
Now we need to activate the newly created venv
```
venv\Scripts\activate
```
once it is activated we want to create a ipython kernel so we can use the cell by cell jupyter coding
```
ipython kernel install --user --name=venv
```
last if you still have your ven active then copy past the following pip install
```
pip install -U git+https://github.com/QuantFreedom1022/QuantFreedom
```
You now should have created a veritual environment
This is a test of adding info

Installation Problems

If you have any trouble or run into installation errors then what i have found is if i shutdown vscode then open it back up and then reactivate my virtual environment then pip install again it is able to make the full install

These are the updated installs i added to setup.py
