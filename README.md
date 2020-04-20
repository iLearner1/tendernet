#To run This project follow the instructions below

create a virtualenv for this, i prefer to use virtualenvwrapper
if you don't have installed then follow the instructions below

for **linux**
`pip install virtualenvwrapper`

for **windows**
`pip install virtualenvwrapper-win`

to create virtualenv
`mkvirtualenv yourenvname`

to activate
`workon yourenvname`

to see list of virtualenv on your machine
`workon`

install required defedency

```
pip install -r requirements.txt
```

then create a file in your project root directory callded `.env`
copy from data from **env-example** and paste inside `.env`

then run migrations

`python manage.py makemigrations`
`python manage.py migrate`

if you are using any of the mail related service please make sure
you have installed **redis**

and run this command on linux
`celery -A tn_first worker -l info`
if you are on windows then
`celery -A tn_first worker -l info --pool=solo`