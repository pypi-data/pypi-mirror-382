# sqlite-utils-llm

This is a plugin for [sqlite-utils](https://sqlite-utils.datasette.io) that adds a custom SQL function `llm(model, prompt)` that can be used to call out to an LLM model using the [llm](https://llm.datasette.io) command line tool.

## Installation

Have [sqlite-utils](https://sqlite-utils.datasette.io/en/stable/installation.html) and [llm](https://llm.datasette.io/en/stable/setup.html) already installed, then install this package with pip:

```bash
sqlite-utils install sqlite-utils-llm
```

## Example

Given the following `combos.csv` file with ice cream flavor combinations we want to complete the `suggestion` column with a flavor suggestion based on the other two flavors using an LLM.

```csv
flavor1,flavor2,suggestion
vanilla,chocolate,
strawberry,vanilla,
chocolate,strawberry,
mint,lemon,
```

Let's load the data into a SQLite database:

```bash
% sqlite-utils insert icecream.db combos combos.csv --csv --empty-null
```

Now we can use the `llm` function to update the `suggestion` column with a flavor suggestion:

```
% sqlite-utils query icecream.db "UPDATE combos set suggestion=llm('gpt-4o-mini', 'What other flavor would I like if I have choosen ' || flavor1 || ' and ' || flavor2 || '? Return just the name of the flavor.')"
```

Now we can query the table to see the suggestions:

```
% sqlite-utils query icecream.db "SELECT * FROM combos" --table
flavor1     flavor2     suggestion
----------  ----------  ------------
vanilla     chocolate   Strawberry
strawberry  vanilla     Chocolate
chocolate   strawberry  Vanilla
mint        lemon       Basil
```
