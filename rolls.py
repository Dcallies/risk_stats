"""
Some random statistics of interest.
"""

from copy import deepcopy
import collections
import random

def make_memo_key(o):
    if isinstance(o, collections.Mapping):
        return frozenset((k, make_memo_key(v)) for k, v in o.items())
    if isinstance(o, collections.Iterable):
        return tuple(make_memo_key(e) for e in o)
    return o

def memo(fn):
    def wrap(*args, **kwargs): 
        k = make_memo_key(args), make_memo_key(kwargs)
        if k not in fn._memo:
            fn._memo[k] = fn(*args, **kwargs)    
        return fn._memo[k]
    fn._memo = {}
    return wrap


def rand_roll(num_die):
    if num_die <= 0:
        return ()
    res = random.randint(1, 6)
    return (res) + roll(num_die - 1)

def all_rolls(num_die):
    """Not optimized"""
    if num_die <= 0:
        return []
    if num_die == 1:
        return [[6], [5], [4], [3], [2], [1]]
    ret = []
    for prev in all_rolls(num_die - 1):
        for i in range(6, 0, -1):
            ret.append([i] + prev)
    return ret

def roll_result(atk_roll, def_roll, def_bonus=[]):
    alost = 0
    dlost = 0
    dbi = 0
    for a, d in zip(sorted(atk_roll, reverse=True), sorted(def_roll, reverse=True)):
        db = 0
        if dbi < len(def_bonus):
            db = def_bonus[dbi]
        dbi += 1
        if a > d + db:
            dlost += 1
        else:
            alost += 1
    return alost, dlost

@memo    
def roll_results(attack_die, defense_die, defender_bonus_add=()):
    ret = {"atk_win": 0, "tie": 0, "def_win": 0}
    atk = all_rolls(attack_die)
    defense = all_rolls(defense_die)
    
    for aroll in atk:
        for droll in defense:
            alost, dlost = roll_result(aroll, droll, defender_bonus_add)
            if alost == dlost:
                ret["tie"] += 1
            elif alost > dlost:
                ret["def_win"] += 1
            else:
                ret["atk_win"] += 1
    return ret
    
def roll_results_perc(*args, **kwargs):
    """
    And now in a human consumable form!
    >>> roll_results_perc(1,1)
    {'def_win': '58.33', 'tie': '0.00', 'atk_win': '41.67'}
    >>> roll_results_perc(1,2)
    {'def_win': '74.54', 'tie': '0.00', 'atk_win': '25.46'}
    >>> roll_results_perc(2,1)
    {'def_win': '42.13', 'tie': '0.00', 'atk_win': '57.87'}
    >>> roll_results_perc(2,2)
    {'def_win': '44.83', 'tie': '32.41', 'atk_win': '22.76'}
    >>> roll_results_perc(3,2)
    {'def_win': '29.26', 'tie': '33.58', 'atk_win': '37.17'}
    
    Risk Legacy (bunker):
    >>> roll_results_perc(1,1)
    {'def_win': '72.22', 'tie': '0.00', 'atk_win': '27.78'}
    >>> roll_results_perc(1,2)
    {'def_win': '86.11', 'tie': '0.00', 'atk_win': '13.89'}
    >>> roll_results_perc(2,1)
    {'def_win': '58.33', 'tie': '0.00', 'atk_win': '41.67'}
    >>> roll_results_perc(2,2)
    {'def_win': '53.32', 'tie': '32.02', 'atk_win': '14.66'}
    >>> roll_results_perc(3,1)
    {'def_win': '50.62', 'tie': '0.00', 'atk_win': '49.38'}
    >>> roll_results_perc(3,2)
    {'def_win': '35.24', 'tie': '40.84', 'atk_win': '23.92'}
    
    Risk Legacy (fortification):
    >>> roll_results_perc(1,1)
    {'def_win': '72.22', 'tie': '0.00', 'atk_win': '27.78'}
    >>> roll_results_perc(1,2)
    {'def_win': '86.11', 'tie': '0.00', 'atk_win': '13.89'}
    >>> roll_results_perc(2,1)
    {'def_win': '58.33', 'tie': '0.00', 'atk_win': '41.67'}
    >>> roll_results_perc(2,2)
    {'def_win': '65.28', 'tie': '24.69', 'atk_win': '10.03'}
    >>> roll_results_perc(3,1)
    {'def_win': '50.62', 'tie': '0.00', 'atk_win': '49.38'}
    >>> roll_results_perc(3,2)
    {'def_win': '49.77', 'tie': '31.33', 'atk_win': '18.90'}
    
    Risk Legacy (ammo shortage):
    >>> roll_results_perc(1,1, [-1])
    {'tie': '0.00', 'atk_win': '58.33', 'def_win': '41.67'}
    >>> roll_results_perc(1,2, [-1])
    {'tie': '0.00', 'atk_win': '42.13', 'def_win': '57.87'}
    >>> roll_results_perc(2,1, [-1])
    {'tie': '0.00', 'atk_win': '74.54', 'def_win': '25.46'}
    >>> roll_results_perc(2,2, [-1])
    {'tie': '37.50', 'atk_win': '31.25', 'def_win': '31.25'}
    >>> roll_results_perc(3,1, [-1])
    {'tie': '0.00', 'atk_win': '82.64', 'def_win': '17.36'}
    >>> roll_results_perc(3,2, [-1])
    {'tie': '30.57', 'atk_win': '51.05', 'def_win': '18.38'}
    """
    
    ret = roll_results(*args, **kwargs)
    tot = sum(ret.values())
    if tot:
        return {k: "%0.2f" % (100 * v / tot) for k, v in ret.items()}
    return ret
    

@memo  
def _battle(a, d, db):
    if a <= 0:
        return 0.0, 0.0
    if d <= 0:
        return 1.0, 0.0
    res = roll_results(min(3, a), min(2, d), db)
    tot = sum(res.values())
    
    poss = [
        (res['def_win'] / tot, _battle(a - min(d, 2), d, db), min(d, 2)),
        (res['tie'] / tot, _battle(a - 1, d - 1, db), 1),
        (res['atk_win'] / tot, _battle(a, d - min(3, a), db), 0),
    ]
    
    tot_wp = 0.0
    tot_loss = 0.0
    for chance, (wp, accum_loss), loss in poss:
        tot_wp += chance * wp
        tot_loss += chance * (accum_loss + loss)
    return tot_wp, tot_loss
    
        
def battle(attackers, defenders, defender_bonus_add):
    """
    General results:
    1) With no modifiers, attackers have a slight edge
    2) Bunkers increase attack losses by ~50%, 
       and make each additional defender cost the attacker
       +0.9 attacker from 3-4, and ~1.0 from 5+...
       Basically even odds. It's most effective to keep 2
       for pure efficiency sake.
    3) Fortifications are godly - give defenders very strong 
       advantage, even two defenders can wreak havoc on a large
       attacking force. Attacker must bring 1.5X forces to overcome.
    4) Ammo shortage is basically inverse fortifications (1.5X multiplier), 
       but even worse. Do not store large numbers of troops here, and it's 
       advantageous to attack a larger force as long as you get 3 dice.
    """
    res = _battle(attackers, defenders, defender_bonus_add)
    return {"atk_win_perc": "%0.2f" % (res[0] * 100), "atk_avg_loss": "%0.2f" % res[1]}
    