How to install in cmd line
I am using vscode so just create a new terminal and then do the following

To avoid all types of issues i would suggestion uninstalling anaconda and all of your python installations, unless you know for sure that you need those previous versions for other projects and everything ... or if you are familar with python already and you know what you are doing you can keep them ... but there have been many pathing issues with having different versions and anaconda installed.

So if you do not need to do any of this then you can move to the next section ... but if you do need to unisntall then go an uninstall all of them ... then go to the python website and download python 3.10.10 and then make sure you select add to path when installing and also install for all users.

Also if you have any spaces in the names of your folders make sure you put quotes around the whole thing like "E:/Coding/virtual environments/qfFree/Scripts/activate.bat" ... as you can see i have a space in virtual environments ... so i was getting errors if i ever needed to copy and past a specific directory

Create a new virtual environement by typing this into your command line
```
python -m venv qfFree
```
Now we need to activate the newly created venv
```
qfFree\Scripts\activate
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
