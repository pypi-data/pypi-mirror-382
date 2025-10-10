import re

class PatternMatcher:
    def match(self, text, pattern):
        return re.match(pattern, text)
