# Welcome
This is a project aiming at predicting binary outcomes of badminton matches (i.e., who will win?). The accuracy is around 70%.


# Getting data

Use the scrapers provided to fetch all the data out there from the internation badminton society's website, `http://bwfbadminton.com`.
It will store all data in a SQLite database as `db/app.db`.

```
python -m scraper.players
python -m scraper.rankings
python -m scraper.tournaments
```

# Generating features
This will take some time. It will store a pickle representation of the entire dataset once done. You will have to regenerate this again, once you've fetched new data.

```
python -m model.make_data
```

# Training model
This will also save a pickled version of the Keras classifier.
```
python -m train_nn
```

# Predicting new matches

See `model/pred.py`.