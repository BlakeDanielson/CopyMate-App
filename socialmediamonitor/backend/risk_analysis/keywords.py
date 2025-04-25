"""
Keyword lists and mapping for the Risk Analysis Engine.
This module contains comprehensive keyword lists for each risk category
and utility functions for keyword management.
"""
from backend.models.base import RiskCategory

# Comprehensive keyword lists for each risk category
KEYWORD_CATEGORIES = {
    RiskCategory.HATE_SPEECH.value: [
        "hate", "extremist", "radical", "supremacy", "nazi", "racism", "racist",
        "antisemitism", "antisemitic", "bigot", "bigotry", "discrimination",
        "homophobia", "homophobic", "islamophobia", "islamophobic", "xenophobia",
        "xenophobic", "white power", "ethnic cleansing", "genocide", "kkk",
        "neo-nazi", "racial slur", "racial hatred", "religious hatred", "hate group",
        "hate speech", "hate crime", "ethnic hatred", "racial superiority"
    ],
    
    RiskCategory.SELF_HARM.value: [
        "suicide", "suicidal", "self-harm", "self harm", "cutting", "kill myself",
        "end my life", "take my own life", "don't want to live", "ways to die",
        "how to kill", "painless death", "suicide method", "suicide note",
        "suicide plan", "suicide pact", "anorexia tips", "bulimia tips",
        "pro-ana", "pro-mia", "thinspiration", "depression", "hopeless",
        "self-injury", "self-mutilation", "self-destruction"
    ],
    
    RiskCategory.GRAPHIC_VIOLENCE.value: [
        "gore", "graphic violence", "brutal", "brutality", "torture", "beheading",
        "execution", "murder", "killing", "blood", "bloody", "massacre", "slaughter",
        "dismemberment", "mutilation", "gruesome", "gory", "horrific", "violent death",
        "extreme violence", "deadly assault", "violent attack", "shooting footage",
        "stabbing video", "real death", "real murder", "real killing", "snuff"
    ],
    
    RiskCategory.EXPLICIT_CONTENT.value: [
        "pornography", "porn", "xxx", "adult content", "explicit content", "nude",
        "nudity", "sexual content", "sexual activity", "sexual act", "sex video",
        "sex tape", "onlyfans", "adult film", "adult video", "adult movie",
        "sexually explicit", "erotic", "erotica", "strip", "striptease",
        "webcam show", "cam girl", "cam boy", "adult performer", "adult star"
    ],
    
    RiskCategory.BULLYING.value: [
        "bullying", "cyberbullying", "harassment", "harassing", "troll", "trolling",
        "hater", "hating", "mock", "mocking", "ridicule", "ridiculing", "humiliate",
        "humiliation", "shame", "shaming", "body shaming", "fat shaming", "insult",
        "insulting", "taunt", "taunting", "name calling", "verbal abuse", "bully victim",
        "online harassment", "internet troll", "hate comment", "hate message"
    ],
    
    RiskCategory.DANGEROUS_CHALLENGES.value: [
        "dangerous challenge", "viral challenge", "tide pod", "tide pod challenge",
        "fire challenge", "choking challenge", "blackout challenge", "pass out challenge",
        "skull breaker", "skull breaker challenge", "salt and ice", "salt and ice challenge",
        "cinnamon challenge", "bird box challenge", "kiki challenge", "car surfing",
        "blue whale", "blue whale challenge", "momo", "momo challenge", "outlet challenge",
        "penny challenge", "benadryl challenge", "milk crate challenge", "devious lick"
    ],
    
    RiskCategory.MISINFORMATION.value: [
        "fake news", "misinformation", "disinformation", "conspiracy", "conspiracy theory",
        "hoax", "propaganda", "misleading", "false information", "false claim", "debunked",
        "fact check", "pseudoscience", "anti-vax", "anti-vaccine", "climate denial",
        "climate change denial", "flat earth", "false flag", "crisis actor", "deep state",
        "qanon", "q-anon", "deep fake", "doctored video", "manipulated media"
    ]
}

# Flattened list of all keywords for easier searching
ALL_KEYWORDS = [keyword for keywords in KEYWORD_CATEGORIES.values() for keyword in keywords]

# Mapping from individual keyword back to its category (for assigning flags)
KEYWORD_TO_CATEGORY = {
    keyword: category
    for category, keywords in KEYWORD_CATEGORIES.items()
    for keyword in keywords
}

# Severity weights for keywords - some keywords indicate higher risk than others
KEYWORD_SEVERITY = {
    # High severity keywords (weight 3)
    "suicide method": 3, "suicide plan": 3, "kill myself": 3, "ways to die": 3,
    "how to kill": 3, "genocide": 3, "ethnic cleansing": 3, "beheading": 3,
    "execution": 3, "murder": 3, "pornography": 3, "xxx": 3, "blue whale challenge": 3,
    "tide pod challenge": 3, "choking challenge": 3, "blackout challenge": 3,
    
    # Medium severity keywords (weight 2)
    "suicide": 2, "self-harm": 2, "cutting": 2, "hate speech": 2, "hate crime": 2,
    "racist": 2, "antisemitic": 2, "homophobic": 2, "gore": 2, "torture": 2,
    "explicit content": 2, "sexual content": 2, "bullying": 2, "cyberbullying": 2,
    "dangerous challenge": 2, "viral challenge": 2, "skull breaker challenge": 2,
    
    # All other keywords default to weight 1
}

def get_keyword_severity(keyword):
    """
    Get the severity weight for a keyword.
    
    Args:
        keyword: The keyword to check
        
    Returns:
        int: Severity weight (1-3, with 3 being highest severity)
    """
    return KEYWORD_SEVERITY.get(keyword, 1)

def calculate_risk_score(matched_keywords):
    """
    Calculate a risk score based on matched keywords and their severity.
    
    Args:
        matched_keywords: List of matched keywords
        
    Returns:
        float: Risk score between 0.0 and 1.0
    """
    if not matched_keywords:
        return 0.0
        
    total_weight = sum(get_keyword_severity(kw) for kw in matched_keywords)
    # Normalize to a 0-1 scale, with diminishing returns for many matches
    # Using a logarithmic scale to prevent extreme scores with many matches
    import math
    normalized_score = min(1.0, 0.3 * math.log(1 + total_weight, 2))
    return normalized_score