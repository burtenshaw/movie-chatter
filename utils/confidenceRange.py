
def _scale(num, min, max):
    return (num * (max-min)) + min


# high confidence: exact statement found in DB
# medium confidence: similar statement found in DB
# low confidence: custom response by logicAdapter
# no confidence: catch-all response

def highConfidence(num):
    """
    Convert num to a "high-confidence" range (i.e. [0.85-1.00]
    param: num any number between 0.00 and 1.00
    """
    return _scale(float(num), 0.85, 1.00)

def mediumConfidence(num):
    """
    Convert num to a "medium-confidence" range (i.e. [0.70-0.85]
    param: num any number between 0.00 and 1.00
    """
    return _scale(float(num), 0.70, 0.85)

def lowConfidence(num):
    """
    Convert num to a "medium-confidence" range (i.e. [0.50-0.70]
    param: num any number between 0.00 and 1.00
    """
    return _scale(float(num), 0.50, 0.70)

def noConfidence(num):
    """
    Convert num to a "medium-confidence" range (i.e. [0.00-0.50]
    param: num any number between 0.00 and 1.00
    """
    return _scale(float(num), 0.00, 0.50)


if __name__ == '__main__':
    assert(highConfidence(0) >= 0.85)
    assert(highConfidence(1) >= 0.85)
    assert(highConfidence(0) <= 1.00)
    assert(highConfidence(1) <= 1.00)

    assert(mediumConfidence(0) >= 0.7)
    assert(mediumConfidence(1) >= 0.7)
    assert(mediumConfidence(0) <= 0.85)
    assert(mediumConfidence(1) <= 0.85)

    assert(lowConfidence(0) >= 0.5)
    assert(lowConfidence(1) >= 0.5)
    assert(lowConfidence(0) <= 0.7)
    assert(lowConfidence(1) <= 0.7)

    assert(noConfidence(0) >= 0.0)
    assert(noConfidence(1) >= 0.0)
    assert(noConfidence(0) <= 0.5)
    assert(noConfidence(1) <= 0.5)