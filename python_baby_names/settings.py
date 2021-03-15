# FILENAME_PREFIX represents what the filename starts with.
FILENAME_PREFIX = 'baby'
FILE_TYPE = '.html'

# EXPECTED_COLUMN_ORDER represents the expected column names of each HTML file.
# Must be lowercase.
EXPECTED_COLUMN_ORDER = ['rank', 'male name', 'female name']

RELATIVE_PATH = './python_baby_names'


# These HTML files only use h3 and h2 tags.
# All except one uses h3 tags.
# None use an h1 tag, but I am future proofing in case they use it
# the future.
HEADER_TAGS = ['h3', 'h2', 'h1']
