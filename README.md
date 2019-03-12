# deduplicate
- App to remove duplication of PL Numbers and Product names, and human errors with the intent to centralize the Railways Database.

- Setup mongoDB locally
- Create a new database named sihdata (type "use sihdata" in the the mongo shell)
- Inside sihdata, create a new collection named newdata (type "db.createCollection("newdata")" in the shell)
- Seed the newdata collection with data of type {"PL Number": eightdigitnumber , "type":"old" , "Description":"Some description"}

- Use "pip install -r requirements.txt" in the main directory to install all the dependencies

- Run the app with "flask run"

- You must have Python 3.7.2 installed.
