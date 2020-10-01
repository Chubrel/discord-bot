#! python
# coding=utf-8

import random


class Common:

    @property
    def id(self):
        s = ''
        for i in self.__class__.__name__:
            if i.islower():
                s += i
            else:
                s += '_' + i.lower()
        return s[1:]


def get_class_name_from_id(ench_id):
    return ench_id.replace('_', ' ').title().replace(' ', '')


# ENCHANTMENTS


class Enchantment(Common):
    max_level = None
    max_ench_table_level = None
    incompatible_with = set()


class CurseOfVanishing(Enchantment):
    max_level = 1
    max_ench_table_level = 0


class CurseOfBinding(Enchantment):
    max_level = 1
    max_ench_table_level = 0


class Mending(Enchantment):
    max_level = 1
    max_ench_table_level = 0
    incompatible_with = {'infinity'}


class Unbreaking(Enchantment):
    max_level = 3
    max_ench_table_level = 3


class Protection(Enchantment):
    max_level = 4
    max_ench_table_level = 4
    incompatible_with = {'fire_protection', 'blast_protection', 'projectile_protection'}


class FireProtection(Enchantment):
    max_level = 4
    max_ench_table_level = 4
    incompatible_with = {'protection', 'blast_protection', 'projectile_protection'}


class BlastProtection(Enchantment):
    max_level = 4
    max_ench_table_level = 4
    incompatible_with = {'protection', 'fire_protection', 'projectile_protection'}


class ProjectileProtection(Enchantment):
    max_level = 4
    max_ench_table_level = 4
    incompatible_with = {'protection', 'fire_protection', 'blast_protection'}


class Thorns(Enchantment):
    max_level = 3
    max_ench_table_level = 2


class AquaAffinity(Enchantment):
    max_level = 1
    max_ench_table_level = 1


class Respiration(Enchantment):
    max_level = 3
    max_ench_table_level = 3


class FeatherFalling(Enchantment):
    max_level = 4
    max_ench_table_level = 4


class DepthStrider(Enchantment):
    max_level = 3
    max_ench_table_level = 3
    incompatible_with = {'frost_walker'}


class FrostWalker(Enchantment):
    max_level = 2
    max_ench_table_level = 0
    incompatible_with = {'depth_strider'}


class SoulSpeed(Enchantment):
    max_level = 3
    max_ench_table_level = 0


class Efficiency(Enchantment):
    max_level = 5
    max_ench_table_level = 4


class SilkTouch(Enchantment):
    max_level = 1
    max_ench_table_level = 1
    incompatible_with = {'fortune'}


class Fortune(Enchantment):
    max_level = 3
    max_ench_table_level = 3
    incompatible_with = {'silk_touch'}


class Sharpness(Enchantment):
    max_level = 5
    max_ench_table_level = 4
    incompatible_with = {'smite', 'bane_of_arthropods'}


class Smite(Enchantment):
    max_level = 5
    max_ench_table_level = 5
    incompatible_with = {'sharpness', 'bane_of_arthropods'}


class BaneOfArthropods(Enchantment):
    max_level = 5
    max_ench_table_level = 5
    incompatible_with = {'sharpness', 'smite'}


class Looting(Enchantment):
    max_level = 3
    max_ench_table_level = 3


class Knockback(Enchantment):
    max_level = 2
    max_ench_table_level = 2


class FireAspect(Enchantment):
    max_level = 2
    max_ench_table_level = 2


class SweepingEdge(Enchantment):
    max_level = 3
    max_ench_table_level = 3


class Flame(Enchantment):
    max_level = 1
    max_ench_table_level = 1


class Punch(Enchantment):
    max_level = 2
    max_ench_table_level = 2


class Infinity(Enchantment):
    max_level = 1
    max_ench_table_level = 1
    incompatible_with = {'mending'}


class Power(Enchantment):
    max_level = 5
    max_ench_table_level = 4


class QuickCharge(Enchantment):
    max_level = 3
    max_ench_table_level = 2


class Piercing(Enchantment):
    max_level = 5
    max_ench_table_level = 5
    incompatible_with = {'multishot'}


class Multishot(Enchantment):
    max_level = 1
    max_ench_table_level = 1
    incompatible_with = {'piercing'}


class Impaling(Enchantment):
    max_level = 5
    max_ench_table_level = 5


class Riptide(Enchantment):
    max_level = 3
    max_ench_table_level = 3
    incompatible_with = {'loyalty', 'channeling'}


class Loyalty(Enchantment):
    max_level = 3
    max_ench_table_level = 3
    incompatible_with = {'riptide'}


class Channeling(Enchantment):
    max_level = 1
    max_ench_table_level = 1
    incompatible_with = {'riptide'}


class Lure(Enchantment):
    max_level = 3
    max_ench_table_level = 3


class LuckOfTheSea(Enchantment):
    max_level = 3
    max_ench_table_level = 3


# ITEMS


class Enchantable(Common):
    _primary = set()
    _secondary = {'curse_of_vanishing'}

    @property
    def primaries(self):
        return self._primary

    @property
    def secondaries(self):
        return self._secondary

    @property
    def all_enchs(self):
        return self._primary | self._secondary


class Wearable(Enchantable):
    _secondary = Enchantable._secondary | {'curse_of_binding'}


class Breakable(Enchantable):
    _secondary = Enchantable._secondary | {'mending'}


class _PrimaryUnbreaking(Breakable):
    _primary = Breakable._primary | {'unbreaking'}


class _SecondaryUnbreaking(Breakable):
    _secondary = Breakable._secondary | {'unbreaking'}


class Shears(_SecondaryUnbreaking):
    _secondary = Breakable._secondary | {'efficiency'}


class FishingRod(_PrimaryUnbreaking):
    _primary = _PrimaryUnbreaking._primary | {'lure', 'luck_of_the_sea'}


class Bow(_PrimaryUnbreaking):
    _primary = _PrimaryUnbreaking._primary | {'infinity', 'flame', 'power', 'punch', 'infinity'}


class Crossbow(_PrimaryUnbreaking):
    _primary = _PrimaryUnbreaking._primary | {'multishot', 'piercing', 'quick_charge'}


class Trident(_PrimaryUnbreaking):
    _primary = _PrimaryUnbreaking._primary | {'impaling', 'loyalty', 'channeling', 'riptide'}


class Armor(Wearable, _PrimaryUnbreaking):
    _primary = Wearable._primary | _PrimaryUnbreaking._primary | {'protection', 'fire_protection',
                                                                  'blast_protection', 'projectile_protection'}
    _secondary = Wearable._secondary | _PrimaryUnbreaking._secondary


class _SecondaryThorns(Armor):
    _secondary = Armor._secondary | {'thorns'}


class Helmet(_SecondaryThorns):
    _primary = _SecondaryThorns._primary | {'aqua_affinity', 'respiration'}


class Chestplate(Armor):
    _primary = Armor._primary | {'thorns'}


class Leggings(_SecondaryThorns):
    pass


class Boots(_SecondaryThorns):
    _primary = _SecondaryThorns._primary | {'feather_falling', 'depth_strider'}
    _secondary = _SecondaryThorns._secondary | {'soul_speed', 'frost_walker'}


class MainInstrument(_PrimaryUnbreaking):
    _primary = _PrimaryUnbreaking._primary | {'fortune', 'silk_touch', 'efficiency'}


class MeleeWeapon(_PrimaryUnbreaking):
    _enchs = {'sharpness', 'smite', 'bane_of_arthropods'}


class Sword(MeleeWeapon):
    _primary = MeleeWeapon._primary | MeleeWeapon._enchs | {'fire_aspect', 'looting', 'knockback', 'sweeping_edge'}


class Axe(MainInstrument, MeleeWeapon):
    _primary = MainInstrument._primary | MeleeWeapon._primary
    _secondary = MainInstrument._secondary | MeleeWeapon._secondary | MeleeWeapon._enchs


class Pickaxe(MainInstrument):
    pass


class Shovel(MainInstrument):
    pass


class Hoe(MainInstrument):
    pass


class Shield(_SecondaryUnbreaking):
    pass


class Elytra(_SecondaryUnbreaking, Wearable):
    _primary = _SecondaryUnbreaking._primary | Wearable._primary
    _secondary = _SecondaryUnbreaking._secondary | Wearable._secondary


class FlintAndSteel(_SecondaryUnbreaking):
    pass


class CarrotOnAStick(_SecondaryUnbreaking):
    pass


class WarpedFungusOnAStick(_SecondaryUnbreaking):
    pass


class Pumpkin(Wearable):
    pass


class Head(Wearable):
    pass


class Compass(Enchantable):
    pass


if __name__ == '__main__':
    print(Axe().primaries)
    print(Axe().secondaries)
    print(Elytra().secondaries)
    print(Sword().all_enchs)
    print(eval(get_class_name_from_id('bane_of_arthropods()')))
    print(FlintAndSteel().id)
    print(Enchantable.__subclasses__())
    print(Axe.__subclasses__())
