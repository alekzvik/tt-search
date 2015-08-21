Plan & process
==============

My plan for this task is:
1. Implement dummy API that returns data in right format
2. Implement fetching on frontend, check it shows something
3. Add .csv file parsing
4. Add filters one by one
5. Optimize where needed

By working this way at each step of the process I will have working solution, but with limited functions.

Solutions
=========

There are two ways to approach this problem.
1. Parse .csv files only once and store data between requests. This approach is faster (you can make some computations on load, like sorting products by popularity, you don't have to read files in request-response loop), but eats more memory. I went with this one.
2. Parse .csv on each request. Can be more memory efficient, but pretty slow.
