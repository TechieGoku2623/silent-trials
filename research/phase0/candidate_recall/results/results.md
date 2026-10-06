# candidate_recall results

Same 200 pairing tasks. Shared corpus size = 260.

NCT search recall is 0.286 because most gold papers in this probe set do not print an NCT. Combined-strategy recall is 1.000. Title and PI+condition+date are not optional if the matcher is going to see the typical psychiatry paper.

| strategy | positive trials | gold pubs | retrieved | recall |
| --- | --- | --- | --- | --- |
| nct_id_search | 120 | 140 | 40 | 0.286 |
| title_search | 120 | 140 | 120 | 0.857 |
| pi_condition_date | 120 | 140 | 140 | 1.000 |
| combined | 120 | 140 | 140 | 1.000 |
