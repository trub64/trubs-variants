#  coding: utf-8
#  Trub's Variants -- a 7D2D Module generator originally conceived by
#     Doughphunghus (https://github.com/doughphunghus)
################################################################################

import argparse
import copy
import json
import logging
import os
import pwd
import random
import sys
# noinspection PyPep8Naming,StandardLibraryXml
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Tuple

# noinspection PyUnusedName
__author__ = "trub64"  # as derived from Doughphunghus's original perl code

logger = logging.getLogger(__name__)

################################################################################
# Begin Globals
################################################################################

NEW_ENTITY_FILTER_OUT_LIST = {  # don't ever clone these nodes. Hardcode obvious here
    'playerMale': "Don't clone players",
    'playerFemale': "Don't clone players",
    'zombieTemplateMale': "Do not clone this as its a template entity",
    'animalTemplateTimid': "Do not clone this as its a template entity",
    'animalTemplateHostile': "Do not clone this as its a template entity"
}
POPULATE_ENTITY_TYPE_LOOKUP_MAX_LOOPS = 2  # Increase number if entity classes nest deeply


################################################################################
# Begin Main Class
################################################################################


class RandEnt(object):
    """
    This class is used for all generation operations.
    """
    CONFIGS = {}

    FILTER_ALLOW_ONLY_LIST_FLAG = False
    NEW_ENTITY_FILTER_ALLOW_ONLY_LIST = {}

    ENTITYCLASSES_DOM: ET.Element = None  # inventory of entity classes
    ENTITYGROUPS_DOM: ET.Element = None  # inventory of entity groups

    ENTITY_TYPE_LOOKUP = {}
    TYPE_ENTITY_LOOKUP = {}

    TOTAL_ZED_ENTITIES_FOUND = 0
    TOTAL_HOSTILE_ANIMAL_ENTITIES_FOUND = 0
    TOTAL_FRIENDLY_ANIMAL_ENTITIES_FOUND = 0

    TOTAL_ZED_ENTITIES_GENERATED = 0
    TOTAL_HOSTILE_ANIMAL_ENTITIES_GENERATED = 0
    TOTAL_FRIENDLY_ANIMAL_ENTITIES_GENERATED = 0

    ENTITY_GROUP_LOOKUP = {}
    NEW_ENTITIES = {}  # name => xml_node

    WalkTypeCrawlLimiter = {}  # key = zed class. val = int of crawler randomizations done

    def __init__(self, args: argparse.Namespace):
        """
        Initialize the generator Class.
        """
        self.repository = os.path.dirname(os.path.abspath(__file__))

        self.config_path = os.path.abspath(os.path.join(self.repository, args.config))
        if not os.path.exists(self.config_path):
            raise RuntimeError(f"No such config file: {self.config_path}")
        logger.debug(f"Using base configuration file '{self.config_path}")

        # load in JSON configs
        with open(self.config_path, 'r') as fp:
            self.CONFIGS = json.load(fp)

        # process command line options
        self.cmd = ""
        if args.zcount > 0:
            self.zcount = args.zcount
            self.cmd += f"-z {self.zcount} "
        else:
            self.zcount = 10
        if args.fcount > 0:
            self.fcount = args.fcount
            self.cmd += f"-f {self.fcount} "
        else:
            self.fcount = 10
        if args.ecount > 0:
            self.ecount = args.ecount
            self.cmd += f"-e {self.ecount}"
        else:
            self.ecount = 30

        self.meshes = args.meshes
        if self.meshes:
            self.cmd += "-m "
        self.mesh_always = args.mesh_always
        if self.mesh_always:
            self.meshes = True  # automatically turn it on
            self.cmd += "--ma "

        self.altered_ai = args.altered_ai
        if self.altered_ai:
            self.cmd += "-a "
        self.altered_ai_percent = float(args.altered_ai_percent) / 100.0
        self.cmd += f"--ap {args.altered_ai_percent}"

        self.raging_stag = args.raging_stag
        if self.raging_stag:
            self.cmd += "-r "
        self.raging_stag_percent = float(args.raging_stag_percent) / 100.0
        self.cmd += f"--rp {args.raging_stag_percent}"

        self.giants = args.giants
        if self.giants:
            self.cmd += "-g "

        self.munchkins = args.munchkins
        if self.munchkins:
            self.cmd += "-k "

        self.headshot = args.headshot
        self.hspower = args.hspower if args.hspower > 0 else 150
        self.hsmeat = args.hsmeat if args.hsmeat > 0 else 3.0
        self.hsspeed = args.hsspeed if args.hsspeed > 0 else 25
        if self.headshot:
            self.cmd += "--hs "
            if args.hspower > 0:
                self.cmd += f"--hs-power={args.hspower} "
            if args.hsmeat > 0:
                self.cmd += f"--hs-meat={args.hsmeat} "
            if args.hsspeed > 0:
                self.cmd += f"--hs-speed={args.hsspeed} "

        self.no_scale = args.noscale
        if self.no_scale:
            self.cmd += "--ns "

        self.game_version = args.version

        self.rand = random.Random()

        # numberings for variants
        self.entity_name_count = {}

        self.zed_library = {}
        self.hostile_animal_library = {}
        self.timid_animal_library = {}

        self.entities_xml_file = ""
        self.entitygroups_xml_file = ""

        self.biggest = {}
        self.raging_stag_count = 0
        self.altered_ai_count = 0

        self.prefix = ""

    # --- Validation ------------------------------------------------------------

    def check_config(self, label: str) -> None:
        """
        Ensure that configuration parameter exists.
        
        :param label: configuration parameter
        """
        check = self.CONFIGS
        for item in label.split("."):
            if item not in check:
                raise RuntimeError(f"Exiting because required argument `{label}` not found")
            check = check[item]

    @staticmethod
    def check_dir(dir_name: str, label: str = None) -> None:
        """
        Ensure that required directory exists.
        
        :param dir_name: directory name
        :param label: configuration parameter involved
        """
        label = "this" if label is None else label
        if not os.path.exists(dir_name) or not os.path.isdir(dir_name):
            raise RuntimeError(f"Exiting because {label} does not exist and/or is not a directory: {dir_name}")

    @staticmethod
    def check_file(file_name: str, label: str = None) -> None:
        """
        Ensure that required file exists.
        
        :param file_name: file name
        :param label: configuration parameter involved
        """
        label = "this" if label is None else label
        if not os.path.exists(file_name) or os.path.isdir(file_name):
            raise RuntimeError(f"Exiting because {label} does not exist and/or is not a file: {file_name}")

    # ---------------------------------------------------------------------- #

    def initial_setup(self) -> None:
        """
        Perform preliminary setup and checking.        
        """
        # check game installation (origin may widely vary between windows and mac)
        install_dir: str = self.CONFIGS.get('game_install_dir', None)
        if install_dir is None:
            raise RuntimeError(f"No definition for 'game_install_dir' in the supplied config file!")
        install_dir = install_dir.replace("<username>", pwd.getpwuid(os.getuid())[0])

        self.check_dir(install_dir, 'game_install_dir')
        self.CONFIGS['game_config_dir'] = install_dir + "/Data/Config"
        self.check_dir(self.CONFIGS['game_config_dir'], 'game_config_dir')
        # self.CONFIGS['using_config_dir'] = self.CONFIGS['game_config_dir']

        # REMOVED: not using saved games
        # # OVERRIDE! Determine if we should use a saved game (with entities from other mods) for entity generation
        # if self.CONFIGS['use_save_game'] != "":  # can be blank, but if something in it, use it!
        #     self.check_config('game_saves_dir')  # can be blank
        #     logger.info(f"use_save_game set. Using save game for configs: {self.CONFIGS['use_save_game']}")
        #     self.check_dir(self.CONFIGS['game_saves_dir'], 'game_saves_dir')
        #     self.CONFIGS['saved_game_dir'] = self.CONFIGS['game_saves_dir'] + "/" + self.CONFIGS[
        #         'use_save_game'] + "/ConfigsDump"
        #     self.check_dir(self.CONFIGS['saved_game_dir'], 'saved_game_dir')
        #     self.CONFIGS['using_config_dir'] = self.CONFIGS['saved_game_dir']

        # Note: Here is where we pull the XML configs from!
        self.CONFIGS['entityclasses_file'] = self.CONFIGS['game_config_dir'] + '/entityclasses.xml'
        self.check_file(self.CONFIGS['entityclasses_file'], 'entityclasses_file')
        self.CONFIGS['entitygroups_file'] = self.CONFIGS['game_config_dir'] + '/entitygroups.xml'
        self.check_file(self.CONFIGS['entitygroups_file'], 'entitygroups_file')

        # Note: Localization file does not exist in a Saved Game! Use config dir ALWAYS!
        self.CONFIGS['localization_file'] = self.CONFIGS['game_config_dir'] + '/Localization.txt'
        self.check_file(self.CONFIGS['localization_file'], 'localization_file')

        # This is used to name the created modlet
        tag = "_freaks" if self.meshes else ""
        tag2a = "_giants" if self.giants else ""
        tag2b = "_munchkins" if self.munchkins else ""
        tag3 = "_HS" if self.headshot else ""
        tag4 = "_AI" if self.altered_ai else ""
        tag5 = "_RS" if self.raging_stag else ""
        gv = "" if self.game_version is None else f"-{self.game_version}"
        self.CONFIGS['modlet_name'] = (f"{self.CONFIGS['modlet_name_prefix']}{tag}{tag2a}{tag2b}{tag3}{tag4}{tag5}"
                                       f"{gv}")
        self.CONFIGS['modlet_gen_dir'] = self.repository + '/' + self.CONFIGS['modlet_name']

        # NOTE: Change from original, loops now controlled via command line
        self.CONFIGS['ConfigEntityZombie']['num_generation_loops'] = self.zcount
        self.CONFIGS['ConfigEntityFriendlyAnimal']['num_generation_loops'] = self.fcount
        self.CONFIGS['ConfigEntityEnemyAnimal']['num_generation_loops'] = self.ecount

        # Make sure we don't have so many crawlers
        self.check_config('ConfigEntityZombie.enable_walktype_crawler_limit')

        # modlet internal name override with --prefix
        self.check_config('unique_entity_prefix')
        self.prefix = self.CONFIGS['unique_entity_prefix']

        # Allow users to configure zeds to NEVER CLONE as modlets may do weird stuff if randomizing against a
        # saved games files
        self.check_config('ignore_entity_list')  # can be empty
        for user_config_ignore_entity, reason in self.CONFIGS['ignore_entity_list'].items():
            logger.info(f"Globally ignoring entity:{user_config_ignore_entity} because: {reason}")
            NEW_ENTITY_FILTER_OUT_LIST[user_config_ignore_entity] = reason

        # Allow users to configure zeds to ONLY CLONE, for very specific, custom randomization
        self.check_config('only_allow_these_entities_list')  # can be empty
        for user_config_only_allow_entity, reason in self.CONFIGS['only_allow_these_entities_list'].items():
            logger.info(f"Globally only allowing cloning of entity:{user_config_only_allow_entity} because: {reason}")
            self.FILTER_ALLOW_ONLY_LIST_FLAG = True  # Ease of knowing when to use these configs
            self.NEW_ENTITY_FILTER_ALLOW_ONLY_LIST[user_config_only_allow_entity] = reason

        # Get game defaults
        self.ENTITYCLASSES_DOM = ET.parse(self.CONFIGS['entityclasses_file']).getroot()
        self.ENTITYGROUPS_DOM = ET.parse(self.CONFIGS['entitygroups_file']).getroot()

    def populate_entity_type_lookup(self) -> bool:
        """
        Loop through Entities, and create the ENTITY_TYPE_LOOKUP table
        
        :return: True if there were lookup failures
        """
        logger.info("\n" + '#' * 79 + "\n" + "## Populating Entity -> Type Lookup table\n" + "#" * 79 + "\n")
        lookup_type_failures = False

        for entity in self.ENTITYCLASSES_DOM.findall('entity_class'):
            entity_name = entity.attrib['name']
            logger.debug(f"Found entity Name: {entity_name}")

            # First, see what type it is
            found_type = False

            # See if the entity is an extended type, and we know about the extended type
            # Note: this is more common? so check it first
            entity_extends_name = entity.attrib.get('extends', None)
            if entity_extends_name is not None:
                logger.debug(f"...{entity_name} EXTENDS: {entity_extends_name}")
                if entity_extends_name in self.ENTITY_TYPE_LOOKUP:
                    found_type = True
                    extends_type_name = self.ENTITY_TYPE_LOOKUP[entity_extends_name]
                    self.ENTITY_TYPE_LOOKUP[entity_name] = extends_type_name
                else:
                    logger.error(f"...Lookup for {entity_name} failed")

            if not found_type:  # See if the entity is a specific class (could be)
                for prop in entity.findall('property'):
                    if prop.attrib.get('name', None) == "Class":
                        value = prop.attrib.get('value', None)
                        found_type = True
                        logger.debug(f"...{entity_name} = Class:{value}")
                        self.ENTITY_TYPE_LOOKUP[entity_name] = value

            if not found_type:
                lookup_type_failures = True
                logger.error(f"...lookup_type_failure for entity: {entity_name}")

        return lookup_type_failures

    def populate_type_entity_lookup(self) -> None:
        """
        build the reverse lookup TYPE_ENTITY_LOOKUP.
        """
        logger.info('#' * 79 + "\n" + "## Populating Type -> Entity Lookup table\n" + "#" * 79 + "\n")

        # build the reverse lookup %TYPE_ENTITY_LOOKUP
        for entity_type_lookup_key, value in self.ENTITY_TYPE_LOOKUP.items():
            logger.debug(f"{entity_type_lookup_key} -> {value}")

            if value not in self.TYPE_ENTITY_LOOKUP:
                self.TYPE_ENTITY_LOOKUP[value] = []

            self.TYPE_ENTITY_LOOKUP[value].append(entity_type_lookup_key)

    def generate_lookup_tables(self) -> None:
        """
        Loop all entity types until we have populated ENTITY_TYPE_LOOKUP with all types
        """
        counter = 1
        while counter > 0:
            if not self.populate_entity_type_lookup():
                break

            if counter > POPULATE_ENTITY_TYPE_LOOKUP_MAX_LOOPS:
                raise RuntimeError(
                        'populate_entity_type_lookup loop_may_count reached. entityclasses nested to deep! Exiting.')

            counter += 1

        self.populate_type_entity_lookup()

        for key, value in self.TYPE_ENTITY_LOOKUP.items():
            logger.debug(f"{key} => {value}")

    # ----- Generation ------------------------------------------------------------

    def generate_new_entity_name(self, name: str) -> str:
        """
        Generate a new name for the variant.
        
        :param name: source name
        :returns: new name
        """
        if name not in self.entity_name_count:
            self.entity_name_count[name] = 0
        self.entity_name_count[name] += 1
        return f"{self.prefix}_{name}_{self.entity_name_count[name]:03d}"

    def generate_new_entity_from_existing_name(self, name: str) -> Tuple[Optional[str], Optional[ET.Element]]:
        """
        Finds, copies, and extends the zed asked for.
        
        :param name: The source entity
        :return: tuple of (new name, modified XML), or (None, None) if invalid
        """
        new_zed = None
        new_name = None

        # find first match
        for entity in self.ENTITYCLASSES_DOM.findall(f".//entity_class[@name='{name}']"):
            entity_name = entity.attrib['name']
            # logger.debug(f"Found: {entity_name}")

            # Filter some out we don't want!
            if entity_name in NEW_ENTITY_FILTER_OUT_LIST:
                logger.debug(f"Zed filter FILTER OUT list matched. Filtering OUT: {entity_name} because: "
                             f"{NEW_ENTITY_FILTER_OUT_LIST[entity_name]}")
                return None, None

            # Filter ONLY those we do want!
            if self.FILTER_ALLOW_ONLY_LIST_FLAG:
                if entity_name in self.NEW_ENTITY_FILTER_ALLOW_ONLY_LIST:
                    logger.debug(
                            f"Zed filter ALLOW ONLY list matched. Filtering IN: {entity_name} because: "
                            f"{self.NEW_ENTITY_FILTER_ALLOW_ONLY_LIST[entity_name]}")
                else:  # didnt match, dont clone.
                    logger.debug(f"Zed filter ALLOW ONLY list used and not matched. Filtering OUT: {entity_name}")
                    return None, None

            new_zed = copy.deepcopy(entity)  # deep clone, all nodes below
            new_name = self.generate_new_entity_name(name)
            new_zed.set('original_name', entity_name)
            new_zed.set('name', new_name)  # Not changing build.xml
            logger.debug(f"%% Generating {name} variant ({new_name}) ----------------------------------------")

            # Extend from parent
            entity_extends_name = new_zed.attrib.get('extends', None)
            if not entity_extends_name:  # Not already extending. Have to add!
                new_zed.set('extends', entity_name)

        return new_name, new_zed

    def is_randomizer_enabled_for_property(self, cfg_entity_key: str, cfg_property_key: str, entity_name: str) -> bool:
        """
        Check to see if property is allowed to randomize.
        
        :param cfg_entity_key: entity key
        :param cfg_property_key: property name
        :param entity_name: entity source name
        :return: True if allowed to vary
        """
        enabled = False  # Disable by default = blocked for all entities

        # ok, this val may not exist
        entity_name = 'UNDEFINED' if entity_name is None or entity_name == "" else entity_name

        # Deepest first. If cfg_property_key exists, then enable but look for specific disable
        # This keeps the config file smaller
        # Literal setting for specific entity
        if entity_name in self.CONFIGS[cfg_entity_key][cfg_property_key]:
            enabled = True
            if 'disable_randomizer' in self.CONFIGS[cfg_entity_key][cfg_property_key][entity_name]:
                enabled = False if int(
                        self.CONFIGS[cfg_entity_key][cfg_property_key][entity_name][
                            'disable_randomizer']) == 1 else True
            # print "is_randomizer_enabled_for_property: ".$enabled."\n"
            return enabled

        # Literal setting for all entities for specific property
        if cfg_property_key in self.CONFIGS[cfg_entity_key]:
            enabled = True
            if 'disable_randomizer' in self.CONFIGS[cfg_entity_key][cfg_property_key]:
                enabled = False if int(
                        self.CONFIGS[cfg_entity_key][cfg_property_key]['disable_randomizer']) == 1 else True
            return enabled

        return enabled

    def is_entity_blocked_for_property(self, cfg_entity_key: str, cfg_property_key: str, entity_name: str) -> bool:
        """
        Check to see if property is blocked from randomize.
        
        :param cfg_entity_key: entity key
        :param cfg_property_key: property name
        :param entity_name: entity source name
        :return: True if allowed to vary
        """
        result = False  # Disable by default = allow all entities

        # ok, this val may not exist
        entity_name = 'UNDEFINED' if entity_name is None or entity_name == "" else entity_name

        # BLocking ONLY allowed at deepest level
        if 'only_allow_these_entities_list exists' in self.CONFIGS[cfg_entity_key][cfg_property_key]:
            result = True  # We have a block list.
            if entity_name in self.CONFIGS[cfg_entity_key][cfg_property_key]['only_allow_these_entities_list']:
                result = False  # This one is allowed

        return result

    def get_entity_config_file_configs(self, cfg_entity_key: str, cfg_property_key: str, entity_name: str) -> Dict:
        """
        Get configurations for a given entity key.
        
        :param cfg_entity_key: entity key
        :param cfg_property_key: property name
        :param entity_name: entity source name
        :return: dict with config information
        """
        # Defaults are always good
        args = self.CONFIGS['ConfigDefaults'][cfg_property_key]

        # standard override: property overrides for a key
        # Ugh, for now; Harder, because there's no yes/no to this. was checking for specific known key
        if cfg_property_key in self.CONFIGS[cfg_entity_key]:
            keys = self.CONFIGS[cfg_entity_key][cfg_property_key].keys()
            if len(keys) > 1:
                # print "get_entity_config_file_configs ($keys) $cfg_entity_key -> $cfg_property_key\n"
                args = self.CONFIGS[cfg_entity_key][cfg_property_key]

        # Deepest nest: entity specific property overrides for a key
        if entity_name in self.CONFIGS[cfg_entity_key][cfg_property_key]:
            # print "get_entity_config_file_configs DEEPEST $cfg_entity_key -> $cfg_property_key -> $entity_name\n"
            args = self.CONFIGS[cfg_entity_key][cfg_property_key][entity_name]

        return args

    def randomize_walk_type(self, entity: ET.Element) -> ET.Element:
        """ 
        <property name="WalkType" value="3"/>
            1 = Moe, Fat Nana, Fat Hawaiian, Fat Cop
            2 = Boe, Lumberjack, Soldier, Wright, Mutated
            3 = Arlene, Darlene, Screamer
            4 = Crawler -> don't make crawlers walk. The legless one floats at you like a ghost :)
            5 = Marlene, Joe, Janitor, Yo
            6 = Steve, Utility
            7 = Default, Nurse, Businessman, Burnt, Lab, Biker, Hazmat
            8 = Spider (monkey! -- don't use)
            9 = Behemouth (possible men in the street? -- don't use)
        zombieSteveCrawlerFeral = WalkType not set, its inherited...sigh
        
        :param entity: source entity
        :return: updated entity
        """
        rand_walk_type = self.rand.choice([1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7])

        # Make sure we dont generate too many crawlers. looks weird.
        if rand_walk_type == 4:
            entity_name = entity.attrib['name']
            root_entity_class = self.NEW_ENTITIES[entity_name]['zed_is_from']

            if root_entity_class not in self.WalkTypeCrawlLimiter:
                self.WalkTypeCrawlLimiter[root_entity_class] = 0

            already_generated_walkers = self.WalkTypeCrawlLimiter[root_entity_class]
            crawler_limit = int(self.CONFIGS['ConfigEntityZombie']['enable_walktype_crawler_limit'])

            if already_generated_walkers >= crawler_limit:  # dont generate a walker
                rand_walk_type = self.rand.choice([1, 2, 3, 5, 6, 7])
                logger.info(f"...randomize_walk_type crawler check hit the limit of: {already_generated_walkers} "
                            f"for: {root_entity_class}! retry was: {rand_walk_type}")
            else:  # new walker ok
                already_generated_walkers += 1
                self.WalkTypeCrawlLimiter[root_entity_class] = already_generated_walkers

        original = None
        for walk_type in entity.findall(f".//property[@name='WalkType']"):
            original = walk_type.attrib['value']  # returned as string
            if original == '8':  # leave spiders alone
                return entity

            if str(rand_walk_type) != original:
                walk_type.set('value', str(rand_walk_type))  # random this
                logger.debug(f"   Changed WalkType from {original} to {rand_walk_type}")
                return entity

        if original is None:  # gotta make a new one
            prop = ET.Element("property")
            prop.set('name', "WalkType")  # random this
            prop.set('value', str(rand_walk_type))  # random this
            prop.tail = "\n    "
            entity.insert(1, prop)
            logger.debug(f" + Defined WalkType as {rand_walk_type}")

        return entity

    def random_rgb(self) -> str:
        """
        Generate random RGB value within a set of distinct tints.
        
        :return: RGB triplet as a string
        """
        colors = [
            [255, 0, 0], [255, 63, 0], [255, 127, 0], [255, 191, 0],  # red -> yellow
            [255, 255, 0], [191, 255, 0], [127, 255, 0], [63, 255, 0],  # yellow -> green
            [0, 255, 0], [0, 255, 63], [0, 255, 127], [0, 255, 191],  # green -> cyan
            [0, 255, 255], [0, 191, 255], [0, 127, 255], [0, 63, 255],  # cyan -> blue
            [0, 0, 255], [63, 0, 255], [127, 0, 255], [191, 0, 255],  # blue -> magenta
            [255, 0, 255], [255, 0, 191], [255, 0, 127], [255, 0, 63],  # magenta -> red
        ]
        pick = self.rand.choice(colors)
        r = pick[0]
        g = pick[1]
        b = pick[2]

        return f"{r},{g},{b}"

    def randomize_tint(self, zed: ET.Element) -> ET.Element:
        """
        OK. TintMaterial is an RGB property
        Can be TintMaterial1, TintMaterial2, TintMaterial3
            <property name="TintMaterial2" value="36,38,45"/>
        """
        # Try TintMaterial1, TintMaterial2, TintMaterial3
        for n in range(3):
            for node in zed.findall(f".//property[@name='TintMaterial{n + 1}']"):
                new_val = self.random_rgb()
                node.set('value', new_val)  # random this

        # Try TintColor
        for node in zed.findall(f".//property[@name='TintColor']"):
            new_val = self.random_rgb()
            node.set('value', new_val)  # random this

        return zed

    @staticmethod
    def determine_num_decimals(num: str) -> int:
        """ 
        Returns count of decimal places based on source string.
        
        :param num: source
        :return: decimal places count
        """
        dec_cnt = 0
        parts = num.split(".")
        if len(parts) > 1:
            dec_cnt = len(parts[1])

        return dec_cnt

    def random_number_from_range(self, low: str, high: str, rescale: str = None) -> str:
        """
        Takes a high and low *positive or negative* numbers (supplied as string from config)
        Returns a random number between them with x decimal places.
        Decimal places are determined by the highest decimal places passed in to either low or high.
        
        :param low: low value as string
        :param high: high value as string
        :param rescale: value scaling
        :return: random range, as string, with decimal places based on greater of low,high
        """
        if float(high) < float(low):
            raise RuntimeError(f"random_number_from_range: high: {high} < low: {low}")

        # Get how many decimals are passed
        low_dec_cnt = self.determine_num_decimals(low)
        high_dec_cnt = self.determine_num_decimals(high)

        num_decimals = max(low_dec_cnt, high_dec_cnt)
        rescale_float = 1.0 if rescale is None else float(rescale) / 100.0

        # Subtract low from high to get single float number e.g. 1.950 = 2.000 - 0.050
        use_low = float(low) * rescale_float
        use_high = float(high) * rescale_float
        diff = float(use_high) - float(use_low)

        rand = self.rand.random() * diff

        # Add rand to low for new value
        new_rand = use_low + rand

        # Force to x decimal places e.g. .346. 0 = no decimals
        if num_decimals == 0:
            new_rand = f"{int(new_rand):d}"
        else:
            new_rand = f"{new_rand:.{num_decimals}f}"
        return new_rand

    # noinspection PyUnusedFunction
    def conform_decimals(self, pattern: str, value: str) -> str:
        """
        Takes a pattern number with decimals and uses that to format the supplied value.
        
        :param pattern: decimal count pattern
        :param value: entity to be converted
        :return: result
        """
        # Get how many decimals are passed
        num_decimals = self.determine_num_decimals(pattern)

        new_rand = float(value)

        # Force to x decimal places e.g. .346. 0 = no decimals
        if num_decimals == 0:
            new_rand = f"{int(new_rand):d}"
        else:
            new_rand = f"{new_rand:.{num_decimals}f}"
        return new_rand

    def vary_percent_around_number(self, num: str, pct: str, num_decimals: int, mult: float = 1.0) -> str:
        """
        Take a given number and generate a variant around by +/- the specified percent.
        Given a pct of 25, we produce a random value up to TWICE that (0-50), subtract 25, divide by 100 and add 1,
        producing a multiplier from 0.75 to 1.25.

        This is then multiplied by the original number and optional scaling multiplier to produce the new number.
        
        :param num: source number as a string
        :param pct: variance percent maximum
        :param num_decimals: max decimal places
        :param mult: additional scaling multipler after variance (default 1.0)
        :return: formatted result string
        """
        rand_pct_float = 1.0 + (((self.rand.random() * float(pct) * 2.0) - float(pct)) / 100.0)

        new_num_float = float(num) * mult * rand_pct_float

        # ok, we finally have the rand +/- percent.  How to round?
        # Force to x decimal places e.g. .346. 0 = no decimals
        if num_decimals == 0:
            new_num = f"{int(new_num_float):d}"
        else:
            new_num = f"{new_num_float:.{num_decimals}f}"

        return new_num

    @staticmethod
    def scale_given_number(num: str, mult: str, num_decimals: int, cap: float = None) -> str:
        """
        Take a given number and scale it by the provided mutiplier.
        
        :param num: source number as string (int or float)
        :param mult: multiplier (integer value where 100 = 100%)
        :param num_decimals: max decimal places
        :param cap: If specified, maximum value
        :return: formatted result string
        """
        rand_pct_float = float(mult) / 100.0
        new_num_float = float(num) * rand_pct_float
        if cap is not None:
            new_num_float = min(new_num_float, cap)

        # Force to x decimal places e.g. .346. 0 = no decimals
        if num_decimals == 0:
            new_num_float = f"{int(new_num_float):d}"
        else:
            new_num_float = f"{new_num_float:.{num_decimals}f}"

        return new_num_float

    def vary_property_around_base_value(self, entity: ET.Element, property_name: str,
                                        cfg: Dict) -> ET.Element:
        """
        This looks for a property.  If found, then randomizes the value around that by +/- pct_random_int
        BUT if it cannot find a property, uses val_if_empty for the source
        and inserts a new property.  Likely just easier for now than trying to
        traverse up a class inheritance tree I don't control
        Can also just start averaging up the vals to get a  decent val_if_empty?
        
        :param entity: source entity
        :param property_name: property being varied
        :param cfg: variance data
        :return: modified element
        """
        pct_random = cfg['pct_random_int']  # amount of variance, where "100" = 100%
        default = cfg['default']  # default value, if property is not found

        original = None
        for node in entity.findall(f".//property[@name='{property_name}']"):
            original = node.attrib['value']
            new_val = self.vary_percent_around_number(original, pct_random, self.determine_num_decimals(original))
            if new_val != original:  # only change if different
                logger.debug(f"   Changed {property_name} from {original} to {new_val}")
                node.set('value', new_val)

        # ok, we did NOT find the attribute, gotta make a new one
        if original is None:
            prop = ET.Element("property")
            prop.set('name', property_name)
            new_val = self.vary_percent_around_number(default, pct_random, self.determine_num_decimals(default))
            prop.set('value', new_val)  # random this
            prop.tail = "\n    "
            entity.insert(1, prop)
            logger.debug(f" + Defined {property_name} as {new_val}")

        return entity

    def scale_property(self, entity: ET.Element, property_name: str, cfg: Dict) -> ET.Element:
        """
        This looks for a property.  If found, then multiplies the value by pct_random_int
        BUT if it cannot find a property, uses val_if_empty and inserts a new property. 
        
        :param entity: source entity
        :param property_name: property being scaled
        :param cfg: variance data
        :return: modified entity
        """
        multiplier = cfg['pct_random_int']  # where "100" = 100%
        default = cfg['default']

        # prevent zombie sizes over 2.0, otherwise they cannot hit you
        cap = 2.0 if self.giants and property_name == "SizeScale" else None

        original = None
        for node in entity.findall(f".//property[@name='{property_name}']"):
            original = node.attrib['value']
            new_val = self.scale_given_number(original, multiplier, self.determine_num_decimals(original), cap=cap)
            if new_val != original:
                node.set('value', new_val)
                logger.debug(f"   Changed {property_name} from {original} to {new_val}")

        # ok, we did NOT find the attribute
        if original is None:
            prop = ET.Element("property")
            prop.set('name', property_name)
            new_val = self.scale_given_number(default, multiplier, self.determine_num_decimals(default), cap=cap)
            prop.set('value', new_val)
            prop.tail = "\n    "
            entity.insert(1, prop)
            logger.debug(f" + Defined {property_name} as {new_val}")

        return entity

    def generate_scaling(self, entity: ET.Element, is_animal: bool, is_enemy: bool = True) -> ET.Element:
        """
        Randomly determine the overall scale varaince of the entity, depending on flags.
        Will add a parameter "trub_scale" which is ignored by 7D2D but used by this tool.

        If --ns is specified. no size variation is done.

        Updated: Variant scaling compressed to allow for POI zombies to actually get out.  Animal
                 scaling retained.

        :param entity: source entity
        :param is_animal: True if animal (not zombie)
        :param is_enemy: True if hostile
        :return: modified entity
        """
        if self.no_scale:
            entity.attrib['trub_scale'] = "100"
            return entity

        # otherwise, get a size variant
        if self.giants:  # will be capped at x2 size in any case
            sizes = ["150", "175", "200", "225", "250"]
            # animals get a bit wider variance since they are generally smaller
            if is_animal:
                sizes.append("275")
                sizes.append("300")
        elif self.munchkins:  # animals varied normal sized, zombies smaller
            if is_animal:
                sizes = ["50", "80", "90", "100", "110", "120"]
            else:
                sizes = ["45", "50", "55", "60", "65", "70"]
        else:
            sizes = ["85", "90", "95", "100", "105", "110", "115"]
            if is_animal:
                sizes += ["50", "75", "125", "150"]
                if not is_enemy:  # allow for larger timids
                    sizes = sizes + ["200", "250"]

        rand_change_pct = random.choice(sizes)
        entity.attrib['trub_scale'] = rand_change_pct
        return entity

    @staticmethod
    def get_trub_scale(entity: ET.Element) -> str:
        """
        Get the saved TrubScale, or 100 if not defined.

        :param entity: supplied entity
        :return: scale as a integer string ("100" = 100%)
        """
        return entity.attrib.get('trub_scale', "100")

    @staticmethod
    def is_raging(entity: ET.Element) -> bool:
        """
        Check for raging information on a stag.

        :param entity: supplied entity
        :return: true if raging
        """
        value = entity.attrib.get('trub_raging', "")
        return value != ""

    def vary_size_and_mass(self, entity: ET.Element, cfg: Dict) -> ET.Element:
        """
        Adjust the SizeScale and Mass of the entity.

        For Male Player:
          <property name="Mass" value="180"/>
          <property name="Weight" value="70"/>

        For Female Player (weight uses male values):
          <property name="Mass" value="130"/>

        For Zombie Template:
          <property name="Mass" value="170"/>
          <property name="Weight" value="70"/>
        Fat Cop has Mass 330

        Animal Timid has default mass 40, weight 70
        rabbits and chickens have weight 10

        Animal Hostile Template  has a default weight of 300 but no defined mass
            Bear has mass 600
                Zombie Bear extends bear
            Snake has mass 30, weight 70
            Boar has mass 200
            Wolf has mass 95
                Coyote has mass 50
                DireWolf has mass 180

        "Weight" has nothing to do with physical weight, but with distribution.

        :param entity: source entity
        :param cfg: variance data
        :return: modified entity
        """
        mass_default: str = cfg['mass_default_int']
        sizescale_default: str = cfg['sizescale_default_two_dec']

        # get previously determined overall scale
        trub_scale = self.get_trub_scale(entity)  # where "100" = 100%

        entity = self.scale_property(entity, 'SizeScale', {'pct_random_int': trub_scale,
                                                           'default': sizescale_default})

        # Mass uses size-cubed rule for gross mass, +/-10% for variance
        ratio = float(trub_scale) / 100.0
        cubed = pow(ratio, 3) * (0.9 + self.rand.random() * 0.2)  # +/- 10%
        cubed_str = str(max(int(cubed * 100), 2))  # mimimum of 2

        # Use SizeScale change ratio to affect mass
        entity = self.scale_property(entity, 'Mass', {'pct_random_int': cubed_str,
                                                      'default': mass_default})

        return entity

    def modify_health_max_base(self, entity: ET.Element, pct_rand: str,
                               scaling: float = 1.0) -> Tuple[ET.Element, float]:
        """
        Alter the max health based on overall scaling
        <effect_group name="Base Effects">
           <passive_effect name="HealthMax" operation="base_set" value="300"/>

        :param entity: source entity
        :param pct_rand: variance around health max
        :param scaling: additional scaling
        :return: Tuple of (modified entity, actual meat-scaling)
        """
        trub_scale = self.get_trub_scale(entity)
        ts_float = float(trub_scale) / 100.0 * scaling
        use_scaling = ts_float

        for health in entity.findall(".//effect_group[@name='Base Effects']/passive_effect[@name='HealthMax']"):
            if health.attrib.get('operation', None) != "base_set":
                continue

            if ts_float >= 1:
                use_scaling = pow(ts_float, 1.66)  # larger is a power
            else:
                use_scaling = pow(ts_float, 0.6)  # smaller is a root

            # raging animals are tougher
            if self.is_raging(entity):
                use_scaling = use_scaling * 3.0

            original = health.attrib['value']  # original size
            new_val = self.vary_percent_around_number(original, pct_rand,
                                                      self.determine_num_decimals(original),
                                                      mult=use_scaling)
            if new_val != original:
                health.set('value', new_val)
                logger.debug(f"   Changed HealthMax from {original} to {new_val}")

            t = entity.attrib.get('original_name', None)
            if t is not None:
                biggest = max(int(original), int(new_val))
                if t not in self.biggest or self.biggest.get(t) < biggest:
                    self.biggest[t] = biggest
            break

        return entity, use_scaling

    def modify_entity_damage(self, entity: ET.Element) -> ET.Element:
        """
        Increase or reduce EntityDamage based on the scaled size.

        <effect_group name="Base Effects">
           <passive_effect name="EntityDamage" operation="perc_add" value=".4" />
           <passive_effect name="EntityDamage" operation="perc_subtract" value=".4" />

        :param entity: source entity
        :return: modified entity
        """
        trub_scale = self.get_trub_scale(entity)
        if trub_scale == 100:
            return entity

        ts_float = float(trub_scale) / 100.0
        for node in entity.findall(f".//effect_group[@name='Base Effects']"):
            if ts_float > 1.0:
                new_val = ts_float - 1.0
                mode = "perc_add"
            elif ts_float < 1.0:
                new_val = 1.0 - ts_float
                mode = "perc_subtract"
            else:
                break

            item = ET.SubElement(node, 'passive_effect')
            item.set('name', "EntityDamage")
            item.set('value', f"{new_val:.2f}")
            item.set('operation', mode)
            item.tail = "\n    "
            logger.debug(f" + Added EntityDamage '{mode}' as {new_val}")
            break

        return entity

    def vary_health_and_exp(self, entity: ET.Element, cfg: Dict, meat_scaling: float = 1.0,
                            exp_scaling: float = 1.0) -> ET.Element:
        """
        The healthier the more damage/bullets the more exp.  However, in headshot mode reduce exp due.
        to
        
        :param entity: source entity
        :param cfg: variance data
        :param meat_scaling: additional scaling for health
        :param exp_scaling: optional scaling for exp; uses meat_scaling if not defined
        :return: modified entity
        """
        pct_rand_int: str = cfg['pct_random_int']
        exp_gain_default_int: str = cfg['experience_gain_default_int']

        entity, ratio = self.modify_health_max_base(entity, pct_rand_int, scaling=meat_scaling)
        ratio = ratio * (exp_scaling / meat_scaling)

        # raging animels get a 25% exp bump
        if self.is_raging(entity):
            ratio = ratio * 1.25

        scaled = str(max(int(ratio * 100), 1))
        self.modify_entity_damage(entity)

        entity = self.scale_property(entity, 'ExperienceGain', {'pct_random_int': scaled,
                                                                'default': exp_gain_default_int})

        return entity

    @staticmethod
    def set_property(entity: ET.Element, property_name: str, val: str) -> ET.Element:
        """
        This looks for a property.  If found, then sets it to the val
        BUT if it cannot find a property, creates it and sets to val
        
        :param entity: source entity
        :param property_name: property to be affected
        :param val: value to set
        :return: modified entity
        """
        found = False
        for node in entity.findall(f".//property[@name='{property_name}']"):
            found = True
            original = node.attrib['value']
            if val != original:  # only change if different
                node.set('value', val)
                logger.debug(f"   Changed {property_name} from {original} to {val}")

        # ok, we did NOT find a property_name attribute. gotta make a new one
        if not found:
            prop = ET.Element("property")
            prop.set('name', property_name)
            prop.set('value', val)
            prop.tail = "\n    "
            entity.insert(1, prop)
            logger.debug(f" + Defined {property_name} as {val}")

        return entity

    def randomize_property_from_range(self, entity: ET.Element, property_name: str,
                                      cfg: Dict) -> ET.Element:
        """
        Take a property and randomize the value within a "low-high" range.
            <property name="DismemberMultiplierArms" value=".7"/> <!-- Feral --> 1 = standard
        
        :param entity: source entity
        :param property_name: property to be affected
        :param cfg: variance data
        :return: modified entity
        """
        if "only_allow_these_entities_list" in cfg and \
                entity.attrib['extends'] not in cfg["only_allow_these_entities_list"]:
            return entity

        low = cfg['low']
        high = cfg['high']

        new_val = self.random_number_from_range(low, high)
        entity = self.set_property(entity, property_name, new_val)

        return entity

    def randomize_ranged_property_from_dual_ranges(self, entity: ET.Element, property_name: str,
                                                   cfg: Dict) -> ET.Element:
        """
        Take a property with a low-high range and randomize those values within their own "low-high" range.
            <property name="JumpMaxDistance" value="2.8, 3.9"/>

        The low2 and high1 should probably not cross/touch, e.g. 3.4,3.5 and not 3.7,3.5

        :param entity: source entity
        :param property_name: property to be affected
        :param cfg: variance data
        :return: modified entity
         """
        low1 = cfg['low1']
        low2 = cfg['low2']
        high1 = cfg['high1']
        high2 = cfg['high2']

        rescale = cfg.get('scale', None)  # use to scale up or down resulting values

        new_low_val = self.random_number_from_range(low1, low2, rescale)
        new_high_val = self.random_number_from_range(high1, high2, rescale)
        new_val = new_low_val + ',' + new_high_val  # Its a range itself
        entity = self.set_property(entity, property_name, new_val)

        return entity

    @staticmethod
    def add_property_if_missing(entity: ET.Element, property_name: str,
                                value: str, replacable: bool = False) -> ET.Element:
        """
        This looks for a property.  If it cannot find a property, it inserts a new property,
        but if it exists we leave it alone.

        :param entity: source entity
        :param property_name: property being varied
        :param value: new value
        :param replacable: If True, can be replaced if it exists
        :return: modified entity
        """
        found = False
        for node in entity.findall(f".//property[@name='{property_name}']"):
            if replacable:
                found = True
                node.set('value', value)
        if found:
            return entity

        # ok, we did NOT find the attribute, gotta make a new one
        if not found:
            prop = ET.Element("property")
            prop.set('name', property_name)
            prop.set('value', value)  # random this
            prop.tail = "\n    "
            entity.insert(1, prop)

        return entity

    # ----- AI alteration code
    # FUTURE: randomize numeric entries?
    AI_BEAR = [
        ("AITask-1", "BreakBlock"),
        ("AITask-2", "DestroyArea"),
        ("AITask-3", "Territorial"),
        ("AITask-4", "ApproachAndAttackTarget", "class=EntityAnimalStag,40,EntityPlayer,25,EntityZombie,30"),
        ("AITask-5", "ApproachSpot"),
        ("AITask-6", "Look"),
        ("AITask-7", "Wander"),
        ("AITask-8", ""),  # end task
        ("AITarget-1", "SetAsTargetIfHurt"),
        ("AITarget-2", "BlockingTargetTask"),
        ("AITarget-3", "SetNearestEntityAsTarget", "class=EntityPlayer,13,8,EntityAnimalStag,0,0,EntityZombie,0,0"),
        ("AITarget-4", "")
    ]

    AI_WOLF = [
        ("AITask-1", "BreakBlock"),
        ("AITask-2", "Territorial"),
        ("AITask-3", "RunawayWhenHurt", "runChance=0.5;healthPer=0.3;healthPerMax=0.6"),
        ("AITask-4", "ApproachAndAttackTarget", "class=EntityAnimalStag,20,EntityPlayer,15,EntityZombie,20"),
        ("AITask-5", "ApproachSpot"),
        ("AITask-6", "Look"),
        ("AITask-7", "Wander"),
        ("AITask-8", ""),
        ("AITarget-1", "SetAsTargetIfHurt"),
        ("AITarget-2", "BlockingTargetTask"),
        ("AITarget-3", "SetNearestEntityAsTarget", "class=EntityPlayer,14,8,EntityAnimalStag,0,0,EntityZombie,0,0"),
        ("AITarget-4", "")
    ]

    AI_COYOTE = [
        ("AITask-1", "BreakBlock"),
        ("AITask-2", "Territorial"),
        ("AITask-3", "RunawayWhenHurt", "runChance=.9;healthPer=.6;healthPerMax=0.75"),
        ("AITask-4", "ApproachAndAttackTarget", "class=EntityAnimalRabbit,8,EntityPlayer,10"),
        ("AITask-5", "ApproachSpot"),
        ("AITask-6", "Look"),
        ("AITask-7", "Wander"),
        ("AITask-8", ""),
        ("AITarget-1", "SetAsTargetIfHurt"),
        ("AITarget-2", "BlockingTargetTask"),
        ("AITarget-3", "SetNearestEntityAsTarget", "class=EntityPlayer,15,10,EntityAnimalRabbit,0,18"),
        ("AITarget-4", "")
    ]

    AI_DIREWOLF = [
        ("AITask-1", "BreakBlock"),
        ("AITask-2", "Territorial"),
        ("AITask-3", "ApproachAndAttackTarget", "class=EntityAnimalStag,30,EntityPlayer,30"),
        ("AITask-4", "ApproachSpot"),
        ("AITask-5", "Look"),
        ("AITask-6", "Wander"),
        ("AITask-7", ""),
        ("AITarget-1", "SetAsTargetIfHurt"),
        ("AITarget-2", "BlockingTargetTask"),
        ("AITarget-3", "SetNearestEntityAsTarget", "class=EntityPlayer,29,24,EntityAnimalStag,0,0"),
        ("AITarget-4", "")
    ]

    AI_MOUNTAINLION = [
        ("AITask-1", "Leap", "legs=4"),
        ("AITask-2", "BreakBlock"),
        ("AITask-3", "Territorial"),
        ("AITask-4", "RunawayWhenHurt", "runChance=.4;healthPer=.1;healthPerMax=.4"),
        ("AITask-5", "ApproachAndAttackTarget", "class=EntityAnimalStag,30,EntityPlayer,15,EntityZombie,20"),
        ("AITask-6", "ApproachSpot"),
        ("AITask-7", "Look"),
        ("AITask-8", "Wander"),
        ("AITask-9", ""),
        ("AITarget-1", "SetAsTargetIfHurt"),
        ("AITarget-2", "BlockingTargetTask"),
        ("AITarget-3", "SetNearestEntityAsTarget", "class=EntityPlayer,14,9,EntityAnimalStag,0,0,EntityZombie,0,5"),
        ("AITarget-4", "")
    ]

    AI_SNAKE = [
        ("AITask-1", "BreakBlock"),
        ("AITask-2", "Territorial"),
        ("AITask-3", "ApproachAndAttackTarget", "class=EntityPlayer,15,EntityNPC,15"),
        ("AITask-4", "ApproachSpot"),
        ("AITask-5", "Look"),
        ("AITask-6", "Wander"),
        ("AITask-7", ""),
        ("AITarget-1", "SetAsTargetIfHurt", "class=EntityNPC,EntityPlayer"),
        ("AITarget-2", "BlockingTargetTask"),
        ("AITarget-3", "SetNearestCorpseAsTarget", "class=EntityPlayer"),
        ("AITarget-4", "SetNearestEntityAsTarget", "class=EntityPlayer,12,0,EntityNPC,0,0"),
        ("AITarget-5", "")
    ]

    # The Boar AI is kind of boring; they usually just stand there like dummies -- tweaking it to add Territorial
    AI_BOAR = [
        ("AITask-1", "BreakBlock"),
        ("AITask-2", "Territorial"),
        ("AITask-3", "ApproachAndAttackTarget", "class=EntityNPC,20,EntityPlayer,20"),
        ("AITask-4", "ApproachSpot"),
        ("AITask-5", "Look"),
        ("AITask-6", "Wander"),
        ("AITask-7", ""),
        ("AITarget-1", "SetAsTargetIfHurt"),
        ("AITarget-2", "BlockIf", "condition=alert e 0"),
        ("AITarget-3", "BlockingTargetTask"),
        ("AITarget-4", "SetNearestEntityAsTarget", "class=EntityPlayer,20,15,EntityNPC,15,10"),
        ("AITarget-5", "")
    ]

    AI_GRACE = [
        ("AITask-1", "BreakBlock"),
        ("AITask-2", "DestroyArea"),
        ("AITask-3", "Territorial"),
        ("AITask-4", "ApproachAndAttackTarget", "class=EntityPlayer,30,EntityZombie,10"),
        ("AITask-5", "ApproachSpot"),
        ("AITask-6", "Look"),
        ("AITask-7", "Wander"),
        ("AITask-8", ""),
        ("AITarget-1", "SetAsTargetIfHurt"),
        ("AITarget-2", "BlockingTargetTask"),
        ("AITarget-3", "SetNearestCorpseAsTarget", "class=EntityPlayer"),
        ("AITarget-4", "SetNearestEntityAsTarget", "class=EntityPlayer,0,0,EntityZombie,0,3"),
        ("AITarget-5", "")
    ]

    AI_DOG = [
        ("AITask-1", "BreakBlock"),
        ("AITask-2", "Territorial"),
        ("AITask-3", "ApproachAndAttackTarget", "class=EntityPlayer,20,EntityNPC,20"),
        ("AITask-4", "ApproachSpot"),
        ("AITask-5", "Look"),
        ("AITask-6", "Wander"),
        ("AITask-7", ""),
        ("AITarget-1", "SetAsTargetIfHurt", "class=EntityNPC,EntityPlayer"),
        ("AITarget-2", "BlockingTargetTask"),
        ("AITarget-3", "SetNearestCorpseAsTarget", "class=EntityPlayer"),
        ("AITarget-4", "SetNearestEntityAsTarget", "class=EntityPlayer,20,0,EntityNPC,0,0"),
        ("AITarget-5", "")
    ]

    AI_ZOMBIE = [
        ("AINoiseSeekDist", "8"),
        ("AIPathCostScale", ".15, .4"),
        ("AITask-1", "BreakBlock"),
        ("AITask-2", "DestroyArea"),
        ("AITask-3", "Territorial"),
        # class,maxChaseTime (return home)
        ("AITask-4", "ApproachAndAttackTarget", "class=EntityNPC,0,EntityEnemyAnimal,0,EntityPlayer,0"),
        ("AITask-5", "ApproachSpot"),
        ("AITask-6", "Look"),
        ("AITask-7", "Wander"),
        ("AITask-8", ""),
        ("AITarget-1", "SetAsTargetIfHurt", "class=EntityNPC,EntityEnemyAnimal,EntityPlayer"),
        ("AITarget-2", "BlockingTargetTask"),
        ("AITarget-3", "SetNearestCorpseAsTarget", "class=EntityPlayer"),
        # class, hear distance, see dist (checked left to right, 0 dist uses entity default)
        ("AITarget-4", "SetNearestEntityAsTarget", "class=EntityPlayer,0,0,EntityNPC,0,0"),
        ("AITarget-5", "")
    ]

    AI_SPIDER = [
        ("AINoiseSeekDist", "3"),
        ("AIPathCostScale", ".6, 1"),
        ("AITask-1", "Leap"),
        ("AITask-2", "BreakBlock"),
        ("AITask-3", "DestroyArea"),
        ("AITask-4", "Territorial"),
        ("AITask-5", "ApproachDistraction"),
        ("AITask-6", "ApproachAndAttackTarget", "class=EntityNPC,0,EntityEnemyAnimal,0,EntityPlayer,0"),
        ("AITask-7", "ApproachSpot"),
        ("AITask-8", "Look"),
        ("AITask-9", "Wander"),
        ("AITask-10", ""),
        ("AITarget-1", "SetAsTargetIfHurt", "class=EntityNPC,EntityEnemyAnimal,EntityPlayer"),
        ("AITarget-2", "BlockingTargetTask"),
        ("AITarget-3", "SetNearestCorpseAsTarget", "class=EntityPlayer"),
        # class, hear distance, see dist (checked left to right, 0 dist uses entity default)
        ("AITarget-4", "SetNearestEntityAsTarget", "class=EntityPlayer,0,0,EntityNPC,0,0"),
        ("AITarget-5", "")
    ]

    AI_COP = [
        ("AINoiseSeekDist", "8"),
        ("AIPathCostScale", ".15, .4"),
        ("AITask-1", "BreakBlock"),
        ("AITask-2", "ApproachAndAttackTarget", "class=EntityNPC,0,EntityPlayer"),
        ("AITask-3", "ApproachSpot"),
        ("AITask-4", "Look"),
        ("AITask-5", "Wander"),
        ("AITask-6", ""),
        ("AITarget-1", "SetAsTargetIfHurt", "class=EntityNPC,EntityEnemyAnimal,EntityPlayer"),
        ("AITarget-2", "BlockingTargetTask"),
        ("AITarget-3", "SetNearestCorpseAsTarget", "class=EntityPlayer"),
        # class, hear distance, see dist (checked left to right, 0 dist uses entity default)
        ("AITarget-4", "SetNearestEntityAsTarget", "class=EntityPlayer,0,0,EntityNPC,0,0"),
        ("AITarget-5", "")
    ]

    AI_DEMO = [
        ("AINoiseSeekDist", "8"),
        ("AIPathCostScale", ".15, .4"),
        ("AITask-1", "BreakBlock"),
        ("AITask-2", "DestroyArea"),
        ("AITask-3", "ApproachAndAttackTarget", "class=EntityNPC,0,EntityEnemyAnimal,0,EntityPlayer,0"),
        ("AITask-4", "ApproachSpot"),
        ("AITask-5", "Look"),
        ("AITask-6", "Wander"),
        ("AITask-7", ""),
        ("AITarget-1", "SetAsTargetIfHurt", "class=EntityNPC,EntityEnemyAnimal,EntityPlayer"),
        ("AITarget-2", "BlockingTargetTask"),
        ("AITarget-3", "SetNearestCorpseAsTarget", "class=EntityPlayer"),
        # class, hear distance, see dist (checked left to right, 0 dist uses entity default)
        ("AITarget-4", "SetNearestEntityAsTarget", "class=EntityPlayer,0,0,EntityNPC,0,0"),
        ("AITarget-5", "")
    ]

    AI_LIST1 = [
        ("animalBear", AI_BEAR),
        ("animalWolf", AI_WOLF),
        ("animalCoyote", AI_COYOTE),
        ("animalMountainLion", AI_MOUNTAINLION),
        ("animalSnake", AI_SNAKE),
        ("animalBoar", AI_BOAR),
        ("animalZombieDog", AI_DOG),
    ]
    AI_LIST2 = [
        ("animalDireWolf", AI_DIREWOLF),
        ("animalBossGrace", AI_GRACE),
        ("zombieTemplateMale", AI_ZOMBIE),
        ("zombieSpider", AI_SPIDER),
        ("zombieFatCop", AI_COP),
        ("zombieDemolition", AI_DEMO),
    ]
    AI_LIST = AI_LIST1 + AI_LIST2

    # Zombie animals always act like zombies, most timid are unaffected
    EXCEPT_FOR = {
        "animalZombieBear": True,
        "animalZombieVulture": True,
        "animalZombieVultureRadiated": True,
        "animalZombieDog": True,
        "animalRabbit": True,
        "animalChicken": True,
        "animalDoe": True,
    }

    def alter_hostile_animal_ai(self, entity: ET.Element) -> ET.Element:
        """
        For enemy animals, have a chance of swapping out their normal AI with a different enemy animal AI.

        :param entity: supplied entity
        :return: modified entity
        """
        original = entity.attrib.get('original_name', "???")
        if self.rand.random() > self.altered_ai_percent or original in self.EXCEPT_FOR:
            return entity  # no change

        # remove any AITask or AITarget entries
        for node in entity.findall(f".//property"):
            if node.get('name').startswith("AITask-") or node.get('name').startswith("AITarget-"):
                logger.info(f"Saw {node.get('name')} = {node.get('value')}")
                entity.remove(node)

        # choose a new AI, other than existing
        use = None
        while use is None:
            pick = self.rand.choice(self.AI_LIST)
            if pick[0] != original:
                use = pick

        # add in new AI in proper order
        # ("name", "value") or ("name", "value", "data") for each entry
        for item in use[1]:
            prop = ET.Element("property")
            prop.set('name', item[0])
            prop.set('value', item[1])
            if len(item) > 2:
                prop.set('data', item[2])
            prop.tail = "\n    "
            entity.insert(-1, prop)
        entity.attrib['trub_ai'] = use[0]
        self.altered_ai_count += 1

        return entity


    MELEE = [
        "meleeHandAnimalWolf",
        "meleeHandAnimalDireWolf",
        "meleeHandAnimalBear",
        "meleeHandAnimalZombieBear",
        "meleeHandBossGrace"
    ]

    def raging_stag_ai(self, entity: ET.Element) -> ET.Element:
        """
        For stags, have a chance of swapping out their normal AI with an enemy animal AI.

        :param entity: supplied entity
        :return: modified entity
        """
        original = entity.attrib.get('original_name', "???")
        if self.rand.random() > self.raging_stag_percent or original != "animalStag":
            return entity  # no change

        # remove any AITask or AITarget entries
        for node in entity.findall(f".//property"):
            if node.get('name').startswith("AITask-") or node.get('name').startswith("AITarget-"):
                logger.info(f"Saw {node.get('name')} = {node.get('value')}")
                entity.remove(node)

        # choose a new AI
        use = self.rand.choice(self.AI_LIST2)  # animal AI only

        # add HandItem so it has something to work with
        use[1].append(("HandItem", self.rand.choice(self.MELEE)))

        # add in new AI in proper order
        # ("name", "value") or ("name", "value", "data") for each entry
        for item in use[1]:
            prop = ET.Element("property")
            prop.set('name', item[0])
            prop.set('value', item[1])
            if len(item) > 2:
                prop.set('data', item[2])
            prop.tail = "\n    "
            entity.insert(-1, prop)
        entity.attrib['trub_ai'] = use[0]

        entity.attrib['trub_raging'] = "yes"
        self.set_property(entity, "IsEnemyEntity", "true")
        self.set_property(entity, "AIGroupCircle", "1")
        self.set_property(entity, "AINoiseSeekDist", "6")
        self.set_property(entity, "AIPathCostScale", ".2, .4")
        self.set_property(entity, "Class", "EntityEnemyAnimal")
        self.raging_stag_count += 1
        return entity

    #######################################
    # ----- Entity Texture changing ----- #
    #######################################

    # NOTE: Don't use the following (makes things invisible):
    #   "particleeffects/materials/waterfallslope"
    #   "particleeffects/models/materials/p_fiber"
    #   "materials/occludeeshadowcaster"
    #   "materials/SoftGlow"

    # A19 materials, something causes problems when used, commented out and left for reference
    # # transparent, picks up eye glow
    # choices0a = [
    #     "entities/buildings/materials/glass_industrial_lod",
    #     "particleeffects/models/materials/p_glass",
    # ]
    # # solid
    # choices0b = [
    #     "entities/buildings/materials/chimney",
    #     "entities/resources/materials/orecoalboulder",
    #     "entities/resources/materials/oreshaleboulder",
    #     "entities/resources/materials/oreleadboulder",
    #     "particleeffects/models/car_explode",
    #     "particleeffects/models/materials/p_dirt",
    #     "particleeffects/models/materials/p_gib",
    #     "particleeffects/models/materials/p_wood",  # mummy
    #     "shapes/materials/wrought_iron_metal",
    #     "entities/animals/vulture/materials/vulture_v2",
    #     "entities/animals/boar/materials/grace",
    #     "entities/doors/materials/steel_door_2",
    #     "particleeffects/blood",
    #     "particleeffects/models/car_explode",
    #     "particleeffects/materials/blood_mist_tile_02",
    #     "itemmodeffects/materials/baton_arc",
    #     "Entities/Animals/Wolf/Materials/zombie_wolf"
    # ]
    # # ephemeral
    # choices0c = [
    #     "itemmodeffects/materials/baton_arc_fp",
    #     "itemmodeffects/materials/melee_fire",
    #     "materials/imageeffect_turretview",
    #     "materials/waterinbucket",
    # ]

    # transparent, picks up eye glow
    transparent = [
        "particleeffects/models/materials/p_glass",
        "entities/buildings/materials/window_glass02_lod",
    ]
    # solid
    solid = [
        "entities/animals/vulture/materials/vulture_v2",
        "entities/animals/boar/materials/grace",
        "entities/resources/materials/orecoalboulder",
        "entities/resources/materials/oreshaleboulder",
        "entities/resources/materials/oreleadboulder",
        "entities/gore/materials/torso_gore",
        "particleeffects/models/materials/p_gib",
        "particleeffects/models/car_explode",
        "entities/electrical/materials/flamethrowertrap",
        "shapes/materials/wrought_iron_metal",
        "particleeffects/models/materials/p_dirt",
        "particleeffects/models/materials/p_wood",
        "entities/electrical/materials/spotlight",
        "particleeffects/blood",
        "entities/electrical/materials/solarpanel",
        "#Other/Items?Misc/snowballPrefab/materials/snowball",
        "entities/buildings/materials/chimney",
        "entities/electrical/materials/electric_fence_post",
        "particleeffects/materials/blood_mist_tile_02",
        "entities/commercial/materials/metalpaintedwhite",
        "entities/furniture/materials/candelabra",
        "particleeffects/materials/heart",
        "Materials/UMAFur_ZombieBear",
    ]
    # ephemeral
    ephemeral = [
        "materials/waterinbucket",
        "itemmodeffects/materials/melee_fire",
        "itemmodeffects/materials/baton_arc",
    ]
    glowing = [
        "#Entities/Zombies?Zombies/Materials/feral_eye.mat",
        "#Entities/Zombies?Zombies/Materials/feral_radiated.mat",
        "#Entities/Zombies?Zombies/Materials/rad_eye.mat",
        "itemmodeffects/materials/melee_fire",
        "materials/wirematerial",
        "particleeffects/materials/p_spark_electricity",
        "itemmodeffects/materials/baton_arc_fp",
        "particleeffects/models/materials/electrical_arc",
    ]

    choices0 = transparent + solid + ephemeral

    # usually eye effects, hair for others
    choices1 = solid + glowing

    # usually hair effects
    choices2 = solid + ephemeral

    # structure to cut down on duplicate variants
    seen_variations = {}

    def replace_materials(self, entity: ET.Element, is_enemy: bool) -> ET.Element:
        """
        Based on information from Robeloto's mod, for some entities replace the meshes to make them freaky.

        Enabled with --meshes

        NOTES:
        Material0 is likely overall body
        Material1 is likely eye coloring
        Material2 is possibly particle effects or hair

        :param entity: source element
        :param is_enemy: True if zombie or hostile animal
        :return: modified element
        """
        entity_name = entity.attrib.get('original_name', None)

        chance = 0.5 if not self.mesh_always else 1.0

        three_strikes = 0  # used to prevent endless looping on material choice
        choice0 = None
        choice1 = None
        choice2 = None

        # not sure if these are even used, adding just in case
        choice3 = None
        choice4 = None
        choice5 = None

        key = ""
        while three_strikes < 3:
            # chance of material0
            if self.rand.random() < chance and is_enemy:
                choice0 = self.rand.choice(self.choices0)

            # chance of material1, automatic if material0 changed
            if (self.rand.random() < chance or choice0 is not None) and is_enemy:
                if choice0 in self.transparent or choice0 in self.glowing or choice0 in self.ephemeral:
                    choice1 = self.rand.choice(self.solid)  # no glowy if transparent or glowy
                elif choice0 in self.solid:
                    choice1 = self.rand.choice(self.glowing)
                else:
                    choice1 = self.rand.choice(self.choices1)

            # chance of material2
            if self.rand.random() < chance and is_enemy:
                choice2 = self.rand.choice(self.choices2)

            # chance of material3
            if self.rand.random() < chance and is_enemy:
                choice3 = self.rand.choice(self.choices1)

            # chance of material4
            if self.rand.random() < chance and is_enemy:
                choice4 = self.rand.choice(self.choices1)

            # chance of material5
            if self.rand.random() < chance and is_enemy:
                choice5 = self.rand.choice(self.choices1)

            key = f"{entity_name}-{choice0}-{choice1}-{choice2}"
            if choice0 is None and choice1 is None and choice2 is None:
                break  # no changes is special cased
            if key in self.seen_variations:
                three_strikes += 1
            else:
                self.seen_variations[key] = True
                break

        if three_strikes >= 3:
            logger.debug(f"%% -- Material 'three strikes' hit with {key} -- live with it...")

        if choice0 is not None:
            entity = self.add_property_if_missing(entity, "ReplaceMaterial0", choice0,
                                                  replacable=True)
        if choice1 is not None:
            entity = self.add_property_if_missing(entity, "ReplaceMaterial1", choice1,
                                                  replacable=True)
        if choice2 is not None:
            entity = self.add_property_if_missing(entity, "ReplaceMaterial2", choice2,
                                                  replacable=True)

        if choice3 is not None:
            entity = self.add_property_if_missing(entity, "ReplaceMaterial3", choice3,
                                                  replacable=True)
        if choice4 is not None:
            entity = self.add_property_if_missing(entity, "ReplaceMaterial4", choice4,
                                                  replacable=True)
        if choice5 is not None:
            entity = self.add_property_if_missing(entity, "ReplaceMaterial5", choice5,
                                                  replacable=True)

        return entity

    def modify_harvestables(self, zed: ET.Element) -> ET.Element:
        """
        The bigger the more stuff you can get off them; likewise smaller has less on them.
         Scaling is always +/- 10%.

        :param zed: source element
        :return: modified element
        """
        scaling = pow(float(self.get_trub_scale(zed)) / 100.0, 0.85)  # 2x -> x1.8; 3x -> x2.5, 1/2 -> x0.6

        for node in zed.findall(f".//drop[@event='Harvest']"):
            val = node.attrib['count']
            new_scale = (self.rand.random() * 0.2 + 0.9) * scaling
            new_val = max(int(val) * new_scale, 0)
            node.set('count', str(int(new_val + 0.5)))

        return zed

    def randomize_entity(self, entity_config_key: str, new_entity: ET.Element, entity_name: str,
                         is_animal: bool = False, is_enemy: bool = False) -> ET.Element:
        """
        Take an existing source entity and mangle it to specs.
        
        :param entity_config_key: entity key
        :param new_entity: source entity element
        :param entity_name: new entity name
        :param is_animal: True if animal (timid or hostile)
        :param is_enemy: True if enemy_animal or zombie
        :return: modified element
        """
        # Loop through configs for this entity
        config_keys = self.CONFIGS[entity_config_key].keys()

        # generate entity scale variation
        new_entity = self.generate_scaling(new_entity, is_animal, is_enemy)

        # check for animal rage
        if self.altered_ai and is_enemy and is_animal:
            new_entity = self.alter_hostile_animal_ai(new_entity)

        # check for raging stags
        if is_animal and not is_enemy and self.raging_stag:
            new_entity = self.raging_stag_ai(new_entity)

        for cfg_property_key in config_keys:

            if cfg_property_key in ['disable_randomizer', 'num_generation_loops', 'ignore_entity_list',
                                    'enable_walktype_crawler_limit']:
                continue

            if not self.is_randomizer_enabled_for_property(entity_config_key, cfg_property_key, entity_name):
                continue

            # Check if should ONLY apply/randomize configs for this entity
            # Specifically for configs that are entity specific: demolishers, vultures, etc.
            if self.is_entity_blocked_for_property(entity_config_key, cfg_property_key, entity_name):
                continue

            args = self.get_entity_config_file_configs(entity_config_key, cfg_property_key, entity_name)

            # Get the randomizer function name to use from defaults
            rand_function_key = self.CONFIGS['ConfigDefaults'][cfg_property_key]['rand_function']

            if rand_function_key == 'custom_WalkType':
                new_entity = self.randomize_walk_type(new_entity)
            elif rand_function_key == 'custom_TintMaterial':
                new_entity = self.randomize_tint(new_entity)
            elif rand_function_key == 'custom_MassAndWeightAndSizeScale':
                new_entity = self.vary_size_and_mass(new_entity, args)
            elif rand_function_key == 'custom_HealthAndExperienceGain':
                if self.headshot and not is_animal:  # headshot shamblers only
                    new_entity = self.vary_health_and_exp(new_entity, args, self.hsmeat, pow(self.hsmeat, 0.5))
                else:
                    new_entity = self.vary_health_and_exp(new_entity, args, 1.0, 1.0)
            elif rand_function_key == 'setcreate_one_range':
                new_entity = self.randomize_property_from_range(new_entity,
                                                                cfg_property_key, args)
            elif rand_function_key == 'setcreate_two_range':
                use_args = copy.deepcopy(args)
                if not is_animal:  # deal with zombie special cases
                    use_scale = 100
                    if self.headshot and cfg_property_key == "MoveSpeedAggro":
                        use_scale = self.hsspeed
                    if self.munchkins and cfg_property_key == "MoveSpeedAggro":
                        use_scale = int(10000.0 / float(self.get_trub_scale(new_entity)) + 0.5)
                    use_args['scale'] = str(use_scale)
                new_entity = self.randomize_ranged_property_from_dual_ranges(new_entity, cfg_property_key,
                                                                             use_args)
            elif rand_function_key == 'setcreate_rand_around_percent':
                new_entity = self.vary_property_around_base_value(new_entity, cfg_property_key, args)

            if cfg_property_key == "MoveSpeed":
                use_scale = 100
                if not is_animal and self.headshot:
                    use_scale = self.hsspeed
                if not is_animal and self.munchkins:
                    use_scale = int(10000.0 / float(self.get_trub_scale(new_entity)) + 0.5)
                if use_scale != 100:
                    new_entity = self.scale_property(new_entity, cfg_property_key,
                                                     {'pct_random_int': f"{use_scale}",
                                                      'default': "1.0"})


        # additions for odd strange zombies and hostile animals
        if self.meshes:
            new_entity = self.replace_materials(new_entity, is_enemy)

        # handle size affecting harvesting
        new_entity = self.modify_harvestables(new_entity)

        return new_entity

    def zed_generate(self) -> None:
        """
        Zombie Generate.
        """
        logger.info("\n" + '#' * 79 + "\n" + "## Generating Zombie Entities\n" + "#" * 79 + "\n")

        self.zed_library = {}

        # Get all the entity_class-es we want to handle, by type
        entity_class_zombies = self.TYPE_ENTITY_LOOKUP['EntityZombie']
        self.TOTAL_ZED_ENTITIES_FOUND = len(entity_class_zombies)
        the_key = 'ConfigEntityZombie'

        # NOTE: looping goes 1 for each type, looped should probably be reversed
        for i in range(int(self.CONFIGS[the_key]['num_generation_loops'])):  # may be str in json
            if self.CONFIGS[the_key]['disable_randomizer'] == 1:
                logger.info(f"!! Ignoring entity: {the_key}  Reason: Entire entity group disabled in config file")
                break

            for entity_name in entity_class_zombies:
                # Check to see if we should not randomise this entity
                if entity_name in self.CONFIGS[the_key]['ignore_entity_list']:
                    # logger.info(f"Ignoring entity: {entity_name} Reason: "
                    #             f"{self.CONFIGS[the_key]['ignore_entity_list'][entity_name]}")
                    continue

                # Clone entity
                self.zed_library[entity_name] = True
                new_entity_name, new_entity = self.generate_new_entity_from_existing_name(entity_name)

                if new_entity_name is None:
                    continue
                self.TOTAL_ZED_ENTITIES_GENERATED += 1

                # SPECIAL: Need this here BEFORE rand, for walktype checker. sigh
                if new_entity_name not in self.NEW_ENTITIES:
                    self.NEW_ENTITIES[new_entity_name] = {}
                self.NEW_ENTITIES[new_entity_name]['zed_is_from'] = entity_name

                new_entity = self.randomize_entity(the_key, new_entity, entity_name, is_enemy=True)
                logger.info("")

                # Save it!
                self.NEW_ENTITIES[new_entity_name]['zed_is_from'] = entity_name
                self.NEW_ENTITIES[new_entity_name]['zed_node'] = new_entity

    def enemy_animal_generate(self) -> None:
        """
        Enemy Animal Generation.
        """
        logger.info("\n" + '#' * 79 + "\n" + "## Generating EnemyAnimal Entities\n" + "#" * 79 + "\n")

        self.hostile_animal_library = {}

        # Get all the entity_class-es we want to handle, by type
        entity_class_hostile_animals = self.TYPE_ENTITY_LOOKUP['EntityEnemyAnimal']
        self.TOTAL_HOSTILE_ANIMAL_ENTITIES_FOUND = len(entity_class_hostile_animals)
        the_key = 'ConfigEntityEnemyAnimal'

        # NOTE: looping goes 1 for each type, looped should probably be reversed
        for i in range(int(self.CONFIGS[the_key]['num_generation_loops'])):
            if self.CONFIGS[the_key]['disable_randomizer'] == 1:
                logger.info(f"!! Ignoring entity: {the_key}  Reason: Entire entity group disabled in config file")
                break

            for entity_name in entity_class_hostile_animals:
                # Check to see if we should not randomise this entity
                if entity_name in self.CONFIGS[the_key]['ignore_entity_list']:
                    # logger.info(f"Ignoring entity: {entity_name} Reason: "
                    #             f"{self.CONFIGS[the_key]['ignore_entity_list'][entity_name]}")
                    continue

                # Clone entity
                self.hostile_animal_library[entity_name] = True
                new_entity_name, new_entity = self.generate_new_entity_from_existing_name(entity_name)
                if new_entity_name is None:
                    continue
                self.TOTAL_HOSTILE_ANIMAL_ENTITIES_GENERATED += 1

                new_entity = self.randomize_entity(the_key, new_entity, entity_name, is_animal=True, is_enemy=True)
                logger.info("")

                # Save it!
                if new_entity_name not in self.NEW_ENTITIES:
                    self.NEW_ENTITIES[new_entity_name] = {}
                self.NEW_ENTITIES[new_entity_name]['zed_is_from'] = entity_name
                self.NEW_ENTITIES[new_entity_name]['zed_node'] = new_entity

    def friendly_animal_generate(self) -> None:
        """
        Timid Animal Generation.
        """
        logger.info("\n" + '#' * 79 + "\n" + "## Generating Animal Entities\n" + "#" * 79 + "\n")

        self.timid_animal_library = {}

        # Get all the entity_class-es we want to handle, by type

        entity_class_friendly_animals = self.TYPE_ENTITY_LOOKUP['EntityAnimalStag']
        self.TOTAL_FRIENDLY_ANIMAL_ENTITIES_FOUND = len(entity_class_friendly_animals)
        the_key = 'ConfigEntityFriendlyAnimal'

        # NOTE: looping goes 1 for each type, looped should probably be reversed
        for i in range(int(self.CONFIGS[the_key]['num_generation_loops'])):
            if self.CONFIGS[the_key]['disable_randomizer'] == 1:
                logger.info(f"!! Ignoring entity: {the_key}  Reason: Entire entity group disabled in config file")
                break

            for entity_name in entity_class_friendly_animals:
                # Check to see if we should not randomise this entity
                if entity_name in self.CONFIGS[the_key]['ignore_entity_list']:
                    continue

                # Clone entity
                self.timid_animal_library[entity_name] = True
                new_entity_name, new_entity = self.generate_new_entity_from_existing_name(entity_name)
                if new_entity_name is None:
                    continue
                self.TOTAL_FRIENDLY_ANIMAL_ENTITIES_GENERATED += 1

                new_entity = self.randomize_entity(the_key, new_entity, entity_name, is_animal=True)
                logger.info("")

                # Save it!
                if new_entity_name not in self.NEW_ENTITIES:
                    self.NEW_ENTITIES[new_entity_name] = {}
                self.NEW_ENTITIES[new_entity_name]['zed_is_from'] = entity_name
                self.NEW_ENTITIES[new_entity_name]['zed_node'] = new_entity

    # ----- Modlet Output ------------------------------------------------------------

    def modlet_gen_start(self) -> None:
        """
        Start the mod creation process.
        """
        # Required Folders
        modlet_config_dir = self.CONFIGS['modlet_gen_dir'] + "/Config"

        if not os.path.exists(modlet_config_dir):
            logger.debug(f"Generating: {modlet_config_dir}")
            os.makedirs(modlet_config_dir)

        # Misc required files
        modinfo_file = self.CONFIGS['modlet_gen_dir'] + '/ModInfo.xml'
        logger.debug(f"Generating: {modinfo_file}")

        with open(modinfo_file, 'w') as fp:
            fp.write(
                    f"""<?xml version="1.0" encoding="UTF-8" ?>
<xml>
  <ModInfo>
    <Name value="{self.CONFIGS['modlet_name']}" />
    <Description value="Generated random entities from existing ones" />
    <Author value="trub64 (derived from Doughphunghus)" />
    <Version value="1.0.0" />
    <Website value="https://github.com/trub64/trubs-variants" />
  </ModInfo>
</xml>""")

        # Localization file
        localization_file = modlet_config_dir + '/Localization.txt'
        logger.debug(f"Generating: {localization_file}")
        with open(localization_file, 'w') as fp:
            fp.write('Key,File,Type,UsedInMainMenu,NoTranslate,english\n')

        # Entities file
        self.entities_xml_file = modlet_config_dir + '/entityclasses.xml'
        logger.debug(f"Starting Entities file: {self.entities_xml_file}")
        with open(self.entities_xml_file, 'w') as fp:
            fp.write(f"<{self.prefix}>" + "\n")
            fp.write('<append xpath="/entity_classes">' + "\n")

        # EntityGroups file
        self.entitygroups_xml_file = modlet_config_dir + '/entitygroups.xml'
        logger.debug(f"Starting EntityGroups file: {self.entitygroups_xml_file}")
        with open(self.entitygroups_xml_file, 'w') as fp:
            fp.write(f"<{self.prefix}>" + "\n")

        # headshots mode
        if self.headshot:
            items_xml_file = modlet_config_dir + '/items.xml'
            logger.debug(f"Generating: {items_xml_file}")

            # as per XML.txt, this adds the stated power as a percent to all headshots.  for the default hspower of
            # 150, that means any headshot hits are increased in power by 150% (i.e. 2.5x damage)
            with open(items_xml_file, 'w') as fp:
                fp.write(f"""<configs>
  <!-- All Headshots count for items that specify entity damage -->
  <append xpath="/items/item/effect_group/passive_effect[@name='EntityDamage'][1]/../.">
    <passive_effect name="DamageModifier" operation="perc_add" value="{self.hspower}" tags="head"/>
  </append>
</configs>
""")

    def modlet_gen_add_zed_to_entities_override(self, zed_node: ET.Element) -> None:
        """
        Add an entity to the entity classes file.
        
        :param zed_node: Entity information in XML format.
        """
        with open(self.entities_xml_file, 'a') as fp:
            fp.write(ET.tostring(zed_node, encoding='unicode'))
            fp.write("\n\n")

    def modlet_gen_add_zed_to_entity_groups_lookup(self, zed_name: str, is_from_zed: str) -> None:
        """
        Parse entity groups to locate where new entities go.
        
        :param zed_name: variant zed name.
        :param is_from_zed: source entity to look for
        """
        # Find the groups its in
        for entity_group in self.ENTITYGROUPS_DOM.findall('.//entitygroup'):
            entity_group_name = entity_group.attrib['name']

            # now search the group for the zed
            for entity in entity_group.findall(f".//entity[@name='{is_from_zed}']"):
                # ok, we found a node. ummm...clone it, update the name, make the override
                new_zed_entity = copy.deepcopy(entity)  # deep clone, all nodes below
                new_zed_entity.set('name', zed_name)  # Not changing build.xml

                xmlstring = ET.tostring(new_zed_entity, encoding='unicode')

                if entity_group_name in self.ENTITY_GROUP_LOOKUP:
                    self.ENTITY_GROUP_LOOKUP[entity_group_name].append(xmlstring)
                else:
                    self.ENTITY_GROUP_LOOKUP[entity_group_name] = [xmlstring]

    def modlet_gen_add_zeds_to_entity_groups_file(self) -> None:
        """
        Save new entites to existing groups.
        """
        entity_groups = sorted(list(self.ENTITY_GROUP_LOOKUP.keys()))
        for entity_group in entity_groups:
            with open(self.entitygroups_xml_file, 'a') as fp:
                fp.write(f"""<append xpath="/entitygroups/entitygroup[@name='{entity_group}']">""" + "\n")
                xml_strings_arayref = self.ENTITY_GROUP_LOOKUP[entity_group]

                for xmlstring in xml_strings_arayref:
                    fp.write("\t" + f"{xmlstring}" + "\n")  # Nice spacing
                fp.write('</append>' + "\n")

    def modlet_gen_finish(self) -> None:
        """
        Finish modlet creation
        """
        # Entities file
        logger.debug('Completing: Entities file.')
        with open(self.entities_xml_file, 'a') as fp:
            fp.write('</append>' + "\n")
            fp.write(f"</{self.prefix}>" + "\n")

        # EntityGroups file
        logger.debug('Completing: EntityGroups file.')
        with open(self.entitygroups_xml_file, 'a') as fp:
            fp.write(f"</{self.prefix}>" + "\n")

        modlet_dir = self.CONFIGS['modlet_gen_dir']

        with open(os.path.join(modlet_dir, "enities.info"), 'w') as fp:
            fp.write("===== Zombies =====\n")
            for item in sorted(list(self.zed_library.keys())):
                fp.write(f"{item}\n")

            fp.write("\n===== Hostile Animals =====\n")
            for item in sorted(list(self.hostile_animal_library.keys())):
                fp.write(f"{item}\n")

            fp.write("\n===== Timid Animals =====\n")
            for item in sorted(list(self.timid_animal_library.keys())):
                fp.write(f"{item}\n")

        with open(os.path.join(modlet_dir, "settings.info"), 'w') as fp:
            fp.write(f"Options Used: {self.cmd}\n\n")

            fp.write(f"x{self.zcount:3d} zombie variants ({self.TOTAL_ZED_ENTITIES_GENERATED})\n")
            fp.write(f"x{self.fcount:3d} timid animal variants ({self.TOTAL_FRIENDLY_ANIMAL_ENTITIES_GENERATED})\n")
            fp.write(f"x{self.ecount:3d} hostile animal variants ({self.TOTAL_HOSTILE_ANIMAL_ENTITIES_GENERATED})\n")
            if self.no_scale:
                fp.write(f" - no size variations\n")
            if self.meshes:
                fp.write(f" - with freak meshes\n")
            if self.mesh_always:
                fp.write(f"    - 100% chance\n")
            if self.altered_ai:
                chance = int(self.altered_ai_percent * 100)
                fp.write(f" - with {chance}% possible altered hostile AI\n")
                if self.altered_ai_count > 0:
                    fp.write(f"   ... {self.altered_ai_count} hostile animal behaviors changed\n")
            if self.raging_stag:
                chance = int(self.raging_stag_percent * 100)
                fp.write(f" - with {chance}% possible stag has hostile AI\n")
                if self.raging_stag_count > 0:
                    fp.write(f"   ... {self.raging_stag_count} raging stags\n")

            if self.giants:
                fp.write(f" - with Land of the Giants mode\n")
            if self.munchkins:
                fp.write(f" - with Munchkins mode\n")
            if self.headshot:
                fp.write(f" - with Headshot mode\n")
                fp.write(f"    - headshot power {self.hspower}%\n")
                fp.write(f"    - zombie meat {self.hsmeat}x\n")
                fp.write(f"    - zombie speed {self.hsspeed}%\n")
            fp.write("\n--------------------------------------------------\n")
            fp.write("BIGGEST:\n")
            for n, v in sorted(self.biggest.items()):
                fp.write(f"   {n:30s} - {v:5d} hp\n")

    def modlet_generate(self) -> None:
        """
        Generate the modlet folder and files.
        """
        logger.info('## Generating Modlet ...')
        self.modlet_gen_start()

        zeds = sorted(list(self.NEW_ENTITIES.keys()))
        if len(zeds) == 0:
            logger.info('## ... no entities generated; exiting.')
            return

        logger.info('#### Adding Entities to Modlet ...')
        for zed_name in zeds:
            zed_node = self.NEW_ENTITIES[zed_name]['zed_node']
            is_from_zed = self.NEW_ENTITIES[zed_name]['zed_is_from']

            self.modlet_gen_add_zed_to_entities_override(zed_node)
            self.modlet_gen_add_zed_to_entity_groups_lookup(zed_name, is_from_zed)

        logger.info('#### Adding Entities to Groups ...')
        self.modlet_gen_add_zeds_to_entity_groups_file()

        self.modlet_gen_finish()

        logger.info(f"Generated Zeds: {self.TOTAL_ZED_ENTITIES_GENERATED} entities from: "
                    f"{self.TOTAL_ZED_ENTITIES_FOUND} base entities")
        logger.info(f"Generated Hostile Animals: {self.TOTAL_HOSTILE_ANIMAL_ENTITIES_GENERATED} entities from: "
                    f"{self.TOTAL_HOSTILE_ANIMAL_ENTITIES_FOUND} base entities")
        logger.info(f"Generated Friendly Animals: {self.TOTAL_FRIENDLY_ANIMAL_ENTITIES_GENERATED} entities from: "
                    f"{self.TOTAL_FRIENDLY_ANIMAL_ENTITIES_FOUND} base entities")


################################################################################
# Begin Main
################################################################################


def build_cli_parser() -> argparse.Namespace:
    """
    Build the set of accepted options.
    """

    parser = argparse.ArgumentParser(description="Create a variant set of 7D2D entities")

    # for each supported output type, add an optiuon
    parser.add_argument("--config", action="store", dest="config", default="./config.json",
                        help="Specify the local JSON config file")
    parser.add_argument("--debug", action="store_true", dest="debug", default=False,
                        help="Enable debug logging\n")
    parser.add_argument("--dryrun", action="store_true", dest="dryrun", default=False,
                        help="Generate only, no output\n")
    parser.add_argument("--version", action="store", dest="version", default=None,
                        help="(optional) game version this is derived from")

    parser.add_argument("-z", action="store", type=int, dest="zcount", default=-1,
                        help="count for zombie variants (default x10")
    parser.add_argument("-f", action="store", type=int, dest="fcount", default=-1,
                        help="count for friendly animal variants (default x10)")
    parser.add_argument("-e", action="store", type=int, dest="ecount", default=-1,
                        help="count for enemy animal variants (default x30)")

    parser.add_argument("-m", action="store_true", dest="meshes", default=False,
                        help="If specified enable freaky meshes")
    parser.add_argument("--ma", action="store_true", dest="mesh_always", default=False,
                        help="If specified, all mesh variants are 100% freaks (instead of 33% chance for each area)")

    parser.add_argument("-g", action="store_true", dest="giants", default=False,
                        help="If specified, land of the giants")
    parser.add_argument("-k", action="store_true", dest="munchkins", default=False,
                        help="If specified, land of the munchkins")

    parser.add_argument("--hs", action="store_true", dest="headshot", default=False,
                        help="If specified, hits are higher, speed is slower, headshots do more damage")
    parser.add_argument("--hs-power", action="store", type=int, dest="hspower", default=-1,
                        help="headshot impact (default 150)")
    parser.add_argument("--hs-meat", action="store", type=float, dest="hsmeat", default=-1.0,
                        help="headshot body toughness (default x3.0)")
    parser.add_argument("--hs-speed", action="store", type=int, dest="hsspeed", default=-1,
                        help="headshot zombie speed (default 25)")

    parser.add_argument("--ns", action="store_true", dest="noscale", default=False,
                        help="If specified, no size variation (incompatible with -g or -k)")

    parser.add_argument("-a", action="store_true", dest="altered_ai", default=False,
                        help="If specified, chance of altered AI for hostile animals (default 33%)")
    parser.add_argument("--ap", action="store", type=int, dest="altered_ai_percent", default=33,
                        help="Specify chance of altered hostile animal AI")

    parser.add_argument("-r", action="store_true", dest="raging_stag", default=False,
                        help="If specified, chance of hostile AI for stags (default 33%)")
    parser.add_argument("--rp", action="store", type=int, dest="raging_stag_percent", default=33,
                        help="Specify chance of raging stags")

    args = parser.parse_args()

    if args.debug:
        fmt = '%(levelname)5s [%(filename)s:%(lineno)-4d] %(message)s'
        logging.basicConfig(level=logging.DEBUG, format=fmt)
    else:
        logging.basicConfig(level=logging.INFO)
    return args


def main():
    """
    Main Routine.
    """
    args = build_cli_parser()

    if args.giants and args.munchkins:
        logger.error("Cannot specify -m and -k at the same time!")
        sys.exit(1)

    if args.noscale and (args.giants or args.munchkins):
        logger.error("Cannot specify -m or -k when --ns is specified!")
        sys.exit(1)

    if args.config is None:
        logger.error("You must specify a configuration file!")
        sys.exit(1)

    engine = RandEnt(args)

    engine.initial_setup()
    engine.generate_lookup_tables()

    engine.zed_generate()
    engine.enemy_animal_generate()
    engine.friendly_animal_generate()

    if not args.dryrun:
        engine.modlet_generate()


if __name__ == "__main__":
    main()
