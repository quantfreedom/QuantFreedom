# Installation
!!! note 
    My goal is to have the best documentation possible and that can only happen if you ask questions or give feedback. So if you have any questions or problems along the way make sure you message me and let me know what you are having a problem with 

!!! warning "Ta-lib and pytables"
    You have to have talib installed and pytables installed. So make sure you go to the bottom of this installation page and install them into your virtual environment

## If you know what your doing
Make sure you create a virtual environment to install all of this into so you don't crowd your main python file.
```
pip install quantfreedom
```
## If you need some guidance
This next part will be for those who need some more guidance on doing the install

## Installing Python
To avoid all types of issues I would suggestion uninstalling anaconda and all of your python installations, unless you know for sure that you need those previous versions for other projects and everything ... or if you are familiar with python already and you know what you are doing you can keep them ... but there have been many pathing issues with having different versions and anaconda installed.

If you do not need to do any of this then you can move to the next section ... but if you do need to uninstall then go and uninstall all of your python versions and anaconda versions ... then go to the python website and download python 3.10.10 and then make sure you select add to path when installing and also install for all users. https://www.python.org/downloads/

## Installing Git
Then make sure you have git installed ... if you don't have it installed, go to the git website and download git and install. To the best of my knowledge all you need to do is just hit next for everything, well thats what I did at least and it worked. https://git-scm.com/downloads

Now you need to configure your user name email from github so open up a cmd terminal and type git config --global user.name ```your github username``` then type git config --global user.email ```the email address you used to sign up to github```. 

An example of this would be <br>
```git config --global user.name quantfreedom``` <br>
```git config --global user.email quantfreedom@gmail.com```

## Checking your paths
Once you have git and python installed we need to check to make sure you were able to add everything to the path properly. Press your windows key and type ```edit the system environment variables``` then click on ```environment variables``` then double click on ```path``` and make sure your python scripts and python for the version you want to use, are at the top then you want your vs code bin below it ... so your order should look something like mine but i think the most important is that the python version you want to use is first ![env var](../assets/env_var.png)

## How to install via VScode
I use vscode and love it so I highly suggest you use it as well even if you are using another IDE ... unless you really love yours then let me know about it because maybe I am missing out on something

### Quick summary
- Go to the terminal menu and start a new terminal in the cmd window
- Make sure you have your virtual environment active and ```pip install quantfreedom```

### More detailed version of installing with vscode
Download vscode https://code.visualstudio.com/download and then go to the extensions tab and search for and install python, jupyter and gitlens. The extensions tab is on the left side menu with an icon that is 4 squares with the upper right square being detached slightly.

Once you have vscode installed launch it and then press ctrl shift p and then type ```terminal select default profile``` .. then make sure you select cmd prompt as the default

Now you want to go to a location on your computer and create a folder called coding because this is where you will store your virtual environment and possibly the cloned repo

### Developers
If you want to help develop the backtester then go to the github link and star and fork the project https://github.com/QuantFreedom1022/QuantFreedom ... if not skip to the next step

Once you have forked it then grab the code of your forked project from the code button and copy the link.

Once you have the link copied then go back to vs code and press ctrl shift p and type git clone and then past the link of the code or if you are signed into your github you can select the new fork from the drop down list.

I would then suggest cloning to the coding folder that you made

### Command Prompt
Before we create the virtual env you have to make sure you are using the cmd prompt
- Go to terminal in the menu and select new terminal
- Once the terminal pops up make sure you are in the cmd prompt.
- If you aren't and have changed your default to the cmd prompt then close out your vs code and open it again and it should work this time.
- It is super important that we are in the cmd prompt or this installation wont work. So if you have problems let me know

If you are in the cmd prompt then make sure the folder location for the cmd prompt is the coding folder you should have created ... if it isn't use cd and type in the location of the coding folder like cd ```"C:\users\my stuff\coding"``` ... make sure you use quotes because if you have spaces in some of your folder names you have to have quotes.

### Creating the virtual Env
Now that you are in the right folder we want to type ```python -m venv qfFree```. This will create a virtual env named qfFree

Next we want to type ```qfFree\Scripts\activate``` to activate the virtual env ... this will make sure anything we install is in the virtual env and not on our global python which is super extra important.

Now we need to create a jupyter notebook kernel by typing ```pip install notebook```. This will install juypter notebook

After that is done then type ```ipython kernel install --user --name=qfFree```

#### Development Environemtnt
If you want to install the dev env then you have to type pip install -e then the location of your cloned repo like ```"C:\user\mystuff\coding\QuantFreedom"```. This will then install the backtester locally so you can work on it.

#### Regular Users
If you are just installing to use the backtester then type ```pip install quantfreedom```

### Selecting Interpreter
Once we have our venv created and everything is pip installed, then we want to do control shift p inside vs code and type ```python: select Interpreter``` and selecting the qfFree venv we just created. If you don't see it then go to enter interpreter path and find the place you created the venv then dig into qfFree then scripts then select python.exe

Next we come back to vscode and do control shift p again and type ```juypter: select interpreter to start jupyter server``` and then select the venv we just created that way it selects that venv every time we use jupyter notebooks.

### Auto Save
Also make sure you have auto save on by going to ```file - preferences - setting``` then type ```auto save``` and then select ```after delay```

For people working in dev env this is for making sure you see the auto updates in the source control for pushing new data and for people who are just working you always want your data saved ... unless you don't you can choose another auto save or turn it off

### Regular Users
Ok so if you are just a regular user you should be done now ... again any problems or questions ask them in the discord.


## Developers
Ok so you have decided you want to contribute and make some nice functions ... let's make it happen! First you have to make sure you have done all the things mentioned previously about installing the dev stuff. If you have done that then lets gets started with developing

In the lower left corner you should see something that says main or dev or stable, but whatever it says click it and make sure you are on the stable branch. 

### Create your own working folder
Once you open the quantfreedom folder then I highly highly highly suggest you work from your own folder and don't edit any original code. If you work on the same file as me and there are updates from both of us then there will be merge problems.

Inside the folder i suggest you make a folder for you and also a test folder where you will store all of the tests you are going to be doing.

### Getting updates
To get updates to your fork
- Make sure you are in the stable version branch
- Go to source control 
- Go the remotes section
- Open the upstream section
- Right click on the stable branch and select merge branch into current branch
- select the first option to merge the upstream branch stable into the local branch stable
- then make sure you sync your changes which basically means you take your local branch and put all the changes into your github fork

##
Installation Problems

!!! warning "Installation Problems"
    If you have any trouble or run into installation errors then what i have found is if i shutdown vscode then open it back up and then reactivate my virtual environment then pip install again it is able to make the full install


## Install TA-Lib
To install ta lib you need to do the following

- Go to this website https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib 
- Download the one that has your python version. You can check your python version ( i run python 3.10.10 on a 64bit windows machine so i am going to choose cp310 ) ... if you don't know your python version in the terminal type python --version.
![talib](../assets/talib.png)
- Once you downloaded the file you need to change your folder path in the terminal by doing cd (download location of folder)
- Then pip install ```entire file name of the tables you downloaded``` 
- example ```pip install TA_Lib‑0.4.24‑cp310‑cp310‑win_amd64.whl```

## Installing pytables
to install pytables you have to do the same thing as talib

- go to this website and download the version of python that you have https://www.lfd.uci.edu/~gohlke/pythonlibs/#pytables
- I have version 3.10.10 right now so I download tables‑3.7.0‑cp310‑cp310‑win_amd64.whl
- Put the file in a folder ( preferably the working directory of the folder that your terminal is working from ) and  if needed change your terminal directory to the directory you put the file in 
- Then pip install ```entire file name of the tables you downloaded``` 
- example ```pip install tables‑3.7.0‑cp310‑cp310‑win_amd64.whl```