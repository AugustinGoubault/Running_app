COLORS = ["rgba(255, 114, 33, 1)",
          "rgba(0, 0, 0, 0.5)",
          "rgba(255, 114, 33, 0.4)",
          "rgba(255, 250, 160, 1)",
          "rgba(238, 75, 43, 1)"] # orange, black, orange transparent, pastel yellow, bright red

# used to f.e set the limit of fetched activities (default - 30)
ACTIVITIES_PER_PAGE = 200
# current page number with activities
PAGE_NUMBER = 1
# parameters for fetching all activities
GET_ALL_ACTIVITIES_PARAMS = {
    'per_page': ACTIVITIES_PER_PAGE,
    'page': PAGE_NUMBER
}

TH = {'1M': 1, '3M': 3, '6M': 6, '12M': 12}

WEEKDAY = {1: 'Mond', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat', 7: 'Sun'}