# Algoritmy pro AI

 1) **RandomAI**

    RandomAI vybere v každém tahu náhodné **relevantní pole** - tj.
    takové, které má ve vzdálenosti nejvýše 2 jiný symbol.
    Pokud je hrací pole prázdné, hraje doprostřed.

 2) **RuleAI**

    RuleAI se řídí několika jednoduchými pravidly:

	1) Pokud máš otevřenou souvislou čtyřku, zahrej vítězný tah
	2) Pokud má soupeř otevřenou souvislou čtyřku, zablokuj ji
	3) Pokud máš z obou stran otevřenou souvislou trojku, rozšiř ji na čtyřku
	4) Pokud má soupeř z obou stran otevřenou souvislou trojku, zablokuj ji
	5) Pokud máš z obou stran otevřenou souvislou dvojku, rozšiř ji na trojku
	6) Pokud má soupeř z obou stran otevřenou souvislou dvojku, zablokuj ji
	7) Jinak zahrej náhodný relevantní tah

 3) **MinimaxAI**

    Tento algoritmus prochází strom hry pomocí algoritmus minimaxu. Je zde využito
    alpha-beta prořezávání. Z časových důvodů algoritmus v každé hloubce vybere
    30 nejperspektivnějších pozic, které dále prozkoumává.

 4) **CombinedAI**

    CombinedAI je kombinací předchozích dvou algoritmů. Nejprve ověří, že ani jedna
    ze stran nemá souvislou čtyřku a AI nemá souvislou trojku, teprve pak pokračuje
    minimaxem.

# Ohodnocení pozice
Ohodnocení jednotlivé souvislé skupiny symbolů se řídí následující tabulkou:

| Velikost skupiny | Neblokovaná | Zablokovaná na jedné straně | Zablokovaná na obou stranách |
|------------------|-------------|-----------------------------|------------------------------|
| 1                | 2           | 1                           | 0                            |
| 2                | 5           | 3                           | 0                            |
| 3                | 15          | 7                           | 0                            |
| 4                | 5000        | 20                          | 0                            |
| 5                | 99999       | 99999                       | 99999                        |

Pro každý směr zvlášť jsou nalezeny souvislé skupiny. Celkové ohodnocení pozice je pak
dáno jako
<img src="https://render.githubusercontent.com/render/math?math=R := \sum_{p \in G_x} r(p) - \sum_{q \in G_o} r(q)">,
kde <img src="https://render.githubusercontent.com/render/math?math=G_x"> je množina všech souvislých skupin křížků,
<img src="https://render.githubusercontent.com/render/math?math=G_o"> množina
všech souvislých skupin koleček a <img src="https://render.githubusercontent.com/render/math?math=r(x)">
ohodnocení skupiny <img src="https://render.githubusercontent.com/render/math?math=x">.

Pro úsporu času se údaje o jednotlivých skupinách i hodnocení udržuje průběžně,
po každém tahu pouze opraví vlastnosti skupin sousedících se zahraným polem.
Pro spojování existujících skupin je použita variace na **Disjoint Find-Union**.

Aby nebylo při minimaxu nutné kopírovat celou reprezentaci aktuální pozice,
je implementováno vracení tahů (včetně udržování skupin). Při každé prováděné operaci
na skupinách je na zásobník uložena informace o tom, jaká operace byla provedena.
Při vracení tahu jsou pak podle těchto informací do původního stavu vráceny i skupiny.
