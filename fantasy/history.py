"""HISTORICAL ANALYTICS — All-time rivalries, Elo ratings, and verified finals.
LEARN: Every function returns data. None creates Streamlit widgets.
"""
import pandas as pd


def manager_names(teams):
    """One stable manager ID -> most recently available display name."""
    if teams.empty: return {}
    recent = teams.sort_values('Season').drop_duplicates('Owner ID', keep='last')
    return recent.set_index('Owner ID')['Manager'].to_dict()


def rivalry_history(games, teams, include_playoffs=False):
    """Aggregate game outcomes by permanent owner ID across multiple seasons."""
    source = games if include_playoffs else games.loc[games['Phase'].eq('Regular')]
    names = manager_names(teams)
    rows = []
    for g in source.to_dict('records'):
        a, b = g['Home Owner'], g['Away Owner']
        if a == b: continue
        for own, opp, pf, pa, team, opposing_team in (
            (a,b,g['Home Score'],g['Away Score'],g['Home Team'],g['Away Team']),
            (b,a,g['Away Score'],g['Home Score'],g['Away Team'],g['Home Team'])):
            result = 'T' if g['Winner ID'] is None else ('W' if pf > pa else 'L')
            rows.append({'Owner ID': own, 'Opponent ID': opp, 'Manager': names.get(own,team),
                         'Opponent': names.get(opp,opposing_team),'Season':g['Season'],
                         'Week':g['Week'],'Phase':g['Phase'],'PF':pf,'PA':pa,
                         'Margin':pf-pa,'Result':result})
    return pd.DataFrame(rows, columns=['Owner ID','Opponent ID','Manager','Opponent','Season',
                  'Week','Phase','PF','PA','Margin','Result'])


def rivalry_matrix(duels, teams):
    names = manager_names(teams)
    ids = sorted(names, key=lambda k: names[k].casefold())
    wins = duels.loc[duels['Result'].eq('W')].groupby(['Owner ID','Opponent ID']).size() if not duels.empty else pd.Series(dtype=int)
    rows = []
    for a in ids:
        row = {'Manager':names[a]}
        for b in ids:
            row[names[b]] = None if a == b else int(wins.get((a,b),0))
        rows.append(row)
    return pd.DataFrame(rows).set_index('Manager')


def elo_history(games, teams, k=24, carryover=0.75, include_playoffs=True):
    """Simple Elo: expected=1/(1+10^((opponent-rating)/400)).
    Ratings regress toward 1500 at each new season. Only completed results count.
    """
    names = manager_names(teams)
    source = games if include_playoffs else games[games['Phase'].eq('Regular')]
    source = source.sort_values(['Season','Week','Game ID'], kind='stable')
    rating = {}
    rows = []
    current_year = None
    for g in source.to_dict('records'):
        year = int(g['Season'])
        if year != current_year:
            # LEARN: Carry over some skill while allowing a fresh start each season.
            rating = {owner: 1500 + (r-1500)*carryover for owner,r in rating.items()}
            current_year = year
        home, away = g['Home Owner'], g['Away Owner']
        if home == away: continue
        rh, ra = rating.get(home,1500.), rating.get(away,1500.)
        eh = 1/(1+10**((ra-rh)/400))
        sh = .5 if g['Winner ID'] is None else (1. if g['Winner ID']==g['Home ID'] else 0.)
        new_h = rh + k*(sh-eh)
        new_a = ra + k*((1-sh)-(1-eh))
        rating[home],rating[away] = new_h,new_a
        for owner, opponent, old, new in ((home,away,rh,new_h),(away,home,ra,new_a)):
            rows.append({'Season':year,'Week':int(g['Week']),'Game ID':g['Game ID'],
                         'Owner ID':owner,'Manager':names.get(owner,owner),
                         'Opponent':names.get(opponent,opponent),'Elo Before':old,
                         'Elo':new,'Change':new-old,'Phase':g['Phase']})
    return pd.DataFrame(rows, columns=['Season','Week','Game ID','Owner ID','Manager',
              'Opponent','Elo Before','Elo','Change','Phase'])


def championship_history(games, teams, metadata):
    """Conservatively infer champions ONLY from a unique, final winners-bracket game.
    We do NOT infer a champion from regular-season rank or consolation outcomes.
    Completed season must have a game from the winners bracket past the regular season.
    If the export is ambiguous, report it as unverified rather than inventing a winner.
    """
    names = manager_names(teams)
    results=[]
    for year in sorted(metadata):
        season = games[games['Season'].eq(year)]
        reg_weeks = int(metadata[year].get('regular_weeks',14))
        bracket = season[(season['Phase'].eq('Playoffs')) &
                         season.get('Playoff Tier',pd.Series('UNKNOWN',index=season.index)).eq('WINNERS_BRACKET')]
        # A unique latest winners-bracket match must be at least two periods after regular season.
        last_week = int(bracket['Week'].max()) if not bracket.empty else 0
        finals = bracket[bracket['Week'].eq(last_week)]
        if last_week >= reg_weeks+2 and len(finals)==1 and pd.notna(finals.iloc[0]['Winner ID']):
            g=finals.iloc[0]
            who=g['Home Owner'] if g['Winner ID']==g['Home ID'] else g['Away Owner']
            runner=g['Away Owner'] if who==g['Home Owner'] else g['Home Owner']
            results.append({'Season':int(year),'Champion':names.get(who,who),
                            'Runner-up':names.get(runner,runner),'Champion ID':who,
                            'Runner-up ID':runner,'Final Week':last_week,'Status':'Inferred from completed winners-bracket final'})
        else:
            results.append({'Season':int(year),'Champion':None,'Runner-up':None,
                            'Champion ID':None,'Runner-up ID':None,'Final Week':None,
                            'Status':'Not verified — check playoff bracket/export'})
    return pd.DataFrame(results)
