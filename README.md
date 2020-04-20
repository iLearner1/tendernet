#To run This project follow the instructions below

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
