# trubs-variants
This is a "7 Days to Die" mod based off Doughphunghus's original `7D2D-EntityRandomizer` mod.  We enjoyed his mod in the 18.x timeframe, but desired some additional functionality, and as such I took on the task of converting it from perl (which I have older proficiency in) to python (which I currently use for my job and greatly prefer) so that it would be easier to add our desired tweaks.

> _**NOTE:** The core concept is 100% his idea -- I simply translated his 
> code to python and then started alterations from there.  If anyone wants to send flowers and chocolates, he is the one you should be mailing them too.  However, at the time it seemed like he was not interested in continuing with it past 19.x, and I have since added many features beyond his original, so there is some original content here as well.  Doughphunghus is fully welcome to plunder what I have done and cross-pollinate my changes back into his original mod._

## 1. Description
This code is not a mod as much as it is a mod generator.  When the python script is executed with the desired options, the program rummages through the current `entityclasses.xml` and `entitygroups.xml` files to determine base entities to vary, then creates corresponding mod files to extend them.

## 2. How it works
This program is written to require Python 3.x, and can be invoked within your terminal shell or console using any desired options.  Invoked alone, without options, a mod is generated with only the basic varient settings.  When complete, simply move the generated folder to your 7D2D mods folder.

When created, several useful file are created for general reference (but have no effect on game execution)

### 2.1. settings.info
This file contains some information about what was generated and the options used (if any).
```text
Options Used: -m -a -r 

x 10 zombie variants (860)
x 10 timid animal variants (40)
x 30 hostile animal variants (360)
 - with 33% possible freaky mesh
   ... 411 freak entities
 - with 33% possible altered hostile AI
   ... 76 hostile animal behaviors changed
 - with 33% possible stag has hostile AI
   ... 4 raging stags

--------------------------------------------------
BIGGEST:
   animalBear                     -  3120 hp
   animalBoar                     -   469 hp
   animalBossGrace                -  4478 hp
   animalChicken                  -    47 hp
   animalCoyote                   -   225 hp
   animalDireWolf                 -  1609 hp
   animalDoe                      -   218 hp
   animalRabbit                   -    43 hp
   animalSnake                    -    21 hp
   animalStag                     -   504 hp
   animalWolf                     -   409 hp
   animalZombieBear               -  4170 hp
   animalZombieDog                -   448 hp
   animalZombieVulture            -    64 hp
   animalZombieVultureRadiated    -   213 hp
   zombieArlene                   -   169 hp
   zombieArleneFeral              -   342 hp
   zombieArleneRadiated           -   623 hp
   zombieBiker                    -   412 hp
   zombieBikerFeral               -   752 hp
   zombieBikerRadiated            -  1426 hp
   zombieBoe                      -   231 hp
   zombieBoeFeral                 -   432 hp
   zombieBoeRadiated              -   722 hp
   zombieBurnt                    -   188 hp
   zombieBurntFeral               -   328 hp
   zombieBurntRadiated            -   640 hp
   zombieBusinessMan              -   165 hp
   zombieBusinessManFeral         -   337 hp
   zombieBusinessManRadiated      -  1232 hp
   zombieDarlene                  -   220 hp
   zombieDarleneFeral             -   413 hp
   zombieDarleneRadiated          -   840 hp
   zombieDemolition               -  1344 hp
   zombieFatCop                   -   448 hp
   zombieFatCopFeral              -   736 hp
   zombieFatCopRadiated           -  1375 hp
   zombieFatHawaiian              -   429 hp
   zombieFatHawaiianFeral         -   615 hp
   zombieFatHawaiianRadiated      -  1525 hp
   zombieFemaleFat                -   461 hp
   zombieFemaleFatFeral           -   832 hp
   zombieFemaleFatRadiated        -  1636 hp
   zombieJanitor                  -   228 hp
   zombieJanitorFeral             -   431 hp
   zombieJanitorRadiated          -   816 hp
   zombieJoe                      -   191 hp
   zombieJoeFeral                 -   346 hp
   zombieJoeRadiated              -   604 hp
   zombieLab                      -   186 hp
   zombieLabFeral                 -   428 hp
   zombieLabRadiated              -   707 hp
   zombieLumberjack               -   417 hp
   zombieLumberjackFeral          -   780 hp
   zombieLumberjackRadiated       -  1302 hp
   zombieMarlene                  -   169 hp
   zombieMarleneFeral             -   332 hp
   zombieMarleneRadiated          -   632 hp
   zombieMoe                      -   218 hp
   zombieMoeFeral                 -   430 hp
   zombieMoeRadiated              -   734 hp
   zombieMutated                  -   212 hp
   zombieMutatedFeral             -   374 hp
   zombieMutatedRadiated          -   721 hp
   zombieNurse                    -   139 hp
   zombieNurseFeral               -   311 hp
   zombieNurseRadiated            -   668 hp
   zombiePartyGirl                -   182 hp
   zombiePartyGirlFeral           -   297 hp
   zombiePartyGirlRadiated        -   700 hp
   zombieScreamer                 -   103 hp
   zombieScreamerFeral            -   196 hp
   zombieScreamerRadiated         -   339 hp
   zombieSkateboarder             -   311 hp
   zombieSkateboarderFeral        -   656 hp
   zombieSkateboarderRadiated     -  1225 hp
   zombieSoldier                  -   203 hp
   zombieSoldierFeral             -   442 hp
   zombieSoldierRadiated          -   744 hp
   zombieSpider                   -   187 hp
   zombieSpiderFeral              -   352 hp
   zombieSpiderRadiated           -   578 hp
   zombieSteve                    -   181 hp
   zombieSteveCrawler             -    99 hp
   zombieSteveCrawlerFeral        -   232 hp
   zombieSteveFeral               -   298 hp
   zombieSteveRadiated            -   627 hp
   zombieTomClark                 -   158 hp
   zombieTomClarkFeral            -   368 hp
   zombieTomClarkRadiated         -   564 hp
   zombieUtilityWorker            -   177 hp
   zombieUtilityWorkerFeral       -   431 hp
   zombieUtilityWorkerRadiated    -  1229 hp
   zombieWightFeral               -   508 hp
   zombieWightRadiated            -  1240 hp
   zombieYo                       -   182 hp
   zombieYoFeral                  -   430 hp
   zombieYoRadiated               -   779 hp

--------------------------------------------------
OTHER DETAILS:
   Raging animalStag Bite meleeHandAnimalBear      - 1
   Raging animalStag Bite meleeHandAnimalDireWolf  - 1
   Raging animalStag Bite meleeHandAnimalZombieDog - 1
   Raging animalStag Bite meleeHandBossGrace       - 1
   animalBear (animalDireWolf AI)                  - 1
   animalBear (animalWolf AI)                      - 2
   animalBear (animalZombieBear AI)                - 2
   animalBear (animalZombieDog AI)                 - 2
   animalBear (zombieSpider AI)                    - 1
   animalBear (zombieTemplateMale AI)              - 1
   animalBoar (animalBear AI)                      - 2
   animalBoar (animalBossGrace AI)                 - 1
   animalBoar (animalDireWolf AI)                  - 2
   animalBoar (animalMountainLion AI)              - 2
   animalBoar (animalSnake AI)                     - 2
   animalBoar (animalZombieBear AI)                - 2
   animalBoar (zombieFatCop AI)                    - 1
   animalBoar (zombieSpider AI)                    - 1
   animalBoar (zombieTemplateMale AI)              - 1
   animalBossGrace (animalDireWolf AI)             - 2
   animalBossGrace (animalSnake AI)                - 1
   animalBossGrace (animalWolf AI)                 - 1
   animalBossGrace (animalZombieBear AI)           - 1
   animalBossGrace (zombieSpider AI)               - 1
   animalCoyote (animalBear AI)                    - 1
   animalCoyote (animalBossGrace AI)               - 1
   animalCoyote (animalDireWolf AI)                - 1
   animalCoyote (animalSnake AI)                   - 1
   animalCoyote (animalZombieBear AI)              - 2
   animalCoyote (animalZombieDog AI)               - 2
   animalCoyote (zombieSpider AI)                  - 1
   animalCoyote (zombieTemplateMale AI)            - 1
   animalDireWolf (animalBossGrace AI)             - 1
   animalDireWolf (animalSnake AI)                 - 2
   animalDireWolf (animalWolf AI)                  - 1
   animalDireWolf (animalZombieBear AI)            - 3
   animalDireWolf (zombieFatCop AI)                - 3
   animalDireWolf (zombieTemplateMale AI)          - 2
   animalMountainLion (animalBear AI)              - 1
   animalMountainLion (animalBossGrace AI)         - 2
   animalMountainLion (animalWolf AI)              - 1
   animalMountainLion (animalZombieDog AI)         - 1
   animalMountainLion (zombieFatCop AI)            - 1
   animalMountainLion (zombieTemplateMale AI)      - 1
   animalSnake (animalBear AI)                     - 2
   animalSnake (animalBossGrace AI)                - 1
   animalSnake (animalDireWolf AI)                 - 3
   animalSnake (animalMountainLion AI)             - 2
   animalSnake (zombieTemplateMale AI)             - 1
   animalStag (animalBossGrace AI)                 - 1
   animalStag (animalDireWolf AI)                  - 1
   animalStag (animalWolf AI)                      - 1
   animalStag (animalZombieBear AI)                - 1
   animalWolf (animalBossGrace AI)                 - 2
   animalWolf (animalDireWolf AI)                  - 1
   animalWolf (animalMountainLion AI)              - 1
   animalWolf (animalZombieBear AI)                - 2
   animalWolf (zombieFatCop AI)                    - 1
   animalWolf (zombieSpider AI)                    - 2
```

### 2.2. entities.info 
This file contains the base entities used to generate the variants:
```text
===== Zombies =====
zombieArlene
zombieArleneFeral
zombieArleneRadiated
zombieBiker
zombieBikerFeral
zombieBikerRadiated
zombieBoe
zombieBoeFeral
zombieBoeRadiated
zombieBurnt
zombieBurntFeral
zombieBurntRadiated
zombieBusinessMan
zombieBusinessManFeral
zombieBusinessManRadiated
zombieDarlene
zombieDarleneFeral
zombieDarleneRadiated
zombieDemolition
zombieFatCop
zombieFatCopFeral
zombieFatCopRadiated
zombieFatHawaiian
zombieFatHawaiianFeral
zombieFatHawaiianRadiated
zombieFemaleFat
zombieFemaleFatFeral
zombieFemaleFatRadiated
zombieJanitor
zombieJanitorFeral
zombieJanitorRadiated
zombieJoe
zombieJoeFeral
zombieJoeRadiated
zombieLab
zombieLabFeral
zombieLabRadiated
zombieLumberjack
zombieLumberjackFeral
zombieLumberjackRadiated
zombieMaleHazmat
zombieMaleHazmatFeral
zombieMaleHazmatRadiated
zombieMarlene
zombieMarleneFeral
zombieMarleneRadiated
zombieMoe
zombieMoeFeral
zombieMoeRadiated
zombieMutated
zombieMutatedFeral
zombieMutatedRadiated
zombieNurse
zombieNurseFeral
zombieNurseRadiated
zombiePartyGirl
zombiePartyGirlFeral
zombiePartyGirlRadiated
zombieScreamer
zombieScreamerFeral
zombieScreamerRadiated
zombieSkateboarder
zombieSkateboarderFeral
zombieSkateboarderRadiated
zombieSoldier
zombieSoldierFeral
zombieSoldierRadiated
zombieSpider
zombieSpiderFeral
zombieSpiderRadiated
zombieSteve
zombieSteveCrawler
zombieSteveCrawlerFeral
zombieSteveFeral
zombieSteveRadiated
zombieTomClark
zombieTomClarkFeral
zombieTomClarkRadiated
zombieUtilityWorker
zombieUtilityWorkerFeral
zombieUtilityWorkerRadiated
zombieWightFeral
zombieWightRadiated
zombieYo
zombieYoFeral
zombieYoRadiated

===== Hostile Animals =====
animalBear
animalBoar
animalBossGrace
animalCoyote
animalDireWolf
animalMountainLion
animalSnake
animalWolf
animalZombieBear
animalZombieDog
animalZombieVulture
animalZombieVultureRadiated

===== Timid Animals =====
animalChicken
animalDoe
animalRabbit
animalStag
```

## 3. Execution
On your system go to the mod repository folder and invoke this program with `python ./randomizer.py` (along with any desired options).  The generated mod folder will be placed in the current repository folder and is usable by simply moving it to your 7D2D mods folder.  It is not expected that game restarts are needed, and the generated mod should be server-side only.

The program relies (at present) on the use of a configuration file in JSON format (as per Dough's original design).  While the existing file can be used without alteration, on configuration will likely be have to be changed:

```text
  "game_install_dir":"/Users/<username>/Library/Application Support/Steam/steamapps/common/7 Days To Die/7DaysToDie.app",
```

This configuration is currently defined for a Mac user (sorry, it's what I use). It will automatically replace `<username>` with your actual username when the file is read in.  For windows users, you probably want to replace that configuration with something like:
```text
  "game_install_dir":"C:\Program Files (x86)\Steam\steamapps\common\7 Days To Die\Data\Config",
```

### 3.1. General Options

#### 3.1.1. --config {path}
Used to specify the location of an alternate configuration file.  If not specified, uses the `config.json` file located in the current folder.

#### 3.1.2. --debug
Enables debug tracing.  This is very noisy any mainly useful for debugging execution issues by the developer.

#### 3.1.3. --dryrun
primarily used for testing, exceutes the program to check for any execution errors, but does not write out any mod files.

#### 3.1.5. --version
This option allows you to add 7d2d version information to the name of your generated mod directory name.  using `--version a20.2` would add the string `-a20.2` to the name of the mod folder. 

### 3.2. Quantity Options
The following options determine the number of variants to be generated for each class of entity.

#### 3.2.1. -z
Indicates how many zombie variants are to be generated.  If not specified, the default is "10" (10 times the number of base zombie definitions).

> _**NOTE:** The default of x10 will create 860 (as of a20.2) variants; higher numbers of variants may result in long load times._

#### 3.2.2. -f
Indicates how many friendly animal (chicken, rabbit, etc) variants are to be generated.  If not specified, the default is "10".

#### 3.2.3. -e
Indicates how many hostile animal (snake, wolf, etc) variants are to be generated.  If not specified, the default is "30".

### 3.3. Meshes Options
This option allows for some alternate zombie forms as seen in mods created by Robeloto.  It alters the various meshes with texture files, producing various "freaks" of nature.

#### 3.3.1. -m
This option enables the creation of zombies and hostile animal variants with a chance of having their texture changed to something other than the normal mesh.  This can produce some very odd entities with an "iron", "mummy" or "mucky" look to them, though for some zombie types only hair may be affected. 

#### 3.3.2. -mp
If specified this allows you to specify the percent chance of freak material for an entity, from 1 to 100.  If not specified, the default is 33 (33% chance)

### 3.4. Sizing Options
By default this variant tries to alter the entity size by some degree so as to produce a variety of sizes.  A value is chosen as  75, 100 or 125 for zombies;  all animals have additional possibilities of 50 and 150, with timid animals having chances of 175, 200, 225 and 250. This chosen value is then varied by +/- 10% to create the final `trub_scale` (considered a percent, so 150 equals 150%, or x1.5). 

This value (seen as an attribute for generated entities) has the following effects:

1) `SizeScale` for the new variant equals the original value multiplied by the `trub_scale`, capped at a lower limit of 0.25 and an upper limit of 2.0.  This will produce the effects of  "baby animals", along with taller/shorter zombies and "riding chickens". 

2) `HealthMax` is modified on a slight power curve based on the assumption that a greater/larger cross-section implies a slightly greater/lesser damage capacity.  The original `HealthMax` is multiplied by `trub_scale` raised to a power of 1.33 to produce the new value (thus, at 200 `trub_scale`, the actual multiplier is about x2.5; at 50 the actual multiplier is about x0.4)
   * Raging Stags (see later option) have an additional x2.0 multiplier to account for their smaller base hit points, to make them a little more dangerous.

   The actual ration of new `HealthMax` to the original value is used as a multiplier to the `ExperienceGain` value

3) `Mass` is based on a more reduced "mass-squared" rule, so something with a `trub_scale` of 200 will have a `Mass` multiplier of x4.0 (and likewise, a 50 will have a `Mass` multiplier of x0.25).  This further tweaked by a random +/- 10% for some variance.  Smaller animals will tend to be knocked farther on a strong hit, but larger animals won't move as much.  `Mass` is capped at a lower limit of 2 and an upper limit of 20000.

4) `EntityDamage` and `BlockDamage` will be altered by a root power curve since being bigger does not produce linearly stronger hits.(and to prevent large entities from completely on-shotting players).  The original damage values are multiplied by the `trub_scale` raised to the 0.75 power (a 200 scale entity will do about x1.7 damage, a 50 scale one will do about x0.6).  This is further varied by +/- 10% for each danmage type and calculated to determine a `perc_add` for each damage type.

5) Havestables defined with `Harvest` are affected by a root power curve as well. The `trub_scale` raised to the 0.85 power multiplies the original harvestable value, +/- 10%.
   * Entities with a freak mesh will have HALF the figured harvestables

#### 3.4.1. -g
This enables "Land of the Giants" mode (see `https://www.youtube.com/watch?v=nHQ_r8ZwPOw`).  While I would have liked to actually have entities 10x the size of normal players, unfortunatly at such size they seem to be unable to hit you.  

This mode creates `trub_scale` sizes of 150, 175, 200, 225, and 250 for zombies, with 275 and 300 allowed for animals. POI zombies will tend to get stuck in buildings, but wandering zombies shound be ok.

This option is incompatible with `-k` or `-ns`

#### 3.4.2. -k
This enables "Munchkin" mode.  Zombies are give a `trub_scale`  25, 50, or 75,  while animals get a choice of 25, 50, 75 or 100.  In both cases a +/- 10% variance is also added.  This can be quite tricky if you encounter a horde in tall grass, and the hit box is tougher.

This option is incompatible with `-g` or `-ns`

#### 3.4.3. --ns
This option turns off size variance entirely, allowing for entity variants without any size changes.

This option is incompatible with `-g` or `-k`

### 3.5. Headshot Mode Options
For those wishing a more "classic" zombie mode, this option makes it so that head shots are especially effective, but adds more hit capacity to the zombies overall.  This makes them into bullet sponges unless you can tag the head.  This will also affect any  animals as well. To compensate for the target box difficulty, overall speed is decreased. 

> _**NOTE:** it is unfortunate that this also affects animals; I would have liked to only affect zombies.  If anyone has a clue on how to modify the created `items.xml` file to accomplish this, it would be most appreciated._

#### 3.5.1. --hs
This option enables the mode.

##### 3.5.1.1. --hs-power {value}
This option allows you to modify the amount of damage a head shot does as compared to hits to other areas.  If not specified, the default value is 150 (150x weapon damage).

##### 3.5.1.2. --hs-meat  {value}
This option allows you to modify the overall toughness of the the entity, making it more critical that you deliver head shots.  If not specified, the default value is 5.0 (5x `HealthMax`).

##### 3.5.1.3. --hs-speed {value}
This option allows you modify the movement speed for zombies in this mode.  This is on top of any speed variations applied by the program itself. If not specified, the default value is 25 (25% speed).

### 3.6. Altered AI Options
In order to mix things up a bit, this option can be used to tweak the AI of hostile animals.  What it does is to have a chance of choosing a different AI set, replacing the original for the enitity.  Thus you could have pigs that act like mountain lions or coyotes that act like zombies.

#### 3.6.1. -a
This option enables the generation of altered AI.

##### 3.6.1.1. --ap {value}
This option allows you to override the chance of altered AI on variants, with a valid range of 1 to 100.  If not specified, the default vale is 33.

### 3.7. Raging Stags
Are they rabid?  This option makes some of the stag variants aggressive, giving them an AI from the list used by the altered AI option.

#### 3.7.1. -r
This option enables the generation of raging stags.

##### 3.7.1.1. --rp {value}
This option allows you to override the chance of raging stags, with a valid range of 1 to 100.  If not specified, the default vale is 33.

#### 3.8 Research mode
Used primarily to check new freaky mesh materials.  It has the effect of increasing the `trub_scale` to 500, reducing `MoveSpeed` to 0.01 and altering `MoveType` to 2. 

#### 3.8.1. --research
This option enables research mode.

