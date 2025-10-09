# Demo Dataset: Populations

These population samples from 2010 and 2015 can be used as a demonstration dataset for the `table-diff` tool.

## Data

The data is from the following version-controlled DoltHub-hosted data repository:
https://www.dolthub.com/repositories/dolthub/city-populations/query/master

The repository is licensed in the public domain.

The following query was used to generate the data:

```sql
SELECT *, CONCAT(country, "|", state, "|", county, "|", city) AS location_id
FROM `populations`
WHERE yr = 2015
ORDER BY `population` DESC, city ASC
LIMIT 1000;
```

The 2015 version used `yr = 2015` and the 2010 version used `yr = 2010`.
