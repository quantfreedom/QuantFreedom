create empty branch
git switch --orphan <new branch>
git commit --allow-empty -m "Initial commit on orphan branch"
git push -u origin <new branch>

configure your user.name and user.email in git
In your shell, add your user name:

git config --global user.name "your_username"

Add your email address:

git config --global user.email "your_email_address@example.com"

To check the configuration, run:

git config --global --list
