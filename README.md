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
Options Used: -m -r --hs 

x 10 zombie variants (860)
x 10 timid animal variants (40)
x 30 hostile animal variants (360)
 - with freak meshes
 - with 25% possible stag has hostile AI
   ... 3 raging stags
 - with Headshot mode
    - headshot power 150%
    - zombie meat 3.0x
    - zombie speed 25%

--------------------------------------------------
BIGGEST:
   animalBear                     -  3559 hp
   animalBoar                     -   539 hp
   animalBossGrace                -  4492 hp
   animalChicken                  -    50 hp
   animalCoyote                   -   225 hp
   animalDireWolf                 -  1646 hp
   animalDoe                      -   258 hp
   animalRabbit                   -    17 hp
   animalSnake                    -    19 hp
   animalStag                     -   472 hp
   animalWolf                     -   412 hp
   animalZombieBear               -  3811 hp
   animalZombieDog                -   430 hp
   animalZombieVulture            -    64 hp
   animalZombieVultureRadiated    -   242 hp
   zombieArlene                   -   152 hp
   zombieArleneFeral              -   298 hp
   zombieArleneRadiated           -   574 hp
   zombieBiker                    -   359 hp
   zombieBikerFeral               -   761 hp
   zombieBikerRadiated            -  1456 hp
   zombieBoe                      -   205 hp
   zombieBoeFeral                 -   396 hp
   zombieBoeRadiated              -   660 hp
   zombieBurnt                    -   154 hp
   zombieBurntFeral               -   342 hp
   zombieBurntRadiated            -   576 hp
   zombieBusinessMan              -   157 hp
   zombieBusinessManFeral         -   309 hp
   zombieBusinessManRadiated      -  1183 hp
   zombieDarlene                  -   201 hp
   zombieDarleneFeral             -   354 hp
   zombieDarleneRadiated          -   659 hp
   zombieDemolition               -  1120 hp
   zombieFatCop                   -   349 hp
   zombieFatCopFeral              -   661 hp
   zombieFatCopRadiated           -  1346 hp
   zombieFatHawaiian              -   401 hp
   zombieFatHawaiianFeral         -   766 hp
   zombieFatHawaiianRadiated      -  1456 hp
   zombieFemaleFat                -   413 hp
   zombieFemaleFatFeral           -   737 hp
   zombieFemaleFatRadiated        -  1409 hp
   zombieJanitor                  -   169 hp
   zombieJanitorFeral             -   377 hp
   zombieJanitorRadiated          -   673 hp
   zombieJoe                      -   171 hp
   zombieJoeFeral                 -   288 hp
   zombieJoeRadiated              -   644 hp
   zombieLab                      -   179 hp
   zombieLabFeral                 -   412 hp
   zombieLabRadiated              -   708 hp
   zombieLumberjack               -   424 hp
   zombieLumberjackFeral          -   783 hp
   zombieLumberjackRadiated       -  1274 hp
   zombieMarlene                  -   159 hp
   zombieMarleneFeral             -   286 hp
   zombieMarleneRadiated          -   490 hp
   zombieMoe                      -   201 hp
   zombieMoeFeral                 -   350 hp
   zombieMoeRadiated              -   698 hp
   zombieMutated                  -   188 hp
   zombieMutatedFeral             -   389 hp
   zombieMutatedRadiated          -   745 hp
   zombieNurse                    -   154 hp
   zombieNurseFeral               -   312 hp
   zombieNurseRadiated            -   495 hp
   zombiePartyGirl                -   172 hp
   zombiePartyGirlFeral           -   334 hp
   zombiePartyGirlRadiated        -   631 hp
   zombieScreamer                 -    89 hp
   zombieScreamerFeral            -   204 hp
   zombieScreamerRadiated         -   317 hp
   zombieSkateboarder             -   300 hp
   zombieSkateboarderFeral        -   542 hp
   zombieSkateboarderRadiated     -  1076 hp
   zombieSoldier                  -   200 hp
   zombieSoldierFeral             -   389 hp
   zombieSoldierRadiated          -   707 hp
   zombieSpider                   -   163 hp
   zombieSpiderFeral              -   335 hp
   zombieSpiderRadiated           -   494 hp
   zombieSteve                    -   180 hp
   zombieSteveCrawler             -   103 hp
   zombieSteveCrawlerFeral        -   179 hp
   zombieSteveFeral               -   318 hp
   zombieSteveRadiated            -   575 hp
   zombieTomClark                 -   173 hp
   zombieTomClarkFeral            -   272 hp
   zombieTomClarkRadiated         -   613 hp
   zombieUtilityWorker            -   206 hp
   zombieUtilityWorkerFeral       -   373 hp
   zombieUtilityWorkerRadiated    -  1259 hp
   zombieWightFeral               -   545 hp
   zombieWightRadiated            -   953 hp
   zombieYo                       -   213 hp
   zombieYoFeral                  -   380 hp
   zombieYoRadiated               -   630 hp
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

This configuration is currently defined for a Mac user (sorry, it's what I have).  I would like to have the system be a bit smarter and go to the right place based on your system, but that awaits me getting some install path information.  For now, if running on windows, you will need to change this path to point to the proper location that contains your "/Data/Config" folders.

> _**NOTE:** This is still a work in progress, in terms of making it generally available -- I would like to have this seamless, but that will require some outside data for me._
> 
### 3.1. General Options

#### 3.1.1. --config {path}
Used to specify the location of an alternate configuration file.  If not specified, uses the `config.json` file located in the current folder.

#### 3.1.2. --debug
Enables debug tracing.  This is very noisy any mainly useful for debugging execution issues by the developer.

#### 3.1.3. --dryrun
primarily used for testing, exceutes the program to check for any execution errors, but does not write out any mod files.

#### 3.1.5. --version
This option allows you to add 7d2d version information to the name of your generated mod directory name.  using `--version a20.2` would add the string `-a20.2` to the name of the mod folder. 

### 3.2. Numbers Options
The following options determine the number of variants to be generated for each class of entity.

#### 3.2.1. -z
Indicates how many zombie variants are to be generated.  If not specified, the default is "10" (10 times the number of base zombie definitions).

> _**NOTE:** The default of x10 will create 860 (as of a20.2) variants; higher values may result in very long load times._

#### 3.2.2. -f
Indicates how many friendly animal (chicken, rabbit, etc) variants are to be generated.  If not specified, the default is "10".

#### 3.2.3. -e
Indicates how many hostile animal (snake, wolf, etc) variants are to be generated.  If not specified, the default is "30".

### 3.3. Meshes Options
This option allows for some alternate zombie forms as seen in mods created by Robeloto.  It alters the various meshes with texture files, producing various "freaks" of nature.

#### 3.3.1. -m
This option enables the creation of zombies and hostile animal variants with a chance of having their texture changed to something other than the normal mesh.  This can produce some very odd entities with a "fire elemental", "mummy" or "glass" look to them. 

#### 3.3.2. -ma
If specified this enables the -m option and also assures that any variant will have a mesh applied to their textures (instead of the 50% used for `-m`).

### 3.4. Sizing Options
By default this variant tries to alter the entity size by some degree so as to produce a better variety.  For zombies this is done by altering their scale to one of  85%, 90%, 95%, 100%, 105%, 110%, and 115%.  Animals have additional possibilities of 50%, 75%, 125%, and 150%, with timid animals having an additional chance of 200%, and 250%.  This can produce seemingly "baby animals", along with huge wolves and "riding chickens".

Sizing will alter the hit capacity by a power of 1.66 if greater than 100% and a power of 0.6 if lesser.  In addition, mass (which can affect knockback from hits or explosions) is based on the "mass-cubed" rule, so something with double the size will have eight times the mass (and likewise, at half the size will have one-eighth the mass).

Sizing will modify damage -- something that is 150% size will do 150% damage!

Sizing  also affects harvesting to a limited degree.  Scale is used at a 0.85 power, so something that is 200% will return about 180% in harvestables, while something at 50% size will produce aboutt 60% harvestables.

#### 3.4.1. -g
This enables "Land of the Giants" mode (see `https://www.youtube.com/watch?v=nHQ_r8ZwPOw`).  This can be quite freaky.  While I would have liked to actually have entities 10x the size of normal players, unfortunatly at such size they seem to be unable to hit you.  With some playing around I found that applying sizings of 150%, 175%, 200%, 225%, and 250% worked ok (POI zombies will tend to get stuck in buildings, but in the wilds will be ok).  Timid and hostile animals have 275% and 300% options.

This option is incompatible with `-k` or `-ns`

#### 3.4.2. -k
This enables "Munchkin" mode.  Zombies are give a scaling range of 45%, 50%, 55%, 60%, 65%, or 70%, while animals get a range of 50%, 80%, 90%, 100%, 110%, and 120%.  This can be quite tricky if you encounter a horde in tall grass, and the hit box is tougher.

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
This option allows you to modify the overall toughness of the the entity, making it more critical that you deliver head shots.  If not specified, the default value is 3.0 (3x base hits).

##### 3.5.1.3. --hs-speed {value}
This option allows you modify the movement speed for zombies in this mode.  This is on top of any speed variations applied by the program itself. If not specified, the default value is 25 (25% speed).

### 3.6. Altered AI Options
In order to mix things up a bit, this option can be used to tweak the AI of some hostile animals and zombies.  What it does is to have a 33% chance of choosing a different AI and swapping it out.  Thus you could have pigs that act like mountain lions, or fat cops that act like coyotes.

#### 3.6.1. -a
This option enables the generation of altered AI.

##### 3.6.1.1. --ap {value}
This option allows you to override the chance of altered AI on variants, with a valid range of 1 to 100.

### 3.7. Raging Stags
Are they rabid?  This option makes 25% of the stag variants aggressive, giving them an AI from the list used by the altered AI option.

#### 3.7.1. -r
This option enables the generation of raging stags.

##### 3.7.1.1. --rp {value}
This option allows you to override the chance of raging stags, with a valid range of 1 to 100.
