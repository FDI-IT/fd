import copy

from collections import OrderedDict, namedtuple
from hazards.hazard_classes import CategoryTest, LD50Test


CategoryTestRow = namedtuple('CategoryTestRow', ('test', 'value', 'category', 'result', 'category_found'))
SubcategoryTestRow = namedtuple('SubcategoryTestRow', ('hazard', 'result', 'subcategory', 'subcategory_found'))

HazardCategoryInfo = namedtuple('HazardCategoryInfo', ('hcode', 'subcategories', 'category_test'))

# HAZARD_CLASS_NO_SUM_LIST = ('TOSTSingleHazard', 'CarcinogenicityHazard')


HazardClassDict = {

    'AcuteToxicityOral': OrderedDict([
        ('1', HazardCategoryInfo(
                hcode='H300',
                subcategories=('',),
                category_test=LD50Test('oral_ld50 <= 5'),
        )),
        ('2', HazardCategoryInfo(
                hcode='H300',
                subcategories=('',),
                category_test=LD50Test('oral_ld50 <= 50'),
        )),
        ('3', HazardCategoryInfo(
                hcode='H301',
                subcategories=('',),
                category_test=LD50Test('oral_ld50 <= 300'),
        )),
        ('4', HazardCategoryInfo(
                hcode='H302',
                subcategories=('',),
                category_test=LD50Test('oral_ld50 <= 2000'),
        )),
        ('5', HazardCategoryInfo( #Not Hazardous
                hcode='H303', #this should never be used in flavor review
                subcategories=('',),
                category_test=LD50Test('oral_ld50 > 2000'),
        )),
    ]),

    'AcuteToxicityDermal': OrderedDict([
        ('1', HazardCategoryInfo(
                hcode='H310',
                subcategories=('',),
                category_test=LD50Test('dermal_ld50 <= 50'),
        )),
        ('2', HazardCategoryInfo(
                hcode='H310',
                subcategories=('',),
                category_test=LD50Test('dermal_ld50 <= 200'),
        )),
        ('3', HazardCategoryInfo(
                hcode='H311',
                subcategories=('',),
                category_test=LD50Test('dermal_ld50 <= 1000'),
        )),
        ('4', HazardCategoryInfo(
                hcode='H312',
                subcategories=('',),
                category_test=LD50Test('dermal_ld50 <= 2000'),
        )),
        ('5', HazardCategoryInfo( #Not Hazardous
                hcode='H313', #this should never be used in flavor review
                subcategories=('',),
                category_test=LD50Test('dermal_ld50 > 2000'),
        )),
    ]),

    'SkinCorrosionHazard': OrderedDict([
        ('1', HazardCategoryInfo(
                hcode='H314',
                subcategories=('','A','B','C'),
                category_test=CategoryTest('SkinCorrosionHazard_1 >= 0.05'),
        )),
        ('2', HazardCategoryInfo(
                hcode='H315',
                subcategories=('',),
                category_test=CategoryTest('10*SkinCorrosionHazard_1 + SkinCorrosionHazard_2 >= 0.1')
        )),
        ('3', HazardCategoryInfo(
                hcode=None,
                subcategories=('',),
                category_test=CategoryTest('False'),
        ))
    ]),

    'SkinSensitizationHazard': OrderedDict([
        ('1', HazardCategoryInfo(
                hcode='H317',
                subcategories=('',),
                category_test=CategoryTest('SkinSensitizationHazard_1 >= 0.001'),
        )),
        ('1A', HazardCategoryInfo(
                hcode='H317',
                subcategories=('',),
                category_test=CategoryTest('SkinSensitizationHazard_1A >= 0.001')
        )),
        ('1B', HazardCategoryInfo(
                hcode='H317',
                subcategories=('',),
                category_test=CategoryTest('SkinSensitizationHazard_1B >= 0.01'),
        ))
    ]),

    'EyeDamageHazard': OrderedDict([
        ('1', HazardCategoryInfo(
                hcode='H318',
                subcategories=('',),
                category_test=CategoryTest('SkinCorrosionHazard_1 + EyeDamageHazard_1 >= 0.03'),
        )),
        ('2', HazardCategoryInfo(
                hcode='H319',
                subcategories=('','A','B'),
                category_test=CategoryTest('10*(SkinCorrosionHazard_1 + EyeDamageHazard_1) + EyeDamageHazard_2 >= 0.1')
        ))
    ]),

    'AcuteToxicityInhalation': OrderedDict([
        ('1', HazardCategoryInfo(
                hcode='H330',
                subcategories=('',),
                category_test=LD50Test('vapors_ld50 <= 0.5'),
        )),
        ('2', HazardCategoryInfo(
                hcode='H330',
                subcategories=('',),
                category_test=LD50Test('vapors_ld50 <= 2.0'),
        )),
        ('3', HazardCategoryInfo(
                hcode='H331',
                subcategories=('',),
                category_test=LD50Test('vapors_ld50 <= 10.0'),
        )),
        ('4', HazardCategoryInfo(
                hcode='H332',
                subcategories=('',),
                category_test=LD50Test('vapors_ld50 <= 20.0'),
        )),
        ('5', HazardCategoryInfo( #Not Hazardous
                hcode='H333', #this should never be used in flavor review
                subcategories=('',),
                category_test=LD50Test('vapors_ld50 > 20.0'),
        )),
    ]),

    'TOSTSingleHazard': OrderedDict([
        ('1', HazardCategoryInfo(
                hcode='H370',
                subcategories=('',),
                category_test=CategoryTest('TOSTSingleHazard_1 >= 0.01'),
        )),
        ('2', HazardCategoryInfo(
                hcode='H371',
                subcategories=('',),
                category_test=CategoryTest('TOSTSingleHazard_2 >= 0.01'),
        )),
        ('3NE', HazardCategoryInfo(
                hcode='H335',
                subcategories=('',),
                category_test=CategoryTest('TOSTSingleHazard_3NE >= 0.2')
        )),
        ('3RI', HazardCategoryInfo(
                hcode='H335',
                subcategories=('',),
                category_test=CategoryTest('TOSTSingleHazard_3RI >= 0.2')
        ))
    ]),

    'TOSTRepeatHazard': OrderedDict([
        ('1', HazardCategoryInfo(
                hcode='H372',
                subcategories=('',),
                category_test=CategoryTest('TOSTRepeatHazard_1 >= 0.01'),
        )),
        ('2', HazardCategoryInfo(
                hcode='H373',
                subcategories=('',),
                category_test=CategoryTest('TOSTRepeatHazard_2 >= 0.01'),
        ))
    ]),
                   
    'CarcinogenicityHazard': OrderedDict([
        ('1', HazardCategoryInfo(
                hcode='H350',
                subcategories=('','A','B'),
                category_test=CategoryTest('CarcinogenicityHazard_1 >= 0.001'),
        )),
        ('2', HazardCategoryInfo(
                hcode='H351',
                subcategories=('',),
                category_test=CategoryTest('CarcinogenicityHazard_2 >= 0.001'),
        ))
    ]),

    #this is a separate class because the same category had multiple h codes
    # 'CarcinogenicityInhalationHazard': OrderedDict([
    #     ('1', HazardCategoryInfo(
    #             hcode='H350i',
    #             subcategories=('','A','B'),
    #             category_test=CategoryTest('CarcinogenicityInhalationHazard_1 >= 0.001'),
    #     )),
    # ]),

    'GermCellMutagenicityHazard': OrderedDict([
        ('1A', HazardCategoryInfo(
                hcode='H340',
                subcategories=('',),
                category_test=CategoryTest('GermCellMutagenicityHazard_1A >= 0.001'),
        )),
        ('1B', HazardCategoryInfo(
                hcode='H340',
                subcategories=('',),
                category_test=CategoryTest('GermCellMutagenicityHazard_1B >= 0.001')
        )),
        ('2', HazardCategoryInfo(
                hcode='H341',
                subcategories=('',),
                category_test=CategoryTest('GermCellMutagenicityHazard_2 >= 0.01'),
        ))
    ]),

    'ReproductiveToxicityHazard': OrderedDict([
        ('1', HazardCategoryInfo(
                hcode='H360',
                subcategories=('','A','B'),
                category_test=CategoryTest('ReproductiveToxicityHazard_1 >= 0.001'),
        )),
        ('2', HazardCategoryInfo(
                hcode='H361',
                subcategories=('',),
                category_test=CategoryTest('ReproductiveToxicityHazard_2 >= 0.001'),
        )),
    ]),

    'AspirationHazard': OrderedDict([
        ('1', HazardCategoryInfo(
                hcode='H304',
                subcategories=('',),
                category_test=CategoryTest('AspirationHazard_1 >= 0.1'),
        )), 
    ]),
                   
    'FlammableLiquidHazard': OrderedDict([
        ('1', HazardCategoryInfo(
                hcode='H224',
                subcategories=('',),
                category_test=CategoryTest('False'),
        )),
        ('2', HazardCategoryInfo(
                hcode='H225',
                subcategories=('',),
                category_test=CategoryTest('False')
        )),
        ('3', HazardCategoryInfo(
                hcode='H226',
                subcategories=('',),
                category_test=CategoryTest('False'),
        )),
        ('4', HazardCategoryInfo(
                hcode='H227',
                subcategories=('',),
                category_test=CategoryTest('False'),
        )),
    ]),
                
}

HCodeDict = {
    'H224': { #flammable liquids
        'pictogram_code': 'GHS02',
        'signal_word': 'Danger',
        'statement': 'Extremely flammable liquid and vapour.',
        'p_codes': ['P210', 'P233', 'P240', 'P241', 'P242', 'P243', 'P280', 'P303+P361+P353', 'P370+P378', 'P403+P235', 'P501']
    },
    'H225': { 
        'pictogram_code': 'GHS02',
        'signal_word': 'Danger',
        'statement': 'Highly flammable liquid and vapour.',
        'p_codes': ['P210', 'P233', 'P240', 'P241', 'P242', 'P243', 'P280', 'P303+P361+P353', 'P370+P378', 'P403+P235', 'P501']
    },
    'H226': { 
        'pictogram_code': 'GHS02',
        'signal_word': 'Warning',
        'statement': 'Flammable liquid and vapour.',
        'p_codes': ['P210', 'P233', 'P240', 'P241', 'P242', 'P243', 'P280', 'P303+P361+P353', 'P370+P378', 'P403+P235', 'P501']
    },
    'H227': { 
        'pictogram_code': 'GHS02',
        'signal_word': 'Warning',
        'statement': 'Combustible liquid.',
        'p_codes': ['P210', 'P233', 'P240', 'P241', 'P242', 'P243', 'P280', 'P303+P361+P353', 'P370+P378', 'P403+P235', 'P501']
    },
    'H300': { #acute tox oral
        'pictogram_code': 'GHS06',
        'signal_word': 'Danger',
        'statement': 'Fatal if swallowed.',
        'p_codes': ['P264', 'P270', 'P301+P310', 'P321', 'P330', 'P405', 'P501']
    },
    'H301': {
        'pictogram_code': 'GHS06',
        'signal_word': 'Danger',
        'statement': 'Toxic if swallowed.',
        'p_codes': ['P264', 'P270', 'P301+P310', 'P321', 'P330', 'P405', 'P501']
    },
    'H302': {
        'pictogram_code': 'GHS07',
        'signal_word': 'Warning',
        'statement': 'Harmful if swallowed.',
        'p_codes': ['P264', 'P270', 'P301+P312', 'P330', 'P501']
    },
    'H304': { #Aspiration Hazard
        'pictogram_code': 'GHS08',
        'signal_word': 'Danger',
        'statement': 'May be fatal if swallowed and enters airway.',
        'p_codes': ['P301+P310', 'P331', 'P405', 'P501']
    },
    'H310': { #acute tox dermal
        'pictogram_code': 'GHS06',
        'signal_word': 'Danger',
        'statement': 'Fatal in contact with skin.',
        'p_codes': ['P262', 'P264', 'P270', 'P280', 'P302+P350', 'P310', 'P322', 'P361', 'P363', 'P405', 'P501']
    },
    'H311': {
        'pictogram_code': 'GHS06',
        'signal_word': 'Danger',
        'statement': 'Toxic in contact with skin',
        'p_codes': ['P280', 'P302+P352', 'P312', 'P322', 'P361', 'P363', 'P405', 'P501']
    },
    'H312': {
        'pictogram_code': 'GHS07',
        'signal_word': 'Warning',
        'statement': 'Harmful in contact with skin.',
        'p_codes': ['P280', 'P302+P352', 'P312', 'P322', 'P363', 'P501']
    },
    'H314': { #skin corrosion
        'pictogram_code': 'GHS05',
        'signal_word': 'Danger',
        'statement': 'Causes severe skin burns and eye damage.',
        'p_codes': ['P260', 'P264', 'P280', 'P301+P330+P331', 'P303+P361+P353',
                    'P363', 'P304+P340', 'P310', 'P321', 'P305+P351+P338',
                    'P405', 'P501']
    },
    'H315': {
        'pictogram_code': 'GHS07',
        'signal_word': 'Warning',
        'statement': 'Causes skin irritation.',
        'p_codes': ['P264', 'P280', 'P302+P352', 'P321', 'P332+P313', 'P362']
    },
    'H317': { #skin sensitization
        'pictogram_code': 'GHS07',
        'signal_word': 'Warning',
        'statement': 'May cause an allergic skin reaction.',
        'p_codes': ['P261', 'P272', 'P280', 'P302+P352', 'P333+P313', 'P321', 'P363', 'P501']
    },
    'H318': { #eye damage
        'pictogram_code': 'GHS05',
        'signal_word': 'Danger',
        'statement': 'Causes serious eye damage.',
        'p_codes': ['P280', 'P305+P351+P338', 'P310']
    },
    'H319': {
        'pictogram_code': 'GHS07',
        'signal_word': 'Warning',
        'statement': 'Causes serious eye irritation.',
        'p_codes': ['P264', 'P280', 'P305+P351+P338', 'P337+P313']
    },
    'H330': { #acute tox inhalation
        'pictogram_code': 'GHS06',
        'signal_word': 'Danger',
        'statement': 'Fatal if inhaled.',
        'p_codes': ['P260', 'P271', 'P284', 'P304+P340', 'P310', 'P320', 'P403+P233', 'P405', 'P501']
    },
    'H331': {
        'pictogram_code': 'GHS06',
        'signal_word': 'Danger',
        'statement': 'Toxic if inhaled.',
        'p_codes': ['P260', 'P271', 'P304+P340', 'P311', 'P321', 'P403+P233', 'P405', 'P501']
    },
    'H332': {
        'pictogram_code': 'GHS07',
        'signal_word': 'Warning',
        'statement': 'Harmful if inhaled.',
        'p_codes': ['P261', 'P271', 'P304+P340', 'P312']
    },
    'H334': { #respiratory sensitization
        'pictogram_code': 'GHS08',
        'signal_word': 'Danger',
        'statement': 'May cause allergy or asthma symptoms or breathing difficulties if inhaled.',
        'p_codes': ['P261', 'P285', 'P304+P341', 'P342+P311', 'P501']
    },
    'H335': { #TOST category 3
        'pictogram_code': 'GHS07',
        'signal_word': 'Warning',
        'statement': 'May cause respiratory irritation.',
        'p_codes': ['P261', 'P271', 'P304+P340', 'P312', 'P403+P233', 'P405', 'P501']
    },
    'H336': {
        'pictogram_code': 'GHS07',
        'signal_word': 'Warning',
        'statement': 'May cause drowsiness or dizziness.',
        'p_codes': ['P261', 'P271', 'P304+P340', 'P312', 'P403+P233', 'P405', 'P501']
    },
    'H340': { #Germ Cell Mutagenicity
        'pictogram_code': 'GHS08',
        'signal_word': 'Danger',
        'statement': 'May cause genetic defects.',
        'p_codes': ['P201', 'P202', 'P281', 'P308+P313', 'P405', 'P501']
    },
    'H341': { 
        'pictogram_code': 'GHS08',
        'signal_word': 'Warning',
        'statement': 'Suspected of causing genetic defects.',
        'p_codes': ['P201', 'P202', 'P281', 'P308+P313', 'P405', 'P501']
    },
    'H350': { #Carcinogenicity
        'pictogram_code': 'GHS08',
        'signal_word': 'Danger',
        'statement': 'May cause cancer.',
        'p_codes': ['P201', 'P202', 'P281', 'P308+P313', 'P405', 'P501']
    },
    'H350i': {
        'pictogram_code': 'GHS08',
        'signal_word': 'Danger',
        'statement': 'May cause cancer if inhaled.',
        'p_codes': ['P201', 'P202', 'P281', 'P308+P313', 'P405', 'P501']
    },
    'H351': {
        'pictogram_code': 'GHS08',
        'signal_word': 'Danger',
        'statement': 'Suspected of causing cancer.',
        'p_codes': ['P201', 'P202', 'P281', 'P308+P313', 'P405', 'P501']
    },
    'H360': { #Reproductive Toxicity
        'pictogram_code': 'GHS08',
        'signal_word': 'Danger',
        'statement': 'May damage fertility or the unborn child.',
        'p_codes': ['P201', 'P202', 'P281', 'P308+P313', 'P405', 'P501']
    },
    'H361': { 
        'pictogram_code': 'GHS08',
        'signal_word': 'Danger',
        'statement': 'Suspected of damaging fertility or the unborn child.',
        'p_codes': ['P201', 'P202', 'P281', 'P308+P313', 'P405', 'P501']
    },
    'H370': { #TOST category 1+2
        'pictogram_code': 'GHS08',
        'signal_word': 'Danger',
        'statement': 'Causes damage to organs.',
        'p_codes': ['P260', 'P264', 'P270', 'P307+P311', 'P405', 'P501']
    },
    'H371': {
        'pictogram_code': 'GHS08',
        'signal_word': 'Warning',
        'statement': 'May cause damage to organs.',
        'p_codes': ['P260', 'P264', 'P270', 'P307+P311', 'P405', 'P501']
    },
    'H372': {
        'pictogram_code': 'GHS08',
        'signal_word': 'Danger',
        'statement': 'Causes damage to organs through prolonged or repeated exposure.',
        'p_codes': ['P260', 'P264', 'P270', 'P314', 'P501']
    },
    'H373': {
        'pictogram_code': 'GHS08',
        'signal_word': 'Warning',
        'statement': 'Causes damage to organs through prolonged or repeated exposure.',
        'p_codes': ['P260', 'P314', 'P501']
    },

}

pcode_dict = {

    #P-100 General
    'P101': 'If medical advice is needed, have product container or label at hand.',
    'P102': 'Keep out of reach of children.',
    'P103': 'Read label before use.',

    #P-200 Prevention
    'P201': 'Obtain special instructions before use.',
    'P202': 'Do not handle until all safety precautions have been read and understood.',
    'P210': 'Keep away from heat/sparks/open flames/hot surfaces. - No smoking.',
    'P211': 'Do not spray on an open flame or other ignition source.',
    'P220': 'Keep/Store away from clothing/.../combustible materials.',
    'P221': 'Take any precaution to avoid mixing with combustibles.',
    'P222': 'Do not allow contact with air.',
    'P223': 'Keep away from any possible contact with water, because of violent reaction and possible flash fire.',
    'P230': 'Keep wetted with ...',
    'P231': 'Handle under inert gas.',
    'P232': 'Protect from moisture.',
    'P233': 'Keep container tightly closed.',
    'P234': 'Keep only in original container.',
    'P235': 'Keep cool.',
    'P240': 'Ground/bond container and receiving equipment.',
    'P241': 'Use explosion-proof electrical/ventilating/lighting/.../equipment.',
    'P242': 'Use only non-sparking tools.',
    'P243': 'Take precautionary measures against static discharge.',
    'P244': 'Keep reduction valves free from grease and oil.',
    'P250': 'Do not subject to grinding/shock/.../friction.',
    'P251': 'Pressurized container: Do not pierce or burn, even after use.',
    'P260': 'Do not breathe dust/fume/gas/mist/vapours/spray.',
    'P261': 'Avoid breathing dust/fume/gas/mist/vapours/spray.',
    'P262': 'Do not get in eyes, on skin, or in clothing.',
    'P263': 'Avoid contact during pregnancy/while nursing.',
    'P264': 'Wash skin thoroughly after handling.',
    'P270': 'Do not eat, drink or smoke when using this product.',
    'P271': 'Use only outdoors or in a well-ventilated area.',
    'P272': 'Contaminated work clothing should not be allowed out of the workplace.',
    'P273': 'Avoid release to the environment.',
    'P280': 'Wear protective gloves/protective clothing/eye protection/face protection.',
    'P281': 'Use personal protective equipment as required.',
    'P282': 'Wear cold insulating gloves/face shield/eye protection.',
    'P283': 'Wear fire/flame resistant/retardant clothing.',
    'P284': 'Wear respiratory protection.',
    'P285': 'In case of inadequate ventilation wear respiratory protection.',
    'P231+P232': 'Handle under inert gas. Protect from moisture.',
    'P235+P410': 'Keep cool. Protect from sunlight.',
   
    #P-300 Response
    'P301': 'IF SWALLOWED',
    'P302': 'IF ON SKIN',
    'P303': 'IF ON SKIN (or hair)',
    'P304': 'IF INHALED',
    'P305': 'IF IN EYES',
    'P306': 'IF ON CLOTHING',
    'P307': 'IF exposed',
    'P308': 'IF exposed or concerned',
    'P309': 'If exposed or if you feel unwell.',
    'P310': 'Immediately call a POISON CENTER or doctor/physician.',
    'P311': 'Call a POISON CENTER or doctor/physician.',
    'P312': 'Call a POISON CENTER or doctor/physician if you feel unwell.',
    'P313': 'Get medical advice/attention.',
    'P314': 'Get medical advice/attention if you feel unwell.',
    'P315': 'Get immediate medical advice/attention.',
    'P320': 'Specific treatment is urgent (see instructions on this label).',
    'P321': 'Specific treatment (see instructions on this label).',
    'P322': 'Specific measures (see instructions on this label).',
    'P330': 'Rinse mouth.',
    'P331': 'Do NOT induce vomiting.',
    'P332': 'IF SKIN irritation occurs: ',
    'P333': 'If skin irritation or rash occurs: ',
    'P334': 'Immerse in cool water/wrap and wet bandages.',
    'P335': 'Brush off loose articles from skin.',
    'P336': 'Thaw frosted parts with lukewarm water. Do not rub afflicted area.',
    'P337': 'If eye irritation persists: ',
    'P338': 'Remove contact lenses, if present and easy to do. Continue rinsing.',
    'P340': 'Remove victim to fresh air and keep at rest in a position comfortable for breathing.',
    'P341': 'If breathing is difficult, remove victim to fresh air and keep at rest in a position comfortable for breathing.',
    'P342': 'If experiencing respiratory symptoms: ',
    'P350': 'Gently wash with plenty of soap and water.',
    'P351': 'Rinse cautiously with water for several minutes.',
    'P352': 'Wash with plenty of soap and water.',
    'P353': 'Rinse skin with water/shower.',
    'P360': 'Rinse immediately contaminated clothing and skin with plenty of water before removing clothes.',
    'P361': 'Remove/Take off immediately all contaminated clothing.',
    'P362': 'Take off contaminated clothing and wash before reuse.',
    'P363': 'Wash contaminated clothing before reuse.',
    'P370': 'In case of fire: ',
    'P371': 'In case of major fire and large quantities:',
    'P372': 'Explosion risk in case of fire.',
    'P373': 'DO NOT fight fire when fire reaches explosives.',
    'P374': 'Fight fire with normal precautions from a reasonable distance.',
    'P376': 'Stop leak if safe to do so.',
    'P377': 'Leaking gas fire: Do not extinguish, unless leak can be stopped safely.',
    'P378': 'Use dry sand, dry chemical or alcohol-resistant foam for extinction.',
    'P380': 'Evacuate area.',
    'P381': 'Eliminate all ignition sources if safe to do so.',
    'P390': 'Absorb spillage to prevent material damage.',
    'P391': 'Collect spillage. Hazardous to the aquatic environment.',
    'P301+P310': 'IF SWALLOWED: Immediately call a POISON CENTER or doctor/physician.',
    'P301+P312': 'IF SWALLOWED: call a POISON CENTER or doctor/physician IF you feel unwell.',
    'P301+P330+P331': 'IF SWALLOWED: Rinse mouth. Do NOT induce vomiting.',
    'P302+P334': 'IF ON SKIN: Immerse in cool water/wrap in web bandages.',
    'P302+P350': 'IF ON SKIN: Gently wash with plenty of soap and water.',
    'P302+P352': 'IF ON SKIN: Wash with plenty of soap and water.',
    'P303+P361+P353': 'IF ON SKIN (or hair): Remove/Take off immediately all contaminated clothing. Rinse SKIN with water/shower.',
    'P304+P312': 'IF INHALED: Call a POISON CENTER or doctor/physician if you feel unwell.',
    'P304+P340': 'IF INHALED: Remove victim to fresh air and keep at rest in a position comfortable for breathing.',
    'P304+P341': 'IF INHALED: If breathing is difficult, remove victim to fresh air and keep at rest in a position comfortable for breathing.',
    'P305+P351+P338': 'IF IN EYES: Rinse cautiously with water for several minutes. Remove contact lenses, if present and easy to do. Continue rinsing.',
    'P306+P360': 'IF ON CLOTHING: Rinse immediately contaminated CLOTHING and SKIN with plenty of water before removing clothes.',
    'P307+P311': 'IF exposed: Call a POISON CENTER or doctor/physician.',
    'P308+P313': 'IF exposed or concerned: Get medical advice/attention.',
    'P309+P311': 'IF exposed or if you feel unwell: Call a POISON CENTER or doctor/physician.',
    'P332+P313': 'IF SKIN irritation occurs: Get medical advice/attention.',
    'P333+P313': 'IF SKIN irritation or rash occurs: Get medical advice/attention.',
    'P335+P334': 'Brush off loose particles from skin. Immerse in cool water/wrap in wet bandages.',
    'P337+P313': 'IF eye irritation persists: Get medical advice/attention.',
    'P342+P311': 'IF experiencing respiratory symptoms: call a POISON CENTER or doctor/physician.',
    'P370+P376': 'In case of fire: Stop leak if safe to do so.',
    'P370+P378': 'In case of fire: Use dry sand, dry chemical or alcohol-resistant foam for extinction.',
    'P370+P380': 'In case of fire: Evacuate area.',
    'P370+P380+P375': 'In case of fire: Evacuate area. Fight fire remotely due to the risk of explosion.',
    'P371+P380+P375': 'In case of major fire and large quantities: Evacuate area. Fight fire remotely due to the risk of explosion.',

    #P-400 Storage
    'P401': 'Store ...',
    'P402': 'Store in a dry place.',
    'P403': 'Store in a well-ventilated place.',
    'P404': 'Store in a closed container.',
    'P405': 'Store locked up.',
    'P406': 'Store in a corrosive resistant/... container with a resistant inner liner.',
    'P407': 'Maintain air grip between stacks/pallets.',
    'P410': 'Protect from sunlight.',
    'P411': 'Store at temperatures not exceeding ... Celsius/ ... Fahrenheit.',
    'P412': 'Do not expose to temperatures exceeding 50 Celsius/122 Fahrenheit',
    'P413': 'Store bulk masses greater than ... kg/... lbs at temperatures not exceeding ... Celsius/... Fahrenheit',
    'P420': 'Store away from other materials.',
    'P422': 'Store contents under ...',
    'P402+P404': 'Store in a dry place. Store in a closed container.',
    'P403+P233': 'Store in a well-ventilated place. Keep container tightly closed.',
    'P403+P235': 'Store in a well-ventilated place. Keep cool.',
    'P410+P403': 'Protect from sunlight. Store in a well-ventilated place.',
    'P410+P412': 'Protect from sunlight. Do not expose to temperatures exceeding 50 Celsius/122 Fahrenheit.',
    'P411+P235': 'Store at temperatures not exceeding ... Celsius/...Fahrenheit. Keep cool.',

    #P-500 Disposal
    'P501': 'Dispose of contents/container to an approved waste disposal plant according to local and federal regulations.',
    'P502': 'Refer to manufacturer/supplier for information on recovery/recycling.',
}


def get_hazard_class_dict_copy():
    #we do not need to store category 5 for mixtures because we always look at raw materials
    #when calculating ld50s for a compound mixture; category 5 is not hazardous
    hazard_class_dict = copy.deepcopy(HazardClassDict)
    hazard_class_dict['AcuteToxicityOral'].pop('5')
    hazard_class_dict['AcuteToxicityDermal'].pop('5')
    hazard_class_dict['AcuteToxicityInhalation'].pop('5')
    #should i get rid of category 3?  it appears in the document once, might be a typoe
    hazard_class_dict['SkinCorrosionHazard'].pop('3')

    return hazard_class_dict

blah = ['H303','H313','H316','H320','H333']

supplier_differences = {
    1: ['H225','H319','H335','H350','H402'],
    15: ['H227'],
    23: ['H315','H335'],
    24: ['H315','H335'],
    31: ['H313','H315','H320','H319','H335'],
    32: ['H315'],
    82: ['H412'],
    90: ['H226'],
    101: ['H227','H302','H315','H317','H304','H401','H411'],
    117: ['H315','H319','H335'],
    126: ['H319'],
    127: ['H303','H412'],
    128: ['H303','H412'],
    134: ['H332'],
    145: ['H301','H315','H319','H227'],
    204: ['H302','H315','H320','H319'],
    205: ['H227','H335'],
    207: ['H303','H315','H317','H319','H412'],
    208: ['H303','H315','H319','H341','H350','H401','H412'],
    214: ['H303'],
    220: ['H227'],
    229: ['H303','H319','H401'],
    246: ['H227'],
    248: ['H227'],
    268: ['H303','H315','H317'],
    277: ['H227'],
    280: ['H319','H402'],
    292: ['H226'],
    293: ['H315','H319'],
    294: ['H315','H317','H401'],
    297: ['H227'],
    303: ['H227'],
    305: ['H227'],
    325: ['H313','H319'],
    327: ['H315','H319','H335'],
    329: ['H319','H411'],
    341: ['H227'],
    355: ['H315','H319','H335'],
}

