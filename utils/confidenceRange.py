"""

This module defines a number of confidence ranges:

    high confidence: near certainty that this is an appropriate answer
    medium confidence: probably a good answer, but other adapters/DB may have better
    low confidence: potentially relevant, but prefer other adapters/DB
    no confidence: answer is almost certainly uselesss

"""

def _scale(num, min, max):
    return (num * (max-min)) + min

def highConfidence(num):
    """
    Convert num to a "high-confidence" range (i.e. [0.85-1.00])
    param: num any number between 0.00 and 1.00
    """
    return _scale(float(num), 0.85, 1.00)

def mediumConfidence(num):
    """
    Convert num to a "medium-confidence" range (i.e. [0.75-0.85])
    param: num any number between 0.00 and 1.00
    """
    return _scale(float(num), 0.75, 0.85)

def lowConfidence(num):
    """
    Convert num to a "medium-confidence" range (i.e. [0.65-0.75])
    param: num any number between 0.00 and 1.00
    """
    return _scale(float(num), 0.65, 0.75)

def noConfidence(num):
    """
    Convert num to a "medium-confidence" range (i.e. [0.00-0.35])
    param: num any number between 0.00 and 1.00
    """
    return _scale(float(num), 0.00, 0.35)


