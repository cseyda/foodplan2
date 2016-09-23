# foodplan

A set of programs to track macros and weight, and do meal plans.

## Short history
Started as simple cli tool. Idea was to parse some files keeping a food log, food macros, weight and show the current weeks stats.

But parsing times kept getting longer, and additional functionality was needed (meal plan gui). Therefore there are rewrites of large parts, while keeping the input format.

## Going forward
Old input files will be archived, only the current week of the food log will be parsed, same with the file keeping macros. Information from the archived files will be kept in a db file (sqlite3).